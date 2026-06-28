"""Sb_23 — Coach Report route.

Serves ``/coach-report`` for the authenticated user only. No public
sharing V1, no token-based access — the user is always the subject of
their own report.
"""
from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.deps import CurrentUser, DbSession
from app.services.body_intelligence import compute_body_intelligence
from app.services.body_intelligence_inputs import build_body_intelligence_input
from app.services.coach_inference import build_inference
from app.services.coach_report import build_report
from app.services.session_state import latest_open_session
from app.templating import templates

router = APIRouter(tags=["coach-report"])


@router.get("/coach-report", response_class=HTMLResponse, name="coach_report")
def coach_report_page(
    request: Request,
    db: DbSession,
    user: CurrentUser,
) -> HTMLResponse:
    """Render the 10-block synthesis report for the authenticated user.

    Spec §B.bis : every block carries its tag (Mesuré / Inféré /
    Non déductible) in the template — surface visibility, not just
    backend semantics.
    """
    report = build_report(db, user)
    inference = build_inference(report)
    # Sb_31.3 — Snapshot Body Intelligence (v2) injecté via la pipeline
    # canonique Sx_31. Le service `coach_report.py` n'est PAS modifié :
    # le router orchestre uniquement input → composer → contexte template.
    body_snapshot = compute_body_intelligence(
        build_body_intelligence_input(db, user)
    )
    return templates.TemplateResponse(
        request,
        "coach_report.html",
        {
            "page_title": "Coach Report",
            "report": report,
            "inference": inference,
            "active_session": latest_open_session(db, user.id),
            "body_snapshot": body_snapshot,
        },
    )
