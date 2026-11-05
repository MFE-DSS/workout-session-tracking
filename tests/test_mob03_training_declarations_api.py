"""MOB-03 — real owner-scoped adapters, with no new training doctrine."""
from __future__ import annotations

import pytest

from tests.helpers import get_test_user_id

URL = "/api/mobile/v1/me/training-preferences/declarations"
EMPTY = {"sessions_per_week": None, "focus_priorities": None, "available_equipment": None}


def bearer(user_id=None):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.device_auth import open_device_session

    with SessionLocal() as db:
        issued = open_device_session(db, db.get(User, user_id or get_test_user_id()), device_label="test")
        db.commit()
    return {"Authorization": "Bearer " + issued.access_token}


def test_undeclared_read_has_no_defaults_and_preserves_recap_contract(client):
    headers = bearer()
    response = client.get(URL, headers=headers)
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    body = response.json()
    assert body["contract_version"] == 1
    assert body["declarations"] == EMPTY
    assert body["options"]["sessions_per_week"] == {"min": 1, "max": 7}
    assert {item["value"] for item in body["options"]["available_equipment"]} == {
        "barbell", "bodyweight", "cable", "dumbbell", "machine", "smith",
    }
    assert client.get("/api/mobile/v1/me/training-preferences", headers=headers).json() == {}


def test_full_replacement_preserves_order_null_empty_and_concrete_environment(client):
    from app.database import SessionLocal
    from app.services.training_preferences import save_available_equipment_items

    # [] is a concrete, explicit declaration, not an inferred family expansion.
    with SessionLocal() as db:
        save_available_equipment_items(db, get_test_user_id(), [])
    headers = bearer()
    declaration = {"sessions_per_week": 4, "focus_priorities": ["lower", "arms"],
                   "available_equipment": ["dumbbell", "barbell", "dumbbell"]}
    response = client.put(URL, headers=headers, json=declaration)
    assert response.status_code == 200
    assert response.json()["declarations"] == {
        "sessions_per_week": 4, "focus_priorities": ["lower", "arms"],
        "available_equipment": ["barbell", "dumbbell"],
    }
    assert client.get(URL, headers=headers).json() == response.json()
    response = client.put(URL, headers=headers, json={**EMPTY, "focus_priorities": []})
    assert response.status_code == 200
    assert response.json()["declarations"] == {**EMPTY, "focus_priorities": []}
    from app.services.training_preferences import get_training_preferences
    with SessionLocal() as db:
        assert get_training_preferences(db, get_test_user_id()).available_equipment_items == ()


@pytest.mark.parametrize("body", [
    {"sessions_per_week": 3},  # incomplete replacement must not erase other facts
    {**EMPTY, "sessions_per_week": True},
    {**EMPTY, "sessions_per_week": "3"},
    {**EMPTY, "sessions_per_week": 3.5},
    {**EMPTY, "sessions_per_week": 0},
    {**EMPTY, "sessions_per_week": 8},
    {**EMPTY, "focus_priorities": ["upper_chest"]},  # lab token is not an axis
    {**EMPTY, "focus_priorities": ["arms", "arms"]},
    {**EMPTY, "available_equipment": ["all"]},
    {**EMPTY, "available_equipment_items": []},
    {**EMPTY, "user_id": 123},
])
def test_invalid_replacement_is_atomic_and_does_not_echo_input(client, body):
    headers = bearer()
    initial = {**EMPTY, "sessions_per_week": 2}
    assert client.put(URL, headers=headers, json=initial).status_code == 200
    response = client.put(URL, headers=headers, json=body)
    assert response.status_code in {400, 422}
    assert '"input"' not in response.text
    assert client.get(URL, headers=headers).json()["declarations"] == initial


def test_repeated_put_is_one_owned_row_and_cannot_change_another_account(client):
    from app.database import SessionLocal
    from app.models.training_preferences import TrainingPreferences
    from app.models.user import User
    from app.services.training_preferences import (
        get_training_preferences,
        save_training_preferences,
    )

    with SessionLocal() as db:
        other = User(username="other-preferences", password_hash="unused", is_active=True)
        db.add(other)
        db.commit()
        other_id = other.id
        save_training_preferences(db, other_id, sessions_per_week=6)
    headers = bearer()
    body = {**EMPTY, "sessions_per_week": 3}
    for _ in range(2):
        assert client.put(URL, headers=headers, json=body).status_code == 200
    with SessionLocal() as db:
        assert db.query(TrainingPreferences).filter_by(user_id=get_test_user_id()).count() == 1
        assert get_training_preferences(db, other_id).sessions_per_week == 6
    assert client.get(URL, headers=bearer(other_id)).json()["declarations"]["sessions_per_week"] == 6


@pytest.mark.parametrize("method", ["get", "put"])
def test_web_cookie_alone_cannot_read_or_write_declarations(client, method):
    kwargs = {"json": EMPTY} if method == "put" else {}
    assert getattr(client, method)(URL, **kwargs).status_code == 401
