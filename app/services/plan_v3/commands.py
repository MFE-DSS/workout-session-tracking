"""Atomic first handoff and durable cancellation. Caller owns commit/rollback."""

from __future__ import annotations

import json
from uuid import uuid4

from sqlalchemy import select

from app.models.first_plan_runtime import FirstSessionRequest
from app.models.session import WorkoutSession
from app.services.plan_v3.authority import lock_authority
from app.services.plan_v3.evaluations import owned_evaluation
from app.services.plan_v3.execution import materialize_first_plan_session
from app.services.plan_v3.packaging import execute_science
from app.services.plan_v3.snapshots import canonical, check_revision, digest
from app.services.plan_v3.transactions import RuntimeFailure, guard_owner, schema_available


def read_owned_first_session_request(db, owner_id, request_id):
    if not schema_available(db):
        raise RuntimeFailure("not_found", 404)
    row = db.scalar(
        select(FirstSessionRequest).where(
            FirstSessionRequest.owner_id == owner_id, FirstSessionRequest.request_id == request_id
        )
    )
    if row is None:
        raise RuntimeFailure("not_found", 404)
    return row


def read_owned_first_session_handoff(db, owner_id):
    if not schema_available(db):
        raise RuntimeFailure("not_found", 404)
    return db.scalar(
        select(FirstSessionRequest).where(
            FirstSessionRequest.owner_id == owner_id, FirstSessionRequest.state == "CREATED"
        )
    )


def _replay(db, owner, request_id, body_digest):
    row = db.scalar(
        select(FirstSessionRequest).where(
            FirstSessionRequest.owner_id == owner, FirstSessionRequest.request_id == request_id
        )
    )
    if row is not None and row.body_digest != body_digest:
        raise RuntimeFailure("idempotency_mismatch")
    return row


def _row(db, owner, key, body, state, *, evaluation=None, session=None, code=None):
    row = FirstSessionRequest(
        id=str(uuid4()),
        owner_id=owner,
        request_id=key,
        body_digest=digest(body),
        body_json=canonical(body),
        state=state,
        evaluation_id=evaluation.id if evaluation is not None else None,
        session_id=session.id if session is not None else None,
        scientific_session_id=body.get("selected_scientific_session_id")
        if state == "CREATED"
        else None,
        terminal_code=code,
    )
    db.add(row)
    db.flush()
    return row


def expected_start_body(evaluation, result, registry_digest):
    return {
        "evaluation_ref": evaluation.id,
        "snapshot_ref": evaluation.snapshot_id,
        "source_revision": evaluation.source_revision,
        **{
            key: result[key]
            for key in (
                "request_fingerprint",
                "observation_fingerprint",
                "full_evaluation_fingerprint",
                "plan_time_fingerprint",
                "binding_ref",
                "binding_digest",
                "bundle_digest",
                "effective_science_digest",
                "engine_version",
                "policy_version",
                "contract_version",
            )
        },
        "registry_digest": registry_digest,
        "selected_scientific_session_id": result["candidate_plan"]["sessions"][0]["session_id"],
    }


def start_owned_first_session(db, owner_id, *, request_id, body, auth=None):
    body_digest = digest(body)
    old = _replay(db, owner_id, request_id, body_digest)
    if old is not None:
        guard_owner(db, owner_id, **(auth or {}))
        return old
    operational, authority, pins = lock_authority(db)
    guard_owner(db, owner_id, **(auth or {}))
    old = _replay(db, owner_id, request_id, body_digest)
    if old is not None:
        return old
    previous = read_owned_first_session_handoff(db, owner_id)
    if previous is not None:
        return _row(db, owner_id, request_id, body, "DENIED", code="first_session_already_created")
    if not isinstance(body.get("evaluation_ref"), str):
        raise ValueError("evaluation_ref required")
    evaluation = owned_evaluation(db, owner_id, body["evaluation_ref"])
    try:
        from app.services.plan_v3.calibration_profiles import assert_snapshot_runtime

        assert_snapshot_runtime(db, evaluation.snapshot_id, operational, authority)
        check_revision(db, owner_id, evaluation.source_revision)
        if evaluation.authority_generation != operational.generation:
            raise RuntimeFailure("authority_generation_changed")
    except RuntimeFailure as error:
        return _row(
            db, owner_id, request_id, body, "DENIED", evaluation=evaluation, code=error.code
        )
    try:
        result = execute_science(
            "evaluate",
            json.loads(evaluation.request_json),
            expected_digest=operational.packaging_digest,
        )
    except ValueError:
        raise RuntimeFailure("producer_unavailable", 503) from None
    if result["start_permission"] != "ELIGIBLE":
        return _row(
            db,
            owner_id,
            request_id,
            body,
            "DENIED",
            evaluation=evaluation,
            code="scientific_permission_required",
        )
    expected = expected_start_body(evaluation, result, pins["registry_digest"])
    if canonical(body) != canonical(expected):
        return _row(
            db,
            owner_id,
            request_id,
            body,
            "DENIED",
            evaluation=evaluation,
            code="evaluation_context_changed",
        )
    opened = db.scalar(
        select(WorkoutSession.id)
        .where(WorkoutSession.user_id == owner_id, WorkoutSession.status == "in_progress")
        .limit(1)
    )
    if opened is not None:
        return _row(
            db, owner_id, request_id, body, "DENIED", evaluation=evaluation, code="session_open"
        )
    try:
        session = materialize_first_plan_session(
            db,
            owner_id,
            validated_evaluation=evaluation,
            result=result,
            first_scientific_session_id=expected["selected_scientific_session_id"],
        )
    except RuntimeFailure as error:
        if error.code != "execution_not_representable":
            raise
        return _row(
            db, owner_id, request_id, body, "DENIED", evaluation=evaluation, code=error.code
        )

    return _row(db, owner_id, request_id, body, "CREATED", evaluation=evaluation, session=session)


def cancel_owned_first_session(db, owner_id, *, request_id, body, auth=None):
    guard_owner(db, owner_id, **(auth or {}))
    old = _replay(db, owner_id, request_id, digest(body))
    if old is not None:
        return old
    return _row(db, owner_id, request_id, body, "CANCELLED", code="cancelled_before_creation")
