"""Pydantic schemas mirroring the reference catalog for the /api layer."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class RepRangeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    set_index: int
    min_reps: int
    max_reps: int
    technique: Optional[str] = None


class ExerciseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    position: int
    code: str
    name: str
    set_scheme: str
    notes: Optional[str] = None
    rep_ranges: list[RepRangeOut] = []


class SplitDayOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    weekday: int
    name: str
    kind: str
    focus: str
    cardio_note: Optional[str] = None
    exercises: list[ExerciseOut] = []
