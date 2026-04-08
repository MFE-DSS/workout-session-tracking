"""Server-side rendered pages.

Sprint 0.5 scope: home with action tiles, template library (list
and detail), plus empty-state stubs for /history and /progress.
Real session logging comes in Sprint 1.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.catalog import TemplateExercise, WorkoutTemplate
from app.models.session import WorkoutSession
from app.templating import templates

router = APIRouter(tags=["pages"])


def _load_templates(db: Session) -> list[WorkoutTemplate]:
    stmt = (
        select(WorkoutTemplate)
        .options(
            selectinload(WorkoutTemplate.exercises).selectinload(
                TemplateExercise.rep_targets
            )
        )
        .order_by(WorkoutTemplate.kind, WorkoutTemplate.slug)
    )
    return list(db.execute(stmt).scalars().all())


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    # Detect an in-progress session (started but not ended)
    open_session = db.execute(
        select(WorkoutSession)
        .where(WorkoutSession.ended_at.is_(None))
        .order_by(WorkoutSession.started_at.desc())
        .limit(1)
    ).scalar_one_or_none()

    return templates.TemplateResponse(
        request,
        "index.html",
        {"page_title": "Accueil", "open_session": open_session},
    )


@router.get("/library", response_class=HTMLResponse)
def library(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    all_templates = _load_templates(db)
    return templates.TemplateResponse(
        request,
        "library.html",
        {"page_title": "Bibliothèque", "templates": all_templates},
    )


@router.get("/library/{slug}", response_class=HTMLResponse)
def template_detail(
    slug: str, request: Request, db: Session = Depends(get_db)
) -> HTMLResponse:
    stmt = (
        select(WorkoutTemplate)
        .where(WorkoutTemplate.slug == slug)
        .options(
            selectinload(WorkoutTemplate.exercises).selectinload(
                TemplateExercise.rep_targets
            )
        )
    )
    tpl = db.execute(stmt).scalar_one_or_none()
    if tpl is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return templates.TemplateResponse(
        request,
        "template_detail.html",
        {"page_title": tpl.name, "template": tpl},
    )


@router.get("/history", response_class=HTMLResponse)
def history(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    stmt = (
        select(WorkoutSession)
        .order_by(WorkoutSession.started_at.desc())
        .limit(50)
    )
    sessions = list(db.execute(stmt).scalars().all())
    return templates.TemplateResponse(
        request,
        "history.html",
        {"page_title": "Historique", "sessions": sessions},
    )


@router.get("/progress", response_class=HTMLResponse)
def progress(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "progress.html",
        {"page_title": "Progression"},
    )
