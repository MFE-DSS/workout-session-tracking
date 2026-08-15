"""Sb_ADAPTIVE_REPLAN_SET_SEMANTICS_01 — la replanification compte en séries.

Un créneau peut désormais porter plusieurs séries, donc un delta exprimé en
créneaux ne dit plus combien de travail bouge. Ce que ces tests protègent :

1. **L'asymétrie porte sur les séries.** Une preuve limitante peut en retirer ;
   une preuve favorable ne peut **rien** en ajouter, jamais.
2. **Le mouvement de créneaux reste observable séparément** — la forme de la
   semaine et sa charge sont deux informations, aucune ne se déduit de l'autre.
3. **La limite plan↔séance est tenue, pas contournée.** Une séance écourtée
   diverge mais ne retire aucune série par déduction.
"""
from __future__ import annotations

import pytest

from app.services.adaptive_replan import (
    PERFORMED_SET_IDENTITY_LIMITATION,
    DivergenceKind,
    PlanDelta,
    detect_divergences,
    replan,
)
from app.services.recovery_contract import (
    Confidence,
    RecoveryBand,
    TrainingState,
    ZoneRecoveryEstimate,
)
from app.services.training_preferences import TrainingPreferencesData
from app.services.weekly_planner import build_weekly_plan

ZONE_QUADS = "quads"
ZONE_PECS = "pecs"


def _plan(cadence=3, **kwargs):
    return build_weekly_plan(
        TrainingPreferencesData(sessions_per_week=cadence, **kwargs))


def _estimate(zone, band, confidence=Confidence.MEDIUM):
    return ZoneRecoveryEstimate(zone_code=zone, band=band, confidence=confidence)


def _state(*estimates):
    return TrainingState(zone_recovery=tuple(estimates))


def _fatigued(zone, confidence=Confidence.MEDIUM):
    return _estimate(zone, RecoveryBand.LIKELY_FATIGUED, confidence)


def _recovered(zone):
    """Preuve FAVORABLE — la seule qui ne doit jamais rien pouvoir ajouter."""
    return _estimate(zone, RecoveryBand.LIKELY_AVAILABLE, Confidence.MEDIUM)


def _zone(plan, code):
    return next(z for z in plan.zone_coverage if z.zone_code == code)


# ── Le delta parle en séries ─────────────────────────────────────────────────


def test_a_delta_reports_the_sets_it_removes():
    plan = _plan()
    quads_before = _zone(plan, ZONE_QUADS).planned_sets
    assert quads_before > 0, "fixture inutile si la zone ne porte aucune série"

    result = replan(plan, completed_sessions=1,
                    training_state=_state(_fatigued(ZONE_QUADS)))
    delta = next(d for d in result.deltas if d.zone_code == ZONE_QUADS)
    assert delta.sets_before == quads_before
    assert delta.sets_after == 0
    assert delta.sets_removed == quads_before


def test_slot_movement_stays_separately_observable():
    """Forme et charge sont deux informations distinctes."""
    plan = _plan()
    result = replan(plan, completed_sessions=1,
                    training_state=_state(_fatigued(ZONE_QUADS)))
    delta = next(d for d in result.deltas if d.zone_code == ZONE_QUADS)
    assert delta.slots_before == _zone(plan, ZONE_QUADS).planned_slots
    assert delta.slots_after == 0
    # …et la charge ne se déduit PAS du nombre de créneaux.
    assert delta.sets_before != delta.slots_before


def test_the_total_of_removed_sets_is_exposed():
    plan = _plan()
    result = replan(plan, completed_sessions=1,
                    training_state=_state(_fatigued(ZONE_QUADS),
                                          _fatigued(ZONE_PECS)))
    expected = sum(
        _zone(plan, z).planned_sets for z in (ZONE_QUADS, ZONE_PECS))
    assert result.sets_removed_total == expected


# ── L'asymétrie, désormais en séries ─────────────────────────────────────────


def test_no_delta_can_ever_add_a_set():
    plan = _plan()
    result = replan(plan, completed_sessions=1, constraint_changed=True,
                    training_state=_state(_fatigued(ZONE_QUADS),
                                          _recovered(ZONE_PECS)))
    for delta in result.deltas:
        assert delta.sets_after <= delta.sets_before
        assert delta.is_reduction


def test_good_readiness_alone_triggers_no_replan_and_no_set():
    plan = _plan()
    result = replan(plan, completed_sessions=len(plan.sessions),
                    training_state=_state(_recovered(ZONE_QUADS),
                                          _recovered(ZONE_PECS)))
    assert result.replanned is False
    assert result.deltas == ()
    assert result.sets_removed_total == 0


def test_a_recovered_zone_produces_no_delta_even_alongside_a_fatigued_one():
    plan = _plan()
    result = replan(plan, completed_sessions=1,
                    training_state=_state(_fatigued(ZONE_QUADS),
                                          _recovered(ZONE_PECS)))
    touched = {d.zone_code for d in result.deltas}
    assert ZONE_QUADS in touched
    assert ZONE_PECS not in touched


def test_null_confidence_fabricates_no_set_reduction():
    """Absence de preuve n'est pas preuve de contrainte — règle P0.4 telle quelle."""
    plan = _plan()
    result = replan(plan, completed_sessions=len(plan.sessions),
                    training_state=_state(
                        _fatigued(ZONE_QUADS, Confidence.NONE)))
    assert result.deltas == ()
    assert result.sets_removed_total == 0


def test_is_reduction_rejects_a_set_increase_even_if_slots_shrink():
    """La garde couvre les DEUX axes : un créneau en moins peut cacher des séries en plus."""
    grown = PlanDelta(
        zone_code=ZONE_QUADS, slots_before=2, slots_after=1,
        sets_before=4, sets_after=8, reason="fixture",
    )
    assert not grown.is_reduction
    assert grown.sets_removed == 0


def test_is_reduction_rejects_a_slot_increase_even_if_sets_shrink():
    grown = PlanDelta(
        zone_code=ZONE_QUADS, slots_before=1, slots_after=3,
        sets_before=8, sets_after=4, reason="fixture",
    )
    assert not grown.is_reduction


# ── Séance écourtée : la limite est tenue, pas contournée ────────────────────


def test_a_shortened_session_diverges_but_removes_no_set():
    """Sans identité plan↔séance, réduire reviendrait à deviner ce qui a été fait."""
    plan = _plan()
    result = replan(plan, completed_sessions=len(plan.sessions),
                    shortened_sessions=1)
    kinds = {d.kind for d in result.divergences}
    assert DivergenceKind.SHORTENED_SESSION in kinds
    assert result.replanned is True
    assert result.sets_removed_total == 0


def test_the_shortened_session_limitation_is_stated_in_the_basis():
    plan = _plan()
    result = replan(plan, completed_sessions=len(plan.sessions),
                    shortened_sessions=1)
    assert any("identité plan↔séance" in line for line in result.basis)


def test_the_limitation_is_recorded_in_code_not_only_in_a_report():
    guard = PERFORMED_SET_IDENTITY_LIMITATION.lower()
    assert "no plan-to-session identity" in guard
    assert "never reduces" in guard


def test_the_module_does_not_pretend_to_match_performed_sets():
    """Garde structurelle : aucun appariement séance↔créneau n'est tenté ici."""
    from app.services import adaptive_replan as mod
    from tests.helpers import module_code_only

    code = module_code_only(mod).lower()
    for banned in ("performed_sets", "actual_sets", "sessionexercise", "setlog"):
        assert banned not in code, (
            f"un appariement plan↔séance semble avoir été tenté ({banned!r})"
        )


# ── Non-régressions du contrat de la tranche précédente ──────────────────────


def test_structural_gaps_still_survive_the_replan():
    plan = _plan()
    result = replan(plan, completed_sessions=1)
    assert "core" in result.unmet_budget_after


def test_a_replan_still_produces_a_new_version_not_a_mutation():
    plan = _plan()
    result = replan(plan, completed_sessions=1,
                    training_state=_state(_fatigued(ZONE_QUADS)))
    assert result.previous_fingerprint == plan.fingerprint
    assert result.new_fingerprint != plan.fingerprint
    # Le plan d'origine est intact.
    assert _zone(plan, ZONE_QUADS).planned_sets > 0


@pytest.mark.parametrize("cadence", [2, 4, 6])
def test_replan_stays_deterministic_across_cadences(cadence):
    plan = _plan(cadence)
    first = replan(plan, completed_sessions=1,
                   training_state=_state(_fatigued(ZONE_QUADS)))
    second = replan(plan, completed_sessions=1,
                    training_state=_state(_fatigued(ZONE_QUADS)))
    assert first.new_fingerprint == second.new_fingerprint
    assert first.sets_removed_total == second.sets_removed_total


def test_no_divergence_still_means_no_replan():
    plan = _plan()
    result = replan(plan, completed_sessions=len(plan.sessions))
    assert result.replanned is False
    assert result.deltas == ()


def test_detect_divergences_is_unchanged_in_shape():
    """La détection n'a pas bougé : seule la comptabilité du delta change."""
    plan = _plan()
    divergences = detect_divergences(plan, completed_sessions=1)
    assert divergences
    assert all(isinstance(d.kind, DivergenceKind) for d in divergences)
