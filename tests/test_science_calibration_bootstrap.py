"""One real encounter kernel, synthetic facts, unchanged plan qualification."""

import copy
import importlib

import pytest

from tests.science_bootstrap_samples import encounter, plan_input
from tools.science_initial_policy.v3_admission import load_v3_registry


def api():
    return importlib.import_module("tools.science_calibration_bootstrap.evaluator")


def test_progression_opens_without_load_then_observes_and_qualifies():
    stages = [
        ("open", "CALIBRATION_REQUIRED"),
        ("familiarize", "SUPPORTED_INITIAL_EXPLORATION"),
        ("trial", "SUPPORTED_INITIAL_EXPLORATION"),
        ("observed", "OBSERVED"),
        ("qualified", "QUALIFIED"),
    ]
    for stage, state in stages:
        out = api().compile_candidate(encounter(stage=stage))
        assert out.state == state
        assert out.admission == "NOT_ADMITTED"
        assert out.artifact_kind == "DRAFT_EVALUATION_SYNTHETIC_NOT_AUTHORITY"
        assert "INITIATE_TRIAL" not in out.allowed_actions
        assert out.duration == "UNKNOWN"
    assert api().compile_candidate(encounter()).qualified_setting.value == 40.0
    assert api().compile_candidate(encounter()).confidence == "LOW"


def test_permissions_to_act_are_distinct_from_recording_past_facts():
    a = api().compile_candidate(encounter(stage="familiarize"))
    assert "INITIATE_FAMILIARIZATION" in a.candidate_actions
    assert "INITIATE_TRIAL" not in a.candidate_actions
    b = api().compile_candidate(encounter(stage="trial"))
    assert "INITIATE_TRIAL" in b.candidate_actions
    raw = encounter(stage="trial")
    raw["concern_state"] = "REPORTED"
    out = api().compile_candidate(raw)
    assert "INITIATE_TRIAL" not in out.candidate_actions
    assert "RECORD_TRIAL" in out.allowed_actions


@pytest.mark.parametrize(
    "change",
    [
        "population",
        "limitations",
        "instruction",
        "control",
        "inventory",
        "ledger",
        "historical_context",
        "other_candidate",
        "side",
        "old_choice",
        "old_preparation",
    ],
)
def test_missing_or_inapplicable_conditions_do_not_allow_a_trial(change):
    raw = encounter(stage="trial")
    if change == "population":
        raw["population"].update(state="UNKNOWN", value=None)
    elif change == "limitations":
        raw["limitations"]["value"] = ["reported limitation"]
    elif change == "instruction":
        raw["preparation"] = None
    elif change == "control":
        raw["preparation"]["controlled"] = False
    elif change == "inventory":
        raw["availability"] = raw["episode"]["availability"] = "UNKNOWN"
    elif change == "ledger":
        raw["ledger_complete"] = False
    elif change == "historical_context":
        raw["context_provenance"]["recorded_at"] = "2026-11-06T11:00:00Z"
    elif change in ("old_choice", "old_preparation"):
        field = "setting_choice" if change == "old_choice" else "preparation"
        raw[field]["provenance"]["recorded_at"] = "2026-11-06T11:00:00Z"
    else:
        from tools.science_initial_policy.calibration_time_contracts import (
            ContextKey,
            context_digest,
        )

        raw["episode"] = None
        raw["context"]["canonical_exercise_id"] = (
            "chest-press-machine" if change == "other_candidate" else "leg-extensions-assises"
        )
        if change == "side":
            raw["context"]["side"] = "LEFT"
        h = context_digest(ContextKey.model_validate(raw["context"]))
        raw["preparation"]["context_fingerprint"] = raw["setting_choice"]["context_fingerprint"] = h
    out = api().compile_candidate(raw)
    assert "INITIATE_TRIAL" not in out.candidate_actions
    assert out.state != "QUALIFIED"


@pytest.mark.parametrize(
    "change",
    [
        "failed",
        "technique",
        "discomfort",
        "unknown_quality",
        "prior",
        "global",
        "global_unknown",
        "reason_unknown",
    ],
)
def test_concern_or_unresolved_predecessor_cannot_be_reset(change):
    raw = encounter(stage="observed")
    trial = raw["episode"]["events"][-1]
    if change == "failed":
        trial["successful"] = False
    elif change == "technique":
        trial["technique"] = "CONCERN"
    elif change == "discomfort":
        trial["discomfort"] = "CONCERN"
    elif change == "unknown_quality":
        trial["technique"] = "UNKNOWN"
    elif change == "prior":
        raw["episode"].update(previous_episode_id="older", predecessor_blocked=True)
    elif change == "global":
        raw["concern_state"] = "REPORTED"
    elif change == "global_unknown":
        raw["concern_state"] = "UNKNOWN"
    else:
        raw["stop_reasons"][trial["event_id"]] = "UNKNOWN"
    raw["retry_requested"] = True
    raw["encounter_ref"] = "new-id-does-not-reset-concern"
    out = api().compile_candidate(raw)
    assert out.state == "CONCERN_REVIEW"
    assert "INITIATE_TRIAL" not in out.candidate_actions


@pytest.mark.parametrize("reason", ["USER_STOPPED", "TIME_LIMIT"])
def test_voluntary_interruption_is_not_failure_and_retry_is_explicit(reason):
    raw = encounter(stage="observed")
    t = raw["episode"]["events"][-1]
    t.update(completed=False, successful=None, reps=4)
    raw["stop_reasons"][t["event_id"]] = reason
    out = api().compile_candidate(raw)
    assert out.state == "OBSERVED"
    assert "INITIATE_TRIAL" not in out.candidate_actions
    raw["retry_requested"] = True
    assert "INITIATE_TRIAL" in api().compile_candidate(raw).candidate_actions
    assert api().compile_candidate(raw).qualified_setting is None


@pytest.mark.parametrize(
    "change",
    [
        "late_familiar",
        "old_trial",
        "old_acceptance",
        "no_acceptance",
        "old_import",
        "different_choice",
    ],
)
def test_diagnostic_alone_does_not_qualify_a_current_v3_context(change):
    raw = encounter()
    ep = raw["episode"]
    if change == "late_familiar":
        ep["events"][1]["provenance"]["measured_at"] = "2026-11-07T11:03:30Z"
        ep["events"][1]["provenance"]["recorded_at"] = "2026-11-07T11:04:00Z"
        ep["events"][2]["provenance"]["recorded_at"] = "2026-11-07T11:04:00Z"
    elif change == "old_trial":
        ep["events"][2]["provenance"]["measured_at"] = "2026-11-06T11:03:00Z"
    elif change == "old_acceptance":
        ep["events"][3]["provenance"]["measured_at"] = "2026-11-06T11:04:00Z"
    elif change == "no_acceptance":
        ep["events"].pop()
    elif change == "old_import":
        ep["events"][2]["provenance"]["origin"] = "DERIVED_FROM_HISTORY"
    else:
        raw["setting_choice"]["setting"]["value"] = 41.0
    assert api().compile_candidate(raw).state != "QUALIFIED"


def test_withdrawal_and_unavailable_never_start_work_or_erase_facts():
    raw = encounter()
    raw["withdrawn"] = True
    assert api().compile_candidate(raw).state == "WITHDRAWN"
    raw["withdrawn"] = False
    raw["availability"] = raw["episode"]["availability"] = "UNAVAILABLE"
    assert api().compile_candidate(raw).state == "UNAVAILABLE"
    assert len(raw["episode"]["events"]) == 4


def test_public_entry_without_authority_does_not_promote_preview():
    out = api().evaluate(encounter())
    assert out.admission == "NOT_ADMITTED"
    assert out.state == "INSUFFICIENT_EVIDENCE"
    assert out.qualified_setting is None
    assert not out.candidate_actions
    assert "INITIATE_TRIAL" not in out.allowed_actions


def test_real_v3_bridge_requires_seven_and_keeps_encounter_out_of_work_sets():
    from tools.science_initial_policy.v3_producer import produce_v3
    from tools.science_initial_policy.v3_validation import validate_admitted_exchange_v3

    registry = load_v3_registry()
    raw = plan_input()
    ep = api().compile_candidate(encounter()).portable_episode.model_dump(mode="json")
    assert ep["subject_ref"] == raw["subject_ref"]
    raw["episodes"] = [ep]
    one = produce_v3(raw, registry)
    assert one.scientific_readiness != "SCIENTIFICALLY_READY"
    raw = plan_input()
    raw["episodes"][0] = ep
    out = produce_v3(raw, registry)
    actual = validate_admitted_exchange_v3(raw, out, registry)
    assert actual.scientific_readiness == "SCIENTIFICALLY_READY"
    assert actual.start_permission == "REQUIRES_TIME_ACK"
    assert actual.candidate_plan.physical_work_sets_total == 28
    assert api().compile_candidate(encounter()).activity_kind == "CALIBRATION_ACTIVITY"


def test_canonical_validation_recomputes_not_only_schema():
    validation = importlib.import_module("tools.science_calibration_bootstrap.validation")
    raw = encounter()
    out = api().evaluate(raw)
    forged = out.model_copy(update={"allowed_actions": ("INITIATE_TRIAL",)})
    with pytest.raises(ValueError):
        validation.validate_result(raw, forged)


@pytest.mark.parametrize("proof", ["preparation", "setting_choice"])
def test_post_trial_setup_or_choice_does_not_qualify_an_earlier_attempt(proof):
    raw = encounter()
    raw[proof] = copy.deepcopy(raw[proof])
    p = raw[proof]["provenance"]
    p.update(recorded_at="2026-11-07T11:04:00Z", measured_at="2026-11-07T11:04:00Z")
    out = api().compile_candidate(raw)
    assert out.state != "QUALIFIED"
    assert "INITIATE_TRIAL" not in out.candidate_actions
    assert "ACCEPT_EXACT_SETTING" not in out.candidate_actions


def test_no_acceptance_action_without_context_confirmation():
    raw = encounter(stage="observed")
    raw["episode"]["events"] = raw["episode"]["events"][1:]
    assert "ACCEPT_EXACT_SETTING" not in api().compile_candidate(raw).candidate_actions


def test_context_confirmed_after_attempt_does_not_offer_acceptance():
    raw = encounter(stage="observed")
    raw["episode"] = copy.deepcopy(raw["episode"])
    context = raw["episode"]["events"][0]
    context["sequence"] = 4
    context["provenance"]["recorded_at"] = "2026-11-07T11:04:00Z"
    out = api().compile_candidate(raw)
    assert "ACCEPT_EXACT_SETTING" not in out.candidate_actions
