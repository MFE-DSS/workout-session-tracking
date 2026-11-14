"""Owned library HTTP adapter; composition config is explicit and default closed.

create_library_router is separately mountable for synthetic consumer proofs.
The production parent/config lease is not inferred from an isolated test mount.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from pydantic import BaseModel, ConfigDict, Field, StrictStr, ValidationError

from app.deps import ApiUser, DbSession
from app.services.library_read_model import (
    VERSION,
    LibraryContext,
    LibraryError,
    read_library,
    read_library_item,
    request_digest,
)
from app.services.library_start import start_library_session

HEADER = "X-Auren-Library-Contract"
_DEFINITE = {
    (403, "acquisition_unavailable"),
    (404, "foreign_or_missing"),
    (406, "unsupported_contract"),
    (409, "stale_selection"),
    (409, "session_open"),
    (409, "start_blocked"),
    (413, "source_too_large"),
    (422, "invalid_request"),
}


@dataclass(frozen=True)
class LibraryRuntime:
    backend_identity: str
    signing_key: str = field(repr=False)
    controlled_test_enabled: bool = False
    app_env: str = ""


class LibraryStartBody(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    contract_version: StrictStr = Field(min_length=1, max_length=64)
    selection_ref: StrictStr = Field(min_length=1, max_length=4096)


class LibraryRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def handle(request):
            headers = {"Cache-Control": "no-store", HEADER: VERSION}
            try:
                if request.method == "POST":
                    chunks, size = [], 0
                    async for chunk in request.stream():
                        size += len(chunk)
                        if size > 8192:
                            raise LibraryError("source_too_large", 413)
                        chunks.append(chunk)
                    # Starlette Request.body cache, bounded before JSON parsing.
                    request._body = b"".join(chunks)
                response = await original(request)
            except LibraryError as error:
                content = {"detail": {"error": error.code}}
                owner = getattr(request.state, "library_owner", None)
                digest = getattr(request.state, "library_request_sha256", None)
                if (
                    owner is not None
                    and digest is not None
                    and (error.status, error.code) in _DEFINITE
                ):
                    content = {
                        "contract_version": VERSION,
                        "owner_id": owner,
                        "request_sha256": digest,
                        "effect": "NOT_CREATED",
                        "code": error.code,
                    }
                return JSONResponse(status_code=error.status, content=content, headers=headers)
            except (RequestValidationError, ValidationError):
                return JSONResponse(
                    status_code=422,
                    content={"detail": {"error": "invalid_request"}},
                    headers=headers,
                )
            except HTTPException as error:
                return JSONResponse(
                    status_code=error.status_code,
                    content={"detail": error.detail},
                    headers={**(error.headers or {}), **headers},
                )
            except Exception:
                # Includes an uncertain commit failure: no definitive refusal.
                return JSONResponse(
                    status_code=503,
                    content={"detail": {"error": "storage_unavailable"}},
                    headers=headers,
                )
            response.headers.update(headers)
            return response

        return handle


def _query(request, allowed):
    if set(request.query_params) - allowed or any(
        len(request.query_params.getlist(k)) != 1 for k in request.query_params
    ):
        raise LibraryError("invalid_request")


def create_library_router(runtime: LibraryRuntime):
    router = APIRouter(prefix="/me/library", route_class=LibraryRoute)

    def context(request, user):
        request.state.library_owner = user.id
        if request.headers.getlist(HEADER) != [VERSION]:
            raise LibraryError("unsupported_contract", 406)
        return LibraryContext(
            user.id, runtime.backend_identity, runtime.signing_key, user.session_epoch
        )

    @router.get("")
    def listing(
        request: Request,
        user: ApiUser,
        db: DbSession,
        section: str = "all",
        zone: Annotated[str | None, Query(max_length=100)] = None,
        limit: Annotated[int, Query(ge=1, le=100)] = 30,
        cursor: Annotated[str | None, Query(min_length=1, max_length=4096)] = None,
    ):
        ctx = context(request, user)
        _query(request, {"section", "zone", "limit", "cursor"})
        return read_library(db, ctx, section=section, zone=zone, limit=limit, cursor=cursor)

    @router.get("/items/{source_ref}")
    def detail(
        request: Request,
        user: ApiUser,
        db: DbSession,
        source_ref: Annotated[str, Path(min_length=1, max_length=4096)],
    ):
        ctx = context(request, user)
        _query(request, set())
        return read_library_item(db, ctx, source_ref)

    @router.post("/start", status_code=201)
    async def start(request: Request, user: ApiUser, db: DbSession):
        try:
            body = LibraryStartBody.model_validate_json(await request.body())
        except (ValidationError, ValueError):
            raise LibraryError("invalid_request") from None
        request.state.library_request_sha256 = request_digest(body.model_dump())
        ctx = context(request, user)
        _query(request, set())
        if body.contract_version != VERSION:
            raise LibraryError("unsupported_contract", 406)
        ds = request.state.device_session
        result = start_library_session(
            db,
            ctx,
            body.selection_ref,
            expected_epoch=user.session_epoch,
            expected_hash=user.password_hash,
            device_id=ds.id,
            controlled_test_enabled=runtime.controlled_test_enabled is True,
            app_env=runtime.app_env,
        )
        return {**result, "request_sha256": request.state.library_request_sha256}

    return router
