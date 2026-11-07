"""Explicit reproducible exports from the real admitted producer; no runtime import."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

from tools.science_contracts.blueprint_first_plan_v3 import (
    observation_fingerprint,
    request_fingerprint,
)
from tools.science_initial_policy.v3_admission import encoded, load_v3_registry
from tools.science_initial_policy.v3_producer import produce_v3
from tools.science_initial_policy.v3_validation import validate_admitted_exchange_v3

ROOT = Path(__file__).resolve().parents[2]
DIRECTORY = "docs/science/sci-p02-initial-policy/stage2-v3"
KIND = "REAL_PRODUCER_SYNTHETIC_INPUT_NOT_SERVED"


def artifacts(root: Path = ROOT) -> dict[str, bytes]:
    registry = load_v3_registry(root)
    raw = json.loads((root / DIRECTORY / "SYNTHETIC_INPUT.json").read_bytes())
    raw.update(
        bundle_digest=registry.bundle_digest,
        effective_science_digest=registry.effective_science_digest,
        requested_binding_ref=registry.binding_ref,
    )
    raw["versions"].update(
        engine=registry.policy["engine_version"], policy=registry.policy["policy_version"]
    )
    cases = []

    def append(name, request):
        response = produce_v3(request, registry)
        checked = validate_admitted_exchange_v3(request, response, registry)
        cases.append(
            dict(
                scenario=name,
                artifact_kind=KIND,
                request=request,
                response=checked.model_dump(mode="json"),
            )
        )
        return response

    out = append("admitted_observed_time_ack_required", raw)
    ack = copy.deepcopy(raw)
    ack["acknowledgment"] = dict(
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
    append("admitted_observed_time_ack_eligible", ack)
    missing = copy.deepcopy(raw)
    missing["blueprint"]["objective"].update(state="UNKNOWN", value=None)
    append("required_objective_unknown", missing)
    unavailable = copy.deepcopy(raw)
    unavailable["episodes"][0]["availability"] = "UNAVAILABLE"
    append("selected_context_unavailable", unavailable)
    outputs = {f"{DIRECTORY}/producer-fixtures.v3.json": encoded(cases)}
    paths = set(registry.source_digests) | {
        "tools/science_initial_policy/v3_admission.py",
        "tools/science_initial_policy/v3_fixtures.py",
        f"{DIRECTORY}/SYNTHETIC_INPUT.json",
        f"{DIRECTORY}/authority/registry.v1.json",
        f"{DIRECTORY}/authority/sources.v1.json",
    }
    outputs[f"{DIRECTORY}/producer-artifact-manifest.v1.json"] = encoded(
        dict(
            artifact_kind=KIND,
            engine_version=registry.policy["engine_version"],
            policy_version=registry.policy["policy_version"],
            binding_ref=registry.binding_ref,
            bundle_digest=registry.bundle_digest,
            binding_digest=registry.binding_digest,
            registry_digest=registry.registry_digest,
            effective_science_digest=registry.effective_science_digest,
            source_sha256={
                p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in sorted(paths)
            },
            artifact_sha256={p: hashlib.sha256(v).hexdigest() for p, v in outputs.items()},
        )
    )
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    for path, content in artifacts().items():
        target = ROOT / path
        if args.write:
            target.write_bytes(content)
        elif not target.exists() or target.read_bytes() != content:
            raise SystemExit("producer artifact drift: " + path)
    print("real v3 producer artifacts verified; NOT_SERVED")


if __name__ == "__main__":
    main()
