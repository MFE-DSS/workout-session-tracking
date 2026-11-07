"""Orthogonal v3 shapes; the actual empty science authority still admits no plan.

Product choice permits future acknowledged exploration, not a positive scientific
binding or account authentication. Existing v1/v2 transports remain unchanged.
"""

from __future__ import annotations

from typing import Literal, Self

from pydantic import AwareDatetime, model_validator

from tools.science_contracts.blueprint_first_plan_v1 import Confidence, Text
from tools.science_contracts.blueprint_first_plan_v2 import (
    AssessmentV2,
    BlockerV2,
    Digest,
    FirstPlanRequestV2,
    PlanV2,
)
from tools.science_contracts.blueprint_first_plan_v2 import assess_inputs as assess_inputs
from tools.science_contracts.blueprint_first_plan_v2 import (
    evaluation_fingerprint as v2_evaluation_fingerprint,
)
from tools.science_contracts.blueprint_first_plan_v2 import (
    request_fingerprint as v2_request_fingerprint,
)
from tools.science_contracts.bootstrap_protocol_v3 import (
    CalibrationProtocolV3,
    SettingTransitionV3,
    TimeAssessmentV3,
    TrialReviewV3,
    assess_structural_time,
)
from tools.science_contracts.first_plan_v2_validation import (
    validate_exchange as validate_v2_negative,
)
from tools.science_initial_policy.admission_registry import assert_trusted_admission_registry
from tools.science_initial_policy.calibration_time_contracts import (
    Record,
    content_digest,
    normalized_record,
)
from tools.science_initial_policy.v2_registry import assert_trusted


class TimeAcknowledgmentV3(Record):
    kind: Literal["TIME_UNCERTAINTY_ACK"]
    subject_ref: Text
    snapshot_ref: Text
    source_revision: Text
    request_fingerprint: Digest
    observation_fingerprint: Digest
    plan_time_fingerprint: Digest
    product_policy_ref: Text
    acknowledged_at: AwareDatetime
    source_ref: Text


def _legacy_request(raw) -> FirstPlanRequestV2:
    value = normalized_record(raw)
    value.pop("acknowledgment", None)
    value["contract_version"] = "first-plan-request/2.0.0"
    return FirstPlanRequestV2.model_validate(value)


def _facts(legacy) -> str:
    return content_digest(
        {"contract": "first-plan-request/3.0.0", "facts": v2_request_fingerprint(legacy)}
    )


def _observations(legacy) -> str:
    return content_digest(
        {
            "contract": "first-plan-observations/3.0.0",
            "facts_and_observations": v2_evaluation_fingerprint(legacy),
        }
    )


class FirstPlanRequestV3(FirstPlanRequestV2):
    contract_version: Literal["first-plan-request/3.0.0"]
    acknowledgment: TimeAcknowledgmentV3 | None

    @model_validator(mode="after")
    def acknowledgment_boundary(self) -> Self:
        legacy = _legacy_request(self)
        ack = self.acknowledgment
        if ack is not None:
            if (
                any(
                    getattr(ack, f) != getattr(self, f)
                    for f in (
                        "subject_ref",
                        "snapshot_ref",
                        "source_revision",
                    )
                )
                or (ack.request_fingerprint, ack.observation_fingerprint)
                != (
                    _facts(legacy),
                    _observations(legacy),
                )
                or ack.acknowledged_at < self.as_of
            ):
                raise ValueError(
                    "acknowledgment does not belong to this subject/snapshot/observation decision"
                )
        return self


def validated_request(raw) -> FirstPlanRequestV3:
    return FirstPlanRequestV3.model_validate(normalized_record(raw))


def request_fingerprint(raw) -> str:
    return _facts(_legacy_request(validated_request(raw)))


def observation_fingerprint(raw) -> str:
    return _observations(_legacy_request(validated_request(raw)))


def evaluation_fingerprint(raw) -> str:
    value = validated_request(raw)
    return content_digest(
        {
            "contract": "first-plan-evaluation/3.0.0",
            "observation_fingerprint": _observations(_legacy_request(value)),
            "acknowledgment": value.acknowledgment.model_dump(mode="json")
            if value.acknowledgment
            else None,
        }
    )


def plan_time_fingerprint(plan, time_assessments) -> str:
    value = PlanV2.model_validate(normalized_record(plan))
    times = [TimeAssessmentV3.model_validate(normalized_record(t)) for t in time_assessments]
    ids = [t.session_id for t in times]
    if len(set(ids)) != len(ids) or set(ids) != {s.session_id for s in value.sessions}:
        raise ValueError("time assessments must belong exactly to the plan sessions")
    return content_digest(
        {
            "contract": "first-plan-time-context/3.0.0",
            "plan": value.model_dump(mode="json"),
            "time_assessments": [
                t.model_dump(mode="json") for t in sorted(times, key=lambda t: t.session_id)
            ],
        }
    )


class FirstPlanRecommendationV3(Record):
    contract_version: Literal["first-plan-recommendation/3.0.0"]
    subject_ref: Text
    snapshot_ref: Text
    source_revision: Text
    as_of: AwareDatetime
    generated_at: AwareDatetime
    request_fingerprint: Digest
    observation_fingerprint: Digest
    full_evaluation_fingerprint: Digest
    bundle_digest: Digest
    effective_science_digest: Digest
    engine_version: Text | None
    policy_version: Text | None
    binding_ref: Text | None
    binding_digest: Digest | None
    admission_refs: tuple[Text, ...]
    revocation_check_ref: Text | None
    assessment: AssessmentV2
    used_fields: tuple[Text, ...]
    scientific_readiness: Literal[
        "SCIENTIFICALLY_READY",
        "INSUFFICIENT_DATA",
        "CONFLICTING_DATA",
        "POLICY_UNAVAILABLE",
        "REVIEW_REQUIRED",
        "CONSTRAINT_UNSATISFIABLE",
    ]
    scientific_issues: tuple[BlockerV2, ...]
    candidate_plan: PlanV2 | None
    time_assessments: tuple[TimeAssessmentV3, ...]
    start_permission: Literal["DENIED", "REQUIRES_TIME_ACK", "ELIGIBLE"]
    start_policy_ref: Text | None
    acknowledgment: TimeAcknowledgmentV3 | None
    plan_time_fingerprint: Digest | None
    confidence: Confidence

    @model_validator(mode="after")
    def orthogonal_shape(self) -> Self:
        if self.generated_at < self.as_of:
            raise ValueError("result predates its decision snapshot")
        if self.candidate_plan is None:
            if (
                self.time_assessments
                or self.plan_time_fingerprint is not None
                or self.acknowledgment is not None
            ):
                raise ValueError("time judgment or acknowledgment needs its actual plan")
        else:
            if self.plan_time_fingerprint != plan_time_fingerprint(
                self.candidate_plan, self.time_assessments
            ):
                raise ValueError("plan/time fingerprint mismatch")
            rows = {t.session_id: t for t in self.time_assessments}
            for session in self.candidate_plan.sessions:
                if rows[session.session_id].duration != session.duration:
                    raise ValueError("time state and session contain divergent duration facts")
        if self.scientific_readiness == "SCIENTIFICALLY_READY":
            self._scientific_shape()
        elif self.start_permission != "DENIED":
            raise ValueError("incomplete/non-admitted science cannot grant start permission")
        self._permission_shape()
        return self

    def _scientific_shape(self) -> None:
        plan = self.candidate_plan
        if (
            self.assessment.state != "SUFFICIENT"
            or any(i.blocking for i in self.scientific_issues)
            or plan is None
            or plan.review_state != "REVIEWED"
            or not plan.coverage_report_complete
            or self.confidence.feasibility != "CONFIRMED"
        ):
            raise ValueError(
                "scientific shape requires sufficient facts and reviewed feasible allocation"
            )
        if not all(
            (
                self.engine_version,
                self.policy_version,
                self.binding_ref,
                self.binding_digest,
                self.admission_refs,
                self.revocation_check_ref,
            )
        ):
            raise ValueError(
                "scientific shape requires explicit authority references, not their trust"
            )
        for session in plan.sessions:
            for slot in session.slots:
                c = slot.selected
                if (
                    c is None
                    or c.compatibility not in {"CONFIRMED", "NOT_REQUIRED"}
                    or not all((c.realization_ref, c.realization_source_ref, c.equipment_ref))
                    or c.side == "UNKNOWN"
                    or c.load_semantics == "UNKNOWN"
                ):
                    raise ValueError("scientific shape requires executable selected realizations")

    def _permission_shape(self) -> None:
        uncertain = any(
            t.state in {"BUDGET_UNCERTAIN", "BUDGET_TIGHT"} for t in self.time_assessments
        )
        too_long = any(t.state == "STRUCTURALLY_TOO_LONG" for t in self.time_assessments)
        if self.start_permission != "DENIED":
            if self.start_policy_ref is None or too_long:
                raise ValueError(
                    "start needs a policy and cannot finish a structurally impossible configuration"
                )
            if self.start_permission == "REQUIRES_TIME_ACK" and (
                not uncertain or self.acknowledgment is not None
            ):
                raise ValueError("pending acknowledgment must be actually needed and absent")
            if self.start_permission == "ELIGIBLE" and uncertain and self.acknowledgment is None:
                raise ValueError("uncertain time requires explicit plan-bound acknowledgment")
        ack = self.acknowledgment
        if ack is not None:
            if (
                self.plan_time_fingerprint is None
                or ack.plan_time_fingerprint != self.plan_time_fingerprint
                or ack.product_policy_ref != self.start_policy_ref
                or not self.as_of <= ack.acknowledged_at <= self.generated_at
                or any(
                    getattr(ack, f) != getattr(self, f)
                    for f in (
                        "subject_ref",
                        "snapshot_ref",
                        "source_revision",
                        "request_fingerprint",
                        "observation_fingerprint",
                    )
                )
            ):
                raise ValueError("acknowledgment is stale or belongs to another decision/policy")


def validate_exchange(
    request, response, *, trusted_bundle, admission_registry
) -> FirstPlanRecommendationV3:
    """Negative consistency on the actual authority, not a new plan producer.

    Internal v2 reuse validates facts/references only; no v3 output is exposed as
    a v2 transport. Positive scientific/start authority requires a future scope.
    """
    assert_trusted(trusted_bundle)
    assert_trusted_admission_registry(admission_registry)
    req = validated_request(request)
    out = FirstPlanRecommendationV3.model_validate(normalized_record(response))
    if (out.request_fingerprint, out.observation_fingerprint, out.full_evaluation_fingerprint) != (
        request_fingerprint(req),
        observation_fingerprint(req),
        evaluation_fingerprint(req),
    ):
        raise ValueError("v3 request/observation/evaluation fingerprint mismatch")
    if out.acknowledgment != req.acknowledgment:
        raise ValueError("result cannot invent or omit request acknowledgment")
    if (
        out.scientific_readiness == "SCIENTIFICALLY_READY"
        or out.start_permission != "DENIED"
        or out.start_policy_ref is not None
    ):
        raise ValueError("actual empty science authority grants no positive v3 decision or start")
    legacy = _legacy_request(req)
    raw = out.model_dump(mode="json")
    for key in (
        "observation_fingerprint",
        "time_assessments",
        "start_permission",
        "start_policy_ref",
        "acknowledgment",
        "plan_time_fingerprint",
    ):
        raw.pop(key)
    raw.update(
        contract_version="first-plan-recommendation/2.0.0",
        status=raw.pop("scientific_readiness"),
        issues=raw.pop("scientific_issues"),
        request_fingerprint=v2_request_fingerprint(legacy),
    )
    raw["full_evaluation_fingerprint"] = v2_evaluation_fingerprint(legacy)
    validate_v2_negative(
        legacy, raw, trusted_bundle=trusted_bundle, admission_registry=admission_registry
    )
    if out.candidate_plan is not None:
        expected = [
            assess_structural_time(
                {
                    "session_id": s.session_id,
                    "slots": [
                        {"prescription": slot.prescription.dose.model_dump()} for slot in s.slots
                    ],
                },
                budget_minutes=s.duration.budget_minutes,
            ).model_dump(mode="json")
            for s in out.candidate_plan.sessions
        ]
        actual = [t.model_dump(mode="json") for t in out.time_assessments]
        if sorted(actual, key=lambda t: t["session_id"]) != sorted(
            expected, key=lambda t: t["session_id"]
        ):
            raise ValueError("time diagnostic differs from the actual structural source")
    return out


def exported_schemas() -> dict[str, dict]:
    return {
        name: cls.model_json_schema()
        for name, cls in (
            ("FirstPlanRequest.v3.schema.json", FirstPlanRequestV3),
            ("FirstPlanRecommendation.v3.schema.json", FirstPlanRecommendationV3),
            ("CalibrationProtocol.v3.schema.json", CalibrationProtocolV3),
            ("TrialReview.v3.schema.json", TrialReviewV3),
            ("SettingTransition.v3.schema.json", SettingTransitionV3),
        )
    }
