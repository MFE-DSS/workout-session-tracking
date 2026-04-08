"""Session creation + logging routes.

Architecture note (V1): the session detail page uses **one form per
exercise card** and **one small form for the session-level feedback**.
No per-set PATCH. Justification: on mobile, a user fills an exercise
(warmup + work sets + exercise feedback) in a single block; submitting
that whole block at once is:
  - less round-trips (no PATCH storm)
  - no JS dependency
  - robust to flaky gym connectivity
  - still small per form (an exercise has at most ~8 inputs x 5 rows)

If the product ever needs finer granularity (live set completion on a
smartwatch, for example), a PATCH layer can be added on top without
touching this router.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.enums import (
    ExerciseSuccessScore,
    MuscleSensation,
    SessionConcentration,
    SessionGlobalState,
    SessionStatus,
    SetExecutionQuality,
    SetRepsTarget,
)
from app.models.catalog import MethodRule, TemplateExercise, WorkoutTemplate
from app.models.session import SessionExercise, WorkoutSession
from app.services.form_parsing import (
    checkbox,
    clean_str,
    enum_int,
    enum_str,
    to_float,
    to_int,
)
from app.services.session_builder import instantiate_session
from app.services.stats import last_time_by_exercise_code
from app.templating import templates

router = APIRouter(tags=["sessions"])


# Whitelists derived from app.enums once, reused in form parsing.
_CONCENTRATION = {e.value for e in SessionConcentration}
_GLOBAL_STATE = {e.value for e in SessionGlobalState}
_MUSCLE_SENSATION = {e.value for e in MuscleSensation}
_EXECUTION_QUALITY = {e.value for e in SetExecutionQuality}
_REPS_TARGET = {e.value for e in SetRepsTarget}
_SUCCESS_SCORE = {int(e) for e in ExerciseSuccessScore}


# ----------------------------------------------------------------------
# Create
# ----------------------------------------------------------------------


@router.post("/sessions")
def create_session(
    template_slug: str = Form(...),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    tpl = db.execute(
        select(WorkoutTemplate)
        .where(WorkoutTemplate.slug == template_slug)
        .options(
            selectinload(WorkoutTemplate.exercises).selectinload(
                TemplateExercise.rep_targets
            )
        )
    ).scalar_one_or_none()
    if tpl is None:
        raise HTTPException(status_code=404, detail="Unknown template")

    session = instantiate_session(db, tpl, datetime.now(timezone.utc))
    db.commit()
    db.refresh(session)
    return RedirectResponse(
        url=f"/sessions/{session.id}", status_code=303
    )


# ----------------------------------------------------------------------
# Read
# ----------------------------------------------------------------------


def _load_session(db: Session, session_id: int) -> WorkoutSession | None:
    stmt = (
        select(WorkoutSession)
        .where(WorkoutSession.id == session_id)
        .options(
            selectinload(WorkoutSession.session_exercises)
            .selectinload(SessionExercise.set_logs),
            selectinload(WorkoutSession.session_exercises)
            .selectinload(SessionExercise.template_exercise),
        )
    )
    return db.execute(stmt).scalar_one_or_none()


def _session_stats(session: WorkoutSession) -> dict:
    """Per-exercise and global counts of completed work sets."""
    per_exercise: dict[int, tuple[int, int]] = {}
    for se in session.session_exercises:
        work_sets = [sl for sl in se.set_logs if sl.kind == "work"]
        done = sum(1 for sl in work_sets if sl.completed)
        per_exercise[se.id] = (done, len(work_sets))
    done_total = sum(d for d, _ in per_exercise.values())
    work_total = sum(t for _, t in per_exercise.values())
    return {
        "per_exercise": per_exercise,
        "done": done_total,
        "total": work_total,
    }


WEEKDAY_LABELS = {
    1: "Lundi",
    2: "Mardi",
    3: "Mercredi",
    4: "Jeudi",
    5: "Vendredi",
    6: "Samedi",
    7: "Dimanche",
}


@router.get("/sessions/{session_id}", response_class=HTMLResponse)
def session_detail(
    session_id: int, request: Request, db: Session = Depends(get_db)
) -> HTMLResponse:
    session = _load_session(db, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    stats = _session_stats(session)
    rules = db.execute(
        select(MethodRule).order_by(MethodRule.position).limit(3)
    ).scalars().all()

    last_time = last_time_by_exercise_code(
        db, session, datetime.now(timezone.utc)
    )

    return templates.TemplateResponse(
        request,
        "session_detail.html",
        {
            "page_title": session.template_name_snapshot,
            "session": session,
            "weekday_label": WEEKDAY_LABELS[session.weekday_iso],
            "stats": stats,
            "rules": rules,
            "last_time": last_time,
        },
    )


# ----------------------------------------------------------------------
# Update — session-level
# ----------------------------------------------------------------------


@router.post("/sessions/{session_id}")
async def update_session(
    session_id: int, request: Request, db: Session = Depends(get_db)
) -> RedirectResponse:
    session = db.get(WorkoutSession, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    form = await request.form()

    session.concentration = enum_str(form.get("concentration"), _CONCENTRATION)
    session.global_state = enum_str(form.get("global_state"), _GLOBAL_STATE)
    session.bodyweight_kg = to_float(form.get("bodyweight_kg"))
    session.free_note = clean_str(form.get("free_note"), max_length=280)

    if form.get("action") == "end":
        session.ended_at = datetime.now(timezone.utc)
        session.status = SessionStatus.COMPLETED
    elif form.get("action") == "reopen" and session.status == SessionStatus.COMPLETED:
        session.ended_at = None
        session.status = SessionStatus.IN_PROGRESS

    db.commit()
    return RedirectResponse(
        url=f"/sessions/{session_id}#session-feedback", status_code=303
    )


# ----------------------------------------------------------------------
# Update — exercise card (feedback + all its sets in one submit)
# ----------------------------------------------------------------------


@router.post("/sessions/{session_id}/exercises/{session_exercise_id}")
async def update_exercise_card(
    session_id: int,
    session_exercise_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> RedirectResponse:
    stmt = (
        select(SessionExercise)
        .where(
            SessionExercise.id == session_exercise_id,
            SessionExercise.session_id == session_id,
        )
        .options(selectinload(SessionExercise.set_logs))
    )
    se = db.execute(stmt).scalar_one_or_none()
    if se is None:
        raise HTTPException(status_code=404, detail="Exercise card not found")

    form = await request.form()

    # Exercise-level feedback
    se.success_score = enum_int(form.get("success_score"), _SUCCESS_SCORE)
    se.muscle_sensation = enum_str(form.get("muscle_sensation"), _MUSCLE_SENSATION)
    se.free_note = clean_str(form.get("free_note"), max_length=140)

    # Per-set values — the form encodes them as set_{id}_{field}
    for sl in se.set_logs:
        p = f"set_{sl.id}_"
        sl.weight_kg = to_float(form.get(p + "weight_kg"))
        sl.reps = to_int(form.get(p + "reps"))
        sl.completed = checkbox(form.get(p + "completed"))
        if sl.kind == "work":
            sl.execution_quality = enum_str(
                form.get(p + "execution_quality"), _EXECUTION_QUALITY
            )
            sl.reps_target = enum_str(form.get(p + "reps_target"), _REPS_TARGET)

    db.commit()
    return RedirectResponse(
        url=f"/sessions/{session_id}#exercise-{session_exercise_id}",
        status_code=303,
    )


# ----------------------------------------------------------------------
# Rules page
# ----------------------------------------------------------------------


@router.get("/rules", response_class=HTMLResponse)
def rules_page(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    rules = db.execute(
        select(MethodRule).order_by(MethodRule.position)
    ).scalars().all()
    return templates.TemplateResponse(
        request,
        "rules.html",
        {"page_title": "Règles", "rules": rules},
    )
