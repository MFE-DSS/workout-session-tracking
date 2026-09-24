"""Tests for /science/atlas route and template rendering."""
from __future__ import annotations


def test_atlas_page_renders(client):
    """⚠ REPOINTÉE PAR `UI-CP7 REFERENCE` — ON ÉPINGLE LA VERSION, PAS SON
    LIBELLÉ.

    Cette garde cherchait la chaîne « Atlas version ». Le libellé a rejoint la
    **signature de document** (« Atlas machines · version <v> »), qui dit la
    provenance d'un document là où le pied générique ne disait qu'un
    mot-marque.

    La propriété protégée est que l'atlas DÉCLARE SA VERSION. Un libellé est
    une formulation ; la version est le fait. On épingle donc la valeur réelle,
    lue à la source, et non le texte qui l'entoure — sans quoi la garde
    rougirait à chaque reformulation tout en laissant disparaître la version.
    """
    from app.services import machine_atlas

    version = machine_atlas.atlas_version()
    assert version, "prémisse : le catalogue expose bien une version"

    r = client.get("/science/atlas")
    assert r.status_code == 200
    body = r.text
    assert "Atlas machines" in body
    assert version in body, f"l'atlas ne déclare plus sa version ({version})"


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
