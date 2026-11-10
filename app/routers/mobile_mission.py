"""Negotiated owned Today projection; legacy /mission remains unchanged."""

from __future__ import annotations

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from sqlalchemy.exc import DBAPIError

from app.deps import ApiUser, DbSession
from app.services.mission_action import VERSION, project_mission_action
from app.services.plan_v3.transactions import RuntimeFailure

HOST = "first-session-runtime/3.0.0"


def private_headers(request):
    headers = {"Cache-Control": "no-store"}
    if request.headers.getlist("X-Auren-Mission-Action") == [VERSION]:
        headers["X-Auren-Mission-Action"] = VERSION
    if request.headers.getlist("X-Auren-Mission-V3-Host") == [HOST]:
        headers["X-Auren-Mission-V3-Host"] = HOST
    return headers


class MissionRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def handle(request):
            headers = private_headers(request)
            try:
                response = await original(request)
            except HTTPException as error:
                raise HTTPException(
                    error.status_code,
                    detail=error.detail,
                    headers={**(error.headers or {}), **headers},
                ) from None
            except RequestValidationError:
                raise HTTPException(
                    422, detail={"error": "invalid_mission_query"}, headers=headers
                ) from None
            except (DBAPIError, RuntimeFailure, ValueError):
                raise HTTPException(
                    503, detail={"error": "mission_action_unavailable"}, headers=headers
                ) from None
            response.headers.update(headers)
            return response

        return handle


def negotiate(request: Request):
    if request.headers.getlist("X-Auren-Mission-Action") != [VERSION]:
        raise HTTPException(406, detail={"error": "mission_contract_not_supported"})
    hosts = request.headers.getlist("X-Auren-Mission-V3-Host")
    if hosts not in ([], [HOST]):
        raise HTTPException(406, detail={"error": "mission_host_not_supported"})
    if (
        set(request.query_params) != {"requested_path"}
        or len(request.query_params.getlist("requested_path")) != 1
    ):
        raise HTTPException(422, detail={"error": "invalid_mission_query"})


router = APIRouter(route_class=MissionRoute, dependencies=[Depends(negotiate)])


@router.get("/mission-action")
def mission_action(
    request: Request,
    user: ApiUser,
    db: DbSession,
    requested_path: Annotated[Literal["FIRST_USE", "HISTORICAL"], Query()],
):
    return project_mission_action(
        db, user.id, requested_path, v3_host=request.headers.get("X-Auren-Mission-V3-Host") == HOST
    )
