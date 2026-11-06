"""A bounded scientific role decision must not turn corroboration into credit or READY."""

import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "docs/science/sci-p02-initial-policy/pull-exposure-01"
NEUTRAL = "tirage-poulie-haute-prise-neutre"
WIDE = "tirage-poulie-haute-prise-large"


def api():
    assert importlib.util.find_spec("tools.science_initial_policy.pull_exposure") is not None
    from tools.science_initial_policy.pull_exposure import (
        load_pull_exposure,
        resolve_vertical_pull,
        validate_pull_exposure,
    )

    return load_pull_exposure, resolve_vertical_pull, validate_pull_exposure


def request():
    return copy.deepcopy(
        json.loads(
            (ROOT / "docs/science/sci-p02-initial-policy/v1/producer-fixtures.json").read_text()
        )[0]["request"]
    )


def raw():
    return json.loads((FOLDER / "overlay.v1.json").read_text())


def confirm(req, candidate, state="AVAILABLE"):
    env = req["blueprint"]["environment"]
    env["exercise_confirmations"].append(
        {
            "canonical_exercise_id": candidate,
            "context_ref": env["context_ref"],
            "state": state,
            "provenance": copy.deepcopy(req["blueprint"]["sessions_per_week"]["provenance"]),
        }
    )


def test_reviewed_neutral_realization_has_one_explicit_bounded_role_delta():
    load, resolve, _ = api()
    bundle = load()
    out = resolve(request(), bundle)
    assert out["status"] == "CANDIDATES_AVAILABLE"
    assert [x["candidate_id"] for x in out["candidates"]] == [NEUTRAL]
    assert len(out["held_candidates"]) == 4
    assert out["parent_curation_status"] == "CATALOG_GAP"
    candidate = out["candidates"][0]
    assert candidate["role_projection"]["source_unknown_roles"] == ["pecs"]
    assert candidate["role_projection"]["unknown_roles"] == []
    assert "pecs" in candidate["role_projection"]["secondary_roles"]
    assert candidate["role_projection"]["scope"] == "QUALIFIED_CANONICAL_EXECUTION_ONLY"
    assert candidate["role_projection"]["application"] == "NOT_APPLIED_TO_EXECUTED_HISTORY"
    assert candidate["execution_confirmation_required"] is True
    assert candidate["rep_range_achievability"] == "UNCONFIRMED"
    assert out["selected"] is None
    assert out["execution_ready"] is False
    assert out["runtime_availability"] == "NOT_SERVED"
    assert out["ready_fixture"] == "NOT_PRODUCED"


@pytest.mark.parametrize("authority", ["ACUTE_EMG", "ANATOMICAL_CAPACITY_ONLY"])
def test_observed_activity_or_capacity_alone_cannot_authorize_a_role_delta(authority):
    _, _, validate = api()
    data = raw()
    data["role_delta"][0]["authority_type"] = authority
    with pytest.raises(ValueError):
        validate(data)


@pytest.mark.parametrize("role", ["PRIMARY", "MINOR"])
def test_no_unreviewed_primary_or_stabilization_category_is_fabricated(role):
    _, _, validate = api()
    data = raw()
    data["role_delta"][0]["after"] = role
    with pytest.raises(ValueError):
        validate(data)


@pytest.mark.parametrize(
    "field", ["hypertrophy_percentage", "secondary_credit", "load_kg", "setup_minutes"]
)
def test_no_numeric_physiology_credit_load_or_time_is_added(field):
    _, _, validate = api()
    data = raw()
    data["candidates"][0][field] = 0.5
    with pytest.raises(ValueError):
        validate(data)


def test_supported_participation_does_not_count_as_secondary_when_category_is_unknown():
    load, resolve, _ = api()
    out = resolve(request(), load())
    candidate = next(x for x in out["held_candidates"] if x["candidate_id"] == WIDE)
    assert "pecs" in candidate["role_projection"]["unknown_roles"]
    assert "pecs" not in candidate["role_projection"]["secondary_roles"]
    assert "credit" not in candidate
    assert "credit" not in out


def test_blocking_primary_uncertainty_cannot_be_hidden_in_a_reviewed_overlay():
    _, _, validate = api()
    data = raw()
    row = next(x for x in data["candidates"] if x["candidate_id"] == NEUTRAL)
    next(x for x in row["effective_roles"] if x["zone"] == "lats")["role"] = "UNKNOWN"
    with pytest.raises(ValueError):
        validate(data)


@pytest.mark.parametrize(
    "replacement", ["rowing-chest-supported", "pullover-cable-paren-bras-tendus-poulie-haute"]
)
def test_vertical_pool_cannot_import_other_patterns_or_aliases(replacement):
    _, _, validate = api()
    data = raw()
    data["candidates"][0]["candidate_id"] = replacement
    with pytest.raises(ValueError):
        validate(data)


def test_missing_or_duplicate_candidate_is_not_an_implicit_pool_amendment():
    _, _, validate = api()
    data = raw()
    data["candidates"].pop()
    with pytest.raises(ValueError):
        validate(data)
    data = raw()
    data["candidates"][-1] = copy.deepcopy(data["candidates"][0])
    with pytest.raises(ValueError):
        validate(data)


def test_neutral_width_and_front_path_cannot_be_changed_by_the_overlay():
    _, _, validate = api()
    data = raw()
    row = next(x for x in data["candidates"] if x["candidate_id"] == NEUTRAL)
    row["canonical_execution"] = "Any neutral grip, behind head allowed"
    with pytest.raises(ValueError):
        validate(data)


def test_unreviewed_or_forged_review_flags_are_not_scientific_authority():
    load, resolve, validate = api()
    data = raw()
    data["scientific_review"] = "PENDING"
    pending = validate(data)
    req = request()
    with pytest.raises(ValueError):
        resolve(req, pending)
    trusted = load()
    forged = trusted.model_copy(update={"contract_decision": "IGNORE_UNCERTAINTY"})
    with pytest.raises(ValueError):
        resolve(req, forged)


def test_source_hash_set_cannot_be_omitted_or_expanded_to_private_paths():
    _, _, validate = api()
    data = raw()
    data["source_sha256"] = {}
    with pytest.raises(ValueError):
        validate(data)
    data = raw()
    data["source_sha256"]["/private/arbitrary/file"] = "0" * 64
    with pytest.raises(ValueError):
        validate(data)


def test_available_equipment_never_certifies_execution_or_calibration():
    load, resolve, _ = api()
    req = request()
    confirm(req, NEUTRAL)
    out = resolve(req, load())
    candidate = out["candidates"][0]
    assert candidate["compatibility"] == "CONFIRMED"
    assert candidate["role_projection"]["scope"] == "QUALIFIED_CANONICAL_EXECUTION_ONLY"
    assert candidate["role_projection"]["application"] == "NOT_APPLIED_TO_EXECUTED_HISTORY"
    assert candidate["execution_confirmation_required"] is True
    assert candidate["rep_range_achievability"] == "UNCONFIRMED"
    assert out["execution_ready"] is False


def test_three_state_context_conflict_stays_a_conflict():
    load, resolve, _ = api()
    req = request()
    for state in ("AVAILABLE", "UNAVAILABLE", "UNKNOWN"):
        confirm(req, NEUTRAL, state)
    out = resolve(req, load())
    assert out["status"] == "REVIEW_REQUIRED"
    assert out["candidates"] == []


def test_explicit_exclusion_or_unavailability_has_no_fallback():
    load, resolve, _ = api()
    req = request()
    confirm(req, NEUTRAL, "UNAVAILABLE")
    out = resolve(req, load())
    assert out["status"] == "CATALOG_GAP"
    assert out["candidates"] == []
    req = request()
    req["blueprint"]["excluded_exercise_ids"].update(
        state="KNOWN",
        value=[NEUTRAL],
        conflicts=[],
        provenance=copy.deepcopy(req["blueprint"]["sessions_per_week"]["provenance"]),
    )
    out = resolve(req, load())
    assert out["status"] == "CATALOG_GAP"
    assert out["candidates"] == []


def test_reported_limitation_is_reviewed_without_diagnosis():
    load, resolve, _ = api()
    req = request()
    req["blueprint"]["limitations"]["value"] = ["reported discomfort"]
    out = resolve(req, load())
    assert out["status"] == "REVIEW_REQUIRED"
    assert out["candidates"] == []


def test_missing_required_context_is_not_a_scientific_admission():
    load, resolve, _ = api()
    req = request()
    fact = req["blueprint"]["limitations"]
    fact.update(state="UNKNOWN", value=None, conflicts=[])
    fact["provenance"].update(
        origin="UNKNOWN",
        acquisition="UNKNOWN",
        source_ref=None,
        recorded_at=None,
        measured_at=None,
    )
    out = resolve(req, load())
    assert out["status"] == "REVIEW_REQUIRED"
    assert out["candidates"] == []


def test_another_context_confirmation_is_rejected_rather_than_reused():
    load, resolve, _ = api()
    req = request()
    confirm(req, NEUTRAL)
    req["blueprint"]["environment"]["exercise_confirmations"][-1]["context_ref"] = "other-context"
    bundle = load()
    with pytest.raises(ValueError):
        resolve(req, bundle)


def test_held_unilateral_realizations_keep_each_side_calibration():
    load, resolve, _ = api()
    out = resolve(request(), load())
    row = next(
        x for x in out["held_candidates"] if x["candidate_id"] == "tirage-vertical-unilateral-cable"
    )
    assert row["unilateral"] is True
    assert "EACH_SIDE_NO_LOAD_TRANSFER" in row["calibration_facts"]


def test_resolution_is_deterministic_and_does_not_mutate_inputs_or_choose_a_default():
    load, resolve, _ = api()
    req = request()
    before = copy.deepcopy(req)
    bundle = load()
    out = resolve(req, bundle)
    assert out == resolve(req, bundle)
    assert req == before
    assert out["selected"] is None


def test_historical_curation_and_producer_remain_byte_reproducible():
    from tools.science_initial_policy.curation import load_curation
    from tools.science_initial_policy.fixtures import generated_cases

    path = ROOT / "docs/science/sci-p02-initial-policy/curation-01/candidates.v1.json"
    assert (
        hashlib.sha256(path.read_bytes()).hexdigest()
        == "d1a3f26268bcb33d3614ce3b4841a2dc42562541b39134646caabf9f37f37803"
    )
    assert len(load_curation().candidates) == 40
    path = ROOT / "docs/science/sci-p02-initial-policy/v1/producer-fixtures.json"
    assert (
        hashlib.sha256(path.read_bytes()).hexdigest()
        == "db31e5f0d247f72b54c52d681c04fb2ea319d6a7e68091f5dd905447afb278a1"
    )
    assert generated_cases() == json.loads(path.read_text())


def test_no_runtime_or_old_producer_statically_imports_the_new_overlay():
    forbidden = "tools.science_initial_policy.pull_exposure"
    paths = list((ROOT / "app").rglob("*.py")) + [
        ROOT / "tools/science_initial_policy/producer.py",
        ROOT / "tools/science_initial_policy/registry.py",
        ROOT / "tools/science_initial_policy/planning.py",
    ]
    for path in paths:
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.ImportFrom):
                module_name = node.module or ""
                assert not module_name.startswith(forbidden)
            elif isinstance(node, ast.Import):
                assert not any(n.name.startswith(forbidden) for n in node.names)


def test_versioned_consumer_fixtures_reproduce_without_a_ready_payload():
    assert (
        importlib.util.find_spec("tools.science_initial_policy.pull_exposure_fixtures") is not None
    )
    from tools.science_initial_policy.pull_exposure_fixtures import generated_cases

    cases = generated_cases()
    assert cases == json.loads((FOLDER / "fixtures.v1.json").read_text())
    assert all(c["result"]["execution_ready"] is False for c in cases)
    assert all(c["result"]["ready_fixture"] == "NOT_PRODUCED" for c in cases)
