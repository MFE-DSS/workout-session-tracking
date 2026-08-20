"""Tests for enriched profile page."""
from __future__ import annotations


def test_the_30d_reading_left_the_profile(client):
    """**Migré par `UX4_01`.**

    La garde exigeait « 30 derniers jours » sur le Profil. Ce bloc répondait à
    « comment est-ce que je progresse ? », question que la décision opérateur
    du 2026-08-20 réserve à `PROGRESSION` — laquelle rend déjà « sessions
    cette semaine » et « sessions terminées (30 j) ».

    La capacité n'est pas perdue, elle est à sa place. La garde est retournée :
    elle vérifie désormais que la lecture de progression a bien quitté le
    Profil.
    """
    body = client.get("/profile").text
    assert "30 derniers jours" not in body


def test_the_30d_reading_exists_on_progression(client):
    """L'invariant qui survit au déplacement : la lecture existe toujours,
    ailleurs. Sans cette garde, le retrait ci-dessus passerait aussi si la
    capacité avait simplement disparu."""
    body = client.get("/progress").text
    assert "30 j" in body or "30 derniers jours" in body


def test_profile_shows_body_form(client):
    body = client.get("/profile").text
    assert "Données de référence" in body or "référence" in body
    assert "Taille" in body


def test_profile_body_submit(client):
    r = client.post("/profile/body", data={
        "height_cm": "180",
        "resting_hr": "60",
        "bp_systolic": "120",
        "bp_diastolic": "80",
    }, follow_redirects=False)
    assert r.status_code == 303

    # Verify data persisted
    body = client.get("/profile").text
    assert "180" in body


def test_profile_body_validation_rejects_invalid(client):
    r = client.post("/profile/body", data={
        "height_cm": "999",
        "resting_hr": "",
        "bp_systolic": "",
        "bp_diastolic": "",
    }, follow_redirects=False)
    assert r.status_code in (303, 400)
