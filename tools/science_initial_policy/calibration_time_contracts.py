"""Strict isolated observation records; no authentication, writes or E7 rail authority."""

from __future__ import annotations

import hashlib
import json
from typing import Annotated, Literal, Self

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, StrictBool, model_validator

from tools.science_contracts.blueprint_first_plan_v1 import Provenance, Text

Number = Annotated[float, Field(strict=True, ge=0, allow_inf_nan=False)]
Count = Annotated[int, Field(strict=True, ge=0)]
Sequence = Annotated[int, Field(strict=True, gt=0)]


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)


class ContextKey(Record):
    canonical_exercise_id: Text | None
    context_ref: Text | None
    equipment_ref: Text | None
    realization_ref: Text | None
    load_semantics: Literal[
        "TOTAL_EXTERNAL", "PER_IMPLEMENT", "MACHINE_DISPLAY_KG", "ASSISTANCE_SETTING",
        "NON_MASS_SETTING", "BODYWEIGHT", "UNKNOWN",
    ]
    side: Literal["BILATERAL", "LEFT", "RIGHT", "UNKNOWN"]


def content_digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode()).hexdigest()


def normalized_record(value):
    """Revalidate nested typed instances too, including unchecked model_copy edits."""
    def encode(item):
        if isinstance(item, BaseModel):
            return item.model_dump(mode="json")
        raise TypeError("observation records must be JSON values or Pydantic records")

    return json.loads(json.dumps(value, default=encode, allow_nan=False))


def context_digest(context: ContextKey) -> str:
    return content_digest(context.model_dump(mode="json"))


class Setting(Record):
    kind: Literal["MASS_KG", "ASSISTANCE_SETTING", "NON_MASS_SETTING", "BODYWEIGHT"]
    value: Number | None
    unit: Literal["kg", "setting", "none"]

    @model_validator(mode="after")
    def units(self) -> Self:
        if self.kind == "BODYWEIGHT":
            if self.value is not None or self.unit != "none":
                raise ValueError("unmeasured bodyweight is not a fictional external mass")
        elif self.value is None or self.unit == "none":
            raise ValueError("an observed setting requires its value and unit")
        if self.kind == "MASS_KG" and self.unit != "kg":
            raise ValueError("mass setting must have explicit kg units")
        if self.kind == "NON_MASS_SETTING" and self.unit != "setting":
            raise ValueError("non-mass setting is not kg")
        return self


class CalibrationEvent(Record):
    event_id: Text
    sequence: Sequence
    kind: Literal[
        "CONTEXT_CONFIRMED", "FAMILIARIZATION_STARTED", "FAMILIARIZATION_CONFIRMED",
        "ATTEMPT_OBSERVED", "SETTING_ACCEPTED", "CONCERN_REPORTED", "EQUIPMENT_UNAVAILABLE",
    ]
    subject_ref: Text
    context_fingerprint: Annotated[str, Field(strict=True, pattern="^[0-9a-f]{64}$")]
    provenance: Provenance
    setting: Setting | None = None
    reps: Count | None = None
    completed: StrictBool | None = None
    successful: StrictBool | None = None
    technique: Literal["ACCEPTABLE", "CONCERN", "UNKNOWN"] = "UNKNOWN"
    discomfort: Literal["NO_CONCERN", "CONCERN", "UNKNOWN"] = "UNKNOWN"
    rir: Number | None = None
    familiarization_confirmed: StrictBool = False
    reference_event_id: Text | None = None

    @model_validator(mode="after")
    def direct_source(self) -> Self:
        p = self.provenance
        if p.source_ref is None or p.recorded_at is None:
            raise ValueError("event requires a dated source")
        if p.origin not in {"USER_REPORTED", "USER_OBSERVED", "DERIVED_FROM_HISTORY"}:
            raise ValueError("a population prior is not an execution observation")
        if p.acquisition not in {"DECLARED", "DEVICE_MEASURED", "EXECUTION_LOG"}:
            raise ValueError("event acquisition must be explicit and direct")
        if self.kind != "ATTEMPT_OBSERVED" and p.origin == "DERIVED_FROM_HISTORY":
            raise ValueError("history alone cannot confirm current availability or acceptance")
        if self.kind == "ATTEMPT_OBSERVED" and (
            p.origin not in {"USER_OBSERVED", "DERIVED_FROM_HISTORY"}
            or p.acquisition != "EXECUTION_LOG" or p.measured_at is None
        ):
            raise ValueError("attempt requires the actual execution source and time")
        if self.kind == "SETTING_ACCEPTED" and self.reference_event_id is None:
            raise ValueError("acceptance requires the exact observed attempt")
        return self


class CalibrationEpisode(Record):
    episode_id: Text
    subject_ref: Text
    context: ContextKey
    as_of: AwareDatetime
    started_at: AwareDatetime
    context_provenance: Provenance
    availability: Literal["AVAILABLE", "UNAVAILABLE", "UNKNOWN"]
    ledger_complete: StrictBool
    ledger_source_ref: Text | None
    events: tuple[CalibrationEvent, ...]
    previous_episode_id: Text | None = None
    predecessor_blocked: StrictBool | None = None
    restart_basis_ref: Text | None = None

    @model_validator(mode="after")
    def event_boundary(self) -> Self:
        if self.started_at > self.as_of:
            raise ValueError("episode starts after as_of")
        if self.previous_episode_id is None and (
            self.predecessor_blocked is not None or self.restart_basis_ref is not None
        ):
            raise ValueError("predecessor facts require their episode identity")
        p = self.context_provenance
        if p.origin not in {"USER_REPORTED", "USER_OBSERVED", "UNKNOWN"}:
            raise ValueError("context cannot be assumed from a population or old history")
        _check_time(p, self.as_of)
        identities, sequences = {}, {}
        for e in self.events:
            if e.subject_ref != self.subject_ref or e.context_fingerprint != context_digest(self.context):
                raise ValueError("event subject/context does not belong to this episode")
            _check_time(e.provenance, self.as_of)
            if e.event_id in identities and identities[e.event_id] != e:
                raise ValueError("divergent duplicate event identity")
            if e.sequence in sequences and sequences[e.sequence] != e:
                raise ValueError("ambiguous event sequence")
            identities[e.event_id], sequences[e.sequence] = e, e
            _check_setting_context(e.setting, self.context)
        ordered = sorted(sequences.values(), key=lambda event: event.sequence)
        times = [e.provenance.recorded_at for e in ordered]
        if times != sorted(times):
            raise ValueError("sequence contradicts recorded chronology")
        return self


def _check_time(provenance: Provenance, as_of: AwareDatetime) -> None:
    if any(t is not None and t > as_of for t in (provenance.recorded_at, provenance.measured_at)):
        raise ValueError("future facts cannot participate in an earlier decision")
    if (
        provenance.measured_at is not None and provenance.recorded_at is not None
        and provenance.measured_at > provenance.recorded_at
    ):
        raise ValueError("observation cannot have been recorded before it occurred")


def _check_setting_context(setting: Setting | None, context: ContextKey) -> None:
    if setting is None or context.load_semantics == "UNKNOWN":
        return
    expected = {
        "TOTAL_EXTERNAL": "MASS_KG", "PER_IMPLEMENT": "MASS_KG", "MACHINE_DISPLAY_KG": "MASS_KG",
        "ASSISTANCE_SETTING": "ASSISTANCE_SETTING", "NON_MASS_SETTING": "NON_MASS_SETTING",
        "BODYWEIGHT": "BODYWEIGHT",
    }
    if expected[context.load_semantics] != setting.kind:
        raise ValueError("setting meaning does not match its equipment context")
