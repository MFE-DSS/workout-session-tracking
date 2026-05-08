"""SMTP email sending for transactional emails.

Uses stdlib smtplib — no external dependency. If SMTP is not
configured (smtp_host empty), all sends silently return False.
"""
from __future__ import annotations

import hashlib
import logging
import smtplib
from email.message import EmailMessage

from app.config import get_settings

logger = logging.getLogger(__name__)


def _redact_email(addr: str) -> str:
    """Hash the address before logging to neutralize CRLF injection
    (CWE-117 / SonarCloud python:S5145) and avoid storing raw PII in logs.
    8 hex chars is enough to correlate in support without leaking the
    original recipient."""
    return hashlib.sha256(addr.encode("utf-8")).hexdigest()[:8]


def send_email(to: str, subject: str, body: str) -> bool:
    """Send a plain text email. Returns True on success, False on any error."""
    settings = get_settings()
    if not settings.smtp_enabled:
        logger.debug("SMTP not configured, skipping email to %s", _redact_email(to))
        return False

    msg = EmailMessage()
    msg["From"] = settings.smtp_from
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        if settings.smtp_port == 465:
            with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
                smtp.login(settings.smtp_user, settings.smtp_password)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
                if settings.smtp_use_tls:
                    smtp.starttls()
                if settings.smtp_user:
                    smtp.login(settings.smtp_user, settings.smtp_password)
                smtp.send_message(msg)
        # Sb_20.4 — never log `subject` verbatim: the contact form lets
        # users set the subject string, opening CWE-117 log injection.
        logger.info("Email sent to %s (subject_len=%d)", _redact_email(to), len(subject))
        return True
    except Exception:
        logger.exception("Failed to send email to %s", _redact_email(to))
        return False
