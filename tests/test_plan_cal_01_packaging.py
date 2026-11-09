"""Actual inventory2 consumer boundary, without importing example factories."""

import hashlib
from pathlib import Path

import pytest

from app.services.plan_v3.packaging import execute_science


def test_inventory2_is_hermetic_and_preserves_pilot_and_v3(tmp_path):
    from tools.plan_calibration_runtime_bundle import build_bundle

    root = tmp_path / "private"
    digest = build_bundle(root)
    result = execute_science("authorities", {}, root=root, expected_digest=digest)
    inventory = result["calibration_inventory"]
    assert inventory["version"] == "plan-calibration-inventory/2.0.0"
    assert len(inventory["profiles"]) == 7
    assert len({p["candidate_id"] for p in inventory["profiles"]}) == 7
    rdl = next(
        p for p in inventory["profiles"] if p["candidate_id"] == "romanian-deadlift-halteres"
    )
    assert rdl["load_semantics"] == "PER_IMPLEMENT"
    assert len(inventory["protocol_material"]["text"]) > 100
    assert result["runtime_payload_source"] == "REQUEST_ONLY"
    assert all(Path(p).is_relative_to(root) for p in result["module_paths"])
    assert not any("artifacts" in p or "fixtures" in p for p in result["module_paths"])
    assert (
        result["v3"]["bundle_digest"]
        == "78b3e5d99fe05093d6141678fd40f16e744b88d3d87405f14b0f8be357724d94"
    )
    assert (
        result["encounter"]["bundle_digest"]
        == "e840d5edfc2bbe150f077062227a503a6f3a996fb92a3f7e7cbe49972dee72f9"
    )
    raw = (root / "packaging-manifest.v1.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == digest
    module = root / "tools/science_calibration_extension/evaluator.py"
    module.write_text(module.read_text() + "\n# altered\n")
    with pytest.raises(ValueError, match="science_bundle_unavailable"):
        execute_science("authorities", {}, root=root, expected_digest=digest)


@pytest.mark.parametrize(
    "candidate",
    [
        "chest-press-machine",
        "rowing-chest-supported",
        "romanian-deadlift-halteres",
        "tirage-poulie-haute-prise-neutre",
        "elevations-laterales-machine",
        "releves-mollets-debout-machine",
    ],
)
def test_inventory2_dispatches_real_sci_and_matches_canonical(tmp_path, candidate):
    # Test-only synthesis is never part of a served request factory.
    from tools.plan_calibration_runtime_bundle import build_bundle
    from tools.science_calibration_extension.artifacts import synthetic_encounter
    from tools.science_calibration_extension.evaluator import evaluate
    from tools.science_calibration_extension.policy import load_authority
    from tools.science_calibration_extension.validation import validate_result

    root = tmp_path / "private"
    digest = build_bundle(root)
    raw = synthetic_encounter(candidate)
    authority = load_authority()
    expected = validate_result(raw, evaluate(raw, authority), authority).model_dump(mode="json")
    actual = execute_science("calibration", raw, root=root, expected_digest=digest)
    assert actual == expected
    assert actual["state"] == "QUALIFIED"


def test_inventory2_never_reads_unattested_bytecode_cache(tmp_path):
    from tools.plan_calibration_runtime_bundle import build_bundle
    root = tmp_path / 'private'
    digest = build_bundle(root)
    execute_science('authorities', {}, root=root, expected_digest=digest)
    assert not list(root.rglob('*.pyc'))
    cache = root / 'tools/science_calibration_extension/__pycache__/unattested.pyc'
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_bytes(b'not an authority')
    with pytest.raises(ValueError, match='science_bundle_unavailable'):
        execute_science('authorities', {}, root=root, expected_digest=digest)


@pytest.mark.parametrize('relative', ['unattested.py','tools/unattested.so','tools/__pycache__/unattested.pyc'])
def test_inventory2_is_a_closed_immutable_file_inventory(tmp_path, relative):
    from tools.plan_calibration_runtime_bundle import build_bundle
    root=tmp_path/'private'
    digest=build_bundle(root)
    extra=root/relative
    extra.parent.mkdir(parents=True,exist_ok=True)
    extra.write_bytes(b'unattested bytes')
    with pytest.raises(ValueError,match='science_bundle_unavailable'):
        execute_science('authorities',{},root=root,expected_digest=digest)
