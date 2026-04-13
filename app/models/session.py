"""Real logged sessions + normalized feedback.

Design rules enforced at the schema level:

1. A `WorkoutSession` is anchored to an absolute timestamp
   (`started_at`). The weekday is DERIVED from that timestamp,
   never stored structurally.

2. Every session snapshots enough of the catalog state
   (`template_slug_snapshot`, `exercise_code_snapshot`,
   `exercise_name_snapshot`) so that historical logs survive a
   template library rewrite. The FKs to the catalog are nullable
   with `ON DELETE SET NULL`: the catalog is free to evolve, the
   history stays intact.

3. Feedback is normalized via string / int enums defined in
   `app.enums`. Free-text notes exist but are optional and short
   (they do not feed analytics).
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Ensure catalog models are loaded so that string-based relationship
# references (e.g. "TemplateExercise") resolve correctly even when
# this module is imported in isolation after an app module purge.
import app.models.catalog  # noqa: F401


class WorkoutSession(Base):
    """One real workout, identified by its start timestamp."""

    __tablename__ = "workout_sessions"
    __table_args__ = (
        Index("ix_workout_sessions_started_at", "started_at"),
        # Covers: KPIs, leaderboard, behavioral engine, timeline,
        # progress — every query that filters eligible sessions for
        # a user and orders by date.
        Index(
            "ix_ws_user_status_excl_started",
            "user_id", "status", "excluded_from_stats", "started_at",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # Owner. Nullable for backward compat with V1 single-user sessions.
    # V2 routes enforce that every new session has a user_id.
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )

    # FK to the catalog. Nullable + SET NULL so the catalog can be
    # rewritten without orphaning history.
    template_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("workout_templates.id", ondelete="SET NULL"), nullable=True
    )
    # Denormalized snapshots captured at session creation time.
    template_slug_snapshot: Mapped[str] = mapped_column(String(64), nullable=False)
    template_name_snapshot: Mapped[str] = mapped_column(String(128), nullable=False)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="in_progress"
    )

    # Sprint 8: soft-exclude from KPI aggregation and timelines.
    # Lets the user hide test / empty / junk sessions from the
    # quality score, the timeline graphs, and the /progress page,
    # without deleting the raw data.
    excluded_from_stats: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    # Normalized session-level feedback (see app.enums)
    concentration: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    global_state: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)

    bodyweight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    free_note: Mapped[Optional[str]] = mapped_column(String(280), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    session_exercises: Mapped[list["SessionExercise"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="SessionExercise.position",
    )

    @property
    def weekday_iso(self) -> int:
        """ISO weekday (1=Mon..7=Sun) derived from `started_at`."""
        return self.started_at.isoweekday()


class SessionExercise(Base):
    """One exercise as it was actually performed inside a session."""

    __tablename__ = "session_exercises"
    __table_args__ = (
        UniqueConstraint("session_id", "position", name="uq_session_exercise_position"),
        # Covers join from WorkoutSession → SessionExercise in KPI
        # and quality score queries. The unique constraint already
        # indexes (session_id, position), but a bare session_id index
        # is more efficient for the join pattern.
        Index("ix_session_exercises_session_id", "session_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("workout_sessions.id", ondelete="CASCADE"), nullable=False
    )
    template_exercise_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("template_exercises.id", ondelete="SET NULL"), nullable=True
    )
    # Denormalized snapshots so analytics keep working after a reseed.
    exercise_code_snapshot: Mapped[str] = mapped_column(String(16), nullable=False)
    exercise_name_snapshot: Mapped[str] = mapped_column(String(255), nullable=False)

    position: Mapped[int] = mapped_column(Integer, nullable=False)

    # Normalized per-exercise feedback
    success_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 100|80|50
    muscle_sensation: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    free_note: Mapped[Optional[str]] = mapped_column(String(140), nullable=True)

    session: Mapped[WorkoutSession] = relationship(back_populates="session_exercises")

    # Optional link back to the catalog. Nullable because a reseed may have
    # detached it (ON DELETE SET NULL). The session page uses this, when
    # present, to render the prescribed set scheme. Never relied on for
    # identity — snapshots above are the source of truth.
    template_exercise = relationship(
        "TemplateExercise",
        lazy="select",
    )

    set_logs: Mapped[list["SetLog"]] = relationship(
        back_populates="session_exercise",
        cascade="all, delete-orphan",
        order_by="SetLog.set_index",
    )


class SetLog(Base):
    """One logged set, warmup or work, actually attempted.

    V1 design choice: warmup and work sets live in the same table
    and are distinguished only by `kind`. Set indexes are scoped per
    (session_exercise, kind), so warmups number 1..N independently
    of work sets, matching how a coach writes a notebook.
    """

    __tablename__ = "set_logs"
    __table_args__ = (
        UniqueConstraint(
            "session_exercise_id", "kind", "set_index", name="uq_set_log_kind_index"
        ),
        # Covers: work set completion counts in KPIs and quality score.
        # Filters on (kind='work', completed=True) are the hottest
        # SetLog access pattern.
        Index(
            "ix_set_logs_exercise_kind_completed",
            "session_exercise_id", "kind", "completed",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    session_exercise_id: Mapped[int] = mapped_column(
        ForeignKey("session_exercises.id", ondelete="CASCADE"), nullable=False
    )
    kind: Mapped[str] = mapped_column(String(8), nullable=False, default="work")
    set_index: Mapped[int] = mapped_column(Integer, nullable=False)

    weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    reps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    technique: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)

    # Normalized per-set feedback
    execution_quality: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    reps_target: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)

    # Explicit "done" flag: distinguishes "not yet attempted" (the row
    # was pre-rendered by the session builder but the user didn't touch
    # it) from "performed" (the user ticked it off, even if weight/reps
    # were not entered).
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    session_exercise: Mapped[SessionExercise] = relationship(back_populates="set_logs")
