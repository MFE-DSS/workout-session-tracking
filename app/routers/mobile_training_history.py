"""Owned read-only history adapter. No body, workout or planning writer."""

from __future__ import annotations

from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Path, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from app.deps import ApiUser, DbSession
from app.services.training_history_reads import (
    HistoryReadError,
    read_exercises,
    read_occurrences,
    read_session_facts,
    read_sessions,
)


class HistoryRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def handle(request):
            headers = {"Cache-Control": "no-store"}
            try:
                response = await original(request)
            except RequestValidationError:
                return JSONResponse(
                    status_code=422,
                    content={"detail": {"error": "invalid_training_history_query"}},
                    headers=headers,
                )
            except HistoryReadError as error:
                return JSONResponse(
                    status_code=error.status,
                    content={
                        "detail": {
                            "error": "invalid_training_history_query"
                            if error.status == 422
                            else error.code
                        }
                    },
                    headers=headers,
                )
            except HTTPException as error:
                raise HTTPException(
                    error.status_code,
                    detail=error.detail,
                    headers={**(error.headers or {}), **headers},
                ) from None
            except Exception:
                # Never serialize failing SQL, a source row or an opaque private token.
                return JSONResponse(
                    status_code=503,
                    content={"detail": {"error": "training_history_unavailable"}},
                    headers=headers,
                )
            response.headers.update(headers)
            return response

        return handle


def _query(request, allowed):
    if set(request.query_params) - allowed or any(
        len(request.query_params.getlist(key)) != 1 for key in request.query_params
    ):
        raise HistoryReadError("invalid_training_history_query", 422)


router = APIRouter(prefix="/me/training-history", route_class=HistoryRoute)
Limit = Annotated[int, Query(ge=1, le=100)]
Reference = Annotated[str, Query(min_length=1, max_length=16384)]
Cursor = Annotated[str | None, Query(min_length=1, max_length=16384)]


@router.get("")
def session_history(
    request: Request,
    user: ApiUser,
    db: DbSession,
    period: Literal["4w", "12w", "all"],
    time_zone: Annotated[str, Query(min_length=1, max_length=100)],
    limit: Limit = 50,
    cursor: Cursor = None,
):
    _query(request, {"period", "time_zone", "limit", "cursor"})
    return read_sessions(
        db, user.id, period=period, time_zone=time_zone, limit=limit, cursor=cursor
    )


@router.get("/sessions/{session_id}")
def session_facts(
    request: Request,
    user: ApiUser,
    db: DbSession,
    session_id: Annotated[int, Path(ge=1, le=2**63 - 1)],
    entry_ref: Reference,
    occurrence_ref: Cursor = None,
):
    _query(request, {"entry_ref", "occurrence_ref"})
    return read_session_facts(db, user.id, session_id, entry_ref, occurrence_ref=occurrence_ref)


@router.get("/exercises")
def exercise_index(
    request: Request,
    user: ApiUser,
    db: DbSession,
    read_context: Reference,
    limit: Limit = 50,
    cursor: Cursor = None,
):
    _query(request, {"read_context", "limit", "cursor"})
    return read_exercises(db, user.id, read_context=read_context, limit=limit, cursor=cursor)


@router.get("/exercises/{exercise_ref}")
def exercise_occurrences(
    request: Request,
    user: ApiUser,
    db: DbSession,
    exercise_ref: Annotated[str, Path(min_length=1, max_length=16384)],
    read_context: Reference,
    limit: Limit = 50,
    cursor: Cursor = None,
):
    _query(request, {"read_context", "limit", "cursor"})
    return read_occurrences(
        db, user.id, exercise_ref, read_context=read_context, limit=limit, cursor=cursor
    )
