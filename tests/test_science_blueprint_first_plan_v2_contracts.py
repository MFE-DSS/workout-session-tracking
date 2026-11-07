"""Contract-shape consistency is never scientific admission or a served plan."""

from __future__ import annotations

import copy
import importlib
import json
from pathlib import Path
from typing import get_args

import pytest

from tools.science_contracts.blueprint_first_plan_v1 import Zone

ROOT = Path(__file__).resolve().parents[1]


def api():
    return importlib.import_module("tools.science_contracts.blueprint_first_plan_v2")


def request(name="returning"):
    cases = json.loads(
        (
            ROOT / "docs/science/sci-p02-initial-policy/calibration-time-01/producer-fixtures.json"
        ).read_text()
    )
    old = copy.deepcopy(next(c["request"] for c in cases if c["scenario"] == name))
    req = old["request"]
    return {
        "contract_version": "first-plan-request/2.0.0",
        "requirement_profile_id": "first-bodybuilding-inputs/2.0.0",
        "as_of": req["as_of"],
        "subject_ref": old["subject_ref"],
        "snapshot_ref": req["blueprint"]["snapshot_id"],
        "source_revision": "SYNTHETIC_TEST_ONLY:revision",
        "blueprint": req["blueprint"],
        "versions": {
            "catalogue": req["versions"]["catalogue"],
            "zones": "zones-15-v1",
            "engine": None,
            "policy": None,
        },
        "requested_binding_ref": None,
        "bundle_digest": old["bundle_digest"],
        "effective_science_digest": old["effective_science_digest"],
        "episodes": old["episodes"],
        "timing_inputs": old["timing_inputs"],
    }


def dose():
    return {
        "work_sets": 2,
        "min_reps": 8,
        "max_reps": 12,
        "rir_target": 2.0,
        "rest_seconds": 120,
        "source_ref": "CONTRACT_EXAMPLE_NOT_ADMITTED:dose",
        "evidence_refs": ["EV-71"],
    }


def bootstrap():
    return {
        "mode": "BOOTSTRAP_PROTOCOL",
        "dose": dose(),
        "protocol_ref": "CONTRACT_EXAMPLE_NOT_ADMITTED:bootstrap",
        "stop_rule_ref": "CONTRACT_EXAMPLE_NOT_ADMITTED:stop",
        "retry_rule_ref": "CONTRACT_EXAMPLE_NOT_ADMITTED:retry",
        "timing_scope_ref": "CONTRACT_EXAMPLE_NOT_ADMITTED:prep-time",
        "steps": [
            {
                "step_id": f"step-{i}",
                "kind": kind,
                "instruction_ref": f"CONTRACT_EXAMPLE_NOT_ADMITTED:{kind}",
            }
            for i, kind in enumerate(["FAMILIARIZE", "TRIAL", "OBSERVE", "DECIDE"])
        ],
    }


def unknown_zones():
    return [
        {
            "zone": z,
            "role_status": "UNKNOWN",
            "contributions": [],
            "unresolved_slot_ids": ["slot-a"],
            "absence_basis_ref": None,
            "limitations": ["No quantitative credit or individual growth estimate."],
        }
        for z in get_args(Zone)
    ]


def plan():
    return {
        "allocation_ref": "CONTRACT_EXAMPLE_NOT_ADMITTED:allocation",
        "review_state": "DRAFT",
        "sessions": [
            {
                "session_id": "session-a",
                "slots": [
                    {
                        "slot_id": "slot-a",
                        "intent_id": "initial_press_v1",
                        "selected": None,
                        "alternatives": [],
                        "substitution_rule_ref": "CONTRACT_EXAMPLE_NOT_ADMITTED:substitution",
                        "prescription": bootstrap(),
                        "rationale": "Contract-only shape, not a recommendation.",
                    }
                ],
                "duration": {"state": "UNKNOWN", "budget_minutes": 75},
            }
        ],
        "physical_work_sets_total": 2,
        "zone_model_version": "zones-15-v1",
        "coverage_report_complete": True,
        "zone_reports": unknown_zones(),
    }


def test_request_reuses_blueprint_and_sourced_observations_without_anthropometry_gate():
    module = api()
    raw = request()
    for key in ["weight_kg", "height_cm", "experience"]:
        raw["blueprint"][key].update(state="UNKNOWN", value=None)
    value = module.FirstPlanRequestV2.model_validate(raw)
    assert value.contract_version == "first-plan-request/2.0.0"
    assert value.blueprint.weight_kg.value is None
    assert value.episodes[0].subject_ref == value.subject_ref


@pytest.mark.parametrize("change", ["subject", "snapshot", "time", "duplicate_episode"])
def test_request_rejects_unbound_or_future_observations(change):
    module = api()
    raw = request()
    if change == "subject":
        raw["subject_ref"] = "subject:other"
    elif change == "snapshot":
        raw["snapshot_ref"] = "another-snapshot"
    elif change == "time":
        raw["episodes"][0]["as_of"] = "2026-11-06T13:00:00Z"
    else:
        raw["episodes"].append(copy.deepcopy(raw["episodes"][0]))
    with pytest.raises(ValueError):
        module.FirstPlanRequestV2.model_validate(raw)


def test_full_fingerprint_binds_observations_without_changing_fact_fingerprint():
    module = api()
    raw = request()
    facts, full = module.request_fingerprint(raw), module.evaluation_fingerprint(raw)
    raw["episodes"][0]["events"][2]["reps"] = 11
    assert module.request_fingerprint(raw) == facts
    assert module.evaluation_fingerprint(raw) != full


def test_fingerprints_ignore_observation_order_and_preserve_priority_order():
    module = api()
    raw = request()
    expected = module.evaluation_fingerprint(raw)
    raw["episodes"].reverse()
    for ep in raw["episodes"]:
        ep["events"].reverse()
    raw["timing_inputs"].reverse()
    for t in raw["timing_inputs"]:
        t["components"].reverse()
    assert module.evaluation_fingerprint(raw) == expected
    raw["blueprint"]["declared_priorities"] = copy.deepcopy(raw["blueprint"]["limitations"])
    raw["blueprint"]["declared_priorities"]["value"] = ["pecs", "arms"]
    first = module.request_fingerprint(raw)
    raw["blueprint"]["declared_priorities"]["value"].reverse()
    assert module.request_fingerprint(raw) != first


def test_plan_can_report_all_fifteen_unknown_zones_without_credit_or_weakness():
    value = api().PlanV2.model_validate(plan())
    assert len(value.zone_reports) == 15
    assert all(z.role_status == "UNKNOWN" for z in value.zone_reports)
    assert all(not z.contributions for z in value.zone_reports)


@pytest.mark.parametrize(
    "change", ["zone_missing", "zone_duplicate", "fake_credit", "total", "duplicate_slot"]
)
def test_plan_refuses_false_accounting_or_unknown_to_zero(change):
    module = api()
    raw = plan()
    if change == "zone_missing":
        raw["zone_reports"].pop()
    elif change == "zone_duplicate":
        raw["zone_reports"][1] = copy.deepcopy(raw["zone_reports"][0])
    elif change == "fake_credit":
        raw["zone_reports"][0]["credited_sets"] = 0.0
    elif change == "total":
        raw["physical_work_sets_total"] = 99
    else:
        raw["sessions"][0]["slots"].append(copy.deepcopy(raw["sessions"][0]["slots"][0]))
    with pytest.raises(ValueError):
        module.PlanV2.model_validate(raw)


@pytest.mark.parametrize("change", ["step_missing", "step_order", "cold_load", "bool_count"])
def test_bootstrap_shape_requires_actual_steps_and_cannot_invent_cold_kg(change):
    module = api()
    raw = bootstrap()
    if change == "step_missing":
        raw["steps"].pop()
    elif change == "step_order":
        raw["steps"].reverse()
    elif change == "cold_load":
        raw["load_kg"] = 40.0
    else:
        raw["dose"]["work_sets"] = True
    with pytest.raises(ValueError):
        module.BootstrapPrescription.model_validate(raw)


def test_observed_nonmass_setting_is_a_typed_setting_not_equivalent_kg():
    module = api()
    raw = {
        "mode": "OBSERVED_SETTING",
        "dose": dose(),
        "episode_id": "episode:test",
        "event_id": "trial:test",
        "acceptance_event_id": "accept:test",
        "context": {
            "canonical_exercise_id": "chest-press-machine",
            "context_ref": "gym:test",
            "equipment_ref": "stack:test",
            "realization_ref": "realization:test",
            "load_semantics": "ASSISTANCE_SETTING",
            "side": "BILATERAL",
        },
        "setting": {"kind": "ASSISTANCE_SETTING", "value": 4.0, "unit": "setting"},
    }
    assert module.ObservedSettingPrescription.model_validate(raw).setting.unit == "setting"
    raw["setting"]["kind"] = "MASS_KG"
    with pytest.raises(ValueError):
        module.ObservedSettingPrescription.model_validate(raw)


@pytest.mark.parametrize("change", ["fake_bound", "missing_scope", "partial_coverage", "reversed"])
def test_duration_does_not_turn_unknown_or_partial_evidence_into_supported(change):
    module = api()
    raw = {
        "state": "SUPPORTED",
        "budget_minutes": 75,
        "lower_seconds": 600.0,
        "upper_seconds": 900.0,
        "unit": "seconds",
        "basis_kind": "ADMITTED_PRODUCT_CONVENTION",
        "basis_ref": "CONTRACT_EXAMPLE_NOT_ADMITTED:time",
        "basis_version": "test-v1",
        "scope_fingerprint": "0" * 64,
        "applicability_ref": "CONTRACT_EXAMPLE_NOT_ADMITTED:scope",
        "covers_bootstrap": True,
        "coverage": ["WORK", "REST", "PREPARATION_CALIBRATION", "SETUP_TRANSITION"],
        "evidence_refs": ["EV-71"],
        "limitations": ["Contract shape is not authority."],
    }
    if change == "fake_bound":
        raw = {"state": "UNKNOWN", "budget_minutes": 75, "upper_seconds": 900.0}
    elif change == "missing_scope":
        raw.pop("scope_fingerprint")
    elif change == "partial_coverage":
        raw["coverage"].pop()
    else:
        raw["lower_seconds"] = 1000.0
    with pytest.raises(ValueError):
        module.DurationEnvelope.model_validate({"duration": raw})
