"""Reproduce the SCI-P02-ADMISSION-01 audit; no admission authority or READY path."""

import argparse
import hashlib
import json
from collections.abc import Mapping

from tools.science_initial_policy import inspect_policy, load_registry
from tools.science_initial_policy.fixtures import generated_cases
from tools.science_initial_policy.registry import POLICY_PATH, POLICY_SHA256, ROOT
from tools.science_initial_policy.time_feasibility import assess_time

OUTPUT = "docs/science/sci-p02-initial-policy/admission-01/audit.json"
DECISIONS = "docs/science/sci-p02-initial-policy/admission-01/policy.json"


def _plain(value):
    if isinstance(value, Mapping):
        return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [_plain(v) for v in value]
    return value


def build_audit() -> dict:
    registry = load_registry()
    cases = generated_cases()
    draft = inspect_policy(cases[0]["request"], registry)
    intents = []
    for slot in draft["sessions"][0]["slots"]:
        candidates = []
        for c in sorted(
            [slot["selected"], *slot["alternatives"]],
            key=lambda item: item["canonical_exercise_id"],
        ):
            record = registry.records[c["canonical_exercise_id"]]
            science, operational = record["exercise_science"], record["exercise_operational"]
            candidates.append(
                {
                    "id": c["canonical_exercise_id"],
                    "pattern": science["movement_pattern"],
                    "joint_type": science["joint_type"],
                    "loaded_joint_actions": list(science["loaded_joint_actions"]),
                    "raw_roles": [dict(r) for r in science["contributions"]],
                    "unknown_role_zones": [
                        r["zone"] for r in science["contributions"] if r["role"] == "UNKNOWN"
                    ],
                    "equipment_requirements": list(operational["equipment_requirements"]),
                    "equipment_requirement_status": operational["equipment_requirement_status"],
                    "unilateral": operational["unilateral"],
                    "stability": "UNKNOWN",  # No curated stability field in this catalogue.
                    "context_compatibility": c["compatibility"],
                    "admitted_for_initial_scope": False,
                }
            )
        intents.append({"intent_id": slot["intent_id"], "candidates": candidates})
    results = []
    for case in cases:
        diagnostics = inspect_policy(case["request"], registry)
        budgets = case["request"]["blueprint"]["session_budgets_minutes"]["value"]
        response = case["response"]
        results.append(
            {
                "scenario": case["scenario"],
                "input_fingerprint": diagnostics["input_fingerprint"],
                "response": {k: response[k] for k in ("status", "confidence", "issues")},
                "sessions_time": [
                    assess_time(s, budgets[i]) for i, s in enumerate(diagnostics["sessions"])
                ],
            }
        )
    return _plain(
        {
            "audit_version": "initial-policy-admission-audit/1.0.0",
            "availability": "NOT_SERVED",
            "ready_fixture": "READY_NOT_PRODUCED",
            "proposed_policy": {"path": POLICY_PATH, "sha256": POLICY_SHA256},
            "decision_artifact_sha256": hashlib.sha256((ROOT / DECISIONS).read_bytes()).hexdigest(),
            "sources": dict(registry.source_hashes),
            "intent_audit": intents,
            "example_zone_exposure": draft["zone_exposure"],
            "cases": results,
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    content = json.dumps(build_audit(), indent=2, ensure_ascii=False) + "\n"
    path = ROOT / OUTPUT
    if args.write:
        path.write_text(content)
    elif path.read_text() != content:
        raise SystemExit("Admission audit differs: regenerate and review")
    print("Admission audit reproduced; no real READY or runtime activation.")


if __name__ == "__main__":
    main()
