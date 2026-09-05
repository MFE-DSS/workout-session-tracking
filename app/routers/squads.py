"""Squad routes: list, create, join, detail, invite, leave, delete, challenges, compare, sharing."""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Optional

from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select

from app.deps import CurrentUser, DbSession
from app.models.catalog import WorkoutTemplate
from app.models.session import WorkoutSession
from app.models.squad import SquadInviteCode
from app.services.challenge import (
    ChallengeError,
    VALID_METRICS,
    _METRIC_LABELS,
    compute_standings,
    create_challenge,
    get_challenge_or_none,
    get_squad_challenges,
)
from app.services.compare import compute_comparison
from app.services.session_state import latest_open_session
from app.services.sharing import SharingError, get_squad_activity, recommend_template, share_session
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

    # Enrichment: challenges, activity, user sessions, templates
    activity = get_squad_activity(db, squad_id)
    challenges = get_squad_challenges(db, squad_id)
    user_sessions = list(
        db.execute(
            select(WorkoutSession)
            .where(
                WorkoutSession.user_id == user.id,
                WorkoutSession.status == "completed",
            )
            .order_by(WorkoutSession.started_at.desc())
            .limit(10)
        ).scalars().all()
    )
    all_templates = list(
        db.execute(
            select(WorkoutTemplate)
            .where(WorkoutTemplate.catalog_section != "archived")
            .order_by(WorkoutTemplate.display_order)
        ).scalars().all()
    )

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
            "activity": activity,
            "challenges": challenges,
            "user_sessions": user_sessions,
            "all_templates": all_templates,
            "today": date.today(),
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


# ---------------------------------------------------------------------------
# Challenges
# ---------------------------------------------------------------------------


@router.get("/squads/{squad_id}/challenges", response_class=HTMLResponse, name="squad_challenges")
def squad_challenges(
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

    challenges = get_squad_challenges(db, squad_id)
    membership = get_membership(db, squad_id, user.id)
    return templates.TemplateResponse(
        request,
        "squad_challenges.html",
        {
            "page_title": f"Challenges · {squad.name}",
            "squad": squad,
            "challenges": challenges,
            "membership": membership,
            "today": date.today(),
            "metric_labels": _METRIC_LABELS,
            "active_session": latest_open_session(db, user.id),
        },
    )


@router.get("/squads/{squad_id}/challenges/create", response_class=HTMLResponse, name="squad_challenge_create")
def squad_challenge_create_page(
    request: Request,
    squad_id: int,
    db: DbSession,
    user: CurrentUser,
):
    squad = get_squad_or_none(db, squad_id)
    if not squad:
        raise HTTPException(status_code=404, detail="Squad introuvable")
    membership = get_membership(db, squad_id, user.id)
    if not membership or membership.role != "owner":
        raise HTTPException(status_code=403, detail="Accès refusé")

    return templates.TemplateResponse(
        request,
        "squad_challenge_create.html",
        {
            "page_title": f"Nouveau challenge · {squad.name}",
            "squad": squad,
            "metric_labels": _METRIC_LABELS,
            "error": None,
            "active_session": latest_open_session(db, user.id),
        },
    )


@router.post("/squads/{squad_id}/challenges/create", response_class=HTMLResponse, name="squad_challenge_create_post")
def squad_challenge_create_post(
    request: Request,
    squad_id: int,
    db: DbSession,
    user: CurrentUser,
    title: str = Form(...),
    metric: str = Form(...),
    starts_at: str = Form(...),
    ends_at: str = Form(...),
):
    squad = get_squad_or_none(db, squad_id)
    if not squad:
        raise HTTPException(status_code=404, detail="Squad introuvable")
    membership = get_membership(db, squad_id, user.id)
    if not membership or membership.role != "owner":
        raise HTTPException(status_code=403, detail="Accès refusé")

    try:
        starts = date.fromisoformat(starts_at)
        ends = date.fromisoformat(ends_at)
    except ValueError:
        return templates.TemplateResponse(
            request,
            "squad_challenge_create.html",
            {
                "page_title": f"Nouveau challenge · {squad.name}",
                "squad": squad,
                "metric_labels": _METRIC_LABELS,
                "error": "Dates invalides.",
                "active_session": latest_open_session(db, user.id),
            },
        )

    try:
        challenge = create_challenge(db, squad_id, user.id, title, metric, starts, ends)
        return RedirectResponse(
            url=request.url_for("squad_challenge_detail", squad_id=squad_id, challenge_id=challenge.id),
            status_code=303,
        )
    except ChallengeError as exc:
        return templates.TemplateResponse(
            request,
            "squad_challenge_create.html",
            {
                "page_title": f"Nouveau challenge · {squad.name}",
                "squad": squad,
                "metric_labels": _METRIC_LABELS,
                "error": str(exc),
                "active_session": latest_open_session(db, user.id),
            },
        )


@router.get("/squads/{squad_id}/challenges/{challenge_id}", response_class=HTMLResponse, name="squad_challenge_detail")
def squad_challenge_detail(
    request: Request,
    squad_id: int,
    challenge_id: int,
    db: DbSession,
    user: CurrentUser,
):
    squad = get_squad_or_none(db, squad_id)
    if not squad:
        raise HTTPException(status_code=404, detail="Squad introuvable")
    if not is_member(db, squad_id, user.id):
        raise HTTPException(status_code=403, detail="Accès refusé")

    challenge = get_challenge_or_none(db, challenge_id)
    if not challenge or challenge.squad_id != squad_id:
        raise HTTPException(status_code=404, detail="Challenge introuvable")

    standings = compute_standings(db, challenge)
    return templates.TemplateResponse(
        request,
        "squad_challenge_detail.html",
        {
            "page_title": challenge.title,
            "squad": squad,
            "challenge": challenge,
            "standings": standings,
            "metric_labels": _METRIC_LABELS,
            "today": date.today(),
            "active_session": latest_open_session(db, user.id),
        },
    )


# ---------------------------------------------------------------------------
# Compare
# ---------------------------------------------------------------------------


@router.get("/squads/{squad_id}/compare", response_class=HTMLResponse, name="squad_compare")
def squad_compare(
    request: Request,
    squad_id: int,
    db: DbSession,
    user: CurrentUser,
    a: int = Query(0),
    b: int = Query(0),
):
    squad = get_squad_or_none(db, squad_id)
    if not squad:
        raise HTTPException(status_code=404, detail="Squad introuvable")
    if not is_member(db, squad_id, user.id):
        raise HTTPException(status_code=403, detail="Accès refusé")

    members = get_squad_members(db, squad_id)
    comparison = None
    if a and b and a != b:
        comparison = compute_comparison(db, squad_id, a, b)

    return templates.TemplateResponse(
        request,
        "squad_compare.html",
        {
            "page_title": f"Comparer · {squad.name}",
            "squad": squad,
            "members": members,
            "comparison": comparison,
            "selected_a": a,
            "selected_b": b,
            "active_session": latest_open_session(db, user.id),
        },
    )


# ---------------------------------------------------------------------------
# Sharing
# ---------------------------------------------------------------------------


@router.post("/squads/{squad_id}/recommend", name="squad_recommend")
def squad_recommend(
    request: Request,
    squad_id: int,
    db: DbSession,
    user: CurrentUser,
    template_slug: str = Form(...),
    # `Sb_UI_FORMULAIRES_01` — LE NOM N'EST PLUS DEMANDÉ AU CLIENT.
    #
    # Il arrivait d'un champ CACHÉ, rempli par un `onchange` inline qui recopiait
    # le TEXTE de l'option sélectionnée. Deux conséquences, l'une de forme et
    # l'autre de fond :
    #
    #   · de forme — ce `<select>` ne pouvait pas adopter la coque canonique du
    #     produit sans perdre son JS, ce qui explique en partie pourquoi il était
    #     écrit à la main ;
    #   · de fond — le nom d'une séance recommandée était fourni par le CLIENT.
    #     Rien n'obligeait `template_name` à correspondre à `template_slug`.
    #
    # Il est désormais dérivé du slug, côté serveur. Le champ reste accepté pour
    # ne casser aucun appel existant, mais il est IGNORÉ.
    template_name: str = Form(""),  # noqa: ARG001 — accepté, jamais lu
    note: str = Form(""),
):
    squad = get_squad_or_none(db, squad_id)
    if not squad:
        raise HTTPException(status_code=404, detail="Squad introuvable")
    if not is_member(db, squad_id, user.id):
        raise HTTPException(status_code=403, detail="Accès refusé")

    tpl = db.execute(
        select(WorkoutTemplate).where(WorkoutTemplate.slug == template_slug)
    ).scalar_one_or_none()
    # Un slug inconnu garde son slug comme nom plutôt que de lever : le
    # formulaire est une entrée hostile, et un 500 sur une recommandation
    # serait une réponse disproportionnée.
    nom = tpl.name if tpl else template_slug

    recommend_template(db, squad_id, user.id, template_slug, nom, note or None)
    return RedirectResponse(
        url=request.url_for("squad_detail", squad_id=squad_id),
        status_code=303,
    )


@router.post("/squads/{squad_id}/share-session", name="squad_share_session")
def squad_share_session(
    request: Request,
    squad_id: int,
    db: DbSession,
    user: CurrentUser,
    session_id: int = Form(...),
):
    squad = get_squad_or_none(db, squad_id)
    if not squad:
        raise HTTPException(status_code=404, detail="Squad introuvable")
    if not is_member(db, squad_id, user.id):
        raise HTTPException(status_code=403, detail="Accès refusé")

    try:
        share_session(db, squad_id, user.id, session_id)
    except SharingError:
        pass
    return RedirectResponse(
        url=request.url_for("squad_detail", squad_id=squad_id),
        status_code=303,
    )
