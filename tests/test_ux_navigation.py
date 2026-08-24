"""Sb_27.6 — UX simplification pass tests.

Verifies the nav contract after OQ-3 decision (deprecation of /dashboard):

* /dashboard redirects 303 to /
* / remains 200 (Home coaching)
* /progress remains 200 (analytique)
* Top navigation surfaces the primary entries (Accueil, Progression,
  Historique) — and a CTA toward starting a session is reachable
* Top navigation does NOT promote /dashboard anymore (no `href="/dashboard"`
  link, no "Synthèse" label)

These tests are HTML-content checks (string `in body`), kept robust by
referencing stable href patterns rather than fragile DOM structure.
"""
from __future__ import annotations


def test_dashboard_redirects_to_progression(client):
    """`TRAIN1-C` — la cible passe de `/` à `/progress` : qui tape `/dashboard`
    cherche de l'analytique, et l'analytique vit sur Progression."""
    r = client.get("/dashboard", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/progress"


def test_home_still_200(client):
    r = client.get("/", follow_redirects=False)
    assert r.status_code == 200


def test_progress_still_200(client):
    r = client.get("/progress", follow_redirects=False)
    assert r.status_code == 200


def test_navigation_has_primary_entries(client):
    """Top nav surfaces Accueil + Progression + Historique.

    `url_for(...)` renders absolute URLs (`http://testserver/...`) in
    TestClient context, so we check for the path substring rather than
    `href="/x"` literal.
    """
    r = client.get("/")
    assert r.status_code == 200
    body = r.text
    # Accueil label + home URL ending
    assert "Accueil" in body
    assert "testserver/\"" in body or 'href="/"' in body
    # Progression label + /progress URL
    assert "Progression" in body
    assert "/progress" in body
    # Historique label + /history URL
    assert "Historique" in body
    assert "/history" in body


def test_navigation_reaches_launcher(client):
    """A user must be able to start a session from Home in 1-2 clicks.

    The Home tile already exposes the launcher CTA (the `tile--cta-main`
    block); we assert the launcher URL is reachable from the rendered
    page.
    """
    r = client.get("/")
    assert r.status_code == 200
    # Substring match — handles both relative and absolute `url_for` outputs.
    assert "/launcher" in r.text


def test_navigation_does_not_promote_dashboard(client):
    """The deprecated /dashboard surface must NOT appear as a primary nav
    entry anymore. We allow incidental references in body text (e.g.
    historical reports), but the topbar must not link to /dashboard."""
    r = client.get("/")
    assert r.status_code == 200
    body = r.text
    # Hard constraint: no nav link to /dashboard. The historical
    # "Synthèse" label is also removed since it pointed there.
    assert 'topbar__link" href="/dashboard"' not in body
    assert "Synthèse</a>" not in body


def test_session_done_does_not_promote_dashboard(client):
    """Same OQ-3 contract on the Session Review page."""
    from datetime import UTC, datetime, timedelta

    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = WorkoutSession(
            user_id=user.id,
            template_slug_snapshot="push-a",
            template_name_snapshot="Push A",
            started_at=datetime.now(UTC) - timedelta(hours=1),
            ended_at=datetime.now(UTC),
            status="completed",
            scoring_version=2,
        )
        se = SessionExercise(
            exercise_code_snapshot="B",
            exercise_name_snapshot="Bench",
            position=1,
            implicit_label="intense",
        )
        se.set_logs.append(SetLog(kind="work", set_index=1, weight_kg=80, reps=8, completed=True))
        s.session_exercises.append(se)
        db.add(s)
        db.commit()
        session_id = s.id

    r = client.get(f"/sessions/{session_id}/done")
    assert r.status_code == 200
    body = r.text
    assert 'topbar__link" href="/dashboard"' not in body
    assert "Synthèse</a>" not in body
