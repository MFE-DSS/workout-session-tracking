"""Inventory2 worker, real published SCI only. No app process SCI import."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

from pydantic import ValidationError

INVENTORY = "plan-calibration-inventory/2.0.0"


def attest_imports(root, manifest):
    paths = []
    for name, module in tuple(sys.modules.items()):
        if name.startswith("tools.") and getattr(module, "__file__", None):
            path = Path(module.__file__).resolve(strict=True)
            if not path.is_relative_to(root):
                raise ValueError("foreign science import")
            relative = str(path.relative_to(root))
            if manifest["sha256"].get(relative) != hashlib.sha256(path.read_bytes()).hexdigest():
                raise ValueError("unattested science import")
            if ".artifacts" in name or "fixtures" in name:
                raise ValueError("runtime example import")
            paths.append(str(path))
    return sorted(paths)


def run(root, expected, payload):
    # Private source attestation also excludes Python bytecode cache fallback.
    sys.dont_write_bytecode = True
    if any(root.rglob("*.pyc")):
        raise ValueError("unattested bytecode cache")
    raw = (root / "packaging-manifest.v1.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("publication changed")
    manifest = json.loads(raw)
    if manifest.get("calibration_inventory_version") != INVENTORY:
        raise ValueError("unsupported inventory")
    for present in root.rglob("*"):
        if present.is_symlink() or present.name == "__pycache__":
            raise ValueError("unattested cache or alias")
        if present.is_file() and str(present.relative_to(root)) not in {
            *manifest["sha256"],
            "packaging-manifest.v1.json",
        }:
            raise ValueError("unattested extra file")
    for relative, digest in manifest["sha256"].items():
        path = (root / relative).resolve(strict=True)
        if Path(relative).is_absolute() or not path.is_relative_to(root):
            raise ValueError("invalid bundle path")
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError("bundle changed")
    sys.path.insert(0, str(root))
    # Load the attested legacy entry by file, without importing app/__init__.
    spec = importlib.util.spec_from_file_location(
        "_historical_worker", root / "app/services/plan_v3/science_worker.py"
    )
    legacy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(legacy)
    from tools.science_calibration_extension.evaluator import evaluate
    from tools.science_calibration_extension.policy import assert_authority, load_authority
    from tools.science_calibration_extension.validation import validate_result
    from tools.science_initial_policy.v2_registry import thaw

    authority = load_authority(root)
    assert_authority(authority)
    if manifest.get("calibration_extension_bundle_digest") != authority.bundle_digest:
        raise ValueError("extension publication differs")
    attest_imports(root, manifest)
    operation, value = payload["operation"], payload["value"]
    profiles = thaw(authority.policy)["profiles"]
    if operation == "calibration" and value["context"]["canonical_exercise_id"] in {
        p["candidate_id"] for p in profiles
    }:
        result = validate_result(value, evaluate(value, authority), authority).model_dump(
            mode="json"
        )
    else:
        result = legacy.run(root, expected, payload)
    if operation == "authorities":
        pilot = result["encounter"]["policy"]
        selection = result["v3"]["policy"]["selection"]
        # Pilot fields are taken from its admitted V3 realization, not redefined.
        pilot_id = pilot["scope"]["candidate_id"]
        selected = next(p for p in selection if p["candidate_id"] == pilot_id)
        pilot_profile = {
            **selected,
            "load_semantics": "MACHINE_DISPLAY_KG",
            "policy_ref": pilot["policy_ref"],
        }
        for p in profiles:
            p["policy_ref"] = authority.policy["policy_ref"]
        protocol_ref = profiles[0]["protocol_ref"].split("#")[0]
        text = (root / protocol_ref).read_bytes()
        result["calibration_inventory"] = {
            "version": INVENTORY,
            "bundle_digest": authority.bundle_digest,
            "profiles": [pilot_profile, *profiles],
            "protocol_material": {
                "source_ref": protocol_ref,
                "sha256": hashlib.sha256(text).hexdigest(),
                "text": text.decode("utf-8"),
            },
        }
        result["module_paths"] = attest_imports(root, manifest)
    attest_imports(root, manifest)  # Includes lazy and relative imports after evaluation.
    return result


if __name__ == "__main__":
    try:
        answer = run(Path(sys.argv[1]).resolve(), sys.argv[2], json.load(sys.stdin))
        print(json.dumps({"result": answer}, allow_nan=False))
    except ValidationError:
        print(json.dumps({"error": "invalid_scientific_input"}))
    except Exception:
        print(json.dumps({"error": "private_science_rejected"}))
        sys.exit(1)
