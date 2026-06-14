"""Sb_26.7 — cross-user data isolation tests.

Creates two real users (`user_a`, `user_b`) and asserts that user_b can
NEVER read, mutate, or otherwise affect user_a's owned resources.

Scope:
* Workout sessions (sessions_id-based routes + admin routes)
* Exports (json/csv must scope to caller)
* Coach Report (per-user only)
* History / progress / dashboard (must filter by caller)
* Leaderboard / public user profile (semi-public per spec — explicitly
  documented in docs/AUTH_SCOPE_MATRIX.md and tested as such)

The default `client` fixture from conftest creates 1 testuser logged
in. For these tests we need 2 users + a way to switch. We build a
dedicated `two_user_client` fixture that:
  * creates user_a + user_b in the DB
  * seeds at least one private session for user_a
  * provides helpers to switch between user contexts (logout/login)
"""
from __future__ import annotations

from datetime import UTC, datetime

import pytest

_PRIVATE_NOTE = "USER-A-PRIVATE-NOTE-DO-NOT-LEAK"
_EXERCISE_NAME = "UserAOnlyExerciseFingerprint"


@pytest.fixture()
def two_user_client(client):
    """Build on top of the standard `client` fixture: replace the default
    testuser session with two distinct users + a private session for
    user_a containing fingerprint strings we can grep for.

    Returns a dict:
      {
        "client": TestClient,
        "user_a_id": int,
        "user_b_id": int,
        "session_id": int,        # owned by user_a
        "login": fn(username, password) -> None,
      }
    """
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession
    from app.models.user import User
    from app.services.auth import hash_password

    with SessionLocal() as db:
        user_a = User(username="user_a", password_hash=hash_password("pwd_a_str"))
        user_b = User(username="user_b", password_hash=hash_password("pwd_b_str"))
        db.add_all([user_a, user_b])
        db.commit()
        db.refresh(user_a)
        db.refresh(user_b)
        a_id, b_id = user_a.id, user_b.id

        s = WorkoutSession(
            user_id=a_id,
            template_slug_snapshot="push-a",
            template_name_snapshot="Push A",
            started_at=datetime.now(UTC),
            status="completed",
            free_note=_PRIVATE_NOTE,
        )
        se = SessionExercise(
            exercise_code_snapshot="E1",
            exercise_name_snapshot=_EXERCISE_NAME,
            position=1,
            success_score=80,
            free_note="user_a exercise secret",
        )
        se.set_logs.append(
            SetLog(kind="work", set_index=1, weight_kg=60.0, reps=10, completed=True)
        )
        s.session_exercises.append(se)
        db.add(s)
        db.commit()
        db.refresh(s)
        session_id = s.id

    def login(username: str, password: str) -> None:
        # Clear cookies first so we start fresh.
        client.cookies.clear()
        r = client.post(
            "/login",
            data={"username": username, "password": password},
            follow_redirects=False,
        )
        assert r.status_code == 303, f"login failed for {username}: {r.status_code}"

    return {
        "client": client,
        "user_a_id": a_id,
        "user_b_id": b_id,
        "session_id": session_id,
        "login": login,
    }


# ───────── isolation tests ─────────


def test_user_b_cannot_read_user_a_session_detail(two_user_client):
    """GET /sessions/{id} for user_a's session, logged in as user_b → 404."""
    c = two_user_client["client"]
    two_user_client["login"]("user_b", "pwd_b_str")
    r = c.get(
        f"/sessions/{two_user_client['session_id']}",
        follow_redirects=False,
    )
    assert r.status_code == 404, (
        f"user_b read user_a's session detail: {r.status_code} {r.text[:200]}"
    )


def test_user_b_cannot_post_to_user_a_session(two_user_client):
    """POST /sessions/{id} to mark user_a's session, logged in as user_b → 404."""
    c = two_user_client["client"]
    two_user_client["login"]("user_b", "pwd_b_str")
    r = c.post(
        f"/sessions/{two_user_client['session_id']}",
        data={"action": "complete"},
        follow_redirects=False,
    )
    assert r.status_code == 404


def test_user_b_cannot_delete_user_a_session_via_admin(two_user_client):
    """POST /admin/sessions/{id}/delete must 404 for non-owner."""
    c = two_user_client["client"]
    two_user_client["login"]("user_b", "pwd_b_str")
    r = c.post(
        f"/admin/sessions/{two_user_client['session_id']}/delete",
        follow_redirects=False,
    )
    assert r.status_code == 404


def test_user_b_cannot_toggle_exclude_user_a_session(two_user_client):
    c = two_user_client["client"]
    two_user_client["login"]("user_b", "pwd_b_str")
    r = c.post(
        f"/admin/sessions/{two_user_client['session_id']}/exclude",
        follow_redirects=False,
    )
    assert r.status_code == 404


def test_user_b_export_json_does_not_contain_user_a_data(two_user_client):
    """JSON export is per-user. user_b's export must not leak user_a's
    private fingerprints."""
    c = two_user_client["client"]
    two_user_client["login"]("user_b", "pwd_b_str")
    r = c.get("/export/sessions.json", follow_redirects=False)
    assert r.status_code == 200
    body = r.text
    assert _PRIVATE_NOTE not in body, "user_a's private note leaked to user_b export"
    assert _EXERCISE_NAME not in body


def test_user_b_export_csv_does_not_contain_user_a_data(two_user_client):
    c = two_user_client["client"]
    two_user_client["login"]("user_b", "pwd_b_str")
    r = c.get("/export/sessions.csv", follow_redirects=False)
    assert r.status_code == 200
    assert _PRIVATE_NOTE not in r.text
    assert _EXERCISE_NAME not in r.text


def test_user_a_can_still_read_own_session(two_user_client):
    """Sanity: the isolation does NOT cripple the owner's access.

    A *completed* session redirects (303) to `/sessions/{id}/done`. We
    follow the redirect — what matters is that the owner reaches the
    detail content (vs the 404 user_b gets without following any redirect).
    """
    c = two_user_client["client"]
    two_user_client["login"]("user_a", "pwd_a_str")
    r = c.get(
        f"/sessions/{two_user_client['session_id']}",
        follow_redirects=True,
    )
    assert r.status_code == 200, (
        f"owner cannot read own session: {r.status_code}"
    )
    # And the private fingerprints DO appear for the owner
    assert _EXERCISE_NAME in r.text or _PRIVATE_NOTE in r.text


def test_user_a_export_contains_own_data(two_user_client):
    c = two_user_client["client"]
    two_user_client["login"]("user_a", "pwd_a_str")
    r = c.get("/export/sessions.json", follow_redirects=False)
    assert r.status_code == 200
    body = r.text
    assert _PRIVATE_NOTE in body
    assert _EXERCISE_NAME in body


def test_coach_report_is_per_user(two_user_client):
    """user_b's /coach-report must not reference user_a's exercise."""
    c = two_user_client["client"]
    two_user_client["login"]("user_b", "pwd_b_str")
    r = c.get("/coach-report", follow_redirects=False)
    assert r.status_code == 200
    assert _EXERCISE_NAME not in r.text


def test_history_does_not_show_other_users_sessions(two_user_client):
    """GET /history for user_b must not list user_a's session row."""
    c = two_user_client["client"]
    two_user_client["login"]("user_b", "pwd_b_str")
    r = c.get("/history", follow_redirects=False)
    assert r.status_code == 200
    assert _PRIVATE_NOTE not in r.text
    assert _EXERCISE_NAME not in r.text


def test_admin_sessions_list_scoped_to_caller(two_user_client):
    """/admin/sessions lists only caller's sessions."""
    c = two_user_client["client"]
    two_user_client["login"]("user_b", "pwd_b_str")
    r = c.get("/admin/sessions", follow_redirects=False)
    assert r.status_code == 200
    assert _PRIVATE_NOTE not in r.text


def test_anonymous_cannot_access_private_routes(two_user_client):
    """No session cookie → 303 redirect to /login on private routes."""
    c = two_user_client["client"]
    c.cookies.clear()
    for path in (
        "/",
        "/history",
        "/progress",
        "/dashboard",
        "/coach-report",
        "/export",
        "/admin/sessions",
    ):
        r = c.get(path, follow_redirects=False)
        assert r.status_code in (303, 307), (
            f"anonymous got {r.status_code} on {path} (expected redirect to /login)"
        )


def test_leaderboard_user_profile_is_intentionally_semi_public(two_user_client):
    """`GET /users/{username}` is documented as semi-public (Sb_19+):
    exposes grade + sessions count + radar — never per-session details.
    The fingerprints from user_a's session_exercise must NOT leak even
    though the page is reachable."""
    c = two_user_client["client"]
    two_user_client["login"]("user_b", "pwd_b_str")
    r = c.get("/users/user_a", follow_redirects=False)
    # Page is allowed (semi-public by design)
    assert r.status_code in (200, 404)
    # But the private fingerprints must NOT leak
    if r.status_code == 200:
        assert _PRIVATE_NOTE not in r.text
        assert _EXERCISE_NAME not in r.text


# ───────── ownership helper tests ─────────


def test_get_owned_session_or_404_returns_session_for_owner(two_user_client):
    from app.database import SessionLocal
    from app.services.ownership import get_owned_session_or_404

    with SessionLocal() as db:
        s = get_owned_session_or_404(
            db, two_user_client["session_id"], two_user_client["user_a_id"]
        )
        assert s.id == two_user_client["session_id"]


def test_get_owned_session_or_404_raises_for_non_owner(two_user_client):
    from fastapi import HTTPException

    from app.database import SessionLocal
    from app.services.ownership import get_owned_session_or_404

    with SessionLocal() as db, pytest.raises(HTTPException) as exc:
        get_owned_session_or_404(
            db, two_user_client["session_id"], two_user_client["user_b_id"]
        )
    assert exc.value.status_code == 404


def test_get_owned_session_or_404_raises_for_missing_session(two_user_client):
    from fastapi import HTTPException

    from app.database import SessionLocal
    from app.services.ownership import get_owned_session_or_404

    with SessionLocal() as db, pytest.raises(HTTPException) as exc:
        get_owned_session_or_404(db, 99999, two_user_client["user_a_id"])
    assert exc.value.status_code == 404
