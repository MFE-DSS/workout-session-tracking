"""Tests for app.services.challenge — create, validate, list, standings."""
from __future__ import annotations

from datetime import date, datetime, timezone

import pytest

from tests.helpers import get_test_user_id


def _get_db():
    from app.database import SessionLocal
    return SessionLocal()


def _create_squad(db, uid, name="ChallengeSquad"):
    from app.services.squad import create_squad
    return create_squad(db, uid, name)


def _add_session_on_date(db, user_id, d: date, *, weight=60.0, reps=10):
    """Insert a completed session on a specific date."""
    from app.models.session import WorkoutSession, SessionExercise, SetLog

    s = WorkoutSession(
        user_id=user_id,
        template_slug_snapshot="push-a",
        template_name_snapshot="Push A",
        started_at=datetime(d.year, d.month, d.day, 10, 0, tzinfo=timezone.utc),
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
        weight_kg=weight, reps=reps,
    ))
    s.session_exercises.append(se)
    db.add(s)
    db.commit()
    return s


def _create_second_user(db, username="challenger"):
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


# ---------------------------------------------------------------------------
# 1. create_challenge — happy path
# ---------------------------------------------------------------------------

def test_create_challenge(client):
    from app.services.challenge import create_challenge

    uid = get_test_user_id()
    with _get_db() as db:
        squad = _create_squad(db, uid)
        ch = create_challenge(
            db, squad.id, uid, "Push-Up Week", "sessions",
            date(2026, 4, 14), date(2026, 4, 20),
        )
        assert ch.title == "Push-Up Week"
        assert ch.metric == "sessions"
        assert ch.id is not None


# ---------------------------------------------------------------------------
# 2. create_challenge — invalid metric
# ---------------------------------------------------------------------------

def test_create_challenge_invalid_metric(client):
    from app.services.challenge import ChallengeError, create_challenge

    uid = get_test_user_id()
    with _get_db() as db:
        squad = _create_squad(db, uid, "MetricSquad")
        with pytest.raises(ChallengeError, match="Métrique invalide"):
            create_challenge(
                db, squad.id, uid, "Bad", "invalid_metric",
                date(2026, 4, 14), date(2026, 4, 20),
            )


# ---------------------------------------------------------------------------
# 3. create_challenge — end before start
# ---------------------------------------------------------------------------

def test_create_challenge_end_before_start(client):
    from app.services.challenge import ChallengeError, create_challenge

    uid = get_test_user_id()
    with _get_db() as db:
        squad = _create_squad(db, uid, "DateSquad")
        with pytest.raises(ChallengeError, match="date de fin"):
            create_challenge(
                db, squad.id, uid, "Bad Dates", "sessions",
                date(2026, 4, 20), date(2026, 4, 14),
            )


# ---------------------------------------------------------------------------
# 4. get_squad_challenges — list ordered by starts_at desc
# ---------------------------------------------------------------------------

def test_get_squad_challenges(client):
    from app.services.challenge import create_challenge, get_squad_challenges

    uid = get_test_user_id()
    with _get_db() as db:
        squad = _create_squad(db, uid, "ListSquad")
        create_challenge(db, squad.id, uid, "Early", "sessions",
                         date(2026, 3, 1), date(2026, 3, 7))
        create_challenge(db, squad.id, uid, "Late", "sessions",
                         date(2026, 4, 1), date(2026, 4, 7))

        challenges = get_squad_challenges(db, squad.id)
        assert len(challenges) == 2
        assert challenges[0].title == "Late"
        assert challenges[1].title == "Early"


# ---------------------------------------------------------------------------
# 5. compute_standings — sessions metric
# ---------------------------------------------------------------------------

def _add_member(db, squad_id, user_id):
    from app.models.squad import SquadMembership
    mem = SquadMembership(squad_id=squad_id, user_id=user_id, role="member")
    db.add(mem)
    db.commit()


def test_compute_standings_sessions(client):
    from app.services.challenge import create_challenge, compute_standings

    uid = get_test_user_id()
    with _get_db() as db:
        uid2 = _create_second_user(db, "standee")
        squad = _create_squad(db, uid, "StandingsSquad")
        _add_member(db, squad.id, uid2)

        # User 1: 2 sessions in window
        _add_session_on_date(db, uid, date(2026, 4, 15))
        _add_session_on_date(db, uid, date(2026, 4, 16))

        # User 2: 1 session in window
        _add_session_on_date(db, uid2, date(2026, 4, 15))

        ch = create_challenge(
            db, squad.id, uid, "Session Count", "sessions",
            date(2026, 4, 14), date(2026, 4, 20),
        )
        standings = compute_standings(db, ch)

        assert len(standings) == 2
        assert standings[0]["value"] == 2.0
        assert standings[0]["rank"] == 1
        assert standings[1]["value"] == 1.0
        assert standings[1]["rank"] == 2


# ---------------------------------------------------------------------------
# 6. compute_standings — tonnage metric
# ---------------------------------------------------------------------------

def test_compute_standings_tonnage(client):
    from app.services.challenge import create_challenge, compute_standings

    uid = get_test_user_id()
    with _get_db() as db:
        uid2 = _create_second_user(db, "tonnager")
        squad = _create_squad(db, uid, "TonnageSquad")
        _add_member(db, squad.id, uid2)

        # uid: 60kg * 10 reps = 600
        _add_session_on_date(db, uid, date(2026, 4, 15), weight=60.0, reps=10)
        # uid2: 80kg * 5 reps = 400
        _add_session_on_date(db, uid2, date(2026, 4, 15), weight=80.0, reps=5)

        ch = create_challenge(
            db, squad.id, uid, "Tonnage Race", "tonnage",
            date(2026, 4, 14), date(2026, 4, 20),
        )
        standings = compute_standings(db, ch)

        assert standings[0]["value"] == 600.0
        assert standings[1]["value"] == 400.0
