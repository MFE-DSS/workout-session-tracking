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


PROGRESSION = "/progress"


def test_dashboard_redirects_to_progression(client):
    """`TRAIN1-C` — LA CIBLE A CHANGÉ : `/` → `/progress`.

    Sb_27.6 renvoyait vers l'Accueil, faute de mieux à l'époque. L'audit du
    contenu du tableau de bord est clos — rien d'unique à absorber —, donc la
    seule question qui restait est celle de l'atterrissage : quelqu'un qui tape
    `/dashboard` cherche de l'analytique, et l'analytique vit sur `/progress`.
    """
    r = client.get("/dashboard", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == PROGRESSION


def test_dashboard_redirects_with_window_param(client):
    """The deprecated `window` query param is ignored — redirect still 303."""
    r = client.get("/dashboard?window=60", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == PROGRESSION


def test_dashboard_unauth_redirects_to_login(client):
    """Unauthenticated request still redirects (auth dependency runs first)."""
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()
    r = client.get("/dashboard", follow_redirects=False)
    # auth redirect lands on /login (303), not on / — auth dependency
    # runs BEFORE the dashboard handler.
    assert r.status_code == 303
    assert r.headers["location"].endswith("/login")


def test_dashboard_follow_redirect_lands_on_progression(client):
    """Following the redirect lands on the analytical surface, not the Home."""
    r = client.get("/dashboard", follow_redirects=True)
    assert r.status_code == 200
    assert "Progression" in r.text
