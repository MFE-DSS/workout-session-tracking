"""Leaderboard + public user profile routes (Sb_19)."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select

from app.deps import CurrentUser, DbSession
from app.models.session import WorkoutSession
from app.models.user import User
from app.services.leaderboard import compute_leaderboard
from app.services.muscle_scoring import compute_physique_dashboard
from app.services.performance import GRADE_LABELS, compute_grade
from app.services.quality_score import compute_session_quality
from app.services.session_state import latest_open_session
from app.templating import templates

router = APIRouter(tags=["leaderboard"])


@router.get("/leaderboard", response_class=HTMLResponse)
def leaderboard_page(
    request: Request,
    db: DbSession,
    user: CurrentUser,
) -> HTMLResponse:
    entries = compute_leaderboard(db)
    return templates.TemplateResponse(
        request,
        "leaderboard.html",
        {
            "page_title": "Leaderboard",
            "entries": entries,
            "current_username": user.username,
            "active_session": latest_open_session(db, user.id),
        },
    )


@router.get(
    "/users/{username}", response_class=HTMLResponse, name="user_profile",
)
def user_profile(
    # Sb_20.3 — explicit path-param validation (CWE-20). Allowlist
    # alphanumeric + underscore + dash, length 2-64. Mirrors the
    # registration regex in auth_routes.py. FastAPI returns 422 on
    # mismatch, before any DB lookup.
    username: Annotated[
        str,
        Path(min_length=2, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$"),
    ],
    request: Request,
    db: DbSession,
    user: CurrentUser,
) -> HTMLResponse:
    """Public synthesis page for a user (Sb_19).

    Exposes username, grade, sessions count 30j, full radar 30j, and
    optional metadata (height_cm / weight_kg). Never exposes per-session
    details, exercises, or notes — same disclosure contract as the
    leaderboard, just one page deeper.
    """
    target = db.execute(
        select(User).where(
            User.username == username, User.is_active.is_(True),
        )
    ).scalar_one_or_none()
    if target is None:
        raise HTTPException(status_code=404, detail="User not found")

    dashboard = compute_physique_dashboard(db, target.id, window_days=30)

    sessions_30d = db.execute(
        select(WorkoutSession)
        .where(
            WorkoutSession.user_id == target.id,
            WorkoutSession.status == "completed",
            WorkoutSession.excluded_from_stats.is_(False),
        )
        .order_by(WorkoutSession.started_at.desc())
    ).scalars().all()

    last_session_score = None
    if sessions_30d:
        last_session_score = compute_session_quality(sessions_30d[0])

    avg = (
        sum(compute_session_quality(s) for s in sessions_30d) / len(sessions_30d)
        if sessions_30d else 0.0
    )
    grade = compute_grade(avg, len(sessions_30d))

    return templates.TemplateResponse(
        request,
        "user_profile.html",
        {
            "page_title": f"Profil de {target.username}",
            "target": target,
            "dashboard": dashboard,
            "sessions_count_30d": len(sessions_30d),
            "last_session_score": last_session_score,
            "grade": grade,
            "grade_label": GRADE_LABELS.get(grade, ""),
            "active_session": latest_open_session(db, user.id),
        },
    )
