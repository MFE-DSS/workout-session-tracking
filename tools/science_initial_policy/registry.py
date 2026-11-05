"""Pinned, read-only proposed registries; not a user-provided approval authority."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

from tools.science_contracts.blueprint_first_plan_v1 import ReferenceSnapshot

ENGINE_VERSION = "initial-policy-producer/1.0.0"
POLICY_PATH = "docs/science/sci-p02-initial-policy/v1/policy.json"
POLICY_SHA256 = "8aef079da6a15298bfa2ec1bdec1b417588b6f535224c61afb2f50f98612dfb4"
ROOT = Path(__file__).resolve().parents[2]


def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


@dataclass(frozen=True)
class Registry:
    policy: Mapping[str, Any]
    records: Mapping[str, Any]
    credit: Mapping[str, Any]
    source_hashes: Mapping[str, str]
    references: ReferenceSnapshot


def load_registry(root: Path = ROOT) -> Registry:
    """Reject drift and freeze snapshots. No admission API or production activation."""
    raw = (root / POLICY_PATH).read_bytes()
    if hashlib.sha256(raw).hexdigest() != POLICY_SHA256:
        raise ValueError("policy hash mismatch; review/version required")
    policy = json.loads(raw)
    sources = {}
    for relative, expected in policy["source_hashes"].items():
        data = (root / relative).read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f"source hash mismatch: {relative}")
        if relative.endswith(".json"):
            sources[relative] = json.loads(data)
    catalogue = sources["data/sci/exercise_catalogue.json"]
    records = {
        r["exercise_id"]: r
        for r in catalogue["records"]
        if r["identity"]["identity_relation"] == "CANONICAL"
    }
    references = ReferenceSnapshot(
        catalogue_version=catalogue["catalogue_header"]["catalogue_version"],
        evidence_refs=frozenset(sources["data/sci/evidence_registry.json"])
        | frozenset(policy["evidence_refs"]),
        canonical_exercise_ids=frozenset(records),
        canonical_intent_ids=frozenset(i["intent_id"] for i in policy["intents"]),
        equipment_item_ids=frozenset(
            item["item_id"] for item in sources["data/equipment_registry.json"]["items"]
        ),
        approved_policy_refs=frozenset(),  # Build approval is not scientific admission.
        no_equipment_exercise_ids=frozenset(
            key
            for key, r in records.items()
            if r["exercise_operational"].get("equipment_requirement_status") == "RESOLVED"
            and r["exercise_operational"].get("equipment_requirements") == []
        ),
    )
    return Registry(
        policy=_freeze(policy),
        records=_freeze(records),
        credit=_freeze(sources["data/sci/exposure_credit_policy.json"]["credits"]),
        source_hashes=_freeze(policy["source_hashes"]),
        references=references,
    )
