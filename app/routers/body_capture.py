"""Sb_Body_02.1 — Capture Quality shell route.

Shell uniquement : route SSR placeholder derrière un flag dédié OFF
par défaut, sans caméra, sans JavaScript, sans MediaPipe, sans modèle,
sans CDN, sans web worker, sans upload, sans stockage. Aucune dépendance
externe ajoutée.

Cf. spec : ``docs/strategy/SPIGNOS_BODY_CAPTURE_QUALITY_SPEC.md``.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.config import get_settings
from app.deps import CurrentUser
from app.templating import templates


def require_body_capture_quality_enabled() -> None:
    """404 when the Body Capture Quality flag is off.

    Declared as a ROUTER-LEVEL dependency (below) so the flag gate runs
    BEFORE the auth dependency: with the flag OFF, anonymous AND
    authenticated requests get 404 — the surface is fully invisible.
    Mirrors :func:`require_body_intelligence_enabled` (Sb_31.X) and
    :func:`require_body_enabled` (Sb_Body_01.1).
    """
    if not get_settings().body_capture_quality_enabled:
        raise HTTPException(status_code=404)


# Router-level dependency : évaluée AVANT les dépendances d'endpoint
# (CurrentUser), donc le 404 du flag bat le 303 d'auth pour les anonymes
# quand Capture Quality est OFF.
router = APIRouter(
    tags=["body_capture_quality"],
    dependencies=[Depends(require_body_capture_quality_enabled)],
)


@router.get(
    "/body/capture-quality",
    response_class=HTMLResponse,
    name="body_capture_quality",
)
def body_capture_quality_shell(
    request: Request,
    user: CurrentUser,
) -> HTMLResponse:
    """Shell SSR strictement statique. Aucune logique métier, aucun
    accès DB, aucun JavaScript, aucune caméra. Affiche un placeholder
    sobre informant que la capture n'est pas disponible dans ce lot.
    """
    return templates.TemplateResponse(
        request,
        "body_capture_quality.html",
        {
            "page_title": "Qualité de capture",
        },
    )
