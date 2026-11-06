"""Synthetic observed facts for calibration/time tests, never production authority."""

import copy
import hashlib
import json


def context(**changes):
    value = {
        "canonical_exercise_id": "developpe-couche-barre",
        "context_ref": "gym:test-a",
        "equipment_ref": "bench:test-a",
        "realization_ref": "execution:test-bench",
        "load_semantics": "TOTAL_EXTERNAL",
        "side": "BILATERAL",
    }
    value.update(changes)
    return value


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def setting(value=40.0, kind="MASS_KG", unit="kg"):
    return {"kind": kind, "value": value, "unit": unit}


def provenance(sequence=0, *, observed=False):
    stamp = f"2026-11-06T11:{sequence:02d}:00Z"
    return {
        "origin": "USER_OBSERVED" if observed else "USER_REPORTED",
        "acquisition": "EXECUTION_LOG" if observed else "DECLARED",
        "source_ref": f"synthetic:event-{sequence}",
        "recorded_at": stamp,
        "measured_at": stamp if observed else None,
    }


def event(kind, sequence, *, ctx=None, **changes):
    value = {
        "event_id": f"e{sequence}",
        "sequence": sequence,
        "kind": kind,
        "subject_ref": "subject:A",
        "context_fingerprint": digest(ctx or context()),
        "provenance": provenance(sequence, observed=kind == "ATTEMPT_OBSERVED"),
    }
    value.update(changes)
    return value


def episode(events=None, *, ctx=None, **changes):
    value = {
        "episode_id": "episode:test-1",
        "subject_ref": "subject:A",
        "context": ctx or context(),
        "as_of": "2026-11-06T12:00:00Z",
        "started_at": "2026-11-06T11:00:00Z",
        "context_provenance": provenance(),
        "availability": "AVAILABLE",
        "ledger_complete": True,
        "ledger_source_ref": "synthetic:complete-ledger",
        "events": events or [],
    }
    value.update(changes)
    return value


def calibrated_episode(*, ctx=None, load=None):
    ctx = ctx or context()
    load = load or setting()
    events = [
        event("CONTEXT_CONFIRMED", 1, ctx=ctx, setting=load),
        event("FAMILIARIZATION_CONFIRMED", 2, ctx=ctx),
        event(
            "ATTEMPT_OBSERVED", 3, ctx=ctx, setting=load, reps=10,
            completed=True, successful=True, technique="ACCEPTABLE", discomfort="NO_CONCERN",
        ),
        event("SETTING_ACCEPTED", 4, ctx=ctx, reference_event_id="e3"),
    ]
    return episode(copy.deepcopy(events), ctx=ctx)
