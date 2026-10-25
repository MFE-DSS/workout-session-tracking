"""FastAPI dependencies shared across routers.

The main one is `require_user`: a dependency that reads the
session cookie, looks up the user, and either returns the User
object or redirects to /login. Every private route takes this
dependency.

Type aliases (`DbSession`, `CurrentUser`) are provided so that
routers can use `Annotated` without repeating the `Depends()`
boilerplate.
"""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.auth import get_current_user
from app.services.device_auth import resolve_access

# Reusable Annotated alias — import in routers.
DbSession = Annotated[Session, Depends(get_db)]


async def require_user(
    request: Request, db: DbSession,
) -> User:
    """Dependency that returns the authenticated User or redirects
    to /login. Used by all private routes."""
    user = get_current_user(request, db)
    if user is None:
        raise _redirect_to_login()
    return user


# Defined after require_user so the reference resolves at import time.
CurrentUser = Annotated[User, Depends(require_user)]


def require_api_user(request: Request, db: DbSession) -> User:
    """`D9` — l'utilisateur d'un jeton d'ACCÈS `Bearer`, ou 401 (jamais une redirection).

    Ne lit QUE l'en-tête `Authorization` : le cookie web n'ouvre pas l'API, et
    réciproquement `get_current_user` ne lit que le cookie. La session d'appareil
    est posée sur `request.state.device_session` pour la déconnexion.
    """
    scheme, _, token = request.headers.get("authorization", "").partition(" ")
    resolved = resolve_access(db, token.strip()) if scheme.lower() == "bearer" else None
    if resolved is None:
        raise HTTPException(
            status_code=401, detail="unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user, device_session = resolved
    request.state.device_session = device_session
    return user


ApiUser = Annotated[User, Depends(require_api_user)]


class _redirect_to_login(Exception):
    """Sentinel exception caught by a global handler that issues
    a 303 redirect to /login. Using an exception instead of
    returning a Response directly lets us keep the dependency's
    return type as `User` (not `User | Response`)."""
    pass
