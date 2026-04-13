"""Squad service: CRUD, invite codes, join/leave, scoped leaderboard.

Business rules:
- Squad names must be unique (case-sensitive).
- Only the owner can generate invite codes or delete the squad.
- Invite codes follow the format SPGN-XXXX (4 uppercase alphanumeric).
- Codes expire after 48 hours and are single-use.
- The owner cannot leave their own squad (must delete instead).
- Scoped leaderboard uses the same scoring formula as the global
  leaderboard but is restricted to squad members.
"""
from __future__ import annotations

import random
import string
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.session import SessionExercise, WorkoutSession
from app.models.squad import Squad, SquadInviteCode, SquadMembership
from app.models.user import User
from app.services.performance import GRADE_LABELS, compute_grade
from app.services.quality_score import compute_session_quality


class SquadError(Exception):
    """Raised for squad business rule violations."""

    pass


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------


def create_squad(db: Session, owner_id: int, name: str) -> Squad:
    """Create a squad and add the owner as the first member."""
    name = (name or "").strip()
    if not name:
        raise SquadError("Le nom de la squad ne peut pas être vide")

    existing = db.execute(
        select(Squad).where(Squad.name == name)
    ).scalar_one_or_none()
    if existing:
        raise SquadError("existe déjà")

    squad = Squad(name=name, owner_id=owner_id)
    db.add(squad)
    db.flush()

    membership = SquadMembership(
        squad_id=squad.id, user_id=owner_id, role="owner"
    )
    db.add(membership)
    db.commit()
    db.refresh(squad)
    return squad


def get_user_squads(db: Session, user_id: int) -> list[Squad]:
    """Return all squads where the user is a member."""
    return list(
        db.execute(
            select(Squad)
            .join(SquadMembership, SquadMembership.squad_id == Squad.id)
            .where(SquadMembership.user_id == user_id)
        )
        .scalars()
        .all()
    )


def get_squad_or_none(db: Session, squad_id: int) -> Optional[Squad]:
    """Return a squad by id or None."""
    return db.execute(
        select(Squad).where(Squad.id == squad_id)
    ).scalar_one_or_none()


def is_member(db: Session, squad_id: int, user_id: int) -> bool:
    """Check if a user is a member of a squad."""
    return get_membership(db, squad_id, user_id) is not None


def get_membership(
    db: Session, squad_id: int, user_id: int
) -> Optional[SquadMembership]:
    """Return the membership record or None."""
    return db.execute(
        select(SquadMembership).where(
            SquadMembership.squad_id == squad_id,
            SquadMembership.user_id == user_id,
        )
    ).scalar_one_or_none()


def get_squad_members(db: Session, squad_id: int) -> list[dict]:
    """Return squad members with user details."""
    rows = (
        db.execute(
            select(
                SquadMembership.user_id,
                User.username,
                SquadMembership.role,
                SquadMembership.joined_at,
            )
            .join(User, User.id == SquadMembership.user_id)
            .where(SquadMembership.squad_id == squad_id)
        )
        .all()
    )
    return [
        {
            "user_id": r.user_id,
            "username": r.username,
            "role": r.role,
            "joined_at": r.joined_at,
        }
        for r in rows
    ]


def delete_squad(db: Session, squad_id: int, owner_id: int) -> None:
    """Delete a squad. Only the owner may do this."""
    squad = db.execute(
        select(Squad).where(Squad.id == squad_id)
    ).scalar_one_or_none()
    if not squad:
        raise SquadError("Squad introuvable")
    if squad.owner_id != owner_id:
        raise SquadError("Seul le propriétaire peut supprimer la squad")
    db.delete(squad)
    db.commit()


# ---------------------------------------------------------------------------
# Invitation
# ---------------------------------------------------------------------------

_CODE_CHARS = string.ascii_uppercase + string.digits


def _random_code() -> str:
    return "SPGN-" + "".join(random.choices(_CODE_CHARS, k=4))


def generate_invite_code(db: Session, squad_id: int, owner_id: int) -> str:
    """Generate a unique invite code for a squad (owner only)."""
    squad = db.execute(
        select(Squad).where(Squad.id == squad_id)
    ).scalar_one_or_none()
    if not squad:
        raise SquadError("Squad introuvable")
    if squad.owner_id != owner_id:
        raise SquadError("Seul le propriétaire peut générer un code")

    for _ in range(5):
        code = _random_code()
        exists = db.execute(
            select(SquadInviteCode).where(SquadInviteCode.code == code)
        ).scalar_one_or_none()
        if not exists:
            invite = SquadInviteCode(
                squad_id=squad_id,
                code=code,
                created_by=owner_id,
                expires_at=datetime.now(timezone.utc) + timedelta(hours=48),
            )
            db.add(invite)
            db.commit()
            return code

    raise SquadError("Impossible de générer un code unique")


def join_by_code(db: Session, user_id: int, code: str) -> Squad:
    """Join a squad using an invite code."""
    invite = db.execute(
        select(SquadInviteCode).where(SquadInviteCode.code == code)
    ).scalar_one_or_none()
    if not invite:
        raise SquadError("Code invalide")

    if invite.used_by is not None:
        raise SquadError("Code déjà utilisé")

    # Handle timezone-naive datetimes from SQLite
    expires = invite.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < datetime.now(timezone.utc):
        raise SquadError("Code expiré")

    if is_member(db, invite.squad_id, user_id):
        raise SquadError("Déjà membre de cette squad")

    membership = SquadMembership(
        squad_id=invite.squad_id, user_id=user_id, role="member"
    )
    db.add(membership)

    invite.used_by = user_id
    invite.used_at = datetime.now(timezone.utc)
    db.commit()

    return db.execute(
        select(Squad).where(Squad.id == invite.squad_id)
    ).scalar_one()


# ---------------------------------------------------------------------------
# Membership
# ---------------------------------------------------------------------------


def leave_squad(db: Session, squad_id: int, user_id: int) -> None:
    """Leave a squad. The owner cannot leave (must delete instead)."""
    membership = get_membership(db, squad_id, user_id)
    if not membership:
        raise SquadError("Pas membre de cette squad")
    if membership.role == "owner":
        raise SquadError("owner")
    db.delete(membership)
    db.commit()


# ---------------------------------------------------------------------------
# Scoped leaderboard
# ---------------------------------------------------------------------------


def compute_squad_leaderboard(db: Session, squad_id: int) -> list[dict]:
    """Compute leaderboard restricted to squad members."""
    members = db.execute(
        select(SquadMembership.user_id, User.username)
        .join(User, User.id == SquadMembership.user_id)
        .where(SquadMembership.squad_id == squad_id)
    ).all()

    raw: list[tuple[str, float, int, Optional[str], Optional[str], int]] = []

    for member in members:
        uid = member.user_id
        uname = member.username

        sessions = (
            db.execute(
                select(WorkoutSession)
                .where(
                    WorkoutSession.user_id == uid,
                    WorkoutSession.status == "completed",
                    WorkoutSession.excluded_from_stats.is_(False),
                )
                .options(
                    selectinload(WorkoutSession.session_exercises).selectinload(
                        SessionExercise.set_logs
                    )
                )
                .order_by(WorkoutSession.started_at.desc())
            )
            .scalars()
            .all()
        )

        total_pts = 0.0
        counted = 0
        last_date: Optional[str] = None
        last_template: Optional[str] = None

        for s in sessions:
            total_work = sum(
                1
                for se in s.session_exercises
                for sl in se.set_logs
                if sl.kind == "work"
            )
            if total_work == 0:
                continue
            done_work = sum(
                1
                for se in s.session_exercises
                for sl in se.set_logs
                if sl.kind == "work" and sl.completed
            )
            quality = compute_session_quality(s)
            completion_ratio = done_work / total_work
            session_pts = quality * completion_ratio
            total_pts += session_pts
            counted += 1

            if last_date is None:
                last_date = s.started_at.strftime("%Y-%m-%d")
                last_template = s.template_name_snapshot

        # Streak: consecutive days with sessions from today backwards
        streak = _compute_streak(db, uid)

        raw.append((uname, total_pts, counted, last_date, last_template, streak))

    # Sort by total_points desc, username asc
    raw.sort(key=lambda x: (-x[1], x[0]))

    entries: list[dict] = []
    for i, (uname, pts, counted, last_date, last_tpl, streak) in enumerate(
        raw, start=1
    ):
        avg = round(pts / counted, 1) if counted > 0 else 0.0
        grade = compute_grade(avg, counted)
        entries.append(
            {
                "rank": i,
                "username": uname,
                "total_points": round(pts, 1),
                "avg_points": avg,
                "grade": grade,
                "grade_label": GRADE_LABELS.get(grade, ""),
                "session_count": counted,
                "last_session_date": last_date,
                "last_session_template": last_tpl,
                "streak": streak,
            }
        )
    return entries


def _compute_streak(db: Session, user_id: int) -> int:
    """Count consecutive days with at least one session, from today backwards."""
    sessions = (
        db.execute(
            select(WorkoutSession.started_at)
            .where(
                WorkoutSession.user_id == user_id,
                WorkoutSession.status == "completed",
                WorkoutSession.excluded_from_stats.is_(False),
            )
            .order_by(WorkoutSession.started_at.desc())
        )
        .scalars()
        .all()
    )
    if not sessions:
        return 0

    # Collect unique dates
    dates = sorted({s.date() for s in sessions}, reverse=True)
    today = datetime.now(timezone.utc).date()

    streak = 0
    expected = today
    for d in dates:
        if d == expected:
            streak += 1
            expected = expected - timedelta(days=1)
        elif d < expected:
            break
    return streak
