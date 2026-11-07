"""Actual v2 producer integration, with synthetic observations and no READY authority."""

import copy
import dataclasses
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path

import pytest

from tests.science_calibration_samples import calibrated_episode, context, digest, provenance

ROOT = Path(__file__).resolve().parents[1]
SELECTED = [
    "hack-squat-machine",
    "chest-press-machine",
    "rowing-cable-assis-prise-neutre",
    "romanian-deadlift-barre",
    "tirage-poulie-haute-prise-neutre",
    "elevations-laterales-halteres",
    "calf-press-leg-press",
]


def api():
    name = "tools.science_initial_policy.v2_producer"
    assert importlib.util.find_spec(name) is not None, "integrated v2 producer is not implemented"
    p = importlib.import_module(name)
    r = importlib.import_module("tools.science_initial_policy.v2_registry")
    return r.load_v2_registry, p.produce_v2, p.verify_evaluation, p.evaluation_fingerprint


def evaluation(registry, scenario="sufficient", *, confirmed=True):
    fixtures = json.loads((ROOT / "docs/science/sci-p01-p02/v1/fixtures.json").read_text())
    req = copy.deepcopy(next(f["request"] for f in fixtures if f["scenario"] == scenario))
    req["as_of"] = "2026-11-06T12:00:00Z"
    req["versions"].update(
        engine="initial-policy-producer/2.0.0", catalogue=registry.effective_catalogue_version
    )
    req["policies"].update(state="PROPOSED", review_ref=None)
    env = req["blueprint"]["environment"]
    env.update(context_ref="gym:test-a", exercise_confirmations=[])
    if confirmed:
        env["exercise_confirmations"] = [
            {
                "canonical_exercise_id": identity,
                "context_ref": env["context_ref"],
                "state": "AVAILABLE",
                "provenance": provenance(),
            }
            for identity in SELECTED
        ]
    cadence = req["blueprint"]["sessions_per_week"]
    if cadence["state"] == "KNOWN":
        cadence["value"] = 2
        req["blueprint"]["session_budgets_minutes"]["value"] = [75, 75]
    return {
        "contract_version": "initial-plan-evaluation/1.0.0",
        "subject_ref": "subject:A",
        "request": req,
        "episodes": [],
        "timing_inputs": [],
        "bundle_digest": registry.bundle_digest,
        "effective_science_digest": registry.effective_science_digest,
    }


def add_observations(raw, registry):
    for identity in SELECTED:
        ctx = context(
            canonical_exercise_id=identity, realization_ref=registry.realization_refs[identity]
        )
        ep = calibrated_episode(ctx=ctx)
        ep["episode_id"] = "synthetic:" + identity
        for e in ep["events"]:
            e["provenance"]["source_ref"] += ":" + identity
        raw["episodes"].append(ep)
    return raw


def timing_for_draft(result):
    inputs = []
    for drafted in result["draft"]["sessions"]:
        session = drafted["time_session"]
        scope = digest({"session": session, "structure": "TRADITIONAL_SEQUENTIAL"})
        specifications = [("session/prep", "PREPARATION_CALIBRATION", 0.0)]
        for slot in session["slots"]:
            name, p = slot["slot_id"], slot["prescription"]
            specifications += [
                (name + "/prep", "PREPARATION_CALIBRATION", 10.0),
                (name + "/operations", "SETUP_TRANSITION", 10.0),
            ]
            specifications += [
                (f"{name}/work/{i}", "WORK", 10.0) for i in range(1, p["work_sets"] + 1)
            ]
            specifications += [
                (f"{name}/rest/{i}", "REST", float(p["rest_seconds"]))
                for i in range(1, p["work_sets"])
            ]
        components = [
            {
                "component_id": f"synthetic:c{i}",
                "coverage_key": key,
                "kind": kind,
                "lower_seconds": seconds,
                "upper_seconds": seconds,
                "basis_ref": "SYNTHETIC_TEST_OBSERVATION_NOT_A_POLICY_CONSTANT",
                "basis_kind": "EXPERIMENTAL_INTERVAL",
                "scope_fingerprint": scope,
                "provenance": provenance(1, observed=True),
            }
            for i, (key, kind, seconds) in enumerate(specifications)
        ]
        inputs.append(
            {
                "session_id": session["session_id"],
                "subject_ref": "subject:A",
                "components": components,
                "layout": "DISJOINT_SEQUENTIAL",
                "structure": "TRADITIONAL_SEQUENTIAL",
            }
        )
    return inputs


def slot_for(result, intent):
    return next(s for s in result["draft"]["sessions"][0]["slots"] if s["intent_id"] == intent)


def test_real_v2_allocation_and_calibration_pending_do_not_create_ready():
    load, produce, verify, _ = api()
    reg = load()
    raw = evaluation(reg)
    original = copy.deepcopy(raw)
    out = produce(raw, reg)
    assert out["recommendation"]["status"] == "POLICY_UNAVAILABLE"
    assert out["recommendation"]["candidate_plan"] is None
    assert out["engine_version"] == "initial-policy-producer/2.0.0"
    assert out["runtime_availability"] == "NOT_SERVED"
    assert out["ready_fixture"] == "NOT_PRODUCED"
    assert out["scientific_admission"] == "NOT_ADMITTED"
    assert out["draft"]["physical_work_sets_total"] == 28
    assert len(out["draft"]["sessions"]) == 2
    assert all(
        s["calibration"]["state"] == "NEEDS_CALIBRATION"
        for s in out["draft"]["sessions"][0]["slots"]
    )
    assert raw == original
    assert verify(raw, out, reg) == out


def test_observed_load_and_positive_conditional_time_flow_through_actual_producer():
    load, produce, verify, _ = api()
    reg = load()
    raw = add_observations(evaluation(reg), reg)
    first = produce(raw, reg)
    reference = slot_for(first, "initial_hinge_v1")["calibration"]
    assert reference["state"] == "CALIBRATED"
    assert reference["load_kg"] == 40.0
    assert reference["reference_source_ref"].endswith("romanian-deadlift-barre")
    raw["timing_inputs"] = timing_for_draft(first)
    out = produce(raw, reg)
    assert all(t["ordinal"] == "LIKELY_FITS" for t in out["time_by_session"])
    assert all(t["upper_seconds"] == 1060.0 for t in out["time_by_session"])
    assert out["recommendation"]["status"] == "POLICY_UNAVAILABLE"
    assert out["recommendation"]["candidate_plan"] is None
    assert verify(raw, out, reg) == out


def test_qualified_g17_role_is_not_applied_to_unconfirmed_execution_or_quantified_hypertrophy():
    load, produce, _, _ = api()
    reg = load()
    raw = evaluation(reg)
    unqualified = slot_for(produce(raw, reg), "initial_vertical_pull_v1")
    assert unqualified["selected"]["canonical_exercise_id"] == "tirage-poulie-haute-prise-neutre"
    assert next(r["role"] for r in unqualified["roles"] if r["zone"] == "pecs") == "UNKNOWN"
    qualified = slot_for(produce(add_observations(raw, reg), reg), "initial_vertical_pull_v1")
    assert next(r["role"] for r in qualified["roles"] if r["zone"] == "pecs") == "SECONDARY"
    assert qualified["role_application"] == "QUALIFIED_CONDITIONAL_PLANNING_ONLY"
    assert qualified["hypertrophy_response"] == "NOT_ESTIMATED"
    assert "credited_sets" not in qualified
    assert qualified["execution_ready"] is False


def test_unknown_equipment_is_not_a_complete_gym_or_an_inventory_requirement():
    load, produce, _, _ = api()
    reg = load()
    raw = evaluation(reg, "unknown_gym", confirmed=False)
    out = produce(raw, reg)
    assert "COMPATIBILITY_UNKNOWN" in {b["code"] for b in out["blockers"]}
    assert raw["request"]["blueprint"]["environment"]["equipment_items"]["state"] == "UNKNOWN"
    assert out["recommendation"]["status"] == "POLICY_UNAVAILABLE"


def test_three_way_availability_conflict_cannot_be_ignored():
    load, produce, _, _ = api()
    reg = load()
    raw = evaluation(reg)
    env = raw["request"]["blueprint"]["environment"]
    record = copy.deepcopy(env["exercise_confirmations"][4])
    record["state"] = "UNAVAILABLE"
    env["exercise_confirmations"].append(record)
    record = copy.deepcopy(record)
    record["state"] = "UNKNOWN"
    env["exercise_confirmations"].append(record)
    out = produce(raw, reg)
    assert "CURRENT_CONTEXT_CONFLICT" in {b["reason"] for b in out["blockers"]}
    assert out["ready_fixture"] == "NOT_PRODUCED"


def test_excluding_only_admitted_vertical_does_not_promote_held_variants_or_fallback():
    load, produce, _, _ = api()
    reg = load()
    raw = evaluation(reg)
    excluded = raw["request"]["blueprint"]["excluded_exercise_ids"]
    excluded.update(
        state="KNOWN",
        value=["tirage-poulie-haute-prise-neutre"],
        conflicts=[],
        provenance=provenance(),
    )
    out = produce(raw, reg)
    assert "CATALOG_GAP" in {b["code"] for b in out["blockers"]}
    slot = slot_for(out, "initial_vertical_pull_v1")
    assert slot["selected"] is None
    assert slot["alternatives"] == []


@pytest.mark.parametrize("cadence,total", [(2, 28), (3, 42)])
def test_supported_cadence_counts_physical_work_without_personal_optimality(cadence, total):
    load, produce, _, _ = api()
    reg = load()
    raw = evaluation(reg)
    raw["request"]["blueprint"]["sessions_per_week"]["value"] = cadence
    raw["request"]["blueprint"]["session_budgets_minutes"]["value"] = [75] * cadence
    out = produce(raw, reg)
    assert out["draft"]["physical_work_sets_total"] == total
    assert len(out["time_by_session"]) == cadence
    assert out["scientific_admission"] == "NOT_ADMITTED"


@pytest.mark.parametrize("cadence", [1, 4, 5, 7])
def test_out_of_scope_known_cadence_is_not_a_missing_input(cadence):
    load, produce, _, _ = api()
    reg = load()
    raw = evaluation(reg)
    raw["request"]["blueprint"]["sessions_per_week"]["value"] = cadence
    raw["request"]["blueprint"]["session_budgets_minutes"]["value"] = [75] * cadence
    out = produce(raw, reg)
    assert out["recommendation"]["assessment"]["state"] == "SUFFICIENT"
    assert out["draft"]["sessions"] == []
    assert "CADENCE_NOT_ADMITTED" in {b["reason"] for b in out["blockers"]}


@pytest.mark.parametrize(
    "scenario,status", [("insufficient", "INSUFFICIENT_DATA"), ("conflicting", "CONFLICTING_DATA")]
)
def test_canonical_required_input_precedence_is_preserved(scenario, status):
    load, produce, _, _ = api()
    reg = load()
    out = produce(evaluation(reg, scenario), reg)
    assert out["recommendation"]["status"] == status
    assert out["draft"]["sessions"] == []


def test_optional_anthropometry_does_not_become_a_calibration_requirement():
    load, produce, _, _ = api()
    reg = load()
    raw = add_observations(evaluation(reg), reg)
    for field in ("height_cm", "weight_kg", "experience", "declared_priorities"):
        fact = raw["request"]["blueprint"][field]
        fact.update(state="UNKNOWN", value=None, conflicts=[])
        fact["provenance"].update(
            origin="UNKNOWN",
            acquisition="UNKNOWN",
            source_ref=None,
            measured_at=None,
            recorded_at=None,
        )
    out = produce(raw, reg)
    assert out["recommendation"]["assessment"]["state"] == "SUFFICIENT"
    assert slot_for(out, "initial_hinge_v1")["calibration"]["load_kg"] == 40.0


def test_tight_time_returns_configuration_constraint_without_discarding_movements_or_rest():
    load, produce, _, _ = api()
    reg = load()
    raw = evaluation(reg)
    raw["request"]["blueprint"]["session_budgets_minutes"]["value"] = [1, 1]
    out = produce(raw, reg)
    assert len(out["draft"]["sessions"][0]["slots"]) == 7
    assert all(t["ordinal"] == "LIKELY_EXCEEDS" for t in out["time_by_session"])
    assert all(
        t["constraint"]["scope"] == "THIS_CONFIGURATION_ONLY" for t in out["time_by_session"]
    )
    assert out["recommendation"]["status"] != "CONSTRAINT_UNSATISFIABLE"
    assert {s["prescription"]["rest_seconds"] for s in out["draft"]["sessions"][0]["slots"]} == {
        90,
        120,
    }


def test_complete_fingerprint_binds_facts_and_rejects_changed_output_or_owner():
    load, produce, verify, fingerprint = api()
    reg = load()
    raw = add_observations(evaluation(reg), reg)
    out = produce(raw, reg)
    altered = copy.deepcopy(raw)
    altered["episodes"][0]["events"][2]["rir"] = 4.0
    other = produce(altered, reg)
    assert other["request_fingerprint"] == out["request_fingerprint"]
    assert fingerprint(altered, reg) != fingerprint(raw, reg)
    with pytest.raises(ValueError):
        verify(altered, out, reg)
    forged = copy.deepcopy(out)
    forged["subject_ref"] = "subject:B"
    with pytest.raises(ValueError):
        verify(raw, forged, reg)
    forged = copy.deepcopy(out)
    forged["draft"]["sessions"][0]["slots"][0]["calibration"]["load_kg"] = 999.0
    with pytest.raises(ValueError):
        verify(raw, forged, reg)


def test_event_order_and_file_restart_preserve_the_full_evaluation(tmp_path):
    load, produce, verify, _ = api()
    reg = load()
    raw = add_observations(evaluation(reg), reg)
    first = produce(raw, reg)
    raw["episodes"] = list(reversed(raw["episodes"]))
    for ep in raw["episodes"]:
        ep["events"] = list(reversed(ep["events"])) + [copy.deepcopy(ep["events"][0])]
    target = tmp_path / "evaluation.json"
    target.write_text(json.dumps(raw))
    recovered = json.loads(target.read_text())
    assert produce(recovered, reg) == first
    assert verify(recovered, first, reg) == first


@pytest.mark.parametrize("change", ["owner", "context", "engine", "catalogue", "bundle", "science"])
def test_stale_or_cross_account_inputs_cannot_enter_the_current_evaluation(change):
    load, produce, _, _ = api()
    reg = load()
    raw = add_observations(evaluation(reg), reg)
    if change == "owner":
        raw["subject_ref"] = "subject:B"
    elif change == "context":
        raw["request"]["blueprint"]["environment"]["context_ref"] = "gym:other"
    elif change in {"engine", "catalogue"}:
        raw["request"]["versions"][change] = "stale"
    else:
        raw["bundle_digest" if change == "bundle" else "effective_science_digest"] = "forged"
    with pytest.raises(ValueError):
        produce(raw, reg)


def test_edited_trusted_registry_and_approval_label_cannot_create_authority():
    load, produce, _, _ = api()
    reg = load()
    raw = evaluation(reg)
    raw["request"]["policies"].update(state="APPROVED", review_ref="client-approval")
    assert produce(raw, reg)["recommendation"]["status"] == "POLICY_UNAVAILABLE"
    forged_refs = dataclasses.replace(
        reg.references, approved_policy_refs=frozenset({"client-approval"})
    )
    forged = dataclasses.replace(reg, references=forged_refs)
    with pytest.raises(ValueError):
        produce(raw, forged)


def test_observation_episode_in_progress_is_visible_not_silently_completed():
    load, produce, _, _ = api()
    reg = load()
    raw = add_observations(evaluation(reg), reg)
    raw["episodes"][3]["events"] = raw["episodes"][3]["events"][:3]
    out = produce(raw, reg)
    assert slot_for(out, "initial_hinge_v1")["calibration"]["state"] == "CALIBRATION_IN_PROGRESS"
    assert "CALIBRATION_IN_PROGRESS" in {b["reason"] for b in out["blockers"]}


def test_historical_sources_and_eleven_v1_producer_outputs_remain_identical():
    load, produce, _, _ = api()
    reg = load()
    produce(evaluation(reg), reg)
    pins = json.loads(
        (
            ROOT / "docs/science/sci-p02-initial-policy/calibration-time-01/SOURCE_PINS.json"
        ).read_text()
    )["sha256"]
    assert all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h for p, h in pins.items())
    from tools.science_initial_policy.fixtures import generated_cases

    saved = json.loads(
        (ROOT / "docs/science/sci-p02-initial-policy/v1/producer-fixtures.json").read_text()
    )
    assert generated_cases() == saved


def test_generated_v2_cases_are_real_reproducible_nonserved_outputs():
    load, _, verify, _ = api()
    fixtures = importlib.import_module("tools.science_initial_policy.v2_fixtures")
    cases = fixtures.generated_cases()
    assert len(cases) >= 10
    assert {c["scenario"] for c in cases} >= {
        "novice",
        "returning",
        "unknown_equipment",
        "limited_time",
        "g17_unqualified",
        "held_vertical",
        "calibration_pending",
    }
    for c in cases:
        assert c["fixture_kind"] == "SYNTHETIC_OBSERVATION_INPUT_REAL_PRODUCER_NOT_SERVED"
        assert c["result"]["recommendation"]["status"] != "READY"
        assert verify(c["request"], c["result"], load()) == c["result"]


def test_versioned_result_schema_and_saved_cases_match_actual_producer():
    load, produce, _, _ = api()
    module = importlib.import_module("tools.science_initial_policy.v2_producer")
    assert hasattr(module, "EvaluationResult"), "versioned result boundary is missing"
    result = produce(evaluation(load()), load())
    assert module.EvaluationResult.model_validate(result).model_dump(mode="json") == result
    schema = module.EvaluationResult.model_json_schema()
    assert schema["additionalProperties"] is False
    assert schema["properties"]["runtime_availability"]["const"] == "NOT_SERVED"


def test_stale_timing_scope_after_observation_change_cannot_remain_positive():
    load, produce, _, _ = api()
    reg = load()
    raw = add_observations(evaluation(reg), reg)
    raw["timing_inputs"] = timing_for_draft(produce(raw, reg))
    ep = raw["episodes"][3]
    ep["events"][0]["setting"]["value"] = 41.0
    ep["events"][2]["setting"]["value"] = 41.0
    out = produce(raw, reg)
    assert slot_for(out, "initial_hinge_v1")["prescription"]["load_kg"] == 41.0
    assert all(
        t["ordinal"] == "UNKNOWN" and "SCOPE_MISMATCH" in t["uncertainty"]
        for t in out["time_by_session"]
    )


def test_same_exercise_wrong_realization_does_not_qualify_pull_roles():
    load, produce, _, _ = api()
    reg = load()
    raw = add_observations(evaluation(reg), reg)
    ep = raw["episodes"][4]
    ep["context"]["realization_ref"] = "another-realization"
    for event in ep["events"]:
        event["context_fingerprint"] = digest(ep["context"])
    out = slot_for(produce(raw, reg), "initial_vertical_pull_v1")
    assert next(r["role"] for r in out["roles"] if r["zone"] == "pecs") == "UNKNOWN"
    assert out["calibration"]["state"] == "NEEDS_CALIBRATION"


def test_single_side_reference_cannot_supply_a_bilateral_plan_load():
    load, produce, _, _ = api()
    reg = load()
    raw = add_observations(evaluation(reg), reg)
    ep = raw["episodes"][3]
    ep["context"]["side"] = "LEFT"
    for event in ep["events"]:
        event["context_fingerprint"] = digest(ep["context"])
    out = slot_for(produce(raw, reg), "initial_hinge_v1")
    assert out["prescription"]["load_kg"] is None
    assert out["calibration"]["state"] == "NEEDS_CALIBRATION"


def test_preparation_scope_changes_when_episode_needs_review_even_with_same_null_load():
    load, produce, _, _ = api()
    reg = load()
    raw = add_observations(evaluation(reg), reg)
    ep = raw["episodes"][3]
    ep["events"] = ep["events"][:3]  # observed, not accepted
    raw["timing_inputs"] = timing_for_draft(produce(raw, reg))
    ep["events"][2]["technique"] = "CONCERN"
    out = produce(raw, reg)
    assert all("SCOPE_MISMATCH" in t["uncertainty"] for t in out["time_by_session"])


def test_changed_equipment_context_invalidates_timing_even_for_same_kg_and_event_ids():
    load, produce, _, _ = api()
    reg = load()
    raw = add_observations(evaluation(reg), reg)
    raw["timing_inputs"] = timing_for_draft(produce(raw, reg))
    ep = raw["episodes"][3]
    ep["context"]["equipment_ref"] = "another-actual-bar"
    for event in ep["events"]:
        event["context_fingerprint"] = digest(ep["context"])
    out = produce(raw, reg)
    assert all("SCOPE_MISMATCH" in t["uncertainty"] for t in out["time_by_session"])


@pytest.mark.parametrize("mutation", ["derived_acquisition", "context_missing", "equipment_missing", "load_unknown", "availability_unknown", "availability_unavailable"])
def test_incomplete_or_derived_context_does_not_qualify_g17_overlay(mutation):
    load, produce, _, _ = api()
    reg = load()
    raw = add_observations(evaluation(reg), reg)
    ep = raw["episodes"][4]
    if mutation == "derived_acquisition":
        ep["context_provenance"]["acquisition"] = "DERIVED"
    elif mutation == "context_missing":
        ep["context"]["context_ref"] = None
    elif mutation == "equipment_missing":
        ep["context"]["equipment_ref"] = None
    elif mutation == "load_unknown":
        ep["context"]["load_semantics"] = "UNKNOWN"
    else:
        ep["availability"] = "UNKNOWN" if mutation.endswith("unknown") else "UNAVAILABLE"
    for event in ep["events"]:
        event["context_fingerprint"] = digest(ep["context"])
    slot = slot_for(produce(raw, reg), "initial_vertical_pull_v1")
    assert next(r["role"] for r in slot["roles"] if r["zone"] == "pecs") == "UNKNOWN"
    assert slot["role_application"] == "SOURCE_ROLE_QUALIFICATION_UNCONFIRMED"


def test_qualified_realization_does_not_require_completed_load_calibration():
    load, produce, _, _ = api()
    reg = load()
    raw = add_observations(evaluation(reg), reg)
    raw["episodes"][4]["events"] = []
    slot = slot_for(produce(raw, reg), "initial_vertical_pull_v1")
    assert slot["calibration"]["state"] == "NEEDS_CALIBRATION"
    assert next(r["role"] for r in slot["roles"] if r["zone"] == "pecs") == "SECONDARY"


def test_generated_schema_and_fixture_bytes_are_versioned_without_drift():
    generator = importlib.import_module("tools.science_initial_policy.v2_fixtures")
    directory = ROOT / generator.DIRECTORY
    files = generator.artifacts()
    assert all((directory / name).read_bytes() == content for name, content in files.items())
    manifest = json.loads((directory / "ARTIFACT_MANIFEST.json").read_text())
    assert manifest["sha256"] == {name: hashlib.sha256(content).hexdigest() for name, content in files.items()}
