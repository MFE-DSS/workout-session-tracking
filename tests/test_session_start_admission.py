"""Legacy starts share the persistent owner guard with SCI; no memory mutex."""

from datetime import UTC, datetime

import pytest

from tests.test_plan_v3_persistence import install


def test_legacy_start_refuses_science_open_and_mobile_rechecks_any_open(client):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    from app.models.user import User
    from app.services.plan_v3.transactions import RuntimeFailure, admit_legacy_start

    install()
    with SessionLocal() as db:
        owner = db.query(User).one().id
        session = WorkoutSession(
            user_id=owner,
            template_slug_snapshot="science:v3:first-session",
            template_name_snapshot="Synthetic guarded profile",
            started_at=datetime.now(UTC),
            status="in_progress",
        )
        db.add(session)
        db.commit()
        with pytest.raises(RuntimeFailure, match="session_open"):
            admit_legacy_start(db, owner)
        db.rollback()
        session.template_slug_snapshot = "legacy"
        db.commit()
        admit_legacy_start(db, owner, reject_any_open=False)
        db.rollback()
        with pytest.raises(RuntimeFailure, match="session_open"):
            admit_legacy_start(db, owner, reject_any_open=True)
        db.rollback()


def test_legacy_restore_is_operationally_excluded_from_plan_database(client):
    from app.database import SessionLocal
    from app.services.restore import restore_from_json_payload

    install()
    with SessionLocal() as db:
        result = restore_from_json_payload(db, {"schema_version": 2, "count": 0, "sessions": []})
        assert any("PLAN" in e for e in result.errors)
