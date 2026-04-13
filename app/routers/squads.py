"""Squad routes: list, create, join, detail, invite, leave, delete."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select

from app.deps import CurrentUser, DbSession
from app.models.squad import SquadInviteCode
from app.services.session_state import latest_open_session
from app.services.squad import (
    SquadError,
    compute_squad_leaderboard,
    create_squad,
    delete_squad,
    generate_invite_code,
    get_membership,
    get_squad_members,
    get_squad_or_none,
    get_user_squads,
    is_member,
    join_by_code,
    leave_squad,
)
from app.templating import templates

router = APIRouter(tags=["squads"])


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------


@router.get("/squads", response_class=HTMLResponse, name="squads_list")
def squads_list(request: Request, db: DbSession, user: CurrentUser):
    squads = get_user_squads(db, user.id)
    squad_data = []
    for s in squads:
        members = get_squad_members(db, s.id)
        membership = get_membership(db, s.id, user.id)
        squad_data.append(
            {
                "squad": s,
                "member_count": len(members),
                "role": membership.role if membership else "member",
            }
        )
    return templates.TemplateResponse(
        request,
        "squads_list.html",
        {
            "page_title": "Squads",
            "squad_data": squad_data,
            "active_session": latest_open_session(db, user.id),
        },
    )


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------


@router.get("/squads/create", response_class=HTMLResponse, name="squad_create")
def squad_create_page(request: Request, db: DbSession, user: CurrentUser):
    return templates.TemplateResponse(
        request,
        "squad_create.html",
        {
            "page_title": "Créer une squad",
            "error": None,
            "active_session": latest_open_session(db, user.id),
        },
    )


@router.post("/squads/create", response_class=HTMLResponse, name="squad_create_post")
def squad_create_post(
    request: Request,
    db: DbSession,
    user: CurrentUser,
    name: str = Form(...),
):
    try:
        squad = create_squad(db, user.id, name)
        return RedirectResponse(
            url=request.url_for("squad_detail", squad_id=squad.id),
            status_code=303,
        )
    except SquadError as exc:
        return templates.TemplateResponse(
            request,
            "squad_create.html",
            {
                "page_title": "Créer une squad",
                "error": str(exc),
                "active_session": latest_open_session(db, user.id),
            },
        )


# ---------------------------------------------------------------------------
# Join
# ---------------------------------------------------------------------------


@router.get("/squads/join", response_class=HTMLResponse, name="squad_join")
def squad_join_page(request: Request, db: DbSession, user: CurrentUser):
    return templates.TemplateResponse(
        request,
        "squad_join.html",
        {
            "page_title": "Rejoindre une squad",
            "error": None,
            "active_session": latest_open_session(db, user.id),
        },
    )


@router.post("/squads/join", response_class=HTMLResponse, name="squad_join_post")
def squad_join_post(
    request: Request,
    db: DbSession,
    user: CurrentUser,
    code: str = Form(...),
):
    try:
        squad = join_by_code(db, user.id, code.strip().upper())
        return RedirectResponse(
            url=request.url_for("squad_detail", squad_id=squad.id),
            status_code=303,
        )
    except SquadError as exc:
        return templates.TemplateResponse(
            request,
            "squad_join.html",
            {
                "page_title": "Rejoindre une squad",
                "error": str(exc),
                "active_session": latest_open_session(db, user.id),
            },
        )


# ---------------------------------------------------------------------------
# Detail
# ---------------------------------------------------------------------------


@router.get("/squads/{squad_id}", response_class=HTMLResponse, name="squad_detail")
def squad_detail(
    request: Request,
    squad_id: int,
    db: DbSession,
    user: CurrentUser,
):
    squad = get_squad_or_none(db, squad_id)
    if not squad:
        raise HTTPException(status_code=404, detail="Squad introuvable")
    if not is_member(db, squad_id, user.id):
        raise HTTPException(status_code=403, detail="Accès refusé")

    members = get_squad_members(db, squad_id)
    leaderboard = compute_squad_leaderboard(db, squad_id)
    membership = get_membership(db, squad_id, user.id)

    # Latest active (unused, not expired) invite code
    latest_code = db.execute(
        select(SquadInviteCode)
        .where(SquadInviteCode.squad_id == squad_id)
        .where(SquadInviteCode.used_by.is_(None))
        .where(SquadInviteCode.expires_at > datetime.now(timezone.utc))
        .order_by(SquadInviteCode.expires_at.desc())
        .limit(1)
    ).scalar_one_or_none()

    return templates.TemplateResponse(
        request,
        "squad_detail.html",
        {
            "page_title": squad.name,
            "squad": squad,
            "members": members,
            "leaderboard": leaderboard,
            "membership": membership,
            "latest_code": latest_code,
            "current_username": user.username,
            "active_session": latest_open_session(db, user.id),
        },
    )


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------


@router.post("/squads/{squad_id}/invite", name="squad_invite")
def squad_invite(
    request: Request,
    squad_id: int,
    db: DbSession,
    user: CurrentUser,
):
    try:
        generate_invite_code(db, squad_id, user.id)
    except SquadError:
        pass  # silently ignore — redirect to detail anyway
    return RedirectResponse(
        url=request.url_for("squad_detail", squad_id=squad_id),
        status_code=303,
    )


@router.post("/squads/{squad_id}/leave", name="squad_leave")
def squad_leave(
    request: Request,
    squad_id: int,
    db: DbSession,
    user: CurrentUser,
):
    try:
        leave_squad(db, squad_id, user.id)
    except SquadError:
        pass
    return RedirectResponse(url=request.url_for("squads_list"), status_code=303)


@router.post("/squads/{squad_id}/delete", name="squad_delete")
def squad_delete(
    request: Request,
    squad_id: int,
    db: DbSession,
    user: CurrentUser,
):
    try:
        delete_squad(db, squad_id, user.id)
    except SquadError:
        pass
    return RedirectResponse(url=request.url_for("squads_list"), status_code=303)
