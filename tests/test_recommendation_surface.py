"""Surface tests for the next-session recommendation block on
home and launcher (Sb_12)."""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from tests.test_recommendation_service import _mk_session
from tests.helpers import get_test_user_id


def test_home_hero_starts_reco_when_no_open_session(client):
    """Sx_UI_06 Sb_UI_06.3 — the standalone « Prochaine séance suggérée »
    block is removed from the home; the hero CTA now starts the recommended
    session directly. The start mechanism is unchanged: a POST /sessions with
    a template_slug hidden input and creation_source=reco_top. Seed history so
    the user leaves cold-start and a reco exists."""
    now = datetime(2026, 4, 21, 18, 0, tzinfo=timezone.utc)
    for delta in (10, 6, 2):
        _mk_session(template_slug="push-a", started_at=now - timedelta(days=delta))
    r = client.get("/")
    assert r.status_code == 200
    body = r.text
    # standalone reco block is gone from the home
    assert 'class="reco-next' not in body
    # the hero carries the direct-start form (same contract as before)
    assert 'today-home__cta-form' in body
    assert 'action="/sessions"' in body
    assert 'name="template_slug"' in body
    assert 'value="reco_top"' in body


def test_home_hides_reco_block_when_session_open(client):
    """If a session is in progress, the reco block must not appear on /."""
    r = client.post("/sessions", data={"template_slug": "push-a"}, follow_redirects=False)
    assert r.status_code in {302, 303}
    home = client.get("/")
    assert home.status_code == 200
    assert 'class="reco-next' not in home.text


def test_launcher_step1_shows_reco_block(client):
    """The launcher step-1 page (no ?type=) renders the same partial."""
    r = client.get("/launcher")
    assert r.status_code == 200
    assert 'class="reco-next' in r.text
    assert 'Prochaine séance suggérée' in r.text


def test_launcher_deep_step_does_not_show_reco(client):
    """Once the user picked a type, the picker dominates and the reco
    block is not rendered again."""
    r = client.get("/launcher?type=standard")
    assert r.status_code == 200
    assert 'class="reco-next' not in r.text


def test_reco_phrase_appears_on_launcher(client):
    """Sx_UI_06 Sb_UI_06.3 — the reco explanation phrase moved off the home
    (the home hero is a single decision now). It still surfaces verbatim on
    the launcher step-1, which keeps the full reco block."""
    now = datetime(2026, 4, 21, 18, 0, tzinfo=timezone.utc)
    for delta in (10, 6, 2):
        _mk_session(template_slug="push-a", started_at=now - timedelta(days=delta))

    r = client.get("/launcher")
    body = r.text
    assert 'reco-next__phrase' in body
    # Phrase is non-empty (check the text between opening and closing tag).
    m = re.search(
        r'<p class="reco-next__phrase">([^<]+)</p>',
        body,
    )
    assert m, "expected a visible phrase inside the reco block"
    phrase = m.group(1).strip()
    assert phrase and len(phrase) <= 140


def test_reco_alternatives_collapsed_when_present(client):
    """When alternatives exist they sit inside a <details> that is
    collapsed by default (no `open` attribute)."""
    now = datetime(2026, 4, 21, 18, 0, tzinfo=timezone.utc)
    for delta in (9, 5, 1):
        _mk_session(template_slug="pull-a", started_at=now - timedelta(days=delta))

    r = client.get("/")
    body = r.text
    if 'reco-next__alternatives' in body:
        # Should not be pre-opened.
        assert '<details class="reco-next__alternatives" open>' not in body
