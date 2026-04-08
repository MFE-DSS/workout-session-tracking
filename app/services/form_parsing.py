"""Tiny, typed helpers for parsing FastAPI form payloads.

Centralises the "empty string -> None" / "invalid -> None" semantics
that the session detail forms need so the route handlers stay short.

V1 policy for invalid values: drop them (set to None). The UI is
SSR and renders only the whitelisted radio buttons, so invalid
values only come from direct POSTs, which we don't need to reject
with a 400 in a single-user app.
"""
from __future__ import annotations

from starlette.datastructures import FormData


def clean_str(value: object, max_length: int | None = None) -> str | None:
    """Trim + strip empty + optionally truncate."""
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    if max_length is not None and len(s) > max_length:
        s = s[:max_length]
    return s


def to_float(value: object) -> float | None:
    if value is None or str(value).strip() == "":
        return None
    try:
        return float(str(value).replace(",", "."))
    except ValueError:
        return None


def to_int(value: object) -> int | None:
    if value is None or str(value).strip() == "":
        return None
    try:
        return int(float(str(value)))
    except ValueError:
        return None


def enum_str(value: object, allowed: set[str]) -> str | None:
    s = clean_str(value)
    if s is None:
        return None
    return s if s in allowed else None


def enum_int(value: object, allowed: set[int]) -> int | None:
    i = to_int(value)
    if i is None:
        return None
    return i if i in allowed else None


def checkbox(value: object) -> bool:
    """HTML checkboxes are present-only when checked."""
    if value is None:
        return False
    s = str(value).strip().lower()
    return s not in ("", "false", "0", "off", "no")


def form_value(form: FormData, key: str) -> object:
    """Shortcut that handles the Starlette FormData slightly opaque API."""
    return form.get(key)
