"""Sb_Body_01 — Manual Body Profile routes (SSR, mobile-first).

Gated by ``BODY_ASSESSMENT_ENABLED`` (default False): when the flag is
off, every route returns 404 — the feature is inaccessible and has zero
production impact. No photo, no image analysis, no external provider.
"""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from app.config import get_settings
from app.deps import CurrentUser, DbSession
from app.services import body_profile as bp
from app.templating import templates


def require_body_enabled() -> None:
    """404 when the Body Assessment feature flag is off.

    Declared as a ROUTER-LEVEL dependency (below) so the flag gate runs
    BEFORE the auth dependency on every ``/body*`` route. Result with the
    flag OFF: anonymous requests get 404 (feature hidden) rather than a
    303 login redirect — the feature is fully invisible. With the flag ON,
    auth/consent/ownership behave exactly as before.
    """
    if not get_settings().body_assessment_enabled:
        raise HTTPException(status_code=404)


# Router-level dependency: evaluated before the endpoints' own dependencies
# (e.g. CurrentUser), so the flag 404 wins over the auth 303 for anonymous
# requests when the feature is off.
router = APIRouter(tags=["body"], dependencies=[Depends(require_body_enabled)])


@router.get("/body", response_class=HTMLResponse, name="body_overview")
def body_overview(
    request: Request, db: DbSession, user: CurrentUser
) -> HTMLResponse:
    consented = bp.has_active_consent(db, user.id)
    measurements = bp.list_measurements(db, user.id) if consented else []
    latest = measurements[0] if measurements else None
    height = float(user.height_cm) if getattr(user, "height_cm", None) else None
    ratios = bp.compute_ratios(latest, height) if consented else []
    return templates.TemplateResponse(
        request,
        "body_assessment/body_overview.html",
        {
            "page_title": "Profil corporel",
            "consented": consented,
            "measurements": measurements,
            "latest": latest,
            "ratios": ratios,
            "fields": bp.BODY_MEASUREMENT_FIELDS,
            "height_cm": height,
        },
    )


@router.post("/body/consent", response_model=None, name="body_consent")
def body_consent(
    db: DbSession,
    user: CurrentUser,
    action: Annotated[str, Form()] = "",
):
    bp.set_consent(db, user.id, granted=(action == "grant"))
    return RedirectResponse(url="/body", status_code=303)


@router.get(
    "/body/measurements/new",
    response_class=HTMLResponse,
    name="body_measurement_new",
)
def measurement_new(
    request: Request, db: DbSession, user: CurrentUser
) -> HTMLResponse:
    if not bp.has_active_consent(db, user.id):
        return RedirectResponse(url="/body", status_code=303)
    return _render_form(request, action_url="/body/measurements", values={}, edit_id=None)


@router.post("/body/measurements", response_model=None, name="body_measurement_create")
async def measurement_create(
    request: Request, db: DbSession, user: CurrentUser
):
    if not bp.has_active_consent(db, user.id):
        # Consent gate: no consent -> no write.
        return RedirectResponse(url="/body", status_code=303)
    raw = _form_to_raw(await request.form())
    try:
        cleaned = bp.parse_and_validate(raw)
    except ValueError as exc:
        return _render_form(
            request, action_url="/body/measurements", values=raw,
            edit_id=None, error=str(exc), status_code=400,
        )
    bp.create_measurement(db, user.id, cleaned)
    return RedirectResponse(url="/body", status_code=303)


@router.get(
    "/body/measurements/{measurement_id}/edit",
    response_class=HTMLResponse,
    name="body_measurement_edit",
)
def measurement_edit(
    request: Request,
    measurement_id: int,
    db: DbSession,
    user: CurrentUser,
) -> HTMLResponse:
    m = bp.get_owned_measurement(db, user.id, measurement_id)
    if m is None:
        raise HTTPException(status_code=404)
    values = {f.key: _fmt(getattr(m, f.key, None)) for f in bp.BODY_MEASUREMENT_FIELDS}
    return _render_form(
        request,
        action_url=f"/body/measurements/{measurement_id}/edit",
        values=values,
        edit_id=measurement_id,
    )


@router.post(
    "/body/measurements/{measurement_id}/edit",
    response_model=None,
    name="body_measurement_update",
)
async def measurement_update(
    request: Request,
    measurement_id: int,
    db: DbSession,
    user: CurrentUser,
):
    m = bp.get_owned_measurement(db, user.id, measurement_id)
    if m is None:
        raise HTTPException(status_code=404)
    raw = _form_to_raw(await request.form())
    try:
        cleaned = bp.parse_and_validate(raw)
    except ValueError as exc:
        return _render_form(
            request,
            action_url=f"/body/measurements/{measurement_id}/edit",
            values=raw, edit_id=measurement_id, error=str(exc), status_code=400,
        )
    bp.update_measurement(db, m, cleaned)
    return RedirectResponse(url="/body", status_code=303)


@router.post(
    "/body/measurements/{measurement_id}/delete",
    response_model=None,
    name="body_measurement_delete",
)
def measurement_delete(
    measurement_id: int,
    db: DbSession,
    user: CurrentUser,
):
    m = bp.get_owned_measurement(db, user.id, measurement_id)
    if m is None:
        raise HTTPException(status_code=404)
    bp.delete_measurement(db, m)
    return RedirectResponse(url="/body", status_code=303)


@router.get("/body/export.json", response_model=None, name="body_export")
def body_export(db: DbSession, user: CurrentUser) -> JSONResponse:
    payload = bp.build_body_export(db, user.id)
    return JSONResponse(
        content=payload,
        headers={
            "Content-Disposition": 'attachment; filename="spignos-body-export.json"'
        },
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fmt(value) -> str:
    if value is None:
        return ""
    return f"{value:g}"


def _form_to_raw(form) -> dict[str, str]:
    return {f.key: str(form.get(f.key, "")) for f in bp.BODY_MEASUREMENT_FIELDS}


def _render_form(
    request: Request,
    *,
    action_url: str,
    values: dict,
    edit_id: int | None,
    error: str | None = None,
    status_code: int = 200,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "body_assessment/measurement_form.html",
        {
            "page_title": "Mesure corporelle",
            "fields": bp.BODY_MEASUREMENT_FIELDS,
            "values": values,
            "action_url": action_url,
            "edit_id": edit_id,
            "error": error,
        },
        status_code=status_code,
    )
