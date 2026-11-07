"""Reviewed authority for the limited v3 profile; no runtime capability.

The historical empty authority and contract validators are not modified.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from tools.science_initial_policy.registry import ROOT, _freeze
from tools.science_initial_policy.v2_registry import (
    V2Registry,
    assert_trusted,
    load_v2_registry,
    thaw,
)

DIRECTORY = "docs/science/sci-p02-initial-policy/stage2-v3/authority"
REGISTRY_SHA256 = "602ff0d32ebc625b4c9474660b5b36ee9983c4c598f16ae9b1269e67e5cea50f"
MANIFEST_SHA256 = "ad7bcea900f054ae7e41a323f68b1935dcace3e7ab1f81167819f2ea3ab08b4b"
ENGINE_VERSION = "initial-policy-producer/3.0.0"
POLICY_VERSION = "initial-hypertrophy-policy/1.0.0-limited"


def encoded(value) -> bytes:
    return (
        json.dumps(thaw(value), sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False)
        + "\n"
    ).encode()


def digest(value) -> str:
    return hashlib.sha256(encoded(value)).hexdigest()


@dataclass(frozen=True, slots=True)
class V3Registry:
    historical: V2Registry
    policy: Mapping
    source_digests: Mapping[str, str]
    registry_digest: str
    manifest_digest: str
    binding_digest: str
    bundle_digest: str
    effective_science_digest: str

    @property
    def admitted(self) -> bool:
        return self.policy["admission"]["state"] == "ADMITTED"

    @property
    def active(self) -> bool:
        return self.policy["binding_status"] == "ACTIVE"

    @property
    def binding_ref(self) -> str:
        return self.policy["binding_ref"]


def _binding_digest(policy, sources, historical):
    return digest(
        {"policy": policy, "sources": sources, "historical_bundle": historical.bundle_digest}
    )


def _bundle_digest(binding, historical):
    return digest({"binding": binding, "historical_bundle": historical.bundle_digest})


def assert_trusted_v3(registry: V3Registry, *, require_admitted: bool = True) -> None:
    if type(registry) is not V3Registry:
        raise ValueError("requires the actual limited v3 authority profile")
    assert_trusted(registry.historical)
    binding = _binding_digest(registry.policy, registry.source_digests, registry.historical)
    if (
        digest(registry.policy) != REGISTRY_SHA256
        or digest({"sha256": registry.source_digests}) != MANIFEST_SHA256
        or registry.registry_digest != REGISTRY_SHA256
        or registry.manifest_digest != MANIFEST_SHA256
        or registry.binding_digest != binding
        or registry.bundle_digest != _bundle_digest(binding, registry.historical)
        or registry.effective_science_digest != registry.historical.effective_science_digest
    ):
        raise ValueError("v3 authority or source material differs from reviewed publication")
    if require_admitted:
        admission = registry.policy["admission"]
        expected = {f"C{i}": "ADMITTED_WITH_LIMITS" for i in range(1, 6)}
        expected["C6"] = "EXPLORATION_POLICY_ADMITTED"
        if (
            not registry.admitted
            or not registry.active
            or dict(admission["gates"]) != expected
            or not admission["review_ref"]
            or not admission["decision_ref"]
        ):
            raise ValueError(
                "limited v3 policy has not received effective admission or is withdrawn"
            )


def load_v3_registry(root: Path = ROOT) -> V3Registry:
    root = Path(root).resolve()
    raw = (root / DIRECTORY / "registry.v1.json").read_bytes()
    manifest_raw = (root / DIRECTORY / "sources.v1.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != REGISTRY_SHA256:
        raise ValueError("v3 publication drift requires reviewed versioning")
    if hashlib.sha256(manifest_raw).hexdigest() != MANIFEST_SHA256:
        raise ValueError("v3 source manifest drift")
    policy, sources = json.loads(raw), json.loads(manifest_raw)["sha256"]
    for relative, expected in sources.items():
        path = Path(relative)
        resolved = (root / path).resolve()
        if path.is_absolute() or ".." in path.parts or not resolved.is_relative_to(root):
            raise ValueError("source path escapes reviewed inventory")
        if hashlib.sha256(resolved.read_bytes()).hexdigest() != expected:
            raise ValueError("v3 reviewed source drift: " + relative)
    historical = load_v2_registry(root)
    binding = _binding_digest(policy, sources, historical)
    registry = V3Registry(
        historical=historical,
        policy=_freeze(policy),
        source_digests=_freeze(sources),
        registry_digest=REGISTRY_SHA256,
        manifest_digest=MANIFEST_SHA256,
        binding_digest=binding,
        bundle_digest=_bundle_digest(binding, historical),
        effective_science_digest=historical.effective_science_digest,
    )
    assert_trusted_v3(registry, require_admitted=False)
    return registry
