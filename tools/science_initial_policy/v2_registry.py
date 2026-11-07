"""Frozen v2 research references; build authorization is not policy admission."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass, fields
from pathlib import Path

from tools.science_contracts.blueprint_first_plan_v1 import ReferenceSnapshot
from tools.science_initial_policy.calibration_time_contracts import content_digest
from tools.science_initial_policy.curation import load_curation
from tools.science_initial_policy.pull_exposure import load_pull_exposure
from tools.science_initial_policy.registry import ROOT, _freeze, load_registry

ENGINE_VERSION = "initial-policy-producer/2.0.0"
PATH = "docs/science/sci-p02-initial-policy/calibration-time-01/policy.v1.json"
FILE_SHA256 = "08a4834113b01f1417a9f45a5c7195c9d6c24c4dd8d1dd72d982b0c51aa73462"
MATERIAL_SHA256 = "28be50b1e5d01164e2922cd0c6eeb7d960f93f94b08fad9ea091125f25e8f86f"


def thaw(value):
    if isinstance(value, Mapping):
        return {key: thaw(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [thaw(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted(value)
    return value


@dataclass(frozen=True, slots=True)
class V2Registry:
    policy: Mapping
    dose: Mapping
    candidates: Mapping
    references: ReferenceSnapshot
    bundle_digest: str
    effective_science_digest: str
    effective_catalogue_version: str
    realization_refs: Mapping
    source_digests: Mapping


def _signature(bundle: V2Registry) -> str:
    material = {
        f.name: thaw(getattr(bundle, f.name)) for f in fields(bundle) if f.name != "references"
    }
    material["references"] = {
        f.name: thaw(getattr(bundle.references, f.name)) for f in fields(bundle.references)
    }
    return content_digest(material)


def assert_trusted(bundle: V2Registry) -> None:
    """Pure in-memory verification, including nested edits/dataclass replacements."""
    if not isinstance(bundle, V2Registry) or _signature(bundle) != MATERIAL_SHA256:
        raise ValueError("v2 requires the pinned trusted non-admitted registry")


def _read_policy(root: Path):
    raw = (root / PATH).read_bytes()
    if hashlib.sha256(raw).hexdigest() != FILE_SHA256:
        raise ValueError("v2 policy drift requires versioned review")
    p = json.loads(raw)
    manifest_raw = (root / p["source_manifest"]).read_bytes()
    if hashlib.sha256(manifest_raw).hexdigest() != p["source_manifest_sha256"]:
        raise ValueError("v2 source inventory drift")
    pins = json.loads(manifest_raw)["sha256"]
    for relative, expected in pins.items():
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("source path escapes the reviewed inventory")
        if hashlib.sha256((root / path).read_bytes()).hexdigest() != expected:
            raise ValueError(f"v2 source hash drift: {relative}")
    if p["approved_policy_refs"] or p["approved_restart_refs"]:
        raise ValueError("no scientific admission authority exists in this v2 release")
    return p, pins


def _candidate_records(curation, pull, legacy):
    overlays = {r.candidate_id: r for r in pull.candidates}
    records, profiles = {}, {}
    for row in curation.candidates:
        other = overlays.get(row.candidate_id)
        definition = (
            other.canonical_execution
            if other
            else legacy.records[row.candidate_id]["exercise_science"].get("canonical_execution")
        )
        profile = {
            "candidate_id": row.candidate_id,
            "loaded_joint_actions": row.loaded_joint_actions,
            "support_setup": row.support_setup,
            "canonical_execution": definition,
        }
        profile_ref = "initial-candidate-realisation/1.0.0@" + content_digest(profile)
        profiles[row.candidate_id] = profile_ref
        records[row.candidate_id] = {
            "candidate_id": row.candidate_id,
            "intent_id": row.intent_id,
            "admission": other.initial_scope_admission if other else row.initial_scope_admission,
            "unilateral": row.unilateral,
            "joint_type": row.joint_type,
            "source_roles": row.roles,
            "effective_roles": other.effective_roles if other else row.roles,
            "requires_qualified_role_projection": other is not None,
            "realization_ref": profile_ref,
        }
    return records, profiles


def _build_registry(root: Path) -> V2Registry:
    p, pins = _read_policy(root)
    legacy = load_registry(root)
    curation, pull = load_curation(root), load_pull_exposure(root)
    if (
        curation.curation_version != p["curation_version"]
        or pull.overlay_version != p["pull_overlay_version"]
    ):
        raise ValueError("scientific overlay version mismatch")
    admission = json.loads((root / p["dose_source"]).read_text())
    rules = {r["rule_id"]: r["value"] for r in admission["rules"]}
    dose = {
        "source_version": admission["policy_version"],
        "cadences": rules["scope"]["cadences"],
        "work_sets": rules["work_sets"],
        "rep_range": rules["repetitions"],
        "rir_target": rules["effort"]["rir_target"],
        "rest_seconds": rules["rest"],
        "intents": thaw(legacy.policy["intents"]),
    }
    records, profiles = _candidate_records(curation, pull, legacy)
    science = content_digest({"candidate_records": records, "dose": dose, "source_hashes": pins})
    catalogue_version = "initial-plan-effective-catalogue/1.0.0@" + science
    refs = ReferenceSnapshot(
        catalogue_version=catalogue_version,
        evidence_refs=legacy.references.evidence_refs,
        canonical_exercise_ids=legacy.references.canonical_exercise_ids,
        canonical_intent_ids=legacy.references.canonical_intent_ids,
        equipment_item_ids=legacy.references.equipment_item_ids,
        approved_policy_refs=frozenset(),
        no_equipment_exercise_ids=legacy.references.no_equipment_exercise_ids,
    )
    return V2Registry(
        policy=_freeze(p),
        dose=_freeze(dose),
        candidates=_freeze(records),
        references=refs,
        bundle_digest=content_digest({"policy_sha256": FILE_SHA256, "sources": pins}),
        effective_science_digest=science,
        effective_catalogue_version=catalogue_version,
        realization_refs=_freeze(profiles),
        source_digests=_freeze(pins),
    )


def load_v2_registry(root: Path = ROOT) -> V2Registry:
    bundle = _build_registry(root)
    assert_trusted(bundle)
    return bundle
