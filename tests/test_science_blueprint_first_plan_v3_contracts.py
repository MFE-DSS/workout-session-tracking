"""V3 shape examples never supply the missing scientific admission authority."""

import copy
import importlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def api():
    return importlib.import_module("tools.science_contracts.blueprint_first_plan_v3")


def request():
    cases = json.loads((ROOT / "docs/science/sci-p01-p02/v2/contract-fixtures.v2.json").read_text())
    raw = copy.deepcopy(next(c["request"] for c in cases if c["scenario"] == "sufficient"))
    raw.update(contract_version="first-plan-request/3.0.0", acknowledgment=None)
    return raw


@pytest.fixture(scope="module")
def authority():
    from tools.science_initial_policy.admission_registry import load_admission_registry
    from tools.science_initial_policy.v2_registry import load_v2_registry

    return dict(trusted_bundle=load_v2_registry(), admission_registry=load_admission_registry())


def response(raw):
    m = api()
    r = m.validated_request(raw)
    assessment = m.assess_inputs(r.blueprint)
    state, code = {
        "SUFFICIENT": ("POLICY_UNAVAILABLE", "POLICY_UNAVAILABLE"),
        "INSUFFICIENT": ("INSUFFICIENT_DATA", "REQUIRED_INPUT_MISSING"),
        "CONFLICTING": ("CONFLICTING_DATA", "INPUT_CONFLICT"),
    }[assessment.state]
    return dict(
        contract_version="first-plan-recommendation/3.0.0",
        subject_ref=r.subject_ref,
        snapshot_ref=r.snapshot_ref,
        source_revision=r.source_revision,
        as_of=r.as_of.isoformat(),
        generated_at=r.as_of.isoformat(),
        request_fingerprint=m.request_fingerprint(r),
        observation_fingerprint=m.observation_fingerprint(r),
        full_evaluation_fingerprint=m.evaluation_fingerprint(r),
        bundle_digest=r.bundle_digest,
        effective_science_digest=r.effective_science_digest,
        engine_version=None,
        policy_version=None,
        binding_ref=None,
        binding_digest=None,
        admission_refs=[],
        revocation_check_ref=None,
        assessment=assessment.model_dump(mode="json"),
        used_fields=[],
        scientific_readiness=state,
        scientific_issues=[
            dict(
                code=code,
                blocking=True,
                gate_ref=None,
                source_refs=[],
                field_refs=list(assessment.conflicting_fields or assessment.missing_fields),
                explanation="Contract example, no admitted producer.",
            )
        ],
        candidate_plan=None,
        time_assessments=[],
        start_permission="DENIED",
        start_policy_ref=None,
        acknowledgment=r.acknowledgment,
        plan_time_fingerprint=None,
        confidence=dict(
            individual_response="NOT_ESTIMATED",
            feasibility="UNKNOWN",
            evidence_refs=[],
            limitations=["Not served, not scientifically admitted."],
        ),
    )


def hypothetical_shape(raw):
    from typing import get_args

    from tools.science_contracts.blueprint_first_plan_v1 import Zone
    from tools.science_contracts.bootstrap_protocol_v3 import assess_structural_time

    ep = raw["episodes"][0]
    ctx = ep["context"]
    dose = dict(
        work_sets=2,
        min_reps=8,
        max_reps=12,
        rir_target=2.0,
        rest_seconds=120,
        source_ref="EXAMPLE_NOT_ADMITTED:dose",
        evidence_refs=["EV-71"],
    )
    prescription = dict(
        mode="OBSERVED_SETTING",
        dose=dose,
        episode_id=ep["episode_id"],
        event_id=ep["events"][2]["event_id"],
        acceptance_event_id=ep["events"][3]["event_id"],
        context=ctx,
        setting=ep["events"][2]["setting"],
    )
    selected = dict(
        ctx,
        compatibility="CONFIRMED",
        compatibility_source_ref="EXAMPLE:context",
        realization_source_ref=ctx["realization_ref"],
    )
    session = dict(
        session_id="s1",
        slots=[
            dict(
                slot_id="a",
                intent_id="initial_quad_v1",
                selected=selected,
                alternatives=[],
                substitution_rule_ref="EXAMPLE:substitution",
                prescription=prescription,
                rationale="Shape, not admission.",
            )
        ],
        duration=dict(state="UNKNOWN", budget_minutes=75),
    )
    plan = dict(
        allocation_ref="EXAMPLE:allocation",
        review_state="REVIEWED",
        sessions=[session],
        physical_work_sets_total=2,
        zone_model_version="zones-15-v1",
        coverage_report_complete=True,
        zone_reports=[
            dict(
                zone=z,
                role_status="UNKNOWN",
                contributions=[],
                unresolved_slot_ids=["a"],
                absence_basis_ref=None,
                limitations=["No physiological zero."],
            )
            for z in get_args(Zone)
        ],
    )
    time = assess_structural_time(
        {"session_id": "s1", "slots": [{"prescription": dose}]}, budget_minutes=75
    ).model_dump(mode="json")
    out = response(raw)
    out.update(
        scientific_readiness="SCIENTIFICALLY_READY",
        scientific_issues=[],
        candidate_plan=plan,
        time_assessments=[time],
        start_permission="REQUIRES_TIME_ACK",
        start_policy_ref="HYPOTHETICAL_NOT_ADMITTED:start",
        engine_version="HYPOTHETICAL_NOT_SERVED",
        policy_version="HYPOTHETICAL_NOT_ADMITTED",
        binding_ref="HYPOTHETICAL",
        binding_digest="0" * 64,
        admission_refs=["HYPOTHETICAL:C1-C6"],
        revocation_check_ref="HYPOTHETICAL:revocation",
    )
    out["confidence"]["feasibility"] = "CONFIRMED"
    out["plan_time_fingerprint"] = api().plan_time_fingerprint(plan, [time])
    return out


def acknowledge(raw, out):
    return dict(
        kind="TIME_UNCERTAINTY_ACK",
        subject_ref=raw["subject_ref"],
        snapshot_ref=raw["snapshot_ref"],
        source_revision=raw["source_revision"],
        request_fingerprint=out["request_fingerprint"],
        observation_fingerprint=out["observation_fingerprint"],
        plan_time_fingerprint=out["plan_time_fingerprint"],
        product_policy_ref=out["start_policy_ref"],
        acknowledged_at=raw["as_of"],
        source_ref="CONTRACT_TEST_ONLY:ack",
    )


def test_real_empty_authority_accepts_honest_negative_v3_and_never_grants_start(authority):
    raw = request()
    out = response(raw)
    v = api().validate_exchange(raw, out, **authority)
    assert v.scientific_readiness == "POLICY_UNAVAILABLE" and v.start_permission == "DENIED"


def test_shape_separates_scientific_readiness_and_time_without_downcasting(authority):
    raw = request()
    out = hypothetical_shape(raw)
    v = api().FirstPlanRecommendationV3.model_validate(out)
    assert v.time_assessments[0].state == "BUDGET_UNCERTAIN"
    assert v.start_permission == "REQUIRES_TIME_ACK"
    with pytest.raises(ValueError):
        api().validate_exchange(raw, out, **authority)
    from tools.science_contracts.blueprint_first_plan_v2 import FirstPlanRecommendationV2

    with pytest.raises(ValueError):
        FirstPlanRecommendationV2.model_validate(out)


def test_ack_changes_full_decision_fingerprint_not_snapshot_or_observation_fingerprints():
    raw = request()
    out = hypothetical_shape(raw)
    facts, obs, full = (
        api().request_fingerprint(raw),
        api().observation_fingerprint(raw),
        api().evaluation_fingerprint(raw),
    )
    raw["acknowledgment"] = acknowledge(raw, out)
    assert api().request_fingerprint(raw) == facts and api().observation_fingerprint(raw) == obs
    assert api().evaluation_fingerprint(raw) != full


@pytest.mark.parametrize(
    "field",
    [
        "subject_ref",
        "snapshot_ref",
        "source_revision",
        "request_fingerprint",
        "observation_fingerprint",
    ],
)
def test_ack_cannot_be_transferred_to_other_snapshot_owner_or_observations(field):
    raw = request()
    out = hypothetical_shape(raw)
    raw["acknowledgment"] = acknowledge(raw, out)
    raw["acknowledgment"][field] = "0" * 64 if "fingerprint" in field else "other"
    fn = api().validated_request
    with pytest.raises(ValueError):
        fn(raw)


@pytest.mark.parametrize(
    "change",
    [
        "no_policy",
        "ack_missing",
        "wrong_plan",
        "wrong_policy",
        "future_ack",
        "too_long",
        "unconfirmed",
        "draft",
        "false_floor",
    ],
)
def test_shape_cannot_grant_eligible_start_by_bare_flag_or_stale_ack(change):
    raw = request()
    out = hypothetical_shape(raw)
    ack = acknowledge(raw, out)
    out.update(acknowledgment=ack, start_permission="ELIGIBLE")
    if change == "no_policy":
        out["start_policy_ref"] = None
    elif change == "ack_missing":
        out["acknowledgment"] = None
    elif change == "wrong_plan":
        ack["plan_time_fingerprint"] = "0" * 64
    elif change == "wrong_policy":
        ack["product_policy_ref"] = "another"
    elif change == "future_ack":
        ack["acknowledged_at"] = "2099-01-01T00:00:00Z"
    elif change == "too_long":
        out["time_assessments"][0].update(
            state="STRUCTURALLY_TOO_LONG", known_rest_floor_seconds=4500.0
        )
        out["plan_time_fingerprint"] = api().plan_time_fingerprint(
            out["candidate_plan"], out["time_assessments"]
        )
        ack["plan_time_fingerprint"] = out["plan_time_fingerprint"]
    elif change == "unconfirmed":
        out["candidate_plan"]["sessions"][0]["slots"][0]["selected"]["compatibility"] = "UNKNOWN"
    elif change == "draft":
        out["candidate_plan"]["review_state"] = "DRAFT"
    else:
        out["time_assessments"][0]["known_rest_floor_seconds"] = 4500.0
    cls = api().FirstPlanRecommendationV3
    with pytest.raises(ValueError):
        cls.model_validate(out)


def test_full_hypothetical_ack_shape_still_fails_real_admission_boundary(authority):
    raw = request()
    out = hypothetical_shape(raw)
    raw["acknowledgment"] = acknowledge(raw, out)
    out.update(
        acknowledgment=raw["acknowledgment"],
        start_permission="ELIGIBLE",
        full_evaluation_fingerprint=api().evaluation_fingerprint(raw),
    )
    assert api().FirstPlanRecommendationV3.model_validate(out).start_permission == "ELIGIBLE"
    with pytest.raises(ValueError):
        api().validate_exchange(raw, out, **authority)


@pytest.mark.parametrize(
    "field",
    [
        "subject_ref",
        "source_revision",
        "snapshot_ref",
        "request_fingerprint",
        "observation_fingerprint",
        "full_evaluation_fingerprint",
    ],
)
def test_exchange_rejects_tampered_identity_and_fingerprints(authority, field):
    raw = request()
    out = response(raw)
    out[field] = "0" * 64 if "fingerprint" in field else "other"
    fn = api().validate_exchange
    with pytest.raises(ValueError):
        fn(raw, out, **authority)


@pytest.mark.parametrize(
    "case", ["missing", "conflict", "invented_weight", "copied_model", "bad_version"]
)
def test_negative_profile_preserves_canonical_facts_and_revalidates_copies(authority, case):
    raw = request()
    if case == "missing":
        raw["blueprint"]["limitations"].update(state="WITHHELD", value=None, conflicts=[])
    elif case == "conflict":
        raw["blueprint"]["sessions_per_week"].update(
            state="CONFLICT",
            value=None,
            conflicts=[dict(value=2, source_ref="a"), dict(value=3, source_ref="b")],
        )
    out = response(raw)
    if case in {"missing", "conflict"}:
        assert api().validate_exchange(raw, out, **authority).scientific_readiness == (
            "INSUFFICIENT_DATA" if case == "missing" else "CONFLICTING_DATA"
        )
    elif case == "invented_weight":
        extra = copy.deepcopy(out["scientific_issues"][0])
        extra.update(code="REQUIRED_INPUT_MISSING", field_refs=["weight_kg"])
        out["scientific_issues"].append(extra)
    elif case == "copied_model":
        raw = api().validated_request(raw).model_copy(update={"subject_ref": "other"})
    else:
        raw["contract_version"] = "first-plan-request/2.0.0"
    fn = api().validate_exchange
    if case not in {"missing", "conflict"}:
        with pytest.raises(ValueError):
            fn(raw, out, **authority)


def test_v3_artifacts_are_reproducible_and_all_actual_exchange_examples_remain_denied(authority):
    module = importlib.import_module("tools.science_contracts.first_plan_v3_fixtures")
    outputs = module.artifacts()
    assert len(outputs) == 9
    for name, encoded in outputs.items():
        assert (ROOT / name).read_bytes() == encoded
    cases = json.loads(outputs["docs/science/sci-p01-p02/v3/contract-fixtures.v3.json"])
    assert len(cases) == 9
    for c in cases:
        assert c["artifact_kind"] == "CONTRACT_EXAMPLE_NOT_ADMITTED_NOT_SERVED"
        result = api().validate_exchange(c["request"], c["response"], **authority)
        assert (
            result.scientific_readiness != "SCIENTIFICALLY_READY"
            and result.start_permission == "DENIED"
        )
    protocol = json.loads(outputs["docs/science/sci-p01-p02/v3/protocol-example.v3.json"])
    from tools.science_contracts.bootstrap_protocol_v3 import CalibrationProtocolV3

    assert (
        CalibrationProtocolV3.model_validate(protocol["protocol"]).contract_version
        == "initial-calibration-protocol/2.0.0"
    )
    assert outputs == module.artifacts()
