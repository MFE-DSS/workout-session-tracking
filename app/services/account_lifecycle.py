"""Canonical account creation shared by the web form and mobile JSON."""

from __future__ import annotations

import re

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.auth import hash_password, verify_password
from app.services.password_policy import validate_password_policy

MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 64
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_-]+$")
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class AccountRejected(ValueError):
    """A public error code/message, never the submitted credentials."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def _existing_account_error(
    db: Session, username: str, email: str | None
) -> AccountRejected | None:
    if (
        db.execute(select(User.id).where(User.username == username)).scalar_one_or_none()
        is not None
    ):
        return AccountRejected("username_unavailable", "Ce nom d'utilisateur est déjà pris.")
    if (
        email
        and db.execute(select(User.id).where(User.email == email)).scalar_one_or_none() is not None
    ):
        return AccountRejected("email_unavailable", "Cet email est déjà associé à un compte.")
    return None


def register_account(
    db: Session,
    *,
    username: str,
    password: str,
    password_confirm: str,
    email: str = "",
) -> User:
    """Validate and flush one User. The caller commits the account and its session together."""
    username_clean = username.strip()
    password_error = validate_password_policy(password)
    if len(username_clean) < MIN_USERNAME_LENGTH:
        raise AccountRejected(
            "username_too_short",
            f"Le nom d'utilisateur doit faire au moins {MIN_USERNAME_LENGTH} caractères.",
        )
    if len(username_clean) > MAX_USERNAME_LENGTH:
        raise AccountRejected(
            "username_too_long", f"Le nom d'utilisateur dépasse {MAX_USERNAME_LENGTH} caractères."
        )
    if not USERNAME_REGEX.match(username_clean):
        raise AccountRejected(
            "invalid_username",
            "Le nom d'utilisateur ne peut contenir que des lettres, chiffres, _ et -.",
        )
    if password_error is not None:
        raise AccountRejected("invalid_password", password_error)
    if password != password_confirm:
        raise AccountRejected("password_mismatch", "Les mots de passe ne correspondent pas.")

    # Keep the web's ordering: an occupied username precedes email validation.
    occupied = _existing_account_error(db, username_clean, None)
    if occupied:
        raise occupied
    email_clean = email.strip().lower() or None
    if email_clean and not EMAIL_REGEX.match(email_clean):
        raise AccountRejected("invalid_email", "Adresse email invalide.")
    occupied = _existing_account_error(db, username_clean, email_clean)
    if occupied:
        raise occupied

    user = User(username=username_clean, password_hash=hash_password(password), email=email_clean)
    db.add(user)
    try:
        db.flush()
    except IntegrityError:
        # Another request can win after the checks above. The UNIQUE constraint
        # is the authority; no token has been minted and nothing was committed.
        db.rollback()
        occupied = _existing_account_error(db, username_clean, email_clean)
        if occupied:
            raise occupied from None
        raise
    return user


def change_password(
    db: Session,
    user: User,
    *,
    current_password: str,
    new_password: str,
    new_password_confirm: str,
) -> None:
    """Apply the web policy and epoch revocation; the caller owns the transaction."""
    current_error = validate_password_policy(current_password, check_minimum=False)
    new_error = validate_password_policy(new_password, field_label="Le nouveau mot de passe")
    if current_error is not None:
        raise AccountRejected("invalid_current_password", current_error)
    if not verify_password(current_password, user.password_hash):
        raise AccountRejected("invalid_current_password", "Le mot de passe actuel est incorrect.")
    if new_error is not None:
        raise AccountRejected("invalid_password", new_error)
    if new_password != new_password_confirm:
        raise AccountRejected(
            "password_mismatch", "Les nouveaux mots de passe ne correspondent pas."
        )
    # Same session_epoch revocation contract as auth.revoke_sessions, but with
    # an optimistic guard: two requests authenticated at epoch N must not both
    # issue replacement credentials at N+1 after different password changes.
    expected_epoch = user.session_epoch or 0
    changed = db.execute(
        update(User)
        .where(
            User.id == user.id,
            User.password_hash == user.password_hash,
            User.session_epoch == expected_epoch,
        )
        .values(password_hash=hash_password(new_password), session_epoch=expected_epoch + 1),
        execution_options={"synchronize_session": False},
    )
    if changed.rowcount != 1:
        db.rollback()
        raise AccountRejected("credentials_changed", "Le mot de passe actuel est incorrect.")
    db.refresh(user)
