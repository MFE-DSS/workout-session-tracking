"""V2 exchange consistency against the actual pinned, non-admitted authorities.

This is not a producer, authentication layer or positive-binding evaluator. Only
negative exchanges are supported by today's empty registry. A future admitted
producer requires a separately reviewed authority profile and runtime adapter.
"""

from __future__ import annotations

from tools.science_contracts.blueprint_first_plan_v2 import (
    BootstrapPrescription,
    FirstPlanRecommendationV2,
    ObservedSettingPrescription,
    UnknownDuration,
    assess_inputs,
    evaluation_fingerprint,
    request_fingerprint,
    validated_request,
)
from tools.science_initial_policy.admission_calibration import calibrate_for_admission
from tools.science_initial_policy.admission_registry import assert_trusted_admission_registry
from tools.science_initial_policy.calibration_time_contracts import normalized_record
from tools.science_initial_policy.curation import ELIGIBLE
from tools.science_initial_policy.v2_registry import assert_trusted


def _references(req, out, bundle):
    refs = bundle.references
    if (req.bundle_digest, req.effective_science_digest, req.versions.catalogue) != (
        bundle.bundle_digest,
        bundle.effective_science_digest,
        bundle.effective_catalogue_version,
    ):
        raise ValueError("request does not reference the pinned scientific bundle")
    for fact in (req.blueprint.excluded_exercise_ids,):
        for identity in fact.value or []:
            if identity not in refs.canonical_exercise_ids:
                raise ValueError("unknown exercise exclusion")
    equipment = req.blueprint.environment.equipment_items
    if any(e not in refs.equipment_item_ids for e in equipment.value or []):
        raise ValueError("unknown declared equipment item")
    if any(
        c.canonical_exercise_id not in refs.canonical_exercise_ids
        for c in req.blueprint.environment.exercise_confirmations
    ):
        raise ValueError("unknown exercise confirmation")
    if not set(out.confidence.evidence_refs) <= refs.evidence_refs:
        raise ValueError("unknown confidence evidence")


def _identity(req, out):
    for field in (
        "subject_ref",
        "snapshot_ref",
        "source_revision",
        "as_of",
        "bundle_digest",
        "effective_science_digest",
    ):
        if getattr(req, field) != getattr(out, field):
            raise ValueError(f"result {field} does not belong to this request")
    if (out.request_fingerprint, out.full_evaluation_fingerprint) != (
        request_fingerprint(req),
        evaluation_fingerprint(req),
    ):
        raise ValueError("request or full observation fingerprint mismatch")


def _negative_authority(req, out):
    # The historical producer emits v1, not this successor contract. Its version
    # must not be attached to a hand-authored v2 example as if it had emitted it.
    if any(
        (
            req.versions.engine,
            req.versions.policy,
            req.requested_binding_ref,
            out.engine_version,
            out.policy_version,
            out.binding_ref,
            out.binding_digest,
            out.admission_refs,
            out.revocation_check_ref,
        )
    ):
        raise ValueError("no producer or admitted binding supports the v2 exchange yet")
    if out.used_fields:
        raise ValueError("no v2 producer has consumed optional personalisation fields")
    expected = assess_inputs(req.blueprint)
    if out.assessment != expected:
        raise ValueError("assessment differs from canonical required inputs")
    state, code = {
        "CONFLICTING": ("CONFLICTING_DATA", "INPUT_CONFLICT"),
        "INSUFFICIENT": ("INSUFFICIENT_DATA", "REQUIRED_INPUT_MISSING"),
        "SUFFICIENT": ("POLICY_UNAVAILABLE", "POLICY_UNAVAILABLE"),
    }[expected.state]
    if out.status != state or not any(i.blocking and i.code == code for i in out.issues):
        raise ValueError(
            "negative result must preserve conflict/missing/policy precedence and blocker"
        )
    needed = set(expected.conflicting_fields or expected.missing_fields)
    reported = {f for i in out.issues if i.code == code and i.blocking for f in i.field_refs}
    if needed != reported:
        raise ValueError("input blockers must name the actual missing/conflicting fields")
    if out.confidence.feasibility != "UNKNOWN":
        raise ValueError("current non-admitted profile cannot assert plan feasibility")
    if out.candidate_plan is not None and expected.state != "SUFFICIENT":
        raise ValueError("incomplete/conflicting required inputs cannot carry a candidate draft")


def _candidate(candidate, slot, req, bundle):
    row = bundle.candidates.get(candidate.canonical_exercise_id)
    if row is None or row["intent_id"] != slot.intent_id or row["admission"] not in ELIGIBLE:
        raise ValueError("candidate is outside the curated intention or eligible pool")
    if candidate.context_ref != req.blueprint.environment.context_ref:
        raise ValueError("candidate belongs to another environment")
    if candidate.canonical_exercise_id in (req.blueprint.excluded_exercise_ids.value or []):
        raise ValueError("candidate is explicitly excluded")
    if (
        candidate.realization_ref is not None
        and candidate.realization_ref != row["realization_ref"]
    ):
        raise ValueError("candidate realization is not the pinned reviewed realization")
    if (
        candidate.realization_source_ref is not None
        and candidate.realization_source_ref != row["realization_ref"]
    ):
        raise ValueError("unsupported realization source")
    confirmations = [
        c
        for c in req.blueprint.environment.exercise_confirmations
        if c.canonical_exercise_id == candidate.canonical_exercise_id
        and c.context_ref == candidate.context_ref
    ]
    episodes = [
        ep
        for ep in req.episodes
        if ep.context.model_dump()
        == {k: getattr(candidate, k) for k in type(ep.context).model_fields}
    ]
    if candidate.compatibility in {"CONFIRMED", "NOT_REQUIRED"}:
        if any(c.state == "UNAVAILABLE" for c in confirmations) or any(
            ep.availability == "UNAVAILABLE" for ep in episodes
        ):
            raise ValueError("unavailable or conflicting environment cannot be called feasible")
    if candidate.compatibility == "NOT_REQUIRED":
        if candidate.canonical_exercise_id not in bundle.references.no_equipment_exercise_ids:
            raise ValueError("equipment requirements cannot be removed")
    elif candidate.compatibility == "CONFIRMED":
        source = candidate.compatibility_source_ref
        confirmed = source is not None and (
            any(c.state == "AVAILABLE" and c.provenance.source_ref == source for c in confirmations)
            or any(
                ep.availability == "AVAILABLE"
                and ep.context_provenance.source_ref == source
                and ep.context_provenance.recorded_at is not None
                and ep.context_provenance.origin in {"USER_REPORTED", "USER_OBSERVED"}
                and ep.context_provenance.acquisition
                in {"DECLARED", "DEVICE_MEASURED", "EXECUTION_LOG"}
                for ep in episodes
            )
        )
        if not confirmed:
            raise ValueError("confirmed candidate needs a matching direct context source")
    return row


def _observed(p, selected, req):
    if selected is None or p.context.model_dump() != {
        field: getattr(selected, field) for field in type(p.context).model_fields
    }:
        raise ValueError("observed prescription and selection have different contexts")
    ep = next((e for e in req.episodes if e.episode_id == p.episode_id), None)
    if ep is None or ep.context != p.context:
        raise ValueError("prescription episode does not belong to this context")
    value = calibrate_for_admission(ep, min_reps=p.dose.min_reps, max_reps=p.dose.max_reps)
    if (
        value["state"] != "CALIBRATED"
        or value["reference_event_id"] != p.event_id
        or value["observed_setting"] != p.setting.model_dump(mode="json")
    ):
        raise ValueError("setting is not the qualified currently accepted observed reference")
    events = sorted({e.event_id: e for e in ep.events}.values(), key=lambda e: e.sequence)
    accepted = [e for e in events if e.kind == "SETTING_ACCEPTED"]
    if not accepted or accepted[-1].event_id != p.acceptance_event_id:
        raise ValueError("acceptance event is not the current acceptance")


def _slot(slot, req, bundle):
    if slot.intent_id not in bundle.references.canonical_intent_ids:
        raise ValueError("unknown intention")
    candidates = ([slot.selected] if slot.selected else []) + list(slot.alternatives)
    ids = [c.canonical_exercise_id for c in candidates]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate selected/alternative exercise")
    for c in candidates:
        _candidate(c, slot, req, bundle)
    p, dose = slot.prescription, slot.prescription.dose
    if (
        dose.source_ref != bundle.dose["source_version"]
        or not set(dose.evidence_refs) <= bundle.references.evidence_refs
    ):
        raise ValueError("draft dose needs the exact historical source, not an admission label")
    if (dose.work_sets, dose.min_reps, dose.max_reps, dose.rir_target) != (
        bundle.dose["work_sets"],
        *bundle.dose["rep_range"],
        bundle.dose["rir_target"],
    ):
        raise ValueError("dose differs from the referenced historical convention")
    if slot.selected is not None:
        expected = bundle.dose["rest_seconds"][
            bundle.candidates[slot.selected.canonical_exercise_id]["joint_type"]
        ]
        if dose.rest_seconds != expected:
            raise ValueError("rest differs from the referenced convention")
    if isinstance(p, BootstrapPrescription):
        raise ValueError("bootstrap references have no admitted protocol in the current registry")
    if isinstance(p, ObservedSettingPrescription):
        _observed(p, slot.selected, req)


def _zones(plan, bundle):
    slots = {s.slot_id: s for session in plan.sessions for s in session.slots}
    for zone in plan.zone_reports:
        if zone.role_status == "NO_SUPPORTED_ROLE_IN_SELECTED_SET":
            raise ValueError("no admitted scoped absence basis exists in this registry")
        for c in zone.contributions:
            row = bundle.candidates[c.canonical_exercise_id]
            if row["requires_qualified_role_projection"]:
                # The G17 qualification cannot be inferred from a generic role
                # string. A future binding must explicitly qualify this overlay.
                raise ValueError("conditional pull role needs a reviewed projection binding")
            role = next((r for r in row["effective_roles"] if r["zone"] == zone.zone), None)
            if role is None or role["role"] != c.role or c.source_ref != row["realization_ref"]:
                raise ValueError("contribution is not the exact sourced qualitative role")
            if not set(c.evidence_refs) <= set(role["evidence_refs"]):
                raise ValueError("contribution cites evidence outside this role")
            if slots[c.slot_id].selected.realization_ref != c.realization_ref:
                raise ValueError("contribution realization mismatch")


def _plan(req, out, bundle):
    plan = out.candidate_plan
    if plan is None:
        return
    if plan.review_state != "DRAFT":
        raise ValueError("no authority has reviewed a v2 plan")
    budgets = req.blueprint.session_budgets_minutes.value
    if len(plan.sessions) > req.blueprint.sessions_per_week.value:
        raise ValueError("draft has more sessions than declared availability")
    for index, session in enumerate(plan.sessions):
        if session.duration.budget_minutes != budgets[index]:
            raise ValueError("duration budget differs from declared session availability")
        if not isinstance(session.duration, UnknownDuration):
            raise ValueError("no v2 temporal basis or diagnostic scope is bound yet")
        for slot in session.slots:
            _slot(slot, req, bundle)
    _zones(plan, bundle)


def validate_exchange(
    request, response, *, trusted_bundle, admission_registry
) -> FirstPlanRecommendationV2:
    """Revalidate model copies and all pins; never accept READY on empty authority.

    Owner fields are consistency references only. The future PLAN adapter must
    authenticate the owner and obtain the authoritative snapshot/consent status.
    No inference of an equipment inventory, anthropometry gate or missing policy.
    """
    assert_trusted(trusted_bundle)
    assert_trusted_admission_registry(admission_registry)
    req = validated_request(request)
    out = FirstPlanRecommendationV2.model_validate(normalized_record(response))
    _identity(req, out)
    _references(req, out, trusted_bundle)
    _negative_authority(req, out)
    _plan(req, out, trusted_bundle)
    return out
