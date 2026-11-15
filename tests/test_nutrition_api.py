"""Actual canonical app HTTP boundaries, auth, consent, schema and receipts."""

import pytest
from nutrition_helpers import nutrition_environment
from sqlalchemy import inspect

ROOT = "/api/mobile/v1/me/nutrition"
VERSION = "nutrition-manual/1.0.0"


@pytest.fixture(autouse=True)
def controlled_environment(monkeypatch):
    with nutrition_environment(monkeypatch):
        yield


def owner(client, *, secondary=False, install=True):
    from app.config import get_settings
    from app.database import SessionLocal, engine
    from app.models.nutrition import NutritionDayRevision, NutritionTargetRevision
    from app.models.user import User
    from app.services.device_auth import open_device_session

    get_settings().nutrition_manual_controlled_test_enabled = True
    if install:
        # Explicit migrated-test provisioning, never application startup DDL.
        NutritionTargetRevision.__table__.create(engine, checkfirst=True)
        NutritionDayRevision.__table__.create(engine, checkfirst=True)
    with SessionLocal() as db:
        user = db.query(User).filter_by(username="testuser").one()
        if secondary:
            user = User(username="nutrition-api-other", password_hash="synthetic-only")
            db.add(user)
            db.flush()
        pair = open_device_session(db, user)
        db.commit()
        return user.id, {"Authorization": f"Bearer {pair.access_token}",
                         "X-Auren-Nutrition-Contract": VERSION}


def consent(client, headers, granted=True):
    current = client.get(ROOT + "/consent", headers=headers)
    assert current.status_code == 200
    return client.post(ROOT + "/consent", headers=headers, json={
        "contract_version": VERSION, "expected_token": current.json()["consent_token"],
        "granted": granted, "wording_version": 1,
    })


def body(token, request="http-day-1", values=None):
    return {"contract_version": "nutrition-command/1.0.0", "request_id": request,
            "expected_head_token": token, "operation": "SET_FIELDS",
            "values": {"kcal_milli": 0} if values is None else values,
            "timezone": "Europe/Paris", "target_ref": None, "confirm_complete": None}


def test_no_startup_nutrition_ddl_cookie_auth_or_silent_contract_downgrade(client):
    from app.database import engine

    assert "nutrition_day_revisions_v1" not in inspect(engine).get_table_names()
    _, headers = owner(client, install=False)
    response = client.get(ROOT + "/capabilities", headers=headers)
    assert response.status_code == 200
    assert response.json()["state"] == "SCHEMA_UNAVAILABLE"
    assert response.json()["can_write"] is False
    assert response.headers["cache-control"] == "no-store"
    assert client.get(ROOT + "/capabilities", headers={"X-Auren-Nutrition-Contract": VERSION}).status_code == 401
    bad = client.get(ROOT + "/capabilities", headers={**headers, "X-Auren-Nutrition-Contract": "old"})
    assert bad.status_code == 406
    assert "nutrition_day_revisions_v1" not in inspect(engine).get_table_names()


def test_real_http_manual_day_and_historical_receipt_survive_consent_revocation(client):
    user_id, headers = owner(client)
    assert consent(client, headers).status_code == 200
    head = client.get(ROOT + "/days/2026-11-12", headers=headers)
    assert head.status_code == 200 and head.json()["state"] == "ABSENT"
    command = body(head.json()["head_token"])
    created = client.post(ROOT + "/days/2026-11-12/revisions", headers=headers, json=command)
    assert created.status_code == 200
    assert created.headers["X-Auren-Nutrition-Contract"] == VERSION
    assert created.json()["owner_id"] == user_id
    current_head = client.get(ROOT + "/days/2026-11-12", headers=headers).json()
    unchanged = body(current_head["head_token"], request="no-change-is-not-an-effect")
    refused = client.post(ROOT + "/days/2026-11-12/revisions", headers=headers, json=unchanged)
    assert refused.status_code == 422
    assert refused.json() == {"detail": {"error": "invalid_command"}}
    page = client.get(ROOT + "/days?from=2026-11-06&through=2026-11-12", headers=headers)
    assert page.status_code == 200
    assert page.json()["totals"]["kcal_milli"] == {"value": 0, "known_days": 1}
    assert page.json()["totals"]["protein_milli"]["value"] is None
    assert consent(client, headers, False).status_code == 200
    replay = client.post(ROOT + "/days/2026-11-12/revisions", headers=headers, json=command)
    assert replay.status_code == 200 and replay.json() == created.json()
    status = client.get(ROOT + "/operations/DAY/http-day-1", headers=headers)
    assert status.status_code == 200 and status.json() == created.json()
    assert "values" not in status.json()
    assert client.get(ROOT + "/days?from=2026-11-06&through=2026-11-12", headers=headers).status_code == 403
    changed = {**command, "request_id": "new-after-revoke"}
    assert client.post(ROOT + "/days/2026-11-12/revisions", headers=headers, json=changed).status_code == 403


def test_foreign_target_and_missing_target_are_indistinguishable(client):
    _, a = owner(client)
    assert consent(client, a).status_code == 200
    head = client.get(ROOT + "/targets/head?variant=STANDARD&effective_from=2026-11-01", headers=a)
    assert head.status_code == 200
    target = {"contract_version": "nutrition-command/1.0.0", "request_id": "preset",
              "expected_head_token": head.json()["head_token"], "operation": "SET_FIELDS",
              "variant": "STANDARD", "effective_from": "2026-11-01", "values": {"kcal_milli": 2000000}}
    result = client.post(ROOT + "/targets/revisions", headers=a, json=target)
    assert result.status_code == 200
    target_id = result.json()["entity_ref"]
    _, b = owner(client, secondary=True)
    assert consent(client, b).status_code == 200
    foreign = client.get(ROOT + f"/targets/{target_id}/revisions", headers=b)
    missing = client.get(ROOT + "/targets/999999/revisions", headers=b)
    assert foreign.status_code == missing.status_code == 404
    assert foreign.json() == missing.json()
