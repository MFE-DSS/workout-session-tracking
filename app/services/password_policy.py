"""Sb_AUTH_PASSWORD_LENGTH_01 — one place that decides if a password is acceptable.

THE DEFECT THIS CLOSES
----------------------
bcrypt hashes at most the first **72 bytes** of a password. Everything past that
is ignored. passlib does not stop it: its `truncate_error` setting defaults to
False, so the full secret is handed to the backend and silently truncated there.

Measured on the shipped code before this module existed::

    verify(same_password, h)                 -> True
    verify(same_72_byte_prefix + other_tail, h) -> True   # <- the defect

Two different passwords sharing their first 72 bytes opened the same account.
Nobody chose that property; it fell out of bcrypt's C implementation meeting an
application with no upper bound. A user typing a long passphrase reasonably
believes its whole length protects them.

WHY BYTES AND NOT CHARACTERS
----------------------------
bcrypt counts **bytes**, not characters. "é" is two bytes in UTF-8, "🏋" is four.
A 72-character password of accented text is 100+ bytes and would still be
truncated. `len(password)` is therefore the wrong measure, and the user-facing
wording says "octets" for the same reason — telling someone "72 caractères"
would be a lie for anyone writing French or emoji.

WHY NOT JUST TRUNCATE
---------------------
Truncating in application code would reproduce the defect deliberately instead
of accidentally. The policy refuses the password and says so.

RELATION TO bcrypt 5.0
----------------------
bcrypt 5.0.0 raises `ValueError` past 72 bytes instead of truncating — it
refuses to do the very thing that causes this defect. Adopting it is the
belt-and-braces fix, but without this module it would turn signup, login, reset
and password change into 500s. This module is the precondition.
"""

from __future__ import annotations

#: bcrypt ignores everything past this many bytes. Not a product choice —
#: a property of the algorithm.
BCRYPT_MAX_PASSWORD_BYTES = 72

#: Minimum length, in characters. Raised from 4 to 8 by Sb_20.3.
MIN_PASSWORD_LENGTH = 8

#: Default label for messages ("Le mot de passe doit faire…").
DEFAULT_FIELD_LABEL = "Le mot de passe"

#: Shown when the password exceeds what bcrypt can actually hash. Deliberately
#: says "octets": "caractères" would be wrong for any accented or emoji input.
TOO_LONG_MESSAGE = (
    "Mot de passe trop long : bcrypt accepte au maximum "
    f"{BCRYPT_MAX_PASSWORD_BYTES} octets. "
    "Utilise une phrase de passe plus courte."
)


def password_utf8_len(password: str) -> int:
    """Length of the password as bcrypt sees it: UTF-8 bytes."""
    return len(password.encode("utf-8"))


def is_password_too_long(password: str) -> bool:
    """True when bcrypt would silently ignore part of this password."""
    return password_utf8_len(password) > BCRYPT_MAX_PASSWORD_BYTES


def validate_password_policy(
    password: str,
    *,
    field_label: str = DEFAULT_FIELD_LABEL,
    check_minimum: bool = True,
) -> str | None:
    """Return a user-facing error message, or ``None`` when acceptable.

    Returning a message rather than raising matches how every auth route in this
    app already reports validation problems (``error = "…"`` then a 400), so
    wiring it in adds no new error-handling shape.

    ``check_minimum=False`` is for the login flow, which has never enforced a
    floor: rejecting a short password at login would tell an attacker something
    about stored credentials, and would lock out any account created before the
    floor was raised. The **maximum** is always enforced, everywhere, because it
    is what keeps an over-long secret away from bcrypt.
    """
    if check_minimum and len(password) < MIN_PASSWORD_LENGTH:
        return f"{field_label} doit faire au moins {MIN_PASSWORD_LENGTH} caractères."
    if is_password_too_long(password):
        return TOO_LONG_MESSAGE
    return None
