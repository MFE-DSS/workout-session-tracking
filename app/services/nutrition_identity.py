"""Explicit immutable QA identity; never defaults to hostname or general app key."""

import re

from app.config import get_settings
from app.services.nutrition_commands import NutritionError

SCHEMA = "nutrition_manual_01"


def nutrition_identity() -> dict:
    settings = get_settings()
    if (not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{7,127}", settings.nutrition_backend_identity)
            or len(settings.nutrition_signing_key) < 32):
        raise NutritionError("storage_unavailable", 503)
    return {"backend": settings.nutrition_backend_identity, "schema": SCHEMA}


def nutrition_signing_key() -> bytes:
    nutrition_identity()
    return get_settings().nutrition_signing_key.encode("utf-8")
