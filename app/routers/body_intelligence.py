"""Sb_31.2 — Body Intelligence v2 route.

Surface SSR ``GET /body/intelligence``.

Coordination de routes :
- ``/body`` (sans suffix) appartient au track parallèle Body Manual
  Profile (cf. ``app/routers/body.py`` + PR #15). Body Intelligence v2
  utilise donc ``/body/intelligence`` comme route canonique pour éviter
  toute collision technique entre les deux tracks.
- ``/physique`` reste la vue analytique 11 zones existante (inchangée).

Cette route est volontairement le seul lieu d'orchestration :
- appelle ``build_body_intelligence_input(db, user)`` (couche I/O)
- appelle ``compute_body_intelligence(input)`` (composeur pur Sb_31.1)
- rend le template SSR

Aucune logique métier ici. Aucune API JSON publique exposée.
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.deps import CurrentUser, DbSession
from app.services.body_intelligence import compute_body_intelligence
from app.services.body_intelligence_inputs import build_body_intelligence_input
from app.templating import templates

router = APIRouter(tags=["body_intelligence"])


@router.get(
    "/body/intelligence",
    response_class=HTMLResponse,
    name="body_intelligence",
)
def body_intelligence_page(
    request: Request,
    db: DbSession,
    user: CurrentUser,
) -> HTMLResponse:
    body_input = build_body_intelligence_input(db, user)
    snapshot = compute_body_intelligence(body_input)
    return templates.TemplateResponse(
        request,
        "body_intelligence.html",
        {
            "page_title": "Lecture corporelle",
            "snapshot": snapshot,
        },
    )
