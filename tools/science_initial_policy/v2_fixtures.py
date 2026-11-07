"""Reproducible v2 outputs; all execution/time observations are synthetic test facts."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

from tools.science_initial_policy.calibration_time_contracts import (
    ContextKey,
    content_digest,
    context_digest,
)
from tools.science_initial_policy.v2_producer import (
    EvaluationRequest,
    EvaluationResult,
    produce_v2,
    verify_evaluation,
)
from tools.science_initial_policy.v2_registry import ROOT, load_v2_registry

DIRECTORY = Path("docs/science/sci-p02-initial-policy/calibration-time-01")
SELECTED = (
    "hack-squat-machine",
    "chest-press-machine",
    "rowing-cable-assis-prise-neutre",
    "romanian-deadlift-barre",
    "tirage-poulie-haute-prise-neutre",
    "elevations-laterales-halteres",
    "calf-press-leg-press",
)


def _source(n=0, observed=False):
    instant = f"2026-11-06T11:{n:02d}:00Z"
    return {
        "origin": "USER_OBSERVED" if observed else "USER_REPORTED",
        "acquisition": "EXECUTION_LOG" if observed else "DECLARED",
        "source_ref": f"SYNTHETIC_NOT_SERVED:event-{n}",
        "recorded_at": instant,
        "measured_at": instant if observed else None,
    }


def _request(bundle, scenario="sufficient"):
    cases = json.loads((ROOT / "docs/science/sci-p01-p02/v1/fixtures.json").read_text())
    req = copy.deepcopy(next(c["request"] for c in cases if c["scenario"] == scenario))
    req["as_of"] = "2026-11-06T12:00:00Z"
    req["versions"].update(
        engine="initial-policy-producer/2.0.0", catalogue=bundle.effective_catalogue_version
    )
    req["policies"].update(state="PROPOSED", review_ref=None)
    env = req["blueprint"]["environment"]
    env.update(
        context_ref="gym:synthetic-a",
        exercise_confirmations=[
            {
                "canonical_exercise_id": identity,
                "context_ref": "gym:synthetic-a",
                "state": "AVAILABLE",
                "provenance": _source(),
            }
            for identity in SELECTED
        ],
    )
    if req["blueprint"]["sessions_per_week"]["state"] == "KNOWN":
        req["blueprint"]["sessions_per_week"]["value"] = 2
        req["blueprint"]["session_budgets_minutes"]["value"] = [75, 75]
    return {
        "contract_version": "initial-plan-evaluation/1.0.0",
        "subject_ref": "subject:synthetic-a",
        "request": req,
        "episodes": [],
        "timing_inputs": [],
        "bundle_digest": bundle.bundle_digest,
        "effective_science_digest": bundle.effective_science_digest,
    }


def _observations(raw, bundle):
    for identity in SELECTED:
        context = ContextKey(
            canonical_exercise_id=identity,
            context_ref="gym:synthetic-a",
            equipment_ref="equipment:synthetic-observed-setting",
            realization_ref=bundle.realization_refs[identity],
            load_semantics="TOTAL_EXTERNAL",
            side="BILATERAL",
        )
        setting = {"kind": "MASS_KG", "value": 40.0, "unit": "kg"}
        events = []
        for n, kind in enumerate(
            (
                "CONTEXT_CONFIRMED",
                "FAMILIARIZATION_CONFIRMED",
                "ATTEMPT_OBSERVED",
                "SETTING_ACCEPTED",
            ),
            1,
        ):
            event = {
                "event_id": f"synthetic:{identity}:e{n}",
                "sequence": n,
                "kind": kind,
                "subject_ref": raw["subject_ref"],
                "context_fingerprint": context_digest(context),
                "provenance": _source(n, observed=kind == "ATTEMPT_OBSERVED"),
            }
            if kind in {"CONTEXT_CONFIRMED", "ATTEMPT_OBSERVED"}:
                event["setting"] = setting
            if kind == "ATTEMPT_OBSERVED":
                event.update(
                    reps=10,
                    completed=True,
                    successful=True,
                    technique="ACCEPTABLE",
                    discomfort="NO_CONCERN",
                )
            if kind == "SETTING_ACCEPTED":
                event["reference_event_id"] = f"synthetic:{identity}:e3"
            events.append(event)
        raw["episodes"].append(
            {
                "episode_id": "synthetic:" + identity,
                "subject_ref": raw["subject_ref"],
                "context": context.model_dump(mode="json"),
                "as_of": raw["request"]["as_of"],
                "started_at": "2026-11-06T11:00:00Z",
                "context_provenance": _source(),
                "availability": "AVAILABLE",
                "ledger_complete": True,
                "ledger_source_ref": "synthetic:complete-event-snapshot",
                "events": events,
            }
        )
    return raw


def _timing(raw, bundle):
    """10s test intervals exercise arithmetic; never a time-policy assumption."""
    for session in produce_v2(raw, bundle)["draft"]["sessions"]:
        s = session["time_session"]
        scope = content_digest({"session": s, "structure": "TRADITIONAL_SEQUENTIAL"})
        rows = [("session/prep", "PREPARATION_CALIBRATION", 0.0)]
        for slot in s["slots"]:
            name, p = slot["slot_id"], slot["prescription"]
            rows.extend(
                (
                    (name + "/prep", "PREPARATION_CALIBRATION", 10.0),
                    (name + "/operations", "SETUP_TRANSITION", 10.0),
                )
            )
            rows.extend((f"{name}/work/{n}", "WORK", 10.0) for n in range(1, p["work_sets"] + 1))
            rows.extend(
                (f"{name}/rest/{n}", "REST", float(p["rest_seconds"]))
                for n in range(1, p["work_sets"])
            )
        raw["timing_inputs"].append(
            {
                "session_id": s["session_id"],
                "subject_ref": raw["subject_ref"],
                "layout": "DISJOINT_SEQUENTIAL",
                "structure": "TRADITIONAL_SEQUENTIAL",
                "components": [
                    {
                        "component_id": f"synthetic:component-{n}",
                        "coverage_key": key,
                        "kind": kind,
                        "lower_seconds": seconds,
                        "upper_seconds": seconds,
                        "basis_ref": "SYNTHETIC_OBSERVATION_NOT_POLICY_CONSTANT",
                        "basis_kind": "EXPERIMENTAL_INTERVAL",
                        "scope_fingerprint": scope,
                        "provenance": _source(1, observed=True),
                    }
                    for n, (key, kind, seconds) in enumerate(rows)
                ],
            }
        )
    return raw


def generated_cases() -> list[dict]:
    bundle = load_v2_registry()
    novice = _request(bundle)
    returning = _timing(_observations(_request(bundle), bundle), bundle)
    unknown = _request(bundle)
    unknown["request"]["blueprint"]["environment"]["exercise_confirmations"] = []
    limited = _request(bundle)
    limited["request"]["blueprint"]["session_budgets_minutes"]["value"] = [1, 1]
    cadence = _request(bundle)
    cadence["request"]["blueprint"]["sessions_per_week"]["value"] = 3
    cadence["request"]["blueprint"]["session_budgets_minutes"]["value"] = [75] * 3
    held = _request(bundle)
    excluded = held["request"]["blueprint"]["excluded_exercise_ids"]
    excluded.update(state="KNOWN", value=["tirage-poulie-haute-prise-neutre"], provenance=_source())
    pending = _observations(_request(bundle), bundle)
    pending["episodes"][3]["events"] = pending["episodes"][3]["events"][:3]
    conflict = _request(bundle)
    conflict["request"]["blueprint"]["environment"]["exercise_confirmations"].append(
        {
            "canonical_exercise_id": SELECTED[0],
            "context_ref": "gym:synthetic-a",
            "state": "UNAVAILABLE",
            "provenance": _source(),
        }
    )
    inputs = [
        ("novice", novice),
        ("returning", returning),
        ("unknown_equipment", unknown),
        ("limited_time", limited),
        ("cadence_3", cadence),
        ("g17_unqualified", copy.deepcopy(novice)),
        ("g17_qualified", copy.deepcopy(returning)),
        ("held_vertical", held),
        ("calibration_pending", pending),
        ("missing_inputs", _request(bundle, "insufficient")),
        ("conflicting_inputs", _request(bundle, "conflicting")),
        ("conflicting_context", conflict),
    ]
    return [
        {
            "scenario": name,
            "fixture_kind": "SYNTHETIC_OBSERVATION_INPUT_REAL_PRODUCER_NOT_SERVED",
            "request": raw,
            "result": verify_evaluation(raw, produce_v2(raw, bundle), bundle),
        }
        for name, raw in inputs
    ]


def _encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode()


def artifacts():
    schema = EvaluationRequest.model_json_schema()
    return {
        "evaluation-request.schema.json": _encoded(schema),
        "evaluation-result.schema.json": _encoded(EvaluationResult.model_json_schema()),
        "producer-fixtures.json": _encoded(generated_cases()),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    files = artifacts()
    manifest = {
        "fixture_version": "initial-plan-evaluation-fixtures/1.0.0",
        "runtime_availability": "NOT_SERVED",
        "sha256": {k: hashlib.sha256(v).hexdigest() for k, v in files.items()},
    }
    files["ARTIFACT_MANIFEST.json"] = _encoded(manifest)
    for name, content in files.items():
        path = ROOT / DIRECTORY / name
        if args.write:
            path.write_bytes(content)
        elif not path.is_file() or path.read_bytes() != content:
            raise SystemExit(f"v2 artifact drift: {name}")
    print(
        "12 actual v2 producer cases and request schema verified; no READY or runtime activation."
    )


if __name__ == "__main__":
    main()
