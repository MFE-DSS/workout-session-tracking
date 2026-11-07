"""Isolated C3/C6 typed consistency. No load prescription or admitted authority."""

from __future__ import annotations

from typing import Literal, Self

from pydantic import AwareDatetime, model_validator

from tools.science_contracts.blueprint_first_plan_v1 import PositiveInt, Provenance, Text
from tools.science_contracts.blueprint_first_plan_v2 import DurationV2, UnknownDuration
from tools.science_initial_policy.calibration_time_contracts import (
    ContextKey,
    Count,
    Number,
    Record,
    Setting,
    _check_setting_context,
    _check_time,
    content_digest,
    normalized_record,
)
from tools.science_initial_policy.time_feasibility import assess_time


class ProtocolStepV3(Record):
    kind: Literal["FAMILIARIZE", "TRIAL", "OBSERVE", "DECIDE"]
    instruction_ref: Text


class CalibrationProtocolV3(Record):
    contract_version: Literal["initial-calibration-protocol/2.0.0"]
    protocol_ref: Text
    source_ref: Text
    steps: tuple[ProtocolStepV3, ...]
    stop_rule_ref: Text
    retry_rule_ref: Text

    @model_validator(mode="after")
    def phases(self) -> Self:
        if [s.kind for s in self.steps] != ["FAMILIARIZE", "TRIAL", "OBSERVE", "DECIDE"]:
            raise ValueError("four ordered instruction phases required, not numerical defaults")
        return self


class TrialReviewV3(Record):
    protocol_version: Literal["initial-calibration-review/2.0.0"]
    subject_ref: Text
    event_id: Text
    context: ContextKey
    setting: Setting
    provenance: Provenance
    episode_started_at: AwareDatetime
    as_of: AwareDatetime
    observed_reps: Count
    min_reps: PositiveInt
    max_reps: PositiveInt
    stop_reason: Literal["COMPLETED", "INTERRUPTED", "USER_STOPPED", "FAILED", "UNKNOWN"]
    technique: Literal["ACCEPTABLE", "CONCERN", "UNKNOWN"]
    discomfort: Literal["NO_CONCERN", "CONCERN", "UNKNOWN"]
    reported_rir: Number | None
    effort_claim: Literal[
        "UNKNOWN", "USER_REPORTED_EASY", "USER_REPORTED_HARD", "USER_REPORTED_TARGET"
    ]
    effort_source_ref: Text | None
    effort_confidence: Literal["LOW", "UNKNOWN"]
    assessment: Literal[
        "NOT_ASSESSABLE", "WITHIN_PRESCRIBED_REPS", "OUTSIDE_PRESCRIBED_REPS", "REVIEW_REQUIRED"
    ]
    next_action: Literal["NONE", "REVIEW", "RETRY_WITH_CONFIRMED_SETTING"]

    @model_validator(mode="after")
    def observed_consistency(self) -> Self:
        _check_time(self.provenance, self.as_of)
        _check_setting_context(self.setting, self.context)
        p = self.provenance
        if (
            self.episode_started_at > self.as_of
            or self.min_reps > self.max_reps
            or p.origin not in {"USER_OBSERVED", "DERIVED_FROM_HISTORY"}
            or p.acquisition != "EXECUTION_LOG"
            or p.source_ref is None
            or p.measured_at is None
            or p.recorded_at is None
        ):
            raise ValueError("trial needs actual dated execution provenance and ordered bounds")
        if (self.effort_claim == "UNKNOWN") != (self.effort_source_ref is None):
            raise ValueError("effort report needs its source; unknown is not a target observation")
        if self.reported_rir is None and self.effort_confidence != "UNKNOWN":
            raise ValueError("no confidence in an absent RIR report")
        concern = (
            self.stop_reason == "FAILED"
            or self.technique != "ACCEPTABLE"
            or self.discomfort != "NO_CONCERN"
        )
        current = min(p.recorded_at, p.measured_at) >= self.episode_started_at
        if concern:
            if self.assessment != "REVIEW_REQUIRED" or self.next_action != "REVIEW":
                raise ValueError(
                    "concern or unknown safety signals require review, not automatic retry"
                )
        elif (
            not current
            or self.stop_reason != "COMPLETED"
            or any(
                getattr(self.context, field) is None
                for field in (
                    "canonical_exercise_id",
                    "context_ref",
                    "equipment_ref",
                    "realization_ref",
                )
            )
            or self.context.side == "UNKNOWN"
            or self.context.load_semantics == "UNKNOWN"
        ):
            if self.assessment != "NOT_ASSESSABLE" or self.next_action != "NONE":
                raise ValueError(
                    "interruption or historical import cannot classify causal difficulty"
                )
        else:
            within = self.min_reps <= self.observed_reps <= self.max_reps
            expected = "WITHIN_PRESCRIBED_REPS" if within else "OUTSIDE_PRESCRIBED_REPS"
            if self.assessment != expected or (
                not within and self.next_action == "RETRY_WITH_CONFIRMED_SETTING"
            ):
                raise ValueError("repetition range is not an automatic load/effort adjustment rule")
        return self


class SettingTransitionV3(Record):
    as_of: AwareDatetime
    context: ContextKey
    observed_setting: Setting
    chosen_setting: Setting | None
    available_in_effort_order: tuple[Setting, ...]
    order_source: Provenance | None
    direction: Literal["NONE", "RETAIN", "MORE_EFFORT", "LESS_EFFORT"]

    @model_validator(mode="after")
    def sourced_transition(self) -> Self:
        if self.order_source is not None:
            _check_time(self.order_source, self.as_of)
        settings = (self.observed_setting, *self.available_in_effort_order)
        for setting in settings:
            _check_setting_context(setting, self.context)
        if self.direction == "NONE":
            if self.chosen_setting is not None:
                raise ValueError("no action cannot carry a fabricated next setting")
            return self
        p = self.order_source
        if (
            p is None
            or p.source_ref is None
            or p.recorded_at is None
            or p.origin not in {"USER_REPORTED", "USER_OBSERVED"}
            or p.acquisition not in {"DECLARED", "DEVICE_MEASURED", "EXECUTION_LOG"}
        ):
            raise ValueError("device effort order requires its direct source")
        if self.context.load_semantics == "UNKNOWN" or self.chosen_setting is None:
            raise ValueError("unknown load meaning cannot authorize a numerical transition")
        _check_setting_context(self.chosen_setting, self.context)
        ids = [content_digest(s.model_dump(mode="json")) for s in self.available_in_effort_order]
        before, after = (
            content_digest(s.model_dump(mode="json"))
            for s in (self.observed_setting, self.chosen_setting)
        )
        if len(set(ids)) != len(ids) or before not in ids or after not in ids:
            raise ValueError("settings must belong to the non-duplicate sourced available order")
        delta = ids.index(after) - ids.index(before)
        if (
            self.direction == "RETAIN"
            and delta != 0
            or self.direction == "MORE_EFFORT"
            and delta <= 0
            or self.direction == "LESS_EFFORT"
            and delta >= 0
        ):
            raise ValueError(
                "chosen setting contradicts device effort order, not numeric magnitude"
            )
        return self


class TimeAssessmentV3(Record):
    session_id: Text
    state: Literal[
        "SUPPORTED",
        "BUDGET_COMPATIBLE_BY_POLICY",
        "BUDGET_TIGHT",
        "BUDGET_UNCERTAIN",
        "STRUCTURALLY_TOO_LONG",
    ]
    duration: DurationV2
    known_rest_floor_seconds: Number | None
    unknown_components: tuple[Text, ...]
    policy_ref: Text | None
    assumption_refs: tuple[Text, ...]
    limitations: tuple[Text, ...]

    @model_validator(mode="after")
    def honesty(self) -> Self:
        floor = self.known_rest_floor_seconds
        exceeds = floor is not None and floor >= self.duration.budget_minutes * 60
        if exceeds != (self.state == "STRUCTURALLY_TOO_LONG"):
            raise ValueError("nonempty work remains when a valid rest floor consumes the budget")
        if self.state == "SUPPORTED":
            if (
                self.duration.state != "SUPPORTED"
                or self.policy_ref is None
                or self.duration.upper_seconds > self.duration.budget_minutes * 60
                or self.unknown_components
            ):
                raise ValueError("supported time requires full applicable evidence within budget")
        elif self.duration.state == "SUPPORTED":
            raise ValueError("partial/uncertain time must not claim a supported duration")
        if self.state in {"BUDGET_COMPATIBLE_BY_POLICY", "BUDGET_TIGHT"}:
            if self.policy_ref is None or not self.assumption_refs or not self.limitations:
                raise ValueError(
                    "planning classification needs an explicit convention, not a label"
                )
        elif (
            self.state in {"BUDGET_UNCERTAIN", "STRUCTURALLY_TOO_LONG"}
            and self.policy_ref is not None
        ):
            raise ValueError("structural negative diagnostic does not admit a temporal policy")
        return self


def assess_structural_time(
    session: dict, *, budget_minutes: int, structure: str = "TRADITIONAL_SEQUENTIAL"
) -> TimeAssessmentV3:
    """Map the existing partial diagnostic; never derive positive fit or a duration."""
    raw = normalized_record(session)
    result = assess_time(raw, budget_minutes, structure)
    return TimeAssessmentV3(
        session_id=raw["session_id"],
        state="STRUCTURALLY_TOO_LONG"
        if result["feasibility"] == "NOT_FEASIBLE"
        else "BUDGET_UNCERTAIN",
        duration=UnknownDuration(state="UNKNOWN", budget_minutes=budget_minutes),
        known_rest_floor_seconds=result["known_rest_floor_seconds"],
        unknown_components=tuple(result["unknown_components"]),
        policy_ref=None,
        assumption_refs=(),
        limitations=("Partial rest floor only; unknown work/preparation/operations are not zero.",),
    )
