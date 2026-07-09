"""Formal Exercise → muscle-zone relation — Sb_32.2.

Second relational object of the Sx_32 refactor. Turns the implicit
``classify_exercise(name)`` substring heuristic into an explicit,
DB-backed relation between an exercise and the body zones it works.

Identity note (OQ-32-A) : the current catalog has **no stable per-exercise
code** — ``code`` in ``reference_split.json`` is a training-day slot
(E1…E7), reused across exercises. The only stable per-exercise identity
today is the **name**, which is exactly what ``classify_exercise`` keys on.
So ``exercise_code`` here holds the exercise *name*; DB lookup and the
substring fallback are therefore keyed on the same value, which is what
makes them provably equivalent against the Sb_32.1 baseline.

Sb_32.2 scope : create the table + backfill from the Sb_32.1 baseline +
add an OPTIONAL DB lookup path in ``classify_exercise`` (name-only calls
stay byte-identical). NO consumer is migrated — invariance is contrainte #1.

Convention alignment : int PK + FK ``body_zone_code`` → ``body_zones.code``
+ nullable FK ``muscle_code`` → ``muscles.code`` + ``created_at``
server_default + ``__table_args__`` unique constraint + indexes.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
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


class ExerciseMuscleMapping(Base):
    __tablename__ = "exercise_muscle_mappings"

    __table_args__ = (
        # One row per (exercise, zone, role) — no duplicate mapping.
        UniqueConstraint(
            "exercise_code",
            "body_zone_code",
            "role",
            name="uq_exercise_muscle_mapping",
        ),
        Index("ix_exercise_muscle_mapping_exercise", "exercise_code"),
        Index("ix_exercise_muscle_mapping_zone", "body_zone_code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    # Stable exercise identity = exercise name (see module docstring).
    exercise_code: Mapped[str] = mapped_column(String(length=256), nullable=False)
    # Worked body zone (natural code FK, aligned with BodyZone).
    body_zone_code: Mapped[str] = mapped_column(
        String(length=64),
        ForeignKey("body_zones.code", ondelete="CASCADE"),
        nullable=False,
    )
    # Optional fine-grained muscle (nullable — no anatomy invented in V1).
    muscle_code: Mapped[str | None] = mapped_column(
        String(length=64),
        ForeignKey("muscles.code", ondelete="SET NULL"),
        nullable=True,
    )
    # Role of the zone for this exercise : primary | secondary | stabilizer.
    # V1 backfills primary + secondary only ; stabilizer stays possible but
    # is never invented.
    role: Mapped[str] = mapped_column(String(length=16), nullable=False)
    # Provenance of the row : baseline | manual | atlas | properties.
    # V1 rows are all `baseline` (generated from the Sb_32.1 snapshot).
    source: Mapped[str] = mapped_column(String(length=16), nullable=False)
    # Ordinal within a (exercise, role) group — preserves the historical
    # secondary-zone ordering deterministically. 0 for the primary row.
    position: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="1"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
