"""BODY-01 real Bearer consumers; no served fixtures or fabricated lineage."""

from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from test_mob03_weight_api import setup_owner

BASE = "/api/mobile/v1/me/body"
PATH = BASE + "/measurements"
HEADER = "X-Auren-Body-Contract"
VERSION = "body-measurements/1.0.0"


def test_withdrawn_owner_can_discover_and_erase_without_a_new_collection_grant(client):
    owner, headers = auth(client)
    receipt = create(client, headers)
    root = receipt["root_ref"]
    old_token = client.get(f"{PATH}/{root}", headers=headers).json()["entry"]["head_token"]
    corrected = client.post(f"{PATH}/{root}/corrections", headers=headers, json={
        "request_id": "correct-before-withdrawal", "expected_head_token": old_token,
        "values": {"weight_kg": 79},
    })
    assert corrected.status_code == 200
    consent = client.get(BASE + "/consent", headers=headers).json()
    withdrawn = client.post(BASE + "/consent", headers=headers, json={
        "granted": False, "consent_version": consent["consent_version"],
        "expected_consent_token": consent["consent_token"],
    })
    assert withdrawn.status_code == 200
    assert withdrawn.json()["granted"] is False
    # Each request creates a new server Session: no retained selection/token.
    assert client.get(PATH, headers=headers).status_code == 403
    assert client.get(f"{PATH}/{root}", headers=headers).status_code == 403
    result = client.get(PATH, params={"purpose": "erasure", "limit": 1}, headers=headers)
    assert result.status_code == 200
    page = result.json()
    assert page["projection"] == "ERASURE_ONLY"
    assert page["owner_id"] == owner
    assert "field_specs" not in page
    assert page["window"] == {"from": None, "through": None}
    minimal = page["entries"][0]
    assert set(minimal) == {"root_ref", "measurement_id", "revision", "head_token",
                            "measured_at", "date_precision", "version_count"}
    assert minimal["root_ref"] == root
    assert minimal["version_count"] == 2
    assert minimal["date_precision"] == "DAY_UTC_CONVENTION"
    fresh = client.get(f"{PATH}/{root}", params={"purpose": "erasure"}, headers=headers)
    assert fresh.status_code == 200
    assert fresh.json()["entry"] == minimal
    assert client.post(f"{PATH}/{root}/corrections", headers=headers, json={
        "request_id": "no-new-acquisition", "expected_head_token": minimal["head_token"],
        "values": {"weight_kg": 78},
    }).status_code == 403
    stale = client.post(f"{PATH}/{root}/erase", headers=headers, json={
        "request_id": "stale-erase", "expected_head_token": old_token,
        "confirm_all_versions": True,
    })
    assert stale.status_code == 409
    assert client.get(f"{PATH}/{root}", params={"purpose": "erasure"}, headers=headers).status_code == 200
    erased = client.post(f"{PATH}/{root}/erase", headers=headers, json={
        "request_id": "erase-after-withdrawal", "expected_head_token": minimal["head_token"],
        "confirm_all_versions": True,
    })
    assert erased.status_code == 200
    assert erased.json()["state"] == "ERASED"
    assert client.get(PATH, params={"purpose": "erasure"}, headers=headers).json()["entries"] == []
    assert client.get(BASE + "/consent", headers=headers).json()["granted"] is False


def test_erasure_metadata_preserves_private_root_and_disabled_acquisition_boundaries(client):
    from app.config import get_settings
    from app.database import SessionLocal
    from app.models.user import User
    from app.services import body_profile
    from app.services.device_auth import open_device_session

    owner, headers = auth(client)
    root = create(client, headers)["root_ref"]
    with SessionLocal() as db:
        body_profile.set_consent(db, owner, False)
        other = User(username="other-erase-owner", password_hash="synthetic")
        db.add(other)
        db.commit()
        token = open_device_session(db, other).access_token
        db.commit()
    foreign_headers = {HEADER: VERSION, "Authorization": f"Bearer {token}"}
    foreign = client.get(f"{PATH}/{root}?purpose=erasure", headers=foreign_headers)
    unknown = client.get(f"{PATH}/999999?purpose=erasure", headers=foreign_headers)
    assert foreign.status_code == 404
    assert foreign.json() == unknown.json()
    get_settings().body_assessment_enabled = False
    assert client.get(PATH, headers=headers).status_code == 404
    metadata = client.get(f"{PATH}/{root}?purpose=erasure", headers=headers)
    assert metadata.status_code == 200
    assert "fields" not in metadata.json()["entry"]
    assert client.get(PATH + "?purpose=erasure", headers=foreign_headers).json()["entries"] == []
    assert client.get(PATH + "?purpose=erasure", headers={HEADER: VERSION}).status_code == 401


def auth(client, **kwargs):
    owner, headers = setup_owner(client, **kwargs)
    return owner, {**headers, HEADER: VERSION}


def test_erasure_http_pagination_binds_projection_and_current_revision(client):
    from app.config import get_settings

    _, headers = auth(client)
    create(client, headers, key="metadata-first")
    create(client, headers, key="metadata-second")
    params = {"purpose": "erasure", "limit": 1}
    first = client.get(PATH, params=params, headers=headers).json()
    cursor = first["next_cursor"]
    assert cursor
    second = client.get(PATH, params={**params, "cursor": cursor}, headers=headers).json()
    assert first["entries"][0]["root_ref"] != second["entries"][0]["root_ref"]
    assert second["next_cursor"] is None
    assert client.get(PATH, params={"limit": 1, "cursor": cursor}, headers=headers).status_code == 409
    create(client, headers, key="metadata-new-revision")
    assert client.get(PATH, params={**params, "cursor": cursor}, headers=headers).status_code == 409
    assert client.get(PATH, params={"purpose": "unrecognised"}, headers=headers).status_code == 422
    get_settings().app_env = "production"
    assert client.get(PATH, params=params, headers=headers).status_code == 503


def create(client, headers, key="http-body-create", **values):
    response = client.post(
        PATH,
        headers=headers,
        json={
            "request_id": key,
            "measured_on": "2025-01-02",
            "values": values or {"weight_kg": 80, "arm_cm_left": 33},
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_real_http_creation_correction_audit_and_progress_weight_projection(client):
    owner, headers = auth(client)
    receipt = create(client, headers)
    assert receipt["owner_id"] == owner
    import hashlib

    canonical = b'{"measured_on":"2025-01-02","operation":"CREATE","request_id":"http-body-create","values":{"arm_cm_left":33,"weight_kg":80}}'
    assert receipt["command_digest"] == hashlib.sha256(canonical).hexdigest()
    root = receipt["root_ref"]
    first = client.get(f"{PATH}/{root}", headers=headers).json()["entry"]
    assert first["fields"]["weight_kg"]["value"] == 80
    assert first["fields"]["weight_kg"]["unit"] == "kg"
    assert first["fields"]["arm_cm_left"]["unit"] == "cm"
    assert first["date_precision"] == "DAY_UTC_CONVENTION"
    original_left_source = first["fields"]["arm_cm_left"]["provenance"]
    response = client.post(
        f"{PATH}/{root}/corrections",
        headers=headers,
        json={
            "request_id": "http-body-correct",
            "expected_head_token": first["head_token"],
            "values": {"weight_kg": 79.5, "arm_cm_right": 34},
        },
    )
    assert response.status_code == 200
    current = client.get(f"{PATH}/{root}", headers=headers).json()["entry"]
    assert current["root_ref"] == root
    assert current["measurement_id"] != first["measurement_id"]
    assert current["fields"]["arm_cm_left"]["provenance"] == original_left_source
    assert current["fields"]["weight_kg"]["provenance"]["acquisition"] == "MANUAL_CORRECTION"
    history = client.get(f"{PATH}/{root}/versions", headers=headers).json()
    assert history["owner_id"] == owner
    assert [entry["state"] for entry in history["entries"]] == ["CURRENT", "SUPERSEDED"]
    assert [entry["fields"]["weight_kg"]["value"] for entry in history["entries"]] == [79.5, 80]
    page = client.get(PATH + "?from=2025-01-01&through=2025-01-31", headers=headers)
    assert page.status_code == 200
    assert [entry["measurement_id"] for entry in page.json()["entries"]] == [
        current["measurement_id"]
    ]
    assert page.headers[HEADER] == VERSION
    assert page.headers["cache-control"] == "no-store"
    legacy = client.get(BASE + "/weight-history", headers=headers).json()
    assert legacy["contract_version"] == "weight-history/1.0.0"
    assert [entry["value"] for entry in legacy["entries"]] == [79.5]
    assert legacy["entries"][0]["provenance"]["origin"] == "UNKNOWN"


def test_exact_contract_required_without_writing_or_downgrade(client):
    _, headers = auth(client)
    for version in [None, "body-measurements/0.9.0"]:
        candidate = {key: value for key, value in headers.items() if key != HEADER}
        if version:
            candidate[HEADER] = version
        response = client.post(
            PATH,
            headers=candidate,
            json={"request_id": "wrong-version", "values": {"weight_kg": 80}},
        )
        assert response.status_code == 406
        assert response.headers["cache-control"] == "no-store"
    assert client.get(PATH, headers=headers).json()["entries"] == []


def test_unknown_and_foreign_roots_share_a_private_404(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.device_auth import open_device_session

    _, headers = auth(client)
    root = create(client, headers)["root_ref"]
    with SessionLocal() as db:
        other = User(username="other-http-body", password_hash="synthetic")
        db.add(other)
        db.commit()
        issued = open_device_session(db, other)
        db.commit()
        other_headers = {HEADER: VERSION, "Authorization": f"Bearer {issued.access_token}"}
    first = client.get(f"{PATH}/{root}", headers=other_headers)
    unknown = client.get(f"{PATH}/999999", headers=other_headers)
    assert (first.status_code, first.json()) == (unknown.status_code, unknown.json())
    assert first.status_code == 404
    assert client.get(f"{PATH}/{root}", headers={HEADER: VERSION}).status_code == 401


def test_withdrawal_and_flag_changes_do_not_destroy_exact_historical_receipt(client):
    from app.config import get_settings
    from app.database import SessionLocal
    from app.services import body_profile

    owner, headers = auth(client)
    receipt = create(client, headers)
    with SessionLocal() as db:
        body_profile.set_consent(db, owner, False)
    get_settings().body_assessment_enabled = False
    replay = client.post(
        PATH,
        headers=headers,
        json={
            "request_id": "http-body-create",
            "measured_on": "2025-01-02",
            "values": {"weight_kg": 80, "arm_cm_left": 33},
        },
    )
    assert replay.status_code == 200
    assert replay.json() == receipt
    status = client.get(BASE + "/operations/http-body-create", headers=headers)
    assert status.json() == receipt
    assert client.get(f"{PATH}/{receipt['root_ref']}", headers=headers).status_code == 404
    assert client.post(
        PATH,
        headers=headers,
        json={
            "request_id": "new-not-allowed",
            "measured_on": "2025-01-02",
            "values": {"weight_kg": 81},
        },
    ).status_code in {404, 503}


@pytest.mark.parametrize(
    "values",
    [
        {"weight_kg": True},
        {"weight_kg": "80"},
        {"calf_cm": 37},
        {"setting_semantics": "PER_IMPLEMENT", "weight_kg": 80},
    ],
)
def test_invalid_inputs_leave_no_fact_and_no_sensitive_validation_echo(client, values):
    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement

    _, headers = auth(client)
    response = client.post(
        PATH,
        headers=headers,
        json={"request_id": "invalid-body", "measured_on": "2025-01-02", "values": values},
    )
    assert response.status_code == 422
    assert "input" not in response.text
    with SessionLocal() as db:
        assert list(db.scalars(select(BodyMeasurement))) == []


def test_legacy_invalid_values_and_unknown_source_survive_correction_and_export(client):
    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement

    owner, headers = auth(client)
    with SessionLocal() as db:
        row = BodyMeasurement(
            user_id=owner,
            measured_at=datetime(2020, 1, 1, tzinfo=UTC),
            weight_kg=800,
            waist_cm=90,
            calf_cm=37,
        )
        db.add(row)
        db.commit()
        root = row.id
    original = client.get(f"{PATH}/{root}", headers=headers).json()["entry"]
    response = client.post(
        f"{PATH}/{root}/corrections",
        headers=headers,
        json={
            "request_id": "correct-legacy-tour",
            "expected_head_token": original["head_token"],
            "values": {"waist_cm": 85},
        },
    )
    assert response.status_code == 200
    entry = client.get(f"{PATH}/{root}", headers=headers).json()["entry"]
    assert entry["fields"]["weight_kg"]["value"] == 800
    assert entry["fields"]["weight_kg"]["quality"] == "LEGACY_OUTSIDE_CURRENT_BOUNDS"
    assert entry["fields"]["weight_kg"]["provenance"]["origin"] == "UNKNOWN"
    assert entry["fields"]["calf_cm"]["value"] == 37
    export = client.get(PATH + "/export", headers=headers)
    assert export.status_code == 200
    assert len(export.json()["entries"]) == 2
    assert {e["fields"]["waist_cm"]["value"] for e in export.json()["entries"]} == {85, 90}


def test_pagination_is_bound_to_range_and_revision_without_duplicates(client):
    _, headers = auth(client)
    for index in range(3):
        create(client, headers, key=f"page-fact-{index}", weight_kg=80 + index)
    query = {"from": "2025-01-01", "through": "2025-01-31", "limit": 1}
    first = client.get(PATH, headers=headers, params=query).json()
    assert first["next_cursor"] is not None
    second = client.get(PATH, headers=headers, params={**query, "cursor": first["next_cursor"]})
    assert second.status_code == 200
    assert first["entries"][0]["measurement_id"] != second.json()["entries"][0]["measurement_id"]
    entry = first["entries"][0]
    assert (
        client.post(
            f"{PATH}/{entry['root_ref']}/corrections",
            headers=headers,
            json={
                "request_id": "change-after-page",
                "expected_head_token": entry["head_token"],
                "values": {"weight_kg": 79},
            },
        ).status_code
        == 200
    )
    assert (
        client.get(
            PATH, headers=headers, params={**query, "cursor": first["next_cursor"]}
        ).status_code
        == 409
    )
    assert (
        client.get(PATH, headers=headers, params={**query, "cursor": "tampered"}).status_code == 422
    )


def test_erase_replays_after_response_loss_without_resurrecting_original(client):
    _, headers = auth(client)
    original = create(client, headers)
    root = original["root_ref"]
    entry = client.get(f"{PATH}/{root}", headers=headers).json()["entry"]
    assert (
        client.post(
            f"{PATH}/{root}/corrections",
            headers=headers,
            json={
                "request_id": "before-http-erase",
                "expected_head_token": entry["head_token"],
                "values": {"weight_kg": 79},
            },
        ).status_code
        == 200
    )
    head = client.get(f"{PATH}/{root}", headers=headers).json()["entry"]
    command = {
        "request_id": "http-erase",
        "expected_head_token": head["head_token"],
        "confirm_all_versions": True,
    }
    response = client.post(f"{PATH}/{root}/erase", headers=headers, json=command)
    assert response.status_code == 200
    assert response.json()["state"] == "ERASED"
    assert (
        client.post(f"{PATH}/{root}/erase", headers=headers, json=command).json() == response.json()
    )
    assert client.get(f"{PATH}/{root}/versions", headers=headers).status_code == 404
    assert client.get(BASE + "/weight-history", headers=headers).json()["entries"] == []
    replacement = create(client, headers, key="after-http-erase")
    assert replacement["measurement_id"] > head["measurement_id"]
    assert create(client, headers) == original


def test_native_consent_requires_explicit_action_and_preserves_source_timestamps_on_retry(client):
    _, headers = auth(client, consent=False)
    assert client.get(PATH, headers=headers).status_code == 403
    before = client.get(BASE + "/consent", headers=headers).json()
    assert before["granted"] is False
    request = {
        "granted": True,
        "consent_version": before["consent_version"],
        "expected_consent_token": before["consent_token"],
    }
    granted = client.post(BASE + "/consent", headers=headers, json=request)
    assert granted.status_code == 200
    assert granted.json()["granted"] is True
    assert client.post(BASE + "/consent", headers=headers, json=request).json() == granted.json()
    assert client.get(PATH, headers=headers).json()["entries"] == []
    withdrawn = client.post(
        BASE + "/consent",
        headers=headers,
        json={
            "granted": False,
            "consent_version": before["consent_version"],
            "expected_consent_token": granted.json()["consent_token"],
        },
    )
    assert withdrawn.status_code == 200
    assert client.get(PATH, headers=headers).status_code == 403


@pytest.mark.parametrize("key", [["not-a-string"], {"not": "a-string"}])
def test_malformed_command_identity_is_rejected_before_sql_binding(client, key):
    _, headers = auth(client)
    response = client.post(
        PATH,
        headers=headers,
        json={"request_id": key, "measured_on": "2025-01-02", "values": {"weight_kg": 80}},
    )
    assert response.status_code == 422


@pytest.mark.parametrize(
    "extra",
    [{"owner_id": 2}, {"_measured_at": "2020-01-02"}, {"_date_precision": "SERVER_CAPTURE_TIME"}],
)
def test_client_cannot_supply_owner_or_private_acquisition_metadata(client, extra):
    _, headers = auth(client)
    response = client.post(
        PATH,
        headers=headers,
        json={
            "request_id": "private-injection",
            "measured_on": "2025-01-02",
            "values": {"weight_kg": 80},
            **extra,
        },
    )
    assert response.status_code == 422


@pytest.mark.parametrize("token", [None, [], {}, "not-a-consent-token"])
def test_malformed_consent_token_does_not_become_an_acknowledged_action(client, token):
    _, headers = auth(client, consent=False)
    response = client.post(
        BASE + "/consent",
        headers=headers,
        json={"granted": False, "consent_version": 1, "expected_consent_token": token},
    )
    assert response.status_code == 422


def test_revoked_device_between_authentication_and_write_cannot_acquire(client):
    from fastapi import Request

    from app import main
    from app.database import SessionLocal
    from app.deps import DbSession, require_api_user
    from app.models.device_session import DeviceSession
    from app.models.measurement import BodyMeasurement

    _, headers = auth(client)

    def revoke_before_command(request: Request, db: DbSession):
        user = require_api_user(request, db)
        with SessionLocal() as other:
            device = other.get(DeviceSession, request.state.device_session.id)
            device.revoked_at = datetime.now(UTC)
            other.commit()
        return user

    main.app.dependency_overrides[require_api_user] = revoke_before_command
    try:
        response = client.post(
            PATH,
            headers=headers,
            json={
                "request_id": "revoked-native",
                "measured_on": "2025-01-02",
                "values": {"weight_kg": 80},
            },
        )
        assert response.status_code == 401
        with SessionLocal() as db:
            assert list(db.scalars(select(BodyMeasurement))) == []
    finally:
        main.app.dependency_overrides.pop(require_api_user, None)
