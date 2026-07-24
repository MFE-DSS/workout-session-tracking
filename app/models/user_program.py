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
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    event,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Status vocabulary (spec 04 §6). Kept as plain constants — no logic
# branches on anything but "draft" until the wizard/publication builds.
USER_PROGRAM_STATUSES = ("draft", "validated", "published", "archived")

# ORM cascade shared by the whole ownership tree (catalog.py pattern).
_TREE_CASCADE = "all, delete-orphan"


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

    # Child tree (PERSISTENCE_02) — catalog.py pattern: ordered children,
    # ORM-level delete-orphan mirroring the DB-level ON DELETE CASCADE.
    sessions: Mapped[list[UserProgramSession]] = relationship(
        back_populates="program",
        cascade=_TREE_CASCADE,
        order_by="UserProgramSession.position",
    )

    # Frozen scoring traces (PERSISTENCE_03) — one immutable row per
    # published version (spec 03 §9 / spec 04 §7).
    quality_reviews: Mapped[list[UserProgramQualityReview]] = relationship(
        back_populates="program",
        cascade=_TREE_CASCADE,
        order_by="UserProgramQualityReview.version",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<UserProgram id={self.id} user_id={self.user_id} "
            f"slug_base={self.slug_base} status={self.status}>"
        )


class UserProgramSession(Base):
    """One planned session slot inside a user program (e.g. « Push A »).

    Spec 04 §5. Materialization contract (spec 05 §6): ONE UserProgramSession
    becomes ONE custom `WorkoutTemplate` at publication — never here.
    """

    __tablename__ = "user_program_sessions"
    __table_args__ = (
        UniqueConstraint(
            "user_program_id", "position", name="uq_user_program_session_position"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_program_id: Mapped[int] = mapped_column(
        ForeignKey("user_programs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    # strength / cardio — aligned on the catalog vocabulary.
    kind: Mapped[str] = mapped_column(String(16), nullable=False, default="strength")
    focus: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    # Declared time budget — consumed by the future duration_realism subscore.
    duration_target_minutes: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    program: Mapped[UserProgram] = relationship(back_populates="sessions")
    exercises: Mapped[list[UserProgramExercise]] = relationship(
        back_populates="session",
        cascade=_TREE_CASCADE,
        order_by="UserProgramExercise.position",
    )


class UserProgramExercise(Base):
    """One exercise slot inside a user program session.

    `exercise_name` is the canonical EKB name (historical identity —
    NEVER renamed, spec 02 §4); `variant_key`/`variant_group` and the
    denormalized equipment/pattern copies are editing/scoring helpers,
    the EKB stays the reference. ZERO foreign key toward the system
    catalog or the EKB (PERSISTENCE contract).
    """

    __tablename__ = "user_program_exercises"
    __table_args__ = (
        UniqueConstraint(
            "user_program_session_id",
            "position",
            name="uq_user_program_exercise_position",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_program_session_id: Mapped[int] = mapped_column(
        ForeignKey("user_program_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    exercise_name: Mapped[str] = mapped_column(String(255), nullable=False)
    variant_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    variant_group: Mapped[str | None] = mapped_column(String(128), nullable=True)
    # Denormalized EKB copies (filtering/scoring convenience only).
    equipment_family: Mapped[str | None] = mapped_column(String(64), nullable=True)
    movement_pattern: Mapped[str | None] = mapped_column(String(64), nullable=True)
    set_scheme: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Generation explainability (« pattern push requis par le split ») or
    # "manual" when the slot was hand-picked.
    source_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    session: Mapped[UserProgramSession] = relationship(back_populates="exercises")
    rep_targets: Mapped[list[UserProgramRepTarget]] = relationship(
        back_populates="exercise",
        cascade=_TREE_CASCADE,
        order_by="UserProgramRepTarget.set_index",
    )


class UserProgramRepTarget(Base):
    """One prescribed rep range for a working (or warmup) set.

    Mirrors the catalog `RepTarget` shape so materialization (spec 05 §6)
    is a straight copy — the condition for native overload compatibility.
    `is_warmup` is prepared (spec 04 §5) but defaults to false everywhere
    in V1 (warmups stay generated at instantiation, like the catalog).
    """

    __tablename__ = "user_program_rep_targets"
    __table_args__ = (
        UniqueConstraint(
            "user_program_exercise_id",
            "set_index",
            "is_warmup",
            name="uq_user_program_rep_target_set",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_program_exercise_id: Mapped[int] = mapped_column(
        ForeignKey("user_program_exercises.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    set_index: Mapped[int] = mapped_column(Integer, nullable=False)
    min_reps: Mapped[int] = mapped_column(Integer, nullable=False)
    max_reps: Mapped[int] = mapped_column(Integer, nullable=False)
    technique: Mapped[str | None] = mapped_column(String(8), nullable=True)
    is_warmup: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="0"
    )

    exercise: Mapped[UserProgramExercise] = relationship(
        back_populates="rep_targets"
    )


class UserProgramQualityReview(Base):
    """Frozen trace of one quality scoring run (Sx_CUSTOM_PROGRAM_03 §9-C).

    One row per published program version — written at publication time,
    NEVER rewritten (immutability is enforced by the per-version unique
    constraint plus service discipline; the past is never recomputed,
    same doctrine as `scoring_version` on sessions / Sx_30).

    This table is a RECEPTACLE only: no score is computed, interpreted or
    thresholded here — the scoring engine lives in
    `app/services/program_quality_engine.py` (`SCORING_01`) and the writer
    in `app/services/program_quality_reviews.py` (`SCORING_03`). Payload
    columns mirror the `QualityReview` model of spec 03 §4 as opaque
    explicable JSON text.

    `SCORING_03` extends the receptacle with the three RUNTIME fields the
    engine produces beyond spec 03 §4 (`confidence`, `coverage_ratio`,
    `grade_cap_reason`). They exist because the engine only measures 4 of
    the 8 subscores while the EKB stays partially curated: without them a
    stored "B" would read as a fully measured B. They depend on the EKB
    state AT SCORING TIME, so they are not derivable after the fact — a
    faithful frozen trace requires storing them.
    """

    __tablename__ = "user_program_quality_reviews"
    __table_args__ = (
        UniqueConstraint(
            "user_program_id",
            "version",
            name="uq_user_program_quality_review_version",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_program_id: Mapped[int] = mapped_column(
        ForeignKey("user_programs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Program version this trace belongs to (spec 04 §7) — one per version.
    version: Mapped[int] = mapped_column(Integer, nullable=False)

    grade: Mapped[str] = mapped_column(String(1), nullable=False)
    global_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Explicable payloads of the QualityReview (spec 03 §4) — opaque here.
    subscores_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    alerts_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggestions_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    assumptions_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    missing_data_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Engine + knowledge-base versions pinned on every trace.
    scoring_version: Mapped[int] = mapped_column(Integer, nullable=False)
    ekb_version: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # Runtime fields of the engine (SCORING_03) — reliability of the reading
    # and grade-cap explanation. Not derivable after the fact: they depend
    # on the EKB coverage at scoring time.
    confidence: Mapped[str | None] = mapped_column(String(16), nullable=True)
    coverage_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    grade_cap_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Set by the caller (the pure engine has no clock — spec 03 §4);
    # server default keeps the column NOT NULL-safe.
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    program: Mapped[UserProgram] = relationship(back_populates="quality_reviews")


@event.listens_for(UserProgramQualityReview, "before_update")
def _reject_quality_review_update(mapper, connection, target) -> None:
    """Application-level immutability (PERSISTENCE_05, spec 03 §9-C).

    A frozen scoring trace is NEVER rewritten — the past is not
    recomputed (same doctrine as `scoring_version` on sessions). The
    unique (program, version) constraint blocks duplicates; this
    listener blocks in-place mutation, closing the remaining gap
    without any schema change. Deletes stay possible only through the
    owning program's cascade (spec 04 §8 keeps even that soft).
    """
    raise ValueError(
        "UserProgramQualityReview est immuable : une trace de scoring "
        f"gelée ne se modifie pas (review id={target.id}, "
        f"version={target.version})"
    )
