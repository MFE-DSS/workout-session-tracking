"""Sb_ATLAS_COVERAGE_01 — couverture atlas des exercices actifs.

Trois exercices du split de référence n'avaient aucun cue : leurs lignes
`TemplateExercise` portent `machine_slug=None` ET `machine_family=None`.

Le correctif ne passe PAS par le catalogue. `seed_reference_split()` est
verrouillé sur la version du payload, et bumper cette version déclenche un
wipe des lignes SYSTEM : mesuré sur copie jetable, le lien `template_exercise`
des séances passées tombe de 7/7 à 0/7 et leurs cues de 4/7 à 0/7
(`ondelete="SET NULL"`). Couvrir trois exercices en retirant les cues de tout
l'historique aurait été un très mauvais échange.

La résolution retombe donc sur le **snapshot de nom**, précisément conçu pour
survivre au reseed. La couverture devient indépendante du seed et
**rétroactive**.
"""
from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
ATLAS = ROOT / "data/machine_atlas.json"
SPLIT = ROOT / "data/reference_split.json"
RESOLVER = ROOT / "app/services/machine_atlas.py"

#: Clés que l'audit Sb_FEEDBACK_SIGNAL_AUDIT_01 interdit tant que rien ne les
#: affiche — ajouter de la donnée morte est précisément le défaut qu'il a
#: documenté.
DEAD_KEYS = ("setup_checklist", "correction_hints", "correction_hint")

PSEUDO_MEDICAL = (
    "diagnostic", "blessure", "pathologie", "lésion", "activation musculaire",
    "EMG", "tendinite", "guérir", "soigner", "thérapeut",
)

#: Textes génériques interdits : un exercice non mappé doit rester SILENCIEUX.
GENERIC = (
    "bien exécuter le mouvement", "reste concentré", "fais attention",
    "exécute correctement", "garde une bonne technique",
)


def _atlas() -> dict:
    return json.loads(ATLAS.read_text(encoding="utf-8"))


def _machines():
    for family in _atlas()["families"]:
        for machine in family["machines"]:
            yield family, machine


# ───────── A1 — couverture des exercices réellement programmés ─────────


def test_every_push_a_exercise_resolves_to_an_atlas_machine():
    """Les 7 exercices de la surface testée ont tous un cue affichable.

    La résolution est vérifiée par NOM, comme en production pour les
    exercices dont le catalogue ne porte pas de `machine_slug`.
    """
    from app.services.machine_atlas import get_machine_by_name

    split = json.loads(SPLIT.read_text(encoding="utf-8"))
    push_a = next(t for t in split["templates"] if t["slug"] == "push-a")

    unresolved = []
    for exercise in push_a["exercises"]:
        slug = exercise.get("machine_slug")
        if slug:
            continue  # déjà relié par le catalogue
        if get_machine_by_name(exercise["name"]) is None:
            unresolved.append(f"{exercise.get('code')} {exercise['name']!r}")

    assert not unresolved, (
        f"no atlas cue for: {unresolved}. Either add the machine/alias, or "
        "leave it silent deliberately — never a generic sentence."
    )


def test_the_three_previously_uncovered_exercises_are_now_mapped():
    """Garde nominative : ces trois-là étaient le défaut mesuré."""
    from app.services.machine_atlas import get_machine_by_name

    expected = {
        "Dips pectoraux (buste penché)": "chest-dips",
        "Écarté arrière d'épaule câble": "cable-rear-delt-fly",
        "Triceps extension poulie haute (corde)": "triceps-pushdown-rope",
    }
    for name, slug in expected.items():
        machine = get_machine_by_name(name)
        assert machine is not None, f"{name!r} still unmapped"
        assert machine["slug"] == slug, f"{name!r} → {machine['slug']}"


def test_resolution_survives_a_missing_template_link():
    """Le cœur du choix : la couverture ne dépend pas du seed.

    Un `SessionExercise` dont `template_exercise` est None — l'état exact des
    séances historiques après un reseed — doit tout de même résoudre son cue
    via le snapshot de nom.
    """
    from app.services.machine_atlas import get_for_session_exercise

    class _Orphan:
        substituted_name = None
        template_exercise = None
        exercise_name_snapshot = "Dips pectoraux (buste penché)"

    entry = get_for_session_exercise(_Orphan())
    assert entry is not None, "no atlas entry resolved"
    assert entry["machine"]["slug"] == "chest-dips"


def test_the_name_fallback_is_exact_never_fuzzy():
    """Un rapprochement approximatif produirait une consigne qui ne
    correspond pas à la machine — pire que le silence."""
    from app.services.machine_atlas import get_machine_by_name

    assert get_machine_by_name("Dips") is None
    assert get_machine_by_name("Triceps") is None
    assert get_machine_by_name("Écarté") is None


# ───────── A2 — silence honnête, jamais de texte générique ─────────


def test_no_generic_cue_exists_in_the_atlas():
    offenders = []
    for _, machine in _machines():
        for text in machine["execution_cues"] + machine["common_mistakes"]:
            low = text.lower()
            for banned in GENERIC:
                if banned in low:
                    offenders.append(f"{machine['slug']}: {text!r}")
    assert not offenders, offenders


def test_an_unmapped_name_returns_nothing_at_all():
    from app.services.machine_atlas import get_machine_by_name

    assert get_machine_by_name("Exercice qui n'existe pas") is None


# ───────── A3 — contrat atlas préservé ─────────


def test_every_machine_has_exactly_three_cues():
    bad = [m["slug"] for _, m in _machines() if len(m["execution_cues"]) != 3]
    assert not bad, bad


def test_every_machine_has_exactly_two_common_mistakes():
    bad = [m["slug"] for _, m in _machines() if len(m["common_mistakes"]) != 2]
    assert not bad, bad


def test_no_machine_makes_a_medical_claim():
    offenders = []
    for _, machine in _machines():
        for text in machine["execution_cues"] + machine["common_mistakes"]:
            low = text.lower()
            for banned in PSEUDO_MEDICAL:
                if banned in low:
                    offenders.append(f"{machine['slug']}: {text!r}")
    assert not offenders, offenders


def test_the_new_family_uses_a_canonical_zone_code():
    """`triceps` existe déjà dans le vocabulaire produit — aucun code
    inventé pour l'occasion."""
    from app.services.muscle_mapping import ZONE_LABELS

    zones = {f["zone"] for f in _atlas()["families"]}
    unknown = sorted(z for z in zones if z not in ZONE_LABELS)
    assert "triceps" in zones, "arms family missing"
    assert not unknown, f"atlas zones outside the canonical vocabulary: {unknown}"


# ───────── A7 — aucune donnée morte ─────────


def test_the_atlas_grows_no_unconsumed_key():
    """`setup_checklist` / `correction_hints` restent absents tant que rien
    ne les affiche — la leçon de Sb_FEEDBACK_SIGNAL_AUDIT_01."""
    raw = ATLAS.read_text(encoding="utf-8")
    for key in DEAD_KEYS:
        assert key not in raw, f"{key} added but nothing renders it"


def test_machine_entries_keep_the_existing_shape():
    reference = {
        "slug", "name", "aliases", "variants", "equipment",
        "laterality", "load_semantics", "execution_cues", "common_mistakes",
    }
    for _, machine in _machines():
        extra = set(machine) - reference
        assert not extra, f"{machine['slug']} introduces keys: {sorted(extra)}"


# ───────── A4 — la source reste l'atlas ─────────


def test_the_name_fallback_reads_the_snapshot_not_a_hardcoded_map():
    src = RESOLVER.read_text(encoding="utf-8")
    assert "exercise_name_snapshot" in src
    assert re.search(r"get_machine_by_name\(\s*\n?\s*getattr\(", src), (
        "the fallback must go through the atlas lookup, not a local dict"
    )
