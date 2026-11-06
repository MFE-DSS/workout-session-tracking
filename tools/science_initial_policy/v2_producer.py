"""Actual isolated successor: sourced calibration/time, no admitted READY authority."""

from __future__ import annotations

import json
from typing import Literal, Self

from pydantic import BaseModel, model_validator

from tools.science_contracts.blueprint_first_plan_v1 import (
    REQUIRED_FIELDS,
    FirstPlanRecommendation,
    FirstPlanRequest,
    Text,
    decision_fingerprint,
    input_assessment,
    validate_exchange,
)
from tools.science_initial_policy.calibration_time_contracts import (
    CalibrationEpisode,
    Record,
    _check_time,
    content_digest,
    context_digest,
)
from tools.science_initial_policy.curation import ELIGIBLE
from tools.science_initial_policy.load_calibration import PROTOCOL_VERSION, calibrate
from tools.science_initial_policy.planning import match_distinct
from tools.science_initial_policy.session_time import TimeComponent, assess_session_time
from tools.science_initial_policy.v2_registry import (
    ENGINE_VERSION,
    V2Registry,
    assert_trusted,
    thaw,
)


class TimingInput(Record):
    session_id: Text
    subject_ref: Text
    components: tuple[TimeComponent, ...] = ()
    structure: Text = "TRADITIONAL_SEQUENTIAL"
    layout: Literal["UNSPECIFIED", "DISJOINT_SEQUENTIAL", "COMMON_CLOCK"] = "UNSPECIFIED"


class EvaluationRequest(Record):
    contract_version: Literal["initial-plan-evaluation/1.0.0"]
    subject_ref: Text
    request: FirstPlanRequest
    episodes: tuple[CalibrationEpisode, ...] = ()
    timing_inputs: tuple[TimingInput, ...] = ()
    bundle_digest: Text
    effective_science_digest: Text

    @model_validator(mode="after")
    def source_boundary(self) -> Self:
        episode_ids, contexts = set(), set()
        for ep in self.episodes:
            key = context_digest(ep.context)
            if ep.episode_id in episode_ids or key in contexts:
                raise ValueError("ambiguous episode identity or current context")
            episode_ids.add(ep.episode_id)
            contexts.add(key)
            if ep.subject_ref != self.subject_ref or ep.as_of != self.request.as_of:
                raise ValueError("episode subject or decision time mismatch")
            if (
                ep.context.context_ref is not None
                and ep.context.context_ref != self.request.blueprint.environment.context_ref
            ):
                raise ValueError("episode belongs to another equipment context")
        session_ids = set()
        for timing in self.timing_inputs:
            if timing.subject_ref != self.subject_ref or timing.session_id in session_ids:
                raise ValueError("timing subject or session identity mismatch")
            session_ids.add(timing.session_id)
            for component in timing.components:
                _check_time(component.provenance, self.request.as_of)
        return self


class EvaluationResult(Record):
    """Versioned research envelope; diagnostics require full recomputation to trust.

    The embedded canonical recommendation keeps its strict v1 schema. Diagnostic
    dictionaries are not executable plans or a served FirstPlanClient transport.
    """

    contract_version: Literal["initial-plan-evaluation-result/1.0.0"]
    subject_ref: Text
    engine_version: Literal["initial-policy-producer/2.0.0"]
    bundle_digest: Text
    effective_science_digest: Text
    request_fingerprint: Text
    evaluation_fingerprint: Text
    recommendation: FirstPlanRecommendation
    draft: dict
    calibration_by_context: dict[str, dict]
    time_by_session: list[dict]
    blockers: list[dict]
    scientific_admission: Literal["NOT_ADMITTED"]
    runtime_availability: Literal["NOT_SERVED"]
    ready_fixture: Literal["NOT_PRODUCED"]


def _plain(value):
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    return value


def _validated(raw, bundle):
    assert_trusted(bundle)
    # JSON boundary prevents nested model_copy and nonfinite untyped-dict values.
    data = json.loads(json.dumps(_plain(raw), allow_nan=False, ensure_ascii=False))
    value = EvaluationRequest.model_validate(data)
    req = value.request
    if (
        req.versions.engine != ENGINE_VERSION
        or req.versions.catalogue != bundle.effective_catalogue_version
    ):
        raise ValueError("v2 engine/effective catalogue mismatch; no silent v1 coercion")
    if (
        value.bundle_digest != bundle.bundle_digest
        or value.effective_science_digest != bundle.effective_science_digest
    ):
        raise ValueError("evaluation does not bind current frozen scientific references")
    for ep in value.episodes:
        identity = ep.context.canonical_exercise_id
        if identity is not None and identity not in bundle.references.canonical_exercise_ids:
            raise ValueError("execution snapshot contains an unresolved exercise identity")
    return value


def _canonical_content(value):
    data = value.model_dump(mode="json")
    for ep in data["episodes"]:
        events = {e["event_id"]: e for e in ep["events"]}
        ep["events"] = sorted(events.values(), key=lambda e: e["sequence"])
    data["episodes"].sort(key=lambda e: (content_digest(e["context"]), e["episode_id"]))
    data["timing_inputs"].sort(key=lambda t: t["session_id"])
    for timing in data["timing_inputs"]:
        timing["components"].sort(key=lambda c: (c["coverage_key"], c["component_id"]))
    return data


def evaluation_fingerprint(request: dict, trusted_bundle: V2Registry) -> str:
    value = _validated(request, trusted_bundle)
    return content_digest(_canonical_content(value))


def _block(code, reason, target=None):
    return {"code": code, "reason": reason, "target": target}


def _used_fields(req):
    used = list(REQUIRED_FIELDS)
    for name in ("excluded_exercise_ids", "declared_priorities"):
        state = getattr(req.blueprint, name).state
        if state == "KNOWN" or (name == "excluded_exercise_ids" and state == "CONFLICT"):
            used.append(name)
    return used


def _recommendation(value, bundle, blockers):
    req, used = value.request, _used_fields(value.request)
    assessment = input_assessment(req.blueprint, tuple(used))
    status = (
        "CONFLICTING_DATA"
        if assessment.conflicting_fields
        else ("INSUFFICIENT_DATA" if assessment.missing_fields else "POLICY_UNAVAILABLE")
    )
    reasons = {
        "POLICY_UNAVAILABLE": "Scientific admission and an applicable positive time model are absent."
    }
    if assessment.conflicting_fields:
        reasons["INPUT_CONFLICT"] = "Resolve sourced required/used input conflicts."
    if assessment.missing_fields:
        reasons["REQUIRED_INPUT_MISSING"] = "Required operational inputs are missing."
    for block in blockers:
        reasons.setdefault(block["code"], block["reason"])
    issues = [
        {"code": k, "blocking": True, "field_refs": [], "explanation": v}
        for k, v in sorted(reasons.items())
    ]
    out = FirstPlanRecommendation.model_validate(
        {
            "contract_version": "first-plan-recommendation/1.0.0",
            "request_fingerprint": decision_fingerprint(req),
            "engine_version": ENGINE_VERSION,
            "status": status,
            "assessment": assessment,
            "issues": issues,
            "used_fields": used,
            "candidate_plan": None,
            "confidence": {
                "individual_response": "NOT_ESTIMATED",
                "feasibility": "UNKNOWN",
                "evidence_refs": list(bundle.policy["evidence_refs"]),
                "limitations": [
                    "Calibration is a provisional observation-backed setting, not true RIR.",
                    "Conditional time arithmetic is not an admitted prediction.",
                    "No runtime activation, executable plan or quantified G17 hypertrophy response.",
                ],
            },
        }
    )
    return validate_exchange(req, out, references=bundle.references)


def _input_blocks(req, bundle):
    assessment = input_assessment(req.blueprint, tuple(_used_fields(req)))
    if assessment.state != "SUFFICIENT":
        return [
            _block(
                "INPUT_CONFLICT" if assessment.conflicting_fields else "REQUIRED_INPUT_MISSING",
                assessment.state,
            )
        ]
    if req.blueprint.sessions_per_week.value not in bundle.dose["cadences"]:
        return [_block("CONSTRAINT_VIOLATION", "CADENCE_NOT_ADMITTED")]
    if req.blueprint.limitations.value:
        return [_block("CONSTRAINT_VIOLATION", "USER_REPORTED_LIMITATION_REQUIRES_REVIEW")]
    if req.blueprint.excluded_exercise_ids.state == "WITHHELD":
        return [_block("CONSTRAINT_VIOLATION", "EXCLUSION_CONSTRAINT_UNRESOLVED")]
    return []


def _compatibility(req, identity, bundle):
    rows = [
        c
        for c in req.blueprint.environment.exercise_confirmations
        if c.canonical_exercise_id == identity
    ]
    states = {c.state for c in rows}
    if {"AVAILABLE", "UNAVAILABLE"} <= states:
        return "CONFLICT", None
    if "UNAVAILABLE" in states:
        return "UNAVAILABLE", None
    available = [c for c in rows if c.state == "AVAILABLE"]
    if available:
        latest = max(available, key=lambda c: (c.provenance.recorded_at, c.provenance.source_ref))
        return "CONFIRMED", latest.provenance.source_ref
    return (
        "NOT_REQUIRED" if identity in bundle.references.no_equipment_exercise_ids else "UNKNOWN"
    ), None


def _options(req, intent, bundle, blockers):
    excluded = set(req.blueprint.excluded_exercise_ids.value or [])
    options = []
    for identity, row in sorted(bundle.candidates.items()):
        if row["intent_id"] != intent["intent_id"]:
            continue
        state, source = _compatibility(req, identity, bundle)
        if state == "CONFLICT":
            blockers.append(_block("CONSTRAINT_VIOLATION", "CURRENT_CONTEXT_CONFLICT", identity))
        if (
            state in {"CONFLICT", "UNAVAILABLE"}
            or identity in excluded
            or row["admission"] not in ELIGIBLE
        ):
            continue
        options.append(
            {
                "canonical_exercise_id": identity,
                "compatibility": state,
                "compatibility_source_ref": source,
                "context_ref": req.blueprint.environment.context_ref,
            }
        )
    order = {"CONFIRMED": 0, "NOT_REQUIRED": 1, "UNKNOWN": 2}
    return sorted(options, key=lambda c: (order[c["compatibility"]], c["canonical_exercise_id"]))


def _episode_for(identity, value, bundle):
    # An exercise-level slot does not aggregate independent sides. Unilateral
    # execution needs a separately admitted appairing contract, absent here.
    if bundle.candidates[identity]["unilateral"] is not False:
        return None
    matches = [
        e
        for e in value.episodes
        if e.context.canonical_exercise_id == identity
        and e.context.realization_ref == bundle.realization_refs[identity]
        and e.context.side == "BILATERAL"
    ]
    if len(matches) != 1:
        return None  # no implicit bilateral/side or machine-context merge
    ep = matches[0]
    if (
        ep.context_provenance.recorded_at is None
        or ep.context_provenance.recorded_at < ep.started_at
    ):
        return None
    return ep


def _pending_calibration():
    return {
        "protocol_version": PROTOCOL_VERSION,
        "state": "NEEDS_CALIBRATION",
        "load_kg": None,
        "load_mode": "CALIBRATION_REQUIRED",
        "effort_sufficiency": "UNKNOWN",
        "confidence": "UNKNOWN",
        "reasons": ["NO_CURRENT_QUALIFIED_OBSERVATION_SNAPSHOT"],
        "automatic_next_action": "NONE",
    }


def _draft_slot(value, bundle, intent, selected, alternatives, slot_id, calibrations, blockers):
    calibration, roles, row, qualified, ep = _pending_calibration(), [], None, False, None
    if selected is not None:
        identity = selected["canonical_exercise_id"]
        row = bundle.candidates[identity]
        ep = _episode_for(identity, value, bundle)
        if ep is not None:
            calibration = calibrations[context_digest(ep.context)]
            p = ep.context_provenance
            qualified = (
                p.origin in {"USER_REPORTED", "USER_OBSERVED"}
                and p.source_ref is not None
                and p.acquisition != "UNKNOWN"
            )
        roles = thaw(row["effective_roles"] if qualified else row["source_roles"])
        if selected["compatibility"] == "UNKNOWN":
            blockers.append(
                _block("COMPATIBILITY_UNKNOWN", "EXERCISE_CONTEXT_UNCONFIRMED", identity)
            )
        if row["requires_qualified_role_projection"] and not qualified:
            blockers.append(
                _block("CONSTRAINT_VIOLATION", "QUALIFIED_REALISATION_REQUIRED", identity)
            )
    if calibration["state"] in {"CALIBRATION_IN_PROGRESS", "INSUFFICIENT_DATA", "UNAVAILABLE"}:
        blockers.append(_block("CONSTRAINT_VIOLATION", calibration["state"], slot_id))
    prescription = {
        "work_sets": bundle.dose["work_sets"],
        "min_reps": bundle.dose["rep_range"][0],
        "max_reps": bundle.dose["rep_range"][1],
        "rir_target": bundle.dose["rir_target"],
        "rest_seconds": bundle.dose["rest_seconds"].get(row["joint_type"]) if row else None,
        "load_kg": calibration["load_kg"],
        "load_mode": calibration["load_mode"],
        "source_kind": "PROPOSED_NOT_EXECUTABLE",
        "dose_source_ref": bundle.dose["source_version"],
        "calibration_fingerprint": content_digest(calibration),
        "execution_scope_fingerprint": content_digest({
            "selected": selected,
            "realization_ref": row["realization_ref"] if row else None,
            "episode_context": ep.context.model_dump(mode="json") if ep else None,
        }),
    }
    return {
        "slot_id": slot_id,
        "intent_id": intent["intent_id"],
        "selected": selected,
        "alternatives": alternatives,
        "unilateral": row["unilateral"] if row else None,
        "prescription": prescription,
        "calibration": calibration,
        "roles": roles,
        "role_application": "QUALIFIED_CONDITIONAL_PLANNING_ONLY"
        if qualified
        else "SOURCE_ROLE_QUALIFICATION_UNCONFIRMED",
        "hypertrophy_response": "NOT_ESTIMATED",
        "execution_ready": False,
    }


def _draft(value, bundle, calibrations, blockers):
    req, sessions = value.request, []
    intents = thaw(bundle.dose["intents"])
    priorities = req.blueprint.declared_priorities.value or []
    if (
        "lower" in priorities
        and "shoulders" in priorities
        and priorities.index("lower") < priorities.index("shoulders")
    ):
        intents[-2:] = reversed(intents[-2:])
    options = [_options(req, intent, bundle, blockers) for intent in intents]
    assignment = match_distinct(options)
    if assignment is None:
        blockers.append(_block("CATALOG_GAP", "NO_DISTINCT_ADMISSIBLE_ASSIGNMENT"))
        assignment = [None] * len(intents)
    for n in range(req.blueprint.sessions_per_week.value):
        sid = f"session-{n + 1}"
        slots = [
            _draft_slot(
                value,
                bundle,
                intent,
                assignment[i],
                [c for c in options[i] if c != assignment[i]],
                f"{sid}-slot-{i + 1}",
                calibrations,
                blockers,
            )
            for i, intent in enumerate(intents)
        ]
        time_session = {
            "session_id": sid,
            "subject_ref": value.subject_ref,
            "context_ref": req.blueprint.environment.context_ref,
            "as_of": req.as_of.isoformat().replace("+00:00", "Z"),
            "slots": [
                {
                    "slot_id": s["slot_id"],
                    "unilateral": s["unilateral"],
                    "prescription": s["prescription"],
                }
                for s in slots
            ],
        }
        sessions.append({"session_id": sid, "slots": slots, "time_session": time_session})
    return {
        "sessions": sessions,
        "physical_work_sets_total": sum(
            s["prescription"]["work_sets"] for session in sessions for s in session["slots"]
        ),
        "quantitative_exposure_projection": "NOT_COMPUTED",
        "executable": False,
    }


def _timing(value, draft, blockers):
    rows = {t.session_id: t for t in value.timing_inputs}
    if not set(rows) <= {s["session_id"] for s in draft["sessions"]}:
        raise ValueError("timing snapshot does not belong to the generated session allocation")
    results = []
    for n, session in enumerate(draft["sessions"]):
        source = rows.get(session["session_id"])
        out = assess_session_time(
            session["time_session"],
            budget_minutes=value.request.blueprint.session_budgets_minutes.value[n],
            components=[c.model_dump(mode="json") for c in source.components] if source else [],
            structure=source.structure if source else "TRADITIONAL_SEQUENTIAL",
            layout=source.layout if source else "UNSPECIFIED",
        )
        out["session_id"] = session["session_id"]
        results.append(out)
        blockers.append(
            _block("TIME_UNCERTAIN", "POSITIVE_TIME_MODEL_NOT_ADMITTED", session["session_id"])
        )
        if out["constraint"] is not None:
            blockers.append(
                _block("CONSTRAINT_VIOLATION", "CONFIGURATION_TIME_EXCEEDS", session["session_id"])
            )
    return results


def produce_v2(evaluation_request: dict, trusted_bundle: V2Registry) -> dict:
    """Pure integrated producer: actual decisions, no fabricated scientific admission."""
    value, bundle = _validated(evaluation_request, trusted_bundle), trusted_bundle
    blockers = _input_blocks(value.request, bundle)
    # Validate canonical reference/required-field semantics before selection/calibration.
    _recommendation(value, bundle, blockers)
    calibrations = {
        context_digest(ep.context): calibrate(
            ep, min_reps=bundle.dose["rep_range"][0], max_reps=bundle.dose["rep_range"][1]
        )
        for ep in sorted(value.episodes, key=lambda e: context_digest(e.context))
    }
    draft = {
        "sessions": [],
        "physical_work_sets_total": 0,
        "quantitative_exposure_projection": "NOT_COMPUTED",
        "executable": False,
    }
    times = []
    if not blockers:
        draft = _draft(value, bundle, calibrations, blockers)
        times = _timing(value, draft, blockers)
    for reason in bundle.policy["admission_blockers"]:
        blockers.append(_block("POLICY_UNAVAILABLE", reason))
    unique = {json.dumps(b, sort_keys=True): b for b in blockers}
    blockers = [unique[k] for k in sorted(unique)]
    recommendation = _recommendation(value, bundle, blockers)
    out = {
        "contract_version": "initial-plan-evaluation-result/1.0.0",
        "subject_ref": value.subject_ref,
        "engine_version": ENGINE_VERSION,
        "bundle_digest": bundle.bundle_digest,
        "effective_science_digest": bundle.effective_science_digest,
        "request_fingerprint": decision_fingerprint(value.request),
        "evaluation_fingerprint": content_digest(_canonical_content(value)),
        "recommendation": recommendation.model_dump(mode="json"),
        "draft": draft,
        "calibration_by_context": calibrations,
        "time_by_session": times,
        "blockers": blockers,
        "scientific_admission": "NOT_ADMITTED",
        "runtime_availability": "NOT_SERVED",
        "ready_fixture": "NOT_PRODUCED",
    }
    json.dumps(out, allow_nan=False)  # no nonfinite values hidden in result dictionaries
    return EvaluationResult.model_validate(out).model_dump(mode="json")


def verify_evaluation(request: dict, result: dict, trusted_bundle: V2Registry) -> dict:
    """Recompute the frozen pure decision; a digest label alone is never authority."""
    expected = produce_v2(request, trusted_bundle)
    candidate = json.loads(json.dumps(_plain(result), allow_nan=False))
    if candidate != expected:
        raise ValueError("result differs from the authoritative full evaluation")
    return expected
