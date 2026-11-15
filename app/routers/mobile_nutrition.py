"""Controlled manual nutrition only. No provider, recommendation or implicit consent."""

from __future__ import annotations

import asyncio
import copy
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from sqlalchemy import select

from app.config import get_settings
from app.deps import ApiUser, DbSession
from app.models.nutrition import NutritionDayRevision as Day
from app.models.nutrition import NutritionTargetRevision as Target
from app.services.nutrition_commands import NutritionError, apply_command, decode_command
from app.services.nutrition_consent import WORDING_VERSION, read_consent, set_consent
from app.services.nutrition_reads import (
    read_days,
    read_export,
    read_head,
    read_targets,
    read_versions,
)
from app.services.nutrition_schema import nutrition_schema_available

CONTRACT = "nutrition-manual/1.0.0"
HEADER = "X-Auren-Nutrition-Contract"


def _external_code(status, code):
    allowed = {
        403: {"consent_required", "acquisition_unavailable"},
        409: {"stale_head", "stale_target", "stale_consent", "idempotency_mismatch"},
    }
    if code in allowed.get(status, set()):
        return code
    return {401: "auth", 404: "foreign_or_missing", 406: "unsupported_contract",
            422: "invalid_command"}.get(status, "storage_unavailable")


class NutritionRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def handle(request):
            headers = {"Cache-Control": "no-store", HEADER: CONTRACT}
            try:
                result = await original(request)
                result.headers.update(headers)
                return result
            except NutritionError as exc:
                status, code = exc.status, exc.code
            except RequestValidationError:
                status, code = 422, "invalid_command"
            except HTTPException as exc:
                return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail},
                                    headers={**(exc.headers or {}), **headers})
            except Exception:
                status, code = 503, "storage_unavailable"
            if status == 401:
                headers["WWW-Authenticate"] = "Bearer"
            code = _external_code(status, code)
            return JSONResponse(status_code=status, content={"detail": {"error": code}}, headers=headers)

        return handle


def negotiate(request: Request):
    if request.headers.getlist(HEADER) != [CONTRACT]:
        raise NutritionError("unsupported_contract", 406)


router = APIRouter(prefix="/me/nutrition", route_class=NutritionRoute, dependencies=[Depends(negotiate)])


def _query(request, allowed):
    if set(request.query_params) - allowed or any(len(request.query_params.getlist(k)) != 1 for k in request.query_params):
        raise NutritionError()


def _proof(request, user):
    return {"expected_epoch": user.session_epoch, "expected_hash": user.password_hash,
            "device_id": request.state.device_session.id}


def _available(db):
    return nutrition_schema_available(db)

def _storage(db):
    if not _available(db):
        raise NutritionError("storage_unavailable", 503)


async def _body(request):
    if request.headers.get("content-type", "").split(";", 1)[0].strip().lower() != "application/json":
        raise NutritionError()
    raw = bytearray()
    try:
        async with asyncio.timeout(10):
            async for chunk in request.stream():
                raw.extend(chunk)
                if len(raw) > 16384:
                    raise NutritionError()
    except TimeoutError:
        raise NutritionError() from None
    return decode_command(bytes(raw))


@router.get("/capabilities")
def capabilities(request: Request, user: ApiUser, db: DbSession):
    _query(request, set())
    available = _available(db)
    grant = read_consent(db, user.id)
    consent = grant["granted"] and grant["wording_version"] == WORDING_VERSION
    settings = get_settings()
    return {"contract_version": CONTRACT, "owner_id": user.id, "mode": "MANUAL_DAILY",
            "state": "AVAILABLE" if available else "SCHEMA_UNAVAILABLE",
            "can_read": available and consent,
            "can_write": available and consent and settings.app_env == "test" and settings.nutrition_manual_controlled_test_enabled,
            "assisted_modes": []}


@router.get("/consent")
def get_consent(request: Request, user: ApiUser, db: DbSession):
    _query(request, set())
    return read_consent(db, user.id)


@router.post("/consent")
async def post_consent(request: Request, user: ApiUser, db: DbSession):
    auth = _proof(request, user)
    _query(request, set())
    body = await _body(request)
    if set(body) != {"contract_version", "expected_token", "granted", "wording_version"} or body["contract_version"] != CONTRACT:
        raise NutritionError()
    return set_consent(db, user.id, body["expected_token"], body["granted"], body["wording_version"], auth_proof=auth)


@router.get("/days")
def days(request: Request, user: ApiUser, db: DbSession):
    _query(request, {"from", "through", "limit", "cursor"})
    _storage(db)
    try:
        limit = int(request.query_params.get("limit", "30"))
    except ValueError:
        raise NutritionError() from None
    return read_days(db, user.id, request.query_params.get("from"), request.query_params.get("through"),
                     limit=limit, cursor=request.query_params.get("cursor"))


@router.get("/days/{day}")
def day_head(day: str, request: Request, user: ApiUser, db: DbSession):
    _query(request, set())
    _storage(db)
    return read_head(db, user.id, "DAY", day)


@router.post("/days/{day}/revisions")
async def day_command(day: str, request: Request, user: ApiUser, db: DbSession):
    auth = _proof(request, user)
    _query(request, set())
    _storage(db)
    return apply_command(db, user.id, "DAY", day, await _body(request), auth_proof=auth)


@router.get("/targets/head")
def target_head(request: Request, user: ApiUser, db: DbSession):
    _query(request, {"variant", "effective_from"})
    _storage(db)
    return read_head(db, user.id, "TARGET", (request.query_params.get("variant"), request.query_params.get("effective_from")))


@router.get("/targets")
def targets(request: Request, user: ApiUser, db: DbSession, limit: int = 100, cursor: str | None = None):
    _query(request, {"limit", "cursor"})
    _storage(db)
    return read_targets(db, user.id, limit=limit, cursor=cursor)


@router.post("/targets/revisions")
async def target_command(request: Request, user: ApiUser, db: DbSession):
    auth = _proof(request, user)
    _query(request, set())
    _storage(db)
    body = await _body(request)
    return apply_command(db, user.id, "TARGET", (body.get("variant"), body.get("effective_from")), body, auth_proof=auth)


@router.get("/days/{day}/revisions")
def day_versions(day: str, request: Request, user: ApiUser, db: DbSession, limit: int = 100, cursor: str | None = None):
    _query(request, {"limit", "cursor"})
    _storage(db)
    return read_versions(db, user.id, "DAY", day, limit=limit, cursor=cursor)


@router.get("/targets/{target_ref}/revisions")
def target_versions(target_ref: int, request: Request, user: ApiUser, db: DbSession, limit: int = 100, cursor: str | None = None):
    _query(request, {"limit", "cursor"})
    _storage(db)
    return read_versions(db, user.id, "TARGET", target_ref, limit=limit, cursor=cursor)


@router.get("/export")
def export(request: Request, user: ApiUser, db: DbSession, limit: int = 100, cursor: str | None = None):
    _query(request, {"limit", "cursor"})
    _storage(db)
    return read_export(db, user.id, limit=limit, cursor=cursor)


@router.get("/operations/{namespace}/{request_id}")
def status(namespace: Literal["DAY", "TARGET"], request_id: str, request: Request, user: ApiUser, db: DbSession):
    _query(request, set())
    _storage(db)
    model = Day if namespace == "DAY" else Target
    row = db.scalar(select(model).where(model.user_id == user.id, model.request_id == request_id))
    if row is None:
        raise NutritionError("foreign_or_missing", 404)
    return copy.deepcopy(row.receipt)
