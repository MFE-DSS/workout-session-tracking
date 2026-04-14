"""Session management (admin) routes.

Sprint 8 adds:
- GET  /admin/sessions          management list with quality scores
- POST /admin/sessions/{id}/delete   hard delete with cascade
- POST /admin/sessions/{id}/exclude  toggle excluded_from_stats
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.deps import CurrentUser, DbSession
from app.models.session import SessionExercise, WorkoutSession
from app.services.ownership import get_owned_session_or_404
from app.services.quality_score import compute_session_quality
from app.services.session_state import latest_open_session
from app.services.time_format import format_duration_short, session_duration
from app.templating import templates

router = APIRouter(tags=["admin"])


@router.get("/admin/sessions", response_class=HTMLResponse)
def admin_sessions(request: Request, db: DbSession, user: CurrentUser) -> HTMLResponse:
    stmt = (
        select(WorkoutSession)
        .where(WorkoutSession.user_id == user.id)
        .order_by(WorkoutSession.started_at.desc())
        .options(
            selectinload(WorkoutSession.session_exercises)
            .selectinload(SessionExercise.set_logs)
        )
    )
    sessions = list(db.execute(stmt).scalars().all())

    rows: list[dict] = []
    for s in sessions:
        quality = compute_session_quality(s) if s.status == "completed" else None
        total_ex = len(s.session_exercises)
        done_ex = 0
        for se in s.session_exercises:
            work = [sl for sl in se.set_logs if sl.kind == "work"]
            if work and all(sl.completed for sl in work):
                done_ex += 1
        rows.append({
            "session": s,
            "quality": quality,
            "total_exercises": total_ex,
            "done_exercises": done_ex,
            "duration": format_duration_short(session_duration(s.started_at, end=s.ended_at)),
        })

    return templates.TemplateResponse(
        request,
        "admin_sessions.html",
        {
            "page_title": "Gestion des séances",
            "rows": rows,
            "active_session": latest_open_session(db, user.id),
        },
    )


@router.post("/admin/sessions/{session_id}/delete")
def delete_session(session_id: int, request: Request, db: DbSession, user: CurrentUser) -> RedirectResponse:
    session = get_owned_session_or_404(db, session_id, user.id)
    db.delete(session)
    db.commit()
    # Redirect back to referring page (history or admin)
    referer = request.headers.get("referer", "")
    if "/history" in referer:
        return RedirectResponse(url="/history", status_code=303)
    return RedirectResponse(url="/admin/sessions", status_code=303)


@router.post("/admin/sessions/{session_id}/exclude")
def toggle_exclude(session_id: int, request: Request, db: DbSession, user: CurrentUser) -> RedirectResponse:
    session = get_owned_session_or_404(db, session_id, user.id)
    session.excluded_from_stats = not session.excluded_from_stats
    db.commit()
    # Redirect back to referring page (history or admin)
    referer = request.headers.get("referer", "")
    if "/history" in referer:
        return RedirectResponse(url="/history", status_code=303)
    return RedirectResponse(url="/admin/sessions", status_code=303)
