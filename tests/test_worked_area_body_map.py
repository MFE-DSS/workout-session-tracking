"""Sb_BODYMAP_01.1 — Inline anatomical worked-area body map.

The decorative worked-area blob is replaced by an inline SVG silhouette
(face + back), 6 macro-regions, primary highlighted full / secondary weak,
`aria-hidden`, non-medical, SSR / no-JS. The text « Principal / Secondaire »
stays the source of truth (labels unchanged, still 11 fine zones).

Asserts (rendered HTML + template/CSS source; no pixels):
- the dedicated partial is included in the exercise card;
- the SVG silhouette is present and aria-hidden;
- a mapped primary zone activates the expected macro-region class;
- an unknown exercise activates NO region (neutral silhouette);
- « Principal » and the human label are still rendered;
- `delt_lat` still renders « Deltoïdes latéraux » in the text;
- no new hex colour in the body-map CSS; no JS added.
"""
from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FOCUS_CSS = ROOT / "app" / "static" / "css" / "session_focus.css"
EXERCISE_CARD = ROOT / "app" / "templates" / "_partials" / "exercise_card.html"
PARTIAL = ROOT / "app" / "templates" / "_partials" / "worked_area_body_map.html"
JS_DIR = ROOT / "app" / "static" / "js"


def _seed(db, user_id, names):
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    s = WorkoutSession(
        user_id=user_id,
        template_slug_snapshot="bodymap",
        template_name_snapshot="Body map test",
        started_at=datetime.now(UTC),
        status="in_progress",
    )
    for i, name in enumerate(names):
        se = SessionExercise(
            exercise_code_snapshot=f"E{i + 1}",
            exercise_name_snapshot=name,
            position=i + 1,
        )
        se.set_logs.append(
            SetLog(kind="work", set_index=1, weight_kg=None, reps=None, completed=False)
        )
        s.session_exercises.append(se)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def _body(client, names):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _seed(db, user.id, names)
        sid = s.id
    r = client.get(f"/sessions/{sid}", follow_redirects=False)
    assert r.status_code == 200, r.text[:400]
    return r.text


# ───────── partial inclusion + SVG structure ─────────


def test_partial_exists():
    assert PARTIAL.exists()


def test_card_includes_partial():
    src = EXERCISE_CARD.read_text(encoding="utf-8")
    assert "worked_area_body_map.html" in src


def test_svg_silhouettes_present(client):
    body = _body(client, ["Chest press"])
    assert "wa-silhouettes" in body
    # face + back → two inline SVGs
    assert body.count("wa-silhouette--front") == 1
    assert body.count("wa-silhouette--back") == 1


def test_body_map_container_preserved(client):
    """The stable slot container is kept (aria-hidden decorative)."""
    body = _body(client, ["Chest press"])
    m = re.search(r'<div[^>]*session-focus__body-map[^>]*>', body)
    assert m is not None
    assert "aria-hidden" in m.group(0)


def test_silhouettes_are_aria_hidden(client):
    body = _body(client, ["Chest press"])
    m = re.search(r'<div class="wa-silhouettes"[^>]*>', body)
    assert m is not None
    assert 'aria-hidden="true"' in m.group(0)


# ───────── mapped → expected macro-region active ─────────


def test_mapped_primary_activates_region(client):
    """A « Chest press » resolves to pecs → chest region is primary."""
    body = _body(client, ["Chest press"])
    assert "wa-region--chest is-primary" in body


def test_mapped_dorsal_zone_activates_back(client):
    """A vertical pull resolves to lats → back region is primary (dos)."""
    body = _body(client, ["Tirage vertical poulie haute"])
    assert "wa-region--back is-primary" in body


# ───────── unknown → no region active ─────────


def test_unknown_activates_no_region(client):
    """Synthetic exercise name → status unknown → neutral silhouette."""
    body = _body(client, ["Exercise Z"])
    assert "is-primary" not in body
    # silhouettes still rendered (neutral), text carries « À qualifier »
    assert "wa-silhouettes" in body
    assert "à qualifier" in body.lower()


# ───────── text source of truth preserved ─────────


def test_primary_row_and_label_preserved(client):
    body = _body(client, ["Chest press"])
    assert "session-focus__worked-area-row--primary" in body
    assert "Pectoraux" in body


def test_delt_lat_text_label_unchanged(client):
    """Text still humanised: delt_lat → « Deltoïdes latéraux ». The body-map
    build must not regress the label (irritant #1 untouched)."""
    body = _body(client, ["Élévation latérale haltères"])
    assert "Deltoïdes latéraux" in body
    # the raw code must never leak in the primary row text
    assert ">Delt_lat<" not in body
    assert ">delt_lat<" not in body


# ───────── non-goals: no JS, no new colour, no external asset ─────────


def test_no_js_added():
    src = PARTIAL.read_text(encoding="utf-8")
    assert "<script" not in src
    assert "addEventListener" not in src
    if JS_DIR.exists():
        # no new nav/bodymap JS file introduced by this build
        assert not any("bodymap" in p.name.lower() for p in JS_DIR.glob("*.js"))


def test_no_new_hex_colour_in_body_map_css():
    css = FOCUS_CSS.read_text(encoding="utf-8")
    start = css.find(".session-focus__body-map")
    end = css.find(".session-focus__worked-area-pattern", start)
    region = css[start:end]
    assert start != -1 and end != -1
    # the body-map region reuses vars only — no raw hex colour
    assert not re.search(r"#[0-9a-fA-F]{3,6}\b", region), region


def test_body_map_css_no_external_asset():
    css = FOCUS_CSS.read_text(encoding="utf-8")
    start = css.find(".session-focus__body-map")
    end = css.find(".session-focus__worked-area-pattern", start)
    region = css[start:end]
    assert "url(" not in region


def test_svg_inline_no_external_reference():
    src = PARTIAL.read_text(encoding="utf-8")
    # inline SVG only — no <img>, no external href/src
    assert "<img" not in src
    assert "src=" not in src
    assert "http" not in src
