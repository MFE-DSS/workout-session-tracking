"""Sb_WEEKLY_PLAN_SET_ALLOCATION_01 — réalisation en séries du plan hebdomadaire.

Le test central de cette tranche n'est pas « une zone reçoit des séries » : c'est
**`test_a_single_slot_never_covers_a_sixteen_set_zone`**. Tant que la couverture
se lisait en créneaux, un exercice de pectoraux valait seize séries de
pectoraux ; c'est précisément la confusion que cette tranche supprime.
"""
from __future__ import annotations

from dataclasses import dataclass

import pytest

from app.services.muscle_mapping import ZONE_VOLUME_TARGET
from app.services.training_preferences import TrainingPreferencesData
from app.services.weekly_planner import build_weekly_plan
from app.services.weekly_set_allocation import (
    ALLOCATION_POLICY_VERSION,
    PRODUCT_DEFAULT_REPS,
    REP_SOURCE_CATALOG,
    REP_SOURCE_INTENT,
    REP_SOURCE_PRODUCT_DEFAULT,
    SETS_PER_SLOT_MAX,
    SETS_PER_SLOT_MIN,
    UNMET_VOLUME,
    allocate_zone,
    distribute_sets,
    resolve_rep_target,
    target_sets_for,
)
from app.services.weekly_volume_budget import build_weekly_volume_budget


@dataclass(frozen=True)
class _FakeZone:
    """Une zone de budget fabriquée, pour éprouver une borne que le plan réel
    n'atteint jamais (la capacité y plafonne toujours en premier)."""

    zone_code: str
    planning_low_sets: int
    baseline_sets: int
    planning_high_sets: int
    priority_rank: int | None = None
    policy_version: str = "weekly-volume-v1"


@dataclass(frozen=True)
class _FakeSlot:
    slot_id: str
    exercise_name: str = "Chest Press machine"
    intent_id: str = "upper_chest_primary_press"
    rationale: str = "fixture"


def _plan(**kwargs):
    return build_weekly_plan(TrainingPreferencesData(**kwargs))


def _zone(plan, code):
    return next(z for z in plan.zone_coverage if z.zone_code == code)


# ── L'unité a changé : séries, plus créneaux ─────────────────────────────────


def test_a_single_slot_never_covers_a_sixteen_set_zone():
    """Le cœur de la tranche : un exercice ne vaut pas seize séries.

    `pecs` a une base de 16 séries et **un** créneau. Avant cette tranche la
    zone ressortait couverte ; elle doit désormais nommer son manque.
    """
    plan = _plan(sessions_per_week=4)
    pecs = _zone(plan, "pecs")
    assert pecs.baseline_sets == 16
    # L'allocateur de capacité place désormais plusieurs occurrences, mais la
    # propriété testée est inchangée : le nombre d'exercices ne fait pas la
    # couverture, seules les séries effectives la font.
    assert pecs.planned_sets > SETS_PER_SLOT_MAX, "plusieurs occurrences"
    assert pecs.effective_sets < pecs.planning_low_sets
    assert pecs.unmet_reason == UNMET_VOLUME


def test_budget_satisfaction_is_judged_on_sets_not_on_exercise_count():
    plan = _plan(sessions_per_week=4)
    for zone in plan.zone_coverage:
        if zone.unmet_reason is None:
            # « Couverte » signifie **atteindre la borne basse**, pas rester
            # sous la borne haute : une zone peut dépasser sa bande par crédit
            # indirect en servant d'autres zones, sans avoir été sur-allouée.
            assert zone.reaches_planning_low, (
                f"{zone.zone_code} déclarée couverte sous sa borne basse"
            )
        else:
            assert not zone.reaches_planning_low or zone.planned_slots == 0


def test_a_zone_reaching_its_band_is_judged_on_EFFECTIVE_sets():
    """Le témoin change de zone parce que l'UNITÉ a changé.

    Avant `Sb_SET_CONTRIBUTION_POLICY_01`, `calves` atteignait sa bande avec
    8 séries **physiques** sur deux créneaux. La couverture se juge désormais
    en séries **effectives**, et `calves` n'en reçoit que 4 : son second
    exercice, « Calf press leg press », est canoniquement rattaché à `quads`
    (voir `test_the_calf_press_miscredit_is_pinned`).

    `biceps` devient le témoin : il atteint sa borne basse **grâce au crédit
    indirect** des tirages, ce que le comptage physique ne voyait pas.
    """
    plan = _plan(sessions_per_week=4)
    biceps = _zone(plan, "biceps")
    assert biceps.indirect_sets > 0
    assert biceps.unmet_reason is None
    assert biceps.reaches_planning_low


def test_the_calf_press_miscredit_is_pinned():
    """Défaut de DONNÉES pré-existant, rendu mesurable par cette tranche.

    « Calf press leg press » est classé `calves` par l'EKB et `quads` par le
    classifieur canonique — le groupe `quads` contient « leg press » et gagne
    dans une liste ordonnée. Tant que la couverture se comptait par créneau, la
    divergence était **invisible** ; en comptabilité effective elle **crédite la
    mauvaise zone**.

    Ce test épingle l'état actuel pour qu'une correction éventuelle soit un
    choix explicite, pas une dérive silencieuse. Il n'approuve pas la donnée.
    """
    from app.services.body_zone_source import resolve_exercise_zones

    assert resolve_exercise_zones(None, "Calf press leg press").primary == "quads"

    # Le mauvais crédit se lit désormais sur l'exercice lui-même plutôt que sur
    # l'agrégat de la zone : l'allocateur peut ne plus retenir « Calf press leg
    # press » selon la couverture relative, ce qui ne corrige en rien la donnée.
    from app.services.set_contribution import exercise_roles

    assert "calves" not in exercise_roles("Calf press leg press"), (
        "la divergence a disparu — vérifier si la donnée a été corrigée"
    )


def test_every_covered_zone_respects_the_band_or_names_a_reason():
    """Acceptance du brief, sur les 11 zones, sans exception tolérée."""
    plan = _plan(sessions_per_week=4)
    for zone in plan.zone_coverage:
        # La couverture se juge en séries EFFECTIVES, et « couverte » veut dire
        # **borne basse atteinte** — un dépassement par crédit indirect n'est
        # pas un manque.
        assert zone.reaches_planning_low or zone.unmet_reason is not None, (
            f"{zone.zone_code} sous sa borne basse ET sans raison nommée"
        )


# ── Priorité : dans la bande, jamais au-delà ─────────────────────────────────


def test_priority_moves_the_target_to_the_high_side():
    budget = build_weekly_volume_budget(
        TrainingPreferencesData(focus_priorities=("arms",)))
    biceps = budget.zone("biceps")
    assert target_sets_for(biceps) == biceps.planning_high_sets


def test_no_priority_targets_the_baseline():
    budget = build_weekly_volume_budget()
    pecs = budget.zone("pecs")
    assert pecs.priority_rank is None
    assert target_sets_for(pecs) == pecs.baseline_sets


def test_priority_can_never_push_ALLOCATED_sets_above_the_high_bound():
    """Le plafond borne ce qui est **attribué**, pas le crédit incident.

    Servir `lats` et `upper_back` crédite `biceps` en secondaire ; refuser de
    programmer le dos pour protéger un plafond de biceps affamerait deux zones
    au profit d'une troisième que personne n'entraîne directement.
    """
    plan = _plan(sessions_per_week=6, focus_priorities=("arms", "lower", "pecs"))
    for zone in plan.zone_coverage:
        assert zone.planned_sets <= zone.planning_high_sets, (
            f"{zone.zone_code} SUR-ALLOUÉE au-delà de sa borne haute"
        )


def test_the_high_bound_binds_when_capacity_would_allow_more():
    """Le plafond doit mordre là où il PEUT être franchi.

    Sur un plan réel la capacité (4 séries × 1 créneau) plafonne bien avant la
    borne haute, si bien que l'assertion précédente passe sans jamais éprouver
    la garde. Une plantation l'a montré : elle ne tombait pas. Ce cas fabrique
    donc la seule configuration où le plafond est la contrainte active —
    quatre créneaux pour une borne haute de 8.
    """
    zone = _FakeZone(
        zone_code="pecs", planning_low_sets=4, baseline_sets=6,
        planning_high_sets=8, priority_rank=1,
    )
    slots = [_FakeSlot(f"slot{i}") for i in range(4)]  # capacité 16 séries
    allocation, prescriptions = allocate_zone(zone, slots)

    assert allocation.slot_capacity_sets == 16
    assert allocation.target_sets == 8
    assert allocation.planned_sets == 8, "le plafond doit être la contrainte active"
    assert sum(p.planned_sets for p in prescriptions) == 8
    assert allocation.unmet_reason is None


def test_priority_never_lowers_the_target():
    plain = _plan(sessions_per_week=4)
    prioritised = _plan(sessions_per_week=4, focus_priorities=("arms",))
    for code in ("biceps", "triceps"):
        assert (_zone(prioritised, code).target_sets
                >= _zone(plain, code).target_sets)


# ── Cadence : répartit, ne crée ni ne retire ─────────────────────────────────


@pytest.mark.parametrize("cadence", [2, 3, 5])
def test_cadence_never_changes_the_zone_BANDS(cadence):
    """L'invariant réel : la cadence ne déplace **aucune borne**.

    Il a changé de forme avec `Sb_WEEKLY_PLAN_CAPACITY_ALLOCATOR_01`. Tant que
    l'allocation était pilotée par la bande, le **total réalisé** était lui
    aussi indépendant de la cadence, et c'est ce que ce test épinglait.

    Désormais la cadence définit la **capacité** — plus de séances, plus de
    volume réalisable — ce que l'amendement opérateur demande explicitement de
    mesurer et de rapporter. Ce qui ne doit toujours pas bouger, c'est la
    **bande produit** de chaque zone : `planning_low`, `baseline`,
    `planning_high` sont identiques à toutes les cadences.
    """
    reference = {
        z.zone_code: (z.planning_low_sets, z.baseline_sets, z.planning_high_sets)
        for z in _plan(sessions_per_week=4).zone_coverage
    }
    actual = {
        z.zone_code: (z.planning_low_sets, z.baseline_sets, z.planning_high_sets)
        for z in _plan(sessions_per_week=cadence).zone_coverage
    }
    assert actual == reference


def test_more_sessions_allow_more_realized_volume():
    """Corollaire assumé : la capacité déclarée est enfin utilisée."""
    totals = [
        _plan(sessions_per_week=c).planned_sets_total for c in (2, 3, 4, 5)]
    assert totals == sorted(totals), "le volume doit croître avec la cadence"
    assert totals[0] < totals[-1], "sinon la capacité n'est toujours pas allouée"


def test_cadence_does_not_change_the_band_TARGET():
    """La cible dans la bande reste indépendante de la cadence.

    C'est la moitié survivante de l'ancien invariant : la cadence change ce
    qu'on peut **réaliser**, jamais ce que la bande **vise**.
    """
    def targets(cadence):
        return {
            z.zone_code: z.target_sets
            for z in _plan(sessions_per_week=cadence).zone_coverage
        }

    assert targets(2) == targets(6)
    assert targets(3) == targets(5)


def test_cadence_never_reaches_the_allocator_at_all():
    """La cadence n'est pas un paramètre du dosage — elle ne lui est pas passée.

    Garde structurelle : tant que l'allocateur n'a pas accès à la cadence, elle
    ne peut pas s'y glisser par inadvertance.
    """
    import inspect

    from app.services import weekly_set_allocation as mod

    for name in ("allocate_zone", "target_sets_for", "distribute_sets"):
        params = inspect.signature(getattr(mod, name)).parameters
        assert not any("cadence" in p or "session" in p for p in params), (
            f"{name} reçoit la cadence — le dosage hebdomadaire en dépendrait"
        )


# ── Répartition déterministe ─────────────────────────────────────────────────


def test_sets_are_distributed_without_a_hidden_remainder():
    assert sum(distribute_sets(10, 3)) == 10
    assert distribute_sets(10, 3) == (4, 3, 3)


def test_distribution_is_capped_by_the_catalog_ceiling():
    assert distribute_sets(40, 2) == (SETS_PER_SLOT_MAX, SETS_PER_SLOT_MAX)


def test_a_slot_below_the_catalog_floor_is_dropped_rather_than_prescribed():
    """Prescrire une série isolée ne serait pas une prescription crédible."""
    assert all(n >= SETS_PER_SLOT_MIN for n in distribute_sets(5, 4))


def test_distribution_is_empty_when_there_is_nothing_to_place():
    assert distribute_sets(0, 3) == ()
    assert distribute_sets(10, 0) == ()


def test_no_fractional_sets_anywhere():
    plan = _plan(sessions_per_week=4, focus_priorities=("arms",))
    for prescription in plan.prescriptions:
        assert isinstance(prescription.planned_sets, int)
    for zone in plan.zone_coverage:
        assert isinstance(zone.planned_sets, int)


# ── Répétitions : hiérarchie de sources, repli visible ───────────────────────


def test_the_catalog_is_the_first_source():
    reps = resolve_rep_target("Élévations latérales câble", "lateral_delt_priority")
    assert reps[2] == REP_SOURCE_CATALOG


def test_an_exercise_absent_from_the_catalog_falls_to_the_intent():
    reps = resolve_rep_target("Exercice inexistant", "lateral_delt_priority")
    assert reps[2] == REP_SOURCE_INTENT
    assert (reps[0], reps[1]) == (12, 20)


def test_a_contradictory_catalog_entry_is_not_arbitrated_here():
    """Huit exercices portent deux plages selon le template : on descend d'un cran.

    Trancher par ordre de lecture donnerait une réponse stable **et
    arbitraire** — le pire des deux mondes, parce qu'elle aurait l'air décidée.
    """
    reps = resolve_rep_target("Curl EZ-bar debout", "elbow_flexor_direct")
    assert reps[2] != REP_SOURCE_CATALOG


def test_a_new_intent_without_prescription_uses_the_named_product_default():
    """Les intentions de la tranche 1 n'héritent PAS des prescriptions morpho."""
    min_reps, max_reps, source = resolve_rep_target(
        "Exercice inexistant", "trunk_core_direct")
    assert source == REP_SOURCE_PRODUCT_DEFAULT
    assert min_reps == PRODUCT_DEFAULT_REPS[0]
    assert max_reps == PRODUCT_DEFAULT_REPS[1]


def test_the_intent_source_contributes_reps_only_never_sets():
    """Le nombre de séries du mapper appartenait à un autre modèle.

    Le témoin est `quad_minimum_effective_dose` (**2** séries au mapper) et non
    `lateral_delt_priority` : celui-ci en prescrit 4, exactement le plafond de
    l'allocateur, si bien que les deux valeurs coïncidaient par accident et que
    l'assertion passait sans rien prouver.
    """
    from app.services.morpho_program_draft_mapper import _INTENT_PRESCRIPTION

    mapper_sets, min_reps, max_reps = _INTENT_PRESCRIPTION[
        "quad_minimum_effective_dose"]
    resolved_min, resolved_max, _ = resolve_rep_target(
        "Exercice inexistant", "quad_minimum_effective_dose")
    # La PLAGE vient bien de l'intention…
    assert resolved_min == min_reps
    assert resolved_max == max_reps
    # …mais le nombre de SÉRIES vient du budget, et diffère du mapper.
    quads = _zone(_plan(sessions_per_week=4), "quads")
    assert quads.planned_sets != mapper_sets


def test_every_fallback_is_visible_in_the_basis():
    plan = _plan(sessions_per_week=4)
    for zone in plan.zone_coverage:
        sources = {
            p.rep_target_source for p in plan.prescriptions
            if p.zone_code == zone.zone_code
        }
        for source in sources - {REP_SOURCE_CATALOG}:
            assert any(source in line for line in zone.allocation_basis), (
                f"repli {source} invisible dans le basis de {zone.zone_code}"
            )


# ── Prescriptions : la forme que la matérialisation consommera ───────────────


def test_a_prescription_carries_everything_a_draft_needs():
    plan = _plan(sessions_per_week=4)
    assert plan.prescriptions
    for p in plan.prescriptions:
        assert p.exercise_name
        assert p.zone_code in ZONE_VOLUME_TARGET
        assert p.intent_id
        assert p.planned_sets >= SETS_PER_SLOT_MIN
        assert p.min_reps <= p.max_reps
        assert p.rep_target_source
        assert p.budget_source
        assert p.policy_version == ALLOCATION_POLICY_VERSION


def test_the_set_scheme_matches_the_catalog_format():
    plan = _plan(sessions_per_week=4)
    scheme = plan.prescriptions[0].set_scheme
    assert "x " in scheme
    assert "-" in scheme


def test_slots_carry_their_dose_so_a_session_reads_on_its_own():
    plan = _plan(sessions_per_week=4)
    filled = [s for sess in plan.sessions for s in sess.slots if s.is_filled]
    assert filled
    for slot in filled:
        assert slot.is_prescribed
        assert slot.planned_sets >= SETS_PER_SLOT_MIN
        assert slot.rep_target_source


def test_an_unservable_zone_never_reaches_a_session():
    """Le fail-open historique est devenu **structurellement impossible**.

    L'allocateur de capacité ne place que des occurrences réellement dotées :
    un créneau vide ne peut plus entrer dans une séance, là où il fallait
    auparavant une garde pour l'empêcher de compter comme couverture.

    La garde change donc de forme — on vérifie que la zone non servable sort
    bien à zéro avec une raison nommée, et qu'aucune séance ne contient de
    créneau sans dose.
    """
    plan = _plan(sessions_per_week=4, available_equipment=("machine", "cable"))
    core = _zone(plan, "core")
    assert core.planned_slots == 0
    assert core.planned_sets == 0
    assert core.unmet_reason is not None

    for session in plan.sessions:
        for slot in session.slots:
            assert slot.is_prescribed, "une séance ne contient que du réalisable"


def test_prescriptions_are_ordered_deterministically():
    first = _plan(sessions_per_week=4, focus_priorities=("arms",))
    second = _plan(sessions_per_week=4, focus_priorities=("arms",))
    assert [p.slot_id for p in first.prescriptions] == [
        p.slot_id for p in second.prescriptions]
    assert first.fingerprint == second.fingerprint


# ── Priorité des raisons : ne pas désigner le mauvais mur ────────────────────


def test_a_zone_without_candidates_reports_that_not_a_volume_shortfall():
    """Dire « il manque des séries » quand aucun exercice n'est disponible
    désignerait le mauvais mur. Témoin sous restriction depuis que `core` est
    servable sans contrainte de matériel."""
    plan = _plan(sessions_per_week=4, available_equipment=("machine", "cable"))
    core = _zone(plan, "core")
    assert core.planned_sets == 0
    assert core.unmet_reason != UNMET_VOLUME


def test_an_equipment_gap_still_outranks_a_volume_gap():
    plan = _plan(
        sessions_per_week=4,
        focus_priorities=("arms",),
        available_equipment=("dumbbell", "barbell", "machine"),
    )
    triceps = _zone(plan, "triceps")
    assert triceps.planned_sets == 0
    assert triceps.unmet_reason != UNMET_VOLUME


# ── Le constat chiffré, épinglé pour qu'il ne dérive pas en silence ──────────


def test_the_structural_shortfall_is_pinned():
    """Le plan ne délivre qu'une fraction du budget — chiffre épinglé, pas caché.

    Ce test n'approuve pas la situation : il empêche qu'elle change sans que
    quelqu'un s'en aperçoive. Le jour où le nombre de créneaux par zone devient
    une décision produit, ce chiffre bougera et ce test le dira.
    """
    plan = _plan(sessions_per_week=4)
    low_sum = sum(z.planning_low_sets for z in plan.zone_coverage)
    effective = sum(z.effective_sets for z in plan.zone_coverage)
    # Le déficit s'est RÉDUIT sans disparaître : l'allocateur de capacité a
    # fait passer le réalisé de 48 à 96 séries physiques, mais `Σ planning_low`
    # reste hors d'atteinte à cette cadence — et ce n'est pas une cible dure.
    assert effective < low_sum, "le déficit produit reste réel à cadence 4"
    unmet_volume = [z for z in plan.unmet_budget if z.unmet_reason == UNMET_VOLUME]
    assert unmet_volume, "les zones encore courtes doivent rester nommées"
    assert len(unmet_volume) < 8, (
        "le déficit ne s'est pas réduit — l'allocateur n'alloue pas"
    )
