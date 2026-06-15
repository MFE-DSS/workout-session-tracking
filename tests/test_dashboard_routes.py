"""Tests for the /dashboard route.

Sb_27.6 — OQ-3 tranchée verbatim user : /dashboard est **déprécié**.
La route retourne désormais un redirect 303 vers / (Home coaching). Le
template `dashboard.html` et le service `compute_dashboard` restent
volontairement préservés (pas de suppression brutale de code métier).

Les tests historiques qui rendaient le template directement sont
remplacés par leur équivalent "deprecated redirect" — l'intention V1
("/dashboard renders") n'est plus contractuelle ; l'intention V2 ("/dashboard
deprecates to /") l'est.
"""
from __future__ import annotations


def test_dashboard_redirects_to_home(client):
    """GET /dashboard returns 303 redirect to / for an authenticated user."""
    r = client.get("/dashboard", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/"


def test_dashboard_redirects_with_window_param(client):
    """The deprecated `window` query param is ignored — redirect still 303 /."""
    r = client.get("/dashboard?window=60", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/"


def test_dashboard_unauth_redirects_to_login(client):
    """Unauthenticated request still redirects (auth dependency runs first)."""
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()
    r = client.get("/dashboard", follow_redirects=False)
    # auth redirect lands on /login (303), not on / — auth dependency
    # runs BEFORE the dashboard handler.
    assert r.status_code == 303
    assert r.headers["location"].endswith("/login")


def test_dashboard_follow_redirect_lands_on_home(client):
    """Following the redirect lands on the new Home coaching surface."""
    r = client.get("/dashboard", follow_redirects=True)
    assert r.status_code == 200
    # Home renders the coaching loop section
    assert "coaching-loop" in r.text or "Aujourd'hui" in r.text
