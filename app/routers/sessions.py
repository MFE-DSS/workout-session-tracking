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

from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.deps import CurrentUser, DbSession
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
from app.services.delta import compute_delta, format_delta
from app.services.exercise_history import get_exercise_history
from app.services.ownership import get_owned_session_or_404
from app.services.form_parsing import (
    checkbox,
    clean_str,
    enum_int,
    enum_str,
    to_float,
    to_int,
)
from app.services.progression_hint import compute_progression_hint
from app.services.session_builder import instantiate_session
from app.services.session_state import latest_open_session
from app.services.stats import (
    last_time_by_exercise_code,
    summarise_current_exercise,
)
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
    template_slug: Annotated[str, Form()],
    db: DbSession, user: CurrentUser,
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

    session = instantiate_session(db, tpl, datetime.now(timezone.utc), user_id=user.id)
    db.commit()
    db.refresh(session)
    return RedirectResponse(
        url=f"/sessions/{session.id}", status_code=303
    )


# ----------------------------------------------------------------------
# Read
# ----------------------------------------------------------------------


def _load_session(db: Session, session_id: int, user_id: int) -> WorkoutSession | None:
    stmt = (
        select(WorkoutSession)
        .where(WorkoutSession.id == session_id, WorkoutSession.user_id == user_id)
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
    session_id: int, request: Request, db: DbSession, user: CurrentUser
) -> HTMLResponse:
    session = _load_session(db, session_id, user.id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    stats = _session_stats(session)
    rules = db.execute(
        select(MethodRule).order_by(MethodRule.position).limit(3)
    ).scalars().all()

    last_time = last_time_by_exercise_code(
        db, session, datetime.now(timezone.utc)
    )

    # Progression hint per exercise card: based strictly on the first
    # rep target of the current template_exercise and the first
    # completed work set of the prior session.
    hints: dict[str, str | None] = {}
    for se in session.session_exercises:
        code = se.exercise_code_snapshot
        prior = last_time.get(code)
        tgt_min, tgt_max = None, None
        te = se.template_exercise
        if te and te.rep_targets:
            first_rt = sorted(te.rep_targets, key=lambda r: r.set_index)[0]
            tgt_min, tgt_max = first_rt.min_reps, first_rt.max_reps
        prior_w, prior_r = None, None
        if prior and prior.get("first_set"):
            prior_w = prior["first_set"].get("weight_kg")
            prior_r = prior["first_set"].get("reps")
        hints[code] = compute_progression_hint(tgt_min, tgt_max, prior_w, prior_r)

    # Per-exercise compact summary used by the completed-session
    # readability block (still computed even when in_progress, the
    # template decides whether to render it).
    exercise_summaries: dict[int, dict | None] = {
        se.id: summarise_current_exercise(se) for se in session.session_exercises
    }

    # Delta vs the prior occurrence's first completed work set.
    # Only rendered when the CURRENT exercise has a first completed
    # work set AND the prior session had one too.
    delta_labels: dict[str, str | None] = {}
    for se in session.session_exercises:
        code = se.exercise_code_snapshot
        # Current first completed work set
        curr_work = sorted(
            (sl for sl in se.set_logs if sl.kind == "work"),
            key=lambda s: s.set_index,
        )
        curr_done = [
            sl for sl in curr_work
            if sl.completed and (sl.weight_kg is not None or sl.reps is not None)
        ]
        curr_w = curr_done[0].weight_kg if curr_done else None
        curr_r = curr_done[0].reps if curr_done else None

        prior = last_time.get(code)
        prior_w, prior_r, prior_score = None, None, None
        if prior and prior.get("first_set"):
            prior_w = prior["first_set"].get("weight_kg")
            prior_r = prior["first_set"].get("reps")
            prior_score = prior.get("success_score")

        delta = compute_delta(
            curr_w, curr_r, se.success_score,
            prior_w, prior_r, prior_score,
        )
        delta_labels[code] = format_delta(delta)

    # Determine which exercise card to expand (Sb_02 accordion)
    active_exercise_id = None
    active_param = request.query_params.get("active")
    if active_param:
        try:
            active_exercise_id = int(active_param)
        except (ValueError, TypeError):
            pass

    if active_exercise_id is None:
        # Default: first non-complete exercise
        for se in session.session_exercises:
            done, total = stats["per_exercise"][se.id]
            if total == 0 or done < total:
                active_exercise_id = se.id
                break

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
            "hints": hints,
            "exercise_summaries": exercise_summaries,
            "deltas": delta_labels,
            "active_exercise_id": active_exercise_id,
        },
    )


# ----------------------------------------------------------------------
# Update — session-level
# ----------------------------------------------------------------------


@router.post("/sessions/{session_id}")
async def update_session(
    session_id: int, request: Request, db: DbSession, user: CurrentUser
) -> RedirectResponse:
    session = get_owned_session_or_404(db, session_id, user.id)

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
    db: DbSession, user: CurrentUser,
) -> RedirectResponse:
    # Verify the parent session belongs to this user first.
    get_owned_session_or_404(db, session_id, user.id)
    stmt = (
        select(SessionExercise)
        .where(
            SessionExercise.id == session_exercise_id,
            SessionExercise.session_id == session_id,
        )
        .options(
            selectinload(SessionExercise.set_logs),
            selectinload(SessionExercise.template_exercise),
        )
    )
    se = db.execute(stmt).scalar_one_or_none()
    if se is None:
        raise HTTPException(status_code=404, detail="Exercise card not found")

    form = await request.form()

    # Exercise-level feedback
    se.muscle_sensation = enum_str(form.get("muscle_sensation"), _MUSCLE_SENSATION)
    se.free_note = clean_str(form.get("free_note"), max_length=140)

    # Per-set values — the form encodes them as set_{id}_{field}
    for sl in se.set_logs:
        p = f"set_{sl.id}_"
        sl.weight_kg = to_float(form.get(p + "weight_kg"))
        sl.reps = to_int(form.get(p + "reps"))
        sl.completed = checkbox(form.get(p + "completed"))

    # Derive success_score from set data (Sb_01)
    from app.services.feedback import compute_success_score
    se.success_score = compute_success_score(se, se.template_exercise)

    db.commit()

    # Sprint 5 daily-use shortcut: after saving an exercise card,
    # send the user to the NEXT exercise's anchor instead of back to
    # the same one. When there is no next exercise, drop them on the
    # session-feedback form so they can finish the session.
    next_se = db.execute(
        select(SessionExercise)
        .where(
            SessionExercise.session_id == session_id,
            SessionExercise.position > se.position,
        )
        .order_by(SessionExercise.position.asc())
        .limit(1)
    ).scalar_one_or_none()
    if next_se is not None:
        target = f"/sessions/{session_id}?active={next_se.id}#exercise-{next_se.id}"
    else:
        target = f"/sessions/{session_id}#session-feedback"
    return RedirectResponse(url=target, status_code=303)


# ----------------------------------------------------------------------
# Rules page
# ----------------------------------------------------------------------


@router.get("/rules", response_class=HTMLResponse)
def rules_page(request: Request, db: DbSession, user: CurrentUser) -> HTMLResponse:
    rules = db.execute(
        select(MethodRule).order_by(MethodRule.position)
    ).scalars().all()
    return templates.TemplateResponse(
        request,
        "rules.html",
        {
            "page_title": "Règles",
            "rules": rules,
            "active_session": latest_open_session(db, user.id),
        },
    )


# ----------------------------------------------------------------------
# Exercise history detail (Sprint 4)
# ----------------------------------------------------------------------


@router.get(
    "/exercise-history/{template_slug}/{exercise_code}",
    response_class=HTMLResponse,
)
def exercise_history_detail(
    template_slug: str,
    exercise_code: str,
    request: Request,
    db: DbSession, user: CurrentUser,
) -> HTMLResponse:
    entries = get_exercise_history(db, template_slug, exercise_code, user_id=user.id)

    # Use the exercise_name snapshot of the most recent entry so the
    # header reads naturally. Fall back to the raw slug/code if the
    # identity has no history yet.
    display_exercise_name: str | None = None
    display_template_name: str | None = None
    if entries:
        # Fetch the SessionExercise row of the most recent entry to
        # get the snapshotted names. One extra SELECT, cheap.
        row = db.execute(
            select(WorkoutSession, SessionExercise)
            .join(SessionExercise, SessionExercise.session_id == WorkoutSession.id)
            .where(
                WorkoutSession.template_slug_snapshot == template_slug,
                SessionExercise.exercise_code_snapshot == exercise_code,
            )
            .order_by(WorkoutSession.started_at.desc())
            .limit(1)
        ).first()
        if row is not None:
            display_template_name = row[0].template_name_snapshot
            display_exercise_name = row[1].exercise_name_snapshot

    return templates.TemplateResponse(
        request,
        "exercise_history.html",
        {
            "page_title": f"{exercise_code} · {display_exercise_name or exercise_code}",
            "template_slug": template_slug,
            "exercise_code": exercise_code,
            "display_template_name": display_template_name or template_slug,
            "display_exercise_name": display_exercise_name or exercise_code,
            "entries": entries,
            "active_session": latest_open_session(db, user.id),
        },
    )
