"""Sprint AUTH_01: authentication tests."""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------


def test_password_hash_is_not_plaintext(client):
    from app.services.auth import hash_password

    hashed = hash_password("secret123")
    assert hashed != "secret123"
    assert len(hashed) > 20


def test_password_verify_correct(client):
    from app.services.auth import hash_password, verify_password

    hashed = hash_password("secret123")
    assert verify_password("secret123", hashed) is True


def test_password_verify_wrong(client):
    from app.services.auth import hash_password, verify_password

    hashed = hash_password("secret123")
    assert verify_password("wrong", hashed) is False


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------


def test_login_page_renders(client):
    # Logout first so we hit the login page as anonymous
    client.post("/logout", follow_redirects=False)
    r = client.get("/login")
    assert r.status_code == 200
    assert "Connexion" in r.text


def test_login_success_sets_cookie_and_redirects(client):
    client.post("/logout", follow_redirects=False)
    r = client.post(
        "/login",
        data={"username": "testuser", "password": "testpass"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert r.headers.get("location", "").endswith("/")
    assert "session_token" in r.headers.get("set-cookie", "")


def test_login_failure_shows_error(client):
    client.post("/logout", follow_redirects=False)
    r = client.post(
        "/login",
        data={"username": "testuser", "password": "wrongpass"},
        follow_redirects=False,
    )
    assert r.status_code == 401
    assert "Identifiants invalides" in r.text


def test_login_unknown_user_fails(client):
    client.post("/logout", follow_redirects=False)
    r = client.post(
        "/login",
        data={"username": "nobody", "password": "anything"},
        follow_redirects=False,
    )
    assert r.status_code == 401


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------


def test_logout_clears_access(client):
    r = client.post("/logout", follow_redirects=False)
    assert r.status_code == 303
    client.cookies.clear()
    # After logout, accessing a private route should redirect to /login
    r2 = client.get("/", follow_redirects=False)
    assert r2.status_code == 303
    assert "/login" in r2.headers.get("location", "")


# ---------------------------------------------------------------------------
# Protected routes redirect when not authenticated
# ---------------------------------------------------------------------------


def test_private_routes_redirect_to_login_when_anonymous(client):
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()
    for path in ["/", "/library", "/history", "/progress", "/science", "/export", "/admin/sessions"]:
        r = client.get(path, follow_redirects=False)
        assert r.status_code == 303, f"{path} did not redirect: {r.status_code}"
        assert "/login" in r.headers.get("location", ""), f"{path} redirect target wrong"


# ---------------------------------------------------------------------------
# Public routes are accessible without auth
# ---------------------------------------------------------------------------


def test_public_routes_accessible_without_auth(client):
    client.post("/logout", follow_redirects=False)
    for path in ["/welcome", "/healthz", "/healthz/strict"]:
        r = client.get(path, follow_redirects=False)
        assert r.status_code == 200, f"{path} should be public: {r.status_code}"


# ---------------------------------------------------------------------------
# User model
# ---------------------------------------------------------------------------


def test_user_exists_in_db(client):
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.execute(select(User).where(User.username == "testuser")).scalar_one()
        assert user.is_active is True
        assert user.created_at is not None
        assert user.password_hash != "testpass"


# ---------------------------------------------------------------------------
# Welcome (public landing)
# ---------------------------------------------------------------------------


def test_welcome_page_renders(client):
    r = client.get("/welcome")
    assert r.status_code == 200
    assert "Auren" in r.text  # Sb_UI_10.3 — visible product name
    assert "Connexion" in r.text
