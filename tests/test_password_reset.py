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
