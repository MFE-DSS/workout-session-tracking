"""Resolve and guard owner access to published custom session templates.

Sb_CUSTOM_PROGRAM_PUBLICATION_03 — after PUBLICATION_01 materializes a validated
`UserProgram` into N custom `WorkoutTemplate`s (`catalog_section="user"`), the owner
launches those sessions **through the owned program context**, never through the shared
catalogue (the global `/library` keeps excluding `catalog_section="user"`).

Access model (spec 05 §14):
  - A user may launch **only their own** custom templates — ownership is resolved through
    `UserProgram (owner) → UserProgramSession → published_template_id`. There is NO
    `WorkoutTemplate.user_id`; ownership lives on the program side.
  - System templates stay launchable by everyone (unchanged behaviour).
  - A non-published program is not launchable: a new edit cycle (PUBLICATION_02) clears the
    session links, so `published_template_id IS NULL` ⇒ not launchable.
  - An **archived** program is soft-deleted (spec 04 §8): it leaves the library and is not
    launchable. Archiving only sets `archived_at` (status stays `published`), so every access
    path here also requires `archived_at IS NULL`.

This module only READS: it never mutates a `WorkoutTemplate` nor the `UserProgram`. The actual
instantiation reuses the existing `session_builder.instantiate_session` at the call site.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.catalog import TemplateExercise, WorkoutTemplate
from app.models.user_program import UserProgram, UserProgramSession


class LaunchNotFound(Exception):
    """Owned published session/template not resolvable — missing OR foreign OR not
    published (indistinct, no existence leak → 404)."""


def resolve_owned_published_template(
    db: Session, user_id: int, program_id: int, session_id: int
) -> WorkoutTemplate:
    """The `WorkoutTemplate` linked to an OWNED, PUBLISHED session, eager-loaded for
    instantiation. Raises `LaunchNotFound` if the program/session is missing, owned by
    someone else, or not published (`published_template_id IS NULL`)."""
    link = db.execute(
        select(UserProgramSession.published_template_id)
        .join(UserProgram, UserProgram.id == UserProgramSession.user_program_id)
        .where(
            UserProgram.user_id == user_id,
            UserProgram.archived_at.is_(None),
            UserProgram.id == program_id,
            UserProgramSession.id == session_id,
        )
    ).scalar_one_or_none()
    if link is None:
        # session missing / foreign program / archived / not linked (not published)
        raise LaunchNotFound("Séance introuvable")
    template = db.execute(
        select(WorkoutTemplate)
        .where(WorkoutTemplate.id == link)
        .options(
            selectinload(WorkoutTemplate.exercises).selectinload(
                TemplateExercise.rep_targets
            )
        )
    ).scalar_one_or_none()
    if template is None:
        raise LaunchNotFound("Modèle introuvable")
    return template


def is_owned_published_template(db: Session, user_id: int, template_id: int) -> bool:
    """True iff the user owns a published `UserProgramSession` linking to this template.

    Reverse lookup used to guard the slug-based `create_session` against launching another
    user's custom template (spec 05 §14) — there is no `WorkoutTemplate.user_id` to check."""
    hit = db.execute(
        select(UserProgramSession.id)
        .join(UserProgram, UserProgram.id == UserProgramSession.user_program_id)
        .where(
            UserProgram.user_id == user_id,
            UserProgram.archived_at.is_(None),
            UserProgramSession.published_template_id == template_id,
        )
        .limit(1)
    ).scalar_one_or_none()
    return hit is not None
