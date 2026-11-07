"""Versioned v3 contract examples and export checks; not a plan producer."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

from tools.science_contracts.blueprint_first_plan_v3 import (
    evaluation_fingerprint,
    exported_schemas,
    observation_fingerprint,
    request_fingerprint,
    validate_exchange,
)
from tools.science_contracts.bootstrap_protocol_v3 import CalibrationProtocolV3
from tools.science_initial_policy.admission_registry import load_admission_registry
from tools.science_initial_policy.v2_registry import load_v2_registry

ROOT = Path(__file__).resolve().parents[2]
DIRECTORY = "docs/science/sci-p01-p02/v3"
SOURCE = "docs/science/sci-p01-p02/v2/contract-fixtures.v2.json"
SEMANTICS = "docs/science/sci-p02-initial-policy/c3-c6-admission-pack-01/PROTOCOL_SEMANTICS_V2.md"
KIND = "CONTRACT_EXAMPLE_NOT_ADMITTED_NOT_SERVED"


def _encode(value):
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
    ).encode()


def artifacts(root: Path = ROOT) -> dict[str, bytes]:
    bundle, authority = load_v2_registry(root), load_admission_registry(root)
    cases = []
    for old in json.loads((root / SOURCE).read_bytes()):
        req = copy.deepcopy(old["request"])
        req.update(contract_version="first-plan-request/3.0.0", acknowledgment=None)
        # A contract example needs only one sourced context, not the entire
        # historical seven-context producer exercise. No positive output claimed.
        req["episodes"] = req["episodes"][:1]
        req["timing_inputs"] = []
        out = copy.deepcopy(old["response"])
        out.update(
            contract_version="first-plan-recommendation/3.0.0",
            request_fingerprint=request_fingerprint(req),
            observation_fingerprint=observation_fingerprint(req),
            full_evaluation_fingerprint=evaluation_fingerprint(req),
            scientific_readiness=out.pop("status"),
            scientific_issues=out.pop("issues"),
            time_assessments=[],
            start_permission="DENIED",
            start_policy_ref=None,
            acknowledgment=None,
            plan_time_fingerprint=None,
        )
        checked = validate_exchange(req, out, trusted_bundle=bundle, admission_registry=authority)
        cases.append(
            dict(
                scenario=old["scenario"],
                artifact_kind=KIND,
                request=req,
                response=checked.model_dump(mode="json"),
            )
        )
    outputs = {
        f"{DIRECTORY}/{name}": _encode(schema) for name, schema in exported_schemas().items()
    }
    outputs[f"{DIRECTORY}/contract-fixtures.v3.json"] = _encode(cases)
    source_digest = hashlib.sha256((root / SEMANTICS).read_bytes()).hexdigest()
    protocol = CalibrationProtocolV3.model_validate(
        dict(
            contract_version="initial-calibration-protocol/2.0.0",
            protocol_ref="initial-calibration-protocol/2.0.0-proposed@" + source_digest,
            source_ref=SEMANTICS + "@" + source_digest,
            steps=[
                dict(
                    kind=kind, instruction_ref=SEMANTICS + "@" + source_digest + "#" + kind.lower()
                )
                for kind in ("FAMILIARIZE", "TRIAL", "OBSERVE", "DECIDE")
            ],
            stop_rule_ref=SEMANTICS + "@" + source_digest + "#stop",
            retry_rule_ref=SEMANTICS + "@" + source_digest + "#retry",
        )
    )
    outputs[f"{DIRECTORY}/protocol-example.v3.json"] = _encode(
        dict(artifact_kind=KIND, protocol=protocol.model_dump(mode="json"))
    )
    paths = (
        set(bundle.source_digests)
        | set(authority.source_digests)
        | {
            SOURCE,
            SEMANTICS,
            "tools/science_contracts/blueprint_first_plan_v1.py",
            "tools/science_contracts/blueprint_first_plan_v2.py",
            "tools/science_contracts/first_plan_v2_validation.py",
            "tools/science_contracts/blueprint_first_plan_v3.py",
            "tools/science_contracts/bootstrap_protocol_v3.py",
            "tools/science_contracts/first_plan_v3_fixtures.py",
            "tools/science_initial_policy/admission_registry.py",
            "docs/science/sci-p02-initial-policy/c3-c6-admission-pack-01/OPERATOR_SOURCE.md",
        }
    )
    outputs[f"{DIRECTORY}/source-manifest.v3.json"] = _encode(
        dict(sha256={p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in sorted(paths)})
    )
    outputs[f"{DIRECTORY}/artifact-manifest.v3.json"] = _encode(
        dict(
            version="first-plan-contract-artifacts/3.0.0",
            artifact_kind=KIND,
            scientific_admission="NOT_ADMITTED",
            runtime_availability="NOT_SERVED",
            positive_plan_fixture="NOT_PRODUCED",
            bundle_digest=bundle.bundle_digest,
            admission_registry_digest=authority.registry_digest,
            sha256={p: hashlib.sha256(v).hexdigest() for p, v in sorted(outputs.items())},
        )
    )
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    outputs = artifacts()
    for relative, encoded in outputs.items():
        path = ROOT / relative
        if args.write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(encoded)
        elif not path.exists() or path.read_bytes() != encoded:
            raise SystemExit("v3 artifact drift: " + relative)
    print(
        f"{len(outputs)} v3 artifacts {'written' if args.write else 'verified'}; NOT_ADMITTED / NOT_SERVED"
    )


if __name__ == "__main__":
    main()
