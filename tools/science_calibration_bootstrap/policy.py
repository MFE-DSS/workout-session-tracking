"""Published isolated encounter authority; no account or runtime activation."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from tools.science_initial_policy.registry import ROOT, _freeze
from tools.science_initial_policy.v2_registry import thaw
from tools.science_initial_policy.v3_admission import load_v3_registry

DIRECTORY = Path("docs/science/sci-p02-initial-policy/first-use-calibration-bootstrap/authority")
REGISTRY_SHA256 = "f993ff958c6d95d61897b5a0a1543033b45b8e635f321373ed7387d9fd4138a8"
SOURCES_SHA256 = "d43b923a96e786dc3175af0386927b9d4bb32106f327b71b60222d0d64dd5473"


def encoded(value):
    return (
        json.dumps(thaw(value), sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False)
        + "\n"
    ).encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


@dataclass(frozen=True, slots=True)
class EncounterAuthority:
    root: Path
    policy: Mapping
    source_digests: Mapping
    historical: object
    bundle_digest: str


def load_authority(root: Path = ROOT) -> EncounterAuthority:
    root = Path(root).resolve()
    raw = (root / DIRECTORY / "registry.v1.json").read_bytes()
    source_raw = (root / DIRECTORY / "sources.v1.json").read_bytes()
    if (
        hashlib.sha256(raw).hexdigest() != REGISTRY_SHA256
        or hashlib.sha256(source_raw).hexdigest() != SOURCES_SHA256
    ):
        raise ValueError("encounter publication drift requires reviewed versioning")
    policy = json.loads(raw)
    sources = json.loads(source_raw)["sha256"]
    for relative, expected in sources.items():
        path = Path(relative)
        source = (root / path).resolve()
        if path.is_absolute() or ".." in path.parts or not source.is_relative_to(root):
            raise ValueError("encounter source escapes reviewed inventory")
        if hashlib.sha256(source.read_bytes()).hexdigest() != expected:
            raise ValueError("encounter reviewed source drift: " + relative)
    historical = load_v3_registry(root)
    if historical.bundle_digest != policy["v3_bundle_digest"]:
        raise ValueError("encounter historical V3 binding differs")
    bundle = digest(dict(policy=policy, sources=sources, v3_bundle=historical.bundle_digest))
    return EncounterAuthority(root, _freeze(policy), _freeze(sources), historical, bundle)


def assert_authority(authority) -> None:
    if type(authority) is not EncounterAuthority:
        raise ValueError("requires the actual published encounter authority")
    actual = load_authority(authority.root)
    if (
        digest(authority.policy) != REGISTRY_SHA256
        or digest({"sha256": authority.source_digests}) != SOURCES_SHA256
        or authority.bundle_digest != actual.bundle_digest
        or authority.historical.bundle_digest != actual.historical.bundle_digest
    ):
        raise ValueError("encounter authority differs from current publication")
    from tools.science_initial_policy.v3_admission import assert_trusted_v3

    assert_trusted_v3(authority.historical)
    p = authority.policy
    if (
        p["state"] != "ADMITTED_WITH_LIMITS"
        or p["status"] != "ACTIVE"
        or p["runtime_availability"] != "NOT_SERVED"
        or not p["review_ref"]
        or not p["decision_ref"]
    ):
        raise ValueError("encounter policy not admitted or withdrawn")
