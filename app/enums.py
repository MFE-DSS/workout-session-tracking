"""Normalized vocabularies for feedback and classification.

Every feedback the user gives in the UI must map to one of these
enum values. Free text exists but is optional and secondary — only
these codified values feed analytics and progression KPIs.

Stored as plain string / small int in the DB (portable across
SQLite and PostgreSQL). Adding a new value is additive; never
rename or delete a value without a data migration.
"""
from __future__ import annotations

from enum import IntEnum, StrEnum


class TemplateKind(StrEnum):
    STRENGTH = "strength"
    CARDIO = "cardio"


class Technique(StrEnum):
    """Intensity technique applied on a working set."""

    RP = "RP"  # Rest-pause
    DS = "DS"  # Drop set


# ---------------------------------------------------------------------------
# Session-level feedback
# ---------------------------------------------------------------------------


class SessionConcentration(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SessionGlobalState(StrEnum):
    GOOD = "good"
    FLAT = "flat"
    FATIGUED = "fatigued"


# ---------------------------------------------------------------------------
# Per-exercise feedback
# ---------------------------------------------------------------------------


class ExerciseSuccessScore(IntEnum):
    """How the whole exercise went. Int so analytics can average it."""

    S100 = 100
    S80 = 80
    S50 = 50


class MuscleSensation(StrEnum):
    STRONG = "strong"
    PARTIAL = "partial"
    WEAK = "weak"


# ---------------------------------------------------------------------------
# Per-set feedback
# ---------------------------------------------------------------------------


class SetExecutionQuality(StrEnum):
    CLEAN = "clean"
    ACCEPTABLE = "acceptable"
    DEGRADED = "degraded"


class SetRepsTarget(StrEnum):
    TARGET_HIT = "target_hit"
    TARGET_NEAR = "target_near"
    TARGET_MISSED = "target_missed"
