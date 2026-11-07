"""The new authority is distinct from historical contracts and runtime activation."""

import dataclasses
import importlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def api():
    return importlib.import_module("tools.science_initial_policy.v3_admission")


def test_exact_limited_policy_reuses_historical_science_without_runtime():
    registry = api().load_v3_registry()
    api().assert_trusted_v3(registry, require_admitted=False)
    policy = registry.policy
    assert policy["scope"]["cadences"] == (2,)
    assert len(policy["selection"]) == 7
    assert policy["dose"]["work_sets"] == 2
    assert policy["dose"]["rep_range"] == (8, 12)
    assert policy["prescription_modes"] == ("OBSERVED_SETTING",)
    assert policy["runtime_availability"] == "NOT_SERVED"
    assert policy["time"]["supported_time"] == "NOT_ESTABLISHED"
    for row in policy["selection"]:
        source = registry.historical.candidates[row["candidate_id"]]
        assert source["unilateral"] is False
        assert row["realization_ref"] == source["realization_ref"]
    from tools.science_initial_policy.admission_registry import load_admission_registry

    assert load_admission_registry().bindings == ()


@pytest.mark.parametrize(
    "field",
    [
        "bundle_digest",
        "binding_digest",
        "registry_digest",
        "manifest_digest",
        "effective_science_digest",
    ],
)
def test_caller_digest_replacement_is_not_authority(field):
    registry = api().load_v3_registry()
    changed = dataclasses.replace(registry, **{field: "0" * 64})
    with pytest.raises(ValueError):
        api().assert_trusted_v3(changed, require_admitted=False)


@pytest.mark.parametrize("change", ["sets", "bool", "candidate", "admitted", "runtime", "source"])
def test_modified_policy_or_sources_cannot_create_an_admission(change):
    from tools.science_initial_policy.registry import _freeze
    from tools.science_initial_policy.v2_registry import thaw

    registry = api().load_v3_registry()
    policy = thaw(registry.policy)
    if change == "sets":
        policy["dose"]["work_sets"] = 3
    elif change == "bool":
        policy["scope"]["requires_empty_limitations"] = 1
    elif change == "candidate":
        policy["selection"][0]["candidate_id"] = "pompes"
    elif change == "admitted":
        policy["admission"]["state"] = "CALLER_APPROVED"
    elif change == "runtime":
        policy["runtime_availability"] = "SERVED"
    else:
        changed = dataclasses.replace(registry, source_digests=_freeze({}))
        with pytest.raises(ValueError):
            api().assert_trusted_v3(changed, require_admitted=False)
        return
    changed = dataclasses.replace(registry, policy=_freeze(policy))
    with pytest.raises(ValueError):
        api().assert_trusted_v3(changed, require_admitted=False)


def test_non_admitted_record_never_conveys_positive_authority():
    from tools.science_initial_policy.registry import _freeze
    from tools.science_initial_policy.v2_registry import thaw

    registry = api().load_v3_registry()
    policy = thaw(registry.policy)
    policy["admission"]["state"] = "CANDIDATE"
    changed = dataclasses.replace(registry, policy=_freeze(policy))
    with pytest.raises(ValueError):
        api().assert_trusted_v3(changed)


def test_old_empty_authority_is_not_implicitly_promoted():
    from tools.science_initial_policy.admission_registry import load_admission_registry

    with pytest.raises(ValueError):
        api().assert_trusted_v3(load_admission_registry())


def test_source_symlinks_cannot_escape_reviewed_root(tmp_path):
    directory = "docs/science/sci-p02-initial-policy/stage2-v3/authority"
    (tmp_path / directory).mkdir(parents=True)
    for name in ["registry.v1.json", "sources.v1.json"]:
        (tmp_path / directory / name).write_bytes((ROOT / directory / name).read_bytes())
    manifest = json.loads((ROOT / directory / "sources.v1.json").read_text())
    for relative in manifest["sha256"]:
        path = tmp_path / relative
        if path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.symlink_to(ROOT / relative)
    with pytest.raises(ValueError):
        api().load_v3_registry(tmp_path)
