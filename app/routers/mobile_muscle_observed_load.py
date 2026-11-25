"""Versioned, disabled-by-default descriptive owned GET. No mutation routes."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from app.config import get_settings
from app.deps import ApiUser
from app.services.muscle_observed_load.contracts import (
    HEADER,
    VERSION,
    ObservedLoadReadError,
    parse_query,
)
from app.services.muscle_observed_load.supervisor import read_owned_muscle_observed_load


def error_response(code, status):
    headers = {"Cache-Control": "no-store"}
    if status == 401:
        headers["WWW-Authenticate"] = "Bearer"
    return JSONResponse(
        status_code=status,
        headers=headers,
        content=dict(
            contract_version=VERSION,
            availability="UNAVAILABLE",
            state="UNAVAILABLE",
            detail={"error": code},
        ),
    )


class ObservedLoadRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def handle(request):
            try:
                response = await original(request)
                response.headers["Cache-Control"] = "no-store"
                return response
            except ObservedLoadReadError as error:
                return error_response(error.code, error.status)
            except HTTPException as error:
                return error_response(
                    "unauthorized"
                    if error.status_code == 401
                    else "muscle_observed_load_unavailable",
                    401 if error.status_code == 401 else 503,
                )
            except RequestValidationError:
                return error_response("invalid_muscle_observed_load_query", 422)
            except Exception:
                return error_response("muscle_observed_load_unavailable", 503)

        return handle


router = APIRouter(prefix="/me/muscle-observed-load", route_class=ObservedLoadRoute)


@router.get("")
async def muscle_observed_load(request: Request, user: ApiUser):
    async for chunk in request.stream():
        if chunk:
            raise ObservedLoadReadError("invalid_muscle_observed_load_query", 422)
    contracts = request.headers.getlist(HEADER)
    if len(contracts) > 1:
        raise ObservedLoadReadError("muscle_observed_load_contract_unsupported", 406)
    query = parse_query(
        list(request.query_params.multi_items()),
        contracts[0] if contracts else None,
        as_of=datetime.now(UTC),
    )
    settings = get_settings()
    if not settings.muscle_observed_load_enabled:
        raise ObservedLoadReadError()
    # Blocking process I/O runs outside the event loop; the supervisor rejects busy,
    # rather than queueing a second worker behind an active one.
    from starlette.concurrency import run_in_threadpool

    response = await run_in_threadpool(
        read_owned_muscle_observed_load,
        user.id,
        query,
        runtime_profile=(
            settings.muscle_observed_load_profile_path,
            settings.muscle_observed_load_profile_sha256,
        ),
        database_url=settings.database_url,
        bundle_root=settings.plan_v3_bundle_path,
    )
    return response.model_dump()
