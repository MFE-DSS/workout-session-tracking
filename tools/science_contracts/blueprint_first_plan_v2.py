"""Isolated v2 contract shapes. Neither JSON validity nor a digest admits science.

Blueprint v1 and historical producers stay unchanged. Runtime negotiation, trusted
positive bindings and an admitted producer are deliberately outside this module.
"""

from __future__ import annotations

from typing import Annotated, Literal, Self, get_args

from pydantic import AwareDatetime, Field, StrictBool, model_validator

from tools.science_contracts.blueprint_first_plan_v1 import (
    FACT_FIELDS,
    Blueprint,
    Confidence,
    PositiveInt,
    Text,
    Zone,
    _provenances,
    input_assessment,
)
from tools.science_initial_policy.calibration_time_contracts import (
    CalibrationEpisode,
    ContextKey,
    Number,
    Record,
    Setting,
    _check_setting_context,
    _check_time,
    content_digest,
    context_digest,
    normalized_record,
)
from tools.science_initial_policy.v2_producer import TimingInput

Digest = Annotated[str, Field(strict=True, pattern="^[0-9a-f]{64}$")]
PROFILE = "first-bodybuilding-inputs/2.0.0"
COVERAGE = frozenset({"WORK", "REST", "PREPARATION_CALIBRATION", "SETUP_TRANSITION"})


class VersionsV2(Record):
    catalogue: Text
    zones: Literal["zones-15-v1"]
    engine: Text | None
    policy: Text | None


class FirstPlanRequestV2(Record):
    contract_version: Literal["first-plan-request/2.0.0"]
    requirement_profile_id: Literal["first-bodybuilding-inputs/2.0.0"]
    as_of: AwareDatetime
    subject_ref: Text
    snapshot_ref: Text
    source_revision: Text
    blueprint: Blueprint
    versions: VersionsV2
    requested_binding_ref: Text | None
    bundle_digest: Digest
    effective_science_digest: Digest
    episodes: tuple[CalibrationEpisode, ...]
    timing_inputs: tuple[TimingInput, ...]

    @model_validator(mode="after")
    def boundaries(self) -> Self:
        if self.snapshot_ref != self.blueprint.snapshot_id:
            raise ValueError("snapshot does not identify these Blueprint facts")
        for p in _provenances(self.blueprint):
            _check_time(p, self.as_of)
        identities, contexts = set(), set()
        for ep in self.episodes:
            key = context_digest(ep.context)
            if ep.episode_id in identities or key in contexts:
                raise ValueError("ambiguous episode or context identity")
            identities.add(ep.episode_id)
            contexts.add(key)
            if ep.subject_ref != self.subject_ref or ep.as_of != self.as_of:
                raise ValueError("episode subject or decision time mismatch")
            if ep.context.context_ref != self.blueprint.environment.context_ref:
                raise ValueError("episode belongs to another environment")
        sessions = set()
        for row in self.timing_inputs:
            if row.subject_ref != self.subject_ref or row.session_id in sessions:
                raise ValueError("ambiguous timing subject or identity")
            sessions.add(row.session_id)
            ids, keys = set(), set()
            for c in row.components:
                if c.component_id in ids or c.coverage_key in keys:
                    raise ValueError("duplicate timing component or coverage")
                ids.add(c.component_id)
                keys.add(c.coverage_key)
                _check_time(c.provenance, self.as_of)
        return self


def validated_request(raw) -> FirstPlanRequestV2:
    return FirstPlanRequestV2.model_validate(normalized_record(raw))


def _canonical_request(raw) -> dict:
    value = validated_request(raw).model_dump(mode="json")
    bp = value["blueprint"]
    for field in ("limitations", "excluded_exercise_ids"):
        if bp[field]["value"] is not None:
            bp[field]["value"] = sorted(set(bp[field]["value"]))
    equipment = bp["environment"]["equipment_items"]
    if equipment["value"] is not None:
        equipment["value"] = sorted(set(equipment["value"]))
    # Priority and session order remain semantic. Observation sets do not.
    for field in ("observations",):
        bp[field] = sorted(bp[field], key=content_digest)
    bp["environment"]["exercise_confirmations"].sort(key=content_digest)
    value["episodes"].sort(key=lambda e: e["episode_id"])
    for ep in value["episodes"]:
        ep["events"] = sorted(
            {e["event_id"]: e for e in ep["events"]}.values(), key=lambda e: e["sequence"]
        )
    value["timing_inputs"].sort(key=lambda t: t["session_id"])
    for t in value["timing_inputs"]:
        t["components"].sort(key=lambda c: c["coverage_key"])
    return value


def request_fingerprint(raw) -> str:
    """V2 fact/snapshot fingerprint, intentionally separate from v1 semantics."""
    value = _canonical_request(raw)
    del value["episodes"], value["timing_inputs"]
    return content_digest(value)


def evaluation_fingerprint(raw) -> str:
    """Complete decision input, including observations, without hidden history."""
    return content_digest(_canonical_request(raw))


class Dose(Record):
    work_sets: PositiveInt
    min_reps: PositiveInt
    max_reps: PositiveInt
    rir_target: Number
    rest_seconds: PositiveInt
    source_ref: Text
    evidence_refs: tuple[Text, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def ordered(self) -> Self:
        if self.min_reps > self.max_reps:
            raise ValueError("repetition interval reversed")
        return self


class ObservedSettingPrescription(Record):
    mode: Literal["OBSERVED_SETTING"]
    dose: Dose
    episode_id: Text
    event_id: Text
    acceptance_event_id: Text
    context: ContextKey
    setting: Setting

    @model_validator(mode="after")
    def context_units(self) -> Self:
        if (
            any(
                getattr(self.context, f) is None
                for f in (
                    "canonical_exercise_id",
                    "context_ref",
                    "equipment_ref",
                    "realization_ref",
                )
            )
            or self.context.side == "UNKNOWN"
            or self.context.load_semantics == "UNKNOWN"
        ):
            raise ValueError("an observed setting needs its exact executable context")
        _check_setting_context(self.setting, self.context)
        return self


class BootstrapStep(Record):
    step_id: Text
    kind: Literal["FAMILIARIZE", "TRIAL", "OBSERVE", "DECIDE"]
    instruction_ref: Text


class BootstrapPrescription(Record):
    mode: Literal["BOOTSTRAP_PROTOCOL"]
    dose: Dose
    protocol_ref: Text
    stop_rule_ref: Text
    retry_rule_ref: Text
    timing_scope_ref: Text
    steps: tuple[BootstrapStep, ...]

    @model_validator(mode="after")
    def executable_sequence(self) -> Self:
        kinds = [s.kind for s in self.steps]
        if kinds != ["FAMILIARIZE", "TRIAL", "OBSERVE", "DECIDE"]:
            raise ValueError("bootstrap needs ordered familiarization/trial/observation/decision")
        if len({s.step_id for s in self.steps}) != len(self.steps):
            raise ValueError("duplicate bootstrap step identity")
        return self


PrescriptionV2 = Annotated[
    ObservedSettingPrescription | BootstrapPrescription,
    Field(discriminator="mode"),
]


class UnknownDuration(Record):
    state: Literal["UNKNOWN"]
    budget_minutes: PositiveInt


class DiagnosticDuration(Record):
    state: Literal["CONDITIONAL_DIAGNOSTIC"]
    budget_minutes: PositiveInt
    lower_seconds: Number | None
    upper_seconds: Number | None
    basis_refs: tuple[Text, ...]
    scope_fingerprint: Digest
    limitations: tuple[Text, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def ordered(self) -> Self:
        if self.lower_seconds is not None and self.upper_seconds is not None:
            if self.lower_seconds > self.upper_seconds:
                raise ValueError("diagnostic bounds reversed")
        return self


class SupportedDuration(Record):
    state: Literal["SUPPORTED"]
    budget_minutes: PositiveInt
    lower_seconds: Number
    upper_seconds: Number
    unit: Literal["seconds"]
    basis_kind: Literal["ADMITTED_MODEL", "ADMITTED_PRODUCT_CONVENTION"]
    basis_ref: Text
    basis_version: Text
    scope_fingerprint: Digest
    applicability_ref: Text
    covers_bootstrap: StrictBool
    coverage: tuple[Literal["WORK", "REST", "PREPARATION_CALIBRATION", "SETUP_TRANSITION"], ...]
    evidence_refs: tuple[Text, ...] = Field(min_length=1)
    limitations: tuple[Text, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def complete_bounds(self) -> Self:
        if self.lower_seconds > self.upper_seconds or self.upper_seconds <= 0:
            raise ValueError("supported duration needs ordered positive upper bound")
        if set(self.coverage) != COVERAGE or len(self.coverage) != len(COVERAGE):
            raise ValueError("duration must cover work/rest/preparation/operations exactly once")
        return self


DurationV2 = Annotated[
    UnknownDuration | DiagnosticDuration | SupportedDuration,
    Field(discriminator="state"),
]


class DurationEnvelope(Record):
    duration: DurationV2


class CandidateV2(Record):
    canonical_exercise_id: Text
    context_ref: Text
    realization_ref: Text | None
    equipment_ref: Text | None
    side: Literal["BILATERAL", "LEFT", "RIGHT", "UNKNOWN"]
    load_semantics: Literal[
        "TOTAL_EXTERNAL",
        "PER_IMPLEMENT",
        "MACHINE_DISPLAY_KG",
        "ASSISTANCE_SETTING",
        "NON_MASS_SETTING",
        "BODYWEIGHT",
        "UNKNOWN",
    ]
    compatibility: Literal["CONFIRMED", "NOT_REQUIRED", "UNKNOWN", "UNAVAILABLE"]
    compatibility_source_ref: Text | None
    realization_source_ref: Text | None


class SlotV2(Record):
    slot_id: Text
    intent_id: Text
    selected: CandidateV2 | None
    alternatives: tuple[CandidateV2, ...]
    substitution_rule_ref: Text
    prescription: PrescriptionV2
    rationale: Text


class SessionV2(Record):
    session_id: Text
    slots: tuple[SlotV2, ...] = Field(min_length=1)
    duration: DurationV2


class RoleContribution(Record):
    slot_id: Text
    canonical_exercise_id: Text
    realization_ref: Text
    role: Literal["PRIMARY", "SECONDARY", "MINOR"]
    source_ref: Text
    evidence_refs: tuple[Text, ...] = Field(min_length=1)


class ZoneReport(Record):
    zone: Zone
    role_status: Literal["SUPPORTED_ROLES", "UNKNOWN", "NO_SUPPORTED_ROLE_IN_SELECTED_SET"]
    contributions: tuple[RoleContribution, ...]
    unresolved_slot_ids: tuple[Text, ...]
    absence_basis_ref: Text | None
    limitations: tuple[Text, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def honest_role(self) -> Self:
        if (self.role_status == "SUPPORTED_ROLES") != bool(self.contributions):
            raise ValueError("supported roles require contributions; unknown is not a role")
        if len(set(self.unresolved_slot_ids)) != len(self.unresolved_slot_ids):
            raise ValueError("duplicate unresolved slot")
        ids = [c.slot_id for c in self.contributions]
        if len(set(ids)) != len(ids) or set(ids) & set(self.unresolved_slot_ids):
            raise ValueError("a slot cannot have conflicting role reports")
        if self.role_status == "NO_SUPPORTED_ROLE_IN_SELECTED_SET":
            if not self.absence_basis_ref or self.unresolved_slot_ids:
                raise ValueError("absence of supported role needs a scoped basis, not unknown")
        elif self.absence_basis_ref is not None:
            raise ValueError("absence basis only belongs to scoped absence")
        return self


class PlanV2(Record):
    allocation_ref: Text
    review_state: Literal["DRAFT", "REVIEWED"]
    sessions: tuple[SessionV2, ...] = Field(min_length=1)
    physical_work_sets_total: PositiveInt
    zone_model_version: Literal["zones-15-v1"]
    coverage_report_complete: StrictBool
    zone_reports: tuple[ZoneReport, ...]

    @model_validator(mode="after")
    def accounting(self) -> Self:
        session_ids = [s.session_id for s in self.sessions]
        slots = [slot for s in self.sessions for slot in s.slots]
        ids = [s.slot_id for s in slots]
        if len(set(session_ids)) != len(session_ids) or len(set(ids)) != len(ids):
            raise ValueError("session and global slot identities must be unique")
        if sum(s.prescription.dose.work_sets for s in slots) != self.physical_work_sets_total:
            raise ValueError("physical work-set total differs from prescriptions")
        zones = [z.zone for z in self.zone_reports]
        if len(set(zones)) != len(zones):
            raise ValueError("duplicate zone")
        if self.coverage_report_complete and set(zones) != set(get_args(Zone)):
            raise ValueError("complete report requires all fifteen zones")
        for z in self.zone_reports:
            if not set(z.unresolved_slot_ids) <= set(ids):
                raise ValueError("unresolved zone slot does not belong to this plan")
            for c in z.contributions:
                slot = next(s for s in slots if s.slot_id == c.slot_id)
                if slot.selected is None or (c.canonical_exercise_id, c.realization_ref) != (
                    slot.selected.canonical_exercise_id,
                    slot.selected.realization_ref,
                ):
                    raise ValueError("zone contribution does not describe the selected realization")
        return self


class AssessmentV2(Record):
    state: Literal["SUFFICIENT", "INSUFFICIENT", "CONFLICTING"]
    requirement_profile_id: Literal["first-bodybuilding-inputs/2.0.0"]
    missing_fields: tuple[Text, ...]
    conflicting_fields: tuple[Text, ...]


def assess_inputs(blueprint: Blueprint, used_fields: tuple[str, ...] = ()) -> AssessmentV2:
    result = input_assessment(blueprint, used_fields).model_dump()
    result["requirement_profile_id"] = PROFILE
    return AssessmentV2.model_validate(result)


class BlockerV2(Record):
    code: Literal[
        "INPUT_CONFLICT",
        "REQUIRED_INPUT_MISSING",
        "POLICY_UNAVAILABLE",
        "NO_FEASIBLE_PLAN",
        "COMPATIBILITY_UNKNOWN",
        "TIME_UNCERTAIN",
        "CATALOG_GAP",
        "CONSTRAINT_VIOLATION",
        "CALIBRATION_REQUIRED",
        "BINDING_UNAVAILABLE",
    ]
    blocking: StrictBool
    gate_ref: Literal["C1", "C2", "C3", "C4", "C5", "C6"] | None
    source_refs: tuple[Text, ...]
    field_refs: tuple[Text, ...]
    explanation: Text

    @model_validator(mode="after")
    def known_fields(self) -> Self:
        if not set(self.field_refs) <= FACT_FIELDS:
            raise ValueError("unknown Blueprint field")
        return self


class FirstPlanRecommendationV2(Record):
    contract_version: Literal["first-plan-recommendation/2.0.0"]
    subject_ref: Text
    snapshot_ref: Text
    source_revision: Text
    as_of: AwareDatetime
    generated_at: AwareDatetime
    request_fingerprint: Digest
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
    issues: tuple[BlockerV2, ...]
    used_fields: tuple[Text, ...]
    status: Literal[
        "READY",
        "INSUFFICIENT_DATA",
        "CONFLICTING_DATA",
        "POLICY_UNAVAILABLE",
        "CONSTRAINT_UNSATISFIABLE",
        "REVIEW_REQUIRED",
    ]
    candidate_plan: PlanV2 | None
    confidence: Confidence

    @model_validator(mode="after")
    def result_shape(self) -> Self:
        if self.generated_at < self.as_of:
            raise ValueError("result generated before its decision time")
        if not set(self.used_fields) <= FACT_FIELDS or len(set(self.used_fields)) != len(
            self.used_fields
        ):
            raise ValueError("invalid used fields")
        if self.status == "READY":
            self._ready_shape()
        return self

    def _ready_shape(self) -> None:
        plan = self.candidate_plan
        if self.assessment.state != "SUFFICIENT" or any(i.blocking for i in self.issues):
            raise ValueError("READY cannot have insufficient facts or blocking issues")
        if not all(
            (
                self.binding_ref,
                self.binding_digest,
                self.revocation_check_ref,
                self.engine_version,
                self.policy_version,
                self.admission_refs,
            )
        ):
            raise ValueError("READY requires explicit binding/admission references")
        if plan is None or plan.review_state != "REVIEWED" or not plan.coverage_report_complete:
            raise ValueError("READY requires a reviewed complete plan")
        if self.confidence.feasibility != "CONFIRMED":
            raise ValueError("READY feasibility cannot remain uncertain")
        for session in plan.sessions:
            duration = session.duration
            if (
                not isinstance(duration, SupportedDuration)
                or duration.upper_seconds > duration.budget_minutes * 60
            ):
                raise ValueError("READY requires a supported duration within its declared budget")
            for slot in session.slots:
                c = slot.selected
                if (
                    c is None
                    or c.compatibility not in {"CONFIRMED", "NOT_REQUIRED"}
                    or (
                        c.realization_ref is None
                        or c.realization_source_ref is None
                        or c.equipment_ref is None
                        or c.side == "UNKNOWN"
                        or c.load_semantics == "UNKNOWN"
                    )
                ):
                    raise ValueError("READY requires qualified executable selections")
                if (
                    isinstance(slot.prescription, BootstrapPrescription)
                    and not duration.covers_bootstrap
                ):
                    raise ValueError("READY duration must cover bootstrap preparation and trials")


def exported_schemas() -> dict[str, dict]:
    return {
        "FirstPlanRequest.v2.schema.json": FirstPlanRequestV2.model_json_schema(),
        "FirstPlanRecommendation.v2.schema.json": FirstPlanRecommendationV2.model_json_schema(),
    }
