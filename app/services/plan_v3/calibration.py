"""Owner ledger -> admitted pilot; navigation/intention never becomes execution."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import uuid4

from app.config import get_settings
from app.models.first_plan_runtime import BlueprintSourceEvent
from app.services.plan_v3 import snapshots as source
from app.services.plan_v3.authority import lock_authority
from app.services.plan_v3.packaging import execute_science
from app.services.plan_v3.transactions import RuntimeFailure, guard_owner

PHYSICAL_ACTIONS = frozenset(
    {
        "INITIATE_FAMILIARIZATION",
        "CONFIRM_FAMILIARIZATION",
        "INITIATE_TRIAL",
        "ACCEPT_EXACT_SETTING",
    }
)


def _owned_open(rows, encounter_ref):
    row = next(
        (r for r in rows if r.kind == "CALIBRATION_ENCOUNTER_OPENED" and r.id == encounter_ref),
        None,
    )
    if row is None:
        raise RuntimeFailure("not_found", 404)
    return row, json.loads(row.payload_json)


def _append(db, owner, key, body_digest, kind, payload, identity=None):
    row = BlueprintSourceEvent(
        id=identity or str(uuid4()),
        owner_id=owner,
        request_id=key,
        body_digest=body_digest,
        source_revision=source.current_revision(db, owner) + 1,
        kind=kind,
        payload_json=source.canonical(payload),
        recorded_at=datetime.now(UTC),
    )
    db.add(row)
    db.flush()
    return row


def open_encounter(
    db,
    owner_id,
    *,
    request_id,
    expected_revision,
    context,
    availability,
    concern_state="UNKNOWN",
    auth=None,
):
    body_digest = source.digest(
        {
            "operation": "ENCOUNTER_OPEN",
            "expected_revision": expected_revision,
            "context": context,
            "availability": availability,
            "concern_state": concern_state,
        }
    )
    old = source.replay(db, owner_id, request_id, body_digest)
    if old is not None:
        guard_owner(db, owner_id, **(auth or {}))
        return old
    operational, authority, pins = lock_authority(db)
    guard_owner(db, owner_id, **(auth or {}))
    old = source.replay(db, owner_id, request_id, body_digest)
    if old is not None:
        return old
    source.check_revision(db, owner_id, expected_revision)
    if concern_state not in {"UNKNOWN", "REPORTED", "CLEAR"} or availability not in {
        "UNKNOWN",
        "AVAILABLE",
        "UNAVAILABLE",
    }:
        raise ValueError("invalid personal state")
    ctx = execute_science("context", context)
    identity = str(uuid4())
    now = datetime.now(UTC).isoformat()
    return _append(
        db,
        owner_id,
        request_id,
        body_digest,
        "CALIBRATION_ENCOUNTER_OPENED",
        {
            "encounter_ref": identity,
            "episode_ref": identity,
            "context": ctx,
            "availability": availability,
            "concern_state": concern_state,
            "started_at": now,
            "provenance": source.provenance(identity, now),
            "authority_generation": operational.generation,
            "encounter_bundle_digest": authority["encounter"]["bundle_digest"],
        },
        identity,
    )


def _history_status(rows):
    concern_refs = []
    withdrawal_refs = []
    for row in rows:
        payload = json.loads(row.payload_json)
        if row.kind == "ENCOUNTER_WITHDRAWN":
            withdrawal_refs.append(row.id)
        if (
            row.kind == "CALIBRATION_ENCOUNTER_OPENED"
            and payload.get("concern_state") == "REPORTED"
        ):
            concern_refs.append(row.id)
        if row.kind in {"CALIBRATION_EVENT", "CALIBRATION_EVENT_REPORTED"}:
            event = payload["event"]
            if event["kind"] == "CONCERN_REPORTED" or (
                event["kind"] == "ATTEMPT_OBSERVED"
                and (
                    event["successful"] is False
                    or event["technique"] != "ACCEPTABLE"
                    or event["discomfort"] != "NO_CONCERN"
                    or (
                        row.kind == "CALIBRATION_EVENT_REPORTED"
                        and payload.get("stop_reason", "UNKNOWN")
                        in {"CONCERN", "FAILURE", "UNKNOWN"}
                    )
                )
            ):
                concern_refs.append(row.id)
    return concern_refs, withdrawal_refs


def _request(rows, owner, encounter_ref, as_of):
    opened, data = _owned_open(rows, encounter_ref)
    episodes = source.episodes_from_events(rows, owner, as_of)
    episode = next(e for e in episodes if e["episode_id"] == encounter_ref)
    declarations = source.blueprint_from_events(rows, "calibration:current")
    preparation = None
    choice = None
    stop_reasons = {}
    retry = False
    for row in rows:
        payload = json.loads(row.payload_json)
        if payload.get("encounter_ref", payload.get("episode_ref")) != encounter_ref:
            continue
        if row.kind == "PREPARATION_REPORTED":
            preparation = payload["preparation"]
        elif row.kind == "SETTING_CHOICE_REPORTED":
            choice = payload["choice"]
        elif row.kind == "CALIBRATION_RETRY_REQUESTED":
            retry = True
        elif (
            row.kind == "CALIBRATION_EVENT_REPORTED"
            and payload["event"]["kind"] == "ATTEMPT_OBSERVED"
        ):
            stop_reasons[payload["event"]["event_id"]] = payload["stop_reason"]
            retry = False
    concerns, withdrawals = _history_status(rows)
    return {
        "contract_version": "first-calibration-encounter/1.0.0",
        "encounter_ref": encounter_ref,
        "subject_ref": source.subject_ref(owner),
        "source_revision": "blueprint-source/" + str(rows[-1].source_revision if rows else 0),
        "started_at": data["started_at"],
        "as_of": as_of,
        "population": declarations["population_scope"],
        "limitations": declarations["limitations"],
        "context": data["context"],
        "context_provenance": data["provenance"],
        "availability": data["availability"],
        "ledger_complete": True,
        "ledger_source_ref": "owned-ledger:" + encounter_ref,
        "concern_state": "REPORTED" if concerns else data["concern_state"],
        "withdrawn": bool(withdrawals),
        "episode": episode,
        "preparation": preparation,
        "setting_choice": choice,
        "stop_reasons": stop_reasons,
        "retry_requested": retry,
    }


def read_encounter(db, owner_id, encounter_ref, *, auth=None):
    try:
        operational, authorities, pins = lock_authority(db)
    except RuntimeFailure as error:
        guard_owner(db, owner_id, **(auth or {}))
        rows = source.events(db, owner_id)
        _owned_open(rows, encounter_ref)
        return {
            "encounter_ref": encounter_ref,
            "source_revision": source.current_revision(db, owner_id),
            "as_of": datetime.now(UTC).isoformat(),
            "result": None,
            "authority": None,
            "runtime_availability": "NOT_SERVED",
            "unavailable_reason": error.code,
            "allowed_actions": [],
            "progress": factual_progress(rows, encounter_ref),
        }
    guard_owner(db, owner_id, **(auth or {}))
    rows = source.events(db, owner_id)
    raw = _request(rows, owner_id, encounter_ref, datetime.now(UTC).isoformat())
    try:
        result = execute_science("calibration", raw, expected_digest=operational.packaging_digest)
    except ValueError:
        raise RuntimeFailure("calibration_producer_unavailable", 503) from None

    allowed = result["allowed_actions"]
    if not get_settings().plan_v3_guidance_enabled:
        allowed = [action for action in allowed if action not in PHYSICAL_ACTIONS]
    return {
        "encounter_ref": encounter_ref,
        "source_revision": source.current_revision(db, owner_id),
        "as_of": raw["as_of"],
        "result": result,
        "allowed_actions": allowed,
        "authority": {
            "generation": operational.generation,
            "encounter_bundle_digest": authorities["encounter"]["bundle_digest"],
            "policy_ref": authorities["encounter"]["policy"]["policy_ref"],
            "context_fingerprint": source.digest(raw["context"]),
            "contract_version": "first-calibration-encounter/1.0.0",
        },
        "progress": factual_progress(rows, encounter_ref),
    }


def factual_progress(rows, encounter_ref):
    entry = next(
        (e for e in source.observation_progress(rows) if e["episode_ref"] == encounter_ref), None
    )
    if entry is None:
        raise RuntimeFailure("not_found", 404)
    attempts = [e for e in entry["events"] if e["kind"] == "ATTEMPT_OBSERVED"]
    return {
        "ledger_complete": True,
        "observed_attempt_count": len(attempts),
        "observation_refs": [e["event_id"] for e in attempts],
        "acceptance_refs": [
            e["event_id"] for e in entry["events"] if e["kind"] == "SETTING_ACCEPTED"
        ],
        **entry,
        "observations": attempts,
    }


def record_encounter_observation(
    db,
    owner_id,
    *,
    request_id,
    expected_revision,
    encounter_ref,
    expected_authority,
    observation,
    auth=None,
):
    body_digest = source.digest(
        {
            "operation": "ENCOUNTER_OBSERVATION",
            "expected_revision": expected_revision,
            "encounter_ref": encounter_ref,
            "expected_authority": expected_authority,
            "observation": observation,
        }
    )
    old = source.replay(db, owner_id, request_id, body_digest)
    if old is not None:
        guard_owner(db, owner_id, **(auth or {}))
        return old
    view = read_encounter(db, owner_id, encounter_ref, auth=auth)
    old = source.replay(db, owner_id, request_id, body_digest)
    if old is not None:
        return old
    source.check_revision(db, owner_id, expected_revision)
    if view["result"] is None or view["authority"] is None:
        # A withdrawn authority cannot guide or accept a new setting. Actual past
        # observations remain recordable and explicitly quarantined from admission.
        return _record_late_fact(db, owner_id, request_id, body_digest, encounter_ref, observation)
    if source.canonical(expected_authority) != source.canonical(view["authority"]):
        raise RuntimeFailure("calibration_authority_changed")
    kind = observation.get("kind")
    identity = str(uuid4())
    now = datetime.now(UTC).isoformat()
    payload = {
        "encounter_ref": encounter_ref,
        "episode_ref": encounter_ref,
        "validation": {
            "input_digest": view["result"]["input_digest"],
            "as_of": view["as_of"],
            "authority": view["authority"],
            "source_revision": view["source_revision"],
        },
    }
    raw = _request(source.events(db, owner_id), owner_id, encounter_ref, now)
    if kind == "PREPARATION_REPORTED":
        if set(observation) != {"kind", "instruction_ref", "setup_ref", "understood", "controlled"}:
            raise ValueError("invalid preparation")
        prep = {key: value for key, value in observation.items() if key != "kind"}
        prep.update(
            context_fingerprint=view["authority"]["context_fingerprint"],
            provenance=source.provenance(identity, now),
        )
        raw["preparation"] = prep
        payload["preparation"] = prep
    elif kind == "SETTING_CHOICE_REPORTED":
        choice = _setting_choice(observation, view, identity, now)
        raw["setting_choice"] = choice
        payload["choice"] = choice
    elif kind == "CALIBRATION_EVENT_REPORTED":
        _record_actual_event(observation, view, raw, payload, owner_id, identity, now)
    elif kind == "CALIBRATION_ACTION_REQUESTED":
        if (
            set(observation) != {"kind", "action"}
            or observation["action"] not in view["allowed_actions"]
        ):
            raise RuntimeFailure("calibration_action_not_permitted")
        payload["action"] = observation["action"]  # Intention, no CalibrationEvent inserted.
    elif kind == "ENCOUNTER_WITHDRAWN":
        if set(observation) != {"kind"}:
            raise ValueError("invalid withdrawal")
        raw["withdrawn"] = True
    elif kind == "CALIBRATION_RETRY_REQUESTED":
        if set(observation) != {"kind"} or raw["concern_state"] != "CLEAR" or raw["withdrawn"]:
            raise RuntimeFailure("calibration_action_not_permitted")
        raw["retry_requested"] = True
    else:
        raise ValueError("unsupported encounter observation")
    # Revalidate fresh facts under the actual authority, never the GET's old time digest.
    execute_science("calibration", raw)
    return _append(db, owner_id, request_id, body_digest, kind, payload, identity)


def _record_actual_event(observation, view, raw, payload, owner_id, identity, now):
    if not set(observation) <= {"kind", "event", "stop_reason"} or "event" not in observation:
        raise ValueError("invalid actual event")
    event = observation["event"]
    event_kind = event.get("kind")
    action = {
        "CONTEXT_CONFIRMED": "CONFIRM_CONTEXT",
        "FAMILIARIZATION_CONFIRMED": "CONFIRM_FAMILIARIZATION",
        "FAMILIARIZATION_STARTED": "INITIATE_FAMILIARIZATION",
        "SETTING_ACCEPTED": "ACCEPT_EXACT_SETTING",
    }.get(event_kind, "RECORD_TRIAL")
    if action not in view["allowed_actions"]:
        raise RuntimeFailure("calibration_action_not_permitted")
    validated = source.prepare_calibration_event(owner_id, raw["episode"], identity, now, event)
    payload["event"] = validated
    if event_kind == "ATTEMPT_OBSERVED":
        if "stop_reason" not in observation:
            raise ValueError("actual stop reason required")
        payload["stop_reason"] = observation["stop_reason"]
        raw["stop_reasons"][identity] = observation["stop_reason"]
    elif "stop_reason" in observation:
        raise ValueError("stop reason requires trial")


def _setting_choice(observation, view, identity, now):
    if (
        set(observation) != {"kind", "setting", "available"}
        or type(observation["available"]) is not bool
    ):
        raise ValueError("invalid setting choice")
    if observation["setting"] is None:
        if observation["available"]:
            raise ValueError("available setting requires observation")
        choice = None
    else:
        choice = {
            "context_fingerprint": view["authority"]["context_fingerprint"],
            "setting": observation["setting"],
            "available": observation["available"],
            "provenance": source.provenance(identity, now),
        }
    return choice


def _record_late_fact(db, owner, request_id, body_digest, encounter_ref, observation):
    if observation.get("kind") != "CALIBRATION_EVENT_REPORTED":
        raise RuntimeFailure("calibration_authority_unavailable", 503)
    event = observation.get("event", {})
    if event.get("kind") not in {
        "ATTEMPT_OBSERVED",
        "CONCERN_REPORTED",
        "FAMILIARIZATION_STARTED",
        "FAMILIARIZATION_CONFIRMED",
    }:
        raise RuntimeFailure("calibration_authority_unavailable", 503)
    if not set(observation) <= {"kind", "event", "stop_reason"}:
        raise ValueError("invalid actual event")
    identity = str(uuid4())
    now = datetime.now(UTC).isoformat()
    raw = _request(source.events(db, owner), owner, encounter_ref, now)
    event = source.prepare_calibration_event(owner, raw["episode"], identity, now, event)
    payload = {
        "encounter_ref": encounter_ref,
        "episode_ref": encounter_ref,
        "event": event,
        "late_observation_only": True,
        "validation": None,
    }
    if event["kind"] == "ATTEMPT_OBSERVED":
        if observation.get("stop_reason") not in {
            "COMPLETED",
            "CONCERN",
            "FAILURE",
            "UNKNOWN",
            "USER_STOPPED",
            "TIME_LIMIT",
        }:
            raise ValueError("actual stop reason required")
        payload["stop_reason"] = observation["stop_reason"]
    elif "stop_reason" in observation:
        raise ValueError("stop reason requires trial")
    return _append(
        db, owner, request_id, body_digest, "CALIBRATION_EVENT_REPORTED", payload, identity
    )
