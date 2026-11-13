"""Bounded projections of canonical catalogue and owned programs, never a planner.

References confer source selection only. They grant no equipment or SCI permission.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.models.catalog import RepTarget, TemplateExercise, WorkoutTemplate
from app.models.user_program import (
    UserProgram,
    UserProgramExercise,
    UserProgramRepTarget,
    UserProgramSession,
)
from app.services.muscle_mapping import ZONE_LABELS
from app.services.template_zone_context import zones_for_names

VERSION = "owned-library/1.0.0"
SCHEMA = "catalog-program-source/1.0.0"
SECTIONS = ("programs", "core", "utility", "specialization")
MAX_CATALOGUE = 500
MAX_PROGRAMS = 200
MAX_INDEX_SLOTS = 5000
MAX_DETAIL_SESSIONS = 50
MAX_DETAIL_SLOTS = 200
MAX_TARGETS_PER_SLOT = 100
MAX_DETAIL_TARGETS = 10000
MAX_RESPONSE_BYTES = 2 * 1024 * 1024


class LibraryError(ValueError):
    def __init__(self, code: str, status: int = 422):
        super().__init__(code)
        self.code, self.status = code, status


@dataclass(frozen=True)
class LibraryContext:
    owner_id: int
    backend_identity: str
    signing_key: str
    epoch: int

    def __post_init__(self):
        if (
            type(self.owner_id) is not int
            or self.owner_id <= 0
            or self.owner_id > 2**53 - 1
            or type(self.epoch) is not int
            or self.epoch < 0
            or not isinstance(self.backend_identity, str)
            or not self.backend_identity.strip()
            or len(self.backend_identity) > 128
            or not isinstance(self.signing_key, str)
            or len(self.signing_key) < 32
        ):
            raise LibraryError("storage_unavailable", 503)

    def binding(self):
        return {
            "owner": self.owner_id,
            "backend": self.backend_identity,
            "epoch": self.epoch,
            "contract": VERSION,
            "schema": SCHEMA,
        }


def canonical_json(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )


def request_digest(value):
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def _sign(ctx, kind, payload):
    raw = canonical_json({"kind": kind, "binding": ctx.binding(), "value": payload}).encode()
    encoded = base64.urlsafe_b64encode(raw).decode().rstrip("=")
    mac = hmac.new(
        ctx.signing_key.encode(), ("library\0" + encoded).encode(), hashlib.sha256
    ).hexdigest()
    return encoded + "." + mac


def _unsigned(ctx, token, kind):
    try:
        if not isinstance(token, str) or len(token) > 4096:
            raise ValueError
        encoded, signature = token.split(".")
        wanted = hmac.new(
            ctx.signing_key.encode(), ("library\0" + encoded).encode(), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, wanted):
            raise ValueError
        raw = base64.b64decode(encoded + "=" * (-len(encoded) % 4), altchars=b"-_", validate=True)
        decoded = json.loads(raw)
        if (
            canonical_json(decoded).encode() != raw
            or set(decoded) != {"kind", "binding", "value"}
            or decoded["kind"] != kind
            or decoded["binding"] != ctx.binding()
        ):
            raise ValueError
        return decoded["value"]
    except (ValueError, TypeError, UnicodeError, AttributeError):
        raise LibraryError("foreign_or_missing", 404) from None


def _id(value):
    if type(value) is not int or not 0 < value <= 2**53 - 1:
        raise LibraryError("storage_unavailable", 503)
    return value


def _text(value, *, note=False, nullable=False):
    if value is None and nullable:
        return None
    if not isinstance(value, str):
        raise LibraryError("storage_unavailable", 503)
    if len(value) > (8192 if note else 1024):
        raise LibraryError("source_too_large", 413)
    return value


def _base(ctx):
    return {"contract_version": VERSION, "owner_id": ctx.owner_id}


def _snapshot(db):
    connection = db.connection()
    if connection.dialect.name == "sqlite":
        # pysqlite's legacy mode does not BEGIN on SELECT. A SQLAlchemy
        # transaction object alone therefore does not give a coherent read.
        if not connection.connection.driver_connection.in_transaction:
            connection.exec_driver_sql("BEGIN")
    elif connection.get_isolation_level() not in ("REPEATABLE READ", "SERIALIZABLE"):
        # Do not claim a consistent multi-query corpus under READ COMMITTED.
        # A non-SQLite target must explicitly supply and verify its isolation.
        raise LibraryError("storage_unavailable", 503)


def _ref(ctx, kind, ident, program_id=None):
    return _sign(ctx, "source", {"kind": kind, "id": _id(ident), "program_id": program_id})


def _source(ctx, token):
    value = _unsigned(ctx, token, "source")
    if (
        not isinstance(value, dict)
        or set(value) != {"kind", "id", "program_id"}
        or value["kind"] not in ("CATALOG_SESSION", "OWNED_PROGRAM", "OWNED_SESSION")
        or type(value["id"]) is not int
        or not 0 < value["id"] <= 2**53 - 1
        or (
            value["kind"] == "OWNED_SESSION"
            and (type(value["program_id"]) is not int or value["program_id"] <= 0)
        )
        or (value["kind"] != "OWNED_SESSION" and value["program_id"] is not None)
    ):
        raise LibraryError("foreign_or_missing", 404)
    return value


def _zones(db, names, seen):
    z = zones_for_names(db, names, {}, seen)
    return {"state": z.state, "codes": [x.code for x in z.zones]}


def _counts(sessions, slots, targets):
    return {
        "sessions": sessions,
        "exercise_slots": slots,
        "prescribed_sets": targets,
        "count_state": "KNOWN",
    }


def _limited(rows, cap):
    result = list(rows)
    if len(result) > cap:
        raise LibraryError("source_too_large", 413)
    return result


def _index_slots(db, parent_ids, *, personal=False):
    ex = UserProgramExercise if personal else TemplateExercise
    query = select(ex)
    if personal:
        query = query.join(UserProgramSession).where(
            UserProgramSession.user_program_id.in_(parent_ids)
        )
    else:
        query = query.where(ex.template_id.in_(parent_ids))
    rows = _limited(db.scalars(query.order_by(ex.id).limit(MAX_INDEX_SLOTS + 1)), MAX_INDEX_SLOTS)
    target = UserProgramRepTarget if personal else RepTarget
    foreign = target.user_program_exercise_id if personal else target.template_exercise_id
    counts = dict(
        db.execute(
            select(foreign, func.count())
            .where(foreign.in_([r.id for r in rows]))
            .where(target.is_warmup.is_(False) if personal else True)
            .group_by(foreign)
        ).all()
    )
    return rows, counts


def _corpus(db, ctx, section, zone):
    templates = []
    programs = []
    if section != "programs":
        sections = SECTIONS[1:] if section == "all" else (section,)
        templates = _limited(
            db.scalars(
                select(WorkoutTemplate)
                .where(WorkoutTemplate.catalog_section.in_(sections))
                .order_by(WorkoutTemplate.display_order, WorkoutTemplate.slug)
                .limit(MAX_CATALOGUE + 1)
            ),
            MAX_CATALOGUE,
        )
    if section in ("all", "programs"):
        programs = _limited(
            db.scalars(
                select(UserProgram)
                .where(
                    UserProgram.user_id == ctx.owner_id,
                    UserProgram.archived_at.is_(None),
                    UserProgram.status != "archived",
                )
                .order_by(UserProgram.updated_at.desc(), UserProgram.id.desc())
                .limit(MAX_PROGRAMS + 1)
            ),
            MAX_PROGRAMS,
        )
    catalog_slots, catalog_counts = _index_slots(db, [x.id for x in templates])
    personal_slots, personal_counts = _index_slots(db, [x.id for x in programs], personal=True)
    if len(catalog_slots) + len(personal_slots) > MAX_INDEX_SLOTS:
        raise LibraryError("source_too_large", 413)
    parents = dict(
        db.execute(
            select(UserProgramSession.id, UserProgramSession.user_program_id).where(
                UserProgramSession.id.in_([x.user_program_session_id for x in personal_slots])
            )
        ).all()
    )
    session_counts = dict(
        db.execute(
            select(UserProgramSession.user_program_id, func.count())
            .where(UserProgramSession.user_program_id.in_([p.id for p in programs]))
            .group_by(UserProgramSession.user_program_id)
        ).all()
    )
    seen, entries = {}, []
    for p in programs:
        if p.status not in ("draft", "validated", "published"):
            raise LibraryError("storage_unavailable", 503)
        slots = [x for x in personal_slots if parents[x.user_program_session_id] == p.id]
        entries.append(
            {
                "kind": "OWNED_PROGRAM",
                "source_ref": _ref(ctx, "OWNED_PROGRAM", p.id),
                "name": _text(p.title),
                "source_status": p.status.upper(),
                "section": "programs",
                "counts": _counts(
                    session_counts.get(p.id, 0),
                    len(slots),
                    sum(personal_counts.get(x.id, 0) for x in slots),
                ),
                "zones": _zones(db, [x.exercise_name for x in slots], seen),
            }
        )
    for group in SECTIONS[1:]:
        for t in templates:
            if t.catalog_section != group:
                continue
            slots = [x for x in catalog_slots if x.template_id == t.id]
            entries.append(
                {
                    "kind": "CATALOG_SESSION",
                    "source_ref": _ref(ctx, "CATALOG_SESSION", t.id),
                    "name": _text(t.name),
                    "source_status": "AVAILABLE",
                    "section": group,
                    "counts": _counts(
                        1, len(slots), sum(catalog_counts.get(x.id, 0) for x in slots)
                    ),
                    "zones": _zones(db, [x.name for x in slots], seen),
                }
            )
    return [x for x in entries if zone is None or zone in x["zones"]["codes"]]


def read_library(db, ctx, *, section="all", zone=None, limit=30, cursor=None):
    if (
        section not in ("all", *SECTIONS)
        or type(limit) is not int
        or not 1 <= limit <= 100
        or (zone is not None and (not isinstance(zone, str) or len(zone) > 100))
    ):
        raise LibraryError("invalid_request")
    _snapshot(db)
    applied = zone if zone in ZONE_LABELS else None
    entries = _corpus(db, ctx, section, applied)
    revision = request_digest(entries)
    params = {"section": section, "requested_zone": zone, "applied_zone": applied, "limit": limit}
    offset = 0
    if cursor:
        value = _unsigned(ctx, cursor, "cursor")
        if (
            not isinstance(value, dict)
            or set(value) != {*params, "revision", "offset"}
            or any(value[k] != v for k, v in params.items())
            or type(value["offset"]) is not int
            or not 0 <= value["offset"] <= len(entries)
        ):
            raise LibraryError("foreign_or_missing", 404)
        if value["revision"] != revision:
            raise LibraryError("source_changed", 409)
        offset = value["offset"]
    end = min(offset + limit, len(entries))
    next_cursor = (
        _sign(ctx, "cursor", {**params, "revision": revision, "offset": end})
        if end < len(entries)
        else None
    )
    page = {
        **_base(ctx),
        "read_revision": revision,
        **{k: v for k, v in params.items() if k != "limit"},
        "groups": [s for s in SECTIONS if section in ("all", s)],
        "entries": entries[offset:end],
        "next_cursor": next_cursor,
        "collection_state": "PARTIAL" if next_cursor else "COMPLETE",
    }
    _response_budget(page)
    return page


def _root(db, ctx, source):
    kind, ident = source["kind"], source["id"]
    if kind == "CATALOG_SESSION":
        root = db.scalar(
            select(WorkoutTemplate)
            .where(WorkoutTemplate.id == ident, WorkoutTemplate.catalog_section.in_(SECTIONS[1:]))
            .execution_options(populate_existing=True)
        )
    else:
        pid = source["program_id"] if kind == "OWNED_SESSION" else ident
        root = db.scalar(
            select(UserProgram)
            .where(
                UserProgram.id == pid,
                UserProgram.user_id == ctx.owner_id,
                UserProgram.archived_at.is_(None),
                UserProgram.status != "archived",
            )
            .execution_options(populate_existing=True)
        )
    if root is None:
        raise LibraryError("foreign_or_missing", 404)
    return root


def _exercises(db, parent_ids, *, personal):
    ex = UserProgramExercise if personal else TemplateExercise
    parent = ex.user_program_session_id if personal else ex.template_id
    rows = _limited(
        db.scalars(
            select(ex)
            .where(parent.in_(parent_ids))
            .order_by(parent, ex.position, ex.id)
            .limit(MAX_DETAIL_SLOTS + 1)
            .execution_options(populate_existing=True)
        ),
        MAX_DETAIL_SLOTS,
    )
    target = UserProgramRepTarget if personal else RepTarget
    foreign = target.user_program_exercise_id if personal else target.template_exercise_id
    counts = list(
        db.execute(
            select(foreign, func.count()).where(foreign.in_([x.id for x in rows])).group_by(foreign)
        )
    )
    if sum(n for _, n in counts) > MAX_DETAIL_TARGETS or any(
        n > MAX_TARGETS_PER_SLOT for _, n in counts
    ):
        raise LibraryError("source_too_large", 413)
    targets = list(
        db.scalars(
            select(target)
            .where(foreign.in_([x.id for x in rows]))
            .order_by(foreign, target.set_index, target.id)
            .limit(MAX_DETAIL_TARGETS + 1)
            .execution_options(populate_existing=True)
        )
    )
    _limited(targets, MAX_DETAIL_TARGETS)
    result = {}
    for row in rows:
        own_targets = [r for r in targets if getattr(r, foreign.key) == row.id]
        rts = []
        for t in own_targets:
            for val in (t.set_index, t.min_reps, t.max_reps):
                _id(val)
            if t.max_reps < t.min_reps:
                raise LibraryError("storage_unavailable", 503)
            rts.append(
                {
                    "set_index": t.set_index,
                    "min_reps": t.min_reps,
                    "max_reps": t.max_reps,
                    "technique": _text(t.technique, nullable=True),
                    "is_warmup": bool(getattr(t, "is_warmup", False)),
                }
            )
        data = {
            "id": _id(row.id),
            "position": _id(row.position),
            "name": _text(row.exercise_name if personal else row.name),
            "code": None if personal else _text(row.code),
            "set_scheme": _text(row.set_scheme),
            "notes": _text(row.notes, note=True, nullable=True),
            "machine_slug": None if personal else _text(row.machine_slug, nullable=True),
            "machine_family": None if personal else _text(row.machine_family, nullable=True),
            "equipment_context": "UNKNOWN",
            "rep_targets": rts,
        }
        result.setdefault(getattr(row, parent.key), []).append(data)
    if len(canonical_json(result).encode()) > 1024 * 1024:
        raise LibraryError("source_too_large", 413)
    return result


def _support(kind, exercises):
    supported = (
        kind == "strength"
        and bool(exercises)
        and all(any(not r["is_warmup"] for r in ex["rep_targets"]) for ex in exercises)
    )
    return {
        "state": "SUPPORTED" if supported else "UNSUPPORTED",
        "reason": None if supported else "NATIVE_EXECUTION_UNSUPPORTED",
    }


def _selection(db, ctx, source, kind, exercises, launchable):
    support = _support(kind, exercises)
    result = {
        "domain_launchable": bool(launchable),
        "native_support": support,
        "selection_ref": None,
    }
    if launchable and support["state"] == "SUPPORTED":
        payload = _start_payload(db, ctx, source)
        result["selection_ref"] = _sign(
            ctx, "selection", {"source": source, "fingerprint": request_digest(payload)}
        )
    return result


def _start_payload(db, ctx, source):
    root = _root(db, ctx, source)
    if source["kind"] == "CATALOG_SESSION":
        template_id = root.id
        program = None
    elif source["kind"] == "OWNED_SESSION":
        session = db.scalar(
            select(UserProgramSession)
            .where(
                UserProgramSession.id == source["id"], UserProgramSession.user_program_id == root.id
            )
            .execution_options(populate_existing=True)
        )
        if session is None or root.status != "published" or not session.published_template_id:
            raise LibraryError("stale_selection", 409)
        template_id = session.published_template_id
        program = {
            "id": root.id,
            "version": root.current_version,
            "session_id": session.id,
            "slug": session.template_slug_snapshot,
        }
    else:
        raise LibraryError("stale_selection", 409)
    template = db.scalar(
        select(WorkoutTemplate)
        .where(WorkoutTemplate.id == template_id)
        .execution_options(populate_existing=True)
    )
    if template is None or (
        program is not None
        and (template.catalog_section != "user" or template.slug != program["slug"])
    ):
        raise LibraryError("stale_selection", 409)
    exercises = _exercises(db, [template_id], personal=False).get(template_id, [])
    return {
        "id": template.id,
        "slug": _text(template.slug),
        "name": _text(template.name),
        "kind": _text(template.kind),
        "focus": _text(template.focus),
        "cardio_note": _text(template.cardio_note, note=True, nullable=True),
        "program": program,
        "exercises": exercises,
    }


def read_library_item(db, ctx, source_ref):
    _snapshot(db)
    source = _source(ctx, source_ref)
    root = _root(db, ctx, source)
    personal = source["kind"] != "CATALOG_SESSION"
    if personal:
        query = select(UserProgramSession).where(UserProgramSession.user_program_id == root.id)
        if source["kind"] == "OWNED_SESSION":
            query = query.where(UserProgramSession.id == source["id"])
        sessions = _limited(
            db.scalars(
                query.order_by(UserProgramSession.position, UserProgramSession.id)
                .limit(MAX_DETAIL_SESSIONS + 1)
                .execution_options(populate_existing=True)
            ),
            MAX_DETAIL_SESSIONS,
        )
        if source["kind"] == "OWNED_SESSION" and not sessions:
            raise LibraryError("foreign_or_missing", 404)
        if root.status not in ("draft", "validated", "published"):
            raise LibraryError("storage_unavailable", 503)
    else:
        sessions = [root]
    by_parent = _exercises(db, [x.id for x in sessions], personal=personal)
    composition = []
    for row in sessions:
        s = {
            "kind": "OWNED_SESSION" if personal else "CATALOG_SESSION",
            "id": row.id,
            "program_id": root.id if personal else None,
        }
        exercises = by_parent.get(row.id, [])
        launchable = bool(
            not personal
            or (
                root.status == "published"
                and row.published_template_id
                and row.template_slug_snapshot
            )
        )
        ref = _ref(ctx, s["kind"], row.id, s["program_id"])
        selection = _selection(db, ctx, s, row.kind, exercises, launchable)
        composition.append(
            {
                "source_ref": ref,
                "name": _text(row.name),
                "kind": _text(row.kind),
                "notes": _text(getattr(row, "notes", None), note=True, nullable=True),
                "exercises": exercises,
                "selection": selection,
            }
        )
    descriptor = {
        **source,
        "name": _text(root.title if source["kind"] == "OWNED_PROGRAM" else sessions[0].name),
        "status": root.status.upper() if personal else "AVAILABLE",
        "version": root.current_version if personal else None,
    }
    selection = None if source["kind"] == "OWNED_PROGRAM" else composition[0]["selection"]
    detail = {
        **_base(ctx),
        "source": descriptor,
        "composition": composition,
        "selection": selection,
        "limitations": ["SOURCE_CONTEXT_UNKNOWN"],
    }
    detail["read_revision"] = request_digest(detail)
    _response_budget(detail)
    return detail


def resolve_library_selection(db, ctx, selection_ref):
    value = _unsigned(ctx, selection_ref, "selection")
    if not isinstance(value, dict) or set(value) != {"source", "fingerprint"}:
        raise LibraryError("foreign_or_missing", 404)
    # Reuse strict source validation, not unvalidated signed JSON as a query.
    source = _source(ctx, _sign(ctx, "source", value["source"]))
    try:
        payload = _start_payload(db, ctx, source)
    except LibraryError as error:
        if error.status == 404:
            raise LibraryError("stale_selection", 409) from None
        raise
    if request_digest(payload) != value["fingerprint"]:
        raise LibraryError("stale_selection", 409)
    if _support(payload["kind"], payload["exercises"])["state"] != "SUPPORTED":
        raise LibraryError("start_blocked", 409)
    # Bounds above precede ORM hydration; the real domain builder consumes this tree.
    return db.scalar(
        select(WorkoutTemplate)
        .where(WorkoutTemplate.id == payload["id"])
        .options(selectinload(WorkoutTemplate.exercises).selectinload(TemplateExercise.rep_targets))
        .execution_options(populate_existing=True)
    )


def _response_budget(value):
    if len(canonical_json(value).encode()) > MAX_RESPONSE_BYTES:
        raise LibraryError("source_too_large", 413)
