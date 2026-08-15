"""Sb_CORE_EXERCISE_PROPERTIES_01 — rendre `core` programmable, sans rien inventer.

Ce que ces tests protègent, par ordre d'importance :

1. **Le registre de substitution n'est pas touché du tout.** Les candidats de
   tronc vivent dans un registre **du planificateur** : l'isolement du tiroir
   N1/N2/N3 est garanti *par construction*, pas démontré après coup. Une
   première version les écrivait dans `exercise_properties.json` ; le contrat
   de ce fichier — un `equipment_family` obligatoire par entrée — l'a
   immédiatement refusé, et il avait raison.
2. **Aucune propriété fabriquée.** Aucun `equipment_family` n'est inventé, et
   les exercices sans preuve restent dehors, nommés.
3. **Aucun vocabulaire nouveau.** `core` est un `PatternMotor` qui existait
   déjà.
"""
from __future__ import annotations

import json

import pytest

from app.config import BASE_DIR
from app.services.body_zone_source import resolve_exercise_zones
from app.services.planner_candidates import (
    CORE_CANDIDATES,
    CORE_WITHOUT_EVIDENCE,
    planner_candidate_pool,
)
from app.services.substitution import (
    VALID_PATTERN_MOTORS,
    compute_suggestions,
    load_exercise_properties,
)
from app.services.training_preferences import TrainingPreferencesData
from app.services.weekly_planner import (
    UNMET_EQUIPMENT,
    UNMET_NO_CANDIDATE,
    build_weekly_plan,
)

#: Les 5 exercices dotés de propriétés par cette tranche — présents dans un
#: template curé de `reference_split.json` ET classés `core` au référentiel.
ADDED = (
    "Crunch câble à genoux",
    "Pallof press câble",
    "Relevé de jambes suspendu",
    "Roulette abdominale",
    "Roulette abdominale (ab wheel rollout)",
)

#: Les 3 exercices canoniques laissés DEHORS, faute de preuve.
LEFT_OUT = ("Decline crunch", "Hanging knee raise", "Machine crunch")


def _plan(**kwargs):
    return build_weekly_plan(TrainingPreferencesData(**kwargs))


def _zone(plan, code):
    return next(z for z in plan.zone_coverage if z.zone_code == code)


class _TE:
    """Minimal template-exercise stand-in for `compute_suggestions`."""

    def __init__(self, name: str) -> None:
        self.exercise_name = name
        self.name = name
        self.substitutes = []


# ── La preuve qui compte : la substitution n'a pas bougé ────────────────────


def test_the_substitution_registry_is_untouched():
    """L'isolement est garanti PAR CONSTRUCTION, pas démontré après coup.

    Les candidats de tronc vivent dans un registre **du planificateur**. Le
    registre de substitution garde exactement ses 69 entrées, donc le tiroir
    N1/N2/N3 ne peut pas changer — il n'a rien de nouveau à voir.

    C'est le contrat `test_exercise_properties_loads_and_validates` qui a
    imposé ce choix : il exige un `equipment_family` sur chaque entrée, et
    aucune source du dépôt n'en documente un pour le tronc.
    """
    registry = load_exercise_properties()
    assert len(registry) == 69
    for name in ADDED:
        assert name not in registry, (
            f"{name} a été écrit dans le registre de SUBSTITUTION"
        )


def test_no_core_candidate_can_ever_be_suggested():
    """Contrôle de bout en bout : aucun exercice de tronc dans le tiroir."""
    added = set(ADDED)
    for name in load_exercise_properties():
        suggestions = compute_suggestions(_TE(name))
        for level in ("N1", "N2", "N3"):
            proposed = {s.name for s in suggestions[level]}
            assert not (proposed & added), (
                f"{name} propose un exercice core en {level}"
            )


def test_the_cross_pattern_bridges_never_mention_core():
    """Quatrième et dernier vecteur possible vers N3 — vérifié, pas supposé."""
    raw = (BASE_DIR / "data" / "cross_pattern_substitutions.json").read_text(
        encoding="utf-8")
    assert "core" not in raw


def test_the_planner_pool_extends_the_registry_without_mutating_it():
    """Le pool du planificateur = registre + tronc, et le registre reste intact."""
    registry = load_exercise_properties()
    pool = planner_candidate_pool()
    assert set(pool) == set(registry) | set(CORE_CANDIDATES)
    assert len(load_exercise_properties()) == 69, "le cache a été muté"
    for name, props in registry.items():
        assert pool[name] == props, f"{name} altéré par le pool planificateur"


# ── Aucune propriété fabriquée ───────────────────────────────────────────────


def test_no_equipment_family_is_invented():
    """Aucune source du dépôt ne dit avec quel matériel ces exercices se font.

    Ni l'EKB, ni `machine_slug`/`machine_family` dans `reference_split`, ni le
    registre. Le champ est donc **absent** — ce qui rend la zone honnêtement
    indisponible sous restriction, plutôt que disponible sur une supposition.
    """
    for name, props in CORE_CANDIDATES.items():
        assert "equipment_family" not in props, (
            f"{name} a reçu un matériel qu'aucune preuve du dépôt ne soutient"
        )


def test_the_added_entries_use_only_existing_vocabulary():
    for props in CORE_CANDIDATES.values():
        assert props["pattern_motor"] == "core"
        assert props["pattern_motor"] in VALID_PATTERN_MOTORS


def test_no_new_pattern_motor_was_created():
    """Ni `flexion_core`, ni `anti_rotation`, ni `anti_extension`."""
    for banned in ("flexion_core", "anti_rotation", "anti_extension",
                   "trunk_flexion"):
        assert banned not in VALID_PATTERN_MOTORS
    assert {p["pattern_motor"] for p in planner_candidate_pool().values()} \
        <= VALID_PATTERN_MOTORS


def test_every_added_exercise_is_canonically_a_core_exercise():
    """Le classement `core` vient du référentiel, pas de cette tranche."""
    for name in ADDED:
        assert resolve_exercise_zones(None, name).primary == "core"


def test_every_added_exercise_appears_in_a_curated_template():
    """Preuve la plus forte disponible : le catalogue les programme déjà."""
    templates = json.loads(
        (BASE_DIR / "data" / "reference_split.json").read_text(encoding="utf-8")
    )["templates"]
    catalogued = {
        e["name"] for t in templates for e in t.get("exercises", [])}
    for name in ADDED:
        assert name in catalogued


def test_the_exercises_without_evidence_are_left_out_and_named():
    """`Zero fabrication outranks completeness` — appliqué littéralement.

    Ces trois exercices sont classés `core` par le classifieur de noms, mais
    n'apparaissent dans **aucun** template curé et l'EKB ne leur attribue
    aucune zone (`confidence: todo`). Rien ne dit comment ils se programment ;
    leur inventer un motif serait exactement ce que le brief interdit.
    """
    pool = planner_candidate_pool()
    for name in LEFT_OUT:
        assert name not in pool, (
            f"{name} a reçu des propriétés sans preuve dans le dépôt"
        )
    assert set(CORE_WITHOUT_EVIDENCE) == set(LEFT_OUT)


# ── `core` devient programmable, honnêtement ────────────────────────────────


def test_core_is_programmable_without_an_equipment_restriction():
    plan = _plan(sessions_per_week=4)
    core = _zone(plan, "core")
    assert core.planned_slots == 1
    assert core.planned_sets > 0
    assert core.unmet_reason != UNMET_NO_CANDIDATE


def test_the_core_slot_selects_a_canonical_core_exercise():
    plan = _plan(sessions_per_week=4)
    chosen = next(
        s.exercise_name for sess in plan.sessions for s in sess.slots
        if s.zone_code == "core" and s.is_prescribed
    )
    assert chosen in CORE_CANDIDATES
    assert resolve_exercise_zones(None, chosen).primary == "core"


def test_core_stays_honestly_unavailable_under_an_equipment_restriction():
    """Sans matériel déclaré au référentiel, la zone tombe — et le dit."""
    plan = _plan(
        sessions_per_week=4, available_equipment=("machine", "cable"))
    core = _zone(plan, "core")
    assert core.planned_slots == 0
    assert core.unmet_reason == UNMET_EQUIPMENT


def test_core_credits_only_the_core_zone():
    """Aucun crédit indirect fabriqué au passage."""
    from app.services.set_contribution import exercise_roles

    for name in ADDED:
        roles = exercise_roles(name)
        assert set(roles) == {"core"}, f"{name} crédite {set(roles)}"


# ── Non-régressions ──────────────────────────────────────────────────────────


def test_the_pool_grew_by_exactly_the_added_entries():
    assert len(planner_candidate_pool()) == 69 + len(ADDED)


def test_the_loader_still_validates_every_pattern_motor():
    """Le garde-fou de chargement reste actif sur le fichier modifié."""
    for name, entry in planner_candidate_pool().items():
        assert entry.get("pattern_motor") in VALID_PATTERN_MOTORS, name


def test_the_physical_dose_grows_only_by_the_new_core_slot():
    plan = _plan(sessions_per_week=4)
    core = _zone(plan, "core")
    assert plan.planned_sets_total == 44 + core.planned_sets


@pytest.mark.parametrize("zone_code", [
    "pecs", "delt_lat", "delt_post", "lats", "upper_back",
    "biceps", "triceps", "quads", "posterior", "calves",
])
def test_no_other_zone_changed_its_physical_dose(zone_code):
    plan = _plan(sessions_per_week=4)
    zone = _zone(plan, zone_code)
    expected = 8 if zone_code == "calves" else 4
    assert zone.planned_sets == expected


def test_the_plan_stays_deterministic():
    first = _plan(sessions_per_week=4)
    second = _plan(sessions_per_week=4)
    assert first.fingerprint == second.fingerprint
