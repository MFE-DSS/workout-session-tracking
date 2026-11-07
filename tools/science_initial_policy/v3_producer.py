"""Actual limited v3 producer; current observed settings, never a runtime route."""

from __future__ import annotations

from dataclasses import dataclass
from typing import get_args

from tools.science_contracts.blueprint_first_plan_v1 import REQUIRED_FIELDS, Zone
from tools.science_contracts.blueprint_first_plan_v2 import (
    AssessmentV2,
    BlockerV2,
    ObservedSettingPrescription,
    PlanV2,
    assess_inputs,
)
from tools.science_contracts.blueprint_first_plan_v3 import (
    FirstPlanRecommendationV3,
    evaluation_fingerprint,
    observation_fingerprint,
    plan_time_fingerprint,
    request_fingerprint,
    validated_request,
)
from tools.science_contracts.bootstrap_protocol_v3 import TimeAssessmentV3, assess_structural_time
from tools.science_initial_policy.admission_calibration import _current, calibrate_for_admission
from tools.science_initial_policy.v3_admission import V3Registry, assert_trusted_v3


@dataclass(frozen=True)
class Compilation:
    plan: PlanV2 | None
    time_assessments: tuple[TimeAssessmentV3, ...]
    issues: tuple[BlockerV2, ...]
    assessment: AssessmentV2
    used_fields: tuple[str, ...]


def _issue(code, reason, *, gate=None, fields=()):
    return BlockerV2(
        code=code,
        blocking=True,
        gate_ref=gate,
        source_refs=(),
        field_refs=tuple(fields),
        explanation=reason,
    )


def _request(raw, registry):
    assert_trusted_v3(registry, require_admitted=False)
    req = validated_request(raw)
    policy = registry.policy
    expected = (
        registry.bundle_digest,
        registry.effective_science_digest,
        registry.historical.effective_catalogue_version,
        policy["engine_version"],
        policy["policy_version"],
        registry.binding_ref,
    )
    actual = (
        req.bundle_digest,
        req.effective_science_digest,
        req.versions.catalogue,
        req.versions.engine,
        req.versions.policy,
        req.requested_binding_ref,
    )
    if actual != expected:
        raise ValueError("request does not bind the actual v3 policy/engine/science versions")
    for identity in req.blueprint.excluded_exercise_ids.value or ():
        if identity not in registry.historical.references.canonical_exercise_ids:
            raise ValueError("unknown canonical exercise exclusion")
    for row in req.blueprint.environment.exercise_confirmations:
        if row.canonical_exercise_id not in registry.historical.references.canonical_exercise_ids:
            raise ValueError("unknown canonical exercise confirmation")
    return req


def _assessment(req):
    used = (*REQUIRED_FIELDS,)
    if req.blueprint.excluded_exercise_ids.state in {"KNOWN", "CONFLICT"}:
        used += ("excluded_exercise_ids",)
    return assess_inputs(req.blueprint, used), used


def _qualified_order(ep, trial, acceptance):
    current = [e for e in ep.events if _current(e, ep.started_at)]

    def occurred(e):
        return e.provenance.measured_at or e.provenance.recorded_at

    trial_at = occurred(trial)
    if occurred(acceptance) < trial_at:
        return False
    contexts = [
        e
        for e in current
        if e.kind == "CONTEXT_CONFIRMED"
        and e.sequence < trial.sequence
        and occurred(e) <= trial_at
        and e.setting == trial.setting
    ]
    starts = [e.sequence for e in current if e.kind == "FAMILIARIZATION_STARTED"]
    if any(e.kind == "FAMILIARIZATION_STARTED" and occurred(e) > trial_at for e in current):
        return False
    if any(sequence > trial.sequence for sequence in starts):
        return False
    latest_start = max(starts, default=-1)
    familiar = trial.familiarization_confirmed is True or any(
        e.kind == "FAMILIARIZATION_CONFIRMED"
        and latest_start < e.sequence < trial.sequence
        and occurred(e) <= trial_at
        for e in current
    )
    return bool(contexts) and familiar


def _prescription(req, spec, registry):
    identity = spec["candidate_id"]
    matches = [e for e in req.episodes if e.context.canonical_exercise_id == identity]
    if len(matches) != 1:
        return None, _issue(
            "CALIBRATION_REQUIRED", "One current qualified context required: " + identity, gate="C3"
        )
    ep = matches[0]
    ctx = ep.context
    p = ep.context_provenance
    if (
        ep.availability != "AVAILABLE"
        or ctx.side != "BILATERAL"
        or ctx.realization_ref != spec["realization_ref"]
        or ctx.context_ref != req.blueprint.environment.context_ref
        or not all((ctx.context_ref, ctx.equipment_ref, ctx.realization_ref))
        or ctx.load_semantics == "UNKNOWN"
        or p.origin not in {"USER_REPORTED", "USER_OBSERVED"}
        or p.recorded_at is None
        or p.recorded_at < ep.started_at
        or (p.measured_at is not None and p.measured_at < ep.started_at)
    ):
        return None, _issue(
            "COMPATIBILITY_UNKNOWN",
            "Realization/device/current context not confirmed: " + identity,
            gate="C4",
        )
    confirmations = [
        c
        for c in req.blueprint.environment.exercise_confirmations
        if c.canonical_exercise_id == identity and c.context_ref == ctx.context_ref
    ]
    if any(c.state == "UNAVAILABLE" for c in confirmations):
        return None, _issue(
            "INPUT_CONFLICT",
            "Availability conflicts with the current observed context: " + identity,
            gate="C4",
        )
    dose = registry.policy["dose"]
    result = calibrate_for_admission(
        ep, min_reps=dose["rep_range"][0], max_reps=dose["rep_range"][1]
    )
    if result["state"] != "CALIBRATED":
        return None, _issue("CALIBRATION_REQUIRED", result["state"] + ": " + identity, gate="C3")
    events = {e.event_id: e for e in ep.events}
    trial = events[result["reference_event_id"]]
    accepted = sorted(
        (e for e in events.values() if e.kind == "SETTING_ACCEPTED" and _current(e, ep.started_at)),
        key=lambda e: e.sequence,
    )
    if (
        not accepted
        or not _qualified_order(ep, trial, accepted[-1])
        or not _current(trial, ep.started_at)
        or trial.provenance.origin != "USER_OBSERVED"
    ):
        return None, _issue(
            "CALIBRATION_REQUIRED",
            "Historical import is not a current observed qualification: " + identity,
            gate="C3",
        )
    if identity == "romanian-deadlift-halteres":
        allowed = {"PER_IMPLEMENT", "TOTAL_EXTERNAL"}
    else:
        allowed = {"MACHINE_DISPLAY_KG", "NON_MASS_SETTING", "TOTAL_EXTERNAL"}
    if ctx.load_semantics not in allowed:
        return None, _issue(
            "CONSTRAINT_VIOLATION",
            "Load meaning conflicts with the curated resistance realization: " + identity,
            gate="C4",
        )
    row = registry.historical.candidates[identity]
    prescription = ObservedSettingPrescription.model_validate(
        dict(
            mode="OBSERVED_SETTING",
            dose=dict(
                work_sets=dose["work_sets"],
                min_reps=dose["rep_range"][0],
                max_reps=dose["rep_range"][1],
                rir_target=dose["rir_target"],
                rest_seconds=dose["rest_seconds"][row["joint_type"]],
                source_ref=dose["source_version"],
                evidence_refs=list(dose["evidence_refs"]),
            ),
            episode_id=ep.episode_id,
            event_id=trial.event_id,
            acceptance_event_id=accepted[-1].event_id,
            context=ctx,
            setting=trial.setting,
        )
    )
    return (ep, prescription), None


def _zones(sessions, registry):
    result = []
    slots = [s for session in sessions for s in session["slots"]]
    for zone in get_args(Zone):
        known = []
        unknown = []
        for slot in slots:
            selected = slot["selected"]
            row = registry.historical.candidates[selected["canonical_exercise_id"]]
            role = next((r for r in row["effective_roles"] if r["zone"] == zone), None)
            if role is None or role["role"] == "UNKNOWN":
                unknown.append(slot["slot_id"])
                continue
            known.append(
                dict(
                    slot_id=slot["slot_id"],
                    canonical_exercise_id=selected["canonical_exercise_id"],
                    realization_ref=selected["realization_ref"],
                    role=role["role"],
                    source_ref=row["realization_ref"],
                    evidence_refs=list(role["evidence_refs"]),
                )
            )
        result.append(
            dict(
                zone=zone,
                role_status="SUPPORTED_ROLES" if known else "UNKNOWN",
                contributions=known,
                unresolved_slot_ids=unknown,
                absence_basis_ref=None,
                limitations=[
                    "Qualitative curated roles only; missing roles are unresolved, not biological zero."
                ],
            )
        )
    return result


def compile_plan_v3(request, registry: V3Registry) -> Compilation:
    req = _request(request, registry)
    assessment, used = _assessment(req)
    issues = []
    if assessment.state != "SUFFICIENT":
        code = "INPUT_CONFLICT" if assessment.conflicting_fields else "REQUIRED_INPUT_MISSING"
        issues = [
            _issue(
                code,
                assessment.state,
                fields=assessment.conflicting_fields or assessment.missing_fields,
            )
        ]
        return Compilation(None, (), tuple(issues), assessment, used)
    bp = req.blueprint
    scope = registry.policy["scope"]
    if (
        bp.objective.value != scope["objective"]
        or bp.population_scope.value != scope["population"]
        or bp.sessions_per_week.value not in scope["cadences"]
        or bp.limitations.value
    ):
        issues = [
            _issue(
                "CONSTRAINT_VIOLATION",
                "Outside the limited adult/nonclinical/two-session/no-limitations scope",
                gate="C1",
            )
        ]
        return Compilation(None, (), tuple(issues), assessment, used)
    excluded = set(bp.excluded_exercise_ids.value or ())
    qualified = []
    for spec in registry.policy["selection"]:
        if spec["candidate_id"] in excluded:
            issues.append(
                _issue(
                    "NO_FEASIBLE_PLAN", "A selected realization is explicitly excluded", gate="C4"
                )
            )
            continue
        item, issue = _prescription(req, spec, registry)
        if issue:
            issues.append(issue)
        else:
            qualified.append((spec, *item))
    if issues:
        return Compilation(None, (), tuple(issues), assessment, used)
    sessions = []
    times = []
    for index, budget in enumerate(bp.session_budgets_minutes.value):
        session_id = f"session-{index + 1}"
        slots = []
        for position, (spec, ep, prescription) in enumerate(qualified):
            slots.append(
                dict(
                    slot_id=f"{session_id}-slot-{position + 1}",
                    intent_id=spec["intent_id"],
                    selected=dict(
                        ep.context.model_dump(),
                        compatibility="CONFIRMED",
                        compatibility_source_ref=ep.context_provenance.source_ref,
                        realization_source_ref=spec["realization_ref"],
                    ),
                    alternatives=[],
                    substitution_rule_ref=registry.policy["withdrawal_rule"],
                    prescription=prescription.model_dump(mode="json"),
                    rationale="Reviewed initial intention and a currently accepted observed setting; not an individual optimum.",
                )
            )
        source = dict(
            session_id=session_id,
            slots=[{"prescription": s["prescription"]["dose"]} for s in slots],
        )
        time = assess_structural_time(
            source, budget_minutes=budget, structure=registry.policy["time"]["structure"]
        )
        if time.state == "STRUCTURALLY_TOO_LONG":
            issues.append(
                _issue(
                    "CONSTRAINT_VIOLATION",
                    "Applicable rest floor consumes the declared budget",
                    gate="C6",
                )
            )
        times.append(time)
        sessions.append(
            dict(session_id=session_id, slots=slots, duration=time.duration.model_dump(mode="json"))
        )
    if issues:
        return Compilation(None, (), tuple(issues), assessment, used)
    plan = PlanV2.model_validate(
        dict(
            allocation_ref=registry.binding_ref + "@" + registry.binding_digest,
            review_state="REVIEWED" if registry.admitted else "DRAFT",
            sessions=sessions,
            physical_work_sets_total=sum(
                s["prescription"]["dose"]["work_sets"] for row in sessions for s in row["slots"]
            ),
            zone_model_version="zones-15-v1",
            coverage_report_complete=True,
            zone_reports=_zones(sessions, registry),
        )
    )
    return Compilation(plan, tuple(times), (), assessment, used)


def produce_v3(request, registry: V3Registry) -> FirstPlanRecommendationV3:
    assert_trusted_v3(registry)
    req = _request(request, registry)
    compiled = compile_plan_v3(req, registry)
    plan = compiled.plan
    if plan is None and req.acknowledgment is not None:
        raise ValueError("acknowledgment cannot belong to an unavailable plan")
    if plan is not None:
        state = "SCIENTIFICALLY_READY"
    elif compiled.assessment.state != "SUFFICIENT":
        state = (
            "CONFLICTING_DATA" if compiled.assessment.conflicting_fields else "INSUFFICIENT_DATA"
        )
    elif any(i.gate_ref in {"C1", "C6"} for i in compiled.issues):
        state = "CONSTRAINT_UNSATISFIABLE"
    else:
        state = "REVIEW_REQUIRED"
    policy = registry.policy
    ack = req.acknowledgment
    return FirstPlanRecommendationV3.model_validate(
        dict(
            contract_version="first-plan-recommendation/3.0.0",
            subject_ref=req.subject_ref,
            snapshot_ref=req.snapshot_ref,
            source_revision=req.source_revision,
            as_of=req.as_of,
            generated_at=max(req.as_of, ack.acknowledged_at) if ack else req.as_of,
            request_fingerprint=request_fingerprint(req),
            observation_fingerprint=observation_fingerprint(req),
            full_evaluation_fingerprint=evaluation_fingerprint(req),
            bundle_digest=registry.bundle_digest,
            effective_science_digest=registry.effective_science_digest,
            engine_version=policy["engine_version"],
            policy_version=policy["policy_version"],
            binding_ref=registry.binding_ref,
            binding_digest=registry.binding_digest,
            admission_refs=[policy["admission"]["decision_ref"], policy["admission"]["review_ref"]],
            revocation_check_ref=policy["registry_version"]
            + "@"
            + registry.registry_digest
            + "#"
            + registry.binding_ref,
            assessment=compiled.assessment,
            used_fields=list(compiled.used_fields),
            scientific_readiness=state,
            scientific_issues=list(compiled.issues),
            candidate_plan=plan,
            time_assessments=compiled.time_assessments,
            start_permission=("ELIGIBLE" if ack else "REQUIRES_TIME_ACK") if plan else "DENIED",
            start_policy_ref=policy["time"]["start_policy_ref"] if plan else None,
            acknowledgment=ack,
            plan_time_fingerprint=plan_time_fingerprint(plan, compiled.time_assessments)
            if plan
            else None,
            confidence=dict(
                individual_response="NOT_ESTIMATED",
                feasibility="CONFIRMED" if plan else "UNKNOWN",
                evidence_refs=list(policy["dose"]["evidence_refs"]),
                limitations=[
                    "Observed setting accepted provisionally, not measured true RIR or individual optimum.",
                    "Uncertain time including preparation/operations; no guarantee of completing the plan in budget.",
                    "Qualitative roles with unresolved regions; no clinical clearance, runtime or session command.",
                ],
            ),
        )
    )
