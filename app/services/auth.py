"""Password hashing and session cookie helpers for V2 auth.

Passwords are stored as bcrypt hashes via passlib. The session
token is a signed cookie produced by itsdangerous. No JWT, no
OAuth, no external provider — just a simple server-side session
cookie for an SSR app.

Cookie name: `session_token`
Cookie content: itsdangerous-signed JSON `{"user_id": <int>}`
Cookie flags: httponly, samesite=lax, secure in production
"""
from __future__ import annotations

from typing import Optional

from itsdangerous import BadSignature, URLSafeTimedSerializer
from passlib.hash import bcrypt
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import Response

from app.config import get_settings
from app.models.user import User

SESSION_COOKIE = "session_token"
SESSION_MAX_AGE = 30 * 86400  # 30 days


def hash_password(plain: str) -> str:
    return bcrypt.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.verify(plain, hashed)


def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(get_settings().app_secret_key)


def create_session_cookie(response: Response, user_id: int) -> None:
    """Sign user_id into a cookie and set it on the response."""
    token = _serializer().dumps({"user_id": user_id})
    settings = get_settings()
    is_prod = settings.app_env == "production"
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        max_age=SESSION_MAX_AGE,
        httponly=True,
        samesite="strict",
        secure=is_prod,
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(key=SESSION_COOKIE, path="/")


def get_user_id_from_cookie(request: Request) -> Optional[int]:
    """Read and validate the session cookie. Returns the user_id
    or None if the cookie is missing / expired / tampered."""
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    try:
        payload = _serializer().loads(token, max_age=SESSION_MAX_AGE)
        return payload.get("user_id")
    except (BadSignature, Exception):
        return None


def get_current_user(request: Request, db: Session) -> Optional[User]:
    """Full user lookup from the cookie. Returns the User object
    or None. Used by the auth dependency."""
    user_id = get_user_id_from_cookie(request)
    if user_id is None:
        return None
    user = db.execute(
        select(User).where(User.id == user_id, User.is_active.is_(True))
    ).scalar_one_or_none()
    return user


RESET_TOKEN_MAX_AGE = 3600  # 1 hour


def create_reset_token(user_id: int) -> str:
    """Create a signed, time-limited token for password reset."""
    return _serializer().dumps({"user_id": user_id, "purpose": "reset"})


def verify_reset_token(token: str, max_age: int = RESET_TOKEN_MAX_AGE) -> int | None:
    """Verify a reset token. Returns user_id if valid, None otherwise."""
    if max_age <= 0:
        return None
    try:
        payload = _serializer().loads(token, max_age=max_age)
        if payload.get("purpose") != "reset":
            return None
        return payload.get("user_id")
    except (BadSignature, Exception):
        return None
