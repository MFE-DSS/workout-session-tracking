"""Tiny time-formatting helpers shared by the session views.

SQLite-safe: handles the "stored-as-naive" quirk by coercing both
operands to the same tz frame before subtraction.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional


def _coerce(dt: datetime, ref: datetime) -> datetime:
    if dt.tzinfo is None and ref.tzinfo is not None:
        return dt.replace(tzinfo=ref.tzinfo)
    if ref.tzinfo is None and dt.tzinfo is not None:
        return dt  # caller's `ref` will be coerced elsewhere
    return dt


def session_duration(
    start: datetime,
    end: Optional[datetime] = None,
    *,
    now: Optional[datetime] = None,
) -> timedelta:
    """Duration of a session. `end` trumps `now`; `now` is used for
    in-progress sessions."""
    now = now or datetime.now(timezone.utc)
    target = end if end is not None else now
    start_c = _coerce(start, target)
    target_c = _coerce(target, start_c)
    return target_c - start_c


def format_duration_short(delta: timedelta) -> str:
    """Compact duration for mobile display.

      < 1 h     -> "{m} min" (including 0 min for < 60 s)
      otherwise -> "{h} h {mm:02d}"

    No characters that would be HTML-escaped. Safe to substring-
    match in assertions.
    """
    total_seconds = max(int(delta.total_seconds()), 0)
    minutes = total_seconds // 60
    hours, minutes = divmod(minutes, 60)
    if hours == 0:
        return f"{minutes} min"
    return f"{hours} h {minutes:02d}"
