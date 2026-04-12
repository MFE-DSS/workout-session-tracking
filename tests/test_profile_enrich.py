"""Tests for enriched profile page."""
from __future__ import annotations


def test_profile_shows_30d_section(client):
    body = client.get("/profile").text
    assert "30 derniers jours" in body


def test_profile_shows_body_form(client):
    body = client.get("/profile").text
    assert "Profil physique" in body
    assert "Taille" in body


def test_profile_body_submit(client):
    r = client.post("/profile/body", data={
        "height_cm": "180",
        "weight_kg": "75.5",
        "resting_hr": "60",
        "waist_cm": "",
        "bp_systolic": "120",
        "bp_diastolic": "80",
    }, follow_redirects=False)
    assert r.status_code == 303

    # Verify data persisted
    body = client.get("/profile").text
    assert "180" in body
    assert "75.5" in body


def test_profile_body_validation_rejects_invalid(client):
    r = client.post("/profile/body", data={
        "height_cm": "999",
        "weight_kg": "75",
        "resting_hr": "",
        "waist_cm": "",
        "bp_systolic": "",
        "bp_diastolic": "",
    }, follow_redirects=False)
    assert r.status_code in (303, 400)
