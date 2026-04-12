"""Authentication + account lifecycle routes.

Public: /welcome, /login, /register
Private: /logout, /profile, /profile/password
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.deps import CurrentUser, DbSession
from app.models.session import SessionExercise, SetLog, WorkoutSession
from app.models.user import User
from app.services.quality_score import compute_session_quality
from app.services.session_state import latest_open_session
from app.services.timeline import TimelinePoint, build_quality_timeline_svg
from app.services.auth import (
    clear_session_cookie,
    create_session_cookie,
    get_current_user,
    hash_password,
    verify_password,
)
from app.templating import templates

router = APIRouter(tags=["auth"])

MIN_PASSWORD_LENGTH = 4
MIN_USERNAME_LENGTH = 3


# ---------------------------------------------------------------------------
# Public
# ---------------------------------------------------------------------------


@router.get("/welcome", response_class=HTMLResponse)
def public_landing(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "welcome.html", {"page_title": "Bienvenue"},
    )


@router.get("/login", response_class=HTMLResponse)
def login_page(
    request: Request,
    db: DbSession,
    success: str | None = None,
) -> HTMLResponse:
    user = get_current_user(request, db)
    if user is not None:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        request,
        "login.html",
        {
            "page_title": "Connexion",
            "error": None,
            "success": success,
        },
    )


@router.post("/login", response_model=None)
async def login_submit(
    request: Request,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    db: DbSession,
):
    user = db.execute(
        select(User).where(User.username == username, User.is_active.is_(True))
    ).scalar_one_or_none()

    # Constant-time: always run bcrypt even if user is None, so the
    # response timing doesn't leak whether the username exists.
    # The dummy hash is a real bcrypt hash of "dummy" — passlib will
    # run the full comparison against it and return False.
    _DUMMY = "$2b$12$LJ3m4ys3Lg3mRIkFLfTMD.ue1tjUTO7ZzNzm3Lf0QLjHEjLN2yJXi"
    pw_ok = verify_password(password, user.password_hash if user else _DUMMY)

    if user is None or not pw_ok:
        return templates.TemplateResponse(
            request,
            "login.html",
            {"page_title": "Connexion", "error": "Identifiants invalides.", "success": None},
            status_code=401,
        )

    response = RedirectResponse(url="/", status_code=303)
    create_session_cookie(response, user.id)
    return response


@router.post("/logout")
def logout(request: Request) -> RedirectResponse:
    response = RedirectResponse(url="/welcome", status_code=303)
    clear_session_cookie(response)
    return response


# ---------------------------------------------------------------------------
# Registration (public)
# ---------------------------------------------------------------------------


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request, db: DbSession) -> HTMLResponse:
    user = get_current_user(request, db)
    if user is not None:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        request, "register.html",
        {"page_title": "Inscription", "error": None},
    )


@router.post("/register", response_model=None)
async def register_submit(
    request: Request,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    password_confirm: Annotated[str, Form()],
    db: DbSession,
):
    error = None
    if len(username.strip()) < MIN_USERNAME_LENGTH:
        error = f"Le nom d'utilisateur doit faire au moins {MIN_USERNAME_LENGTH} caractères."
    elif len(password) < MIN_PASSWORD_LENGTH:
        error = f"Le mot de passe doit faire au moins {MIN_PASSWORD_LENGTH} caractères."
    elif password != password_confirm:
        error = "Les mots de passe ne correspondent pas."
    else:
        existing = db.execute(
            select(User).where(User.username == username.strip())
        ).scalar_one_or_none()
        if existing is not None:
            error = "Ce nom d'utilisateur est déjà pris."

    if error:
        return templates.TemplateResponse(
            request, "register.html",
            {"page_title": "Inscription", "error": error},
            status_code=400,
        )

    user = User(
        username=username.strip(),
        password_hash=hash_password(password),
    )
    db.add(user)
    db.commit()

    # Auto-login after registration.
    response = RedirectResponse(url="/", status_code=303)
    create_session_cookie(response, user.id)
    return response


# ---------------------------------------------------------------------------
# Profile (private)
# ---------------------------------------------------------------------------


@router.get("/profile", response_class=HTMLResponse)
def profile_page(
    request: Request,
    db: DbSession,
    user: CurrentUser,
) -> HTMLResponse:
    session_count = db.execute(
        select(func.count(WorkoutSession.id))
        .where(WorkoutSession.user_id == user.id)
    ).scalar_one() or 0
    completed_count = db.execute(
        select(func.count(WorkoutSession.id))
        .where(WorkoutSession.user_id == user.id)
        .where(WorkoutSession.status == "completed")
    ).scalar_one() or 0

    # 30-day quality timeline
    now = datetime.now(timezone.utc)
    window_30 = now - timedelta(days=30)
    window_60 = now - timedelta(days=60)

    sessions_30d = db.execute(
        select(WorkoutSession)
        .where(WorkoutSession.user_id == user.id)
        .where(WorkoutSession.status == "completed")
        .where(WorkoutSession.excluded_from_stats.is_(False))
        .where(WorkoutSession.started_at >= window_30)
        .order_by(WorkoutSession.started_at.asc())
        .options(
            selectinload(WorkoutSession.session_exercises)
            .selectinload(SessionExercise.set_logs)
        )
    ).scalars().all()

    quality_points = [
        TimelinePoint(
            label=s.started_at.strftime("%d/%m"),
            value=compute_session_quality(s),
        )
        for s in sessions_30d
    ]
    quality_svg = build_quality_timeline_svg(quality_points)
    sessions_30d_count = len(sessions_30d)

    # Trend: compare 30d count vs previous 30d
    prev_30d_count = db.execute(
        select(func.count(WorkoutSession.id))
        .where(WorkoutSession.user_id == user.id)
        .where(WorkoutSession.status == "completed")
        .where(WorkoutSession.excluded_from_stats.is_(False))
        .where(WorkoutSession.started_at >= window_60)
        .where(WorkoutSession.started_at < window_30)
    ).scalar_one() or 0

    if sessions_30d_count > prev_30d_count:
        trend = "up"
        trend_label = "\u2191 en hausse"
    elif sessions_30d_count < prev_30d_count:
        trend = "down"
        trend_label = "\u2193 en baisse"
    else:
        trend = "stable"
        trend_label = "\u2192 stable"

    return templates.TemplateResponse(
        request, "profile.html",
        {
            "page_title": "Profil",
            "user": user,
            "session_count": session_count,
            "completed_count": completed_count,
            "quality_svg": quality_svg,
            "sessions_30d_count": sessions_30d_count,
            "trend": trend,
            "trend_label": trend_label,
            "active_session": latest_open_session(db, user.id),
        },
    )


@router.post("/profile/body", response_model=None)
async def profile_body_submit(
    request: Request,
    height_cm: Annotated[str, Form()] = "",
    weight_kg: Annotated[str, Form()] = "",
    resting_hr: Annotated[str, Form()] = "",
    waist_cm: Annotated[str, Form()] = "",
    bp_systolic: Annotated[str, Form()] = "",
    bp_diastolic: Annotated[str, Form()] = "",
    db: DbSession = None,
    user: CurrentUser = None,
):
    """Save physical profile fields."""
    def _int_or_none(v: str, lo: int, hi: int) -> int | None:
        v = v.strip()
        if not v:
            return None
        try:
            n = int(v)
        except ValueError:
            return None
        if n < lo or n > hi:
            return None
        return n

    def _float_or_none(v: str, lo: float, hi: float) -> float | None:
        v = v.strip()
        if not v:
            return None
        try:
            n = float(v)
        except ValueError:
            return None
        if n < lo or n > hi:
            return None
        return n

    user.height_cm = _int_or_none(height_cm, 100, 250)
    user.weight_kg = _float_or_none(weight_kg, 30.0, 300.0)
    user.resting_hr = _int_or_none(resting_hr, 30, 220)
    user.waist_cm = _float_or_none(waist_cm, 40.0, 200.0)
    user.bp_systolic = _int_or_none(bp_systolic, 60, 250)
    user.bp_diastolic = _int_or_none(bp_diastolic, 30, 150)
    db.commit()

    return RedirectResponse(url="/profile", status_code=303)


# ---------------------------------------------------------------------------
# Password change (private)
# ---------------------------------------------------------------------------


@router.get("/profile/password", response_class=HTMLResponse)
def password_change_page(
    request: Request,
    user: CurrentUser,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "password_change.html",
        {"page_title": "Changer le mot de passe", "error": None, "success": False},
    )


@router.post("/profile/password", response_model=None)
async def password_change_submit(
    request: Request,
    current_password: Annotated[str, Form()],
    new_password: Annotated[str, Form()],
    new_password_confirm: Annotated[str, Form()],
    db: DbSession,
    user: CurrentUser,
):
    error = None
    if not verify_password(current_password, user.password_hash):
        error = "Le mot de passe actuel est incorrect."
    elif len(new_password) < MIN_PASSWORD_LENGTH:
        error = f"Le nouveau mot de passe doit faire au moins {MIN_PASSWORD_LENGTH} caractères."
    elif new_password != new_password_confirm:
        error = "Les nouveaux mots de passe ne correspondent pas."

    if error:
        return templates.TemplateResponse(
            request, "password_change.html",
            {"page_title": "Changer le mot de passe", "error": error, "success": False},
            status_code=400,
        )

    user.password_hash = hash_password(new_password)
    db.commit()

    return templates.TemplateResponse(
        request, "password_change.html",
        {"page_title": "Changer le mot de passe", "error": None, "success": True},
    )
