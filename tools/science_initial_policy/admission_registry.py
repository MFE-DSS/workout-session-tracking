"""Pinned, empty authority registry for isolated admission diagnostics only."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

from tools.science_initial_policy.registry import ROOT

DIRECTORY = "docs/science/sci-p02-initial-policy/admission-system-01"
REGISTRY_SHA256 = "186bbf84ebd1b1934c67cd4ca88ff15d2a3417cd1ba041b9fa98aed59256ae82"
MANIFEST_SHA256 = "d833446c93e95c0f909f88a6a693537b1b6b1afaf0916e82b2f980c1a4f61aa5"


@dataclass(frozen=True, slots=True)
class AdmissionRegistry:
    version: str
    registry_digest: str
    manifest_digest: str
    source_digests: Mapping[str, str]
    bindings: tuple = ()


def assert_trusted_admission_registry(registry: AdmissionRegistry) -> None:
    """No caller-side status or dataclass mutation can confer approval."""
    if (
        type(registry) is not AdmissionRegistry
        or registry.version != "initial-policy-admission-registry/1.0.0"
        or registry.registry_digest != REGISTRY_SHA256
        or registry.manifest_digest != MANIFEST_SHA256
        or type(registry.bindings) is not tuple or registry.bindings
        or _manifest_bytes(registry.source_digests) != MANIFEST_SHA256
    ):
        raise ValueError("requires the pinned empty admission registry")


def _manifest_bytes(sources: Mapping) -> str:
    raw = (json.dumps({"sha256": dict(sources)}, sort_keys=True, indent=2) + "\n").encode()
    return hashlib.sha256(raw).hexdigest()


def load_admission_registry(root: Path = ROOT) -> AdmissionRegistry:
    root = Path(root).resolve()
    raw = (root / DIRECTORY / "registry.v1.json").read_bytes()
    manifest_raw = (root / DIRECTORY / "registry-manifest.v1.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != REGISTRY_SHA256:
        raise ValueError("admission registry drift requires versioned review")
    if hashlib.sha256(manifest_raw).hexdigest() != MANIFEST_SHA256:
        raise ValueError("admission manifest drift requires versioned review")
    registry, manifest = json.loads(raw), json.loads(manifest_raw)
    if registry != {
        "version": "initial-policy-admission-registry/1.0.0",
        "scientific_admission": "NOT_ADMITTED", "bindings": [],
    }:
        raise ValueError("admitted bindings are not enabled in this isolated release")
    pins = manifest["sha256"]
    for relative, expected in pins.items():
        path = Path(relative)
        resolved = (root / path).resolve()
        if path.is_absolute() or ".." in path.parts or not resolved.is_relative_to(root):
            raise ValueError("source path escapes admission inventory")
        if hashlib.sha256(resolved.read_bytes()).hexdigest() != expected:
            raise ValueError(f"admission source drift: {relative}")
    result = AdmissionRegistry(
        version=registry["version"], registry_digest=REGISTRY_SHA256,
        manifest_digest=MANIFEST_SHA256, source_digests=MappingProxyType(pins),
    )
    assert_trusted_admission_registry(result)
    return result
