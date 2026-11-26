"""Mounted API authentication/negotiation stays separate from runtime admission."""

import pytest

ROOT = "/api/mobile/v1/me/muscle-observed-load"
QUERY = "?from=2026-11-01T00:00:00Z&until=2026-11-25T00:00:00Z"
HEADER = {"X-Auren-Muscle-Observed-Load-Contract": "muscle-observed-load/1.0.0"}


def mounted(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.device_auth import open_device_session

    with SessionLocal() as db:
        user = db.query(User).one()
        issued = open_device_session(db, user)
        db.commit()
        return user.id, dict(HEADER, Authorization="Bearer " + issued.access_token)


def test_cookie_only_is_unauthorized_no_store(client):
    response = client.get(ROOT + QUERY, headers=HEADER)
    assert response.status_code == 401 and response.headers["cache-control"] == "no-store"
    assert response.headers["www-authenticate"] == "Bearer"
    assert "owner_id" not in response.json()


def test_feature_is_default_off_and_returns_generic_unavailable(client):
    _, headers = mounted(client)
    response = client.get(ROOT + QUERY, headers=headers)
    assert response.status_code == 503
    assert response.json()["detail"]["error"] == "muscle_observed_load_unavailable"
    assert response.headers["cache-control"] == "no-store"


@pytest.mark.parametrize(
    "suffix",
    [
        "&owner_id=2",
        "&from=2026-11-01T00:00:00Z",
        "&time_zone=Europe/Paris",
        "&cursor=anything",
        "&profile_path=../../outside",
        "&runtime_profile=../../outside",
        "&muscle_observed_load_profile_path=../../outside",
        "&database_url=sqlite:///outside",
        "&bundle_root=../../outside",
    ],
)
def test_query_extras_and_duplicates_rejected_before_work(client, suffix):
    _, headers = mounted(client)
    response = client.get(ROOT + QUERY + suffix, headers=headers)
    assert response.status_code == 422 and response.headers["cache-control"] == "no-store"


def test_contract_required_and_get_body_refused(client):
    _, headers = mounted(client)
    no_contract = {k: v for k, v in headers.items() if k == "Authorization"}
    assert client.get(ROOT + QUERY, headers=no_contract).status_code == 406
    response = client.request("GET", ROOT + QUERY, headers=headers, content=b'{"owner_id":2}')
    assert response.status_code == 422


def test_owned_http_port_cannot_change_owner_and_keeps_strict_response(client, monkeypatch):
    from test_muscle_observed_load_contract import empty_wire

    import app.routers.mobile_muscle_observed_load as route
    from app.config import get_settings
    from app.services.muscle_observed_load.contracts import ObservedLoadResponse

    owner, headers = mounted(client)
    monkeypatch.setattr(get_settings(), "muscle_observed_load_enabled", True)
    called = []

    def read(owner_id, query, **kwargs):
        called.append(owner_id)
        wire = empty_wire()
        wire["owner_id"] = owner_id
        return ObservedLoadResponse.model_validate(wire)

    monkeypatch.setattr(route, "read_owned_muscle_observed_load", read)
    response = client.get(ROOT + QUERY, headers=headers)
    assert response.status_code == 200 and response.json()["owner_id"] == owner
    assert called == [owner] and response.headers["cache-control"] == "no-store"


def test_mounted_http_real_sqlite_projection_and_owner_isolation(client, monkeypatch):
    """Actual HTTP + owned capture/projection; only Linux transport/source port substituted.

    Not an installed Linux/profile qualification. Canonical asset admission remains HOLD.
    """
    import hashlib
    import sqlite3
    from datetime import UTC, datetime
    from pathlib import Path

    from test_muscle_observed_load_projection import project

    import app.routers.mobile_muscle_observed_load as route
    from app.config import get_settings
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession
    from app.models.user import User
    from app.services.muscle_observed_load.contracts import ObservedLoadResponse

    owner, headers = mounted(client)
    with SessionLocal() as db:
        foreign = User(username="synthetic-other-owner", password_hash="not-a-real-password")
        db.add(foreign)
        db.flush()
        for who in (owner, foreign.id):
            session = WorkoutSession(
                user_id=who,
                status="completed",
                excluded_from_stats=False,
                started_at=datetime(2026, 10, 1, tzinfo=UTC),
                template_slug_snapshot="legacy",
                template_name_snapshot="Synthetic",
            )
            db.add(session)
            db.flush()
            exercise = SessionExercise(
                session_id=session.id,
                exercise_name_snapshot="Pompes",
                exercise_code_snapshot="not-an-identity",
                position=0,
            )
            db.add(exercise)
            db.flush()
            db.add(
                SetLog(
                    session_exercise_id=exercise.id,
                    kind="work",
                    completed=True,
                    completed_at=datetime(2026, 11, 2, tzinfo=UTC),
                    set_index=1,
                    reps=9 if who == owner else 999,
                )
            )
        db.commit()
    settings = get_settings()
    monkeypatch.setattr(settings, "muscle_observed_load_enabled", True)
    path = Path(settings.database_url.removeprefix("sqlite:///"))

    def snapshot():
        with sqlite3.connect(path) as db:
            return hashlib.sha256("\n".join(db.iterdump()).encode()).hexdigest()

    before = snapshot()

    # Real capture opens the same canonical file as the mounted authentication DB.
    def reader(owner_id, query, **kwargs):
        return ObservedLoadResponse.model_validate(project(path, owner=owner_id))

    monkeypatch.setattr(route, "read_owned_muscle_observed_load", reader)
    response = client.get(ROOT + QUERY, headers=headers)
    assert response.status_code == 200
    assert response.json()["state"] == "PARTIAL"
    assert len(response.json()["facts"]) == 1 and response.json()["facts"][0]["reps"] == 9
    assert snapshot() == before  # includes all server rows, not only set count
