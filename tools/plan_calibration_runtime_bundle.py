"""Build inventory2 in a new immutable bundle; historical builder stays intact."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.build_plan_v3_runtime_bundle import ROOT, encoded
from scripts.build_plan_v3_runtime_bundle import build_bundle as build_historical

INVENTORY = "plan-calibration-inventory/2.0.0"


def build_bundle(destination: Path, source: Path = ROOT) -> str:
    source, destination = source.resolve(), destination.resolve()
    build_historical(destination, source)
    from tools.science_calibration_extension.policy import DIRECTORY, load_authority

    authority = load_authority(source)
    manifest_path = destination / "packaging-manifest.v1.json"
    manifest = json.loads(manifest_path.read_bytes())
    paths = {Path(p) for p in authority.source_digests} | {
        DIRECTORY / "registry.v1.json",
        DIRECTORY / "sources.v1.json",
        Path("tools/science_calibration_extension/policy.py"),
        Path("app/services/plan_v3/science_worker_v2.py"),
    }
    for relative in sorted(paths):
        raw = (source / relative).read_bytes()
        output = destination / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(raw)
        manifest["sha256"][str(relative)] = hashlib.sha256(raw).hexdigest()
    manifest["calibration_inventory_version"] = INVENTORY
    manifest["calibration_extension_bundle_digest"] = authority.bundle_digest
    data = encoded(manifest)
    manifest_path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    print(build_bundle(parser.parse_args().destination))
