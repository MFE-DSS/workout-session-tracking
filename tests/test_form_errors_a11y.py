"""Sb_UI_09.2 — Form-Errors ARIA (2nd build of Sx_UI_09).

Form-error containers (`.integrity-errors`, rendering `{{ error }}`) gain
`role="alert"` so screen readers announce the error (SSR / no-JS — announced on
reload; role="alert" implies aria-live="assertive"). On login/register the form
references the error message via `aria-describedby` (an `id` on the container).
No `aria-invalid` is added: the error is a GLOBAL message and the backend does
not identify which field is at fault, so marking fields would be false.

Template-only — no route/service/model/JS/POST-contract/colour change.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TPL = ROOT / "app" / "templates"

ERROR_TEMPLATES = [
    "login.html", "register.html", "reset_password.html",
    "forgot_password.html", "contact.html", "password_change.html",
    "export.html",
]


def _src(name: str) -> str:
    return (TPL / name).read_text(encoding="utf-8")


# ───────── role="alert" on every error container ─────────


def test_every_integrity_errors_container_has_role_alert():
    for name in ERROR_TEMPLATES:
        src = _src(name)
        # every `<div class="integrity-errors"...>` opening carries role="alert"
        containers = re.findall(r'<div class="integrity-errors"[^>]*>', src)
        assert containers, f"{name}: no integrity-errors container found"
        for c in containers:
            assert 'role="alert"' in c, f"{name}: container without role=alert: {c}"


def test_no_integrity_errors_container_without_role():
    """Guard: no error container anywhere is missing role=alert."""
    for name in ERROR_TEMPLATES:
        src = _src(name)
        # a container div followed by no role on the same tag
        for tag in re.findall(r'<div class="integrity-errors"[^>]*>', src):
            assert 'role="alert"' in tag, f"{name}: {tag}"


# ───────── login / register: id + aria-describedby ─────────


def test_login_error_has_id_and_form_describedby():
    src = _src("login.html")
    assert re.search(r'class="integrity-errors"[^>]*id="login-error"', src) or \
           re.search(r'id="login-error"[^>]*class="integrity-errors"', src) or \
           'id="login-error"' in src
    # the form references it when an error is present
    assert 'aria-describedby="login-error"' in src


def test_register_error_has_id_and_form_describedby():
    src = _src("register.html")
    assert 'id="register-error"' in src
    assert 'aria-describedby="register-error"' in src


def test_describedby_is_conditional_on_error():
    """aria-describedby only appears when {% if error %} (no dangling ref)."""
    for name, eid in [("login.html", "login-error"), ("register.html", "register-error")]:
        src = _src(name)
        # the aria-describedby is guarded by an {% if error %} on the <form> line
        m = re.search(r"<form[^>]*aria-describedby=\"" + eid + r"\"", src)
        assert m, f"{name}: form missing conditional aria-describedby"
        assert "{% if error %}" in src


# ───────── no aria-invalid (honest: field-level state unknown) ─────────


def test_no_aria_invalid_added():
    """The backend returns a global message, not per-field validity — so no
    field is marked aria-invalid (would be false). Check the ATTRIBUTE, not the
    word (which legitimately appears in an explanatory Jinja comment)."""
    for name in ("login.html", "register.html"):
        src = _src(name)
        assert 'aria-invalid="' not in src, f"{name}: aria-invalid attribute must not be added"


# ───────── non-regression: no-JS, POST contract, fields ─────────


def test_no_js_added():
    for name in ("login.html", "register.html"):
        src = _src(name)
        assert "<script" not in src.lower()
        assert "addEventListener" not in src


def test_login_form_contract_unchanged():
    src = _src("login.html")
    assert 'method="post"' in src
    assert 'name="username"' in src
    assert 'name="password"' in src
    assert 'autocomplete="current-password"' in src


def test_register_form_contract_unchanged():
    src = _src("register.html")
    assert 'method="post"' in src
    for field in ('name="username"', 'name="email"', 'name="password"',
                  'name="password_confirm"'):
        assert field in src, f"register field missing: {field}"


def test_no_new_hex_colour_in_error_markup():
    """The a11y pass adds ARIA attributes only — no styling/colour change."""
    # the error container styling is unchanged (still .integrity-errors class)
    for name in ("login.html", "register.html"):
        src = _src(name)
        assert 'class="integrity-errors"' in src


# ───────── source-level guarantee ─────────


def test_error_templates_ship_role_alert():
    """Every error-rendering template ships role="alert" so any rendered error
    is announced (the container renders only under {% if error %}; the failed-
    POST path is covered by existing auth tests)."""
    for name in ERROR_TEMPLATES:
        assert 'role="alert"' in _src(name), f"{name}: missing role=alert"
