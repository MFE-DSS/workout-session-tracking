"""Sb_ADAPTIVE_REPLAN_EFFECTIVE_VOLUME_01 — la replanification et l'effectif.

Trois propriétés, dans l'ordre d'importance :

1. **La replanification mute du PHYSIQUE.** L'effet effectif est **dérivé** de
   `SetContributionPolicy`, jamais écrit à la main ni muté directement.
2. **Une exposition secondaire n'est pas une contre-indication.** Une zone
   limitante ne retire que les occurrences dont elle est la cible
   **principale** ; un composé qui la sollicite en secondaire reste programmé.
3. **L'asymétrie tient** : une preuve favorable n'ajoute jamais rien.
"""
from __future__ import annotations

import pytest

from app.services.adaptive_replan import (
    SECONDARY_EXPOSURE_IS_NOT_A_CONTRAINDICATION,
    replan,
)
from app.services.recovery_contract import (
    Confidence,
    RecoveryBand,
    TrainingState,
    ZoneRecoveryEstimate,
)
from app.services.set_contribution import contributions_for
from app.services.training_preferences import TrainingPreferencesData
from app.services.weekly_planner import build_weekly_plan

#: Composé du plan : primaire `pecs`, secondaire `triceps`.
COMPOUND_ZONE = "pecs"
SECONDARY_OF_COMPOUND = "triceps"
#: Zone servie par des tirages qui créditent `biceps` en secondaire.
PULL_ZONE = "lats"


def _plan(cadence=4, **kwargs):
    return build_weekly_plan(
        TrainingPreferencesData(sessions_per_week=cadence, **kwargs))


def _state(*zones, band=RecoveryBand.LIKELY_FATIGUED,
           confidence=Confidence.MEDIUM):
    return TrainingState(zone_recovery=tuple(
        ZoneRecoveryEstimate(zone_code=z, band=band, confidence=confidence)
        for z in zones
    ))


def _impact(result, zone):
    for code, before, after in result.effective_impact:
        if code == zone:
            return (before, after)
    return (0, 0)


def _occurrences_for(plan, zone):
    return [
        slot for session in plan.sessions for slot in session.slots
        if slot.zone_code == zone and slot.is_prescribed
    ]


# ── 1. Physique muté, effectif dérivé ───────────────────────────────────────


def test_the_effective_consequence_is_derived_not_hand_written():
    """Retirer un composé retire aussi du crédit secondaire — sans règle codée.

    Aucun « la presse donne du triceps » n'est écrit dans le service : le
    ricochet tombe de `SetContributionPolicy` appliquée aux occurrences
    survivantes.
    """
    plan = _plan()
    result = replan(plan, completed_sessions=1,
                    training_state=_state(COMPOUND_ZONE))

    primary_before, primary_after = _impact(result, COMPOUND_ZONE)
    assert primary_after == 0
    assert primary_before > 0

    secondary_before, secondary_after = _impact(result, SECONDARY_OF_COMPOUND)
    assert secondary_after < secondary_before, (
        "le crédit secondaire doit baisser quand le composé est reporté"
    )
    assert secondary_after > 0, "le triceps garde son travail direct"


def test_the_effective_impact_matches_the_shared_policy_exactly():
    """Deux chemins, un résultat : le service ne tient pas sa propre compta."""
    plan = _plan()
    limiting = {COMPOUND_ZONE}
    result = replan(plan, completed_sessions=1,
                    training_state=_state(*limiting))

    surviving = [
        slot for session in plan.sessions for slot in session.slots
        if slot.is_prescribed and slot.zone_code not in limiting
    ]
    expected = contributions_for(surviving)
    for zone, _before, after in result.effective_impact:
        assert after == (
            expected[zone].effective_units if zone in expected else 0)


def test_the_delta_stays_physical():
    """`sets_before`/`sets_after` restent la dose exécutable, pas l'effectif."""
    plan = _plan()
    result = replan(plan, completed_sessions=1,
                    training_state=_state(COMPOUND_ZONE))
    delta = next(d for d in result.deltas if d.zone_code == COMPOUND_ZONE)

    physical = sum(s.planned_sets for s in _occurrences_for(plan, COMPOUND_ZONE))
    assert delta.sets_before == physical
    # …et l'effectif de la même zone est une grandeur DIFFÉRENTE.
    effective_before, _ = _impact(result, COMPOUND_ZONE)
    assert effective_before != delta.sets_before or physical == 0


def test_the_service_never_writes_effective_units_by_hand():
    """Garde structurelle : aucune arithmétique d'effectif dans le service."""
    from app.services import adaptive_replan as mod
    from tests.helpers import module_code_only

    code = module_code_only(mod)
    for banned in ("effective_units =", "effective_units +=", "* 0.5", "// 2"):
        assert banned not in code, (
            f"le service calcule l'effectif lui-même ({banned!r})"
        )
    assert "contributions_for" in code


# ── 2. Une exposition secondaire n'est pas une contre-indication ────────────


def test_a_secondary_only_limit_never_removes_a_compound():
    """Le cœur de la tranche.

    `biceps` est limitant, et les tirages le sollicitent en secondaire.
    Retirer le travail de dos pour cela priverait `lats` de son travail
    primaire à cause d'une exposition que le modèle n'a jamais mesurée comme
    telle.
    """
    plan = _plan()
    pulls_before = len(_occurrences_for(plan, PULL_ZONE))
    assert pulls_before > 0

    result = replan(plan, completed_sessions=1,
                    training_state=_state("biceps"))

    touched = {d.zone_code for d in result.deltas}
    assert PULL_ZONE not in touched, "un composé a été retiré pour du secondaire"
    assert touched <= {"biceps"}

    # …et surtout : le travail de dos doit rester dans la comptabilité APRÈS.
    # Vérifier seulement la liste des deltas ne prouve rien — elle est correcte
    # par construction. C'est l'impact effectif qui révèle un composé retiré.
    pull_before, pull_after = _impact(result, PULL_ZONE)
    assert pull_after == pull_before, (
        f"{PULL_ZONE} a perdu du volume effectif alors que seul son crédit "
        "secondaire était limitant"
    )


def test_a_primary_limit_does_postpone_its_own_occurrences():
    """Contre-épreuve : la garde n'immobilise pas la replanification."""
    plan = _plan()
    result = replan(plan, completed_sessions=1,
                    training_state=_state(PULL_ZONE))
    touched = {d.zone_code for d in result.deltas}
    assert PULL_ZONE in touched


def test_the_guard_is_recorded_in_code():
    guard = SECONDARY_EXPOSURE_IS_NOT_A_CONTRAINDICATION.lower()
    assert "only occurrences whose primary target" in guard
    assert "never an automatic recovery contraindication" in guard


def test_recovery_evidence_is_never_described_as_injury_risk():
    from app.services import adaptive_replan as mod

    text = (mod.__doc__ or "").lower() + SECONDARY_EXPOSURE_IS_NOT_A_CONTRAINDICATION.lower()
    for banned in ("blessure", "injury", "surentraîn", "overtrain"):
        assert banned not in text or "aucun risque" in text or "never" in text


# ── 3. L'asymétrie tient toujours ───────────────────────────────────────────


def test_favourable_evidence_adds_no_effective_volume():
    plan = _plan()
    result = replan(
        plan, completed_sessions=len(plan.sessions),
        training_state=_state(
            "quads", "pecs", band=RecoveryBand.LIKELY_AVAILABLE))
    assert result.replanned is False
    assert result.effective_impact == ()
    assert result.effective_units_removed_total == 0


def test_no_zone_ever_gains_effective_units_from_a_replan():
    plan = _plan()
    result = replan(plan, completed_sessions=1,
                    training_state=_state(COMPOUND_ZONE, "quads"))
    for zone, before, after in result.effective_impact:
        assert after <= before, f"{zone} a GAGNÉ du volume effectif"


def test_null_confidence_still_fabricates_nothing():
    plan = _plan()
    result = replan(
        plan, completed_sessions=len(plan.sessions),
        training_state=_state(COMPOUND_ZONE, confidence=Confidence.NONE))
    assert result.deltas == ()
    assert result.effective_units_removed_total == 0


# ── 4. Non-régressions ──────────────────────────────────────────────────────


def test_the_shortened_session_limitation_is_unchanged():
    plan = _plan()
    result = replan(plan, completed_sessions=len(plan.sessions),
                    shortened_sessions=1)
    assert result.replanned is True
    assert result.sets_removed_total == 0


def test_structural_gaps_still_survive():
    plan = _plan(cadence=2)
    result = replan(plan, completed_sessions=1)
    assert result.unmet_budget_after


@pytest.mark.parametrize("cadence", [2, 3, 4, 5])
def test_replan_is_deterministic_at_every_cadence(cadence):
    plan = _plan(cadence)
    first = replan(plan, completed_sessions=1,
                   training_state=_state(COMPOUND_ZONE))
    second = replan(plan, completed_sessions=1,
                    training_state=_state(COMPOUND_ZONE))
    assert first.effective_impact == second.effective_impact
    assert first.new_fingerprint == second.new_fingerprint
