"""Explicit synthetic examples from real evaluators; never imported by a runtime."""

import copy
import hashlib
from pathlib import Path

from tools.science_calibration_bootstrap.artifacts import synthetic_plan_input
from tools.science_initial_policy.calibration_time_contracts import ContextKey, context_digest
from tools.science_initial_policy.registry import ROOT

DIRECTORY = Path("docs/science/sci-p02-initial-policy/calibration-six-extensions/exports")


def synthetic_encounter(candidate_id, *, stage="qualified", root=ROOT):
    """Fixed test-only observations/choice, not an engine-selected first load."""
    from .evaluator import PROFILES

    if candidate_id not in PROFILES:
        raise ValueError("not a supported extension realization")
    plan = synthetic_plan_input(root)
    ep = copy.deepcopy(
        next(e for e in plan["episodes"] if e["context"]["canonical_exercise_id"] == candidate_id)
    )
    ep["events"][1]["setting"] = copy.deepcopy(ep["events"][0]["setting"])
    proof = copy.deepcopy(ep["context_provenance"])
    fingerprint = context_digest(ContextKey.model_validate(ep["context"]))
    raw = dict(
        contract_version="first-calibration-encounter/1.0.0",
        encounter_ref="synthetic:extension:" + candidate_id,
        subject_ref=ep["subject_ref"],
        source_revision="synthetic:source/1",
        started_at=ep["started_at"],
        as_of=ep["as_of"],
        population=plan["blueprint"]["population_scope"],
        limitations=plan["blueprint"]["limitations"],
        context=ep["context"],
        context_provenance=proof,
        availability="AVAILABLE",
        ledger_complete=True,
        ledger_source_ref="synthetic:complete-ledger",
        concern_state="CLEAR",
        withdrawn=False,
        episode=ep,
        preparation=dict(
            context_fingerprint=fingerprint,
            instruction_ref="synthetic:actual-device-instructions",
            setup_ref="synthetic:actual-setup",
            understood=True,
            controlled=True,
            provenance=proof,
        ),
        setting_choice=dict(
            context_fingerprint=fingerprint,
            setting=copy.deepcopy(ep["events"][0]["setting"]),
            available=True,
            provenance=copy.deepcopy(proof),
        ),
        stop_reasons={ep["events"][2]["event_id"]: "COMPLETED"},
        retry_requested=False,
    )
    if stage == "open":
        raw.update(episode=None, preparation=None, setting_choice=None, stop_reasons={})
    elif stage == "setup":
        raw.update(episode=None, setting_choice=None, stop_reasons={})
    elif stage == "trial":
        ep["events"] = ep["events"][:2]
        raw["stop_reasons"] = {}
    elif stage == "observed":
        ep["events"] = ep["events"][:3]
    elif stage != "qualified":
        raise ValueError("unknown synthetic stage")
    return raw


def bridge(root=ROOT):
    from tools.science_calibration_bootstrap.artifacts import synthetic_encounter as pilot_input
    from tools.science_calibration_bootstrap.evaluator import evaluate as evaluate_pilot
    from tools.science_calibration_bootstrap.policy import load_authority as load_pilot
    from tools.science_calibration_bootstrap.validation import validate_result as validate_pilot
    from tools.science_contracts.blueprint_first_plan_v3 import (
        observation_fingerprint,
        request_fingerprint,
    )
    from tools.science_initial_policy.v3_admission import load_v3_registry
    from tools.science_initial_policy.v3_producer import produce_v3
    from tools.science_initial_policy.v3_validation import validate_admitted_exchange_v3

    from .evaluator import PROFILES, evaluate
    from .policy import load_authority
    from .validation import validate_result

    authority = load_authority(root)
    pilot = load_pilot(root)
    raw_pilot = pilot_input(root=root)
    out_pilot = validate_pilot(raw_pilot, evaluate_pilot(raw_pilot, pilot), pilot)
    cases = [dict(request=raw_pilot, result=out_pilot.model_dump(mode="json"))]
    episodes = [out_pilot.portable_episode.model_dump(mode="json")]
    for candidate_id in PROFILES:
        raw = synthetic_encounter(candidate_id, root=root)
        out = validate_result(raw, evaluate(raw, authority), authority)
        if out.state != "QUALIFIED":
            raise ValueError("actual encounter did not qualify: " + candidate_id)
        episodes.append(out.portable_episode.model_dump(mode="json"))
        cases.append(dict(request=raw, result=out.model_dump(mode="json")))
    req = synthetic_plan_input(root)
    req["episodes"] = episodes
    registry = load_v3_registry(root)
    first = validate_admitted_exchange_v3(req, produce_v3(req, registry), registry)
    acknowledged = copy.deepcopy(req)
    acknowledged["acknowledgment"] = dict(
        kind="TIME_UNCERTAINTY_ACK",
        subject_ref=req["subject_ref"],
        snapshot_ref=req["snapshot_ref"],
        source_revision=req["source_revision"],
        request_fingerprint=request_fingerprint(req),
        observation_fingerprint=observation_fingerprint(req),
        plan_time_fingerprint=first.plan_time_fingerprint,
        product_policy_ref=first.start_policy_ref,
        acknowledged_at="2026-11-07T12:01:00Z",
        source_ref="synthetic:explicit-time-ack",
    )
    second = validate_admitted_exchange_v3(
        acknowledged, produce_v3(acknowledged, registry), registry
    )
    return dict(
        artifact_kind="REAL_EVALUATORS_AND_V3_SYNTHETIC_INPUT_NOT_SERVED",
        encounters=cases,
        request=req,
        before_ack=first.model_dump(mode="json"),
        acknowledged_request=acknowledged,
        after_ack=second.model_dump(mode="json"),
    )


def build_artifacts(root=ROOT):
    from tools.science_calibration_bootstrap.policy import encoded

    from .evaluator import PROFILES, evaluate
    from .policy import DIRECTORY as authority_directory
    from .policy import load_authority
    from .validation import validate_result

    authority = load_authority(root)
    cases = []
    for candidate_id in PROFILES:
        for stage in ("open", "setup", "trial", "observed", "qualified"):
            req = synthetic_encounter(candidate_id, stage=stage, root=root)
            out = validate_result(req, evaluate(req, authority), authority)
            cases.append(
                dict(
                    candidate_id=candidate_id,
                    stage=stage,
                    request=req,
                    result=out.model_dump(mode="json"),
                )
            )
    values = {
        "encounter-fixtures.v1.json": encoded(
            dict(
                artifact_kind="REAL_EVALUATOR_SYNTHETIC_INPUT_NOT_SERVED",
                authority_digest=authority.bundle_digest,
                cases=cases,
            )
        ),
        "seven-encounter-v3-bridge.v1.json": encoded(bridge(root)),
    }
    sources = set(authority.source_digests) | {
        str(authority_directory / "registry.v1.json"),
        str(authority_directory / "sources.v1.json"),
        "tools/science_calibration_extension/policy.py",
    }
    values["artifact-manifest.v1.json"] = encoded(
        dict(
            artifact_kind="REAL_EVALUATORS_AND_V3_SYNTHETIC_INPUT_NOT_SERVED",
            sources={
                p: hashlib.sha256((Path(root) / p).read_bytes()).hexdigest()
                for p in sorted(sources)
            },
            artifacts={p: hashlib.sha256(data).hexdigest() for p, data in sorted(values.items())},
        )
    )
    return values


def export_artifacts(root=ROOT):
    output = Path(root) / DIRECTORY
    output.mkdir(parents=True, exist_ok=True)
    for name, data in build_artifacts(root).items():
        (output / name).write_bytes(data)


def verify_artifacts(root=ROOT):
    return all(
        (Path(root) / DIRECTORY / p).read_bytes() == data
        for p, data in build_artifacts(root).items()
    )
