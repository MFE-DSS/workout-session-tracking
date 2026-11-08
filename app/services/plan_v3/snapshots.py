"""Owned append-only declarations and captures; no client-authored Blueprint."""

from __future__ import annotations

import hashlib
import hmac
import json
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.first_plan_runtime import BlueprintSourceEvent, OwnedBlueprintSnapshot
from app.services.plan_v3.packaging import execute_science
from app.services.plan_v3.transactions import RuntimeFailure, guard_owner, schema_available

DECLARABLE = frozenset(
    {
        "objective",
        "population_scope",
        "sessions_per_week",
        "session_budgets_minutes",
        "limitations",
        "experience",
        "declared_priorities",
        "excluded_exercise_ids",
    }
)


def canonical(value) -> str:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False
    )


def digest(value) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def subject_ref(owner: int) -> str:
    return (
        "subject:"
        + hmac.new(
            get_settings().app_secret_key.encode(),
            f"plan-v3-subject:{owner}".encode(),
            hashlib.sha256,
        ).hexdigest()
    )


def events(db: Session, owner_id: int):
    return list(
        db.scalars(
            select(BlueprintSourceEvent)
            .where(BlueprintSourceEvent.owner_id == owner_id)
            .order_by(BlueprintSourceEvent.source_revision)
        )
    )


def current_revision(db: Session, owner_id: int) -> int:
    return (
        db.scalar(
            select(func.max(BlueprintSourceEvent.source_revision)).where(
                BlueprintSourceEvent.owner_id == owner_id
            )
        )
        or 0
    )


def check_revision(db: Session, owner: int, expected: int):
    if type(expected) is not int or expected < 0:
        raise ValueError("invalid revision")
    if current_revision(db, owner) != expected:
        raise RuntimeFailure("source_revision_changed")


def replay(db: Session, owner: int, request_id: str, body_digest: str):
    row = db.scalar(
        select(BlueprintSourceEvent).where(
            BlueprintSourceEvent.owner_id == owner, BlueprintSourceEvent.request_id == request_id
        )
    )
    if row is not None and row.body_digest != body_digest:
        raise RuntimeFailure("idempotency_mismatch")
    return row


def append_event(
    db: Session, owner: int, request_id: str, kind: str, payload, body_digest: str
) -> BlueprintSourceEvent:
    row = BlueprintSourceEvent(
        id=str(uuid4()),
        owner_id=owner,
        request_id=request_id,
        source_revision=current_revision(db, owner) + 1,
        body_digest=body_digest,
        kind=kind,
        payload_json=canonical(payload),
        recorded_at=datetime.now(UTC),
    )
    db.add(row)
    db.flush()
    return row


def unknown():
    return {
        "state": "UNKNOWN",
        "value": None,
        "conflicts": [],
        "provenance": {
            "origin": "UNKNOWN",
            "acquisition": "UNKNOWN",
            "source_ref": None,
            "recorded_at": None,
            "measured_at": None,
        },
    }


def blank_blueprint(snapshot_id: str):
    FACT_FIELDS = DECLARABLE | {"weight_kg", "height_cm", "legacy_weight_kg"}

    return {
        "contract_version": "body-training-blueprint/1.0.0",
        "snapshot_id": snapshot_id,
        **{name: unknown() for name in FACT_FIELDS},
        "observations": [],
        "environment": {
            "context_ref": "environment:unknown",
            "description": unknown(),
            "equipment_items": unknown(),
            "exercise_confirmations": [],
        },
    }


def blueprint_from_events(rows, snapshot_id: str):
    bp = blank_blueprint(snapshot_id)
    for row in rows:
        data = json.loads(row.payload_json)
        if row.kind == "DECLARATIONS":
            bp.update(data["facts"])
        elif row.kind == "SOURCE_INVALIDATED":
            for field in data["fields"]:
                if field == "environment":
                    bp[field] = blank_blueprint(snapshot_id)["environment"]
                elif field in bp:
                    bp[field] = unknown()
    return bp


def declare(db: Session, owner_id: int, *, request_id: str, expected_revision: int, fields: dict):
    from app.services.training_preferences import apply_training_preferences_in_transaction

    if not set(fields) <= DECLARABLE:
        raise ValueError("unsupported declaration")
    body_digest = digest(
        {"operation": "DECLARE", "expected_revision": expected_revision, "fields": fields}
    )
    guard_owner(db, owner_id)
    previous = replay(db, owner_id, request_id, body_digest)
    if previous is not None:
        return previous
    check_revision(db, owner_id, expected_revision)
    now = datetime.now(UTC).isoformat()
    facts = {}
    for name, raw in fields.items():
        if not isinstance(raw, dict) or set(raw) != {"state", "value"}:
            raise ValueError("declaration requires state and value")
        if raw["state"] not in {"KNOWN", "UNKNOWN", "WITHHELD"}:
            raise ValueError("unsupported declaration state")
        facts[name] = {
            **raw,
            "conflicts": [],
            "provenance": {
                "origin": "USER_REPORTED",
                "acquisition": "DECLARED",
                "source_ref": "declaration:" + request_id + ":" + name,
                "recorded_at": now,
                "measured_at": None,
            },
        }
    bp = blueprint_from_events(events(db, owner_id), "validation")
    bp.update(facts)
    # Canonical strict scalar checks (bool is never a cadence/budget).
    execute_science("blueprint", bp)
    if {"sessions_per_week", "declared_priorities"} & set(fields):
        from app.services.training_preferences import get_training_preferences

        prefs = get_training_preferences(db, owner_id)
        apply_training_preferences_in_transaction(
            db,
            owner_id,
            sessions_per_week=facts.get("sessions_per_week", {"value": prefs.sessions_per_week})[
                "value"
            ],
            focus_priorities=facts.get("declared_priorities", {"value": prefs.focus_priorities})[
                "value"
            ],
            available_equipment=prefs.available_equipment,
            invalidate_plan=False,
        )
    return append_event(db, owner_id, request_id, "DECLARATIONS", {"facts": facts}, body_digest)


def build_owned_snapshot(
    db: Session, owner_id: int, *, request_id: str, expected_revision: int
) -> OwnedBlueprintSnapshot:

    guard_owner(db, owner_id)
    body_digest = digest({"operation": "SNAPSHOT", "expected_revision": expected_revision})
    old = db.scalar(
        select(OwnedBlueprintSnapshot).where(
            OwnedBlueprintSnapshot.owner_id == owner_id,
            OwnedBlueprintSnapshot.request_id == request_id,
        )
    )
    if old is not None:
        if old.body_digest != body_digest:
            raise RuntimeFailure("idempotency_mismatch")
        return old
    check_revision(db, owner_id, expected_revision)
    identity = str(uuid4())
    rows = events(db, owner_id)
    as_of = datetime.now(UTC)
    episodes = episodes_from_events(rows, owner_id, as_of.isoformat())
    raw_blueprint = blueprint_from_events(rows, identity)
    if episodes:
        raw_blueprint["environment"]["context_ref"] = (
            episodes[-1]["context"]["context_ref"] or "environment:unknown"
        )
    bp = execute_science("blueprint", raw_blueprint)
    from app.services.plan_v3.calibration import _history_status

    concerns, withdrawals = _history_status(rows)
    # A later unavailable choice/preparation is not erased by an old accepted trial.
    latest = {}
    late_refs = []
    for event_row in rows:
        payload = json.loads(event_row.payload_json)
        if payload.get("late_observation_only"):
            late_refs.append(event_row.id)
        if event_row.kind in {"SETTING_CHOICE_REPORTED", "PREPARATION_REPORTED"}:
            latest[(payload.get("encounter_ref"), event_row.kind)] = (event_row.id, payload)
    for (_encounter, kind), (event_id, payload) in latest.items():
        value = payload.get("choice" if kind == "SETTING_CHOICE_REPORTED" else "preparation")
        if (
            value is None
            or (kind == "SETTING_CHOICE_REPORTED" and not value.get("available"))
            or (
                kind == "PREPARATION_REPORTED"
                and not (value.get("understood") and value.get("controlled"))
            )
        ):
            late_refs.append(event_id)
    authorities = execute_science("authorities", {})
    data = {
        "review_source_refs": concerns + late_refs,
        "withdrawal_source_refs": withdrawals,
        "authority_pins": {
            key: authorities["v3"][key]
            for key in (
                "registry_digest",
                "binding_digest",
                "bundle_digest",
                "effective_science_digest",
            )
        },
        "encounter_bundle_digest": authorities["encounter"]["bundle_digest"],
        "subject_ref": subject_ref(owner_id),
        "blueprint": bp,
        "episodes": episodes,
        "consent_assessment": {
            "state": "UNAVAILABLE",
            "purpose_ref": None,
            "revision": None,
            "receipt_ref": None,
        },
    }
    row = OwnedBlueprintSnapshot(
        id=identity,
        owner_id=owner_id,
        request_id=request_id,
        body_digest=body_digest,
        source_revision=expected_revision,
        as_of=as_of,
        snapshot_json=canonical(data),
        snapshot_digest=digest(data),
    )
    db.add(row)
    db.flush()
    return row


def invalidate_preferences(db: Session, owner_id: int, fields: tuple[str, ...]):
    """Integrity kernel remains active for existing owners when creation is off."""
    if not schema_available(db):
        from app.models.session import WorkoutSession

        if db.scalar(
            select(WorkoutSession.id)
            .where(
                WorkoutSession.user_id == owner_id,
                WorkoutSession.template_slug_snapshot == "science:v3:first-session",
            )
            .limit(1)
        ):
            raise RuntimeFailure("plan_schema_unavailable", 503)
        return
    if current_revision(db, owner_id) == 0 and not db.scalar(
        select(OwnedBlueprintSnapshot.id)
        .where(OwnedBlueprintSnapshot.owner_id == owner_id)
        .limit(1)
    ):
        return
    guard_owner(db, owner_id)
    key = str(uuid4())
    payload = {"fields": list(fields), "source": "training_preferences", "cause": "legacy_write"}
    append_event(db, owner_id, key, "SOURCE_INVALIDATED", payload, digest(payload))


def provenance(source_ref: str, at: str, *, observed: bool = False, measured_at=None):
    return {
        "origin": "USER_OBSERVED" if observed else "USER_REPORTED",
        "acquisition": "EXECUTION_LOG" if observed else "DECLARED",
        "source_ref": source_ref,
        "recorded_at": at,
        "measured_at": measured_at,
    }


def episodes_from_events(rows, owner: int, as_of: str):

    episodes = {}
    for row in rows:
        payload = json.loads(row.payload_json)
        if row.kind in {"CONTEXT_OPENED", "CALIBRATION_ENCOUNTER_OPENED"}:
            ref = payload["episode_ref"]
            episodes[ref] = {
                "episode_id": ref,
                "subject_ref": subject_ref(owner),
                "context": payload["context"],
                "as_of": as_of,
                "started_at": payload["started_at"],
                "context_provenance": payload["provenance"],
                "availability": payload["availability"],
                "ledger_complete": True,
                "ledger_source_ref": "owned-ledger:" + ref,
                "events": [],
            }
        elif (
            row.kind in {"CALIBRATION_EVENT", "CALIBRATION_EVENT_REPORTED"}
            and payload["episode_ref"] in episodes
        ):
            episodes[payload["episode_ref"]]["events"].append(payload["event"])
    # Actual history is preserved. Duplicate contexts are not silently collapsed
    # into a newly qualified episode; the canonical request rejects ambiguity.
    return execute_science("episodes", {"episodes": list(episodes.values())})


def append_owned_observation(
    db: Session, owner_id: int, *, request_id: str, expected_revision: int, event: dict
):
    body_digest = digest(
        {"operation": "OBSERVATION", "expected_revision": expected_revision, "event": event}
    )
    guard_owner(db, owner_id)
    old = replay(db, owner_id, request_id, body_digest)
    if old is not None:
        return old
    check_revision(db, owner_id, expected_revision)
    now = datetime.now(UTC).isoformat()
    identity = str(uuid4())
    rows = events(db, owner_id)
    if event.get("kind") == "CONTEXT_OPENED":
        if set(event) != {"kind", "context", "availability"}:
            raise ValueError("invalid context opening")
        context = execute_science("context", event["context"])
        existing = episodes_from_events(rows, owner_id, now)
        if any(e["context"] == context for e in existing):
            raise RuntimeFailure("context_already_opened")
        ep = execute_science(
            "episode",
            {
                "episode_id": identity,
                "subject_ref": subject_ref(owner_id),
                "context": context,
                "as_of": now,
                "started_at": now,
                "context_provenance": provenance(identity, now),
                "availability": event["availability"],
                "ledger_complete": True,
                "ledger_source_ref": "owned-ledger:" + identity,
                "events": [],
            },
        )
        payload = {
            "episode_ref": identity,
            "context": ep["context"],
            "availability": ep["availability"],
            "started_at": now,
            "provenance": provenance(identity, now),
        }
        kind = "CONTEXT_OPENED"
    elif event.get("kind") == "CALIBRATION_EVENT":
        if set(event) != {"kind", "episode_ref", "event"}:
            raise ValueError("invalid observation")
        ep = next(
            (
                e
                for e in episodes_from_events(rows, owner_id, now)
                if e["episode_id"] == event["episode_ref"]
            ),
            None,
        )
        if ep is None:
            raise RuntimeFailure("not_found", 404)
        validated = prepare_calibration_event(owner_id, ep, identity, now, event["event"])
        payload = {"episode_ref": event["episode_ref"], "event": validated}
        kind = "CALIBRATION_EVENT"
    else:
        raise ValueError("unsupported observation kind")
    row = BlueprintSourceEvent(
        id=identity,
        owner_id=owner_id,
        request_id=request_id,
        body_digest=body_digest,
        source_revision=expected_revision + 1,
        kind=kind,
        payload_json=canonical(payload),
        recorded_at=datetime.now(UTC),
    )
    db.add(row)
    db.flush()
    return row


def prepare_calibration_event(owner_id, ep, identity, now, raw):
    allowed = {
        "kind",
        "setting",
        "reps",
        "completed",
        "successful",
        "technique",
        "discomfort",
        "rir",
        "familiarization_confirmed",
        "reference_event_id",
        "occurred_at",
    }
    if not isinstance(raw, dict) or not set(raw) <= allowed:
        raise ValueError("observation contains server fields")
    actual = dict(raw)
    occurred_at = actual.pop("occurred_at", None)
    observed = actual.get("kind") == "ATTEMPT_OBSERVED"
    if observed and occurred_at is None:
        raise ValueError("actual attempt time required")
    if not observed and occurred_at is not None:
        raise ValueError("declaration time assigned by server")
    actual.update(
        event_id=identity,
        sequence=len(ep["events"]) + 1,
        subject_ref=subject_ref(owner_id),
        context_fingerprint=digest(ep["context"]),
        provenance=provenance(identity, now, observed=observed, measured_at=occurred_at),
    )
    validated = execute_science("event", actual)
    if validated["reference_event_id"] is not None and not any(
        e["event_id"] == validated["reference_event_id"] and e["kind"] == "ATTEMPT_OBSERVED"
        for e in ep["events"]
    ):
        raise ValueError("acceptance must identify an owned actual attempt")
    ep["events"].append(validated)
    execute_science("episode", ep)
    return validated


def observation_progress(rows):
    """Owned, previously validated facts only; never a permission or qualification."""
    episodes = {}
    for row in rows:
        payload = json.loads(row.payload_json)
        ref = payload.get("episode_ref")
        if row.kind in {"CONTEXT_OPENED", "CALIBRATION_ENCOUNTER_OPENED"}:
            episodes[ref] = {
                "episode_ref": ref,
                "kind": row.kind,
                "context": payload["context"],
                "availability": payload["availability"],
                "events": [],
                "preparation": None,
                "setting_choice": None,
            }
        elif ref in episodes:
            if row.kind in {"CALIBRATION_EVENT", "CALIBRATION_EVENT_REPORTED"}:
                episodes[ref]["events"].append(payload["event"])
            elif row.kind == "PREPARATION_REPORTED":
                episodes[ref]["preparation"] = payload["preparation"]
            elif row.kind == "SETTING_CHOICE_REPORTED":
                episodes[ref]["setting_choice"] = payload["choice"]
    return list(episodes.values())
