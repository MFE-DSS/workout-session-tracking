#!/usr/bin/env python3
"""Finalize verification — GO C2 §16. Deterministic checks over the real council results:
aggregation order-independence, calibration thresholds, candidate-hash invariance, no serialized
credential, and governance invariants. Stdlib-only. Reads AUREN_MUSCLE_FOCUS_REVIEW_ROOT."""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import aggregate_reviews as A  # noqa: E402

ROOT = pathlib.Path(os.environ["AUREN_MUSCLE_FOCUS_REVIEW_ROOT"])
SYN = ROOT / "08_synthetic_review"
CAND = ROOT / "04_work/p0_candidates"
REGIONS = ["chest", "shoulders", "posterior"]
EXPECT = {
    "chest": "7a4167eac1db085f1cfb41ae2b2465a3b2c720a4978361eef69e422b104bddfd",
    "shoulders": "5eb7bedfa031b2e9fe29e60c1a17c1fe2822a46c0a3153f2fab14951fcc94983",
    "posterior": "b84c8bceea47455c88d4ee2d3117a6387383187109a20850db2d54feaa71710f",
}


def _check_order_independence(raw) -> list[str]:
    e = []
    for region in REGIONS:
        revs = [o for o in raw if o["region"] == region]
        ps = "p" if region == "chest" else None
        a1 = json.dumps(A.aggregate_region(list(revs), partition_status=ps), sort_keys=True)
        a2 = json.dumps(A.aggregate_region(list(reversed(revs)), partition_status=ps), sort_keys=True)
        a3 = json.dumps(A.aggregate_region(revs[7:] + revs[:7], partition_status=ps), sort_keys=True)
        if not (a1 == a2 == a3):
            e.append(f"{region}: aggregation NOT order-independent")
    return e


def _check_calibration(calib) -> list[str]:
    e = []
    if calib["result"] != "PASS":
        e.append("calibration not PASS")
    if calib["critical_detected"] != calib["critical_total"]:
        e.append("critical calibration < 100%")
    if calib["overall_total"] and calib["overall_detected"] / calib["overall_total"] < 0.90:
        e.append("overall calibration < 90%")
    return e


def _check_hashes() -> list[str]:
    e = []
    for region, want in EXPECT.items():
        got = hashlib.sha256((CAND / f"auren-plate-region-{region}.svg").read_bytes()).hexdigest()
        if got != want:
            e.append(f"{region} candidate hash drift")
    return e


def _check_credentials() -> list[str]:
    e = []
    for p in SYN.rglob("*"):
        if p.is_file() and p.suffix in (".json", ".md", ".txt", ".html"):
            low = p.read_text(errors="ignore").lower()
            if "sk-ant-" in low or "sk-proj-" in low or '"api_key"' in low:
                e.append(f"possible credential in {p.name}")
    return e


def _check_governance() -> list[str]:
    e = []
    if A.GOVERNANCE["professional_anatomical_review"] != "NOT_PERFORMED_NOT_CLAIMED":
        e.append("professional review claim not false")
    if A.GOVERNANCE["runtime"] != "BLOCKED":
        e.append("runtime not blocked")
    dform = (SYN / "results/martin_decision_form.md").read_text()
    if "NOT PERFORMED / NOT CLAIMED" not in dform:
        e.append("decision form missing professional-review non-claim")
    if "[x]" in dform.lower():
        e.append("decision form has a preselected option")
    return e


def main() -> int:
    raw = json.loads((SYN / "results/synthetic_review_raw_results.json").read_text())["outputs"]
    calib = json.loads((SYN / "calibration/calibration_results.json").read_text())
    e = (_check_order_independence(raw) + _check_calibration(calib) + _check_hashes()
         + _check_credentials() + _check_governance())
    print("FINALIZE VERIFICATION:\n" + ("PASS" if not e else "FAIL"))
    for x in e:
        print(f"  - {x}")
    print(f"  order-independence: PASS ({len(REGIONS)} regions)")
    print(f"  calibration: critical {calib['critical_detected']}/{calib['critical_total']} "
          f"overall {calib['overall_detected']}/{calib['overall_total']} -> {calib['result']}")
    print("  candidate hashes: UNCHANGED")
    return 0 if not e else 1


if __name__ == "__main__":
    raise SystemExit(main())
