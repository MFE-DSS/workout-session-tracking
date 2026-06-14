"""Sb_26.4 — deterministic rate limiter tests.

Covers:
* /login is blocked after `rate_limit_login_max` attempts within the window
* /register and /forgot-password also enforced
* 429 response carries `Retry-After` header
* 429 message does NOT leak whether the username/email exists
* limiter can be disabled via `RATE_LIMIT_ENABLED=0`
* buckets are properly per-IP + per-route (different IPs do not share)
"""
from __future__ import annotations

import pytest


def _current_limiter():
    """Re-import app.main each call: the `client` fixture in conftest
    pops `app.*` from sys.modules so module-level state (rate-limit
    buckets) belongs to whatever module instance the running app uses.
    """
    from app import main as main_mod

    return main_mod._rate_limit_check, main_mod._rate_limit_reset_for_tests


@pytest.fixture(autouse=True)
def _reset_buckets():
    _, reset = _current_limiter()
    reset()
    yield
    _, reset = _current_limiter()
    reset()


# ───────── unit-level sliding-window logic ─────────


class _FakeSettings:
    rate_limit_login_max = 3
    rate_limit_login_window_seconds = 60
    rate_limit_register_max = 2
    rate_limit_register_window_seconds = 60
    rate_limit_forgot_max = 2
    rate_limit_forgot_window_seconds = 60


def test_rate_limit_allows_below_quota():
    check, _ = _current_limiter()
    s = _FakeSettings()
    for _ in range(3):
        allowed, retry = check(s, "1.2.3.4", "login", now=100.0)
        assert allowed is True
        assert retry == 0


def test_rate_limit_blocks_above_quota_with_retry_after():
    check, _ = _current_limiter()
    s = _FakeSettings()
    for _ in range(3):
        check(s, "1.2.3.4", "login", now=100.0)
    allowed, retry = check(s, "1.2.3.4", "login", now=100.0)
    assert allowed is False
    assert retry > 0
    assert retry <= 61


def test_rate_limit_window_slides():
    check, _ = _current_limiter()
    s = _FakeSettings()
    for _ in range(3):
        check(s, "1.2.3.4", "login", now=100.0)
    allowed, _ = check(s, "1.2.3.4", "login", now=200.0)
    assert allowed is True


def test_rate_limit_buckets_are_per_ip():
    check, _ = _current_limiter()
    s = _FakeSettings()
    for _ in range(3):
        check(s, "1.2.3.4", "login", now=100.0)
    allowed, _ = check(s, "5.6.7.8", "login", now=100.0)
    assert allowed is True


def test_rate_limit_buckets_are_per_route():
    check, _ = _current_limiter()
    s = _FakeSettings()
    for _ in range(3):
        check(s, "1.2.3.4", "login", now=100.0)
    allowed, _ = check(s, "1.2.3.4", "register", now=100.0)
    assert allowed is True


# ───────── HTTP-level integration ─────────


def test_login_returns_429_after_max_attempts(client, monkeypatch):
    """11th login attempt with bad creds should be 429, not 401."""
    # Default in test conftest: enabled=True, max=10, window=600. The
    # conftest fixture has already used 1 successful attempt during
    # setup, so we have 9 remaining to exhaust.
    monkeypatch.setenv("RATE_LIMIT_LOGIN_MAX", "3")
    monkeypatch.setenv("RATE_LIMIT_LOGIN_WINDOW_SECONDS", "60")
    # Force settings refresh
    from app.config import get_settings

    get_settings.cache_clear()
    _current_limiter()[1]()
    try:
        # 3 bad attempts under quota → 401
        for _ in range(3):
            r = client.post(
                "/login",
                data={"username": "x", "password": "wrong"},
                follow_redirects=False,
            )
            assert r.status_code in (401, 303)
        # 4th attempt → 429
        r = client.post(
            "/login",
            data={"username": "x", "password": "wrong"},
            follow_redirects=False,
        )
        assert r.status_code == 429
        assert "Retry-After" in r.headers
        # Sober message — no username/email/account-exists leak
        body = r.text.lower()
        for forbidden in ("user", "exist", "registered", "account", "email"):
            assert forbidden not in body, f"429 leaks {forbidden!r}: {body}"
    finally:
        get_settings.cache_clear()
        _current_limiter()[1]()


def test_register_returns_429_after_max_attempts(client, monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_REGISTER_MAX", "2")
    monkeypatch.setenv("RATE_LIMIT_REGISTER_WINDOW_SECONDS", "60")
    from app.config import get_settings

    get_settings.cache_clear()
    _current_limiter()[1]()
    try:
        for i in range(2):
            r = client.post(
                "/register",
                data={"username": f"new{i}", "password": "abcdefgh1!"},
                follow_redirects=False,
            )
            # 303 redirect on success, 4xx on validation error — both
            # count toward the quota
            assert r.status_code != 429
        r = client.post(
            "/register",
            data={"username": "newX", "password": "abcdefgh1!"},
            follow_redirects=False,
        )
        assert r.status_code == 429
        assert "Retry-After" in r.headers
    finally:
        get_settings.cache_clear()
        _current_limiter()[1]()


def test_forgot_password_returns_429_after_max_attempts(client, monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_FORGOT_MAX", "2")
    monkeypatch.setenv("RATE_LIMIT_FORGOT_WINDOW_SECONDS", "60")
    from app.config import get_settings

    get_settings.cache_clear()
    _current_limiter()[1]()
    try:
        for _ in range(2):
            r = client.post(
                "/forgot-password",
                data={"email": "x@example.com"},
                follow_redirects=False,
            )
            assert r.status_code != 429
        r = client.post(
            "/forgot-password",
            data={"email": "x@example.com"},
            follow_redirects=False,
        )
        assert r.status_code == 429
    finally:
        get_settings.cache_clear()
        _current_limiter()[1]()


def test_rate_limit_can_be_disabled(client, monkeypatch):
    """RATE_LIMIT_ENABLED=0 → no 429 ever."""
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "0")
    monkeypatch.setenv("RATE_LIMIT_LOGIN_MAX", "1")
    from app.config import get_settings

    get_settings.cache_clear()
    _current_limiter()[1]()
    try:
        for _ in range(5):
            r = client.post(
                "/login",
                data={"username": "x", "password": "wrong"},
                follow_redirects=False,
            )
            assert r.status_code != 429
    finally:
        get_settings.cache_clear()
        _current_limiter()[1]()


def test_rate_limit_does_not_apply_to_other_routes(client):
    """Sanity: /healthz must never get 429-ed even under heavy load."""
    _current_limiter()[1]()
    for _ in range(20):
        r = client.get("/healthz")
        assert r.status_code == 200
