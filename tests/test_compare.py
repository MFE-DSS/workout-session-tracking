"""Tests for app.services.compare — head-to-head comparison."""
from __future__ import annotations

from datetime import datetime, timezone

from tests.helpers import get_test_user_id


def _get_db():
    from app.database import SessionLocal
    return SessionLocal()


def _create_second_user(db, username="comparee"):
    from app.models.user import User
    from app.services.auth import hash_password
    from sqlalchemy import select

    existing = db.execute(
        select(User).where(User.username == username)
    ).scalar_one_or_none()
    if existing:
        return existing.id
    user = User(
        username=username, password_hash=hash_password("pass1234"), is_active=True
    )
    db.add(user)
    db.commit()
    return user.id


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
        success_score=100,
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
# 1. compute_comparison — returns entries for both users
# ---------------------------------------------------------------------------

def _add_member(db, squad_id, user_id):
    from app.models.squad import SquadMembership
    mem = SquadMembership(squad_id=squad_id, user_id=user_id, role="member")
    db.add(mem)
    db.commit()


def test_compute_comparison(client):
    from app.services.compare import compute_comparison
    from app.services.squad import create_squad

    uid = get_test_user_id()
    with _get_db() as db:
        uid2 = _create_second_user(db)
        squad = create_squad(db, uid, "CompareSquad")
        _add_member(db, squad.id, uid2)

        _add_session(db, uid)
        _add_session(db, uid2)

        result = compute_comparison(db, squad.id, uid, uid2)

        assert result["a"] is not None
        assert result["b"] is not None
        assert result["a"]["username"] == "testuser"
        assert result["b"]["username"] == "comparee"
        assert "total_points" in result["a"]


# ---------------------------------------------------------------------------
# 2. compute_comparison — missing user returns None
# ---------------------------------------------------------------------------

def test_compute_comparison_missing_user(client):
    from app.services.compare import compute_comparison

    uid = get_test_user_id()
    with _get_db() as db:
        result = compute_comparison(db, 999, uid, 99999)
        assert result["a"] is None or result["b"] is None
