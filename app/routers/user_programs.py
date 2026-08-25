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

Sb_CUSTOM_PROGRAM_WIZARD_04 — surfaces a NON-PERSISTED quality preview of the
draft: a dedicated read-only `GET /programs/{id}/quality` reuses the pure
SCORING_01 engine + SCORING_02 feedback layer (via the pure
`app/services/user_program_quality_preview.py`) to show a grade, sub-scores and
plain-language feedback. It writes NOTHING — reusing the SAME adapter as the
SCORING_03 writer so a preview and a future persisted trace of the same version
compute identically. Scorable eras only (draft/validated), and an empty draft
gets a friendly prompt instead of a misleading grade.

Deliberate NON-goals (spec 01 §6/§11 + build-gate order):
- NO LLM, NO opaque generation — the proposal is a deterministic assembly of
  named reference templates;
- NO `UserProgramQualityReview` write and NO DB mutation from the preview (a
  persisted review is a publication-time artifact, spec 03 §9-C); scoring is
  surfaced read-only, never persisted here;
- NO publication to `WorkoutTemplate`, NO `session_builder` touch (spec 05);
- NO EKB dependency / no seed (reference_split.json is self-contained);
- NO migration — the existing draft persistence is reused as-is.

An EKB-assisted exercise picker onto the flow is WIZARD_05+.
"""
from __future__ import annotations

import logging
import re
import unicodedata
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Path, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.deps import CurrentUser, DbSession
from app.services.program_quality_reviews import SCORABLE_STATUSES
from app.services.session_builder import instantiate_session
from app.services.session_state import latest_open_session
from app.services.user_program_drafts import (
    UserProgramDraftError,
    create_draft,
    get_draft,
    list_drafts,
    replace_draft_tree,
    validate_draft,
)
from app.services.user_program_exercise_catalog import enrich, picker_options
from app.services.user_program_generator import (
    MAX_SESSIONS,
    SPLIT_LABELS,
    ProgramGenerationError,
    generate_program_tree,
)
from app.services.user_program_launch import (
    LaunchNotFound,
    resolve_owned_published_template,
)
from app.services.user_program_publish import (
    PublishNotFound,
    PublishRefused,
    publication_slug,
    publish_user_program,
)
from app.services.user_program_quality_preview import compute_quality_preview
from app.services.user_program_versioning import (
    VersioningNotFound,
    VersioningRefused,
    start_new_edit_cycle,
)
from app.templating import templates

router = APIRouter(tags=["user_programs"])

logger = logging.getLogger(__name__)

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
# Owner-scoped 404 detail, reused across routes (missing OR foreign, no existence leak).
_NOT_FOUND = "Programme introuvable"


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
            # WIZARD_05 — read-only EKB picker options (all 103 canonical names)
            # for the add-exercise <datalist>. Single common render path → every
            # editor re-render inherits the same catalog, no duplicated loading.
            "picker_options": picker_options(),
            "error": error,
            "active_session": latest_open_session(db, user.id),
        },
    )


def _owned_or_404(db, user, program_id: int):
    """Owner-scoped fetch. Missing OR foreign programs return the SAME 404 (no
    existence leak) — `get_draft` already collapses both to None."""
    program = get_draft(db, user.id, program_id)
    if program is None:
        raise HTTPException(status_code=404, detail=_NOT_FOUND)
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
                    # WIZARD_05 — denormalized EKB fields for an EXACT canonical
                    # match; `enrich` returns {} for free-text (fields stay
                    # absent/null). Spread FIRST so the explicit contract keys
                    # below always win: `exercise_name` verbatim, source_reason
                    # 'manual'. No EKB DB dependency (JSON read-only).
                    **enrich(exercise_name),
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
    request: Request,
    db,
    user,
    program,
    *,
    error: str | None = None,
    notice: str | None = None,
) -> HTMLResponse:
    """Render the deterministic-generation form (WIZARD_03, regeneration WIZARD_06)."""
    sessions = program.sessions
    exercises = [exercise for session in sessions for exercise in session.exercises]
    return templates.TemplateResponse(
        request,
        "user_programs/generate.html",
        {
            "page_title": f"Générer — {program.title}",
            "program": program,
            "split_labels": SPLIT_LABELS,
            "max_sessions": MAX_SESSIONS,
            "is_empty": len(sessions) == 0,
            # WIZARD_06 — a regeneration REPLACES the whole tree, so the form states exactly
            # what would be lost. A bare "this will overwrite" is not informed consent.
            "has_existing_tree": len(sessions) > 0,
            "existing_session_count": len(sessions),
            "existing_exercise_count": len(exercises),
            "existing_set_count": sum(len(exercise.rep_targets) for exercise in exercises),
            "error": error,
            # WIZARD_06 — an unconfirmed replacement is NOT an error: the user did nothing
            # wrong, the form simply has not been agreed to yet. Painting it in the danger
            # colour would say "you made a mistake" when the answer is "please confirm".
            "notice": notice,
            "active_session": latest_open_session(db, user.id),
        },
    )


def _render_quality(
    request: Request, db, user, program, *, scorable: bool, is_empty: bool, preview
) -> HTMLResponse:
    """Render the non-persisted quality preview (WIZARD_04).

    `preview` is a `QualityPreview` only when the draft is both scorable and
    non-empty; otherwise it is None and the template shows a friendly prompt.
    """
    return templates.TemplateResponse(
        request,
        "user_programs/quality.html",
        {
            "page_title": f"Qualité — {program.title}",
            "program": program,
            "scorable": scorable,
            "is_empty": is_empty,
            "preview": preview,
            "active_session": latest_open_session(db, user.id),
        },
    )


# ─────────────────────────── list / create (WIZARD_01) ───────────────────────


def _weekly_plan_proposal(db, user_id: int) -> dict | None:
    """Le plan hebdomadaire proposé, prêt à être affiché — ou `None`.

    Confiné : toute panne de la chaîne de planification laisse la page des
    programmes strictement inchangée. Proposer un programme est un **plus** ;
    ce n'est jamais une raison de casser la bibliothèque existante.
    """
    try:
        from app.services.muscle_mapping import RADAR_AXES
        from app.services.training_preferences import get_training_preferences
        from app.services.weekly_plan_materialization import (
            assess_materialization,
        )
        from app.services.weekly_planner import build_weekly_plan_for_user

        preferences = get_training_preferences(db, user_id)
        if preferences is None or not preferences.sessions_per_week:
            return None
        plan = build_weekly_plan_for_user(db, user_id)
        readiness = assess_materialization(plan)
        if not readiness.can_materialize:
            return None
        return {
            "sessions": readiness.sessions,
            "exercises": readiness.exercises,
            "planned_sets": readiness.planned_sets,
            "status": readiness.status.value,
            "priorities": [
                RADAR_AXES[axis]["label"]
                for axis in (preferences.focus_priorities or ())
                if axis in RADAR_AXES
            ],
            "constraints": list(readiness.unserved_priorities),
            "unmet_zones": len(readiness.unmet_zones),
        }
    # Confinement volontaire et large : voir la docstring. Toute panne de la
    # chaîne de planification doit laisser la bibliothèque servie.
    except Exception:  # noqa: BLE001
        return None


@router.get("/programs", response_class=HTMLResponse, name="user_programs_list")
def user_programs_list(request: Request, db: DbSession, user: CurrentUser):
    """Owner-scoped library of the current user's custom programs (archived
    excluded — `list_drafts` filters them by default)."""
    # `UX4_02` / TRAIN 2 — LE PLAN A QUITTÉ CETTE SURFACE.
    #
    # « Mes programmes » répond à « qu'est-ce que j'ai créé ». La proposition
    # hebdomadaire et son explication répondent à « comment je veux
    # m'entraîner » — c'est la question de **Mon plan**, et elles y vivent
    # désormais avec la déclaration qui les produit. Aucune des deux n'est
    # supprimée : elles sont réunies avec ce qui les explique.
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


@router.get("/plan", response_class=HTMLResponse, name="user_plan")
def user_plan(request: Request, db: DbSession, user: CurrentUser):
    """`UX4_02` / TRAIN 2 — **Mon plan**.

    Réunit ce qui ne pouvait pas se lire séparément : la déclaration
    d'entraînement, le plan qu'elle produit, et l'explication de ce plan.

    L'éditeur de préférences arrive du Profil, où le gabarit lui-même
    déclarait son emplacement TRANSITIONNEL en attendant `UX4_02`. La route de
    soumission et les noms de champs sont inchangés — ce sont des contrats.

    ⚠ AUCUN MOTEUR OPAQUE (`OPERATOR_DECISION` C8). `build_weekly_plan_for_user`
    ne lit que les déclarations ; `build_plan_explanation` cite ses sources une
    par une. Sans déclaration, il n'y a pas de plan, et c'est dit.
    """
    from app.services.muscle_mapping import RADAR_AXES
    from app.services.training_preferences import (
        EQUIPMENT_FAMILY_VOCAB,
        FOCUS_PRIORITY_VOCAB,
        SESSIONS_PER_WEEK_MAX,
        SESSIONS_PER_WEEK_MIN,
        equipment_family_label,
        focus_priority_label,
        get_training_preferences,
    )

    preferences = get_training_preferences(db, user.id)
    labels = [
        RADAR_AXES[axis]["label"]
        for axis in ((preferences.focus_priorities if preferences else None) or ())
        if axis in RADAR_AXES
    ]
    return templates.TemplateResponse(
        request,
        "user_programs/plan.html",
        {
            "page_title": "Mon plan",
            "preferences": preferences or _NO_PREFERENCES,
            "priority_labels": labels,
            # Les trois vocabulaires de l'éditeur voyagent AVEC lui. Sans eux
            # le formulaire rend ses légendes et zéro option : une grille de
            # cadence vide, muette, et qu'aucune erreur ne signale — Jinja
            # itère sur `Undefined` sans rien dire.
            "focus_vocab": [
                (key, focus_priority_label(key)) for key in FOCUS_PRIORITY_VOCAB
            ],
            "equipment_vocab": [
                (key, equipment_family_label(key)) for key in EQUIPMENT_FAMILY_VOCAB
            ],
            "sessions_range": list(
                range(SESSIONS_PER_WEEK_MIN, SESSIONS_PER_WEEK_MAX + 1)
            ),
            "weekly_plan_proposal": _weekly_plan_proposal(db, user.id),
            # Sb_ORCHESTRATOR_EXPLAINER_01 — lecture seule, jamais bloquante.
            "plan_explanation": _plan_explanation(db, user.id),
            "active_session": latest_open_session(db, user.id),
            "pref_saved": request.query_params.get("pref_saved") == "1",
            "pref_error": request.query_params.get("pref_error") == "1",
        },
    )


class _NoPreferences:
    """Aucune préférence enregistrée — les trois champs sont NON DÉCLARÉS.

    `None` pour `available_equipment` est significatif et distinct de `[]` :
    « pas déclaré » n'est pas « déclaré vide ». Un objet plutôt qu'un `dict`
    pour que le gabarit lise les mêmes attributs dans les deux cas.
    """

    sessions_per_week = None
    focus_priorities = None
    available_equipment = None


_NO_PREFERENCES = _NoPreferences()


def _plan_explanation(db, user_id: int):
    """« Pourquoi ce plan ? » — l'explication ne peut pas casser la page.

    `build_plan_explanation` avale déjà ses erreurs, mais la même leçon que
    pour le collecteur s'applique : une garantie qui dépend de la discipline
    interne de l'appelé n'en est pas une. `/programs` doit s'afficher même si
    la couche d'explication est entièrement cassée.
    """
    from app.services.orchestrator_explainer import (
        PlanExplanation,
        build_plan_explanation,
    )

    try:
        return build_plan_explanation(db, user_id)
    except Exception:  # noqa: BLE001
        logger.exception("plan explanation failed; /programs stays usable")
        return PlanExplanation(items=(), available=False)


@router.post(
    "/programs/from-weekly-plan",
    response_class=HTMLResponse,
    name="user_program_from_weekly_plan",
)
def user_program_from_weekly_plan(
    request: Request, db: DbSession, user: CurrentUser
):
    """Matérialise le plan hebdomadaire proposé en **brouillon**.

    Action explicite de l'utilisateur, jamais automatique. Rien n'est publié :
    la page suivante est l'éditeur de brouillon habituel, où la validation puis
    la publication restent des gestes séparés.
    """
    from app.services.weekly_plan_materialization import (
        DEFAULT_PROGRAM_TITLE,
        materialize_weekly_plan,
    )
    from app.services.weekly_planner import build_weekly_plan_for_user

    try:
        plan = build_weekly_plan_for_user(db, user.id)
        program, _ = materialize_weekly_plan(
            db, user.id, plan,
            title=DEFAULT_PROGRAM_TITLE,
            slug_base=_slugify(DEFAULT_PROGRAM_TITLE),
        )
    except UserProgramDraftError as exc:
        # Quota, collision de slug, plan sans rien d'exécutable : message du
        # service, jamais un 500.
        return _render_new(request, db, user, title="", error=str(exc))

    # Sb_DECISION_ANALYTICS_RUNTIME_01 — observation APRÈS la décision produit,
    # et seulement ici.
    #
    # La matérialisation est le vrai point de décision : l'utilisateur agit. Un
    # rendu de `/programs` calcule aussi une proposition, mais l'observer
    # écrirait un groupe de traces à chaque affichage de page — c'est exactement
    # ce que l'opérateur interdit pour la récupération et la morphologie
    # (« pas à chaque rendu de read-model »), et la même règle vaut ici.
    #
    # Double garde, délibérément. `observe_plan_generation_for_user` avale déjà
    # ses erreurs, mais une garantie qui dépend de la discipline interne de
    # l'appelé n'est pas une garantie : le jour où quelqu'un modifie
    # l'observateur et le laisse lever, cette route rendrait 500 alors que le
    # brouillon est **déjà créé et valide**. Le brouillon prime sur sa trace.
    try:
        from app.services.decision_analytics import (
            observe_plan_generation_for_user,
        )

        observe_plan_generation_for_user(db, user.id, plan)
    except Exception:  # noqa: BLE001
        logger.exception(
            "decision-trace observation failed; draft %s stays valid", program.id
        )

    return _redirect_to_editor(request, program.id)


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
    responses={404: {"description": _NOT_FOUND}},
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
    responses={404: {"description": _NOT_FOUND}},
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
    responses={404: {"description": _NOT_FOUND}},
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
    responses={404: {"description": _NOT_FOUND}},
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
    responses={404: {"description": _NOT_FOUND}},
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
    responses={404: {"description": _NOT_FOUND}},
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
    responses={404: {"description": _NOT_FOUND}},
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
    responses={404: {"description": _NOT_FOUND}},
)
def user_program_generate(
    request: Request,
    db: DbSession,
    user: CurrentUser,
    program_id: Annotated[int, Path()],
    split: Annotated[str, Form()],
    sessions: Annotated[int, Form()],
    confirm_replace: Annotated[bool, Form()] = False,
):
    program = _owned_or_404(db, user, program_id)
    # WIZARD_06 — regeneration over a filled program is allowed, but only on an EXPLICIT
    # confirmation. `replace_draft_tree` overwrites the whole tree, so an unconfirmed POST
    # would silently destroy manual work; the previous hard refusal protected against that
    # but also left the user with no way through except emptying the program by hand.
    #
    # Unconfirmed is not an error the user made: the form simply has not been agreed to yet,
    # so this returns 200 with the summary and the checkbox rather than a failure.
    if program.sessions and not confirm_replace:
        return _render_generate(
            request, db, user, program,
            notice="Ce programme contient déjà des séances. "
            "Cochez la confirmation pour remplacer l'arbre existant.",
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


# ─────────────────── non-persisted quality preview (WIZARD_04) ────────────────


@router.get(
    "/programs/{program_id}/quality",
    response_class=HTMLResponse,
    name="user_program_quality",
    responses={404: {"description": _NOT_FOUND}},
)
def user_program_quality(
    request: Request,
    db: DbSession,
    user: CurrentUser,
    program_id: Annotated[int, Path()],
):
    """Non-persisted quality preview. Owner-scoped 404 like every program route.

    Reads the scored draft and renders it — writing NOTHING. Only the edition
    eras (draft/validated) get a scorecard; an empty draft gets a friendly
    prompt rather than a misleading grade computed on zero exercises.
    """
    program = _owned_or_404(db, user, program_id)
    scorable = program.archived_at is None and program.status in SCORABLE_STATUSES
    is_empty = sum(len(s.exercises) for s in program.sessions) == 0
    preview = (
        compute_quality_preview(program) if scorable and not is_empty else None
    )
    return _render_quality(
        request, db, user, program,
        scorable=scorable, is_empty=is_empty, preview=preview,
    )


# ──────────────────── publication to catalog (PUBLICATION_01) ─────────────────


def _publish_rows(program, user) -> list[dict]:
    """Per-session preview rows for the publish page.

    A published program shows the FROZEN slugs (`template_slug_snapshot`); a
    not-yet-published one shows the SAME slug the service will mint — so the page
    never promises a slug the materializer would not produce."""
    published = program.status == "published" and program.archived_at is None
    rows = []
    for session in program.sessions:
        slug = (
            session.template_slug_snapshot
            if published
            else publication_slug(
                user.id, program.slug_base, program.current_version, session.position
            )
        )
        rows.append(
            {
                "position": session.position,
                "name": session.name,
                "slug": slug,
                "exercise_count": len(session.exercises),
            }
        )
    return rows


def _render_publish(
    request: Request,
    db,
    user,
    program,
    *,
    error: str | None = None,
    success: str | None = None,
) -> HTMLResponse:
    """Render the SSR publication confirmation/status page (no JS)."""
    is_archived = program.archived_at is not None or program.status == "archived"
    is_published = program.status == "published" and not is_archived
    return templates.TemplateResponse(
        request,
        "user_programs/publish.html",
        {
            "page_title": f"Publier — {program.title}",
            "program": program,
            "rows": _publish_rows(program, user),
            "session_count": len(program.sessions),
            # A validated, non-archived program is the only publishable state.
            "publishable": program.status == "validated" and not is_archived,
            "is_published": is_published,
            "is_archived": is_archived,
            "is_draft": program.status == "draft" and not is_archived,
            "error": error,
            "success": success,
            "active_session": latest_open_session(db, user.id),
        },
    )


@router.get(
    "/programs/{program_id}/publish",
    response_class=HTMLResponse,
    name="user_program_publish_form",
    responses={404: {"description": _NOT_FOUND}},
)
def user_program_publish_form(
    request: Request,
    db: DbSession,
    user: CurrentUser,
    program_id: Annotated[int, Path()],
):
    """Publication confirmation/status page. Owner-scoped 404 like every route.

    Shows how many sessions would publish, their future (or frozen) template
    slugs, and the immutable-publication warning. Writes nothing."""
    return _render_publish(request, db, user, _owned_or_404(db, user, program_id))


@router.post(
    "/programs/{program_id}/publish",
    response_class=HTMLResponse,
    name="user_program_publish",
    responses={404: {"description": _NOT_FOUND}},
)
def user_program_publish(
    request: Request,
    db: DbSession,
    user: CurrentUser,
    program_id: Annotated[int, Path()],
):
    """Materialize a validated program into N user-owned templates.

    Owner-scoped: a missing/foreign program 404s. A lifecycle refusal
    (draft/archived/slug clash) returns 200 with a soft message and NO template
    created. Success re-renders the published state (idempotent on re-submit)."""
    _owned_or_404(db, user, program_id)  # 404 guard; the service re-checks ownership
    try:
        result = publish_user_program(db, user.id, program_id)
    except PublishNotFound as exc:
        raise HTTPException(status_code=404, detail=_NOT_FOUND) from exc
    except PublishRefused as exc:
        db.rollback()
        return _render_publish(
            request, db, user, _owned_or_404(db, user, program_id), error=exc.message
        )
    program = _owned_or_404(db, user, program_id)
    success = (
        f"Programme publié : {len(result.templates)} séance(s) disponible(s) "
        "dans vos modèles."
        if result.created
        else "Ce programme est déjà publié — aucune séance dupliquée."
    )
    return _render_publish(request, db, user, program, success=success)


# ─────────────────── new edit cycle from published (PUBLICATION_02) ────────────


@router.post(
    "/programs/{program_id}/new-version",
    response_class=HTMLResponse,
    name="user_program_new_version",
    responses={404: {"description": _NOT_FOUND}},
)
def user_program_new_version(
    request: Request,
    db: DbSession,
    user: CurrentUser,
    program_id: Annotated[int, Path()],
):
    """Start a new edit cycle on a PUBLISHED program (spec 04 §6-7, mono-row).

    The same `UserProgram` row returns to `draft` at `current_version + 1`; the
    published v{n} templates are untouched. Owner-scoped 404. An archived program
    is softly refused; a draft/validated program is already editable (no
    increment). Success → the existing editor (the returned draft)."""
    _owned_or_404(db, user, program_id)  # 404 guard; the service re-checks ownership
    try:
        start_new_edit_cycle(db, user.id, program_id)
    except VersioningNotFound as exc:
        raise HTTPException(status_code=404, detail=_NOT_FOUND) from exc
    except VersioningRefused as exc:
        db.rollback()
        return _render_editor(
            request, db, user, _owned_or_404(db, user, program_id), error=exc.message
        )
    return _redirect_to_editor(request, program_id)


# ─────────────── launch a published session template (PUBLICATION_03) ───────────────


@router.post(
    "/programs/{program_id}/sessions/{session_id}/start",
    name="user_program_start_session",
    responses={404: {"description": _NOT_FOUND}},
)
def user_program_start_session(
    db: DbSession,
    user: CurrentUser,
    program_id: Annotated[int, Path()],
    session_id: Annotated[int, Path()],
) -> RedirectResponse:
    """Launch an OWNED, PUBLISHED session as a real WorkoutSession (spec 05 §14).

    Ownership is resolved through `UserProgram (owner) → UserProgramSession →
    published_template_id` — a missing/foreign/not-published session is an indistinct
    404 (no existence leak). The published `WorkoutTemplate` is instantiated via the
    existing `session_builder` (reused, unchanged) and never mutated; the program is
    never mutated. Success → the existing session page."""
    try:
        template = resolve_owned_published_template(db, user.id, program_id, session_id)
    except LaunchNotFound as exc:
        raise HTTPException(status_code=404, detail=_NOT_FOUND) from exc
    session = instantiate_session(db, template, datetime.now(UTC), user_id=user.id)
    db.commit()  # instantiate_session already stages the session (session_builder.py:82)
    db.refresh(session)
    return RedirectResponse(url=f"/sessions/{session.id}", status_code=303)
