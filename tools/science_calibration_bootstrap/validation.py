"""Canonical strict exchange validation, independent qualification checks."""

from tools.science_contracts.bootstrap_protocol_v3 import strict_record
from tools.science_initial_policy.calibration_time_contracts import content_digest

from .contracts import EncounterResult
from .evaluator import evaluate


def validate_result(raw, response, authority=None) -> EncounterResult:
    actual = EncounterResult.model_validate(strict_record(response))
    expected = evaluate(raw, authority)
    if actual.state == "QUALIFIED":
        from tools.science_initial_policy.admission_calibration import calibrate_for_admission

        episode = actual.portable_episode
        if episode is None or actual.qualified_setting is None:
            raise ValueError("qualification requires an actual portable episode")
        diagnostic = calibrate_for_admission(episode, min_reps=8, max_reps=12)
        if (
            diagnostic["state"] != "CALIBRATED"
            or diagnostic["reference_event_id"] != actual.reference_event_id
        ):
            raise ValueError("qualification differs from the observed C3 diagnostic")
    if content_digest(actual.model_dump(mode="json")) != content_digest(
        expected.model_dump(mode="json")
    ):
        raise ValueError("encounter result differs from canonical recomputation")
    return expected
