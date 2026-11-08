"""Typed factual operations; no new-work permission is inferred from logging."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import func, select

from app.models.first_plan_runtime import FirstPlanSetObservation
from app.models.session import SetLog
from app.services.plan_v3.execution import owned_binding
from app.services.plan_v3.packaging import execute_science
from app.services.plan_v3.snapshots import canonical, digest
from app.services.plan_v3.transactions import RuntimeFailure, guard_owner

PERFORMED_AT_TOLERANCE = timedelta(seconds=120)


def record_first_plan_set(
    db, owner_id, session_id, set_id, *, op_id, expected_set_revision, observation, auth=None
):
    guard_owner(db, owner_id, **(auth or {}))
    body_digest = digest(
        {
            "session_id": session_id,
            "set_id": set_id,
            "expected_revision": expected_set_revision,
            "observation": observation,
        }
    )
    old = db.scalar(
        select(FirstPlanSetObservation).where(
            FirstPlanSetObservation.owner_id == owner_id, FirstPlanSetObservation.op_id == op_id
        )
    )
    if old is not None:
        if old.body_digest != body_digest:
            raise RuntimeFailure("idempotency_mismatch")
        return json.loads(old.receipt_json)
    session, binding, payload, _ = owned_binding(db, owner_id, session_id)
    matches = [
        (mapping, slot)
        for mapping, slot in zip(
            payload["mapping"], payload["scientific_session"]["slots"], strict=True
        )
        if set_id in mapping["set_ids"]
    ]
    if len(matches) != 1:
        raise RuntimeFailure("not_found", 404)
    mapping, slot = matches[0]
    logged = db.get(SetLog, set_id)
    revision = (
        db.scalar(
            select(func.max(FirstPlanSetObservation.applied_revision)).where(
                FirstPlanSetObservation.set_id == set_id
            )
        )
        or 0
    )
    if type(expected_set_revision) is not int or expected_set_revision != revision:
        raise RuntimeFailure("set_revision_changed")
    required = {"setting", "context", "reps", "completed", "performed_at"}
    if not required <= set(observation) or set(observation) - required - {"performed_at_estimated"}:
        raise ValueError("invalid factual operation")
    if (
        "performed_at_estimated" in observation
        and type(observation["performed_at_estimated"]) is not bool
    ):
        raise ValueError("invalid clock provenance")
    reps = observation["reps"]
    completed = observation["completed"]
    if (
        type(completed) is not bool
        or (reps is not None and (type(reps) is not int or reps < 0))
        or (completed and reps is None)
    ):
        raise ValueError("invalid factual count")
    normalized = execute_science(
        "setting_context", {key: observation[key] for key in ("context", "setting")}
    )
    if canonical(normalized["context"]) != canonical(slot["prescription"]["context"]):
        raise RuntimeFailure("setting_context_changed")
    performed = datetime.fromisoformat(observation["performed_at"].replace("Z", "+00:00"))
    if performed.tzinfo is None:
        raise ValueError("explicit UTC offset required")
    performed = performed.astimezone(UTC)
    now = datetime.now(UTC)
    floor = session.started_at.replace(tzinfo=UTC)
    prior = db.scalars(
        select(SetLog).where(
            SetLog.session_exercise_id == mapping["se_id"],
            SetLog.set_index < logged.set_index,
            SetLog.completed.is_(True),
            SetLog.completed_at.is_not(None),
        )
    )
    floor = max([floor, *[row.completed_at.replace(tzinfo=UTC) for row in prior]])
    adjusted = not floor <= performed <= now + PERFORMED_AT_TOLERANCE
    at = now if adjusted else min(performed, now)
    if completed and not logged.completed and logged.completed_at is None:
        logged.completed_at = at
        logged.rest_dismissed_at = None
    logged.completed = completed
    logged.reps = reps
    # Only a real total external mass belongs in the legacy mass column.
    setting = normalized["setting"]
    logged.weight_kg = (
        setting["value"]
        if setting is not None
        and setting["kind"] == "MASS_KG"
        and normalized["context"]["load_semantics"] == "TOTAL_EXTERNAL"
        else None
    )
    receipt = {
        "state": "APPLIED",
        "session_id": session_id,
        "set_id": set_id,
        "op_id": op_id,
        "applied_revision": revision + 1,
        "performed_at": logged.completed_at.replace(tzinfo=UTC).isoformat()
        if logged.completed_at
        else None,
        "performed_at_adjusted": adjusted,
        "current_state_requires_read": True,
    }
    row = FirstPlanSetObservation(
        id=str(uuid4()),
        owner_id=owner_id,
        session_id=session_id,
        session_exercise_id=mapping["se_id"],
        set_id=set_id,
        op_id=op_id,
        body_digest=body_digest,
        expected_revision=revision,
        applied_revision=revision + 1,
        observation_json=canonical({**observation, **normalized}),
        receipt_json=canonical(receipt),
    )
    db.add(row)
    db.flush()
    return receipt
