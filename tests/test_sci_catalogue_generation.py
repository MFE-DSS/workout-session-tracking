"""Sb_SCI_V2_01 — les artefacts versionnés se reproduisent à l'octet depuis leurs sources.

Aucune fiche scientifique n'est éditée à la main : le générateur rejoue la clôture
(rulings opérateur) sur les sources de `data/sci/sources/`, le validateur régénère le rapport.
Si un fichier versionné diffère d'un seul octet de ce que rendent ses sources, c'est qu'il a été
touché à la main — ou que le générateur a changé sans être rejoué.
"""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path

import pytest

from scripts import generate_sci_catalogue as g
from scripts import validate_sci_catalogue as v

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def built() -> dict[str, bytes]:
    return g.build(ROOT)


def test_generator_outputs_are_exactly_the_versioned_files(built):
    assert set(built) == set(g.OUTPUTS)
    for rel, data in built.items():
        assert (ROOT / rel).read_bytes() == data, f"{rel} differs from its generator"


def test_two_builds_are_byte_identical(built):
    again = g.build(ROOT)
    assert again == built


def test_validation_report_reproduces_byte_for_byte(built):
    report = v.render_report(v.validate(v.parse(built[g.CATALOGUE]), v.load_inputs(ROOT)), built[g.CATALOGUE])
    assert (ROOT / v.REPORT).read_bytes() == report


def test_report_pins_the_catalogue_it_validated():
    import json

    report = json.loads((ROOT / v.REPORT).read_text(encoding="utf-8"))
    digest = hashlib.sha256((ROOT / g.CATALOGUE).read_bytes()).hexdigest()
    assert report["catalogue_digest"] == digest
    assert report["metrics"]["format_errors"] == 0


def test_header_records_the_digest_of_its_sources(built):
    import json

    header = json.loads(built[g.CATALOGUE])["catalogue_header"]
    assert header["sources_digest"] == g.sources_digest(ROOT)
    assert "generated_at" not in header


def test_changing_a_source_changes_the_build(tmp_path, built):
    """Le générateur lit vraiment ses sources : sans cela, l'égalité à l'octet ne prouverait rien.
    La mutation est vérifiée avant d'en tirer quoi que ce soit — une mutation qui ne mute rien
    rendrait ce test vert pour de mauvaises raisons."""
    import json
    import shutil

    shutil.copytree(ROOT / "data" / "sci", tmp_path / "data" / "sci")
    source = tmp_path / "data" / "sci" / "sources" / "identity_map.json"
    identity_map = json.loads(source.read_text(encoding="utf-8"))
    assert identity_map["pompes"]["identity_relation"] == "CANONICAL"
    identity_map["pompes"]["canonical_display_name"] = "Pompes (mutation de test)"
    source.write_text(json.dumps(identity_map, ensure_ascii=False, indent=2), encoding="utf-8")

    mutated = g.build(tmp_path)
    assert g.sources_digest(tmp_path) != g.sources_digest(ROOT)
    assert mutated[g.CATALOGUE] != built[g.CATALOGUE]
    assert "Pompes (mutation de test)" in mutated[g.CATALOGUE].decode("utf-8")


# ── nommage : « v2 » est déjà le nom de l'ancien recommandeur (spec §4)

SCI_MODULES = [ROOT / "app/services/sci_catalogue.py",
               ROOT / "scripts/generate_sci_catalogue.py",
               ROOT / "scripts/validate_sci_catalogue.py"]


@pytest.mark.parametrize("path", SCI_MODULES, ids=lambda p: p.name)
def test_sci_code_never_uses_the_recommender_policy_literal(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    literals = {n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    assert "v2" not in literals
    assert "v3" not in literals


@pytest.mark.parametrize("path", SCI_MODULES, ids=lambda p: p.name)
def test_sci_code_imports_nothing_from_the_product(path):
    """Fondation statique : ni le service, ni TRAIN A, ni le recommandeur ne sont atteints.
    Les scripts n'importent pas `app` non plus — l'installation éditable épinglerait sinon
    `app` sur un autre arbre que celui qu'on valide."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imported = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    imported |= {n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    assert not {m for m in imported if m == "app" or m.startswith("app.")}
