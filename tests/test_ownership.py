"""Ownership tests: user-scoped data access + horizontal access control.

Two users: testuser (the default from conftest) and 'other'. The tests
verify that testuser cannot see or mutate other's sessions, and that
newly created sessions are owned by the current user.
"""
from __future__ import annotations

import re
from datetime import UTC

from tests.helpers import get_test_user_id


def _create_other_user_session() -> int:
    """Insert a session owned by a different user ('other')."""
    from datetime import datetime

    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    from app.models.user import User
    from app.services.auth import hash_password

    with SessionLocal() as db:
        other = db.execute(select(User).where(User.username == "other")).scalar_one_or_none()
        if other is None:
            other = User(username="other", password_hash=hash_password("otherpass"))
            db.add(other)
            db.flush()
        s = WorkoutSession(
            user_id=other.id,
            template_slug_snapshot="push-a",
            template_name_snapshot="Push A",
            started_at=datetime.now(UTC),
            status="completed",
        )
        db.add(s)
        db.commit()
        return s.id


def _start(client, slug="push-a") -> int:
    r = client.post("/sessions", data={"template_slug": slug}, follow_redirects=False)
    return int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))


# ---------------------------------------------------------------------------
# New sessions are owned by the current user
# ---------------------------------------------------------------------------


def test_new_session_is_owned_by_current_user(client):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    sid = _start(client, "push-a")
    uid = get_test_user_id()
    with SessionLocal() as db:
        s = db.get(WorkoutSession, sid)
        assert s.user_id == uid


# ---------------------------------------------------------------------------
# Horizontal access control: user cannot see/mutate other's sessions
# ---------------------------------------------------------------------------


def test_cannot_view_other_user_session_detail(client):
    other_sid = _create_other_user_session()
    r = client.get(f"/sessions/{other_sid}", follow_redirects=False)
    assert r.status_code == 404


def test_cannot_update_other_user_session(client):
    other_sid = _create_other_user_session()
    r = client.post(
        f"/sessions/{other_sid}",
        data={"concentration": "high"},
        follow_redirects=False,
    )
    assert r.status_code == 404


def test_cannot_delete_other_user_session(client):
    other_sid = _create_other_user_session()
    r = client.post(
        f"/admin/sessions/{other_sid}/delete",
        follow_redirects=False,
    )
    assert r.status_code == 404

    # Verify the session still exists
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    with SessionLocal() as db:
        assert db.get(WorkoutSession, other_sid) is not None


def test_cannot_exclude_other_user_session(client):
    other_sid = _create_other_user_session()
    r = client.post(
        f"/admin/sessions/{other_sid}/exclude",
        follow_redirects=False,
    )
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Scoped reads: other user's sessions are invisible
# ---------------------------------------------------------------------------


def test_history_does_not_show_other_user_sessions(client):
    _create_other_user_session()
    _start(client, "push-a")  # own session

    body = client.get("/history").text
    # Only own session should appear (Push A from _start), not the other's
    import re
    assert len(re.findall(r'session-card__name[^>]*>Push A', body)) == 1


def test_export_json_does_not_contain_other_user_data(client):
    _create_other_user_session()
    _start(client, "legs-a")

    payload = client.get("/export/sessions.json").json()
    # Only the Legs session (ours) should be exported
    slugs = [s["template_slug"] for s in payload["sessions"]]
    assert "legs-a" in slugs
    # The 'other' user's push-a should NOT be here
    for s in payload["sessions"]:
        assert s["template_slug"] != "push-a" or s.get("id") != _create_other_user_session()


def test_export_csv_is_scoped_to_current_user(client):
    _create_other_user_session()
    _start(client, "legs-a")

    csv_text = client.get("/export/sessions.csv").text
    lines = csv_text.strip().split("\n")
    # Header + at least one data row
    assert len(lines) >= 2
    # All data rows should reference 'legs' template (ours), not 'push-a' from other
    for line in lines[1:]:
        # The template_slug column is the 5th (index 4)
        assert "legs-a" in line


def test_progress_kpis_are_scoped(client):
    """`TRAIN1-A` / A4 — RÉORIENTÉ, ET RENFORCÉ.

    Ce test cherchait un `0` quelque part dans la page : un proxy faible de
    l'étanchéité — n'importe quel zéro le satisfaisait. Depuis A4, une page
    sans séance ne rend plus de compteur à zéro du tout, mais la propriété qui
    compte est intacte et se vérifie mieux : **rien de l'autre compte
    n'apparaît**, et la page dit qu'elle n'a rien.
    """
    _create_other_user_session()

    body = client.get("/progress").text
    assert 'class="empty-line"' in body
    assert "Push A" not in body
    assert "Aucune séance" in body


def test_admin_sessions_only_shows_own(client):
    _create_other_user_session()
    _start(client, "legs-a")

    body = client.get("/admin/sessions").text
    # Only one session card (our Legs), not the other's Push A
    assert body.count('admin-row__name">Legs A') == 1
    assert 'admin-row__name">Push A' not in body


def test_exercise_history_is_scoped(client):
    _create_other_user_session()
    body = client.get("/exercise-history/push-a/E1").text
    # We haven't done any push-a sessions, so the history is empty
    # even though 'other' has one
    assert "Aucune séance" in body


# ---------------------------------------------------------------------------
# Resume banner is scoped
# ---------------------------------------------------------------------------


def test_resume_banner_only_shows_own_sessions(client):
    # Other user has an in-progress session
    from datetime import datetime

    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    from app.models.user import User
    from app.services.auth import hash_password

    with SessionLocal() as db:
        other = db.execute(select(User).where(User.username == "other")).scalar_one_or_none()
        if other is None:
            other = User(username="other", password_hash=hash_password("otherpass"))
            db.add(other)
            db.flush()
        s = WorkoutSession(
            user_id=other.id,
            template_slug_snapshot="pull-a",
            template_name_snapshot="Pull A",
            started_at=datetime.now(UTC),
            status="in_progress",
        )
        db.add(s)
        db.commit()

    # Our home should NOT show a resume tile for the other user's session
    body = client.get("/").text
    assert "Reprendre" not in body
    assert "Pull A" not in body
