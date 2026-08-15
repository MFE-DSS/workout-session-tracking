"""Sb_WEEKLY_VOLUME_BUDGET_01 — bandes de planification hebdomadaires.

Les tests visent des **classes d'équivalence** et des **invariants**, pas une
permutation par cas : la suite complète shardée est déjà la preuve d'intégration,
et gonfler le nombre de tests coûte désormais de la mémoire CI mesurable.

Trois familles :

1. **politique** — la bande est ce que la politique dit, et rien d'autre ;
2. **non-création de volume** — ni priorité ni cadence ne déplacent une borne ;
3. **isolation** — recommandation, P0.4 et comptage des séries inchangés.
"""
from __future__ import annotations

import inspect

import pytest

from app.services.muscle_mapping import RADAR_AXES, ZONE_VOLUME_TARGET
from app.services.training_preferences import TrainingPreferencesData
from app.services.weekly_volume_budget import (
    PLANNING_TOLERANCE_SETS,
    POLICY_VERSION,
    SOURCE_LEGACY_BASELINE,
    build_weekly_volume_budget,
    planning_band,
)
from tests.helpers import module_code_only

AXIS_ARMS = "arms"
AXIS_LOWER = "lower"


def _budget(**kwargs):
    return build_weekly_volume_budget(TrainingPreferencesData(**kwargs))


# ─────────────────── politique de bande ───────────────────


class TestPlanningBand:
    @pytest.mark.parametrize("baseline,expected", [
        (10, (8, 10, 12)),
        (18, (16, 18, 20)),
        (16, (14, 16, 18)),
    ])
    def test_the_band_is_the_policy_output(self, baseline, expected):
        """Sorties de POLITIQUE PRODUIT, jamais une affirmation scientifique."""
        assert planning_band(baseline) == expected

    def test_the_floor_never_goes_negative(self):
        assert planning_band(1)[0] == 0

    def test_every_canonical_zone_gets_a_band(self):
        budget = _budget()
        assert {z.zone_code for z in budget.zones} == set(ZONE_VOLUME_TARGET)

    def test_the_baseline_is_the_legacy_referential(self):
        budget = _budget()
        assert all(
            z.baseline_sets == ZONE_VOLUME_TARGET[z.zone_code] for z in budget.zones
        )

    def test_every_zone_names_its_source(self):
        budget = _budget()
        assert all(z.source == SOURCE_LEGACY_BASELINE for z in budget.zones)

    def test_every_zone_carries_the_policy_version(self):
        budget = _budget()
        assert all(z.policy_version == POLICY_VERSION for z in budget.zones)

    def test_every_zone_traces_to_a_basis(self):
        budget = _budget()
        assert all(z.basis for z in budget.zones)

    def test_the_band_is_symmetric_around_the_baseline(self):
        budget = _budget()
        for z in budget.zones:
            assert z.planning_high_sets - z.baseline_sets == PLANNING_TOLERANCE_SETS

    def test_changing_the_tolerance_moves_the_band(self, monkeypatch):
        """Le réglage vit dans la politique — ni dans `BodyZone`, ni dans le schéma."""
        import app.services.weekly_volume_budget as mod

        monkeypatch.setattr(mod, "PLANNING_TOLERANCE_SETS", 5)
        assert mod.planning_band(10) == (5, 10, 15)

    def test_changing_the_tolerance_touches_no_schema(self):
        import app.services.weekly_volume_budget as mod

        source = module_code_only(mod)
        for forbidden in ("BodyZone", "op.add_column", "migration"):
            assert forbidden not in source


# ─────────────────── le vocabulaire interdit ───────────────────


class TestForbiddenVocabulary:
    @pytest.mark.parametrize("banned", [
        "minimum_sets", "maximum_sets", "MEV", "MRV",
        "optimal_volume", "ideal_volume", "scientific_target",
    ])
    def test_the_contract_never_uses_a_claiming_name(self, banned):
        """Scanne le CODE : la docstring nomme ces termes pour les proscrire."""
        import app.services.weekly_volume_budget as mod

        assert banned not in module_code_only(mod)

    def test_the_field_names_are_the_planning_ones(self):
        zone = _budget().zones[0]
        for attr in ("planning_low_sets", "baseline_sets", "planning_high_sets"):
            assert hasattr(zone, attr)

    def test_the_tolerance_is_documented_as_a_product_decision(self):
        """Ici on scanne la DOCUMENTATION : c'est elle qui doit le dire."""
        import app.services.weekly_volume_budget as mod

        assert "pas un seuil biologique" in inspect.getsource(mod)

    def test_no_literature_is_invoked_to_justify_the_band(self):
        import app.services.weekly_volume_budget as mod

        source = inspect.getsource(mod).lower()
        for citation in ("acsm", "et al", "étude", "meta-analys"):
            assert citation not in source


# ─────────────────── les priorités ne créent pas de volume ───────────────────


class TestPrioritiesDoNotCreateVolume:
    def test_a_declared_priority_annotates_its_zones(self):
        budget = _budget(focus_priorities=(AXIS_ARMS,))
        arms_zones = RADAR_AXES[AXIS_ARMS]["zones"]
        assert all(budget.zone(z).priority_rank == 1 for z in arms_zones)

    def test_the_priority_names_the_user_as_its_source(self):
        budget = _budget(focus_priorities=(AXIS_ARMS,))
        zone = budget.zone(RADAR_AXES[AXIS_ARMS]["zones"][0])
        assert zone.priority_source == "USER_DECLARED"

    def test_the_priority_only_states_a_direction(self):
        budget = _budget(focus_priorities=(AXIS_ARMS,))
        zone = budget.zone(RADAR_AXES[AXIS_ARMS]["zones"][0])
        assert zone.preferred_direction == "HIGHER_WITHIN_BAND"

    def test_rank_order_follows_the_declared_order(self):
        budget = _budget(focus_priorities=(AXIS_LOWER, AXIS_ARMS))
        lower = budget.zone(RADAR_AXES[AXIS_LOWER]["zones"][0])
        arms = budget.zone(RADAR_AXES[AXIS_ARMS]["zones"][0])
        assert (lower.priority_rank, arms.priority_rank) == (1, 2)

    def test_a_priority_moves_no_bound(self):
        """L'invariant central de la tranche."""
        plain = _budget()
        prioritised = _budget(focus_priorities=(AXIS_ARMS, AXIS_LOWER))
        for a, b in zip(plain.zones, prioritised.zones, strict=True):
            assert (a.planning_low_sets, a.baseline_sets, a.planning_high_sets) == (
                b.planning_low_sets, b.baseline_sets, b.planning_high_sets)

    def test_the_weekly_total_is_unchanged_by_priorities(self):
        plain = sum(z.baseline_sets for z in _budget().zones)
        prioritised = sum(
            z.baseline_sets for z in _budget(focus_priorities=(AXIS_ARMS,)).zones)
        assert plain == prioritised

    def test_non_priority_zones_never_disappear(self):
        budget = _budget(focus_priorities=(AXIS_ARMS,))
        assert len(budget.zones) == len(ZONE_VOLUME_TARGET)

    def test_core_is_never_fabricated_into_an_axis(self):
        """`core` n'appartient à aucun axe radar — limite, pas oubli."""
        budget = _budget(focus_priorities=(AXIS_ARMS, AXIS_LOWER))
        assert budget.zone("core").priority_rank is None

    def test_an_axis_shared_by_two_priorities_keeps_the_better_rank(self):
        budget = _budget(focus_priorities=(AXIS_ARMS, AXIS_ARMS[::-1]))
        zone = budget.zone(RADAR_AXES[AXIS_ARMS]["zones"][0])
        assert zone.priority_rank == 1

    def test_no_numeric_rank_bonus_exists_in_v1(self):
        import app.services.weekly_volume_budget as mod

        source = module_code_only(mod)
        for formula in ("rank1", "+= 2", "+= 1", "rank_bonus"):
            assert formula not in source


# ─────────────────── la cadence ne change pas la dose ───────────────────


class TestCadenceIsContextOnly:
    @pytest.mark.parametrize("cadence", [1, 3, 6, None])
    def test_the_bands_are_identical_at_any_cadence(self, cadence):
        reference = _budget()
        candidate = _budget(sessions_per_week=cadence)
        for a, b in zip(reference.zones, candidate.zones, strict=True):
            assert (a.planning_low_sets, a.baseline_sets, a.planning_high_sets) == (
                b.planning_low_sets, b.baseline_sets, b.planning_high_sets)

    def test_the_declared_cadence_is_carried_as_context(self):
        assert _budget(sessions_per_week=4).sessions_per_week == 4

    def test_an_undeclared_cadence_stays_undeclared(self):
        assert _budget().sessions_per_week is None

    def test_no_frequency_multiplier_exists(self):
        import app.services.weekly_volume_budget as mod

        source = module_code_only(mod)
        for banned in ("* sessions_per_week", "/ sessions_per_week"):
            assert banned not in source


# ─────────────────── absence de déclaration ───────────────────


class TestUndeclared:
    def test_no_preference_still_yields_a_full_budget(self):
        assert len(_budget().zones) == len(ZONE_VOLUME_TARGET)

    def test_the_baseline_is_flagged_as_a_system_assumption(self):
        assert all(z.system_assumption for z in _budget().zones)

    def test_no_priority_metadata_when_nothing_is_declared(self):
        budget = _budget()
        assert all(z.priority_rank is None for z in budget.zones)

    def test_null_priorities_and_empty_priorities_are_distinguished(self):
        """`None` = non déclaré ; `()` = déclaré sans priorité particulière."""
        undeclared = " ".join(_budget(focus_priorities=None).basis)
        explicit = " ".join(_budget(focus_priorities=()).basis)
        assert undeclared != explicit

    def test_an_explicit_absence_of_priority_is_stated(self):
        basis = " ".join(_budget(focus_priorities=()).basis)
        assert "explicitement" in basis


# ─────────────────── déterminisme et pureté ───────────────────


class TestDeterminismAndPurity:
    def test_two_builds_are_identical(self):
        first = _budget(sessions_per_week=3, focus_priorities=(AXIS_ARMS,))
        second = _budget(sessions_per_week=3, focus_priorities=(AXIS_ARMS,))
        assert first == second

    def test_the_service_reads_no_clock(self):
        import app.services.weekly_volume_budget as mod

        assert "datetime" not in module_code_only(mod)

    def test_the_service_uses_no_randomness(self):
        import app.services.weekly_volume_budget as mod

        assert "random" not in module_code_only(mod)

    def test_the_result_is_immutable(self):
        from dataclasses import FrozenInstanceError

        zone = _budget().zones[0]
        with pytest.raises(FrozenInstanceError):
            zone.baseline_sets = 99

    def test_no_persistence_of_the_computed_budget(self):
        import app.services.weekly_volume_budget as mod

        source = module_code_only(mod)
        for write in ("db.add", "db.commit", "__tablename__"):
            assert write not in source


# ─────────────────── isolation ───────────────────


class TestIsolation:
    def test_the_recommendation_engine_never_reads_the_budget(self):
        from app.services import recommendation

        assert "weekly_volume_budget" not in inspect.getsource(recommendation)

    def test_the_behavioural_producer_never_reads_the_budget(self):
        from app.services import behavioral

        assert "weekly_volume_budget" not in inspect.getsource(behavioral)

    def test_no_fractional_set_accounting_was_introduced(self):
        """Changer l'unité de comptage est une migration sémantique."""
        import app.services.weekly_volume_budget as mod

        source = module_code_only(mod)
        for fractional in ("0.5", "* 0.", "indirect_weight"):
            assert fractional not in source

    def test_the_future_candidate_is_recorded_not_built(self):
        from app.services.weekly_volume_budget import SET_CONTRIBUTION_CANDIDATE

        assert SET_CONTRIBUTION_CANDIDATE["direct"] == 1

    def test_no_morphology_is_consumed_yet(self):
        import app.services.weekly_volume_budget as mod

        assert "morphology" not in module_code_only(mod)

    def test_no_recovery_model_is_consumed(self):
        import app.services.weekly_volume_budget as mod

        source = module_code_only(mod)
        for recovery in ("TrainingState", "ZoneRecoveryEstimate", "recovery_contract"):
            assert recovery not in source


# ─────────────────── bout en bout depuis la base ───────────────────


class TestAgainstPersistedPreferences:
    def test_a_user_without_preferences_gets_a_system_baseline(self, client):
        from app.database import SessionLocal
        from app.services.weekly_volume_budget import (
            build_weekly_volume_budget_for_user,
        )
        from tests.helpers import get_test_user_id

        with SessionLocal() as db:
            budget = build_weekly_volume_budget_for_user(db, get_test_user_id())
        assert all(z.system_assumption for z in budget.zones)

    def test_declared_priorities_reach_the_budget(self, client):
        from app.database import SessionLocal
        from app.services.training_preferences import save_training_preferences
        from app.services.weekly_volume_budget import (
            build_weekly_volume_budget_for_user,
        )
        from tests.helpers import get_test_user_id

        uid = get_test_user_id()
        with SessionLocal() as db:
            save_training_preferences(db, uid, focus_priorities=[AXIS_ARMS])
        with SessionLocal() as db:
            budget = build_weekly_volume_budget_for_user(db, uid)
        ranked = [z for z in budget.zones if z.priority_rank is not None]
        assert ranked != []

    def test_reading_the_budget_writes_nothing(self, client):
        from sqlalchemy import event

        from app.database import SessionLocal, engine
        from app.services.weekly_volume_budget import (
            build_weekly_volume_budget_for_user,
        )
        from tests.helpers import get_test_user_id

        seen: list[str] = []

        def listener(_c, _cur, statement, *_a, **_k):
            seen.append(statement)

        event.listen(engine, "before_cursor_execute", listener)
        try:
            with SessionLocal() as db:
                build_weekly_volume_budget_for_user(db, get_test_user_id())
        finally:
            event.remove(engine, "before_cursor_execute", listener)
        writes = [
            s for s in seen
            if s.strip().split()[0].upper() in {"INSERT", "UPDATE", "DELETE"}
        ]
        assert writes == []
