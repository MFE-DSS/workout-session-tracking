"""Smoke tests for the reference seed + SSR pages."""
from __future__ import annotations


def test_index_renders_seven_days(client):
    r = client.get("/")
    assert r.status_code == 200
    body = r.text
    for day in ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]:
        assert day in body


def test_monday_day_has_all_eight_exercises(client):
    r = client.get("/jours/1")
    assert r.status_code == 200
    body = r.text
    assert "Pectoral, Delts, Triceps" in body
    for code in ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8"]:
        assert code in body


def test_rest_day_is_flagged(client):
    r = client.get("/jours/3")
    assert r.status_code == 200
    body = r.text
    assert "Repos" in body
    assert "LISS" in body


def test_unknown_weekday_returns_404(client):
    r = client.get("/jours/9")
    assert r.status_code == 404
