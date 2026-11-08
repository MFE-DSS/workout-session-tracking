"""Private JSON worker entry. Executed with -I from a verified immutable bundle."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from pydantic import ValidationError


def run(root: Path, expected: str, payload):
    raw = (root / "packaging-manifest.v1.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("publication changed")
    manifest = json.loads(raw)
    for relative, digest in manifest["sha256"].items():
        path = (root / relative).resolve(strict=True)
        if not path.is_relative_to(root) or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError("private bundle changed")
    sys.path.insert(0, str(root))
    from tools.science_calibration_bootstrap.evaluator import evaluate
    from tools.science_calibration_bootstrap.policy import load_authority
    from tools.science_calibration_bootstrap.validation import validate_result
    from tools.science_contracts.blueprint_first_plan_v1 import Blueprint
    from tools.science_contracts.blueprint_first_plan_v3 import (
        evaluation_fingerprint,
        observation_fingerprint,
        request_fingerprint,
        validated_request,
    )
    from tools.science_initial_policy.calibration_time_contracts import (
        CalibrationEpisode,
        CalibrationEvent,
        ContextKey,
    )
    from tools.science_initial_policy.v3_admission import load_v3_registry
    from tools.science_initial_policy.v3_producer import produce_v3
    from tools.science_initial_policy.v3_validation import validate_admitted_exchange_v3

    paths = []
    for name, module in tuple(sys.modules.items()):
        if name.startswith("tools.") and getattr(module, "__file__", None):
            path = Path(module.__file__).resolve()
            if not path.is_relative_to(root):
                raise ValueError("foreign science import")
            relative = str(path.relative_to(root))
            if (
                relative not in manifest["sha256"]
                or hashlib.sha256(path.read_bytes()).hexdigest() != manifest["sha256"][relative]
            ):
                raise ValueError("unattested science import")
            paths.append(str(path))
    registry = load_v3_registry(root)
    authority = load_authority(root)
    operation, value = payload["operation"], payload["value"]
    if operation == "authorities":
        from tools.science_initial_policy.v2_registry import thaw

        catalogue = json.loads((root / "data/sci/exercise_catalogue.json").read_bytes())
        selected_ids = {spec["candidate_id"] for spec in registry.policy["selection"]}
        labels = {
            row["exercise_id"]: row["identity"]["canonical_display_name"]
            for row in catalogue["records"]
            if row["exercise_id"] in selected_ids
        }

        protocol_material = _protocol_material(root, manifest)
        return {
            "v3": {
                "registry_digest": registry.registry_digest,
                "binding_digest": registry.binding_digest,
                "bundle_digest": registry.bundle_digest,
                "effective_science_digest": registry.effective_science_digest,
                "binding_ref": registry.binding_ref,
                "policy": thaw(registry.policy),
                "catalogue_version": registry.historical.effective_catalogue_version,
                "catalogue_labels": {
                    s["candidate_id"]: labels[s["candidate_id"]]
                    for s in registry.policy["selection"]
                },
            },
            "encounter": {
                "protocol_material": protocol_material,
                "bundle_digest": authority.bundle_digest,
                "policy": thaw(authority.policy),
            },
            "module_paths": sorted(paths),
            "runtime_payload_source": "REQUEST_ONLY",
        }
    shapes = {
        "blueprint": Blueprint,
        "context": ContextKey,
        "event": CalibrationEvent,
        "episode": CalibrationEpisode,
    }
    if operation == "setting_context":
        from tools.science_initial_policy.calibration_time_contracts import (
            Setting,
            _check_setting_context,
        )

        context = ContextKey.model_validate(value["context"])
        setting = Setting.model_validate(value["setting"]) if value["setting"] is not None else None
        _check_setting_context(setting, context)
        return {
            "context": context.model_dump(mode="json"),
            "setting": setting.model_dump(mode="json") if setting is not None else None,
        }
    if operation == "episodes":
        return [
            CalibrationEpisode.model_validate(item).model_dump(mode="json")
            for item in value["episodes"]
        ]
    if operation in shapes:
        return shapes[operation].model_validate(value).model_dump(mode="json")
    if operation == "evaluate":
        request = validated_request(value)
        result = produce_v3(request, registry)
        return validate_admitted_exchange_v3(request, result, registry).model_dump(mode="json")
    if operation == "fingerprints":
        return {
            "request_fingerprint": request_fingerprint(value),
            "observation_fingerprint": observation_fingerprint(value),
            "full_evaluation_fingerprint": evaluation_fingerprint(value),
        }
    if operation == "calibration":
        result = evaluate(value, authority)
        return validate_result(value, result, authority).model_dump(mode="json")
    raise ValueError("unsupported private operation")


def _protocol_material(root, manifest):
    publication = json.loads(
        (
            root
            / "docs/science/sci-p02-initial-policy/first-use-calibration-bootstrap/authority/registry.v1.json"
        ).read_bytes()
    )
    protocol_ref = publication["protocol_ref"]
    protocol = (root / protocol_ref).read_bytes()
    checksum = hashlib.sha256(protocol).hexdigest()
    if manifest["sha256"].get(protocol_ref) != checksum:
        raise ValueError("unattested instruction material")
    return {"source_ref": protocol_ref, "sha256": checksum, "text": protocol.decode("utf-8")}


if __name__ == "__main__":
    try:
        answer = run(Path(sys.argv[1]).resolve(), sys.argv[2], json.load(sys.stdin))
        print(json.dumps({"result": answer}, allow_nan=False))
    except ValidationError:
        print(json.dumps({"error": "invalid_scientific_input"}))
    except Exception:
        # IPC carries no traceback or raw input; caller turns this into NOT_SERVED.
        print(json.dumps({"error": "private_science_rejected"}))
        sys.exit(1)
