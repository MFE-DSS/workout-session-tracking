"""MOB-03 approved read-only body adapter; canonical ownership/consent/flag."""

from __future__ import annotations

import base64
import json
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from app.deps import ApiUser, DbSession
from app.routers.body import require_body_enabled
from app.services import body_profile


class _PrivateBodyReadRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def handle(request: Request) -> Response:
            try:
                response = await original(request)
                response.headers["Cache-Control"] = "no-store"
                return response
            except RequestValidationError:
                return JSONResponse(
                    status_code=422,
                    content={"detail": {"error": "invalid_weight_history_query"}},
                    headers={"Cache-Control": "no-store"},
                )
            except HTTPException as error:
                raise HTTPException(
                    error.status_code,
                    detail=error.detail,
                    headers={**(error.headers or {}), "Cache-Control": "no-store"},
                ) from None
            except Exception:
                # Do not serialize a DB exception or a sensitive source row in an error.
                return JSONResponse(
                    status_code=503,
                    content={"detail": {"error": "weight_history_unavailable"}},
                    headers={"Cache-Control": "no-store"},
                )

        return handle


router = APIRouter(
    prefix="/me/body",
    route_class=_PrivateBodyReadRoute,
    dependencies=[Depends(require_body_enabled)],
)


def _cursor(raw: str | None) -> tuple[datetime, int] | None:
    if raw is None:
        return None
    try:
        value = json.loads(
            base64.b64decode(raw + "=" * (-len(raw) % 4), altchars=b"-_", validate=True)
        )
        if not isinstance(value, list) or len(value) != 2 or not isinstance(value[0], str):
            raise ValueError
        if type(value[1]) is not int or not 0 < value[1] < 2**63:
            raise ValueError
        when = datetime.fromisoformat(value[0].replace("Z", "+00:00"))
        if when.tzinfo is None or when.utcoffset() is None:
            raise ValueError
        return when.astimezone(UTC), value[1]
    except (ValueError, TypeError, UnicodeError):
        raise HTTPException(400, detail={"error": "invalid_weight_history_cursor"}) from None


@router.get("/weight-history")
def weight_history(
    user: ApiUser,
    db: DbSession,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    cursor: Annotated[str | None, Query(max_length=256)] = None,
) -> dict:
    before = _cursor(cursor)
    page = body_profile.weight_history_page(db, user.id, limit=limit, before=before)
    if page["state"] == "CONSENT_REQUIRED":
        raise HTTPException(403, detail={"error": "body_consent_required"})
    if page["next_cursor"] is not None:
        page["next_cursor"] = (
            base64.urlsafe_b64encode(
                json.dumps(page["next_cursor"], separators=(",", ":")).encode(),
            )
            .decode()
            .rstrip("=")
        )
    return page
