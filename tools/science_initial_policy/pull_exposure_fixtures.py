"""Reproduce non-served vertical-pull diagnostics; no prescription or READY fixture."""

import argparse
import copy
import json

from tools.science_initial_policy.pull_exposure import load_pull_exposure, resolve_vertical_pull
from tools.science_initial_policy.registry import ROOT

OUTPUT = "docs/science/sci-p02-initial-policy/pull-exposure-01/fixtures.v1.json"
NEUTRAL = "tirage-poulie-haute-prise-neutre"


def generated_cases() -> list[dict]:
    seed = json.loads(
        (ROOT / "docs/science/sci-p02-initial-policy/v1/producer-fixtures.json").read_text()
    )[0]["request"]
    bundle = load_pull_exposure()
    unknown = copy.deepcopy(seed)
    unknown["blueprint"]["environment"]["exercise_confirmations"] = []
    available = copy.deepcopy(unknown)
    fact = available["blueprint"]["sessions_per_week"]["provenance"]
    env = available["blueprint"]["environment"]
    confirmation = {
        "canonical_exercise_id": NEUTRAL,
        "context_ref": env["context_ref"],
        "state": "AVAILABLE",
        "provenance": copy.deepcopy(fact),
    }
    env["exercise_confirmations"] = [confirmation]
    unavailable = copy.deepcopy(available)
    unavailable["blueprint"]["environment"]["exercise_confirmations"][0]["state"] = "UNAVAILABLE"
    conflict = copy.deepcopy(available)
    for state in ("UNAVAILABLE", "UNKNOWN"):
        c = copy.deepcopy(confirmation)
        c["state"] = state
        conflict["blueprint"]["environment"]["exercise_confirmations"].append(c)
    excluded = copy.deepcopy(available)
    excluded["blueprint"]["excluded_exercise_ids"].update(
        state="KNOWN", value=[NEUTRAL], conflicts=[], provenance=copy.deepcopy(fact)
    )
    limited = copy.deepcopy(available)
    limited["blueprint"]["limitations"]["value"] = ["reported discomfort"]
    missing = copy.deepcopy(unknown)
    p = missing["blueprint"]["limitations"]
    p.update(state="UNKNOWN", value=None, conflicts=[])
    p["provenance"].update(
        origin="UNKNOWN", acquisition="UNKNOWN", source_ref=None, recorded_at=None, measured_at=None
    )
    return [
        {
            "case_id": name,
            "fixture_role": "SYNTHETIC_INPUT_NON_SERVED_DIAGNOSTIC",
            "request": req,
            "result": resolve_vertical_pull(req, bundle),
        }
        for name, req in [
            ("unconfirmed_context", unknown),
            ("equipment_available_execution_not_observed", available),
            ("equipment_unavailable", unavailable),
            ("three_state_context_conflict", conflict),
            ("explicit_exclusion_no_fallback", excluded),
            ("reported_limitation_review", limited),
            ("missing_required_context", missing),
        ]
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    content = json.dumps(generated_cases(), indent=2, ensure_ascii=False) + "\n"
    path = ROOT / OUTPUT
    if args.write:
        path.write_text(content)
    elif path.read_text() != content:
        raise SystemExit("Pull diagnostics differ; regenerate and review")
    print("Seven non-served diagnostics reproduced; no READY, credit or execution certification.")


if __name__ == "__main__":
    main()
