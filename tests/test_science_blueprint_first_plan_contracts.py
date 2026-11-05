"""Proposed SCI-P01/02 contracts only: no endpoint, dose engine or personal data."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from tools.science_contracts.blueprint_first_plan_v1 import (
    FirstPlanRecommendation,
    FirstPlanRequest,
    ReferenceSnapshot,
    decision_fingerprint,
    exported_schemas,
    input_assessment,
)
from tools.science_contracts.blueprint_first_plan_v1 import (
    validate_exchange as validate_contract,
)

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs/science/sci-p01-p02/v1"
AS_OF = "2026-11-05T12:00:00Z"


def references():
    data = json.loads((ROOT / "data/sci/exercise_catalogue.json").read_text())
    from app.services.equipment_model import equipment_item_vocabulary
    from app.services.slot_intent import _INTENT_SPECS

    return ReferenceSnapshot(
        catalogue_version=data["catalogue_header"]["catalogue_version"],
        evidence_refs=frozenset(json.loads((ROOT / "data/sci/evidence_registry.json").read_text())),
        canonical_exercise_ids=frozenset(
            r["exercise_id"]
            for r in data["records"]
            if r["identity"]["identity_relation"] == "CANONICAL"
        ),
        canonical_intent_ids=frozenset(_INTENT_SPECS),
        equipment_item_ids=frozenset(equipment_item_vocabulary()),
        approved_policy_refs=frozenset(),
        no_equipment_exercise_ids=frozenset(
            r["exercise_id"]
            for r in data["records"]
            if r["identity"]["identity_relation"] == "CANONICAL"
            and r["exercise_operational"].get("equipment_requirement_status") == "RESOLVED"
            and r["exercise_operational"].get("equipment_requirements") == []
        ),
    )


def validate_exchange(req, out, evidence_refs=None):
    from dataclasses import replace

    refs = references()
    if evidence_refs is not None:
        refs = replace(refs, evidence_refs=evidence_refs)
    return validate_contract(req, out, references=refs)


def fact(value=None, *, state=None, source="fixture:user-declaration"):
    known = value is not None
    return {
        "state": state or ("KNOWN" if known else "UNKNOWN"),
        "value": value,
        "provenance": {
            "origin": "USER_REPORTED" if known else "UNKNOWN",
            "acquisition": "DECLARED" if known else "UNKNOWN",
            "source_ref": source if known else None,
            "recorded_at": AS_OF if known else None,
            "measured_at": None,
        },
        "conflicts": [],
    }


def request_data():
    return {
        "contract_version": "first-plan-request/1.0.0",
        "as_of": AS_OF,
        "requirement_profile_id": "first-bodybuilding-inputs-v1-proposed",
        "blueprint": {
            "contract_version": "body-training-blueprint/1.0.0",
            "snapshot_id": "fixture-blueprint-v1",
            "objective": fact("HYPERTROPHY"),
            "population_scope": fact("ADULT_NON_CLINICAL"),
            "sessions_per_week": fact(3),
            "session_budgets_minutes": fact([60, 60, 60]),
            "experience": fact(),
            "limitations": fact([]),
            "excluded_exercise_ids": fact([]),
            "declared_priorities": fact(["shoulders"]),
            "height_cm": fact(),
            "weight_kg": fact(),
            "legacy_weight_kg": fact(),
            "observations": [],
            "environment": {
                "context_ref": "fixture-context",
                "description": fact("Salle de sport"),
                "equipment_items": fact(),
                "exercise_confirmations": [],
            },
        },
        "policies": {
            "state": "UNAVAILABLE",
            "dose_id": None,
            "time_id": None,
            "selection_id": None,
            "taxonomy_projection_id": None,
            "review_ref": None,
        },
        "versions": {
            "catalogue": "auren-exercise-catalogue-v2-closure-2",
            "zones": "zones-15-v1",
            "credit": "sci-exposure-credit-v1",
            "engine": None,
        },
    }


def response_data(req=None):
    req = FirstPlanRequest.model_validate(req or request_data())
    return {
        "contract_version": "first-plan-recommendation/1.0.0",
        "request_fingerprint": decision_fingerprint(req),
        "status": "POLICY_UNAVAILABLE",
        "engine_version": None,
        "assessment": input_assessment(req.blueprint).model_dump(),
        "issues": [
            {
                "code": "POLICY_UNAVAILABLE",
                "blocking": True,
                "field_refs": [],
                "explanation": "Politique de dose et de temps non validée.",
            }
        ],
        "used_fields": [
            "objective",
            "population_scope",
            "sessions_per_week",
            "session_budgets_minutes",
            "limitations",
        ],
        "candidate_plan": None,
        "confidence": {
            "individual_response": "NOT_ESTIMATED",
            "feasibility": "UNKNOWN",
            "evidence_refs": ["EV-04"],
            "limitations": ["Aucune dose individuelle validée."],
        },
    }


def test_sufficient_inputs_do_not_require_body_dimensions_experience_or_inventory():
    req = FirstPlanRequest.model_validate(request_data())
    result = input_assessment(req.blueprint)
    assert result.state == "SUFFICIENT"
    assert result.missing_fields == ()
    assert req.blueprint.environment.equipment_items.value is None
    assert validate_exchange(req, response_data(req)).status == "POLICY_UNAVAILABLE"


def test_missing_required_fact_is_not_a_default_or_policy_failure():
    raw = request_data()
    raw["blueprint"]["sessions_per_week"] = fact()
    req = FirstPlanRequest.model_validate(raw)
    result = input_assessment(req.blueprint)
    assert result.state == "INSUFFICIENT" and result.missing_fields == ("sessions_per_week",)
    output = response_data(req)
    output["assessment"] = result.model_dump()
    with pytest.raises(ValueError, match="status"):
        validate_exchange(req, output)
    output["status"] = "INSUFFICIENT_DATA"
    output["issues"].append(
        {
            "code": "REQUIRED_INPUT_MISSING",
            "blocking": True,
            "field_refs": ["sessions_per_week"],
            "explanation": "Cadence non déclarée.",
        }
    )
    assert validate_exchange(req, output).status == "INSUFFICIENT_DATA"


def test_required_conflict_remains_explicit_but_unused_optional_conflict_is_not_a_gate():
    raw = request_data()
    conflict = fact(state="CONFLICT")
    conflict["conflicts"] = [
        {"value": 2, "source_ref": "fixture:a"},
        {"value": 3, "source_ref": "fixture:b"},
    ]
    raw["blueprint"]["sessions_per_week"] = conflict
    req = FirstPlanRequest.model_validate(raw)
    assert input_assessment(req.blueprint).state == "CONFLICTING"
    raw = request_data()
    raw["blueprint"]["height_cm"] = conflict
    req = FirstPlanRequest.model_validate(raw)
    assert input_assessment(req.blueprint).state == "SUFFICIENT"
    out = response_data(req)
    out["used_fields"].append("height_cm")
    with pytest.raises(ValueError, match="conflict"):
        validate_exchange(req, out)


@pytest.mark.parametrize("value", [True, 3.0, "3", 0, 8])
def test_cadence_refuses_coercion_and_outside_structural_week(value):
    raw = request_data()
    raw["blueprint"]["sessions_per_week"] = fact(value)
    with pytest.raises(ValidationError):
        FirstPlanRequest.model_validate(raw)


def test_unknown_empty_withheld_and_legacy_weight_are_distinct():
    raw = request_data()
    raw["blueprint"]["environment"]["equipment_items"] = fact([])
    raw["blueprint"]["weight_kg"] = fact(state="WITHHELD")
    raw["blueprint"]["legacy_weight_kg"] = fact(80.0, source="users.weight_kg")
    req = FirstPlanRequest.model_validate(raw)
    assert req.blueprint.environment.equipment_items.value == []
    assert req.blueprint.weight_kg.state == "WITHHELD"
    raw["blueprint"]["legacy_weight_kg"]["provenance"]["measured_at"] = AS_OF
    with pytest.raises(ValidationError, match="legacy"):
        FirstPlanRequest.model_validate(raw)
    raw = request_data()
    raw["blueprint"]["weight_kg"] = fact(80.0, source="users.weight_kg")
    with pytest.raises(ValidationError, match="legacy"):
        FirstPlanRequest.model_validate(raw)


def test_provenance_and_conflict_payload_cannot_be_invented_or_empty():
    raw = request_data()
    raw["blueprint"]["sessions_per_week"]["provenance"]["source_ref"] = None
    with pytest.raises(ValidationError):
        FirstPlanRequest.model_validate(raw)
    raw = request_data()
    raw["blueprint"]["sessions_per_week"] = fact(3, state="UNKNOWN")
    with pytest.raises(ValidationError):
        FirstPlanRequest.model_validate(raw)
    raw = request_data()
    raw["blueprint"]["sessions_per_week"] = fact(state="CONFLICT")
    with pytest.raises(ValidationError):
        FirstPlanRequest.model_validate(raw)


def test_priority_cannot_be_an_observed_weakness_and_confidence_has_no_percentage():
    raw = request_data()
    raw["blueprint"]["observations"] = [{"kind": "DECLARED_WEAKNESS", "fact": fact("shoulders")}]
    with pytest.raises(ValidationError):
        FirstPlanRequest.model_validate(raw)
    out = response_data()
    out["confidence"]["percentage"] = 95
    with pytest.raises(ValidationError):
        FirstPlanRecommendation.model_validate(out)
    assert response_data()["confidence"]["individual_response"] == "NOT_ESTIMATED"


def test_version_and_time_budget_alignment_are_explicit():
    raw = request_data()
    raw["blueprint"]["session_budgets_minutes"] = fact([60, 45])
    with pytest.raises(ValidationError, match="budget"):
        FirstPlanRequest.model_validate(raw)
    raw = request_data()
    raw["versions"]["zones"] = "legacy-11"
    with pytest.raises(ValidationError):
        FirstPlanRequest.model_validate(raw)


def test_fingerprint_is_stable_for_key_order_and_sensitive_to_versions_or_facts():
    raw = request_data()
    reversed_raw = dict(reversed(list(raw.items())))
    first = decision_fingerprint(FirstPlanRequest.model_validate(raw))
    assert first == decision_fingerprint(FirstPlanRequest.model_validate(reversed_raw))
    raw["blueprint"]["sessions_per_week"] = fact(2)
    raw["blueprint"]["session_budgets_minutes"] = fact([60, 60])
    assert first != decision_fingerprint(FirstPlanRequest.model_validate(raw))
    with pytest.raises(ValueError, match="fingerprint"):
        out = response_data()
        out["request_fingerprint"] = "0" * 64
        validate_exchange(request_data(), out)


def test_no_ready_plan_without_approved_policy_complete_plan_and_engine_version():
    out = response_data()
    out["status"] = "READY"
    out["issues"] = []
    with pytest.raises(ValueError):
        validate_exchange(request_data(), out)


def test_reference_and_input_claims_are_checked_against_frozen_registry():
    out = response_data()
    out["confidence"]["evidence_refs"] = ["EV-NONEXISTENT"]
    with pytest.raises(ValueError, match="evidence"):
        validate_exchange(request_data(), out, evidence_refs=frozenset({"EV-04"}))
    out = response_data()
    out["used_fields"].append("not_a_blueprint_field")
    with pytest.raises(ValueError, match="field"):
        validate_exchange(request_data(), out)


def test_exported_schema_artifacts_are_exact_and_fixtures_validate():
    for name, schema in exported_schemas().items():
        assert json.loads((PACK / (name + ".schema.json")).read_text()) == schema
    cases = json.loads((PACK / "fixtures.json").read_text())
    assert {c["scenario"] for c in cases} >= {
        "sufficient",
        "insufficient",
        "conflicting",
        "unknown_gym",
        "optional_conflict",
    }
    for case in cases:
        assert case["availability"] == "NOT_SERVED"
        assert (
            validate_exchange(case["request"], case["response"]).status
            == case["response"]["status"]
        )


def legacy_case():
    cases = json.loads((PACK / "fixtures.json").read_text())
    return copy.deepcopy(
        next(c for c in cases if c["scenario"] == "legacy_candidate_requires_policies_and_review")
    )


def test_no_equipment_requirement_cannot_be_claimed_for_a_smith_exercise():
    case = legacy_case()
    case["response"]["candidate_plan"]["sessions"][0]["slots"][0]["selected"]["compatibility"] = (
        "NOT_REQUIRED"
    )
    with pytest.raises(ValueError, match="equipment"):
        validate_exchange(case["request"], case["response"])


def test_compatibility_confirmation_requires_a_matching_current_context_fact():
    case = legacy_case()
    selected = case["response"]["candidate_plan"]["sessions"][0]["slots"][0]["selected"]
    selected["compatibility"] = "CONFIRMED"
    selected["compatibility_source_ref"] = "invented:source"
    with pytest.raises(ValueError, match="confirmation"):
        validate_exchange(case["request"], case["response"])


def test_excluded_or_noncanonical_exercise_and_nonexistent_intent_are_refused():
    for field, value, match in [
        ("canonical_exercise_id", "not-canonical", "identity"),
        ("intent_id", "fake-intent", "intention"),
    ]:
        case = legacy_case()
        slot = case["response"]["candidate_plan"]["sessions"][0]["slots"][0]
        (slot if field == "intent_id" else slot["selected"])[field] = value
        with pytest.raises(ValueError, match=match):
            validate_exchange(case["request"], case["response"])
    case = legacy_case()
    candidate = case["response"]["candidate_plan"]["sessions"][0]["slots"][0]["selected"]
    case["request"]["blueprint"]["excluded_exercise_ids"] = fact(
        [candidate["canonical_exercise_id"]]
    )
    case["response"]["request_fingerprint"] = decision_fingerprint(
        FirstPlanRequest.model_validate(case["request"])
    )
    with pytest.raises(ValueError, match="excluded"):
        validate_exchange(case["request"], case["response"])


def test_unknown_roles_cannot_be_exact_or_become_zero_and_total_sets_cannot_drift():
    case = legacy_case()
    plan = case["response"]["candidate_plan"]
    plan["physical_work_sets_total"] += 1
    with pytest.raises(ValidationError, match="total"):
        validate_exchange(case["request"], case["response"])
    for bound, value in [("UNKNOWN", 0.0), ("EXACT", 1.0)]:
        case = legacy_case()
        case["response"]["candidate_plan"]["zone_exposure"] = [
            {
                "zone": "pecs",
                "raw_primary_sets": 0,
                "raw_secondary_sets": 0,
                "unknown_role_sets": 1,
                "credited_sets": value,
                "bound": bound,
            }
        ]
        with pytest.raises(ValidationError):
            validate_exchange(case["request"], case["response"])


def test_missing_time_model_cannot_be_disguised_as_an_estimated_duration():
    case = legacy_case()
    duration = case["response"]["candidate_plan"]["sessions"][0]["duration"]
    duration["upper_minutes"] = 30.0
    with pytest.raises(ValidationError, match="duration"):
        validate_exchange(case["request"], case["response"])


def test_optional_conflict_sources_need_distinct_values_and_distinct_source_refs():
    raw = request_data()
    c = fact(state="CONFLICT")
    c["conflicts"] = [
        {"value": 2, "source_ref": "same-source"},
        {"value": 3, "source_ref": "same-source"},
    ]
    raw["blueprint"]["sessions_per_week"] = c
    with pytest.raises(ValidationError, match="source"):
        FirstPlanRequest.model_validate(raw)


def test_snapshot_event_ids_and_set_order_do_not_change_decision_content():
    a = request_data()
    b = copy.deepcopy(a)
    b["blueprint"]["snapshot_id"] = "another-event"
    assert decision_fingerprint(FirstPlanRequest.model_validate(a)) == decision_fingerprint(
        FirstPlanRequest.model_validate(b)
    )
    a["blueprint"]["environment"]["equipment_items"] = fact(["dumbbells", "adjustable_bench"])
    b["blueprint"]["environment"]["equipment_items"] = fact(["adjustable_bench", "dumbbells"])
    assert decision_fingerprint(FirstPlanRequest.model_validate(a)) == decision_fingerprint(
        FirstPlanRequest.model_validate(b)
    )


def test_population_prior_is_not_a_known_user_availability_or_measurement():
    for field in ["sessions_per_week", "height_cm"]:
        raw = request_data()
        raw["blueprint"][field] = fact(3 if field == "sessions_per_week" else 180.0)
        raw["blueprint"][field]["provenance"]["origin"] = "POPULATION_PRIOR"
        with pytest.raises(ValidationError, match="personal"):
            FirstPlanRequest.model_validate(raw)


def test_future_recorded_or_measured_fact_cannot_be_used_as_of_today():
    raw = request_data()
    raw["blueprint"]["sessions_per_week"]["provenance"]["recorded_at"] = "2027-01-01T00:00:00Z"
    with pytest.raises(ValidationError, match="future"):
        FirstPlanRequest.model_validate(raw)


def test_a_missing_engine_is_an_implementation_blocker_not_more_user_data():
    from dataclasses import replace

    raw = request_data()
    raw["policies"] = {
        "state": "APPROVED",
        "dose_id": "fixture-dose",
        "time_id": "fixture-time",
        "selection_id": "fixture-selection",
        "taxonomy_projection_id": "fixture-projection",
        "review_ref": "SYNTHETIC-TEST-NOT-APPROVAL",
    }
    req = FirstPlanRequest.model_validate(raw)
    out = response_data(req)
    refs = replace(
        references(),
        approved_policy_refs=frozenset(v for k, v in raw["policies"].items() if k.endswith("_id")),
    )
    assert validate_contract(req, out, references=refs).status == "POLICY_UNAVAILABLE"


def test_confirmed_feasibility_requires_an_actual_fully_resolved_candidate():
    out = response_data()
    out["confidence"]["feasibility"] = "CONFIRMED"
    with pytest.raises(ValueError, match="feasibility"):
        validate_exchange(request_data(), out)
    case = legacy_case()
    case["response"]["confidence"]["feasibility"] = "CONFIRMED"
    with pytest.raises(ValueError, match="feasibility"):
        validate_exchange(case["request"], case["response"])


def test_complete_exposure_requires_all_canonical_zones_without_unknown_roles():
    case = legacy_case()
    case["response"]["candidate_plan"]["exposure_complete"] = True
    with pytest.raises(ValidationError, match="exposure"):
        validate_exchange(case["request"], case["response"])


def test_unvalidated_minutes_are_not_a_supported_duration_estimate():
    case = legacy_case()
    d = case["response"]["candidate_plan"]["sessions"][0]["duration"]
    d.update(
        state="ESTIMATED",
        lower_minutes=10.0,
        upper_minutes=20.0,
        model_ref="unreviewed-time-model",
        basis_refs=["made-up"],
    )
    with pytest.raises(ValueError, match="time model"):
        validate_exchange(case["request"], case["response"])


def test_unfilled_slot_requires_a_visible_gap_and_empty_sessions_are_not_a_plan():
    case = legacy_case()
    case["response"]["candidate_plan"]["sessions"][0]["slots"][0]["selected"] = None
    case["response"]["issues"] = [
        i for i in case["response"]["issues"] if i["code"] != "CATALOG_GAP"
    ]
    with pytest.raises(ValueError, match="gap"):
        validate_exchange(case["request"], case["response"])
    case = legacy_case()
    empty = copy.deepcopy(case["response"]["candidate_plan"]["sessions"][0])
    empty.update(session_id="empty", slots=[])
    case["response"]["candidate_plan"]["sessions"].append(empty)
    with pytest.raises(ValidationError):
        validate_exchange(case["request"], case["response"])


def future_protocol_example():
    """Schema exercise with synthetic policy authority, never a scientific prescription.

    Existing legacy set/repetition counts are copied, not generated. Other values
    are test-only sentinels for validating the future READY branch. This object is
    not exported in the mobile fixtures or admitted as an approved archetype.
    """
    from dataclasses import replace
    from typing import get_args

    from tools.science_contracts.blueprint_first_plan_v1 import Zone

    case = legacy_case()
    raw, out = case["request"], case["response"]
    raw["blueprint"]["sessions_per_week"] = fact(1)
    raw["blueprint"]["session_budgets_minutes"] = fact([60])
    raw["versions"]["engine"] = "UNIT_TEST_ENGINE_NOT_SERVED"
    ids = {
        "dose_id": "TEST_ONLY_DOSE",
        "time_id": "TEST_ONLY_TIME",
        "selection_id": "TEST_ONLY_SELECTION",
        "taxonomy_projection_id": "TEST_ONLY_PROJECTION",
    }
    raw["policies"] = {
        "state": "APPROVED",
        **ids,
        "review_ref": "UNIT_TEST_AUTHORITY_NOT_REAL_APPROVAL",
    }
    plan = out["candidate_plan"]
    plan.update(review_state="REVIEWED", exposure_complete=True)
    slot = plan["sessions"][0]["slots"][0]
    selected = slot["selected"]
    selected.update(
        compatibility="CONFIRMED", compatibility_source_ref="fixture:in-context-confirmation"
    )
    raw["blueprint"]["environment"]["exercise_confirmations"] = [
        {
            "canonical_exercise_id": selected["canonical_exercise_id"],
            "context_ref": "fixture-context",
            "state": "AVAILABLE",
            "provenance": fact(True, source="fixture:in-context-confirmation")["provenance"],
        }
    ]
    slot["prescription"].update(
        dose_policy_ref=ids["dose_id"],
        rir_target=2.0,
        rest_seconds=90,
        load_mode="CALIBRATION_REQUIRED",
    )
    plan["sessions"][0]["duration"].update(
        state="ESTIMATED",
        lower_minutes=30.0,
        upper_minutes=45.0,
        model_ref=ids["time_id"],
        basis_refs=["unit-test:time-model-not-science"],
    )
    catalogue = json.loads((ROOT / "data/sci/exercise_catalogue.json").read_text())
    record = next(
        r for r in catalogue["records"] if r["exercise_id"] == selected["canonical_exercise_id"]
    )
    role_by_zone = {c["zone"]: c["role"] for c in record["exercise_science"]["contributions"]}
    sets = slot["prescription"]["work_sets"]
    credits = json.loads((ROOT / "data/sci/exposure_credit_policy.json").read_text())["credits"]
    plan["zone_exposure"] = []
    for zone in get_args(Zone):
        role = role_by_zone.get(zone)
        assert role != "UNKNOWN"  # This test does not fabricate an exact unknown contribution.
        primary, secondary = (
            (sets if role == "PRIMARY" else 0),
            (sets if role == "SECONDARY" else 0),
        )
        plan["zone_exposure"].append(
            {
                "zone": zone,
                "raw_primary_sets": primary,
                "raw_secondary_sets": secondary,
                "unknown_role_sets": 0,
                "credited_sets": primary * credits["PRIMARY"] + secondary * credits["SECONDARY"],
                "bound": "EXACT",
            }
        )
    req = FirstPlanRequest.model_validate(raw)
    out.update(
        status="READY",
        request_fingerprint=decision_fingerprint(req),
        engine_version=req.versions.engine,
        assessment=input_assessment(req.blueprint).model_dump(),
        issues=[],
    )
    out["confidence"]["feasibility"] = "CONFIRMED"
    return req, out, replace(references(), approved_policy_refs=frozenset(ids.values()))


def test_ready_branch_can_represent_a_future_trusted_producer_without_approving_its_test_policy():
    req, out, refs = future_protocol_example()
    assert validate_contract(req, out, references=refs).status == "READY"
    # None of these policy IDs is approved by the actual registry supplied to fixtures.
    with pytest.raises(ValueError, match="status"):
        validate_contract(req, out, references=references())


@pytest.mark.parametrize(
    "mutation,match",
    [("duration", "budget"), ("effort", "prescription"), ("policy", "prescription")],
)
def test_ready_guards_time_effort_and_prescription_source(mutation, match):
    req, out, refs = future_protocol_example()
    session = out["candidate_plan"]["sessions"][0]
    if mutation == "duration":
        session["duration"]["upper_minutes"] = 61.0
    elif mutation == "effort":
        session["slots"][0]["prescription"]["rir_target"] = None
    else:
        session["slots"][0]["prescription"]["dose_policy_ref"] = "wrong-policy"
    with pytest.raises(ValueError, match=match):
        validate_contract(req, out, references=refs)


def test_proven_impossibility_and_uncertainty_are_distinct_future_responses():
    req, out, refs = future_protocol_example()
    out.update(
        status="CONSTRAINT_UNSATISFIABLE",
        candidate_plan=None,
        issues=[
            {
                "code": "NO_FEASIBLE_PLAN",
                "blocking": True,
                "field_refs": ["limitations"],
                "explanation": "Hypothetical test of a producer's constraint verdict, not an evaluated user.",
            }
        ],
    )
    out["confidence"]["feasibility"] = "NOT_FEASIBLE"
    assert validate_contract(req, out, references=refs).status == "CONSTRAINT_UNSATISFIABLE"
    out.update(
        status="REVIEW_REQUIRED",
        issues=[
            {
                "code": "COMPATIBILITY_UNKNOWN",
                "blocking": True,
                "field_refs": [],
                "explanation": "Availability unconfirmed, not impossible.",
            }
        ],
    )
    out["confidence"]["feasibility"] = "UNKNOWN"
    assert validate_contract(req, out, references=refs).status == "REVIEW_REQUIRED"


def test_conflicting_availability_cannot_become_ready_but_can_remain_explicitly_under_review():
    req, out, refs = future_protocol_example()
    raw = req.model_dump(mode="json")
    negative = copy.deepcopy(raw["blueprint"]["environment"]["exercise_confirmations"][0])
    negative.update(state="UNAVAILABLE")
    negative["provenance"]["source_ref"] = "fixture:contradictory-context-confirmation"
    raw["blueprint"]["environment"]["exercise_confirmations"].append(negative)
    req = FirstPlanRequest.model_validate(raw)
    out["request_fingerprint"] = decision_fingerprint(req)
    with pytest.raises(ValueError, match="conflicting"):
        validate_contract(req, out, references=refs)
    slot = out["candidate_plan"]["sessions"][0]["slots"][0]
    slot["selected"].update(compatibility="UNKNOWN", compatibility_source_ref=None)
    out.update(
        status="REVIEW_REQUIRED",
        issues=[
            {
                "code": "COMPATIBILITY_UNKNOWN",
                "blocking": True,
                "field_refs": [],
                "explanation": "Contradictory availability observations are preserved for resolution.",
            }
        ],
    )
    out["confidence"]["feasibility"] = "UNKNOWN"
    assert validate_contract(req, out, references=refs).status == "REVIEW_REQUIRED"
    assert len(req.blueprint.environment.exercise_confirmations) == 2


@pytest.mark.parametrize("origin", ["POPULATION_PRIOR", "PRODUCT_CONTRACT", "DERIVED_FROM_HISTORY"])
def test_known_equipment_cannot_be_assumed_from_a_prior_or_past_history(origin):
    raw = request_data()
    raw["blueprint"]["environment"]["equipment_items"] = fact(["dumbbells"])
    raw["blueprint"]["environment"]["equipment_items"]["provenance"]["origin"] = origin
    with pytest.raises(ValidationError, match="environment"):
        FirstPlanRequest.model_validate(raw)


@pytest.mark.parametrize(
    "change",
    [
        {"acquisition": "UNKNOWN"},
        {"source_ref": None},
        {"recorded_at": None},
        {"origin": "DERIVED_FROM_HISTORY"},
    ],
)
def test_known_context_confirmation_requires_full_direct_provenance(change):
    req, out, refs = future_protocol_example()
    raw = req.model_dump(mode="json")
    raw["blueprint"]["environment"]["exercise_confirmations"][0]["provenance"].update(change)
    with pytest.raises(ValidationError, match="confirmation"):
        FirstPlanRequest.model_validate(raw)
