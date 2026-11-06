"""Scientific curation earns an eligibility set, never an executable recommendation."""

import copy
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def api():
    from tools.science_initial_policy.curation import (
        load_curation,
        resolve_candidates,
        validate_curation,
    )

    return load_curation, resolve_candidates, validate_curation


def request():
    cases = json.loads(
        (ROOT / "docs/science/sci-p02-initial-policy/v1/producer-fixtures.json").read_text()
    )
    return copy.deepcopy(cases[0]["request"])


def confirm(req, identity, state="AVAILABLE"):
    env = req["blueprint"]["environment"]
    env["exercise_confirmations"].append(
        {
            "canonical_exercise_id": identity,
            "context_ref": env["context_ref"],
            "state": state,
            "provenance": copy.deepcopy(req["blueprint"]["sessions_per_week"]["provenance"]),
        }
    )


def raw():
    return json.loads(
        (ROOT / "docs/science/sci-p02-initial-policy/curation-01/candidates.v1.json").read_text()
    )


def test_every_current_candidate_has_one_disposition_without_pool_widening():
    load, _, _ = api()
    c = load()
    assert len(c.candidates) == 40
    assert len({(r.intent_id, r.candidate_id) for r in c.candidates}) == 40
    assert c.runtime_availability == "NOT_SERVED"
    assert c.producer_binding is None
    assert c.ready_fixture == "NOT_PRODUCED"


@pytest.mark.parametrize("replacement", ["MINOR", "SECONDARY", "PRIMARY"])
def test_unknown_is_not_changed_to_satisfy_coverage_even_with_emg_citation(replacement):
    _, _, validate = api()
    data = raw()
    row = next(
        r for r in data["candidates"] if r["candidate_id"] == "tirage-poulie-haute-prise-neutre"
    )
    role = next(r for r in row["roles"] if r["role"] == "UNKNOWN")
    role.update(role=replacement, role_basis="emg_only", evidence_refs=["EV-70"])
    with pytest.raises(ValueError, match="roles"):
        validate(data)


def test_unsupported_candidate_is_not_added_as_substitution():
    _, _, validate = api()
    data = raw()
    data["candidates"][0]["candidate_id"] = "adduction-assise"
    with pytest.raises(ValueError):
        validate(data)


@pytest.mark.parametrize(
    "field,value",
    [("quality_score", 93), ("starting_load_kg", 10), ("setup_seconds", 30), ("stability", 8)],
)
def test_no_scalar_ranking_load_or_duration_fields(field, value):
    _, _, validate = api()
    data = raw()
    data["candidates"][0][field] = value
    with pytest.raises(ValueError):
        validate(data)


def test_machine_mode_is_not_invented_and_regional_scope_cannot_be_widened():
    _, _, validate = api()
    data = raw()
    row = next(r for r in data["candidates"] if r["candidate_id"] == "chest-press-machine")
    row["equipment_mode"] = "machine_selectorized"
    with pytest.raises(ValueError, match="canonical"):
        validate(data)
    data = raw()
    row = next(r for r in data["candidates"] if r["candidate_id"] == "chest-press-machine")
    row["regional_claim_refs"] = ["CALF_KNEE_POSITION"]
    with pytest.raises(ValueError, match="regional"):
        validate(data)


def test_gear_confirmation_never_proves_calibration_or_execution_readiness():
    load, resolve, _ = api()
    req = request()
    confirm(req, "chest-press-machine")
    out = resolve(req, "initial_press_v1", load())
    c = next(c for c in out["candidates"] if c["candidate_id"] == "chest-press-machine")
    assert c["compatibility"] == "CONFIRMED"
    assert c["rep_range_achievability"] == "UNCONFIRMED"
    assert out["execution_ready"] is False
    assert out["ready_fixture"] == "NOT_PRODUCED"


def test_unknown_equipment_and_bodyweight_capacity_remain_unknown_without_inventory():
    load, resolve, _ = api()
    req = request()
    req["blueprint"]["environment"]["exercise_confirmations"] = []
    out = resolve(req, "initial_press_v1", load())
    machine = next(c for c in out["candidates"] if c["candidate_id"] == "chest-press-machine")
    pushup = next(c for c in out["candidates"] if c["candidate_id"] == "pompes")
    assert machine["compatibility"] == "UNKNOWN"
    assert pushup["compatibility"] == "NOT_REQUIRED"
    assert pushup["rep_range_achievability"] == "UNCONFIRMED"


def test_no_vertical_candidate_earns_exact_exposure_admission():
    load, resolve, _ = api()
    out = resolve(request(), "initial_vertical_pull_v1", load())
    assert out["status"] == "CATALOG_GAP"
    assert out["candidates"] == []
    assert len(out["held_candidates"]) == 5
    assert all(c["unknown_roles"] for c in out["held_candidates"])


def test_all_candidates_excluded_preserves_gap_and_historical_records():
    load, resolve, _ = api()
    c = load()
    req = request()
    fact = req["blueprint"]["excluded_exercise_ids"]
    fact.update(
        state="KNOWN",
        value=[r.candidate_id for r in c.candidates if r.intent_id == "initial_press_v1"],
        conflicts=[],
    )
    fact["provenance"] = copy.deepcopy(req["blueprint"]["sessions_per_week"]["provenance"])
    out = resolve(req, "initial_press_v1", c)
    assert out["status"] == "CATALOG_GAP"
    assert len(c.candidates) == 40


def test_unavailable_or_conflicting_context_cannot_be_confirmed():
    load, resolve, _ = api()
    req = request()
    confirm(req, "chest-press-machine", "UNAVAILABLE")
    out = resolve(req, "initial_press_v1", load())
    assert not any(c["candidate_id"] == "chest-press-machine" for c in out["candidates"])
    confirm(req, "chest-press-machine")
    out = resolve(req, "initial_press_v1", load())
    assert out["status"] == "REVIEW_REQUIRED"
    assert out["candidates"] == []


def test_unknown_confirmation_cannot_hide_an_existing_context_conflict():
    load, resolve, _ = api()
    req = request()
    for state in ("AVAILABLE", "UNAVAILABLE", "UNKNOWN"):
        confirm(req, "chest-press-machine", state)
    out = resolve(req, "initial_press_v1", load())
    assert out["status"] == "REVIEW_REQUIRED"
    assert out["reason"] == "CURRENT_CONTEXT_CONFLICT"
    assert out["candidates"] == []


def test_user_reported_limitation_requires_review_not_diagnosis():
    load, resolve, _ = api()
    req = request()
    req["blueprint"]["limitations"]["value"] = ["reported discomfort"]
    out = resolve(req, "initial_press_v1", load())
    assert out["status"] == "REVIEW_REQUIRED"
    assert out["candidates"] == []
    assert out["reason"] == "USER_REPORTED_LIMITATION"


def test_reproducible_no_default_ordering_no_side_or_identity_loss():
    load, resolve, _ = api()
    req = request()
    before = copy.deepcopy(req)
    c = load()
    out = resolve(req, "initial_row_v1", c)
    assert out == resolve(req, "initial_row_v1", c)
    assert req == before
    assert out["selected"] is None
    unilateral = next(
        c for c in out["candidates"] if c["candidate_id"] == "rowing-haltere-un-bras-paren-banc"
    )
    assert unilateral["unilateral"] is True
    assert "EACH_SIDE_NO_LOAD_TRANSFER" in unilateral["calibration_facts"]


def test_original_producer_policy_and_historical_fingerprints_remain_reproducible():
    from tools.science_initial_policy.fixtures import generated_cases

    cases = json.loads(
        (ROOT / "docs/science/sci-p02-initial-policy/v1/producer-fixtures.json").read_text()
    )
    assert generated_cases() == cases
    assert all(c["response"]["status"] != "READY" for c in cases)


def test_audit_validation_cannot_omit_canonical_hashes_or_add_arbitrary_read_paths():
    _, _, validate = api()
    data = raw()
    data["source_sha256"] = {}
    with pytest.raises(ValueError, match="source set"):
        validate(data)
    data = raw()
    data["source_sha256"]["/arbitrary/private/file"] = "0" * 64
    with pytest.raises(ValueError, match="source set"):
        validate(data)


def test_structural_validation_is_not_authority_for_forged_dispositions():
    load, resolve, _ = api()
    bundle = load()
    original = next(r for r in bundle.candidates if r.candidate_id == "sissy-squat-machine")
    forged = original.model_copy(
        update={"initial_scope_admission": "ADMITTED_WITH_CONTEXT_CONFIRMATION"}
    )
    other = bundle.model_copy(
        update={"candidates": [forged if r == original else r for r in bundle.candidates]}
    )
    with pytest.raises(ValueError, match="trusted"):
        resolve(request(), "initial_quad_v1", other)


def test_curation_uses_only_its_context_inputs_without_requiring_anthropometry_or_time():
    load, resolve, _ = api()
    req = request()
    for field in ("height_cm", "weight_kg", "session_budgets_minutes"):
        fact = req["blueprint"][field]
        fact.update(state="UNKNOWN", value=None, conflicts=[])
        fact["provenance"].update(
            origin="UNKNOWN",
            acquisition="UNKNOWN",
            source_ref=None,
            recorded_at=None,
            measured_at=None,
        )
    out = resolve(req, "initial_press_v1", load())
    assert out["status"] == "CANDIDATES_AVAILABLE"
    assert out["execution_ready"] is False


def test_coverage_unknown_and_none_known_are_distinct_and_artifacts_reproduce():
    from tools.science_initial_policy.curation_fixtures import generated_artifacts

    out = generated_artifacts()
    expected = json.loads(
        (
            ROOT / "docs/science/sci-p02-initial-policy/curation-01/coverage-and-fixtures.v1.json"
        ).read_text()
    )
    assert out == expected
    assert len(out["coverage"]) == 7
    assert all(len(r["zones"]) == 15 for r in out["coverage"])
    vertical = next(r for r in out["coverage"] if r["intent_id"] == "initial_vertical_pull_v1")
    assert "UNKNOWN" in vertical["zones"]["pecs"]["candidate_role_states"]
    assert vertical["admissible_candidate_count"] == 0
    assert out["effective_role_changes"] == []


def test_proposed_e0_delta_uses_canonical_evidence_id_syntax_without_overwriting_e0():
    folder = ROOT / "docs/science/sci-p02-initial-policy/curation-01"
    delta = json.loads((folder / "evidence-delta.v1.json").read_text())
    schema = json.loads((ROOT / "data/sci/exercise_catalogue.schema.json").read_text())
    pattern = schema["$defs"]["contribution"]["properties"]["evidence_refs"]["items"]["pattern"]
    current = json.loads((ROOT / delta["target"]).read_text())
    assert delta["status"] == "PROPOSED_NOT_APPLIED"
    assert delta["runtime_import"] is False
    assert set(delta["entries"]).isdisjoint(current)
    for identity, record in delta["entries"].items():
        assert re.fullmatch(pattern, identity)
        assert set(record) == {"claim", "row"}
        assert delta["provenance"][identity]["doi"]
