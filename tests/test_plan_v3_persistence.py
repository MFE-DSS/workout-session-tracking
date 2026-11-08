"""Additive PLAN schema: no startup apply, real ownership constraints."""

import importlib
from pathlib import Path

import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

ROOT = Path(__file__).resolve().parents[1]


def models():
    return importlib.import_module("app.models.first_plan_runtime")


def install():
    import importlib.util

    from alembic.migration import MigrationContext
    from alembic.operations import Operations

    from app.database import engine

    spec = importlib.util.spec_from_file_location(
        "plan_migration", ROOT / "migrations/versions/plan_v3_20261107_01.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with engine.begin() as conn:
        with Operations.context(MigrationContext.configure(conn)):
            module.upgrade()


def test_legacy_startup_has_no_plan_tables_or_composite_indexes(client):
    from app.database import engine

    m = models()
    schema = inspect(engine)
    assert set(m.PLAN_TABLE_NAMES).isdisjoint(schema.get_table_names())
    for table in ("workout_sessions", "session_exercises", "set_logs"):
        assert not any(i["name"] in m.PLAN_INDEX_NAMES for i in schema.get_indexes(table))


def test_migration_adds_exactly_seven_tables_and_preserves_identity(client):
    from app.database import SessionLocal, engine
    from app.models.user import User

    m = models()
    before = set(inspect(engine).get_table_names())
    with SessionLocal() as db:
        u = db.query(User).one()
        original = (u.id, u.username, u.password_hash, u.session_epoch)
    install()
    assert set(inspect(engine).get_table_names()) - before == set(m.PLAN_TABLE_NAMES)
    with SessionLocal() as db:
        u = db.query(User).one()
        assert (u.id, u.username, u.password_hash, u.session_epoch) == original
    for table in ("workout_sessions", "session_exercises", "set_logs"):
        assert any(
            i["name"] in m.PLAN_INDEX_NAMES and i["unique"]
            for i in inspect(engine).get_indexes(table)
        )


def _snapshot_eval(db, owner, suffix):
    from datetime import UTC, datetime

    m = models()
    now = datetime.now(UTC)
    snap = m.OwnedBlueprintSnapshot(
        id="snap-" + suffix,
        owner_id=owner,
        request_id="snapshot-" + suffix,
        body_digest="a" * 64,
        source_revision=0,
        as_of=now,
        snapshot_json="{}",
        snapshot_digest="b" * 64,
    )
    db.add(snap)
    db.flush()
    ev = m.FirstPlanEvaluation(
        id="eval-" + suffix,
        owner_id=owner,
        snapshot_id=snap.id,
        operation_kind="EVALUATE",
        request_id="evaluate-" + suffix,
        body_digest="c" * 64,
        request_json="{}",
        result_json="{}",
        source_revision=0,
        authority_generation=1,
    )
    db.add(ev)
    db.flush()
    return ev


def test_foreign_evaluation_cannot_attach_to_owned_snapshot(client):
    from app.database import SessionLocal
    from app.models.user import User

    m = models()
    install()
    with SessionLocal() as db:
        a = db.query(User).one()
        b = User(username="second", password_hash=a.password_hash)
        db.add(b)
        db.flush()
        ev = _snapshot_eval(db, a.id, "a")
        db.commit()
        bad = m.FirstPlanEvaluation(
            id="foreign",
            owner_id=b.id,
            snapshot_id=ev.snapshot_id,
            operation_kind="EVALUATE",
            request_id="foreign",
            body_digest="a" * 64,
            request_json="{}",
            result_json="{}",
            source_revision=0,
            authority_generation=1,
        )
        db.add(bad)
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()


def test_created_handoff_is_unique_and_foreign_session_is_rejected(client):
    from datetime import UTC, datetime

    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    from app.models.user import User

    m = models()
    install()
    with SessionLocal() as db:
        a = db.query(User).one()
        b = User(username="second", password_hash=a.password_hash)
        db.add(b)
        db.flush()
        ev = _snapshot_eval(db, a.id, "a")
        sessions = [
            WorkoutSession(
                user_id=owner,
                template_slug_snapshot="test",
                template_name_snapshot="Test",
                started_at=datetime.now(UTC),
            )
            for owner in (a.id, a.id, b.id)
        ]
        db.add_all(sessions)
        db.flush()
        ids = [s.id for s in sessions]
        owner = a.id
        eid = ev.id
        db.commit()

        def row(key, sid):
            return m.FirstSessionRequest(
                owner_id=owner,
                request_id=key,
                body_digest="d" * 64,
                body_json="{}",
                evaluation_id=eid,
                state="CREATED",
                session_id=sid,
                scientific_session_id="first",
            )

        db.add(row("first", ids[0]))
        db.commit()
        db.add(row("second", ids[1]))
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()
        # Another owner cannot reuse A's evaluation or session ownership chain.
        db.add(
            m.FirstSessionRequest(
                owner_id=b.id,
                request_id="foreign",
                body_digest="d" * 64,
                body_json="{}",
                evaluation_id=eid,
                state="CREATED",
                session_id=ids[2],
                scientific_session_id="first",
            )
        )
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()


def test_empty_created_and_active_unapproved_authority_are_rejected(client):
    from app.database import SessionLocal
    from app.models.user import User

    m = models()
    install()
    with SessionLocal() as db:
        owner = db.query(User).one().id
        db.add(
            m.FirstSessionRequest(
                owner_id=owner,
                request_id="empty",
                body_digest="x" * 64,
                body_json="{}",
                state="CREATED",
            )
        )
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()
        db.add(
            m.FirstPlanRuntimeAuthority(
                profile_key="first-session-runtime/3.0.0", generation=1, state="ACTIVE"
            )
        )
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()


def test_evidence_rows_cannot_be_rewritten_through_the_orm(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.plan_v3.transactions import RuntimeFailure

    m = models()
    install()
    with SessionLocal() as db:
        owner = db.query(User).one().id
        ev = _snapshot_eval(db, owner, "immutable")
        db.commit()
        ev.result_json = '{"forged":"replacement"}'
        with pytest.raises(RuntimeFailure, match="immutable_plan_evidence"):
            db.commit()
        db.rollback()
        assert db.get(m.FirstPlanEvaluation, ev.id).result_json == "{}"
        snap = db.get(m.OwnedBlueprintSnapshot, ev.snapshot_id)
        db.delete(snap)
        with pytest.raises(RuntimeFailure, match="immutable_plan_evidence"):
            db.flush()
        db.rollback()


def test_partial_or_corrupt_schema_is_never_reported_ready(client):
    from sqlalchemy import text

    from app.database import SessionLocal
    from app.services.plan_v3.transactions import schema_available

    install()
    with SessionLocal() as db:
        assert schema_available(db)
        db.execute(text("DROP INDEX uq_plan_v3_set_exercise"))
        db.commit()
        assert not schema_available(db)
