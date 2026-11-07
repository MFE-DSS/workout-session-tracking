"""Reproducible contract examples, never outputs of an admitted v2 producer.

Run as a module: --write explicitly exports; default checks bytes. Historical
inputs are synthetic protocol exercises. No observation, policy or authority is
created by this generator, and no production consumer imports these examples.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

from tools.science_contracts.blueprint_first_plan_v2 import (
    assess_inputs,
    evaluation_fingerprint,
    exported_schemas,
    request_fingerprint,
    validated_request,
)
from tools.science_contracts.first_plan_v2_validation import validate_exchange
from tools.science_initial_policy.admission_registry import load_admission_registry
from tools.science_initial_policy.v2_registry import load_v2_registry

ROOT = Path(__file__).resolve().parents[2]
DIRECTORY = "docs/science/sci-p01-p02/v2"
SEED = "docs/science/sci-p02-initial-policy/calibration-time-01/producer-fixtures.json"
KIND = "CONTRACT_EXAMPLE_NOT_ADMITTED_NOT_SERVED"


def _encode(value) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode()


def _request(seed):
    old = seed["request"]
    return dict(
        contract_version="first-plan-request/2.0.0",
        requirement_profile_id="first-bodybuilding-inputs/2.0.0",
        as_of=old["as_of"],
        subject_ref=seed["subject_ref"],
        snapshot_ref=old["blueprint"]["snapshot_id"],
        source_revision="CONTRACT_EXAMPLE:historical-fixture",
        blueprint=copy.deepcopy(old["blueprint"]),
        versions=dict(
            catalogue=old["versions"]["catalogue"], zones="zones-15-v1", engine=None, policy=None
        ),
        requested_binding_ref=None,
        bundle_digest=seed["bundle_digest"],
        effective_science_digest=seed["effective_science_digest"],
        episodes=copy.deepcopy(seed["episodes"]),
        timing_inputs=copy.deepcopy(seed["timing_inputs"]),
    )


def _response(raw):
    req = validated_request(raw)
    assessment = assess_inputs(req.blueprint)
    status, code = {
        "SUFFICIENT": ("POLICY_UNAVAILABLE", "POLICY_UNAVAILABLE"),
        "INSUFFICIENT": ("INSUFFICIENT_DATA", "REQUIRED_INPUT_MISSING"),
        "CONFLICTING": ("CONFLICTING_DATA", "INPUT_CONFLICT"),
    }[assessment.state]
    return dict(
        contract_version="first-plan-recommendation/2.0.0",
        subject_ref=req.subject_ref,
        snapshot_ref=req.snapshot_ref,
        source_revision=req.source_revision,
        as_of=req.as_of.isoformat(),
        generated_at=req.as_of.isoformat(),
        request_fingerprint=request_fingerprint(req),
        full_evaluation_fingerprint=evaluation_fingerprint(req),
        bundle_digest=req.bundle_digest,
        effective_science_digest=req.effective_science_digest,
        engine_version=None,
        policy_version=None,
        binding_ref=None,
        binding_digest=None,
        admission_refs=[],
        revocation_check_ref=None,
        assessment=assessment.model_dump(mode="json"),
        issues=[
            dict(
                code=code,
                blocking=True,
                gate_ref=None,
                source_refs=[],
                field_refs=list(assessment.conflicting_fields or assessment.missing_fields),
                explanation="Contract example only. No admitted v2 policy producer is served.",
            )
        ],
        used_fields=[],
        status=status,
        candidate_plan=None,
        confidence=dict(
            individual_response="NOT_ESTIMATED",
            feasibility="UNKNOWN",
            evidence_refs=[],
            limitations=["No individual response estimate or plan authority from this example."],
        ),
    )


def _scenario(base, name):
    value = copy.deepcopy(base)
    bp = value["blueprint"]
    if name in {"insufficient", "withheld"}:
        key = "session_budgets_minutes" if name == "insufficient" else "limitations"
        bp[key].update(
            state="UNKNOWN" if name == "insufficient" else "WITHHELD", value=None, conflicts=[]
        )
    elif name == "conflicting":
        bp["sessions_per_week"].update(
            state="CONFLICT",
            value=None,
            conflicts=[
                dict(value=2, source_ref="SYNTHETIC:availability-a"),
                dict(value=3, source_ref="SYNTHETIC:availability-b"),
            ],
        )
    elif name == "unknown-equipment":
        bp["environment"]["equipment_items"].update(state="UNKNOWN", value=None, conflicts=[])
        bp["environment"]["exercise_confirmations"] = []
        value["episodes"] = []
    elif name == "unknown-anthropometry":
        for key in ("weight_kg", "height_cm", "experience"):
            bp[key].update(state="UNKNOWN", value=None, conflicts=[])
    elif name == "no-observations":
        value["episodes"], value["timing_inputs"] = [], []
    elif name == "unknown-rir":
        for ep in value["episodes"]:
            for event in ep["events"]:
                if event["kind"] == "ATTEMPT_OBSERVED":
                    event["rir"] = None
    elif name == "priorities-are-preferences":
        bp["declared_priorities"] = copy.deepcopy(bp["limitations"])
        bp["declared_priorities"].update(state="KNOWN", value=["pecs", "arms"], conflicts=[])
    return value


def artifacts(root: Path = ROOT) -> dict[str, bytes]:
    """Generate examples and hashes; their status never authorizes a real plan."""
    bundle, authority = load_v2_registry(root), load_admission_registry(root)
    seed = next(
        c["request"] for c in json.loads((root / SEED).read_bytes()) if c["scenario"] == "returning"
    )
    base = _request(seed)
    scenarios = (
        "sufficient",
        "insufficient",
        "conflicting",
        "withheld",
        "unknown-equipment",
        "unknown-anthropometry",
        "no-observations",
        "unknown-rir",
        "priorities-are-preferences",
    )
    examples = []
    for name in scenarios:
        req = _scenario(base, name)
        out = _response(req)
        # Uses the actual unchanged authorities, not a test registry or fake engine.
        checked = validate_exchange(req, out, trusted_bundle=bundle, admission_registry=authority)
        examples.append(
            dict(
                scenario=name,
                artifact_kind=KIND,
                request=req,
                response=checked.model_dump(mode="json"),
            )
        )
    result = {f"{DIRECTORY}/{name}": _encode(schema) for name, schema in exported_schemas().items()}
    result[f"{DIRECTORY}/contract-fixtures.v2.json"] = _encode(examples)
    source_paths = (
        set(bundle.source_digests)
        | set(authority.source_digests)
        | {
            SEED,
            "tools/science_contracts/blueprint_first_plan_v1.py",
            "tools/science_contracts/blueprint_first_plan_v2.py",
            "tools/science_contracts/first_plan_v2_validation.py",
            "tools/science_contracts/first_plan_v2_fixtures.py",
            "tools/science_initial_policy/admission_registry.py",
        }
    )
    sources = {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in sorted(source_paths)}
    result[f"{DIRECTORY}/source-manifest.v2.json"] = _encode(dict(sha256=sources))
    result[f"{DIRECTORY}/artifact-manifest.v2.json"] = _encode(
        dict(
            version="first-plan-contract-artifacts/2.0.0",
            artifact_kind=KIND,
            scientific_admission="NOT_ADMITTED",
            runtime_availability="NOT_SERVED",
            ready_fixture="NOT_PRODUCED",
            seed_ref=SEED,
            bundle_digest=bundle.bundle_digest,
            admission_registry_digest=authority.registry_digest,
            sha256={
                p: hashlib.sha256(encoded).hexdigest() for p, encoded in sorted(result.items())
            },
        )
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write", action="store_true", help="Explicitly replace only v2 contract artifacts"
    )
    args = parser.parse_args()
    outputs = artifacts()
    for relative, encoded in outputs.items():
        path = ROOT / relative
        if args.write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(encoded)
        elif not path.exists() or path.read_bytes() != encoded:
            raise SystemExit(f"v2 artifact drift: {relative}")
    print(
        f"{len(outputs)} v2 contract artifacts {'written' if args.write else 'verified'}; NOT_ADMITTED / NOT_SERVED"
    )


if __name__ == "__main__":
    main()
