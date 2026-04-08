"""Server-side rendered pages.

V1 ships a read-only view of the reference split so the phone is usable as a
pocket catalog while we finish the session-logging UI in Sprint 1.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.catalog import Exercise, SplitDay
from app.templating import templates

router = APIRouter(tags=["pages"])


def _load_days(db: Session) -> list[SplitDay]:
    stmt = (
        select(SplitDay)
        .options(
            selectinload(SplitDay.exercises).selectinload(Exercise.rep_ranges)
        )
        .order_by(SplitDay.weekday)
    )
    return list(db.execute(stmt).scalars().all())


@router.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    days = _load_days(db)
    return templates.TemplateResponse(
        request,
        "index.html",
        {"days": days, "page_title": "Split"},
    )


@router.get("/jours/{weekday}", response_class=HTMLResponse)
def day_detail(
    weekday: int, request: Request, db: Session = Depends(get_db)
) -> HTMLResponse:
    if weekday < 1 or weekday > 7:
        raise HTTPException(status_code=404, detail="Unknown weekday")
    stmt = (
        select(SplitDay)
        .where(SplitDay.weekday == weekday)
        .options(
            selectinload(SplitDay.exercises).selectinload(Exercise.rep_ranges)
        )
    )
    day = db.execute(stmt).scalar_one_or_none()
    if day is None:
        raise HTTPException(status_code=404, detail="Split day not seeded")
    return templates.TemplateResponse(
        request,
        "day.html",
        {"day": day, "page_title": day.name},
    )
