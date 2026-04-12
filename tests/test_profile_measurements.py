"""Tests for measurement integration on profile page."""
from __future__ import annotations


def test_profile_shows_measurement_form(client):
    body = client.get("/profile").text
    assert "measured_at" in body
    assert "Nouvelle mesure" in body.lower() or "mesure" in body.lower()


def test_profile_measurement_submit(client):
    r = client.post("/profile/measurements", data={
        "measured_at": "2026-04-12",
        "weight_kg": "75.5",
        "chest_cm": "100",
        "arm_cm": "36",
        "waist_cm": "",
        "thigh_cm": "",
        "calf_cm": "",
    }, follow_redirects=False)
    assert r.status_code == 303


def test_profile_measurement_empty_date_uses_fallback(client):
    r = client.post("/profile/measurements", data={
        "measured_at": "",
        "weight_kg": "75",
        "chest_cm": "",
        "arm_cm": "",
        "waist_cm": "",
        "thigh_cm": "",
        "calf_cm": "",
    }, follow_redirects=False)
    assert r.status_code == 303
