"""Partial rest-only bound for research diagnostics; never a duration predictor.

See admission-01/TIME_MODEL.md. Nothing imports this into the v1 producer/runtime.
"""

from collections.abc import Mapping

MODEL_VERSION = "initial-rest-floor/1.0.0"


def _positive_integer(value: object, label: str) -> int:
    if type(value) is not int or value < 1:
        raise ValueError(f"{label} must be a positive integer")
    return value


def assess_time(
    session: Mapping,
    budget_minutes: int | None,
    structure: str = "TRADITIONAL_SEQUENTIAL",
) -> dict:
    """Prove only this configuration too long, or keep feasibility UNKNOWN.

    Rest intervals must not overlap other exercises. Other time is nonnegative;
    actual work is strictly positive. Even a partial rest floor can disprove fit.
    Rest is counted between sets within a slot, never after its last set.
    """
    if budget_minutes is not None:
        _positive_integer(budget_minutes, "budget_minutes")
    slots = session.get("slots")
    if not isinstance(slots, (list, tuple)) or not slots:
        raise ValueError("a nonempty session is required")
    floor, complete = 0, True
    for slot in slots:
        prescription = slot.get("prescription", {})
        sets = _positive_integer(prescription.get("work_sets"), "work_sets")
        rest = prescription.get("rest_seconds")
        if rest is not None:
            _positive_integer(rest, "rest_seconds")
        if sets > 1:
            if rest is None:
                complete = False
            else:
                floor += (sets - 1) * rest
    unknowns = ["WORK_DURATION", "WARM_UP", "OPERATIONAL_OVERHEAD", "PERSONAL_EXECUTION"]
    if not complete:
        unknowns.append("REST_UNSPECIFIED")
    if structure != "TRADITIONAL_SEQUENTIAL":
        unknowns.append("STRUCTURE_UNSUPPORTED")
        floor, complete = None, False
    exceeds = floor is not None and budget_minutes is not None and floor >= budget_minutes * 60
    return {
        "model_version": MODEL_VERSION,
        "scope": "THIS_CONFIGURATION_ONLY",
        "budget_minutes": budget_minutes,
        "known_rest_floor_seconds": floor,
        "rest_floor_complete": complete,
        "unknown_components": unknowns,
        "feasibility": "NOT_FEASIBLE" if exceeds else "UNKNOWN",
        "issue_code": "CONSTRAINT_VIOLATION" if exceeds else "TIME_UNCERTAIN",
        "duration": {
            "state": "UNKNOWN",
            "lower_minutes": None,
            "upper_minutes": None,
            "model_ref": None,
        },
    }
