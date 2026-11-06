"""Pinned initial-scope curation overlay. No producer binding or runtime authority.

Validation is structural/source validation; only the pinned reviewed bundle is
accepted by the resolver. Neither path may create a recommendation or a load.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from tools.science_contracts.blueprint_first_plan_v1 import FirstPlanRequest, decision_fingerprint
from tools.science_initial_policy.producer import validate_input
from tools.science_initial_policy.registry import ROOT, load_registry

PATH = "docs/science/sci-p02-initial-policy/curation-01/candidates.v1.json"
FILE_SHA256 = "d1a3f26268bcb33d3614ce3b4841a2dc42562541b39134646caabf9f37f37803"
MODEL_SHA256 = "f66893fe4bcc568bad6e372d1ebf193339af2cfaf6134febd827d07420458104"
ELIGIBLE = {"ADMITTED_WITH_CONTEXT_CONFIRMATION", "ADMITTED_AS_ALTERNATIVE"}
SCIENTIFIC_INPUTS = frozenset(
    {
        "data/sci/exercise_catalogue.json",
        "data/sci/exercise_catalogue.schema.json",
        "data/sci/evidence_registry.json",
        "data/sci/exposure_credit_policy.json",
        "data/equipment_registry.json",
        "tools/science_contracts/blueprint_first_plan_v1.py",
        "docs/science/sci-p02-initial-policy/v1/policy.json",
        "docs/science/sci-p02-initial-policy/v1/producer-fixtures.json",
        "docs/science/sci-p02-initial-policy/admission-01/audit.json",
        "docs/science/sci-p02-initial-policy/admission-01/policy.json",
    }
)
Text = Annotated[str, Field(min_length=1, strict=True)]


class StrictRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class RegionalClaim(StrictRecord):
    applies_to: list[Text]
    statement: Text
    evidence_refs: list[Text]
    bibliography_refs: list[Text]
    scope_limit: Text


class CuratedCandidate(StrictRecord):
    candidate_id: Text
    intent_id: Text
    movement_pattern: Text
    joint_type: Text
    loaded_joint_actions: list[Text]
    roles: list[dict]
    unilateral: bool
    equipment_mode: Text
    equipment_requirements: list[Text]
    support_setup: list[
        Literal[
            "SELF_STABILISED",
            "BENCH_SUPPORT",
            "CHEST_SUPPORT",
            "SEATED_SUPPORT",
            "SMITH_GUIDANCE",
            "DEDICATED_STATION",
            "REQUIRED_SUPPORT_UNSPECIFIED",
        ]
    ]
    support_basis: Text
    calibration_mode: Literal[
        "BODYWEIGHT_REALISATION",
        "ASSISTANCE_UNSPECIFIED",
        "FREE_DUMBBELL",
        "FREE_BARBELL",
        "SMITH_RESISTANCE",
        "MACHINE_UNSPECIFIED",
        "CABLE_UNSPECIFIED",
    ]
    calibration_facts: Annotated[list[Text], Field(min_length=1)]
    preparation_class: Literal["CONTEXT_DEPENDENT", "UNKNOWN"]
    preparation_requirements: Annotated[list[Text], Field(min_length=1)]
    rep_range_achievability: Literal["UNCONFIRMED"]
    initial_scope_admission: Literal[
        "ADMITTED_WITH_CONTEXT_CONFIRMATION",
        "ADMITTED_AS_ALTERNATIVE",
        "NOT_ADMITTED_FOR_INITIAL_SCOPE",
        "INSUFFICIENT_EVIDENCE",
    ]
    admission_reason: Text
    limitations: Annotated[list[Text], Field(min_length=1)]
    invalidation_conditions: Annotated[list[Text], Field(min_length=1)]
    context_confirmation_kind: Annotated[list[Text], Field(min_length=1)]
    confirmation_validity: Literal["CURRENT_CONTEXT_ONLY_NO_TTL"]
    evidence_refs: Annotated[list[Text], Field(min_length=1)]
    evidence_certainty: Literal["LOW", "LOW_MODERATE", "MODERATE", "INSUFFICIENT"]
    regional_claim_refs: list[Text]
    role_review: Text


class Curation(StrictRecord):
    curation_version: Literal["initial-candidate-curation/1.0.0"]
    review_date: Literal["2026-11-06"]
    base_sha: Text
    runtime_availability: Literal["NOT_SERVED"]
    producer_binding: None
    ready_fixture: Literal["NOT_PRODUCED"]
    source_sha256: dict[Text, Text]
    regional_claims: dict[Text, RegionalClaim]
    candidates: list[CuratedCandidate]


def fingerprint(data: dict) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def validate_curation(data: dict, root: Path = ROOT) -> Curation:
    """Validate pinned-source facts. This does not approve unreviewed decisions."""
    bundle = Curation.model_validate(data)
    if set(bundle.source_sha256) != SCIENTIFIC_INPUTS:
        raise ValueError("canonical source set must be complete and bounded")
    for path, expected in bundle.source_sha256.items():
        if path.startswith("/") or ".." in Path(path).parts:
            raise ValueError("invalid canonical source path")
        if hashlib.sha256((root / path).read_bytes()).hexdigest() != expected:
            raise ValueError(f"canonical source drift: {path}")
    source = json.loads((root / "data/sci/exercise_catalogue.json").read_text())
    records = {
        r["exercise_id"]: r
        for r in source["records"]
        if r["identity"]["identity_relation"] == "CANONICAL"
    }
    evidence = json.loads((root / "data/sci/evidence_registry.json").read_text())
    pool = json.loads(
        (root / "docs/science/sci-p02-initial-policy/admission-01/audit.json").read_text()
    )
    expected_pool = {
        (i["intent_id"], c["id"]) for i in pool["intent_audit"] for c in i["candidates"]
    }
    actual = [(c.intent_id, c.candidate_id) for c in bundle.candidates]
    if len(actual) != len(set(actual)) or set(actual) != expected_pool:
        raise ValueError("canonical candidate pool changed without intent/version review")
    for c in bundle.candidates:
        _validate_candidate(c, records[c.candidate_id], evidence, bundle.regional_claims)
    return bundle


def _validate_candidate(
    c: CuratedCandidate, record: dict, evidence: dict, claims: dict[str, RegionalClaim]
) -> None:
    science, operational = record["exercise_science"], record["exercise_operational"]
    source_roles = science["contributions"]
    if len(c.roles) != len(source_roles):
        raise ValueError("source roles changed")
    for role, source in zip(c.roles, source_roles, strict=True):
        expected = dict(source)
        # The actual trial did not test either named foot-position variant.
        # Categories stay historical; this overlay corrects the evidence basis.
        if (
            c.candidate_id in {"leg-press-paren-pieds-bas", "leg-press-paren-pieds-hauts-ecartes"}
            and source["role_basis"] == "longitudinal_trial"
        ):
            expected["role_basis"] = "joint_action_anatomy"
        if role != expected:
            raise ValueError("source roles changed without a separately reviewed role delta")
    for field in ("movement_pattern", "joint_type", "loaded_joint_actions"):
        if getattr(c, field) != science[field]:
            raise ValueError("canonical movement changed")
    for field in ("equipment_mode", "equipment_requirements", "unilateral"):
        if getattr(c, field) != operational[field]:
            raise ValueError("canonical operational facts changed")
    if not set(c.evidence_refs) <= evidence.keys():
        raise ValueError("noncanonical evidence reference")
    if any(r["role"] == "UNKNOWN" for r in c.roles) and c.initial_scope_admission in ELIGIBLE:
        raise ValueError("UNKNOWN roles block this exact-exposure initial-scope admission")
    for ref in c.regional_claim_refs:
        if ref not in claims or c.candidate_id not in claims[ref].applies_to:
            raise ValueError("regional evidence applied beyond curated configuration")
        if not set(claims[ref].evidence_refs) <= evidence.keys():
            raise ValueError("regional evidence reference is not canonical")


def load_curation(root: Path = ROOT) -> Curation:
    raw = (root / PATH).read_bytes()
    if hashlib.sha256(raw).hexdigest() != FILE_SHA256:
        raise ValueError("curation hash drift; review/version required")
    return validate_curation(json.loads(raw), root)


def _context_state(req: FirstPlanRequest, identity: str, no_equipment: bool) -> str:
    confirmations = [
        c
        for c in req.blueprint.environment.exercise_confirmations
        if c.canonical_exercise_id == identity
    ]
    states = {c.state for c in confirmations}
    if {"AVAILABLE", "UNAVAILABLE"} <= states:
        return "CONFLICT"
    if "UNAVAILABLE" in states:
        return "UNAVAILABLE"
    if "AVAILABLE" in states:
        return "CONFIRMED"
    return "NOT_REQUIRED" if no_equipment else "UNKNOWN"


def resolve_candidates(request: FirstPlanRequest | dict, intent_id: str, bundle: Curation) -> dict:
    """Unranked eligibility/context set, not a default or executable plan."""
    if fingerprint(bundle.model_dump(mode="json")) != MODEL_SHA256:
        raise ValueError("resolver requires the trusted reviewed curation bundle")
    req = FirstPlanRequest.model_validate(request)
    registry = load_registry()
    validate_input(req, registry)
    if intent_id not in registry.references.canonical_intent_ids:
        raise ValueError("unknown canonical intent")
    out = {
        "curation_version": bundle.curation_version,
        "input_fingerprint": decision_fingerprint(req),
        "intent_id": intent_id,
        "status": "CANDIDATES_AVAILABLE",
        "reason": None,
        "candidates": [],
        "held_candidates": [],
        "selected": None,
        "execution_ready": False,
        "ready_fixture": "NOT_PRODUCED",
    }
    reason = _input_review(req)
    if reason:
        out.update(status="REVIEW_REQUIRED", reason=reason)
        return out
    excluded = set(req.blueprint.excluded_exercise_ids.value or [])
    for candidate in sorted(
        (c for c in bundle.candidates if c.intent_id == intent_id), key=lambda c: c.candidate_id
    ):
        state = _context_state(
            req,
            candidate.candidate_id,
            candidate.candidate_id in registry.references.no_equipment_exercise_ids,
        )
        if state == "CONFLICT":
            out.update(status="REVIEW_REQUIRED", reason="CURRENT_CONTEXT_CONFLICT", candidates=[])
            return out
        summary = {
            "candidate_id": candidate.candidate_id,
            "admission": candidate.initial_scope_admission,
            "compatibility": state,
            "unknown_roles": [r["zone"] for r in candidate.roles if r["role"] == "UNKNOWN"],
            "unilateral": candidate.unilateral,
            "calibration_mode": candidate.calibration_mode,
            "calibration_facts": list(candidate.calibration_facts),
            "preparation_class": candidate.preparation_class,
            "preparation_requirements": list(candidate.preparation_requirements),
            "rep_range_achievability": candidate.rep_range_achievability,
        }
        if candidate.candidate_id in excluded or state == "UNAVAILABLE":
            summary["hold_reason"] = (
                "USER_EXCLUDED" if candidate.candidate_id in excluded else state
            )
            out["held_candidates"].append(summary)
        elif candidate.initial_scope_admission not in ELIGIBLE:
            summary["hold_reason"] = candidate.admission_reason
            out["held_candidates"].append(summary)
        else:
            out["candidates"].append(summary)
    if not out["candidates"]:
        out.update(status="CATALOG_GAP", reason="NO_ADMISSIBLE_REALISATION")
    return out


def _input_review(req: FirstPlanRequest) -> str | None:
    # Curation needs these facts, not anthropometry or a session-time prediction.
    for field in ("objective", "population_scope", "limitations"):
        if getattr(req.blueprint, field).state != "KNOWN":
            return "REQUIRED_CONTEXT_UNKNOWN_OR_CONFLICTING"
    if req.blueprint.limitations.value:
        return "USER_REPORTED_LIMITATION"
    if req.blueprint.excluded_exercise_ids.state in {"CONFLICT", "WITHHELD"}:
        return "EXCLUSION_CONSTRAINT_UNRESOLVED"
    return None
