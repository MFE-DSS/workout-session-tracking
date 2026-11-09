"""Operational generation is a selector of published SCI authority, never admission."""

from __future__ import annotations

import json

from sqlalchemy import select, update

from app.config import get_settings
from app.models.first_plan_runtime import FirstPlanRuntimeAuthority
from app.services.plan_v3.packaging import execute_science
from app.services.plan_v3.transactions import RuntimeFailure, schema_available

PROFILE = "first-session-runtime/3.0.0"
PIN_FIELDS = ("registry_digest", "binding_digest", "bundle_digest", "effective_science_digest")


def lock_authority(db, *, lock=True):
    settings = get_settings()
    if (
        settings.app_env != "test"
        or not settings.plan_v3_controlled_test_enabled
        or not schema_available(db)
    ):
        raise RuntimeFailure("authority_not_served", 503)
    if lock and db.get_bind().dialect.name == "sqlite":
        db.execute(
            update(FirstPlanRuntimeAuthority)
            .where(FirstPlanRuntimeAuthority.profile_key == PROFILE)
            .values(generation=FirstPlanRuntimeAuthority.generation)
            .execution_options(synchronize_session=False)
        )
    statement = (
        select(FirstPlanRuntimeAuthority)
        .where(FirstPlanRuntimeAuthority.profile_key == PROFILE)
        .execution_options(populate_existing=True)
    )
    row = db.scalar(statement.with_for_update() if lock else statement)
    if row is None or row.state != "ACTIVE":
        raise RuntimeFailure("authority_not_served", 503)
    try:
        authorities = execute_science("authorities", {}, expected_digest=row.packaging_digest)
        pins = {key: authorities["v3"][key] for key in PIN_FIELDS}
        if json.loads(row.publication_json) != pins or not row.approval_ref:
            raise ValueError("operational publication mismatch")
    except (ValueError, TypeError, KeyError):
        raise RuntimeFailure("authority_unavailable", 503) from None
    return row, authorities, pins
