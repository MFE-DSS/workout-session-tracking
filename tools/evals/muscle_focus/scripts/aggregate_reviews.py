#!/usr/bin/env python3
"""Deterministic aggregation of blinded judge reviews — GO C2 §11.

Pure and order-independent: given a list of schema-valid agent_review objects for ONE region,
it produces the deterministic aggregate (per-criterion normalized stats, weighted score, consensus,
confirmed vetoes, status). No network, no randomness. The arbiter may only LOWER status.

Weights/thresholds are loaded from rubrics/common.yaml when PyYAML is available, else from the
embedded fallback (kept identical to common.yaml). Scores are integers 0-5, normalized x*20 -> 0-100.
"""
from __future__ import annotations

import json
import pathlib
import statistics
import sys

CRITERIA = [
    "orientation_and_laterality", "source_structure_completeness", "anatomical_visual_consistency",
    "context_relationships", "occlusion_integrity", "silhouette_readability", "mobile_readability",
    "product_semantic_clarity", "provenance_honesty", "scope_and_claim_discipline",
]

# Fallback — MUST stay identical to rubrics/common.yaml (a test asserts the sum is 100).
WEIGHTS = {
    "anatomical_visual_consistency": 20, "orientation_and_laterality": 12,
    "source_structure_completeness": 12, "context_relationships": 8, "occlusion_integrity": 8,
    "silhouette_readability": 10, "mobile_readability": 8, "product_semantic_clarity": 8,
    "provenance_honesty": 8, "scope_and_claim_discipline": 6,
}
CONSENSUS = {"high_max_stddev": 7, "medium_max_stddev": 12}
VETO_CFG = {"min_independent_roles": 2, "min_role_confidence": 0.80}
VERDICT_ORDER = {"BLOCKED": 1, "REVISION_REQUIRED": 2, "ACCEPT_WITH_CONSTRAINTS": 3, "ACCEPT": 4}

# Governance invariants for this sprint — centralised so reports/tests share one source of truth.
GOVERNANCE = {
    "professional_anatomical_review": "NOT_PERFORMED_NOT_CLAIMED",
    "runtime": "BLOCKED",
    "asset_intake": "NOT_STARTED",
    "section_5bis": "NOT_ENACTED",
    "global_acceptance": "BLOCKED",
    "external_dispatch": "DEFERRED_BY_OWNER",
    "chest_partition": "REVIEW_PARTITION_UNRESOLVED / NOT ACCEPTED",
}
CALIB_REQUIRE_CRITICAL = 1.00
CALIB_REQUIRE_OVERALL = 0.90


def calibration_result(cases, detections):
    """Pure calibration scoring. cases: [{case_id, is_critical}]; detections: {case_id: bool}.
    Council must detect 100% of CRITICAL and >= 90% overall (rubrics/common.yaml)."""
    crit = [c for c in cases if c.get("is_critical")]
    crit_det = sum(1 for c in crit if detections.get(c["case_id"]))
    overall_det = sum(1 for c in cases if detections.get(c["case_id"]))
    crit_ok = (len(crit) == 0) or (crit_det == len(crit))
    overall_ok = (len(cases) == 0) or (overall_det / len(cases) >= CALIB_REQUIRE_OVERALL)
    return {
        "critical_total": len(crit), "critical_detected": crit_det,
        "overall_total": len(cases), "overall_detected": overall_det,
        "critical_ok": crit_ok, "overall_ok": overall_ok,
        "result": "PASS" if (crit_ok and overall_ok) else "FAILED",
    }


def partition_accepted(_aggregate=None):
    """The chest diagnostic partition can NEVER be internally accepted in this sprint."""
    return False


def _load_common():
    """Load weights/thresholds from common.yaml if PyYAML is present; else keep embedded."""
    global WEIGHTS, CONSENSUS, VETO_CFG
    try:
        import yaml  # noqa
    except Exception:
        return
    p = pathlib.Path(__file__).resolve().parent.parent / "rubrics" / "common.yaml"
    if not p.is_file():
        return
    cfg = yaml.safe_load(p.read_text())
    WEIGHTS = dict(cfg["weights"])
    CONSENSUS = {"high_max_stddev": cfg["consensus"]["high_max_stddev"],
                 "medium_max_stddev": cfg["consensus"]["medium_max_stddev"]}
    VETO_CFG = {"min_independent_roles": cfg["veto_confirmation"]["min_independent_roles"],
                "min_role_confidence": cfg["veto_confirmation"]["min_role_confidence"]}


_load_common()


def _norm(v):
    return float(v) * 20.0


def _composite(review):
    s = review["scores"]
    return sum(_norm(s[c]) * WEIGHTS[c] for c in CRITERIA) / 100.0


def _median(xs):
    return round(statistics.median(sorted(xs)), 4)


def _arbiter_extra_vetoes(arbiter, confirmed):
    """Arbiter-confirmed vetoes (single-judge, cited evidence) not already role-confirmed.

    Reads untrusted arbiter output: an entry lacking `type` is skipped, never a KeyError."""
    if not arbiter:
        return []
    seen = {c["type"] for c in confirmed}
    extra = []
    for cv in arbiter.get("confirmed_vetoes", []):
        vtype = cv.get("type")
        if not vtype or vtype in seen:
            continue
        seen.add(vtype)
        extra.append({"type": vtype,
                      "confirmed_by": cv.get("confirmed_by", ["arbiter"]),
                      "rationale": "arbiter-confirmed with cited evidence: " + cv.get("rationale", "")})
    return extra


def confirm_vetoes(reviews, arbiter=None):
    """A veto type is confirmed if >=2 independent judge roles raised it with conf>=threshold,
    OR the arbiter confirmed it (single-judge) with cited evidence."""
    by_type = {}
    for r in reviews:
        for v in r.get("vetoes", []):
            if v.get("confidence", 0) >= VETO_CFG["min_role_confidence"]:
                by_type.setdefault(v["type"], set()).add(r["judge_role"])
    confirmed = []
    for vtype, roles in sorted(by_type.items()):
        if len(roles) >= VETO_CFG["min_independent_roles"]:
            confirmed.append({"type": vtype, "confirmed_by": sorted(roles),
                              "rationale": f"{len(roles)} independent roles >= confidence threshold"})
    confirmed += _arbiter_extra_vetoes(arbiter, confirmed)
    return sorted(confirmed, key=lambda c: c["type"])


def _distinct_major_count(reviews):
    """Count DISTINCT MAJOR/CRITICAL findings, collapsing the harness's repeat runs
    (`repeat: 3`): the same defect reported by one judge across runs counts once, so the
    human-facing count reflects distinct issues, not per-observation tallies."""
    seen = set()
    for r in reviews:
        for f in r.get("findings", []):
            if isinstance(f, dict) and f.get("severity") in ("MAJOR", "CRITICAL"):
                seen.add((r.get("judge_role"), f.get("structure"), f.get("side"),
                          f.get("view"), f.get("severity")))
    return len(seen)


def aggregate_region(reviews, region=None, arbiter=None, calibration_ok=True,
                     evidence_integrity_ok=True, partition_status=None):
    if not reviews:
        raise ValueError("no reviews")
    region = region or reviews[0]["region"]
    reviews = sorted(reviews, key=lambda r: (r["judge_role"], r["provider_family"], r["run_id"]))

    criteria = {}
    for c in CRITERIA:
        vals = [_norm(r["scores"][c]) for r in reviews]
        by_role = {}
        by_family = {}
        for r in reviews:
            by_role.setdefault(r["judge_role"], []).append(_norm(r["scores"][c]))
            by_family.setdefault(r["provider_family"], []).append(_norm(r["scores"][c]))
        criteria[c] = {
            "median": _median(vals), "min": round(min(vals), 4), "max": round(max(vals), 4),
            "stddev": round(statistics.pstdev(vals), 4) if len(vals) > 1 else 0.0,
            "by_role_median": {k: _median(v) for k, v in sorted(by_role.items())},
            "by_family_median": {k: _median(v) for k, v in sorted(by_family.items())},
        }

    weighted_score = round(sum(criteria[c]["median"] * WEIGHTS[c] for c in CRITERIA) / 100.0, 2)

    composites = [_composite(r) for r in reviews]
    comp_std = statistics.pstdev(composites) if len(composites) > 1 else 0.0
    verdict_levels = [VERDICT_ORDER.get(r["proposed_verdict"]) for r in reviews
                      if r["proposed_verdict"] in VERDICT_ORDER]
    verdict_spread = (max(verdict_levels) - min(verdict_levels)) if verdict_levels else 0

    if comp_std <= CONSENSUS["high_max_stddev"] and verdict_spread <= 1:
        consensus = "HIGH"
    elif comp_std <= CONSENSUS["medium_max_stddev"] and verdict_spread <= 1:
        consensus = "MEDIUM"
    else:
        consensus = "LOW"

    confirmed = confirm_vetoes(reviews, arbiter)
    major = _distinct_major_count(reviews)
    unresolved_major = major  # at synthetic stage every MAJOR/CRITICAL is unresolved

    if confirmed or (not calibration_ok) or (not evidence_integrity_ok):
        status = "BLOCKED"
    elif weighted_score >= 85 and consensus in ("HIGH", "MEDIUM") and unresolved_major == 0:
        status = "SYNTHETIC_ACCEPTED_INTERNAL"
    elif weighted_score >= 75:
        status = "SYNTHETIC_ACCEPTED_WITH_CONSTRAINTS"
    else:
        status = "REVISION_REQUIRED"
    if unresolved_major > 0 and status in ("SYNTHETIC_ACCEPTED_INTERNAL",):
        status = "REVISION_REQUIRED"
    if consensus == "LOW" and status == "SYNTHETIC_ACCEPTED_INTERNAL":
        status = "SYNTHETIC_ACCEPTED_WITH_CONSTRAINTS"

    # arbiter may only LOWER status
    lowered = False
    if arbiter and arbiter.get("lowered_status"):
        order = ["BLOCKED", "REVISION_REQUIRED", "SYNTHETIC_ACCEPTED_WITH_CONSTRAINTS", "SYNTHETIC_ACCEPTED_INTERNAL"]
        target = arbiter.get("target_status")
        if target in order and order.index(target) < order.index(status):
            status, lowered = target, True

    out = {
        "schema_version": "1.0.0", "region": region,
        "candidate_sha256": reviews[0]["candidate_sha256"],
        "run_mode": "MULTI_FAMILY" if len({r["provider_family"] for r in reviews}) > 1 else "SINGLE_FAMILY_MULTI_AGENT",
        "judge_output_count": len(reviews), "criteria": criteria, "weighted_score": weighted_score,
        "consensus": consensus, "confirmed_vetoes": confirmed, "major_findings_count": major,
        "unresolved_major_findings_count": unresolved_major, "status": status,
        "arbiter": {
            "notes": (arbiter or {}).get("notes", "no arbiter adjustment"),
            "lowered_status": lowered,
            "preserved_disagreements": (arbiter or {}).get("preserved_disagreements", []),
            "requests_martin_adjudication": bool((arbiter or {}).get("requests_martin_adjudication", False)),
        },
    }
    if partition_status is not None:
        out["partition_status"] = partition_status
    return out


def main() -> int:
    reviews = json.loads(pathlib.Path(sys.argv[sys.argv.index("--reviews") + 1]).read_text())
    arbiter = None
    if "--arbiter" in sys.argv:
        arbiter = json.loads(pathlib.Path(sys.argv[sys.argv.index("--arbiter") + 1]).read_text())
    agg = aggregate_region(reviews, arbiter=arbiter)
    print(json.dumps(agg, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
