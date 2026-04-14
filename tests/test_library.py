"""SSR smoke tests for the home + template library.

Sprint 0.5 explicitly removed the weekday-pivoted home, so these
tests also guard against its accidental reintroduction.
"""
from __future__ import annotations


def test_home_renders_action_tiles(client):
    r = client.get("/")
    assert r.status_code == 200
    body = r.text
    # Main CTA: "Démarrer une séance" (primary) or "Nouvelle séance" (when open session)
    assert "Démarrer une séance" in body or "Nouvelle séance" in body
    for label in ["Historique", "Progression", "Programmes"]:
        assert label in body


def test_home_has_no_weekday_pivot(client):
    r = client.get("/")
    body = r.text
    # The home must not present a weekly grid; weekdays are derived
    # from session.started_at, never from the catalog.
    for weekday in ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]:
        assert weekday not in body


def test_library_shows_catalog_sections(client):
    r = client.get("/library")
    assert r.status_code == 200
    body = r.text
    # Sections headings visible
    assert "Programmes principaux" in body
    assert "Modules utilitaires" in body
    # Core templates visible
    for name in ["Push A", "Push B", "Pull A", "Pull B", "Legs A", "Legs B"]:
        assert name in body
    # Utility templates visible
    assert "Session courte" in body
    assert "LISS cardio" in body
    # Specialization visible
    assert "Rattrapage" in body
    # Archived templates NOT visible
    assert "Accent quadriceps" not in body
    assert "Accent chaîne postérieure" not in body
    assert "Biais pecs" not in body
    assert "Biais dos" not in body


def test_push_a_detail_has_all_eight_exercises(client):
    r = client.get("/library/push-a")
    assert r.status_code == 200
    body = r.text
    assert "Pectoraux, Deltoïdes, Triceps" in body
    for code in ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8"]:
        assert code in body


def test_pull_a_has_five_exercises(client):
    # Pull A targets back width + rear delts with 5 exercises.
    r = client.get("/library/pull-a")
    assert r.status_code == 200
    body = r.text
    assert "Dos largeur" in body
    for code in ["E1", "E2", "E3", "E4", "E5"]:
        assert code in body


def test_liss_template_is_cardio(client):
    r = client.get("/library/liss-abs")
    assert r.status_code == 200
    body = r.text
    assert "LISS" in body
    assert "120-130" in body
    assert "Roulette abdominale" in body


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


# ---------------------------------------------------------------------------
# Vocabulary: "Programmes de séance", no stale "Bibliothèque" / "template"
# ---------------------------------------------------------------------------


def test_library_page_uses_programmes_vocabulary(client):
    r = client.get("/library")
    body = r.text
    assert "Programmes de séance" in body
    assert "Bibliothèque" not in body
    assert "Catalogue complet" in body


def test_strength_template_hides_cardio_note(client):
    """Strength templates must not display cardio_note in their detail page."""
    r = client.get("/library/push-a")
    body = r.text
    # The old "10 miles de pas" or any "Cardio :" prefix must be gone
    assert "Cardio :" not in body
    # But the suggestion label should still be present
    assert "suggested_label" not in body  # raw key must not leak
    assert "incliné" in body.lower() or "lourd" in body.lower()
