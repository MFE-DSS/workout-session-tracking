"""Owned presentation only. No evaluation, start, acknowledgement or write."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select

from app.config import get_settings
from app.models.session import WorkoutSession
from app.services.mobile_read_models import _resume, iso_utc, mission_read_model
from app.services.plan_v3.authority import lock_authority
from app.services.plan_v3.commands import read_owned_first_session_handoff
from app.services.plan_v3.execution import is_scientific_session, owned_binding
from app.services.plan_v3.snapshots import current_revision
from app.services.plan_v3.transactions import RuntimeFailure, schema_available

VERSION = "mission-action/1.0.0"
V3_PROFILE = "first-plan-execution/3.0.0"
INVENTORY = "plan-calibration-inventory/2.0.0"


def _result(base, state, source, action=None, payload=None, reason=None):
    return {
        **base,
        "state": state,
        "source": source,
        "primary_action": action,
        "payload": payload,
        "reason": reason,
    }


def _unavailable(base, source, reason, *, retry=True):
    return _result(
        base, "UNAVAILABLE", source, {"kind": "REFRESH"} if retry else None, reason=reason
    )


def _scientific_projection(db, base, session, v3_host, *, closed):
    source = "OWNED_FIRST_USE" if closed else "OPEN_SESSION"
    if not v3_host:
        return _unavailable(base, source, "EXECUTION_PROFILE_REQUIRED", retry=False)
    if not schema_available(db):
        return _unavailable(base, source, "SCHEMA_UNAVAILABLE")
    try:
        owned_binding(db, base["owner_id"], session.id)
    except RuntimeFailure:
        return _unavailable(base, source, "RUNTIME_NOT_SERVED")
    summary = _resume(db, session)
    payload = {**summary, "execution_profile": V3_PROFILE}
    action = "OPEN_FIRST_SESSION_HISTORY" if closed else "RESUME_V3"
    return _result(
        base,
        "FIRST_SESSION_HISTORY" if closed else "RESUME",
        source,
        {"kind": action, "session_id": session.id},
        payload,
    )


def _first_use_projection(db, base, v3_host):
    source = "OWNED_FIRST_USE"
    owner = base["owner_id"]
    if not schema_available(db):
        return _unavailable(base, source, "SCHEMA_UNAVAILABLE")
    handoff = read_owned_first_session_handoff(db, owner)
    if handoff is not None:
        session = db.scalar(
            select(WorkoutSession).where(
                WorkoutSession.id == handoff.session_id,
                WorkoutSession.user_id == owner,
            )
        )
        if session is None or not is_scientific_session(session):
            return _unavailable(base, source, "RUNTIME_NOT_SERVED")
        return _scientific_projection(db, base, session, v3_host, closed=True)
    settings = get_settings()
    if settings.app_env != "test" or not settings.plan_v3_controlled_test_enabled:
        return _unavailable(base, source, "RUNTIME_NOT_SERVED")
    if not v3_host:
        return _unavailable(base, source, "EXECUTION_PROFILE_REQUIRED", retry=False)
    try:
        _, authorities, _ = lock_authority(db, lock=False)
    except RuntimeFailure:
        return _unavailable(base, source, "AUTHORITY_UNAVAILABLE")
    if authorities.get("calibration_inventory", {}).get("version") != INVENTORY:
        return _unavailable(base, source, "RUNTIME_NOT_SERVED")
    return _result(
        base,
        "FIRST_USE",
        source,
        {"kind": "OPEN_FIRST_USE"},
        {
            "execution_profile": V3_PROFILE,
            "calibration_inventory": INVENTORY,
            "source_revision": f"blueprint-source/{current_revision(db, owner)}",
        },
    )


def _historical_projection(db, base):
    historical = mission_read_model(db, base["owner_id"])
    if historical["state"] == "NO_MISSION":
        return _result(base, "NO_MISSION", "NONE")
    if historical["state"] != "READY" or not historical.get("executable"):
        return _unavailable(base, "HISTORICAL_MISSION", "HISTORICAL_NOT_EXECUTABLE")
    return _result(
        base,
        "HISTORICAL_READY",
        "HISTORICAL_MISSION",
        {
            "kind": "START_LEGACY",
            "template_slug": historical["template"]["slug"],
            "decision": historical["decision"],
        },
        historical,
    )


def project_mission_action(db, owner_id, requested_path, *, v3_host=False, now=None):
    """Read facts first; a chosen source never supplies scientific permission."""
    if requested_path not in ("FIRST_USE", "HISTORICAL"):
        raise ValueError("mission_path_required")
    if type(v3_host) is not bool:
        raise ValueError("mission_host_required")
    if type(owner_id) is not int or owner_id <= 0:
        raise ValueError("mission_owner_required")
    base = {
        "contract_version": VERSION,
        "owner_id": owner_id,
        "requested_path": requested_path,
        "observed_at": iso_utc(now or datetime.now(UTC)),
    }
    # A read must not flush unrelated pending ORM facts or acquire a write guard.
    with db.no_autoflush:
        opened = list(
            db.scalars(
                select(WorkoutSession)
                .where(
                    WorkoutSession.user_id == owner_id,
                    WorkoutSession.status == "in_progress",
                )
                .order_by(WorkoutSession.id)
                .limit(2)
            )
        )
        if len(opened) > 1:
            return _result(base, "CONFLICT", "OPEN_SESSION", reason="MULTIPLE_OPEN_SESSIONS")
        if opened:
            session = opened[0]
            if is_scientific_session(session):
                return _scientific_projection(db, base, session, v3_host, closed=False)
            return _result(
                base,
                "RESUME",
                "OPEN_SESSION",
                {"kind": "RESUME_LEGACY", "session_id": session.id},
                {**_resume(db, session), "execution_profile": "LEGACY_V1"},
            )
        if requested_path == "HISTORICAL":
            return _historical_projection(db, base)
        return _first_use_projection(db, base, v3_host)
