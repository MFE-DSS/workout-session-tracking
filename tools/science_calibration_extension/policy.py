"""Exact reviewed successor authority; never accepts a caller admission label."""

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from tools.science_calibration_bootstrap.policy import digest
from tools.science_initial_policy.registry import ROOT, _freeze
from tools.science_initial_policy.v3_admission import assert_trusted_v3, load_v3_registry

DIRECTORY = Path("docs/science/sci-p02-initial-policy/calibration-six-extensions/authority")
REGISTRY_SHA256 = "a0c9a20a48490bb47272c7b8e03edc3b06ef4369e0eaf671bdd45eff39acb6ff"
SOURCES_SHA256 = "d89b9308891b7e7c98a5a750ba7acdcc53825d06824cd236d2aefa4c7e4cc95f"


@dataclass(frozen=True, slots=True)
class ExtensionAuthority:
    root: Path
    policy: Mapping
    source_digests: Mapping
    historical: object
    bundle_digest: str


def load_authority(root: Path = ROOT) -> ExtensionAuthority:
    root = Path(root).resolve()
    raw = (root / DIRECTORY / "registry.v1.json").read_bytes()
    source_raw = (root / DIRECTORY / "sources.v1.json").read_bytes()
    if (
        hashlib.sha256(raw).hexdigest() != REGISTRY_SHA256
        or hashlib.sha256(source_raw).hexdigest() != SOURCES_SHA256
    ):
        raise ValueError("extension publication drift requires reviewed versioning")
    policy, sources = json.loads(raw), json.loads(source_raw)["sha256"]
    for relative, expected in sources.items():
        path = Path(relative)
        source = (root / path).resolve()
        if path.is_absolute() or ".." in path.parts or not source.is_relative_to(root):
            raise ValueError("extension source escapes reviewed inventory")
        if hashlib.sha256(source.read_bytes()).hexdigest() != expected:
            raise ValueError("extension reviewed source drift: " + relative)
    historical = load_v3_registry(root)
    if historical.bundle_digest != policy["v3_bundle_digest"]:
        raise ValueError("extension parent V3 differs")
    return ExtensionAuthority(
        root,
        _freeze(policy),
        _freeze(sources),
        historical,
        digest(dict(policy=policy, sources=sources, v3_bundle=historical.bundle_digest)),
    )


def assert_authority(authority):
    if type(authority) is not ExtensionAuthority:
        raise ValueError("requires actual published extension authority")
    actual = load_authority(authority.root)
    if (
        digest(authority.policy) != REGISTRY_SHA256
        or digest({"sha256": authority.source_digests}) != SOURCES_SHA256
        or authority.bundle_digest != actual.bundle_digest
    ):
        raise ValueError("extension authority differs from current publication")
    assert_trusted_v3(authority.historical)
    from .evaluator import PROFILES

    p = authority.policy
    if (
        p["state"] != "ADMITTED_WITH_LIMITS"
        or p["status"] != "ACTIVE"
        or p["runtime_availability"] != "NOT_SERVED"
        or not p["review_ref"]
        or not p["decision_ref"]
        or {r["candidate_id"] for r in p["profiles"]} != set(PROFILES)
    ):
        raise ValueError("extension not admitted or withdrawn")
    for row in p["profiles"]:
        parent = next(
            s
            for s in authority.historical.policy["selection"]
            if s["candidate_id"] == row["candidate_id"]
        )
        if (
            row["state"] != "ADMITTED_WITH_LIMITS"
            or row["status"] != "ACTIVE"
            or row["load_semantics"] != PROFILES[row["candidate_id"]]
            or row["realization_ref"] != parent["realization_ref"]
            or row["intent_id"] != parent["intent_id"]
            or not row["review_ref"]
            or not row["protocol_ref"]
            or not row["withdrawal_ref"]
        ):
            raise ValueError("realization not admitted or withdrawn")
