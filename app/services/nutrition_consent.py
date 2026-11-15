"""Distinct nutrition purpose, current wording and owner-serialized consent CAS."""

from __future__ import annotations

import hashlib
import hmac
import json
import re
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.body_consent import BodyConsent
from app.services.nutrition_commands import NutritionError
from app.services.plan_v3.transactions import RuntimeFailure, guard_owner

PURPOSE = "nutrition_manual"
WORDING_VERSION = 1


def _utc(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


def _instant(value: datetime | None) -> str | None:
    return None if value is None else _utc(value).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _row(db: Session, owner_id: int) -> BodyConsent | None:
    return db.scalar(select(BodyConsent).where(
        BodyConsent.user_id == owner_id, BodyConsent.consent_type == PURPOSE
    ).execution_options(populate_existing=True))


def read_consent(db: Session, owner_id: int) -> dict:
    row = _row(db, owner_id)
    state = {
        "contract_version": "nutrition-manual/1.0.0", "owner_id": owner_id,
        "purpose": PURPOSE, "state": "PRESENT" if row else "ABSENT",
        "granted": bool(row.granted) if row else False,
        "wording_version": row.consent_version if row else WORDING_VERSION,
        "current_wording_version": WORDING_VERSION,
        "granted_at": _instant(row.granted_at) if row else None,
        "withdrawn_at": _instant(row.withdrawn_at) if row else None,
    }
    from app.services.nutrition_identity import nutrition_identity, nutrition_signing_key

    payload = b"NUT-CONSENT-1\n" + json.dumps({**nutrition_identity(), "state": state}, sort_keys=True, separators=(",", ":")).encode()
    state["consent_token"] = hmac.new(
        nutrition_signing_key(), payload, hashlib.sha256
    ).hexdigest()
    return state


def require_controlled_acquisition() -> None:
    settings = get_settings()
    if settings.app_env != "test" or not settings.nutrition_manual_controlled_test_enabled:
        raise NutritionError("acquisition_unavailable", 403)


def require_consent(db: Session, owner_id: int) -> None:
    row = _row(db, owner_id)
    if row is None or not row.granted or row.consent_version != WORDING_VERSION:
        raise NutritionError("consent_required", 403)


def guard_nutrition_owner(db: Session, owner_id: int, auth_proof: dict) -> None:
    if db.get_bind().dialect.name != "sqlite":
        raise NutritionError("storage_unavailable", 503)
    if (
        type(auth_proof) is not dict
        or set(auth_proof) != {"expected_epoch", "expected_hash", "device_id"}
        or type(auth_proof["expected_epoch"]) is not int
        or not isinstance(auth_proof["expected_hash"], str)
        or not auth_proof["expected_hash"]
        or auth_proof["device_id"] is not None and (
            not isinstance(auth_proof["device_id"], str) or not auth_proof["device_id"]
        )
    ):
        raise NutritionError("authentication_changed", 401)
    try:
        guard_owner(db, owner_id, **auth_proof)
    except RuntimeFailure as exc:
        raise NutritionError(exc.code, exc.status) from exc


def set_consent(
    db: Session, owner_id: int, expected_token: str, granted: bool, wording_version: int,
    *, auth_proof: dict, now: datetime | None = None,
) -> dict:
    if type(granted) is not bool or type(wording_version) is not int or wording_version != WORDING_VERSION:
        raise NutritionError()
    if not isinstance(expected_token, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_token):
        raise NutritionError()
    try:
        guard_nutrition_owner(db, owner_id, auth_proof)
        current = read_consent(db, owner_id)
        if not hmac.compare_digest(expected_token, current["consent_token"]):
            raise NutritionError("stale_consent", 409)
        if granted:
            require_controlled_acquisition()
        row = _row(db, owner_id)
        if row and row.granted == granted and row.consent_version == wording_version:
            raise NutritionError("no_change")
        stamp = _utc(now or datetime.now(UTC))
        previous = [x for x in (row.granted_at, row.withdrawn_at) if x is not None] if row else []
        if previous and stamp <= max(_utc(x) for x in previous):
            stamp = max(_utc(x) for x in previous) + timedelta(microseconds=1)
        if row is None:
            row = BodyConsent(user_id=owner_id, consent_type=PURPOSE)
            db.add(row)
        row.granted, row.consent_version = granted, wording_version
        if granted:
            row.granted_at = stamp
        else:
            row.withdrawn_at = stamp
        db.commit()
        return read_consent(db, owner_id)
    except Exception:
        db.rollback()
        raise
