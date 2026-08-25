"""Leaderboard + public user profile routes (Sb_19 + Sb_22b)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select

from app.deps import CurrentUser, DbSession
from app.models.session import WorkoutSession
from app.models.user import User
from app.services.leaderboard import compute_leaderboard
from app.services.performance import GRADE_LABELS, compute_grade
from app.services.profile_metrics import build_page, build_preview
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

    # `TRAIN1-E` / C4 — le profil public ne rend plus ni radar ni score
    # physique : le calculer serait produire une lecture corporelle
    # d'autrui pour la jeter.
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

    # Sb_22b — L3 page payload (preview + activity blocks).
    page = build_page(db, target.id, sessions_30d=len(sessions_30d))

    return templates.TemplateResponse(
        request,
        "user_profile.html",
        {
            "page_title": f"Profil de {target.username}",
            "target": target,
            "sessions_count_30d": len(sessions_30d),
            "last_session_score": last_session_score,
            "grade": grade,
            "grade_label": GRADE_LABELS.get(grade, ""),
            "page": page,
            "active_session": latest_open_session(db, user.id),
        },
    )


# Sb_22b — L2 preview endpoint (fragment HTML for the leaderboard hover).
@router.get(
    "/users/{username}/preview",
    response_class=HTMLResponse,
    name="user_profile_preview",
)
def user_profile_preview(
    username: Annotated[
        str,
        Path(min_length=2, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$"),
    ],
    request: Request,
    db: DbSession,
    user: CurrentUser,
) -> HTMLResponse:
    """Return a small HTML fragment with the L2 preview card content.

    Mirrors the privacy contract of the leaderboard / public profile:
    no session details, only aggregates. Auth-gated like every other
    page (CurrentUser).
    """
    target = db.execute(
        select(User).where(
            User.username == username, User.is_active.is_(True),
        )
    ).scalar_one_or_none()
    if target is None:
        raise HTTPException(status_code=404, detail="User not found")

    sessions_count = db.execute(
        select(WorkoutSession)
        .where(
            WorkoutSession.user_id == target.id,
            WorkoutSession.status == "completed",
            WorkoutSession.excluded_from_stats.is_(False),
            WorkoutSession.started_at
            >= datetime.now(timezone.utc) - timedelta(days=30),
        )
    ).scalars().all()
    preview = build_preview(db, target.id, sessions_30d=len(sessions_count))

    # Compute grade for the badge (same as L1 logic — derived from all-time
    # sessions, not just 30d, so the badge stays consistent with leaderboard).
    all_sessions = db.execute(
        select(WorkoutSession)
        .where(
            WorkoutSession.user_id == target.id,
            WorkoutSession.status == "completed",
            WorkoutSession.excluded_from_stats.is_(False),
        )
    ).scalars().all()
    if all_sessions:
        avg = sum(compute_session_quality(s) for s in all_sessions) / len(all_sessions)
        grade = compute_grade(avg, len(all_sessions))
    else:
        grade = "C"

    return templates.TemplateResponse(
        request,
        "_partials/profile_preview.html",
        {
            "target": target,
            "preview": preview,
            "grade": grade,
            "grade_label": GRADE_LABELS.get(grade, ""),
        },
    )
