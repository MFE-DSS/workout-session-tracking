"""Body measurement CRUD and muscle-template mapping.

Provides time-series storage for body measurements and a static
mapping from measurement fields to muscle groups, used to display
related workout templates alongside evolution graphs.
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
    "arm_cm": ["biceps", "triceps", "bras"],
    "waist_cm": ["abdos", "abs", "cardio"],
    "thigh_cm": ["jambes", "quadriceps", "cuisses"],
}

MEASUREMENT_LABELS: dict[str, str] = {
    "weight_kg": "Poids (kg)",
    "chest_cm": "Tour de poitrine (cm)",
    "arm_cm": "Tour de bras (cm)",
    "waist_cm": "Tour de taille (cm)",
    "thigh_cm": "Tour de cuisses (cm)",
}

MEASUREMENT_UNITS: dict[str, str] = {
    "weight_kg": " kg",
    "chest_cm": " cm",
    "arm_cm": " cm",
    "waist_cm": " cm",
    "thigh_cm": " cm",
}

MEASUREMENT_FIELDS = list(MEASUREMENT_LABELS.keys())


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
    """Return (measured_at, value) pairs for one field, non-null only, ASC."""
    col = getattr(BodyMeasurement, field)
    rows = db.execute(
        select(BodyMeasurement.measured_at, col)
        .where(BodyMeasurement.user_id == user_id)
        .where(col.is_not(None))
        .order_by(BodyMeasurement.measured_at.asc())
        .limit(limit)
    ).all()
    return [(r[0], r[1]) for r in rows]
