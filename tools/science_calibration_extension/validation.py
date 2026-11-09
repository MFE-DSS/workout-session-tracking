"""Canonical exchange validation plus independent observed/exact-setting guards."""

from tools.science_calibration_bootstrap.contracts import EncounterResult, validated_input
from tools.science_contracts.bootstrap_protocol_v3 import strict_record
from tools.science_initial_policy.admission_calibration import calibrate_for_admission
from tools.science_initial_policy.calibration_time_contracts import content_digest

from .evaluator import evaluate, loaded_familiarization


def validate_result(raw, response, authority=None) -> EncounterResult:
    req = validated_input(raw)
    actual = EncounterResult.model_validate(strict_record(response))
    if actual.state == "QUALIFIED":
        ep = actual.portable_episode
        if ep is None or actual.qualified_setting is None or ep != req.episode:
            raise ValueError("qualification requires the exact observed input episode")
        diagnostic = calibrate_for_admission(ep, min_reps=8, max_reps=12)
        trial = next((e for e in ep.events if e.event_id == actual.reference_event_id), None)
        if (
            diagnostic["state"] != "CALIBRATED"
            or trial is None
            or diagnostic["reference_event_id"] != trial.event_id
            or trial.setting != actual.qualified_setting
            or not loaded_familiarization(req, before=trial)
        ):
            raise ValueError("qualification lacks observed C3 and exact-setting familiarization")
    expected = evaluate(req, authority)
    if content_digest(actual.model_dump(mode="json")) != content_digest(
        expected.model_dump(mode="json")
    ):
        raise ValueError("extension result differs from canonical recomputation")
    return expected
