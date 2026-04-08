"""Tiny shared helper for the 'active session' signal.

Used by:
- the Reprendre tile on the home page
- the 'séance en cours' banner on library / history / progress /
  rules / exercise-history / export

Kept in its own module so both `app.routers.pages` and
`app.routers.sessions` can depend on it without a circular
import via `app.templating`.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.enums import SessionStatus
from app.models.session import WorkoutSession


def latest_open_session(db: Session) -> Optional[WorkoutSession]:
    """Return the most recently-started `in_progress` session, or None."""
    return db.execute(
        select(WorkoutSession)
        .where(WorkoutSession.status == SessionStatus.IN_PROGRESS)
        .order_by(WorkoutSession.started_at.desc())
        .limit(1)
    ).scalar_one_or_none()
