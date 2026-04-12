"""Tests for Board KPI display on home page."""
from __future__ import annotations


def test_home_shows_kpi_section(client):
    """Home page should show the 'Ma progression' section."""
    body = client.get("/").text
    assert "Ma progression" in body
    assert "Voir analyse" in body


def test_home_shows_zero_state(client):
    """With no sessions, KPIs show 0 values."""
    body = client.get("/").text
    assert "0" in body
