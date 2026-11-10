"""Actual Bearer consumers; global mounting waits the sequential composition lease."""

from datetime import UTC, datetime, timedelta

import pytest

ROOT = "/api/mobile/v1/me/training-history"


def mounted(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.routers.mobile_training_history import router
    from app.services.device_auth import open_device_session

    client.app.include_router(router, prefix="/api/mobile/v1")
    with SessionLocal() as db:
        user = db.query(User).one()
        issued = open_device_session(db, user)
        db.commit()
        return user.id, {"Authorization": f"Bearer {issued.access_token}"}


@pytest.mark.parametrize(
    ("path", "query"),
    [
        ("", {"period": "4w", "time_zone": "UTC"}),
        ("/sessions/1", {"entry_ref": "opaque"}),
        ("/exercises", {"read_context": "opaque"}),
        ("/exercises/opaque", {"read_context": "opaque"}),
    ],
)
def test_web_cookie_cannot_open_private_history(client, path, query):
    mounted(client)
    response = client.get(ROOT + path, params=query)
    assert response.status_code == 401
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize(
    "query",
    [
        "period=4w",
        "period=4w&time_zone=PrivateInvalidZone",
        "period=4w&time_zone=UTC&limit=0",
        "period=all&time_zone=UTC&period=4w",
        "period=4w&time_zone=UTC&owner_id=8",
    ],
)
def test_invalid_query_is_private_and_never_silently_normalized(client, query):
    _, headers = mounted(client)
    response = client.get(ROOT + "?" + query, headers=headers)
    assert response.status_code == 422
    assert response.json() == {"detail": {"error": "invalid_training_history_query"}}
    assert "PrivateInvalidZone" not in response.text
    assert response.headers["cache-control"] == "no-store"


def test_real_owned_routes_list_detail_exercise_and_occurrence_preserve_facts(client):
    from app.database import SessionLocal
    from app.services.exercise_identity import ensure_exercise
    from tests.test_training_history_reads import add_session

    owner, headers = mounted(client)
    with SessionLocal() as db:
        ensure_exercise(db, "Captured exercise")
        session = add_session(
            db, owner, started=datetime.now(UTC) - timedelta(minutes=10), reps=9, weight=17.5
        )
        session_id = session.id
    page = client.get(ROOT, params={"period": "4w", "time_zone": "Europe/Paris"}, headers=headers)
    assert page.status_code == 200
    assert page.headers["cache-control"] == "no-store"
    body = page.json()
    entry = body["entries"][0]
    assert entry["session_id"] == session_id
    detail = client.get(
        ROOT + f"/sessions/{session_id}", params={"entry_ref": entry["entry_ref"]}, headers=headers
    )
    assert detail.status_code == 200
    assert detail.json()["exercises"][0]["sets"][0]["weight_kg"] == 17.5
    index = client.get(
        ROOT + "/exercises", params={"read_context": body["read_context"]}, headers=headers
    )
    assert index.status_code == 200
    ref = index.json()["entries"][0]["exercise_ref"]
    occurrences = client.get(
        ROOT + "/exercises/" + ref, params={"read_context": body["read_context"]}, headers=headers
    )
    assert occurrences.status_code == 200
    occurrence = occurrences.json()["entries"][0]
    assert occurrence["comparison"] == "NON_COMPARABLE"
    selected = client.get(
        ROOT + f"/sessions/{session_id}",
        params={"entry_ref": entry["entry_ref"], "occurrence_ref": occurrence["occurrence_ref"]},
        headers=headers,
    )
    assert selected.status_code == 200
    assert selected.json()["selected_se_id"] == occurrence["se_id"]


def test_foreign_and_unknown_detail_do_not_disclose_reference_or_owner_existence(client):
    from app.database import SessionLocal
    from app.models.user import User
    from tests.test_training_history_reads import add_session

    owner, headers = mounted(client)
    with SessionLocal() as db:
        other = User(username="other-http-history", password_hash="synthetic-unused")
        db.add(other)
        db.commit()
        foreign = add_session(
            db, other.id, started=datetime.now(UTC) - timedelta(minutes=10), reps=8
        )
        unowned = add_session(db, None, started=datetime.now(UTC) - timedelta(minutes=10), reps=8)
        ids = [foreign.id, unowned.id, 999999]
    results = [
        client.get(
            ROOT + f"/sessions/{identity}",
            params={"entry_ref": "private-invalid-reference"},
            headers=headers,
        )
        for identity in ids
    ]
    assert [(r.status_code, r.json()) for r in results] == [
        (404, {"detail": {"error": "history_entry_not_found"}})
    ] * 3
    assert all(r.headers["cache-control"] == "no-store" for r in results)


def test_changed_captured_metadata_requires_refresh_with_no_old_payload(client):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    from tests.test_training_history_reads import add_session

    owner, headers = mounted(client)
    with SessionLocal() as db:
        session = add_session(db, owner, started=datetime.now(UTC) - timedelta(minutes=10), reps=8)
        identity = session.id
    entry = client.get(ROOT, params={"period": "all", "time_zone": "UTC"}, headers=headers).json()[
        "entries"
    ][0]
    with SessionLocal() as db:
        db.get(WorkoutSession, identity).template_name_snapshot = "Changed private captured name"
        db.commit()
    response = client.get(
        ROOT + f"/sessions/{identity}", params={"entry_ref": entry["entry_ref"]}, headers=headers
    )
    assert response.status_code == 409
    assert response.json() == {"detail": {"error": "READ_CHANGED"}}


def test_database_error_is_unavailable_without_serializing_private_values(client, monkeypatch):
    from app.routers import mobile_training_history

    _, headers = mounted(client)

    def failed(*_args, **_kwargs):
        raise RuntimeError("Private row, credentials and source detail")

    monkeypatch.setattr(mobile_training_history, "read_sessions", failed)
    response = client.get(ROOT, params={"period": "all", "time_zone": "UTC"}, headers=headers)
    assert response.status_code == 503
    assert response.json() == {"detail": {"error": "training_history_unavailable"}}
    assert response.headers["cache-control"] == "no-store"
