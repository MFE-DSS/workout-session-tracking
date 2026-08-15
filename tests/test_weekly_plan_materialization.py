"""Sb_WEEKLY_PLAN_MATERIALIZATION_01 — du plan au brouillon exécutable.

Ce que ces tests protègent :

1. **Aucun cycle de vie parallèle** — le brouillon passe par les services
   existants, sort en `draft`, et rien n'est publié ni lancé.
2. **Le statut dit la vérité** — un plan partiel est matérialisable mais n'est
   jamais annoncé comme complet.
3. **Les créneaux vides ne deviennent pas des exercices** — sans quoi
   `validate_draft` refuserait tout le brouillon pour une lacune déjà signalée.
4. **Le volume vient du PLAN**, jamais de la table de prescriptions du mapper
   morpho.
"""
from __future__ import annotations

import pytest

from app.services.training_preferences import TrainingPreferencesData
from app.services.weekly_plan_materialization import (
    BLOCKED_NO_CADENCE,
    SOURCE_REASON_PREFIX,
    MaterializationStatus,
    assess_materialization,
    plan_to_draft_tree,
)
from app.services.weekly_planner import build_weekly_plan


def _plan(**kwargs):
    return build_weekly_plan(TrainingPreferencesData(**kwargs))


# ── Verdict de matérialisation ───────────────────────────────────────────────


def test_a_plan_without_cadence_is_blocked_and_says_why():
    readiness = assess_materialization(_plan())
    assert readiness.status is MaterializationStatus.BLOCKED
    assert BLOCKED_NO_CADENCE in readiness.blocked_reasons
    assert readiness.can_materialize is False


def test_a_volume_shortfall_makes_the_plan_partial_not_ready():
    """Exécutable, mais pas complet — et le programme ne prétend pas l'être."""
    readiness = assess_materialization(_plan(sessions_per_week=4))
    assert readiness.status is MaterializationStatus.PARTIAL
    assert readiness.can_materialize is True
    assert readiness.unmet_zones


def test_an_unservable_declared_priority_outranks_a_volume_shortfall():
    """La promesse non tenue prime sur le chiffre en deçà."""
    readiness = assess_materialization(_plan(
        sessions_per_week=4,
        focus_priorities=("arms",),
        available_equipment=("dumbbell", "barbell", "machine"),
    ))
    assert readiness.status is MaterializationStatus.CONSTRAINT_UNMET
    assert readiness.unserved_priorities
    # …et il reste matérialisable : c'est l'utilisateur qui tranche.
    assert readiness.can_materialize is True


def test_a_partial_plan_is_never_reported_as_ready():
    for prefs in ({"sessions_per_week": 3}, {"sessions_per_week": 6}):
        readiness = assess_materialization(_plan(**prefs))
        assert readiness.status is not MaterializationStatus.READY


def test_the_verdict_counts_only_executable_work():
    plan = _plan(sessions_per_week=4)
    readiness = assess_materialization(plan)
    assert readiness.planned_sets == plan.planned_sets_total
    assert readiness.exercises == sum(
        1 for s in plan.sessions for slot in s.slots if slot.is_prescribed)


# ── L'arbre de brouillon ─────────────────────────────────────────────────────


def test_empty_slots_never_become_exercises():
    """Un créneau vide ne doit pas entrer dans l'arbre.

    `validate_draft` refuse une séance sans exercice ; y laisser un créneau
    vide rendrait tout le brouillon invalidable pour une lacune que le plan
    signale déjà.

    Le témoin est désormais une **restriction de matériel** : `core` était le
    seul créneau structurellement vide, et il est servable depuis
    `Sb_CORE_EXERCISE_PROPERTIES_01`.
    """
    plan = _plan(sessions_per_week=4, available_equipment=("machine", "cable"))
    empty = [s for sess in plan.sessions for s in sess.slots if not s.is_filled]
    assert empty, "fixture inutile sans créneau vide"

    names = {
        e["exercise_name"]
        for session in plan_to_draft_tree(plan)
        for e in session["exercises"]
    }
    assert None not in names
    assert all(name for name in names)


def test_no_session_in_the_tree_is_empty():
    for session in plan_to_draft_tree(_plan(sessions_per_week=6)):
        assert session["exercises"], "validate_draft refuserait cette séance"


def test_positions_are_contiguous_from_one():
    """`replace_draft_tree` exige des positions contiguës après écartement."""
    tree = plan_to_draft_tree(_plan(sessions_per_week=4))
    assert [s["position"] for s in tree] == list(range(1, len(tree) + 1))
    for session in tree:
        positions = [e["position"] for e in session["exercises"]]
        assert positions == list(range(1, len(positions) + 1))


def test_one_rep_target_per_planned_set():
    """La dose vient du plan : autant de cibles que de séries prescrites."""
    plan = _plan(sessions_per_week=4)
    by_name = {
        slot.exercise_name: slot
        for s in plan.sessions for slot in s.slots if slot.is_prescribed
    }
    for session in plan_to_draft_tree(plan):
        for exercise in session["exercises"]:
            slot = by_name[exercise["exercise_name"]]
            assert len(exercise["rep_targets"]) == slot.planned_sets
            assert exercise["set_scheme"].startswith(f"{slot.planned_sets}x ")


def test_every_exercise_is_traceable_to_its_intent():
    for session in plan_to_draft_tree(_plan(sessions_per_week=4)):
        for exercise in session["exercises"]:
            assert exercise["source_reason"].startswith(SOURCE_REASON_PREFIX)


def test_the_volume_does_not_come_from_the_morpho_prescription_table():
    """Le nombre de séries vient du budget, pas de `_INTENT_PRESCRIPTION`."""
    from app.services.morpho_program_draft_mapper import _INTENT_PRESCRIPTION

    plan = _plan(sessions_per_week=4)
    mismatches = 0
    for session in plan_to_draft_tree(plan):
        for exercise in session["exercises"]:
            intent = exercise["source_reason"].split(":")[-1]
            mapper = _INTENT_PRESCRIPTION.get(intent)
            if mapper and len(exercise["rep_targets"]) != mapper[0]:
                mismatches += 1
    assert mismatches, (
        "aucun exercice ne diffère du mapper — le volume pourrait en venir"
    )


def test_the_materializer_does_not_import_the_prescription_table():
    """Garde structurelle : la table du mapper n'est pas une source de volume."""
    from app.services import weekly_plan_materialization as mod
    from tests.helpers import module_code_only

    code = module_code_only(mod)
    assert "_INTENT_PRESCRIPTION" not in code
    assert "_DEFAULT_PRESCRIPTION" not in code


def test_the_tree_is_deterministic():
    first = plan_to_draft_tree(_plan(sessions_per_week=4))
    second = plan_to_draft_tree(_plan(sessions_per_week=4))
    assert first == second
    assert first, "un arbre vide rendrait cette égalité sans intérêt"


# ── Bout en bout, sur la base ────────────────────────────────────────────────


class TestEndToEnd:
    """Préférences → budget → plan → brouillon → preview → validation."""

    def test_the_whole_chain_produces_a_validatable_draft(self, client):
        from app.database import SessionLocal
        from app.services.training_preferences import save_training_preferences
        from app.services.user_program_drafts import validate_draft
        from app.services.user_program_quality_preview import (
            compute_quality_preview,
        )
        from app.services.weekly_plan_materialization import (
            DEFAULT_PROGRAM_TITLE,
            materialize_weekly_plan,
        )
        from app.services.weekly_planner import build_weekly_plan_for_user
        from tests.helpers import get_test_user_id

        uid = get_test_user_id()
        with SessionLocal() as db:
            save_training_preferences(
                db, uid, sessions_per_week=4, focus_priorities=["arms"])

        with SessionLocal() as db:
            plan = build_weekly_plan_for_user(db, uid)
            program, readiness = materialize_weekly_plan(
                db, uid, plan,
                title=DEFAULT_PROGRAM_TITLE, slug_base="plan-hebdo-e2e")
            program_id = program.id
            assert program.status == "draft", "rien n'est publié ni validé"
            assert readiness.status is not MaterializationStatus.BLOCKED

        with SessionLocal() as db:
            from app.services.user_program_drafts import get_draft

            preview = compute_quality_preview(get_draft(db, uid, program_id))
            assert preview is not None
            # Le moteur de qualité existant note le brouillon sans modification.
            assert preview.result.global_score is not None
            assert preview.feedback is not None

        with SessionLocal() as db:
            validated = validate_draft(db, uid, program_id)
            assert validated.status == "validated"

    def test_the_draft_carries_the_planned_sets(self, client):
        from app.database import SessionLocal
        from app.services.training_preferences import save_training_preferences
        from app.services.weekly_plan_materialization import (
            materialize_weekly_plan,
        )
        from app.services.weekly_planner import build_weekly_plan_for_user
        from tests.helpers import get_test_user_id

        uid = get_test_user_id()
        with SessionLocal() as db:
            save_training_preferences(db, uid, sessions_per_week=3)

        with SessionLocal() as db:
            plan = build_weekly_plan_for_user(db, uid)
            expected = plan.planned_sets_total
            program, _ = materialize_weekly_plan(
                db, uid, plan, title="Plan séries", slug_base="plan-series")
            stored = sum(
                len(e.rep_targets)
                for s in program.sessions for e in s.exercises
            )
            assert stored == expected

    def test_materialization_refuses_a_plan_with_nothing_executable(self, client):
        from app.database import SessionLocal
        from app.services.training_preferences import save_training_preferences
        from app.services.user_program_drafts import UserProgramDraftError
        from app.services.weekly_plan_materialization import (
            materialize_weekly_plan,
        )
        from app.services.weekly_planner import build_weekly_plan_for_user
        from tests.helpers import get_test_user_id

        uid = get_test_user_id()
        with SessionLocal() as db:
            # Cadence déclarée mais aucun matériel exploitable : rien à écrire.
            save_training_preferences(
                db, uid, sessions_per_week=3, available_equipment=[])

        with SessionLocal() as db:
            plan = build_weekly_plan_for_user(db, uid)
            with pytest.raises(UserProgramDraftError):
                materialize_weekly_plan(
                    db, uid, plan, title="Vide", slug_base="vide")


# ── La surface utilisateur ───────────────────────────────────────────────────


class TestUserSurface:
    def test_the_proposal_is_absent_without_declared_cadence(self, client):
        page = client.get("/programs").text
        assert "Créer le programme proposé" not in page

    def test_the_proposal_appears_once_a_cadence_is_declared(self, client):
        import html

        from app.database import SessionLocal
        from app.services.training_preferences import save_training_preferences
        from tests.helpers import get_test_user_id

        with SessionLocal() as db:
            save_training_preferences(
                db, get_test_user_id(), sessions_per_week=4,
                focus_priorities=["arms"])

        page = html.unescape(client.get("/programs").text)
        assert "Créer le programme proposé" in page
        assert "Programme proposé pour ta semaine" in page
        assert "Bras" in page

    def test_the_surface_states_that_nothing_is_published(self, client):
        import html

        from app.database import SessionLocal
        from app.services.training_preferences import save_training_preferences
        from tests.helpers import get_test_user_id

        with SessionLocal() as db:
            save_training_preferences(
                db, get_test_user_id(), sessions_per_week=4)

        page = html.unescape(client.get("/programs").text)
        assert "brouillon" in page.lower()
        assert "Rien n'est publié ni lancé sans ton accord" in page

    def test_a_partial_proposal_says_so_on_the_page(self, client):
        import html

        from app.database import SessionLocal
        from app.services.training_preferences import save_training_preferences
        from tests.helpers import get_test_user_id

        with SessionLocal() as db:
            save_training_preferences(
                db, get_test_user_id(), sessions_per_week=4)

        page = html.unescape(client.get("/programs").text)
        assert "Proposition partielle" in page

    def test_the_action_creates_a_draft_and_lands_on_the_editor(self, client):
        from app.database import SessionLocal
        from app.models.user_program import UserProgram
        from app.services.training_preferences import save_training_preferences
        from tests.helpers import get_test_user_id

        uid = get_test_user_id()
        with SessionLocal() as db:
            save_training_preferences(db, uid, sessions_per_week=4)

        response = client.post("/programs/from-weekly-plan")
        assert response.status_code == 200

        with SessionLocal() as db:
            programs = db.query(UserProgram).filter(
                UserProgram.user_id == uid).all()
            assert len(programs) == 1
            assert programs[0].status == "draft"
            assert programs[0].sessions

    def test_the_action_never_publishes(self, client):
        from app.database import SessionLocal
        from app.models.user_program import UserProgram
        from app.services.training_preferences import save_training_preferences
        from tests.helpers import get_test_user_id

        uid = get_test_user_id()
        with SessionLocal() as db:
            save_training_preferences(db, uid, sessions_per_week=4)
        client.post("/programs/from-weekly-plan")

        with SessionLocal() as db:
            statuses = {
                p.status for p in db.query(UserProgram).filter(
                    UserProgram.user_id == uid).all()
            }
        assert statuses == {"draft"}

    def test_the_proposal_is_confined_when_the_chain_raises(self, client, monkeypatch):
        from app.database import SessionLocal
        from app.services import weekly_planner
        from app.services.training_preferences import save_training_preferences
        from tests.helpers import get_test_user_id

        with SessionLocal() as db:
            save_training_preferences(
                db, get_test_user_id(), sessions_per_week=4)

        def _boom(*_args, **_kwargs):
            raise RuntimeError("planner down")

        monkeypatch.setattr(weekly_planner, "build_weekly_plan_for_user", _boom)
        response = client.get("/programs")
        assert response.status_code == 200
        assert "Créer le programme proposé" not in response.text
