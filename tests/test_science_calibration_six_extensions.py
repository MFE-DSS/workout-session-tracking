"""Six limited encounters from synthetic actual-choice facts, never runtime data."""

import copy
import importlib

import pytest

from tools.science_calibration_bootstrap.artifacts import synthetic_plan_input
from tools.science_initial_policy.calibration_time_contracts import ContextKey, context_digest

IDS = (
    "chest-press-machine",
    "rowing-chest-supported",
    "romanian-deadlift-halteres",
    "tirage-poulie-haute-prise-neutre",
    "elevations-laterales-machine",
    "releves-mollets-debout-machine",
)


def api():
    return importlib.import_module("tools.science_calibration_extension.evaluator")


def encounter(candidate=IDS[0], stage="qualified"):
    plan = synthetic_plan_input()
    ep = copy.deepcopy(
        next(e for e in plan["episodes"] if e["context"]["canonical_exercise_id"] == candidate)
    )
    load = ep["events"][0]["setting"]
    ep["events"][1]["setting"] = copy.deepcopy(load)
    p = copy.deepcopy(ep["context_provenance"])
    raw = dict(
        contract_version="first-calibration-encounter/1.0.0",
        encounter_ref="synthetic:" + candidate,
        subject_ref=ep["subject_ref"],
        source_revision="synthetic:source/1",
        started_at=ep["started_at"],
        as_of=ep["as_of"],
        population=plan["blueprint"]["population_scope"],
        limitations=plan["blueprint"]["limitations"],
        context=ep["context"],
        context_provenance=p,
        availability="AVAILABLE",
        ledger_complete=True,
        ledger_source_ref="synthetic:complete-ledger",
        concern_state="CLEAR",
        withdrawn=False,
        episode=ep,
        preparation=dict(
            context_fingerprint=context_digest(ContextKey.model_validate(ep["context"])),
            instruction_ref="synthetic:actual-device-instructions",
            setup_ref="synthetic:actual-setup",
            understood=True,
            controlled=True,
            provenance=p,
        ),
        setting_choice=dict(
            context_fingerprint=context_digest(ContextKey.model_validate(ep["context"])),
            setting=copy.deepcopy(load),
            available=True,
            provenance=p,
        ),
        stop_reasons={ep["events"][2]["event_id"]: "COMPLETED"},
        retry_requested=False,
    )
    if stage == "open":
        raw.update(episode=None, preparation=None, setting_choice=None, stop_reasons={})
    elif stage == "setup":
        raw.update(episode=None, setting_choice=None, stop_reasons={})
    elif stage == "trial":
        ep["events"] = ep["events"][:2]
        raw["stop_reasons"] = {}
    elif stage == "observed":
        ep["events"] = ep["events"][:3]
    return raw


@pytest.mark.parametrize("candidate", IDS)
@pytest.mark.parametrize(
    "stage,state",
    [
        ("open", "CALIBRATION_REQUIRED"),
        ("setup", "SUPPORTED_INITIAL_EXPLORATION"),
        ("trial", "SUPPORTED_INITIAL_EXPLORATION"),
        ("observed", "OBSERVED"),
        ("qualified", "QUALIFIED"),
    ],
)
def test_each_realization_progresses_without_seven_prior_settings(candidate, stage, state):
    raw = encounter(candidate, stage)
    out = api().compile_candidate(raw)
    assert out.state == state
    assert out.admission == "NOT_ADMITTED"
    assert "INITIATE_TRIAL" not in out.allowed_actions
    assert out.duration == "UNKNOWN"
    assert out.effort_sufficiency == "UNKNOWN"
    if stage == "qualified":
        assert out.portable_episode.context.canonical_exercise_id == candidate
        assert out.qualified_setting.model_dump(mode="json") == raw["setting_choice"]["setting"]
        assert out.confidence == "LOW"
    elif stage == "trial":
        assert "INITIATE_TRIAL" in out.candidate_actions
    elif stage == "observed":
        assert "ACCEPT_EXACT_SETTING" in out.candidate_actions
    else:
        assert "INITIATE_TRIAL" not in out.candidate_actions
        assert out.qualified_setting is None


@pytest.mark.parametrize(
    "change,stage",
    [
        (change, stage)
        for change in (
            "no_setting",
            "different_setting",
            "boolean_only",
            "late_familiar",
            "late_context",
            "late_choice",
            "late_setup",
            "later_restart",
        )
        for stage in ("trial", "observed", "qualified")
        if (change, stage) != ("late_familiar", "trial")
    ],
)
def test_exact_loaded_familiarization_cannot_be_replaced_by_history_or_boolean(change, stage):
    raw = encounter(stage=stage)
    ep = raw["episode"]
    if change == "no_setting":
        ep["events"][1]["setting"] = None
    elif change == "different_setting":
        ep["events"][1]["setting"]["value"] = 41.0
    elif change == "boolean_only":
        ep["events"].pop(1)
        for e in ep["events"]:
            if e["kind"] == "ATTEMPT_OBSERVED":
                e["familiarization_confirmed"] = True
    elif change == "later_restart":
        e = copy.deepcopy(ep["events"][1])
        e.update(kind="FAMILIARIZATION_STARTED", event_id="later-start", sequence=10)
        e["provenance"]["recorded_at"] = "2026-11-07T11:10:00Z"
        ep["events"].append(e)
    else:
        proof = {
            "late_familiar": ep["events"][1],
            "late_context": ep["events"][0],
            "late_choice": raw["setting_choice"],
            "late_setup": raw["preparation"],
        }[change]
        if change in {"late_familiar", "late_context"}:
            proof["sequence"] = 10
        proof["provenance"].update(
            recorded_at="2026-11-07T11:05:00Z", measured_at="2026-11-07T11:05:00Z"
        )
    out = api().compile_candidate(raw)
    assert out.state != "QUALIFIED"
    assert "INITIATE_TRIAL" not in out.candidate_actions
    assert "ACCEPT_EXACT_SETTING" not in out.candidate_actions


@pytest.mark.parametrize(
    "change",
    [
        "global",
        "unknown_global",
        "ledger",
        "predecessor",
        "quality",
        "unknown_quality",
        "discomfort",
        "unknown_stop",
        "withdrawn",
        "unavailable",
        "population",
        "limitations",
        "control",
        "old_choice",
    ],
)
def test_concern_or_missing_applicability_closes_physical_guidance(change):
    raw = encounter()
    trial = raw["episode"]["events"][2]
    if change == "global":
        raw["concern_state"] = "REPORTED"
    elif change == "unknown_global":
        raw["concern_state"] = "UNKNOWN"
    elif change == "ledger":
        raw["ledger_complete"] = False
    elif change == "predecessor":
        raw["episode"].update(previous_episode_id="old", predecessor_blocked=True)
    elif change == "quality":
        trial["technique"] = "CONCERN"
    elif change == "unknown_quality":
        trial["technique"] = "UNKNOWN"
    elif change == "discomfort":
        trial["discomfort"] = "UNKNOWN"
    elif change == "unknown_stop":
        raw["stop_reasons"][trial["event_id"]] = "UNKNOWN"
    elif change == "withdrawn":
        raw["withdrawn"] = True
    elif change == "unavailable":
        raw["availability"] = raw["episode"]["availability"] = "UNAVAILABLE"
    elif change == "population":
        raw["population"].update(state="UNKNOWN", value=None)
    elif change == "limitations":
        raw["limitations"]["value"] = ["reported limitation"]
    elif change == "control":
        raw["preparation"]["controlled"] = False
    else:
        raw["setting_choice"]["provenance"]["recorded_at"] = "2026-11-06T11:00:00Z"
    raw.update(retry_requested=True, encounter_ref="new-id-not-a-reset")
    out = api().compile_candidate(raw)
    assert out.state != "QUALIFIED"
    assert not out.candidate_actions
    assert "RECORD_TRIAL" in out.allowed_actions
    assert len(raw["episode"]["events"]) == 4


@pytest.mark.parametrize("reason", ["TIME_LIMIT", "USER_STOPPED"])
def test_interruption_keeps_observation_and_requires_explicit_retry(reason):
    raw = encounter(stage="observed")
    trial = raw["episode"]["events"][-1]
    trial.update(completed=False, successful=None, reps=4)
    raw["stop_reasons"][trial["event_id"]] = reason
    out = api().compile_candidate(raw)
    assert out.state == "OBSERVED"
    assert "INITIATE_TRIAL" not in out.candidate_actions
    raw["retry_requested"] = True
    assert "INITIATE_TRIAL" in api().compile_candidate(raw).candidate_actions
    assert "ACCEPT_EXACT_SETTING" not in api().compile_candidate(raw).candidate_actions


@pytest.mark.parametrize("candidate", IDS)
@pytest.mark.parametrize("change", ["realization", "side", "semantics"])
def test_no_transfer_between_realizations_sides_or_setting_semantics(candidate, change):
    raw = encounter(candidate, "setup")
    if change == "realization":
        raw["context"]["realization_ref"] = "other-realization"
    elif change == "side":
        raw["context"]["side"] = "LEFT"
    else:
        raw["context"]["load_semantics"] = "TOTAL_EXTERNAL"
    raw["preparation"]["context_fingerprint"] = context_digest(
        ContextKey.model_validate(raw["context"])
    )
    out = api().compile_candidate(raw)
    assert not out.candidate_actions
    assert out.state in {"UNAVAILABLE", "INSUFFICIENT_EVIDENCE"}


def test_rdl_rehearsal_is_not_a_mass_zero_or_trial():
    raw = encounter(IDS[2], "setup")
    out = api().compile_candidate(raw)
    assert out.state == "SUPPORTED_INITIAL_EXPLORATION"
    assert "INITIATE_FAMILIARIZATION" in out.candidate_actions
    assert "INITIATE_TRIAL" not in out.candidate_actions
    assert raw["setting_choice"] is None
    assert out.portable_episode is None
    assert out.qualified_setting is None


def policy():
    return importlib.import_module("tools.science_calibration_extension.policy")


def test_public_evaluation_requires_actual_published_authority():
    out = api().evaluate(encounter())
    assert out.admission == "NOT_ADMITTED"
    assert out.state == "INSUFFICIENT_EVIDENCE"
    assert out.portable_episode is None
    assert "INITIATE_TRIAL" not in out.allowed_actions
    with pytest.raises(ValueError):
        api().evaluate(encounter(), {"state": "ADMITTED_WITH_LIMITS"})


@pytest.mark.parametrize("change", ["policy", "sources", "bundle", "parent"])
def test_caller_cannot_mutate_published_authority(change):
    import dataclasses

    a = policy().load_authority()
    if change == "policy":
        p = dict(a.policy)
        p["status"] = "WITHDRAWN"
        a = dataclasses.replace(a, policy=p)
    elif change == "sources":
        a = dataclasses.replace(a, source_digests={})
    elif change == "bundle":
        a = dataclasses.replace(a, bundle_digest="0" * 64)
    else:
        a = dataclasses.replace(a, historical=None)
    with pytest.raises(ValueError):
        api().evaluate(encounter(), a)


def test_source_drift_cannot_reuse_cached_authority(tmp_path):
    import shutil

    a = policy().load_authority()
    for rel in set(a.source_digests) | {
        str(policy().DIRECTORY / "registry.v1.json"),
        str(policy().DIRECTORY / "sources.v1.json"),
    }:
        dest = tmp_path / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(a.root / rel, dest)
    local = policy().load_authority(tmp_path)
    target = tmp_path / "tools/science_calibration_extension/evaluator.py"
    target.write_text(target.read_text() + "\n# drift\n")
    with pytest.raises(ValueError, match="source drift"):
        api().evaluate(encounter(), local)


@pytest.mark.parametrize(
    "field,value",
    [("available", True), ("value", float("nan")), ("value", float("inf")), ("value", True)],
)
def test_strict_setting_revalidation_rejects_native_coercions(field, value):
    from tools.science_calibration_bootstrap.contracts import validated_input

    raw = encounter()
    if field == "available":
        req = validated_input(raw)
        invalid = req.model_copy(
            update={"setting_choice": req.setting_choice.model_copy(update={"available": 1})}
        )
    else:
        raw["setting_choice"]["setting"][field] = value
        invalid = raw
    with pytest.raises(ValueError):
        api().compile_candidate(invalid)


@pytest.mark.parametrize("stage", ["trial", "observed", "qualified"])
def test_actual_published_permissions_and_canonical_validation(stage):
    validation = importlib.import_module("tools.science_calibration_extension.validation")
    a = policy().load_authority()
    raw = encounter(stage=stage)
    out = api().evaluate(raw, a)
    assert out.admission == "ADMITTED_WITH_LIMITS"
    assert not out.candidate_actions
    assert validation.validate_result(raw, out, a) == out
    altered = out.model_dump(mode="json")
    altered["state"] = "CALIBRATION_REQUIRED" if out.state == "QUALIFIED" else "QUALIFIED"
    with pytest.raises(ValueError):
        validation.validate_result(raw, altered, a)


def test_independent_qualification_rejects_c3_boolean_without_loaded_confirmation():
    validation = importlib.import_module("tools.science_calibration_extension.validation")
    raw = encounter()
    a = policy().load_authority()
    good = api().evaluate(raw, a)
    raw["episode"]["events"][1]["setting"] = None
    raw["episode"]["events"][2]["familiarization_confirmed"] = True
    with pytest.raises(ValueError):
        validation.validate_result(raw, good, a)
    assert api().evaluate(raw, a).state != "QUALIFIED"


def test_six_real_encounters_and_pilot_bridge_through_real_v3_and_exact_ack():
    artifacts = importlib.import_module("tools.science_calibration_extension.artifacts")
    result = artifacts.bridge()
    assert len(result["encounters"]) == 7
    assert all(e["result"]["state"] == "QUALIFIED" for e in result["encounters"])
    assert result["before_ack"]["scientific_readiness"] == "SCIENTIFICALLY_READY"
    assert result["before_ack"]["start_permission"] == "REQUIRES_TIME_ACK"
    assert result["after_ack"]["start_permission"] == "ELIGIBLE"
    assert all(t["duration"]["state"] == "UNKNOWN" for t in result["after_ack"]["time_assessments"])
    assert result["after_ack"]["candidate_plan"]["physical_work_sets_total"] == 28
    assert len(result["request"]["episodes"]) == 7
    assert result["artifact_kind"] == "REAL_EVALUATORS_AND_V3_SYNTHETIC_INPUT_NOT_SERVED"
    from tools.science_initial_policy.v3_admission import load_v3_registry
    from tools.science_initial_policy.v3_producer import produce_v3
    from tools.science_initial_policy.v3_validation import validate_admitted_exchange_v3

    req = copy.deepcopy(result["request"])
    req["episodes"].pop()
    out = produce_v3(req, load_v3_registry())
    assert out.start_permission == "DENIED"
    assert validate_admitted_exchange_v3(req, out, load_v3_registry()) == out
    req = copy.deepcopy(result["acknowledged_request"])
    req["acknowledgment"]["plan_time_fingerprint"] = "0" * 64
    with pytest.raises(ValueError):
        produce_v3(req, load_v3_registry())


def test_exports_are_reproducible_and_not_a_source_of_permission():
    artifacts = importlib.import_module("tools.science_calibration_extension.artifacts")
    assert artifacts.verify_artifacts()
    import json

    fixtures = json.loads(artifacts.build_artifacts()["encounter-fixtures.v1.json"])
    assert len(fixtures["cases"]) == 30
    assert sum(c["result"]["state"] == "QUALIFIED" for c in fixtures["cases"]) == 6
    assert all(c["result"]["duration"] == "UNKNOWN" for c in fixtures["cases"])


def test_recording_late_does_not_erase_actual_earlier_familiarization():
    raw = encounter()
    events = raw["episode"]["events"]
    for e in events:
        e["provenance"]["measured_at"] = e["provenance"]["recorded_at"]
        e["provenance"]["recorded_at"] = "2026-11-07T11:10:00Z"
    assert api().compile_candidate(raw).state == "QUALIFIED"


def test_no_current_choice_preserves_history_but_does_not_qualify_it():
    raw = encounter()
    events = copy.deepcopy(raw["episode"]["events"])
    raw["setting_choice"] = None
    out = api().compile_candidate(raw)
    assert out.state == "SUPPORTED_INITIAL_EXPLORATION"
    assert "INITIATE_TRIAL" not in out.candidate_actions
    assert out.portable_episode is None
    assert raw["episode"]["events"] == events


def test_trial_without_prior_attempt_can_follow_later_current_familiarization():
    raw = encounter(stage="trial")
    raw["episode"]["events"][1]["provenance"]["recorded_at"] = "2026-11-07T11:05:00Z"
    assert "INITIATE_TRIAL" in api().compile_candidate(raw).candidate_actions


@pytest.mark.parametrize("stage", ["trial", "observed", "qualified"])
@pytest.mark.parametrize("candidate", IDS)
def test_newer_episode_context_invalidates_prior_loaded_familiarization(stage, candidate):
    raw = encounter(candidate, stage=stage)
    raw["episode"]["context_provenance"].update(
        recorded_at="2026-11-07T11:10:00Z", measured_at="2026-11-07T11:10:00Z"
    )
    out = api().compile_candidate(raw)
    assert out.state != "QUALIFIED"
    assert "INITIATE_TRIAL" not in out.candidate_actions
    assert "ACCEPT_EXACT_SETTING" not in out.candidate_actions
