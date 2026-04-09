"""FastAPI dependencies shared across routers.

The main one is `require_user`: a dependency that reads the
session cookie, looks up the user, and either returns the User
object or redirects to /login. Every private route takes this
dependency.
"""
from __future__ import annotations

from fastapi import Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.auth import get_current_user


async def require_user(
    request: Request, db: Session = Depends(get_db)
) -> User:
    """Dependency that returns the authenticated User or redirects
    to /login. Used by all private routes."""
    user = get_current_user(request, db)
    if user is None:
        raise _redirect_to_login()
    return user


class _redirect_to_login(Exception):
    """Sentinel exception caught by a global handler that issues
    a 303 redirect to /login. Using an exception instead of
    returning a Response directly lets us keep the dependency's
    return type as `User` (not `User | Response`)."""
    pass
