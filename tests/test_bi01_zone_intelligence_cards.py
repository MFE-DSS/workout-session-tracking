"""Sb_BI_01.1 — Zone Intelligence Cards.

V1 "Lecture par zones" on the existing /body/intelligence surface. Reuses
the per-zone signals from muscle_scoring (hard sets, session count, trend,
confidence) WITHOUT creating a new score. No opaque global score in the
header, no radar, no Home change, no /physique change.

Rule (Sx_BI_01): silence rather than an invented number; non-medical
wording; confidence visible; each figure traceable.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "app" / "templates" / "body_intelligence.html"
ZONE_CARD_PARTIAL = ROOT / "app" / "templates" / "_partials" / "body_intelligence_zone_card.html"
ROUTER_FILE = ROOT / "app" / "routers" / "body_intelligence.py"
CSS_FILE = ROOT / "app" / "static" / "css" / "body_intelligence.css"
# `TRAIN1-C` — `physique.html` a été supprimé avec sa surface. Ces gardes
# de confinement visent la SURFACE VOISINE : c'est Progression qui porte
# désormais l'instrument anatomique, donc c'est elle qu'il faut vérifier.
PROGRESS_TEMPLATE = ROOT / "app" / "templates" / "progress.html"
INDEX_TEMPLATE = ROOT / "app" / "templates" / "index.html"


# ───────── flag fixture (mirror the existing route tests) ─────────
# autouse + ordered BEFORE the `client` fixture so the flag is read when
# the app is built. Default ON for this module; the 404 test builds its own
# flag-off client explicitly.


@pytest.fixture(autouse=True)
def _enable_bi(monkeypatch):
    monkeypatch.setenv("BODY_INTELLIGENCE_ENABLED", "1")


# ───────── seed ─────────


def _seed_zone_volume(db, user_id):
    """Seed sessions with two zones worked: back squat (quads) + curl (biceps)."""
    from app.models.catalog import RepTarget, TemplateExercise, WorkoutTemplate
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    t = WorkoutTemplate(slug=f"zone-{user_id}", name="Zone test", kind="strength")
    db.add(t)
    db.flush()
    te1 = TemplateExercise(
        template_id=t.id, position=1, code="A1", name="Back squat", set_scheme="3×6-10"
    )
    te2 = TemplateExercise(
        template_id=t.id, position=2, code="A2", name="Curl EZ-bar debout", set_scheme="3×8-12"
    )
    db.add_all([te1, te2])
    db.flush()
    db.add_all([
        RepTarget(template_exercise_id=te1.id, set_index=1, min_reps=6, max_reps=10),
        RepTarget(template_exercise_id=te2.id, set_index=1, min_reps=8, max_reps=12),
    ])
    db.flush()
    now = datetime.now(UTC)
    for k in range(4):
        s = WorkoutSession(
            user_id=user_id, template_id=t.id, template_slug_snapshot=t.slug,
            template_name_snapshot=t.name, started_at=now - timedelta(days=k * 3 + 1),
            ended_at=now - timedelta(days=k * 3 + 1), status="completed",
            global_state="good", concentration="high",
        )
        se1 = SessionExercise(
            template_exercise_id=te1.id, exercise_code_snapshot="A1",
            exercise_name_snapshot="Back squat", position=1, success_score=80,
        )
        se1.set_logs.append(
            SetLog(kind="work", set_index=1, weight_kg=100.0, reps=8, completed=True)
        )
        se2 = SessionExercise(
            template_exercise_id=te2.id, exercise_code_snapshot="A2",
            exercise_name_snapshot="Curl EZ-bar debout", position=2, success_score=80,
        )
        se2.set_logs.append(
            SetLog(kind="work", set_index=1, weight_kg=20.0, reps=10, completed=True)
        )
        s.session_exercises.extend([se1, se2])
        db.add(s)
    db.commit()


def _uid(db):
    from app.models.user import User

    return db.query(User).first().id


def _render(client):
    r = client.get("/body/intelligence", follow_redirects=False)
    return r


# ───────── 1. route respects the flag ─────────


def test_route_404_when_flag_off(monkeypatch):
    """Build a dedicated flag-OFF client and assert the surface is 404."""
    import sys
    import tempfile
    from pathlib import Path

    monkeypatch.setenv("BODY_INTELLIGENCE_ENABLED", "0")
    tmp_dir = tempfile.mkdtemp(prefix="workout-test-bioff-")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{Path(tmp_dir) / 'off.db'}")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("APP_SECRET_KEY", "test-secret-key-for-signing")
    for mod_name in [m for m in list(sys.modules) if m == "app" or m.startswith("app.")]:
        sys.modules.pop(mod_name, None)
    from fastapi.testclient import TestClient

    from app import main as main_mod

    with TestClient(main_mod.app) as c:
        r = c.get("/body/intelligence", follow_redirects=False)
    assert r.status_code == 404


def test_route_renders_zone_cards_when_flag_on_with_data(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        _seed_zone_volume(db, _uid(db))
    r = _render(client)
    assert r.status_code == 200, r.text[:300]
    html = r.text
    assert "Lecture par zones" in html
    assert "zone-card" in html
    # two worked zones surface with FR labels
    assert "Quadriceps" in html or "quads" in html
    assert "Biceps" in html or "biceps" in html


# ───────── 2. zone cards content ─────────


def test_zone_cards_show_volume_confidence_and_non_medical(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        _seed_zone_volume(db, _uid(db))
    html = _render(client).text
    assert "séries" in html               # traceable volume, not a score
    assert "Confiance" in html            # confidence visible
    assert "Estimation non médicale." in html  # non-medical mention
    assert "% du volume" in html          # contribution (traceable share)


def _zone_section(html: str) -> str:
    """Extract only the Zone Intelligence section markup from the page."""
    import re

    m = re.search(
        r'<section[^>]*class="body-intelligence__zones".*?</section>',
        html,
        re.DOTALL,
    )
    assert m, "zone section not found in rendered page"
    return m.group(0)


def test_zone_cards_no_opaque_global_score_in_section(client):
    """The ZONE section must carry no A/B/C grade, no /100 note, no radar,
    no global score — only traceable per-zone figures."""
    from app.database import SessionLocal

    with SessionLocal() as db:
        _seed_zone_volume(db, _uid(db))
    section = _zone_section(_render(client).text).lower()
    assert "radar" not in section
    assert "/100" not in section
    assert "/ 100" not in section
    assert "global_grade" not in section
    assert "note globale" not in section
    assert "score global" not in section
    # a bare grade letter as a rating is never rendered in the section
    assert "grade" not in section


# ───────── 3. insufficient data → sober empty state ─────────


def test_zone_section_empty_state_when_no_volume(client):
    """No sessions → no zone cards, sober empty state, no invented figure."""
    html = _render(client).text
    assert "Données insuffisantes pour une lecture par zones" in html
    assert "zone-card" not in html  # no card, no invented number


# ───────── 4. non-goals (no JS / no new model / no Home change) ─────────


def test_no_js_added_to_bi_surface():
    tpl = TEMPLATE.read_text(encoding="utf-8")
    card = ZONE_CARD_PARTIAL.read_text(encoding="utf-8")
    for src in (tpl, card):
        assert "<script" not in src
        assert "onclick" not in src


def test_router_reuses_zonescore_no_new_score():
    src = ROUTER_FILE.read_text(encoding="utf-8")
    # reuses the existing ZoneScore / physique dashboard (read-only)
    assert "ZoneScore" in src
    assert "compute_physique_dashboard" in src
    # the router never surfaces the opaque score/grade: it must not read
    # `.score` or `.global_grade` off the dashboard into a card field.
    assert ".global_grade" not in src
    assert '"score"' not in src
    assert "'score'" not in src
    assert '"grade"' not in src
    assert "'grade'" not in src


def test_home_not_touched_by_zone_cards():
    """Sx_UI_06 / Sx_TRANSFORM_01 : Home must not gain a BI widget."""
    home = INDEX_TEMPLATE.read_text(encoding="utf-8")
    assert "zone-card" not in home
    assert "body_intelligence_zone_card" not in home


# ───────── 5. regression: /physique untouched, limits preserved ─────────


def test_progression_template_not_modified_for_zone_cards():
    """Progression must not reference the new zone-card partial."""
    prog = PROGRESS_TEMPLATE.read_text(encoding="utf-8")
    assert "body_intelligence_zone_card" not in prog
    assert "Lecture par zones" not in prog


def test_bi_non_medical_limits_still_present(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        _seed_zone_volume(db, _uid(db))
    html = _render(client).text
    # the existing non-medical limits block stays rendered
    assert "non déductible" in html or "clinique" in html


# ───────── 6. forbidden wording ─────────


def test_no_forbidden_wording_in_zone_surface():
    tpl = TEMPLATE.read_text(encoding="utf-8")
    card = ZONE_CARD_PARTIAL.read_text(encoding="utf-8")
    css = CSS_FILE.read_text(encoding="utf-8")
    blob = (tpl + card + css).lower()
    # "non médical" is allowed as a disclaimer; a bare medical CLAIM is not.
    for tok in ("diagnostic", "body fat", "morphotype", "attractivité", "pathologie"):
        assert tok not in blob, f"forbidden token {tok!r} in zone surface"


def test_zone_card_partial_exists():
    assert ZONE_CARD_PARTIAL.exists()
    src = ZONE_CARD_PARTIAL.read_text(encoding="utf-8")
    assert "zone-card" in src
    assert "Confiance" in src
