#!/usr/bin/env python3
"""Validate a judge agent output against agent_review.schema.json — GO C2 §7.
Stdlib-only, no external jsonschema dependency. Returns a list of error strings (empty = valid).
Kept intentionally strict: missing evidence, out-of-range scores, and unknown verdicts are errors."""
from __future__ import annotations

import json
import pathlib
import re
import sys

CRITERIA = [
    "orientation_and_laterality", "source_structure_completeness", "anatomical_visual_consistency",
    "context_relationships", "occlusion_integrity", "silhouette_readability", "mobile_readability",
    "product_semantic_clarity", "provenance_honesty", "scope_and_claim_discipline",
]
REGIONS = {"chest", "shoulders", "posterior"}
ROLES = {"J1_anatomy_consistency", "J2_medical_illustration", "J3_fitness_semantics",
         "J4_adversarial_falsifier", "J5_provenance_governance"}
VERDICTS = {"ACCEPT", "ACCEPT_WITH_CONSTRAINTS", "REVISION_REQUIRED", "BLOCKED", "INSUFFICIENT_EVIDENCE"}
SEVERITIES = {"CRITICAL", "MAJOR", "MINOR", "OBSERVATION"}
SIDES = {"left", "right", "bilateral", "midline", "not_applicable"}
VIEWS = {"front", "back", "both", "not_applicable"}
VETO_TYPES = {"mirror_or_laterality_inversion", "mandatory_source_structure_missing",
              "source_provenance_lost", "false_source_segmented_claim",
              "open3dmodel_or_servier_contamination", "generative_anatomy",
              "false_professional_approval_claim", "unsafe_runtime_claim",
              "schema_or_calibration_integrity_failure"}
TOP = ["schema_version", "region", "candidate_sha256", "judge_role", "provider_family",
       "model_id", "run_id", "evidence_files_reviewed", "scores", "findings", "vetoes",
       "confidence", "proposed_verdict"]


def _conf(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and 0.0 <= float(x) <= 1.0


def _check_header(o) -> list[str]:
    e = [f"missing field: {k}" for k in TOP if k not in o]
    if o.get("schema_version") != "1.0.0":
        e.append("schema_version must be 1.0.0")
    if o.get("region") not in REGIONS:
        e.append("bad region")
    if not isinstance(o.get("candidate_sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", o.get("candidate_sha256", "")):
        e.append("bad candidate_sha256")
    if o.get("judge_role") not in ROLES:
        e.append("bad judge_role")
    for k in ("provider_family", "model_id", "run_id"):
        if not isinstance(o.get(k), str) or not o.get(k):
            e.append(f"bad {k}")
    ev = o.get("evidence_files_reviewed")
    if not isinstance(ev, list) or not ev or not all(isinstance(x, str) and x for x in ev):
        e.append("evidence_files_reviewed must be a non-empty list of strings")
    if not _conf(o.get("confidence")):
        e.append("bad top-level confidence")
    if o.get("proposed_verdict") not in VERDICTS:
        e.append("bad proposed_verdict")
    return e


def _check_scores(o) -> list[str]:
    sc = o.get("scores")
    if not isinstance(sc, dict):
        return ["scores missing"]
    e = []
    for c in CRITERIA:
        if c not in sc:
            e.append(f"missing score: {c}")
        elif not isinstance(sc[c], int) or isinstance(sc[c], bool) or not (0 <= sc[c] <= 5):
            e.append(f"score out of range 0-5: {c}={sc.get(c)}")
    e += [f"unknown score key: {k}" for k in sc if k not in CRITERIA]
    return e


def _check_findings(o) -> list[str]:
    fs = o.get("findings")
    if not isinstance(fs, list):
        return ["findings must be a list"]
    e = []
    for i, f in enumerate(fs):
        e += [f"finding[{i}] missing {k}" for k in
              ("severity", "structure", "side", "view", "evidence", "rationale", "proposed_action", "confidence")
              if k not in f]
        if f.get("severity") not in SEVERITIES:
            e.append(f"finding[{i}] bad severity")
        if f.get("side") not in SIDES:
            e.append(f"finding[{i}] bad side")
        if f.get("view") not in VIEWS:
            e.append(f"finding[{i}] bad view")
        if not _conf(f.get("confidence")):
            e.append(f"finding[{i}] bad confidence")
    return e


def _check_vetoes(o) -> list[str]:
    vs = o.get("vetoes")
    if not isinstance(vs, list):
        return ["vetoes must be a list"]
    e = []
    for i, v in enumerate(vs):
        if v.get("type") not in VETO_TYPES:
            e.append(f"veto[{i}] bad type")
        if not _conf(v.get("confidence")):
            e.append(f"veto[{i}] bad confidence")
        e += [f"veto[{i}] missing {k}" for k in ("rationale", "evidence") if not v.get(k)]
    return e


def validate_agent_review(o) -> list[str]:
    if not isinstance(o, dict):
        return ["not an object"]
    return _check_header(o) + _check_scores(o) + _check_findings(o) + _check_vetoes(o)


def main() -> int:
    o = json.loads(pathlib.Path(sys.argv[1]).read_text())
    errs = validate_agent_review(o)
    print("VALID" if not errs else "INVALID")
    for x in errs:
        print(f"  - {x}")
    return 0 if not errs else 1


if __name__ == "__main__":
    raise SystemExit(main())
