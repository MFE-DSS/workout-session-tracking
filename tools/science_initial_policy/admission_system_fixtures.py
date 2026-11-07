"""Real isolated refusal outputs from synthetic facts; no admission or READY authority."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json

from tools.science_initial_policy.admission_registry import DIRECTORY, load_admission_registry
from tools.science_initial_policy.admission_system import AdmissionResult, evaluate_admission
from tools.science_initial_policy.registry import ROOT
from tools.science_initial_policy.v2_fixtures import generated_cases as historical_cases
from tools.science_initial_policy.v2_producer import produce_v2
from tools.science_initial_policy.v2_registry import load_v2_registry

KIND = "SYNTHETIC_INPUT_REAL_ADMISSION_EVALUATOR_NOT_SERVED"


def generated_cases() -> list[dict]:
    bundle, registry = load_v2_registry(), load_admission_registry()
    originals = historical_cases()
    cases = []
    for old in originals:
        cases.append({
            "scenario": old["scenario"], "fixture_kind": KIND,
            "request": old["request"], "historical_result": old["result"],
            "result": evaluate_admission(old["request"], old["result"], bundle, registry),
        })
    returning = next(c for c in originals if c["scenario"] == "returning")
    for name in ("old_history_only", "partial_time_bound"):
        request = copy.deepcopy(returning["request"])
        if name == "old_history_only":
            for ep in request["episodes"]:
                ep["started_at"] = "2026-11-06T11:10:00Z"
        else:
            work = next(c for c in request["timing_inputs"][0]["components"] if c["kind"] == "WORK")
            work.update(lower_seconds=5000.0, upper_seconds=None)
        historical = produce_v2(request, bundle)
        cases.append({
            "scenario": name, "fixture_kind": KIND, "request": request,
            "historical_result": historical,
            "result": evaluate_admission(request, historical, bundle, registry),
        })
    for name in ("boolean_as_number", "integer_as_float", "wrong_subject", "stale_engine"):
        case = copy.deepcopy(next(c for c in originals if c["scenario"] == "novice"))
        if name == "boolean_as_number":
            case["result"]["draft"]["executable"] = 0
        elif name == "integer_as_float":
            case["result"]["draft"]["physical_work_sets_total"] = 28.0
        elif name == "wrong_subject":
            case["request"]["subject_ref"] = "subject:synthetic-other"
        else:
            case["request"]["request"]["versions"]["engine"] = "initial-policy-producer/unknown"
        try:
            evaluate_admission(case["request"], case["result"], bundle, registry)
        except ValueError:
            cases.append({
                "scenario": name, "fixture_kind": KIND, "request": case["request"],
                "historical_result": case["result"], "rejection": {"code": "INVALID_EVALUATION"},
            })
        else:
            raise ValueError(f"invalid evaluation unexpectedly accepted: {name}")
    return cases


def _encoded(value) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode()


def artifacts() -> dict[str, bytes]:
    files = {
        "admission-result.v1.schema.json": _encoded(AdmissionResult.model_json_schema()),
        "producer-fixtures.v1.json": _encoded(generated_cases()),
    }
    pins = json.loads((ROOT / DIRECTORY / "registry-manifest.v1.json").read_text())["sha256"]
    # The versioned loader is the trust bootstrap, outside its own source-pin
    # digest to avoid a self-referential hash. Record it here for code audit.
    code = dict(pins)
    for name in ("admission_registry.py", "admission_system_fixtures.py"):
        path = "tools/science_initial_policy/" + name
        code[path] = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
    files["ARTIFACT_MANIFEST.json"] = _encoded({
        "fixture_version": "initial-policy-admission-fixtures/1.0.0",
        "scientific_admission": "NOT_ADMITTED", "runtime_availability": "NOT_SERVED",
        "implementation_sha256": code,
        "sha256": {**{n: hashlib.sha256(v).hexdigest() for n, v in files.items()}, **{
            n: hashlib.sha256((ROOT / DIRECTORY / n).read_bytes()).hexdigest()
            for n in ("registry.v1.json", "registry-manifest.v1.json")
        }},
    })
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    for name, content in artifacts().items():
        path = ROOT / DIRECTORY / name
        if args.write:
            path.write_bytes(content)
        elif not path.is_file() or path.read_bytes() != content:
            raise SystemExit(f"admission artifact drift: {name}")
    print("18 isolated refusal/rejection fixtures verified; NOT_ADMITTED/NOT_SERVED; no READY.")


if __name__ == "__main__":
    main()
