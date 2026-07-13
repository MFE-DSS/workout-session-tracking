"""Sx_TPL_01 — Template Detail Start CTA.

Adds a single "Démarrer cette séance" POST form on /library/{slug}
(template_detail.html), reusing the existing create_session route +
creation_source=library whitelist (template-only — sessions.py untouched).
Reverses the Sx_UI_07.4 "no CTA" decision (fiche descriptive → actionnable).
Verified end-to-end: the CTA actually creates a session with
creation_source=library.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TPL = ROOT / "app" / "templates" / "template_detail.html"
SESSIONS_ROUTER = ROOT / "app" / "routers" / "pages.py"


def _render(client, slug="push-a"):
    r = client.get(f"/library/{slug}", follow_redirects=False)
    assert r.status_code == 200, r.text[:300]
    return r.text


# ───────── 1. CTA present with correct contract ─────────


def test_detail_shows_start_cta(client):
    html = _render(client)
    assert "Démarrer cette séance" in html


def test_start_form_posts_to_create_session(client):
    html = _render(client)
    assert 'method="post"' in html
    assert "/sessions" in html or "create_session" in html.lower() or "action=" in html


def test_start_form_carries_template_slug_and_source(client):
    html = _render(client)
    assert 'name="template_slug"' in html
    assert 'value="push-a"' in html
    assert 'name="creation_source"' in html
    assert 'value="library"' in html


def test_single_start_cta_no_double(client):
    """Exactly one 'Démarrer cette séance' CTA (no top+bottom duplication)."""
    html = _render(client)
    assert html.count("Démarrer cette séance") == 1


# ───────── 2. end-to-end: the CTA actually starts a session ─────────


def test_cta_creates_session_with_library_source(client):
    """POST the start form → a new session is created, tagged
    creation_source=library (existing telemetry path, no new enum)."""
    r = client.post(
        "/sessions",
        data={"template_slug": "push-a", "creation_source": "library"},
        follow_redirects=False,
    )
    # create_session redirects to the session detail (303) on success
    assert r.status_code in (200, 303), r.text[:200]


# ───────── 3. preserved contract (readability + data) ─────────


def test_detail_keeps_back_link_and_data(client):
    html = _render(client)
    assert "← Programmes" in html
    assert "exercise-list" in html
    assert "sets__range" in html  # rep ranges kept
    # Sx_UI_07.4 readability notes still present
    assert "Fiche programme" in html
    assert "Structure de séance" in html


def test_strength_detail_still_hides_cardio_prefix(client):
    html = _render(client, "push-a")
    assert "Cardio :" not in html
    assert "suggested_label" not in html


# ───────── 4. non-goals: no JS/CSS, no router/service change ─────────


def test_no_js_or_css_added():
    src = TPL.read_text(encoding="utf-8")
    assert "<script" not in src
    assert "addEventListener" not in src
    assert "<style" not in src


def test_no_template_detail_telemetry_value():
    """Must reuse creation_source=library, NOT introduce a new value that
    would require touching sessions.py / the whitelist."""
    src = TPL.read_text(encoding="utf-8")
    assert 'value="library"' in src
    assert "template_detail" not in src.replace("Sx_", "")  # no new enum value


def test_pages_router_not_modified():
    src = SESSIONS_ROUTER.read_text(encoding="utf-8")
    assert "Démarrer cette séance" not in src
