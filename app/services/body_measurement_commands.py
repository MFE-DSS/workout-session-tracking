"""Atomic BODY-01 commands; callers never supply authority or ownership."""

from __future__ import annotations

import math
import re
from datetime import UTC, date, datetime

from sqlalchemy import delete, func, inspect, select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.models.body_consent import CONSENT_BODY_MEASUREMENTS, BodyConsent
from app.models.body_measurement_operation import BodyMeasurementOperation as Operation
from app.models.measurement import BodyMeasurement
from app.services.body_measurement_reads import (
    BodyCommandError,
    canonical_digest,
    fingerprint,
    instant,
    owned_head,
)
from app.services.plan_v3.transactions import RuntimeFailure, guard_owner

SAFE_ID = 9007199254740991


class BodyValueError(BodyCommandError):
    """A rejected numeric input; keep the existing SSR form message available."""

    def __init__(self, form_message: str):
        super().__init__("invalid_measurement_value", 422)
        self.form_message = form_message


def require_schema(db: Session) -> None:
    if db.get_bind().dialect.name != "sqlite":
        raise BodyCommandError("body_dialect_not_admitted", 503)
    schema = inspect(db.connection())
    expected = Operation.__table__
    if not schema.has_table(expected.name):
        raise BodyCommandError("body_schema_unavailable", 503)
    if {c["name"] for c in schema.get_columns(expected.name)} != set(expected.columns.keys()):
        raise BodyCommandError("body_schema_unavailable", 503)
    uniques = {tuple(c["column_names"]) for c in schema.get_unique_constraints(expected.name)}
    if not {("owner_id", "request_id"), ("owner_id", "root_ref", "applied_revision")} <= uniques:
        raise BodyCommandError("body_schema_unavailable", 503)
    indexes = {i["name"]: i for i in schema.get_indexes(expected.name)}
    if not indexes.get("uq_body_correction_parent", {}).get("unique"):
        raise BodyCommandError("body_schema_unavailable", 503)


def validate_command(command: dict, *, check_bounds: bool = True) -> None:
    if not isinstance(command, dict) or set(command) - {
        "request_id",
        "operation",
        "root_ref",
        "expected_head_token",
        "values",
        "measured_on",
        "confirm_all_versions",
        "_measured_at",
        "_date_precision",
    }:
        raise BodyCommandError("invalid_body_command", 422)
    key = command.get("request_id")
    if not isinstance(key, str) or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}", key) is None:
        raise BodyCommandError("invalid_request_id", 422)
    if not isinstance(command.get("operation"), str) or command["operation"] not in {
        "CREATE",
        "CORRECT",
        "ERASE",
    }:
        raise BodyCommandError("invalid_body_operation", 422)
    if command["operation"] == "ERASE":
        if command.get("confirm_all_versions") is not True or set(command) - {
            "request_id",
            "operation",
            "root_ref",
            "expected_head_token",
            "confirm_all_versions",
        }:
            raise BodyCommandError("erase_confirmation_required", 422)
        return
    from app.services.body_profile import BODY_MEASUREMENT_FIELDS

    specs = {s.key: s for s in BODY_MEASUREMENT_FIELDS}
    values = command.get("values", {})
    if not isinstance(values, dict) or set(values) - specs.keys():
        raise BodyCommandError("invalid_measurement_fields", 422)
    for key, value in values.items():
        if value is None:
            continue
        spec = specs[key]
        try:
            finite = type(value) in {int, float} and math.isfinite(value)
        except OverflowError:
            finite = False
        if not finite:
            raise BodyValueError(f"{spec.label} : valeur non numérique")
        if check_bounds and not spec.min <= value <= spec.max:
            raise BodyValueError(
                f"{spec.label} : valeur hors plage plausible ({spec.min:g}–{spec.max:g})"
            )


def _command_time(command: dict, previous: BodyMeasurement | None) -> tuple[datetime, dict | None]:
    if "measured_on" in command:
        text = command["measured_on"]
        try:
            day = date.fromisoformat(text) if isinstance(text, str) and len(text) == 10 else None
        except ValueError:
            day = None
        if day is None or day.isoformat() != text or day > datetime.now(UTC).date():
            raise BodyCommandError("invalid_measurement_day", 422)
        return datetime(day.year, day.month, day.day, tzinfo=UTC), {
            "precision": "DAY_UTC_CONVENTION"
        }
    if "_measured_at" in command:
        try:
            value = datetime.fromisoformat(command["_measured_at"])
        except (TypeError, ValueError):
            raise BodyCommandError("invalid_measurement_date", 422) from None
        return value, {"precision": command.get("_date_precision", "UNKNOWN")}
    if previous is not None:
        return previous.measured_at, None
    if command.get("_date_precision") == "SERVER_CAPTURE_TIME":
        # Capture on first application only, after replay lookup. Including
        # a freshly generated timestamp in the digest breaks exact retries.
        return datetime.now(UTC), {"precision": "SERVER_CAPTURE_TIME"}
    raise BodyCommandError("measurement_day_required", 422)


def _next_id(db: Session) -> int:
    maxima = [db.scalar(select(func.max(BodyMeasurement.id))) or 0]
    for column in (Operation.measurement_ref, Operation.parent_ref, Operation.root_ref):
        maxima.append(db.scalar(select(func.max(column))) or 0)
    result = max(maxima) + 1
    if result > SAFE_ID:
        raise BodyCommandError("id_allocation_unavailable", 503)
    return result


def _mutate(db: Session, owner_id: int, command: dict, source: str) -> dict:
    from app.services.body_profile import BODY_MEASUREMENT_FIELDS

    operation = command["operation"]
    previous = None
    revision = 0
    root = command.get("root_ref")
    if operation != "CREATE":
        previous, token, revision = owned_head(db, owner_id, root)
        if command.get("expected_head_token") != token:
            raise BodyCommandError("head_conflict")
    elif any(key in command for key in ("root_ref", "expected_head_token", "confirm_all_versions")):
        raise BodyCommandError("invalid_body_command", 422)
    before = fingerprint(previous) if previous is not None else None
    fields = [s.key for s in BODY_MEASUREMENT_FIELDS]
    values = command.get("values", {})
    provenance = {}
    date_provenance = None
    if operation == "ERASE":
        refs = list(
            db.scalars(
                select(Operation.measurement_ref).where(
                    Operation.owner_id == owner_id,
                    Operation.root_ref == root,
                )
            )
        )
        refs.extend([root, previous.id])
        measurement_ref = previous.id
        db.execute(
            delete(BodyMeasurement).where(
                BodyMeasurement.user_id == owner_id, BodyMeasurement.id.in_(refs)
            )
        )
        changed = []
        after = None
    else:
        changed = [
            key for key in values if previous is None or values[key] != getattr(previous, key)
        ]
        # Syntax/finite inputs were checked before replay. Fresh bounds apply
        # only to real changes, under the owned head lock; command bytes stay exact.
        validate_command({**command, "values": {key: values[key] for key in changed}})
        measured_at, date_provenance = _command_time(command, previous)
        merged = {key: getattr(previous, key) if previous else None for key in fields}
        merged.update(values)
        if not any(value is not None for value in merged.values()) and not (
            previous is not None and previous.calf_cm is not None
        ):
            raise BodyCommandError("measurement_empty_use_erase", 422)
        if (
            previous is not None
            and not changed
            and instant(measured_at) == instant(previous.measured_at)
        ):
            raise BodyCommandError("measurement_unchanged", 422)
        measurement_ref = _next_id(db)
        root = measurement_ref if previous is None else root
        row = BodyMeasurement(
            id=measurement_ref, user_id=owner_id, measured_at=measured_at, **merged
        )
        if previous is not None:
            row.calf_cm = previous.calf_cm
        db.add(row)
        db.flush()
        after = fingerprint(row)
        for key in changed:
            provenance[key] = {
                "origin": "USER_DECLARED",
                "acquisition": source,
                "source_ref": f"body_measurements/{row.id}/{key}",
            }
    recorded_at = datetime.now(UTC)
    receipt = {
        "contract_version": "body-operation/1.0.0",
        "owner_id": owner_id,
        "command_digest": canonical_digest(command),
        "request_id": command["request_id"],
        "operation": operation,
        "root_ref": root,
        "measurement_id": measurement_ref,
        "applied_revision": revision + 1,
        "recorded_at": instant(recorded_at),
        "state": "ERASED" if operation == "ERASE" else "APPLIED",
    }
    db.add(
        Operation(
            owner_id=owner_id,
            request_id=command["request_id"],
            command_digest=canonical_digest(command),
            operation=operation,
            root_ref=root,
            parent_ref=previous.id if operation == "CORRECT" else None,
            measurement_ref=measurement_ref,
            applied_revision=revision + 1,
            changed_fields=changed,
            provenance_by_changed_field=provenance,
            date_provenance=date_provenance,
            before_fingerprint=before,
            after_fingerprint=after,
            receipt=receipt,
            recorded_at=recorded_at,
        )
    )
    db.flush()
    return receipt


def apply_command(
    db: Session, owner_id: int, command: dict, *, source: str, require_consent: bool = True
) -> dict:
    """Reserve SQLite's global write lock before checking or allocating anything."""
    validate_command(command, check_bounds=False)
    try:
        require_schema(db)
        guard_owner(db, owner_id)
        existing = db.scalar(
            select(Operation).where(
                Operation.owner_id == owner_id, Operation.request_id == command["request_id"]
            )
        )
        if existing is not None:
            if existing.command_digest != canonical_digest(command):
                raise BodyCommandError("idempotency_mismatch")
            receipt = dict(existing.receipt)
            db.commit()
            return receipt
        if require_consent and command["operation"] != "ERASE":
            # The write guard is held: re-read the grant, never a retained ORM value.
            consent = db.scalar(
                select(BodyConsent).where(
                    BodyConsent.user_id == owner_id,
                    BodyConsent.consent_type == CONSENT_BODY_MEASUREMENTS,
                ).execution_options(populate_existing=True)
            )
            if not (consent and consent.granted):
                raise BodyCommandError("body_consent_required", 403)
        receipt = _mutate(db, owner_id, command, source)
        db.commit()
        return receipt
    except RuntimeFailure as exc:
        db.rollback()
        raise BodyCommandError(exc.code, exc.status) from None
    except BodyCommandError:
        db.rollback()
        raise
    except IntegrityError:
        db.rollback()
        raise BodyCommandError("head_conflict") from None
    except OperationalError:
        db.rollback()
        raise BodyCommandError("body_storage_unavailable", 503) from None
    except Exception:
        # A flush hook/driver failure can leave the Session inactive even
        # after SQLite rolled back. Return a clean caller-owned session and
        # let the HTTP boundary redact unexpected failures.
        db.rollback()
        raise
