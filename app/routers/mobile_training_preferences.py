"""MOB-03 adapters of declared preferences; no recommendation logic lives here."""
from __future__ import annotations

from typing import Any

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict

from app.deps import ApiUser, DbSession
from app.services import training_preferences as preferences


class TrainingDeclarationsBody(BaseModel):
    """All three keys required: omission must never erase an existing declaration."""

    model_config = ConfigDict(strict=True, extra="forbid", hide_input_in_errors=True)

    sessions_per_week: int | None
    focus_priorities: list[str] | None
    available_equipment: list[str] | None


def _projection(data: preferences.TrainingPreferencesData) -> dict[str, Any]:
    return {
        "contract_version": preferences.PREFERENCES_CONTRACT_VERSION,
        "declarations": {
            "sessions_per_week": data.sessions_per_week,
            "focus_priorities": data.focus_priorities,
            "available_equipment": data.available_equipment,
        },
        "options": {
            "sessions_per_week": {
                "min": preferences.SESSIONS_PER_WEEK_MIN,
                "max": preferences.SESSIONS_PER_WEEK_MAX,
            },
            "focus_priorities": [
                {"value": key, "label": preferences.focus_priority_label(key)}
                for key in preferences.FOCUS_PRIORITY_VOCAB
            ],
            "available_equipment": [
                {"value": key, "label": preferences.equipment_family_label(key)}
                for key in preferences.EQUIPMENT_FAMILY_VOCAB
            ],
        },
    }


def read_declarations(user: ApiUser, db: DbSession) -> dict[str, Any]:
    return _projection(preferences.get_training_preferences(db, user.id))


def replace_declarations(body: TrainingDeclarationsBody, user: ApiUser, db: DbSession) -> dict[str, Any]:
    try:
        result = preferences.save_training_preferences(db, user.id, **body.model_dump())
    except preferences.PreferenceValidationError:
        # Do not echo submitted declarations in an error or invent a second validator.
        raise HTTPException(400, detail={"error": "invalid_training_preferences"}) from None
    return _projection(result)
