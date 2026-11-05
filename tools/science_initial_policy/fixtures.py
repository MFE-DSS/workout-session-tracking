"""Regenerate actual producer outputs from synthetic, non-served contract inputs."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from tools.science_initial_policy import ENGINE_VERSION, inspect_policy, load_registry, produce
from tools.science_initial_policy.registry import ROOT

OUTPUT = Path("docs/science/sci-p02-initial-policy/v1/producer-fixtures.json")


def generated_cases() -> list[dict]:
    registry = load_registry()
    source = json.loads((ROOT / "docs/science/sci-p01-p02/v1/fixtures.json").read_text())
    inputs = [(case["scenario"], copy.deepcopy(case["request"])) for case in source]
    for _, req in inputs:
        req["versions"]["engine"] = ENGINE_VERSION
    confirmed = copy.deepcopy(inputs[0][1])
    env = confirmed["blueprint"]["environment"]
    first = inspect_policy(confirmed, registry)
    identities = {
        slot["selected"]["canonical_exercise_id"]
        for session in first["sessions"]
        for slot in session["slots"]
        if slot["selected"]
    }
    env["exercise_confirmations"] = [
        {
            "canonical_exercise_id": identity,
            "context_ref": env["context_ref"],
            "state": "AVAILABLE",
            "provenance": copy.deepcopy(confirmed["blueprint"]["sessions_per_week"]["provenance"]),
        }
        for identity in sorted(identities)
    ]
    inputs.append(("confirmed_exercises_no_inventory", confirmed))
    forged = copy.deepcopy(inputs[0][1])
    forged["policies"].update(
        state="APPROVED",
        review_ref="untrusted-client-approval",
        dose_id="unadmitted",
        time_id="unadmitted",
        selection_id="unadmitted",
        taxonomy_projection_id="unadmitted",
    )
    inputs.append(("forged_policy_approval", forged))
    one = copy.deepcopy(inputs[0][1])
    one["blueprint"]["sessions_per_week"]["value"] = 1
    one["blueprint"]["session_budgets_minutes"]["value"] = [75]
    inputs.append(("known_cadence_outside_initial_subset", one))
    return [
        {
            "scenario": name,
            "availability": "NOT_SERVED",
            "input_authority": "SYNTHETIC_INPUT_ACTUAL_PRODUCER_OUTPUT",
            "request": req,
            "response": produce(req, registry).model_dump(mode="json"),
        }
        for name, req in inputs
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write", action="store_true", help="Regenerate the dedicated fixture artifact"
    )
    args = parser.parse_args()
    content = json.dumps(generated_cases(), indent=2, ensure_ascii=False) + "\n"
    target = ROOT / OUTPUT
    if args.write:
        target.write_text(content)
    elif not target.is_file() or target.read_text() != content:
        raise SystemExit("Producer fixtures differ: regenerate and review")
    print("11 actual producer fixtures verified; no READY or runtime activation.")


if __name__ == "__main__":
    main()
