"""Sb_BI_01.2 — Zone Drill Detail.

Inline no-JS drill (<details> SSR natif) inside each Zone Intelligence Card.
Explains a card by surfacing the zone's top exercises (names only, reused
from ZoneScore.top_exercises). No new route, no JS, no score, no radar, no
per-exercise volume (heavy recompute deferred). Flag stays OFF in prod.

Rule (Sx_BI_01 / Sx_TRANSFORM_01): deepen traceability, not apparent
intelligence. The drill explains the card; it never becomes a dashboard.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
ZONE_CARD_PARTIAL = ROOT / "app" / "templates" / "_partials" / "body_intelligence_zone_card.html"
ROUTER_FILE = ROOT / "app" / "routers" / "body_intelligence.py"
CSS_FILE = ROOT / "app" / "static" / "css" / "body_intelligence.css"
TEMPLATE = ROOT / "app" / "templates" / "body_intelligence.html"
# `TRAIN1-C` — `physique.html` a été supprimé avec sa surface. Ces gardes
# de confinement visent la SURFACE VOISINE : c'est Progression qui porte
# désormais l'instrument anatomique, donc c'est elle qu'il faut vérifier.
PROGRESS_TEMPLATE = ROOT / "app" / "templates" / "progress.html"
INDEX_TEMPLATE = ROOT / "app" / "templates" / "index.html"


@pytest.fixture(autouse=True)
def _enable_bi(monkeypatch):
    monkeypatch.setenv("BODY_INTELLIGENCE_ENABLED", "1")


# ───────── seed (two zones, distinct exercises → non-empty top lists) ─────────


def _seed(db, user_id):
    from app.models.catalog import RepTarget, TemplateExercise, WorkoutTemplate
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    t = WorkoutTemplate(slug=f"drill-{user_id}", name="Drill test", kind="strength")
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
    return client.get("/body/intelligence", follow_redirects=False)


def _zone_section(html: str) -> str:
    import re

    m = re.search(
        r'<section[^>]*class="body-intelligence__zones".*?</section>',
        html,
        re.DOTALL,
    )
    assert m, "zone section not found"
    return m.group(0)


# ───────── 1. flag ─────────


def test_route_404_when_flag_off(monkeypatch):
    import sys
    import tempfile
    from pathlib import Path as P

    monkeypatch.setenv("BODY_INTELLIGENCE_ENABLED", "0")
    tmp = tempfile.mkdtemp(prefix="workout-test-drilloff-")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{P(tmp) / 'off.db'}")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("APP_SECRET_KEY", "test-secret-key-for-signing")
    for m in [x for x in list(sys.modules) if x == "app" or x.startswith("app.")]:
        sys.modules.pop(m, None)
    from fastapi.testclient import TestClient

    from app import main as main_mod

    with TestClient(main_mod.app) as c:
        r = c.get("/body/intelligence", follow_redirects=False)
    assert r.status_code == 404


def test_drill_rendered_when_flag_on(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        _seed(db, _uid(db))
    r = _render(client)
    assert r.status_code == 200, r.text[:300]
    assert "<details" in r.text
    assert "Détail zone" in r.text


# ───────── 2. drill content ─────────


def test_drill_shows_top_exercises_inline_no_js(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        _seed(db, _uid(db))
    section = _zone_section(_render(client).text)
    # a <details> per active zone card
    assert section.count("<details") >= 1
    assert "zone-card__drill" in section
    assert "Exercices principaux" in section
    # the actual seeded exercises surface in the drill
    assert "Back squat" in section or "Curl EZ-bar debout" in section
    # no JS anywhere in the section
    assert "<script" not in section
    assert "onclick" not in section
    assert "addEventListener" not in section


def test_drill_summary_is_native_details_element(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        _seed(db, _uid(db))
    section = _zone_section(_render(client).text)
    # native disclosure widget: <summary> inside <details>, no JS toggle
    assert "<summary" in section


# ───────── 3. non-score / non-radar ─────────


def test_drill_section_has_no_opaque_score_or_radar(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        _seed(db, _uid(db))
    section = _zone_section(_render(client).text).lower()
    assert "/100" not in section
    assert "/ 100" not in section
    assert "radar" not in section
    assert "score global" not in section
    assert "note globale" not in section
    assert "grade" not in section


# ───────── 4. empty state ─────────


def test_drill_empty_state_partial_wording():
    """The partial carries the sober empty-state string for zones with no top
    exercises."""
    src = ZONE_CARD_PARTIAL.read_text(encoding="utf-8")
    assert "Détail insuffisant" in src
    assert "<details" in src
    assert "<summary" in src


# ───────── 5. architecture / non-goals ─────────


def test_no_js_added_to_partial_or_template():
    for f in (ZONE_CARD_PARTIAL, TEMPLATE):
        src = f.read_text(encoding="utf-8")
        assert "<script" not in src
        assert "onclick" not in src
        assert "addEventListener" not in src


def test_router_still_reuses_top_exercises_no_new_score():
    src = ROUTER_FILE.read_text(encoding="utf-8")
    assert "top_exercises" in src
    # still no opaque score/grade surfaced by the router
    assert ".global_grade" not in src
    assert '"score"' not in src
    assert "'score'" not in src


def test_progression_and_home_untouched_by_drill():
    prog = PROGRESS_TEMPLATE.read_text(encoding="utf-8")
    home = INDEX_TEMPLATE.read_text(encoding="utf-8")
    assert "zone-card__drill" not in prog
    assert "zone-card__drill" not in home
    assert "zone-card" not in home


# ───────── 6. forbidden wording ─────────


def test_no_forbidden_wording_in_drill():
    src = (
        ZONE_CARD_PARTIAL.read_text(encoding="utf-8")
        + CSS_FILE.read_text(encoding="utf-8")
    ).lower()
    for tok in (
        "diagnostic", "body fat", "morphotype", "attractivité",
        "pathologie", "score physique", "note corporelle",
    ):
        assert tok not in src, f"forbidden token {tok!r} in drill surface"
