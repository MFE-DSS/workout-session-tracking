"""KPI aggregation for the /progress page.

**KPI rules (all explicit, see docs/PRODUCT_SPEC.md):**

- Work set completion rate counts only `SetLog.kind == "work"`.
  Warmup rows never contribute to the denominator OR the numerator.
- Average success score counts only `SessionExercise.success_score`
  rows where the value is not NULL. NULLs mean "not rated" and are
  excluded from the mean entirely (not treated as 0 or anything).
- The "last 30 days" window is `now - 30d`, no timezone tricks.
- **In-progress sessions are excluded** from the long-term KPIs
  (`completion_rate_30d`, `avg_success_score_30d`, `completed_last_30`).
  They would otherwise drag the completion rate down with unfilled
  rows that simply haven't been touched yet.
- `sessions_this_week` and `total_sessions` include every session
  regardless of status — they answer the question "how often am I
  opening the app", which must not depend on whether I pressed
  *Terminer* at the end.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.session import SessionExercise, SetLog, WorkoutSession


@dataclass
class GlobalKPIs:
    total_sessions: int
    completed_total: int
    sessions_this_week: int
    sessions_last_30: int
    completed_last_30: int
    avg_success_score_30d: Optional[float]
    completion_rate_30d: Optional[float]
    work_sets_done_30d: int
    work_sets_total_30d: int


def _start_of_iso_week(now: datetime) -> datetime:
    """Midnight UTC at the start of the current ISO week (Monday)."""
    monday = now - timedelta(days=now.isoweekday() - 1)
    return monday.replace(hour=0, minute=0, second=0, microsecond=0)


def compute_global_kpis(
    db: Session, now: Optional[datetime] = None
) -> GlobalKPIs:
    now = now or datetime.now(timezone.utc)
    week_start = _start_of_iso_week(now)
    window_start = now - timedelta(days=30)

    total_sessions = db.execute(
        select(func.count(WorkoutSession.id))
    ).scalar_one() or 0

    completed_total = db.execute(
        select(func.count(WorkoutSession.id)).where(
            WorkoutSession.status == "completed"
        )
    ).scalar_one() or 0

    sessions_this_week = db.execute(
        select(func.count(WorkoutSession.id)).where(
            WorkoutSession.started_at >= week_start
        )
    ).scalar_one() or 0

    sessions_last_30 = db.execute(
        select(func.count(WorkoutSession.id)).where(
            WorkoutSession.started_at >= window_start
        )
    ).scalar_one() or 0

    completed_last_30 = db.execute(
        select(func.count(WorkoutSession.id))
        .where(WorkoutSession.started_at >= window_start)
        .where(WorkoutSession.status == "completed")
    ).scalar_one() or 0

    # Average success score: 30d window, completed sessions only,
    # NULL success_scores excluded by the WHERE clause.
    avg_success_score = db.execute(
        select(func.avg(SessionExercise.success_score))
        .join(WorkoutSession, WorkoutSession.id == SessionExercise.session_id)
        .where(WorkoutSession.started_at >= window_start)
        .where(WorkoutSession.status == "completed")
        .where(SessionExercise.success_score.is_not(None))
    ).scalar()

    # Work set completion rate: 30d window, completed sessions only,
    # warmups never counted.
    work_sets_total = db.execute(
        select(func.count(SetLog.id))
        .join(SessionExercise, SessionExercise.id == SetLog.session_exercise_id)
        .join(WorkoutSession, WorkoutSession.id == SessionExercise.session_id)
        .where(SetLog.kind == "work")
        .where(WorkoutSession.started_at >= window_start)
        .where(WorkoutSession.status == "completed")
    ).scalar_one() or 0

    work_sets_done = db.execute(
        select(func.count(SetLog.id))
        .join(SessionExercise, SessionExercise.id == SetLog.session_exercise_id)
        .join(WorkoutSession, WorkoutSession.id == SessionExercise.session_id)
        .where(SetLog.kind == "work")
        .where(SetLog.completed.is_(True))
        .where(WorkoutSession.started_at >= window_start)
        .where(WorkoutSession.status == "completed")
    ).scalar_one() or 0

    completion_rate = (
        (work_sets_done / work_sets_total) if work_sets_total > 0 else None
    )

    return GlobalKPIs(
        total_sessions=total_sessions,
        completed_total=completed_total,
        sessions_this_week=sessions_this_week,
        sessions_last_30=sessions_last_30,
        completed_last_30=completed_last_30,
        avg_success_score_30d=float(avg_success_score)
        if avg_success_score is not None
        else None,
        completion_rate_30d=completion_rate,
        work_sets_done_30d=work_sets_done,
        work_sets_total_30d=work_sets_total,
    )


@dataclass
class TemplateKPI:
    slug: str
    name: str
    n_completed: int
    last_done_at: Optional[datetime]
    avg_success_score: Optional[float]


def compute_template_kpis(db: Session) -> list[TemplateKPI]:
    """Per-template summary: number of completed sessions, when the
    last one happened, and the average success score across all its
    logged exercises. Keyed on `template_slug_snapshot` so reseeded
    templates still show up coherently.
    """
    stmt = (
        select(
            WorkoutSession.template_slug_snapshot.label("slug"),
            WorkoutSession.template_name_snapshot.label("name"),
            func.count(WorkoutSession.id.distinct()).label("n_completed"),
            func.max(WorkoutSession.started_at).label("last_done_at"),
            func.avg(SessionExercise.success_score).label("avg_success_score"),
        )
        .outerjoin(
            SessionExercise, SessionExercise.session_id == WorkoutSession.id
        )
        .where(WorkoutSession.status == "completed")
        .group_by(
            WorkoutSession.template_slug_snapshot,
            WorkoutSession.template_name_snapshot,
        )
        .order_by(func.max(WorkoutSession.started_at).desc())
    )
    rows = db.execute(stmt).all()
    return [
        TemplateKPI(
            slug=r.slug,
            name=r.name,
            n_completed=r.n_completed,
            last_done_at=r.last_done_at,
            avg_success_score=float(r.avg_success_score)
            if r.avg_success_score is not None
            else None,
        )
        for r in rows
    ]
