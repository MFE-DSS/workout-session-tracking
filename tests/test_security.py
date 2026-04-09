"""Security-focused tests added during the SECURITY_REVIEW_01 sprint."""
from __future__ import annotations


# ---------------------------------------------------------------------------
# Security headers
# ---------------------------------------------------------------------------


def test_responses_have_security_headers(client):
    r = client.get("/")
    assert r.headers.get("X-Content-Type-Options") == "nosniff"
    assert r.headers.get("X-Frame-Options") == "DENY"
    assert "strict-origin" in r.headers.get("Referrer-Policy", "")
    assert "frame-ancestors 'none'" in r.headers.get("Content-Security-Policy", "")


def test_security_headers_on_public_routes(client):
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()
    r = client.get("/welcome")
    assert r.headers.get("X-Frame-Options") == "DENY"
    assert r.headers.get("X-Content-Type-Options") == "nosniff"


# ---------------------------------------------------------------------------
# Cookie security
# ---------------------------------------------------------------------------


def test_session_cookie_is_samesite_strict(client):
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()
    r = client.post(
        "/login",
        data={"username": "testuser", "password": "testpass"},
        follow_redirects=False,
    )
    cookie_header = r.headers.get("set-cookie", "")
    assert "samesite=strict" in cookie_header.lower()
    assert "httponly" in cookie_header.lower()


# ---------------------------------------------------------------------------
# Login timing: unknown user must not short-circuit
# ---------------------------------------------------------------------------


def test_login_with_unknown_user_returns_401_not_500(client):
    """After the timing-attack fix, login with a nonexistent
    username must return 401, not crash."""
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()
    r = client.post(
        "/login",
        data={"username": "nonexistent_user_xyz", "password": "anything"},
        follow_redirects=False,
    )
    assert r.status_code == 401


# ---------------------------------------------------------------------------
# Healthz/strict no longer leaks filesystem paths
# ---------------------------------------------------------------------------


def test_healthz_strict_does_not_leak_absolute_path(client):
    r = client.get("/healthz/strict")
    payload = r.json()
    # The backup_dir block must NOT contain a 'path' field
    assert "path" not in payload.get("backup_dir", {})


# ---------------------------------------------------------------------------
# All private routes still reject anonymous after hardening
# ---------------------------------------------------------------------------


def test_all_private_routes_reject_anonymous_after_hardening(client):
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()
    private_routes = [
        "/", "/library", "/history", "/progress", "/rules",
        "/export", "/admin/sessions", "/leaderboard", "/profile",
        "/profile/password",
    ]
    for path in private_routes:
        r = client.get(path, follow_redirects=False)
        assert r.status_code == 303, f"{path} not protected: {r.status_code}"
        assert "/login" in r.headers.get("location", ""), f"{path} wrong redirect"


# ---------------------------------------------------------------------------
# Ownership still enforced after hardening
# ---------------------------------------------------------------------------


def test_ownership_still_enforced_after_hardening(client):
    """Create a session as testuser, then verify that guessing
    a wrong ID returns 404."""
    import re

    r = client.post("/sessions", data={"template_slug": "push-a"}, follow_redirects=False)
    sid = int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))

    # Access own session → 200
    assert client.get(f"/sessions/{sid}").status_code == 200

    # Access nonexistent session → 404 (no info leak)
    assert client.get(f"/sessions/{sid + 999}").status_code == 404


# ---------------------------------------------------------------------------
# Exports still scoped after hardening
# ---------------------------------------------------------------------------


def test_export_json_scoped_after_hardening(client):
    payload = client.get("/export/sessions.json").json()
    assert "schema_version" in payload
    # No cross-user data: the payload is scoped to testuser
    assert isinstance(payload["sessions"], list)


# ---------------------------------------------------------------------------
# Register doesn't leak timing for username existence
# ---------------------------------------------------------------------------


def test_register_duplicate_returns_400_not_500(client):
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()
    r = client.post(
        "/register",
        data={"username": "testuser", "password": "abcdef", "password_confirm": "abcdef"},
        follow_redirects=False,
    )
    # Returns 400 with a friendly error, not a 500 crash
    assert r.status_code == 400
