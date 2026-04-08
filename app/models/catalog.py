"""Reference catalog models.

These tables describe the *prescribed* training split (what the coach wrote
in the reference document). They are seeded once and are read-only from the
user's point of view. The actual per-date session logs live in
`app/models/session.py`.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SplitDay(Base):
    """A day of the weekly split (Lundi, Mardi, ...).

    `kind` is one of:
      - "training"  -> a muscle-group training day with exercises
      - "rest_abs"  -> rest day with abs + LISS cardio

    `weekday` is ISO weekday 1..7 (Lundi=1, Dimanche=7).
    """

    __tablename__ = "split_days"

    id: Mapped[int] = mapped_column(primary_key=True)
    weekday: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    kind: Mapped[str] = mapped_column(String(16), nullable=False, default="training")
    focus: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    cardio_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    exercises: Mapped[list["Exercise"]] = relationship(
        back_populates="split_day",
        cascade="all, delete-orphan",
        order_by="Exercise.position",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<SplitDay {self.weekday} {self.name} ({self.kind})>"


class Exercise(Base):
    """A prescribed exercise slot inside a training day.

    `code` mirrors the source document (E1, E2, ...). The source sometimes
    reuses E6 or skips E5; we preserve the code as a label but use `position`
    as the stable ordering.

    `set_scheme` is a text representation of the rep ranges exactly as the
    coach wrote them ("6-10, 6-10, 10-15", "2x 12-15", ...). This is the
    human-facing reference. Machine-readable ranges live in `rep_ranges`.
    """

    __tablename__ = "exercises"
    __table_args__ = (
        UniqueConstraint("split_day_id", "position", name="uq_exercise_day_position"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    split_day_id: Mapped[int] = mapped_column(
        ForeignKey("split_days.id", ondelete="CASCADE"), nullable=False
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    code: Mapped[str] = mapped_column(String(8), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    set_scheme: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    split_day: Mapped[SplitDay] = relationship(back_populates="exercises")
    rep_ranges: Mapped[list["RepRange"]] = relationship(
        back_populates="exercise",
        cascade="all, delete-orphan",
        order_by="RepRange.set_index",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Exercise {self.code} {self.name!r}>"


class RepRange(Base):
    """A single working set's prescribed rep range.

    A 3-set exercise with scheme "6-10, 6-10, 10-15" produces 3 RepRange rows
    (set_index 1..3). A "2x 12-15" exercise produces 2 rows with identical
    min/max. This representation is what Sprint 1+ uses for progression and
    surcharge-progressive checks.
    """

    __tablename__ = "rep_ranges"
    __table_args__ = (
        UniqueConstraint("exercise_id", "set_index", name="uq_reprange_exercise_set"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    exercise_id: Mapped[int] = mapped_column(
        ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False
    )
    set_index: Mapped[int] = mapped_column(Integer, nullable=False)
    min_reps: Mapped[int] = mapped_column(Integer, nullable=False)
    max_reps: Mapped[int] = mapped_column(Integer, nullable=False)
    technique: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)

    exercise: Mapped[Exercise] = relationship(back_populates="rep_ranges")


class ReferenceDoc(Base):
    """Stores the version of the seeded reference document.

    Lets us detect when the source spec changes and trigger a re-seed. The
    hash/version comes from `data/reference_split.json`.
    """

    __tablename__ = "reference_docs"

    id: Mapped[int] = mapped_column(primary_key=True)
    version: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    seeded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
