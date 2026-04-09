"""Leaderboard route. Private to authenticated users."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_user
from app.models.user import User
from app.services.leaderboard import compute_leaderboard
from app.services.session_state import latest_open_session
from app.templating import templates

router = APIRouter(tags=["leaderboard"])


@router.get("/leaderboard", response_class=HTMLResponse)
def leaderboard_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
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
