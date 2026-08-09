#!/usr/bin/env python3
"""Ingest council outputs -> runs/ + results/ + calibration scoring + deterministic aggregation.
GO C2 §10/§11. Consumes a JSON file holding {council:[...], calibration:[...], arbiters:[...]} produced
by the promptfoo run or the Claude Code subagent council. Deterministic; no network; no credentials.

Reads AUREN_MUSCLE_FOCUS_REVIEW_ROOT. Writes under <ROOT>/08_synthetic_review/.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import aggregate_reviews as A  # noqa: E402
import validate_agent_output as V  # noqa: E402

ROOT = pathlib.Path(os.environ["AUREN_MUSCLE_FOCUS_REVIEW_ROOT"])
SYN = ROOT / "08_synthetic_review"
RUNS = SYN / "runs"
RES = SYN / "results"
REGIONS = ["chest", "shoulders", "posterior"]
PARTITION = "REVIEW_PARTITION_UNRESOLVED / NOT ACCEPTED"


def _hash(s):
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def persist_run(rec, kind):
    rid = rec.get("run_id") or f"{kind}-{_hash(json.dumps(rec, sort_keys=True))}"
    d = RUNS / rid
    d.mkdir(parents=True, exist_ok=True)
    errs = V.validate_agent_review(rec)
    (d / "meta.json").write_text(json.dumps({
        "run_id": rid, "kind": kind, "provider_family": rec.get("provider_family"),
        "model_id": rec.get("model_id"), "region": rec.get("region"), "judge_role": rec.get("judge_role"),
        "prompt_ref": f"prompts/{rec.get('judge_role','')}", "candidate_sha256": rec.get("candidate_sha256"),
        "output_sha256": hashlib.sha256(json.dumps(rec, sort_keys=True).encode()).hexdigest(),
        "schema_valid": not errs, "validation_errors": errs, "credentials": "none-recorded",
    }, indent=2) + "\n")
    (d / "parsed.json").write_text(json.dumps(rec, indent=2) + "\n")
    return not errs


def score_calibration(calibration):
    manifest = json.loads((SYN / "calibration/manifest.json").read_text())
    cases = {c["case_id"]: c for c in manifest["cases"]}
    by_case = {}
    for item in calibration:
        by_case.setdefault(item["case_id"], []).append(item["output"])
    detections = {}
    details = []
    for cid, meta in cases.items():
        outs = by_case.get(cid, [])
        want_veto = set(meta["expected_veto_types"])
        kws = [k.lower() for k in meta["expected_keywords"]]
        detected = False
        why = []
        for o in outs:
            for v in o.get("vetoes", []):
                if v.get("type") in want_veto:
                    detected = True
                    why.append(f"{o.get('judge_role')}:veto:{v['type']}")
            for f in o.get("findings", []):
                if f.get("severity") in ("MAJOR", "CRITICAL"):
                    txt = (f.get("rationale", "") + " " + f.get("evidence", "") + " " + f.get("structure", "")).lower()
                    if any(k in txt for k in kws):
                        detected = True
                        why.append(f"{o.get('judge_role')}:finding:{f['severity']}")
        detections[cid] = detected
        details.append({"case_id": cid, "is_critical": meta["is_critical"], "detected": detected,
                        "signals": sorted(set(why)), "targets_run": [o.get("judge_role") for o in outs]})
    result = A.calibration_result(list(cases.values()), detections)
    result["cases"] = details
    return result


def main() -> int:
    data = json.loads(pathlib.Path(sys.argv[sys.argv.index("--results") + 1]).read_text())
    council = data.get("council", [])
    calibration = data.get("calibration", [])
    arbiters = {a["region"]: a for a in data.get("arbiters", []) if a}

    RUNS.mkdir(parents=True, exist_ok=True)
    RES.mkdir(parents=True, exist_ok=True)
    valid = sum(persist_run(r, "council") for r in council)
    for item in calibration:
        persist_run(item["output"], "calibration")

    (RES / "synthetic_review_raw_results.json").write_text(json.dumps(
        {"_schema": "raw council results", "run_mode": "SINGLE_FAMILY_MULTI_AGENT",
         "council_count": len(council), "valid_count": valid, "outputs": council}, indent=2) + "\n")

    calib = score_calibration(calibration)
    (SYN / "calibration/calibration_results.json").write_text(json.dumps(calib, indent=2) + "\n")

    calib_ok = calib["result"] == "PASS"
    agg = {}
    for region in REGIONS:
        revs = [o for o in council if o.get("region") == region]
        arb = arbiters.get(region)
        agg[region] = A.aggregate_region(
            revs, region=region, arbiter=arb, calibration_ok=calib_ok,
            partition_status=PARTITION if region == "chest" else None)
    (RES / "synthetic_review_aggregate.json").write_text(json.dumps(agg, indent=2, sort_keys=True) + "\n")

    print(f"ingested council={len(council)} (valid {valid}) calibration={len(calibration)} arbiters={len(arbiters)}")
    print(f"calibration: critical {calib['critical_detected']}/{calib['critical_total']} "
          f"overall {calib['overall_detected']}/{calib['overall_total']} -> {calib['result']}")
    for region in REGIONS:
        a = agg[region]
        print(f"  {region:10} score={a['weighted_score']:6} consensus={a['consensus']:7} "
              f"status={a['status']:34} vetoes={len(a['confirmed_vetoes'])} major={a['major_findings_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
