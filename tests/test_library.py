"""SSR smoke tests for the home + template library.

Sprint 0.5 explicitly removed the weekday-pivoted home, so these
tests also guard against its accidental reintroduction.
"""
from __future__ import annotations


def test_home_renders_action_tiles(client):
    r = client.get("/")
    assert r.status_code == 200
    body = r.text
    for label in ["Nouvelle séance", "Historique", "Progression", "Bibliothèque"]:
        assert label in body


def test_home_has_no_weekday_pivot(client):
    r = client.get("/")
    body = r.text
    # The home must not present a weekly grid; weekdays are derived
    # from session.started_at, never from the catalog.
    for weekday in ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]:
        assert weekday not in body


def test_library_lists_all_six_templates(client):
    r = client.get("/library")
    assert r.status_code == 200
    body = r.text
    for name in ["Push A", "Pull A", "Push B", "Pull B", "Legs", "LISS cardio"]:
        assert name in body


def test_push_a_detail_has_all_eight_exercises(client):
    r = client.get("/library/push-a")
    assert r.status_code == 200
    body = r.text
    assert "Pectoral, Delts, Triceps" in body
    for code in ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8"]:
        assert code in body


def test_pull_a_preserves_source_quirk(client):
    # Pull A has 5 exercises and uses source code "E6" after E4
    # because the original document skipped E5.
    r = client.get("/library/pull-a")
    assert r.status_code == 200
    body = r.text
    assert "Écarté arrière" in body


def test_liss_template_is_cardio(client):
    r = client.get("/library/liss-abs")
    assert r.status_code == 200
    body = r.text
    assert "LISS" in body
    assert "120-130" in body
    assert "Aucun exercice" in body  # empty exercise list


def test_unknown_template_returns_404(client):
    r = client.get("/library/this-slug-does-not-exist")
    assert r.status_code == 404


def test_history_stub_is_empty(client):
    r = client.get("/history")
    assert r.status_code == 200
    assert "Aucune séance" in r.text


def test_progress_stub_renders(client):
    r = client.get("/progress")
    assert r.status_code == 200
    assert "Progression" in r.text
