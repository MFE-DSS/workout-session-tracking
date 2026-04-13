"""Readiness CRUD — one entry per user per calendar day.

All subjective fields use a 1-5 scale where 5 is always the best state.
"""
from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.readiness import ReadinessEntry

SCALE_FIELDS = [
    "sleep_quality", "fatigue_level", "soreness_level",
    "stress_level", "motivation_level",
]

READINESS_LABELS: dict[str, dict[int, str]] = {
    "sleep_quality": {1: "Très mauvais", 2: "Mauvais", 3: "Correct", 4: "Bon", 5: "Excellent"},
    "fatigue_level": {1: "Épuisé", 2: "Fatigué", 3: "Normal", 4: "En forme", 5: "Très frais"},
    "soreness_level": {1: "Très douloureux", 2: "Douloureux", 3: "Modéré", 4: "Léger", 5: "Aucune douleur"},
    "stress_level": {1: "Très stressé", 2: "Stressé", 3: "Moyen", 4: "Détendu", 5: "Très détendu"},
    "motivation_level": {1: "Aucune", 2: "Faible", 3: "Normale", 4: "Bonne", 5: "Très motivé"},
}

READINESS_FIELD_LABELS: dict[str, str] = {
    "sleep_quality": "Sommeil", "fatigue_level": "Fatigue",
    "soreness_level": "Courbatures", "stress_level": "Stress",
    "motivation_level": "Motivation",
}


def _validate_scale(data: dict) -> None:
    """Raise ValueError if any scale field is missing or not an int in 1-5."""
    for field in SCALE_FIELDS:
        val = data.get(field)
        if not isinstance(val, int) or val < 1 or val > 5:
            raise ValueError(f"{field} must be an integer between 1 and 5, got {val!r}")


def save_readiness(db: Session, user_id: int, data: dict) -> ReadinessEntry:
    """Upsert a readiness entry for user + today.

    If an entry already exists for (user_id, today), it is updated.
    Otherwise a new row is created.
    """
    _validate_scale(data)
    today = date.today()

    entry = db.execute(
        select(ReadinessEntry).where(
            ReadinessEntry.user_id == user_id,
            ReadinessEntry.recorded_on == today,
        )
    ).scalar_one_or_none()

    if entry is None:
        entry = ReadinessEntry(user_id=user_id, recorded_on=today)
        db.add(entry)

    for field in SCALE_FIELDS:
        setattr(entry, field, data[field])

    entry.resting_hr = data.get("resting_hr")
    entry.note = data.get("note")

    db.commit()
    db.refresh(entry)
    return entry


def get_today_readiness(db: Session, user_id: int) -> ReadinessEntry | None:
    """Return today's readiness entry for the user, or None."""
    return db.execute(
        select(ReadinessEntry).where(
            ReadinessEntry.user_id == user_id,
            ReadinessEntry.recorded_on == date.today(),
        )
    ).scalar_one_or_none()


def get_readiness_history(
    db: Session, user_id: int, days: int = 30,
) -> list[ReadinessEntry]:
    """Return readiness entries for the last *days* days, most recent first."""
    cutoff = date.today() - timedelta(days=days)
    return list(
        db.execute(
            select(ReadinessEntry)
            .where(
                ReadinessEntry.user_id == user_id,
                ReadinessEntry.recorded_on >= cutoff,
            )
            .order_by(ReadinessEntry.recorded_on.desc())
        ).scalars().all()
    )
