"""Real immutable evaluations and plan-bound time acknowledgment, flush-only."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select

from app.models.first_plan_runtime import FirstPlanEvaluation, OwnedBlueprintSnapshot
from app.services.plan_v3.authority import lock_authority
from app.services.plan_v3.packaging import execute_science
from app.services.plan_v3.snapshots import canonical, check_revision, digest
from app.services.plan_v3.transactions import RuntimeFailure, guard_owner


def owned_evaluation(db, owner_id, evaluation_ref):
    row = db.scalar(
        select(FirstPlanEvaluation).where(
            FirstPlanEvaluation.owner_id == owner_id, FirstPlanEvaluation.id == evaluation_ref
        )
    )
    if row is None:
        raise RuntimeFailure("not_found", 404)
    return row


def replay(db, owner_id, kind, request_id, body_digest):
    row = db.scalar(
        select(FirstPlanEvaluation).where(
            FirstPlanEvaluation.owner_id == owner_id,
            FirstPlanEvaluation.operation_kind == kind,
            FirstPlanEvaluation.request_id == request_id,
        )
    )
    if row is not None and row.body_digest != body_digest:
        raise RuntimeFailure("idempotency_mismatch")
    return row


def request_from_snapshot(snapshot, authority):
    value = json.loads(snapshot.snapshot_json)
    registry = authority["v3"]
    return {
        "contract_version": "first-plan-request/3.0.0",
        "requirement_profile_id": "first-bodybuilding-inputs/2.0.0",
        "as_of": snapshot.as_of.replace(tzinfo=UTC).isoformat(),
        "subject_ref": value["subject_ref"],
        "snapshot_ref": snapshot.id,
        "source_revision": "blueprint-source/" + str(snapshot.source_revision),
        "blueprint": value["blueprint"],
        "episodes": value["episodes"],
        "timing_inputs": [],
        "versions": {
            "catalogue": registry["catalogue_version"],
            "zones": "zones-15-v1",
            "engine": registry["policy"]["engine_version"],
            "policy": registry["policy"]["policy_version"],
        },
        "requested_binding_ref": registry["binding_ref"],
        "bundle_digest": registry["bundle_digest"],
        "effective_science_digest": registry["effective_science_digest"],
        "acknowledgment": None,
    }


def evaluate_owned_snapshot(db, owner_id, *, snapshot_ref, request_id, expected_pins, auth=None):
    body_digest = digest({"snapshot_ref": snapshot_ref, "expected_pins": expected_pins})
    # A durable replay is history, not renewed permission or fresh authority.
    old = replay(db, owner_id, "EVALUATE", request_id, body_digest)
    if old is not None:
        guard_owner(db, owner_id, **(auth or {}))
        return old
    operational, authority, pins = lock_authority(db)
    guard_owner(db, owner_id, **(auth or {}))
    old = replay(db, owner_id, "EVALUATE", request_id, body_digest)
    if old is not None:
        return old
    snapshot = db.scalar(
        select(OwnedBlueprintSnapshot).where(
            OwnedBlueprintSnapshot.owner_id == owner_id, OwnedBlueprintSnapshot.id == snapshot_ref
        )
    )
    if snapshot is None:
        raise RuntimeFailure("not_found", 404)
    if expected_pins != pins:
        raise RuntimeFailure("authority_version_mismatch", 406)
    check_revision(db, owner_id, snapshot.source_revision)
    snapshot_data = json.loads(snapshot.snapshot_json)
    if snapshot_data.get("review_source_refs"):
        raise RuntimeFailure("calibration_review_required")
    if snapshot_data.get("withdrawal_source_refs"):
        raise RuntimeFailure("calibration_withdrawn")
    if snapshot_data.get("authority_pins") != pins:
        raise RuntimeFailure("snapshot_authority_changed")
    from app.services.plan_v3.calibration_profiles import assert_snapshot_runtime

    assert_snapshot_runtime(db, snapshot.id, operational, authority)
    request = request_from_snapshot(snapshot, authority)
    try:
        result = execute_science("evaluate", request, expected_digest=operational.packaging_digest)
    except ValueError:
        raise RuntimeFailure("producer_unavailable", 503) from None
    row = FirstPlanEvaluation(
        id=str(uuid4()),
        owner_id=owner_id,
        snapshot_id=snapshot.id,
        operation_kind="EVALUATE",
        request_id=request_id,
        body_digest=body_digest,
        source_revision=snapshot.source_revision,
        authority_generation=operational.generation,
        request_json=canonical(request),
        result_json=canonical(result),
    )
    db.add(row)
    db.flush()
    return row


def acknowledge_time(db, owner_id, *, evaluation_ref, request_id, expected_context, auth=None):
    body_digest = digest({"evaluation_ref": evaluation_ref, "expected_context": expected_context})
    old = replay(db, owner_id, "TIME_ACK", request_id, body_digest)
    if old is not None:
        guard_owner(db, owner_id, **(auth or {}))
        return old
    operational, authority, pins = lock_authority(db)
    guard_owner(db, owner_id, **(auth or {}))
    old = replay(db, owner_id, "TIME_ACK", request_id, body_digest)
    if old is not None:
        return old
    parent = owned_evaluation(db, owner_id, evaluation_ref)
    check_revision(db, owner_id, parent.source_revision)
    if parent.authority_generation != operational.generation:
        raise RuntimeFailure("authority_generation_changed")
    from app.services.plan_v3.calibration_profiles import assert_snapshot_runtime

    assert_snapshot_runtime(db, parent.snapshot_id, operational, authority)
    request = json.loads(parent.request_json)
    try:
        previous = execute_science(
            "evaluate", request, expected_digest=operational.packaging_digest
        )
    except ValueError:
        raise RuntimeFailure("producer_unavailable", 503) from None
    if previous["start_permission"] != "REQUIRES_TIME_ACK":
        raise RuntimeFailure("time_ack_not_applicable")
    expected = {
        key: previous[key]
        for key in (
            "request_fingerprint",
            "observation_fingerprint",
            "plan_time_fingerprint",
            "start_policy_ref",
        )
    }
    if expected_context != expected:
        raise RuntimeFailure("time_ack_context_changed")
    request["acknowledgment"] = {
        "kind": "TIME_UNCERTAINTY_ACK",
        "subject_ref": request["subject_ref"],
        "snapshot_ref": request["snapshot_ref"],
        "source_revision": request["source_revision"],
        "request_fingerprint": expected["request_fingerprint"],
        "observation_fingerprint": expected["observation_fingerprint"],
        "plan_time_fingerprint": expected["plan_time_fingerprint"],
        "product_policy_ref": expected["start_policy_ref"],
        "acknowledged_at": datetime.now(UTC).isoformat(),
        "source_ref": "time-ack:" + str(uuid4()),
    }
    try:
        result = execute_science("evaluate", request, expected_digest=operational.packaging_digest)
    except ValueError:
        raise RuntimeFailure("producer_unavailable", 503) from None
    row = FirstPlanEvaluation(
        id=str(uuid4()),
        owner_id=owner_id,
        snapshot_id=parent.snapshot_id,
        parent_evaluation_id=parent.id,
        operation_kind="TIME_ACK",
        request_id=request_id,
        body_digest=body_digest,
        source_revision=parent.source_revision,
        authority_generation=operational.generation,
        request_json=canonical(request),
        result_json=canonical(result),
    )
    db.add(row)
    db.flush()
    return row
