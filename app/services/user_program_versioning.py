"""Start a new edit cycle on a published custom program (mono-row versioning).

Sb_CUSTOM_PROGRAM_PUBLICATION_02 — the lifecycle step after PUBLICATION_01. Once a
program is published, its tree is frozen behind an immutable published artifact. To
keep iterating, the user starts a **new edit cycle**: the SAME `UserProgram` row
returns to `draft` at `current_version + 1` (spec 04 §6-7 / spec 05 §6-7 — mono-row
versioning, `current_version` on the row, NO copy row, NO versions table).

Contract (spec 04 §6, transitions):
  - Only a `published` program starts a new cycle.
  - The **same row** is updated: `id` unchanged · `status` → `draft` ·
    `current_version += 1` (exactly once).
  - The editable tree (sessions/exercises/rep_targets) is **kept as-is** — it becomes
    the draft the user edits through the existing WIZARD/editor flows.
  - Each session's `published_template_id` + `template_slug_snapshot` are **cleared**
    (they were the v{n} links; the fresh draft is not published).
  - The already-materialized `WorkoutTemplate` artifacts v{n} are **never mutated nor
    deleted** here — they stay as immutable catalog artifacts. (Archiving old catalog
    artifacts happens later, at the v{n+1} publication — out of scope of this sprint.)
  - **No quality review is written** — quality is frozen at publication only.

Idempotence / double-submit:
  - A `draft` or `validated` program is **already editable** → no change, no increment
    (`incremented=False`). This also guards a double-submit: after the first call the
    status is `draft`, so a repeat POST never increments a second time.
  - An `archived` program is softly refused (unarchive first) — no increment.

Owner-scope: a missing OR foreign program raises the SAME `VersioningNotFound`
(no existence leak), mirroring the other custom-program services.
"""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.user_program import UserProgram


class VersioningError(Exception):
    """Base error for the new-edit-cycle flow."""


class VersioningNotFound(VersioningError):
    """Program missing OR owned by someone else — indistinct, no leak (→ 404)."""


class VersioningRefused(VersioningError):
    """Refused for a lifecycle reason (archived). Soft, actionable message (→ 200)."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


@dataclass
class NewCycleResult:
    """Outcome of a start-new-edit-cycle attempt.

    `incremented` is True only when a `published` program actually started a new
    cycle (status→draft, current_version+1). A program that was already editable
    (`draft`/`validated`) returns `incremented=False` and is left untouched.
    """

    program: UserProgram
    incremented: bool


def _load_owned(db: Session, user_id: int, program_id: int) -> UserProgram:
    """Owner-scoped program with its sessions. Missing/foreign → VersioningNotFound."""
    program = db.execute(
        select(UserProgram)
        .where(UserProgram.user_id == user_id, UserProgram.id == program_id)
        .options(selectinload(UserProgram.sessions))
    ).scalar_one_or_none()
    if program is None:
        raise VersioningNotFound("Programme introuvable")
    return program


def start_new_edit_cycle(
    db: Session, user_id: int, program_id: int
) -> NewCycleResult:
    """Return a published program to `draft` at `current_version + 1` (same row).

    See the module docstring for the full contract. Never mutates/deletes a
    `WorkoutTemplate`, never writes a quality review, never creates a second row.
    """
    program = _load_owned(db, user_id, program_id)

    if program.archived_at is not None or program.status == "archived":
        raise VersioningRefused(
            "Ce programme est archivé — désarchivez-le d'abord pour l'éditer."
        )
    if program.status in ("draft", "validated"):
        # Already editable — no new cycle, no increment (also guards double-submit:
        # after the first published→draft transition the status is no longer
        # "published", so a repeated call can never increment twice).
        return NewCycleResult(program=program, incremented=False)

    # status == "published": start a NEW edit cycle on the SAME row (spec 04 §6-7).
    program.status = "draft"
    program.current_version = program.current_version + 1
    for session in program.sessions:
        session.published_template_id = None
        session.template_slug_snapshot = None
    db.commit()
    db.refresh(program)
    return NewCycleResult(program=program, incremented=True)
