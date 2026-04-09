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


def relative_hours_ago(now: datetime, then: datetime) -> str:
    """Compact 'how long ago' label down to the minute.

    Used by /export and /healthz/strict to surface backup file age
    in plain French. Sub-minute deltas show as "à l'instant", to
    avoid noisy sub-second strings on freshly-written files.
    """
    if then.tzinfo is None and now.tzinfo is not None:
        then = then.replace(tzinfo=now.tzinfo)
    elif now.tzinfo is None and then.tzinfo is not None:
        now = now.replace(tzinfo=then.tzinfo)

    delta_sec = max((now - then).total_seconds(), 0.0)
    if delta_sec < 60:
        return "à l'instant"
    if delta_sec < 3600:
        return f"il y a {int(delta_sec // 60)} min"
    if delta_sec < 86400:
        return f"il y a {int(delta_sec // 3600)} h"
    days = int(delta_sec // 86400)
    if days == 1:
        return "hier"
    if days < 30:
        return f"il y a {days} j"
    return f"il y a {days // 30} mois"
