"""Build private immutable SCI attestation/code bundle, without a runtime fixture.

The pinned synthetic sources are private evidence bytes required by historical
loaders. They are not imported as factories or selected as request data.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRIES = (
    "tools.science_initial_policy.v3_admission",
    "tools.science_initial_policy.v3_producer",
    "tools.science_initial_policy.v3_validation",
    "tools.science_calibration_bootstrap.policy",
    "tools.science_calibration_bootstrap.evaluator",
    "tools.science_calibration_bootstrap.validation",
)


def encoded(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode()


def code_closure(source: Path):
    pending = list(ENTRIES)
    result = set()
    while pending:
        name = pending.pop()
        path = Path(name.replace(".", "/") + ".py")
        if path in result or not (source / path).is_file():
            continue
        result.add(path)
        for parent in path.parents:
            if str(parent) != "." and (source / parent / "__init__.py").is_file():
                result.add(parent / "__init__.py")
        tree = ast.parse((source / path).read_text())
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ImportFrom)
                and node.module
                and node.module.startswith("tools.")
            ):
                pending.append(node.module)
            elif isinstance(node, ast.Import):
                pending.extend(a.name for a in node.names if a.name.startswith("tools."))
    return result


def build_bundle(destination: Path, source: Path = ROOT) -> str:
    source = source.resolve()
    destination = destination.resolve()
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("bundle destination must be empty")
    # Record concrete transitive authority reads, not a guessed list of registries.
    reads = set()
    active = [True]

    def audit(event, args):
        if active[0] and event == "open" and isinstance(args[0], str):
            path = Path(args[0]).resolve()
            if path.is_relative_to(source) and path.is_file() and "__pycache__" not in path.parts:
                reads.add(path.relative_to(source))

    sys.addaudithook(audit)
    try:
        from tools.science_calibration_bootstrap.policy import load_authority
        from tools.science_initial_policy.v3_admission import load_v3_registry

        v3 = load_v3_registry(source)
        encounter = load_authority(source)
    finally:
        active[0] = False
    paths = reads | {Path(p) for p in encounter.source_digests} | code_closure(source)
    worker = Path("app/services/plan_v3/science_worker.py")
    paths.add(worker)
    hashes = {}
    for relative in sorted(paths):
        raw = (source / relative).read_bytes()
        output = destination / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(raw)
        hashes[str(relative)] = hashlib.sha256(raw).hexdigest()
    manifest = {
        "contract_version": "plan-v3-private-science-bundle/1.0.0",
        "sha256": hashes,
        "v3_bundle_digest": v3.bundle_digest,
        "encounter_bundle_digest": encounter.bundle_digest,
    }
    data = encoded(manifest)
    (destination / "packaging-manifest.v1.json").write_bytes(data)
    return hashlib.sha256(data).hexdigest()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    print(build_bundle(args.destination))
