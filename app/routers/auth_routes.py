"""Authentication routes: login, logout, public landing page.

The public landing is the only page that anonymous visitors see.
Everything else requires a session cookie.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.auth import (
    clear_session_cookie,
    create_session_cookie,
    get_current_user,
    verify_password,
)
from app.templating import templates

router = APIRouter(tags=["auth"])


@router.get("/welcome", response_class=HTMLResponse)
def public_landing(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "welcome.html",
        {"page_title": "Bienvenue"},
    )


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    # If already logged in, go straight to the app.
    user = get_current_user(request, db)
    if user is not None:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        request,
        "login.html",
        {"page_title": "Connexion", "error": None},
    )


@router.post("/login", response_model=None)
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.execute(
        select(User).where(User.username == username, User.is_active.is_(True))
    ).scalar_one_or_none()

    if user is None or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            request,
            "login.html",
            {"page_title": "Connexion", "error": "Identifiants invalides."},
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
