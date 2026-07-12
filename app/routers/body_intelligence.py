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

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.config import get_settings
from app.deps import CurrentUser, DbSession
from app.services.body_intelligence import compute_body_intelligence
from app.services.body_intelligence_inputs import build_body_intelligence_input
from app.services.muscle_scoring import ZoneScore, compute_physique_dashboard
from app.templating import templates


def _build_zone_cards(zone_scores: list[ZoneScore]) -> list[dict]:
    """Sb_BI_01.1 — presentation-only derivation of Zone Intelligence Cards
    from the existing ``ZoneScore`` list produced by ``muscle_scoring``.

    NO new score is computed here. We reuse the already-computed per-zone
    signals (hard sets, session count, trend, confidence) and add a single
    *traceable* derived field — ``contribution_pct`` — which is a pure
    arithmetic share of the zone's hard sets in the total hard sets over
    the window (rounded int %). It is a proportion, not a rating.

    Zones with no recent volume (``hard_sets == 0``) are dropped: they carry
    no signal and rendering 11 empty cards would re-densify the surface. If
    every zone is empty, the caller gets ``[]`` and the template shows the
    sober empty state.

    The opaque ``ZoneScore.score`` (0..100) and the A/B/C grade are
    deliberately NOT surfaced (Sx_BI_01 rule: no opaque score first).
    """
    active = [z for z in zone_scores if z.hard_sets > 0]
    total_hard_sets = sum(z.hard_sets for z in active)
    cards: list[dict] = []
    for z in active:
        contribution_pct = (
            round(100 * z.hard_sets / total_hard_sets) if total_hard_sets else None
        )
        cards.append(
            {
                "zone": z.zone,
                "label": z.label,
                "hard_sets": z.hard_sets,
                "session_count": z.session_count,
                "trend": z.trend,  # "up" | "down" | "stable"
                "confidence": z.confidence,  # "élevée" | "moyenne" | "faible"
                "contribution_pct": contribution_pct,
                "top_exercises": list(z.top_exercises[:2]),
            }
        )
    # Most-trained zone first — a transparent ordering by recent volume,
    # never by the hidden score.
    cards.sort(key=lambda c: c["hard_sets"], reverse=True)
    return cards


def require_body_intelligence_enabled() -> None:
    """404 when the Body Intelligence v2 feature flag is off.

    Declared as a ROUTER-LEVEL dependency (below) so the flag gate runs
    BEFORE the auth dependency: with the flag OFF, anonymous AND
    authenticated requests get 404 — the surface is fully invisible.
    Mirrors the Manual Body Profile gate (Sb_Body_01.1).
    """
    if not get_settings().body_intelligence_enabled:
        raise HTTPException(status_code=404)


# Router-level dependency: evaluated before the endpoints' own
# dependencies (e.g. CurrentUser), so the flag 404 wins over the auth 303
# for anonymous requests when Body Intelligence v2 is off.
router = APIRouter(
    tags=["body_intelligence"],
    dependencies=[Depends(require_body_intelligence_enabled)],
)


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
    # Sb_BI_01.1 — reuse the existing per-zone signals (read-only) to build
    # traceable Zone Intelligence Cards. No new score, no /physique change.
    dashboard = compute_physique_dashboard(db, user.id, window_days=30)
    zone_cards = _build_zone_cards(dashboard.zone_scores)
    return templates.TemplateResponse(
        request,
        "body_intelligence.html",
        {
            "page_title": "Lecture corporelle",
            "snapshot": snapshot,
            "zone_cards": zone_cards,
        },
    )
