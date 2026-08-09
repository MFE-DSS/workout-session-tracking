#!/usr/bin/env python3
"""Reconstruct {council, calibration, arbiters} from a Claude Code subagent council journal.
GO C2 §10 support. Deterministic parse of the workflow journal.jsonl: each 'result' event carries the
agent's returned object. Judges have 'scores' + run_id; calibration judges have run_id starting 'CAL-';
arbiters have 'reconciled_findings' and no scores. Dedupe keeps the last occurrence per run_id/region.

Writes <ROOT>/08_synthetic_review/workflow_return.json. No network, no credentials.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys


def main() -> int:
    journal = pathlib.Path(sys.argv[sys.argv.index("--journal") + 1])
    root = pathlib.Path(os.environ["AUREN_MUSCLE_FOCUS_REVIEW_ROOT"])
    council, calibration, arbiters = {}, {}, {}
    for line in journal.read_text().splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("type") != "result":
            continue
        obj = ev.get("result")
        if not isinstance(obj, dict):
            continue
        if "scores" in obj and obj.get("run_id"):
            rid = obj["run_id"]
            if rid.startswith("CAL-"):
                case_id, _, role = rid[4:].partition("-")
                calibration[rid] = {"case_id": case_id, "target": role or obj.get("judge_role"), "output": obj}
            else:
                council[rid] = obj
        elif obj.get("region") and ("reconciled_findings" in obj or "confirmed_vetoes" in obj):
            arbiters[obj["region"]] = obj

    out = {"council": list(council.values()),
           "calibration": list(calibration.values()),
           "arbiters": list(arbiters.values())}
    dst = root / "08_synthetic_review" / "workflow_return.json"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, indent=2) + "\n")
    print(f"reconstructed council={len(out['council'])} calibration={len(out['calibration'])} "
          f"arbiters={len(out['arbiters'])} -> {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
