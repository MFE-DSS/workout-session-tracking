"""Explicit parallel V3 transport. Disabled for real-person runtime."""

from __future__ import annotations

import json
from datetime import UTC
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.exc import DBAPIError

from app.config import get_settings
from app.deps import ApiUser, DbSession
from app.models.first_plan_runtime import OwnedBlueprintSnapshot
from app.services.plan_v3 import snapshots
from app.services.plan_v3.transactions import RuntimeFailure, guard_owner, schema_available

CONTRACT = "first-session-runtime/3.0.0"
VERSIONS = {
    "runtime": CONTRACT,
    "request": "first-plan-request/3.0.0",
    "result": "first-plan-recommendation/3.0.0",
    "execution": "first-plan-execution/3.0.0",
    "calibration": "first-calibration-encounter/1.0.0",
}


class PrivateRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def handle(request: Request):
            try:
                response = await original(request)
            except HTTPException as error:
                error.headers = {**(error.headers or {}), "Cache-Control": "no-store"}
                raise
            except RequestValidationError:
                raise HTTPException(
                    422,
                    detail={"error": "invalid_runtime_request"},
                    headers={"Cache-Control": "no-store"},
                ) from None
            except DBAPIError:
                raise HTTPException(
                    503,
                    detail={"error": "runtime_storage_unavailable"},
                    headers={"Cache-Control": "no-store"},
                ) from None
            except RuntimeFailure as error:
                raise HTTPException(
                    error.status,
                    detail={"error": error.code},
                    headers={"Cache-Control": "no-store"},
                ) from None
            except ValueError as error:
                if str(error) == "science_bundle_unavailable":
                    raise HTTPException(
                        503,
                        detail={"error": "producer_unavailable"},
                        headers={"Cache-Control": "no-store"},
                    ) from None
                raise HTTPException(
                    422,
                    detail={"error": "invalid_runtime_request"},
                    headers={"Cache-Control": "no-store"},
                ) from None
            response.headers["Cache-Control"] = "no-store"
            response.headers["X-Auren-Contract"] = CONTRACT
            return response

        return handle


def negotiate(x_auren_contract: Annotated[str | None, Header()] = None):
    if x_auren_contract != CONTRACT:
        raise RuntimeFailure("contract_not_supported", 406)


router = APIRouter(
    prefix="/api/mobile/v3", route_class=PrivateRoute, dependencies=[Depends(negotiate)]
)


class Command(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", hide_input_in_errors=True)
    request_id: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9:_-]+$")


class DeclarationsBody(Command):
    fields: dict


class ObservationBody(Command):
    expected_revision: int = Field(ge=0)
    event: dict


class CaptureBody(Command):
    expected_revision: int = Field(ge=0)


def controlled_enabled() -> bool:
    settings = get_settings()
    return settings.app_env == "test" and settings.plan_v3_controlled_test_enabled


def require_controlled(db, flag: str):
    settings = get_settings()
    if not controlled_enabled() or not getattr(settings, flag) or not schema_available(db):
        raise RuntimeFailure("runtime_not_served", 503)


def authenticate_current(request: Request, user, db):
    guard_owner(
        db,
        user.id,
        expected_epoch=user.session_epoch,
        expected_hash=user.password_hash,
        device_id=request.state.device_session.id,
    )


def envelope(**data):
    return {"contract_version": CONTRACT, "versions": VERSIONS, **data}


@router.get("/me/first-plan/capabilities")
def capabilities(user: ApiUser, db: DbSession):
    current = None
    selection = []
    pilot = None
    protocol_material = None
    if controlled_enabled() and schema_available(db):
        from app.services.plan_v3.authority import lock_authority

        try:
            operational, authorities, pins = lock_authority(db)
            policy = authorities["v3"]["policy"]
            pilot_id = authorities["encounter"]["policy"]["scope"]["candidate_id"]
            selection = [
                {
                    **spec,
                    "display_name": authorities["v3"]["catalogue_labels"][spec["candidate_id"]],
                    "initial_guidance_supported": spec["candidate_id"] == pilot_id,
                }
                for spec in policy["selection"]
            ]
            pilot = next(row for row in selection if row["candidate_id"] == pilot_id)
            protocol_material = authorities["encounter"]["protocol_material"]
            current = {
                "generation": operational.generation,
                "pins": pins,
                "state": operational.state,
                "engine_version": policy["engine_version"],
                "policy_version": policy["policy_version"],
                "binding_ref": policy["binding_ref"],
                "start_policy_ref": policy["time"]["start_policy_ref"],
                "encounter_bundle_digest": authorities["encounter"]["bundle_digest"],
            }
        except RuntimeFailure:
            current = None
    return envelope(
        owner_id=user.id,
        runtime_availability="NOT_SERVED",
        controlled_test_available=controlled_enabled() and schema_available(db),
        controlled_authority=current,
        supported_realizations=selection,
        initial_calibration_pilot=pilot,
        calibration_protocol_material=protocol_material,
        controlled_guidance_available=controlled_enabled()
        and get_settings().plan_v3_guidance_enabled,
    )


@router.get("/me/blueprint/declarations")
def declarations(user: ApiUser, db: DbSession):
    # Reads/reconciliation survive a rollback of acquisition and creation.
    if not schema_available(db):
        raise RuntimeFailure("runtime_not_served", 503)
    from sqlalchemy import select

    from app.models.first_plan_runtime import FirstPlanEvaluation

    rows = snapshots.events(db, user.id)
    captures = list(
        db.scalars(select(OwnedBlueprintSnapshot).where(OwnedBlueprintSnapshot.owner_id == user.id))
    )
    evaluations = list(
        db.scalars(select(FirstPlanEvaluation).where(FirstPlanEvaluation.owner_id == user.id))
    )
    return envelope(
        owner_id=user.id,
        source_revision=snapshots.current_revision(db, user.id),
        blueprint=snapshots.blueprint_from_events(rows, "declarations:current"),
        subject_ref=snapshots.subject_ref(user.id),
        observation_progress=snapshots.observation_progress(rows),
        receipts={
            "sources": [
                {
                    "request_id": r.request_id,
                    "event_ref": r.id,
                    "source_revision": r.source_revision,
                    "kind": r.kind,
                }
                for r in rows
            ],
            "snapshots": [
                {
                    "request_id": r.request_id,
                    "snapshot_ref": r.id,
                    "source_revision": r.source_revision,
                }
                for r in captures
            ],
            "evaluations": [
                {
                    "request_id": r.request_id,
                    "evaluation_ref": r.id,
                    "snapshot_ref": r.snapshot_id,
                    "operation_kind": r.operation_kind,
                }
                for r in evaluations
            ],
        },
    )


@router.put("/me/blueprint/declarations")
def write_declarations(
    body: DeclarationsBody,
    request: Request,
    user: ApiUser,
    db: DbSession,
    if_match: Annotated[str | None, Header()] = None,
):
    require_controlled(db, "plan_v3_acquisition_enabled")
    if if_match is None or not if_match.isdecimal():
        raise RuntimeFailure("source_revision_required", 409)
    authenticate_current(request, user, db)
    row = snapshots.declare(
        db, user.id, request_id=body.request_id, expected_revision=int(if_match), fields=body.fields
    )
    db.commit()
    return envelope(owner_id=user.id, source_revision=row.source_revision, event_ref=row.id)


def project_snapshot(row):
    return envelope(
        owner_id=row.owner_id,
        snapshot_ref=row.id,
        source_revision=row.source_revision,
        as_of=row.as_of.replace(tzinfo=UTC).isoformat(),
        snapshot_digest=row.snapshot_digest,
        **json.loads(row.snapshot_json),
    )


@router.post("/me/blueprint/snapshots")
def capture(body: CaptureBody, request: Request, user: ApiUser, db: DbSession):
    require_controlled(db, "plan_v3_acquisition_enabled")
    authenticate_current(request, user, db)
    row = snapshots.build_owned_snapshot(db, user.id, **body.model_dump())
    db.commit()
    return project_snapshot(row)


@router.get("/me/blueprint/snapshots/{snapshot_ref}")
def read_snapshot(snapshot_ref: str, user: ApiUser, db: DbSession):
    if not schema_available(db):
        raise RuntimeFailure("not_found", 404)
    row = db.get(OwnedBlueprintSnapshot, snapshot_ref)
    if row is None or row.owner_id != user.id:
        raise RuntimeFailure("not_found", 404)
    return project_snapshot(row)


@router.post("/me/blueprint/observations")
def write_observation(body: ObservationBody, request: Request, user: ApiUser, db: DbSession):
    require_controlled(db, "plan_v3_acquisition_enabled")
    if body.event.get("kind") == "ENCOUNTER_OBSERVATION":
        require_calibration_negotiation(request)
        if set(body.event) != {"kind", "encounter_ref", "expected_authority", "observation"}:
            raise ValueError("invalid encounter observation envelope")
        from app.services.plan_v3.calibration import record_encounter_observation

        row = record_encounter_observation(
            db,
            user.id,
            request_id=body.request_id,
            expected_revision=body.expected_revision,
            **{key: value for key, value in body.event.items() if key != "kind"},
            auth=auth_proof(request, user),
        )
    else:
        authenticate_current(request, user, db)
        row = snapshots.append_owned_observation(db, user.id, **body.model_dump())
    db.commit()
    payload = json.loads(row.payload_json)
    return envelope(
        owner_id=user.id,
        event_ref=row.id,
        source_revision=row.source_revision,
        episode_ref=payload.get("episode_ref"),
    )


class EvaluationBody(Command):
    snapshot_ref: str = Field(min_length=1, max_length=36)
    expected_pins: dict[str, str]


class AcknowledgmentBody(Command):
    expected_context: dict[str, str]


def auth_proof(request, user):
    return {
        "expected_epoch": user.session_epoch,
        "expected_hash": user.password_hash,
        "device_id": request.state.device_session.id,
    }


def project_evaluation(row):
    return envelope(
        owner_id=row.owner_id,
        evaluation_ref=row.id,
        snapshot_ref=row.snapshot_id,
        source_revision=row.source_revision,
        authority_generation=row.authority_generation,
        operation_kind=row.operation_kind,
        parent_evaluation_ref=row.parent_evaluation_id,
        recommendation=json.loads(row.result_json),
        historical=True,
    )


@router.post("/me/first-plan/evaluations")
def evaluate_plan(body: EvaluationBody, request: Request, user: ApiUser, db: DbSession):
    from app.services.plan_v3.evaluations import evaluate_owned_snapshot

    require_controlled(db, "plan_v3_evaluation_enabled")
    row = evaluate_owned_snapshot(db, user.id, **body.model_dump(), auth=auth_proof(request, user))
    db.commit()
    return project_evaluation(row)


@router.get("/me/first-plan/evaluations/{evaluation_ref}")
def read_evaluation(evaluation_ref: str, user: ApiUser, db: DbSession):
    from app.services.plan_v3.evaluations import owned_evaluation

    if not schema_available(db):
        raise RuntimeFailure("not_found", 404)
    return project_evaluation(owned_evaluation(db, user.id, evaluation_ref))


@router.post("/me/first-plan/evaluations/{evaluation_ref}/time-acknowledgments")
def acknowledge_plan_time(
    evaluation_ref: str, body: AcknowledgmentBody, request: Request, user: ApiUser, db: DbSession
):
    from app.services.plan_v3.evaluations import acknowledge_time

    require_controlled(db, "plan_v3_evaluation_enabled")
    row = acknowledge_time(
        db,
        user.id,
        evaluation_ref=evaluation_ref,
        **body.model_dump(),
        auth=auth_proof(request, user),
    )
    db.commit()
    return project_evaluation(row)


class FirstSessionBody(Command):
    command: dict


class SetObservationBody(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", hide_input_in_errors=True)
    op_id: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9:_-]+$")
    expected_set_revision: int = Field(ge=0)
    observation: dict


def project_command(db, owner, row):
    from app.services.plan_v3.commands import read_owned_first_session_handoff

    existing = (
        read_owned_first_session_handoff(db, owner)
        if row.state == "DENIED" and row.terminal_code == "first_session_already_created"
        else None
    )
    return envelope(
        owner_id=owner,
        request_id=row.request_id,
        state=row.state,
        session_id=row.session_id,
        terminal_code=row.terminal_code,
        scientific_session_id=row.scientific_session_id,
        existing_handoff={"request_id": existing.request_id, "session_id": existing.session_id}
        if existing
        else None,
    )


@router.post("/me/first-session-requests")
def start_first_session(body: FirstSessionBody, request: Request, user: ApiUser, db: DbSession):
    from app.services.plan_v3.commands import start_owned_first_session

    require_controlled(db, "plan_v3_creation_enabled")
    row = start_owned_first_session(
        db, user.id, request_id=body.request_id, body=body.command, auth=auth_proof(request, user)
    )
    db.commit()
    return project_command(db, user.id, row)


@router.get("/me/first-session-requests/{request_id}")
def read_first_request(request_id: str, user: ApiUser, db: DbSession):
    from app.services.plan_v3.commands import read_owned_first_session_request

    return project_command(db, user.id, read_owned_first_session_request(db, user.id, request_id))


@router.post("/me/first-session-requests/{request_id}/cancel")
def cancel_first_request(
    request_id: str, body: FirstSessionBody, request: Request, user: ApiUser, db: DbSession
):
    from app.services.plan_v3.commands import cancel_owned_first_session

    if body.request_id != request_id:
        raise ValueError("request identity mismatch")
    if not schema_available(db):
        raise RuntimeFailure("runtime_not_served", 503)
    row = cancel_owned_first_session(
        db, user.id, request_id=request_id, body=body.command, auth=auth_proof(request, user)
    )
    db.commit()
    return project_command(db, user.id, row)


@router.get("/me/first-session-handoff")
def read_handoff(user: ApiUser, db: DbSession):
    from app.services.plan_v3.commands import read_owned_first_session_handoff

    row = read_owned_first_session_handoff(db, user.id)
    return envelope(
        owner_id=user.id, handoff=project_command(db, user.id, row) if row is not None else None
    )


@router.get("/sessions/{session_id}/execution")
def read_execution(session_id: int, request: Request, user: ApiUser, db: DbSession):
    from app.services.plan_v3.execution import first_plan_execution_read_model

    return envelope(
        owner_id=user.id,
        execution=first_plan_execution_read_model(
            db, user.id, session_id, auth=auth_proof(request, user)
        ),
    )


@router.put("/sessions/{session_id}/sets/{set_id}")
def record_set(
    session_id: int,
    set_id: int,
    body: SetObservationBody,
    request: Request,
    user: ApiUser,
    db: DbSession,
):
    from app.services.plan_v3.journal import record_first_plan_set

    if not schema_available(db):
        raise RuntimeFailure("not_found", 404)
    receipt = record_first_plan_set(
        db, user.id, session_id, set_id, **body.model_dump(), auth=auth_proof(request, user)
    )
    db.commit()
    return envelope(owner_id=user.id, receipt=receipt)


@router.post("/sessions/{session_id}/applicability")
def refresh_applicability(session_id: int, request: Request, user: ApiUser, db: DbSession):
    from app.services.plan_v3.execution import assess_applicability

    return envelope(
        owner_id=user.id,
        applicability=assess_applicability(db, user.id, session_id, auth=auth_proof(request, user)),
    )


class EncounterBody(CaptureBody):
    context: dict
    availability: str
    concern_state: str = "UNKNOWN"


def require_calibration_negotiation(request: Request):
    if request.headers.get("X-Auren-Calibration") != VERSIONS["calibration"]:
        raise RuntimeFailure("calibration_contract_not_supported", 406)


@router.post("/me/blueprint/calibration-encounters")
def open_calibration(body: EncounterBody, request: Request, user: ApiUser, db: DbSession):
    from app.services.plan_v3.calibration import open_encounter

    require_calibration_negotiation(request)
    require_controlled(db, "plan_v3_acquisition_enabled")
    row = open_encounter(db, user.id, **body.model_dump(), auth=auth_proof(request, user))
    db.commit()
    return envelope(owner_id=user.id, encounter_ref=row.id, source_revision=row.source_revision)


@router.get("/me/blueprint/calibration-encounters/{encounter_ref}")
def read_calibration(encounter_ref: str, request: Request, user: ApiUser, db: DbSession):
    from app.services.plan_v3.calibration import read_encounter

    require_calibration_negotiation(request)
    if not schema_available(db):
        raise RuntimeFailure("not_found", 404)
    return envelope(
        owner_id=user.id,
        encounter=read_encounter(db, user.id, encounter_ref, auth=auth_proof(request, user)),
    )
