"""Sb_ADAPTIVE_REPLAN_01 — replanification sur divergence réelle.

Le résultat central : **une preuve favorable ne peut rien ajouter**. Tout le
reste découle de cette asymétrie.
"""
from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.services.adaptive_replan import (
    DivergenceKind,
    detect_divergences,
    replan,
)
from app.services.recovery_contract import (
    Confidence,
    ReadinessSignal,
    RecoveryBand,
    Sufficiency,
    TrainingState,
    ZoneRecoveryEstimate,
)
from app.services.training_preferences import TrainingPreferencesData
from app.services.weekly_planner import build_weekly_plan
from tests.helpers import module_code_only

NOW = datetime(2026, 8, 15, 9, 0, tzinfo=UTC)
ZONE_QUADS = "quads"


def _plan(cadence: int = 3):
    return build_weekly_plan(TrainingPreferencesData(sessions_per_week=cadence))


def _state(*estimates: ZoneRecoveryEstimate, readiness=None) -> TrainingState:
    return TrainingState(
        computed_at=NOW,
        zone_recovery=estimates,
        readiness=readiness or ReadinessSignal(),
    )


def _fatigued(zone: str) -> ZoneRecoveryEstimate:
    return ZoneRecoveryEstimate(
        zone_code=zone, estimate=0.2, band=RecoveryBand.LIKELY_FATIGUED,
        confidence=Confidence.MEDIUM, staleness=Sufficiency.SUFFICIENT,
    )


# ─────────────────── pas de divergence, pas de replanification ───────────────────


class TestNoDivergence:
    def test_a_fully_completed_week_does_not_replan(self):
        plan = _plan(3)
        assert replan(plan, completed_sessions=3).replanned is False

    def test_no_divergence_is_stated_not_silent(self):
        result = replan(_plan(3), completed_sessions=3)
        assert "aucune divergence" in " ".join(result.basis)

    def test_no_divergence_keeps_the_same_fingerprint(self):
        plan = _plan(3)
        result = replan(plan, completed_sessions=3)
        assert result.new_fingerprint == plan.fingerprint

    def test_no_divergence_produces_no_delta(self):
        assert replan(_plan(3), completed_sessions=3).deltas == ()


# ─────────────────── divergences réelles ───────────────────


class TestDivergenceDetection:
    def test_a_missed_session_is_detected(self):
        kinds = [d.kind for d in detect_divergences(_plan(3), completed_sessions=1)]
        assert DivergenceKind.MISSED_SESSION in kinds

    def test_a_shortened_session_is_detected(self):
        kinds = [
            d.kind for d in detect_divergences(
                _plan(3), completed_sessions=3, shortened_sessions=1)
        ]
        assert DivergenceKind.SHORTENED_SESSION in kinds

    def test_only_unperformed_work_is_reconsidered(self):
        divergences = detect_divergences(
            _plan(3), completed_sessions=3, shortened_sessions=1)
        short = next(
            d for d in divergences if d.kind is DivergenceKind.SHORTENED_SESSION)
        assert "non effectué" in short.detail

    def test_a_declared_constraint_change_is_detected(self):
        kinds = [
            d.kind for d in detect_divergences(
                _plan(3), completed_sessions=3, constraint_changed=True)
        ]
        assert DivergenceKind.CONSTRAINT_CHANGE in kinds

    def test_limiting_recovery_is_detected(self):
        kinds = [
            d.kind for d in detect_divergences(
                _plan(3), completed_sessions=3, training_state=_state(_fatigued(ZONE_QUADS)))
        ]
        assert DivergenceKind.LIMITING_RECOVERY in kinds

    def test_a_missed_session_triggers_a_replan(self):
        assert replan(_plan(3), completed_sessions=1).replanned is True


# ─────────────────── l'asymétrie ───────────────────


class TestAsymmetry:
    def test_limiting_recovery_may_postpone_work(self):
        result = replan(
            _plan(3), completed_sessions=3, training_state=_state(_fatigued(ZONE_QUADS)))
        assert any(d.zone_code == ZONE_QUADS for d in result.deltas)

    def test_postponed_work_is_reduced_never_increased(self):
        result = replan(
            _plan(3), completed_sessions=3, training_state=_state(_fatigued(ZONE_QUADS)))
        assert all(d.is_reduction for d in result.deltas)

    def test_work_is_postponed_not_declared_useless(self):
        result = replan(
            _plan(3), completed_sessions=3, training_state=_state(_fatigued(ZONE_QUADS)))
        assert "reporté" in result.deltas[0].reason

    def test_good_readiness_alone_triggers_no_replan(self):
        """Le cœur de la tranche : l'optimisme ne prescrit rien."""
        good = ReadinessSignal(
            overall=0.95, age_days=0, sufficiency=Sufficiency.SUFFICIENT)
        result = replan(_plan(3), completed_sessions=3,
                        training_state=_state(readiness=good))
        assert result.replanned is False

    def test_a_recovered_zone_adds_no_work(self):
        recovered = ZoneRecoveryEstimate(
            zone_code=ZONE_QUADS, estimate=1.0, band=RecoveryBand.LIKELY_AVAILABLE,
            confidence=Confidence.MEDIUM, staleness=Sufficiency.SUFFICIENT)
        result = replan(_plan(3), completed_sessions=3,
                        training_state=_state(recovered))
        assert result.deltas == ()

    def test_no_delta_ever_increases_slots(self):
        result = replan(
            _plan(3), completed_sessions=1,
            training_state=_state(_fatigued(ZONE_QUADS), _fatigued("pecs")))
        assert all(d.slots_after <= d.slots_before for d in result.deltas)

    def test_the_asymmetry_is_stated_in_the_basis(self):
        result = replan(_plan(3), completed_sessions=1)
        assert "ne peut que" in " ".join(result.basis)


# ─────────────────── absence de preuve ───────────────────


class TestInsufficientEvidence:
    def test_unknown_recovery_fabricates_no_constraint(self):
        """Une absence de preuve n'est pas une preuve de contrainte."""
        unknown = ZoneRecoveryEstimate(
            zone_code=ZONE_QUADS, band=RecoveryBand.UNKNOWN, confidence=Confidence.NONE)
        result = replan(_plan(3), completed_sessions=3,
                        training_state=_state(unknown))
        assert result.replanned is False

    def test_a_fatigued_band_without_confidence_constrains_nothing(self):
        """La garde de confiance doit porter, pas seulement la garde de bande.

        Une plantation a montré que retirer le filtre `Confidence.NONE` ne
        cassait aucun test : la bande `UNKNOWN` suffisait à protéger les autres
        cas. Ce cas-ci — bande limitante MAIS confiance nulle — est le seul qui
        rende cette garde load-bearing, et il manquait.
        """
        unproven = ZoneRecoveryEstimate(
            zone_code=ZONE_QUADS, band=RecoveryBand.LIKELY_FATIGUED,
            confidence=Confidence.NONE)
        result = replan(_plan(3), completed_sessions=3,
                        training_state=_state(unproven))
        assert result.replanned is False

    def test_a_new_user_state_triggers_no_replan(self):
        result = replan(_plan(3), completed_sessions=3, training_state=_state())
        assert result.replanned is False

    def test_no_training_state_at_all_is_tolerated(self):
        assert replan(_plan(3), completed_sessions=3).replanned is False


# ─────────────────── budget et versionnement ───────────────────


class TestBudgetAndVersioning:
    def test_a_structural_gap_survives_the_replan(self):
        """Replanifier ne comble pas un manque structurel."""
        plan = _plan(3)
        result = replan(plan, completed_sessions=1)
        assert "lats" in result.unmet_budget_after

    def test_an_impossible_redistribution_is_explicit(self):
        result = replan(_plan(3), completed_sessions=1,
                        training_state=_state(_fatigued(ZONE_QUADS)))
        assert ZONE_QUADS in result.unmet_budget_after

    def test_the_previous_fingerprint_is_retained(self):
        plan = _plan(3)
        result = replan(plan, completed_sessions=1)
        assert result.previous_fingerprint == plan.fingerprint

    def test_a_replan_produces_a_new_version(self):
        plan = _plan(3)
        result = replan(plan, completed_sessions=1)
        assert result.new_fingerprint != plan.fingerprint

    def test_the_divergence_is_retained_with_the_delta(self):
        result = replan(_plan(3), completed_sessions=1)
        assert result.divergences != ()

    def test_no_published_program_is_mutated(self):
        import app.services.adaptive_replan as mod

        source = module_code_only(mod)
        for banned in ("db.commit", "db.add", "publish", "UserProgram"):
            assert banned not in source


# ─────────────────── déterminisme et vocabulaire ───────────────────


class TestDeterminismAndLanguage:
    def test_the_same_state_yields_the_same_result(self):
        plan = _plan(3)
        state = _state(_fatigued(ZONE_QUADS))
        first = replan(plan, 1, training_state=state)
        second = replan(plan, 1, training_state=state)
        assert first == second

    def test_the_service_reads_no_clock(self):
        import app.services.adaptive_replan as mod

        assert "datetime.now" not in module_code_only(mod)

    def test_the_service_uses_no_randomness(self):
        import app.services.adaptive_replan as mod

        assert "random" not in module_code_only(mod)

    def test_no_second_recovery_model_is_read(self):
        """P0.4 est la seule source ; un second modèle divergerait."""
        import app.services.adaptive_replan as mod

        source = module_code_only(mod)
        for banned in ("behavioral", "compute_weighted_fatigue", "muscle_scoring"):
            assert banned not in source

    @pytest.mark.parametrize("banned", [
        "% de récupération", "risque de blessure", "heures de récupération",
        "surentraînement",
    ])
    def test_no_forbidden_recovery_claim_is_produced(self, banned):
        result = replan(_plan(3), completed_sessions=1,
                        training_state=_state(_fatigued(ZONE_QUADS)))
        text = " ".join(result.basis) + " ".join(d.reason for d in result.deltas)
        assert banned not in text

    def test_recovery_stays_an_estimate_in_the_wording(self):
        result = replan(_plan(3), completed_sessions=3,
                        training_state=_state(_fatigued(ZONE_QUADS)))
        assert "estimée" in result.deltas[0].reason
