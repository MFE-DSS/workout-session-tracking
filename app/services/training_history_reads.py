"""Bounded owned history. Reads captured facts; never reconstructs old prescriptions."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import math
import uuid
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import and_, case, func, or_, select

from app.config import get_settings
from app.models.session import SessionExercise, SetLog, WorkoutSession

VERSION = "training-history/1.0.0"


class HistoryReadError(ValueError):
    def __init__(self, code, status=400):
        super().__init__(code)
        self.code, self.status = code, status


def _utc(value):
    # Existing database timestamps use the canonical UTC convention when naive.
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


def _iso(value):
    return None if value is None else _utc(value).isoformat().replace("+00:00", "Z")


def _instant(value):
    if not isinstance(value, str):
        raise ValueError("instant required")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("offset required")
    return result.astimezone(UTC)


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _digest(value):
    return hashlib.sha256(_json(value).encode()).hexdigest()


def _sign(kind, payload):
    encoded = (
        base64.urlsafe_b64encode(
            _json({"version": VERSION, "kind": kind, "value": payload}).encode()
        )
        .rstrip(b"=")
        .decode()
    )
    signature = hmac.new(
        get_settings().app_secret_key.encode(),
        ("training-history\0" + encoded).encode(),
        hashlib.sha256,
    ).hexdigest()
    return encoded + "." + signature


def _unsigned(token, kind):
    try:
        if not isinstance(token, str) or len(token) > 16384:
            raise ValueError
        encoded, signature = token.split(".")
        expected = hmac.new(
            get_settings().app_secret_key.encode(),
            ("training-history\0" + encoded).encode(),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError
        raw = base64.b64decode(encoded + "=" * (-len(encoded) % 4), altchars=b"-_", validate=True)
        if base64.urlsafe_b64encode(raw).rstrip(b"=").decode() != encoded:
            raise ValueError
        data = json.loads(raw, parse_constant=lambda _v: (_ for _ in ()).throw(ValueError()))
        if (
            set(data) != {"version", "kind", "value"}
            or data["version"] != VERSION
            or data["kind"] != kind
        ):
            raise ValueError
        return data["value"]
    except (ValueError, TypeError, UnicodeError, AttributeError):
        raise HistoryReadError("invalid_history_reference") from None


def _parameters(owner, period, time_zone, limit):
    try:
        if type(owner) is not int or owner <= 0 or period not in {"4w", "12w", "all"}:
            raise ValueError
        if type(limit) is not int or not 1 <= limit <= 100 or not isinstance(time_zone, str):
            raise ValueError
        zone = ZoneInfo(time_zone)
    except (TypeError, ValueError, ZoneInfoNotFoundError):
        raise HistoryReadError("invalid_history_query", 422) from None
    return zone


def _window(period, time_zone, zone, now):
    local = now.astimezone(zone)
    monday = local.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(
        days=local.weekday()
    )
    start = None if period == "all" else monday - timedelta(weeks=3 if period == "4w" else 11)
    return {"period": period, "time_zone": time_zone, "from": _iso(start), "until": _iso(now)}


def _filters(owner, window, ceiling):
    result = [
        WorkoutSession.user_id == owner,
        WorkoutSession.id <= ceiling,
        WorkoutSession.started_at < _instant(window["until"]),
    ]
    if window["from"] is not None:
        result.append(WorkoutSession.started_at >= _instant(window["from"]))
    return result


def _work_fact():
    return (
        select(SetLog.id)
        .join(SessionExercise, SessionExercise.id == SetLog.session_exercise_id)
        .where(
            SessionExercise.session_id == WorkoutSession.id,
            SetLog.kind == "work",
            SetLog.completed.is_(True),
            or_(SetLog.reps.is_not(None), SetLog.weight_kg.is_not(None)),
        )
        .exists()
    )


def _performed():
    return and_(
        WorkoutSession.status == "completed",
        WorkoutSession.excluded_from_stats.is_(False),
        _work_fact(),
    )


def _counts(db, filters):
    row = db.execute(
        select(
            func.count(WorkoutSession.id),
            func.coalesce(func.sum(case((WorkoutSession.status == "completed", 1), else_=0)), 0),
            func.coalesce(func.sum(case((WorkoutSession.status == "in_progress", 1), else_=0)), 0),
            func.coalesce(
                func.sum(case((WorkoutSession.excluded_from_stats.is_(True), 1), else_=0)), 0
            ),
            func.coalesce(func.sum(case((_performed(), 1), else_=0)), 0),
        ).where(*filters)
    ).one()
    return dict(
        zip(
            ("recorded", "completed", "open", "excluded", "completed_with_work"),
            map(int, row),
            strict=True,
        ),
        state="AVAILABLE",
    )


def _weekly(db, filters, window, zone):
    if window["from"] is None:
        return []
    current = _instant(window["from"]).astimezone(zone)
    until = _instant(window["until"])
    rows = []
    while current < until:
        end = current + timedelta(weeks=1)
        count = db.scalar(
            select(func.count(WorkoutSession.id)).where(
                *filters,
                _performed(),
                WorkoutSession.started_at >= current.astimezone(UTC),
                WorkoutSession.started_at < end.astimezone(UTC),
            )
        )
        rows.append(
            {
                "week_from": _iso(current),
                "week_until": _iso(end),
                "completed_with_work": int(count),
                "partial_current_week": end.astimezone(UTC) > until,
            }
        )
        current = end
    return rows


def _descriptor(db, session):
    from app.services.plan_v3.execution import is_scientific_session, owned_binding
    from app.services.plan_v3.transactions import RuntimeFailure, schema_available

    if not is_scientific_session(session):
        captured = list(
            db.scalars(
                select(SessionExercise)
                .where(SessionExercise.session_id == session.id)
                .order_by(SessionExercise.position, SessionExercise.id)
            )
        )
        return {
            "execution_profile": "LEGACY_V1",
            "prescription": "UNKNOWN_NOT_CAPTURED",
            "equipment_context": "UNKNOWN_NOT_CAPTURED",
            "mapping": [
                {
                    "se_id": row.id,
                    "position": row.position,
                    "code": row.exercise_code_snapshot,
                    "name": row.exercise_name_snapshot,
                }
                for row in captured
            ],
        }
    if not schema_available(db):
        return {"execution_profile": "UNKNOWN", "reason": "SCHEMA_UNAVAILABLE"}
    try:
        _, binding, payload, _ = owned_binding(db, session.user_id, session.id)
        return {
            "execution_profile": "SCI_V3",
            "binding_digest": binding.binding_digest,
            "execution_profile_version": binding.execution_profile_version,
            "mapping": payload["mapping"],
        }
    except RuntimeFailure:
        return {"execution_profile": "UNKNOWN", "reason": "BINDING_UNAVAILABLE"}


def _metadata(session, descriptor):
    return {
        "owner_id": session.user_id,
        "session_id": session.id,
        "started_at": _iso(session.started_at),
        "created_at": _iso(session.created_at),
        "template_slug": session.template_slug_snapshot,
        "name": session.template_name_snapshot,
        "descriptor": descriptor,
    }


def _exercise_links(db, session, descriptor, context):
    if descriptor["execution_profile"] == "UNKNOWN":
        return []
    cache = {("SCI_DESCRIPTOR", session.id): descriptor}
    rows = db.scalars(select(SessionExercise).where(SessionExercise.session_id == session.id)
                      .order_by(SessionExercise.position, SessionExercise.id))
    links = []
    for row in rows:
        identity = _exercise_identity(db, row, session, cache)
        links.append({"se_id": row.id, "name": row.substituted_name or row.exercise_name_snapshot or "",
                      "exercise_ref": _exercise_reference(context, identity) if identity else None})
    return links


def _entry(db, session, context):
    descriptor = _descriptor(db, session)
    links = _exercise_links(db, session, descriptor, context)
    return {
        "session_id": session.id,
        "started_at": _iso(session.started_at),
        "ended_at": _iso(session.ended_at),
        "status": session.status,
        "excluded_from_stats": session.excluded_from_stats,
        "template_slug": session.template_slug_snapshot,
        "name": session.template_name_snapshot,
        "execution_profile": descriptor["execution_profile"],
        "descriptor": descriptor,
        "exercise_links": links,
        "entry_ref": _sign(
            "ENTRY",
            {
                "context": context,
                "session_id": session.id,
                "metadata_digest": _digest(_metadata(session, descriptor)),
                "exercise_links_digest": _digest(links),
            },
        ),
    }


def _new_context(db, owner, period, time_zone, zone, now):
    window = _window(period, time_zone, zone, now)
    ceiling = int(
        db.scalar(select(func.max(WorkoutSession.id)).where(WorkoutSession.user_id == owner)) or 0
    )
    filters = _filters(owner, window, ceiling)
    return {
        "owner_id": owner,
        "read_id": uuid.uuid4().hex,
        "window": window,
        "id_ceiling": ceiling,
        "counts_read_at": _iso(now),
        "counts": _counts(db, filters),
        "weekly_counts": _weekly(db, filters, window, zone),
    }


def _continued_context(token, owner, period, time_zone):
    cursor = _unsigned(token, "SESSIONS_CURSOR")
    try:
        context = cursor["context"]
        if (
            context["owner_id"] != owner
            or context["window"]["period"] != period
            or context["window"]["time_zone"] != time_zone
        ):
            raise ValueError
        if type(cursor["after_id"]) is not int or cursor["after_id"] <= 0:
            raise ValueError
        _instant(cursor["after_at"])
        return context, cursor
    except (KeyError, TypeError, ValueError):
        raise HistoryReadError("invalid_history_cursor") from None


def read_sessions(db, owner_id, *, period, time_zone, limit=50, cursor=None, now=None):
    zone = _parameters(owner_id, period, time_zone, limit)
    now = now or datetime.now(UTC)
    if not isinstance(now, datetime) or now.tzinfo is None:
        raise HistoryReadError("invalid_history_instant", 422)
    with db.no_autoflush:
        if cursor is None:
            context, after = _new_context(db, owner_id, period, time_zone, zone, now), None
        else:
            context, after = _continued_context(cursor, owner_id, period, time_zone)
        filters = _filters(owner_id, context["window"], context["id_ceiling"])
        if after:
            at = _instant(after["after_at"])
            filters.append(
                or_(
                    WorkoutSession.started_at < at,
                    and_(WorkoutSession.started_at == at, WorkoutSession.id < after["after_id"]),
                )
            )
        found = list(
            db.scalars(
                select(WorkoutSession)
                .where(*filters)
                .order_by(WorkoutSession.started_at.desc(), WorkoutSession.id.desc())
                .limit(limit + 1)
            )
        )
        rows, more = found[:limit], len(found) > limit
        next_cursor = None
        if more:
            last = rows[-1]
            next_cursor = _sign(
                "SESSIONS_CURSOR",
                {"context": context, "after_at": _iso(last.started_at), "after_id": last.id},
            )
        return {
            "contract_version": VERSION,
            "owner_id": owner_id,
            "state": "AVAILABLE" if rows else "EMPTY",
            "read_id": context["read_id"],
            "read_context": _sign("READ_CONTEXT", context),
            "window": context["window"],
            "membership": "LIVE_BOUNDED_MEMBERSHIP",
            "counts_read_at": context["counts_read_at"],
            "rows_read_at": _iso(now),
            "counts": context["counts"],
            "weekly_counts": context["weekly_counts"],
            "planned_calendar": {"state": "NOT_PERSISTED", "count": None},
            "completeness": "MORE_AVAILABLE" if more else "COMPLETE",
            "next_cursor": next_cursor,
            "entries": [_entry(db, session, context) for session in rows],
        }


def _selected(db, owner, session_id, entry_ref):
    # Ownership lookup deliberately precedes token parsing, including bad tokens.
    if type(owner) is not int or owner <= 0 or type(session_id) is not int or session_id <= 0:
        raise HistoryReadError("history_entry_not_found", 404)
    session = db.scalar(
        select(WorkoutSession).where(
            WorkoutSession.id == session_id, WorkoutSession.user_id == owner
        )
    )
    if session is None:
        raise HistoryReadError("history_entry_not_found", 404)
    try:
        reference = _unsigned(entry_ref, "ENTRY")
        context = reference["context"]
        if reference["session_id"] != session_id or context["owner_id"] != owner:
            raise ValueError
        if not db.scalar(
            select(WorkoutSession.id).where(
                WorkoutSession.id == session_id,
                *_filters(owner, context["window"], context["id_ceiling"]),
            )
        ):
            raise ValueError
    except (HistoryReadError, KeyError, TypeError, ValueError):
        raise HistoryReadError("history_entry_not_found", 404) from None
    descriptor = _descriptor(db, session)
    if reference.get("metadata_digest") != _digest(_metadata(session, descriptor)):
        raise HistoryReadError("READ_CHANGED", 409)
    if reference.get("exercise_links_digest") != _digest(_exercise_links(db, session, descriptor, context)):
        raise HistoryReadError("READ_CHANGED", 409)
    return session, descriptor, context


def _set_fact(row):
    mass = row.weight_kg
    finite = mass is None or math.isfinite(mass)
    result = {
        "set_id": row.id,
        "kind": row.kind,
        "set_index": row.set_index,
        "completed": row.completed,
        "reps": row.reps,
        "weight_kg": mass if finite else None,
        "raw_weight_repr": None if finite else str(mass),
        "completed_at": _iso(row.completed_at),
    }
    if row.reps is not None and (not isinstance(row.reps, int) or abs(row.reps) > 2**53 - 1):
        result["reps"], result["raw_reps_repr"] = None, str(row.reps)
    return result


def _legacy_exercises(db, session_id):
    exercises = list(
        db.scalars(
            select(SessionExercise)
            .where(SessionExercise.session_id == session_id)
            .order_by(SessionExercise.position, SessionExercise.id)
        )
    )
    sets = list(
        db.scalars(
            select(SetLog)
            .join(SessionExercise, SessionExercise.id == SetLog.session_exercise_id)
            .where(SessionExercise.session_id == session_id)
            .order_by(SetLog.session_exercise_id, SetLog.kind, SetLog.set_index, SetLog.id)
        )
    )
    grouped = {}
    for row in sets:
        grouped.setdefault(row.session_exercise_id, []).append(_set_fact(row))
    return [
        {
            "se_id": row.id,
            "position": row.position,
            "code": row.exercise_code_snapshot,
            "prescribed_name": row.exercise_name_snapshot,
            "executed_name": row.substituted_name
            if row.substituted_name is not None
            else row.exercise_name_snapshot,
            "substituted_name": row.substituted_name,
            "prescription": "UNKNOWN_NOT_CAPTURED",
            "equipment_context": "UNKNOWN_NOT_CAPTURED",
            "load_semantics": "UNKNOWN",
            "sets": grouped.get(row.id, []),
        }
        for row in exercises
    ]


def read_session_facts(db, owner_id, session_id, entry_ref, *, occurrence_ref=None):
    with db.no_autoflush:
        session, descriptor, context = _selected(db, owner_id, session_id, entry_ref)
        selected_se_id = None
        if occurrence_ref is not None:
            selected_se_id = _selected_occurrence(db, session, descriptor, context, occurrence_ref)
        if descriptor["execution_profile"] == "SCI_V3":
            raise HistoryReadError("execution_profile_required", 409)
        if descriptor["execution_profile"] != "LEGACY_V1":
            raise HistoryReadError("history_profile_unavailable", 503)
        result = {
            "contract_version": "training-session-facts/1.0.0",
            "owner_id": owner_id,
            "read_id": context["read_id"],
            "window": context["window"],
            "rows_read_at": _iso(datetime.now(UTC)),
            "execution_profile": "LEGACY_V1",
            "prescription": "UNKNOWN_NOT_CAPTURED",
            "timezone_basis": "DATABASE_UTC_CONVENTION",
            "session": {
                "session_id": session.id,
                "name": session.template_name_snapshot,
                "template_slug": session.template_slug_snapshot,
                "started_at": _iso(session.started_at),
                "ended_at": _iso(session.ended_at),
                "status": session.status,
                "excluded_from_stats": session.excluded_from_stats,
            },
            "cardio": {
                "duration_min": session.cardio_duration_min,
                "bpm_avg": session.cardio_bpm_avg,
                "machine_calories": session.cardio_machine_calories,
                "machine_type": session.cardio_machine_type,
            },
            "exercises": _legacy_exercises(db, session.id),
        }
        if selected_se_id is not None:
            result["selected_se_id"] = selected_se_id
        return result


def _read_context(token, owner):
    context = _unsigned(token, "READ_CONTEXT")
    try:
        if type(owner) is not int or owner <= 0 or context["owner_id"] != owner:
            raise ValueError
        _parameters(owner, context["window"]["period"], context["window"]["time_zone"], 1)
        _instant(context["window"]["until"])
        if type(context["id_ceiling"]) is not int or context["id_ceiling"] < 0:
            raise ValueError
        return context
    except (KeyError, TypeError, ValueError):
        raise HistoryReadError("invalid_history_context") from None


def _scan_after(row, session):
    return {
        "started_at": _iso(session.started_at),
        "session_id": session.id,
        "position": row.position,
        "se_id": row.id,
    }


def _source_filters(after):
    if after is None:
        return []
    try:
        at, sid, position, seid = (
            _instant(after["started_at"]),
            after["session_id"],
            after["position"],
            after["se_id"],
        )
        if any(type(v) is not int for v in (sid, position, seid)) or sid <= 0 or seid <= 0:
            raise ValueError
    except (KeyError, TypeError, ValueError):
        raise HistoryReadError("invalid_history_cursor") from None
    same_session = and_(WorkoutSession.started_at == at, WorkoutSession.id == sid)
    return [
        or_(
            WorkoutSession.started_at < at,
            and_(WorkoutSession.started_at == at, WorkoutSession.id < sid),
            and_(same_session, SessionExercise.position > position),
            and_(same_session, SessionExercise.position == position, SessionExercise.id > seid),
        )
    ]


def _scan_cursor(token, purpose, context, exercise_ref):
    if token is None:
        return None, None
    value = _unsigned(token, purpose)
    try:
        if value["context_digest"] != _digest(context) or value["exercise_ref"] != exercise_ref:
            raise ValueError
        _source_filters(value["source_after"])
        display = value["display_after"]
        if display is not None and not isinstance(display, str):
            raise ValueError
        return value["source_after"], display
    except (KeyError, TypeError, ValueError):
        raise HistoryReadError("invalid_history_cursor") from None


def _exercise_identity(db, row, session, cache):
    from app.services.exercise_identity import normalize, resolve_exercise
    from app.services.plan_v3.execution import is_scientific_session

    if is_scientific_session(session):
        key = ("SCI_DESCRIPTOR", session.id)
        if key not in cache:
            cache[key] = _descriptor(db, session)
        descriptor = cache[key]
        if descriptor["execution_profile"] != "SCI_V3":
            return None
        mapping = next((m for m in descriptor["mapping"] if m["se_id"] == row.id), None)
        return (
            {"namespace": "SCI_CANONICAL_EXERCISE", "id": mapping["canonical_exercise_id"]}
            if mapping
            else None
        )
    # Same exact alias resolver as canonical exercise history; never fuzzy names.
    name = row.substituted_name or row.exercise_name_snapshot or ""
    key = ("LEGACY_ALIAS", normalize(name))
    if key not in cache:
        found = resolve_exercise(db, name)
        cache[key] = (
            {"namespace": "LEGACY_EXERCISE", "id": found.slug} if found is not None else None
        )
    return cache[key]


def _exercise_reference(context, identity):
    return _sign(
        "EXERCISE",
        {"owner_id": context["owner_id"], "read_id": context["read_id"], "identity": identity},
    )


def _read_exercise_reference(token, context):
    value = _unsigned(token, "EXERCISE")
    try:
        identity = value["identity"]
        if value["owner_id"] != context["owner_id"] or value["read_id"] != context["read_id"]:
            raise ValueError
        if (
            identity["namespace"] not in {"LEGACY_EXERCISE", "SCI_CANONICAL_EXERCISE"}
            or not isinstance(identity["id"], str)
            or not identity["id"]
        ):
            raise ValueError
        return identity
    except (KeyError, TypeError, ValueError):
        raise HistoryReadError("invalid_history_exercise_reference") from None


def _occurrence_metadata(row, session, descriptor, context, identity):
    return {
        "context_digest": _digest(context),
        "metadata_digest": _digest(_metadata(session, descriptor)),
        "session_id": session.id,
        "se_id": row.id,
        "position": row.position,
        "identity": identity,
        "executed_name": row.substituted_name or row.exercise_name_snapshot,
    }


def _occurrence(db, row, session, context, identity):
    entry = _entry(db, session, context)
    return {
        "session_id": session.id,
        "se_id": row.id,
        "position": row.position,
        "started_at": _iso(session.started_at),
        "status": session.status,
        "excluded_from_stats": session.excluded_from_stats,
        "identity": identity,
        "name": row.substituted_name or row.exercise_name_snapshot,
        "entry_ref": entry["entry_ref"],
        "execution_profile": entry["execution_profile"],
        "descriptor": entry["descriptor"],
        "exercise_links": entry["exercise_links"],
        "comparison": "NON_COMPARABLE",
        "occurrence_ref": _sign(
            "OCCURRENCE", _occurrence_metadata(row, session, entry["descriptor"], context, identity)
        ),
    }


def _selected_occurrence(db, session, descriptor, context, token):
    try:
        ref = _unsigned(token, "OCCURRENCE")
        if ref["session_id"] != session.id or ref["context_digest"] != _digest(context):
            raise ValueError
        row = db.scalar(
            select(SessionExercise).where(
                SessionExercise.id == ref["se_id"], SessionExercise.session_id == session.id
            )
        )
        if row is None:
            raise ValueError
    except (HistoryReadError, KeyError, TypeError, ValueError):
        raise HistoryReadError("history_entry_not_found", 404) from None
    identity = _exercise_identity(db, row, session, {})
    if ref != _occurrence_metadata(row, session, descriptor, context, identity):
        raise HistoryReadError("READ_CHANGED", 409)
    return row.id


def _source_batch(db, context, after, count):
    return list(
        db.execute(
            select(WorkoutSession, SessionExercise)
            .join(SessionExercise, SessionExercise.session_id == WorkoutSession.id)
            .where(
                *_filters(context["owner_id"], context["window"], context["id_ceiling"]),
                *_source_filters(after),
            )
            .order_by(
                WorkoutSession.started_at.desc(),
                WorkoutSession.id.desc(),
                SessionExercise.position,
                SessionExercise.id,
            )
            .limit(count)
        )
    )


def _scan(db, owner, context, *, limit, cursor, exercise_ref=None, identity=None):
    purpose = "OCCURRENCES_CURSOR" if exercise_ref is not None else "EXERCISES_CURSOR"
    after, display = _scan_cursor(cursor, purpose, context, exercise_ref)
    found, seen, cache = [], set(), {}
    inspected, unresolved, exhausted = 0, 0, False
    while inspected < 1000 and len(found) < limit:
        count = min(200, 1000 - inspected)
        batch = _source_batch(db, context, after, count)
        for index, (session, row) in enumerate(batch):
            inspected += 1
            after = _scan_after(row, session)
            resolved = _exercise_identity(db, row, session, cache)
            if resolved is None:
                unresolved += 1
            elif exercise_ref is not None:
                if resolved == identity:
                    item = _occurrence(db, row, session, context, resolved)
                    found.append(item)
                    display = item["occurrence_ref"]
            else:
                key = _json(resolved)
                if key not in seen:
                    seen.add(key)
                    display = _exercise_reference(context, resolved)
                    found.append(
                        {
                            "exercise_ref": display,
                            "identity": resolved,
                            "name": row.substituted_name or row.exercise_name_snapshot,
                        }
                    )
            if len(found) == limit:
                exhausted = index == len(batch) - 1 and len(batch) < count
                break
        else:
            exhausted = len(batch) < count
        if exhausted:
            break
    next_cursor = (
        None
        if exhausted
        else _sign(
            purpose,
            {
                "context_digest": _digest(context),
                "source_after": after,
                "display_after": display,
                "exercise_ref": exercise_ref,
            },
        )
    )
    return {
        "contract_version": "training-exercise-occurrences/1.0.0"
        if exercise_ref is not None
        else "training-exercise-index/1.0.0",
        "owner_id": owner,
        "read_id": context["read_id"],
        "window": context["window"],
        "rows_read_at": _iso(datetime.now(UTC)),
        "state": "AVAILABLE" if found else "EMPTY" if exhausted else "SCANNING",
        "entries": found,
        "scan": "EXHAUSTED" if exhausted else "PARTIAL_SCAN",
        "source_inspected": inspected,
        "unresolved_count": unresolved,
        "coverage_complete": exhausted,
        "next_cursor": next_cursor,
    }


def read_exercises(db, owner_id, *, read_context, limit=50, cursor=None):
    context = _read_context(read_context, owner_id)
    _parameters(owner_id, context["window"]["period"], context["window"]["time_zone"], limit)
    with db.no_autoflush:
        return _scan(db, owner_id, context, limit=limit, cursor=cursor)


def read_occurrences(db, owner_id, exercise_ref, *, read_context, limit=50, cursor=None):
    context = _read_context(read_context, owner_id)
    _parameters(owner_id, context["window"]["period"], context["window"]["time_zone"], limit)
    identity = _read_exercise_reference(exercise_ref, context)
    with db.no_autoflush:
        return _scan(
            db,
            owner_id,
            context,
            limit=limit,
            cursor=cursor,
            exercise_ref=exercise_ref,
            identity=identity,
        )
