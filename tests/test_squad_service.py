"""Tests for app.services.squad — CRUD, invite codes, join, leave, leaderboard."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from tests.helpers import get_test_user_id


def _get_db():
    from app.database import SessionLocal

    return SessionLocal()


def _create_second_user(db):
    from sqlalchemy import select

    from app.models.user import User
    from app.services.auth import hash_password

    existing = db.execute(
        select(User).where(User.username == "squadmate")
    ).scalar_one_or_none()
    if existing:
        return existing.id
    user = User(
        username="squadmate", password_hash=hash_password("pass1234"), is_active=True
    )
    db.add(user)
    db.commit()
    return user.id


# ---------------------------------------------------------------------------
# 1. create_squad — creates squad + owner membership
# ---------------------------------------------------------------------------


def test_create_squad(client):
    from app.services.squad import create_squad, get_membership

    uid = get_test_user_id()
    with _get_db() as db:
        squad = create_squad(db, uid, "TeamAlpha")
        assert squad.name == "TeamAlpha"
        assert squad.owner_id == uid

        mem = get_membership(db, squad.id, uid)
        assert mem is not None
        assert mem.role == "owner"


# ---------------------------------------------------------------------------
# 2. create_squad — duplicate name raises SquadError
# ---------------------------------------------------------------------------


def test_create_squad_duplicate_name(client):
    from app.services.squad import SquadError, create_squad

    uid = get_test_user_id()
    with _get_db() as db:
        create_squad(db, uid, "Unique")
        with pytest.raises(SquadError, match="existe déjà"):
            create_squad(db, uid, "Unique")


# ---------------------------------------------------------------------------
# 3. get_user_squads — returns user's squads
# ---------------------------------------------------------------------------


def test_get_user_squads(client):
    from app.services.squad import create_squad, get_user_squads

    uid = get_test_user_id()
    with _get_db() as db:
        create_squad(db, uid, "SquadA")
        create_squad(db, uid, "SquadB")

        squads = get_user_squads(db, uid)
        names = {s.name for s in squads}
        assert "SquadA" in names
        assert "SquadB" in names


# ---------------------------------------------------------------------------
# 4. generate_invite_code — returns SPGN-XXXX format
# ---------------------------------------------------------------------------


def test_generate_invite_code_format(client):
    import re

    from app.services.squad import create_squad, generate_invite_code

    uid = get_test_user_id()
    with _get_db() as db:
        squad = create_squad(db, uid, "InviteTeam")
        code = generate_invite_code(db, squad.id, uid)
        assert re.match(r"^SPGN-[A-Z0-9]{4}$", code)


# ---------------------------------------------------------------------------
# 5. join_by_code — creates membership, marks code used
# ---------------------------------------------------------------------------


def test_join_by_code(client):
    from app.services.squad import (
        create_squad,
        generate_invite_code,
        get_membership,
        join_by_code,
    )

    uid = get_test_user_id()
    with _get_db() as db:
        mate_id = _create_second_user(db)
        squad = create_squad(db, uid, "JoinTeam")
        code = generate_invite_code(db, squad.id, uid)

        joined_squad = join_by_code(db, mate_id, code)
        assert joined_squad.id == squad.id

        mem = get_membership(db, squad.id, mate_id)
        assert mem is not None
        assert mem.role == "member"


# ---------------------------------------------------------------------------
# 6. join_by_code — expired code raises SquadError
# ---------------------------------------------------------------------------


def test_join_by_code_expired(client):
    from sqlalchemy import select

    from app.models.squad import SquadInviteCode
    from app.services.squad import (
        SquadError,
        create_squad,
        generate_invite_code,
        join_by_code,
    )

    uid = get_test_user_id()
    with _get_db() as db:
        mate_id = _create_second_user(db)
        squad = create_squad(db, uid, "ExpiredTeam")
        code = generate_invite_code(db, squad.id, uid)

        # Force-expire the code
        invite = db.execute(
            select(SquadInviteCode).where(SquadInviteCode.code == code)
        ).scalar_one()
        invite.expires_at = datetime.now(UTC) - timedelta(hours=1)
        db.commit()

        with pytest.raises(SquadError, match="expiré"):
            join_by_code(db, mate_id, code)


# ---------------------------------------------------------------------------
# 7. leave_squad — removes membership
# ---------------------------------------------------------------------------


def test_leave_squad(client):
    from app.services.squad import (
        create_squad,
        generate_invite_code,
        get_membership,
        join_by_code,
        leave_squad,
    )

    uid = get_test_user_id()
    with _get_db() as db:
        mate_id = _create_second_user(db)
        squad = create_squad(db, uid, "LeaveTeam")
        code = generate_invite_code(db, squad.id, uid)
        join_by_code(db, mate_id, code)

        leave_squad(db, squad.id, mate_id)
        assert get_membership(db, squad.id, mate_id) is None


# ---------------------------------------------------------------------------
# 8. owner cannot leave — raises SquadError
# ---------------------------------------------------------------------------


def test_owner_cannot_leave(client):
    from app.services.squad import SquadError, create_squad, leave_squad

    uid = get_test_user_id()
    with _get_db() as db:
        squad = create_squad(db, uid, "OwnerStays")
        with pytest.raises(SquadError, match="owner"):
            leave_squad(db, squad.id, uid)


# ---------------------------------------------------------------------------
# 9. delete_squad — removes squad
# ---------------------------------------------------------------------------


def test_delete_squad(client):
    from app.services.squad import create_squad, delete_squad, get_squad_or_none

    uid = get_test_user_id()
    with _get_db() as db:
        squad = create_squad(db, uid, "DeleteMe")
        squad_id = squad.id
        delete_squad(db, squad_id, uid)
        assert get_squad_or_none(db, squad_id) is None


# ---------------------------------------------------------------------------
# 10. compute_squad_leaderboard — returns entries for members
# ---------------------------------------------------------------------------


def test_compute_squad_leaderboard(client):
    from app.models.session import SessionExercise, SetLog, WorkoutSession
    from app.services.squad import (
        compute_squad_leaderboard,
        create_squad,
        generate_invite_code,
        join_by_code,
    )

    uid = get_test_user_id()
    with _get_db() as db:
        mate_id = _create_second_user(db)
        squad = create_squad(db, uid, "LeaderTeam")
        code = generate_invite_code(db, squad.id, uid)
        join_by_code(db, mate_id, code)

        # Create a completed session for the owner
        session = WorkoutSession(
            user_id=uid,
            template_slug_snapshot="upper-a",
            template_name_snapshot="Upper A",
            started_at=datetime.now(UTC),
            status="completed",
            excluded_from_stats=False,
            concentration="high",
            global_state="good",
        )
        db.add(session)
        db.flush()

        se = SessionExercise(
            session_id=session.id,
            exercise_code_snapshot="BP",
            exercise_name_snapshot="Bench Press",
            position=1,
            success_score=100,
        )
        db.add(se)
        db.flush()

        sl = SetLog(
            session_exercise_id=se.id,
            kind="work",
            set_index=1,
            weight_kg=80,
            reps=10,
            completed=True,
        )
        db.add(sl)
        db.commit()

        lb = compute_squad_leaderboard(db, squad.id)
        assert len(lb) == 2  # both members appear

        # Owner should be ranked first (has a session)
        owner_entry = next(e for e in lb if e["username"] == "testuser")
        assert owner_entry["rank"] == 1
        assert owner_entry["session_count"] == 1
        assert owner_entry["total_points"] > 0
        assert "grade" in owner_entry
        assert "streak" in owner_entry

        # Mate has 0 sessions
        mate_entry = next(e for e in lb if e["username"] == "squadmate")
        assert mate_entry["session_count"] == 0
        assert mate_entry["total_points"] == 0.0
