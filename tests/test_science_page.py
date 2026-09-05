"""Tests for the /science page (replaces /rules)."""
from __future__ import annotations


def test_science_page_renders(client):
    r = client.get("/science")
    assert r.status_code == 200
    assert "Science" in r.text
    assert "Pourquoi noter" in r.text


def test_science_page_shows_all_method_rules(client):
    """All 7 seeded method_rules must appear with their slug anchors.

    DS (Drop Set) has been removed from the legend and rules because no
    template in the current catalog uses the DS technique. The Technique
    enum still defines DS for future programs.
    """
    r = client.get("/science")
    body = r.text
    assert 'id="rule-carnet-progression"' in body
    assert 'id="rule-plages-repetitions"' in body
    assert 'id="rule-series-approche"' in body
    assert 'id="rule-tempo"' in body
    assert 'id="rule-temps-repos"' in body
    assert 'id="rule-legende-technique"' in body
    assert 'id="rule-rest-pause"' in body
    # DS removed — no "drop-sets" rule while no template uses DS
    assert 'id="rule-drop-sets"' not in body


def test_science_page_has_architecture_diagram(client):
    """The SVG diagram must be rendered inline."""
    r = client.get("/science")
    body = r.text
    assert "<svg" in body
    assert "diagram-title" in body
    assert "Programmes" in body
    assert "Seance" in body
    assert "Historique" in body


def test_science_page_has_cardio_section(client):
    """The cardio section must be present with the anti-pseudo-science disclaimer."""
    r = client.get("/science")
    body = r.text
    assert "Place du cardio" in body
    assert "LISS" in body
    assert "Pas de pseudo-science" in body


def test_science_page_has_materialisation_section(client):
    """Sb_UI_10.4 — the materialisation section must appear. Visible product
    name migrated SPIGNOS → Auren (the section header is now
    'Comment Auren matérialise'); the section itself is unchanged.

    ⚠ `Sb_UI_SCIENCE_ACCENTS_01` — CETTE GARDE ÉPINGLAIT LE DÉFAUT.

    Elle exigeait « Comment Auren materialise » et « Ce qui reste prive »,
    c'est-à-dire les graphies SANS ACCENT, dans un produit français. Une garde
    peut fixer un défaut aussi solidement qu'une propriété ; c'est la
    cinquième fois que ce dépôt en prend une à le faire.

    Son intention — la section doit apparaître — est intacte. Seule la chaîne
    attendue est corrigée.
    """
    r = client.get("/science")
    body = r.text
    assert "Comment Auren matérialise" in body
    assert "Ce qui reste privé" in body


def test_rules_redirects_to_science(client):
    """Legacy /rules must redirect (301) to /science."""
    r = client.get("/rules", follow_redirects=False)
    assert r.status_code == 301
    assert r.headers["location"] == "/science"


def test_home_tile_points_to_science(client):
    """Home tile 'Science' must link to /science."""
    r = client.get("/")
    body = r.text
    assert ">Science<" in body
    assert "/science" in body


def test_science_page_requires_auth(client):
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()
    r = client.get("/science", follow_redirects=False)
    assert r.status_code == 303
