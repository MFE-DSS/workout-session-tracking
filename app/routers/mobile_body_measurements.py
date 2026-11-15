"""BODY-01 owned native boundary, enabled only for controlled writes."""

from __future__ import annotations

import re
from datetime import UTC, date, datetime, timedelta
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_settings
from app.deps import ApiUser, DbSession
from app.models.body_measurement_operation import BodyMeasurementOperation as Operation
from app.services import body_profile
from app.services.body_measurement_commands import apply_command, require_schema, validate_command
from app.services.body_measurement_reads import (
    CONTRACT,
    BodyCommandError,
    canonical_digest,
    instant,
    owned_document,
    owned_erasure_document,
    owned_head,
    page,
)
from app.services.plan_v3.transactions import RuntimeFailure, guard_owner

HEADER = "X-Auren-Body-Contract"


class _PrivateBodyRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def handle(request):
            headers = {"Cache-Control": "no-store", HEADER: CONTRACT}
            try:
                response = await original(request)
                response.headers.update(headers)
                return response
            except HTTPException as exc:
                exc.headers = {**(exc.headers or {}), **headers}
                raise
            except (BodyCommandError, RuntimeFailure) as exc:
                if exc.status == 401:
                    headers["WWW-Authenticate"] = "Bearer"
                raise HTTPException(
                    exc.status, detail={"error": exc.code}, headers=headers
                ) from None
            except RequestValidationError:
                raise HTTPException(
                    422, detail={"error": "invalid_body_request"}, headers=headers
                ) from None
            except SQLAlchemyError:
                raise HTTPException(
                    503, detail={"error": "body_storage_unavailable"}, headers=headers
                ) from None

        return handle


def _negotiate(request: Request):
    if request.headers.get(HEADER) != CONTRACT:
        raise HTTPException(406, detail={"error": "body_contract_not_supported"})


router = APIRouter(
    prefix="/me/body", route_class=_PrivateBodyRoute, dependencies=[Depends(_negotiate)]
)


def _read_gate(db, owner_id, *, consent=True):
    if not get_settings().body_assessment_enabled:
        raise BodyCommandError("body_not_served", 404)
    require_schema(db)
    if consent and not body_profile.has_active_consent(db, owner_id):
        raise BodyCommandError("body_consent_required", 403)


def _authenticate_current(request, user, db):
    guard_owner(
        db,
        user.id,
        expected_epoch=user.session_epoch,
        expected_hash=user.password_hash,
        device_id=request.state.device_session.id,
    )


def _new_write_gate(operation):
    settings = get_settings()
    if settings.app_env != "test":
        raise BodyCommandError("body_write_not_served", 503)
    if operation != "ERASE" and not settings.body_assessment_enabled:
        raise BodyCommandError("body_not_served", 404)


def _write(request, user, db, body, operation, root_ref=None):
    allowed = (
        {"request_id", "values", "measured_on"}
        if operation == "CREATE"
        else (
            {"request_id", "values", "measured_on", "expected_head_token"}
            if operation == "CORRECT"
            else {"request_id", "expected_head_token", "confirm_all_versions"}
        )
    )
    if not isinstance(body, dict) or set(body) - allowed:
        raise BodyCommandError("invalid_body_request", 422)
    command = {**body, "operation": operation}
    if root_ref is not None:
        command["root_ref"] = root_ref
    # Reject malformed request identities before attempting a SQL lookup.
    validate_command(command, check_bounds=False)
    require_schema(db)
    _authenticate_current(request, user, db)
    prior = db.scalar(
        select(Operation.id).where(
            Operation.owner_id == user.id, Operation.request_id == body.get("request_id")
        )
    )
    if prior is None:
        _new_write_gate(operation)
    return apply_command(
        db,
        user.id,
        command,
        source="MANUAL_CORRECTION" if operation == "CORRECT" else "MANUAL_ENTRY",
    )


def _day(value):
    try:
        result = date.fromisoformat(value)
        if result.isoformat() != value or result > datetime.now(UTC).date():
            raise ValueError
        return result
    except (TypeError, ValueError):
        raise BodyCommandError("invalid_body_range", 422) from None


@router.get("/measurements")
def measurements(
    user: ApiUser,
    db: DbSession,
    from_: Annotated[str | None, Query(alias="from")] = None,
    through: str | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    cursor: Annotated[str | None, Query(max_length=4096)] = None,
    purpose: Literal["facts", "erasure"] = "facts",
):
    if purpose == "erasure":
        require_schema(db)
        _new_write_gate("ERASE")
        if from_ is None and through is None:
            return page(db, user.id, kind="ERASURE", limit=limit, cursor=cursor)
    else:
        _read_gate(db, user.id)
    end = _day(through) if through else datetime.now(UTC).date()
    start = _day(from_) if from_ else end - timedelta(days=365)
    if not 0 <= (end - start).days <= 365:
        raise BodyCommandError("invalid_body_range", 422)
    return page(
        db, user.id, kind="ERASURE" if purpose == "erasure" else "CURRENT",
        from_day=start, through_day=end, limit=limit, cursor=cursor
    )


@router.get("/measurements/export")
def export(
    user: ApiUser,
    db: DbSession,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    cursor: Annotated[str | None, Query(max_length=4096)] = None,
):
    _read_gate(db, user.id)
    return page(db, user.id, kind="EXPORT", limit=limit, cursor=cursor)


@router.get("/measurements/weight-history")
def weight_history(
    user: ApiUser,
    db: DbSession,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    cursor: Annotated[str | None, Query(max_length=4096)] = None,
):
    # Same all-history pagination as the existing weight reader, with the
    # new source-aware DTO. Explicit date-range entry lists remain <=366d.
    _read_gate(db, user.id)
    return page(db, user.id, kind="WEIGHT", limit=limit, cursor=cursor)


@router.post("/measurements")
def create(body: dict, request: Request, user: ApiUser, db: DbSession):
    return _write(request, user, db, body, "CREATE")


@router.get("/measurements/{root_ref}")
def measurement(
    root_ref: int, user: ApiUser, db: DbSession,
    purpose: Literal["facts", "erasure"] = "facts",
):
    if purpose == "erasure":
        require_schema(db)
        _new_write_gate("ERASE")
        return {
            "contract_version": CONTRACT, "owner_id": user.id,
            "projection": "ERASURE_ONLY",
            "entry": owned_erasure_document(db, user.id, root_ref),
        }
    _read_gate(db, user.id, consent=False)
    owned_head(db, user.id, root_ref)
    if not body_profile.has_active_consent(db, user.id):
        raise BodyCommandError("body_consent_required", 403)
    return {
        "contract_version": CONTRACT,
        "owner_id": user.id,
        "entry": owned_document(db, user.id, root_ref),
    }


@router.get("/measurements/{root_ref}/versions")
def versions(
    root_ref: int,
    user: ApiUser,
    db: DbSession,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    cursor: Annotated[str | None, Query(max_length=4096)] = None,
):
    _read_gate(db, user.id, consent=False)
    owned_head(db, user.id, root_ref)
    if not body_profile.has_active_consent(db, user.id):
        raise BodyCommandError("body_consent_required", 403)
    return page(db, user.id, kind="VERSIONS", root_ref=root_ref, limit=limit, cursor=cursor)


@router.post("/measurements/{root_ref}/corrections")
def correct(root_ref: int, body: dict, request: Request, user: ApiUser, db: DbSession):
    return _write(request, user, db, body, "CORRECT", root_ref)


@router.post("/measurements/{root_ref}/erase")
def erase(root_ref: int, body: dict, request: Request, user: ApiUser, db: DbSession):
    return _write(request, user, db, body, "ERASE", root_ref)


@router.get("/operations/{request_id}")
def operation(request_id: str, user: ApiUser, db: DbSession):
    require_schema(db)
    prior = db.scalar(
        select(Operation).where(Operation.owner_id == user.id, Operation.request_id == request_id)
    )
    if prior is None:
        raise BodyCommandError("body_operation_unknown", 404)
    return prior.receipt


def _consent(db, owner_id):
    row = body_profile.get_consent(db, owner_id)
    state = {
        "granted": bool(row and row.granted),
        "consent_version": body_profile.CONSENT_TEXT_VERSION,
        "granted_at": instant(row.granted_at) if row else None,
        "withdrawn_at": instant(row.withdrawn_at) if row else None,
    }
    return {
        "contract_version": CONTRACT,
        "owner_id": owner_id,
        **state,
        "consent_token": canonical_digest({"owner": owner_id, **state}),
    }


@router.get("/consent")
def consent(user: ApiUser, db: DbSession):
    _read_gate(db, user.id, consent=False)
    return _consent(db, user.id)


@router.post("/consent")
def set_consent(body: dict, request: Request, user: ApiUser, db: DbSession):
    if (
        set(body) != {"granted", "consent_version", "expected_consent_token"}
        or type(body["granted"]) is not bool
        or type(body["consent_version"]) is not int
        or not isinstance(body["expected_consent_token"], str)
        or re.fullmatch(r"[a-f0-9]{64}", body["expected_consent_token"]) is None
        or body["consent_version"] != body_profile.CONSENT_TEXT_VERSION
    ):
        raise BodyCommandError("invalid_consent_request", 422)
    require_schema(db)
    _authenticate_current(request, user, db)
    _new_write_gate("CREATE" if body["granted"] else "ERASE")
    current = _consent(db, user.id)
    if body["expected_consent_token"] != current["consent_token"]:
        if current["granted"] == body["granted"]:
            db.rollback()
            return current
        raise BodyCommandError("consent_conflict")
    if current["granted"] != body["granted"]:
        body_profile.set_consent(db, user.id, body["granted"])
    else:
        db.rollback()
    return _consent(db, user.id)
