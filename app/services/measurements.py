"""Body measurement CRUD and muscle-template mapping.

Provides time-series storage for body measurements and a static
mapping from measurement fields to muscle groups, used to display
related workout templates alongside evolution graphs.

Lateralized fields (arm, thigh) are stored as left/right pairs.
Helper functions compute averages for the physique dashboard.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.measurement import BodyMeasurement


MEASUREMENT_MUSCLE_MAP: dict[str, list[str]] = {
    "weight_kg": [],
    "chest_cm": ["pectoral", "pectoraux", "pecs"],
    "arm_cm_left": ["biceps", "triceps", "bras"],
    "arm_cm_right": ["biceps", "triceps", "bras"],
    "waist_cm": ["abdos", "abs", "cardio"],
    "thigh_cm_left": ["jambes", "quadriceps", "cuisses"],
    "thigh_cm_right": ["jambes", "quadriceps", "cuisses"],
    "hip_cm": [],
    "neck_cm": [],
    "calf_cm": ["mollets"],
}

MEASUREMENT_LABELS: dict[str, str] = {
    "weight_kg": "Poids (kg)",
    "chest_cm": "Tour de poitrine (cm)",
    "arm_cm_left": "Bras gauche (cm)",
    "arm_cm_right": "Bras droit (cm)",
    "waist_cm": "Tour de taille (cm)",
    "thigh_cm_left": "Cuisse gauche (cm)",
    "thigh_cm_right": "Cuisse droite (cm)",
    "hip_cm": "Tour de hanches (cm)",
    "neck_cm": "Tour de cou (cm)",
    "calf_cm": "Tour de mollet (cm)",
}

MEASUREMENT_UNITS: dict[str, str] = {
    "weight_kg": " kg",
    "chest_cm": " cm",
    "arm_cm_left": " cm",
    "arm_cm_right": " cm",
    "waist_cm": " cm",
    "thigh_cm_left": " cm",
    "thigh_cm_right": " cm",
    "hip_cm": " cm",
    "neck_cm": " cm",
    "calf_cm": " cm",
}

MEASUREMENT_FIELDS = list(MEASUREMENT_LABELS.keys())


# ---------------------------------------------------------------------------
# Lateralized average helpers
# ---------------------------------------------------------------------------

def compute_arm_avg(m) -> float | None:
    """Average of left/right arm. Single side if only one. None if neither."""
    left = getattr(m, "arm_cm_left", None)
    right = getattr(m, "arm_cm_right", None)
    if left is not None and right is not None:
        return (left + right) / 2
    return left or right


def compute_thigh_avg(m) -> float | None:
    """Average of left/right thigh. Single side if only one. None if neither."""
    left = getattr(m, "thigh_cm_left", None)
    right = getattr(m, "thigh_cm_right", None)
    if left is not None and right is not None:
        return (left + right) / 2
    return left or right


# ---------------------------------------------------------------------------
# Zone measurement resolver
# ---------------------------------------------------------------------------

_ZONE_DIRECT = {"pecs": "chest_cm", "core": "waist_cm"}
_ZONE_LATERALIZED = {
    "biceps": "arm",
    "triceps": "arm",
    "quads": "thigh",
    "posterior": "thigh",
}


def compute_zone_measurement(m, zone: str) -> float | None:
    """Resolve a zone to the relevant measurement value on a BodyMeasurement row."""
    if zone in _ZONE_DIRECT:
        return getattr(m, _ZONE_DIRECT[zone], None)
    if zone in _ZONE_LATERALIZED:
        limb = _ZONE_LATERALIZED[zone]
        return compute_arm_avg(m) if limb == "arm" else compute_thigh_avg(m)
    return None


# ---------------------------------------------------------------------------
# CRUD helpers
# ---------------------------------------------------------------------------

def find_related_templates(field_name: str, templates: list) -> list[str]:
    """Find catalog templates whose focus matches a measurement's muscle group."""
    keywords = MEASUREMENT_MUSCLE_MAP.get(field_name, [])
    if not keywords:
        return []
    result = []
    for t in templates:
        focus_lower = (t.focus or "").lower()
        if any(kw in focus_lower for kw in keywords):
            result.append(t.name)
    return result


def get_latest_measurement(
    db: Session, user_id: int
) -> Optional[BodyMeasurement]:
    """Return the most recent measurement for a user."""
    return db.execute(
        select(BodyMeasurement)
        .where(BodyMeasurement.user_id == user_id)
        .order_by(BodyMeasurement.measured_at.desc())
        .limit(1)
    ).scalar_one_or_none()


def get_measurement_series(
    db: Session, user_id: int, field: str, limit: int = 20
) -> list[tuple[datetime, float]]:
    """Return (measured_at, value) pairs for one field, non-null only, ASC.

    Sb_17 — for ``field == "weight_kg"`` only, also pull the
    ``WorkoutSession.bodyweight_kg`` saisie sur le feedback de chaque
    séance terminée. In real usage, pre-session weighings are far more
    frequent than the formal profile measurement form, so merging the
    two sources gives a useful continuous timeline without forcing the
    user to duplicate the data entry. Other measurement fields stay on
    BodyMeasurement only.
    """
    col = getattr(BodyMeasurement, field, None)
    if col is None:
        return []

    rows: list[tuple[datetime, float]] = []

    measurement_rows = db.execute(
        select(BodyMeasurement.measured_at, col)
        .where(BodyMeasurement.user_id == user_id)
        .where(col.is_not(None))
    ).all()
    rows.extend((r[0], float(r[1])) for r in measurement_rows)

    if field == "weight_kg":
        # Local import to avoid a circular dependency at module load
        # time (measurements is imported by routers, session models
        # already pull in measurements transitively in some paths).
        from app.models.session import WorkoutSession

        session_rows = db.execute(
            select(WorkoutSession.started_at, WorkoutSession.bodyweight_kg)
            .where(WorkoutSession.user_id == user_id)
            .where(WorkoutSession.bodyweight_kg.is_not(None))
            .where(WorkoutSession.status == "completed")
            .where(WorkoutSession.excluded_from_stats.is_(False))
        ).all()
        rows.extend((r[0], float(r[1])) for r in session_rows)

    rows.sort(key=lambda r: r[0])
    if len(rows) > limit:
        rows = rows[-limit:]
    return rows
