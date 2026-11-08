"""Real published authority, replay and reproducible non-served artifacts."""

import dataclasses
import importlib
import json
from pathlib import Path

import pytest

from tests.science_bootstrap_samples import encounter

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = Path("docs/science/sci-p02-initial-policy/first-use-calibration-bootstrap")


def policy():
    return importlib.import_module("tools.science_calibration_bootstrap.policy")


def test_actual_publication_allows_scoped_encounter_and_exact_validation():
    from tools.science_calibration_bootstrap.evaluator import evaluate
    from tools.science_calibration_bootstrap.validation import validate_result

    a = policy().load_authority()
    q = encounter(stage="trial")
    out = evaluate(q, a)
    assert out.admission == "ADMITTED_WITH_LIMITS"
    assert out.authority_digest == a.bundle_digest
    assert "INITIATE_TRIAL" in out.allowed_actions
    assert validate_result(q, out, a) == out
    out = evaluate(encounter(), a)
    assert out.state == "QUALIFIED"
    assert out.qualified_setting.value == 40.0
    assert not out.candidate_actions


@pytest.mark.parametrize("change", ["policy", "bundle", "sources", "subclass"])
def test_mutated_authority_objects_fail_closed(change):
    a = policy().load_authority()
    if change == "policy":
        q = dict(a.policy)
        q["state"] = "WITHDRAWN"
        a = dataclasses.replace(a, policy=q)
    elif change == "bundle":
        a = dataclasses.replace(a, bundle_digest="a" * 64)
    elif change == "sources":
        a = dataclasses.replace(a, source_digests={})
    else:

        class Impostor:
            pass

        a = Impostor()
    with pytest.raises(ValueError):
        policy().assert_authority(a)


def test_loader_detects_disk_drift_before_cached_authority_is_reused(tmp_path):
    import shutil

    from tools.science_calibration_bootstrap.evaluator import evaluate
    from tools.science_initial_policy.v3_admission import load_v3_registry

    # Copy only source closure plus publications, not any user database.
    r = load_v3_registry()
    from tools.science_initial_policy.v2_registry import PATH as v2_path

    sources = set(r.source_digests) | set(r.historical.source_digests)
    sources.add(v2_path)
    sources.add(json.loads((ROOT / v2_path).read_text())["source_manifest"])
    from tools.science_initial_policy.registry import POLICY_PATH

    sources.add(POLICY_PATH)
    sources.update(policy().load_authority().source_digests)
    sources.update(
        {
            str(DIRECTORY / "authority/registry.v1.json"),
            str(DIRECTORY / "authority/sources.v1.json"),
            "docs/science/sci-p02-initial-policy/stage2-v3/authority/registry.v1.json",
            "docs/science/sci-p02-initial-policy/stage2-v3/authority/sources.v1.json",
        }
    )
    for relative in sources:
        src = ROOT / relative
        if src.is_file():
            dest = tmp_path / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dest)
    a = policy().load_authority(tmp_path)
    target = tmp_path / "tools/science_calibration_bootstrap/evaluator.py"
    target.write_text(target.read_text() + "\n# drift\n")
    with pytest.raises(ValueError):
        evaluate(encounter(), a)


def test_published_artifacts_reproduce_without_clock_or_personal_evidence():
    artifacts = importlib.import_module("tools.science_calibration_bootstrap.artifacts")
    assert artifacts.verify_artifacts(ROOT)
    values = artifacts.build_artifacts(ROOT)
    fixture = json.loads(values["encounter-fixtures.v1.json"])
    assert fixture["artifact_kind"] == "REAL_EVALUATOR_SYNTHETIC_INPUT_NOT_SERVED"
    assert fixture["cases"][-1]["result"]["state"] == "QUALIFIED"
    assert fixture["cases"][0]["request"]["setting_choice"] is None
    assert all(row["result"]["activity_kind"] == "CALIBRATION_ACTIVITY" for row in fixture["cases"])


def test_schema_output_alone_cannot_override_canonical_permission():
    from tools.science_calibration_bootstrap.evaluator import evaluate
    from tools.science_calibration_bootstrap.validation import validate_result

    q = encounter(stage="familiarize")
    a = policy().load_authority()
    out = evaluate(q, a).model_dump(mode="json")
    out["allowed_actions"].append("INITIATE_TRIAL")
    with pytest.raises(ValueError):
        validate_result(q, out, a)
