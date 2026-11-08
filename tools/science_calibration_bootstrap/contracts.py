"""Strict calibration encounter exchange; no plan or work-set permission."""

from __future__ import annotations

from typing import Literal, Self

from pydantic import AwareDatetime, StrictBool, model_validator

from tools.science_contracts.blueprint_first_plan_v1 import Fact, Provenance, Text
from tools.science_contracts.bootstrap_protocol_v3 import V3Record, strict_record
from tools.science_initial_policy.calibration_time_contracts import (
    CalibrationEpisode,
    ContextKey,
    Setting,
    _check_setting_context,
    _check_time,
    content_digest,
    context_digest,
)

State = Literal[
    "CALIBRATION_REQUIRED",
    "SUPPORTED_INITIAL_EXPLORATION",
    "OBSERVED",
    "QUALIFIED",
    "CONCERN_REVIEW",
    "UNAVAILABLE",
    "INSUFFICIENT_EVIDENCE",
    "WITHDRAWN",
]
Action = Literal[
    "READ_GUIDANCE",
    "PROVIDE_FACTS",
    "REQUEST_ASSISTANCE",
    "CONFIRM_CONTEXT",
    "INITIATE_FAMILIARIZATION",
    "CONFIRM_FAMILIARIZATION",
    "INITIATE_TRIAL",
    "RECORD_TRIAL",
    "ACCEPT_EXACT_SETTING",
    "PAUSE",
    "WITHDRAW",
]
StopReason = Literal["COMPLETED", "USER_STOPPED", "TIME_LIMIT", "CONCERN", "FAILURE", "UNKNOWN"]


class Preparation(V3Record):
    context_fingerprint: Text
    instruction_ref: Text
    setup_ref: Text
    understood: StrictBool
    controlled: StrictBool
    provenance: Provenance


class SettingChoice(V3Record):
    context_fingerprint: Text
    setting: Setting
    available: StrictBool
    provenance: Provenance


class EncounterRequest(V3Record):
    contract_version: Literal["first-calibration-encounter/1.0.0"]
    encounter_ref: Text
    subject_ref: Text
    source_revision: Text
    started_at: AwareDatetime
    as_of: AwareDatetime
    population: Fact[Text]
    limitations: Fact[tuple[Text, ...]]
    context: ContextKey
    context_provenance: Provenance
    availability: Literal["AVAILABLE", "UNAVAILABLE", "UNKNOWN"]
    ledger_complete: StrictBool
    ledger_source_ref: Text | None
    concern_state: Literal["CLEAR", "REPORTED", "UNKNOWN"]
    withdrawn: StrictBool
    episode: CalibrationEpisode | None
    preparation: Preparation | None
    setting_choice: SettingChoice | None
    stop_reasons: dict[str, StopReason]
    retry_requested: StrictBool

    @model_validator(mode="after")
    def boundaries(self) -> Self:
        if self.started_at > self.as_of:
            raise ValueError("encounter starts in the future")
        proofs = [self.context_provenance, self.population.provenance, self.limitations.provenance]
        for item in (self.preparation, self.setting_choice):
            if item:
                proofs.append(item.provenance)
                if item.context_fingerprint != context_digest(self.context):
                    raise ValueError("proof belongs to another context")
        for p in proofs:
            _check_time(p, self.as_of)
        if self.setting_choice:
            _check_setting_context(self.setting_choice.setting, self.context)
        ep = self.episode
        if ep and (
            ep.subject_ref != self.subject_ref
            or ep.context != self.context
            or ep.as_of > self.as_of
            or ep.availability != self.availability
        ):
            raise ValueError(
                "episode does not match the encounter subject/context/time/availability"
            )
        attempts = {e.event_id: e for e in ep.events if e.kind == "ATTEMPT_OBSERVED"} if ep else {}
        if not self.stop_reasons.keys() <= attempts.keys():
            raise ValueError("stop reason must identify an actual attempt")
        for identity, reason in self.stop_reasons.items():
            if reason in {"USER_STOPPED", "TIME_LIMIT"} and attempts[identity].completed is True:
                raise ValueError("an interrupted attempt cannot claim completion")
        return self


class EncounterResult(V3Record):
    contract_version: Literal["first-calibration-encounter/1.0.0"] = (
        "first-calibration-encounter/1.0.0"
    )
    activity_kind: Literal["CALIBRATION_ACTIVITY"] = "CALIBRATION_ACTIVITY"
    artifact_kind: Literal[
        "DRAFT_EVALUATION_SYNTHETIC_NOT_AUTHORITY", "ISOLATED_EVALUATION_NOT_SERVED"
    ]
    admission: Literal["NOT_ADMITTED", "ADMITTED_WITH_LIMITS"]
    encounter_ref: Text
    subject_ref: Text
    source_revision: Text
    input_digest: Text
    policy_ref: Text | None
    authority_digest: Text | None
    state: State
    phase: Literal["IDENTIFY", "FAMILIARIZE", "TRIAL", "OBSERVE", "DECIDE"]
    allowed_actions: tuple[Action, ...]
    candidate_actions: tuple[Action, ...] = ()
    reasons: tuple[Text, ...]
    instruction_refs: tuple[Text, ...]
    qualified_setting: Setting | None = None
    reference_event_id: Text | None = None
    acceptance_event_id: Text | None = None
    portable_episode: CalibrationEpisode | None = None
    confidence: Literal["LOW", "UNKNOWN"] = "UNKNOWN"
    effort_sufficiency: Literal["UNKNOWN"] = "UNKNOWN"
    duration: Literal["UNKNOWN"] = "UNKNOWN"


def validated_input(raw) -> EncounterRequest:
    return EncounterRequest.model_validate(strict_record(raw))


def input_digest(raw) -> str:
    return content_digest(validated_input(raw).model_dump(mode="json"))
