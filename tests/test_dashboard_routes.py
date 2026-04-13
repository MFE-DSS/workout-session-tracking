"""Tests for the /dashboard route."""
from __future__ import annotations


def test_dashboard_renders(client):
    """GET /dashboard returns 200 with page title."""
    r = client.get("/dashboard")
    assert r.status_code == 200
    assert "Body Engineering" in r.text


def test_dashboard_window_param(client):
    """GET /dashboard?window=60 returns 200."""
    r = client.get("/dashboard?window=60")
    assert r.status_code == 200
    assert "is-active" in r.text


def test_dashboard_requires_auth(client):
    """Unauthenticated request redirects (303)."""
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()
    r = client.get("/dashboard", follow_redirects=False)
    assert r.status_code == 303


def test_dashboard_shows_axis_cards(client):
    """All 5 axis labels are present in the response."""
    r = client.get("/dashboard")
    assert r.status_code == 200
    for label in ("Régularité", "Progression", "Évolution corporelle", "Récupération", "Équilibre musculaire"):
        assert label in r.text


def test_dashboard_nav_link_present(client):
    """Dashboard link appears in the navbar."""
    r = client.get("/dashboard")
    assert r.status_code == 200
    assert "Dashboard" in r.text
