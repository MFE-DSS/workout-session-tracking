"""Tests for Board KPI display on home page."""
from __future__ import annotations


def test_home_links_to_the_analysis_surface(client):
    """Tier **T4** — `Sx_UIV3_01 §7`, BLOCKER-1 tranché : **OUI**.

    L'accueil ne porte plus de section KPI : l'analytique quitte la surface de
    DÉCISION pour la surface d'ANALYSE (D8). Rien n'est supprimé du produit —
    `/progress` et `/dashboard` montrent toujours tout.

    Ce que cette garde protège désormais : le chemin vers l'analyse reste **à
    un tap depuis l'accueil**. C'est l'invariant qui comptait ; « la section
    KPI existe » n'en était qu'une implémentation.
    """
    body = client.get("/").text
    assert "today-home__analysis" in body
    assert "/progress" in body


def test_home_shows_zero_state(client):
    """With no sessions, KPIs show 0 values."""
    body = client.get("/").text
    assert "0" in body
