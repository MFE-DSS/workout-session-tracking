"""Regression tests for the Auren Muscle Focus synthetic multimodel review harness — GO C2 §15.

Fixture data only (frozen synthetic judge outputs) — never real model outputs. Verifies the schema
validator, the pure deterministic aggregation, calibration thresholds, veto/arbiter governance, and
the in-repo governance invariants (no candidate binaries, no external package, no credential fields).
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

HARNESS = pathlib.Path(__file__).resolve().parent.parent / "tools/evals/muscle_focus"
sys.path.insert(0, str(HARNESS / "scripts"))

import aggregate_reviews as A  # noqa: E402
import validate_agent_output as V  # noqa: E402

SHA = {"chest": "7a4167eac1db085f1cfb41ae2b2465a3b2c720a4978361eef69e422b104bddfd",
       "shoulders": "5eb7bedfa031b2e9fe29e60c1a17c1fe2822a46c0a3153f2fab14951fcc94983",
       "posterior": "b84c8bceea47455c88d4ee2d3117a6387383187109a20850db2d54feaa71710f"}
ROLES = ["J1_anatomy_consistency", "J2_medical_illustration", "J3_fitness_semantics",
         "J4_adversarial_falsifier", "J5_provenance_governance"]


def review(role, region="shoulders", score=4, verdict="ACCEPT", vetoes=None, findings=None,
           family="claude", run="r1", conf=0.85):
    scores = {c: score for c in A.CRITERIA} if isinstance(score, int) else dict(score)
    return {"schema_version": "1.0.0", "region": region, "candidate_sha256": SHA[region],
            "judge_role": role, "provider_family": family, "model_id": "claude-opus-4-8",
            "run_id": f"{region}-{role}-{run}", "evidence_files_reviewed": ["02_PREVIEWS/x.png"],
            "scores": scores, "findings": findings or [], "vetoes": vetoes or [],
            "confidence": conf, "proposed_verdict": verdict}


def council(region="shoulders", score=4, verdict="ACCEPT", runs=3, **kw):
    return [review(r, region=region, score=score, verdict=verdict, run=f"r{i}", **kw)
            for r in ROLES for i in range(1, runs + 1)]


def veto(vtype, conf=0.9):
    return {"type": vtype, "rationale": "x", "confidence": conf, "evidence": "file:y"}


def finding(sev="MAJOR"):
    return {"severity": sev, "structure": "deltoid", "side": "left", "view": "front",
            "evidence": "f", "rationale": "r", "proposed_action": "a", "confidence": 0.8}


# ---- schema / validator ----

def test_five_judge_roles_exist():
    assert V.ROLES == set(ROLES) and len(V.ROLES) == 5


def test_schema_rejects_missing_evidence():
    r = review("J1_anatomy_consistency")
    r["evidence_files_reviewed"] = []
    assert any("evidence" in e for e in V.validate_agent_review(r))


def test_scores_out_of_range_rejected():
    r = review("J1_anatomy_consistency")
    r["scores"]["orientation_and_laterality"] = 6
    assert any("out of range" in e for e in V.validate_agent_review(r))
    r2 = review("J1_anatomy_consistency")
    r2["scores"]["mobile_readability"] = -1
    assert any("out of range" in e for e in V.validate_agent_review(r2))


def test_unknown_verdict_rejected():
    r = review("J1_anatomy_consistency")
    r["proposed_verdict"] = "MAYBE"
    assert any("proposed_verdict" in e for e in V.validate_agent_review(r))


def test_valid_review_passes():
    assert V.validate_agent_review(review("J5_provenance_governance")) == []


def test_no_credential_field_in_schemas():
    for name in ("agent_review.schema.json", "aggregate_review.schema.json"):
        txt = (HARNESS / "schemas" / name).read_text().lower()
        for bad in ("api_key", "apikey", "credential", "secret", "token", "password"):
            assert bad not in txt, f"{bad} in {name}"


# ---- aggregation ----

def test_weights_total_100():
    assert sum(A.WEIGHTS.values()) == 100


def test_aggregation_order_independent():
    revs = council(score=4)
    a1 = A.aggregate_region(list(revs))
    a2 = A.aggregate_region(list(reversed(revs)))
    a3 = A.aggregate_region([revs[i] for i in (7, 0, 14, 3, 9, 1, 12, 2, 5, 11, 4, 8, 13, 6, 10)])
    assert json.dumps(a1, sort_keys=True) == json.dumps(a2, sort_keys=True) == json.dumps(a3, sort_keys=True)


def test_high_scores_accept_internal():
    a = A.aggregate_region(council(score=5, verdict="ACCEPT"))
    assert a["weighted_score"] == 100.0
    assert a["status"] == "SYNTHETIC_ACCEPTED_INTERNAL"
    assert a["consensus"] == "HIGH"


def test_low_scores_revision_required():
    a = A.aggregate_region(council(score=2, verdict="REVISION_REQUIRED"))
    assert a["weighted_score"] < 75
    assert a["status"] == "REVISION_REQUIRED"


def test_confirmed_veto_blocks_even_with_high_scores():
    revs = council(score=5, verdict="ACCEPT")
    # two independent roles raise the same veto at high confidence
    revs[0]["vetoes"] = [veto("mirror_or_laterality_inversion", 0.95)]   # J1 r1
    revs[9]["vetoes"] = [veto("mirror_or_laterality_inversion", 0.9)]    # J4 r1
    a = A.aggregate_region(revs)
    assert len(a["confirmed_vetoes"]) == 1
    assert a["status"] == "BLOCKED"


def test_single_judge_cannot_confirm_veto():
    revs = council(score=5, verdict="ACCEPT")
    revs[0]["vetoes"] = [veto("source_provenance_lost", 0.99)]  # only one role
    a = A.aggregate_region(revs)
    assert a["confirmed_vetoes"] == []
    assert a["status"] != "BLOCKED"


def test_arbiter_single_confirm_with_evidence():
    revs = council(score=5, verdict="ACCEPT")
    revs[0]["vetoes"] = [veto("false_professional_approval_claim", 0.99)]
    arb = {"confirmed_vetoes": [{"type": "false_professional_approval_claim",
                                 "confirmed_by": ["J5", "arbiter"], "rationale": "cited evidence"}],
           "lowered_status": False}
    a = A.aggregate_region(revs, arbiter=arb)
    assert any(v["type"] == "false_professional_approval_claim" for v in a["confirmed_vetoes"])
    assert a["status"] == "BLOCKED"


def test_arbiter_cannot_raise_score_or_status():
    revs = council(score=3, verdict="REVISION_REQUIRED")  # ~60, revision
    base = A.aggregate_region(revs)
    arb = {"lowered_status": True, "target_status": "SYNTHETIC_ACCEPTED_INTERNAL", "notes": "x"}
    a = A.aggregate_region(revs, arbiter=arb)
    assert a["weighted_score"] == base["weighted_score"]      # score never changes
    assert a["status"] == base["status"]                       # cannot be raised
    assert A.VERDICT_ORDER.get("ACCEPT", 4) > A.VERDICT_ORDER.get("REVISION_REQUIRED")


def test_arbiter_can_lower_status():
    revs = council(score=5, verdict="ACCEPT")
    arb = {"lowered_status": True, "target_status": "REVISION_REQUIRED", "notes": "reservation"}
    a = A.aggregate_region(revs, arbiter=arb)
    assert a["status"] == "REVISION_REQUIRED"
    assert a["arbiter"]["lowered_status"] is True


def test_calibration_failure_blocks():
    a = A.aggregate_region(council(score=5, verdict="ACCEPT"), calibration_ok=False)
    assert a["status"] == "BLOCKED"


def test_chest_partition_cannot_be_accepted():
    a = A.aggregate_region(council(region="chest", score=5, verdict="ACCEPT"),
                           partition_status="REVIEW_PARTITION_UNRESOLVED / NOT ACCEPTED")
    assert a["partition_status"] == "REVIEW_PARTITION_UNRESOLVED / NOT ACCEPTED"
    assert A.partition_accepted(a) is False


# ---- calibration thresholds ----

def test_calibration_thresholds_enforced():
    cases = [{"case_id": f"c{i}", "is_critical": i < 6} for i in range(12)]  # 6 critical
    all_det = {c["case_id"]: True for c in cases}
    assert A.calibration_result(cases, all_det)["result"] == "PASS"
    # one critical missed -> FAIL
    miss_crit = dict(all_det)
    miss_crit["c0"] = False
    assert A.calibration_result(cases, miss_crit)["result"] == "FAILED"
    # 2 non-critical missed -> 10/12 = 0.83 < 0.90 -> FAIL
    miss_two = dict(all_det)
    miss_two["c6"] = False
    miss_two["c7"] = False
    assert A.calibration_result(cases, miss_two)["result"] == "FAILED"


# ---- governance invariants ----

def test_governance_constants():
    g = A.GOVERNANCE
    assert g["professional_anatomical_review"] == "NOT_PERFORMED_NOT_CLAIMED"
    assert g["runtime"] == "BLOCKED"
    assert g["asset_intake"] == "NOT_STARTED"
    assert g["section_5bis"] == "NOT_ENACTED"
    assert "NOT ACCEPTED" in g["chest_partition"]


def test_no_candidate_binaries_in_git():
    bad = [p for p in HARNESS.rglob("*") if p.suffix.lower() in (".svg", ".png", ".jpg", ".obj", ".zip", ".pbm")]
    assert bad == [], f"binary artifacts committed: {bad}"


def test_external_review_package_not_in_repo():
    repo = pathlib.Path(__file__).resolve().parent.parent
    assert not (repo / "07_external_review").exists()
    assert not list(repo.rglob("AUREN_Sb_ASSET_03B_2R_QUALIFIED_ANATOMICAL_REVIEW.zip"))


def test_no_credentials_serialized_in_harness():
    # Match a realistic key BODY (prefix + token chars), so credential-detection needles like the bare
    # string "sk-ant-" inside the scanner scripts do not false-positive.
    key_re = re.compile(r"sk-(ant|proj)-[a-z0-9_-]{16,}")
    for p in HARNESS.rglob("*"):
        if p.is_file() and p.suffix in (".py", ".yaml", ".yml", ".json", ".md"):
            assert not key_re.search(p.read_text(errors="ignore").lower()), f"key-like token in {p}"
