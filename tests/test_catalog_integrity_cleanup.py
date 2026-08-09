"""Sx_CAT_01 — Catalog Integrity Cleanup (data-only semantic fixes).

Sentinel tests locking the 3 CLEAR machine_slug/machine_family corrections in
data/reference_split.json, and proving that NO other field (slug/code/position/
set_scheme/rep_targets/name) is affected. Data-only: no schema change, no
service change, no history migration — the fixes only affect FUTURE sessions
(machine_slug/machine_family are snapshotted at session creation, so existing
SessionExercise rows keep their old values).
"""
from __future__ import annotations

import json
from pathlib import Path

CATALOG_PATH = Path(__file__).resolve().parent.parent / "data" / "reference_split.json"


def _catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def _exercise(templates: list[dict], slug: str, code: str) -> dict:
    for t in templates:
        if t.get("slug") == slug:
            for e in t.get("exercises", []):
                if e.get("code") == code:
                    return e
    raise AssertionError(f"exercise {slug}/{code} not found")


# ───────── 1. the 3 CLEAR corrections are applied ─────────


def test_push_b_e5_upright_row_reclassified():
    """push-b/E5 'Tirage front câble' (notes: deltoïdes latéraux) → shoulder
    lateral family, slug nulled (lat-pulldown was plainly wrong)."""
    e = _exercise(_catalog()["templates"], "push-b", "E5")
    assert e["machine_family"] == "shoulders-lateral-posterior"
    assert e["machine_slug"] is None


def test_catch_up_shoulders_e4_upright_row_reclassified():
    """catch-up-shoulders/E4 — same exercise, same fix."""
    e = _exercise(_catalog()["templates"], "catch-up-shoulders", "E4")
    assert e["machine_family"] == "shoulders-lateral-posterior"
    assert e["machine_slug"] is None


def test_legs_b_e3_high_wide_leg_press_reclassified():
    """legs-b/E3 'Leg Press (pieds hauts, écartés)' (notes: fessiers/ischios)
    → posterior family, slug nulled (leg-press resolves to quad-dominant in the
    atlas, so keeping the slug would break machine-link coherence)."""
    e = _exercise(_catalog()["templates"], "legs-b", "E3")
    assert e["machine_family"] == "legs-posterior-calves"
    assert e["machine_slug"] is None


# ───────── 2. immutable fields on the 3 fixed exercises are unchanged ─────────


def test_fixed_exercises_keep_code_position_scheme_reps_name():
    templates = _catalog()["templates"]
    expected = {
        ("push-b", "E5"): (5, "3x 12-15", "Tirage front câble (prise large)"),
        ("catch-up-shoulders", "E4"): (4, "3x 12-15", "Tirage front câble (prise large)"),
        ("legs-b", "E3"): (3, "3x 10-12", "Leg Press (pieds hauts, écartés)"),
    }
    for (slug, code), (pos, scheme, name) in expected.items():
        e = _exercise(templates, slug, code)
        assert e["code"] == code
        assert e["position"] == pos
        assert e["set_scheme"] == scheme
        assert e["name"] == name
        assert e.get("rep_targets"), "rep_targets must be preserved"


# ───────── 3. no lat-pulldown slug survives on an upright-row exercise ─────────


def test_no_upright_row_still_tagged_as_lat_pulldown():
    """Any exercise whose notes target lateral delts must NOT carry a
    lat-pulldown / back-vertical classification."""
    for t in _catalog()["templates"]:
        for e in t.get("exercises", []):
            notes = (e.get("notes") or "").lower()
            if "deltoïdes latéraux" in notes or "cibler les deltoïdes" in notes:
                assert e.get("machine_slug") != "lat-pulldown"
                assert e.get("machine_family") != "back-vertical"


# ───────── 4. corrected families resolve to valid atlas families ─────────


def test_corrected_families_are_valid_atlas_families():
    atlas = json.loads(
        (CATALOG_PATH.parent / "machine_atlas.json").read_text(encoding="utf-8")
    )
    valid = {f["slug"] for f in atlas["families"]}
    for slug, code in (("push-b", "E5"), ("catch-up-shoulders", "E4"), ("legs-b", "E3")):
        e = _exercise(_catalog()["templates"], slug, code)
        assert e["machine_family"] in valid


# ───────── 5. catalog global invariants still hold (data-only) ─────────


def test_all_codes_unique_within_template():
    for t in _catalog()["templates"]:
        codes = [e["code"] for e in t.get("exercises", [])]
        assert len(codes) == len(set(codes)), f"duplicate code in {t['slug']}"


def test_positions_sequential_within_template():
    for t in _catalog()["templates"]:
        positions = [e["position"] for e in t.get("exercises", [])]
        if positions:
            assert positions == list(range(1, len(positions) + 1)), (
                f"non-sequential positions in {t['slug']}"
            )


def test_template_slugs_unchanged():
    """The original 16 template slugs must be intact (no slug renamed) — plus the
    additive 'full-body-morphotype-priority-v1' catalog program (specialization)."""
    slugs = {t["slug"] for t in _catalog()["templates"]}
    expected = {
        "push-a", "push-b", "pull-a", "pull-b", "legs-a", "legs-b",
        "upper-pecs-delts", "upper-back-arms", "lower-quad-bias",
        "lower-posterior-bias", "liss-only", "liss-abs", "short-upper",
        "catch-up-shoulders", "catch-up-arms", "catch-up-back-width",
        "full-body-morphotype-priority-v1",
    }
    assert slugs == expected
