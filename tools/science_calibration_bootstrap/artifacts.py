"""Explicit artifact generation, never imported by a runtime or authority loader."""

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def synthetic_plan_input(root=ROOT):
    value = json.loads(
        (root / "docs/science/sci-p02-initial-policy/stage2-v3/SYNTHETIC_INPUT.json").read_text()
    )
    # Construct a NEW request against the current published authority; never
    # rewrite the historical synthetic source or its coordination fingerprints.
    from tools.science_initial_policy.v3_admission import load_v3_registry

    r = load_v3_registry(root)
    value.update(
        bundle_digest=r.bundle_digest,
        effective_science_digest=r.effective_science_digest,
        requested_binding_ref=r.binding_ref,
    )
    value["versions"].update(
        engine=r.policy["engine_version"],
        policy=r.policy["policy_version"],
        catalogue=r.historical.effective_catalogue_version,
    )
    return value


def synthetic_encounter(*, stage="qualified", root=ROOT):
    plan = synthetic_plan_input(root)
    ep = copy.deepcopy(plan["episodes"][0])
    p = copy.deepcopy(ep["context_provenance"])
    ctx = ep["context"]
    from tools.science_initial_policy.calibration_time_contracts import ContextKey, context_digest

    ctx_hash = context_digest(ContextKey.model_validate(ctx))
    raw = dict(
        contract_version="first-calibration-encounter/1.0.0",
        encounter_ref="synthetic:encounter-a",
        subject_ref=ep["subject_ref"],
        source_revision="synthetic:source/1",
        started_at=ep["started_at"],
        as_of=ep["as_of"],
        population=plan["blueprint"]["population_scope"],
        limitations=plan["blueprint"]["limitations"],
        context=ctx,
        context_provenance=p,
        availability="AVAILABLE",
        ledger_complete=True,
        ledger_source_ref="synthetic:owner-complete-ledger",
        concern_state="CLEAR",
        withdrawn=False,
        episode=ep,
        preparation=dict(
            context_fingerprint=ctx_hash,
            instruction_ref="synthetic:device-instructions",
            setup_ref="synthetic:seat-axis-pad-fit",
            understood=True,
            controlled=True,
            provenance=p,
        ),
        setting_choice=dict(
            context_fingerprint=ctx_hash,
            setting=ep["events"][0]["setting"],
            available=True,
            provenance=ep["events"][0]["provenance"],
        ),
        stop_reasons={ep["events"][2]["event_id"]: "COMPLETED"},
        retry_requested=False,
    )
    if stage == "open":
        raw.update(episode=None, preparation=None, setting_choice=None, stop_reasons={})
    elif stage == "familiarize":
        raw.update(episode=None, setting_choice=None, stop_reasons={})
    elif stage == "trial":
        ep["events"] = ep["events"][:2]
        raw["stop_reasons"] = {}
    elif stage == "observed":
        ep["events"] = ep["events"][:3]
    return raw


DIRECTORY = Path("docs/science/sci-p02-initial-policy/first-use-calibration-bootstrap")


def build_artifacts(root=ROOT):
    from .contracts import EncounterRequest, EncounterResult
    from .evaluator import evaluate
    from .policy import encoded, load_authority
    from .validation import validate_result

    authority = load_authority(root)
    cases = []
    for stage in ("open", "familiarize", "trial", "observed", "qualified"):
        req = synthetic_encounter(stage=stage, root=root)
        result = validate_result(req, evaluate(req, authority), authority)
        cases.append(dict(scenario=stage, request=req, result=result.model_dump(mode="json")))
    values = {
        "encounter-request.schema.json": encoded(EncounterRequest.model_json_schema()),
        "encounter-result.schema.json": encoded(EncounterResult.model_json_schema()),
        "encounter-fixtures.v1.json": encoded(
            dict(
                artifact_kind="REAL_EVALUATOR_SYNTHETIC_INPUT_NOT_SERVED",
                contract_version="first-calibration-encounter/1.0.0",
                authority_digest=authority.bundle_digest,
                cases=cases,
            )
        ),
    }
    import hashlib

    source_paths = set(authority.source_digests) | set(authority.historical.source_digests)
    source_paths.update(
        {
            "tools/science_calibration_bootstrap/policy.py",
            str(DIRECTORY / "authority/registry.v1.json"),
            str(DIRECTORY / "authority/sources.v1.json"),
        }
    )
    values["artifact-manifest.v1.json"] = encoded(
        dict(
            artifact_kind="REAL_EVALUATOR_SYNTHETIC_INPUT_NOT_SERVED",
            sources={
                p: hashlib.sha256((Path(root) / p).read_bytes()).hexdigest()
                for p in sorted(source_paths)
            },
            artifacts={p: hashlib.sha256(v).hexdigest() for p, v in sorted(values.items())},
        )
    )
    return values


def export_artifacts(root=ROOT):
    output = Path(root) / DIRECTORY / "exports"
    output.mkdir(parents=True, exist_ok=True)
    for name, value in build_artifacts(root).items():
        (output / name).write_bytes(value)


def verify_artifacts(root=ROOT):
    return all(
        (Path(root) / DIRECTORY / "exports" / p).read_bytes() == data
        for p, data in build_artifacts(root).items()
    )
