"""User-created program root (Sb_CUSTOM_PROGRAM_PERSISTENCE_01).

`UserProgram` is the ROOT of the Custom Program editing model
(Sx_CUSTOM_PROGRAM_04): the source of truth of the future wizard /
card-editing flow, strictly separate from the system catalog
(`WorkoutTemplate`) — Option C of Sx_CUSTOM_PROGRAM_01 §9.

V1 scope of this table (PERSISTENCE_01): ownership, minimal identity,
minimal draft status, versioning counter, timestamps + soft delete.
Child structure (sessions / exercises / rep targets / quality reviews),
wizard payloads, score caches and the publication pointer
(`published_template_id`) arrive in later, separately gated builds.

Design rules:

1. `user_id` is NOT NULL — every program has an owner, no shared or
   global user-created program in V1 (spec 04 §8). Reads must always
   filter by owner.
2. `slug_base` is fixed at creation and unique PER USER: it is the base
   of the future published slug `up{user_id}-{slug_base}-v{n}`
   (spec 05 §5) — the per-user uniqueness prevents publication slug
   collisions at the root.
3. `status` vocabulary: draft / validated / published / archived
   (spec 04 §6). Only `draft` is actively used until the wizard and
   publication builds land; editing a published program starts a NEW
   cycle (`current_version + 1`) — a published artifact is never
   mutated in place.
4. Soft delete via `archived_at` — never destructive (spec 04 §8).
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

# Status vocabulary (spec 04 §6). Kept as plain constants — no logic
# branches on anything but "draft" until the wizard/publication builds.
USER_PROGRAM_STATUSES = ("draft", "validated", "published", "archived")


class UserProgram(Base):
    """Root row of a user-created program (editing source of truth)."""

    __tablename__ = "user_programs"
    __table_args__ = (
        UniqueConstraint("user_id", "slug_base", name="uq_user_program_slug_base"),
        # Covers the future library listing ("my active programs") and
        # any status-scoped read.
        Index("ix_user_programs_user_status", "user_id", "status"),
        # Covers "most recently edited first" listings.
        Index("ix_user_programs_user_updated", "user_id", "updated_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # Owner — hard ownership, no NULL, no sharing in V1.
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    title: Mapped[str] = mapped_column(String(128), nullable=False)

    # Base of the future published slug `up{user_id}-{slug_base}-v{n}`.
    # Fixed at creation, never rewritten.
    slug_base: Mapped[str] = mapped_column(String(64), nullable=False)

    # draft / validated / published / archived — see USER_PROGRAM_STATUSES.
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="draft")

    # Bumped when an edition of a published program starts a new cycle
    # (spec 04 §7). Published versions themselves are immutable.
    current_version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default="1"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Soft delete — archived programs disappear from the library but the
    # data (and any logged history) is preserved.
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<UserProgram id={self.id} user_id={self.user_id} "
            f"slug_base={self.slug_base} status={self.status}>"
        )
