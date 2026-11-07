"""Fresh review regressions against actual authority, with intentional producer fault injection."""

import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

from tests.test_science_initial_policy_v3 import ROOT, request
from tools.science_contracts.blueprint_first_plan_v3 import (
    evaluation_fingerprint,
    observation_fingerprint,
    request_fingerprint,
    validated_request,
)
from tools.science_initial_policy.v3_admission import load_v3_registry
from tools.science_initial_policy.v3_producer import produce_v3
from tools.science_initial_policy.v3_validation import _observed_slot, validate_admitted_exchange_v3


def chronology(raw, contradictory):
    events = raw["episodes"][0]["events"]
    for event in events[:2]:
        event["provenance"]["measured_at"] = event["provenance"]["recorded_at"]
    events[2]["provenance"]["measured_at"] = (
        "2026-11-07T11:00:01Z" if contradictory else "2026-11-07T11:02:30Z"
    )
    return raw


def test_explicit_trial_occurrence_before_preparation_denies_plan():
    r = load_v3_registry()
    out = produce_v3(chronology(request(r), True), r)
    assert out.candidate_plan is None
    assert out.start_permission == "DENIED"


def test_occurrence_guard_independent_of_current_producer():
    r = load_v3_registry()
    raw = request(r)
    good = produce_v3(raw, r)
    with pytest.raises(ValueError):
        _observed_slot(
            validated_request(chronology(raw, True)),
            good.candidate_plan.sessions[0].slots[0],
            r.policy["selection"][0],
            "session-1",
            0,
            r,
        )


def test_valid_delayed_recording_preserves_occurrence_order():
    r = load_v3_registry()
    raw = chronology(request(r), False)
    out = produce_v3(raw, r)
    assert out.scientific_readiness == "SCIENTIFICALLY_READY"
    assert validate_admitted_exchange_v3(raw, out, r) == out


@pytest.mark.parametrize(
    "path",
    [
        "tools/science_initial_policy/admission_calibration.py",
        "tools/science_initial_policy/load_calibration.py",
        "tools/science_initial_policy/calibration_time_contracts.py",
        "tools/science_contracts/blueprint_first_plan_v2.py",
        "tools/science_contracts/first_plan_v2_validation.py",
        "tools/science_initial_policy/v2_registry.py",
    ],
)
def test_effective_helper_drift_invalidates_admission_root(tmp_path, path):
    seen = set()
    original = Path.read_bytes

    def trace(p):
        if p.is_relative_to(ROOT):
            seen.add(p)
        return original(p)

    with patch.object(Path, "read_bytes", trace):
        load_v3_registry()
    for source in seen:
        target = tmp_path / source.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    target = tmp_path / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("# altered effective helper\n")
    with pytest.raises(ValueError):
        load_v3_registry(tmp_path)


@pytest.mark.parametrize("change", ["missing_limitations", "conflicting_exclusions"])
def test_independent_public_validation_refuses_identical_faulty_replay(change):
    r = load_v3_registry()
    raw = request(r)
    good = produce_v3(raw, r)
    if change == "missing_limitations":
        raw["blueprint"]["limitations"].update(state="UNKNOWN", value=None)
    else:
        f = raw["blueprint"]["excluded_exercise_ids"]
        f.update(
            state="CONFLICT",
            value=None,
            conflicts=[
                dict(value=[], source_ref="a"),
                dict(value=["leg-extensions-assises"], source_ref="b"),
            ],
        )
    forged = good.model_copy(
        update=dict(
            request_fingerprint=request_fingerprint(raw),
            observation_fingerprint=observation_fingerprint(raw),
            full_evaluation_fingerprint=evaluation_fingerprint(raw),
        )
    )
    with patch("tools.science_initial_policy.v3_producer.produce_v3", return_value=forged):
        with pytest.raises(ValueError):
            validate_admitted_exchange_v3(raw, forged, r)


def test_nullable_context_source_returns_review_not_comparison_error():
    r = load_v3_registry()
    raw = request(r)
    raw["episodes"][0]["context_provenance"]["recorded_at"] = None
    out = produce_v3(raw, r)
    assert out.scientific_readiness == "REVIEW_REQUIRED"
    assert out.start_permission == "DENIED"
    assert validate_admitted_exchange_v3(raw, out, r) == out


def test_independent_nullable_context_source_is_explicitly_rejected():
    r = load_v3_registry()
    raw = request(r)
    out = produce_v3(raw, r)
    raw["episodes"][0]["context_provenance"]["recorded_at"] = None
    with pytest.raises(ValueError):
        _observed_slot(
            validated_request(raw),
            out.candidate_plan.sessions[0].slots[0],
            r.policy["selection"][0],
            "session-1",
            0,
            r,
        )


@pytest.mark.parametrize("same", [True, False])
def test_availability_conflict_belongs_to_consumed_gym_context(same):
    r = load_v3_registry()
    raw = request(r)
    raw["blueprint"]["environment"]["exercise_confirmations"] = [
        dict(
            canonical_exercise_id=raw["episodes"][0]["context"]["canonical_exercise_id"],
            context_ref="gym:test-a" if same else "other-gym",
            state="UNAVAILABLE",
            provenance=raw["episodes"][0]["context_provenance"],
        )
    ]
    out = produce_v3(raw, r)
    assert out.scientific_readiness == ("REVIEW_REQUIRED" if same else "SCIENTIFICALLY_READY")
    assert validate_admitted_exchange_v3(raw, out, r) == out
