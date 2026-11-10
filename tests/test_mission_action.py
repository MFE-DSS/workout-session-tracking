"""MOB04: owned presentation never creates training permission or writes facts."""

from datetime import UTC, datetime

import pytest
from sqlalchemy import event


def test_first_use_without_plan_schema_is_honest_and_does_not_fall_back(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.mission_action import project_mission_action

    with SessionLocal() as db:
        owner = db.query(User).one().id
        writes = []

        def trace(connection, cursor, statement, parameters, context, many):
            if statement.lstrip().split(None, 1)[0].upper() in {"INSERT", "UPDATE", "DELETE"}:
                writes.append(statement)

        event.listen(db.get_bind(), "before_cursor_execute", trace)
        try:
            result = project_mission_action(db, owner, "FIRST_USE", v3_host=True)
        finally:
            event.remove(db.get_bind(), "before_cursor_execute", trace)
        assert result["state"] == "UNAVAILABLE"
        assert result["source"] == "OWNED_FIRST_USE"
        assert result["reason"] == "SCHEMA_UNAVAILABLE"
        assert result["primary_action"] == {"kind": "REFRESH"}
        assert writes == []


def test_owned_open_legacy_session_wins_over_both_recommendation_paths(client):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    from app.models.user import User
    from app.services.mission_action import project_mission_action

    with SessionLocal() as db:
        owner = db.query(User).one().id
        session = WorkoutSession(
            started_at=datetime(2026, 11, 10, 9, tzinfo=UTC),
            user_id=owner,
            template_slug_snapshot="old-owned",
            template_name_snapshot="Nom capturé",
            status="in_progress",
        )
        db.add(session)
        db.commit()
        for path in ("FIRST_USE", "HISTORICAL"):
            result = project_mission_action(db, owner, path)
            assert result["state"] == "RESUME"
            assert result["source"] == "OPEN_SESSION"
            assert result["primary_action"] == {"kind": "RESUME_LEGACY", "session_id": session.id}
            assert result["payload"]["session"]["name"] == "Nom capturé"


def test_multiple_owned_open_sessions_do_not_pick_the_latest_arbitrarily(client):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    from app.models.user import User
    from app.services.mission_action import project_mission_action

    with SessionLocal() as db:
        owner = db.query(User).one().id
        for index in range(2):
            db.add(
                WorkoutSession(
                    started_at=datetime(2026, 11, 10, 9, tzinfo=UTC),
                    user_id=owner,
                    template_slug_snapshot=f"old-{index}",
                    template_name_snapshot="Ouverte",
                    status="in_progress",
                )
            )
        db.commit()
        result = project_mission_action(db, owner, "HISTORICAL")
        assert result["state"] == "CONFLICT"
        assert result["reason"] == "MULTIPLE_OPEN_SESSIONS"
        assert result["primary_action"] is None
        assert result["payload"] is None


@pytest.mark.parametrize("path", ["", "first_use", "READY", None, True])
def test_a_missing_or_invented_requested_source_is_rejected(client, path):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.mission_action import project_mission_action

    with SessionLocal() as db:
        with pytest.raises(ValueError, match="mission_path_required"):
            project_mission_action(db, db.query(User).one().id, path)


def test_foreign_session_cannot_become_another_owners_resume(client):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    from app.models.user import User
    from app.services.mission_action import project_mission_action

    with SessionLocal() as db:
        owner = db.query(User).one().id
        other = User(username="other-owner", password_hash="synthetic-unused")
        db.add(other)
        db.flush()
        foreign = WorkoutSession(
            started_at=datetime(2026, 11, 10, 9, tzinfo=UTC),
            user_id=other.id,
            template_slug_snapshot="foreign-session",
            template_name_snapshot="Other private name",
            status="in_progress",
        )
        db.add(foreign)
        db.commit()
        result = project_mission_action(db, owner, "FIRST_USE", v3_host=True)
        assert result["state"] == "UNAVAILABLE"
        assert result["payload"] is None
        assert "Other private name" not in str(result)


def test_scientific_resume_never_uses_legacy_without_explicit_host(client):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    from app.models.user import User
    from app.services.mission_action import project_mission_action

    with SessionLocal() as db:
        owner = db.query(User).one().id
        db.add(
            WorkoutSession(
                started_at=datetime(2026, 11, 10, 9, tzinfo=UTC),
                user_id=owner,
                template_slug_snapshot="science:v3:first-session",
                template_name_snapshot="Première séance",
                status="in_progress",
            )
        )
        db.commit()
        result = project_mission_action(db, owner, "HISTORICAL")
        assert result["state"] == "UNAVAILABLE"
        assert result["source"] == "OPEN_SESSION"
        assert result["reason"] == "EXECUTION_PROFILE_REQUIRED"
        assert result["primary_action"] is None


def test_runtime_off_does_not_become_a_first_use_positive(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.mission_action import project_mission_action
    from tests.test_plan_v3_persistence import install

    install()
    with SessionLocal() as db:
        result = project_mission_action(db, db.query(User).one().id, "FIRST_USE", v3_host=True)
        assert result["state"] == "UNAVAILABLE"
        assert result["reason"] == "RUNTIME_NOT_SERVED"


def test_current_authority_absent_does_not_become_a_positive(client, monkeypatch):
    from app.config import get_settings
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.mission_action import project_mission_action
    from tests.test_plan_v3_persistence import install

    install()
    monkeypatch.setattr(get_settings(), "plan_v3_controlled_test_enabled", True)
    with SessionLocal() as db:
        result = project_mission_action(db, db.query(User).one().id, "FIRST_USE", v3_host=True)
        assert result["state"] == "UNAVAILABLE"
        assert result["reason"] == "AUTHORITY_UNAVAILABLE"
        assert result["primary_action"] == {"kind": "REFRESH"}


def test_explicit_historical_path_preserves_real_domain_recommendation(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.mission_action import project_mission_action
    from app.services.mobile_read_models import mission_read_model

    with SessionLocal() as db:
        owner = db.query(User).one().id
        canonical = mission_read_model(db, owner)
        assert canonical["state"] == "READY"  # Existing seed supplies a real candidate.
        result = project_mission_action(db, owner, "HISTORICAL")
        assert result["state"] == "HISTORICAL_READY"
        assert result["source"] == "HISTORICAL_MISSION"
        assert result["payload"] == canonical
        assert result["primary_action"] == {
            "kind": "START_LEGACY",
            "template_slug": canonical["template"]["slug"],
            "decision": canonical["decision"],
        }


@pytest.fixture(scope="session")
def v2_science_bundle(tmp_path_factory):
    from tools.plan_calibration_runtime_bundle import build_bundle

    root = tmp_path_factory.mktemp("mob04-inventory2") / "private"
    return root, build_bundle(root)


@pytest.fixture(scope="session")
def v1_science_bundle(tmp_path_factory):
    from scripts.build_plan_v3_runtime_bundle import build_bundle

    root = tmp_path_factory.mktemp("mob04-historical-binding") / "private"
    return root, build_bundle(root)


def test_real_inventory_opens_first_use_without_facts_and_withdrawal_blocks_it(
    client, monkeypatch, v2_science_bundle
):
    from app.config import get_settings
    from app.database import SessionLocal
    from app.models.first_plan_runtime import (
        BlueprintSourceEvent,
        FirstPlanEvaluation,
        FirstPlanRuntimeAuthority,
    )
    from app.models.session import WorkoutSession
    from app.models.user import User
    from app.services.mission_action import project_mission_action
    from tests.plan_v3_test_support import activate_test_authority
    from tests.test_plan_v3_persistence import install

    install()
    monkeypatch.setattr(get_settings(), "plan_v3_bundle_path", str(v2_science_bundle[0]))
    monkeypatch.setattr(get_settings(), "plan_v3_controlled_test_enabled", True)
    with SessionLocal() as db:
        owner = db.query(User).one().id
        activate_test_authority(db, v2_science_bundle)
        writes = []

        def trace(connection, cursor, statement, parameters, context, many):
            if statement.lstrip().split(None, 1)[0].upper() in {"INSERT", "UPDATE", "DELETE"}:
                writes.append(statement)

        event.listen(db.get_bind(), "before_cursor_execute", trace)
        try:
            result = project_mission_action(db, owner, "FIRST_USE", v3_host=True)
        finally:
            event.remove(db.get_bind(), "before_cursor_execute", trace)
        assert writes == []  # Even the authority-generation no-op UPDATE is forbidden.
        assert result["state"] == "FIRST_USE"
        assert result["primary_action"] == {"kind": "OPEN_FIRST_USE"}
        assert result["payload"]["source_revision"] == "blueprint-source/0"
        assert result["payload"]["calibration_inventory"] == "plan-calibration-inventory/2.0.0"
        assert db.query(BlueprintSourceEvent).count() == 0
        assert db.query(FirstPlanEvaluation).count() == 0
        assert db.query(WorkoutSession).count() == 0
        authority = db.get(FirstPlanRuntimeAuthority, "first-session-runtime/3.0.0")
        authority.state = "WITHDRAWN"
        authority.generation += 1
        db.commit()
        after = project_mission_action(db, owner, "FIRST_USE", v3_host=True)
        assert after["state"] == "UNAVAILABLE"
        assert after["reason"] == "AUTHORITY_UNAVAILABLE"


def test_real_owned_handoff_is_read_after_close_and_withdrawal_without_new_start(
    client, monkeypatch, v1_science_bundle
):
    from app.config import get_settings
    from app.database import SessionLocal
    from app.models.first_plan_runtime import FirstPlanRuntimeAuthority, FirstSessionRequest
    from app.models.session import WorkoutSession
    from app.models.user import User
    from app.services.mission_action import project_mission_action
    from app.services.plan_v3.commands import start_owned_first_session
    from tests.test_first_session_commands import final_evaluation, start_body
    from tests.test_plan_v3_persistence import install

    install()
    monkeypatch.setattr(get_settings(), "plan_v3_bundle_path", str(v1_science_bundle[0]))
    with SessionLocal() as db:
        owner = db.query(User).one().id
        evaluation = final_evaluation(db, owner, v1_science_bundle, monkeypatch)
        handoff = start_owned_first_session(
            db, owner, request_id="real-owned", body=start_body(evaluation)
        )
        db.commit()
        opened = project_mission_action(db, owner, "FIRST_USE", v3_host=True)
        assert opened["state"] == "RESUME"
        assert opened["primary_action"] == {"kind": "RESUME_V3", "session_id": handoff.session_id}
        session = db.get(WorkoutSession, handoff.session_id)
        session.status = "completed"
        session.ended_at = datetime.now(UTC)
        authority = db.get(FirstPlanRuntimeAuthority, "first-session-runtime/3.0.0")
        authority.state = "WITHDRAWN"
        authority.generation += 1
        db.commit()
        monkeypatch.setattr(get_settings(), "plan_v3_controlled_test_enabled", False)
        writes = []

        def trace(connection, cursor, statement, parameters, context, many):
            if statement.lstrip().split(None, 1)[0].upper() in {"INSERT", "UPDATE", "DELETE"}:
                writes.append(statement)

        event.listen(db.get_bind(), "before_cursor_execute", trace)
        try:
            result = project_mission_action(db, owner, "FIRST_USE", v3_host=True)
        finally:
            event.remove(db.get_bind(), "before_cursor_execute", trace)
        assert result["state"] == "FIRST_SESSION_HISTORY"
        assert result["primary_action"] == {
            "kind": "OPEN_FIRST_SESSION_HISTORY",
            "session_id": handoff.session_id,
        }
        assert db.query(FirstSessionRequest).filter_by(state="CREATED").count() == 1
        assert db.query(WorkoutSession).count() == 1
        assert writes == []
