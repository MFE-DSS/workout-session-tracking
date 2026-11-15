"""Bounded owned builder projections, exact identity intersection and cursors."""

import base64
import hashlib
import hmac
import json

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.models.exercise import Exercise, ExerciseAlias
from app.services.program_builder_commands import (
    MAX_BYTES,
    VERSION,
    ProgramBuilderError,
    collection_source_rows,
    exercise_source,
    program_source_digest,
    slot_digest,
)
from app.services.user_program_exercise_catalog import _EKB_PATH, picker_options

MAX_SOURCE_ROWS = 1000


def picker(db):
    if db.scalar(select(func.count()).select_from(ExerciseAlias)) > MAX_SOURCE_ROWS:
        raise ProgramBuilderError("source_too_large", 413)
    rows = list(
        db.scalars(
            select(Exercise)
            .options(selectinload(Exercise.aliases))
            .order_by(Exercise.slug)
            .limit(MAX_SOURCE_ROWS + 1)
        )
    )
    if len(rows) > MAX_SOURCE_ROWS:
        raise ProgramBuilderError("source_too_large", 413)
    canonical = {p["name"]: p for p in picker_options()}
    with _EKB_PATH.open(encoding="utf-8") as f:
        ekb = json.load(f)
    candidates = {}
    for row in rows:
        names = {row.name, *[a.alias for a in row.aliases]}
        resolved = {
            name if name in canonical else ekb.get("_aliases", {}).get(name) for name in names
        }
        resolved = {name for name in resolved if name in canonical}
        if len(resolved) == 1:
            name = next(iter(resolved))
            candidates.setdefault(name, []).append(row)
    out = []
    for name, identities in candidates.items():
        if len(identities) != 1:
            continue
        row = identities[0]
        meta = canonical[name]
        out.append(
            {
                "slug": row.slug,
                "name": name,
                "ekb_version": ekb["_version"],
                "equipment_family": meta["equipment_family"],
                "movement_pattern": meta["movement_pattern"],
            }
        )
    return sorted(out, key=lambda x: x["slug"])


def resolve_selection(db, selection):
    matches = [
        p for p in picker(db) if all(p[k] == selection[k] for k in ("slug", "name", "ekb_version"))
    ]
    if len(matches) != 1:
        raise ProgramBuilderError("stale_selection", 409)
    return {k: matches[0][k] for k in ("slug", "name", "ekb_version")}


def project_program(db, program):
    options = {p["name"]: p for p in picker(db)}
    sessions = []
    for s in program.sessions:
        exercises = []
        for e in s.exercises:
            p = options.get(e.exercise_name)
            identity = {
                "state": "RESOLVED_CURRENT_NAME" if p else "UNRESOLVED",
                "slug": p["slug"] if p else None,
                "name": p["name"] if p else None,
                "ekb_version": p["ekb_version"] if p else None,
            }
            source = exercise_source(e)
            source["rep_targets"] = [
                {
                    "set_index": rt.set_index,
                    **{
                        k: getattr(rt, k)
                        for k in ("min_reps", "max_reps", "technique", "is_warmup")
                    },
                }
                for rt in e.rep_targets
            ]
            exercises.append(
                {"slot_id": e.id, "slot_digest": slot_digest(e), **source, "identity": identity}
            )
        sessions.append(
            {
                **{
                    k: getattr(s, k)
                    for k in (
                        "position",
                        "name",
                        "kind",
                        "focus",
                        "duration_target_minutes",
                        "notes",
                    )
                },
                "exercises": exercises,
            }
        )
    result = {
        "id": program.id,
        "title": program.title,
        "slug_base": program.slug_base,
        "status": "archived" if program.archived_at else program.status,
        "version": program.current_version,
        "source_digest": program_source_digest(program),
        "sessions": sessions,
        "publication_ids": [
            s.published_template_id for s in program.sessions if s.published_template_id is not None
        ],
    }
    bounded(result)
    return result


def bounded(value):
    if len(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()) > MAX_BYTES:
        raise ProgramBuilderError("source_too_large", 413)
    return value


def _cursor(runtime, binding, watermark, offset):
    payload = json.dumps(
        {"binding": binding, "watermark": watermark, "offset": offset},
        sort_keys=True,
        separators=(",", ":"),
    )
    signed = (
        payload
        + "."
        + hmac.new(runtime.signing_key.encode(), payload.encode(), hashlib.sha256).hexdigest()
    )
    return base64.urlsafe_b64encode(signed.encode()).decode()


def _read_cursor(runtime, binding, watermark, cursor):
    try:
        raw = base64.urlsafe_b64decode(cursor.encode()).decode()
        payload, signature = raw.rsplit(".", 1)
        expected = hmac.new(
            runtime.signing_key.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError()
        data = json.loads(payload)
        if (
            data["binding"] != binding
            or type(data["offset"]) is not int
            or not 0 <= data["offset"] <= MAX_SOURCE_ROWS
        ):
            raise ValueError()
    except (ValueError, KeyError, TypeError, UnicodeError):
        raise ProgramBuilderError("invalid_cursor", 422) from None
    if data["watermark"] != watermark:
        raise ProgramBuilderError("stale_cursor", 409)
    return data["offset"]


def page(db, owner, runtime, scope, limit, cursor):
    if not runtime.backend_identity or not runtime.signing_key:
        raise ProgramBuilderError("configuration_unavailable", 503)
    binding = f"{owner}:{runtime.backend_identity}:{scope}"
    if scope == "exercises":
        items = picker(db)
    else:
        items = collection_source_rows(db, owner)
    watermark = hashlib.sha256(
        json.dumps(items, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()
    offset = _read_cursor(runtime, binding, watermark, cursor) if cursor else 0
    selected = items[offset : offset + limit]
    next_cursor = (
        _cursor(runtime, binding, watermark, offset + limit)
        if len(items) > offset + limit
        else None
    )
    return bounded(
        {
            "contract_version": VERSION,
            "owner_id": owner,
            "items": selected,
            "next_cursor": next_cursor,
        }
    )
