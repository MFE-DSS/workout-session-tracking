"""SSR smoke tests for the home + template library.

Sprint 0.5 explicitly removed the weekday-pivoted home, so these
tests also guard against its accidental reintroduction.
"""
from __future__ import annotations


def test_home_renders_action_tiles(client):
    r = client.get("/")
    assert r.status_code == 200
    body = r.text
    # Main CTA (Sx_UI_06 Sb_UI_06.3): a start/resume action in the hero —
    # « Démarrer » (recommended session, direct start), « Démarrer une séance »
    # (cold-start fallback), « Reprendre » (active session) or the « Nouvelle
    # séance » tile when a session is open.
    assert any(
        label in body
        for label in ("Démarrer", "Reprendre", "Nouvelle séance")
    )
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
    # Sections headings visible.
    # `Sb_UI_BIBLIO_01` / `OPERATOR_DECISION` NAMING — l'écran employait DEUX
    # mots pour la même chose (« Programmes » / « Modules »), et « Programmes »
    # nommait déjà le domaine qui contient cet écran. Un seul mot : « Séances ».
    assert "Séances principales" in body
    assert "Séances utilitaires" in body
    assert "Programmes principaux" not in body, (
        "l'ancien libellé est revenu — deux mots pour le même objet"
    )
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


def test_push_a_detail_has_all_seven_exercises(client):
    # v10: Push A reduit a 7 exercices (E8 retire pour respecter cible 1h15)
    r = client.get("/library/push-a")
    assert r.status_code == 200
    body = r.text
    assert "Pectoraux, Deltoïdes, Triceps" in body
    for code in ["E1", "E2", "E3", "E4", "E5", "E6", "E7"]:
        assert code in body
    assert "E8" not in body


def test_pull_a_has_seven_exercises(client):
    # Pull A targets back width + rear delts. v12 balance raised the
    # density to 7 exercises / 20 work sets (benchmark review chantier 3).
    r = client.get("/library/pull-a")
    assert r.status_code == 200
    body = r.text
    assert "Dos largeur" in body
    for code in ["E1", "E2", "E3", "E4", "E5", "E6", "E7"]:
        assert code in body
    assert "Pullover machine" in body
    assert "Straight-arm pulldown" in body


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
# Vocabulaire : « Explorer », sans « Bibliothèque » ni « template » résiduels
# ---------------------------------------------------------------------------


def test_library_page_uses_programmes_vocabulary(client):
    """`OPERATOR_DECISION` NAMING — le domaine s'appelle **Programmes** ; cette
    surface est l'un de ses trois enfants et s'appelle **Explorer**.

    « Programmes de séance » confondait l'enfant avec le domaine. La garde
    suit la décision au lieu de la refuser, et elle vérifie EN PLUS que
    l'ancienne appellation ne subsiste pas : deux noms pour une surface, c'est
    le défaut qu'on vient de retirer.
    """
    r = client.get("/library")
    body = r.text
    assert "Explorer" in body
    assert "Programmes de séance" not in body
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
