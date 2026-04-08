"""Instantiate a fully pre-populated WorkoutSession from a template.

This is the V1 answer to "each exercise in a session must render
input rows usable for both warmup and work sets, as simply as
possible and uniformly across exercises":

- one SessionExercise per TemplateExercise, with name/code snapshots
- `warmup_sets` empty warmup SetLog rows, kind="warmup"
- as many work SetLog rows as the template has RepTargets, kind="work"
- every row pre-created with `completed=False` and null weight/reps

The mobile session page can then just iterate on existing rows and
PATCH them one tap at a time; no row creation logic on the client.

Cardio templates (0 exercises) produce a WorkoutSession with 0
SessionExercise rows — the caller only fills session-level feedback.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.enums import SetKind
from app.models.catalog import WorkoutTemplate
from app.models.session import SessionExercise, SetLog, WorkoutSession

DEFAULT_WARMUP_SETS = 2


def instantiate_session(
    db: Session,
    template: WorkoutTemplate,
    started_at: datetime,
    warmup_sets: int = DEFAULT_WARMUP_SETS,
) -> WorkoutSession:
    """Build (but do not commit) a WorkoutSession pre-seeded with
    warmup + work rows for every exercise of the template.

    The caller is responsible for ``db.add(session)`` (if needed —
    the cascade from the relationships already handles that via the
    back_populates) and ``db.commit()``. We leave the commit out so
    tests can wrap it in a transaction.
    """
    if warmup_sets < 0:
        raise ValueError("warmup_sets must be >= 0")

    session = WorkoutSession(
        template_id=template.id,
        template_slug_snapshot=template.slug,
        template_name_snapshot=template.name,
        started_at=started_at,
    )

    for te in template.exercises:
        se = SessionExercise(
            template_exercise_id=te.id,
            exercise_code_snapshot=te.code,
            exercise_name_snapshot=te.name,
            position=te.position,
        )

        # Warmup rows: uniform count across exercises, empty values.
        for i in range(1, warmup_sets + 1):
            se.set_logs.append(
                SetLog(kind=SetKind.WARMUP, set_index=i, completed=False)
            )

        # Work rows: one per prescribed RepTarget, numbered 1..N.
        for i, _ in enumerate(te.rep_targets, start=1):
            se.set_logs.append(
                SetLog(kind=SetKind.WORK, set_index=i, completed=False)
            )

        session.session_exercises.append(se)

    db.add(session)
    return session
