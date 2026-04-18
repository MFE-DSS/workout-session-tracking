"""Tests for /science/atlas route and template rendering."""
from __future__ import annotations


def test_atlas_page_renders(client):
    r = client.get("/science/atlas")
    assert r.status_code == 200
    body = r.text
    assert "Atlas machines" in body
    # Version tag present
    assert "Atlas version" in body


def test_atlas_page_lists_all_families(client):
    r = client.get("/science/atlas")
    body = r.text
    # Eight family anchors expected
    for slug in [
        "pecs-press",
        "pecs-fly",
        "back-vertical",
        "back-horizontal",
        "shoulders-press",
        "shoulders-lateral-posterior",
        "legs-quad-dominant",
        "legs-posterior-calves",
    ]:
        assert f'id="family-{slug}"' in body


def test_atlas_page_lists_machines_with_cues_and_mistakes(client):
    r = client.get("/science/atlas")
    body = r.text
    assert 'id="machine-chest-press-machine"' in body
    assert "Points d'exécution" in body
    assert "Erreurs fréquentes" in body


def test_atlas_page_toc_has_family_links(client):
    r = client.get("/science/atlas")
    body = r.text
    assert 'class="atlas-toc"' in body
    assert 'href="#family-pecs-press"' in body


def test_science_page_links_to_atlas(client):
    r = client.get("/science")
    assert r.status_code == 200
    assert "/science/atlas" in r.text
    assert "section-atlas" in r.text


def test_atlas_page_contains_load_semantic_label(client):
    r = client.get("/science/atlas")
    body = r.text
    assert "totale affichée sur la machine" in body or "par côté" in body
