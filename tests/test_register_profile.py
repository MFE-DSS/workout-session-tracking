"""Registration, profile, and password change tests."""
from __future__ import annotations


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def test_register_page_renders(client):
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()
    r = client.get("/register")
    assert r.status_code == 200
    assert "Inscription" in r.text
    assert 'name="username"' in r.text
    assert 'name="password_confirm"' in r.text


def test_register_success_creates_user_and_auto_logs_in(client):
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()

    r = client.post(
        "/register",
        data={
            "username": "newuser",
            "password": "newpass1",
            "password_confirm": "newpass1",
        },
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert r.headers["location"].endswith("/")
    # The cookie is set — verify by hitting a private route
    r2 = client.get("/", follow_redirects=False)
    assert r2.status_code == 200

    # User exists in DB
    from sqlalchemy import select
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        u = db.execute(select(User).where(User.username == "newuser")).scalar_one()
        assert u.is_active is True
        assert u.password_hash != "newpass"


def test_register_duplicate_username_rejected(client):
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()

    r = client.post(
        "/register",
        data={
            "username": "testuser",  # already exists (conftest)
            "password": "anything",
            "password_confirm": "anything",
        },
        follow_redirects=False,
    )
    assert r.status_code == 400
    assert "déjà pris" in r.text


def test_register_password_mismatch_rejected(client):
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()

    r = client.post(
        "/register",
        data={
            "username": "mismatchuser",
            "password": "pass1234",
            "password_confirm": "pass5678",
        },
        follow_redirects=False,
    )
    assert r.status_code == 400
    assert "ne correspondent pas" in r.text


def test_register_short_username_rejected(client):
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()

    r = client.post(
        "/register",
        data={
            "username": "ab",
            "password": "pass1234",
            "password_confirm": "pass1234",
        },
        follow_redirects=False,
    )
    assert r.status_code == 400
    assert "au moins" in r.text


def test_register_short_password_rejected(client):
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()

    r = client.post(
        "/register",
        data={
            "username": "shortpwuser",
            "password": "ab",
            "password_confirm": "ab",
        },
        follow_redirects=False,
    )
    assert r.status_code == 400
    assert "au moins" in r.text


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------


def test_profile_requires_auth(client):
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()
    r = client.get("/profile", follow_redirects=False)
    assert r.status_code == 303
    assert "/login" in r.headers.get("location", "")


def test_profile_renders_for_authenticated_user(client):
    r = client.get("/profile")
    assert r.status_code == 200
    assert "testuser" in r.text
    assert "Sessions totales" in r.text
    assert "Changer le mot de passe" in r.text


# ---------------------------------------------------------------------------
# Password change
# ---------------------------------------------------------------------------


def test_password_change_page_renders(client):
    r = client.get("/profile/password")
    assert r.status_code == 200
    assert "Changer le mot de passe" in r.text
    assert 'name="current_password"' in r.text


def test_password_change_success(client):
    r = client.post(
        "/profile/password",
        data={
            "current_password": "testpass",
            "new_password": "newpass123",
            "new_password_confirm": "newpass123",
        },
        follow_redirects=False,
    )
    assert r.status_code == 200
    assert "succès" in r.text or "succ" in r.text


def test_password_change_fails_wrong_current(client):
    r = client.post(
        "/profile/password",
        data={
            "current_password": "wrongcurrent",
            "new_password": "newpass123",
            "new_password_confirm": "newpass123",
        },
        follow_redirects=False,
    )
    assert r.status_code == 400
    assert "incorrect" in r.text


def test_password_change_fails_mismatch(client):
    r = client.post(
        "/profile/password",
        data={
            "current_password": "testpass",
            "new_password": "aaa11111",
            "new_password_confirm": "bbb22222",
        },
        follow_redirects=False,
    )
    assert r.status_code == 400
    assert "ne correspondent pas" in r.text


def test_login_works_with_new_password_after_change(client):
    # Change password
    client.post(
        "/profile/password",
        data={
            "current_password": "testpass",
            "new_password": "changed99",
            "new_password_confirm": "changed99",
        },
        follow_redirects=False,
    )

    # Logout
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()

    # Login with NEW password
    r = client.post(
        "/login",
        data={"username": "testuser", "password": "changed99"},
        follow_redirects=False,
    )
    assert r.status_code == 303

    # Old password no longer works
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()
    r2 = client.post(
        "/login",
        data={"username": "testuser", "password": "testpass"},
        follow_redirects=False,
    )
    assert r2.status_code == 401


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------


def test_base_template_has_profile_link(client):
    body = client.get("/").text
    assert "/profile" in body
    assert "Profil" in body


def test_login_page_has_register_link(client):
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()
    body = client.get("/login").text
    assert "/register" in body
    assert "inscrire" in body.lower()


def test_welcome_page_has_register_link(client):
    body = client.get("/welcome").text
    assert "/register" in body
    assert "Créer un compte" in body
