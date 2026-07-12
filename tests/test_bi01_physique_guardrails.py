"""Sb_BI_01.3 — Physique Surface Guardrails.

Encadre la surface live /physique (score A/B/C + radar) sans la renforcer ni
la casser : microcopy « lecture synthétique · score indicatif, non médical »,
et un lien vers /body/intelligence UNIQUEMENT quand le flag BI est actif (jamais
un lien mort 404).

Invariants (Sb_BI_01.next, Option B prudente) :
- score / grade / radar existants CONSERVÉS ;
- compute_physique_dashboard NON modifié (service partagé leaderboard/user_profile) ;
- lien BI conditionnel au flag ;
- pas de JS, pas de nouveau score, pas de nouveau radar, pas de suppression.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PHYSIQUE_TEMPLATE = ROOT / "app" / "templates" / "physique.html"
MUSCLE_SCORING = ROOT / "app" / "services" / "muscle_scoring.py"
LEADERBOARD_SVC = ROOT / "app" / "services" / "leaderboard.py"
USER_PROFILE_TPL = ROOT / "app" / "templates" / "user_profile.html"
INDEX_TPL = ROOT / "app" / "templates" / "index.html"
BI_TEMPLATE = ROOT / "app" / "templates" / "body_intelligence.html"


# ───────── seed (some volume so /physique renders a real dashboard) ─────────


def _seed(db, user_id):
    from app.models.catalog import RepTarget, TemplateExercise, WorkoutTemplate
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    t = WorkoutTemplate(slug=f"phys-{user_id}", name="Phys test", kind="strength")
    db.add(t)
    db.flush()
    te = TemplateExercise(
        template_id=t.id, position=1, code="A1", name="Back squat", set_scheme="3×6-10"
    )
    db.add(te)
    db.flush()
    db.add(RepTarget(template_exercise_id=te.id, set_index=1, min_reps=6, max_reps=10))
    db.flush()
    now = datetime.now(UTC)
    for k in range(4):
        s = WorkoutSession(
            user_id=user_id, template_id=t.id, template_slug_snapshot=t.slug,
            template_name_snapshot=t.name, started_at=now - timedelta(days=k * 3 + 1),
            ended_at=now - timedelta(days=k * 3 + 1), status="completed",
            global_state="good", concentration="high",
        )
        se = SessionExercise(
            template_exercise_id=te.id, exercise_code_snapshot="A1",
            exercise_name_snapshot="Back squat", position=1, success_score=80,
        )
        se.set_logs.append(
            SetLog(kind="work", set_index=1, weight_kg=100.0, reps=8, completed=True)
        )
        s.session_exercises.append(se)
        db.add(s)
    db.commit()


def _uid(db):
    from app.models.user import User

    return db.query(User).first().id


def _render_physique(client):
    r = client.get("/physique", follow_redirects=False)
    assert r.status_code == 200, r.text[:300]
    return r.text


# ───────── 1. /physique renders guardrails + keeps score/grade/radar ─────────


def test_physique_shows_guardrail_microcopy(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        _seed(db, _uid(db))
    html = _render_physique(client)
    assert "Lecture synthétique" in html
    assert "Score indicatif, non médical." in html
    assert "signaux d'entraînement et d'exposition" in html


def test_physique_keeps_score_grade_radar(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        _seed(db, _uid(db))
    html = _render_physique(client)
    # score + grade badge + radar still rendered (not masked, not moved out)
    assert "global-score" in html
    assert "grade-badge" in html
    assert "radar-wrap" in html


# ───────── 2. flag OFF (default) → no dead link ─────────


def test_no_bi_link_when_flag_off(client):
    """Default prod config: flag OFF → no link to the (404) BI surface."""
    from app.database import SessionLocal

    with SessionLocal() as db:
        _seed(db, _uid(db))
    html = _render_physique(client)
    assert "Voir la lecture par zones" not in html
    assert "/body/intelligence" not in html


# ───────── 3. flag ON → link present (real HTTP client, auth'd) ─────────


def test_bi_link_present_when_flag_on(monkeypatch):
    """A flag-ON app must render the guardrail link on /physique. Rebuilds an
    auth'd client exactly like the conftest `client` fixture (auto-login), so
    the assertion runs on a real authenticated request."""
    import sys
    import tempfile
    from pathlib import Path as P

    monkeypatch.setenv("BODY_INTELLIGENCE_ENABLED", "1")
    tmp = tempfile.mkdtemp(prefix="workout-test-physon-")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{P(tmp) / 'on.db'}")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("APP_SECRET_KEY", "test-secret-key-for-signing")
    for m in [x for x in list(sys.modules) if x == "app" or x.startswith("app.")]:
        sys.modules.pop(m, None)
    from fastapi.testclient import TestClient

    from app import main as main_mod

    with TestClient(main_mod.app) as c:
        # Replicate the conftest auto-login (username/password + POST /login).
        from app.database import SessionLocal
        from app.models.user import User
        from app.services.auth import hash_password

        with SessionLocal() as db:
            db.add(User(username="testuser", password_hash=hash_password("testpass")))
            db.commit()
            uid = db.query(User).first().id
            _seed(db, uid)
        login_r = c.post(
            "/login",
            data={"username": "testuser", "password": "testpass"},
            follow_redirects=False,
        )
        assert login_r.status_code == 303, f"login failed: {login_r.status_code}"
        r = c.get("/physique", follow_redirects=False)
        assert r.status_code == 200, r.text[:300]
        assert "Voir la lecture par zones" in r.text
        assert "/body/intelligence" in r.text


# ───────── 4. non-regression: shared service + consumers untouched ─────────


def test_muscle_scoring_not_modified_by_guardrails():
    """The guardrails must not touch compute_physique_dashboard."""
    src = MUSCLE_SCORING.read_text(encoding="utf-8")
    # sentinel: the guardrail marker must NOT appear in the service
    assert "physique-guardrails" not in src
    assert "Lecture synthétique" not in src


def test_leaderboard_and_userprofile_untouched():
    lb = LEADERBOARD_SVC.read_text(encoding="utf-8")
    up = USER_PROFILE_TPL.read_text(encoding="utf-8")
    for src in (lb, up):
        assert "physique-guardrails" not in src


def test_home_and_bi_templates_untouched_by_guardrails():
    home = INDEX_TPL.read_text(encoding="utf-8")
    bi = BI_TEMPLATE.read_text(encoding="utf-8")
    assert "physique-guardrails" not in home
    assert "physique-guardrails" not in bi


# ───────── 5. non-goals: no JS ─────────


def test_no_js_added_to_physique():
    src = PHYSIQUE_TEMPLATE.read_text(encoding="utf-8")
    assert "<script" not in src
    assert "onclick" not in src
    assert "addEventListener" not in src


# ───────── 6. forbidden wording ─────────


def test_no_forbidden_wording_in_physique():
    src = PHYSIQUE_TEMPLATE.read_text(encoding="utf-8").lower()
    for tok in (
        "diagnostic", "body fat", "morphotype", "attractivité",
        "pathologie", "score de santé", "vérité corporelle",
        "composition corporelle", "bilan médical",
    ):
        assert tok not in src, f"forbidden token {tok!r} in physique.html"
