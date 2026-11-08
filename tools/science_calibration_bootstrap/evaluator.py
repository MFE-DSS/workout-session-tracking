"""One deterministic encounter kernel. Preview never supplies public authority."""

from __future__ import annotations

from tools.science_initial_policy.admission_calibration import calibrate_for_admission
from tools.science_initial_policy.v3_admission import assert_trusted_v3, load_v3_registry

from .contracts import EncounterResult, input_digest, validated_input

POLICY_REF = "initial-calibration-encounter/1.0.0"
PILOT = "leg-extensions-assises"
PROTOCOL_REF = (
    "docs/science/sci-p02-initial-policy/first-use-calibration-bootstrap/OPERATIONAL_PROTOCOL.md"
)
BASE_ACTIONS = (
    "READ_GUIDANCE",
    "PROVIDE_FACTS",
    "REQUEST_ASSISTANCE",
    "CONFIRM_CONTEXT",
    "RECORD_TRIAL",
    "PAUSE",
    "WITHDRAW",
)


def _current(provenance, start):
    return (
        provenance.source_ref is not None
        and provenance.origin in {"USER_REPORTED", "USER_OBSERVED"}
        and provenance.acquisition in {"DECLARED", "EXECUTION_LOG", "DEVICE_MEASURED"}
        and provenance.recorded_at is not None
        and provenance.recorded_at >= start
        and (provenance.measured_at is None or provenance.measured_at >= start)
    )


def _occurred(event):
    return event.provenance.measured_at or event.provenance.recorded_at


def _concerns(req):
    ep = req.episode
    if req.concern_state != "CLEAR":
        return "OWNER_CONCERN_NOT_CLEARED"
    if ep is None:
        return None
    if ep.previous_episode_id and ep.predecessor_blocked is not False:
        return "RESTART_POLICY_UNAVAILABLE"
    for event in ep.events:
        if event.kind == "CONCERN_REPORTED":
            return "CONCERN_REPORTED"
        if event.kind == "ATTEMPT_OBSERVED" and (
            event.successful is False
            or event.technique != "ACCEPTABLE"
            or event.discomfort != "NO_CONCERN"
            or req.stop_reasons.get(event.event_id, "UNKNOWN") in {"CONCERN", "FAILURE", "UNKNOWN"}
        ):
            return "TRIAL_REVIEW_REQUIRED"
    return None


def _familiar(ep, *, before=None, not_before=None):
    if ep is None:
        return False
    current = [e for e in ep.events if _current(e.provenance, ep.started_at)]
    starts = [e for e in current if e.kind == "FAMILIARIZATION_STARTED"]
    if before and any(
        e.sequence > before.sequence or _occurred(e) > _occurred(before) for e in starts
    ):
        return False
    last_start = max((e.sequence for e in starts), default=-1)
    if before and before.familiarization_confirmed is True:
        return not_before is None or _occurred(before) >= not_before
    return any(
        e.kind == "FAMILIARIZATION_CONFIRMED"
        and e.sequence > last_start
        and (not_before is None or _occurred(e) >= not_before)
        and (before is None or (e.sequence < before.sequence and _occurred(e) <= _occurred(before)))
        for e in current
    )


def _qualified(req, dose):
    ep = req.episode
    if ep is None or ep.started_at < req.started_at:
        return None
    if not _current(ep.context_provenance, ep.started_at):
        return None
    result = calibrate_for_admission(
        ep, min_reps=dose["rep_range"][0], max_reps=dose["rep_range"][1]
    )
    if result["state"] != "CALIBRATED":
        return None
    by_id = {e.event_id: e for e in ep.events}
    trial = by_id[result["reference_event_id"]]
    accepts = sorted(
        (
            e
            for e in ep.events
            if e.kind == "SETTING_ACCEPTED" and _current(e.provenance, ep.started_at)
        ),
        key=lambda e: e.sequence,
    )
    if not accepts or not _current(trial.provenance, ep.started_at):
        return None
    accepted = accepts[-1]
    contexts = [
        e
        for e in ep.events
        if e.kind == "CONTEXT_CONFIRMED"
        and _current(e.provenance, ep.started_at)
        and e.sequence < trial.sequence
        and _occurred(e) <= _occurred(trial)
        and e.setting == trial.setting
    ]
    prep_at = req.preparation.provenance.measured_at or req.preparation.provenance.recorded_at
    choice_at = (
        req.setting_choice.provenance.measured_at or req.setting_choice.provenance.recorded_at
    )
    if (
        prep_at > _occurred(trial)
        or choice_at > _occurred(trial)
        or not contexts
        or not _familiar(ep, before=trial, not_before=prep_at)
        or _occurred(accepted) < _occurred(trial)
        or req.stop_reasons.get(trial.event_id) != "COMPLETED"
        or req.setting_choice.setting != trial.setting
    ):
        return None
    return trial, accepted


def _encounter_block(req, spec):
    concern = _concerns(req)
    if concern:
        return ("CONCERN_REVIEW", "OBSERVE", concern)
    if req.withdrawn:
        return ("WITHDRAWN", "DECIDE", "USER_WITHDREW")
    if req.availability == "UNAVAILABLE" or (
        req.episode and any(e.kind == "EQUIPMENT_UNAVAILABLE" for e in req.episode.events)
    ):
        return ("UNAVAILABLE", "IDENTIFY", "DEVICE_UNAVAILABLE")
    if (
        not req.ledger_complete
        or not req.ledger_source_ref
        or (req.episode and (not req.episode.ledger_complete or not req.episode.ledger_source_ref))
    ):
        return ("INSUFFICIENT_EVIDENCE", "IDENTIFY", "OWNER_LEDGER_INCOMPLETE")
    if (
        req.population.state != "KNOWN"
        or req.population.value != "ADULT_NON_CLINICAL"
        or req.limitations.state != "KNOWN"
        or req.limitations.value != ()
    ):
        return ("INSUFFICIENT_EVIDENCE", "IDENTIFY", "POPULATION_OR_LIMITATIONS_NOT_APPLICABLE")
    ctx = req.context
    if (
        ctx.canonical_exercise_id != PILOT
        or ctx.realization_ref != spec["realization_ref"]
        or ctx.side != "BILATERAL"
    ):
        return ("UNAVAILABLE", "IDENTIFY", "REALIZATION_NOT_IN_ENCOUNTER_POLICY")
    if (
        req.availability != "AVAILABLE"
        or not all((ctx.context_ref, ctx.equipment_ref))
        or ctx.load_semantics not in {"MACHINE_DISPLAY_KG", "NON_MASS_SETTING", "TOTAL_EXTERNAL"}
        or not _current(req.context_provenance, req.started_at)
    ):
        return ("INSUFFICIENT_EVIDENCE", "IDENTIFY", "CURRENT_DEVICE_OR_SETTING_SEMANTICS_UNKNOWN")
    prep = req.preparation
    if (
        prep is None
        or not prep.understood
        or not prep.controlled
        or not _current(prep.provenance, req.started_at)
    ):
        return ("CALIBRATION_REQUIRED", "IDENTIFY", "ACTUAL_INSTRUCTIONS_AND_SETUP_REQUIRED")
    return None


def compile_candidate(raw, historical_registry=None) -> EncounterResult:
    """Pure research compilation, not permission to act or a personal fact writer."""
    req = validated_input(raw)
    registry = historical_registry or load_v3_registry()
    assert_trusted_v3(registry)
    spec = next(s for s in registry.policy["selection"] if s["candidate_id"] == PILOT)
    refs = (PROTOCOL_REF,)
    if req.preparation:
        refs += (req.preparation.instruction_ref, req.preparation.setup_ref)

    def out(state, phase, reason, actions=(), qualified=None):
        details = {}
        if qualified:
            trial, acceptance = qualified
            details = dict(
                qualified_setting=trial.setting,
                reference_event_id=trial.event_id,
                acceptance_event_id=acceptance.event_id,
                portable_episode=req.episode,
                confidence="LOW",
            )
        return EncounterResult(
            artifact_kind="DRAFT_EVALUATION_SYNTHETIC_NOT_AUTHORITY",
            admission="NOT_ADMITTED",
            encounter_ref=req.encounter_ref,
            subject_ref=req.subject_ref,
            source_revision=req.source_revision,
            input_digest=input_digest(req),
            policy_ref=POLICY_REF,
            authority_digest=None,
            state=state,
            phase=phase,
            allowed_actions=BASE_ACTIONS,
            candidate_actions=actions,
            reasons=(reason,),
            instruction_refs=refs,
            **details,
        )

    blocked = _encounter_block(req, spec)
    if blocked:
        return out(*blocked)
    familiar_actions = ("INITIATE_FAMILIARIZATION", "CONFIRM_FAMILIARIZATION")
    choice = req.setting_choice
    if choice is None or not choice.available or not _current(choice.provenance, req.started_at):
        return out(
            "SUPPORTED_INITIAL_EXPLORATION",
            "FAMILIARIZE",
            "SETUP_ONLY_NO_LOADED_TRIAL",
            familiar_actions,
        )
    qualified = _qualified(req, registry.policy["dose"])
    if qualified:
        return out(
            "QUALIFIED", "DECIDE", "OBSERVED_SETTING_PROVISIONALLY_ACCEPTED", qualified=qualified
        )
    ep = req.episode
    trials = [e for e in ep.events if e.kind == "ATTEMPT_OBSERVED"] if ep else []
    prep_at = req.preparation.provenance.measured_at or req.preparation.provenance.recorded_at
    choice_at = choice.provenance.measured_at or choice.provenance.recorded_at
    confirmations = [e for e in ep.events if e.kind == "CONTEXT_CONFIRMED"] if ep else []
    last_context = max(confirmations, key=lambda e: e.sequence) if confirmations else None
    can_trial = bool(
        ep
        and ep.started_at >= req.started_at
        and last_context
        and last_context.setting == choice.setting
        and choice_at <= _occurred(last_context)
        and _familiar(ep, not_before=prep_at)
    )
    actions = familiar_actions
    if can_trial and (not trials or req.retry_requested):
        actions += ("INITIATE_TRIAL",)
    if trials:
        # Offer acceptance only when this exact episode would qualify after a
        # real acceptance action; do not synthesize that action to probe it.
        trial = max(trials, key=lambda e: e.sequence)
        if (
            trial.completed is True
            and trial.successful is True
            and trial.reps is not None
            and registry.policy["dose"]["rep_range"][0]
            <= trial.reps
            <= registry.policy["dose"]["rep_range"][1]
            and trial.setting == choice.setting
            and _current(trial.provenance, ep.started_at)
            and any(
                e.kind == "CONTEXT_CONFIRMED"
                and e.setting == trial.setting
                and _current(e.provenance, ep.started_at)
                and e.sequence < trial.sequence
                and _occurred(e) <= _occurred(trial)
                for e in ep.events
            )
            and prep_at <= _occurred(trial)
            and choice_at <= _occurred(trial)
            and _familiar(ep, before=trial, not_before=prep_at)
        ):
            actions += ("ACCEPT_EXACT_SETTING",)
        return out("OBSERVED", "OBSERVE", "ACTUAL_OBSERVATION_NOT_YET_QUALIFIED", actions)
    return out(
        "SUPPORTED_INITIAL_EXPLORATION",
        "TRIAL" if can_trial else "FAMILIARIZE",
        "TRIAL_REQUIRES_CURRENT_SETTING_AND_PRIOR_FAMILIARIZATION",
        actions,
    )


def evaluate(raw, authority=None) -> EncounterResult:
    if authority is not None:
        from .policy import assert_authority

        assert_authority(authority)
    candidate = compile_candidate(raw, authority.historical if authority is not None else None)
    data = candidate.model_dump(mode="python")
    data.update(artifact_kind="ISOLATED_EVALUATION_NOT_SERVED", candidate_actions=())
    if authority is None:
        data.update(
            state="INSUFFICIENT_EVIDENCE",
            admission="NOT_ADMITTED",
            reasons=("ENCOUNTER_AUTHORITY_REQUIRED",),
            qualified_setting=None,
            reference_event_id=None,
            acceptance_event_id=None,
            portable_episode=None,
            confidence="UNKNOWN",
        )
    else:
        data.update(
            admission="ADMITTED_WITH_LIMITS",
            authority_digest=authority.bundle_digest,
            allowed_actions=tuple(dict.fromkeys((*BASE_ACTIONS, *candidate.candidate_actions))),
        )
    return EncounterResult.model_validate(data)
