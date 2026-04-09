"""Ownership helpers for user-scoped data access.

V2 rule: every query that touches WorkoutSession (or data derived
from it) must filter by the authenticated user's id. These small
helpers centralise the filter so no route forgets it.

Legacy V1 sessions may have `user_id IS NULL`. They are invisible
to V2 users — the filter `user_id == uid` naturally excludes them.
A backfill script can assign them to the bootstrap user if needed.
"""
from __future__ import annotations

from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.session import WorkoutSession


def get_owned_session_or_404(
    db: Session, session_id: int, user_id: int
) -> WorkoutSession:
    """Load a single session that belongs to `user_id`, or 404."""
    session = db.execute(
        select(WorkoutSession).where(
            WorkoutSession.id == session_id,
            WorkoutSession.user_id == user_id,
        )
    ).scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


def user_sessions_filter(user_id: int):
    """Return a WHERE clause fragment: WorkoutSession.user_id == uid.

    Usage:
        stmt = select(WorkoutSession).where(user_sessions_filter(uid))
    """
    return WorkoutSession.user_id == user_id
