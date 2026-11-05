"""Approved GET boundary: real FastAPI auth/flag/consent/ownership, no writer."""

import base64
import json
from datetime import datetime

import pytest

PATH = "/api/mobile/v1/me/body/weight-history"


def setup_owner(client, *, consent=True, enabled=True):
    from app.config import get_settings
    from app.database import SessionLocal
    from app.models.user import User
    from app.services import body_profile as bp
    from app.services.device_auth import open_device_session

    get_settings().body_assessment_enabled = enabled
    with SessionLocal() as db:
        user = db.query(User).filter_by(username="testuser").one()
        if consent:
            bp.set_consent(db, user.id, True)
        issued = open_device_session(db, user)
        db.commit()
        return user.id, {"Authorization": f"Bearer {issued.access_token}"}


def cursor(value):
    return base64.urlsafe_b64encode(json.dumps(value).encode()).decode().rstrip("=")


def test_flag_is_preserved_and_errors_are_not_cached(client):
    setup_owner(client, enabled=False)
    response = client.get(PATH)
    assert response.status_code == 404
    assert response.headers["cache-control"] == "no-store"


def test_web_cookie_does_not_open_the_weight_api(client):
    setup_owner(client)
    response = client.get(PATH)
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.headers["cache-control"] == "no-store"


def test_consent_is_explicit_and_withdrawal_blocks_further_reads(client):
    from app.database import SessionLocal
    from app.services import body_profile as bp

    owner, headers = setup_owner(client, consent=False)
    assert client.get(PATH, headers=headers).status_code == 403
    with SessionLocal() as db:
        assert bp.get_consent(db, owner) is None
        bp.set_consent(db, owner, True)
    assert client.get(PATH, headers=headers).json()["state"] == "EMPTY"
    with SessionLocal() as db:
        bp.set_consent(db, owner, False)
    response = client.get(PATH, headers=headers)
    assert response.status_code == 403
    assert response.json() == {"detail": {"error": "body_consent_required"}}
    assert response.headers["cache-control"] == "no-store"


def test_owner_is_from_bearer_and_history_is_not_copied_or_backfilled(client):
    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement
    from app.models.user import User
    from app.services import body_profile as bp

    owner, headers = setup_owner(client)
    with SessionLocal() as db:
        user = db.get(User, owner)
        user.weight_kg = 99
        other = User(username="other-weight-owner", password_hash=user.password_hash)
        db.add(other)
        db.flush()
        bp.create_measurement(db, owner, {"weight_kg": 72}, measured_at=datetime(2025, 1, 2))
        bp.create_measurement(db, other.id, {"weight_kg": 91}, measured_at=datetime(2025, 1, 3))
        other_id = other.id
    response = client.get(PATH + f"?user_id={other_id}", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["owner_id"] == owner
    assert body["unit"] == "kg"
    assert body["legacy_profile_included"] is False
    assert [v["value"] for v in body["entries"]] == [72]
    assert body["entries"][0]["measured_at"] == "2025-01-02T00:00:00+00:00"
    assert body["entries"][0]["provenance"]["origin"] == "UNKNOWN"
    assert response.headers["cache-control"] == "no-store"
    with SessionLocal() as db:
        assert db.query(BodyMeasurement).count() == 2
        assert db.get(User, owner).weight_kg == 99


def test_keyset_pages_keep_equal_timestamps_and_partial_entries_do_not_hide_weight(client):
    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement

    owner, headers = setup_owner(client)
    when = datetime(2025, 1, 1, 12)
    with SessionLocal() as db:
        rows = [BodyMeasurement(user_id=owner, measured_at=when, weight_kg=v) for v in [71, 72, 73]]
        db.add_all(
            rows + [BodyMeasurement(user_id=owner, measured_at=datetime(2025, 2, 1), waist_cm=80)]
        )
        db.commit()
        ids = [row.id for row in reversed(rows)]
    collected = []
    query = {"limit": 1}
    for _ in range(3):
        response = client.get(PATH, headers=headers, params=query)
        assert response.status_code == 200
        data = response.json()
        collected.extend(r["measurement_id"] for r in data["entries"])
        query = {"limit": 1, "cursor": data["next_cursor"]}
    assert collected == ids
    assert query["cursor"] is None
    assert client.post(PATH, headers=headers, json={"weight_kg": 80}).status_code == 405


@pytest.mark.parametrize(
    "query",
    [
        {"limit": 0},
        {"limit": 101},
        {"limit": "not-a-number"},
        {"cursor": "***"},
        {"cursor": cursor(["2025-01-01", 1])},
        {"cursor": cursor(["2025-01-01T00:00:00Z", True])},
        {"cursor": cursor({"id": 1})},
    ],
)
def test_invalid_query_is_rejected_privately(client, query):
    _, headers = setup_owner(client)
    response = client.get(PATH, headers=headers, params=query)
    assert response.status_code in [400, 422]
    assert response.headers["cache-control"] == "no-store"
    assert "not-a-number" not in response.text


def test_offset_cursor_is_normalized_and_the_boundary_is_not_repeated(client):
    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement

    owner, headers = setup_owner(client)
    with SessionLocal() as db:
        older = BodyMeasurement(user_id=owner, measured_at=datetime(2026, 1, 1, 11), weight_kg=71)
        bound = BodyMeasurement(user_id=owner, measured_at=datetime(2026, 1, 1, 12), weight_kg=72)
        db.add_all([older, bound])
        db.commit()
        key = bound.id
        expected = older.id
    response = client.get(
        PATH, headers=headers, params={"cursor": cursor(["2026-01-01T13:00:00+01:00", key])}
    )
    assert response.status_code == 200
    assert [r["measurement_id"] for r in response.json()["entries"]] == [expected]
