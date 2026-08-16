"""Sx_UI_06 / Sb_UI_06.3 — home density cleanup invariants.

Locks the home de-densification per the accepted spec
(docs/strategy/Sx_UI_06_INFO_DENSITY_DEDUP_SPEC.md), rule « one information =
one place, closest to the action ». Decisions:

- the hero CTA starts the recommended session DIRECTLY (POST /sessions,
  template_slug + creation_source=reco_top); the standalone
  « Prochaine séance suggérée » block is removed from the home (no double
  start CTA). The full reco block stays on the launcher.
- the hero readiness teaser (« détail plus bas », no data) is removed; the
  readiness state lives in its single widget below.
- last-session on the home is compact (name + date), without Ressenti/Qualité
  (analytics live in session-done / progress).
- home KPI reduced to the single decisional « séances cette sem. »; analytical
  KPI (score moyen, complétion 30j) live on /progress.

No business / route / model / migration change; SSR & no-JS preserved.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "app" / "templates" / "index.html"
COACHING = ROOT / "app" / "templates" / "_partials" / "home_coaching_loop.html"


def _home(client) -> str:
    r = client.get("/", follow_redirects=True)
    assert r.status_code == 200
    return r.text


def _seed_history(client):
    from tests.test_recommendation_service import _mk_session

    now = datetime(2026, 4, 21, 18, 0, tzinfo=UTC)
    for delta in (10, 6, 2):
        _mk_session(template_slug="push-a", started_at=now - timedelta(days=delta))


# ───────── reco block removed from home; hero starts it directly ─────────


def test_standalone_reco_block_removed_from_home(client):
    _seed_history(client)
    body = _home(client)
    assert 'class="reco-next' not in body


def test_hero_starts_reco_directly(client):
    _seed_history(client)
    body = _home(client)
    assert "today-home__cta-form" in body
    assert 'action="/sessions"' in body
    assert 'name="template_slug"' in body
    assert 'value="reco_top"' in body


def test_launcher_still_has_full_reco_block(client):
    """The reco detail is not lost — it stays on the launcher."""
    _seed_history(client)
    r = client.get("/launcher")
    assert "reco-next" in r.text


# ───────── readiness teaser removed from hero ─────────


def test_hero_readiness_teaser_removed(client):
    src = INDEX.read_text(encoding="utf-8")
    assert "today-home__readiness" not in src
    # widget remains
    assert "readiness-widget" in src


# ───────── last-session compact (no ressenti / qualité) ─────────


def test_last_session_compact_no_ressenti_quality(client):
    src = COACHING.read_text(encoding="utf-8")
    assert "Ressenti :" not in src
    assert "Qualité :" not in src


# ───────── KPI reduced on home ─────────


def test_home_kpi_reduced_to_week(client):
    body = _home(client)
    assert "séances cette sem." in body
    # analytical KPI moved to /progress
    assert "score moy." not in body
    assert "complétion 30j" not in body
    # link to full analysis kept
    assert "/progress" in body


# ───────── contracts preserved ─────────


def test_home_renders_server_side_no_js(client):
    """The home decision surface is fully server-rendered: the primary CTA is
    present in the initial HTML, no client fetch needed."""
    body = _home(client)
    assert "today-home__cta" in body
    # the index template must not reference a new inline script for the CTA
    src = INDEX.read_text(encoding="utf-8")
    assert "<script" not in src
