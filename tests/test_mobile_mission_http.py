"""Actual Bearer consumers through the production mobile parent router."""

import pytest

PATH = "/api/mobile/v1/mission-action"
VERSION = "mission-action/1.0.0"


def mounted(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.device_auth import open_device_session

    with SessionLocal() as db:
        user = db.query(User).one()
        issued = open_device_session(db, user)
        db.commit()
        return {"Authorization": f"Bearer {issued.access_token}", "X-Auren-Mission-Action": VERSION}


def test_existing_web_cookie_does_not_open_new_mission_route(client):
    headers = mounted(client)
    headers.pop("Authorization")
    response = client.get(PATH + "?requested_path=HISTORICAL", headers=headers)
    assert response.status_code == 401
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize("version", [None, "mission-action/2.0.0", "", "MISSION-ACTION/1.0.0"])
def test_no_silent_contract_downgrade(client, version):
    headers = mounted(client)
    if version is None:
        headers.pop("X-Auren-Mission-Action")
    else:
        headers["X-Auren-Mission-Action"] = version
    response = client.get(PATH + "?requested_path=HISTORICAL", headers=headers)
    assert response.status_code == 406
    assert response.json() == {"detail": {"error": "mission_contract_not_supported"}}
    assert response.headers["cache-control"] == "no-store"


@pytest.mark.parametrize(
    "query", ["", "?requested_path=READY", "?requested_path=FIRST_USE&requested_path=HISTORICAL"]
)
def test_source_must_be_single_and_explicit_without_echoing_private_input(client, query):
    headers = mounted(client)
    response = client.get(PATH + query, headers=headers)
    assert response.status_code == 422
    assert response.json() == {"detail": {"error": "invalid_mission_query"}}
    assert response.headers["cache-control"] == "no-store"


def test_unknown_v3_host_is_not_assumed_supported(client):
    headers = mounted(client)
    headers["X-Auren-Mission-V3-Host"] = "future"
    response = client.get(PATH + "?requested_path=FIRST_USE", headers=headers)
    assert response.status_code == 406
    assert response.json() == {"detail": {"error": "mission_host_not_supported"}}


def test_real_domain_recommendation_has_exact_negotiated_echo(client):
    headers = mounted(client)
    response = client.get(PATH + "?requested_path=HISTORICAL", headers=headers)
    assert response.status_code == 200
    assert response.headers["X-Auren-Mission-Action"] == VERSION
    assert response.headers["cache-control"] == "no-store"
    body = response.json()
    assert body["state"] == "HISTORICAL_READY"
    assert body["source"] == "HISTORICAL_MISSION"
    assert body["primary_action"]["template_slug"] == body["payload"]["template"]["slug"]
    assert body["primary_action"]["decision"] == body["payload"]["decision"]


def test_production_mobile_parent_mounts_negotiated_mission_without_test_include(client):
    response = client.get(
        PATH + '?requested_path=FIRST_USE', headers={'X-Auren-Mission-Action': VERSION}
    )
    assert response.status_code == 401
    assert response.headers['cache-control'] == 'no-store'
    assert response.headers['www-authenticate'] == 'Bearer'
