"""Pydantic DTOs mirroring the template catalog."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class RepTargetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    set_index: int
    min_reps: int
    max_reps: int
    technique: Optional[str] = None


class TemplateExerciseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    position: int
    code: str
    name: str
    set_scheme: str
    notes: Optional[str] = None
    rep_targets: list[RepTargetOut] = []


class WorkoutTemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    slug: str
    name: str
    kind: str
    focus: str
    cardio_note: Optional[str] = None
    suggested_label: Optional[str] = None
    exercises: list[TemplateExerciseOut] = []
