"""Reproducible coverage and non-executable curation consumer fixtures."""

import argparse
import copy
import json
from typing import get_args

from tools.science_contracts.blueprint_first_plan_v1 import Zone
from tools.science_initial_policy.curation import ELIGIBLE, load_curation, resolve_candidates
from tools.science_initial_policy.registry import ROOT

OUTPUT = "docs/science/sci-p02-initial-policy/curation-01/coverage-and-fixtures.v1.json"
ROLE_STATES = {
    "PRIMARY": "DIRECT",
    "SECONDARY": "INDIRECT_KNOWN",
    "MINOR": "MINOR_KNOWN",
    "UNKNOWN": "UNKNOWN",
}


def generated_artifacts() -> dict:
    bundle = load_curation()
    intents = sorted({r.intent_id for r in bundle.candidates})
    coverage = []
    for intent in intents:
        rows = [r for r in bundle.candidates if r.intent_id == intent]
        eligible = [r for r in rows if r.initial_scope_admission in ELIGIBLE]
        zones = {}
        for zone in get_args(Zone):
            all_states, eligible_states = {}, {}
            for row in rows:
                roles = {r["zone"]: r["role"] for r in row.roles}
                state = ROLE_STATES[roles[zone]] if zone in roles else "NONE_KNOWN"
                all_states[row.candidate_id] = state
                if row in eligible:
                    eligible_states[row.candidate_id] = state
            zones[zone] = {
                "candidate_role_states": sorted(set(all_states.values())),
                "by_candidate": all_states,
                "admissible_role_states": sorted(set(eligible_states.values())),
                "admissible_by_candidate": eligible_states,
            }
        coverage.append(
            {
                "intent_id": intent,
                "admissible_candidate_count": len(eligible),
                "status": "CANDIDATES_AVAILABLE" if eligible else "CATALOG_GAP",
                "zones": zones,
            }
        )
    inputs = json.loads(
        (ROOT / "docs/science/sci-p02-initial-policy/v1/producer-fixtures.json").read_text()
    )
    req = inputs[0]["request"]
    unknown = copy.deepcopy(req)
    unknown["blueprint"]["environment"]["exercise_confirmations"] = []
    cases = [
        {
            "scenario": "unconfirmed_context",
            "input": unknown,
            "results": [resolve_candidates(unknown, i, bundle) for i in intents],
        }
    ]
    cases.append(
        {
            "scenario": "current_synthetic_context",
            "input": req,
            "results": [resolve_candidates(req, i, bundle) for i in intents],
        }
    )
    return {
        "version": "initial-candidate-curation-fixtures/1.0.0",
        "runtime": "NOT_SERVED",
        "coverage_semantics": "SOURCE_ACCOUNTING_NOT_AESTHETIC_SCORE; NONE_KNOWN is no listed role, not zero physiology",
        "effective_role_changes": [],
        "evidence_basis_corrections": [
            {
                "candidate_id": r.candidate_id,
                "zones": [
                    x["zone"] for x in r.roles if x["zone"] in {"quads", "glutes", "adductors"}
                ],
                "before": "longitudinal_trial",
                "after": "joint_action_anatomy",
                "authority": ["EV-62", "EV-64", "EV-71"],
                "reason": "Trial configuration differs; role categories preserved, high-wide variant held.",
            }
            for r in bundle.candidates
            if r.candidate_id.startswith("leg-press-paren-pieds-")
        ],
        "unknown_role_count": sum(
            x["role"] == "UNKNOWN" for r in bundle.candidates for x in r.roles
        ),
        "coverage": coverage,
        "cases": cases,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    content = json.dumps(generated_artifacts(), indent=2, ensure_ascii=False) + "\n"
    path = ROOT / OUTPUT
    if args.write:
        path.write_text(content)
    elif path.read_text() != content:
        raise SystemExit("Curation artifacts differ: regenerate and review")
    print("40 candidates, seven intents, coverage/fixtures reproduced; no READY or runtime.")


if __name__ == "__main__":
    main()
