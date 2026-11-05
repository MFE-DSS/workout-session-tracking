"""SCI-P01/02 proposed DTOs and contract invariants. No prescription engine or I/O.

Approval of a policy is supplied by an authoritative caller's frozen registry,
never inferred from a label in a request. No production module imports this file.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Annotated, Generic, Literal, Self, TypeVar

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictFloat,
    StrictInt,
    StrictStr,
    model_validator,
)

T = TypeVar("T")
Text = Annotated[StrictStr, Field(min_length=1)]
PositiveInt = Annotated[StrictInt, Field(gt=0)]
PositiveNumber = Annotated[StrictFloat, Field(gt=0)]
Cadence = Annotated[StrictInt, Field(ge=1, le=7)]
NonNegativeInt = Annotated[StrictInt, Field(ge=0)]
Zone = Literal[
    "pecs",
    "lats",
    "upper_back",
    "anterior_delts",
    "lateral_delts",
    "rear_delts",
    "biceps",
    "triceps",
    "quads",
    "hamstrings",
    "glutes",
    "adductors",
    "calves",
    "abs",
    "hip_flexors",
]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Provenance(Contract):
    origin: Literal[
        "USER_REPORTED",
        "USER_OBSERVED",
        "DERIVED_FROM_HISTORY",
        "POPULATION_PRIOR",
        "PRODUCT_CONTRACT",
        "UNKNOWN",
    ]
    acquisition: Literal[
        "DECLARED", "SELF_MEASURED", "DEVICE_MEASURED", "EXECUTION_LOG", "DERIVED", "UNKNOWN"
    ]
    source_ref: Text | None
    recorded_at: AwareDatetime | None
    measured_at: AwareDatetime | None


class ConflictingValue(Contract, Generic[T]):
    value: T
    source_ref: Text


class Fact(Contract, Generic[T]):
    state: Literal["KNOWN", "UNKNOWN", "CONFLICT", "WITHHELD"]
    value: T | None
    provenance: Provenance
    conflicts: tuple[ConflictingValue[T], ...]

    @model_validator(mode="after")
    def fact_state(self) -> Self:
        if self.state == "KNOWN":
            if (
                self.value is None
                or self.provenance.source_ref is None
                or self.provenance.origin == "UNKNOWN"
                or self.provenance.acquisition == "UNKNOWN"
            ):
                raise ValueError("known fact requires value and source provenance")
        elif self.value is not None:
            raise ValueError("unknown/conflicting/withheld fact cannot assert a value")
        if self.state == "CONFLICT":
            values = {json.dumps(v.value, sort_keys=True) for v in self.conflicts}
            if len({v.source_ref for v in self.conflicts}) < 2:
                raise ValueError("conflict requires distinct source references")
            if len(values) < 2:
                raise ValueError("conflict requires two distinct sourced values")
        elif self.conflicts:
            raise ValueError("conflict alternatives require CONFLICT state")
        return self


class ExerciseConfirmation(Contract):
    canonical_exercise_id: Text
    context_ref: Text
    state: Literal["AVAILABLE", "UNAVAILABLE", "UNKNOWN"]
    provenance: Provenance

    @model_validator(mode="after")
    def confirmation_source(self) -> Self:
        p = self.provenance
        if self.state != "UNKNOWN" and (
            p.origin not in {"USER_REPORTED", "USER_OBSERVED"}
            or p.acquisition not in {"DECLARED", "DEVICE_MEASURED", "EXECUTION_LOG"}
            or p.source_ref is None
            or p.recorded_at is None
        ):
            raise ValueError("known confirmation requires full direct source provenance")
        return self


class Environment(Contract):
    context_ref: Text
    description: Fact[Text]
    equipment_items: Fact[list[Text]]
    exercise_confirmations: list[ExerciseConfirmation]

    @model_validator(mode="after")
    def environmental_source(self) -> Self:
        for fact in (self.description, self.equipment_items):
            if fact.state == "KNOWN" and fact.provenance.origin not in {
                "USER_REPORTED",
                "USER_OBSERVED",
            }:
                raise ValueError("known environment cannot be assumed from a prior or history")
        return self


class Observation(Contract):
    kind: Literal["MEASUREMENT_TREND", "EXECUTION_TREND", "FUNCTIONAL_REPORT"]
    fact: Fact[Text]
    interpretation: Literal["OBSERVED", "INFERRED"]
    evidence_refs: list[Text]


class Blueprint(Contract):
    contract_version: Literal["body-training-blueprint/1.0.0"]
    snapshot_id: Text
    objective: Fact[Literal["HYPERTROPHY"]]
    population_scope: Fact[Literal["ADULT_NON_CLINICAL"]]
    sessions_per_week: Fact[Cadence]
    session_budgets_minutes: Fact[list[PositiveInt]]
    experience: Fact[Literal["REPORTED_UNTRAINED", "REPORTED_TRAINING", "RETURNING_AFTER_BREAK"]]
    limitations: Fact[list[Text]]
    excluded_exercise_ids: Fact[list[Text]]
    declared_priorities: Fact[
        list[Literal["pecs", "shoulders", "back_width", "back_thickness", "arms", "lower"]]
    ]
    height_cm: Fact[PositiveNumber]
    weight_kg: Fact[PositiveNumber]
    legacy_weight_kg: Fact[PositiveNumber]
    observations: list[Observation]
    environment: Environment

    @model_validator(mode="after")
    def snapshot_semantics(self) -> Self:
        cadence, budgets = self.sessions_per_week, self.session_budgets_minutes
        if cadence.state == budgets.state == "KNOWN" and len(budgets.value or []) != cadence.value:
            raise ValueError("one time budget is required per declared session")
        if self.legacy_weight_kg.provenance.measured_at is not None:
            raise ValueError("legacy undated weight cannot acquire a measurement date")
        if self.weight_kg.provenance.source_ref == "users.weight_kg":
            raise ValueError("legacy profile weight is not a dated weight measurement")
        if self.weight_kg.state == "KNOWN" and self.weight_kg.provenance.measured_at is None:
            raise ValueError("dated weight requires its measurement time")
        personal_fields = (
            "population_scope",
            "sessions_per_week",
            "session_budgets_minutes",
            "experience",
            "limitations",
            "excluded_exercise_ids",
            "declared_priorities",
            "height_cm",
            "weight_kg",
            "legacy_weight_kg",
        )
        for name in personal_fields:
            value = getattr(self, name)
            if value.state == "KNOWN" and value.provenance.origin in {
                "POPULATION_PRIOR",
                "PRODUCT_CONTRACT",
            }:
                raise ValueError("a population prior is not a known personal fact")
        for name in (
            "sessions_per_week",
            "session_budgets_minutes",
            "limitations",
            "declared_priorities",
        ):
            value = getattr(self, name)
            if value.state == "KNOWN" and value.provenance.origin != "USER_REPORTED":
                raise ValueError("personal availability and preferences require user declaration")
        for name in ("excluded_exercise_ids", "declared_priorities"):
            value = getattr(self, name).value
            if value is not None and len(value) != len(set(value)):
                raise ValueError(f"duplicate {name}")
        return self


class Policies(Contract):
    state: Literal["UNAVAILABLE", "PROPOSED", "APPROVED"]
    dose_id: Text | None
    time_id: Text | None
    selection_id: Text | None
    taxonomy_projection_id: Text | None
    review_ref: Text | None

    @property
    def ids(self) -> tuple[str | None, ...]:
        return (self.dose_id, self.time_id, self.selection_id, self.taxonomy_projection_id)


class Versions(Contract):
    catalogue: Text
    zones: Literal["zones-15-v1"]
    credit: Literal["sci-exposure-credit-v1"]
    engine: Text | None


class FirstPlanRequest(Contract):
    contract_version: Literal["first-plan-request/1.0.0"]
    as_of: AwareDatetime
    requirement_profile_id: Literal["first-bodybuilding-inputs-v1-proposed"]
    blueprint: Blueprint
    policies: Policies
    versions: Versions

    @model_validator(mode="after")
    def temporal_boundary(self) -> Self:
        for provenance in _provenances(self.blueprint):
            if any(
                t is not None and t > self.as_of
                for t in (provenance.recorded_at, provenance.measured_at)
            ):
                raise ValueError("future provenance cannot be used before as_of")
        return self


def _provenances(value):
    if isinstance(value, Provenance):
        yield value
    elif isinstance(value, BaseModel):
        for name in type(value).model_fields:
            yield from _provenances(getattr(value, name))
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _provenances(item)


class InputAssessment(Contract):
    state: Literal["SUFFICIENT", "INSUFFICIENT", "CONFLICTING"]
    requirement_profile_id: Literal["first-bodybuilding-inputs-v1-proposed"]
    missing_fields: tuple[Text, ...]
    conflicting_fields: tuple[Text, ...]


REQUIRED_FIELDS = (
    "objective",
    "population_scope",
    "sessions_per_week",
    "session_budgets_minutes",
    "limitations",
)
FACT_FIELDS = frozenset(
    REQUIRED_FIELDS
    + (
        "experience",
        "excluded_exercise_ids",
        "declared_priorities",
        "height_cm",
        "weight_kg",
        "legacy_weight_kg",
    )
)


def input_assessment(blueprint: Blueprint, used_fields: tuple[str, ...] = ()) -> InputAssessment:
    fields = tuple(dict.fromkeys((*REQUIRED_FIELDS, *used_fields)))
    if not set(fields) <= FACT_FIELDS:
        raise ValueError("unknown Blueprint field reference")
    conflicting = tuple(f for f in fields if getattr(blueprint, f).state == "CONFLICT")
    missing = tuple(f for f in fields if getattr(blueprint, f).state in {"UNKNOWN", "WITHHELD"})
    return InputAssessment(
        state="CONFLICTING" if conflicting else "INSUFFICIENT" if missing else "SUFFICIENT",
        requirement_profile_id="first-bodybuilding-inputs-v1-proposed",
        missing_fields=missing,
        conflicting_fields=conflicting,
    )


class Issue(Contract):
    code: Literal[
        "INPUT_CONFLICT",
        "REQUIRED_INPUT_MISSING",
        "POLICY_UNAVAILABLE",
        "NO_FEASIBLE_PLAN",
        "COMPATIBILITY_UNKNOWN",
        "TIME_UNCERTAIN",
        "CATALOG_GAP",
        "CONSTRAINT_VIOLATION",
    ]
    blocking: StrictBool
    field_refs: list[Text]
    explanation: Text


class Prescription(Contract):
    work_sets: PositiveInt
    min_reps: PositiveInt
    max_reps: PositiveInt
    rir_target: Annotated[StrictFloat, Field(ge=0)] | None
    rest_seconds: PositiveInt | None
    load_kg: Annotated[StrictFloat, Field(ge=0)] | None
    load_mode: Literal["CALIBRATION_REQUIRED", "HISTORY_SUPPORTED", "NOT_DEFINED"]
    source_kind: Literal["LEGACY_TEMPLATE", "REVIEWED_POLICY", "CONTRACT_EXAMPLE"]
    source_ref: Text
    dose_policy_ref: Text | None
    evidence_refs: list[Text]

    @model_validator(mode="after")
    def rep_range(self) -> Self:
        if self.min_reps > self.max_reps:
            raise ValueError("repetition bounds reversed")
        if self.load_mode == "CALIBRATION_REQUIRED" and self.load_kg is not None:
            raise ValueError("calibration is not a known starting load")
        return self


class Candidate(Contract):
    canonical_exercise_id: Text
    compatibility: Literal["CONFIRMED", "NOT_REQUIRED", "UNKNOWN", "UNAVAILABLE"]
    compatibility_source_ref: Text | None
    context_ref: Text


class Slot(Contract):
    slot_id: Text
    intent_id: Text
    selected: Candidate | None
    alternatives: list[Candidate]
    substitution_rule_ref: Text
    prescription: Prescription
    rationale: Text


class Duration(Contract):
    budget_minutes: PositiveInt
    state: Literal["UNKNOWN", "ESTIMATED"]
    lower_minutes: Annotated[StrictFloat, Field(ge=0)] | None
    upper_minutes: Annotated[StrictFloat, Field(ge=0)] | None
    model_ref: Text | None
    basis_refs: list[Text]

    @model_validator(mode="after")
    def estimate(self) -> Self:
        if self.state == "UNKNOWN" and any(
            v is not None for v in (self.lower_minutes, self.upper_minutes, self.model_ref)
        ):
            raise ValueError("unknown duration cannot carry an invented estimate")
        if self.state == "ESTIMATED" and (
            self.lower_minutes is None
            or self.upper_minutes is None
            or self.model_ref is None
            or not self.basis_refs
            or self.lower_minutes > self.upper_minutes
        ):
            raise ValueError("duration estimate requires model, basis and ordered bounds")
        return self


class Session(Contract):
    session_id: Text
    slots: Annotated[list[Slot], Field(min_length=1)]
    duration: Duration


class Exposure(Contract):
    zone: Zone
    raw_primary_sets: NonNegativeInt
    raw_secondary_sets: NonNegativeInt
    unknown_role_sets: NonNegativeInt
    credited_sets: Annotated[StrictFloat, Field(ge=0)] | None
    bound: Literal["EXACT", "LOWER_BOUND", "UNKNOWN"]

    @model_validator(mode="after")
    def unknown_credit(self) -> Self:
        if self.bound == "UNKNOWN" and self.credited_sets is not None:
            raise ValueError("unknown exposure cannot become zero")
        if self.bound == "EXACT" and (self.unknown_role_sets or self.credited_sets is None):
            raise ValueError("unknown role prevents an exact exposure")
        return self


class Plan(Contract):
    archetype_ref: Text
    review_state: Literal["LEGACY_UNVALIDATED", "REVIEWED"]
    sessions: Annotated[list[Session], Field(min_length=1)]
    physical_work_sets_total: PositiveInt
    zone_model_version: Literal["zones-15-v1"]
    credit_policy_version: Literal["sci-exposure-credit-v1"]
    exposure_complete: StrictBool
    zone_exposure: list[Exposure]

    @model_validator(mode="after")
    def accounting(self) -> Self:
        slots = [s for session in self.sessions for s in session.slots]
        if (
            not slots
            or sum(s.prescription.work_sets for s in slots) != self.physical_work_sets_total
        ):
            raise ValueError("physical set total must equal prescribed slots")
        if len({s.slot_id for s in slots}) != len(slots) or len(
            {s.session_id for s in self.sessions}
        ) != len(self.sessions):
            raise ValueError("duplicate plan identifiers")
        zones = [e.zone for e in self.zone_exposure]
        if len(zones) != len(set(zones)):
            raise ValueError("duplicate exposure zones")
        from typing import get_args

        if self.exposure_complete and (
            set(zones) != set(get_args(Zone)) or any(e.bound != "EXACT" for e in self.zone_exposure)
        ):
            raise ValueError("complete exposure requires all fifteen zones with exact bounds")
        return self


class Confidence(Contract):
    individual_response: Literal["NOT_ESTIMATED"]
    feasibility: Literal["UNKNOWN", "MIXED", "CONFIRMED", "NOT_FEASIBLE"]
    evidence_refs: list[Text]
    limitations: list[Text]


class FirstPlanRecommendation(Contract):
    contract_version: Literal["first-plan-recommendation/1.0.0"]
    request_fingerprint: Annotated[StrictStr, Field(pattern="^[0-9a-f]{64}$")]
    status: Literal[
        "INSUFFICIENT_DATA",
        "CONFLICTING_DATA",
        "POLICY_UNAVAILABLE",
        "CONSTRAINT_UNSATISFIABLE",
        "REVIEW_REQUIRED",
        "READY",
    ]
    engine_version: Text | None
    assessment: InputAssessment
    issues: list[Issue]
    used_fields: list[Text]
    candidate_plan: Plan | None
    confidence: Confidence


@dataclass(frozen=True)
class ReferenceSnapshot:
    catalogue_version: str
    evidence_refs: frozenset[str]
    canonical_exercise_ids: frozenset[str]
    canonical_intent_ids: frozenset[str]
    equipment_item_ids: frozenset[str]
    approved_policy_refs: frozenset[str]
    no_equipment_exercise_ids: frozenset[str]


def decision_fingerprint(request: FirstPlanRequest) -> str:
    content = request.model_dump(mode="json")
    content["blueprint"].pop("snapshot_id")  # snapshot event identity is not decision content
    for key in ("limitations", "excluded_exercise_ids"):
        value = content["blueprint"][key]["value"]
        if value is not None:
            content["blueprint"][key]["value"] = sorted(value)
    items = content["blueprint"]["environment"]["equipment_items"]["value"]
    if items is not None:
        content["blueprint"]["environment"]["equipment_items"]["value"] = sorted(items)
    encoded = json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode()).hexdigest()


def _policy_available(request: FirstPlanRequest, references: ReferenceSnapshot) -> bool:
    p = request.policies
    return (
        request.versions.engine is not None
        and p.state == "APPROVED"
        and bool(p.review_ref)
        and all(i is not None and i in references.approved_policy_refs for i in p.ids)
    )


def validate_exchange(
    request: FirstPlanRequest | dict,
    response: FirstPlanRecommendation | dict,
    *,
    references: ReferenceSnapshot,
) -> FirstPlanRecommendation:
    """Check proposed exchange consistency; never choose exercises or generate prescriptions."""
    req = (
        request
        if isinstance(request, FirstPlanRequest)
        else FirstPlanRequest.model_validate(request)
    )
    out = (
        response
        if isinstance(response, FirstPlanRecommendation)
        else FirstPlanRecommendation.model_validate(response)
    )
    if req.versions.catalogue != references.catalogue_version:
        raise ValueError("catalogue version does not match frozen references")
    if out.request_fingerprint != decision_fingerprint(req):
        raise ValueError("request fingerprint mismatch")
    assessment = input_assessment(req.blueprint, tuple(out.used_fields))
    if assessment != out.assessment:
        raise ValueError("input conflict/missing assessment mismatch")
    codes = {i.code for i in out.issues if i.blocking}
    expected = (
        "CONFLICTING_DATA"
        if assessment.conflicting_fields
        else "INSUFFICIENT_DATA"
        if assessment.missing_fields
        else "POLICY_UNAVAILABLE"
        if not _policy_available(req, references)
        else "CONSTRAINT_UNSATISFIABLE"
        if "NO_FEASIBLE_PLAN" in codes
        else "REVIEW_REQUIRED"
        if codes
        else "READY"
    )
    if out.status != expected:
        raise ValueError(f"status must be {expected}")
    required_codes = ({"INPUT_CONFLICT"} if assessment.conflicting_fields else set()) | (
        {"REQUIRED_INPUT_MISSING"} if assessment.missing_fields else set()
    )
    if not _policy_available(req, references):
        required_codes.add("POLICY_UNAVAILABLE")
    if not required_codes <= codes:
        raise ValueError("missing explicit blocker codes")
    _validate_references(req, out, references)
    if out.candidate_plan:
        _validate_plan(req, out, references, codes)
    _validate_feasibility_claim(req, out, codes)
    return out


def _validate_references(
    req: FirstPlanRequest, out: FirstPlanRecommendation, references: ReferenceSnapshot
) -> None:
    if not set(out.used_fields) <= FACT_FIELDS:
        raise ValueError("unknown Blueprint field reference")
    for issue in out.issues:
        if not set(issue.field_refs) <= FACT_FIELDS:
            raise ValueError("unknown issue field reference")
    evidence = set(out.confidence.evidence_refs)
    for observation in req.blueprint.observations:
        evidence.update(observation.evidence_refs)
    if out.candidate_plan:
        for session in out.candidate_plan.sessions:
            for slot in session.slots:
                evidence.update(slot.prescription.evidence_refs)
    if not evidence <= references.evidence_refs:
        raise ValueError("nonexistent evidence reference")
    env = req.blueprint.environment
    if (
        env.equipment_items.value is not None
        and not set(env.equipment_items.value) <= references.equipment_item_ids
    ):
        raise ValueError("unknown equipment item, not a capability")
    excluded = req.blueprint.excluded_exercise_ids.value
    if excluded is not None and not set(excluded) <= references.canonical_exercise_ids:
        raise ValueError("unknown excluded exercise identity")
    for confirmation in env.exercise_confirmations:
        if (
            confirmation.canonical_exercise_id not in references.canonical_exercise_ids
            or confirmation.context_ref != env.context_ref
        ):
            raise ValueError("confirmation identity or context mismatch")


def _validate_feasibility_claim(
    req: FirstPlanRequest, out: FirstPlanRecommendation, codes: set[str]
) -> None:
    if out.status == "READY" and (
        out.candidate_plan is None
        or req.versions.engine is None
        or out.engine_version != req.versions.engine
    ):
        raise ValueError("READY requires plan and actual engine version")
    if out.status == "CONSTRAINT_UNSATISFIABLE" and out.candidate_plan is not None:
        raise ValueError("no feasible plan cannot carry an executable candidate")
    if out.confidence.feasibility == "CONFIRMED":
        selected = (
            []
            if out.candidate_plan is None
            else [
                slot.selected for session in out.candidate_plan.sessions for slot in session.slots
            ]
        )
        if not selected or any(
            c is None or c.compatibility not in {"CONFIRMED", "NOT_REQUIRED"} for c in selected
        ):
            raise ValueError("confirmed feasibility requires a resolved candidate plan")
    if out.confidence.feasibility == "NOT_FEASIBLE" and "NO_FEASIBLE_PLAN" not in codes:
        raise ValueError("infeasibility needs an explicit proven constraint blocker")


def _validate_candidate(
    candidate: Candidate, req: FirstPlanRequest, references: ReferenceSnapshot
) -> None:
    if (
        candidate.canonical_exercise_id not in references.canonical_exercise_ids
        or candidate.context_ref != req.blueprint.environment.context_ref
    ):
        raise ValueError("candidate identity or context mismatch")
    if (
        candidate.compatibility == "NOT_REQUIRED"
        and candidate.canonical_exercise_id not in references.no_equipment_exercise_ids
    ):
        raise ValueError("equipment requirements cannot be silently removed")
    if candidate.compatibility in {"CONFIRMED", "NOT_REQUIRED"}:
        states = {
            c.state
            for c in req.blueprint.environment.exercise_confirmations
            if c.canonical_exercise_id == candidate.canonical_exercise_id
            and c.context_ref == candidate.context_ref
        }
        if "UNAVAILABLE" in states:
            raise ValueError("conflicting or unavailable context confirmations require resolution")
    if candidate.compatibility == "CONFIRMED":
        confirmed = any(
            c.canonical_exercise_id == candidate.canonical_exercise_id
            and c.context_ref == candidate.context_ref
            and c.state == "AVAILABLE"
            and c.provenance.source_ref == candidate.compatibility_source_ref
            and c.provenance.origin in {"USER_REPORTED", "USER_OBSERVED"}
            and c.provenance.recorded_at is not None
            for c in req.blueprint.environment.exercise_confirmations
        )
        if candidate.compatibility_source_ref is None or not confirmed:
            raise ValueError("confirmed compatibility requires a matching context confirmation")


def _validate_slot(
    slot: Slot, req: FirstPlanRequest, references: ReferenceSnapshot, codes: set[str]
) -> None:
    if slot.selected is None and "CATALOG_GAP" not in codes:
        raise ValueError("an unfilled slot requires an explicit coverage gap")
    if slot.intent_id not in references.canonical_intent_ids:
        raise ValueError("unknown slot intention")
    for candidate in ([slot.selected] if slot.selected else []) + slot.alternatives:
        _validate_candidate(candidate, req, references)
    if slot.selected and slot.selected.canonical_exercise_id in set(
        req.blueprint.excluded_exercise_ids.value or []
    ):
        raise ValueError("selected exercise excluded by a hard constraint")
    if (
        slot.selected
        and slot.selected.compatibility in {"UNKNOWN", "UNAVAILABLE"}
        and not codes.intersection({"COMPATIBILITY_UNKNOWN", "CONSTRAINT_VIOLATION"})
    ):
        raise ValueError("unresolved compatibility requires explicit blocker")


def _validate_ready_plan(req: FirstPlanRequest, out: FirstPlanRecommendation) -> None:
    plan = out.candidate_plan
    assert plan is not None
    if (
        plan.review_state != "REVIEWED"
        or not plan.exposure_complete
        or len(plan.sessions) != req.blueprint.sessions_per_week.value
    ):
        raise ValueError("READY requires reviewed, complete, cadence-matched allocation")
    if out.confidence.feasibility != "CONFIRMED":
        raise ValueError("READY feasibility cannot be unknown")
    for session in plan.sessions:
        d = session.duration
        if (
            d.state != "ESTIMATED"
            or d.model_ref != req.policies.time_id
            or d.upper_minutes is None
            or d.upper_minutes > d.budget_minutes
        ):
            raise ValueError("READY requires supported duration within budget")
        for slot in session.slots:
            if slot.selected is None or slot.selected.compatibility not in {
                "CONFIRMED",
                "NOT_REQUIRED",
            }:
                raise ValueError("READY requires a feasible selection for every slot")
            p = slot.prescription
            if (
                p.source_kind == "CONTRACT_EXAMPLE"
                or p.dose_policy_ref != req.policies.dose_id
                or p.rir_target is None
                or p.rest_seconds is None
                or p.load_mode == "NOT_DEFINED"
            ):
                raise ValueError("READY requires a traced complete prescription")


def _validate_plan(
    req: FirstPlanRequest,
    out: FirstPlanRecommendation,
    references: ReferenceSnapshot,
    codes: set[str],
) -> None:
    plan = out.candidate_plan
    assert plan is not None
    budgets = req.blueprint.session_budgets_minutes.value
    for n, session in enumerate(plan.sessions):
        d = session.duration
        if d.state == "ESTIMATED" and (
            d.model_ref != req.policies.time_id
            or d.model_ref not in references.approved_policy_refs
        ):
            raise ValueError("estimated duration requires an approved time model")
        if budgets is not None and (n >= len(budgets) or d.budget_minutes != budgets[n]):
            raise ValueError("session budget differs from declared availability")
        for slot in session.slots:
            _validate_slot(slot, req, references, codes)
    if out.status == "READY":
        _validate_ready_plan(req, out)


def exported_schemas() -> dict[str, dict]:
    models = {
        "body_training_blueprint.v1": Blueprint,
        "first_plan_request.v1": FirstPlanRequest,
        "first_plan_recommendation.v1": FirstPlanRecommendation,
    }
    return {
        name: {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": f"urn:auren:science:{name}",
            **model.model_json_schema(),
        }
        for name, model in models.items()
    }
