"""Per-date workout session logs.

Sprint 0 only ships the *table shapes* so migrations are stable from day 1;
the UI for actually creating/editing sessions arrives in Sprint 1. Keeping
the schema present now avoids a destructive migration later and lets tests
cover the relations immediately.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class WorkoutSession(Base):
    """One logged workout on a given calendar date."""

    __tablename__ = "workout_sessions"
    __table_args__ = (
        UniqueConstraint("session_date", name="uq_session_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    session_date: Mapped[date] = mapped_column(Date, nullable=False)
    split_day_id: Mapped[int] = mapped_column(
        ForeignKey("split_days.id", ondelete="RESTRICT"), nullable=False
    )
    bodyweight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    set_logs: Mapped[list["SetLog"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="SetLog.id",
    )


class SetLog(Base):
    """One working set actually performed during a session."""

    __tablename__ = "set_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("workout_sessions.id", ondelete="CASCADE"), nullable=False
    )
    exercise_id: Mapped[int] = mapped_column(
        ForeignKey("exercises.id", ondelete="RESTRICT"), nullable=False
    )
    set_index: Mapped[int] = mapped_column(Integer, nullable=False)
    weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    reps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    technique: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)
    quality: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    session: Mapped[WorkoutSession] = relationship(back_populates="set_logs")
