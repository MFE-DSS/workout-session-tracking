"""Sb_31.2 — Tests route GET /body/intelligence + rendu template.

Conflit route /body : le track parallèle Body Manual Profile (PR #15)
occupe déjà /body via app/routers/body.py. Body Intelligence v2
utilise donc /body/intelligence comme route canonique.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _enable_body_intelligence_v2(monkeypatch):
    """Sb_31.X — Body Intelligence v2 is now flag-gated (default OFF).
    These tests exercise the ON behavior, so enable the flag before the
    `client` fixture builds the app."""
    monkeypatch.setenv("BODY_INTELLIGENCE_ENABLED", "1")


ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "app" / "templates" / "body_intelligence.html"
BLOCK_PARTIAL = ROOT / "app" / "templates" / "_partials" / "body_intelligence_block.html"
PRIORITY_PARTIAL = ROOT / "app" / "templates" / "_partials" / "body_intelligence_priority.html"
ROUTER_FILE = ROOT / "app" / "routers" / "body_intelligence.py"
CSS_FILE = ROOT / "app" / "static" / "css" / "body_intelligence.css"


# ───────── seed helpers ─────────


def _seed_solid_30d(db, user_id):
    """Seed 4 sessions completed récentes avec un peu de signal."""
    from app.models.catalog import (
        RepTarget,
        TemplateExercise,
        WorkoutTemplate,
    )
    from app.models.session import (
        SessionExercise,
        SetLog,
        WorkoutSession,
    )

    t = WorkoutTemplate(
        slug=f"route-{user_id}",
        name="Route test",
        kind="strength",
    )
    db.add(t)
    db.flush()
    te = TemplateExercise(
        template_id=t.id,
        position=1,
        code="A1",
        name="Back squat",
        set_scheme="3×6-10",
    )
    db.add(te)
    db.flush()
    db.add(
        RepTarget(template_exercise_id=te.id, set_index=1, min_reps=6, max_reps=10)
    )
    db.flush()
    now = datetime.now(UTC)
    for k in range(4):
        s = WorkoutSession(
            user_id=user_id,
            template_id=t.id,
            template_slug_snapshot=t.slug,
            template_name_snapshot=t.name,
            started_at=now - timedelta(days=k * 3 + 1),
            ended_at=now - timedelta(days=k * 3 + 1),
            status="completed",
            global_state="good",
            concentration="high",
        )
        se = SessionExercise(
            template_exercise_id=te.id,
            exercise_code_snapshot="A1",
            exercise_name_snapshot="Back squat",
            position=1,
            success_score=80,
        )
        se.set_logs.append(
            SetLog(
                kind="work",
                set_index=1,
                weight_kg=100.0,
                reps=8,
                completed=True,
            )
        )
        s.session_exercises.append(se)
        db.add(s)
    db.commit()


# ───────── existence + structure ─────────


def test_template_exists():
    assert TEMPLATE.exists()
    body = TEMPLATE.read_text(encoding="utf-8")
    assert "body-intelligence" in body
    assert "snapshot.engine_version" in body


def test_block_partial_exists_and_renders_classification():
    assert BLOCK_PARTIAL.exists()
    src = BLOCK_PARTIAL.read_text(encoding="utf-8")
    # Labels Mesuré / Dérivé / Inféré / Hors de portée
    assert "Mesuré" in src
    assert "Dérivé" in src
    assert "Inféré" in src
    assert "Hors de portée" in src


def test_priority_partial_exists():
    assert PRIORITY_PARTIAL.exists()
    src = PRIORITY_PARTIAL.read_text(encoding="utf-8")
    assert "data-priority-key" in src
    assert "<details" in src  # no-JS friendly


def test_router_exists_and_uses_composer():
    src = ROUTER_FILE.read_text(encoding="utf-8")
    assert "compute_body_intelligence" in src
    assert "build_body_intelligence_input" in src
    assert "/body/intelligence" in src


def test_css_exists_and_has_classification_cues():
    src = CSS_FILE.read_text(encoding="utf-8")
    # Non-color cues sur les 4 niveaux de classification
    for c in (
        ".bi-block__classification--measured",
        ".bi-block__classification--derived",
        ".bi-block__classification--inferred",
        ".bi-block__classification--not_deductible",
    ):
        assert c in src, f"missing CSS classification cue {c}"
    # Status global cues
    assert ".body-intelligence--ok" in src
    assert ".body-intelligence--partial_data" in src
    assert ".body-intelligence--insufficient_data" in src


# ───────── route smoke ─────────


def test_route_returns_200_with_no_data(client):
    r = client.get("/body/intelligence", follow_redirects=False)
    assert r.status_code == 200, r.text[:400]


def test_route_returns_200_with_solid_data(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        _seed_solid_30d(db, user.id)

    r = client.get("/body/intelligence", follow_redirects=False)
    assert r.status_code == 200


def test_route_does_not_create_json_api(client):
    """Sb_31.2 ne doit pas exposer d'endpoint JSON public sous
    /body/intelligence."""
    r = client.get("/body/intelligence.json", follow_redirects=False)
    assert r.status_code in (404, 405)


# ───────── HTML rendu ─────────


def test_rendered_html_contains_headline(client):
    r = client.get("/body/intelligence", follow_redirects=False)
    body = r.text
    assert "body-intelligence__headline" in body
    assert "id=\"body-intelligence-headline\"" in body


def test_rendered_html_marks_status(client):
    """Status global rendu en data attribute + CSS modifier."""
    r = client.get("/body/intelligence", follow_redirects=False)
    body = r.text
    assert re.search(r'data-status="(ok|partial_data|insufficient_data)"', body)


def test_rendered_html_shows_seven_blocks(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        _seed_solid_30d(db, user.id)

    body = client.get("/body/intelligence").text
    for key in (
        "training_consistency",
        "body_metrics",
        "muscle_zone_balance",
        "push_pull_legs_balance",
        "quality_and_confidence",
        "implicit_signal_summary",
        "unavailable_or_limits",
    ):
        assert f'data-block-key="{key}"' in body, f"block {key} missing in HTML"


def test_rendered_html_shows_classification_labels(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        _seed_solid_30d(db, user.id)

    body = client.get("/body/intelligence").text
    for label in ("Mesuré", "Dérivé", "Inféré", "Hors de portée"):
        assert label in body, f"classification label {label!r} not rendered"


def test_rendered_html_caps_priorities_at_3(client):
    """Le composeur garantit MAX_PRIORITIES=3 ; on vérifie côté HTML
    que jamais > 3 articles bi-priority n'apparaissent."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        _seed_solid_30d(db, user.id)

    body = client.get("/body/intelligence").text
    # Compte les <article ...> de priorité uniquement (le BEM ``bi-priority__*``
    # crée des sous-éléments qu'il ne faut pas confondre).
    n_articles = len(
        re.findall(r'<article\b[^>]*class="bi-priority\b', body)
    )
    assert n_articles <= 3, f"too many priority articles: {n_articles}"


def test_rendered_html_shows_limits_block_always(client):
    body = client.get("/body/intelligence").text
    # Bloc limits always-on même sans data
    assert 'data-block-key="unavailable_or_limits"' in body
    # Mentions explicites
    assert "Composition corporelle non déductible" in body or "composition corporelle" in body.lower()


def test_rendered_html_has_no_forbidden_wording(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        _seed_solid_30d(db, user.id)

    body = client.get("/body/intelligence").text.lower()
    # Restreindre au bloc body intelligence pour éviter faux positifs
    m = re.search(
        r'<section\s+class="body-intelligence[^"]*".*?</section>',
        body,
        re.DOTALL,
    )
    assert m is not None
    block = m.group(0)
    forbidden = (
        "tu es gras",
        "tu es sec",
        "ton taux de gras",
        "ton physique est",
        "diagnostic",
        "problème médical",
        "posture réelle",
        "symétrie corporelle réelle",
        "tu dois",
        "il faut absolument",
        "obligatoire",
    )
    for tok in forbidden:
        assert tok not in block, f"forbidden wording {tok!r} in /body/intelligence"


def test_rendered_html_loads_dedicated_css(client):
    body = client.get("/body/intelligence").text
    assert "css/body_intelligence.css" in body


# ───────── garde-fous structurels ─────────


def test_template_has_no_business_loops_or_thresholds():
    """Le template ne doit pas dupliquer les seuils du moteur ni
    réimplémenter d'arbre de décision."""
    src = TEMPLATE.read_text(encoding="utf-8")
    block_src = BLOCK_PARTIAL.read_text(encoding="utf-8")
    priority_src = PRIORITY_PARTIAL.read_text(encoding="utf-8")
    all_src = src + block_src + priority_src
    # Pas de constante seuil dupliquée
    for forbidden_constant in (
        "MIN_SESSIONS_OK",
        "MIN_SESSIONS_CONSISTENCY_30D",
        "LOW_QUALITY_THRESHOLD",
        "LOW_CONFIDENCE_THRESHOLD",
        "IMBALANCE_LOW_RATIO",
        "IMBALANCE_HIGH_RATIO",
        "MAX_PRIORITIES",
        "compute_body_intelligence",
    ):
        assert forbidden_constant not in all_src, (
            f"template should not reference engine constant {forbidden_constant!r}"
        )


def test_router_does_not_recompute_business():
    """Le router orchestre uniquement input → engine → template."""
    src = ROUTER_FILE.read_text(encoding="utf-8")
    # Aucune importation de seuils ; aucune référence aux helpers privés
    # du composeur.
    for forbidden in (
        "MIN_SESSIONS_OK",
        "MIN_SESSIONS_CONSISTENCY_30D",
        "_priorities_for",
        "_block_training_consistency",
        "_bmi",
        "_push_pull_ratio",
    ):
        assert forbidden not in src, (
            f"router should not import engine internal {forbidden!r}"
        )


# ───────── no migration / no JS ─────────


def test_no_new_js_file_introduced():
    """Sb_31.2 ne doit introduire AUCUN nouveau fichier JS."""
    js_dir = ROOT / "app" / "static" / "js"
    existing = {p.name for p in js_dir.glob("*.js")}
    # preview.js + session_focus.js sont les seuls autorisés (héritage Sx_29).
    assert existing <= {"preview.js", "session_focus.js"}, (
        f"unexpected JS files: {existing}"
    )


def test_no_new_migration_introduced():
    """Sb_31.2 ne doit ajouter aucune migration Alembic."""
    versions = ROOT / "migrations" / "versions"
    # Garde structurelle : aucun fichier 2026-06-28+ ne doit apparaître
    # avant la prochaine spec autorisée. (Test souple : on vérifie juste
    # qu'aucune migration ne mentionne body_intelligence.)
    for p in versions.glob("*.py"):
        src = p.read_text(encoding="utf-8")
        assert "body_intelligence" not in src, (
            f"unexpected migration mentioning body_intelligence: {p.name}"
        )
