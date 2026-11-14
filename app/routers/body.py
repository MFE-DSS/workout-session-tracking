"""Sb_Body_01 — Manual Body Profile routes (SSR, mobile-first).

Gated by ``BODY_ASSESSMENT_ENABLED`` (default False): when the flag is
off, every route returns 404 — the feature is inaccessible and has zero
production impact. No photo, no image analysis, no external provider.
"""
from __future__ import annotations

from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.routing import APIRoute
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_settings
from app.deps import CurrentUser, DbSession
from app.models.body_measurement_operation import BodyMeasurementOperation
from app.services import body_profile as bp
from app.services.body_measurement_commands import BodyValueError, apply_command, require_schema
from app.services.body_measurement_reads import BodyCommandError, head_contexts, page
from app.services.plan_v3.transactions import RuntimeFailure, guard_owner
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
class _OwnedBodyRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def handle(request):
            try:
                response = await original(request)
                response.headers["Cache-Control"] = "no-store"
                return response
            except (BodyCommandError, RuntimeFailure) as exc:
                raise HTTPException(exc.status, detail={"error": exc.code},
                                    headers={"Cache-Control": "no-store"}) from None
            except SQLAlchemyError:
                raise HTTPException(503, detail={"error": "body_storage_unavailable"},
                                    headers={"Cache-Control": "no-store"}) from None
        return handle


def _authenticate_current(db, user):
    guard_owner(db, user.id, expected_epoch=user.session_epoch, expected_hash=user.password_hash)


def _mutation_root(db, user, measurement_id, form, operation):
    """Bind replay to the owned original path, even after its facts are erased."""
    _authenticate_current(db, user)
    owner_id = user.id
    key = form.get("request_id")
    prior = db.scalar(select(BodyMeasurementOperation).where(
        BodyMeasurementOperation.owner_id == owner_id,
        BodyMeasurementOperation.request_id == key,
        BodyMeasurementOperation.operation == operation,
        (BodyMeasurementOperation.parent_ref if operation == "CORRECT"
         else BodyMeasurementOperation.measurement_ref) == measurement_id,
    )) if key else None
    measurement = bp.get_owned_measurement(db, owner_id, measurement_id)
    if measurement is None and prior is None:
        raise HTTPException(404)
    if not isinstance(key, str) or not isinstance(form.get("expected_head_token"), str):
        raise HTTPException(422, detail={"error": "body_command_identity_required"})
    return prior.root_ref if prior is not None else bp._owned_root(db, measurement)


router = APIRouter(tags=["body"], route_class=_OwnedBodyRoute,
                   dependencies=[Depends(require_body_enabled)])


@router.get("/body", response_class=HTMLResponse, name="body_overview")
def body_overview(
    request: Request, db: DbSession, user: CurrentUser,
    manage_erasure: bool = False,
    cursor: Annotated[str | None, Query(max_length=4096)] = None,
) -> HTMLResponse:
    erasure_page = None
    if manage_erasure:
        _authenticate_current(db, user)
        require_schema(db)
        erasure_page = page(db, user.id, kind="ERASURE", cursor=cursor)
    consented = bp.has_active_consent(db, user.id)
    measurements = bp.list_measurements(db, user.id) if consented and not manage_erasure else []
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
            "erasure_page": erasure_page,
            "body_contexts": head_contexts(db, user.id, measurements),
            "new_request_id": lambda: str(uuid4()),
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
    form = await request.form()
    raw = _form_to_raw(form)
    try:
        cleaned = bp.parse_and_validate(raw, check_bounds=False)
    except ValueError as exc:
        return _render_form(
            request, action_url="/body/measurements", values=raw,
            edit_id=None, error=str(exc), status_code=400,
        )
    _authenticate_current(db, user)
    try:
        bp.create_measurement(db, user.id, cleaned, request_id=form.get("request_id") or None)
    except BodyValueError as exc:
        return _render_form(
            request, action_url="/body/measurements", values=raw,
            edit_id=None, error=exc.form_message, status_code=400,
            request_id=form.get("request_id"),
        )
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
    if not bp.has_active_consent(db, user.id):
        return RedirectResponse(url="/body", status_code=303)
    values = {f.key: _fmt(getattr(m, f.key, None)) for f in bp.BODY_MEASUREMENT_FIELDS}
    return _render_form(
        request,
        action_url=f"/body/measurements/{measurement_id}/edit",
        values=values,
        edit_id=measurement_id,
        head_token=bp.measurement_head_token(db, m),
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
    formulaire = await request.form()
    root = _mutation_root(db, user, measurement_id, formulaire, "CORRECT")
    raw = _form_to_raw(formulaire)
    try:
        # A submitted blank explicitly clears that field; absent fields remain inherited.
        clear_only = any(spec.key in formulaire for spec in bp.BODY_MEASUREMENT_FIELDS) and not any(
            value.strip() for value in raw.values()
        )
        cleaned = {} if clear_only else bp.parse_and_validate(raw, check_bounds=False)
    except ValueError as exc:
        return _render_form(
            request,
            action_url=f"/body/measurements/{measurement_id}/edit",
            values=raw, edit_id=measurement_id, error=str(exc), status_code=400,
            head_token=formulaire.get("expected_head_token"),
            request_id=formulaire.get("request_id"),
        )
    # `UI-CP7.5A` — SEULS LES CHAMPS RÉELLEMENT SOUMIS SONT ÉCRITS.
    #
    # `_form_to_raw` rend les treize clés quoi qu'il arrive, en substituant
    # `""` aux absentes : le service ne pouvait donc pas distinguer « champ
    # vidé » de « champ pas dans ce formulaire », et remettait tout à `NULL`.
    #
    # On lit la présence sur le formulaire BRUT, avant cette normalisation.
    # C'est ce qui rend une saisie partielle possible sans perte — et donc ce
    # qui rend une capture guidée concevable.
    values = {spec.key: cleaned.get(spec.key) for spec in bp.BODY_MEASUREMENT_FIELDS
              if spec.key in formulaire}
    try:
        apply_command(db, user.id, {"operation": "CORRECT", "root_ref": root,
            "request_id": formulaire["request_id"], "expected_head_token": formulaire["expected_head_token"],
            "values": values}, source="MANUAL_CORRECTION")
    except BodyValueError as exc:
        return _render_form(
            request, action_url=f"/body/measurements/{measurement_id}/edit",
            values=raw, edit_id=measurement_id, error=exc.form_message, status_code=400,
            head_token=formulaire.get("expected_head_token"),
            request_id=formulaire.get("request_id"),
        )
    return RedirectResponse(url="/body", status_code=303)


@router.post(
    "/body/measurements/{measurement_id}/delete",
    response_model=None,
    name="body_measurement_delete",
)
async def measurement_delete(
    request: Request,
    measurement_id: int,
    db: DbSession,
    user: CurrentUser,
):
    form = await request.form()
    root = _mutation_root(db, user, measurement_id, form, "ERASE")
    if form.get("confirm_all_versions") != "yes":
        raise HTTPException(422, detail={"error": "erase_confirmation_required"})
    apply_command(db, user.id, {"operation": "ERASE", "root_ref": root,
        "request_id": form["request_id"], "expected_head_token": form["expected_head_token"],
        "confirm_all_versions": True}, source="MANUAL_ENTRY")
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
    # The edit form must round-trip the stored number, not reacquire a rounded one.
    rendered = str(value)
    return rendered[:-2] if rendered.endswith(".0") else rendered


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
    head_token: str | None = None,
    request_id: str | None = None,
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
            "head_token": head_token,
            "request_id": request_id or str(uuid4()),
        },
        status_code=status_code,
    )
