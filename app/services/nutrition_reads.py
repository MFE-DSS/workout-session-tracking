"""Owned nutrition views at two stable append-only watermarks. No inference."""

from __future__ import annotations

import base64
import copy
import hashlib
import hmac
import json
from contextlib import contextmanager
from datetime import date

from sqlalchemy import exists, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import aliased

from app.models.nutrition import NutritionDayRevision as Day
from app.models.nutrition import NutritionTargetRevision as Target
from app.models.user import User
from app.services.nutrition_commands import (
    FIELDS,
    NutritionError,
    decode_command,
    owned_head,
    revision_token,
)
from app.services.nutrition_consent import require_consent
from app.services.nutrition_identity import nutrition_identity, nutrition_signing_key

CONTRACT = "nutrition-manual/1.0.0"
UNITS = {f: {"unit": "kcal" if f == "kcal_milli" else "g", "scale": 1000} for f in FIELDS}


def _signature(value: dict) -> str:
    payload = b"NUT-READ-1\n" + json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hmac.new(nutrition_signing_key(), payload, hashlib.sha256).hexdigest()


def _encode(context: dict) -> str:
    raw = json.dumps(context, sort_keys=True, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode() + "." + _signature(context)


def _decode(cursor: str) -> dict:
    try:
        if not isinstance(cursor, str) or len(cursor) > 4096:
            raise ValueError()
        encoded, signature = cursor.split(".")
        context = decode_command(base64.b64decode(encoded + "=" * (-len(encoded) % 4), altchars=b"-_", validate=True))
        if not hmac.compare_digest(signature, _signature(context)):
            raise ValueError()
        return context
    except (ValueError, TypeError, UnicodeError):
        raise NutritionError("foreign_or_missing", 404) from None


@contextmanager
def _snapshot(db, owner_id):
    if db.get_bind().dialect.name != "sqlite":
        raise NutritionError("storage_unavailable", 503)
    connection = db.connection()
    started = not connection.connection.driver_connection.in_transaction
    try:
        if started:
            connection.exec_driver_sql("BEGIN")
        require_consent(db, owner_id)
        yield
    except SQLAlchemyError as exc:
        raise NutritionError("storage_unavailable", 503) from exc
    finally:
        if started:
            db.rollback()


def _context(db, owner_id, kind, limit, cursor, window=None):
    if type(limit) is not int or not 1 <= limit <= 100:
        raise NutritionError()
    epoch = db.scalar(select(User.session_epoch).where(User.id == owner_id, User.is_active.is_(True)))
    if epoch is None:
        raise NutritionError("foreign_or_missing", 404)
    identity = {"contract": CONTRACT, "owner": owner_id, "epoch": epoch, "kind": kind,
                **nutrition_identity(), "limit": limit, "window": window}
    if cursor is not None:
        context = _decode(cursor)
        if set(context) != set(identity) | {"wd", "wt", "after"} or any(context[k] != v for k, v in identity.items()):
            raise NutritionError("foreign_or_missing", 404)
        if any(type(context[k]) is not int or context[k] < 0 for k in ("wd", "wt")):
            raise NutritionError("foreign_or_missing", 404)
        return context
    return {**identity, "wd": db.scalar(select(func.max(Day.id)).where(Day.user_id == owner_id)) or 0,
            "wt": db.scalar(select(func.max(Target.id)).where(Target.user_id == owner_id)) or 0, "after": None}


def _heads(model, owner_id, watermark):
    newer = aliased(model)
    key = [newer.local_day == model.local_day] if model is Day else [
        newer.variant == model.variant, newer.effective_from == model.effective_from]
    return select(model).where(model.user_id == owner_id, model.id <= watermark, ~exists(
        select(newer.id).where(newer.user_id == owner_id, *key,
                               newer.id <= watermark, newer.revision > model.revision)
    ))


def _entry(row, *, historical=False):
    result = {"id": row.id, "revision": row.revision, "values": {f: getattr(row, f) for f in FIELDS},
              "units": copy.deepcopy(UNITS), "provenance": copy.deepcopy(row.provenance),
              "recorded_at": row.recorded_at.isoformat() + "Z"}
    if isinstance(row, Day):
        result.update(local_day=row.local_day, timezone=row.timezone, state=row.state,
                      declared_complete=row.declared_complete, target_ref=row.target_ref)
    else:
        result.update(variant=row.variant, effective_from=row.effective_from, enabled=row.enabled)
    namespace = "DAY" if isinstance(row, Day) else "TARGET"
    key = row.local_day if namespace == "DAY" else (row.variant, row.effective_from)
    result["head_token"] = None if historical else revision_token(row.user_id, namespace, key, row)
    return result


def _page(owner_id, context, entries, after):
    identity = {k: v for k, v in context.items() if k != "after"}
    return {"contract_version": CONTRACT, "owner_id": owner_id, "read_id": _signature(identity),
            "window": context["window"], "entries": entries,
            "next_cursor": _encode({**context, "after": after}) if after is not None else None,
            "collection_state": "PARTIAL" if after is not None else "COMPLETE"}


def read_days(db, owner_id: int, from_day: str, through_day: str, *, limit=30, cursor=None):
    try:
        first, last = date.fromisoformat(from_day), date.fromisoformat(through_day)
        if first.isoformat() != from_day or last.isoformat() != through_day or not 0 <= (last - first).days <= 365:
            raise ValueError()
    except (ValueError, TypeError):
        raise NutritionError() from None
    window = {"from": from_day, "through": through_day}
    with _snapshot(db, owner_id):
        context = _context(db, owner_id, "days", limit, cursor, window)
        if context["after"] is not None and not isinstance(context["after"], str):
            raise NutritionError("foreign_or_missing", 404)
        rows = list(db.scalars(_heads(Day, owner_id, context["wd"]).where(
            Day.local_day >= from_day, Day.local_day <= through_day).order_by(Day.local_day)))
        selected = [r for r in rows if context["after"] is None or r.local_day > context["after"]]
        page_rows = selected[:limit]
        next_key = page_rows[-1].local_day if len(selected) > limit else None
        page = _page(owner_id, context, [_entry(r) for r in page_rows], next_key)
        coverage, totals = {}, {}
        calendar_days = (last - first).days + 1
        for field in FIELDS:
            values = [getattr(r, field) for r in rows if r.state == "ACTIVE" and getattr(r, field) is not None]
            total = sum(values) if values else None
            totals[field] = {"value": total if total is None or total <= 9007199254740991 else None,
                             "known_days": len(values)}
            if total is not None and total > 9007199254740991:
                totals[field]["reason"] = "UNKNOWN_ARITHMETIC_RANGE"
            coverage[field] = {"known_days": len(values), "missing_days": calendar_days - len(values),
                "partial_days": sum(r.state == "ACTIVE" and not r.declared_complete for r in rows),
                "declared_complete_days": sum(r.state == "ACTIVE" and r.declared_complete for r in rows),
                "withdrawn_days": sum(r.state == "WITHDRAWN" for r in rows), "total_calendar_days": calendar_days}
        page.update(coverage=coverage, totals=totals)
        return page


def read_head(db, owner_id: int, namespace: str, key):
    with _snapshot(db, owner_id):
        row, token = owned_head(db, owner_id, namespace, key)
        return {"contract_version": CONTRACT, "owner_id": owner_id,
                "key": {"local_day": key} if namespace == "DAY" else {"variant": key[0], "effective_from": key[1]},
                "state": "PRESENT" if row else "ABSENT", "head_token": token,
                "entry": _entry(row) if row else None}


def read_export(db, owner_id: int, *, limit=100, cursor=None):
    with _snapshot(db, owner_id):
        context = _context(db, owner_id, "export", limit, cursor)
        after = context["after"]
        if after is not None and (type(after) is not list or len(after) != 2 or after[0] not in (0, 1)
                                  or type(after[1]) is not int or after[1] < 0):
            raise NutritionError("foreign_or_missing", 404)
        found = []
        for index, (namespace, model, wm) in enumerate((("TARGET", Target, context["wt"]), ("DAY", Day, context["wd"]))):
            if after is not None and index < after[0]:
                continue
            query = select(model).where(model.user_id == owner_id, model.id <= wm)
            if after is not None and index == after[0]:
                query = query.where(model.id > after[1])
            for row in db.scalars(query.order_by(model.id).limit(limit + 1 - len(found))):
                found.append((index, namespace, row))
            if len(found) > limit:
                break
        selected = found[:limit]
        next_key = [selected[-1][0], selected[-1][2].id] if len(found) > limit else None
        return _page(owner_id, context,
                     [{"namespace": namespace, "entry": _entry(row, historical=True)} for _, namespace, row in selected], next_key)


def read_targets(db, owner_id: int, *, limit=100, cursor=None):
    with _snapshot(db, owner_id):
        context = _context(db, owner_id, "targets", limit, cursor)
        after = context["after"]
        if after is not None and (type(after) is not list or len(after) != 2
                                  or any(not isinstance(x, str) for x in after)):
            raise NutritionError("foreign_or_missing", 404)
        query = _heads(Target, owner_id, context["wt"])
        if after is not None:
            query = query.where((Target.variant > after[0]) | (
                (Target.variant == after[0]) & (Target.effective_from > after[1])))
        found = list(db.scalars(query.order_by(Target.variant, Target.effective_from).limit(limit + 1)))
        selected = found[:limit]
        next_key = [selected[-1].variant, selected[-1].effective_from] if len(found) > limit else None
        return _page(owner_id, context, [_entry(row) for row in selected], next_key)


def read_versions(db, owner_id: int, namespace: str, reference, *, limit=100, cursor=None):
    with _snapshot(db, owner_id):
        if namespace == "TARGET":
            if type(reference) is not int or not 0 < reference <= 9007199254740991:
                raise NutritionError()
            original = db.scalar(select(Target).where(Target.user_id == owner_id, Target.id == reference))
            if original is None:
                raise NutritionError("foreign_or_missing", 404)
            model, key = Target, [original.variant, original.effective_from]
            conditions = [Target.variant == key[0], Target.effective_from == key[1]]
        elif namespace == "DAY":
            model, key = Day, reference
            # owned_head validates the natural date key without creating a row.
            original, _ = owned_head(db, owner_id, "DAY", reference)
            if original is None:
                raise NutritionError("foreign_or_missing", 404)
            conditions = [Day.local_day == reference]
        else:
            raise NutritionError()
        context = _context(db, owner_id, "versions", limit, cursor, {"namespace": namespace, "key": key})
        after = context["after"]
        if after is not None and (type(after) is not int or after < 0):
            raise NutritionError("foreign_or_missing", 404)
        watermark = context["wd"] if namespace == "DAY" else context["wt"]
        query = select(model).where(model.user_id == owner_id, *conditions, model.id <= watermark)
        if after is not None:
            query = query.where(model.id > after)
        found = list(db.scalars(query.order_by(model.id).limit(limit + 1)))
        selected = found[:limit]
        return _page(owner_id, context, [_entry(row, historical=True) for row in selected],
                     selected[-1].id if len(found) > limit else None)
