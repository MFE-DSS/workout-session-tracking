"""Actual SSR consumers share version/CAS/erasure semantics with native API."""

import re
from decimal import Decimal
from html.parser import HTMLParser

import pytest
from sqlalchemy import select


def prepare(client):
    from app.config import get_settings
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.body_profile import create_measurement, set_consent

    get_settings().body_assessment_enabled = True
    with SessionLocal() as db:
        owner = db.scalar(select(User).where(User.username == "testuser"))
        set_consent(db, owner.id, True)
        row = create_measurement(db, owner.id, {"weight_kg": 80, "waist_cm": 90})
        return row.id


def hidden(html, name):
    match = re.search(rf'name="{name}" value="([^"]+)"', html)
    assert match is not None, f"Form is missing its actual {name} state"
    return match.group(1)


def test_browser_erasure_after_withdrawal_needs_no_new_collection_grant(client):
    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement
    from app.services import body_profile as bp

    mid = prepare(client)
    form = client.get(f"/body/measurements/{mid}/edit").text
    assert client.post(f"/body/measurements/{mid}/edit", data={
        "waist_cm": "85", "request_id": "before-withdrawal",
        "expected_head_token": hidden(form, "expected_head_token"),
    }, follow_redirects=False).status_code == 303
    assert client.post("/body/consent", data={"action": "withdraw"},
                       follow_redirects=False).status_code == 303
    overview = client.get("/body").text
    assert '/body?manage_erasure=1' in overview
    response = client.get("/body?manage_erasure=1")
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    html = response.text
    assert "Je consens" not in html
    assert "weight_kg" not in html and "Ratios (" not in html
    assert 'name="confirm_all_versions" value="yes"' in html
    assert "2 versions" in html
    path = re.search(r'action="([^"]+/measurements/\d+/delete)"', html).group(1)
    payload = {"request_id": hidden(html, "request_id"),
               "expected_head_token": hidden(html, "expected_head_token"),
               "confirm_all_versions": "yes"}
    assert client.post(path, data=payload, follow_redirects=False).status_code == 303
    with SessionLocal() as db:
        assert list(db.scalars(select(BodyMeasurement))) == []
        assert not bp.has_active_consent(db, 1)
    assert "Aucun relevé à effacer" in client.get("/body?manage_erasure=1").text


@pytest.mark.parametrize("historical_weight", [800, 12, 71.25, 71.123456])
def test_browser_constraints_allow_unchanged_history_during_correction(client, historical_weight):
    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement

    mid = prepare(client)
    with SessionLocal() as db:
        # Legacy DB fixture only: a fresh acquisition must still pass current bounds.
        db.get(BodyMeasurement, mid).weight_kg = historical_weight
        db.commit()

    class Inputs(HTMLParser):
        def __init__(self, html):
            super().__init__()
            self.fields = {}
            self.feed(html)

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag == "input" and attrs.get("name"):
                self.fields[attrs["name"]] = attrs

    fields = Inputs(client.get(f"/body/measurements/{mid}/edit").text).fields
    weight = fields["weight_kg"]
    value = Decimal(weight["value"])
    assert value == Decimal(str(historical_weight))
    assert Decimal(weight["min"]) <= value <= Decimal(weight["max"])
    step = weight.get("step", "1")
    assert step == "any" or (value - Decimal(weight["min"])) % Decimal(step) == 0
    fresh = Inputs(client.get("/body/measurements/new").text).fields["weight_kg"]
    assert Decimal(fresh["min"]) > 12
    assert Decimal(fresh["max"]) < 800

    # A full browser form correcting only waist must not reacquire a rounded weight.
    payload = {key: attrs.get("value", "") for key, attrs in fields.items()}
    payload["waist_cm"] = "85"
    response = client.post(
        f"/body/measurements/{mid}/edit", data=payload, follow_redirects=False
    )
    assert response.status_code == 303
    from app.models.body_measurement_operation import BodyMeasurementOperation

    with SessionLocal() as db:
        operation = db.scalar(
            select(BodyMeasurementOperation)
            .where(BodyMeasurementOperation.operation == "CORRECT")
            .order_by(BodyMeasurementOperation.id.desc())
        )
        assert operation.changed_fields == ["waist_cm"]
        assert "weight_kg" not in operation.provenance_by_changed_field
        assert db.get(BodyMeasurement, operation.measurement_ref).weight_kg == historical_weight
        assert db.get(BodyMeasurement, mid).weight_kg == historical_weight


def test_repeated_browser_capture_reuses_its_first_server_timestamp(client):
    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement

    prepare(client)
    form = client.get("/body/measurements/new").text
    payload = {"request_id": hidden(form, "request_id"), "waist_cm": "82"}
    assert (
        client.post("/body/measurements", data=payload, follow_redirects=False).status_code == 303
    )
    assert (
        client.post("/body/measurements", data=payload, follow_redirects=False).status_code == 303
    )
    with SessionLocal() as db:
        assert len(list(db.scalars(select(BodyMeasurement)))) == 2


def test_partial_browser_correction_can_clear_one_field_without_resubmitting_others(client):
    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement
    from app.services import body_profile as bp

    mid = prepare(client)
    form = client.get(f"/body/measurements/{mid}/edit").text
    response = client.post(f"/body/measurements/{mid}/edit", data={
        "waist_cm": "", "request_id": hidden(form, "request_id"),
        "expected_head_token": hidden(form, "expected_head_token"),
    }, follow_redirects=False)
    assert response.status_code == 303
    with SessionLocal() as db:
        original = db.get(BodyMeasurement, mid)
        current = bp.list_measurements(db, original.user_id)
        assert (original.weight_kg, original.waist_cm) == (80, 90)
        assert [(row.weight_kg, row.waist_cm) for row in current] == [(80, None)]
    fresh = client.get("/body/measurements/new").text
    assert client.post("/body/measurements", data={
        "waist_cm": "", "request_id": hidden(fresh, "request_id"),
    }, follow_redirects=False).status_code == 400


def test_browser_correction_preserves_original_and_refuses_stale_form(client):
    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement
    from app.services.body_profile import list_measurements

    mid = prepare(client)
    html = client.get(f"/body/measurements/{mid}/edit").text
    token, key = hidden(html, "expected_head_token"), hidden(html, "request_id")
    payload = {"waist_cm": "85", "expected_head_token": token, "request_id": key}
    assert (
        client.post(
            f"/body/measurements/{mid}/edit", data=payload, follow_redirects=False
        ).status_code
        == 303
    )
    assert (
        client.post(
            f"/body/measurements/{mid}/edit", data=payload, follow_redirects=False
        ).status_code
        == 303
    )
    stale = {**payload, "waist_cm": "84", "request_id": "another-stale-form"}
    assert (
        client.post(
            f"/body/measurements/{mid}/edit", data=stale, follow_redirects=False
        ).status_code
        == 409
    )
    with SessionLocal() as db:
        original = db.get(BodyMeasurement, mid)
        assert original.waist_cm == 90
        current = list_measurements(db, original.user_id)
        assert [(r.weight_kg, r.waist_cm) for r in current] == [(80, 85)]
        assert len(list(db.scalars(select(BodyMeasurement)))) == 2


def test_web_erasure_requires_confirmation_and_is_replayable(client):
    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement
    from app.services.body_profile import measurement_head_token

    mid = prepare(client)
    with SessionLocal() as db:
        token = measurement_head_token(db, db.get(BodyMeasurement, mid))
    payload = {"expected_head_token": token, "request_id": "browser-erasure"}
    assert (
        client.post(
            f"/body/measurements/{mid}/delete", data=payload, follow_redirects=False
        ).status_code
        == 422
    )
    payload["confirm_all_versions"] = "yes"
    assert (
        client.post(
            f"/body/measurements/{mid}/delete", data=payload, follow_redirects=False
        ).status_code
        == 303
    )
    assert (
        client.post(
            f"/body/measurements/{mid}/delete", data=payload, follow_redirects=False
        ).status_code
        == 303
    )
    with SessionLocal() as db:
        assert list(db.scalars(select(BodyMeasurement))) == []


@pytest.mark.parametrize(
    "submitted,precision",
    [
        ("2020-01-02", "DAY_UTC_CONVENTION"),
        ("not-a-date", "SERVER_CAPTURE_TIME"),
        ("2999-01-02", "SERVER_CAPTURE_TIME"),
    ],
)
def test_profile_acquisition_attests_actual_date_precision(client, submitted, precision):
    from app.database import SessionLocal
    from app.models.body_measurement_operation import BodyMeasurementOperation

    prepare(client)
    response = client.post(
        "/profile/measurements",
        data={"weight_kg": "79", "measured_at": submitted},
        follow_redirects=False,
    )
    assert response.status_code == 303
    with SessionLocal() as db:
        operation = db.scalar(
            select(BodyMeasurementOperation).order_by(BodyMeasurementOperation.id.desc())
        )
        assert operation.date_provenance == {"precision": precision}


@pytest.mark.parametrize("path", ["/body/measurements", "/profile/measurements"])
def test_cookie_revoked_after_authentication_cannot_acquire_a_fact(client, path):
    from fastapi import Request

    from app import main
    from app.database import SessionLocal
    from app.deps import DbSession, require_user
    from app.models.measurement import BodyMeasurement
    from app.models.user import User

    prepare(client)

    async def revoked_between_auth_and_command(request: Request, db: DbSession):
        user = await require_user(request, db)
        with SessionLocal() as other:
            current = other.get(User, user.id)
            current.session_epoch += 1
            other.commit()
        return user

    main.app.dependency_overrides[require_user] = revoked_between_auth_and_command
    try:
        response = client.post(path, data={"weight_kg": "79"}, follow_redirects=False)
        assert response.status_code == 401
        with SessionLocal() as db:
            assert len(list(db.scalars(select(BodyMeasurement)))) == 1
    finally:
        main.app.dependency_overrides.pop(require_user, None)


def test_full_browser_form_preserves_resubmitted_outside_bounds_legacy_value(client):
    from datetime import UTC, datetime

    from app.database import SessionLocal
    from app.models.body_measurement_operation import BodyMeasurementOperation
    from app.models.measurement import BodyMeasurement
    from app.services import body_profile as bp

    first = prepare(client)
    with SessionLocal() as db:
        owner = db.get(BodyMeasurement, first).user_id
        legacy = BodyMeasurement(
            user_id=owner, measured_at=datetime(2020, 1, 1, tzinfo=UTC),
            weight_kg=800, waist_cm=90,
        )
        db.add(legacy)
        db.commit()
        mid = legacy.id
    form = client.get(f"/body/measurements/{mid}/edit").text
    payload = {s.key: "" for s in bp.BODY_MEASUREMENT_FIELDS}
    payload.update(weight_kg="800", waist_cm="85",
                   expected_head_token=hidden(form, "expected_head_token"),
                   request_id=hidden(form, "request_id"))
    result = client.post(f"/body/measurements/{mid}/edit", data=payload, follow_redirects=False)
    assert result.status_code == 303
    with SessionLocal() as db:
        original = db.get(BodyMeasurement, mid)
        assert (original.weight_kg, original.waist_cm) == (800, 90)
        head = next(r for r in bp.list_measurements(db, owner) if r.id != first)
        assert (head.weight_kg, head.waist_cm) == (800, 85)
        op = db.scalar(select(BodyMeasurementOperation).where(
            BodyMeasurementOperation.request_id == payload["request_id"]))
        assert op.changed_fields == ["waist_cm"]
        assert "weight_kg" not in op.provenance_by_changed_field


@pytest.mark.parametrize("operation", ["CREATE", "CORRECT"])
def test_browser_exact_replay_precedes_new_bounds_and_divergence_still_fails(client, monkeypatch, operation):
    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement
    from app.services import body_profile as bp

    mid = prepare(client)
    form_url = "/body/measurements/new" if operation == "CREATE" else f"/body/measurements/{mid}/edit"
    path = "/body/measurements" if operation == "CREATE" else f"/body/measurements/{mid}/edit"
    form = client.get(form_url).text
    payload = {"request_id": hidden(form, "request_id"), "waist_cm": "85"}
    if operation == "CORRECT":
        payload["expected_head_token"] = hidden(form, "expected_head_token")
    assert client.post(path, data=payload, follow_redirects=False).status_code == 303
    specs = [bp.FieldSpec(s.key, s.label, 86, s.max) if s.key == "waist_cm" else s
             for s in bp.BODY_MEASUREMENT_FIELDS]
    monkeypatch.setattr(bp, "BODY_MEASUREMENT_FIELDS", specs)
    assert client.post(path, data=payload, follow_redirects=False).status_code == 303
    divergent = {**payload, "waist_cm": "84"}
    assert client.post(path, data=divergent, follow_redirects=False).status_code == 409
    if operation == "CREATE":
        assert client.post(path, data={**divergent, "request_id": "new-invalid-under-bounds"},
                           follow_redirects=False).status_code == 400
    with SessionLocal() as db:
        assert len(list(db.scalars(select(BodyMeasurement)))) == 2


@pytest.mark.parametrize("value", ["nan", "inf", "-inf"])
def test_browser_structural_parsing_never_accepts_nonfinite_numbers(client, value):
    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement

    mid = prepare(client)
    form = client.get(f"/body/measurements/{mid}/edit").text
    payload = {"request_id": hidden(form, "request_id"),
               "expected_head_token": hidden(form, "expected_head_token"), "waist_cm": value}
    assert client.post(f"/body/measurements/{mid}/edit", data=payload,
                       follow_redirects=False).status_code == 400
    with SessionLocal() as db:
        assert len(list(db.scalars(select(BodyMeasurement)))) == 1
