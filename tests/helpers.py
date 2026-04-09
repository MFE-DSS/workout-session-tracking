"""Shared test utilities."""
from __future__ import annotations


def get_test_user_id() -> int:
    """Return the id of the 'testuser' user that conftest creates.

    Call this INSIDE the test function (after the client fixture has
    run) so the DB is populated.
    """
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.execute(
            select(User).where(User.username == "testuser")
        ).scalar_one()
        return user.id
