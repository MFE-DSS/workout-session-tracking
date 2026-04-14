"""Compare service — head-to-head comparison between two squad members."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.squad import compute_squad_leaderboard


def compute_comparison(db: Session, squad_id: int, user_a_id: int, user_b_id: int) -> dict:
    """Return leaderboard entries for two users within a squad.

    Returns {"a": entry_dict, "b": entry_dict} using the squad leaderboard
    data filtered to the two requested users.
    """
    # Look up usernames
    user_a = db.get(User, user_a_id)
    user_b = db.get(User, user_b_id)
    if not user_a or not user_b:
        return {"a": None, "b": None}

    leaderboard = compute_squad_leaderboard(db, squad_id)

    entry_a = None
    entry_b = None
    for entry in leaderboard:
        if entry["username"] == user_a.username:
            entry_a = entry
        if entry["username"] == user_b.username:
            entry_b = entry

    return {"a": entry_a, "b": entry_b}
