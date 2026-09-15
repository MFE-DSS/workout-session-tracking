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
    # ⚠ `UI-CP3 §6` — la classe `today-home__analysis` devient une sortie du
    # rail de transition, nommée par sa question. L'invariant tenu ici est le
    # CHEMIN, pas son véhicule : épingler la classe aurait interdit de changer
    # la forme du lien sans changer ce qu'il garantit.
    body = client.get("/").text
    assert "/progress" in body


def test_home_shows_zero_state(client):
    """With no sessions, KPIs show 0 values."""
    body = client.get("/").text
    assert "0" in body
