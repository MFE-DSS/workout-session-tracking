"""Real owner Bearer adapter; exact replay is checked before fresh preconditions."""

import json
import re
from dataclasses import dataclass, field
from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from app.deps import ApiUser, DbSession
from app.services.mobile_program_builder import page
from app.services.plan_v3.transactions import RuntimeFailure, guard_owner
from app.services.program_builder_commands import (
    MAX_BYTES,
    VERSION,
    ProgramBuilderError,
    apply_command,
    canonical_command,
    command_digest,
    read_program,
    read_receipt,
)
from app.services.program_builder_transactions import owner_transaction

HEADER = "X-Auren-Program-Builder"


@dataclass(frozen=True)
class ProgramBuilderRuntime:
    backend_identity: str
    signing_key: str = field(repr=False)
    controlled_test_enabled: bool = False
    app_env: str = ""


class BuilderRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def handle(request):
            headers = {"Cache-Control": "no-store", HEADER: VERSION}
            try:
                if request.method == "POST":
                    chunks = []
                    size = 0
                    async for chunk in request.stream():
                        size += len(chunk)
                        if size > MAX_BYTES:
                            raise ProgramBuilderError("source_too_large", 413)
                        chunks.append(chunk)
                    request._body = b"".join(chunks)
                response = await original(request)
                response.headers.update(headers)
                return response
            except (ProgramBuilderError, RuntimeFailure) as error:
                return JSONResponse(
                    status_code=error.status,
                    content={"detail": {"error": error.code}},
                    headers=headers,
                )
            except RequestValidationError:
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
                # A storage/commit failure is uncertain, never NOT_APPLIED.
                return JSONResponse(
                    status_code=503,
                    content={"detail": {"error": "storage_unavailable"}},
                    headers=headers,
                )

        return handle


def _query(request, allowed):
    if set(request.query_params) - allowed or any(
        len(request.query_params.getlist(k)) != 1 for k in request.query_params
    ):
        raise ProgramBuilderError("invalid_request")


def _pairs(pairs):
    result = {}
    for k, v in pairs:
        if k in result:
            raise ProgramBuilderError("invalid_request")
        result[k] = v
    return result


def create_program_builder_router(runtime):
    router = APIRouter(prefix="/api/mobile/v1/me/program-builder", route_class=BuilderRoute)

    def context(request, user):
        current = runtime() if callable(runtime) else runtime
        if request.headers.getlist(HEADER) != [VERSION]:
            raise ProgramBuilderError("unsupported_contract", 406)
        if not current.backend_identity or not current.signing_key:
            raise ProgramBuilderError("configuration_unavailable", 503)
        return current

    def proof(request, user):
        return {
            "expected_epoch": user.session_epoch,
            "expected_hash": user.password_hash,
            "device_id": request.state.device_session.id,
        }

    @router.get("/exercises")
    def exercises(
        request: Request,
        user: ApiUser,
        db: DbSession,
        limit: Annotated[int, Query(ge=1, le=50)] = 25,
        cursor: Annotated[str | None, Query(max_length=4096)] = None,
    ):
        current = context(request, user)
        _query(request, {"limit", "cursor"})
        with owner_transaction(db, user.id, auth_proof=proof(request, user), commit=False):
            return page(db, user.id, current, "exercises", limit, cursor)

    @router.get("/programs")
    def programs(
        request: Request,
        user: ApiUser,
        db: DbSession,
        limit: Annotated[int, Query(ge=1, le=50)] = 25,
        cursor: Annotated[str | None, Query(max_length=4096)] = None,
    ):
        current = context(request, user)
        _query(request, {"limit", "cursor"})
        with owner_transaction(db, user.id, auth_proof=proof(request, user), commit=False):
            return page(db, user.id, current, "programs", limit, cursor)

    @router.get("/programs/{program_id}")
    def program(
        request: Request,
        user: ApiUser,
        db: DbSession,
        program_id: Annotated[int, Path(ge=1, le=9007199254740991)],
    ):
        context(request, user)
        _query(request, set())
        with owner_transaction(db, user.id, auth_proof=proof(request, user), commit=False):
            return {
                "contract_version": VERSION,
                "owner_id": user.id,
                "program": read_program(db, user.id, program_id),
            }

    @router.get("/operations/{command_id}")
    def operation(
        request: Request,
        user: ApiUser,
        db: DbSession,
        command_id: Annotated[str, Path(min_length=1, max_length=128)],
    ):
        context(request, user)
        _query(request, set())
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", command_id):
            raise ProgramBuilderError("invalid_request")
        guard_owner(db, user.id, **proof(request, user))
        receipt = read_receipt(db, user.id, command_id)
        if receipt is None:
            raise ProgramBuilderError("foreign_or_missing", 404)
        return receipt

    @router.post("/commands")
    async def command(request: Request, user: ApiUser, db: DbSession):
        current = context(request, user)
        _query(request, set())
        try:
            body = canonical_command(
                json.loads(
                    await request.body(),
                    object_pairs_hook=_pairs,
                    parse_constant=lambda _: (_ for _ in ()).throw(ValueError()),
                )
            )
        except (ValueError, TypeError, UnicodeDecodeError, RecursionError) as error:
            if isinstance(error, ProgramBuilderError):
                raise
            raise ProgramBuilderError("invalid_request") from None
        return _execute_command(request, db, user, body, current, proof(request, user))

    return router


def _execute_command(request, db, user, body, current, auth_proof):
    with owner_transaction(db, user.id, auth_proof=auth_proof):
        receipt = read_receipt(db, user.id, body["command_id"])
        if receipt:
            if receipt["request_sha256"] != command_digest(body):
                raise ProgramBuilderError("command_conflict", 409)
            return receipt
        if body["operation"] == "CREATE":
            values = request.headers.getlist("If-None-Match")
            if not values:
                raise ProgramBuilderError("precondition_required", 428)
            if values != ["*"]:
                raise ProgramBuilderError("invalid_precondition", 400)
        else:
            values = request.headers.getlist("If-Match")
            if not values:
                raise ProgramBuilderError("precondition_required", 428)
            if values != [body["expected_source_digest"]]:
                raise ProgramBuilderError("invalid_precondition", 400)
        return apply_command(
            db,
            user.id,
            body,
            auth_proof=auth_proof,
            controlled=current.controlled_test_enabled is True and current.app_env == "test",
        )


def configured_program_builder_runtime():
    from app.config import get_settings

    settings = get_settings()
    return ProgramBuilderRuntime(
        settings.program_builder_backend_identity,
        settings.program_builder_signing_key.get_secret_value(),
        settings.program_builder_controlled_test_enabled,
        settings.app_env,
    )
