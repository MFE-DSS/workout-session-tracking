"""Tests for app.services.sharing — recommendations, session sharing, activity feed."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from tests.helpers import get_test_user_id


def _get_db():
    from app.database import SessionLocal
    return SessionLocal()


def _add_session(db, user_id):
    from app.models.session import WorkoutSession, SessionExercise, SetLog

    s = WorkoutSession(
        user_id=user_id,
        template_slug_snapshot="push-a",
        template_name_snapshot="Push A",
        started_at=datetime.now(timezone.utc),
        status="completed",
        concentration="high",
        global_state="good",
    )
    se = SessionExercise(
        exercise_code_snapshot="BP",
        exercise_name_snapshot="Bench Press",
        position=1,
        success_score=80,
    )
    se.set_logs.append(SetLog(
        kind="work", set_index=1, completed=True,
        weight_kg=60.0, reps=10,
    ))
    s.session_exercises.append(se)
    db.add(s)
    db.commit()
    return s


# ---------------------------------------------------------------------------
# 1. recommend_template — creates recommendation
# ---------------------------------------------------------------------------

def test_recommend_template(client):
    from app.services.sharing import recommend_template
    from app.services.squad import create_squad

    uid = get_test_user_id()
    with _get_db() as db:
        squad = create_squad(db, uid, "ShareSquad")
        rec = recommend_template(
            db, squad.id, uid, "push-a", "Push A", note="Great template!"
        )
        assert rec.id is not None
        assert rec.template_slug == "push-a"
        assert rec.note == "Great template!"


# ---------------------------------------------------------------------------
# 2. share_session — happy path
# ---------------------------------------------------------------------------

def test_share_session(client):
    from app.services.sharing import share_session
    from app.services.squad import create_squad

    uid = get_test_user_id()
    with _get_db() as db:
        squad = create_squad(db, uid, "SessionShareSquad")
        session = _add_session(db, uid)
        shared = share_session(db, squad.id, uid, session.id)
        assert shared.id is not None
        assert shared.session_id == session.id


# ---------------------------------------------------------------------------
# 3. share_session — wrong owner raises SharingError
# ---------------------------------------------------------------------------

def test_share_session_wrong_owner(client):
    from app.services.sharing import SharingError, share_session
    from app.services.squad import create_squad

    uid = get_test_user_id()
    with _get_db() as db:
        squad = create_squad(db, uid, "WrongOwnerSquad")
        session = _add_session(db, uid)
        with pytest.raises(SharingError, match="introuvable"):
            share_session(db, squad.id, uid + 999, session.id)


# ---------------------------------------------------------------------------
# 4. get_squad_activity — mixed feed
# ---------------------------------------------------------------------------

def test_get_squad_activity(client):
    from app.services.sharing import get_squad_activity, recommend_template, share_session
    from app.services.squad import create_squad

    uid = get_test_user_id()
    with _get_db() as db:
        squad = create_squad(db, uid, "ActivitySquad")
        session = _add_session(db, uid)

        recommend_template(db, squad.id, uid, "push-a", "Push A")
        share_session(db, squad.id, uid, session.id)

        activity = get_squad_activity(db, squad.id)

        assert len(activity) == 2
        types = {a["type"] for a in activity}
        assert "recommendation" in types
        assert "shared_session" in types

        # Check shared session has exercises with allowed fields only
        shared = next(a for a in activity if a["type"] == "shared_session")
        assert len(shared["exercises"]) > 0
        ex = shared["exercises"][0]
        assert "code" in ex
        assert "name" in ex
        assert "success_score" in ex
        # Must NOT contain private data
        assert "weight_kg" not in ex
        assert "reps" not in ex
        assert "muscle_sensation" not in ex
