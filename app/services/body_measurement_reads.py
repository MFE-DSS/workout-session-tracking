"""Canonical current-version predicate and owned lineage identity."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import math
from datetime import UTC, datetime

from sqlalchemy import case, exists, func, or_, select
from sqlalchemy.orm import Session

from app.models.body_measurement_operation import BodyMeasurementOperation as Operation
from app.models.measurement import BodyMeasurement


class BodyCommandError(ValueError):
    def __init__(self, code: str, status: int = 409):
        self.code = code
        self.status = status
        super().__init__(code)


def instant(value: datetime | None) -> str | None:
    if value is None:
        return None
    aware = value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)
    return aware.isoformat()


def canonical_digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
        ).encode()
    ).hexdigest()


def fingerprint(row: BodyMeasurement) -> str:
    values = {
        c.key: (
            instant(getattr(row, c.key))
            if c.key in {"measured_at", "created_at"}
            else repr(getattr(row, c.key))
        )
        for c in BodyMeasurement.__table__.columns
    }
    return canonical_digest(values)


def head_contexts(db: Session, owner_id: int, rows: list[BodyMeasurement]) -> dict:
    """Batch identity/count projection for existing SSR history cards."""
    ids = [row.id for row in rows if row.user_id == owner_id]
    heads = {
        op.measurement_ref: op
        for op in db.scalars(
            select(Operation).where(
                Operation.owner_id == owner_id,
                Operation.measurement_ref.in_(ids),
                Operation.operation.in_(["CREATE", "CORRECT"]),
            )
        )
    }
    roots = {heads[row.id].root_ref if row.id in heads else row.id for row in rows}
    counts = {
        root: (count, creates)
        for root, count, creates in db.execute(
            select(
                Operation.root_ref,
                func.count(Operation.id),
                func.sum(case((Operation.operation == "CREATE", 1), else_=0)),
            )
            .where(
                Operation.owner_id == owner_id,
                Operation.root_ref.in_(roots),
                Operation.operation.in_(["CREATE", "CORRECT"]),
            )
            .group_by(Operation.root_ref)
        )
    }
    result = {}
    for row in rows:
        if row.user_id != owner_id:
            raise BodyCommandError("measurement_not_found", 404)
        op = heads.get(row.id)
        root, revision = (op.root_ref, op.applied_revision) if op else (row.id, 0)
        count, creates = counts.get(root, (0, 0))
        result[row.id] = {
            "root_ref": root,
            "revision": revision,
            "version_count": count if creates else count + 1,
            "token": canonical_digest(
                {
                    "owner": owner_id,
                    "root": root,
                    "head": row.id,
                    "revision": revision,
                    "facts": fingerprint(row),
                }
            ),
        }
    return result


def current_measurement_predicate():
    """One SQL predicate, no per-row query or raw fallback if schema is missing."""
    return ~exists(
        select(Operation.id).where(
            Operation.owner_id == BodyMeasurement.user_id,
            Operation.parent_ref == BodyMeasurement.id,
            Operation.operation == "CORRECT",
        )
    )


def owned_head(db: Session, owner_id: int, root_ref: int) -> tuple[BodyMeasurement, str, int]:
    if type(root_ref) is not int or not 0 < root_ref <= 9007199254740991:
        raise BodyCommandError("measurement_not_found", 404)
    latest = db.scalar(
        select(Operation)
        .where(Operation.owner_id == owner_id, Operation.root_ref == root_ref)
        .order_by(Operation.applied_revision.desc())
        .limit(1)
    )
    if latest and latest.operation == "ERASE":
        raise BodyCommandError("measurement_not_found", 404)
    measurement_ref = latest.measurement_ref if latest else root_ref
    row = db.scalar(
        select(BodyMeasurement)
        .where(BodyMeasurement.id == measurement_ref, BodyMeasurement.user_id == owner_id)
        .execution_options(populate_existing=True)
    )
    if row is None:
        raise BodyCommandError("measurement_not_found", 404)
    if (
        latest is None
        and db.scalar(
            select(Operation.id)
            .where(
                Operation.owner_id == owner_id,
                Operation.measurement_ref == root_ref,
                Operation.root_ref != root_ref,
            )
            .limit(1)
        )
        is not None
    ):
        raise BodyCommandError("measurement_not_found", 404)
    revision = latest.applied_revision if latest else 0
    token = canonical_digest(
        {
            "owner": owner_id,
            "root": root_ref,
            "head": row.id,
            "revision": revision,
            "facts": fingerprint(row),
        }
    )
    return row, token, revision


CONTRACT = "body-measurements/1.0.0"


def body_revision(db: Session, owner_id: int) -> int:
    return db.scalar(select(func.max(Operation.id)).where(Operation.owner_id == owner_id)) or 0


def _sources(db, owner_id, root_ref, revision):
    """Fold metadata in bounded-memory chunks; never duplicate the numbers."""
    sources, date_precision = {}, None
    query = (
        select(Operation)
        .where(
            Operation.owner_id == owner_id,
            Operation.root_ref == root_ref,
            Operation.applied_revision <= revision,
        )
        .order_by(Operation.applied_revision.desc())
    )
    for operation in db.scalars(query.execution_options(yield_per=64)):
        for key, source in operation.provenance_by_changed_field.items():
            sources.setdefault(key, source)
        if date_precision is None and operation.date_provenance:
            date_precision = operation.date_provenance["precision"]
        if operation.operation == "CREATE":
            break
    return sources, date_precision or "UNKNOWN"


def document(db: Session, owner_id: int, row: BodyMeasurement, *, context=None) -> dict:
    from app.services.body_profile import BODY_MEASUREMENT_FIELDS

    if row.user_id != owner_id:
        raise BodyCommandError("measurement_not_found", 404)
    operation = db.scalar(
        select(Operation)
        .where(
            Operation.owner_id == owner_id,
            Operation.measurement_ref == row.id,
            Operation.operation.in_(["CREATE", "CORRECT"]),
        )
        .limit(1)
    )
    root = operation.root_ref if operation else row.id
    head, token, _ = context if context is not None else owned_head(db, owner_id, root)
    revision = operation.applied_revision if operation else 0
    sources, precision = _sources(db, owner_id, root, revision)
    fields = {}
    specs = {spec.key: spec for spec in BODY_MEASUREMENT_FIELDS}
    for key in [*specs, "calf_cm"]:
        value = getattr(row, key)
        finite = value is None or math.isfinite(value)
        spec = specs.get(key)
        quality = (
            "MISSING"
            if value is None
            else (
                "INVALID_NONFINITE"
                if not finite
                else (
                    "LEGACY_OUTSIDE_CURRENT_BOUNDS"
                    if spec and not spec.min <= value <= spec.max
                    else "KNOWN"
                )
            )
        )
        fields[key] = {
            "value": value if finite else None,
            "raw_value_repr": None if finite else str(value),
            "quality": quality,
            "unit": "kg" if key == "weight_kg" else "cm",
            "provenance": sources.get(
                key,
                {
                    "origin": "UNKNOWN",
                    "acquisition": "UNKNOWN",
                    "source_ref": f"body_measurements/{root}/{key}",
                },
            ),
        }
    return {
        "root_ref": root,
        "measurement_id": row.id,
        "revision": revision,
        "state": "CURRENT" if row.id == head.id else "SUPERSEDED",
        "head_token": token if row.id == head.id else None,
        "measured_at": instant(row.measured_at),
        "recorded_at": instant(row.created_at),
        "date_precision": precision,
        "timezone_basis": "DATABASE_UTC_CONVENTION",
        "fields": fields,
    }


def owned_document(db: Session, owner_id: int, root_ref: int) -> dict:
    context = owned_head(db, owner_id, root_ref)
    return document(db, owner_id, context[0], context=context)


def _encode_cursor(payload: dict) -> str:
    from app.config import get_settings

    encoded = (
        base64.urlsafe_b64encode(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        )
        .rstrip(b"=")
        .decode()
    )
    signature = hmac.new(
        get_settings().app_secret_key.encode(), ("body-cursor\0" + encoded).encode(), hashlib.sha256
    ).hexdigest()
    return encoded + "." + signature


def _cursor(raw: str | None, identity: dict) -> dict | None:
    if raw is None:
        return None
    try:
        from app.config import get_settings

        if not isinstance(raw, str) or len(raw) > 4096:
            raise ValueError
        encoded, signature = raw.split(".")
        expected = hmac.new(
            get_settings().app_secret_key.encode(),
            ("body-cursor\0" + encoded).encode(),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError
        data = json.loads(
            base64.b64decode(encoded + "=" * (-len(encoded) % 4), altchars=b"-_", validate=True)
        )
        if (
            set(data) != {"identity", "last_id", "last_at"}
            or type(data["last_id"]) is not int
            or data["last_id"] <= 0
        ):
            raise ValueError
        if data["identity"] != identity:
            raise BodyCommandError("body_cursor_conflict")
        return data
    except BodyCommandError:
        raise
    except (ValueError, TypeError, UnicodeError, AttributeError, KeyError):
        raise BodyCommandError("invalid_body_cursor", 422) from None


def page(
    db: Session,
    owner_id: int,
    *,
    kind: str,
    limit: int = 50,
    cursor: str | None = None,
    from_day=None,
    through_day=None,
    root_ref=None,
) -> dict:
    """Bounded current, weight-only, version or raw export page."""
    from datetime import timedelta

    from app.services.body_profile import BODY_MEASUREMENT_FIELDS

    if type(limit) is not int or not 1 <= limit <= 100:
        raise BodyCommandError("invalid_body_limit", 422)
    revision = body_revision(db, owner_id)
    window = {
        "from": from_day.isoformat() if from_day else None,
        "through": through_day.isoformat() if through_day else None,
    }
    identity = {
        "owner": owner_id,
        "kind": kind,
        "root": root_ref,
        "window": window,
        "revision": revision,
    }
    previous = _cursor(cursor, identity)
    query = select(BodyMeasurement).where(BodyMeasurement.user_id == owner_id)
    context = None
    if kind in {"CURRENT", "WEIGHT"}:
        query = query.where(current_measurement_predicate())
    if kind == "WEIGHT":
        query = query.where(BodyMeasurement.weight_kg.is_not(None))
    if kind == "VERSIONS":
        context = owned_head(db, owner_id, root_ref)
        refs = select(Operation.measurement_ref).where(
            Operation.owner_id == owner_id,
            Operation.root_ref == root_ref,
            Operation.operation.in_(["CREATE", "CORRECT"]),
        )
        query = query.where(or_(BodyMeasurement.id == root_ref, BodyMeasurement.id.in_(refs)))
    if from_day:
        query = query.where(
            BodyMeasurement.measured_at
            >= datetime.combine(from_day, datetime.min.time(), tzinfo=UTC)
        )
    if through_day:
        query = query.where(
            BodyMeasurement.measured_at
            < datetime.combine(through_day + timedelta(days=1), datetime.min.time(), tzinfo=UTC)
        )
    chronological = kind in {"CURRENT", "WEIGHT"}
    if previous:
        if chronological:
            try:
                at = datetime.fromisoformat(previous["last_at"])
            except (ValueError, TypeError):
                raise BodyCommandError("invalid_body_cursor", 422) from None
            query = query.where(
                (BodyMeasurement.measured_at < at)
                | ((BodyMeasurement.measured_at == at) & (BodyMeasurement.id < previous["last_id"]))
            )
        else:
            query = query.where(BodyMeasurement.id < previous["last_id"])
    query = (
        query.order_by(BodyMeasurement.measured_at.desc(), BodyMeasurement.id.desc())
        if chronological
        else query.order_by(BodyMeasurement.id.desc())
    )
    rows = list(db.scalars(query.limit(limit + 1)))
    entries = [document(db, owner_id, row, context=context) for row in rows[:limit]]
    if body_revision(db, owner_id) != revision:
        raise BodyCommandError("body_cursor_conflict")
    next_cursor = None
    if len(rows) > limit:
        last = rows[limit - 1]
        next_cursor = _encode_cursor(
            {"identity": identity, "last_id": last.id, "last_at": instant(last.measured_at)}
        )
    return {
        "contract_version": CONTRACT,
        "owner_id": owner_id,
        "body_revision": revision,
        "state": "AVAILABLE" if entries else "EMPTY",
        "entries": entries,
        "next_cursor": next_cursor,
        "window": window,
        "field_specs": [
            {
                "key": spec.key,
                "label": spec.label,
                "min": spec.min,
                "max": spec.max,
                "unit": "kg" if spec.key == "weight_kg" else "cm",
            }
            for spec in BODY_MEASUREMENT_FIELDS
        ],
    }
