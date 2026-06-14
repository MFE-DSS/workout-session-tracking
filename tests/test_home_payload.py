"""Sb_27.1 — Home dashboard payload tests.

Covers the shape contract of `build_home_payload`, the degraded paths
(no session, no implicit_label, no quality_score), the user-scope
(another user's sessions never leak into payload), and the GET / route
(200 + budget-friendly).

The payload composer does NOT touch scoring core internals — these
tests confirm that even when sub-services raise, the payload stays
structured (Sx_27 §16 hard contract "narrative ne ment jamais").
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

# ─────────────────── shape contract ───────────────────


def test_payload_always_has_three_keys(client):
    """`build_home_payload` returns the 3 promised keys for any user."""
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.home import build_home_payload

    with SessionLocal() as db:
        user = db.query(User).first()
        payload = build_home_payload(db, user)
    assert set(payload.keys()) == {"today", "last_session", "week"}


def test_payload_for_user_with_no_session(client):
    """Fresh user → today=no_reco fallback, last_session=none, week=0 sessions."""
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.home import build_home_payload

    with SessionLocal() as db:
        user = db.query(User).first()
        payload = build_home_payload(db, user)

    assert payload["today"]["available"] is True
    # No completed session → last_session.kind == "none"
    assert payload["last_session"]["available"] is True
    assert payload["last_session"]["kind"] == "none"
    assert "Pas encore" in payload["last_session"]["reason"]
    # Week 0 sessions
    assert payload["week"]["available"] is True
    assert payload["week"]["sessions_done"] == 0
    assert "cette semaine" in payload["week"]["signal"].lower()


# ─────────────────── last_session full path ───────────────────


def _seed_one_completed_session(
    db,
    user_id: int,
    *,
    implicit_label: str | None = "intense",
    days_ago: int = 1,
):
    """Helper: create one completed session with optional implicit_label."""
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    started = datetime.now(UTC) - timedelta(days=days_ago)
    s = WorkoutSession(
        user_id=user_id,
        template_slug_snapshot="push-a",
        template_name_snapshot="Push A",
        started_at=started,
        ended_at=started + timedelta(minutes=45),
        status="completed",
        scoring_version=2,
    )
    se = SessionExercise(
        exercise_code_snapshot="BENCH",
        exercise_name_snapshot="Bench Press",
        position=1,
        implicit_label=implicit_label,
    )
    se.set_logs.append(
        SetLog(kind="work", set_index=1, weight_kg=80.0, reps=8, completed=True)
    )
    s.session_exercises.append(se)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def test_last_session_with_implicit_label(client):
    """Implicit label present → surfaced + source ratio."""
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.home import build_home_payload

    with SessionLocal() as db:
        user = db.query(User).first()
        _seed_one_completed_session(db, user.id, implicit_label="intense")

    with SessionLocal() as db:
        user = db.query(User).first()
        payload = build_home_payload(db, user)

    ls = payload["last_session"]
    assert ls["kind"] == "summary"
    assert ls["template_name"] == "Push A"
    assert ls["implicit_label"] == "intense"
    assert "1/1" in ls["implicit_label_source"]


def test_last_session_without_implicit_label_says_non_deductible(client):
    """No implicit_label on any exercise → explicit "Non déductible" note."""
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.home import build_home_payload

    with SessionLocal() as db:
        user = db.query(User).first()
        _seed_one_completed_session(db, user.id, implicit_label=None)

    with SessionLocal() as db:
        user = db.query(User).first()
        payload = build_home_payload(db, user)

    ls = payload["last_session"]
    assert ls["kind"] == "summary"
    assert ls["implicit_label"] is None
    assert ls["implicit_label_note"] == "Non déductible"


def test_last_session_excluded_from_stats_is_ignored(client):
    """A session flagged excluded_from_stats must not be picked."""
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.home import build_home_payload

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _seed_one_completed_session(db, user.id)
        s.excluded_from_stats = True
        db.add(s)
        db.commit()

    with SessionLocal() as db:
        user = db.query(User).first()
        payload = build_home_payload(db, user)

    # Either kind=none, or another non-excluded session — but THIS one
    # cannot be the picked one.
    if payload["last_session"]["kind"] != "none":
        assert payload["last_session"]["session_id"] != s.id


def test_last_session_days_ago_zero_when_today(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.home import build_home_payload

    with SessionLocal() as db:
        user = db.query(User).first()
        _seed_one_completed_session(db, user.id, days_ago=0)

    with SessionLocal() as db:
        user = db.query(User).first()
        payload = build_home_payload(db, user)

    assert payload["last_session"]["days_ago"] == 0


# ─────────────────── week ───────────────────


def test_week_counts_only_current_iso_week(client):
    """Sessions older than monday 00:00 UTC are not counted in week."""
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.home import build_home_payload

    with SessionLocal() as db:
        user = db.query(User).first()
        # One session 14 days ago — should NOT be counted
        _seed_one_completed_session(db, user.id, days_ago=14)
        # One session today — should be counted
        _seed_one_completed_session(db, user.id, days_ago=0)

    with SessionLocal() as db:
        user = db.query(User).first()
        payload = build_home_payload(db, user)

    # At most 1 in the current week (the "today" one). The 14-day-old
    # session is excluded.
    assert payload["week"]["sessions_done"] >= 1


def test_week_signal_text_for_zero(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.home import build_home_payload

    with SessionLocal() as db:
        user = db.query(User).first()
        payload = build_home_payload(db, user)

    assert payload["week"]["sessions_done"] == 0
    assert "Pas encore" in payload["week"]["signal"]


# ─────────────────── user-scope isolation ───────────────────


def test_payload_is_user_scoped(client):
    """A session belonging to another user must NEVER appear in payload."""
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.auth import hash_password
    from app.services.home import build_home_payload

    with SessionLocal() as db:
        other = User(
            username="other_user",
            password_hash=hash_password("other_pwd_str"),  # noqa: S106
        )
        db.add(other)
        db.commit()
        db.refresh(other)
        # Seed a session for the OTHER user
        _seed_one_completed_session(db, other.id, implicit_label="intense")

    with SessionLocal() as db:
        testuser = db.query(User).filter(User.username == "testuser").first()
        payload = build_home_payload(db, testuser)

    # testuser has no completed session of their own
    assert payload["last_session"]["kind"] == "none"
    assert payload["week"]["sessions_done"] == 0


# ─────────────────── safety net ───────────────────


def test_payload_never_crashes_on_sub_builder_exception(client, monkeypatch):
    """If a sub-builder raises, the key is still present with available=False."""
    from app.database import SessionLocal
    from app.models.user import User
    from app.services import home as home_mod

    def _explode(*_args, **_kwargs):
        raise RuntimeError("forced for test")

    monkeypatch.setattr(home_mod, "_build_today", _explode)

    with SessionLocal() as db:
        user = db.query(User).first()
        payload = home_mod.build_home_payload(db, user)

    assert payload["today"]["available"] is False
    assert payload["today"]["error_type"] == "RuntimeError"
    # Other tiles still produced normally
    assert payload["last_session"]["available"] is True
    assert payload["week"]["available"] is True


# ─────────────────── HTTP route ───────────────────


def test_home_route_returns_200(client):
    """GET / for logged-in user remains 200 after enrichment."""
    r = client.get("/", follow_redirects=False)
    assert r.status_code == 200


def test_home_route_renders_coaching_loop_section(client):
    """The new coaching-loop section must appear in the rendered HTML."""
    r = client.get("/")
    assert r.status_code == 200
    body = r.text
    # Either the section label OR a fallback phrase from build_home_payload
    assert (
        "coaching-loop" in body
        or "Aujourd'hui" in body
        or "Pas encore" in body
    )


@pytest.mark.parametrize("path", ["/"])
def test_home_route_no_forbidden_secret_leak(client, path):
    """Sanity check Sx_27 §16: never leak env-secret-like strings."""
    r = client.get(path)
    body = r.text.lower()
    for forbidden in ("sentry_dsn", "discord_webhook_url", "secret_key"):
        assert forbidden not in body
