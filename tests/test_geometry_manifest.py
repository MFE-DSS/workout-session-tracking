"""`UIV3_VISUAL_BASELINE_01` — gardes du manifeste de géométrie.

POURQUOI CETTE COUCHE EXISTE
-----------------------------
Deux défauts de ce programme étaient **invisibles à l'œil ET invisibles au
CSS** :

  · un `id` dupliqué en état `CORRECTION` — deux séries rendues au même
    endroit, avec les mêmes `name` de champs masqués. Aucun pixel ne bouge.
    1 178 tests ne l'avaient pas vu ; l'analyseur statique si ;
  · `TERMINER LA SÉANCE` rabotée de 56 à 44 px par une règle d'accessibilité
    plus spécifique chargée plus tard. La garde qui lisait les noms de
    sélecteurs est restée VERTE : la collision vivait dans la cascade.

Une baseline en pixels seule ne les attrape ni l'un ni l'autre. D'où la
couche B.
"""
from __future__ import annotations

import re

from scripts.geometry_manifest import (
    LEGACY_REFERENCE_FLAG,
    MANIFEST_JS,
    REQUIRED_FIELDS,
    SOVEREIGN,
    SURFACE_STATUS,
    TRANSITIONAL,
    drifted_fields,
    gate_is_allowed,
    missing_fields,
    shrunk_elements,
)


def _manifest(**kw) -> dict:
    base = dict.fromkeys(REQUIRED_FIELDS, 0)
    base["viewport"] = "390x844"
    base["_element_heights"] = {}
    base.update(kw)
    return base


# ───────────────────── complétude du manifeste ─────────────────────


def test_the_operator_required_fields_are_all_declared():
    """La liste vient d'une décision opérateur, pas d'un choix d'implémentation."""
    assert set(REQUIRED_FIELDS) == {
        "viewport", "document_width", "document_height",
        "hard_overflow_count", "target_below_44_count",
        "dominant_action_count", "open_disclosure_count",
        "sticky_layer_count", "primary_action_y", "active_instrument_y",
        "duplicate_id_count",
    }


def test_an_incomplete_manifest_is_reported_not_ignored():
    """Un manifeste amputé qui passe en silence, c'est une baseline qui a
    l'air de garder plus qu'elle ne garde."""
    partial = _manifest()
    del partial["duplicate_id_count"]
    assert missing_fields(partial) == ["duplicate_id_count"]


def test_a_complete_manifest_reports_nothing_missing():
    assert missing_fields(_manifest()) == []


# ───────────────────── détection de rétrécissement ─────────────────────


def test_a_shrunk_element_is_detected():
    """C'est la fonction qui a attrapé `TERMINER LA SÉANCE` à 56 → 44."""
    before = _manifest(_element_heights={"0|button.btn--end|TERMINER": 56.0})
    after = _manifest(_element_heights={"0|button.btn--end|TERMINER": 44.0})
    assert shrunk_elements(before, after) == [
        ("0|button.btn--end|TERMINER", 56.0, 44.0)]


def test_growing_is_never_reported_as_shrinking():
    """Une fermeture 44 px fait GRANDIR — 49 éléments dans cette tranche.
    Les signaler serait rendre l'instrument inutilisable."""
    before = _manifest(_element_heights={"0|button.btn|Démarrer": 26.8})
    after = _manifest(_element_heights={"0|button.btn|Démarrer": 44.0})
    assert shrunk_elements(before, after) == []


def test_sub_pixel_noise_is_not_a_shrink():
    """Une différence de rastérisation n'est pas une régression de design."""
    before = _manifest(_element_heights={"0|a.x|y": 44.0})
    after = _manifest(_element_heights={"0|a.x|y": 43.8})
    assert shrunk_elements(before, after) == []


def test_an_element_that_disappeared_is_not_counted_as_shrunk():
    """Une suppression est un autre problème, traité par la couche pixel et
    par le décompte d'éléments — pas un rétrécissement de 44 à 0."""
    before = _manifest(_element_heights={"0|a.x|y": 44.0})
    assert shrunk_elements(before, _manifest()) == []


# ───────────────────── dérive structurelle ─────────────────────


def test_a_duplicate_id_appearing_is_reported():
    """Le défaut de phase 2 : deux séries rendues au même endroit, aucun
    pixel déplacé."""
    drift = drifted_fields(_manifest(), _manifest(duplicate_id_count=1))
    assert drift == {"duplicate_id_count": (0, 1)}


def test_a_second_sticky_layer_is_reported():
    """La passe de densité a ramené 4 couches collantes à 1. En reprendre une
    doit être un choix, pas une découverte."""
    drift = drifted_fields(_manifest(sticky_layer_count=1),
                           _manifest(sticky_layer_count=2))
    assert drift == {"sticky_layer_count": (1, 2)}


def test_identical_manifests_report_no_drift():
    assert drifted_fields(_manifest(), _manifest()) == {}


def test_element_heights_are_not_reported_as_field_drift():
    """Les hauteurs ont leur propre comparateur, directionnel. Les mêler aux
    champs rendrait tout diff illisible."""
    drift = drifted_fields(_manifest(_element_heights={"a": 1}),
                           _manifest(_element_heights={"a": 2}))
    assert drift == {}


# ───────────────────── la sonde ─────────────────────


def _code() -> str:
    """Sans commentaires — une garde qui lit sa propre prose ne garde rien."""
    return re.sub(r"/\*.*?\*/", " ", MANIFEST_JS, flags=re.S)


def test_the_manifest_probe_emits_every_required_field():
    code = _code()
    for field in REQUIRED_FIELDS:
        assert f"{field}:" in code, f"{field} absent de la sonde"


def test_hard_overflow_requires_all_three_conditions():
    """Un débordement DUR n'est pas un simple `scrollWidth > clientWidth` :
    il faut aussi `overflow-x: visible` et pas d'ellipse. Sans ces deux
    conditions, la mesure rendait 31 débordements dont 23 faux."""
    code = _code()
    assert "scrollWidth" in code
    assert "clientWidth" in code
    assert "overflowX" in code
    assert "textOverflow" in code


def test_the_probe_skips_closed_disclosures():
    assert "details:not([open])" in _code()


# ───────────────────── statut de surface ─────────────────────
#
# Décision opérateur du 2026-08-20. Ces gardes existent pour qu'une baseline
# ne puisse pas GELER LA DETTE EN LA RENDANT CONTRACTUELLE.


def test_home_and_session_are_sovereign():
    """Les deux surfaces passées par Design Lab, dogfood et validation
    humaine. Une dérive y est une régression."""
    for surface in ("home", "session-active", "session-done"):
        assert SURFACE_STATUS[surface] == SOVEREIGN


def test_profile_and_library_are_transitional():
    """Leur modèle d'interaction est hérité. Les figer reviendrait à
    contractualiser ce que `UX4_01` et `UX4_02` doivent démolir."""
    for surface in ("profile", "library", "progress", "dashboard"):
        assert SURFACE_STATUS[surface] == TRANSITIONAL


def test_a_transitional_surface_admits_only_mechanical_gates():
    """La garantie centrale : une refonte structurelle de Profile ou Library
    ne doit JAMAIS être traitée comme une régression."""
    assert gate_is_allowed("profile", "mechanical") is True
    assert gate_is_allowed("profile", "pixel") is False
    assert gate_is_allowed("library", "architecture") is False


def test_a_sovereign_surface_admits_every_gate():
    for gate in ("pixel", "architecture", "mechanical"):
        assert gate_is_allowed("home", gate) is True


def test_an_unregistered_surface_defaults_to_transitional():
    """Promouvoir une surface en `SOVEREIGN` doit être un geste délibéré.
    Un oubli d'inscription ne doit pas la geler par défaut."""
    assert gate_is_allowed("surface-inconnue", "pixel") is False
    assert gate_is_allowed("surface-inconnue", "mechanical") is True


def test_the_legacy_reference_flag_exists_for_transitional_captures():
    """Une capture de surface transitionnelle est une ARCHIVE de l'état de
    départ, pas un design à préserver — et doit se lire comme telle."""
    assert LEGACY_REFERENCE_FLAG == "legacy_reference"


def test_the_target_count_is_left_to_the_taxonomy_module():
    """Un décompte approximatif dans un manifeste de non-régression est pire
    qu'absent : il donne une fausse assurance. `target_size_taxonomy` sait
    distinguer une zone tactile étendue d'un rectangle nu ; pas cette sonde."""
    assert "target_below_44_count: null" in _code()
