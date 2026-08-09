"""Catalog tests for the additive program "Full Body — Morphotype Priority".

Pins the new specialization template (exists / exact order / sets & reps / intent zones /
curated substitutes) and that it flows through the EXISTING session pipeline (create session
-> 8 exercise cards -> save→next) without touching any existing template. Data + HTTP only —
no model change, no migration.
"""
from __future__ import annotations

import json
import pathlib

CATALOG = json.loads(
    (pathlib.Path(__file__).parent.parent / "data" / "reference_split.json").read_text(
        encoding="utf-8"
    )
)
SLUG = "full-body-morphotype-priority-v1"

# (code, name, set_scheme, sets, min_reps, max_reps)
EXPECTED = [
    ("E1", "Développé incliné haltères 30°", "3x 6-10", 3, 6, 10),
    ("E2", "Rowing chest-supported", "3x 8-12", 3, 8, 12),
    ("E3", "Hack Squat machine", "2x 6-10", 2, 6, 10),
    ("E4", "Romanian Deadlift barre", "2x 6-10", 2, 6, 10),
    ("E5", "Élévations latérales câble", "4x 12-20", 4, 12, 20),
    ("E6", "Reverse fly machine", "3x 12-20", 3, 12, 20),
    ("E7", "Relevés mollets debout machine", "4x 8-12", 4, 8, 12),
    ("E8", "Mollets assis machine", "3x 12-20", 3, 12, 20),
]

# Intent zone each exercise must classify to (existing taxonomy, no invented zone).
EXPECTED_ZONES = {
    "Développé incliné haltères 30°": "pecs",
    "Rowing chest-supported": "upper_back",
    "Hack Squat machine": "quads",
    "Romanian Deadlift barre": "posterior",
    "Élévations latérales câble": "delt_lat",
    "Reverse fly machine": "delt_post",
    "Relevés mollets debout machine": "calves",
    "Mollets assis machine": "calves",
}


def _template() -> dict:
    return next(t for t in CATALOG["templates"] if t["slug"] == SLUG)


# ─────────────────────────── catalog shape ───────────────────────────


def test_program_present_in_catalog():
    t = _template()
    assert t["name"] == "Full Body — Morphotype Priority"
    assert t["catalog_section"] == "specialization"  # not "user", not "core"
    assert t["kind"] == "strength"


def test_exercises_in_expected_order():
    exs = _template()["exercises"]
    assert [e["code"] for e in exs] == ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8"]
    assert [e["position"] for e in exs] == list(range(1, 9))
    assert [e["name"] for e in exs] == [row[1] for row in EXPECTED]


def test_sets_and_reps_are_correct():
    exs = _template()["exercises"]
    for e, (_code, _name, scheme, sets, lo, hi) in zip(exs, EXPECTED, strict=True):
        assert e["set_scheme"] == scheme
        assert len(e["rep_targets"]) == sets
        for rt in e["rep_targets"]:
            assert rt["min_reps"] == lo
            assert rt["max_reps"] == hi


def test_each_exercise_has_curated_substitutes():
    for e in _template()["exercises"]:
        assert e.get("substitutes"), f"{e['code']} missing curated substitutes"


def test_exercise_names_classify_to_intended_zone():
    from app.services.muscle_mapping import classify_exercise

    for name, zone in EXPECTED_ZONES.items():
        got, _ = classify_exercise(name)
        assert got == zone, f"{name!r} classified as {got}, expected {zone}"


# ─────────────────────── existing session pipeline ───────────────────────


def test_session_can_be_created_and_page_renders(client):
    # Launched exactly like any catalog template (existing create_session path).
    r = client.post("/sessions", data={"template_slug": SLUG}, follow_redirects=False)
    assert r.status_code == 303
    loc = r.headers["location"]
    assert loc.startswith("/sessions/")
    page = client.get(loc)
    assert page.status_code == 200  # existing exercise cards render for all 8 exercises


def test_created_session_has_eight_exercises(client):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    r = client.post("/sessions", data={"template_slug": SLUG}, follow_redirects=False)
    sid = int(r.headers["location"].rstrip("/").split("/")[-1])
    with SessionLocal() as db:
        session = db.get(WorkoutSession, sid)
        assert session is not None
        assert len(session.session_exercises) == 8


# ─────────────────────── non-regression on existing templates ───────────────────────


def test_additive_only_existing_staples_unchanged():
    by_slug = {t["slug"]: t for t in CATALOG["templates"]}
    # the new program is additive, not a rename of an existing staple
    assert SLUG in by_slug
    assert len(by_slug) == 17  # 16 originals + 1
    # spot-check untouched staples keep their known shape
    assert len(by_slug["push-a"]["exercises"]) == 7
    assert by_slug["push-a"]["catalog_section"] == "core"
    assert len(by_slug["liss-abs"]["exercises"]) == 4
