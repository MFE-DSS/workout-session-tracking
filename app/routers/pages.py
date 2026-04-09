"""Navigation + catalog pages (home, library, history, progress).

The session logging flow lives in `app.routers.sessions`.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.deps import require_user
from app.models.catalog import TemplateExercise, WorkoutTemplate
from app.models.session import SessionExercise, SetLog, WorkoutSession
from app.models.user import User
from app.services.kpis import (
    compute_global_kpis,
    compute_recent_exercise_activity,
    compute_template_kpis,
)
from app.services.quality_score import compute_session_quality
from app.services.session_state import latest_open_session
from app.services.time_format import format_duration_short, session_duration
from app.services.timeline import (
    TimelinePoint,
    build_bodyweight_timeline_svg,
    build_quality_timeline_svg,
)
from app.templating import templates

router = APIRouter(tags=["pages"])


def _load_templates(db: Session) -> list[WorkoutTemplate]:
    stmt = (
        select(WorkoutTemplate)
        .options(
            selectinload(WorkoutTemplate.exercises).selectinload(
                TemplateExercise.rep_targets
            )
        )
        .order_by(WorkoutTemplate.kind, WorkoutTemplate.slug)
    )
    return list(db.execute(stmt).scalars().all())


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db), user: User = Depends(require_user)) -> HTMLResponse:
    # Home shows its own Reprendre tile — the header banner would
    # be redundant here, so we intentionally do NOT pass active_session.
    open_session = latest_open_session(db, user.id)
    open_since: str | None = None
    if open_session is not None:
        open_since = format_duration_short(
            session_duration(open_session.started_at, end=None)
        )
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "page_title": "Accueil",
            "open_session": open_session,
            "open_since": open_since,
        },
    )


@router.get("/library", response_class=HTMLResponse)
def library(request: Request, db: Session = Depends(get_db), user: User = Depends(require_user)) -> HTMLResponse:
    all_templates = _load_templates(db)
    return templates.TemplateResponse(
        request,
        "library.html",
        {
            "page_title": "Bibliothèque",
            "templates": all_templates,
            "active_session": latest_open_session(db, user.id),
        },
    )


@router.get("/library/{slug}", response_class=HTMLResponse)
def template_detail(
    slug: str, request: Request, db: Session = Depends(get_db), user: User = Depends(require_user)
) -> HTMLResponse:
    stmt = (
        select(WorkoutTemplate)
        .where(WorkoutTemplate.slug == slug)
        .options(
            selectinload(WorkoutTemplate.exercises).selectinload(
                TemplateExercise.rep_targets
            )
        )
    )
    tpl = db.execute(stmt).scalar_one_or_none()
    if tpl is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return templates.TemplateResponse(
        request,
        "template_detail.html",
        {
            "page_title": tpl.name,
            "template": tpl,
            "active_session": latest_open_session(db, user.id),
        },
    )


_HISTORY_STATUS_CHOICES = ("all", "in_progress", "completed")


@router.get("/history", response_class=HTMLResponse)
def history(
    request: Request,
    status: str = Query("all"),
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
) -> HTMLResponse:
    status = status if status in _HISTORY_STATUS_CHOICES else "all"

    stmt = (
        select(WorkoutSession)
        .where(WorkoutSession.user_id == user.id)
        .order_by(WorkoutSession.started_at.desc())
        .limit(100)
    )
    if status != "all":
        stmt = stmt.where(WorkoutSession.status == status)

    sessions = list(db.execute(stmt).scalars().all())

    # Per-session counts of exercise cards and "done" cards.
    # A card is "done" if it has at least one work set and every work
    # set has `completed=True`. We compute it all in Python so we stay
    # portable across SQLite and PostgreSQL without dialect-specific
    # aggregates.
    session_stats: dict[int, dict] = {}
    if sessions:
        sids = [s.id for s in sessions]
        work_rows = db.execute(
            select(
                SessionExercise.id,
                SessionExercise.session_id,
                SetLog.kind,
                SetLog.completed,
            )
            .join(SetLog, SetLog.session_exercise_id == SessionExercise.id, isouter=True)
            .where(SessionExercise.session_id.in_(sids))
        ).all()

        # { session_id: { exercise_id: [ (kind, completed), ... ] } }
        grouped: dict[int, dict[int, list[tuple]]] = {}
        for se_id, sid_, kind, completed in work_rows:
            grouped.setdefault(sid_, {}).setdefault(se_id, []).append((kind, completed))

        for s in sessions:
            exercises = grouped.get(s.id, {})
            total = len(exercises)
            done = 0
            for _, sl_list in exercises.items():
                work_sets = [c for k, c in sl_list if k == "work"]
                if work_sets and all(work_sets):
                    done += 1
            session_stats[s.id] = {"total": total, "done": done}

    # Per-session duration string (unused for empty history list).
    durations: dict[int, str] = {}
    for s in sessions:
        durations[s.id] = format_duration_short(
            session_duration(s.started_at, end=s.ended_at)
        )

    return templates.TemplateResponse(
        request,
        "history.html",
        {
            "page_title": "Historique",
            "sessions": sessions,
            "session_stats": session_stats,
            "durations": durations,
            "status_filter": status,
            "status_choices": _HISTORY_STATUS_CHOICES,
            "active_session": latest_open_session(db, user.id),
        },
    )


@router.get("/progress", response_class=HTMLResponse)
def progress(request: Request, db: Session = Depends(get_db), user: User = Depends(require_user)) -> HTMLResponse:
    global_kpis = compute_global_kpis(db, user_id=user.id)
    template_kpis = compute_template_kpis(db, user_id=user.id)
    recent_activity = compute_recent_exercise_activity(db, limit=10, user_id=user.id)

    # Sprint 8: build quality + bodyweight timeline SVGs from
    # completed non-excluded sessions, oldest first.
    timeline_stmt = (
        select(WorkoutSession)
        .where(WorkoutSession.user_id == user.id)
        .where(WorkoutSession.status == "completed")
        .where(WorkoutSession.excluded_from_stats.is_(False))
        .order_by(WorkoutSession.started_at.asc())
        .options(
            selectinload(WorkoutSession.session_exercises)
            .selectinload(SessionExercise.set_logs)
        )
    )
    eligible = list(db.execute(timeline_stmt).scalars().all())

    quality_points = [
        TimelinePoint(
            label=s.started_at.strftime("%d/%m"),
            value=compute_session_quality(s),
        )
        for s in eligible
    ]
    bw_points = [
        TimelinePoint(
            label=s.started_at.strftime("%d/%m"),
            value=s.bodyweight_kg,
        )
        for s in eligible
        if s.bodyweight_kg is not None
    ]

    quality_svg = build_quality_timeline_svg(quality_points)
    bodyweight_svg = build_bodyweight_timeline_svg(bw_points)

    return templates.TemplateResponse(
        request,
        "progress.html",
        {
            "page_title": "Progression",
            "kpis": global_kpis,
            "template_kpis": template_kpis,
            "recent_activity": recent_activity,
            "quality_svg": quality_svg,
            "bodyweight_svg": bodyweight_svg,
            "active_session": latest_open_session(db, user.id),
        },
    )
