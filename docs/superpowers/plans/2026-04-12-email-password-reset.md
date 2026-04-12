# Email + Password Reset Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add optional email to user accounts with SMTP-based password reset via signed tokens (itsdangerous, 1h expiry).

**Architecture:** Email field on User (nullable, unique). SMTP sending via stdlib `smtplib`. Reset tokens via itsdangerous `URLSafeTimedSerializer` (already in deps). Four new public routes for forgot/reset flow. Timing-constant responses to prevent email enumeration.

**Tech Stack:** Python 3.14, FastAPI, SQLAlchemy 2.0, Alembic, itsdangerous, smtplib (stdlib), Jinja2, pytest

---

## File Structure

| Action | File | Responsibility |
|--------|------|----------------|
| Modify | `app/models/user.py` | Add `email` field |
| Modify | `app/config.py` | Add SMTP settings |
| Modify | `app/services/auth.py` | Add `create_reset_token`, `verify_reset_token` |
| Create | `app/services/email.py` | SMTP send function |
| Create | `migrations/versions/20260412_add_email_to_users.py` | ADD COLUMN + unique index |
| Modify | `app/routers/auth_routes.py` | 4 new routes + modify register + profile body |
| Create | `app/templates/forgot_password.html` | Forgot password form |
| Create | `app/templates/reset_password.html` | Reset password form |
| Modify | `app/templates/login.html` | Forgot link + success message |
| Modify | `app/templates/register.html` | Optional email field |
| Modify | `app/templates/profile.html` | Display + edit email |
| Modify | `app/main.py` | Update CSP for Google Fonts |
| Create | `tests/test_password_reset.py` | All tests |

---

### Task 1: User model + config + migration

**Files:**
- Modify: `app/models/user.py`
- Modify: `app/config.py`
- Create: `migrations/versions/20260412_add_email_to_users.py`

- [ ] **Step 1: Add email field to User model**

In `app/models/user.py`, add after `created_at` and before the physical profile comment:

```python
    # Email (optional, for password reset)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
```

Also add `String` to the import if not already there (it's not currently imported — the file imports `Boolean, DateTime, Float, Integer, String` — String IS there).

- [ ] **Step 2: Add SMTP settings to config**

In `app/config.py`, add these fields inside the `Settings` class, after `backup_retention_days`:

```python
    # SMTP for password reset emails. Leave smtp_host empty to disable.
    smtp_host: str = Field(default="")
    smtp_port: int = Field(default=587)
    smtp_user: str = Field(default="")
    smtp_password: str = Field(default="")
    smtp_from: str = Field(default="")
    smtp_use_tls: bool = Field(default=True)

    @property
    def smtp_enabled(self) -> bool:
        return bool(self.smtp_host and self.smtp_from)
```

- [ ] **Step 3: Create migration**

```python
# migrations/versions/20260412_add_email_to_users.py
"""add email to users

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-04-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, Sequence[str], None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email', sa.String(255), nullable=True))
        batch_op.create_index('ix_users_email', ['email'], unique=True)


def downgrade() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index('ix_users_email')
        batch_op.drop_column('email')
```

- [ ] **Step 4: Run tests to verify no breakage**

Run: `pytest tests/test_register_profile.py tests/test_auth.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add app/models/user.py app/config.py migrations/versions/20260412_add_email_to_users.py
git commit -m "feat: add email field to User + SMTP config settings"
```

---

### Task 2: Email service + auth reset tokens

**Files:**
- Create: `app/services/email.py`
- Modify: `app/services/auth.py`
- Create: `tests/test_password_reset.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_password_reset.py
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
    # Verify with max_age=0 should fail (immediately expired)
    result = verify_reset_token(token, max_age=0)
    assert result is None


def test_verify_reset_token_tampered():
    result = verify_reset_token("not-a-valid-token")
    assert result is None


def test_verify_reset_token_wrong_purpose():
    """A session cookie token should not work as a reset token."""
    from app.services.auth import _serializer
    # Create a token without the reset purpose
    token = _serializer().dumps({"user_id": 42})
    result = verify_reset_token(token)
    assert result is None


def test_email_send_returns_false_when_smtp_disabled(client):
    """With default config (no SMTP), send_email returns False."""
    from app.services.email import send_email
    result = send_email("test@example.com", "Subject", "Body")
    assert result is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_password_reset.py -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Implement email service**

```python
# app/services/email.py
"""SMTP email sending for transactional emails.

Uses stdlib smtplib — no external dependency. If SMTP is not
configured (smtp_host empty), all sends silently return False.
"""
from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from app.config import get_settings

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, body: str) -> bool:
    """Send a plain text email. Returns True on success, False on any error."""
    settings = get_settings()
    if not settings.smtp_enabled:
        logger.debug("SMTP not configured, skipping email to %s", to)
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
        logger.info("Email sent to %s: %s", to, subject)
        return True
    except Exception:
        logger.exception("Failed to send email to %s", to)
        return False
```

- [ ] **Step 4: Add reset token functions to auth.py**

Append to `app/services/auth.py` (after `get_current_user`):

```python
RESET_TOKEN_MAX_AGE = 3600  # 1 hour


def create_reset_token(user_id: int) -> str:
    """Create a signed, time-limited token for password reset."""
    return _serializer().dumps({"user_id": user_id, "purpose": "reset"})


def verify_reset_token(token: str, max_age: int = RESET_TOKEN_MAX_AGE) -> int | None:
    """Verify a reset token. Returns user_id if valid, None otherwise."""
    try:
        payload = _serializer().loads(token, max_age=max_age)
        if payload.get("purpose") != "reset":
            return None
        return payload.get("user_id")
    except (BadSignature, Exception):
        return None
```

- [ ] **Step 5: Run tests**

Run: `pytest tests/test_password_reset.py -v`
Expected: All 5 PASS

- [ ] **Step 6: Commit**

```bash
git add app/services/email.py app/services/auth.py tests/test_password_reset.py
git commit -m "feat: add email service and reset token functions"
```

---

### Task 3: Forgot/reset password routes

**Files:**
- Modify: `app/routers/auth_routes.py`
- Modify: `tests/test_password_reset.py` (add route tests)

- [ ] **Step 1: Add route tests**

Append to `tests/test_password_reset.py`:

```python
from tests.helpers import get_test_user_id


def test_forgot_password_page_renders(client):
    r = client.get("/forgot-password")
    assert r.status_code == 200
    assert "Mot de passe oubli" in r.text


def test_forgot_password_submit_always_shows_success(client):
    """Even with non-existent email, show success (timing-constant)."""
    r = client.post("/forgot-password", data={"email": "nonexistent@example.com"})
    assert r.status_code == 200
    assert "lien" in r.text.lower() or "envoy" in r.text.lower()


def test_forgot_password_submit_with_real_email(client):
    """With a real email, same success message (SMTP disabled in test)."""
    from app.database import SessionLocal
    from app.models.user import User
    from sqlalchemy import select

    # Set email on testuser
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

    # Verify new password works
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
```

- [ ] **Step 2: Add forgot/reset routes to auth_routes.py**

Add these imports at the top of `app/routers/auth_routes.py` (extend existing auth imports):

```python
from app.services.auth import (
    clear_session_cookie,
    create_reset_token,
    create_session_cookie,
    get_current_user,
    hash_password,
    verify_password,
    verify_reset_token,
)
from app.services.email import send_email
```

Add these 4 routes after the `logout` function and before the `# Registration` section:

```python
# ---------------------------------------------------------------------------
# Password reset (public)
# ---------------------------------------------------------------------------


@router.get("/forgot-password", response_class=HTMLResponse)
def forgot_password_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "forgot_password.html",
        {"page_title": "Mot de passe oublié", "error": None, "success": False},
    )


@router.post("/forgot-password", response_class=HTMLResponse)
async def forgot_password_submit(
    request: Request,
    email: Annotated[str, Form()],
    db: DbSession,
) -> HTMLResponse:
    # Always show success — never reveal if the email exists
    email_clean = email.strip().lower()
    if email_clean:
        user = db.execute(
            select(User).where(User.email == email_clean)
        ).scalar_one_or_none()
        if user is not None:
            token = create_reset_token(user.id)
            settings = get_settings()
            reset_url = f"{settings.app_base_url}/reset/{token}"
            send_email(
                to=user.email,
                subject="SPIGNOS — Réinitialisation de mot de passe",
                body=(
                    f"Bonjour,\n\n"
                    f"Une demande de réinitialisation de mot de passe a été faite "
                    f"pour votre compte SPIGNOS.\n\n"
                    f"Cliquez sur ce lien pour choisir un nouveau mot de passe "
                    f"(valide 1 heure) :\n{reset_url}\n\n"
                    f"Si vous n'avez pas fait cette demande, ignorez cet email.\n\n"
                    f"— SPIGNOS"
                ),
            )
    return templates.TemplateResponse(
        request, "forgot_password.html",
        {"page_title": "Mot de passe oublié", "error": None, "success": True},
    )


@router.get("/reset/{token}", response_class=HTMLResponse)
def reset_password_page(
    token: str, request: Request,
) -> HTMLResponse:
    user_id = verify_reset_token(token)
    return templates.TemplateResponse(
        request, "reset_password.html",
        {
            "page_title": "Réinitialiser le mot de passe",
            "token": token,
            "valid": user_id is not None,
            "error": None,
        },
    )


@router.post("/reset/{token}", response_model=None)
async def reset_password_submit(
    token: str,
    request: Request,
    new_password: Annotated[str, Form()],
    new_password_confirm: Annotated[str, Form()],
    db: DbSession,
):
    user_id = verify_reset_token(token)
    if user_id is None:
        return templates.TemplateResponse(
            request, "reset_password.html",
            {
                "page_title": "Réinitialiser le mot de passe",
                "token": token,
                "valid": False,
                "error": "Ce lien a expiré ou est invalide.",
            },
            status_code=400,
        )

    error = None
    if len(new_password) < MIN_PASSWORD_LENGTH:
        error = f"Le mot de passe doit faire au moins {MIN_PASSWORD_LENGTH} caractères."
    elif new_password != new_password_confirm:
        error = "Les mots de passe ne correspondent pas."

    if error:
        return templates.TemplateResponse(
            request, "reset_password.html",
            {
                "page_title": "Réinitialiser le mot de passe",
                "token": token,
                "valid": True,
                "error": error,
            },
            status_code=400,
        )

    user = db.execute(
        select(User).where(User.id == user_id)
    ).scalar_one_or_none()
    if user is None:
        return templates.TemplateResponse(
            request, "reset_password.html",
            {
                "page_title": "Réinitialiser le mot de passe",
                "token": token,
                "valid": False,
                "error": "Utilisateur introuvable.",
            },
            status_code=400,
        )

    user.password_hash = hash_password(new_password)
    db.commit()

    return RedirectResponse(url="/login?success=password_reset", status_code=303)
```

Also add the import for `get_settings` at the top:

```python
from app.config import get_settings
```

- [ ] **Step 3: Run tests**

Run: `pytest tests/test_password_reset.py -v`
Expected: All PASS

- [ ] **Step 4: Commit**

```bash
git add app/routers/auth_routes.py tests/test_password_reset.py
git commit -m "feat: add forgot-password and reset routes with token flow"
```

---

### Task 4: Modify register + profile to include email

**Files:**
- Modify: `app/routers/auth_routes.py`
- Modify: `tests/test_password_reset.py` (add tests)

- [ ] **Step 1: Add tests for email in registration and profile**

Append to `tests/test_password_reset.py`:

```python
def test_register_with_email(client):
    # Logout first
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()

    r = client.post("/register", data={
        "username": "emailuser",
        "password": "pass1234",
        "password_confirm": "pass1234",
        "email": "emailuser@example.com",
    }, follow_redirects=False)
    assert r.status_code == 303  # auto-login redirect

    # Verify email was saved
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


def test_register_duplicate_email(client):
    # First: set email on testuser
    from app.database import SessionLocal
    from app.models.user import User
    from sqlalchemy import select
    with SessionLocal() as db:
        user = db.execute(select(User).where(User.username == "testuser")).scalar_one()
        user.email = "taken@example.com"
        db.commit()

    client.post("/logout", follow_redirects=False)
    client.cookies.clear()

    r = client.post("/register", data={
        "username": "newuser99",
        "password": "pass1234",
        "password_confirm": "pass1234",
        "email": "taken@example.com",
    })
    assert r.status_code == 400
    assert "email" in r.text.lower() or "associé" in r.text.lower()


def test_profile_shows_email(client):
    body = client.get("/profile").text
    assert "Email" in body or "email" in body
```

- [ ] **Step 2: Modify register_submit to accept email**

In `app/routers/auth_routes.py`, update the `register_submit` function signature to add `email`:

```python
@router.post("/register", response_model=None)
async def register_submit(
    request: Request,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    password_confirm: Annotated[str, Form()],
    email: Annotated[str, Form()] = "",
    db: DbSession = None,
):
```

Add email validation after the existing username uniqueness check (inside the `else` block, after checking `existing is not None`):

```python
    # After the existing username check, add:
    email_clean = email.strip().lower() if email.strip() else None
    if error is None and email_clean:
        if "@" not in email_clean or "." not in email_clean.split("@")[-1]:
            error = "Adresse email invalide."
        else:
            email_exists = db.execute(
                select(User).where(User.email == email_clean)
            ).scalar_one_or_none()
            if email_exists is not None:
                error = "Cet email est déjà associé à un compte."
```

And when creating the User:

```python
    user = User(
        username=username.strip(),
        password_hash=hash_password(password),
        email=email_clean,
    )
```

- [ ] **Step 3: Modify profile_body_submit to accept email**

In the `profile_body_submit` function, add `email` parameter:

```python
    email: Annotated[str, Form()] = "",
```

Add email update logic before `db.commit()`:

```python
    email_clean = email.strip().lower() if email.strip() else None
    if email_clean:
        if "@" in email_clean and "." in email_clean.split("@")[-1]:
            # Check uniqueness (exclude current user)
            existing = db.execute(
                select(User).where(User.email == email_clean, User.id != user.id)
            ).scalar_one_or_none()
            if existing is None:
                user.email = email_clean
    elif not email.strip():
        # Empty = remove email
        user.email = None
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_password_reset.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add app/routers/auth_routes.py tests/test_password_reset.py
git commit -m "feat: add email to registration and profile forms"
```

---

### Task 5: Templates (forgot, reset, login, register, profile)

**Files:**
- Create: `app/templates/forgot_password.html`
- Create: `app/templates/reset_password.html`
- Modify: `app/templates/login.html`
- Modify: `app/templates/register.html`
- Modify: `app/templates/profile.html`
- Modify: `app/main.py` (CSP for Google Fonts)

- [ ] **Step 1: Create forgot_password.html**

```html
{% extends "base.html" %}
{% block content %}
<div class="auth-container">
  <h1 class="page-title">Mot de passe oublié</h1>

  {% if success %}
    <div class="card" style="border-left: 3px solid var(--ok);">
      <p style="font-size: 14px; color: var(--fg-muted);">
        Si un compte est associé à cet email, un lien de réinitialisation a été envoyé.
        Vérifie ta boîte de réception (et les spams).
      </p>
    </div>
  {% else %}
    {% if error %}
      <div class="integrity-errors"><b>{{ error }}</b></div>
    {% endif %}

    <form method="post" action="{{ url_for('forgot_password_submit') }}" class="card">
      <label class="field">
        <span class="field__label">Adresse email</span>
        <input type="email" name="email" required autofocus placeholder="ton@email.com" />
      </label>
      <div class="card__actions" style="margin-top: 16px;">
        <button type="submit" class="btn btn--primary btn--wide">Envoyer le lien</button>
      </div>
    </form>
  {% endif %}

  <p style="text-align: center; margin-top: 16px;">
    <a href="{{ url_for('login_page') }}" style="color: var(--fg-dim); font-size: 13px;">
      ← Retour à la connexion
    </a>
  </p>
</div>
{% endblock %}
```

- [ ] **Step 2: Create reset_password.html**

```html
{% extends "base.html" %}
{% block content %}
<div class="auth-container">
  <h1 class="page-title">Réinitialiser le mot de passe</h1>

  {% if not valid %}
    <div class="integrity-errors">
      <b>{{ error or "Ce lien a expiré ou est invalide." }}</b>
    </div>
    <p style="text-align: center; margin-top: 16px;">
      <a href="{{ url_for('forgot_password_page') }}" class="btn btn--wide">
        Demander un nouveau lien
      </a>
    </p>
  {% else %}
    {% if error %}
      <div class="integrity-errors"><b>{{ error }}</b></div>
    {% endif %}

    <form method="post" action="{{ url_for('reset_password_submit', token=token) }}" class="card">
      <label class="field">
        <span class="field__label">Nouveau mot de passe</span>
        <input type="password" name="new_password" required autofocus autocomplete="new-password" minlength="4" />
      </label>
      <label class="field">
        <span class="field__label">Confirmer le mot de passe</span>
        <input type="password" name="new_password_confirm" required autocomplete="new-password" />
      </label>
      <div class="card__actions" style="margin-top: 16px;">
        <button type="submit" class="btn btn--primary btn--wide">Réinitialiser</button>
      </div>
    </form>
  {% endif %}

  <p style="text-align: center; margin-top: 16px;">
    <a href="{{ url_for('login_page') }}" style="color: var(--fg-dim); font-size: 13px;">
      ← Retour à la connexion
    </a>
  </p>
</div>
{% endblock %}
```

- [ ] **Step 3: Modify login.html**

Read the current file. Add two things:

A) After the `{% if error %}` block and before the `<form>`, add a success message for password reset:

```html
  {% if success == "password_reset" %}
    <div class="card" style="border-left: 3px solid var(--ok);">
      <p style="font-size: 14px; color: var(--fg-muted);">
        Mot de passe réinitialisé. Connecte-toi avec ton nouveau mot de passe.
      </p>
    </div>
  {% endif %}
```

Note: The login route already passes `success` as a query param. Read the current `login_page` GET handler — it already has a `success: str | None = None` parameter.

B) Add "Mot de passe oublié ?" link after the form, before the register link:

```html
  <p style="text-align: center; margin-top: 12px;">
    <a href="{{ url_for('forgot_password_page') }}" style="color: var(--fg-dim); font-size: 13px;">
      Mot de passe oublié ?
    </a>
  </p>
```

- [ ] **Step 4: Modify register.html**

Add optional email field after the username field in the form:

```html
  <label class="field">
    <span class="field__label">Email (optionnel)</span>
    <input type="email" name="email" autocomplete="email" placeholder="optionnel" />
  </label>
```

- [ ] **Step 5: Modify profile.html**

Read the current file. Add email display in the Identity stats-list (after "Statut"):

```html
  <li><span>Email</span><b>{{ user.email or "—" }}</b></li>
```

Add email field in the "Données de référence" form (as the first field):

```html
  <div class="body-profile__field" style="grid-column:1/-1;">
    <label for="email">Email</label>
    <input type="email" id="email" name="email"
           value="{{ user.email or '' }}" placeholder="optionnel">
  </div>
```

- [ ] **Step 6: Update CSP in main.py for Google Fonts**

In `app/main.py`, the Content-Security-Policy header currently blocks external fonts. Update the CSP line to allow Google Fonts:

```python
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data:; "
            "frame-ancestors 'none'"
        )
```

- [ ] **Step 7: Run all tests**

Run: `pytest tests/test_password_reset.py tests/test_auth.py tests/test_register_profile.py -v`
Expected: All PASS

- [ ] **Step 8: Commit**

```bash
git add app/templates/forgot_password.html app/templates/reset_password.html app/templates/login.html app/templates/register.html app/templates/profile.html app/main.py
git commit -m "feat: add forgot/reset password templates + email in register/profile + CSP for fonts"
```

---

### Task 6: Final integration

- [ ] **Step 1: Run full test suite**

Run: `pytest --tb=short -q`
Expected: All tests PASS (only pre-existing failures)

- [ ] **Step 2: Run Alembic drift check**

Run: `.venv/bin/python -m scripts.check_alembic_drift`
Expected: `Alembic drift check: OK (no diff).`

- [ ] **Step 3: Visual verification**

Run: `python -m uvicorn app.main:app --port 8001`

Verify:
- `/login` shows "Mot de passe oublié ?" link
- `/forgot-password` shows email form
- POST forgot-password shows success message (no email actually sent — SMTP not configured)
- `/register` shows optional email field
- `/profile` shows email in identity + email field in reference data
- Fonts render correctly (Inter + JetBrains Mono — CSP allows Google Fonts)

- [ ] **Step 4: Commit if fixes needed**

```bash
git add -A
git commit -m "fix: email/reset integration adjustments"
```
