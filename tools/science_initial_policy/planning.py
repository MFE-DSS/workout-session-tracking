"""Non-executable deterministic diagnostics of a PROPOSED initial policy.

These are not Plan DTOs and must never be used to start a workout.
"""

from __future__ import annotations

from typing import get_args

from tools.science_contracts.blueprint_first_plan_v1 import (
    FirstPlanRequest,
    Zone,
    decision_fingerprint,
    input_assessment,
)
from tools.science_initial_policy.registry import Registry


def match_distinct(options: list[list[dict]]) -> list[dict] | None:
    """Stable global assignment; backtrack instead of starving a later slot."""

    def assign(index: int, used: frozenset[str]) -> list[dict] | None:
        if index == len(options):
            return []
        for candidate in options[index]:
            identity = candidate["canonical_exercise_id"]
            if identity in used:
                continue
            tail = assign(index + 1, used | {identity})
            if tail is not None:
                return [candidate, *tail]
        return None

    return assign(0, frozenset())


def _candidate(identity: str, req: FirstPlanRequest, registry: Registry) -> dict | None:
    env = req.blueprint.environment
    declarations = [c for c in env.exercise_confirmations if c.canonical_exercise_id == identity]
    states = {c.state for c in declarations}
    if "UNAVAILABLE" in states:
        return None
    available = sorted(
        (c for c in declarations if c.state == "AVAILABLE"),
        key=lambda c: (c.provenance.recorded_at, c.provenance.source_ref),
    )
    source = available[-1].provenance.source_ref if available else None
    compatibility = "UNKNOWN"
    if available:
        compatibility = "CONFIRMED"
    elif identity in registry.references.no_equipment_exercise_ids:
        compatibility = "NOT_REQUIRED"
    return {
        "canonical_exercise_id": identity,
        "context_ref": env.context_ref,
        "compatibility": compatibility,
        "compatibility_source_ref": source,
    }


def _options(req: FirstPlanRequest, registry: Registry, intent: dict) -> list[dict]:
    excluded = set(req.blueprint.excluded_exercise_ids.value or [])
    result = []
    for identity, record in sorted(registry.records.items()):
        science = record["exercise_science"]
        primary = {c["zone"] for c in science["contributions"] if c["role"] == "PRIMARY"}
        if (
            identity in excluded
            or intent["primary_zone"] not in primary
            or science["movement_pattern"] not in intent["patterns"]
        ):
            continue
        candidate = _candidate(identity, req, registry)
        if candidate is not None:
            result.append(candidate)
    return sorted(
        result,
        key=lambda c: (
            c["compatibility"] not in {"CONFIRMED", "NOT_REQUIRED"},
            c["canonical_exercise_id"],
        ),
    )


def _exposure(sessions: list[dict], registry: Registry) -> list[dict]:
    totals = {
        z: {
            "zone": z,
            "raw_primary_sets": 0,
            "raw_secondary_sets": 0,
            "unknown_role_sets": 0,
            "credited_sets": 0.0,
            "bound": "EXACT",
        }
        for z in get_args(Zone)
    }
    for session in sessions:
        for slot in session["slots"]:
            if slot["selected"] is None:
                for total in totals.values():
                    total.update(bound="UNKNOWN", credited_sets=None)
                continue
            record = registry.records[slot["selected"]["canonical_exercise_id"]]
            sets = slot["prescription"]["work_sets"]
            for contribution in record["exercise_science"]["contributions"]:
                total = totals[contribution["zone"]]
                role = contribution["role"]
                if role in {"PRIMARY", "SECONDARY"}:
                    total["raw_" + role.lower() + "_sets"] += sets
                if role == "UNKNOWN":
                    total["unknown_role_sets"] += sets
                    total.update(bound="UNKNOWN", credited_sets=None)
                elif total["credited_sets"] is not None:
                    total["credited_sets"] += sets * registry.credit[role]
    return list(totals.values())


def _admission_blockers(req: FirstPlanRequest, registry: Registry) -> list[str]:
    assessment = input_assessment(req.blueprint)
    if assessment.conflicting_fields:
        return ["INPUT_CONFLICT"]
    if assessment.missing_fields:
        return ["REQUIRED_INPUT_MISSING"]
    if req.blueprint.sessions_per_week.value not in registry.policy["cadences"]:
        return ["CONSTRAINT_VIOLATION"]
    if req.blueprint.limitations.value:
        return ["CONSTRAINT_VIOLATION"]
    return []


def inspect_policy(request: FirstPlanRequest | dict, registry: Registry) -> dict:
    """Explain proposed choices separately from any executable recommendation."""
    req = FirstPlanRequest.model_validate(request)
    # Reuse v1's authoritative identity/context checks before considering candidates.
    from tools.science_initial_policy.producer import validate_input

    validate_input(req, registry)
    blocks = _admission_blockers(req, registry)
    result = {
        "diagnostics_version": "initial-policy-diagnostics/1.0.0",
        "executable": False,
        "policy_version": registry.policy["policy_version"],
        "input_fingerprint": decision_fingerprint(req),
        "sessions": [],
        "physical_work_sets_total": 0,
        "zone_exposure": [],
        "time": {"state": "UNKNOWN", "upper_minutes": None, "model_ref": None},
        "blocker_codes": blocks + ["POLICY_UNAVAILABLE", "TIME_UNCERTAIN"],
    }
    if blocks:
        return result
    intents = list(registry.policy["intents"])
    priorities = req.blueprint.declared_priorities.value or []
    if (
        "lower" in priorities
        and "shoulders" in priorities
        and priorities.index("lower") < priorities.index("shoulders")
    ):
        intents[-2:] = reversed(intents[-2:])
    options = [_options(req, registry, intent) for intent in intents]
    selected = match_distinct(options)
    if selected is None:
        result["blocker_codes"].append("CATALOG_GAP")
    p = registry.policy
    for index in range(req.blueprint.sessions_per_week.value):
        slots = []
        for position, intent in enumerate(intents):
            choice = selected[position] if selected is not None else None
            if choice and choice["compatibility"] == "UNKNOWN":
                result["blocker_codes"].append("COMPATIBILITY_UNKNOWN")
            joint = (
                registry.records[choice["canonical_exercise_id"]]["exercise_science"]["joint_type"]
                if choice
                else None
            )
            slots.append(
                {
                    "slot_id": f"session-{index + 1}-slot-{position + 1}",
                    "intent_id": intent["intent_id"],
                    "selected": choice,
                    "alternatives": [c for c in options[position] if c != choice],
                    "prescription": {
                        "status": "PROPOSED_NOT_EXECUTABLE",
                        "work_sets": p["work_sets"],
                        "min_reps": p["rep_range"][0],
                        "max_reps": p["rep_range"][1],
                        "rir_target": p["rir_target"],
                        "rest_seconds": p["rest_seconds"].get(joint),
                        "load_kg": None,
                        "load_mode": "CALIBRATION_REQUIRED",
                    },
                }
            )
        result["sessions"].append({"session_id": f"session-{index + 1}", "slots": slots})
    result["physical_work_sets_total"] = sum(
        s["prescription"]["work_sets"] for session in result["sessions"] for s in session["slots"]
    )
    result["zone_exposure"] = _exposure(result["sessions"], registry)
    if any(z["bound"] == "UNKNOWN" for z in result["zone_exposure"]):
        result["blocker_codes"].append("CATALOG_GAP")
    result["blocker_codes"] = sorted(set(result["blocker_codes"]))
    return result
