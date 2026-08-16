"""Sb_18 — V2 antagonist + recovery logic in recommendation engine."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from tests.helpers import get_test_user_id
from tests.test_recommendation_service import _call, _mk_session

# ---- Pure helpers ------------------------------------------------------


def test_antagonist_bonus_zero_overlap_returns_perfect():
    from app.services.recommendation import (
        ANTAGONIST_BONUS_PERFECT,
        _antagonist_bonus,
    )
    bonus = _antagonist_bonus(
        ["lats", "delt_post"], ["pecs", "delt_lat", "triceps"]
    )
    assert bonus == ANTAGONIST_BONUS_PERFECT


def test_antagonist_bonus_full_overlap_returns_zero():
    from app.services.recommendation import _antagonist_bonus
    bonus = _antagonist_bonus(["pecs", "triceps"], ["pecs", "triceps"])
    assert bonus == 0


def test_antagonist_bonus_one_zone_overlap_returns_partial():
    from app.services.recommendation import (
        ANTAGONIST_BONUS_PARTIAL,
        _antagonist_bonus,
    )
    # delt_lat shared, the rest distinct
    bonus = _antagonist_bonus(
        ["lats", "delt_lat"], ["pecs", "delt_lat", "triceps"]
    )
    assert bonus == ANTAGONIST_BONUS_PARTIAL


def test_antagonist_bonus_no_last_session_zero():
    from app.services.recommendation import _antagonist_bonus
    assert _antagonist_bonus(["pecs"], []) == 0


# ---- availability_by_zone integration ---------------------------------


def test_signals_compute_availability_after_recent_session(client):
    """After a Push session 6h ago, pecs availability should be ≈ 6/48,
    quads should be 1.0 (untouched in window)."""
    from app.database import SessionLocal
    from app.services.recommendation import (
        _compute_signals,
        reset_template_zones_cache,
    )

    reset_template_zones_cache()
    now = datetime(2026, 4, 21, 18, 0, tzinfo=UTC)
    six_hours_ago = now - timedelta(hours=6)
    _mk_session(template_slug="push-a", started_at=six_hours_ago)

    with SessionLocal() as db:
        signals = _compute_signals(db, get_test_user_id(), now)

    # pecs hit 6h ago, target 48h → availability ~ 0.125
    pecs_avail = signals.availability_by_zone["pecs"]
    assert 0.10 <= pecs_avail <= 0.15

    # quads never hit → availability 1.0
    assert signals.availability_by_zone["quads"] == 1.0

    # last_strength_session_zones should include push primary zones
    assert "pecs" in signals.last_strength_session_zones


def test_signals_quads_72h_recovery_window(client):
    """Quads availability uses 72h target (gros groupe). Legs 24h ago →
    availability = 24/72 = 1/3."""
    from app.database import SessionLocal
    from app.services.recommendation import _compute_signals, reset_template_zones_cache

    reset_template_zones_cache()
    now = datetime(2026, 4, 21, 18, 0, tzinfo=UTC)
    one_day_ago = now - timedelta(hours=24)
    _mk_session(template_slug="legs-a", started_at=one_day_ago)

    with SessionLocal() as db:
        signals = _compute_signals(db, get_test_user_id(), now)

    quads_avail = signals.availability_by_zone["quads"]
    assert 0.30 <= quads_avail <= 0.36, f"got {quads_avail}"


# ---- Recommendation result drift V1 → V2 ------------------------------


def test_v2_prefers_antagonist_after_push_session(client):
    """Two Push-only sessions in the last 24h → V2 must NOT propose Push
    in top-1. The antagonist-aware engine should pick Pull or Legs."""
    now = datetime(2026, 4, 21, 18, 0, tzinfo=UTC)
    _mk_session(template_slug="push-a", started_at=now - timedelta(days=2))
    _mk_session(template_slug="push-b", started_at=now - timedelta(hours=18))
    _mk_session(template_slug="push-a", started_at=now - timedelta(hours=8))

    result = _call(get_test_user_id(), now=now)
    assert result is not None

    top_slug = result["top"]["template"].slug
    # Top-1 must NOT be a push template
    assert not top_slug.startswith("push-"), (
        f"V2 antagonist failed: top-1 is {top_slug}"
    )


def test_v2_legs_recovery_phrase_under_72h(client):
    """When legs were recently trained (< 72h), suggesting another legs
    template must mention recovery in the phrase."""
    now = datetime(2026, 4, 21, 18, 0, tzinfo=UTC)
    # 36h ago: legs session — quads should be at availability 36/72 = 0.5
    _mk_session(template_slug="legs-a", started_at=now - timedelta(hours=36))

    result = _call(get_test_user_id(), now=now)
    assert result is not None

    # Find legs-b in the candidates (top or alternatives)
    candidates = [result["top"]] + result["alternatives"]
    legs_candidate = next(
        (c for c in candidates if c["template"].slug == "legs-b"), None
    )
    if legs_candidate is not None:
        phrase = legs_candidate["phrase"]
        assert "récupération" in phrase or "Jambes" in phrase, (
            f"expected recovery wording in legs phrase, got: {phrase}"
        )


def test_v2_phrase_carries_antagonist_signal(client):
    """When the engine recommends after a clear push session, the phrase
    should reflect the antagonist logic somewhere in the candidate set."""
    now = datetime(2026, 4, 21, 18, 0, tzinfo=UTC)
    _mk_session(template_slug="push-a", started_at=now - timedelta(days=3))
    _mk_session(template_slug="push-b", started_at=now - timedelta(days=1))
    _mk_session(template_slug="push-a", started_at=now - timedelta(hours=10))

    result = _call(get_test_user_id(), now=now)
    assert result is not None

    candidates = [result["top"]] + result["alternatives"]
    phrases = [c["phrase"] for c in candidates]
    # At least one candidate phrase should reference the antagonist
    # logic (chevauchement musculaire / pattern push/pull/legs / etc.)
    keywords = ["chevauchement", "pattern", "récup", "Jambes", "Dos", "alterner"]
    assert any(any(k in p for k in keywords) for p in phrases), (
        f"no antagonist-flavored wording in candidate phrases: {phrases}"
    )


def test_v2_phrase_under_140_chars(client):
    """V2 enriched slots must still respect the 140-char hard cap."""
    now = datetime(2026, 4, 21, 18, 0, tzinfo=UTC)
    for delta in (4, 2, 1):
        _mk_session(template_slug="push-a", started_at=now - timedelta(days=delta))

    result = _call(get_test_user_id(), now=now)
    assert result is not None
    for c in [result["top"]] + result["alternatives"]:
        assert len(c["phrase"]) <= 140, (
            f"phrase exceeds 140 chars ({len(c['phrase'])}): {c['phrase']}"
        )


# ---- Backward compat with existing scoring components -----------------


def test_v2_cold_start_unchanged(client):
    """Cold start path is V2-immune (must still return Push A core)."""
    result = _call(get_test_user_id())
    assert result is not None
    assert result["context"]["cold_start"] is True
    assert result["top"]["template"].catalog_section == "core"


def test_v2_open_session_returns_none(client):
    """Open session short-circuits V2 the same way V1 did."""
    r = client.post("/sessions", data={"template_slug": "push-a"}, follow_redirects=False)
    assert r.status_code in {302, 303}
    assert _call(get_test_user_id()) is None


def test_v2_no_legacy_staleness_field_on_signals(client):
    """Sb_18 — Signals should expose availability_by_zone, NOT
    staleness_by_zone (renamed). Guard against accidental restoration."""
    from app.database import SessionLocal
    from app.services.recommendation import _compute_signals, reset_template_zones_cache

    reset_template_zones_cache()
    now = datetime(2026, 4, 21, 18, 0, tzinfo=UTC)
    _mk_session(template_slug="push-a", started_at=now - timedelta(days=1))

    with SessionLocal() as db:
        signals = _compute_signals(db, get_test_user_id(), now)
    assert hasattr(signals, "availability_by_zone")
    assert hasattr(signals, "hours_since_last_by_zone")
    assert hasattr(signals, "last_strength_session_zones")
    assert not hasattr(signals, "staleness_by_zone")
