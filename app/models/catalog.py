"""Workout template library.

A `WorkoutTemplate` is a *type of workout* the user can pick
(push A, pull B, legs, LISS cardio, ...). It has no structural
coupling to any day of the week. The weekday of a real session
is derived from `WorkoutSession.started_at`, never from the
catalog.

A template can carry a `suggested_label` (e.g. "usually day 1"),
but this is a non-structural memory aid only — never branch
application logic on it.
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


class WorkoutTemplate(Base):
    """A pickable workout template (strength or cardio)."""

    __tablename__ = "workout_templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    kind: Mapped[str] = mapped_column(String(16), nullable=False, default="strength")
    focus: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    cardio_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Non-structural hint only. NEVER branch logic on this field.
    suggested_label: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    # Catalog hierarchy: controls grouping and ordering in /library.
    # Values: "core", "utility", "specialization", "archived"
    catalog_section: Mapped[str] = mapped_column(
        String(32), nullable=False, default="core"
    )
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    exercises: Mapped[list["TemplateExercise"]] = relationship(
        back_populates="template",
        cascade="all, delete-orphan",
        order_by="TemplateExercise.position",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<WorkoutTemplate slug={self.slug} kind={self.kind}>"


class TemplateExercise(Base):
    """A prescribed exercise slot inside a template."""

    __tablename__ = "template_exercises"
    __table_args__ = (
        UniqueConstraint("template_id", "position", name="uq_template_exercise_position"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    template_id: Mapped[int] = mapped_column(
        ForeignKey("workout_templates.id", ondelete="CASCADE"), nullable=False
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    code: Mapped[str] = mapped_column(String(8), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    set_scheme: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    substitutes_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    template: Mapped[WorkoutTemplate] = relationship(back_populates="exercises")
    rep_targets: Mapped[list["RepTarget"]] = relationship(
        back_populates="exercise",
        cascade="all, delete-orphan",
        order_by="RepTarget.set_index",
    )


class RepTarget(Base):
    """A prescribed rep range for one working set of a template exercise."""

    __tablename__ = "rep_targets"
    __table_args__ = (
        UniqueConstraint("template_exercise_id", "set_index", name="uq_rep_target_set"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    template_exercise_id: Mapped[int] = mapped_column(
        ForeignKey("template_exercises.id", ondelete="CASCADE"), nullable=False
    )
    set_index: Mapped[int] = mapped_column(Integer, nullable=False)
    min_reps: Mapped[int] = mapped_column(Integer, nullable=False)
    max_reps: Mapped[int] = mapped_column(Integer, nullable=False)
    technique: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)

    exercise: Mapped[TemplateExercise] = relationship(back_populates="rep_targets")


class ReferenceDoc(Base):
    """Tracks which version of the catalog JSON is currently seeded."""

    __tablename__ = "reference_docs"

    id: Mapped[int] = mapped_column(primary_key=True)
    version: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    seeded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class MethodRule(Base):
    """Static method reminder cards shown on /rules and inline in the
    session detail page (method reminder area).

    Seeded from `data/method_rules.json`. Not versioned independently —
    any change reseeds the table in place.
    """

    __tablename__ = "method_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
