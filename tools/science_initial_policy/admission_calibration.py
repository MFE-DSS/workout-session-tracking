"""Successor calibration diagnostic; frozen v1 behavior remains replayable."""

from __future__ import annotations

from tools.science_initial_policy.calibration_time_contracts import (
    CalibrationEpisode,
    normalized_record,
)
from tools.science_initial_policy.load_calibration import calibrate

PROTOCOL_VERSION = "initial-load-calibration/1.1.0-isolated"


def calibrate_for_admission(episode: CalibrationEpisode | dict, *, min_reps: int, max_reps: int) -> dict:
    """Old facts alone do not imply current activity; concerns remain blocking.

    A newly recorded import of an older observation is still historical. Accepted
    comparable settings continue through the existing reconfirmation protocol.
    This diagnostic neither admits a bootstrap nor estimates true RIR.
    """
    ep = CalibrationEpisode.model_validate(normalized_record(episode))
    result = calibrate(ep, min_reps=min_reps, max_reps=max_reps)
    result["protocol_version"] = PROTOCOL_VERSION
    if result["state"] != "CALIBRATION_IN_PROGRESS" or result["reasons"] != ["TRIAL_NOT_QUALIFIED"]:
        return result
    active = any(
        e.kind in {"ATTEMPT_OBSERVED", "FAMILIARIZATION_STARTED"}
        and e.provenance.recorded_at >= ep.started_at
        and (e.provenance.measured_at is None or e.provenance.measured_at >= ep.started_at)
        for e in ep.events
    )
    if not active:
        result["state"] = "NEEDS_CALIBRATION"
    return result
