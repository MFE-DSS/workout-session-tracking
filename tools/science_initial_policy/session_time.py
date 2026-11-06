"""Conditional timing arithmetic; no admitted predictive model or runtime duration."""

from __future__ import annotations

from decimal import Decimal
from math import isfinite
from typing import Literal, Self

from pydantic import AwareDatetime, StrictBool, model_validator

from tools.science_contracts.blueprint_first_plan_v1 import Provenance, Text
from tools.science_initial_policy.calibration_time_contracts import (
    Number,
    Record,
    _check_time,
    content_digest,
)
from tools.science_initial_policy.time_feasibility import assess_time

MODEL_VERSION = "initial-session-time/1.0.0"


def _decimal(value: float | int) -> Decimal:
    return Decimal(str(value))


def _output_seconds(value: Decimal | None) -> float | None:
    if value is None:
        return None
    result = float(value)
    if not isfinite(result):
        raise ValueError("aggregate seconds are not representable as a finite number")
    return result


class TimeSlot(Record):
    slot_id: Text
    unilateral: StrictBool | None = None
    prescription: dict


class TimeSession(Record):
    session_id: Text
    subject_ref: Text
    context_ref: Text
    as_of: AwareDatetime
    slots: tuple[TimeSlot, ...]

    @model_validator(mode="after")
    def slot_identity(self) -> Self:
        ids = [s.slot_id for s in self.slots]
        if not ids or len(set(ids)) != len(ids):
            raise ValueError("nonempty unique session slots required")
        return self


class TimeComponent(Record):
    component_id: Text
    coverage_key: Text
    kind: Literal["WORK", "REST", "PREPARATION_CALIBRATION", "SETUP_TRANSITION"]
    lower_seconds: Number | None
    upper_seconds: Number | None
    basis_ref: Text | None
    basis_kind: Literal[
        "EXPERIMENTAL_INTERVAL", "OBSERVED_HISTORY", "PRODUCT_ASSUMPTION",
        "VALIDATED_MODEL", "PRESCRIPTION", "UNKNOWN",
    ]
    scope_fingerprint: Text
    provenance: Provenance
    clock_ref: Text | None = None
    start_seconds: Number | None = None
    end_seconds: Number | None = None

    @model_validator(mode="after")
    def bounds_and_clock(self) -> Self:
        low, high = self.lower_seconds, self.upper_seconds
        if low is not None and high is not None and low > high:
            raise ValueError("time bounds reversed")
        start, end = self.start_seconds, self.end_seconds
        if start is not None and end is not None:
            span = _decimal(end) - _decimal(start)
            if span < 0 or (low is not None and span < _decimal(low)) or (
                high is not None and span > _decimal(high)
            ):
                raise ValueError("clock span contradicts component bounds")
        return self


def _coverage(session: TimeSession) -> tuple[dict, dict]:
    expected, rests = {"session/prep": "PREPARATION_CALIBRATION"}, {}
    for slot in session.slots:
        sets = slot.prescription["work_sets"]  # validated by canonical rest-floor first
        expected[slot.slot_id + "/prep"] = "PREPARATION_CALIBRATION"
        expected[slot.slot_id + "/operations"] = "SETUP_TRANSITION"
        for n in range(1, sets + 1):
            expected[f"{slot.slot_id}/work/{n}"] = "WORK"
        for n in range(1, sets):
            key = f"{slot.slot_id}/rest/{n}"
            expected[key], rests[key] = "REST", slot.prescription.get("rest_seconds")
    return expected, rests


def _basis_issues(component: TimeComponent) -> list[str]:
    p, issues = component.provenance, []
    if component.basis_kind == "OBSERVED_HISTORY":
        issues.append("HISTORY_IS_NOT_A_PREDICTIVE_BOUND")
    if component.basis_kind == "VALIDATED_MODEL":
        issues.append("MODEL_NOT_ADMITTED")
    if p.origin == "POPULATION_PRIOR":
        issues.append("POPULATION_PRIOR_NOT_AN_INDIVIDUAL_BOUND")
    if component.basis_kind == "UNKNOWN" or not component.basis_ref or (
        p.source_ref is None or p.recorded_at is None or p.origin == "UNKNOWN"
        or p.acquisition == "UNKNOWN"
    ):
        issues.append("COMPONENT_SOURCE_UNKNOWN")
    if component.basis_kind == "PRESCRIPTION" and component.kind != "REST":
        issues.append("PRESCRIPTION_HAS_NO_WORK_OR_SETUP_TIME")
    if component.basis_kind == "PRODUCT_ASSUMPTION" and p.origin != "PRODUCT_CONTRACT":
        issues.append("ASSUMPTION_IS_NOT_AN_OBSERVATION")
    if component.lower_seconds is None or component.upper_seconds is None:
        issues.append("COMPONENT_BOUND_UNKNOWN")
    if component.kind == "WORK" and component.upper_seconds == 0:
        issues.append("WORK_DURATION_NOT_POSITIVE")
    return issues


def _validate_components(session, raw_components, expected, rests, scope):
    components, seen_ids, seen_keys, issues = [], set(), set(), []
    for raw in raw_components:
        data = raw.model_dump(mode="json") if isinstance(raw, TimeComponent) else raw
        c = TimeComponent.model_validate(data)
        if c.component_id in seen_ids or c.coverage_key in seen_keys:
            raise ValueError("duplicate timing identity or coverage")
        if expected.get(c.coverage_key) != c.kind:
            raise ValueError("timing key/kind does not belong to this prescription")
        seen_ids.add(c.component_id)
        seen_keys.add(c.coverage_key)
        _check_time(c.provenance, session.as_of)
        if c.scope_fingerprint != scope:
            issues.append("SCOPE_MISMATCH")
        minimum = rests.get(c.coverage_key)
        if minimum is not None and c.lower_seconds is not None and c.lower_seconds < minimum:
            raise ValueError("time estimate cannot shorten prescribed rest")
        issues.extend(_basis_issues(c))
        components.append(c)
    return sorted(components, key=lambda c: c.coverage_key), issues


def _clock_sum(components):
    if not components or any(
        c.clock_ref is None or c.start_seconds is None or c.end_seconds is None
        or c.lower_seconds is None or c.upper_seconds != c.lower_seconds for c in components
    ) or len({c.clock_ref for c in components}) != 1:
        return None, None, ["CLOCK_SCOPE_UNKNOWN"]
    spans = [(_decimal(c.start_seconds), _decimal(c.end_seconds), c.kind) for c in components]
    if any(
        min(a[1], b[1]) > max(a[0], b[0])
        for i, a in enumerate(spans) for b in spans[i + 1:]
        if {a[2], b[2]} != {"REST", "SETUP_TRANSITION"}
    ):
        return None, None, ["WORK_REST_STRUCTURE_CONFLICT"]
    merged = []
    for start, end, _ in sorted(spans):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(end, merged[-1][1])
        else:
            merged.append([start, end])
    total = sum((end - start for start, end in merged), Decimal(0))
    full_span = merged[-1][1] - merged[0][0]
    if full_span > total:
        return None, None, ["UNACCOUNTED_CLOCK_GAP"]
    overlap = sum((end - start for start, end, _ in spans), Decimal(0)) - total
    return total, overlap, []


def _total(components, layout):
    if layout == "COMMON_CLOCK":
        seconds, overlap, issues = _clock_sum(components)
        return seconds, seconds, overlap, issues
    if layout != "DISJOINT_SEQUENTIAL":
        return None, None, None, ["OVERLAP_NOT_SPECIFIED"]
    if any(c.clock_ref is not None for c in components):
        return None, None, None, ["CLOCK_LAYOUT_REQUIRES_EXPLICIT_UNION"]
    low = sum((_decimal(c.lower_seconds) for c in components), Decimal(0))
    high = sum((_decimal(c.upper_seconds) for c in components), Decimal(0))
    return low, high, Decimal(0), []


def _constraint(session, budget):
    return {
        "code": "CONSTRAINT_VIOLATION", "scope": "THIS_CONFIGURATION_ONLY",
        "session_id": session.session_id, "budget_minutes": budget,
        "prescribed_rest_preserved": True, "coverage_preserved": True,
        "actions": ["REPLAN_WITH_ADMITTED_CONFIGURATION", "REVIEW_TIME_MODEL"],
    }


def assess_session_time(
    session: dict, *, budget_minutes: int | None, components: list[dict],
    structure: str = "TRADITIONAL_SEQUENTIAL", layout: str = "UNSPECIFIED",
) -> dict:
    """Assess conditional intervals; no caller argument can confer model admission.

    Arithmetic positives are experimental/product-conditional diagnostics, never
    Duration ESTIMATED or a scientific claim of individual completion probability.
    """
    raw = session.model_dump(mode="json") if isinstance(session, TimeSession) else session
    s = TimeSession.model_validate(raw)
    normalized = s.model_dump(mode="json")
    floor_result = assess_time(normalized, budget_minutes, structure)
    scope = content_digest({"session": normalized, "structure": structure})
    expected, rests = _coverage(s)
    rows, issues = _validate_components(s, components, expected, rests, scope)
    missing = sorted(set(expected) - {c.coverage_key for c in rows})
    if missing:
        issues.append("COVERAGE_INCOMPLETE")
    issues.extend(x for x in floor_result["unknown_components"] if x in {
        "REST_UNSPECIFIED", "STRUCTURE_UNSUPPORTED",
    })
    if any(slot.unilateral is not False for slot in s.slots):
        issues.append("UNILATERAL_TIME_SCOPE_UNRESOLVED")
    low, high, overlap = None, None, None
    if not issues:
        low, high, overlap, layout_issues = _total(rows, layout)
        issues.extend(layout_issues)
    floor = floor_result["known_rest_floor_seconds"]
    if "UNILATERAL_TIME_SCOPE_UNRESOLVED" in issues:
        floor = None  # no side/appairing assumption
    ordinal = "UNKNOWN"
    budget = None if budget_minutes is None else Decimal(budget_minutes * 60)
    if budget is not None and floor is not None and Decimal(floor) >= budget:
        ordinal = "LIKELY_EXCEEDS"
    elif budget is not None and low is not None and high is not None:
        ordinal = "LIKELY_EXCEEDS" if low > budget else "LIKELY_FITS" if high <= budget else "BORDERLINE"
    all_assumptions = bool(rows) and all(c.basis_kind == "PRODUCT_ASSUMPTION" for c in rows)
    return {
        "model_version": MODEL_VERSION, "scope_fingerprint": scope,
        "scope": "THIS_CONFIGURATION_ONLY", "ordinal": ordinal,
        "budget_minutes": budget_minutes, "known_rest_floor_seconds": floor,
        "lower_seconds": _output_seconds(low) if low is not None else floor,
        "upper_seconds": _output_seconds(high),
        "overlap_seconds": _output_seconds(overlap),
        "missing_coverage": missing,
        "basis_class": "PRODUCT_ASSUMPTIONS_ONLY" if all_assumptions else "EXPERIMENTAL_NOT_ADMITTED",
        "basis_refs": sorted({c.basis_ref for c in rows if c.basis_ref}),
        "uncertainty": sorted(set(issues + ["NO_ADMITTED_TIME_MODEL"])),
        "component_bounds": [c.model_dump(mode="json") for c in rows],
        "duration": {"state": "UNKNOWN", "lower_minutes": None, "upper_minutes": None, "model_ref": None},
        "constraint": _constraint(s, budget_minutes) if ordinal == "LIKELY_EXCEEDS" else None,
        "runtime_availability": "NOT_SERVED",
    }
