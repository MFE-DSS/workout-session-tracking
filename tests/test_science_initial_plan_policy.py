"""Real isolated producer tests; no test-created policy admission or runtime activation."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def api():
    from tools.science_initial_policy import inspect_policy, load_registry, produce

    return load_registry, inspect_policy, produce


def request(scenario="sufficient"):
    fixtures = json.loads((ROOT / "docs/science/sci-p01-p02/v1/fixtures.json").read_text())
    req = copy.deepcopy(next(f["request"] for f in fixtures if f["scenario"] == scenario))
    req["versions"]["engine"] = "initial-policy-producer/1.0.0"
    if req["blueprint"]["sessions_per_week"]["state"] == "KNOWN":
        req["blueprint"]["sessions_per_week"]["value"] = 2
    req["blueprint"]["session_budgets_minutes"]["value"] = [75, 75]
    return req


def confirmation(req, exercise_id, state="AVAILABLE", context=None):
    return {
        "canonical_exercise_id": exercise_id,
        "context_ref": context or req["blueprint"]["environment"]["context_ref"],
        "state": state,
        "provenance": copy.deepcopy(req["blueprint"]["sessions_per_week"]["provenance"]),
    }


def unknown(req, field):
    fact = req["blueprint"][field]
    fact.update(state="UNKNOWN", value=None, conflicts=[])
    fact["provenance"].update(
        origin="UNKNOWN", acquisition="UNKNOWN", source_ref=None, recorded_at=None, measured_at=None
    )


def test_current_producer_never_promotes_sufficient_inputs_to_ready():
    load, _, produce = api()
    r = load()
    out = produce(request(), r)
    assert out.status == "POLICY_UNAVAILABLE"
    assert out.candidate_plan is None
    assert out.confidence.individual_response == "NOT_ESTIMATED"
    assert {i.code for i in out.issues} >= {"POLICY_UNAVAILABLE", "TIME_UNCERTAIN"}
    assert out.engine_version == "initial-policy-producer/1.0.0"


def test_forged_approval_cannot_create_policy_authority():
    load, _, produce = api()
    req = request()
    req["policies"].update(
        state="APPROVED",
        review_ref="client-says-approved",
        dose_id="invented",
        time_id="invented",
        selection_id="invented",
        taxonomy_projection_id="invented",
    )
    assert produce(req, load()).status == "POLICY_UNAVAILABLE"


@pytest.mark.parametrize("field", ["sessions_per_week", "session_budgets_minutes", "limitations"])
def test_required_missing_precedes_policy_and_does_not_fabricate_input(field):
    load, inspect, produce = api()
    req = request()
    unknown(req, field)
    original = copy.deepcopy(req)
    out = produce(req, load())
    assert out.status == "INSUFFICIENT_DATA"
    assert field in out.assessment.missing_fields
    assert req == original
    assert inspect(req, load())["sessions"] == []


def test_conflicting_required_data_precedes_unavailable_policy():
    load, _, produce = api()
    req = request("conflicting")
    out = produce(req, load())
    assert out.status == "CONFLICTING_DATA"
    assert out.assessment.conflicting_fields


def test_missing_optional_anthropometry_and_experience_do_not_block_as_missing():
    load, _, produce = api()
    req = request()
    for field in ("height_cm", "weight_kg", "experience", "declared_priorities"):
        unknown(req, field)
    out = produce(req, load())
    assert out.assessment.state == "SUFFICIENT"
    assert out.status == "POLICY_UNAVAILABLE"
    assert "weight_kg" not in out.used_fields


def test_proposed_allocation_is_non_executable_and_counts_physical_sets():
    load, inspect, _ = api()
    draft = inspect(request(), load())
    assert draft["executable"] is False
    assert draft["physical_work_sets_total"] == 28
    assert len(draft["sessions"]) == 2
    assert all(len(s["slots"]) == 7 for s in draft["sessions"])
    assert all(
        slot["prescription"]["load_kg"] is None for s in draft["sessions"] for slot in s["slots"]
    )
    assert all(
        slot["prescription"]["load_mode"] == "CALIBRATION_REQUIRED"
        for s in draft["sessions"]
        for slot in s["slots"]
    )
    assert draft["time"]["state"] == "UNKNOWN"
    assert draft["time"]["upper_minutes"] is None


def test_unknown_gym_stays_unknown_and_never_infers_inventory():
    load, inspect, produce = api()
    req = request("unknown_gym")
    d = inspect(req, load())
    assert "COMPATIBILITY_UNKNOWN" in d["blocker_codes"]
    assert produce(req, load()).candidate_plan is None
    assert req["blueprint"]["environment"]["equipment_items"]["state"] == "UNKNOWN"


def test_confirmed_context_needs_no_equipment_inventory_and_does_not_solve_time():
    load, inspect, produce = api()
    req = request("unknown_gym")
    r = load()
    first = inspect(req, r)
    ids = {
        slot["selected"]["canonical_exercise_id"]
        for slot in first["sessions"][0]["slots"]
        if slot["selected"]
    }
    assert len(ids) == 7
    req["blueprint"]["environment"]["exercise_confirmations"] = [
        confirmation(req, i) for i in sorted(ids)
    ]
    d = inspect(req, r)
    assert "COMPATIBILITY_UNKNOWN" not in d["blocker_codes"]
    assert all(
        slot["selected"]["compatibility"] == "CONFIRMED"
        for s in d["sessions"]
        for slot in s["slots"]
    )
    assert produce(req, r).status == "POLICY_UNAVAILABLE"


def test_unavailable_and_conflicting_confirmations_never_select_that_exercise():
    load, inspect, _ = api()
    req = request()
    r = load()
    exercise_id = inspect(req, r)["sessions"][0]["slots"][0]["selected"]["canonical_exercise_id"]
    req["blueprint"]["environment"]["exercise_confirmations"] = [
        confirmation(req, exercise_id),
        confirmation(req, exercise_id, "UNAVAILABLE"),
    ]
    d = inspect(req, r)
    assert all(
        slot["selected"] is None or slot["selected"]["canonical_exercise_id"] != exercise_id
        for s in d["sessions"]
        for slot in s["slots"]
    )
    assert "COMPATIBILITY_UNKNOWN" in d["blocker_codes"]


def test_foreign_context_is_rejected_instead_of_silently_normalized():
    load, _, produce = api()
    req = request()
    req["blueprint"]["environment"]["exercise_confirmations"] = [
        confirmation(req, "incline-smith-press", context="another-gym")
    ]
    registry = load()
    with pytest.raises(ValueError, match="context"):
        produce(req, registry)


def test_hard_exclusion_removes_candidates_without_claiming_unknown_is_empty():
    load, inspect, _ = api()
    req = request()
    r = load()
    first = inspect(req, r)
    exercise_id = first["sessions"][0]["slots"][0]["selected"]["canonical_exercise_id"]
    fact = req["blueprint"]["excluded_exercise_ids"]
    fact.update(state="KNOWN", value=[exercise_id], conflicts=[])
    fact["provenance"] = copy.deepcopy(req["blueprint"]["sessions_per_week"]["provenance"])
    d = inspect(req, r)
    assert all(
        slot["selected"] is None or slot["selected"]["canonical_exercise_id"] != exercise_id
        for s in d["sessions"]
        for slot in s["slots"]
    )


@pytest.mark.parametrize("cadence", [1, 4, 7])
def test_valid_but_unsupported_cadence_is_not_a_missing_input(cadence):
    load, inspect, produce = api()
    req = request()
    req["blueprint"]["sessions_per_week"]["value"] = cadence
    req["blueprint"]["session_budgets_minutes"]["value"] = [75] * cadence
    assert "CONSTRAINT_VIOLATION" in inspect(req, load())["blocker_codes"]
    assert produce(req, load()).assessment.state == "SUFFICIENT"


def test_unknown_time_stays_unknown_even_with_very_large_budget():
    load, inspect, produce = api()
    req = request()
    req["blueprint"]["session_budgets_minutes"]["value"] = [10000, 10000]
    assert inspect(req, load())["time"]["upper_minutes"] is None
    assert produce(req, load()).status == "POLICY_UNAVAILABLE"


def test_observed_limitation_is_not_turned_into_medical_exercise_filter():
    load, inspect, _ = api()
    req = request()
    req["blueprint"]["limitations"]["value"] = ["unresolved shoulder report"]
    d = inspect(req, load())
    assert "CONSTRAINT_VIOLATION" in d["blocker_codes"]
    assert d["sessions"] == []


def test_determinism_input_immutability_and_optional_priority_not_weakness():
    load, inspect, produce = api()
    req = request()
    original = copy.deepcopy(req)
    a, b = inspect(req, load()), inspect(copy.deepcopy(req), load())
    assert a == b
    first_response = produce(req, load()).model_dump()
    equivalent_input = dict(reversed(list(copy.deepcopy(req).items())))
    repeated_response = produce(equivalent_input, load()).model_dump()
    assert repeated_response == first_response
    assert req == original
    assert "weakness" not in a
    assert all(
        len({slot["selected"]["canonical_exercise_id"] for slot in s["slots"] if slot["selected"]})
        == 7
        for s in a["sessions"]
    )


def test_actual_fifteen_zone_accounting_includes_raw_and_credited_sets():
    load, inspect, _ = api()
    d = inspect(request(), load())
    assert len(d["zone_exposure"]) == 15
    pecs = next(z for z in d["zone_exposure"] if z["zone"] == "pecs")
    assert pecs["raw_primary_sets"] >= 4
    assert pecs["unknown_role_sets"] > 0
    assert pecs["credited_sets"] is None
    assert pecs["bound"] == "UNKNOWN"
    assert d["physical_work_sets_total"] == 28


def test_registry_is_pinned_and_immutable(tmp_path):
    import shutil

    load, _, _ = api()
    r = load()
    with pytest.raises(TypeError):
        r.policy["admission_state"] = "APPROVED"
    for rel in r.source_hashes:
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, target)
    policy_rel = "docs/science/sci-p02-initial-policy/v1/policy.json"
    target = tmp_path / policy_rel
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / policy_rel, target)
    catalogue = tmp_path / "data/sci/exercise_catalogue.json"
    catalogue.write_text(catalogue.read_text() + " ")
    with pytest.raises(ValueError, match="hash"):
        load(tmp_path)


def test_engine_and_reference_versions_cannot_be_silently_relabelled():
    load, _, produce = api()
    req = request()
    req["versions"]["engine"] = "invented-engine"
    registry = load()
    with pytest.raises(ValueError, match="engine"):
        produce(req, registry)


def test_every_public_producer_fixture_is_generated_and_canonical_valid():
    load, _, produce = api()
    from tools.science_contracts.blueprint_first_plan_v1 import validate_exchange

    fixtures = json.loads(
        (ROOT / "docs/science/sci-p02-initial-policy/v1/producer-fixtures.json").read_text()
    )
    r = load()
    for case in fixtures:
        out = produce(case["request"], r)
        assert out.model_dump(mode="json") == case["response"]
        validate_exchange(case["request"], out, references=r.references)
        assert case["availability"] == "NOT_SERVED"
        assert out.status != "READY"


def test_global_assignment_preserves_a_solution_greedy_would_starve():
    from tools.science_initial_policy.planning import match_distinct

    a = {"canonical_exercise_id": "a"}
    b = {"canonical_exercise_id": "b"}
    assert match_distinct([[a, b], [a]]) == [b, a]
    assert match_distinct([[a], [a]]) is None


def test_unknown_roles_are_explicit_catalogue_blockers_not_zero_credit():
    load, inspect, _ = api()
    d = inspect(request(), load())
    assert any(z["bound"] == "UNKNOWN" for z in d["zone_exposure"])
    assert "CATALOG_GAP" in d["blocker_codes"]


def test_alternatives_do_not_repeat_the_selected_exercise():
    load, inspect, _ = api()
    d = inspect(request(), load())
    for session in d["sessions"]:
        for slot in session["slots"]:
            assert slot["selected"]["canonical_exercise_id"] not in {
                c["canonical_exercise_id"] for c in slot["alternatives"]
            }


def test_conflicting_optional_exclusion_is_reported_without_applying_one_side():
    load, inspect, produce = api()
    req = request("optional_conflict")
    out = produce(req, load())
    assert out.status == "POLICY_UNAVAILABLE"
    assert out.assessment.state == "SUFFICIENT"
    assert inspect(req, load())["executable"] is False


def test_conflict_diagnostics_do_not_mislabel_a_contradiction_as_missing():
    load, inspect, _ = api()
    d = inspect(request("conflicting"), load())
    assert "INPUT_CONFLICT" in d["blocker_codes"]
    assert "REQUIRED_INPUT_MISSING" not in d["blocker_codes"]


def test_used_fields_trace_operational_inputs_and_optional_conflict_is_nonblocking():
    load, _, produce = api()
    out = produce(request("optional_conflict"), load())
    assert {
        "objective",
        "population_scope",
        "sessions_per_week",
        "session_budgets_minutes",
        "limitations",
    } <= set(out.used_fields)
    assert any(i.code == "INPUT_CONFLICT" and not i.blocking for i in out.issues)
    assert out.status == "POLICY_UNAVAILABLE"
