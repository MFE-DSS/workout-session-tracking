"""Tests for password reset flow."""
from __future__ import annotations

from app.services.auth import create_reset_token, verify_reset_token


def test_create_and_verify_reset_token():
    token = create_reset_token(user_id=42)
    assert isinstance(token, str)
    assert len(token) > 20
    result = verify_reset_token(token)
    assert result == 42


def test_verify_reset_token_expired():
    token = create_reset_token(user_id=42)
    result = verify_reset_token(token, max_age=0)
    assert result is None


def test_verify_reset_token_tampered():
    result = verify_reset_token("not-a-valid-token")
    assert result is None


def test_verify_reset_token_wrong_purpose():
    """A session cookie token should not work as a reset token."""
    from app.services.auth import _serializer
    token = _serializer().dumps({"user_id": 42})
    result = verify_reset_token(token)
    assert result is None


def test_email_send_returns_false_when_smtp_disabled(client):
    """With default config (no SMTP), send_email returns False."""
    from app.services.email import send_email
    result = send_email("test@example.com", "Subject", "Body")
    assert result is False


from tests.helpers import get_test_user_id


def test_forgot_password_page_renders(client):
    r = client.get("/forgot-password")
    assert r.status_code == 200
    assert "oubli" in r.text.lower()


def test_forgot_password_submit_always_shows_success(client):
    r = client.post("/forgot-password", data={"email": "nonexistent@example.com"})
    assert r.status_code == 200
    assert "lien" in r.text.lower() or "envoy" in r.text.lower()


def test_forgot_password_submit_with_real_email(client):
    from app.database import SessionLocal
    from app.models.user import User
    from sqlalchemy import select

    with SessionLocal() as db:
        user = db.execute(select(User).where(User.username == "testuser")).scalar_one()
        user.email = "test@example.com"
        db.commit()

    r = client.post("/forgot-password", data={"email": "test@example.com"})
    assert r.status_code == 200
    assert "lien" in r.text.lower() or "envoy" in r.text.lower()


def test_reset_page_invalid_token(client):
    r = client.get("/reset/invalid-token")
    assert r.status_code == 200
    assert "expir" in r.text.lower() or "invalide" in r.text.lower()


def test_reset_page_valid_token(client):
    from app.services.auth import create_reset_token
    uid = get_test_user_id()
    token = create_reset_token(uid)
    r = client.get(f"/reset/{token}")
    assert r.status_code == 200
    assert "new_password" in r.text


def test_reset_submit_changes_password(client):
    from app.services.auth import create_reset_token
    uid = get_test_user_id()
    token = create_reset_token(uid)
    r = client.post(f"/reset/{token}", data={
        "new_password": "newpass123",
        "new_password_confirm": "newpass123",
    }, follow_redirects=False)
    assert r.status_code == 303
    assert "/login" in r.headers.get("location", "")

    r2 = client.post("/login", data={
        "username": "testuser",
        "password": "newpass123",
    }, follow_redirects=False)
    assert r2.status_code == 303


def test_reset_submit_password_mismatch(client):
    from app.services.auth import create_reset_token
    uid = get_test_user_id()
    token = create_reset_token(uid)
    r = client.post(f"/reset/{token}", data={
        "new_password": "newpass123",
        "new_password_confirm": "different",
    })
    assert r.status_code == 400


def test_register_with_email(client):
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()

    r = client.post("/register", data={
        "username": "emailuser",
        "password": "pass1234",
        "password_confirm": "pass1234",
        "email": "emailuser@example.com",
    }, follow_redirects=False)
    assert r.status_code == 303

    from app.database import SessionLocal
    from app.models.user import User
    from sqlalchemy import select
    with SessionLocal() as db:
        user = db.execute(select(User).where(User.username == "emailuser")).scalar_one()
        assert user.email == "emailuser@example.com"


def test_register_without_email(client):
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()

    r = client.post("/register", data={
        "username": "noemailuser",
        "password": "pass1234",
        "password_confirm": "pass1234",
        "email": "",
    }, follow_redirects=False)
    assert r.status_code == 303

    from app.database import SessionLocal
    from app.models.user import User
    from sqlalchemy import select
    with SessionLocal() as db:
        user = db.execute(select(User).where(User.username == "noemailuser")).scalar_one()
        assert user.email is None


def test_profile_shows_email(client):
    body = client.get("/profile").text
    assert "Email" in body or "email" in body
