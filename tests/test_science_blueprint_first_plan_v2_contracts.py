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


def exchange_api():
    return importlib.import_module("tools.science_contracts.first_plan_v2_validation")


@pytest.fixture(scope="module")
def authority():
    from tools.science_initial_policy.admission_registry import load_admission_registry
    from tools.science_initial_policy.v2_registry import load_v2_registry

    return {"trusted_bundle": load_v2_registry(), "admission_registry": load_admission_registry()}


def response(raw):
    m = api()
    value = m.validated_request(raw)
    assessment = m.assess_inputs(value.blueprint)
    status = {
        "CONFLICTING": "CONFLICTING_DATA",
        "INSUFFICIENT": "INSUFFICIENT_DATA",
        "SUFFICIENT": "POLICY_UNAVAILABLE",
    }[assessment.state]
    code = {
        "CONFLICTING": "INPUT_CONFLICT",
        "INSUFFICIENT": "REQUIRED_INPUT_MISSING",
        "SUFFICIENT": "POLICY_UNAVAILABLE",
    }[assessment.state]
    return {
        "contract_version": "first-plan-recommendation/2.0.0",
        "subject_ref": value.subject_ref,
        "snapshot_ref": value.snapshot_ref,
        "source_revision": value.source_revision,
        "as_of": value.as_of.isoformat(),
        "generated_at": value.as_of.isoformat(),
        "request_fingerprint": m.request_fingerprint(value),
        "full_evaluation_fingerprint": m.evaluation_fingerprint(value),
        "bundle_digest": value.bundle_digest,
        "effective_science_digest": value.effective_science_digest,
        "engine_version": None,
        "policy_version": None,
        "binding_ref": None,
        "binding_digest": None,
        "admission_refs": [],
        "revocation_check_ref": None,
        "assessment": assessment.model_dump(mode="json"),
        "issues": [
            {
                "code": code,
                "blocking": True,
                "gate_ref": None,
                "source_refs": [],
                "field_refs": list(assessment.conflicting_fields or assessment.missing_fields),
                "explanation": "Contract example; no admitted v2 producer or binding.",
            }
        ],
        "used_fields": [],
        "status": status,
        "candidate_plan": None,
        "confidence": {
            "individual_response": "NOT_ESTIMATED",
            "feasibility": "UNKNOWN",
            "evidence_refs": [],
            "limitations": ["Contract example, NOT_SERVED."],
        },
    }


def observed_plan(raw, authority):
    b = authority["trusted_bundle"]
    ep = raw["episodes"][0]
    candidate = dict(
        ep["context"],
        compatibility="CONFIRMED",
        compatibility_source_ref=ep["context_provenance"]["source_ref"],
        realization_source_ref=b.realization_refs[ep["context"]["canonical_exercise_id"]],
    )
    trial, accept = ep["events"][2:4]
    d = dose()
    d["source_ref"] = b.dose["source_version"]
    p = plan()
    slot = p["sessions"][0]["slots"][0]
    slot["intent_id"] = b.candidates[candidate["canonical_exercise_id"]]["intent_id"]
    slot["selected"] = candidate
    slot["prescription"] = dict(
        mode="OBSERVED_SETTING",
        dose=d,
        episode_id=ep["episode_id"],
        event_id=trial["event_id"],
        acceptance_event_id=accept["event_id"],
        context=ep["context"],
        setting=trial["setting"],
    )
    # This is an unreviewed partial draft, not the seven-intention policy output.
    return p


def test_negative_exchange_validates_real_pins_without_claiming_a_producer(authority):
    raw = request()
    result = exchange_api().validate_exchange(raw, response(raw), **authority)
    assert result.status == "POLICY_UNAVAILABLE"
    assert result.engine_version is None
    assert authority["admission_registry"].bindings == ()


@pytest.mark.parametrize(
    "field",
    [
        "subject_ref",
        "snapshot_ref",
        "source_revision",
        "request_fingerprint",
        "full_evaluation_fingerprint",
        "bundle_digest",
        "effective_science_digest",
        "as_of",
    ],
)
def test_exchange_rejects_stale_or_other_subject_result(field, authority):
    raw = request()
    out = response(raw)
    out[field] = (
        "0" * 64
        if "fingerprint" in field or "digest" in field
        else ("2026-11-01T12:00:00Z" if field == "as_of" else "unrelated")
    )
    with pytest.raises(ValueError):
        exchange_api().validate_exchange(raw, out, **authority)


@pytest.mark.parametrize("case", ["missing", "conflict"])
def test_conflict_and_missing_take_precedence_over_policy(authority, case):
    raw = request()
    fact = raw["blueprint"]["sessions_per_week"]
    fact.update(state="UNKNOWN", value=None)
    if case == "conflict":
        fact.update(
            state="CONFLICT",
            conflicts=[{"value": 2, "source_ref": "a"}, {"value": 3, "source_ref": "b"}],
        )
    out = response(raw)
    assert exchange_api().validate_exchange(raw, out, **authority).status == (
        "INSUFFICIENT_DATA" if case == "missing" else "CONFLICTING_DATA"
    )
    out["status"] = "POLICY_UNAVAILABLE"
    with pytest.raises(ValueError):
        exchange_api().validate_exchange(raw, out, **authority)


@pytest.mark.parametrize(
    "change",
    [
        "fake_binding",
        "engine",
        "policy",
        "used_weight",
        "wrong_assessment",
        "no_blocker",
        "unknown_evidence",
        "READY",
        "forged_registry",
    ],
)
def test_current_authority_does_not_admit_caller_claims(authority, change):
    from dataclasses import replace

    raw = request()
    out = response(raw)
    auth = dict(authority)
    if change == "fake_binding":
        out.update(binding_ref="APPROVED_BY_CALLER", binding_digest="0" * 64, admission_refs=["C1"])
    elif change == "engine":
        out["engine_version"] = "initial-policy-producer/2.0.0"
    elif change == "policy":
        out["policy_version"] = "initial-hypertrophy-policy/0.3.0-proposed"
    elif change == "used_weight":
        out["used_fields"] = ["weight_kg"]
    elif change == "wrong_assessment":
        out["assessment"]["missing_fields"] = ["weight_kg"]
    elif change == "no_blocker":
        out["issues"] = []
    elif change == "unknown_evidence":
        out["confidence"]["evidence_refs"] = ["EVIDENCE_DOES_NOT_EXIST"]
    elif change == "READY":
        out["status"] = "READY"
    else:
        auth["admission_registry"] = replace(auth["admission_registry"], bindings=("APPROVED",))
    with pytest.raises(ValueError):
        exchange_api().validate_exchange(raw, out, **auth)


def test_observed_draft_references_real_episode_but_remains_non_admitted(authority):
    raw = request()
    out = response(raw)
    out["candidate_plan"] = observed_plan(raw, authority)
    result = exchange_api().validate_exchange(raw, out, **authority)
    assert result.candidate_plan.sessions[0].slots[0].prescription.setting.value == 40.0
    assert result.status == "POLICY_UNAVAILABLE"


@pytest.mark.parametrize(
    "change",
    [
        "setting",
        "acceptance",
        "episode",
        "equipment",
        "realization",
        "exercise",
        "intent",
        "dose",
        "excluded",
        "availability",
        "time_supported",
    ],
)
def test_draft_rejects_unsupported_or_cross_context_claims(authority, change):
    raw = request()
    out = response(raw)
    p = out["candidate_plan"] = observed_plan(raw, authority)
    slot = p["sessions"][0]["slots"][0]
    if change == "setting":
        slot["prescription"]["setting"] = dict(kind="MASS_KG", value=100.0, unit="kg")
    elif change == "acceptance":
        slot["prescription"]["acceptance_event_id"] = "old:acceptance"
    elif change == "episode":
        slot["prescription"]["episode_id"] = "other:episode"
    elif change in {"equipment", "realization", "exercise"}:
        slot["selected"][
            {
                "equipment": "equipment_ref",
                "realization": "realization_ref",
                "exercise": "canonical_exercise_id",
            }[change]
        ] = "unrelated"
    elif change == "intent":
        slot["intent_id"] = "initial_calf_v1"
    elif change == "dose":
        slot["prescription"]["dose"]["work_sets"] = 4
        p["physical_work_sets_total"] = 4
    elif change == "excluded":
        fact = raw["blueprint"]["excluded_exercise_ids"]
        fact.update(state="KNOWN", value=[slot["selected"]["canonical_exercise_id"]])
        out.update(
            request_fingerprint=api().request_fingerprint(raw),
            full_evaluation_fingerprint=api().evaluation_fingerprint(raw),
        )
    elif change == "availability":
        raw["episodes"][0]["availability"] = "UNAVAILABLE"
        out["full_evaluation_fingerprint"] = api().evaluation_fingerprint(raw)
    else:
        p["sessions"][0]["duration"] = {
            "state": "CONDITIONAL_DIAGNOSTIC",
            "budget_minutes": 75,
            "lower_seconds": 10.0,
            "upper_seconds": 20.0,
            "basis_refs": ["unrelated"],
            "scope_fingerprint": "0" * 64,
            "limitations": ["Not authority."],
        }
    with pytest.raises(ValueError):
        exchange_api().validate_exchange(raw, out, **authority)


def test_unchecked_model_copies_are_revalidated_at_exchange_and_hash_boundary(authority):
    m = api()
    value = m.validated_request(request())
    corrupted = value.model_copy(update={"subject_ref": "other"})
    out = response(value)
    with pytest.raises(ValueError):
        m.evaluation_fingerprint(corrupted)
    with pytest.raises(ValueError):
        exchange_api().validate_exchange(corrupted, out, **authority)


def supported_duration():
    return {
        "state": "SUPPORTED",
        "budget_minutes": 75,
        "lower_seconds": 600.0,
        "upper_seconds": 900.0,
        "unit": "seconds",
        "basis_kind": "ADMITTED_PRODUCT_CONVENTION",
        "basis_ref": "CONTRACT_EXAMPLE_NOT_ADMITTED:time",
        "basis_version": "example",
        "scope_fingerprint": "0" * 64,
        "applicability_ref": "CONTRACT_EXAMPLE_NOT_ADMITTED:scope",
        "covers_bootstrap": True,
        "coverage": ["WORK", "REST", "PREPARATION_CALIBRATION", "SETUP_TRANSITION"],
        "evidence_refs": ["EV-71"],
        "limitations": ["Shape only, no authority."],
    }


def ready_shape(raw, authority):
    out = response(raw)
    out.update(
        status="READY",
        issues=[],
        engine_version="HYPOTHETICAL_NOT_SERVED",
        policy_version="HYPOTHETICAL_NOT_ADMITTED",
        binding_ref="HYPOTHETICAL_NOT_ADMITTED",
        binding_digest="0" * 64,
        admission_refs=[f"C{i}:HYPOTHETICAL" for i in range(1, 7)],
        revocation_check_ref="HYPOTHETICAL_NOT_CHECKED",
    )
    p = out["candidate_plan"] = observed_plan(raw, authority)
    p["review_state"] = "REVIEWED"
    p["sessions"][0]["duration"] = supported_duration()
    out["confidence"]["feasibility"] = "CONFIRMED"
    return out


def test_complete_shape_and_valid_json_cannot_substitute_for_empty_authority(authority):
    raw = request()
    out = ready_shape(raw, authority)
    assert api().FirstPlanRecommendationV2.model_validate(out).status == "READY"
    with pytest.raises(ValueError, match="no producer or admitted binding"):
        exchange_api().validate_exchange(raw, out, **authority)


@pytest.mark.parametrize(
    "change",
    [
        "unknown_time",
        "over_budget",
        "uncovered_bootstrap",
        "missing_selection",
        "draft",
        "missing_binding",
        "blocked",
        "unconfirmed",
    ],
)
def test_ready_shape_retains_execution_and_duration_gates(authority, change):
    out = ready_shape(request(), authority)
    p = out["candidate_plan"]
    s = p["sessions"][0]
    if change == "unknown_time":
        s["duration"] = {"state": "UNKNOWN", "budget_minutes": 75}
    elif change == "over_budget":
        s["duration"]["upper_seconds"] = 99999.0
    elif change == "uncovered_bootstrap":
        s["slots"][0]["prescription"] = bootstrap()
        s["duration"]["covers_bootstrap"] = False
    elif change == "missing_selection":
        s["slots"][0]["selected"] = None
    elif change == "draft":
        p["review_state"] = "DRAFT"
    elif change == "missing_binding":
        out["binding_ref"] = None
    elif change == "blocked":
        out["issues"] = response(request())["issues"]
    else:
        out["confidence"]["feasibility"] = "UNKNOWN"
    with pytest.raises(ValueError):
        api().FirstPlanRecommendationV2.model_validate(out)


@pytest.mark.parametrize(
    "change", ["role", "evidence", "foreign_slot", "foreign_realization", "absence"]
)
def test_qualitative_projection_cannot_claim_foreign_roles_or_zero(authority, change):
    raw = request()
    out = response(raw)
    p = out["candidate_plan"] = observed_plan(raw, authority)
    slot = p["sessions"][0]["slots"][0]
    c = slot["selected"]
    row = authority["trusted_bundle"].candidates[c["canonical_exercise_id"]]
    r = row["effective_roles"][0]
    z = next(z for z in p["zone_reports"] if z["zone"] == r["zone"])
    z.update(
        role_status="SUPPORTED_ROLES",
        unresolved_slot_ids=[],
        contributions=[
            dict(
                slot_id=slot["slot_id"],
                canonical_exercise_id=c["canonical_exercise_id"],
                realization_ref=c["realization_ref"],
                role=r["role"],
                source_ref=row["realization_ref"],
                evidence_refs=list(r["evidence_refs"]),
            )
        ],
    )
    assert exchange_api().validate_exchange(raw, out, **authority).status == "POLICY_UNAVAILABLE"
    contribution = z["contributions"][0]
    if change == "role":
        contribution["role"] = "MINOR" if r["role"] != "MINOR" else "PRIMARY"
    elif change == "evidence":
        contribution["evidence_refs"] = ["UNKNOWN"]
    elif change == "foreign_slot":
        contribution["slot_id"] = "another-slot"
    elif change == "foreign_realization":
        contribution["realization_ref"] = "another-realization"
    else:
        z.update(
            role_status="NO_SUPPORTED_ROLE_IN_SELECTED_SET",
            contributions=[],
            absence_basis_ref="NO_ROLE_LABEL_IS_NOT_PROOF",
        )
    with pytest.raises(ValueError):
        exchange_api().validate_exchange(raw, out, **authority)


@pytest.mark.parametrize("change", ["nan", "bool", "constructed_response", "future_fact"])
def test_public_boundary_revalidates_nested_scalars_and_provenance(authority, change):
    raw = request()
    out = response(raw)
    if change == "nan":
        raw["blueprint"]["height_cm"]["value"] = float("nan")
    elif change == "bool":
        raw["episodes"][0]["events"][2]["reps"] = True
    elif change == "constructed_response":
        out = (
            api()
            .FirstPlanRecommendationV2.model_validate(out)
            .model_copy(update={"used_fields": ("invented",)})
        )
    else:
        raw["blueprint"]["objective"]["provenance"]["recorded_at"] = "2099-01-01T00:00:00Z"
    with pytest.raises(ValueError):
        exchange_api().validate_exchange(raw, out, **authority)


def test_exported_v2_artifacts_reproduce_and_refuse_positive_or_synthetic_authority(authority):

    module = importlib.import_module("tools.science_contracts.first_plan_v2_fixtures")
    artifacts = module.artifacts()
    for relative, encoded in artifacts.items():
        assert (ROOT / relative).read_bytes() == encoded
    cases = json.loads(artifacts["docs/science/sci-p01-p02/v2/contract-fixtures.v2.json"])
    assert len(cases) == 9
    assert {"sufficient", "insufficient", "conflicting", "withheld", "unknown-equipment"} <= {
        c["scenario"] for c in cases
    }
    schemas = api().exported_schemas()
    assert set(schemas) == {
        "FirstPlanRequest.v2.schema.json",
        "FirstPlanRecommendation.v2.schema.json",
    }
    for c in cases:
        assert c["artifact_kind"] == "CONTRACT_EXAMPLE_NOT_ADMITTED_NOT_SERVED"
        assert c["response"]["status"] != "READY"
        api().FirstPlanRequestV2.model_validate(c["request"])
        api().FirstPlanRecommendationV2.model_validate(c["response"])
        assert (
            exchange_api().validate_exchange(c["request"], c["response"], **authority).binding_ref
            is None
        )
    assert artifacts == module.artifacts()


def test_v1_consumer_contract_does_not_silently_accept_v2():
    from tools.science_contracts.blueprint_first_plan_v1 import (
        FirstPlanRecommendation,
        FirstPlanRequest,
    )

    raw = request()
    out = response(raw)
    with pytest.raises(ValueError):
        FirstPlanRequest.model_validate(raw)
    with pytest.raises(ValueError):
        FirstPlanRecommendation.model_validate(out)


@pytest.mark.parametrize("use_imported_ref", [False, True])
def test_imported_historical_acceptance_cannot_replace_current_qualification(
    authority, use_imported_ref
):
    raw = request()
    ep = raw["episodes"][0]
    current = ep["events"][-1]["event_id"]
    old = copy.deepcopy(ep["events"][-1])
    old.update(event_id="imported-old-acceptance", sequence=5)
    old["provenance"]["measured_at"] = "2026-11-01T10:00:00Z"
    ep["events"].append(old)
    out = response(raw)
    out["candidate_plan"] = observed_plan(raw, authority)
    p = out["candidate_plan"]["sessions"][0]["slots"][0]["prescription"]
    p["acceptance_event_id"] = old["event_id"] if use_imported_ref else current
    if use_imported_ref:
        with pytest.raises(ValueError, match="acceptance"):
            exchange_api().validate_exchange(raw, out, **authority)
    else:
        assert (
            exchange_api().validate_exchange(raw, out, **authority).status == "POLICY_UNAVAILABLE"
        )


@pytest.mark.parametrize("code", ["REQUIRED_INPUT_MISSING", "INPUT_CONFLICT"])
def test_additional_input_blockers_cannot_invent_missing_or_conflicting_anthropometry(
    authority, code
):
    raw = request()
    out = response(raw)
    extra = copy.deepcopy(out["issues"][0])
    extra.update(code=code, field_refs=["weight_kg"])
    out["issues"].append(extra)
    with pytest.raises(ValueError, match="input blocker"):
        exchange_api().validate_exchange(raw, out, **authority)


def test_actual_simultaneous_conflict_and_missing_issues_remain_supported(authority):
    raw = request()
    raw["blueprint"]["sessions_per_week"].update(
        state="CONFLICT",
        value=None,
        conflicts=[{"value": 2, "source_ref": "a"}, {"value": 3, "source_ref": "b"}],
    )
    raw["blueprint"]["limitations"].update(state="UNKNOWN", value=None, conflicts=[])
    out = response(raw)
    extra = copy.deepcopy(out["issues"][0])
    extra.update(code="REQUIRED_INPUT_MISSING", field_refs=["limitations"])
    out["issues"].append(extra)
    value = exchange_api().validate_exchange(raw, out, **authority)
    assert value.status == "CONFLICTING_DATA"
    assert value.assessment.missing_fields == ("limitations",)
