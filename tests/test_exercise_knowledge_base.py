"""Sb_CUSTOM_PROGRAM_EKB_02 — canonical exercise knowledge base JSON.

Pins the 103-entry canonical EKB derived from the EKB_01 snapshot: byte-exact
names, unique variant keys, the covered/gap split, the alias handling of the 2
orphan properties, the 11-fine-zone / macro-zone reconciliation, and the V1
`variant_group: null` decision. No scoring, no curated fine metadata, no
anatomical claim — those stay in later builds.
"""
from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EKB_FILE = PROJECT_ROOT / "data" / "exercise_knowledge_base.json"
SNAPSHOT_FILE = PROJECT_ROOT / "tests" / "fixtures" / "ekb_names_snapshot.json"
PROPERTIES_FILE = PROJECT_ROOT / "data" / "exercise_properties.json"

# 11 fine zones reconciled to 6 macro zones + core (muscle_mapping.RADAR_AXES).
FINE_TO_MACRO = {
    "pecs": "pecs",
    "delt_lat": "shoulders",
    "delt_post": "shoulders",
    "lats": "back_width",
    "upper_back": "back_thickness",
    "biceps": "arms",
    "triceps": "arms",
    "quads": "lower",
    "posterior": "lower",
    "calves": "lower",
    "core": "core",
}

COVERAGE_STATUSES = {"covered", "gap"}
CONFIDENCE_LEVELS = {"measured", "derived", "todo"}

# Lexique médical interdit (spec 02 §9-7) — l'EKB est opératoire, jamais clinique.
_MEDICAL_LEXICON = (
    "blessure", "pathologie", "douleur", "tendinite", "hernie", "diagnostic",
    "hormonal", "testostérone", "cortisol", "médical", "thérapeutique",
)


def _load_ekb() -> dict:
    return json.loads(EKB_FILE.read_text(encoding="utf-8"))


def _exercises() -> dict:
    return _load_ekb()["exercises"]


# ───────── référentiel : 103 noms byte-à-byte ─────────


def test_exactly_103_entries():
    assert len(_exercises()) == 103


def test_keys_match_snapshot_byte_exact():
    snapshot = json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))
    assert sorted(_exercises().keys()) == sorted(snapshot["names"])


def test_no_renaming_canonical_name_equals_key():
    for key, entry in _exercises().items():
        assert entry["canonical_name"] == key


# ───────── variant_key ─────────


def test_variant_key_present_and_unique():
    exercises = _exercises()
    keys = [e["variant_key"] for e in exercises.values()]
    assert all(k for k in keys)
    assert len(set(keys)) == 103


# ───────── variant_group : null V1 ─────────


def test_variant_group_null_in_v1():
    assert all(e["variant_group"] is None for e in _exercises().values())


# ───────── couverture 51 / 52 ─────────


def test_coverage_split_51_covered_52_gap():
    exercises = _exercises()
    covered = [e for e in exercises.values() if e["coverage_status"] == "covered"]
    gaps = [e for e in exercises.values() if e["coverage_status"] == "gap"]
    assert len(covered) == 67
    assert len(gaps) == 36


def test_covered_entries_consistent_with_properties():
    props = json.loads(PROPERTIES_FILE.read_text(encoding="utf-8"))["exercises"]
    for name, entry in _exercises().items():
        if entry["coverage_status"] == "covered":
            assert name in props
            assert entry["movement_pattern"] == props[name]["pattern_motor"]
            assert entry["chain"] == props[name]["chain"]
            assert entry["properties_source"]


def test_covered_status_matches_properties_membership():
    props = json.loads(PROPERTIES_FILE.read_text(encoding="utf-8"))["exercises"]
    for name, entry in _exercises().items():
        expected = "covered" if name in props else "gap"
        assert entry["coverage_status"] == expected


def test_gaps_remain_explicitly_marked():
    props = json.loads(PROPERTIES_FILE.read_text(encoding="utf-8"))["exercises"]
    for name, entry in _exercises().items():
        if name not in props:
            assert entry["coverage_status"] == "gap"
            # un gap n'a jamais de movement_pattern/chain inventé (source = properties)
            assert entry["movement_pattern"] is None
            assert entry["chain"] is None


def test_blackholes_stay_visible_not_masked():
    # les trous noirs : gap SANS zone, SANS machine, SANS equipment → todo
    # (Sb_MORPHO_POOL_COVERAGE_01: 7 anciens trous noirs morphotype couverts → 19 - 7 = 12)
    blackholes = [
        name
        for name, e in _exercises().items()
        if e["coverage_status"] == "gap"
        and not e["zone_primary"]
        and not e["machine_slug"]
        and not e["equipment_family"]
    ]
    assert len(blackholes) == 12
    for name in blackholes:
        assert _exercises()[name]["confidence"] == "todo"


# ───────── alias des 2 orphelines ─────────


def test_two_orphan_aliases_recorded():
    aliases = _load_ekb()["_aliases"]
    assert set(aliases) == {"Incline DB Press 30°", "Incline Dumbbell Press"}


def test_each_alias_points_to_existing_canonical_name():
    ekb = _load_ekb()
    names = set(ekb["exercises"])
    for source, target in ekb["_aliases"].items():
        assert target in names


def test_aliases_are_never_ekb_entries():
    ekb = _load_ekb()
    for source in ekb["_aliases"]:
        assert source not in ekb["exercises"]


# ───────── zones ─────────


def test_zone_primary_in_eleven_fine_zones():
    for entry in _exercises().values():
        if entry["zone_primary"] is not None:
            assert entry["zone_primary"] in FINE_TO_MACRO


def test_zone_macro_derived_from_zone_primary():
    for entry in _exercises().values():
        if entry["zone_primary"] is not None:
            assert entry["zone_macro"] == FINE_TO_MACRO[entry["zone_primary"]]
        else:
            assert entry["zone_macro"] is None


# ───────── enums fermés ─────────


def test_closed_enums_coverage_and_confidence():
    for entry in _exercises().values():
        assert entry["coverage_status"] in COVERAGE_STATUSES
        assert entry["confidence"] in CONFIDENCE_LEVELS


# ───────── non-médical ─────────


def test_no_medical_lexicon_in_ekb():
    blob = EKB_FILE.read_text(encoding="utf-8").lower()
    hits = [w for w in _MEDICAL_LEXICON if w in blob]
    assert not hits, f"lexique médical interdit présent: {hits}"


# ───────── non-régression EKB_01 ─────────


def test_ekb01_coverage_audit_still_green():
    from scripts.ekb_coverage_qa import run_audit

    report = run_audit()
    assert not report["errors"]
    assert report["canonical_count"] == 103


# ───────── Sb_EKB_ORTHOGRAPHIC_ALIAS_01 — deux écritures, une vérité ─────────
#
# LE DÉFAUT QU'AUCUNE GARDE NE VOYAIT. L'EKB portait 103 entrées pour 102
# exercices : `Curl marteau câble (corde)` et `Curl marteau câble corde`
# désignent le même mouvement, et se CONTREDISAIENT —
# `zone_primary: biceps` / `confidence: measured` d'un côté, `None` / `derived`
# de l'autre. Le même exercice était donc cartographié ou non **selon
# l'orthographe rencontrée**, dans la base dite canonique.
#
# Aucune source amont ne justifiait cet écart : `exercise_properties` porte les
# deux orthographes avec un contenu identique, et `classify_exercise` rend
# `biceps` pour les deux. C'était un défaut de CONSTRUCTION.
#
# Les 19 gardes existantes vérifiaient l'unicité des `variant_key`, la
# répartition covered/gap, la réconciliation des zones — jamais l'accord entre
# deux écritures d'un même nom. Cette garde ferme ce trou.
#
# ⚠ PORTÉE. La décision opérateur du 2026-08-23 **ne se généralise pas** aux 17
# autres candidats de quasi-doublon relevés par l'audit A1 : distinguer
# « Hip thrust Smith » de « Hip thrust Smith machine » reste un jugement
# produit. Cette garde ne teste que l'égalité APRÈS normalisation stricte, ce
# qui n'attrape que les écarts de ponctuation, d'accent et de casse — jamais
# une différence de mots.

#: Champs de cartographie qui doivent s'accorder entre deux écritures d'un même
#: nom. `variant_key` en est EXCLU : il est distinct par construction et sert
#: de clé de variante, pas d'identité — l'aligner créerait une collision.
_MAPPING_FIELDS = (
    "movement_pattern", "equipment_family", "chain",
    "zone_primary", "zone_macro", "coverage_status", "confidence",
)


def _normalized_groups() -> dict[str, list[str]]:
    from app.services.exercise_identity import normalize

    groups: dict[str, list[str]] = {}
    for name in _exercises():
        groups.setdefault(normalize(name), []).append(name)
    return {k: v for k, v in groups.items() if len(v) > 1}


def test_two_spellings_of_one_name_never_disagree():
    """La garde qui aurait attrapé la contradiction, si elle avait existé."""
    exercises = _exercises()
    conflicts: list[str] = []
    for names in _normalized_groups().values():
        first = names[0]
        for other in names[1:]:
            for field in _MAPPING_FIELDS:
                if exercises[first][field] != exercises[other][field]:
                    conflicts.append(
                        f"{field}: {first!r}={exercises[first][field]!r} vs "
                        f"{other!r}={exercises[other][field]!r}"
                    )
    assert conflicts == [], (
        "deux écritures d'un même nom portent des cartographies différentes — "
        f"l'exercice serait décrit selon l'orthographe rencontrée : {conflicts}"
    )


def test_the_known_orthographic_pair_is_still_the_only_one():
    """Un doublon d'orthographe NEUF doit se faire remarquer, pas se fondre
    dans une garde d'accord déjà satisfaite."""
    assert {tuple(sorted(v)) for v in _normalized_groups().values()} == {
        ("Curl marteau câble (corde)", "Curl marteau câble corde")
    }


def test_the_alias_entry_records_why_it_was_aligned():
    """Sans la note, le prochain lecteur croira à deux exercices distincts."""
    for name in ("Curl marteau câble (corde)", "Curl marteau câble corde"):
        note = _exercises()[name]["curation_note"]
        assert note and "ORTHOGRAPHIC_ALIAS" in note, name


def test_both_spellings_are_kept_history_is_not_rewritten():
    """Décision opérateur : **préserver les chaînes historiques.** Supprimer
    l'alias casserait toute donnée déjà écrite avec cette orthographe."""
    exercises = _exercises()
    assert "Curl marteau câble (corde)" in exercises
    assert "Curl marteau câble corde" in exercises
    assert len(exercises) == 103


def test_the_two_spellings_resolve_to_a_single_exercise_identity():
    """L'autorité d'identité reste `exercise_aliases`, pas l'EKB. Les 103
    entrées produisent **102** identités, et c'est la forme du catalogue qui
    porte le nom."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from app.database import Base
    from app.services.exercise_identity import resolve_exercise
    from app.services.seed_exercise_identity import seed_exercise_identity

    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine)() as db:
        report = seed_exercise_identity(db)
        assert report.total == 102
        canon = resolve_exercise(db, "Curl marteau câble (corde)")
        alias = resolve_exercise(db, "Curl marteau câble corde")
        assert canon.id == alias.id
        assert canon.name == "Curl marteau câble (corde)"


def test_alembic_head_unchanged():
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    script = ScriptDirectory.from_config(Config(str(PROJECT_ROOT / "alembic.ini")))
    # EKB_02 est data-only ; le head a ensuite avancé avec SCORING_03
    # (`o6p1j7k8m09`), PUBLICATION_01 (`p7q2k8l9n10`), TRAINING_PREFERENCES_01
    # (`q8r3l9m0o11` : table additive `training_preferences`, aucune colonne
    # ajoutée à `users`, aucun backfill), MORPHO_PROFILE_RUNTIME_01
    # (`r9s4m0n1p12` : colonne additive nullable `wingspan_cm` sur
    # `body_measurements`, aucun backfill, colonne héritée `calf_cm` intacte)
    # puis DECISION_ANALYTICS_RUNTIME_01 (`s0t5n1o2q13` : table additive
    # `decision_traces`, aucune colonne ajoutée ailleurs, aucun backfill — les
    # décisions passées n'ont pas été tracées et fabriquer leurs lignes
    # inventerait un raisonnement qui n'a jamais eu lieu),
    # puis EXERCISE_IDENTITY_01 (`t1u6o2p3r14` : deux tables additives
    # `exercises` et `exercise_aliases`, **aucune clé étrangère posée sur
    # `template_exercises` ni `session_exercises`** — remplir une colonne neuve
    # sur ces tables resterait un UPDATE de lignes historiques ; la résolution
    # se fait à la lecture, par la table d'alias).
    # Cette sentinelle suit le head courant.
    assert script.get_current_head() == "t1u6o2p3r14"
