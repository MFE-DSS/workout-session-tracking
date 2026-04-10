"""Leaderboard route. Private to authenticated users."""
from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.deps import CurrentUser, DbSession
from app.services.leaderboard import compute_leaderboard
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
