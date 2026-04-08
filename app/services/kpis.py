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


@dataclass
class RecentExerciseActivity:
    template_slug: str
    template_name: str
    exercise_code: str
    exercise_name: str
    n_sessions_30d: int
    last_done_at: datetime
    last_weights_str: str
    last_reps_str: str


def _fmt_weight(w: Optional[float]) -> str:
    if w is None:
        return "—"
    if w == int(w):
        return str(int(w))
    return f"{w:g}"


def compute_recent_exercise_activity(
    db: Session,
    *,
    limit: int = 10,
    now: Optional[datetime] = None,
) -> list[RecentExerciseActivity]:
    """Last N exercise codes (across all templates) with completed
    work sets in the trailing 30 days, most recent first.

    Intentionally compact: one row per
    (template_slug_snapshot, exercise_code_snapshot), summarising the
    most recent completed work sets. Feeds the /progress "Activité
    récente par exercice" section.

    Rules:
      - only `completed` sessions enter the aggregate
      - only `work` sets are summarised (warmups ignored)
      - only completed work sets contribute to the weight/reps strings
      - window = 30 days back from `now`
    """
    from app.models.session import SessionExercise, SetLog

    now = now or datetime.now(timezone.utc)
    window_start = now - timedelta(days=30)

    # Fetch all SessionExercise rows of completed sessions in the
    # window, eager-load their parent session and their set_logs.
    stmt = (
        select(SessionExercise)
        .join(WorkoutSession, WorkoutSession.id == SessionExercise.session_id)
        .where(WorkoutSession.status == "completed")
        .where(WorkoutSession.started_at >= window_start)
        .order_by(WorkoutSession.started_at.desc())
    )
    rows = db.execute(stmt).scalars().all()
    # Eager-load parent + set_logs in separate queries to avoid
    # an explosion of cartesian products.
    if rows:
        ids = [r.id for r in rows]
        set_rows = db.execute(
            select(SetLog).where(SetLog.session_exercise_id.in_(ids))
        ).scalars().all()
        by_se: dict[int, list] = {}
        for sl in set_rows:
            by_se.setdefault(sl.session_exercise_id, []).append(sl)
        sess_ids = {r.session_id for r in rows}
        sess_rows = db.execute(
            select(WorkoutSession).where(WorkoutSession.id.in_(sess_ids))
        ).scalars().all()
        by_sid = {s.id: s for s in sess_rows}
    else:
        by_se = {}
        by_sid = {}

    # Group by (template_slug, code); keep the most recent hit.
    grouped: dict[tuple[str, str], dict] = {}
    for se in rows:
        parent = by_sid.get(se.session_id)
        if parent is None:
            continue
        key = (parent.template_slug_snapshot, se.exercise_code_snapshot)
        entry = grouped.setdefault(
            key,
            {
                "template_name": parent.template_name_snapshot,
                "exercise_name": se.exercise_name_snapshot,
                "n": 0,
                "last_done_at": parent.started_at,
                "last_se": se,
            },
        )
        entry["n"] += 1
        if parent.started_at > entry["last_done_at"]:
            entry["last_done_at"] = parent.started_at
            entry["last_se"] = se

    def _build(key, entry) -> RecentExerciseActivity:
        slug, code = key
        last_se = entry["last_se"]
        done_work = sorted(
            (
                sl
                for sl in by_se.get(last_se.id, [])
                if sl.kind == "work" and sl.completed
            ),
            key=lambda s: s.set_index,
        )
        weights_str = " / ".join(_fmt_weight(sl.weight_kg) for sl in done_work)
        reps_str = " / ".join(
            ("—" if sl.reps is None else str(sl.reps)) for sl in done_work
        )
        return RecentExerciseActivity(
            template_slug=slug,
            template_name=entry["template_name"],
            exercise_code=code,
            exercise_name=entry["exercise_name"],
            n_sessions_30d=entry["n"],
            last_done_at=entry["last_done_at"],
            last_weights_str=weights_str,
            last_reps_str=reps_str,
        )

    out = [_build(k, v) for k, v in grouped.items()]
    out.sort(key=lambda a: a.last_done_at, reverse=True)
    return out[:limit]


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
