"""Canonical admitted-profile invariants and strict replay, not the historical negative validator."""

from __future__ import annotations

from tools.science_contracts.blueprint_first_plan_v1 import REQUIRED_FIELDS
from tools.science_contracts.blueprint_first_plan_v2 import assess_inputs
from tools.science_contracts.blueprint_first_plan_v3 import (
    FirstPlanRecommendationV3,
    evaluation_fingerprint,
    observation_fingerprint,
    plan_time_fingerprint,
    request_fingerprint,
    validated_request,
)
from tools.science_contracts.bootstrap_protocol_v3 import assess_structural_time, strict_record
from tools.science_contracts.first_plan_v2_validation import _slot
from tools.science_initial_policy.admission_calibration import _current
from tools.science_initial_policy.v3_admission import assert_trusted_v3, encoded


def _check_phase_order(ep, trial, acceptance):
    commands = sorted(
        (e for e in ep.events if _current(e, ep.started_at)), key=lambda e: e.sequence
    )
    trial_at = trial.provenance.measured_at
    if (acceptance.provenance.measured_at or acceptance.provenance.recorded_at) < trial_at:
        raise ValueError("acceptance occurred before its observed trial")
    context_ready = False
    familiar_ready = False
    for event in commands:
        if event.sequence >= trial.sequence:
            break
        occurred = event.provenance.measured_at or event.provenance.recorded_at
        if occurred > trial_at:
            continue
        if event.kind == "CONTEXT_CONFIRMED" and event.setting == trial.setting:
            context_ready = True
        elif event.kind == "FAMILIARIZATION_STARTED":
            familiar_ready = False
        elif event.kind == "FAMILIARIZATION_CONFIRMED":
            familiar_ready = True
    restart_after = any(
        e.kind == "FAMILIARIZATION_STARTED"
        and (
            e.sequence > trial.sequence
            or (e.provenance.measured_at or e.provenance.recorded_at) > trial_at
        )
        for e in commands
    )
    if (
        not context_ready
        or not (familiar_ready or trial.familiarization_confirmed is True)
        or restart_after
    ):
        raise ValueError(
            "trial not preceded by applicable context and familiarization, or restarted"
        )


def _observed_slot(req, slot, spec, session_id, position, registry):
    if (
        slot.intent_id != spec["intent_id"]
        or slot.slot_id != f"{session_id}-slot-{position + 1}"
        or slot.selected is None
        or slot.selected.canonical_exercise_id != spec["candidate_id"]
        or slot.selected.realization_ref != spec["realization_ref"]
        or slot.selected.side != "BILATERAL"
        or slot.prescription.mode != "OBSERVED_SETTING"
        or slot.alternatives
    ):
        raise ValueError("selection/context/prescription is outside the exact admitted binding")
    _slot(slot, req, registry.historical)
    matches = [
        ep for ep in req.episodes if ep.context.canonical_exercise_id == spec["candidate_id"]
    ]
    if len(matches) != 1:
        raise ValueError("ambiguous observed execution context")
    ep = matches[0]
    events = {e.event_id: e for e in ep.events}
    trial = events[slot.prescription.event_id]
    _check_phase_order(ep, trial, events[slot.prescription.acceptance_event_id])
    if (
        ep.availability != "AVAILABLE"
        or not _current(trial, ep.started_at)
        or trial.provenance.origin != "USER_OBSERVED"
        or ep.context_provenance.recorded_at is None
        or ep.context_provenance.recorded_at < ep.started_at
        or (
            ep.context_provenance.measured_at is not None
            and ep.context_provenance.measured_at < ep.started_at
        )
    ):
        raise ValueError("historical import or unavailable context is not current qualification")
    allowed = (
        {"PER_IMPLEMENT", "TOTAL_EXTERNAL"}
        if spec["candidate_id"] == "romanian-deadlift-halteres"
        else {"MACHINE_DISPLAY_KG", "NON_MASS_SETTING", "TOTAL_EXTERNAL"}
    )
    if ep.context.load_semantics not in allowed:
        raise ValueError("resistance meaning conflicts with the curated realization")


def _check_assessment(req, out):
    used = tuple(REQUIRED_FIELDS)
    if req.blueprint.excluded_exercise_ids.state in {"KNOWN", "CONFLICT"}:
        used += ("excluded_exercise_ids",)
    assessment = assess_inputs(req.blueprint, used)
    if assessment.state != "SUFFICIENT" or out.assessment != assessment or out.used_fields != used:
        raise ValueError(
            "positive result requires independently sufficient nonconflicting consumed facts"
        )


def _positive_invariants(req, out, registry):
    _check_assessment(req, out)
    plan = out.candidate_plan
    policy = registry.policy
    dose = policy["dose"]
    if plan is None or len(plan.sessions) != 2 or plan.review_state != "REVIEWED":
        raise ValueError("admitted profile requires exactly two reviewed sessions")
    if (
        req.blueprint.sessions_per_week.value != 2
        or req.blueprint.limitations.value
        or req.blueprint.objective.value != policy["scope"]["objective"]
        or req.blueprint.population_scope.value != policy["scope"]["population"]
    ):
        raise ValueError("positive result outside limited applicability")
    if plan.allocation_ref != registry.binding_ref + "@" + registry.binding_digest:
        raise ValueError("allocation does not belong to the actual binding")
    times = {t.session_id: t for t in out.time_assessments}
    all_slots = []
    for index, session in enumerate(plan.sessions):
        if session.session_id != f"session-{index + 1}" or len(session.slots) != 7:
            raise ValueError("session/intention allocation differs from the limited policy")
        budget = req.blueprint.session_budgets_minutes.value[index]
        if session.duration.state != "UNKNOWN" or session.duration.budget_minutes != budget:
            raise ValueError("no supported time is admitted for this profile")
        for position, (slot, spec) in enumerate(
            zip(session.slots, policy["selection"], strict=True)
        ):
            _observed_slot(req, slot, spec, session.session_id, position, registry)
            all_slots.append(slot)
        source = dict(
            session_id=session.session_id,
            slots=[{"prescription": s.prescription.dose.model_dump()} for s in session.slots],
        )
        expected = assess_structural_time(
            source, budget_minutes=budget, structure=policy["time"]["structure"]
        )
        if expected.state != "BUDGET_UNCERTAIN" or times[session.session_id] != expected:
            raise ValueError("time claim differs from the actual admitted sequential structure")
    if plan.physical_work_sets_total != 2 * 7 * dose["work_sets"]:
        raise ValueError("incorrect weekly physical allocation")
    for report in plan.zone_reports:
        expected_known = {}
        expected_unknown = set()
        for slot in all_slots:
            row = registry.historical.candidates[slot.selected.canonical_exercise_id]
            role = next((r for r in row["effective_roles"] if r["zone"] == report.zone), None)
            if role is None or role["role"] == "UNKNOWN":
                expected_unknown.add(slot.slot_id)
            else:
                expected_known[slot.slot_id] = (
                    slot.selected.canonical_exercise_id,
                    row["realization_ref"],
                    role["role"],
                    tuple(role["evidence_refs"]),
                )
        actual = {
            c.slot_id: (c.canonical_exercise_id, c.source_ref, c.role, tuple(c.evidence_refs))
            for c in report.contributions
        }
        if (
            actual != expected_known
            or set(report.unresolved_slot_ids) != expected_unknown
            or report.role_status != ("SUPPORTED_ROLES" if expected_known else "UNKNOWN")
            or report.absence_basis_ref is not None
        ):
            raise ValueError(
                "qualitative zone source or unknown coverage differs from reviewed roles"
            )
    if out.start_permission != ("ELIGIBLE" if req.acknowledgment else "REQUIRES_TIME_ACK"):
        raise ValueError("permission does not reflect actual acknowledgment requirement")


def validate_admitted_exchange_v3(request, response, registry):
    assert_trusted_v3(registry)
    req = validated_request(request)
    out = FirstPlanRecommendationV3.model_validate(strict_record(response))
    for field in [
        "subject_ref",
        "snapshot_ref",
        "source_revision",
        "as_of",
        "bundle_digest",
        "effective_science_digest",
    ]:
        if getattr(req, field) != getattr(out, field):
            raise ValueError("result does not belong to the authoritative input: " + field)
    if (out.request_fingerprint, out.observation_fingerprint, out.full_evaluation_fingerprint) != (
        request_fingerprint(req),
        observation_fingerprint(req),
        evaluation_fingerprint(req),
    ):
        raise ValueError("fact/observation/evaluation fingerprint mismatch")
    if out.acknowledgment != req.acknowledgment:
        raise ValueError("result invents or omits the request acknowledgment")
    if out.scientific_readiness == "SCIENTIFICALLY_READY":
        _positive_invariants(req, out, registry)
        if out.plan_time_fingerprint != plan_time_fingerprint(
            out.candidate_plan, out.time_assessments
        ):
            raise ValueError("plan/time identity mismatch")
    from tools.science_initial_policy.v3_producer import produce_v3

    expected = produce_v3(req, registry)
    if encoded(out.model_dump(mode="json")) != encoded(expected.model_dump(mode="json")):
        raise ValueError("result differs from independently checked canonical producer replay")
    return expected
