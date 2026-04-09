"""Read-side helper for the Exercise History Detail page.

Returns an ordered list of SessionExercise occurrences matching
a single `(template_slug_snapshot, exercise_code_snapshot)`
identity, with per-row deltas precomputed.

Scope rules (documented in docs/PRODUCT_SPEC.md):

- **Identity**: `(template_slug_snapshot, exercise_code_snapshot)`.
  Deliberately does not merge exercises across templates.
- **Included sessions**: both `in_progress` and `completed`. The
  status is rendered so the user can tell them apart.
- **Ordering**: newest first (`started_at DESC`).
- **Delta per row**: compared against the NEXT-OLDER row's first
  completed work set. If either side has no first completed work
  set, the delta is None.
- **first_set**: the first completed work set of each row (by
  set_index). Used both for delta computation and the per-row
  summary strings.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.session import SessionExercise, WorkoutSession
from app.services.delta import Delta, compute_delta, format_delta


def _fmt_weight(w: Optional[float]) -> str:
    if w is None:
        return "—"
    if w == int(w):
        return str(int(w))
    return f"{w:g}"


@dataclass
class ExerciseHistoryEntry:
    session_id: int
    started_at: datetime
    status: str
    weights_str: str  # joined, completed work sets only
    reps_str: str
    success_score: Optional[int]
    muscle_sensation: Optional[str]
    first_weight: Optional[float]
    first_reps: Optional[int]
    delta: Optional[Delta]
    delta_label: Optional[str]  # pre-rendered for the template


def _summarise(se: SessionExercise) -> tuple[ExerciseHistoryEntry, Optional[float], Optional[int]]:
    work = sorted(
        (sl for sl in se.set_logs if sl.kind == "work"),
        key=lambda s: s.set_index,
    )
    done = [
        sl for sl in work
        if sl.completed and (sl.weight_kg is not None or sl.reps is not None)
    ]
    first_w = done[0].weight_kg if done else None
    first_r = done[0].reps if done else None
    entry = ExerciseHistoryEntry(
        session_id=se.session_id,
        started_at=se.session.started_at,
        status=se.session.status,
        weights_str=" / ".join(_fmt_weight(sl.weight_kg) for sl in done),
        reps_str=" / ".join(
            ("—" if sl.reps is None else str(sl.reps)) for sl in done
        ),
        success_score=se.success_score,
        muscle_sensation=se.muscle_sensation,
        first_weight=first_w,
        first_reps=first_r,
        delta=None,
        delta_label=None,
    )
    return entry, first_w, first_r


def get_exercise_history(
    db: Session,
    template_slug: str,
    exercise_code: str,
    *,
    user_id: int | None = None,
) -> list[ExerciseHistoryEntry]:
    """Return the history entries (newest first) for a given
    exercise identity, with deltas precomputed row-by-row."""
    stmt = (
        select(SessionExercise)
        .join(WorkoutSession, WorkoutSession.id == SessionExercise.session_id)
        .where(
            WorkoutSession.template_slug_snapshot == template_slug,
            SessionExercise.exercise_code_snapshot == exercise_code,
            WorkoutSession.user_id == user_id if user_id is not None else True,
        )
        .options(
            selectinload(SessionExercise.set_logs),
            joinedload(SessionExercise.session),
        )
        .order_by(WorkoutSession.started_at.desc())
    )
    ses = db.execute(stmt).unique().scalars().all()
    entries: list[ExerciseHistoryEntry] = []
    for se in ses:
        entry, _, _ = _summarise(se)
        entries.append(entry)

    # Deltas: for each row i, compare against row i+1 (next older)
    # when both rows have a first_completed_work_set.
    for i, entry in enumerate(entries):
        if i + 1 >= len(entries):
            continue
        older = entries[i + 1]
        if entry.first_weight is None and entry.first_reps is None:
            continue
        if older.first_weight is None and older.first_reps is None:
            continue
        entry.delta = compute_delta(
            entry.first_weight,
            entry.first_reps,
            entry.success_score,
            older.first_weight,
            older.first_reps,
            older.success_score,
        )
        entry.delta_label = format_delta(entry.delta)

    return entries
