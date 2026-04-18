"""Tests for app.services.machine_atlas loader and data/machine_atlas.json."""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.services import machine_atlas


@pytest.fixture(autouse=True)
def _reset_cache():
    machine_atlas.reset_cache()
    yield
    machine_atlas.reset_cache()


def test_atlas_version_present():
    assert machine_atlas.atlas_version()


def test_all_families_non_empty():
    families = machine_atlas.all_families()
    assert len(families) >= 8
    for fam in families:
        assert fam.get("slug")
        assert fam.get("name")
        assert fam.get("zone")
        assert isinstance(fam.get("machines"), list)
        assert len(fam["machines"]) >= 1


def test_family_slugs_unique():
    families = machine_atlas.all_families()
    slugs = [f["slug"] for f in families]
    assert len(slugs) == len(set(slugs))


def test_machine_slugs_unique_globally():
    families = machine_atlas.all_families()
    seen: set[str] = set()
    for fam in families:
        for m in fam["machines"]:
            assert m["slug"] not in seen, f"duplicate machine slug {m['slug']}"
            seen.add(m["slug"])


def test_get_family_known():
    fam = machine_atlas.get_family("pecs-press")
    assert fam is not None
    assert fam["zone"] == "pecs"


def test_get_family_unknown_returns_none():
    assert machine_atlas.get_family("does-not-exist") is None
    assert machine_atlas.get_family(None) is None
    assert machine_atlas.get_family("") is None


def test_get_machine_known():
    m = machine_atlas.get_machine("chest-press-machine")
    assert m is not None
    assert m["equipment"] == "machine"
    assert len(m["execution_cues"]) >= 2
    assert len(m["common_mistakes"]) >= 2


def test_get_machine_unknown_returns_none():
    assert machine_atlas.get_machine("does-not-exist") is None
    assert machine_atlas.get_machine(None) is None


def test_family_of_machine():
    fam = machine_atlas.family_of_machine("chest-press-machine")
    assert fam is not None
    assert fam["slug"] == "pecs-press"


def test_get_for_template_exercise_machine_only():
    te = SimpleNamespace(machine_slug="chest-press-machine", machine_family=None)
    result = machine_atlas.get_for_template_exercise(te)
    assert result is not None
    assert result["machine"]["slug"] == "chest-press-machine"
    assert result["family"]["slug"] == "pecs-press"


def test_get_for_template_exercise_family_only():
    te = SimpleNamespace(machine_slug=None, machine_family="pecs-press")
    result = machine_atlas.get_for_template_exercise(te)
    assert result is not None
    assert result["machine"] is None
    assert result["family"]["slug"] == "pecs-press"


def test_get_for_template_exercise_no_link():
    te = SimpleNamespace(machine_slug=None, machine_family=None)
    assert machine_atlas.get_for_template_exercise(te) is None


def test_get_for_template_exercise_none_input():
    assert machine_atlas.get_for_template_exercise(None) is None


def test_cache_reset():
    v1 = machine_atlas.atlas_version()
    machine_atlas.reset_cache()
    v2 = machine_atlas.atlas_version()
    assert v1 == v2


def test_all_machines_have_valid_enums():
    valid_equip = {"machine", "smith", "cable", "haltere", "barbell", "bodyweight"}
    valid_lat = {"bilateral", "unilateral", "both"}
    valid_load = {"total", "per_side"}
    for fam in machine_atlas.all_families():
        for m in fam["machines"]:
            assert m["equipment"] in valid_equip, f"{m['slug']}: {m['equipment']}"
            assert m["laterality"] in valid_lat, f"{m['slug']}: {m['laterality']}"
            assert m["load_semantics"] in valid_load, f"{m['slug']}: {m['load_semantics']}"
