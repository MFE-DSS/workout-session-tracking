"""Tests for behavioral data on Profile page."""
from __future__ import annotations


def test_profile_shows_fatigue(client):
    body = client.get("/profile").text
    assert "fatigue" in body.lower()


def test_profile_shows_consistency(client):
    body = client.get("/profile").text
    assert "gularit" in body.lower()  # "régularité"


def test_profile_shows_streak(client):
    body = client.get("/profile").text
    assert "rie" in body.lower()  # "série"
