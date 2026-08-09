"""Publish a validated custom program into user-owned catalog templates.

Sb_CUSTOM_PROGRAM_PUBLICATION_01 — the gated materialization step of the Custom
Program cycle (spec 05 §6). A *validated* `UserProgram` becomes a set of live,
launchable `WorkoutTemplate`s the owner can start like any catalog session.

Materialization contract (spec 05 §6 — N templates, NOT one flattened):
  - ONE `UserProgramSession` → ONE custom `WorkoutTemplate`. A program of N
    sessions materializes N templates (never a single flattened container).
  - Each template's slug is `up{user_id}-{slug_base}-v{current_version}-s{position}`,
    deterministically truncated to fit `WorkoutTemplate.slug` (64 chars).
  - Each template carries `catalog_section = "user"` — the reserved section the
    seed wipe-guard (`app/services/seed.py`) refuses to recreate and never
    deletes, so **user templates survive a reseed**.
  - The program→template link lives on the SESSION: `published_template_id` +
    `template_slug_snapshot` (PUBLICATION_01 migration).
  - Exercises copy in stable order with catalog codes `E1..En`; rep targets copy
    as working sets (warmups stay generated at instantiation, catalog parity —
    `session_builder.instantiate_session` therefore runs unchanged).

Lifecycle rules (spec 04 §6-7):
  - Only a `validated` program publishes. `draft` gets a soft "validate first",
    `archived` a soft "unarchive first" — neither creates a template.
  - Publication is idempotent: an already-`published` program returns its
    existing templates without creating duplicates.
  - Publication freezes quality ONCE via the existing
    `compute_and_store_quality_review` — called while the program is still
    `validated` (that writer refuses a non-scorable status), BEFORE the flip to
    `published`.
  - No silent overwrite: a slug clash surfaces a soft refusal, never a 500 and
    never a mutated built-in template.

Owner-scope: a missing OR foreign program raises the SAME `PublishNotFound`
(no existence leak), mirroring the other custom-program services.
"""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.catalog import RepTarget, TemplateExercise, WorkoutTemplate
from app.models.user_program import (
    UserProgram,
    UserProgramExercise,
    UserProgramSession,
)
from app.services.program_quality_reviews import (
    QualityReviewError,
    compute_and_store_quality_review,
)
from app.services.seed import CUSTOM_CATALOG_SECTION

# `WorkoutTemplate.slug` is VARCHAR(64); SQLite does not enforce it, so the
# publication slug is bounded here (spec 05 §5).
_SLUG_MAX = 64
# `WorkoutTemplate.name` is VARCHAR(128).
_NAME_MAX = 128


class PublishError(Exception):
    """Base error for the publication flow."""


class PublishNotFound(PublishError):
    """Program missing OR owned by someone else — indistinct, no leak (→ 404)."""


class PublishRefused(PublishError):
    """Publication refused for a lifecycle reason (draft/archived/slug clash).

    A soft, actionable message — the router renders it at 200, not a 500: the
    user did nothing wrong, the program simply is not in a publishable state.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


@dataclass
class PublishResult:
    """Outcome of a publish attempt.

    `created` is True only when this call materialized the templates; an
    idempotent re-publish of an already-published program returns the existing
    templates with `created=False`.
    """

    program: UserProgram
    templates: list[WorkoutTemplate]
    created: bool


def publication_slug(
    user_id: int, slug_base: str, version: int, position: int
) -> str:
    """Deterministic publication slug, guaranteed to fit `_SLUG_MAX` (64).

    Shape `up{user_id}-{slug_base}-v{version}-s{position}`; only the free
    `slug_base` is truncated (the fixed identity parts always survive), and any
    trailing hyphen left by truncation is stripped so the slug stays clean.
    """
    prefix = f"up{user_id}"
    suffix = f"-v{version}-s{position}"
    # -1 reserves the hyphen that joins prefix and base.
    room = _SLUG_MAX - len(prefix) - len(suffix) - 1
    base = slug_base[:room].rstrip("-") if room > 0 else ""
    core = f"-{base}" if base else ""
    return f"{prefix}{core}{suffix}"


def _load_owned(db: Session, user_id: int, program_id: int) -> UserProgram:
    """Owner-scoped program with its full tree. Missing/foreign → PublishNotFound."""
    program = db.execute(
        select(UserProgram)
        .where(UserProgram.user_id == user_id, UserProgram.id == program_id)
        .options(
            selectinload(UserProgram.sessions)
            .selectinload(UserProgramSession.exercises)
            .selectinload(UserProgramExercise.rep_targets)
        )
    ).scalar_one_or_none()
    if program is None:
        raise PublishNotFound("Programme introuvable")
    return program


def _existing_templates(
    db: Session, program: UserProgram
) -> list[WorkoutTemplate]:
    """Templates already linked from a published program's sessions."""
    ids = [
        s.published_template_id
        for s in program.sessions
        if s.published_template_id is not None
    ]
    if not ids:
        return []
    return list(
        db.execute(
            select(WorkoutTemplate)
            .where(WorkoutTemplate.id.in_(ids))
            .order_by(WorkoutTemplate.display_order, WorkoutTemplate.slug)
        )
        .scalars()
        .all()
    )


def _template_name(program: UserProgram, session: UserProgramSession) -> str:
    """« {program title} — {session name} », bounded to the column width."""
    return f"{program.title} — {session.name}"[:_NAME_MAX]


def _materialize_session(
    program: UserProgram, session: UserProgramSession, slug: str
) -> WorkoutTemplate:
    """Build (not add) ONE custom `WorkoutTemplate` from one program session.

    Exercises copy in stable position order with fresh catalog codes `E1..En`
    and sequential positions; only WORKING rep targets copy (warmups are
    regenerated by `session_builder` at instantiation, catalog parity), re-indexed
    1..N so the `(template_exercise, set_index)` uniqueness holds.
    """
    template = WorkoutTemplate(
        slug=slug,
        name=_template_name(program, session),
        kind=session.kind,
        focus=session.focus,
        catalog_section=CUSTOM_CATALOG_SECTION,
        display_order=session.position,
    )
    for index, exercise in enumerate(session.exercises, start=1):
        te = TemplateExercise(
            position=index,
            code=f"E{index}",
            name=exercise.exercise_name,
            set_scheme=exercise.set_scheme,
            notes=exercise.notes,
        )
        working = [rt for rt in exercise.rep_targets if not rt.is_warmup]
        for set_index, rep in enumerate(working, start=1):
            te.rep_targets.append(
                RepTarget(
                    set_index=set_index,
                    min_reps=rep.min_reps,
                    max_reps=rep.max_reps,
                    technique=rep.technique,
                )
            )
        template.exercises.append(te)
    return template


def publish_user_program(
    db: Session, user_id: int, program_id: int
) -> PublishResult:
    """Publish a validated custom program into N user-owned templates.

    See the module docstring for the full contract. Never mutates a built-in
    template; never leaves a program half-published (a slug clash rolls back the
    whole materialization and surfaces a soft refusal).
    """
    program = _load_owned(db, user_id, program_id)

    if program.archived_at is not None or program.status == "archived":
        raise PublishRefused(
            "Ce programme est archivé — désarchivez-le avant de le publier."
        )
    if program.status == "draft":
        raise PublishRefused(
            "Validez d'abord ce programme : seul un programme validé peut être publié."
        )
    if program.status == "published":
        # Idempotent — an already-published version never re-materializes
        # (immutability, spec 04 §7). Return its existing templates.
        return PublishResult(
            program=program,
            templates=_existing_templates(db, program),
            created=False,
        )

    # status == "validated": freeze quality FIRST, while still scorable. The
    # writer commits its own transaction and expires the session, so the tree is
    # re-loaded fresh before materialization.
    try:
        compute_and_store_quality_review(db, user_id, program_id)
    except QualityReviewError as exc:
        db.rollback()
        raise PublishRefused(str(exc)) from exc
    program = _load_owned(db, user_id, program_id)

    created: list[WorkoutTemplate] = []
    for session in program.sessions:
        slug = publication_slug(
            user_id, program.slug_base, program.current_version, session.position
        )
        template = _materialize_session(program, session, slug)
        db.add(template)
        db.flush()  # assign template.id before linking it back to the session
        session.published_template_id = template.id
        session.template_slug_snapshot = slug
        created.append(template)

    program.status = "published"
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise PublishRefused(
            "Un identifiant de séance publiée est déjà pris — renommez le "
            "programme avant de le publier."
        ) from exc
    for template in created:
        db.refresh(template)
    return PublishResult(program=program, templates=created, created=True)
