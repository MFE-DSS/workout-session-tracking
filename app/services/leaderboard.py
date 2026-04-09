"""Leaderboard scoring and ranking.

Score rule (documented in docs/PRODUCT_SPEC.md):

For each eligible session:
  - status == "completed"
  - excluded_from_stats == False
  - total_work_sets > 0

  session_points = session_quality_score
                   × (completed_work_sets / total_work_sets)

  This rewards both quality AND completion. A 100-quality session
  with only 50% of work sets done earns 50 points, not 100.

Per user:
  total_points = sum(session_points) across all eligible sessions
  counted_sessions = number of eligible sessions
  avg_points = total_points / counted_sessions (if > 0)

Tie handling: users with equal total_points are ordered by
username ASC (deterministic, alphabetical). Documented.

The function queries ALL users, not just the current one. It
returns aggregated ranking data only — no private session detail.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.session import SessionExercise, WorkoutSession
from app.models.user import User
from app.services.quality_score import compute_session_quality


@dataclass
class LeaderboardEntry:
    rank: int
    username: str
    total_points: float
    counted_sessions: int
    avg_points: Optional[float]


def compute_leaderboard(db: Session) -> list[LeaderboardEntry]:
    """Compute the full leaderboard across all active users."""
    users = db.execute(
        select(User).where(User.is_active.is_(True))
    ).scalars().all()

    raw: list[tuple[str, float, int]] = []

    for user in users:
        sessions = db.execute(
            select(WorkoutSession)
            .where(
                WorkoutSession.user_id == user.id,
                WorkoutSession.status == "completed",
                WorkoutSession.excluded_from_stats.is_(False),
            )
            .options(
                selectinload(WorkoutSession.session_exercises)
                .selectinload(SessionExercise.set_logs)
            )
        ).scalars().all()

        total_pts = 0.0
        counted = 0
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
            session_pts = quality * completion_ratio
            total_pts += session_pts
            counted += 1

        raw.append((user.username, total_pts, counted))

    # Sort: highest total_points first, then username ASC for ties.
    raw.sort(key=lambda x: (-x[1], x[0]))

    entries: list[LeaderboardEntry] = []
    for i, (username, pts, counted) in enumerate(raw, start=1):
        entries.append(LeaderboardEntry(
            rank=i,
            username=username,
            total_points=round(pts, 1),
            counted_sessions=counted,
            avg_points=round(pts / counted, 1) if counted > 0 else None,
        ))
    return entries
