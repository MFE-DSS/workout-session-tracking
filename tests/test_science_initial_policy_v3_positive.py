"""Real authority and producer outputs from synthetic observations, never served."""

import copy
import dataclasses

import pytest

from tests.test_science_initial_policy_v3 import request
from tools.science_contracts.blueprint_first_plan_v3 import (
    observation_fingerprint,
    request_fingerprint,
)
from tools.science_initial_policy.v3_admission import load_v3_registry
from tools.science_initial_policy.v3_producer import produce_v3
from tools.science_initial_policy.v3_validation import validate_admitted_exchange_v3


def acknowledged(raw, out):
    value = copy.deepcopy(raw)
    value["acknowledgment"] = dict(
        kind="TIME_UNCERTAINTY_ACK",
        subject_ref=raw["subject_ref"],
        snapshot_ref=raw["snapshot_ref"],
        source_revision=raw["source_revision"],
        request_fingerprint=request_fingerprint(raw),
        observation_fingerprint=observation_fingerprint(raw),
        plan_time_fingerprint=out.plan_time_fingerprint,
        product_policy_ref=out.start_policy_ref,
        acknowledged_at="2026-11-07T12:01:00Z",
        source_ref="synthetic:explicit-time-ack",
    )
    return value


def test_real_admitted_producer_separates_science_time_ack_and_permission():
    r = load_v3_registry()
    raw = request(r)
    out = produce_v3(raw, r)
    assert out.scientific_readiness == "SCIENTIFICALLY_READY"
    assert out.start_permission == "REQUIRES_TIME_ACK"
    assert all(t.state == "BUDGET_UNCERTAIN" for t in out.time_assessments)
    assert all(t.duration.state == "UNKNOWN" for t in out.time_assessments)
    assert validate_admitted_exchange_v3(raw, out, r) == out
    approved = acknowledged(raw, out)
    second = produce_v3(approved, r)
    assert second.start_permission == "ELIGIBLE"
    assert second.generated_at > out.generated_at
    assert second.request_fingerprint == out.request_fingerprint
    assert second.observation_fingerprint == out.observation_fingerprint
    assert second.full_evaluation_fingerprint != out.full_evaluation_fingerprint
    assert validate_admitted_exchange_v3(approved, second, r) == second
    assert produce_v3(approved, r).model_dump_json() == second.model_dump_json()


@pytest.mark.parametrize(
    "field",
    [
        "subject_ref",
        "snapshot_ref",
        "source_revision",
        "bundle_digest",
        "binding_digest",
        "engine_version",
        "policy_version",
        "plan_time_fingerprint",
    ],
)
def test_tampered_positive_is_not_authoritative(field):
    r = load_v3_registry()
    raw = request(r)
    out = produce_v3(raw, r)
    record = out.model_dump(mode="json")
    record[field] = "0" * 64 if "digest" in field or "fingerprint" in field else "wrong"
    with pytest.raises(ValueError):
        validate_admitted_exchange_v3(raw, record, r)


@pytest.mark.parametrize("change", ["plan", "policy", "owner", "revision", "observation"])
def test_ack_is_not_transferable(change):
    r = load_v3_registry()
    raw = request(r)
    out = produce_v3(raw, r)
    raw = acknowledged(raw, out)
    if change == "plan":
        raw["acknowledgment"]["plan_time_fingerprint"] = "0" * 64
    elif change == "policy":
        raw["acknowledgment"]["product_policy_ref"] = "wrong"
    elif change == "owner":
        raw["acknowledgment"]["subject_ref"] = "wrong"
    elif change == "revision":
        raw["source_revision"] = "changed"
    else:
        raw["episodes"][0]["events"][2]["reps"] = 11
    with pytest.raises(ValueError):
        produce_v3(raw, r)


def test_withdrawal_and_stale_reference_reject_without_test_authority():
    from tools.science_initial_policy.registry import _freeze
    from tools.science_initial_policy.v2_registry import thaw

    r = load_v3_registry()
    raw = request(r)
    policy = thaw(r.policy)
    policy["binding_status"] = "WITHDRAWN"
    with pytest.raises(ValueError):
        produce_v3(raw, dataclasses.replace(r, policy=_freeze(policy)))
    raw["requested_binding_ref"] = "old-binding"
    with pytest.raises(ValueError):
        produce_v3(raw, r)


def test_unknown_inventory_is_preserved_and_no_qualification_is_no_plan():
    r = load_v3_registry()
    raw = request(r)
    assert raw["blueprint"]["environment"]["equipment_items"]["state"] == "UNKNOWN"
    assert produce_v3(raw, r).scientific_readiness == "SCIENTIFICALLY_READY"
    raw["episodes"].pop()
    out = produce_v3(raw, r)
    assert out.scientific_readiness == "REVIEW_REQUIRED"
    assert out.start_permission == "DENIED"
    assert out.candidate_plan is None
    assert validate_admitted_exchange_v3(raw, out, r) == out


def test_real_artifacts_reproduce_and_are_not_runtime_fixtures():
    from tools.science_initial_policy.v3_fixtures import KIND, artifacts

    assert KIND == "REAL_PRODUCER_SYNTHETIC_INPUT_NOT_SERVED"
    first = artifacts()
    assert first == artifacts()
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    assert all((root / path).read_bytes() == content for path, content in first.items())
