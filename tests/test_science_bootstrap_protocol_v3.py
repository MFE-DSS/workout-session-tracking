"""Typed protocol reviews are consistency, never scientific or account authority."""

import copy
import importlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def api():
    return importlib.import_module("tools.science_contracts.bootstrap_protocol_v3")


def sample():
    rows = json.loads(
        (
            ROOT / "docs/science/sci-p02-initial-policy/calibration-time-01/producer-fixtures.json"
        ).read_text()
    )
    return copy.deepcopy(
        next(r["request"] for r in rows if r["scenario"] == "returning")["episodes"][0]
    )


def trial():
    ep = sample()
    e = ep["events"][2]
    return dict(
        protocol_version="initial-calibration-review/2.0.0",
        subject_ref=ep["subject_ref"],
        event_id=e["event_id"],
        context=ep["context"],
        setting=e["setting"],
        provenance=e["provenance"],
        episode_started_at=ep["started_at"],
        as_of=ep["as_of"],
        observed_reps=10,
        min_reps=8,
        max_reps=12,
        stop_reason="COMPLETED",
        technique="ACCEPTABLE",
        discomfort="NO_CONCERN",
        reported_rir=None,
        effort_claim="UNKNOWN",
        effort_source_ref=None,
        effort_confidence="UNKNOWN",
        assessment="WITHIN_PRESCRIBED_REPS",
        next_action="RETRY_WITH_CONFIRMED_SETTING",
    )


def test_unknown_rir_does_not_invent_two_reps_or_a_cold_load():
    v = api().TrialReviewV3.model_validate(trial())
    assert v.reported_rir is None and v.effort_confidence == "UNKNOWN"
    assert v.setting.value == 40.0  # synthetic observation, not a prescribed constant


@pytest.mark.parametrize(
    "change",
    [
        "interrupted",
        "unknown_stop",
        "concern",
        "unknown_technique",
        "old_import",
        "false_effort",
        "bad_units",
        "future",
        "bool",
        "nan",
    ],
)
def test_trial_cannot_assert_qualification_from_inadequate_observation(change):
    raw = trial()
    if change == "interrupted":
        raw.update(stop_reason="INTERRUPTED", observed_reps=3, assessment="OUTSIDE_PRESCRIBED_REPS")
    elif change == "unknown_stop":
        raw["stop_reason"] = "UNKNOWN"
    elif change == "concern":
        raw["discomfort"] = "CONCERN"
    elif change == "unknown_technique":
        raw["technique"] = "UNKNOWN"
    elif change == "old_import":
        raw["provenance"]["measured_at"] = "2026-11-01T11:00:00Z"
    elif change == "false_effort":
        raw["effort_claim"] = "USER_REPORTED_EASY"
    elif change == "bad_units":
        raw["setting"]["unit"] = "setting"
    elif change == "future":
        raw["provenance"]["recorded_at"] = "2099-01-01T00:00:00Z"
    elif change == "bool":
        raw["observed_reps"] = True
    else:
        raw["reported_rir"] = float("nan")
    cls = api().TrialReviewV3
    with pytest.raises(ValueError):
        cls.model_validate(raw)


def test_interruption_and_concern_remain_explicit_not_causal_load_assessments():
    raw = trial()
    raw.update(
        stop_reason="INTERRUPTED", observed_reps=3, assessment="NOT_ASSESSABLE", next_action="NONE"
    )
    assert api().TrialReviewV3.model_validate(raw).assessment == "NOT_ASSESSABLE"
    raw.update(discomfort="CONCERN", assessment="REVIEW_REQUIRED", next_action="REVIEW")
    assert api().TrialReviewV3.model_validate(raw).next_action == "REVIEW"


def transition():
    ep = sample()
    context = ep["context"]
    context["load_semantics"] = "ASSISTANCE_SETTING"
    return dict(
        as_of=ep["as_of"],
        context=context,
        observed_setting={"kind": "ASSISTANCE_SETTING", "value": 10.0, "unit": "setting"},
        chosen_setting={"kind": "ASSISTANCE_SETTING", "value": 5.0, "unit": "setting"},
        available_in_effort_order=[
            {"kind": "ASSISTANCE_SETTING", "value": 10.0, "unit": "setting"},
            {"kind": "ASSISTANCE_SETTING", "value": 5.0, "unit": "setting"},
        ],
        order_source=ep["context_provenance"],
        direction="MORE_EFFORT",
    )


def test_effort_order_comes_from_device_source_not_increasing_numeric_assistance():
    value = api().SettingTransitionV3.model_validate(transition())
    assert value.chosen_setting.value < value.observed_setting.value


@pytest.mark.parametrize(
    "change",
    ["reverse", "invented_increment", "unknown_order", "wrong_kind", "duplicate", "unknown_origin"],
)
def test_transition_refuses_unsourced_or_unavailable_numeric_settings(change):
    raw = transition()
    if change == "reverse":
        raw["direction"] = "LESS_EFFORT"
    elif change == "invented_increment":
        raw["chosen_setting"]["value"] = 7.5
    elif change == "unknown_order":
        raw["order_source"] = None
    elif change == "wrong_kind":
        raw["chosen_setting"]["kind"] = "MASS_KG"
    elif change == "duplicate":
        raw["available_in_effort_order"].append(copy.deepcopy(raw["available_in_effort_order"][0]))
    else:
        raw["order_source"]["origin"] = "UNKNOWN"
    cls = api().SettingTransitionV3
    with pytest.raises(ValueError):
        cls.model_validate(raw)


@pytest.mark.parametrize(
    "budget,structure,state",
    [
        (4, "TRADITIONAL_SEQUENTIAL", "STRUCTURALLY_TOO_LONG"),
        (3, "TRADITIONAL_SEQUENTIAL", "STRUCTURALLY_TOO_LONG"),
        (5, "TRADITIONAL_SEQUENTIAL", "BUDGET_UNCERTAIN"),
        (100, "PAIRED_UNADMITTED", "BUDGET_UNCERTAIN"),
    ],
)
def test_partial_rest_floor_refutes_equality_without_making_positive_fit(budget, structure, state):
    session = {
        "session_id": "s",
        "slots": [{"prescription": {"work_sets": 3, "rest_seconds": 120}}],
    }
    v = api().assess_structural_time(session, budget_minutes=budget, structure=structure)
    assert v.state == state
    assert v.duration.state == "UNKNOWN"
    assert v.policy_ref is None


def test_protocol_has_four_referenced_phases_and_no_numeric_defaults():
    cls = api().CalibrationProtocolV3
    raw = dict(
        contract_version="initial-calibration-protocol/2.0.0",
        protocol_ref="CONTRACT_EXAMPLE_NOT_ADMITTED",
        source_ref="OPERATOR_PACKET_1.0.0",
        steps=[
            dict(kind=k, instruction_ref="EXAMPLE:" + k)
            for k in ["FAMILIARIZE", "TRIAL", "OBSERVE", "DECIDE"]
        ],
        stop_rule_ref="EXAMPLE:STOP",
        retry_rule_ref="EXAMPLE:RETRY",
    )
    assert len(cls.model_validate(raw).steps) == 4
    raw["warm_up_sets"] = 2
    with pytest.raises(ValueError):
        cls.model_validate(raw)


@pytest.mark.parametrize(
    "field,value", [("context_ref", None), ("side", "UNKNOWN"), ("load_semantics", "UNKNOWN")]
)
def test_unknown_execution_context_cannot_claim_a_qualified_retry(field, value):
    raw = trial()
    raw["context"][field] = value
    cls = api().TrialReviewV3
    with pytest.raises(ValueError):
        cls.model_validate(raw)


def test_future_device_order_is_not_an_available_current_transition():
    raw = transition()
    raw["as_of"] = sample()["as_of"]
    cls = api().SettingTransitionV3
    cls.model_validate(raw)
    raw["order_source"]["recorded_at"] = "2099-01-01T00:00:00Z"
    cls = api().SettingTransitionV3
    with pytest.raises(ValueError):
        cls.model_validate(raw)


@pytest.mark.parametrize("case", ["nested_nan", "copied_infinity", "nested_bool", "copied_context"])
def test_typed_trial_revalidates_unchecked_copied_models(case):
    cls = api().TrialReviewV3
    valid = cls.model_validate(trial())
    raw = trial()
    if case == "nested_nan":
        raw["setting"] = valid.setting.model_copy(update={"value": float("nan")})
    elif case == "copied_infinity":
        raw = valid.model_copy(update={"reported_rir": float("inf")})
    elif case == "nested_bool":
        raw["setting"] = valid.setting.model_copy(update={"value": True})
    else:
        raw["context"] = valid.context.model_copy(update={"side": "IMPOSSIBLE"})
    with pytest.raises(ValueError):
        cls.model_validate(raw)


@pytest.mark.parametrize(
    "field,value",
    [
        ("canonical_exercise_id", None),
        ("context_ref", None),
        ("equipment_ref", None),
        ("realization_ref", None),
        ("side", "UNKNOWN"),
    ],
)
def test_numeric_transition_requires_exact_identified_context(field, value):
    raw = transition()
    raw["context"][field] = value
    cls = api().SettingTransitionV3
    with pytest.raises(ValueError):
        cls.model_validate(raw)
    raw.update(direction="NONE", chosen_setting=None)
    assert cls.model_validate(raw).direction == "NONE"


@pytest.mark.parametrize("upper", [60.0, 1200.0, 1201.0])
def test_supported_duration_cannot_contradict_known_rest_floor(upper):
    raw = dict(
        session_id="s",
        state="SUPPORTED",
        known_rest_floor_seconds=1200.0,
        duration=dict(
            state="SUPPORTED",
            budget_minutes=75,
            lower_seconds=1.0,
            upper_seconds=upper,
            unit="seconds",
            basis_kind="ADMITTED_PRODUCT_CONVENTION",
            basis_ref="HYPOTHETICAL_NOT_ADMITTED",
            basis_version="test-v1",
            scope_fingerprint="0" * 64,
            applicability_ref="HYPOTHETICAL_SCOPE",
            covers_bootstrap=True,
            coverage=["WORK", "REST", "PREPARATION_CALIBRATION", "SETUP_TRANSITION"],
            evidence_refs=["EV-71"],
            limitations=["Shape only."],
        ),
        unknown_components=[],
        policy_ref="HYPOTHETICAL_POLICY",
        assumption_refs=[],
        limitations=["Not admitted."],
    )
    cls = api().TimeAssessmentV3
    if upper <= 1200:
        with pytest.raises(ValueError):
            cls.model_validate(raw)
    else:
        assert cls.model_validate(raw).duration.upper_seconds == upper


def test_absent_structure_never_invents_sequential_rest_floor():
    session = {
        "session_id": "s",
        "slots": [{"prescription": {"work_sets": 2, "rest_seconds": 120}}],
    }
    value = api().assess_structural_time(session, budget_minutes=2)
    assert value.state == "BUDGET_UNCERTAIN"
    assert value.known_rest_floor_seconds is None
    assert "STRUCTURE_UNSUPPORTED" in value.unknown_components
