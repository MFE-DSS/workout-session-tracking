"""Atomic owner/CAS commands and exact historical receipts for MOB07."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime

from sqlalchemy import select

from app.models.program_builder_operations import ProgramBuilderOperation
from app.services import user_program_drafts as drafts
from app.services.program_builder_transactions import owner_transaction

VERSION = "program-builder/1.0.0"
MAX_BYTES = 131072
HEX = re.compile(r"[0-9a-f]{64}\Z")
OPERATIONS = {"CREATE", "RENAME", "SAVE_TREE", "VALIDATE", "PUBLISH", "NEW_CYCLE", "ARCHIVE"}


class ProgramBuilderError(ValueError):
    def __init__(self, code, status=422):
        self.code, self.status = code, status
        super().__init__(code)


def _exact(value, keys):
    if type(value) is not dict or set(value) != set(keys):
        raise ProgramBuilderError("invalid_request")


def _int(value, low=1, high=9007199254740991):
    if type(value) is not int or not low <= value <= high:
        raise ProgramBuilderError("invalid_request")
    return value


def _text(value, maximum, *, empty=False, nullable=False):
    if value is None and nullable:
        return value
    if type(value) is not str or len(value) > maximum or (not empty and not value.strip()):
        raise ProgramBuilderError("invalid_request")
    return value


def _json(value):
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
        )
    except (TypeError, ValueError, RecursionError):
        raise ProgramBuilderError("invalid_request") from None


def _strict_numbers(value):
    if type(value) is float:
        raise ProgramBuilderError("invalid_request")
    if type(value) is dict:
        for v in value.values():
            _strict_numbers(v)
    elif type(value) is list:
        for v in value:
            _strict_numbers(v)


def canonical_command(body):
    _exact(
        body,
        [
            "contract_version",
            "command_id",
            "operation",
            "program_id",
            "expected_source_digest",
            "payload",
        ],
    )
    if body["contract_version"] != VERSION:
        raise ProgramBuilderError("unsupported_contract", 406)
    key = body["command_id"]
    if type(key) is not str or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", key):
        raise ProgramBuilderError("invalid_request")
    op = body["operation"]
    if type(op) is not str or op not in OPERATIONS:
        raise ProgramBuilderError("invalid_request")
    if op == "CREATE":
        if body["program_id"] is not None or body["expected_source_digest"] is not None:
            raise ProgramBuilderError("invalid_request")
    else:
        _int(body["program_id"])
        if type(body["expected_source_digest"]) is not str or not HEX.fullmatch(
            body["expected_source_digest"]
        ):
            raise ProgramBuilderError("invalid_request")
    payload = body["payload"]
    _exact(
        payload,
        ["title"] if op in {"CREATE", "RENAME"} else ["sessions"] if op == "SAVE_TREE" else [],
    )
    if op in {"CREATE", "RENAME"}:
        _text(payload["title"], 128)
    if op == "SAVE_TREE":
        _validate_tree_shape(payload["sessions"])
    _strict_numbers(body)
    try:
        encoded = _json(body).encode("utf-8")
    except UnicodeError:
        raise ProgramBuilderError("invalid_request") from None
    if len(encoded) > MAX_BYTES:
        raise ProgramBuilderError("source_too_large", 413)
    return json.loads(encoded)


def command_digest(body):
    return hashlib.sha256(_json(canonical_command(body)).encode("utf-8")).hexdigest()


def _validate_tree_shape(sessions):
    if type(sessions) is not list or len(sessions) > 7:
        raise ProgramBuilderError("invalid_request")
    for si, s in enumerate(sessions, 1):
        _exact(
            s,
            ["position", "name", "kind", "focus", "duration_target_minutes", "notes", "exercises"],
        )
        if _int(s["position"]) != si:
            raise ProgramBuilderError("invalid_request")
        _text(s["name"], 128)
        _text(s["focus"], 128, empty=True)
        _text(s["notes"], 8192, nullable=True, empty=True)
        if s["kind"] not in ("strength", "cardio"):
            raise ProgramBuilderError("invalid_request")
        if s["duration_target_minutes"] is not None:
            _int(s["duration_target_minutes"], -9007199254740991, 9007199254740991)
        if type(s["exercises"]) is not list or len(s["exercises"]) > 10:
            raise ProgramBuilderError("invalid_request")
        for ei, e in enumerate(s["exercises"], 1):
            _validate_exercise_shape(e, ei)


def _validate_exercise_shape(e, ei):
    _exact(e, ["position", "selection", "keep", "rep_targets", "notes"])
    if _int(e["position"]) != ei:
        raise ProgramBuilderError("invalid_request")
    if e["keep"] is not None:
        _exact(e["keep"], ["slot_id", "slot_digest"])
        _int(e["keep"]["slot_id"])
        if type(e["keep"]["slot_digest"]) is not str or not HEX.fullmatch(e["keep"]["slot_digest"]):
            raise ProgramBuilderError("invalid_request")
        if e["selection"] is not None or e["rep_targets"] is not None or e["notes"] is not None:
            raise ProgramBuilderError("invalid_request")
    else:
        _exact(e["selection"], ["slug", "name", "ekb_version"])
        for k, n in [("slug", 96), ("name", 255), ("ekb_version", 128)]:
            _text(e["selection"][k], n)
        _text(e["notes"], 8192, nullable=True, empty=True)
        targets = e["rep_targets"]
        if type(targets) is not list or not 1 <= len(targets) <= 6:
            raise ProgramBuilderError("invalid_request")
        for rt in targets:
            _exact(rt, ["min_reps", "max_reps", "technique", "is_warmup"])
            _int(rt["min_reps"], 1, 50)
            _int(rt["max_reps"], 1, 50)
            if rt["min_reps"] > rt["max_reps"] or type(rt["is_warmup"]) is not bool:
                raise ProgramBuilderError("invalid_request")
            _text(rt["technique"], 8, nullable=True, empty=True)


def exercise_source(e):
    return {
        **{
            k: getattr(e, k)
            for k in (
                "position",
                "exercise_name",
                "set_scheme",
                "variant_key",
                "variant_group",
                "equipment_family",
                "movement_pattern",
                "notes",
                "source_reason",
            )
        },
        "rep_targets": [
            {
                k: getattr(rt, k)
                for k in ("set_index", "min_reps", "max_reps", "technique", "is_warmup")
            }
            for rt in e.rep_targets
        ],
    }


def slot_digest(e):
    # Position may move; every historical source field is otherwise frozen.
    source = exercise_source(e)
    source.pop("position")
    return hashlib.sha256(_json({"slot_id": e.id, "source": source}).encode()).hexdigest()


def source_projection(program):
    return {
        "id": program.id,
        "title": program.title,
        "slug_base": program.slug_base,
        "status": program.status,
        "version": program.current_version,
        "archived_at": program.archived_at.isoformat() if program.archived_at else None,
        "wizard_answers": getattr(program, "wizard_answers", None),
        "sessions": [
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
                        "published_template_id",
                        "template_slug_snapshot",
                    )
                },
                "exercises": [{"slot_id": e.id, **exercise_source(e)} for e in s.exercises],
            }
            for s in program.sessions
        ],
    }


def program_source_digest(program):
    return hashlib.sha256(_json(source_projection(program)).encode()).hexdigest()


def load_program(db, owner, program_id):
    from app.services.program_builder_bounds import check_source_budget

    check_source_budget(db, owner, [program_id])
    program = drafts.get_draft(db, owner, program_id)
    if program is None:
        raise ProgramBuilderError("foreign_or_missing", 404)
    return program


def read_program(db, owner, program_id):
    from app.services.mobile_program_builder import project_program

    return project_program(db, load_program(db, owner, program_id))


def read_receipt(db, owner, key):
    row = db.scalar(
        select(ProgramBuilderOperation).where(
            ProgramBuilderOperation.user_id == owner, ProgramBuilderOperation.command_id == key
        )
    )
    return json.loads(row.result_json) if row else None


def collection_source_rows(db, owner):
    """Keep only summaries, validating and releasing one source tree at a time."""
    from app.services.program_builder_bounds import bounded_program_ids

    rows = []
    for program_id in bounded_program_ids(db, owner):
        program = load_program(db, owner, program_id)
        rows.append(
            {
                "id": program.id,
                "title": program.title,
                "status": "archived" if program.archived_at else program.status,
                "version": program.current_version,
                "source_digest": program_source_digest(program),
            }
        )
        # The collection owns only scalar summaries. Do not retain every
        # descendant graph (including archived programmes) in the identity map.
        db.expire(program, ["sessions", "quality_reviews"])
    return rows


def collection_digest(db, owner):
    rows = collection_source_rows(db, owner)
    return hashlib.sha256(
        _json([(row["id"], row["source_digest"]) for row in rows]).encode()
    ).hexdigest()


def web_mutation(db, owner, *, program_id, expected_source_digest, callback):
    with owner_transaction(db, owner):
        program = load_program(db, owner, program_id) if program_id is not None else None
        if not expected_source_digest:
            raise ProgramBuilderError("precondition_required", 428)
        current = program_source_digest(program) if program else collection_digest(db, owner)
        if current != expected_source_digest:
            raise ProgramBuilderError("stale_source", 409)
        return callback(program)


def _native_tree(db, program, sessions):
    from app.services.mobile_program_builder import resolve_selection

    slots = {e.id: e for s in program.sessions for e in s.exercises}
    used = set()
    selections = []
    tree = []
    for s in sessions:
        out = {k: v for k, v in s.items() if k != "exercises"}
        out["exercises"] = []
        for e in s["exercises"]:
            if e["keep"]:
                keep = e["keep"]
                original = slots.get(keep["slot_id"])
                if (
                    original is None
                    or original.id in used
                    or slot_digest(original) != keep["slot_digest"]
                ):
                    raise ProgramBuilderError("stale_slot", 409)
                used.add(original.id)
                exercise = exercise_source(original)
                exercise["position"] = e["position"]
            else:
                selected = resolve_selection(db, e["selection"])
                targets = e["rep_targets"]
                ranges = [f"{rt['min_reps']}-{rt['max_reps']}" for rt in targets]
                scheme = (
                    f"{len(targets)}x {ranges[0]}" if len(set(ranges)) == 1 else " / ".join(ranges)
                )
                from app.services.user_program_exercise_catalog import enrich

                exercise = {
                    **enrich(selected["name"]),
                    "position": e["position"],
                    "exercise_name": selected["name"],
                    "set_scheme": scheme,
                    "source_reason": "manual",
                    "notes": e["notes"],
                    "rep_targets": targets,
                }
                selections.append(selected)
            out["exercises"].append(exercise)
        tree.append(out)
    return tree, selections


def apply_command(db, owner, body, *, auth_proof, controlled):
    from app.services.user_program_publish import PublishError
    from app.services.user_program_versioning import VersioningError

    body = canonical_command(body)
    digest = command_digest(body)
    try:
        with owner_transaction(db, owner, auth_proof=auth_proof):
            replay = read_receipt(db, owner, body["command_id"])
            if replay:
                if replay["request_sha256"] != digest:
                    raise ProgramBuilderError("command_conflict", 409)
                return replay
            if not controlled:
                raise ProgramBuilderError("acquisition_unavailable", 403)
            op = body["operation"]
            payload = body["payload"]
            selections = []
            if op == "CREATE":
                from app.routers.user_programs import _slugify

                program = drafts.create_draft(
                    db, owner, payload["title"], _slugify(payload["title"]), commit=False
                )
            else:
                program = load_program(db, owner, body["program_id"])
                if program_source_digest(program) != body["expected_source_digest"]:
                    raise ProgramBuilderError("stale_source", 409)
                if op == "RENAME":
                    drafts.rename_draft(db, owner, program.id, payload["title"], commit=False)
                elif op == "SAVE_TREE":
                    tree, selections = _native_tree(db, program, payload["sessions"])
                    drafts.replace_draft_tree(db, owner, program.id, tree, commit=False)
                elif op == "VALIDATE":
                    drafts.validate_draft(db, owner, program.id, commit=False)
                elif op == "ARCHIVE":
                    drafts.archive_draft(db, owner, program.id, commit=False)
                elif op == "PUBLISH":
                    from app.services.user_program_publish import publish_user_program

                    publish_user_program(db, owner, program.id, commit=False)
                elif op == "NEW_CYCLE":
                    from app.services.user_program_versioning import start_new_edit_cycle

                    start_new_edit_cycle(db, owner, program.id, commit=False)
            db.flush()
            program = load_program(db, owner, program.id)
            if selections:
                # Match by the explicit selected positions, avoiding any claim of
                # provenance for preserved slots with currently resolvable names.
                selections = [
                    {"slot_id": e.id, **selected}
                    for s, wire in zip(program.sessions, payload["sessions"], strict=True)
                    for e, w in zip(s.exercises, wire["exercises"], strict=True)
                    if w["selection"] is not None
                    for selected in [w["selection"]]
                ]
            receipt = {
                "contract_version": VERSION,
                "owner_id": owner,
                "command_id": body["command_id"],
                "request_sha256": digest,
                "operation": op,
                "program_id": program.id,
                "resulting_source_digest": program_source_digest(program),
                "resulting_version": program.current_version,
                "publication_ids": [
                    s.published_template_id
                    for s in program.sessions
                    if s.published_template_id is not None
                ],
                "selections": selections,
                "recorded_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            }
            db.add(
                ProgramBuilderOperation(
                    user_id=owner,
                    command_id=body["command_id"],
                    operation=op,
                    request_sha256=digest,
                    program_id=program.id,
                    source_digest_before=body["expected_source_digest"],
                    source_digest_after=receipt["resulting_source_digest"],
                    result_version=program.current_version,
                    result_json=_json(receipt),
                )
            )
            return receipt
    except ProgramBuilderError:
        raise
    except (drafts.UserProgramDraftError, PublishError, VersioningError) as error:
        raise ProgramBuilderError("domain_refused", 409) from error
