"""Tests for the timezone rendering helper (Sb_06 etape 2).

Storage stays UTC. Rendering uses the `local` Jinja filter which
converts to DEFAULT_TIMEZONE (Europe/Paris).
"""
from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from app.templating import local_weekday_iso, to_local

PARIS = ZoneInfo("Europe/Paris")


def test_to_local_handles_none():
    assert to_local(None) is None


def test_to_local_utc_aware_winter():
    """UTC 18:00 on 2026-01-15 → Paris 19:00 (winter, UTC+1)."""
    dt = datetime(2026, 1, 15, 18, 0, tzinfo=UTC)
    local = to_local(dt)
    assert local.hour == 19
    assert local.minute == 0
    assert local.tzinfo == PARIS


def test_to_local_utc_aware_summer():
    """UTC 18:00 on 2026-07-15 → Paris 20:00 (summer, UTC+2)."""
    dt = datetime(2026, 7, 15, 18, 0, tzinfo=UTC)
    local = to_local(dt)
    assert local.hour == 20


def test_to_local_naive_assumes_utc():
    """SQLite roundtrip can lose tzinfo — helper must assume UTC."""
    dt = datetime(2026, 1, 15, 18, 0)  # naive
    local = to_local(dt)
    assert local.hour == 19  # Winter → +1
    assert local.tzinfo == PARIS


def test_to_local_crosses_midnight_winter():
    """UTC 23:30 Sunday → Paris 00:30 Monday (winter)."""
    dt = datetime(2026, 1, 18, 23, 30, tzinfo=UTC)  # Sunday 23:30 UTC
    local = to_local(dt)
    assert local.isoweekday() == 1  # Monday locally
    assert local.hour == 0
    assert local.minute == 30


def test_to_local_near_midnight_evening():
    """UTC 22:30 → Paris 23:30 (winter), same day."""
    dt = datetime(2026, 1, 15, 22, 30, tzinfo=UTC)
    local = to_local(dt)
    assert local.hour == 23
    assert local.day == 15


def test_local_weekday_iso_returns_local_weekday():
    """Sunday 23:30 UTC becomes Monday locally."""
    dt = datetime(2026, 1, 18, 23, 30, tzinfo=UTC)  # Sunday UTC
    assert local_weekday_iso(dt) == 1  # Monday


def test_local_weekday_iso_none():
    assert local_weekday_iso(None) is None


def test_local_weekday_iso_morning_utc():
    """UTC 07:00 Tuesday stays Tuesday locally (winter/summer)."""
    dt = datetime(2026, 1, 13, 7, 0, tzinfo=UTC)  # Tuesday
    assert local_weekday_iso(dt) == 2
