"""Sb_31.3 — Tests intégration bloc Snapshot Body Intelligence
dans /coach-report.

Garde-fous (verbatim user) :
- /coach-report retourne 200 avec body snapshot
- Le bloc est visible
- Le lien vers /body/intelligence est visible
- Max 3 bullets affichées
- Max 3 priorités affichées
- insufficient_data rendu proprement
- partial_data rendu proprement
- Aucun wording interdit dans le HTML rendu
- Le template ne contient pas de seuils métier
- app/services/coach_report.py NON modifié + ne référence pas
  body_intelligence
- Aucune migration ajoutée
- Aucun JS ajouté
- Aucune API JSON créée
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
PARTIAL = ROOT / "app" / "templates" / "_partials" / "coach_body_snapshot.html"
COACH_TEMPLATE = ROOT / "app" / "templates" / "coach_report.html"
COACH_ROUTER = ROOT / "app" / "routers" / "coach_report.py"
COACH_SERVICE = ROOT / "app" / "services" / "coach_report.py"
COMPOSER = ROOT / "app" / "services" / "body_intelligence.py"
INPUTS_LAYER = ROOT / "app" / "services" / "body_intelligence_inputs.py"


# ───────── seed helpers ─────────


def _seed_solid(db, user_id):
    from app.models.catalog import RepTarget, TemplateExercise, WorkoutTemplate
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    t = WorkoutTemplate(
        slug=f"coach-bi-{user_id}",
        name="Coach BI snapshot",
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
            SetLog(kind="work", set_index=1, weight_kg=100.0, reps=8, completed=True)
        )
        s.session_exercises.append(se)
        db.add(s)
    db.commit()


# ───────── structure ─────────


def test_partial_exists():
    assert PARTIAL.exists()
    body = PARTIAL.read_text(encoding="utf-8")
    assert "body-snapshot" in body
    assert "Snapshot Body Intelligence" in body


def test_partial_uses_url_for_body_intelligence():
    body = PARTIAL.read_text(encoding="utf-8")
    assert "url_for('body_intelligence')" in body, (
        "partial must link to /body/intelligence via url_for"
    )


def test_coach_report_template_includes_partial():
    body = COACH_TEMPLATE.read_text(encoding="utf-8")
    assert '_partials/coach_body_snapshot.html' in body
    # Position : après section 1 (identité), avant section 2 (volume)
    pos_partial = body.index("coach_body_snapshot.html")
    pos_section_2 = body.index("2. Volume et fréquence")
    assert pos_partial < pos_section_2, (
        "snapshot partial must be included BEFORE section 2"
    )


def test_router_imports_pipeline_canonical():
    src = COACH_ROUTER.read_text(encoding="utf-8")
    assert "compute_body_intelligence" in src
    assert "build_body_intelligence_input" in src
    assert "body_snapshot" in src


# ───────── route smoke ─────────


def test_coach_report_returns_200_no_data(client):
    r = client.get("/coach-report", follow_redirects=False)
    assert r.status_code == 200


def test_coach_report_returns_200_with_solid_data(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        _seed_solid(db, user.id)

    r = client.get("/coach-report", follow_redirects=False)
    assert r.status_code == 200


# ───────── HTML rendu ─────────


def test_rendered_html_contains_body_snapshot_section(client):
    r = client.get("/coach-report", follow_redirects=False)
    body = r.text
    assert "coach-block--body-snapshot" in body
    assert "Snapshot Body Intelligence" in body
    assert 'id="coach-body-snapshot-title"' in body


def test_rendered_html_carries_status_data_attribute(client):
    r = client.get("/coach-report", follow_redirects=False)
    body = r.text
    assert re.search(
        r'data-body-snapshot-status="(ok|partial_data|insufficient_data)"',
        body,
    )


def test_rendered_html_link_to_body_intelligence_visible(client):
    r = client.get("/coach-report", follow_redirects=False)
    body = r.text
    assert "/body/intelligence" in body
    assert "Voir le détail" in body


def test_rendered_html_caps_bullets_at_3(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        _seed_solid(db, user.id)

    body = client.get("/coach-report").text
    # Scope au bloc snapshot
    m = re.search(
        r'<section[^>]*coach-block--body-snapshot[^>]*>(.*?)</section>',
        body,
        re.DOTALL,
    )
    assert m is not None
    block = m.group(1)
    n_bullets = block.count('class="body-snapshot__bullet"')
    assert n_bullets <= 3, f"expected ≤ 3 bullets in snapshot, got {n_bullets}"


def test_rendered_html_caps_priorities_at_3(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        _seed_solid(db, user.id)

    body = client.get("/coach-report").text
    m = re.search(
        r'<section[^>]*coach-block--body-snapshot[^>]*>(.*?)</section>',
        body,
        re.DOTALL,
    )
    assert m is not None
    block = m.group(1)
    # Une <li> de priorité ouvre par class="body-snapshot__priority ..."
    n_prio = len(
        re.findall(
            r'<li\b[^>]*class="body-snapshot__priority\b',
            block,
        )
    )
    assert n_prio <= 3, f"expected ≤ 3 priorities in snapshot, got {n_prio}"


def test_insufficient_data_renders_cleanly(client):
    """Avec aucune donnée seed → status=insufficient_data → tag
    "Données partielles" + note "À confirmer"."""
    r = client.get("/coach-report", follow_redirects=False)
    assert r.status_code == 200
    body = r.text
    assert 'data-body-snapshot-status="insufficient_data"' in body
    assert "Données partielles" in body or "Partiel" in body
    assert "À confirmer avec plus de séances" in body


def test_partial_data_renders_cleanly(client):
    """Avec quelques séances mais blocs incomplets (peu de zones,
    pas de body metrics, etc.) → status=partial_data."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        _seed_solid(db, user.id)

    body = client.get("/coach-report").text
    # Le seed génère 4 sessions → sessions_30d >= 3 → status ≠ insufficient.
    # Avec ce seed limité, status = partial_data (blocs quality/zones
    # peuvent être unavailable) ou ok.
    assert (
        'data-body-snapshot-status="partial_data"' in body
        or 'data-body-snapshot-status="ok"' in body
    )


# ───────── wording ─────────


def test_no_forbidden_wording_in_snapshot_block(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        _seed_solid(db, user.id)

    body = client.get("/coach-report").text.lower()
    m = re.search(
        r'<section[^>]*coach-block--body-snapshot[^>]*>(.*?)</section>',
        body,
        re.DOTALL,
    )
    assert m is not None
    block = m.group(1)
    forbidden = (
        "ton physique est",
        "tu es gras",
        "tu es sec",
        "ton taux de gras",
        "diagnostic",
        "problème médical",
        "posture réelle",
        "symétrie corporelle réelle",
        "tu dois absolument",
        "il faut absolument",
        "obligatoire",
    )
    for tok in forbidden:
        assert tok not in block, (
            f"forbidden wording {tok!r} in /coach-report body snapshot"
        )


# ───────── garde-fous structurels ─────────


def test_partial_does_not_reference_engine_constants():
    src = PARTIAL.read_text(encoding="utf-8")
    for forbidden in (
        "MIN_SESSIONS_OK",
        "MIN_SESSIONS_CONSISTENCY_30D",
        "LOW_QUALITY_THRESHOLD",
        "LOW_CONFIDENCE_THRESHOLD",
        "IMBALANCE_LOW_RATIO",
        "IMBALANCE_HIGH_RATIO",
        "MAX_PRIORITIES",
        "compute_body_intelligence",
    ):
        assert forbidden not in src, (
            f"partial should not reference engine constant {forbidden!r}"
        )


def test_coach_report_service_unchanged_no_body_imports():
    """Garde stricte : ``app/services/coach_report.py`` ne doit pas
    importer le composer ni la couche I/O body_intelligence."""
    src = COACH_SERVICE.read_text(encoding="utf-8")
    assert "body_intelligence" not in src, (
        "coach_report.py service must remain untouched by Sb_31.3"
    )


def test_composer_unchanged():
    """``body_intelligence.py`` reste intact (composer pur Sb_31.1)."""
    src = COMPOSER.read_text(encoding="utf-8")
    # On vérifie la version constante (sentinelle stable)
    assert "BODY_INTELLIGENCE_VERSION = 1" in src


def test_inputs_layer_unchanged_by_sb_31_3():
    """Sb_31.3 ne doit pas avoir modifié la signature publique de
    ``build_body_intelligence_input``."""
    src = INPUTS_LAYER.read_text(encoding="utf-8")
    assert "def build_body_intelligence_input(" in src
    assert "db: Session, user: User" in src


# ───────── no migration / no JS / no JSON ─────────


def test_no_new_js_file_introduced():
    js_dir = ROOT / "app" / "static" / "js"
    existing = {p.name for p in js_dir.glob("*.js")}
    assert existing <= {"preview.js", "session_focus.js"}, (
        f"unexpected JS files: {existing}"
    )


def test_no_migration_mentions_body_snapshot():
    versions = ROOT / "migrations" / "versions"
    for p in versions.glob("*.py"):
        src = p.read_text(encoding="utf-8")
        for token in ("body_snapshot", "coach_body_snapshot"):
            assert token not in src, (
                f"unexpected migration mentioning {token}: {p.name}"
            )


def test_no_json_api_for_coach_body_snapshot(client):
    """Sb_31.3 ne doit pas créer d'endpoint JSON sous /coach-report."""
    r = client.get("/coach-report.json", follow_redirects=False)
    assert r.status_code in (404, 405)
    r = client.get("/coach-report/body-snapshot.json", follow_redirects=False)
    assert r.status_code in (404, 405)


# ───────── non-régression /body/intelligence et engine ─────────


def test_body_intelligence_route_still_200(client):
    """La route /body/intelligence livrée Sb_31.2 doit rester opérationnelle."""
    r = client.get("/body/intelligence", follow_redirects=False)
    assert r.status_code == 200


def test_body_intelligence_unit_tests_unaffected():
    """Garde marqueur : le composer expose toujours
    ``BODY_INTELLIGENCE_VERSION`` (sentinelle Sb_31.1)."""
    from app.services.body_intelligence import (
        BODY_INTELLIGENCE_VERSION,
        compute_body_intelligence,
    )

    assert BODY_INTELLIGENCE_VERSION == 1
    assert callable(compute_body_intelligence)
