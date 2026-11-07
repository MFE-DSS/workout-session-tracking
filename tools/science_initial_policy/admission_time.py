"""Partial disjoint lower bounds for rejection, never positive time admission."""

from __future__ import annotations

from decimal import Decimal

from tools.science_initial_policy.calibration_time_contracts import normalized_record
from tools.science_initial_policy.session_time import (
    TimeComponent,
    TimeSession,
    _basis_issues,
    _constraint,
    _decimal,
    _output_seconds,
    assess_session_time,
)

MODEL_VERSION = "initial-session-time/1.1.0-isolated"


def assess_time_for_admission(
    session: dict, *, budget_minutes: int | None, components: list[dict],
    structure: str = "TRADITIONAL_SEQUENTIAL", layout: str = "UNSPECIFIED",
) -> dict:
    """Keep only justified lower bounds whose disjoint scope is explicit.

    Missing coverage/high bounds preclude a fit. Invalid source/scope components
    contribute nothing; history is not a future bound. The rest floor and a
    partial sum are combined by max, never added and double counted. Clock
    overlap remains governed exclusively by the frozen complete union path.
    """
    result = assess_session_time(
        session, budget_minutes=budget_minutes, components=components, structure=structure, layout=layout
    )
    result["model_version"] = MODEL_VERSION
    s = TimeSession.model_validate(normalized_record(session))
    if (
        layout != "DISJOINT_SEQUENTIAL" or structure != "TRADITIONAL_SEQUENTIAL"
        or any(slot.unilateral is not False for slot in s.slots)
        or result["upper_seconds"] is not None
    ):
        return result
    rows = [TimeComponent.model_validate(normalized_record(raw)) for raw in components]
    if any(c.clock_ref is not None for c in rows):
        return result
    usable = [c for c in rows if (
        c.lower_seconds is not None and c.scope_fingerprint == result["scope_fingerprint"]
        and not (set(_basis_issues(c)) - {"COMPONENT_BOUND_UNKNOWN"})
    )]
    lower = sum((_decimal(c.lower_seconds) for c in usable), Decimal(0))
    previous = result["lower_seconds"]
    if not usable or (previous is not None and lower <= _decimal(previous)):
        return result
    result["lower_seconds"] = _output_seconds(lower)
    result["uncertainty"] = sorted(set(result["uncertainty"] + ["PARTIAL_LOWER_BOUND_ONLY"]))
    if budget_minutes is not None and lower > Decimal(budget_minutes * 60):
        result["ordinal"] = "LIKELY_EXCEEDS"
        result["constraint"] = _constraint(s, budget_minutes)
    return result
