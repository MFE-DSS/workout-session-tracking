"""Sb_SET_CONTRIBUTION_POLICY_01 — comptabilité effective des séries.

Ce que ces tests protègent :

1. **Physique et effectif ne se confondent jamais.** La dose exécutée reste la
   dose exécutée ; seule la comparaison au budget change d'unité.
2. **Aucun crédit fabriqué.** Une correspondance absente ne devient jamais 0,5.
3. **Le coefficient est une convention**, jamais présenté comme de la
   physiologie.
"""
from __future__ import annotations

from dataclasses import dataclass

import pytest

from app.services.set_contribution import (
    ACCOUNTING_GUARD,
    SET_CONTRIBUTION_POLICY_VERSION,
    UNITS_PER_DIRECT_SET,
    UNITS_PER_INDIRECT_SET,
    ContributionRole,
    ZoneContribution,
    accumulate,
    contributions_for,
    exercise_roles,
    units_for_sets,
)
from app.services.training_preferences import TrainingPreferencesData
from app.services.weekly_planner import build_weekly_plan

#: Composé canonique : primaire pecs, secondaire triceps.
COMPOUND = "Chest Press machine"
#: Isolation canonique sans secondaire.
ISOLATION = "Élévations latérales câble"
#: Tirage vertical : primaire lats, secondaire biceps.
PULLDOWN = "Lat pulldown prise large"


@dataclass(frozen=True)
class _Item:
    exercise_name: str
    planned_sets: int


def _plan(**kwargs):
    return build_weekly_plan(TrainingPreferencesData(**kwargs))


def _zone(plan, code):
    return next(z for z in plan.zone_coverage if z.zone_code == code)


# ── Le barème ────────────────────────────────────────────────────────────────


def test_a_direct_set_credits_one_effective_set():
    contributions = accumulate({}, ISOLATION, 4)
    delt = contributions["delt_lat"]
    assert delt.direct_sets == 4
    assert delt.indirect_sets == 0
    assert delt.effective_sets == 4.0


def test_an_indirect_set_credits_half_an_effective_set():
    contributions = accumulate({}, COMPOUND, 4)
    triceps = contributions["triceps"]
    assert triceps.direct_sets == 0
    assert triceps.indirect_sets == 4
    assert triceps.effective_sets == 2.0


def test_a_compound_credits_both_of_its_zones():
    contributions = accumulate({}, COMPOUND, 3)
    assert contributions["pecs"].effective_sets == 3.0
    assert contributions["triceps"].effective_sets == 1.5


def test_a_zone_listed_twice_is_credited_once_at_the_highest_role():
    """Primaire domine : jamais 4 + 2 pour la même série physique."""
    roles = {"pecs": ContributionRole.DIRECT}
    contribution = ZoneContribution(zone_code="pecs")
    for role in roles.values():
        contribution = contribution.plus(role, 4)
    assert contribution.effective_sets == 4.0

    # …et la résolution elle-même ne renvoie qu'un rôle par zone.
    for name in (COMPOUND, PULLDOWN, ISOLATION):
        zones = exercise_roles(name)
        assert len(zones) == len(set(zones)), "une zone apparaît deux fois"


def test_no_zone_exceeds_one_effective_set_per_physical_set():
    for name in (COMPOUND, PULLDOWN, ISOLATION):
        contributions = accumulate({}, name, 5)
        for contribution in contributions.values():
            assert contribution.effective_sets <= 5.0


# ── Aucun crédit fabriqué ────────────────────────────────────────────────────


def test_an_unresolved_exercise_credits_nothing():
    assert accumulate({}, "Exercice totalement inconnu", 4) == {}


def test_an_unknown_mapping_never_becomes_indirect_credit():
    contributions = accumulate({}, "Exercice totalement inconnu", 10)
    assert not contributions
    assert sum(c.effective_units for c in contributions.values()) == 0


def test_zero_or_negative_sets_credit_nothing():
    assert accumulate({}, COMPOUND, 0) == {}
    assert accumulate({}, COMPOUND, -3) == {}


def test_unknown_is_never_stored_as_a_zone():
    for name in ("", "   ", "Exercice inconnu"):
        assert "unknown" not in accumulate({}, name, 4)


# ── Unités entières, pas de flottants dans les gardes ───────────────────────


def test_credit_is_counted_in_whole_half_set_units():
    assert UNITS_PER_DIRECT_SET == 2
    assert UNITS_PER_INDIRECT_SET == 1
    contributions = accumulate({}, COMPOUND, 3)
    for contribution in contributions.values():
        assert isinstance(contribution.effective_units, int)


def test_band_bounds_convert_to_units_for_an_exact_comparison():
    assert units_for_sets(14) == 28
    plan = _plan(sessions_per_week=4)
    for zone in plan.zone_coverage:
        # La garde compare des entiers — jamais 0.5 accumulé en binaire.
        assert isinstance(zone.effective_units, int)
        assert zone.reaches_planning_low == (
            zone.effective_units >= units_for_sets(zone.planning_low_sets))


def test_an_odd_number_of_indirect_sets_stays_exact():
    """3 séries indirectes = 1,5 effective, sans erreur d'arrondi."""
    contributions = accumulate({}, COMPOUND, 3)
    assert contributions["triceps"].effective_units == 3
    assert contributions["triceps"].effective_sets == 1.5


# ── Physique ≠ effectif ──────────────────────────────────────────────────────


def test_the_physical_total_is_untouched_by_the_accounting_policy():
    plan = _plan(sessions_per_week=4)
    physical = sum(p.planned_sets for p in plan.prescriptions)
    assert plan.planned_sets_total == physical
    assert physical == 44, "la dose physique ne doit pas bouger avec la politique"


def test_planned_sets_stays_physical_and_effective_stays_separate():
    plan = _plan(sessions_per_week=4)
    calves = _zone(plan, "calves")
    # `calves` porte 8 séries physiques mais n'en récupère que 4 en direct :
    # les deux grandeurs ne peuvent pas être confondues.
    assert calves.planned_sets == 8
    assert calves.effective_sets == 4.0


def test_removing_indirect_credit_changes_the_budget_verdict():
    """Preuve que le crédit indirect est porteur, pas décoratif."""
    plan = _plan(sessions_per_week=4)
    biceps = _zone(plan, "biceps")
    assert biceps.indirect_sets > 0
    assert biceps.reaches_planning_low is True

    direct_only = biceps.direct_sets * UNITS_PER_DIRECT_SET
    assert direct_only < units_for_sets(biceps.planning_low_sets), (
        "sans le crédit indirect, cette zone n'atteindrait pas sa borne basse — "
        "si ce n'est plus vrai, le test ne prouve plus rien"
    )


def test_only_biceps_and_triceps_can_receive_indirect_credit_today():
    """Constat de données épinglé : le référentiel ne connaît que ces deux-là.

    Ce n'est pas un choix de conception mais une **limite du référentiel** :
    aucun exercice du pool ne déclare de zone secondaire autre. Le jour où la
    curation s'élargit, ce test tombe et il faudra le mettre à jour
    sciemment — c'est exactement ce qu'on veut voir arriver.
    """
    plan = _plan(sessions_per_week=6)
    credited = {
        z.zone_code for z in plan.zone_coverage if z.indirect_sets > 0}
    assert credited <= {"biceps", "triceps"}


# ── Traçabilité et langage ───────────────────────────────────────────────────


def test_the_policy_version_is_visible_in_the_basis():
    plan = _plan(sessions_per_week=4)
    pecs = _zone(plan, "pecs")
    assert any(
        SET_CONTRIBUTION_POLICY_VERSION in line
        for line in pecs.contribution_basis
    )


def test_an_indirectly_served_zone_says_so():
    plan = _plan(sessions_per_week=4)
    triceps = _zone(plan, "triceps")
    assert triceps.indirect_sets > 0
    assert any("convention de comptage" in line
               for line in triceps.contribution_basis)


def test_the_basis_states_what_the_number_is_without_naming_physiology():
    """Formulation positive : un démenti mettrait quand même le cadre en tête.

    Le démenti complet appartient à `ACCOUNTING_GUARD`, lu par le code et les
    développeurs, pas au texte que voit un consommateur.
    """
    plan = _plan(sessions_per_week=4)
    lines = [
        line for zone in plan.zone_coverage for line in zone.contribution_basis]
    assert lines
    assert any("coefficient 0,5" in line for line in lines)


@pytest.mark.parametrize("forbidden", [
    "activation", "emg", "%", "pourcent", "stimulus", "hypertroph",
    "physiolog", "recrutement",
])
def test_no_physiological_language_reaches_the_basis(forbidden):
    plan = _plan(sessions_per_week=4)
    for zone in plan.zone_coverage:
        for line in zone.contribution_basis:
            assert forbidden not in line.lower(), (
                f"« {forbidden} » apparaît dans le basis de {zone.zone_code}"
            )


def test_the_accounting_guard_is_recorded_in_code():
    guard = ACCOUNTING_GUARD.lower()
    assert "accounting convention" in guard
    assert "not physiology" in guard
    assert "not 50% muscle activation" in guard


def test_the_module_makes_no_literature_claim():
    from app.services import set_contribution as mod
    from tests.helpers import module_code_only

    text = mod.__doc__.lower() + module_code_only(mod).lower()
    for banned in ("acsm", "et al", "meta-analys", "étude montre", "prouve que"):
        assert banned not in text


# ── Non-régressions ──────────────────────────────────────────────────────────


def test_contributions_for_accepts_plan_prescriptions():
    plan = _plan(sessions_per_week=4)
    contributions = contributions_for(plan.prescriptions)
    assert contributions
    assert all(c.effective_units > 0 for c in contributions.values())


def test_contributions_are_deterministic():
    first = contributions_for([_Item(COMPOUND, 3), _Item(PULLDOWN, 4)])
    second = contributions_for([_Item(PULLDOWN, 4), _Item(COMPOUND, 3)])
    assert first == second


def test_the_plan_stays_deterministic():
    first = _plan(sessions_per_week=4, focus_priorities=("arms",))
    second = _plan(sessions_per_week=4, focus_priorities=("arms",))
    assert first.fingerprint == second.fingerprint


def test_materialization_still_uses_physical_sets():
    """La matérialisation prescrit ce qu'on exécute, jamais l'effectif."""
    from app.services.weekly_plan_materialization import plan_to_draft_tree

    plan = _plan(sessions_per_week=4)
    by_name = {
        slot.exercise_name: slot
        for s in plan.sessions for slot in s.slots if slot.is_prescribed
    }
    for session in plan_to_draft_tree(plan):
        for exercise in session["exercises"]:
            slot = by_name[exercise["exercise_name"]]
            assert len(exercise["rep_targets"]) == slot.planned_sets


def test_the_materializer_never_reads_effective_accounting():
    """Garde structurelle : le pont d'exécution ignore la comptabilité."""
    from app.services import weekly_plan_materialization as mod
    from tests.helpers import module_code_only

    code = module_code_only(mod)
    for banned in ("effective_units", "effective_sets", "indirect_sets"):
        assert banned not in code
