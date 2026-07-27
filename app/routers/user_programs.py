"""Custom program creation entry flow (Sb_CUSTOM_PROGRAM_WIZARD_01).

First user-facing surface of the Custom Program track: the minimal SSR entry
that makes an empty draft `UserProgram` reachable from the browser. Everything
below the HTTP line already exists and is owner-scoped + quota-guarded
(`app/services/user_program_drafts.py`); this router adds only the thin SSR
layer, cloning the squads create-flow pattern (GET form -> POST -> 303).

Deliberate NON-goals of this first build (spec 01 §6 + build-gate order):
- NO generator (no deterministic proposition, no LLM) — creation is MANUAL;
- NO scoring, NO `UserProgramQualityReview` write (a review is a publication-
  time artifact, spec 03 §9-C);
- NO publication to `WorkoutTemplate`, NO `session_builder` touch (spec 05);
- NO migration — the existing draft persistence is reused as-is.

The card editor (tree editing via `replace_draft_tree`) is WIZARD_02; branching
the scoring/feedback layer onto the flow is WIZARD_03+.
"""
from __future__ import annotations

import re
import unicodedata

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.deps import CurrentUser, DbSession
from app.services.session_state import latest_open_session
from app.services.user_program_drafts import (
    UserProgramDraftError,
    create_draft,
    get_draft,
    list_drafts,
)
from app.templating import templates

router = APIRouter(tags=["user_programs"])

# Mirrors the model column `UserProgram.title String(128)`. SQLite does not
# enforce VARCHAR length, so the upper bound is guarded here (spec 04 §6).
_MAX_TITLE = 128


def _slugify(value: str) -> str:
    """Derive a URL/publication-safe `slug_base` from a free title.

    ASCII-only, lowercase, hyphen-separated, bounded to 64 chars — it becomes
    the base of the future published slug `up{user_id}-{slug_base}-v{n}`
    (spec 05 §5). Accents are neutralised via NFKD; every unsafe run collapses
    to a single hyphen. Never asked from the user. A title that slugifies to
    empty (all-symbol) falls back to a stable literal so `create_draft` never
    receives a blank slug; a genuine per-user collision then surfaces the
    service's gentle message (no silent auto-suffix in WIZARD_01).
    """
    normalized = unicodedata.normalize("NFKD", value)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    hyphenated = re.sub(r"[^a-z0-9]+", "-", ascii_only.lower()).strip("-")
    return hyphenated[:64].strip("-") or "programme"


def _render_new(
    request: Request, db, user, *, title: str, error: str | None
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "user_programs/new.html",
        {
            "page_title": "Créer un programme",
            "error": error,
            "title_value": title,
            "active_session": latest_open_session(db, user.id),
        },
    )


@router.get("/programs", response_class=HTMLResponse, name="user_programs_list")
def user_programs_list(request: Request, db: DbSession, user: CurrentUser):
    """Owner-scoped library of the current user's custom programs (archived
    excluded — `list_drafts` filters them by default)."""
    programs = list_drafts(db, user.id)
    return templates.TemplateResponse(
        request,
        "user_programs/list.html",
        {
            "page_title": "Mes programmes",
            "programs": programs,
            "active_session": latest_open_session(db, user.id),
        },
    )


# Declared BEFORE `/programs/{program_id}`: even though `{program_id:int}`
# would 422 (not shadow) on "new", the explicit order is the contract.
@router.get("/programs/new", response_class=HTMLResponse, name="user_program_new")
def user_program_new(request: Request, db: DbSession, user: CurrentUser):
    return _render_new(request, db, user, title="", error=None)


@router.post("/programs", response_class=HTMLResponse, name="user_program_create")
def user_program_create(
    request: Request,
    db: DbSession,
    user: CurrentUser,
    title: str = Form(...),
):
    title = (title or "").strip()
    if not title:
        return _render_new(
            request, db, user, title="", error="Le titre ne peut pas être vide"
        )
    if len(title) > _MAX_TITLE:
        return _render_new(
            request,
            db,
            user,
            title=title,
            error=f"Le titre est trop long (maximum {_MAX_TITLE} caractères)",
        )
    try:
        program = create_draft(db, user.id, title, _slugify(title))
    except UserProgramDraftError as exc:
        # Quota reached / slug collision / service refusal — surface the
        # service's gentle, actionable message; never a 500.
        return _render_new(request, db, user, title=title, error=str(exc))
    return RedirectResponse(
        url=request.url_for("user_program_detail", program_id=program.id),
        status_code=303,
    )


@router.get(
    "/programs/{program_id}",
    response_class=HTMLResponse,
    name="user_program_detail",
)
def user_program_detail(
    request: Request,
    program_id: int,
    db: DbSession,
    user: CurrentUser,
):
    """Minimal read-only recap. Owner-scoped via `get_draft`: a program that is
    missing OR owned by someone else returns the SAME 404 (no existence leak)."""
    program = get_draft(db, user.id, program_id)
    if program is None:
        raise HTTPException(status_code=404, detail="Programme introuvable")
    session_count = len(program.sessions)
    exercise_count = sum(len(s.exercises) for s in program.sessions)
    return templates.TemplateResponse(
        request,
        "user_programs/detail.html",
        {
            "page_title": program.title,
            "program": program,
            "session_count": session_count,
            "exercise_count": exercise_count,
            "active_session": latest_open_session(db, user.id),
        },
    )
