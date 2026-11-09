"""Per-realization encounter orchestration; historical pilot remains immutable."""

from tools.science_calibration_bootstrap.contracts import (
    EncounterResult,
    input_digest,
    validated_input,
)
from tools.science_calibration_bootstrap.evaluator import (
    BASE_ACTIONS,
    _concerns,
    _current,
    _familiar,
    _occurred,
    _qualified,
)
from tools.science_initial_policy.v3_admission import assert_trusted_v3, load_v3_registry

POLICY_REF = "initial-calibration-extension/1.0.0"
PROTOCOL_REF = (
    "docs/science/sci-p02-initial-policy/calibration-six-extensions/OPERATIONAL_PROTOCOL.md"
)
PROFILES = {
    "chest-press-machine": "MACHINE_DISPLAY_KG",
    "rowing-chest-supported": "MACHINE_DISPLAY_KG",
    "romanian-deadlift-halteres": "PER_IMPLEMENT",
    "tirage-poulie-haute-prise-neutre": "MACHINE_DISPLAY_KG",
    "elevations-laterales-machine": "MACHINE_DISPLAY_KG",
    "releves-mollets-debout-machine": "MACHINE_DISPLAY_KG",
}
FAMILIAR_ACTIONS = ("INITIATE_FAMILIARIZATION", "CONFIRM_FAMILIARIZATION")


def loaded_familiarization(req, *, before=None):
    """Actual exact-setting familiarization after current setup, choice and context."""
    ep, prep, choice = req.episode, req.preparation, req.setting_choice
    if not ep or not prep or not choice or ep.started_at < req.started_at:
        return False
    if not _current(ep.context_provenance, ep.started_at):
        return False
    current = [e for e in ep.events if _current(e.provenance, ep.started_at)]
    contexts = [e for e in current if e.kind == "CONTEXT_CONFIRMED"]
    context = max(contexts, key=lambda e: e.sequence) if contexts else None
    if (
        context is None
        or context.setting != choice.setting
        or _occurred(context)
        < max(
            _occurred(prep),
            _occurred(choice),
            (req.context_provenance.measured_at or req.context_provenance.recorded_at),
            (ep.context_provenance.measured_at or ep.context_provenance.recorded_at),
        )
    ):
        return False
    if before and (context.sequence >= before.sequence or _occurred(context) > _occurred(before)):
        return False
    starts = [e for e in current if e.kind == "FAMILIARIZATION_STARTED"]
    return any(
        e.kind == "FAMILIARIZATION_CONFIRMED"
        and e.setting == choice.setting
        and e.sequence > context.sequence
        and _occurred(e) >= _occurred(context)
        and all(e.sequence > s.sequence and _occurred(e) >= _occurred(s) for s in starts)
        and (before is None or (e.sequence < before.sequence and _occurred(e) <= _occurred(before)))
        for e in current
    ) and _familiar(ep, before=before, not_before=_occurred(prep))


def _declaration(fact):
    p = fact.provenance
    return (
        p.origin in {"USER_REPORTED", "USER_OBSERVED"}
        and p.acquisition == "DECLARED"
        and p.source_ref is not None
        and p.recorded_at is not None
    )


def _block(req, spec):
    concern = _concerns(req)
    if concern:
        return "CONCERN_REVIEW", "OBSERVE", concern
    if req.withdrawn:
        return "WITHDRAWN", "DECIDE", "USER_WITHDREW"
    if req.availability == "UNAVAILABLE" or (
        req.episode and any(e.kind == "EQUIPMENT_UNAVAILABLE" for e in req.episode.events)
    ):
        return "UNAVAILABLE", "IDENTIFY", "DEVICE_UNAVAILABLE"
    if (
        not req.ledger_complete
        or not req.ledger_source_ref
        or (req.episode and (not req.episode.ledger_complete or not req.episode.ledger_source_ref))
    ):
        return "INSUFFICIENT_EVIDENCE", "IDENTIFY", "OWNER_LEDGER_INCOMPLETE"
    if (
        not _declaration(req.population)
        or not _declaration(req.limitations)
        or req.population.state != "KNOWN"
        or req.population.value != "ADULT_NON_CLINICAL"
        or req.limitations.state != "KNOWN"
        or req.limitations.value != ()
    ):
        return "INSUFFICIENT_EVIDENCE", "IDENTIFY", "POPULATION_OR_LIMITATIONS_NOT_APPLICABLE"
    ctx = req.context
    if not spec or ctx.realization_ref != spec["realization_ref"] or ctx.side != "BILATERAL":
        return "UNAVAILABLE", "IDENTIFY", "REALIZATION_NOT_IN_EXTENSION_POLICY"
    if (
        req.availability != "AVAILABLE"
        or not ctx.context_ref
        or not ctx.equipment_ref
        or ctx.load_semantics != PROFILES[ctx.canonical_exercise_id]
        or not _current(req.context_provenance, req.started_at)
    ):
        return "INSUFFICIENT_EVIDENCE", "IDENTIFY", "CURRENT_DEVICE_OR_SETTING_SEMANTICS_UNKNOWN"
    prep = req.preparation
    if (
        not prep
        or not prep.understood
        or not prep.controlled
        or not _current(prep.provenance, req.started_at)
    ):
        return "CALIBRATION_REQUIRED", "IDENTIFY", "ACTUAL_INSTRUCTIONS_AND_SETUP_REQUIRED"
    return None


def compile_candidate(raw, historical_registry=None) -> EncounterResult:
    """Research preview only; does not supply permission or write observed facts."""
    req = validated_input(raw)
    registry = historical_registry or load_v3_registry()
    assert_trusted_v3(registry)
    candidate = req.context.canonical_exercise_id
    spec = (
        next((s for s in registry.policy["selection"] if s["candidate_id"] == candidate), None)
        if candidate in PROFILES
        else None
    )
    refs = (PROTOCOL_REF + "#" + candidate,)
    if req.preparation:
        refs += (req.preparation.instruction_ref, req.preparation.setup_ref)

    def out(state, phase, reason, actions=(), qualified=None):
        details = {}
        if qualified:
            trial, accepted = qualified
            details = dict(
                qualified_setting=trial.setting,
                reference_event_id=trial.event_id,
                acceptance_event_id=accepted.event_id,
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

    blocked = _block(req, spec)
    if blocked:
        return out(*blocked)
    choice = req.setting_choice
    if choice is None or not choice.available or not _current(choice.provenance, req.started_at):
        return out(
            "SUPPORTED_INITIAL_EXPLORATION",
            "FAMILIARIZE",
            "SETUP_ONLY_NO_LOADED_TRIAL",
            FAMILIAR_ACTIONS,
        )
    qualified = _qualified(req, registry.policy["dose"])
    if qualified and loaded_familiarization(req, before=qualified[0]):
        return out(
            "QUALIFIED", "DECIDE", "OBSERVED_SETTING_PROVISIONALLY_ACCEPTED", qualified=qualified
        )
    ep = req.episode
    trials = [e for e in ep.events if e.kind == "ATTEMPT_OBSERVED"] if ep else []
    actions = FAMILIAR_ACTIONS
    can_trial = loaded_familiarization(req)
    if can_trial and (not trials or req.retry_requested):
        actions += ("INITIATE_TRIAL",)
    if trials:
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
            and req.stop_reasons.get(trial.event_id) == "COMPLETED"
            and loaded_familiarization(req, before=trial)
        ):
            actions += ("ACCEPT_EXACT_SETTING",)
        return out("OBSERVED", "OBSERVE", "ACTUAL_OBSERVATION_NOT_YET_QUALIFIED", actions)
    return out(
        "SUPPORTED_INITIAL_EXPLORATION",
        "TRIAL" if can_trial else "FAMILIARIZE",
        "TRIAL_REQUIRES_EXACT_SETTING_FAMILIARIZATION",
        actions,
    )


def evaluate(raw, authority=None) -> EncounterResult:
    """Public isolated evaluation: published admission is distinct from preview."""
    if authority is not None:
        from .policy import assert_authority

        assert_authority(authority)
    candidate = compile_candidate(raw, authority.historical if authority else None)
    data = candidate.model_dump(mode="python")
    data.update(artifact_kind="ISOLATED_EVALUATION_NOT_SERVED", candidate_actions=())
    if authority is None:
        data.update(
            state="INSUFFICIENT_EVIDENCE",
            admission="NOT_ADMITTED",
            reasons=("EXTENSION_AUTHORITY_REQUIRED",),
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
