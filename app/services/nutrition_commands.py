"""Manual nutrition command boundary. No inferred numbers or scientific targets."""

from __future__ import annotations

import copy
import hashlib
import hmac
import json
import re
from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

CONTRACT = "nutrition-command/1.0.0"
FIELDS = ("kcal_milli", "protein_milli", "carbohydrate_milli", "fat_milli")
VARIANTS = ("STANDARD", "TRAINING", "REST")
MAX_MILLI = 999999999
MAX_ID = 9007199254740991


class NutritionError(ValueError):
    def __init__(self, code: str = "invalid_command", status: int = 422):
        self.code, self.status = code, status
        super().__init__(code)


def _require(condition: bool) -> None:
    if not condition:
        raise NutritionError()


def _day(value: object) -> bool:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def _zone(value: object) -> bool:
    if not isinstance(value, str) or not value.isascii() or not 1 <= len(value) <= 128:
        return False
    try:
        ZoneInfo(value)
        return True
    except (ValueError, ZoneInfoNotFoundError):
        return False


def _values(value: object) -> bool:
    return (
        type(value) is dict
        and not set(value) - set(FIELDS)
        and all(v is None or type(v) is int and 0 <= v <= MAX_MILLI for v in value.values())
    )


def validate_command(namespace: str, key: object, body: object) -> dict:
    """Strict transport/intent validation; transactional acquisition rules follow later."""
    _require(type(body) is dict)
    common = {"contract_version", "request_id", "expected_head_token", "operation", "values"}
    extra = (
        {"timezone", "target_ref", "confirm_complete"}
        if namespace == "DAY" else {"variant", "effective_from"}
    )
    _require(namespace in ("DAY", "TARGET") and set(body) == common | extra)
    _require(body["contract_version"] == CONTRACT)
    _require(isinstance(body["request_id"], str) and bool(re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}", body["request_id"]
    )))
    _require(isinstance(body["expected_head_token"], str) and bool(re.fullmatch(
        r"[0-9a-f]{64}", body["expected_head_token"]
    )))
    _require(_values(body["values"]))
    op = body["operation"]
    if namespace == "TARGET":
        _require(body["variant"] in VARIANTS and _day(body["effective_from"]))
        _require(key == (body["variant"], body["effective_from"]))
        _require(op in ("SET_FIELDS", "DISABLE"))
        _require(bool(body["values"]) if op == "SET_FIELDS" else body["values"] == {})
    else:
        _require(_day(key))
        _require(op in ("SET_FIELDS", "SET_TARGET_REF", "COMPLETE", "WITHDRAW"))
        target = body["target_ref"]
        _require(target is None or type(target) is int and 0 < target <= MAX_ID)
        if op == "SET_FIELDS":
            _require(bool(body["values"]) and _zone(body["timezone"]) and target is None)
            _require(body["confirm_complete"] is None or type(body["confirm_complete"]) is bool)
        else:
            _require(body["values"] == {} and body["timezone"] is None)
            if op == "COMPLETE":
                _require(target is None and type(body["confirm_complete"]) is bool)
            else:
                _require(body["confirm_complete"] is None)
                if op == "WITHDRAW":
                    _require(target is None)
    return copy.deepcopy(body)


def decode_command(raw: str | bytes) -> dict:
    """Do not normalize duplicate keys, exponents or nonfinite numbers into commands."""
    _require(isinstance(raw, (str, bytes)) and len(raw) <= 16384)

    def pairs(items):
        result = {}
        for key, value in items:
            _require(key not in result)
            result[key] = value
        return result

    def reject_number(_):
        raise NutritionError()

    try:
        body = json.loads(raw, object_pairs_hook=pairs, parse_float=reject_number,
                          parse_constant=reject_number)
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise NutritionError() from exc
    _require(type(body) is dict)
    return body


def command_bytes(namespace: str, path: str, body: dict) -> bytes:
    if namespace == "DAY":
        match = re.fullmatch(r"/me/nutrition/days/(\d{4}-\d{2}-\d{2})/revisions", path)
        _require(match is not None)
        key = match[1]
    else:
        _require(namespace == "TARGET" and path == "/me/nutrition/targets/revisions")
        _require(type(body) is dict)
        key = (body.get("variant"), body.get("effective_from"))
    validated = validate_command(namespace, key, body)
    envelope = {"body": validated, "method": "POST", "namespace": namespace, "path": path}
    return b"NUT-CMD-1\n" + json.dumps(
        envelope, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")


def command_digest(namespace: str, path: str, body: dict) -> str:
    return hashlib.sha256(command_bytes(namespace, path, body)).hexdigest()


def _model(namespace):
    from app.models.nutrition import NutritionDayRevision, NutritionTargetRevision

    if namespace not in ("DAY", "TARGET"):
        raise NutritionError()
    return NutritionDayRevision if namespace == "DAY" else NutritionTargetRevision


def _key_conditions(model, namespace, key):
    if namespace == "DAY":
        _require(_day(key))
        return [model.local_day == key]
    _require(type(key) is tuple and len(key) == 2 and key[0] in VARIANTS and _day(key[1]))
    return [model.variant == key[0], model.effective_from == key[1]]


def owned_head(db, owner_id: int, namespace: str, key) -> tuple:
    from sqlalchemy import select


    model = _model(namespace)
    row = db.scalar(select(model).where(model.user_id == owner_id,
        *_key_conditions(model, namespace, key)).order_by(model.revision.desc()).limit(1)
        .execution_options(populate_existing=True))
    return row, revision_token(owner_id, namespace, key, row)


def revision_token(owner_id: int, namespace: str, key, row) -> str:
    from app.services.nutrition_identity import nutrition_identity, nutrition_signing_key

    identity = {**nutrition_identity(), "owner_id": owner_id, "namespace": namespace, "key": key,
                "id": row.id if row else None, "revision": row.revision if row else 0}
    payload = b"NUT-HEAD-1\n" + json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()
    token = hmac.new(nutrition_signing_key(), payload, hashlib.sha256).hexdigest()
    return token


def _selected_target(db, owner_id, target_ref, day):
    from sqlalchemy import select

    model = _model("TARGET")
    wanted = db.scalar(select(model).where(model.user_id == owner_id, model.id == target_ref))
    if wanted is None:
        raise NutritionError("foreign_or_missing", 404)
    effective = db.scalar(select(model.effective_from).where(
        model.user_id == owner_id, model.variant == wanted.variant,
        model.effective_from <= day).order_by(model.effective_from.desc()).limit(1))
    current, _ = owned_head(db, owner_id, "TARGET", (wanted.variant, effective)) if effective else (None, None)
    if current is None or current.id != wanted.id or not current.enabled:
        raise NutritionError("stale_target", 409)
    return wanted.id


def _next_values(previous, body, active):
    values = {key: getattr(previous, key) if active else None for key in FIELDS}
    changed = []
    for key, value in body["values"].items():
        if values[key] != value:
            changed.append(key)
        values[key] = value
    return values, changed


def _target_change(previous, active, values, changed, key, body):
    op = body["operation"]
    data = {"variant": key[0], "effective_from": key[1], "enabled": op != "DISABLE"}
    if op == "DISABLE":
        if not active:
            raise NutritionError("no_change")
        changed = [f for f in FIELDS if values[f] is not None]
        values = dict.fromkeys(FIELDS)
    else:
        _require(any(v is not None for v in values.values()))
        if active and not changed:
            raise NutritionError("no_change")
    return data, values, changed


def _mutate(db, owner_id, namespace, key, body, digest):
    previous, token = owned_head(db, owner_id, namespace, key)
    if not hmac.compare_digest(body["expected_head_token"], token):
        raise NutritionError("stale_head", 409)
    op = body["operation"]
    model = _model(namespace)
    active = previous is not None and (previous.state == "ACTIVE" if namespace == "DAY" else previous.enabled)
    values, changed = _next_values(previous, body, active)
    data = {}
    if namespace == "DAY":
        timezone = body["timezone"] if op == "SET_FIELDS" else previous.timezone if previous else None
        if timezone is None:
            raise NutritionError("foreign_or_missing", 404)
        if date.fromisoformat(key) > datetime.now(ZoneInfo(timezone)).date():
            raise NutritionError()
        data = {"local_day": key, "timezone": timezone, "state": "ACTIVE",
                "target_ref": previous.target_ref if active else None,
                "declared_complete": previous.declared_complete if active else False}
        if op == "SET_FIELDS":
            _require(any(v is not None for v in values.values()))
            data["declared_complete"] = body["confirm_complete"] is True
            if active and not changed and previous.timezone == timezone:
                if body["confirm_complete"] is None or previous.declared_complete == body["confirm_complete"]:
                    raise NutritionError("no_change")
        elif not active:
            raise NutritionError("no_change")
        elif op == "SET_TARGET_REF":
            selected = _selected_target(db, owner_id, body["target_ref"], key) if body["target_ref"] is not None else None
            if selected == previous.target_ref:
                raise NutritionError("no_change")
            data["target_ref"] = selected
        elif op == "COMPLETE":
            if body["confirm_complete"] == previous.declared_complete:
                raise NutritionError("no_change")
            data["declared_complete"] = body["confirm_complete"]
        else:
            data.update(state="WITHDRAWN", target_ref=None, declared_complete=False)
            changed = [f for f in FIELDS if values[f] is not None]
            values = dict.fromkeys(FIELDS)
    else:
        data, values, changed = _target_change(previous, active, values, changed, key, body)
    row = model(user_id=owner_id, parent_ref=previous.id if previous else None,
                revision=previous.revision + 1 if previous else 1, request_id=body["request_id"],
                command_digest=digest, receipt={}, provenance={}, **values, **data)
    db.add(row)
    db.flush()
    provenance = copy.deepcopy(previous.provenance) if previous else {"fields": {}}
    fields = provenance.setdefault("fields", {})
    for field in changed:
        fields[field] = {"origin": "USER_DECLARED" if namespace == "DAY" else "USER_DEFINED_TARGET",
                         "method": "MANUAL_ENTRY" if previous is None else "MANUAL_CORRECTION",
                         "source_ref": f"{model.__tablename__}/{row.id}/{field}"}
    if previous is None or namespace == "DAY" and previous.timezone != row.timezone:
        provenance["date"] = {"origin": "USER_DECLARED", "precision": "LOCAL_DAY",
                               "source_ref": f"{model.__tablename__}/{row.id}"}
    row.provenance = provenance
    receipt = {"contract_version": "nutrition-operation/1.0.0", "owner_id": owner_id,
               "namespace": namespace, "request_id": body["request_id"], "command_digest": digest,
               "state": "APPLIED", "entity_ref": row.id, "applied_revision": row.revision,
               "recorded_at": row.recorded_at.replace(tzinfo=UTC).isoformat().replace("+00:00", "Z")}
    row.receipt = receipt
    db.commit()
    return copy.deepcopy(receipt)


def apply_command(db, owner_id: int, namespace: str, key, body: dict, *, auth_proof: dict) -> dict:
    from sqlalchemy import select
    from sqlalchemy.exc import SQLAlchemyError

    from app.services.nutrition_consent import (
        guard_nutrition_owner,
        require_consent,
        require_controlled_acquisition,
    )

    body = validate_command(namespace, key, body)
    path = f"/me/nutrition/days/{key}/revisions" if namespace == "DAY" else "/me/nutrition/targets/revisions"
    digest = command_digest(namespace, path, body)
    model = _model(namespace)
    try:
        guard_nutrition_owner(db, owner_id, auth_proof)
        old = db.scalar(select(model).where(model.user_id == owner_id, model.request_id == body["request_id"]))
        if old is not None:
            if not hmac.compare_digest(old.command_digest, digest):
                raise NutritionError("idempotency_mismatch", 409)
            receipt = copy.deepcopy(old.receipt)
            db.rollback()
            return receipt
        require_controlled_acquisition()
        require_consent(db, owner_id)
        return _mutate(db, owner_id, namespace, key, body, digest)
    except SQLAlchemyError as exc:
        db.rollback()
        raise NutritionError("storage_unavailable", 503) from exc
    except Exception:
        db.rollback()
        raise
