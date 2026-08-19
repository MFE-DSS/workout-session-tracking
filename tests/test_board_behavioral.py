"""Tests for behavioral data on Board home page."""
from __future__ import annotations


def test_readiness_left_the_home_for_the_analysis_surface(client):
    """Tier **T4** — `Sx_UIV3_01 §7`, BLOCKER-1 tranché : **OUI**.

    Le KPI « disponibilité » quitte l'accueil. Trois échelles d'état
    concurrentes y vivaient — déclarée 1–5, inférée en 4 bandes, calculée
    0–100 — dont aucune ne s'accordait avec les autres, et celle-ci exprimait
    en pourcentage ce que `zone_recovery` refuse d'exprimer ainsi.

    **Déplacé, pas supprimé** : le moteur le calcule toujours. C'est vérifié
    au niveau du service et non sur le HTML d'une page, dont le rendu dépend
    de l'historique — une assertion sur le markup serait verte ou rouge selon
    les données.
    """
    assert "disponibilit" not in client.get("/").text.lower()

    from app.database import SessionLocal
    from app.models.user import User
    from app.services.behavioral import compute_behavioral_state

    with SessionLocal() as db:
        user = db.query(User).first()
        assert compute_behavioral_state(db, user.id).readiness_score is not None


def test_home_shows_recommendation(client):
    body = client.get("/").text
    assert "ance" in body.lower()  # "séance" from fallback text
