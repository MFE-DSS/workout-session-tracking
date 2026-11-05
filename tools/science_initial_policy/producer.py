"""Actual isolated contract producer. Scientific policy admission is still absent."""

from __future__ import annotations

from tools.science_contracts.blueprint_first_plan_v1 import (
    REQUIRED_FIELDS,
    FirstPlanRecommendation,
    FirstPlanRequest,
    Issue,
    decision_fingerprint,
    input_assessment,
    validate_exchange,
)
from tools.science_initial_policy.registry import ENGINE_VERSION, Registry


def _envelope(req: FirstPlanRequest, registry: Registry) -> FirstPlanRecommendation:
    used = list(REQUIRED_FIELDS) + [
        f
        for f in ("excluded_exercise_ids", "declared_priorities")
        if getattr(req.blueprint, f).state == "KNOWN"
    ]
    assessment = input_assessment(req.blueprint, tuple(used))
    status = "POLICY_UNAVAILABLE"
    issues = [
        {
            "code": "POLICY_UNAVAILABLE",
            "blocking": True,
            "field_refs": [],
            "explanation": "The isolated producer exists; scientific policy admission does not.",
        }
    ]
    if assessment.conflicting_fields:
        status = "CONFLICTING_DATA"
        issues.append(
            {
                "code": "INPUT_CONFLICT",
                "blocking": True,
                "field_refs": list(assessment.conflicting_fields),
                "explanation": "Resolve sourced input conflicts before prescription.",
            }
        )
    if assessment.missing_fields:
        if not assessment.conflicting_fields:
            status = "INSUFFICIENT_DATA"
        issues.append(
            {
                "code": "REQUIRED_INPUT_MISSING",
                "blocking": True,
                "field_refs": list(assessment.missing_fields),
                "explanation": "Required operational inputs are explicitly missing.",
            }
        )
    for field in (
        "experience",
        "excluded_exercise_ids",
        "declared_priorities",
        "height_cm",
        "weight_kg",
        "legacy_weight_kg",
    ):
        if getattr(req.blueprint, field).state == "CONFLICT":
            issues.append(
                {
                    "code": "INPUT_CONFLICT",
                    "blocking": False,
                    "field_refs": [field],
                    "explanation": "Optional conflicting input is not used for personalisation.",
                }
            )
    return FirstPlanRecommendation.model_validate(
        {
            "contract_version": "first-plan-recommendation/1.0.0",
            "request_fingerprint": decision_fingerprint(req),
            "status": status,
            "engine_version": ENGINE_VERSION,
            "assessment": assessment,
            "issues": issues,
            "used_fields": used,
            "candidate_plan": None,
            "confidence": {
                "individual_response": "NOT_ESTIMATED",
                "feasibility": "UNKNOWN",
                "evidence_refs": list(registry.policy["evidence_refs"]),
                "limitations": [
                    "Proposed dose is not individually validated.",
                    "No supported time upper bound or admitted runtime policy.",
                    "No runtime/API activation; diagnostics are non-executable.",
                ],
            },
        }
    )


def validate_input(req: FirstPlanRequest, registry: Registry) -> None:
    if req.versions.engine != ENGINE_VERSION:
        raise ValueError("unsupported engine version; explicit version binding required")
    validate_exchange(req, _envelope(req, registry), references=registry.references)


def produce(request: FirstPlanRequest | dict, registry: Registry) -> FirstPlanRecommendation:
    req = FirstPlanRequest.model_validate(request)
    validate_input(req, registry)
    from tools.science_initial_policy.planning import inspect_policy

    diagnostics = inspect_policy(req, registry)
    out = _envelope(req, registry)
    for code in diagnostics["blocker_codes"]:
        if code in {"POLICY_UNAVAILABLE", "REQUIRED_INPUT_MISSING"}:
            continue
        out.issues.append(
            Issue.model_validate(
                {
                    "code": code,
                    "blocking": True,
                    "field_refs": [],
                    "explanation": "Proposed policy diagnostic: " + code,
                }
            )
        )
    # Revalidate appended issues as models, then canonical exchange semantics.
    out = FirstPlanRecommendation.model_validate(out.model_dump())
    return validate_exchange(req, out, references=registry.references)
