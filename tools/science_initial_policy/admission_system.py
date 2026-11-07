"""Isolated negative admission consumer, not a FirstPlan transport or authority."""

from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel

from tools.science_contracts.blueprint_first_plan_v1 import Text
from tools.science_initial_policy.admission_calibration import calibrate_for_admission
from tools.science_initial_policy.admission_registry import (
    AdmissionRegistry,
    assert_trusted_admission_registry,
)
from tools.science_initial_policy.admission_time import assess_time_for_admission
from tools.science_initial_policy.calibration_time_contracts import (
    Record,
    content_digest,
    context_digest,
    normalized_record,
)
from tools.science_initial_policy.v2_producer import EvaluationRequest, produce_v2
from tools.science_initial_policy.v2_registry import V2Registry

ENGINE_VERSION = "initial-policy-admission-evaluator/1.0.0"


class GateDecision(Record):
    gate: Literal["C1", "C2", "C3", "C4", "C5", "C6"]
    state: Literal["NOT_ADMITTED"]
    reason: Text


class AdmissionResult(Record):
    contract_version: Literal["initial-policy-admission-result/1.0.0"]
    evaluator_version: Literal["initial-policy-admission-evaluator/1.0.0"]
    evaluated_engine: Literal["initial-policy-producer/2.0.0"]
    evaluated_policy: Text
    subject_ref: Text
    request_fingerprint: Text
    evaluation_fingerprint: Text
    admission_fingerprint: Text
    registry_digest: Text
    source_manifest_digest: Text
    bundle_digest: Text
    effective_science_digest: Text
    historical_status: Text
    gates: tuple[GateDecision, ...]
    calibration_by_context: dict[str, dict]
    time_by_session: list[dict]
    verdict: Literal["NOT_ADMITTED"]
    runtime_availability: Literal["NOT_SERVED"]
    ready_fixture: Literal["NOT_PRODUCED"]


def _strict_json(value) -> str:
    """Exact JSON types: bool/int and int/float are distinct in this contract."""
    if isinstance(value, BaseModel):
        value = value.model_dump(mode="json")

    def check(item):
        if type(item) is dict:
            if any(type(k) is not str for k in item):
                raise ValueError("JSON object keys must be strings")
            for child in item.values():
                check(child)
        elif type(item) is list:
            for child in item:
                check(child)
        elif item is not None and type(item) not in (str, int, float, bool):
            raise ValueError("only exact JSON value types are accepted")

    check(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def verify_evaluation_strict(request: dict, result: dict, trusted_bundle: V2Registry) -> dict:
    """Verify raw types BEFORE Pydantic could normalize an edited artifact."""
    expected = produce_v2(request, trusted_bundle)
    if _strict_json(result) != _strict_json(expected):
        raise ValueError("result differs from the strict authoritative evaluation")
    return expected


def _diagnostics(value, historical, bundle):
    calibrations = {
        context_digest(ep.context): calibrate_for_admission(
            ep, min_reps=bundle.dose["rep_range"][0], max_reps=bundle.dose["rep_range"][1]
        ) for ep in sorted(value.episodes, key=lambda ep: context_digest(ep.context))
    }
    timing = {t.session_id: t for t in value.timing_inputs}
    results = []
    for index, row in enumerate(historical["draft"]["sessions"]):
        session = row["time_session"]
        source = timing.get(session["session_id"])
        result = assess_time_for_admission(
            session, budget_minutes=value.request.blueprint.session_budgets_minutes.value[index],
            components=[c.model_dump(mode="json") for c in source.components] if source else [],
            structure=source.structure if source else "TRADITIONAL_SEQUENTIAL",
            layout=source.layout if source else "UNSPECIFIED",
        )
        results.append({"session_id": session["session_id"], **result})
    return calibrations, results


def evaluate_admission(
    evaluation_request: dict, evaluation_result: dict, trusted_v2_bundle: V2Registry,
    trusted_admission_registry: AdmissionRegistry,
) -> dict:
    """Recompute frozen v2 and successor diagnostics; empty registry always refuses.

    This pure boundary authenticates no account and serves no runtime. The
    result's fingerprints bind the full sourced observation request and pinned
    successor code; successful engineering checks never admit a policy.
    """
    registry = trusted_admission_registry
    assert_trusted_admission_registry(registry)
    historical = verify_evaluation_strict(evaluation_request, evaluation_result, trusted_v2_bundle)
    value = EvaluationRequest.model_validate(normalized_record(evaluation_request))
    calibrations, times = _diagnostics(value, historical, trusted_v2_bundle)
    reasons = (
        "POPULATION_BINDING_NOT_ADMITTED", "DOSE_BINDING_NOT_ADMITTED",
        "BOOTSTRAP_PROTOCOL_NOT_ADMITTED", "EXACT_SELECTION_BINDING_NOT_ADMITTED",
        "READY_CONTRACT_PROJECTION_NOT_ADMITTED", "POSITIVE_TIME_BASIS_NOT_ADMITTED",
    )
    data = {
        "contract_version": "initial-policy-admission-result/1.0.0",
        "evaluator_version": ENGINE_VERSION, "evaluated_engine": historical["engine_version"],
        "evaluated_policy": trusted_v2_bundle.policy["policy_version"],
        "subject_ref": value.subject_ref, "request_fingerprint": historical["request_fingerprint"],
        "evaluation_fingerprint": historical["evaluation_fingerprint"],
        "registry_digest": registry.registry_digest, "source_manifest_digest": registry.manifest_digest,
        "bundle_digest": historical["bundle_digest"],
        "effective_science_digest": historical["effective_science_digest"],
        "historical_status": historical["recommendation"]["status"],
        "gates": [{"gate": f"C{n}", "state": "NOT_ADMITTED", "reason": reason}
                  for n, reason in enumerate(reasons, 1)],
        "calibration_by_context": calibrations, "time_by_session": times,
        "verdict": "NOT_ADMITTED", "runtime_availability": "NOT_SERVED", "ready_fixture": "NOT_PRODUCED",
    }
    data["admission_fingerprint"] = content_digest(data)
    return AdmissionResult.model_validate(data).model_dump(mode="json")
