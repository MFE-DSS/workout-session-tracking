# Email + Password Reset — Design Spec

**Date:** 2026-04-12
**Scope:** Optional email field on User, SMTP email sending, token-based password reset flow

## Decisions

- Email: optional (nullable, unique) on User model
- SMTP via stdlib `smtplib`, config in `.env`
- Reset: signed token (itsdangerous, 1h expiry), link sent by email
- No token storage in DB — token is self-contained (signed)
- Timing-constant responses — never leak account existence
- If SMTP not configured, reset flow silently does nothing

## Constraints

- No new Python dependencies (smtplib is stdlib, itsdangerous already present)
- No breaking changes to existing auth flow
- All new routes are public (no auth required)
- Email is optional everywhere — app works fully without it

---

## 1. Data Model

### User model — new field

```
email    String(255), nullable=True, unique=True
```

- Nullable: email is optional
- Unique: one email per account (NULL values don't violate uniqueness)
- Validation: contains `@` and at least one `.` after `@` — no complex regex

### Migration

Additive: ADD COLUMN `email` (nullable) + CREATE UNIQUE INDEX.

---

## 2. Config

### New settings in `app/config.py`

```python
smtp_host: str = Field(default="")
smtp_port: int = Field(default=587)
smtp_user: str = Field(default="")
smtp_password: str = Field(default="")
smtp_from: str = Field(default="")
smtp_use_tls: bool = Field(default=True)
```

Property to check if email is enabled:

```python
@property
def smtp_enabled(self) -> bool:
    return bool(self.smtp_host and self.smtp_from)
```

If `smtp_host` is empty, all email operations silently return False.

### .env variables

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your@gmail.com
SMTP_USE_TLS=true
```

---

## 3. Email Service

### New file: `app/services/email.py`

**`send_email(to: str, subject: str, body: str) -> bool`**

- Checks `settings.smtp_enabled` — returns False if not configured
- Opens SMTP connection (port 587 → STARTTLS, port 465 → SMTP_SSL)
- Sends plain text email (no HTML)
- Returns True on success, False on any error
- Logs errors but never exposes them to the user
- Timeout: 10 seconds connect, 10 seconds send

---

## 4. Auth Service — Reset Tokens

### New functions in `app/services/auth.py`

**`create_reset_token(user_id: int) -> str`**

- Signs `{"user_id": user_id, "purpose": "reset"}` using `URLSafeTimedSerializer`
- Same `app_secret_key` as session cookies (different `purpose` field prevents cross-use)
- Returns URL-safe string

**`verify_reset_token(token: str, max_age: int = 3600) -> int | None`**

- Verifies signature + expiration (default 1 hour)
- Checks `purpose == "reset"`
- Returns `user_id` if valid, `None` if invalid/expired/tampered

No DB storage — token is self-contained. Trade-off: cannot invalidate before expiry (acceptable for 1h window).

---

## 5. Routes

### New routes (all public)

**`GET /forgot-password`**
- Renders `forgot_password.html` with email input field
- Template variables: `error` (None), `success` (False)

**`POST /forgot-password`**
- Accepts `email` from form
- Looks up User by email (case-insensitive)
- If found + `settings.smtp_enabled`: generates token, sends email with link `{app_base_url}/reset/{token}`
- Always displays: "Si un compte est associé à cet email, un lien de réinitialisation a été envoyé."
- Never reveals whether the email exists or whether SMTP is configured
- Template variables: `error` (None), `success` (True)

**`GET /reset/{token}`**
- Verifies token via `verify_reset_token()`
- If valid: renders `reset_password.html` with password + confirm fields
- If invalid: renders with error message + link back to `/forgot-password`
- Template variables: `token`, `error` (None or message), `valid` (bool)

**`POST /reset/{token}`**
- Re-verifies token
- Validates: password length >= 4, password == confirm
- If valid: hashes new password, updates User, redirects to `/login?success=password_reset`
- If invalid token: error message
- If validation fails: re-render form with error

### Modified routes

**`POST /register`**
- Add optional `email` form parameter
- If provided: validate format + check uniqueness
- If valid: store on User
- If duplicate: error "Cet email est déjà associé à un compte."

**`POST /profile/body`**
- Add optional `email` form parameter
- Same validation + uniqueness check
- Updates `user.email`

### Modified GET routes (template context)

**`GET /profile`** — User.email already available via `user` object in template.

---

## 6. Templates

### New templates

**`forgot_password.html`**
- Extends `base.html`
- `auth-container` centered layout
- Form: email input + submit button "Envoyer le lien"
- Success message (if success): green card with confirmation text
- Link back to `/login`

**`reset_password.html`**
- Extends `base.html`
- `auth-container` centered layout
- If valid token: form with new_password + new_password_confirm + submit "Réinitialiser"
- If invalid token: error message + link to `/forgot-password`
- Link back to `/login`

### Modified templates

**`login.html`**
- Add link below form: "Mot de passe oublié ?" → `/forgot-password`
- Add success message if `success == "password_reset"`: "Mot de passe réinitialisé. Connecte-toi avec ton nouveau mot de passe."

**`register.html`**
- Add optional email field after username: `<input type="email" name="email" placeholder="optionnel">`

**`profile.html`**
- Display email in Identity stats list: `Email` → `user.email or "—"`
- Add email field in "Données de référence" form

### Email content (plain text)

```
Subject: SPIGNOS — Réinitialisation de mot de passe

Bonjour,

Une demande de réinitialisation de mot de passe a été faite
pour votre compte SPIGNOS.

Cliquez sur ce lien pour choisir un nouveau mot de passe
(valide 1 heure) :
{app_base_url}/reset/{token}

Si vous n'avez pas fait cette demande, ignorez cet email.

— SPIGNOS
```

---

## 7. Security Considerations

| Concern | Mitigation |
|---------|-----------|
| Email enumeration | Always show same message regardless of account existence |
| Token prediction | Signed with app_secret_key via itsdangerous (cryptographically secure) |
| Token reuse | 1h expiry, purpose-scoped ("reset" != session cookie) |
| SMTP credentials | In .env, never in code, never logged |
| Brute force | Token is long URL-safe string (~100 chars), not guessable |
| Email in transit | TLS enforced on SMTP connection |
| Cross-purpose tokens | `purpose` field in payload prevents using session cookie as reset token |

---

## 8. Files Summary

| Action | File |
|--------|------|
| Modify | `app/models/user.py` — add `email` field |
| Modify | `app/config.py` — add SMTP settings |
| Modify | `app/services/auth.py` — add `create_reset_token`, `verify_reset_token` |
| Create | `app/services/email.py` — SMTP send function |
| Create | `migrations/versions/20260412_add_email_to_users.py` |
| Modify | `app/routers/auth_routes.py` — 4 new routes + modify register + profile |
| Create | `app/templates/forgot_password.html` |
| Create | `app/templates/reset_password.html` |
| Modify | `app/templates/login.html` — forgot password link + success message |
| Modify | `app/templates/register.html` — optional email field |
| Modify | `app/templates/profile.html` — display + edit email |
| Create | `tests/test_password_reset.py` |
