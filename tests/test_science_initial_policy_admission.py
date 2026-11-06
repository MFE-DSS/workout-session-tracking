"""Admission diagnostics cannot promote an unserved proposal to a prescription."""

import copy
import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def assess(slots, budget=30, structure="TRADITIONAL_SEQUENTIAL"):
    from tools.science_initial_policy.time_feasibility import assess_time

    return assess_time({"slots": [{"prescription": s} for s in slots]}, budget, structure)


def test_only_between_set_rests_count_not_after_last_set_or_between_exercises():
    out = assess(
        [{"work_sets": 2, "rest_seconds": 120}] * 4 + [{"work_sets": 2, "rest_seconds": 90}] * 3
    )
    assert out["known_rest_floor_seconds"] == 750
    assert out["feasibility"] == "UNKNOWN"
    assert out["issue_code"] == "TIME_UNCERTAIN"
    assert out["duration"] == {
        "state": "UNKNOWN",
        "lower_minutes": None,
        "upper_minutes": None,
        "model_ref": None,
    }


@pytest.mark.parametrize("budget", [1, 4])
def test_work_remains_when_rest_floor_equals_or_exceeds_budget(budget):
    out = assess([{"work_sets": 3, "rest_seconds": 120}], budget)
    assert out["known_rest_floor_seconds"] == 240
    assert out["feasibility"] == "NOT_FEASIBLE"
    assert out["issue_code"] == "CONSTRAINT_VIOLATION"
    assert out["scope"] == "THIS_CONFIGURATION_ONLY"


@pytest.mark.parametrize("budget", [5, 100000, None])
def test_above_floor_or_missing_budget_is_never_a_fit_claim(budget):
    out = assess([{"work_sets": 3, "rest_seconds": 120}], budget)
    assert out["feasibility"] == "UNKNOWN"
    assert out["issue_code"] == "TIME_UNCERTAIN"


def test_missing_rest_gives_partial_floor_without_inventing_zero_rest():
    out = assess([{"work_sets": 2, "rest_seconds": 120}, {"work_sets": 2, "rest_seconds": None}])
    assert out["known_rest_floor_seconds"] == 120
    assert out["rest_floor_complete"] is False
    assert "REST_UNSPECIFIED" in out["unknown_components"]


def test_one_set_has_no_intraslot_rest_even_if_rest_value_absent():
    out = assess([{"work_sets": 1, "rest_seconds": None}])
    assert out["known_rest_floor_seconds"] == 0
    assert out["rest_floor_complete"] is True
    assert out["feasibility"] == "UNKNOWN"


@pytest.mark.parametrize("structure", ["SUPERSET", "UNKNOWN", "PAIRED"])
def test_overlapping_or_unknown_structure_cannot_sum_sequential_rests(structure):
    out = assess([{"work_sets": 4, "rest_seconds": 120}], 1, structure)
    assert out["known_rest_floor_seconds"] is None
    assert out["feasibility"] == "UNKNOWN"
    assert "STRUCTURE_UNSUPPORTED" in out["unknown_components"]


@pytest.mark.parametrize(
    "slot",
    [
        {"work_sets": True, "rest_seconds": 120},
        {"work_sets": 0, "rest_seconds": 120},
        {"work_sets": 2.5, "rest_seconds": 120},
        {"work_sets": 2, "rest_seconds": -1},
        {"work_sets": 2, "rest_seconds": float("nan")},
        {"work_sets": 2, "rest_seconds": True},
    ],
)
def test_invalid_prescription_is_not_silently_normalized(slot):
    with pytest.raises(ValueError):
        assess([slot])


@pytest.mark.parametrize("budget", [0, -1, True, 2.5, float("inf")])
def test_invalid_budget_is_rejected(budget):
    with pytest.raises(ValueError):
        assess([{"work_sets": 2, "rest_seconds": 120}], budget)


def test_empty_session_cannot_prove_feasibility():
    with pytest.raises(ValueError):
        assess([])


def test_actual_producer_session_can_be_analyzed_without_mutating_it():
    from tools.science_initial_policy import inspect_policy, load_registry, produce
    from tools.science_initial_policy.time_feasibility import assess_time

    cases = json.loads(
        (ROOT / "docs/science/sci-p02-initial-policy/v1/producer-fixtures.json").read_text()
    )
    request = cases[0]["request"]
    registry = load_registry()
    draft = inspect_policy(request, registry)
    before = copy.deepcopy(draft)
    out = assess_time(draft["sessions"][0], 100000)
    assert out["feasibility"] == "UNKNOWN"
    assert draft == before
    assert produce(request, registry).status == "POLICY_UNAVAILABLE"


def test_new_admission_does_not_rewrite_old_policy_or_recommendations():
    from tools.science_initial_policy.fixtures import generated_cases
    from tools.science_initial_policy.registry import POLICY_PATH, POLICY_SHA256

    assert hashlib.sha256((ROOT / POLICY_PATH).read_bytes()).hexdigest() == POLICY_SHA256
    old = ROOT / "docs/science/sci-p02-initial-policy/v1/producer-fixtures.json"
    assert hashlib.sha256(old.read_bytes()).hexdigest() == (
        "db31e5f0d247f72b54c52d681c04fb2ea319d6a7e68091f5dd905447afb278a1"
    )
    assert generated_cases() == json.loads(old.read_text())


def test_losing_required_input_cannot_increase_recommendation_confidence():
    from tools.science_initial_policy import load_registry, produce

    cases = json.loads(
        (ROOT / "docs/science/sci-p02-initial-policy/v1/producer-fixtures.json").read_text()
    )
    registry = load_registry()
    sufficient = produce(cases[0]["request"], registry)
    missing = produce(
        next(c["request"] for c in cases if c["scenario"] == "insufficient"), registry
    )
    assert missing.status == "INSUFFICIENT_DATA"
    assert missing.confidence.feasibility == sufficient.confidence.feasibility == "UNKNOWN"
    assert (
        missing.confidence.individual_response
        == sufficient.confidence.individual_response
        == "NOT_ESTIMATED"
    )


def test_reviewed_artifact_separates_product_default_from_measured_evidence():
    path = ROOT / "docs/science/sci-p02-initial-policy/admission-01/policy.json"
    policy = json.loads(path.read_text())
    assert policy["policy_version"] == "initial-hypertrophy-policy/0.2.0-partially-admitted"
    assert policy["admission_state"] == "PARTIALLY_ADMITTED"
    assert policy["runtime_availability"] == "NOT_SERVED"
    assert policy["ready_eligible"] is False
    assert policy["engine_binding"] is None
    evidence = json.loads((ROOT / "data/sci/evidence_registry.json").read_text())
    for rule in policy["rules"]:
        assert rule["evidence_refs"]
        assert set(rule["evidence_refs"]) <= evidence.keys()
        assert rule["population"]
        assert rule["review_trigger"]
        assert rule["limitations"]
    dose = {r["rule_id"]: r for r in policy["rules"]}
    for name in ("work_sets", "repetitions", "effort", "rest"):
        assert dose[name]["decision"] == "ADMITTED_AS_CONSERVATIVE_DEFAULT"
        assert dose[name]["basis"] == "CONVENTION"
        assert dose[name]["exact_value_certainty"] == "INSUFFICIENT"
    assert dose["time"]["decision"] == "ADMITTED_WITH_LIMITS"
    assert dose["candidates"]["decision"] == "NOT_ADMITTED"


def test_versioned_diagnostics_reproduce_and_keep_catalogue_gaps():
    from tools.science_initial_policy.admission import build_audit

    actual = build_audit()
    target = ROOT / "docs/science/sci-p02-initial-policy/admission-01/audit.json"
    assert actual == json.loads(target.read_text())
    assert actual["ready_fixture"] == "READY_NOT_PRODUCED"
    vertical = next(
        r for r in actual["intent_audit"] if r["intent_id"] == "initial_vertical_pull_v1"
    )
    assert all(c["unknown_role_zones"] for c in vertical["candidates"])
    assert all(c["stability"] == "UNKNOWN" for c in vertical["candidates"])
    for case in actual["cases"]:
        assert case["response"]["status"] != "READY"
        assert case["response"]["confidence"]["individual_response"] == "NOT_ESTIMATED"
    unknown = next(c for c in actual["cases"] if c["scenario"] == "unknown_gym")
    assert "COMPATIBILITY_UNKNOWN" in {i["code"] for i in unknown["response"]["issues"]}
