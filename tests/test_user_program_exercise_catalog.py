"""Sb_CUSTOM_PROGRAM_WIZARD_05 — the read-only EKB exercise catalog service.

Pins the picker projection of `data/exercise_knowledge_base.json` (EKB_02, 103
entries): full sorted option list with honest null metadata, EXACT-match
enrichment only (no case/accent/alias normalisation in V1), determinism, and
cache immutability (callers never receive the cached internal data).

Read-only, no DB, no ORM. Every `app.*` import is inside the test/helper.
"""
from __future__ import annotations

import json


def _catalog():
    from app.services import user_program_exercise_catalog as cat

    cat._entries.cache_clear()
    return cat


def _ekb_exercises() -> dict:
    from app.config import BASE_DIR

    with (BASE_DIR / "data" / "exercise_knowledge_base.json").open(encoding="utf-8") as fh:
        return json.load(fh)["exercises"]


# ───────── picker_options ─────────


def test_catalog_is_non_empty():
    assert _catalog().picker_options()


def test_exact_count_is_103():
    assert len(_catalog().picker_options()) == 103


def test_options_are_deterministically_sorted():
    options = _catalog().picker_options()
    names = [o["name"] for o in options]
    assert names == sorted(names)


def test_names_match_ekb_canonical_keys_exactly():
    names = {o["name"] for o in _catalog().picker_options()}
    assert names == set(_ekb_exercises().keys())


def test_each_item_has_expected_shape():
    for o in _catalog().picker_options():
        assert set(o) == {"name", "zone_primary", "movement_pattern", "equipment_family"}


def test_null_metadata_is_supported():
    # The 52 EKB gaps carry null movement_pattern/etc.; the option list keeps
    # them honest (nulls preserved, never masked).
    options = _catalog().picker_options()
    assert any(o["movement_pattern"] is None for o in options)


# ───────── enrich ─────────


def test_exact_known_name_returns_enrichment():
    result = _catalog().enrich("Adduction assise")
    assert set(result) == {
        "variant_key",
        "variant_group",
        "equipment_family",
        "movement_pattern",
    }
    assert result["variant_key"] == "adduction-assise"
    assert result["movement_pattern"] == "isolation_lower"
    assert result["equipment_family"] == "machine"
    assert result["variant_group"] is None  # null in V1 by design


def test_unknown_name_returns_empty():
    assert _catalog().enrich("Exercice Totalement Inventé XYZ") == {}


def test_case_variation_does_not_match():
    # Exact canonical match only — no case folding in V1.
    assert _catalog().enrich("adduction assise") == {}


def test_alias_only_name_does_not_match_in_v1():
    # "Incline Dumbbell Press" is an _aliases key, NOT an `exercises` key →
    # not resolved in V1 (falls back to free-text `manual`).
    assert _catalog().enrich("Incline Dumbbell Press") == {}


# ───────── determinism & immutability ─────────


def test_repeated_calls_are_stable():
    cat = _catalog()
    # Distinct bindings (not `f() == f()`) so the assertion compares two real
    # computed results — deterministic, and free of the S5863 self-comparison.
    first_options = cat.picker_options()
    second_options = cat.picker_options()
    assert first_options == second_options
    first_enrich = cat.enrich("Adduction assise")
    second_enrich = cat.enrich("Adduction assise")
    assert first_enrich == second_enrich


def test_callers_cannot_mutate_cached_data():
    cat = _catalog()
    options = cat.picker_options()
    options[0]["name"] = "MUTATED"
    options.append({"name": "INJECTED"})
    fresh = cat.picker_options()
    assert all(o["name"] != "MUTATED" for o in fresh)
    assert len(fresh) == 103

    enriched = cat.enrich("Adduction assise")
    enriched["variant_key"] = "MUTATED"
    assert cat.enrich("Adduction assise")["variant_key"] == "adduction-assise"
