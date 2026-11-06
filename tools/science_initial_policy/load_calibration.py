"""Observation-backed provisional settings, not true-RIR estimates or load ramps."""

from __future__ import annotations

from tools.science_initial_policy.calibration_time_contracts import (
    CalibrationEpisode,
    normalized_record,
)

PROTOCOL_VERSION = "initial-load-calibration/1.0.0"


def _result(episode: CalibrationEpisode, state: str, *reasons: str) -> dict:
    return {
        "protocol_version": PROTOCOL_VERSION,
        "episode_id": episode.episode_id,
        "state": state,
        "observed_setting": None,
        "reference_event_id": None,
        "reference_source_ref": None,
        "reference_role": None,
        "load_kg": None,
        "load_mode": "CALIBRATION_REQUIRED",
        "reported_rir": None,
        "effort_sufficiency": "UNKNOWN",
        "confidence": "UNKNOWN",
        "automatic_next_action": "NONE",
        "reasons": list(reasons),
        "limitations": [
            "An accepted observed setting is a provisional reference, not verified true RIR or optimum.",
            "No automatic increment, clinical clearance, E7 rail or equipment force equivalence.",
        ],
    }


def _context_block(episode: CalibrationEpisode) -> str | None:
    if not episode.ledger_complete or not episode.ledger_source_ref:
        return "LEDGER_COMPLETENESS_UNKNOWN"
    if episode.previous_episode_id is not None and episode.predecessor_blocked is not False:
        return "RESTART_POLICY_UNAVAILABLE"
    c, p = episode.context, episode.context_provenance
    if (
        any(getattr(c, field) is None for field in (
            "canonical_exercise_id", "context_ref", "equipment_ref", "realization_ref",
        )) or c.load_semantics == "UNKNOWN" or c.side == "UNKNOWN"
        or p.source_ref is None or p.recorded_at is None or p.origin == "UNKNOWN"
        or p.acquisition not in {"DECLARED", "DEVICE_MEASURED", "EXECUTION_LOG"}
        or episode.availability == "UNKNOWN"
    ):
        return "CONTEXT_NOT_CONFIRMED"
    return None


def _concern(event) -> bool:
    if event.kind == "CONCERN_REPORTED":
        return True
    if event.kind != "ATTEMPT_OBSERVED":
        return False
    return (
        event.successful is False or event.technique == "CONCERN" or event.discomfort == "CONCERN"
        or (event.completed is True and (
            event.technique == "UNKNOWN" or event.discomfort == "UNKNOWN"
        ))
    )


def _accepted_reference(episode: CalibrationEpisode, events: list, min_reps: int, max_reps: int):
    current = [e for e in events if e.provenance.recorded_at >= episode.started_at]
    accepted = [e for e in current if e.kind == "SETTING_ACCEPTED"]
    if not accepted:
        return None
    acceptance = accepted[-1]
    if any(e.kind == "FAMILIARIZATION_STARTED" and e.sequence > acceptance.sequence for e in current):
        return None
    attempts = [e for e in events if e.kind == "ATTEMPT_OBSERVED"]
    trial = next((e for e in attempts if e.event_id == acceptance.reference_event_id), None)
    if trial is None or trial.sequence >= acceptance.sequence:
        return None
    if trial != attempts[-1] or trial.setting is None or trial.reps is None:
        return None
    if acceptance.setting is not None and acceptance.setting != trial.setting:
        return None
    if trial.completed is not True or trial.successful is not True or not min_reps <= trial.reps <= max_reps:
        return None
    availability = [e for e in current if e.kind == "CONTEXT_CONFIRMED" and e.setting is not None]
    if not availability or availability[-1].setting != trial.setting:
        return None
    if availability[-1].sequence >= acceptance.sequence:
        return None
    familiar = (
        trial.familiarization_confirmed and trial.provenance.measured_at >= episode.started_at
    ) or any(
        e.kind == "FAMILIARIZATION_CONFIRMED" and e.sequence < acceptance.sequence for e in current
    )
    return trial if familiar else None


def calibrate(episode: CalibrationEpisode | dict, *, min_reps: int, max_reps: int) -> dict:
    """Replay a complete sourced snapshot. Typed model copies are revalidated too.

    Completeness/identity checks are contract consistency, not authentication of a
    future caller. No restart rule has been scientifically admitted in this version.
    """
    for n in (min_reps, max_reps):
        if type(n) is not int or n < 1:
            raise ValueError("prescribed repetition bounds must be positive integers")
    if min_reps > max_reps:
        raise ValueError("repetition bounds reversed")
    ep = CalibrationEpisode.model_validate(normalized_record(episode))
    events = sorted({e.event_id: e for e in ep.events}.values(), key=lambda e: e.sequence)
    if ep.availability == "UNAVAILABLE" or any(e.kind == "EQUIPMENT_UNAVAILABLE" for e in events):
        return _result(ep, "UNAVAILABLE", "EXERCISE_UNAVAILABLE_IN_CONTEXT")
    block = _context_block(ep)
    if block:
        return _result(ep, "INSUFFICIENT_DATA", block)
    if any(_concern(e) for e in events):
        return _result(ep, "CALIBRATION_IN_PROGRESS", "EPISODE_REVIEW_REQUIRED")
    trial = _accepted_reference(ep, events, min_reps, max_reps)
    if trial is None:
        started = any(e.kind in {"ATTEMPT_OBSERVED", "FAMILIARIZATION_STARTED"} for e in events)
        return _result(ep, "CALIBRATION_IN_PROGRESS" if started else "NEEDS_CALIBRATION", "TRIAL_NOT_QUALIFIED")
    out = _result(ep, "CALIBRATED", "OBSERVED_SETTING_ACCEPTED_FOR_TRIAL")
    out.update(
        observed_setting=trial.setting.model_dump(mode="json"),
        reference_event_id=trial.event_id, reference_source_ref=trial.provenance.source_ref,
        reference_role="CALIBRATION_TRIAL", reported_rir=trial.rir, confidence="LOW",
        load_mode="NOT_DEFINED",
    )
    if ep.context.load_semantics == "TOTAL_EXTERNAL" and trial.setting.kind == "MASS_KG":
        out.update(load_kg=trial.setting.value, load_mode="HISTORY_SUPPORTED")
    else:
        out["reasons"].append("V1_LOAD_MEANING_NOT_REPRESENTABLE")
    return out
