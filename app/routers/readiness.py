"""Readiness routes — daily self-assessment."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from app.deps import CurrentUser, DbSession
from app.services.readiness import save_readiness

router = APIRouter(tags=["readiness"])


@router.post("/readiness", response_model=None)
async def readiness_submit(
    request: Request,
    sleep_quality: Annotated[str, Form()] = "",
    fatigue_level: Annotated[str, Form()] = "",
    soreness_level: Annotated[str, Form()] = "",
    stress_level: Annotated[str, Form()] = "",
    motivation_level: Annotated[str, Form()] = "",
    resting_hr: Annotated[str, Form()] = "",
    note: Annotated[str, Form()] = "",
    db: DbSession = None,
    user: CurrentUser = None,
):
    """Save today's readiness check-in and redirect to home."""
    data: dict = {}
    try:
        for field_name, raw in [
            ("sleep_quality", sleep_quality),
            ("fatigue_level", fatigue_level),
            ("soreness_level", soreness_level),
            ("stress_level", stress_level),
            ("motivation_level", motivation_level),
        ]:
            data[field_name] = int(raw)
    except (ValueError, TypeError):
        # Invalid or missing scale value — redirect home gracefully.
        return RedirectResponse(url="/", status_code=303)

    if resting_hr.strip():
        try:
            data["resting_hr"] = int(resting_hr)
        except (ValueError, TypeError):
            data["resting_hr"] = None
    else:
        data["resting_hr"] = None

    data["note"] = note.strip() or None

    try:
        save_readiness(db, user.id, data)
    except ValueError:
        # Scale validation failed — redirect gracefully.
        return RedirectResponse(url="/", status_code=303)

    return RedirectResponse(url="/", status_code=303)
