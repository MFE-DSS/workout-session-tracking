"""Negotiated Bearer-only runtime; test activation is explicit and isolated."""

from tests import plan_v3_test_support as support
from tests.test_plan_v3_persistence import install

science_bundle = support.science_bundle
plan_bundle = support.plan_bundle

ROOT = "/api/mobile/v3"
HEADERS = {"X-Auren-Contract": "first-session-runtime/3.0.0"}


def token(client):
    response = client.post(
        "/api/mobile/v1/auth/login", json={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200, response.text
    return {"Authorization": "Bearer " + response.json()["access_token"], **HEADERS}


def enable(monkeypatch):
    from app.config import get_settings

    monkeypatch.setattr(get_settings(), "plan_v3_controlled_test_enabled", True)
    monkeypatch.setattr(get_settings(), "plan_v3_acquisition_enabled", True)


def test_cookie_does_not_authenticate_and_default_is_unserved(client):
    unauthenticated = client.get(ROOT + "/me/first-plan/capabilities", headers=HEADERS)
    assert unauthenticated.status_code == 401
    assert unauthenticated.headers.get("cache-control") == "no-store"
    h = token(client)
    r = client.get(ROOT + "/me/first-plan/capabilities", headers=h)
    assert r.status_code == 200
    assert r.json()["owner_id"] == 1
    assert r.json()["runtime_availability"] == "NOT_SERVED"
    assert r.headers["cache-control"] == "no-store"
    assert (
        client.post(
            ROOT + "/me/blueprint/snapshots",
            headers=h,
            json={"request_id": "off", "expected_revision": 0},
        ).status_code
        == 503
    )


def test_negotiation_owner_isolation_private_validation_and_replay(client, monkeypatch):
    enable(monkeypatch)
    install()
    h = token(client)
    assert (
        client.get(
            ROOT + "/me/blueprint/declarations", headers={"Authorization": h["Authorization"]}
        ).status_code
        == 406
    )
    before = client.get(ROOT + "/me/blueprint/declarations", headers=h).json()
    assert before["source_revision"] == 0
    r = client.put(
        ROOT + "/me/blueprint/declarations",
        headers={**h, "If-Match": "0"},
        json={
            "request_id": "bad",
            "fields": {"owner_id": {"state": "KNOWN", "value": "SECRET_DECLARATION"}},
        },
    )
    assert r.status_code == 422
    assert "SECRET_DECLARATION" not in r.text
    body = {"request_id": "capture", "expected_revision": 0}
    first = client.post(ROOT + "/me/blueprint/snapshots", headers=h, json=body)
    assert first.status_code == 200, first.text
    identity = first.json()["snapshot_ref"]
    assert (
        client.post(ROOT + "/me/blueprint/snapshots", headers=h, json=body).json()["snapshot_ref"]
        == identity
    )
    assert client.get(ROOT + "/me/blueprint/snapshots/unknown", headers=h).status_code == 404
    second = client.post(
        "/api/mobile/v1/auth/register",
        json={
            "username": "other-plan",
            "password": "Test-password-42!",
            "password_confirm": "Test-password-42!",
            "email": "",
        },
    )
    assert second.status_code == 201
    foreign = {**HEADERS, "Authorization": "Bearer " + second.json()["access_token"]}
    assert (
        client.get(ROOT + "/me/blueprint/snapshots/" + identity, headers=foreign).status_code == 404
    )
    assert (
        client.get(ROOT + "/me/blueprint/snapshots/" + identity, headers=h).json()["snapshot_ref"]
        == identity
    )


def test_storage_failure_is_private_unknown_transport_not_durable_business_denial(
    client, monkeypatch
):
    from sqlalchemy.exc import OperationalError

    from app.services.plan_v3 import snapshots

    enable(monkeypatch)
    install()
    headers = token(client)

    def fail(*args, **kwargs):
        raise OperationalError(
            "SELECT private_synthetic_value",
            {"sensitive": "never-echo-this-sentinel"},
            Exception("disk failure"),
        )

    monkeypatch.setattr(snapshots, "declare", fail)
    response = client.put(
        ROOT + "/me/blueprint/declarations",
        headers={**headers, "If-Match": "0"},
        json={"request_id": "disk-failure", "fields": {}},
    )
    assert response.status_code == 503
    assert response.headers["cache-control"] == "no-store"
    assert response.json()["detail"]["error"] == "runtime_storage_unavailable"
    assert "never-echo-this-sentinel" not in response.text
