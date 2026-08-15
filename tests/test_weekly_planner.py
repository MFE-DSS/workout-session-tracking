"""Sb_WEEKLY_PLANNER_01 — plan hebdomadaire déterministe.

Classes d'équivalence et invariants, pas une permutation par cas.

Le résultat central de cette tranche n'est pas qu'un plan sorte : c'est que les
**manques sortent aussi**, nommés, plutôt qu'un exercice plausible inventé pour
les combler.
"""
from __future__ import annotations

import inspect

import pytest

from app.services.muscle_mapping import RADAR_AXES, ZONE_VOLUME_TARGET
from app.services.training_preferences import TrainingPreferencesData
from app.services.weekly_planner import (
    UNMET_NO_CADENCE,
    UNMET_NO_INTENT,
    build_weekly_plan,
    priority_keys_for_zones,
    zones_servable_as_primary,
)
from tests.helpers import module_code_only

AXIS_LOWER = "lower"
AXIS_BACK_WIDTH = "back_width"
AXIS_ARMS = "arms"
FAM_BARBELL = "barbell"


def _plan(**kwargs):
    return build_weekly_plan(TrainingPreferencesData(**kwargs))


# ─────────────────── cadence déclarée ───────────────────


class TestCadence:
    @pytest.mark.parametrize("cadence", [2, 3, 5])
    def test_the_declared_cadence_is_obeyed(self, cadence):
        assert len(_plan(sessions_per_week=cadence).sessions) == cadence

    @pytest.mark.parametrize("cadence", [2, 3, 5])
    def test_every_slot_lands_in_exactly_one_session(self, cadence):
        plan = _plan(sessions_per_week=cadence)
        ids = [s.slot_id for sess in plan.sessions for s in sess.slots]
        assert len(ids) == len(set(ids))

    def test_sessions_are_indexed_from_one(self):
        plan = _plan(sessions_per_week=3)
        assert [s.index for s in plan.sessions] == [1, 2, 3]

    def test_an_undeclared_cadence_fabricates_no_session(self):
        """Inventer « 3 » transformerait une absence en fait utilisateur."""
        assert _plan().sessions == ()

    def test_an_undeclared_cadence_is_an_explicit_constraint(self):
        assert UNMET_NO_CADENCE in _plan().unmet_constraints

    def test_the_slot_total_does_not_depend_on_cadence(self):
        """La cadence répartit ; elle ne crée ni ne retire de travail."""
        two = sum(len(s.slots) for s in _plan(sessions_per_week=2).sessions)
        five = sum(len(s.slots) for s in _plan(sessions_per_week=5).sessions)
        assert two == five


# ─────────────────── les manques sont dits, pas comblés ───────────────────


class TestFeasibilityGaps:
    def test_the_intent_registry_covers_only_part_of_the_taxonomy(self):
        """Constat d'audit épinglé : le registre est fermé et incomplet."""
        assert zones_servable_as_primary() < set(ZONE_VOLUME_TARGET)

    @pytest.mark.parametrize("zone", ["lats", "core", "biceps", "triceps"])
    def test_an_unservable_zone_is_reported_not_filled(self, zone):
        plan = _plan(sessions_per_week=3)
        entry = next(z for z in plan.zone_coverage if z.zone_code == zone)
        assert entry.unmet_reason == UNMET_NO_INTENT

    def test_an_unservable_zone_receives_no_slot(self):
        plan = _plan(sessions_per_week=3)
        planned = {s.zone_code for sess in plan.sessions for s in sess.slots}
        assert "lats" not in planned

    def test_a_declared_but_unservable_axis_is_surfaced(self):
        """L'utilisateur peut déclarer une priorité non programmable."""
        plan = _plan(sessions_per_week=3, focus_priorities=(AXIS_BACK_WIDTH,))
        label = RADAR_AXES[AXIS_BACK_WIDTH]["label"]
        assert any(label in c for c in plan.unmet_constraints)

    def test_a_servable_axis_raises_no_constraint(self):
        plan = _plan(sessions_per_week=3, focus_priorities=(AXIS_LOWER,))
        labels = RADAR_AXES[AXIS_LOWER]["label"]
        assert not any(labels in c for c in plan.unmet_constraints)

    def test_the_plan_states_it_is_not_feasible(self):
        assert _plan(sessions_per_week=3).is_feasible is False

    def test_every_canonical_zone_appears_in_coverage(self):
        plan = _plan(sessions_per_week=3)
        assert {z.zone_code for z in plan.zone_coverage} == set(ZONE_VOLUME_TARGET)

    def test_coverage_carries_the_budget_band(self):
        plan = _plan(sessions_per_week=3)
        quads = next(z for z in plan.zone_coverage if z.zone_code == "quads")
        assert (quads.planning_low_sets, quads.planning_high_sets) == (14, 18)


# ─────────────────── aucune fabrication ───────────────────


class TestNoFabrication:
    def test_the_planner_builds_no_exercise_ranker(self):
        """La sélection appartient au générateur fermé."""
        import app.services.weekly_planner as mod

        source = module_code_only(mod)
        for banned in ("compute_proximity", "score_candidate", "sorted(candidates"):
            assert banned not in source

    def test_the_planner_reuses_the_closed_generator(self):
        import app.services.weekly_planner as mod

        assert "generate_program" in module_code_only(mod)

    def test_no_new_axis_to_intent_mapping_is_written(self):
        """Les clés de priorité sont DÉRIVÉES des tables existantes."""
        import app.services.weekly_planner as mod

        source = module_code_only(mod)
        assert "lateral_delts" not in source

    def test_the_derivation_follows_the_existing_registry(self):
        keys = priority_keys_for_zones(frozenset({"quads"}))
        assert "quads_maintenance" in keys

    def test_an_unknown_zone_derives_no_priority_key(self):
        assert priority_keys_for_zones(frozenset({"not_a_zone"})) == ()

    def test_a_slot_without_a_candidate_keeps_a_null_exercise(self):
        """Un créneau sans exercice reste vide plutôt que rempli."""
        plan = build_weekly_plan(
            TrainingPreferencesData(sessions_per_week=2), pool={})
        names = [s.exercise_name for sess in plan.sessions for s in sess.slots]
        assert all(n is None for n in names)


# ─────────────────── équipement ───────────────────


class TestEquipment:
    def test_declared_equipment_is_carried(self):
        plan = _plan(sessions_per_week=3, available_equipment=(FAM_BARBELL,))
        assert plan.equipment_declared == (FAM_BARBELL,)

    def test_undeclared_equipment_applies_no_constraint(self):
        plan = _plan(sessions_per_week=3)
        assert "aucune contrainte" in " ".join(plan.basis)

    def test_an_empty_equipment_declaration_is_not_undeclared(self):
        """`()` = rien de disponible ; `None` = non renseigné."""
        empty = _plan(sessions_per_week=3, available_equipment=())
        undeclared = _plan(sessions_per_week=3)
        assert empty.equipment_declared != undeclared.equipment_declared

    def test_a_constrained_plan_never_invents_an_exercise(self):
        plan = _plan(sessions_per_week=3, available_equipment=())
        names = [
            s.exercise_name for sess in plan.sessions for s in sess.slots
            if s.exercise_name is not None
        ]
        assert names == []


# ─────────────────── déterminisme ───────────────────


class TestDeterminism:
    def test_two_plans_are_identical(self):
        first = _plan(sessions_per_week=3, focus_priorities=(AXIS_LOWER,))
        second = _plan(sessions_per_week=3, focus_priorities=(AXIS_LOWER,))
        assert first == second

    def test_the_fingerprint_is_stable(self):
        first = _plan(sessions_per_week=3)
        second = _plan(sessions_per_week=3)
        assert first.fingerprint == second.fingerprint

    def test_a_different_cadence_changes_the_fingerprint(self):
        assert _plan(sessions_per_week=2).fingerprint != _plan(
            sessions_per_week=4).fingerprint

    def test_the_planner_reads_no_clock(self):
        import app.services.weekly_planner as mod

        assert "datetime" not in module_code_only(mod)

    def test_the_planner_uses_no_randomness(self):
        import app.services.weekly_planner as mod

        assert "random" not in module_code_only(mod)

    def test_the_planner_persists_nothing(self):
        import app.services.weekly_planner as mod

        source = module_code_only(mod)
        for write in ("db.add", "db.commit", "__tablename__"):
            assert write not in source


# ─────────────────── isolation ───────────────────


class TestIsolation:
    def test_the_recommendation_engine_never_reads_the_planner(self):
        from app.services import recommendation

        assert "weekly_planner" not in inspect.getsource(recommendation)

    def test_the_planner_never_reads_the_recommendation(self):
        import app.services.weekly_planner as mod

        assert "recommendation" not in module_code_only(mod)

    def test_no_published_program_is_mutated(self):
        import app.services.weekly_planner as mod

        source = module_code_only(mod)
        for banned in ("UserProgram", "publish", "status ="):
            assert banned not in source

    def test_failure_is_not_required(self):
        import app.services.weekly_planner as mod

        source = inspect.getsource(mod).lower()
        for banned in ("échec musculaire requis", "to failure"):
            assert banned not in source

    def test_frequency_is_never_treated_as_quality(self):
        import app.services.weekly_planner as mod

        source = module_code_only(mod)
        for banned in ("* sessions_per_week", "frequency_bonus"):
            assert banned not in source


# ─────────────────── consommateur Home + parité ───────────────────


class TestHomeConsumer:
    def test_the_home_payload_carries_the_weekly_plan(self, client):
        from app.database import SessionLocal
        from app.models.user import User
        from app.services.home import build_home_payload

        with SessionLocal() as db:
            payload = build_home_payload(db, db.query(User).first())
        assert "weekly_plan" in payload

    def test_an_undeclared_cadence_hides_the_tile(self, client):
        from app.database import SessionLocal
        from app.models.user import User
        from app.services.home import build_home_payload

        with SessionLocal() as db:
            payload = build_home_payload(db, db.query(User).first())
        assert payload["weekly_plan"]["available"] is False

    def test_a_declared_cadence_shows_the_tile(self, client):
        from app.database import SessionLocal
        from app.models.user import User
        from app.services.home import build_home_payload
        from app.services.training_preferences import save_training_preferences
        from tests.helpers import get_test_user_id

        uid = get_test_user_id()
        with SessionLocal() as db:
            save_training_preferences(db, uid, sessions_per_week=3)
        with SessionLocal() as db:
            payload = build_home_payload(db, db.get(User, uid))
        assert payload["weekly_plan"]["planned_sessions"] == 3

    def test_the_tile_renders_on_home(self, client):
        import html

        from app.database import SessionLocal
        from app.services.training_preferences import save_training_preferences
        from tests.helpers import get_test_user_id

        with SessionLocal() as db:
            save_training_preferences(db, get_test_user_id(), sessions_per_week=3)
        page = html.unescape(client.get("/").text)
        assert "Semaine planifiée" in page

    def test_only_one_unmet_constraint_is_surfaced(self, client):
        from app.database import SessionLocal
        from app.models.user import User
        from app.services.home import build_home_payload
        from app.services.training_preferences import save_training_preferences
        from tests.helpers import get_test_user_id

        uid = get_test_user_id()
        with SessionLocal() as db:
            save_training_preferences(
                db, uid, sessions_per_week=3,
                focus_priorities=[AXIS_BACK_WIDTH, AXIS_ARMS])
        with SessionLocal() as db:
            tile = build_home_payload(db, db.get(User, uid))["weekly_plan"]
        assert isinstance(tile["unmet_constraint"], str)

    def test_the_recommendation_is_unchanged_by_the_planner(self, client, monkeypatch):
        """Parité prouvée : la tuile désactivée ne déplace pas `today`."""
        from app.database import SessionLocal
        from app.models.user import User
        from app.services import home as home_module
        from app.services.home import build_home_payload
        from app.services.training_preferences import save_training_preferences
        from tests.helpers import get_test_user_id

        uid = get_test_user_id()
        with SessionLocal() as db:
            save_training_preferences(db, uid, sessions_per_week=4)
        with SessionLocal() as db:
            after = build_home_payload(db, db.get(User, uid))

        def boom(*_a, **_k):
            raise RuntimeError("planner down")

        monkeypatch.setattr(home_module, "_build_weekly_plan", boom)
        with SessionLocal() as db:
            before = build_home_payload(db, db.get(User, uid))
        assert after["today"] == before["today"]

    def test_a_planner_failure_keeps_home_up(self, client, monkeypatch):
        from app.services import home as home_module

        def boom(*_a, **_k):
            raise RuntimeError("planner down")

        monkeypatch.setattr(home_module, "_build_weekly_plan", boom)
        assert client.get("/").status_code == 200

    def test_a_planner_failure_marks_the_tile_unavailable(self, client, monkeypatch):
        from app.database import SessionLocal
        from app.models.user import User
        from app.services import home as home_module
        from app.services.home import build_home_payload

        def boom(*_a, **_k):
            raise RuntimeError("planner down")

        monkeypatch.setattr(home_module, "_build_weekly_plan", boom)
        with SessionLocal() as db:
            payload = build_home_payload(db, db.query(User).first())
        assert payload["weekly_plan"]["available"] is False
