"""Custom program creation entry flow + draft tree editor.

Sb_CUSTOM_PROGRAM_WIZARD_01 — the minimal SSR entry that makes an empty draft
`UserProgram` reachable and creatable from the browser (list / new / create /
detail), cloning the squads create-flow pattern (GET form -> POST -> 303).

Sb_CUSTOM_PROGRAM_WIZARD_02 — enriches the detail page into a **draft tree
editor**: add/delete sessions, add/delete exercises (with simple rep targets),
and validate the draft. Every mutation reads the current tree, applies ONE
change to a plain payload, and hands it to the existing `replace_draft_tree`
service — so the deep business rules (quotas 7 sessions / 10 exercises,
sequential positions, editable statuses, owner-scope) stay owned and tested in
`app/services/user_program_drafts.py`. This router adds NO new service.

Sb_CUSTOM_PROGRAM_WIZARD_03 — adds a DETERMINISTIC generator: assemble a full
editable tree from curated `data/reference_split.json` templates (read-only),
written once via `replace_draft_tree`, only on an EMPTY program. The generation
logic lives in the pure `app/services/user_program_generator.py`; this router
only wires the SSR form. WIZARD_02 remains the editor for correction.

Deliberate NON-goals (spec 01 §6/§11 + build-gate order):
- NO LLM, NO opaque generation — the proposal is a deterministic assembly of
  named reference templates;
- NO scoring, NO `UserProgramQualityReview` write (a review is a publication-
  time artifact, spec 03 §9-C);
- NO publication to `WorkoutTemplate`, NO `session_builder` touch (spec 05);
- NO EKB dependency / no seed (reference_split.json is self-contained);
- NO migration — the existing draft persistence is reused as-is.

Branching the scoring/feedback layer and an EKB-assisted picker onto the flow
is WIZARD_04+.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Path, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.deps import CurrentUser, DbSession
from app.services.session_state import latest_open_session
from app.services.user_program_drafts import (
    UserProgramDraftError,
    create_draft,
    get_draft,
    list_drafts,
    replace_draft_tree,
    validate_draft,
)
from app.services.user_program_generator import (
    MAX_SESSIONS,
    SPLIT_LABELS,
    ProgramGenerationError,
    generate_program_tree,
)
from app.templating import templates

router = APIRouter(tags=["user_programs"])

# Mirrors the model column `UserProgram.title String(128)`. SQLite does not
# enforce VARCHAR length, so the upper bound is guarded here (spec 04 §6).
_MAX_TITLE = 128
# WIZARD_02 editor form bounds. The DEEP rules (quotas 7/10, sequential
# positions, editable statuses) stay owned by `replace_draft_tree`; these only
# shape the form inputs (spec 04 §5-6).
_MAX_SESSION_NAME = 128
_MAX_EXERCISE_NAME = 255
_MAX_SETS = 6
_MAX_REPS = 50


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


def _render_editor(
    request: Request, db, user, program, *, error: str | None = None
) -> HTMLResponse:
    """Render the draft editor (the detail page enriched for WIZARD_02)."""
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
            "error": error,
            "active_session": latest_open_session(db, user.id),
        },
    )


def _owned_or_404(db, user, program_id: int):
    """Owner-scoped fetch. Missing OR foreign programs return the SAME 404 (no
    existence leak) — `get_draft` already collapses both to None."""
    program = get_draft(db, user.id, program_id)
    if program is None:
        raise HTTPException(status_code=404, detail="Programme introuvable")
    return program


# ── tree ⇄ payload helpers (WIZARD_02) ──
# Each editor action reads the current tree, applies ONE mutation to a plain
# payload, then hands it back to `replace_draft_tree`. Quotas / positions /
# statuses / owner-scope are NOT re-implemented here — the service owns them.


def _tree_to_payload(program) -> list[dict]:
    """Project the ORM tree into the `replace_draft_tree` payload shape."""
    return [
        {
            "position": s.position,
            "name": s.name,
            "kind": s.kind,
            "focus": s.focus,
            "duration_target_minutes": s.duration_target_minutes,
            "notes": s.notes,
            "exercises": [
                {
                    "position": e.position,
                    "exercise_name": e.exercise_name,
                    "set_scheme": e.set_scheme,
                    "variant_key": e.variant_key,
                    "variant_group": e.variant_group,
                    "equipment_family": e.equipment_family,
                    "movement_pattern": e.movement_pattern,
                    "notes": e.notes,
                    "source_reason": e.source_reason,
                    "rep_targets": [
                        {
                            "min_reps": rt.min_reps,
                            "max_reps": rt.max_reps,
                            "technique": rt.technique,
                            "is_warmup": rt.is_warmup,
                        }
                        for rt in e.rep_targets
                    ],
                }
                for e in s.exercises
            ],
        }
        for s in program.sessions
    ]


def _resequence(payload: list[dict]) -> list[dict]:
    """Renumber sessions (1..N) and each session's exercises (1..M) so the
    service's sequential-position invariant holds after a delete."""
    for si, session in enumerate(payload, start=1):
        session["position"] = si
        for ei, exercise in enumerate(session.get("exercises", []), start=1):
            exercise["position"] = ei
    return payload


def _append_session(payload: list[dict], name: str) -> list[dict]:
    payload.append({"position": len(payload) + 1, "name": name, "exercises": []})
    return payload


def _delete_session(payload: list[dict], position: int) -> list[dict]:
    payload[:] = [s for s in payload if s["position"] != position]
    return _resequence(payload)


def _append_exercise(
    payload: list[dict],
    session_position: int,
    exercise_name: str,
    sets: int,
    min_reps: int,
    max_reps: int,
) -> bool:
    """Append an exercise to the session at `session_position`. Returns False if
    that session is absent (stale form) so the caller can surface a soft error.
    Simple rep targets: `sets` identical [min, max] ranges, `source_reason`
    'manual' — never a generated slot."""
    for session in payload:
        if session["position"] == session_position:
            exercises = session.setdefault("exercises", [])
            exercises.append(
                {
                    "position": len(exercises) + 1,
                    "exercise_name": exercise_name,
                    "set_scheme": f"{sets}x {min_reps}-{max_reps}",
                    "source_reason": "manual",
                    "rep_targets": [
                        {"min_reps": min_reps, "max_reps": max_reps}
                        # Clamp the loop bound at the sink: `sets` is already
                        # validated 1.._MAX_SETS upstream, but never loop on a
                        # raw user-controlled value (Sonar S6680, defense-in-depth).
                        for _ in range(min(sets, _MAX_SETS))
                    ],
                }
            )
            return True
    return False


def _delete_exercise(
    payload: list[dict], session_position: int, exercise_position: int
) -> list[dict]:
    for session in payload:
        if session["position"] == session_position:
            session["exercises"] = [
                e
                for e in session.get("exercises", [])
                if e["position"] != exercise_position
            ]
    return _resequence(payload)


def _validate_exercise_form(
    exercise_name: str, sets: int, min_reps: int, max_reps: int
) -> str | None:
    """Presentation-level bounds for the add-exercise form. Returns an error
    message or None."""
    if not exercise_name:
        return "Le nom de l'exercice ne peut pas être vide"
    if len(exercise_name) > _MAX_EXERCISE_NAME:
        return f"Le nom de l'exercice est trop long (maximum {_MAX_EXERCISE_NAME})."
    if not 1 <= sets <= _MAX_SETS:
        return f"Le nombre de séries doit être entre 1 et {_MAX_SETS}."
    if not 1 <= min_reps <= _MAX_REPS or not 1 <= max_reps <= _MAX_REPS:
        return f"Les répétitions doivent être entre 1 et {_MAX_REPS}."
    if min_reps > max_reps:
        return "Le minimum de répétitions doit être inférieur ou égal au maximum."
    return None


def _redirect_to_editor(request: Request, program_id: int) -> RedirectResponse:
    return RedirectResponse(
        url=request.url_for("user_program_detail", program_id=program_id),
        status_code=303,
    )


def _render_generate(
    request: Request, db, user, program, *, error: str | None = None
) -> HTMLResponse:
    """Render the deterministic-generation form (WIZARD_03)."""
    return templates.TemplateResponse(
        request,
        "user_programs/generate.html",
        {
            "page_title": f"Générer — {program.title}",
            "program": program,
            "split_labels": SPLIT_LABELS,
            "max_sessions": MAX_SESSIONS,
            "is_empty": len(program.sessions) == 0,
            "error": error,
            "active_session": latest_open_session(db, user.id),
        },
    )


# ─────────────────────────── list / create (WIZARD_01) ───────────────────────


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
    title: Annotated[str, Form()],
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
    return _redirect_to_editor(request, program.id)


# ─────────────────────────── draft editor (WIZARD_02) ────────────────────────


@router.get(
    "/programs/{program_id}",
    response_class=HTMLResponse,
    name="user_program_detail",
    responses={404: {"description": "Programme introuvable"}},
)
def user_program_detail(
    request: Request,
    program_id: int,
    db: DbSession,
    user: CurrentUser,
):
    """Draft editor. Owner-scoped via `get_draft`: a program that is missing OR
    owned by someone else returns the SAME 404 (no existence leak)."""
    return _render_editor(request, db, user, _owned_or_404(db, user, program_id))


@router.post(
    "/programs/{program_id}/sessions",
    response_class=HTMLResponse,
    name="user_program_add_session",
    responses={404: {"description": "Programme introuvable"}},
)
def user_program_add_session(
    request: Request,
    db: DbSession,
    user: CurrentUser,
    program_id: Annotated[int, Path()],
    name: Annotated[str, Form()],
):
    program = _owned_or_404(db, user, program_id)
    name = (name or "").strip()
    if not name:
        return _render_editor(
            request, db, user, program,
            error="Le nom de la séance ne peut pas être vide",
        )
    if len(name) > _MAX_SESSION_NAME:
        return _render_editor(
            request, db, user, program,
            error=f"Le nom de la séance est trop long (maximum {_MAX_SESSION_NAME}).",
        )
    payload = _append_session(_tree_to_payload(program), name)
    try:
        replace_draft_tree(db, user.id, program_id, payload)
    except UserProgramDraftError as exc:
        db.rollback()
        return _render_editor(
            request, db, user, _owned_or_404(db, user, program_id), error=str(exc)
        )
    return _redirect_to_editor(request, program_id)


@router.post(
    "/programs/{program_id}/sessions/{position}/delete",
    response_class=HTMLResponse,
    name="user_program_delete_session",
    responses={404: {"description": "Programme introuvable"}},
)
def user_program_delete_session(
    request: Request,
    db: DbSession,
    user: CurrentUser,
    program_id: Annotated[int, Path()],
    position: Annotated[int, Path()],
):
    program = _owned_or_404(db, user, program_id)
    payload = _delete_session(_tree_to_payload(program), position)
    try:
        replace_draft_tree(db, user.id, program_id, payload)
    except UserProgramDraftError as exc:
        db.rollback()
        return _render_editor(
            request, db, user, _owned_or_404(db, user, program_id), error=str(exc)
        )
    return _redirect_to_editor(request, program_id)


@router.post(
    "/programs/{program_id}/sessions/{position}/exercises",
    response_class=HTMLResponse,
    name="user_program_add_exercise",
    responses={404: {"description": "Programme introuvable"}},
)
def user_program_add_exercise(
    request: Request,
    db: DbSession,
    user: CurrentUser,
    program_id: Annotated[int, Path()],
    position: Annotated[int, Path()],
    exercise_name: Annotated[str, Form()],
    sets: Annotated[int, Form()],
    min_reps: Annotated[int, Form()],
    max_reps: Annotated[int, Form()],
):
    program = _owned_or_404(db, user, program_id)
    exercise_name = (exercise_name or "").strip()
    error = _validate_exercise_form(exercise_name, sets, min_reps, max_reps)
    if error is not None:
        return _render_editor(request, db, user, program, error=error)
    payload = _tree_to_payload(program)
    if not _append_exercise(
        payload, position, exercise_name, sets, min_reps, max_reps
    ):
        return _render_editor(request, db, user, program, error="Séance introuvable.")
    try:
        replace_draft_tree(db, user.id, program_id, payload)
    except UserProgramDraftError as exc:
        db.rollback()
        return _render_editor(
            request, db, user, _owned_or_404(db, user, program_id), error=str(exc)
        )
    return _redirect_to_editor(request, program_id)


@router.post(
    "/programs/{program_id}/sessions/{session_position}/exercises/{exercise_position}/delete",
    response_class=HTMLResponse,
    name="user_program_delete_exercise",
    responses={404: {"description": "Programme introuvable"}},
)
def user_program_delete_exercise(
    request: Request,
    db: DbSession,
    user: CurrentUser,
    program_id: Annotated[int, Path()],
    session_position: Annotated[int, Path()],
    exercise_position: Annotated[int, Path()],
):
    program = _owned_or_404(db, user, program_id)
    payload = _delete_exercise(
        _tree_to_payload(program), session_position, exercise_position
    )
    try:
        replace_draft_tree(db, user.id, program_id, payload)
    except UserProgramDraftError as exc:
        db.rollback()
        return _render_editor(
            request, db, user, _owned_or_404(db, user, program_id), error=str(exc)
        )
    return _redirect_to_editor(request, program_id)


@router.post(
    "/programs/{program_id}/validate",
    response_class=HTMLResponse,
    name="user_program_validate",
    responses={404: {"description": "Programme introuvable"}},
)
def user_program_validate(
    request: Request,
    db: DbSession,
    user: CurrentUser,
    program_id: Annotated[int, Path()],
):
    _owned_or_404(db, user, program_id)  # 404 guard; validate_draft re-checks ownership
    try:
        validate_draft(db, user.id, program_id)
    except UserProgramDraftError as exc:
        db.rollback()
        return _render_editor(
            request, db, user, _owned_or_404(db, user, program_id), error=str(exc)
        )
    return _redirect_to_editor(request, program_id)


# ─────────────────── deterministic generation (WIZARD_03) ────────────────────


@router.get(
    "/programs/{program_id}/generate",
    response_class=HTMLResponse,
    name="user_program_generate_form",
    responses={404: {"description": "Programme introuvable"}},
)
def user_program_generate_form(
    request: Request,
    db: DbSession,
    user: CurrentUser,
    program_id: Annotated[int, Path()],
):
    """Deterministic-generation form. Owner-scoped 404 like every program route."""
    return _render_generate(request, db, user, _owned_or_404(db, user, program_id))


@router.post(
    "/programs/{program_id}/generate",
    response_class=HTMLResponse,
    name="user_program_generate",
    responses={404: {"description": "Programme introuvable"}},
)
def user_program_generate(
    request: Request,
    db: DbSession,
    user: CurrentUser,
    program_id: Annotated[int, Path()],
    split: Annotated[str, Form()],
    sessions: Annotated[int, Form()],
):
    program = _owned_or_404(db, user, program_id)
    # Generation ONLY on an empty tree: `replace_draft_tree` overwrites the whole
    # tree, so generating over an existing program would destroy manual work.
    if program.sessions:
        return _render_generate(
            request, db, user, program,
            error="Ce programme contient déjà des séances. "
            "Videz-le ou créez-en un autre pour générer une base.",
        )
    if split not in SPLIT_LABELS:
        return _render_generate(
            request, db, user, program, error="Style de split inconnu."
        )
    if not 1 <= sessions <= MAX_SESSIONS:
        return _render_generate(
            request, db, user, program,
            error=f"Le nombre de séances doit être entre 1 et {MAX_SESSIONS}.",
        )
    try:
        payload = generate_program_tree(split, sessions)
        replace_draft_tree(db, user.id, program_id, payload)
    except (ProgramGenerationError, UserProgramDraftError) as exc:
        db.rollback()
        return _render_generate(
            request, db, user, _owned_or_404(db, user, program_id), error=str(exc)
        )
    return _redirect_to_editor(request, program_id)
