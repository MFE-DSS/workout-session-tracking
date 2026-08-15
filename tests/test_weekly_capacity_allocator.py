"""Sb_WEEKLY_PLAN_CAPACITY_ALLOCATOR_01 — allouer la capacité déclarée.

Ce que ces tests protègent :

1. **Le dépassement PRÉVENTABLE est nul.** Un allocateur qui attribue du volume
   direct au-delà de la bande est en défaut ; un dépassement reçu en servant
   d'autres zones ne l'est pas. Les deux états ne se confondent jamais.
2. **Le budget est indépendant de la cadence**, sa réalisation ne l'est pas.
3. **Les identités d'exercice restent stables** — le volume vient
   d'occurrences répétées, pas d'exercices inventés.
"""
from __future__ import annotations

import statistics

import pytest

from app.services.training_preferences import TrainingPreferencesData
from app.services.weekly_capacity_allocator import (
    CAPACITY_ALLOCATOR_VERSION,
    COVERAGE_RATIO_GUARD,
    SESSION_SHAPE_CONVENTION_VERSION,
    SOFT_MAX_EXERCISES_PER_SESSION,
    SOFT_MAX_SETS_PER_SESSION,
    OvershootKind,
    classify_overshoot,
    coverage_ratio,
    indirect_receiving_zones,
)
from app.services.weekly_planner import PLANNER_VERSION, build_weekly_plan


def _plan(**kwargs):
    return build_weekly_plan(TrainingPreferencesData(**kwargs))


def _zone(plan, code):
    return next(z for z in plan.zone_coverage if z.zone_code == code)


def _ratios(plan):
    return [
        coverage_ratio(z.effective_units, z.planning_low_sets)
        for z in plan.zone_coverage
    ]


# ── 1. Dépassement : trois états, et PREVENTABLE reste à zéro ───────────────


@pytest.mark.parametrize("cadence", [2, 3, 4, 5])
def test_no_preventable_overshoot_at_any_cadence(cadence):
    """Exigence dure du brief. Un seul cas suffirait à invalider l'allocateur."""
    plan = _plan(sessions_per_week=cadence)
    offenders = [
        z.zone_code for z in plan.zone_coverage
        if z.overshoot_kind == OvershootKind.PREVENTABLE.value
    ]
    assert not offenders, f"sur-allocation directe sur {offenders}"


@pytest.mark.parametrize("cadence", [2, 3, 4, 5])
def test_allocated_volume_never_exceeds_the_high_band(cadence):
    """La garde dure porte sur ce qui est ATTRIBUÉ, pas sur le crédit reçu."""
    plan = _plan(sessions_per_week=cadence)
    for zone in plan.zone_coverage:
        assert zone.planned_sets <= zone.planning_high_sets, (
            f"{zone.zone_code} sur-allouée au-delà de sa borne haute"
        )


def test_the_three_overshoot_states_are_never_collapsed():
    zone = _zone(_plan(sessions_per_week=4), "pecs")
    high_units = zone.planning_high_sets * 2

    assert classify_overshoot(zone, high_units, 0) is OvershootKind.NONE
    # Au-dessus, mais sans sur-allocation : incident, pas défaut.
    assert classify_overshoot(zone, high_units + 4, 0) is OvershootKind.INCIDENTAL
    # Au-dessus PAR l'allocation elle-même : défaut.
    assert classify_overshoot(
        zone, high_units + 4, zone.planning_high_sets + 4
    ) is OvershootKind.PREVENTABLE


def test_an_incidental_overshoot_is_reported_with_its_size():
    """Quand il arrive, il est explicite — jamais silencieux."""
    plan = _plan(sessions_per_week=5)
    incidental = [
        z for z in plan.zone_coverage
        if z.overshoot_kind == OvershootKind.INCIDENTAL.value
    ]
    for zone in incidental:
        assert zone.effective_overshoot_units > 0
        assert zone.planned_sets <= zone.planning_high_sets


def test_indirect_receiving_zones_are_derived_not_hardcoded():
    """Aucune table « le dos donne du biceps » : la liste vient des données."""
    candidates = {
        "lats": [("Lat pulldown prise large", "lats_width_vertical_pull")],
        "pecs": [("Chest Press machine", "upper_chest_primary_press")],
    }
    receiving = indirect_receiving_zones(candidates)
    assert "biceps" in receiving
    assert "triceps" in receiving
    assert "lats" not in receiving, "une zone servie en primaire n'est pas receveuse"


def test_the_arms_case_is_incidental_not_preventable():
    """Le cas réel qui a motivé la décision opérateur, épinglé.

    `biceps` dépasse sa bande haute en exposition **effective** : servir `lats`
    et `upper_back` le crédite en secondaire. Ce qui compte est que ce
    dépassement soit **incident** et non provoqué — l'allocation directe reste
    largement dans la bande.

    Une version intermédiaire différait complètement les zones receveuses pour
    supprimer le dépassement. Elle a produit bien pire : la capacité de séance
    était consommée avant leur tour, et un utilisateur déclarant « Bras »
    recevait un programme **sans aucun exercice de bras**. Supprimer un
    dépassement comptable ne vaut pas d'affamer une zone demandée.
    """
    plan = _plan(sessions_per_week=4)
    biceps = _zone(plan, "biceps")
    assert biceps.indirect_sets > 0, "sans crédit indirect, le cas n'existe pas"
    assert biceps.overshoot_kind == OvershootKind.INCIDENTAL.value
    assert biceps.planned_sets <= biceps.planning_high_sets, (
        "l'allocation DIRECTE doit rester dans la bande"
    )


def test_a_zone_covered_only_indirectly_still_gets_a_real_exercise():
    """La garde qui manquait, et que l'incident a révélée.

    Un compteur rempli par du crédit indirect n'est pas un programme : si
    l'utilisateur ne voit aucun exercice pour la zone qu'il a déclarée, la
    demande n'est pas servie, quels que soient les chiffres.
    """
    for kwargs in ({}, {"focus_priorities": ("arms",)}):
        plan = _plan(sessions_per_week=4, **kwargs)
        for code in ("biceps", "triceps"):
            exercises = [
                slot.exercise_name for session in plan.sessions
                for slot in session.slots if slot.zone_code == code
            ]
            assert exercises, f"{code} n'a aucun exercice réel dans le plan"


# ── 2. Cadence : budget invariant, réalisation variable ─────────────────────


@pytest.mark.parametrize("cadence", [2, 3, 5, 6, 7])
def test_INVARIANT_1_the_budget_never_depends_on_cadence(cadence):
    """`WeeklyVolumeBudget` reste indépendant de la cadence. Sans exception."""
    reference = {
        z.zone_code: (z.planning_low_sets, z.baseline_sets, z.planning_high_sets)
        for z in _plan(sessions_per_week=4).zone_coverage
    }
    actual = {
        z.zone_code: (z.planning_low_sets, z.baseline_sets, z.planning_high_sets)
        for z in _plan(sessions_per_week=cadence).zone_coverage
    }
    assert actual == reference


def test_INVARIANT_2_more_capacity_never_yields_a_worse_solution():
    """Comparaison **objective**, pas monotonie brute du nombre de séries.

    Ajouter de la capacité ne doit pas pousser l'optimiseur vers une solution
    lexicographiquement pire, toutes choses égales par ailleurs. Un plateau
    reste légitime : une contrainte, un manque de candidat ou un plafond
    peuvent empêcher d'utiliser la capacité supplémentaire.

    C'est pourquoi ce fichier **n'affirme nulle part** une monotonie brute du
    type `phys(5) > phys(4) > phys(3)` : ce serait transformer une observation
    en loi, et faire échouer un plan correct le jour où une contrainte mord.
    La comparaison porte sur l'objectif, pas sur le compteur de séries.
    """
    def objective(cadence):
        plan = _plan(sessions_per_week=cadence)
        ratios = _ratios(plan)
        return (
            sum(1 for z in plan.zone_coverage if z.effective_units > 0),
            sum(1 for z in plan.zone_coverage if z.reaches_planning_low),
            round(min(ratios), 6),
        )

    for lower, higher in ((2, 3), (3, 4), (4, 5)):
        assert objective(higher) >= objective(lower), (
            f"cadence {higher} produit une solution pire que {lower}"
        )


def test_declared_capacity_is_actually_used():
    """Le défaut d'origine : 48 séries quelle que soit la cadence."""
    totals = {c: _plan(sessions_per_week=c).planned_sets_total for c in (2, 4)}
    assert totals[4] > totals[2], (
        "la capacité déclarée n'est toujours pas allouée"
    )


# ── 3. Stabilité des identités et forme de séance ───────────────────────────


@pytest.mark.parametrize("cadence", [2, 3, 4, 5])
def test_exercise_identities_stay_stable_as_cadence_rises(cadence):
    """Plus de volume = plus d'occurrences, pas plus d'exercices."""
    plan = _plan(sessions_per_week=cadence)
    identities = {p.exercise_name for p in plan.prescriptions}
    assert len(identities) <= 12, "l'allocateur invente de la variété"
    assert len(plan.prescriptions) >= len(identities), "des occurrences répétées"


def test_the_same_exercise_may_recur_across_sessions():
    plan = _plan(sessions_per_week=4)
    by_name: dict[str, set[int]] = {}
    for session in plan.sessions:
        for slot in session.slots:
            by_name.setdefault(slot.exercise_name, set()).add(session.index)
    repeated = {n: s for n, s in by_name.items() if len(s) > 1}
    assert repeated, "aucune identité répétée — la stabilité n'est pas obtenue"


def test_no_exercise_appears_twice_in_the_same_session():
    for cadence in (2, 3, 4, 5):
        for session in _plan(sessions_per_week=cadence).sessions:
            names = [slot.exercise_name for slot in session.slots]
            assert len(names) == len(set(names)), f"doublon en séance {session.index}"


@pytest.mark.parametrize("cadence", [2, 3, 4, 5])
def test_session_shape_stays_inside_the_measured_catalog_precedent(cadence):
    """6–8 exercices et 18–24 séries : précédent PRODUIT, pas optimum."""
    for session in _plan(sessions_per_week=cadence).sessions:
        assert len(session.slots) <= SOFT_MAX_EXERCISES_PER_SESSION
        assert sum(s.planned_sets for s in session.slots) <= SOFT_MAX_SETS_PER_SESSION


def test_the_hard_lifecycle_ceiling_is_never_approached_by_accident():
    from app.services.user_program_drafts import MAX_EXERCISES_PER_SESSION

    assert SOFT_MAX_EXERCISES_PER_SESSION < MAX_EXERCISES_PER_SESSION
    for session in _plan(sessions_per_week=4).sessions:
        assert len(session.slots) < MAX_EXERCISES_PER_SESSION


# ── 4. Équité et priorités ──────────────────────────────────────────────────


def test_a_priority_never_starves_the_other_zones():
    """Une priorité départage ; elle ne rafle pas la capacité."""
    plan = _plan(sessions_per_week=4, focus_priorities=("arms",))
    starved = [
        z.zone_code for z in plan.zone_coverage
        if z.effective_units == 0 and z.unmet_reason is None
    ]
    assert not starved
    served = sum(1 for z in plan.zone_coverage if z.effective_units > 0)
    assert served >= 10, "une priorité a assché les autres zones"


def test_a_declared_priority_is_materially_represented():
    plan = _plan(sessions_per_week=4, focus_priorities=("arms",))
    for code in ("biceps", "triceps"):
        assert _zone(plan, code).effective_units > 0


# ── 5. Langage et versions ──────────────────────────────────────────────────


def test_the_coverage_ratio_guard_is_recorded_in_code():
    guard = COVERAGE_RATIO_GUARD.lower()
    assert "planner coverage ratio" in guard
    assert "not physiological recovery" in guard
    assert "never displayed to users as a body metric" in guard


def test_the_session_shape_convention_is_versioned_as_product_precedent():
    assert SESSION_SHAPE_CONVENTION_VERSION == "session-shape-v1"
    assert SOFT_MAX_EXERCISES_PER_SESSION == 8
    assert SOFT_MAX_SETS_PER_SESSION == 24


def test_the_planner_version_was_bumped_but_not_the_volume_policy():
    """La sémantique réalisée change ; la politique de volume, non."""
    from app.services.weekly_volume_budget import POLICY_VERSION

    assert PLANNER_VERSION >= 2
    assert CAPACITY_ALLOCATOR_VERSION == "capacity-allocator-v1"
    assert POLICY_VERSION == "weekly-volume-v1", (
        "la politique de volume ne doit pas bouger pour un changement de "
        "réalisation"
    )


def test_the_fingerprint_incorporates_the_new_versions():
    plan = _plan(sessions_per_week=4)
    assert plan.fingerprint
    assert plan.planner_version == PLANNER_VERSION


def test_the_plan_stays_deterministic():
    first = _plan(sessions_per_week=4, focus_priorities=("arms",))
    second = _plan(sessions_per_week=4, focus_priorities=("arms",))
    assert first.fingerprint == second.fingerprint
    assert [p.exercise_name for p in first.prescriptions] == [
        p.exercise_name for p in second.prescriptions]


# ── 6. Le tableau de bord mesuré, épinglé contre la dérive ──────────────────


def test_the_cadence_matrix_is_pinned():
    """Résultats MESURÉS, épinglés pour détecter une dérive — pas une cible.

    Ces chiffres ne sont pas des vérités produit : ils décrivent ce que
    l'allocateur produit aujourd'hui sur le référentiel actuel. S'ils changent,
    il faut **enquêter**, pas forcer l'égalité.
    """
    observed = {}
    for cadence in (2, 3, 4, 5):
        plan = _plan(sessions_per_week=cadence)
        ratios = _ratios(plan)
        observed[cadence] = (
            plan.planned_sets_total,
            len({p.exercise_name for p in plan.prescriptions}),
            sum(1 for z in plan.zone_coverage if z.reaches_planning_low),
            round(statistics.median(ratios), 2),
        )

    assert observed[2][0] == 48
    assert observed[4][0] == 96
    assert observed[5][0] == 120
    # Couverture croissante avec la capacité, sans l'imposer comme loi.
    assert observed[5][2] > observed[2][2]
    # Identités stables à toutes les cadences.
    assert len({v[1] for v in observed.values()}) == 1
