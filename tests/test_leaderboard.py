"""Leaderboard tests: scoring, ranking, privacy, auth."""
from __future__ import annotations

from datetime import UTC, datetime

from tests.helpers import get_test_user_id


def _other_user_id() -> int:
    """Create or fetch the 'other' user for multi-user tests."""
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.user import User
    from app.services.auth import hash_password

    with SessionLocal() as db:
        u = db.execute(select(User).where(User.username == "lb_other")).scalar_one_or_none()
        if u is None:
            u = User(username="lb_other", password_hash=hash_password("pass"))
            db.add(u)
            db.commit()
        return u.id


def _add_session(user_id, *, quality_inputs, n_work=2, n_done=2):
    """Insert a completed session with controlled quality inputs."""
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    with SessionLocal() as db:
        s = WorkoutSession(
            user_id=user_id,
            template_slug_snapshot="push-a",
            template_name_snapshot="Push A",
            started_at=datetime.now(UTC),
            status="completed",
            concentration=quality_inputs.get("concentration"),
            global_state=quality_inputs.get("global_state"),
        )
        se = SessionExercise(
            exercise_code_snapshot="E1",
            exercise_name_snapshot="Ex",
            position=1,
            success_score=quality_inputs.get("success_score"),
        )
        for i in range(1, n_work + 1):
            se.set_logs.append(SetLog(
                kind="work", set_index=i,
                completed=(i <= n_done),
                weight_kg=60.0, reps=10,
            ))
        s.session_exercises.append(se)
        db.add(s)
        db.commit()
        return s.id


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


def test_leaderboard_requires_auth(client):
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()
    r = client.get("/leaderboard", follow_redirects=False)
    assert r.status_code == 303
    assert "/login" in r.headers.get("location", "")


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def test_leaderboard_renders_empty_state(client):
    body = client.get("/leaderboard").text
    assert "Classement" in body
    # testuser exists but has no completed sessions
    assert "testuser" in body


def test_leaderboard_renders_with_data(client):
    uid = get_test_user_id()
    _add_session(uid, quality_inputs={
        "concentration": "high", "global_state": "good", "success_score": 100,
    })
    body = client.get("/leaderboard").text
    assert "testuser" in body
    assert "pts" in body
    assert "#1" in body


# ---------------------------------------------------------------------------
# Scoring rules
# ---------------------------------------------------------------------------


def test_completed_sessions_contribute(client):
    from app.database import SessionLocal
    from app.services.leaderboard import compute_leaderboard

    uid = get_test_user_id()
    _add_session(uid, quality_inputs={
        "concentration": "high", "global_state": "good", "success_score": 100,
    }, n_work=2, n_done=2)

    with SessionLocal() as db:
        entries = compute_leaderboard(db)
    me = next(e for e in entries if e.username == "testuser")
    assert me.total_points > 0
    assert me.counted_sessions >= 1


def test_excluded_sessions_do_not_contribute(client):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    from app.services.leaderboard import compute_leaderboard

    uid = get_test_user_id()
    sid = _add_session(uid, quality_inputs={
        "concentration": "high", "global_state": "good", "success_score": 100,
    })
    # Exclude it
    with SessionLocal() as db:
        s = db.get(WorkoutSession, sid)
        s.excluded_from_stats = True
        db.commit()
        entries = compute_leaderboard(db)
    me = next(e for e in entries if e.username == "testuser")
    # The excluded session must not contribute points
    assert me.counted_sessions == 0 or me.total_points == 0


def test_in_progress_sessions_do_not_contribute(client):
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession
    from app.services.leaderboard import compute_leaderboard

    uid = get_test_user_id()
    with SessionLocal() as db:
        s = WorkoutSession(
            user_id=uid,
            template_slug_snapshot="push-a",
            template_name_snapshot="Push A",
            started_at=datetime.now(UTC),
            status="in_progress",  # NOT completed
        )
        se = SessionExercise(
            exercise_code_snapshot="E1", exercise_name_snapshot="Ex", position=1,
            success_score=100,
        )
        se.set_logs.append(SetLog(kind="work", set_index=1, completed=True))
        s.session_exercises.append(se)
        db.add(s)
        db.commit()

        entries = compute_leaderboard(db)
    me = next(e for e in entries if e.username == "testuser")
    # in_progress sessions are invisible to the leaderboard
    assert me.counted_sessions == 0


# ---------------------------------------------------------------------------
# Ordering
# ---------------------------------------------------------------------------


def test_ordering_is_descending_by_total_points(client):
    from app.database import SessionLocal
    from app.services.leaderboard import compute_leaderboard

    uid_a = get_test_user_id()
    uid_b = _other_user_id()

    # User A: one strong session
    _add_session(uid_a, quality_inputs={
        "concentration": "high", "global_state": "good", "success_score": 100,
    }, n_work=3, n_done=3)

    # User B: one weaker session
    _add_session(uid_b, quality_inputs={
        "concentration": "low", "global_state": "fatigued", "success_score": 50,
    }, n_work=3, n_done=1)

    with SessionLocal() as db:
        entries = compute_leaderboard(db)

    ranked_names = [e.username for e in entries if e.total_points > 0]
    # testuser scored more -> should be ranked first
    assert ranked_names[0] == "testuser"


def test_weighted_score_penalizes_incomplete_sessions(client):
    """A session where only 50% of work sets are done earns half
    the quality-score points."""
    from app.database import SessionLocal
    from app.services.leaderboard import compute_leaderboard

    uid = get_test_user_id()
    _add_session(uid, quality_inputs={
        "concentration": "high", "global_state": "good", "success_score": 100,
    }, n_work=4, n_done=2)  # 50% completion

    with SessionLocal() as db:
        entries = compute_leaderboard(db)
    me = next(e for e in entries if e.username == "testuser")
    # Quality: work_completion = (2/4)*40 = 20, success = 40,
    # concentration = 10, global_state = 10. Total quality = 80.
    # Leaderboard points = 80 * (2/4) = 40.
    assert 35 <= me.total_points <= 45


# ---------------------------------------------------------------------------
# Privacy: no session detail leakage
# ---------------------------------------------------------------------------


def test_leaderboard_does_not_expose_session_details(client):
    uid_b = _other_user_id()
    _add_session(uid_b, quality_inputs={
        "concentration": "high", "global_state": "good", "success_score": 100,
    })
    body = client.get("/leaderboard").text
    # The leaderboard mentions lb_other's username + points but not
    # any session-level detail (template name, exercise data, etc.)
    assert "lb_other" in body
    assert "pts" in body
    # No session detail links for other users
    assert "/sessions/" not in body


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------


def test_topbar_has_leaderboard_link(client):
    body = client.get("/").text
    assert "/leaderboard" in body
    assert "Classement" in body


def test_leaderboard_entry_has_grade_fields(client):
    """LeaderboardEntry should include grade and last_session_score."""
    from app.database import SessionLocal
    from app.services.leaderboard import compute_leaderboard

    uid = get_test_user_id()
    _add_session(uid, quality_inputs={
        "concentration": "high", "global_state": "good", "success_score": 100,
    }, n_work=4, n_done=4)

    with SessionLocal() as db:
        entries = compute_leaderboard(db)
    me = next(e for e in entries if e.username == "testuser")
    assert hasattr(me, "grade")
    assert me.grade in ("A", "B", "C")
    assert hasattr(me, "last_session_score")
    assert me.last_session_score is not None
    assert hasattr(me, "grade_label")
    assert len(me.grade_label) > 0


def test_leaderboard_grade_c_for_low_volume(client):
    """One weak session should yield grade C."""
    from app.database import SessionLocal
    from app.services.leaderboard import compute_leaderboard

    uid = get_test_user_id()
    _add_session(uid, quality_inputs={
        "concentration": "low", "global_state": "fatigued", "success_score": 50,
    }, n_work=2, n_done=1)

    with SessionLocal() as db:
        entries = compute_leaderboard(db)
    me = next(e for e in entries if e.username == "testuser")
    assert me.grade == "C"
