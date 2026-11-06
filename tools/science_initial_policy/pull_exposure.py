"""Reviewed five-candidate overlay; no runtime binding, prescription or credit calculator."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field

from tools.science_contracts.blueprint_first_plan_v1 import FirstPlanRequest, decision_fingerprint
from tools.science_initial_policy.curation import (
    StrictRecord,
    Text,
    fingerprint,
    load_curation,
    resolve_candidates,
)
from tools.science_initial_policy.registry import ROOT

PATH = "docs/science/sci-p02-initial-policy/pull-exposure-01/overlay.v1.json"
FILE_SHA256 = "7aa247871658d62a00f02836e768d1bdc3ff3aa248f236660ab99efa2dbc75a1"
MODEL_SHA256 = "662d5a19df3544ac2c83a2a7cd5b2691a02fbadb3dc4c9c7a4e7aa4eb0412730"
NEUTRAL = "tirage-poulie-haute-prise-neutre"
INTENT = "initial_vertical_pull_v1"
IDS = frozenset(
    {
        "tirage-poulie-haute-prise-large",
        NEUTRAL,
        "tirage-vertical-unilateral-cable",
        "traction-assistee-machine",
        "traction-assistee-unilaterale",
    }
)
SOURCE_PATHS = frozenset(
    {
        "tools/science_initial_policy/curation.py",
        "docs/science/sci-p02-initial-policy/admission-01/policy.json",
        "scripts/generate_sci_catalogue.py",
        "docs/science/sci-p02-initial-policy/curation-01/coverage-and-fixtures.v1.json",
        "data/reference_split.json",
        "data/exercise_knowledge_base.json",
        "tools/science_contracts/blueprint_first_plan_v1.py",
        "tools/science_initial_policy/producer.py",
        "data/sci/sources/curation_reviewed.json",
        "docs/strategy/Sx_SCI_V2_CATALOGUE_INTEGRATION_01_SPEC.md",
        "data/sci/exercise_catalogue.json",
        "docs/science/sci-p02-initial-policy/v1/producer-fixtures.json",
        "docs/science/sci-p02-initial-policy/v1/policy.json",
        "data/sci/sources/identity_map.json",
        "data/sci/exposure_credit_policy.json",
        "docs/science/sci-p02-initial-policy/curation-01/candidates.v1.json",
        "data/sci/evidence_registry.json",
        "app/services/sci_exposure.py",
        "tools/science_initial_policy/registry.py",
        "data/sci/exercise_catalogue.schema.json",
        "docs/strategy/Sx_AUREN_SCIENTIFIC_ENGINE_V2_SPEC.md",
    }
)
Role = Literal["PRIMARY", "SECONDARY", "MINOR", "UNKNOWN"]
Review = Literal["PENDING", "ACCEPTED", "REJECTED"]


class Levels(StrictRecord):
    ANATOMICAL_CAPACITY: Text
    ACUTE_RECRUITMENT: Text
    PLAUSIBLE_HYPERTROPHY: Text
    ORDINAL_AUREN_ROLE: Text


class ZoneAssessment(StrictRecord):
    source_role: Role
    effective_role: Role
    levels: Levels
    bibliography_refs: list[Text]
    longitudinal_hypertrophy: Literal["UNAVAILABLE_FOR_CANDIDATE_ZONE"]
    ordinal_decision: Literal[
        "REVIEWED_DERIVED_SYNERGIST", "EXISTING_DERIVED_SYNERGIST", "CATEGORY_UNRESOLVED"
    ]
    credit_authority: Literal["EXISTING_POLICY_ONLY_NOT_CALCULATED_HERE"]


class RoleDelta(StrictRecord):
    candidate_id: Literal["tirage-poulie-haute-prise-neutre"]
    zone: Literal["pecs"]
    before: Literal["UNKNOWN"]
    after: Literal["SECONDARY"]
    claim: Text
    authority_type: Literal["LOADED_JOINT_ACTION_FUNCTIONAL_ANATOMY"]
    role_basis: Literal["joint_action_anatomy"]
    evidence_refs: Annotated[list[Text], Field(min_length=1)]
    bibliography_refs: Annotated[list[Text], Field(min_length=1)]
    limitations: Annotated[list[Text], Field(min_length=1)]
    reviewer_decision: Review
    scope: Literal["QUALIFIED_CANONICAL_EXECUTION_ONLY"]
    reassessment: Text


class PullCandidate(StrictRecord):
    candidate_id: Text
    scientific_identity_id: Text
    intent_id: Literal["initial_vertical_pull_v1"]
    movement_pattern: Literal["vertical_pull"]
    loaded_joint_actions: list[Text]
    canonical_execution: Text | None
    execution_source: Literal[
        "CANONICAL_CATALOGUE_OPERATOR_RULING", "CANONICAL_FIELDS_AND_SOURCE_CUES_INCOMPLETE"
    ]
    identity_assessment: Text
    source_roles: list[dict]
    effective_roles: list[dict]
    zone_assessments: dict[Literal["pecs", "rear_delts"], ZoneAssessment]
    initial_scope_admission: Literal["ADMITTED_WITH_CONTEXT_CONFIRMATION", "INSUFFICIENT_EVIDENCE"]
    admission_reason: Text
    execution_requirements: Annotated[list[Text], Field(min_length=1)]
    equipment_mode: Text
    equipment_requirements: list[Text]
    unilateral: bool
    calibration_mode: Text
    calibration_facts: list[Text]
    preparation_class: Text
    preparation_requirements: list[Text]
    rep_range_achievability: Literal["UNCONFIRMED"]
    evidence_refs: list[Text]
    limitations: Annotated[list[Text], Field(min_length=1)]
    source_limitations: list[Text]
    role_scope: Literal["QUALIFIED_CANONICAL_EXECUTION_ONLY"]
    reviewer_decision: Review


class PullExposure(StrictRecord):
    overlay_version: Literal["vertical-pull-exposure/1.0.0"]
    parent_curation_version: Literal["initial-candidate-curation/1.0.0"]
    base_sha: Text
    review_date: Literal["2026-11-06"]
    scientific_review: Review
    runtime_availability: Literal["NOT_SERVED"]
    producer_binding: None
    ready_fixture: Literal["NOT_PRODUCED"]
    source_sha256: dict[Text, Text]
    contract_decision: Literal["CURRENT_CONTRACT_SUFFICIENT", "CONTRACT_AMENDMENT_REQUIRED"]
    credit_policy_ref: Literal["sci-exposure-credit-v1"]
    credit_interpretation: Literal["CONVENTION_NOT_MEASURED_PHYSIOLOGICAL_FRACTION"]
    role_delta: Annotated[list[RoleDelta], Field(max_length=1)]
    candidates: list[PullCandidate]


def validate_pull_exposure(data: dict, root: Path = ROOT) -> PullExposure:
    """Source/structure validation is not authority to apply an unreviewed artefact."""
    bundle = PullExposure.model_validate(data)
    if set(bundle.source_sha256) != SOURCE_PATHS:
        raise ValueError("source set must be complete and bounded")
    for path, expected in bundle.source_sha256.items():
        if hashlib.sha256((root / path).read_bytes()).hexdigest() != expected:
            raise ValueError(f"source drift: {path}")
    identities = [c.candidate_id for c in bundle.candidates]
    if len(identities) != len(IDS) or set(identities) != IDS:
        raise ValueError("vertical pool must be exactly the five canonical candidates")
    parent = load_curation(root)
    old = {c.candidate_id: c for c in parent.candidates}
    catalogue = json.loads((root / "data/sci/exercise_catalogue.json").read_text())
    records = {r["exercise_id"]: r for r in catalogue["records"]}
    evidence = json.loads((root / "data/sci/evidence_registry.json").read_text())
    for delta in bundle.role_delta:
        if delta.evidence_refs != ["EV-71"]:
            raise ValueError("role authority is EV-71, not EMG or an unpromoted evidence ID")
    for row in bundle.candidates:
        _validate_candidate(row, old[row.candidate_id], records[row.candidate_id], bundle)
        if not set(row.evidence_refs) <= evidence.keys():
            raise ValueError("uncanonical evidence reference")
    return bundle


def _validate_parent_facts(row, old, record: dict) -> None:
    for field in (
        "movement_pattern",
        "loaded_joint_actions",
        "equipment_mode",
        "equipment_requirements",
        "unilateral",
        "calibration_mode",
        "calibration_facts",
        "preparation_class",
        "preparation_requirements",
    ):
        if getattr(row, field) != getattr(old, field):
            raise ValueError(f"canonical or parent fact changed: {field}")
    if row.scientific_identity_id != record["identity"]["scientific_identity_id"]:
        raise ValueError("canonical identity changed")
    execution = record["exercise_science"].get("canonical_execution")
    if row.canonical_execution != execution:
        raise ValueError("canonical execution changed")
    if row.source_roles != old.roles or row.source_limitations != old.limitations:
        raise ValueError("historical parent facts changed")


def _validate_candidate(row, old, record: dict, bundle: PullExposure) -> None:
    _validate_parent_facts(row, old, record)
    expected = copy.deepcopy(old.roles)
    for delta in bundle.role_delta:
        if delta.candidate_id == row.candidate_id:
            role = next(r for r in expected if r["zone"] == delta.zone)
            if role["role"] != delta.before:
                raise ValueError("role delta does not match its source")
            role.update(
                role=delta.after, role_basis=delta.role_basis, evidence_refs=delta.evidence_refs
            )
    if row.effective_roles != expected:
        raise ValueError("effective roles exceed the explicit bounded delta")
    if set(row.zone_assessments) != {"pecs", "rear_delts"}:
        raise ValueError("both ancillary zones require an assessment")
    for zone, assessment in row.zone_assessments.items():
        before = next(r["role"] for r in old.roles if r["zone"] == zone)
        after = next(r["role"] for r in expected if r["zone"] == zone)
        if (assessment.source_role, assessment.effective_role) != (before, after):
            raise ValueError("participation assessment cannot change an ordinal role")
    if row.initial_scope_admission == "ADMITTED_WITH_CONTEXT_CONFIRMATION":
        if any(r["role"] == "UNKNOWN" for r in expected):
            raise ValueError("unresolved category cannot be silently admitted or credited")
        if not any(r["zone"] == "lats" and r["role"] == "PRIMARY" for r in expected):
            raise ValueError("primary uncertainty remains blocking")
        if not row.canonical_execution or "shoulder_extension" not in row.loaded_joint_actions:
            raise ValueError("the role inference requires its defined loaded-extension execution")


def _require_reviewed(bundle: PullExposure) -> None:
    if bundle.scientific_review != "ACCEPTED" or any(
        r.reviewer_decision != "ACCEPTED" for r in [*bundle.candidates, *bundle.role_delta]
    ):
        raise ValueError("scientific review is not accepted")


def load_pull_exposure(root: Path = ROOT) -> PullExposure:
    raw = (root / PATH).read_bytes()
    if hashlib.sha256(raw).hexdigest() != FILE_SHA256:
        raise ValueError("overlay drift requires review/versioning")
    bundle = validate_pull_exposure(json.loads(raw), root)
    _require_reviewed(bundle)
    return bundle


def resolve_vertical_pull(request: FirstPlanRequest | dict, bundle: PullExposure) -> dict:
    """Scientific conditional candidate set; never an executed role, credit or READY payload."""
    _require_reviewed(bundle)
    if fingerprint(bundle.model_dump(mode="json")) != MODEL_SHA256:
        raise ValueError("resolver requires the trusted reviewed overlay")
    req = FirstPlanRequest.model_validate(request)
    parent = resolve_candidates(req, INTENT, load_curation())
    out = {
        "overlay_version": bundle.overlay_version,
        "input_fingerprint": decision_fingerprint(req),
        "parent_curation_status": parent["status"],
        "status": parent["status"],
        "reason": parent["reason"],
        "candidates": [],
        "held_candidates": [],
        "selected": None,
        "execution_ready": False,
        "runtime_availability": "NOT_SERVED",
        "ready_fixture": "NOT_PRODUCED",
    }
    if parent["status"] == "REVIEW_REQUIRED":
        return out
    rows = {r.candidate_id: r for r in bundle.candidates}
    excluded = set(req.blueprint.excluded_exercise_ids.value or [])
    for original in parent["held_candidates"]:
        row = rows[original["candidate_id"]]
        item = copy.deepcopy(original)
        item.update(
            admission=row.initial_scope_admission,
            role_projection={
                "scope": row.role_scope,
                "application": "NOT_APPLIED_TO_EXECUTED_HISTORY",
                "source_unknown_roles": [
                    r["zone"] for r in row.source_roles if r["role"] == "UNKNOWN"
                ],
                "unknown_roles": [r["zone"] for r in row.effective_roles if r["role"] == "UNKNOWN"],
                "secondary_roles": [
                    r["zone"] for r in row.effective_roles if r["role"] == "SECONDARY"
                ],
            },
            canonical_execution=row.canonical_execution,
            execution_confirmation_required=True,
            execution_requirements=list(row.execution_requirements),
        )
        item.pop("unknown_roles", None)
        eligible = (
            row.initial_scope_admission == "ADMITTED_WITH_CONTEXT_CONFIRMATION"
            and row.candidate_id not in excluded
            and item["compatibility"] != "UNAVAILABLE"
        )
        if eligible:
            item.pop("hold_reason", None)
            out["candidates"].append(item)
        else:
            if row.initial_scope_admission == "INSUFFICIENT_EVIDENCE":
                item["hold_reason"] = row.admission_reason
            out["held_candidates"].append(item)
    out.update(
        status="CANDIDATES_AVAILABLE" if out["candidates"] else "CATALOG_GAP",
        reason=None if out["candidates"] else "NO_ADMISSIBLE_REALISATION",
    )
    return out
