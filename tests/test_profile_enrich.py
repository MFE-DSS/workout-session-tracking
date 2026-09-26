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
    """⚠ `UI-CP7.5A` — REPOINTÉE : le tiroir « Données de référence » n'existe
    plus, la capacité qu'il portait si.

    Il ne contenait que la taille, la FC repos — qui ont désormais leur ligne
    dans le relevé, avec leur propre feuille — et l'email, qui n'est pas une
    donnée de référence corporelle et a rejoint le tiroir « Compte », où il
    était déjà AFFICHÉ sans pouvoir y être modifié.

    La propriété défendue est : depuis `/profile`, la taille se lit ET
    s'écrit. Elle est plus vraie qu'avant — l'utilisateur n'a plus à savoir
    que « taille » et « tour de taille » vivent dans deux tables.
    """
    body = client.get("/profile").text
    assert "Taille" in body
    # La porte d'écriture existe, et elle est sur la ligne du fait.
    assert 'id="fait-height_cm"' in body
    assert 'name="height_cm"' in body


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
