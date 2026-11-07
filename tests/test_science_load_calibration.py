"""Real replay tests: observed references are not true-RIR or optimal-load estimates."""

import copy
import importlib
import importlib.util
import json

import pytest

from tests.science_calibration_samples import (
    calibrated_episode,
    context,
    digest,
    episode,
    event,
    setting,
)


def api():
    name = "tools.science_initial_policy.load_calibration"
    assert importlib.util.find_spec(name) is not None, "calibration replay is not implemented"
    return importlib.import_module(name).calibrate


def test_no_history_never_fabricates_initial_kg():
    out = api()(episode(), min_reps=8, max_reps=12)
    assert out["state"] == "NEEDS_CALIBRATION"
    assert out["load_kg"] is None
    assert out["observed_setting"] is None


def test_calibrated_setting_is_exactly_the_observed_reference_with_optional_rir():
    source = calibrated_episode()
    original = copy.deepcopy(source)
    out = api()(source, min_reps=8, max_reps=12)
    assert out["state"] == "CALIBRATED"
    assert out["load_kg"] == 40.0
    assert out["load_mode"] == "HISTORY_SUPPORTED"
    assert out["reference_event_id"] == "e3"
    assert out["reference_source_ref"] == "synthetic:event-3"
    assert out["effort_sufficiency"] == "UNKNOWN"
    assert out["confidence"] == "LOW"
    assert source == original
    source["events"][2]["rir"] = 4.0
    again = api()(source, min_reps=8, max_reps=12)
    assert again["load_kg"] == 40.0
    assert again["reported_rir"] == 4.0
    assert again["effort_sufficiency"] == "UNKNOWN"


def test_declaration_without_trial_cannot_become_calibrated():
    raw = episode([event("CONTEXT_CONFIRMED", 1, setting=setting())])
    out = api()(raw, min_reps=8, max_reps=12)
    assert out["state"] == "NEEDS_CALIBRATION"
    assert out["load_kg"] is None


@pytest.mark.parametrize("field", ["equipment_ref", "realization_ref"])
def test_unknown_context_does_not_claim_comparable_load(field):
    ctx = context(**{field: None})
    out = api()(episode(ctx=ctx), min_reps=8, max_reps=12)
    assert out["state"] == "INSUFFICIENT_DATA"
    assert out["load_kg"] is None


def test_unknown_availability_and_unavailable_are_distinct():
    raw = calibrated_episode()
    raw["availability"] = "UNKNOWN"
    assert api()(raw, min_reps=8, max_reps=12)["state"] == "INSUFFICIENT_DATA"
    raw["availability"] = "UNAVAILABLE"
    out = api()(raw, min_reps=8, max_reps=12)
    assert out["state"] == "UNAVAILABLE"
    assert out["load_kg"] is None


def test_started_familiarization_is_not_positive_confirmation():
    raw = calibrated_episode()
    raw["events"][1]["kind"] = "FAMILIARIZATION_STARTED"
    assert api()(raw, min_reps=8, max_reps=12)["state"] == "CALIBRATION_IN_PROGRESS"
    raw["events"].pop(1)
    raw["events"][1]["familiarization_confirmed"] = True
    out = api()(raw, min_reps=8, max_reps=12)
    assert out["state"] == "CALIBRATED"
    assert out["reference_role"] == "CALIBRATION_TRIAL"


@pytest.mark.parametrize("field,value", [
    ("technique", "CONCERN"), ("technique", "UNKNOWN"),
    ("discomfort", "CONCERN"), ("discomfort", "UNKNOWN"),
    ("successful", False), ("completed", False), ("reps", None),
])
def test_unknown_or_concerning_trial_cannot_earn_positive_load(field, value):
    raw = calibrated_episode()
    raw["events"][2][field] = value
    out = api()(raw, min_reps=8, max_reps=12)
    assert out["state"] != "CALIBRATED"
    assert out["load_kg"] is None
    assert out["automatic_next_action"] == "NONE"


def test_concern_is_terminal_within_episode_despite_later_acceptance():
    raw = calibrated_episode()
    raw["events"] += [
        event("CONCERN_REPORTED", 5),
        event("SETTING_ACCEPTED", 6, reference_event_id="e3"),
    ]
    original = copy.deepcopy(raw)
    out = api()(raw, min_reps=8, max_reps=12)
    assert out["state"] == "CALIBRATION_IN_PROGRESS"
    assert "EPISODE_REVIEW_REQUIRED" in out["reasons"]
    assert out["load_kg"] is None
    assert raw == original


def test_restart_label_cannot_invent_review_authority():
    raw = calibrated_episode()
    raw.update(previous_episode_id="old", predecessor_blocked=True, restart_basis_ref="says-approved")
    out = api()(raw, min_reps=8, max_reps=12)
    assert out["state"] == "INSUFFICIENT_DATA"
    assert "RESTART_POLICY_UNAVAILABLE" in out["reasons"]
    assert out["load_kg"] is None


def test_incomplete_ledger_does_not_certify_no_prior_concern():
    out = api()(calibrated_episode() | {"ledger_complete": False}, min_reps=8, max_reps=12)
    assert out["state"] == "INSUFFICIENT_DATA"


def test_returning_history_needs_current_available_setting_and_acceptance():
    raw = calibrated_episode()
    raw["events"][2]["provenance"].update(
        origin="DERIVED_FROM_HISTORY", measured_at="2026-07-01T10:00:00Z",
    )
    assert api()(raw, min_reps=8, max_reps=12)["state"] == "CALIBRATED"
    raw["events"] = raw["events"][1:3]
    out = api()(raw, min_reps=8, max_reps=12)
    assert out["state"] != "CALIBRATED"
    assert out["load_kg"] is None


def test_reps_outside_prescribed_range_do_not_trigger_kg_arithmetic():
    raw = calibrated_episode()
    raw["events"][2]["reps"] = 4
    out = api()(raw, min_reps=8, max_reps=12)
    assert out["state"] != "CALIBRATED"
    assert out["load_kg"] is None


@pytest.mark.parametrize("meaning,load", [
    ("ASSISTANCE_SETTING", setting(20.0, "ASSISTANCE_SETTING", "kg")),
    ("PER_IMPLEMENT", setting()),
    ("MACHINE_DISPLAY_KG", setting()),
    ("BODYWEIGHT", setting(None, "BODYWEIGHT", "none")),
    ("NON_MASS_SETTING", setting(3.0, "NON_MASS_SETTING", "setting")),
])
def test_non_total_load_setting_is_not_silently_projected_to_external_kg(meaning, load):
    raw = calibrated_episode(ctx=context(load_semantics=meaning), load=load)
    out = api()(raw, min_reps=8, max_reps=12)
    assert out["state"] == "CALIBRATED"
    assert out["observed_setting"] == load
    assert out["load_kg"] is None
    assert out["load_mode"] == "NOT_DEFINED"


@pytest.mark.parametrize("mutation", ["owner", "equipment", "side", "exercise"])
def test_event_cannot_cross_subject_or_context_identity(mutation):
    raw = calibrated_episode()
    if mutation == "owner":
        raw["events"][2]["subject_ref"] = "subject:B"
    else:
        key = {"equipment": "equipment_ref", "side": "side", "exercise": "canonical_exercise_id"}[mutation]
        altered = context(**{key: "RIGHT" if key == "side" else "different"})
        raw["events"][2]["context_fingerprint"] = digest(altered)
    run = api()
    with pytest.raises(ValueError):
        run(raw, min_reps=8, max_reps=12)


@pytest.mark.parametrize("value", [True, -1.0, float("nan"), float("inf")])
def test_illegal_observed_setting_is_rejected_not_coerced(value):
    raw = calibrated_episode()
    raw["events"][2]["setting"]["value"] = value
    run = api()
    with pytest.raises(ValueError):
        run(raw, min_reps=8, max_reps=12)


def test_future_fact_unknown_unit_and_population_prior_do_not_become_observations():
    run = api()
    variants = []
    future = calibrated_episode()
    future["events"][2]["provenance"]["recorded_at"] = "2026-11-06T12:01:00Z"
    variants.append(future)
    unit = calibrated_episode()
    unit["events"][2]["setting"]["unit"] = "lb"
    variants.append(unit)
    prior = calibrated_episode()
    prior["events"][2]["provenance"]["origin"] = "POPULATION_PRIOR"
    variants.append(prior)
    for raw in variants:
        with pytest.raises(ValueError):
            run(raw, min_reps=8, max_reps=12)


def test_replay_order_duplicates_and_file_restart_are_deterministic(tmp_path):
    raw = calibrated_episode()
    run = api()
    first = run(raw, min_reps=8, max_reps=12)
    raw["events"] = list(reversed(raw["events"])) + [copy.deepcopy(raw["events"][2])]
    assert run(raw, min_reps=8, max_reps=12) == first
    target = tmp_path / "episode.json"
    target.write_text(json.dumps(raw))
    recovered = json.loads(target.read_text())
    assert run(recovered, min_reps=8, max_reps=12) == first
    recovered["events"][-1]["reps"] = 9
    with pytest.raises(ValueError):
        run(recovered, min_reps=8, max_reps=12)


def test_typed_model_copy_is_revalidated_at_public_boundary():
    run = api()
    contracts = importlib.import_module("tools.science_initial_policy.calibration_time_contracts")
    model = contracts.CalibrationEpisode.model_validate(calibrated_episode())
    forged = model.model_copy(update={"subject_ref": "subject:B"})
    with pytest.raises(ValueError):
        run(forged, min_reps=8, max_reps=12)


def test_new_trial_start_cannot_reuse_older_positive_acceptance():
    raw = calibrated_episode()
    raw["events"].append(event("FAMILIARIZATION_STARTED", 5))
    out = api()(raw, min_reps=8, max_reps=12)
    assert out["state"] == "CALIBRATION_IN_PROGRESS"
    assert out["load_kg"] is None


def test_old_familiarization_flag_does_not_replace_current_confirmation():
    raw = calibrated_episode()
    raw["events"].pop(1)
    raw["events"][1]["familiarization_confirmed"] = True
    raw["events"][1]["provenance"].update(
        origin="DERIVED_FROM_HISTORY", measured_at="2026-07-01T10:00:00Z",
    )
    out = api()(raw, min_reps=8, max_reps=12)
    assert out["state"] == "CALIBRATION_IN_PROGRESS"


def test_acceptance_payload_cannot_contradict_the_referenced_setting():
    raw = calibrated_episode()
    raw["events"][-1]["setting"] = setting(50.0)
    out = api()(raw, min_reps=8, max_reps=12)
    assert out["state"] != "CALIBRATED"


@pytest.mark.parametrize("mutation", ["unknown_acquisition", "history_confirmation", "unlinked_predecessor"])
def test_incomplete_or_incoherent_confirmation_source_is_rejected(mutation):
    raw = calibrated_episode()
    if mutation == "unknown_acquisition":
        raw["events"][0]["provenance"]["acquisition"] = "UNKNOWN"
    elif mutation == "history_confirmation":
        raw["events"][0]["provenance"]["origin"] = "DERIVED_FROM_HISTORY"
    else:
        raw["predecessor_blocked"] = True
    run = api()
    with pytest.raises(ValueError):
        run(raw, min_reps=8, max_reps=12)


def test_unknown_context_acquisition_does_not_prove_availability():
    raw = calibrated_episode()
    raw["context_provenance"]["acquisition"] = "UNKNOWN"
    assert api()(raw, min_reps=8, max_reps=12)["state"] == "INSUFFICIENT_DATA"


@pytest.mark.filterwarnings("ignore:Pydantic serializer warnings:UserWarning")
@pytest.mark.parametrize("updates", [{"value": -40.0}, {"unit": "lb"}, {"value": float("nan")}])
@pytest.mark.parametrize("construct", [False, True])
def test_nested_model_copies_in_raw_dict_cannot_bypass_setting_validation(updates, construct):
    from tools.science_initial_policy.calibration_time_contracts import CalibrationEpisode
    model = CalibrationEpisode.model_validate(calibrated_episode())
    data = calibrated_episode()
    original = model.events[2].setting
    forged_setting = original.model_copy(update=updates)
    if construct:
        forged_setting = type(original).model_construct(**(original.model_dump() | updates))
    data["events"][0] = model.events[0].model_copy(update={"setting": forged_setting})
    data["events"][2] = model.events[2].model_copy(update={"setting": forged_setting})
    run = api()
    with pytest.raises(ValueError):
        run(data, min_reps=8, max_reps=12)
