"""MOB-02 : lectures du bilan sur les vraies routes, sans fuite ni données inventées."""
from datetime import UTC, datetime, timedelta

import pytest

from tests.helpers import get_test_user_id
from tests.test_d9_mobile_sessions import _other_user, _token

API = "/api/mobile/v1/me"


def _session(db, owner, slug, at, *, status="completed", excluded=False):
    from app.models.session import WorkoutSession
    row = WorkoutSession(user_id=owner, template_slug_snapshot=slug, template_name_snapshot=slug,
                         started_at=at, ended_at=at + timedelta(hours=1) if status == "completed" else None,
                         status=status, excluded_from_stats=excluded)
    db.add(row)
    db.flush()
    return row.id


@pytest.mark.parametrize("path", ["training-preferences", "sessions"])
def test_reads_require_bearer_not_web_cookie(client, path):
    assert client.get(f"{API}/{path}").status_code == 401
    client.cookies.clear()
    assert client.get(f"{API}/{path}").status_code == 401


def test_undeclared_preference_is_omitted_and_no_row_is_created(client):
    from app.database import SessionLocal
    from app.models.training_preferences import TrainingPreferences
    h = _token()
    client.cookies.clear()
    with SessionLocal() as db:
        before = db.query(TrainingPreferences).count()
    r = client.get(f"{API}/training-preferences", headers=h)
    assert r.status_code == 200
    assert r.json() == {}
    assert r.headers["cache-control"] == "no-store"
    with SessionLocal() as db:
        assert db.query(TrainingPreferences).count() == before


def test_frequency_is_the_authenticated_users_declaration(client):
    from app.database import SessionLocal
    from app.services.training_preferences import save_training_preferences
    other = _other_user()
    uid = get_test_user_id()
    with SessionLocal() as db:
        save_training_preferences(db, uid, sessions_per_week=3)
        save_training_preferences(db, other, sessions_per_week=6)
        db.commit()
    h = _token(uid)
    r = client.get(f"{API}/training-preferences?user_id={other}", headers=h)
    assert r.status_code == 200
    assert r.json() == {"sessions_per_week": 3}


def test_history_is_owned_completed_countable_and_ordered_with_explicit_truncation(client):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    uid, other = get_test_user_id(), _other_user()
    now = datetime(2026, 11, 4, 10, tzinfo=UTC)
    with SessionLocal() as db:
        oldest = _session(db, uid, "old", now - timedelta(days=3))
        newest = _session(db, uid, "recent", now)
        _session(db, other, "other", now)
        _session(db, None, "legacy-unowned", now)
        _session(db, uid, "in-progress", now, status="in_progress")
        _session(db, uid, "excluded", now, excluded=True)
        db.commit()
        before = [(s.id, s.status, s.excluded_from_stats, s.ended_at) for s in db.query(WorkoutSession)]
    h = _token(uid)
    r = client.get(f"{API}/sessions?limit=1&user_id={other}", headers=h)
    assert r.status_code == 200
    assert r.headers["cache-control"] == "no-store"
    assert r.json()["has_more"] is True
    assert [s["id"] for s in r.json()["sessions"]] == [newest]
    full = client.get(f"{API}/sessions?limit=100", headers=h).json()
    assert full["has_more"] is False
    assert [s["id"] for s in full["sessions"]] == [newest, oldest]
    assert full["sessions"][0]["template_slug"] == "recent"
    assert datetime.fromisoformat(full["sessions"][0]["ended_at"]) == now + timedelta(hours=1)
    with SessionLocal() as db:
        after = [(s.id, s.status, s.excluded_from_stats, s.ended_at) for s in db.query(WorkoutSession)]
    assert after == before


def test_empty_history_is_resolved_empty_not_unknown(client):
    r = client.get(f"{API}/sessions", headers=_token())
    assert r.status_code == 200
    assert r.json() == {"sessions": [], "has_more": False}


@pytest.mark.parametrize("limit", ["0", "-1", "501", "invalid"])
def test_history_limit_is_bounded(client, limit):
    assert client.get(f"{API}/sessions?limit={limit}", headers=_token()).status_code == 422
