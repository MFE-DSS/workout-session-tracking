"""Explicit synthetic encounter inputs, never personal evidence."""

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def plan_input():
    return json.loads(
        (ROOT / "docs/science/sci-p02-initial-policy/stage2-v3/SYNTHETIC_INPUT.json").read_text()
    )


def encounter(*, stage="qualified"):
    plan = plan_input()
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
