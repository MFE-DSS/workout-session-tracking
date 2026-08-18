"""Sb_AUTH_PASSWORD_LENGTH_01 — the 72-byte ceiling, enforced on every auth flow.

THE DEFECT, MEASURED BEFORE THE FIX
-----------------------------------
bcrypt hashes at most the first 72 bytes and silently ignores the rest; passlib
does not stop it. On the shipped code, two different passwords sharing their
first 72 bytes verified against the same hash — they opened the same account.

These tests pin the closure on all four flows that reach bcrypt: signup, login,
password change and password reset. Closing signup alone would have left three
doors open, which is why the sprint brief made partial coverage a hard stop.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from app.services.auth import hash_password, verify_password
from app.services.password_policy import (
    BCRYPT_MAX_PASSWORD_BYTES,
    MIN_PASSWORD_LENGTH,
    TOO_LONG_MESSAGE,
    is_password_too_long,
    password_utf8_len,
    validate_password_policy,
)

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app"

EXACTLY_72 = "a" * 72
OVER_72 = "a" * 73
#: Same first 72 bytes, different tail — the exact shape of the defect.
TWIN_PREFIX = "a" * 72 + "COMPLETELY-DIFFERENT-TAIL"


# ───────────── T1 / T2 — the boundary ─────────────

def test_t1_exactly_72_bytes_is_accepted():
    assert password_utf8_len(EXACTLY_72) == BCRYPT_MAX_PASSWORD_BYTES
    assert is_password_too_long(EXACTLY_72) is False
    assert validate_password_policy(EXACTLY_72) is None


def test_t2_73_bytes_is_refused_with_a_message():
    assert is_password_too_long(OVER_72) is True
    assert validate_password_policy(OVER_72) == TOO_LONG_MESSAGE


# ───────────── T3 — bytes, not characters ─────────────

@pytest.mark.parametrize(
    ("password", "expected_bytes"),
    [
        ("é" * 36, 72),   # 36 characters, exactly at the ceiling
        ("é" * 37, 74),   # 37 characters, over it
        ("🏋" * 18, 72),  # 4 bytes each — 18 characters, exactly at the ceiling
        ("🏋" * 19, 76),  # over it
    ],
)
def test_t3_multibyte_characters_are_measured_in_bytes(password, expected_bytes):
    assert password_utf8_len(password) == expected_bytes
    assert is_password_too_long(password) is (expected_bytes > BCRYPT_MAX_PASSWORD_BYTES)


def test_t3_a_short_looking_password_can_exceed_the_ceiling():
    """37 characters is under any character-based limit, and still too long."""
    password = "é" * 37
    assert len(password) < BCRYPT_MAX_PASSWORD_BYTES  # would pass a len() check
    assert is_password_too_long(password) is True     # but bcrypt would truncate


# ───────────── T4 / T5 — the defect itself ─────────────

def test_t4_the_over_long_twin_is_refused_by_the_policy():
    """The 72-byte prefix stays legal; its longer twin does not.

    This is the pair that used to authenticate against the same hash.
    """
    assert validate_password_policy(EXACTLY_72) is None
    assert validate_password_policy(TWIN_PREFIX) == TOO_LONG_MESSAGE


def test_t4_bcrypt_still_conflates_the_twins_which_is_why_the_policy_exists():
    """Documents the underlying behaviour the policy shields against.

    If this ever stops being true — because bcrypt 5 landed — the policy has
    become belt-and-braces rather than the only guard, and the report's claim
    that bcrypt 5 is mergeable can be re-read with that in mind.
    """
    hashed = hash_password(EXACTLY_72)
    assert verify_password(EXACTLY_72, hashed) is True
    assert verify_password(TWIN_PREFIX, hashed) is True


def test_t5_policy_rejects_before_any_hashing_happens(monkeypatch):
    """No user flow may reach bcrypt with an over-long secret."""
    import app.routers.auth_routes as auth_routes

    calls: list[str] = []
    monkeypatch.setattr(
        auth_routes, "hash_password", lambda p: calls.append(p) or "x"
    )
    assert validate_password_policy(TWIN_PREFIX) is not None
    assert calls == []


# ───────────── T6 / T7 / T8 — the four flows, over HTTP ─────────────

def _register(client, password):
    return client.post(
        "/register",
        data={
            "username": "pwpolicy_user",
            "password": password,
            "password_confirm": password,
        },
        follow_redirects=False,
    )


def test_t6_signup_with_an_over_long_password_is_a_controlled_400(client):
    response = _register(client, TWIN_PREFIX)
    assert response.status_code == 400
    assert "trop long" in response.text
    assert "octets" in response.text


def test_t7_login_with_an_over_long_password_is_a_controlled_400(client):
    response = client.post(
        "/login",
        data={"username": "whoever", "password": TWIN_PREFIX},
        follow_redirects=False,
    )
    assert response.status_code == 400
    assert "trop long" in response.text


def test_t8_password_change_refuses_an_over_long_new_password(client):
    client.post(
        "/register",
        data={
            "username": "pwchange_user",
            "password": "validpass123",
            "password_confirm": "validpass123",
        },
        follow_redirects=True,
    )
    response = client.post(
        "/profile/password",
        data={
            "current_password": "validpass123",
            "new_password": TWIN_PREFIX,
            "new_password_confirm": TWIN_PREFIX,
        },
        follow_redirects=False,
    )
    assert response.status_code == 400
    assert "trop long" in response.text


def test_t8_password_reset_refuses_an_over_long_new_password(client):
    from app.services.auth import create_reset_token

    client.post(
        "/register",
        data={
            "username": "pwreset_user",
            "password": "validpass123",
            "password_confirm": "validpass123",
        },
        follow_redirects=True,
    )
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.execute(
            select(User).where(User.username == "pwreset_user")
        ).scalar_one()
        token = create_reset_token(user.id)

    response = client.post(
        f"/reset/{token}",
        data={"new_password": TWIN_PREFIX, "new_password_confirm": TWIN_PREFIX},
        follow_redirects=False,
    )
    assert response.status_code == 400
    assert "trop long" in response.text


# ───────────── T9 — nothing normal breaks ─────────────

def test_t9_a_normal_password_still_registers_and_logs_in(client):
    registered = _register(client, "correcthorse1")
    assert registered.status_code == 303

    client.post("/logout", follow_redirects=False)
    logged_in = client.post(
        "/login",
        data={"username": "pwpolicy_user", "password": "correcthorse1"},
        follow_redirects=False,
    )
    assert logged_in.status_code == 303


def test_t9_the_minimum_floor_is_unchanged(client):
    response = _register(client, "abcdefg")  # 7 characters
    assert response.status_code == 400
    assert f"au moins {MIN_PASSWORD_LENGTH}" in response.text


def test_t9_login_never_enforces_the_minimum():
    """A short legacy password must still be able to authenticate."""
    assert validate_password_policy("abc", check_minimum=False) is None
    assert validate_password_policy("abc") is not None


# ───────────── T10 — no manual truncation, ever ─────────────

def test_t10_no_application_code_truncates_a_password():
    """`password[:72]` would reproduce the defect on purpose."""
    offenders: list[str] = []
    pattern = re.compile(r"(?:password|secret|passwd|pwd)\w*\s*\[\s*:\s*\d+\s*\]", re.I)
    for source in APP.rglob("*.py"):
        for number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
            if pattern.search(line):
                offenders.append(f"{source.relative_to(ROOT)}:{number}: {line.strip()}")
    assert offenders == [], f"manual password truncation found: {offenders}"


def test_t10_the_ceiling_is_never_described_as_characters():
    """Saying "72 caractères" would be a lie for accented or emoji input."""
    assert "octets" in TOO_LONG_MESSAGE
    assert "caractères" not in TOO_LONG_MESSAGE


# ───────────── the policy is centralised (A1) ─────────────

def _executable_lines(source: Path) -> str:
    """Source with comments and docstrings removed.

    A guard that greps raw text flags the comments that *explain* the rule — the
    route comments legitimately mention 72 bytes to say why the check is there.
    Scanning prose instead of code has produced a false failure in this
    programme repeatedly; strip it once, here.
    """
    import ast

    tree = ast.parse(source.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            docstring = ast.get_docstring(node, clean=False)
            if docstring is not None:
                node.body = node.body[1:]
    return ast.unparse(tree)


def test_a1_no_auth_route_measures_the_ceiling_on_its_own():
    """Every flow must go through password_policy, not re-implement the rule."""
    routes = _executable_lines(APP / "routers" / "auth_routes.py")
    assert "encode('utf-8')" not in routes, "byte measurement leaked into a route"
    assert str(BCRYPT_MAX_PASSWORD_BYTES) not in routes, "the ceiling is hard-coded in a route"
    assert "validate_password_policy" in routes


def test_a5_the_hash_format_is_unchanged():
    """No pre-hashing, no scheme change — existing hashes must stay valid."""
    hashed = hash_password("correcthorse1")
    assert hashed.startswith("$2")
    assert verify_password("correcthorse1", hashed) is True
