"""Squad challenge service — create, list, and compute standings."""
from __future__ import annotations

from collections import defaultdict
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.challenge import SquadChallenge
from app.models.session import SessionExercise, SetLog, WorkoutSession
from app.models.squad import SquadMembership
from app.models.user import User
from app.services.quality_score import compute_session_quality


class ChallengeError(Exception):
    """Raised on invalid challenge operations."""


VALID_METRICS = {"sessions", "score", "tonnage", "streak"}

_METRIC_LABELS = {
    "sessions": "séances",
    "score": "points",
    "tonnage": "kg",
    "streak": "jours",
}


def create_challenge(
    db: Session,
    squad_id: int,
    created_by: int,
    title: str,
    metric: str,
    starts_at: date,
    ends_at: date,
) -> SquadChallenge:
    """Create a new challenge for a squad."""
    if not title or not title.strip():
        raise ChallengeError("Le titre est obligatoire.")
    if metric not in VALID_METRICS:
        raise ChallengeError(f"Métrique invalide : {metric}")
    if ends_at <= starts_at:
        raise ChallengeError("La date de fin doit être après la date de début.")

    challenge = SquadChallenge(
        squad_id=squad_id,
        created_by=created_by,
        title=title.strip(),
        metric=metric,
        starts_at=starts_at,
        ends_at=ends_at,
    )
    db.add(challenge)
    db.commit()
    db.refresh(challenge)
    return challenge


def get_squad_challenges(db: Session, squad_id: int) -> list[SquadChallenge]:
    """Return all challenges for a squad, most recent first."""
    return list(
        db.execute(
            select(SquadChallenge)
            .where(SquadChallenge.squad_id == squad_id)
            .order_by(SquadChallenge.starts_at.desc())
        )
        .scalars()
        .all()
    )


def get_challenge_or_none(db: Session, challenge_id: int) -> SquadChallenge | None:
    """Return a challenge by ID, or None."""
    return db.get(SquadChallenge, challenge_id)


def compute_standings(db: Session, challenge: SquadChallenge) -> list[dict]:
    """Compute ranked standings for a challenge.

    Returns list of dicts: {rank, username, value} sorted by value desc.
    """
    # Get squad members
    members = db.execute(
        select(SquadMembership.user_id, User.username)
        .join(User, User.id == SquadMembership.user_id)
        .where(SquadMembership.squad_id == challenge.squad_id)
    ).all()

    results: list[tuple[str, float]] = []

    for member in members:
        uid = member.user_id
        uname = member.username

        # Fetch sessions in the challenge window
        sessions = (
            db.execute(
                select(WorkoutSession)
                .where(
                    WorkoutSession.user_id == uid,
                    WorkoutSession.status == "completed",
                    WorkoutSession.excluded_from_stats.is_(False),
                    WorkoutSession.started_at >= _date_to_datetime_start(challenge.starts_at),
                    WorkoutSession.started_at < _date_to_datetime_end(challenge.ends_at),
                )
                .options(
                    selectinload(WorkoutSession.session_exercises)
                    .selectinload(SessionExercise.set_logs)
                )
                .order_by(WorkoutSession.started_at)
            )
            .scalars()
            .all()
        )

        value = _compute_metric(challenge.metric, sessions)
        results.append((uname, value))

    # Sort by value desc, then username asc for ties
    results.sort(key=lambda x: (-x[1], x[0]))

    standings = []
    for i, (uname, value) in enumerate(results, start=1):
        standings.append({"rank": i, "username": uname, "value": value})
    return standings


def _date_to_datetime_start(d: date):
    """Convert a date to a datetime at midnight for range filtering."""
    from datetime import datetime, timezone
    return datetime(d.year, d.month, d.day, tzinfo=timezone.utc)


def _date_to_datetime_end(d: date):
    """Convert a date to a datetime at end of day (next day midnight)."""
    from datetime import datetime, timedelta, timezone
    next_day = d + timedelta(days=1)
    return datetime(next_day.year, next_day.month, next_day.day, tzinfo=timezone.utc)


def _compute_metric(metric: str, sessions: list) -> float:
    """Compute the metric value for a list of sessions."""
    if metric == "sessions":
        return float(len(sessions))

    if metric == "score":
        total = 0.0
        for s in sessions:
            total_work = sum(
                1 for se in s.session_exercises
                for sl in se.set_logs if sl.kind == "work"
            )
            if total_work == 0:
                continue
            done_work = sum(
                1 for se in s.session_exercises
                for sl in se.set_logs if sl.kind == "work" and sl.completed
            )
            quality = compute_session_quality(s)
            completion_ratio = done_work / total_work
            total += quality * completion_ratio
        return total

    if metric == "tonnage":
        total = 0.0
        for s in sessions:
            for se in s.session_exercises:
                for sl in se.set_logs:
                    if sl.kind == "work" and sl.completed and sl.weight_kg and sl.reps:
                        total += sl.weight_kg * sl.reps
        return total

    if metric == "streak":
        # Longest consecutive days with a session in the window
        if not sessions:
            return 0.0
        dates = sorted({s.started_at.date() for s in sessions})
        longest = 1
        current = 1
        for i in range(1, len(dates)):
            if (dates[i] - dates[i - 1]).days == 1:
                current += 1
                longest = max(longest, current)
            else:
                current = 1
        return float(longest)

    return 0.0
