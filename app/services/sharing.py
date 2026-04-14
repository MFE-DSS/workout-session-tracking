"""Sharing service — template recommendations and session sharing within squads."""
from __future__ import annotations

from sqlalchemy import select, union_all
from sqlalchemy.orm import Session, selectinload

from app.models.session import SessionExercise, WorkoutSession
from app.models.sharing import SquadSharedSession, SquadTemplateRecommendation
from app.models.user import User
from app.services.substitution import actual_exercise_name


class SharingError(Exception):
    """Raised on invalid sharing operations."""


def recommend_template(
    db: Session,
    squad_id: int,
    user_id: int,
    template_slug: str,
    template_name: str,
    note: str | None = None,
) -> SquadTemplateRecommendation:
    """Create a template recommendation in a squad."""
    rec = SquadTemplateRecommendation(
        squad_id=squad_id,
        user_id=user_id,
        template_slug=template_slug,
        template_name=template_name,
        note=note,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


def share_session(
    db: Session,
    squad_id: int,
    user_id: int,
    session_id: int,
) -> SquadSharedSession:
    """Share a session with a squad. Validates session ownership."""
    ws = db.get(WorkoutSession, session_id)
    if ws is None or ws.user_id != user_id:
        raise SharingError("Session introuvable ou non autorisée.")

    shared = SquadSharedSession(
        squad_id=squad_id,
        user_id=user_id,
        session_id=session_id,
    )
    db.add(shared)
    db.commit()
    db.refresh(shared)
    return shared


def get_squad_activity(db: Session, squad_id: int, limit: int = 20) -> list[dict]:
    """Return a mixed feed of recommendations and shared sessions.

    Ordered by created_at desc. Shared sessions include exercise list
    with code, name, and success_score only (no weights/reps/notes/muscle_sensation).
    """
    # Fetch recommendations
    recs = (
        db.execute(
            select(SquadTemplateRecommendation)
            .where(SquadTemplateRecommendation.squad_id == squad_id)
            .order_by(SquadTemplateRecommendation.created_at.desc())
            .limit(limit)
        )
        .scalars()
        .all()
    )

    # Fetch shared sessions
    shared_rows = (
        db.execute(
            select(SquadSharedSession)
            .where(SquadSharedSession.squad_id == squad_id)
            .order_by(SquadSharedSession.created_at.desc())
            .limit(limit)
        )
        .scalars()
        .all()
    )

    items: list[dict] = []

    for rec in recs:
        user = db.get(User, rec.user_id)
        items.append({
            "type": "recommendation",
            "created_at": rec.created_at,
            "username": user.username if user else "?",
            "template_slug": rec.template_slug,
            "template_name": rec.template_name,
            "note": rec.note,
        })

    for shared in shared_rows:
        user = db.get(User, shared.user_id)
        ws = db.execute(
            select(WorkoutSession)
            .where(WorkoutSession.id == shared.session_id)
            .options(selectinload(WorkoutSession.session_exercises))
        ).scalar_one_or_none()

        exercises = []
        if ws:
            for se in ws.session_exercises:
                exercises.append({
                    "code": se.exercise_code_snapshot,
                    "name": actual_exercise_name(se),
                    "success_score": se.success_score,
                })

        items.append({
            "type": "shared_session",
            "created_at": shared.created_at,
            "username": user.username if user else "?",
            "session_id": shared.session_id,
            "exercises": exercises,
        })

    # Sort by created_at desc, take top `limit`
    items.sort(key=lambda x: x["created_at"], reverse=True)
    return items[:limit]
