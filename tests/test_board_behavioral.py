"""Tests for behavioral data on Board home page."""
from __future__ import annotations


def test_home_shows_readiness(client):
    body = client.get("/").text
    assert "disponibilit" in body.lower()


def test_home_shows_recommendation(client):
    body = client.get("/").text
    assert "ance" in body.lower()  # "séance" from fallback text
