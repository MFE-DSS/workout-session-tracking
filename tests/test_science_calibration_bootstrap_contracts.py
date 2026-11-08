"""Strict encounter exchange and copied-object adversaries."""

import importlib

import pytest

from tests.science_bootstrap_samples import encounter


def api():
    return importlib.import_module("tools.science_calibration_bootstrap.contracts")


def test_open_without_history_is_valid_and_does_not_invent_a_setting():
    req = api().validated_input(encounter(stage="open"))
    assert req.setting_choice is None
    assert req.episode is None
    assert api().input_digest(req) == api().input_digest(req.model_dump(mode="json"))


@pytest.mark.parametrize(
    "change",
    [
        "subject",
        "context",
        "future",
        "before_start",
        "availability",
        "bool",
        "nan",
        "extra",
        "choice_context",
        "instruction_future",
    ],
)
def test_structural_inconsistencies_are_rejected(change):
    raw = encounter()
    if change == "subject":
        raw["episode"]["subject_ref"] = "subject:B"
    elif change == "context":
        raw["context"]["equipment_ref"] = "other-device"
    elif change == "future":
        raw["episode"]["as_of"] = "2027-01-01T00:00:00Z"
    elif change == "before_start":
        raw["started_at"] = "2027-01-01T00:00:00Z"
    elif change == "availability":
        raw["availability"] = "UNAVAILABLE"
    elif change == "bool":
        raw["setting_choice"]["setting"]["value"] = True
    elif change == "nan":
        raw["setting_choice"]["setting"]["value"] = float("nan")
    elif change == "extra":
        raw["initial_kg"] = 2.5
    elif change == "choice_context":
        raw["setting_choice"]["context_fingerprint"] = "a" * 64
    else:
        raw["preparation"]["provenance"]["recorded_at"] = "2027-01-01T00:00:00Z"
    with pytest.raises(ValueError):
        api().validated_input(raw)


@pytest.mark.parametrize("bad", [True, float("inf"), float("nan")])
def test_copied_nested_numeric_values_revalidated_without_json_coercion(bad):
    req = api().validated_input(encounter())
    choice = req.setting_choice.model_copy(
        update={"setting": req.setting_choice.setting.model_copy(update={"value": bad})}
    )
    altered = req.model_copy(update={"setting_choice": choice})
    with pytest.raises(ValueError):
        api().validated_input(altered)


def test_digest_changes_with_observation_or_revision():
    raw = encounter()
    before = api().input_digest(raw)
    raw["source_revision"] = "synthetic:source/2"
    assert before != api().input_digest(raw)


def test_unknown_facts_and_context_are_representable_for_opening():
    raw = encounter(stage="open")
    for key in ("population", "limitations"):
        raw[key].update(state="UNKNOWN", value=None, conflicts=[])
    raw["context"] = {
        k: None if k not in ("side", "load_semantics") else "UNKNOWN" for k in raw["context"]
    }
    raw["availability"] = "UNKNOWN"
    assert api().validated_input(raw).context.equipment_ref is None
