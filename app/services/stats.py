"""Read-side helpers for the session detail page.

In V1 the only consumer is the "Dernière fois" block rendered per
exercise card. The lookup is:
  - identity = (template_slug_snapshot, exercise_code_snapshot)
  - scope    = prior sessions only (strictly excluding the current one)
  - source   = work sets only (warmups never count)

The function returns a dict keyed by `exercise_code_snapshot`, so the
view can match it against each SessionExercise on the page in O(1).
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional  # noqa: F401  (used below)

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.session import SessionExercise, WorkoutSession


def _fmt_weight(w: Optional[float]) -> str:
    if w is None:
        return "—"
    # Drop .0 tails so "60.0" renders as "60"
    if w == int(w):
        return str(int(w))
    return f"{w:g}"


def _fmt_reps(r: Optional[int]) -> str:
    return "—" if r is None else str(r)


def _relative_when(now: datetime, then: datetime) -> str:
    # SQLite round-trips DATETIMEs as naive. Coerce both sides to a
    # common frame so arithmetic is safe regardless of the dialect.
    if then.tzinfo is None and now.tzinfo is not None:
        then = then.replace(tzinfo=now.tzinfo)
    elif now.tzinfo is None and then.tzinfo is not None:
        now = now.replace(tzinfo=then.tzinfo)
    delta = now - then
    days = delta.days
    if days < 0:
        return "à venir"
    if days == 0:
        return "aujourd'hui"
    if days == 1:
        return "hier"
    if days < 7:
        return f"il y a {days} j"
    if days < 30:
        weeks = days // 7
        return f"il y a {weeks} sem"
    months = days // 30
    return f"il y a {months} mois"


def _summarise_prior(prior: SessionExercise, now: datetime) -> dict:
    """Turn a prior SessionExercise into a display-ready dict."""
    work = sorted(
        (sl for sl in prior.set_logs if sl.kind == "work"),
        key=lambda s: s.set_index,
    )
    # Only completed sets contribute to the summary strings, but we
    # still need to know if the prior session had any work data at all.
    done = [sl for sl in work if sl.completed and (sl.weight_kg is not None or sl.reps is not None)]

    has_data = len(done) > 0
    first_set = None
    if has_data:
        sl = done[0]
        first_set = {"weight_kg": sl.weight_kg, "reps": sl.reps}

    return {
        "relative": _relative_when(now, prior.session.started_at),
        "started_at": prior.session.started_at,
        "session_id": prior.session.id,
        "has_data": has_data,
        "weights_str": " / ".join(_fmt_weight(sl.weight_kg) for sl in done) if has_data else "",
        "reps_str": " / ".join(_fmt_reps(sl.reps) for sl in done) if has_data else "",
        "n_work_sets": len(work),
        "n_done": len(done),
        "first_set": first_set,
        "success_score": prior.success_score,
    }


def summarise_current_exercise(se: SessionExercise) -> Optional[dict]:
    """Compact summary of what was actually performed on a
    SessionExercise. Used by the completed-session readability block.

    Returns None if no work set has been marked completed — nothing
    to show for an untouched exercise.
    """
    work = sorted(
        (sl for sl in se.set_logs if sl.kind == "work"),
        key=lambda s: s.set_index,
    )
    done = [sl for sl in work if sl.completed]
    if not done:
        return None
    return {
        "work_done": len(done),
        "work_total": len(work),
        "weights_str": " / ".join(_fmt_weight(sl.weight_kg) for sl in done),
        "reps_str": " / ".join(_fmt_reps(sl.reps) for sl in done),
        "success_score": se.success_score,
        "muscle_sensation": se.muscle_sensation,
    }


def last_time_by_exercise_code(
    db: Session,
    current_session: WorkoutSession,
    now: datetime,
) -> dict[str, dict]:
    """Return a dict mapping exercise_code_snapshot -> prior summary.

    Codes that have no prior match are simply absent from the dict.
    The caller decides how to render the empty case.

    V1 identity key: (template_slug_snapshot, exercise_code_snapshot).
    Sessions from other templates never contribute — doing so would
    merge "E2 Incline Smith" with "E2 Tirage nuque" etc.
    """
    # One query that fetches every prior SessionExercise of the same
    # template, ordered by session started_at desc, with its parent
    # session and its set_logs eagerly loaded. We then walk the list
    # in Python and keep only the first hit per exercise code.
    stmt = (
        select(SessionExercise)
        .join(WorkoutSession, WorkoutSession.id == SessionExercise.session_id)
        .where(
            WorkoutSession.id != current_session.id,
            WorkoutSession.template_slug_snapshot == current_session.template_slug_snapshot,
        )
        .options(
            selectinload(SessionExercise.set_logs),
            joinedload(SessionExercise.session),
        )
        .order_by(WorkoutSession.started_at.desc())
    )

    result: dict[str, dict] = {}
    for prior in db.execute(stmt).unique().scalars().all():
        code = prior.exercise_code_snapshot
        if code in result:
            continue  # we already have a more recent one
        result[code] = _summarise_prior(prior, now)
    return result
