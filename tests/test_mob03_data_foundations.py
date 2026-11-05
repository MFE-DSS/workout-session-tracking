"""MOB-03 non-destructive canonical readers and sensitive-account foundations."""

from datetime import UTC, datetime

import pytest
from sqlalchemy import update


def test_weight_reader_owns_and_preserves_the_existing_chronology(client):
    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement
    from app.models.user import User
    from app.services import body_profile

    with SessionLocal() as db:
        owner = db.query(User).filter_by(username="testuser").one()
        owner.weight_kg = 99
        other = User(username="other-owner", password_hash=owner.password_hash)
        db.add(other)
        db.flush()
        when = datetime(2026, 1, 2, tzinfo=UTC)
        a = BodyMeasurement(user_id=owner.id, measured_at=when, weight_kg=72)
        b = BodyMeasurement(user_id=owner.id, measured_at=when, weight_kg=73)
        partial = BodyMeasurement(user_id=owner.id, measured_at=when, waist_cm=80)
        foreign = BodyMeasurement(user_id=other.id, measured_at=when, weight_kg=91)
        db.add_all([a, b, partial, foreign])
        db.commit()
        rows = body_profile.list_weight_measurements(db, owner.id, limit=1)
        assert [r.id for r in rows] == [b.id]
        older = body_profile.list_weight_measurements(db, owner.id, before=(when, b.id))
        assert [r.id for r in older] == [a.id]
        assert db.get(BodyMeasurement, foreign.id).weight_kg == 91
        assert owner.weight_kg == 99
        assert db.query(BodyMeasurement).count() == 4


def test_undated_profile_weight_never_creates_a_dated_fact(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services import body_profile

    with SessionLocal() as db:
        owner = db.query(User).filter_by(username="testuser").one()
        owner.weight_kg = 75
        db.commit()
        assert body_profile.list_weight_measurements(db, owner.id) == []


def test_atypical_history_is_returned_without_correction_or_silent_filtering(client):
    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement
    from app.models.user import User
    from app.services import body_profile

    with SessionLocal() as db:
        owner = db.query(User).filter_by(username="testuser").one()
        row = BodyMeasurement(user_id=owner.id, measured_at=datetime(2025, 1, 1), weight_kg=0)
        db.add(row)
        db.commit()
        assert body_profile.list_weight_measurements(db, owner.id)[0].weight_kg == 0
        assert db.get(BodyMeasurement, row.id).weight_kg == 0


@pytest.mark.parametrize("limit", [0, -1, 102, True, "50"])
def test_reader_rejects_invalid_transport_window(client, limit):
    from app.database import SessionLocal
    from app.services import body_profile

    with SessionLocal() as db, pytest.raises(ValueError, match="limit"):
        body_profile.list_weight_measurements(db, 1, limit=limit)


def test_sensitive_account_operation_reauthenticates_canonical_owner(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.account_lifecycle import reauthenticate_account

    with SessionLocal() as db:
        owner = db.query(User).filter_by(username="testuser").one()
        assert reauthenticate_account(db, owner, current_password="testpass").id == owner.id


@pytest.mark.parametrize("mutation", ["wrong_password", "inactive", "epoch", "hash"])
def test_reauthentication_refuses_invalid_or_stale_authority(client, mutation):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.account_lifecycle import AccountRejected, reauthenticate_account

    with SessionLocal() as db:
        owner = db.query(User).filter_by(username="testuser").one()
        if mutation != "wrong_password":
            field = {"inactive": "is_active", "epoch": "session_epoch", "hash": "password_hash"}[
                mutation
            ]
            value = {"inactive": False, "epoch": 1, "hash": "not-the-current-hash"}[mutation]
            with SessionLocal() as changed:
                changed.execute(update(User).where(User.id == owner.id).values(**{field: value}))
                changed.commit()
        password = "wrong-test-only" if mutation == "wrong_password" else "testpass"
        with pytest.raises(AccountRejected, match="Réauthentification") as error:
            reauthenticate_account(db, owner, current_password=password)
        assert password not in str(error.value)
        assert error.value.code == "reauthentication_required"


def test_confirmed_revocation_invalidates_access_refresh_and_web_but_preserves_data(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.account_lifecycle import revoke_account_sessions
    from app.services.device_auth import open_device_session

    with SessionLocal() as db:
        owner = db.query(User).filter_by(username="testuser").one()
        first = open_device_session(db, owner)
        second = open_device_session(db, owner)
        db.commit()
        revoke_account_sessions(db, owner, current_password="testpass")
        db.commit()
        assert owner.session_epoch == 1
        assert db.query(User).count() == 1
    for issued in [first, second]:
        response = client.get(
            "/api/mobile/v1/auth/me", headers={"Authorization": f"Bearer {issued.access_token}"}
        )
        assert response.status_code == 401
        response = client.post(
            "/api/mobile/v1/auth/refresh", json={"refresh_token": issued.refresh_token}
        )
        assert response.status_code == 401
    assert client.get("/", follow_redirects=False).status_code == 303


def test_weight_page_has_explicit_units_dates_and_honest_provenance(client):
    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement
    from app.models.user import User
    from app.services import body_profile as bp

    with SessionLocal() as db:
        user = db.query(User).filter_by(username="testuser").one()
        bp.set_consent(db, user.id, True)
        user.weight_kg = 97
        a = BodyMeasurement(user_id=user.id, measured_at=datetime(2024, 1, 1), weight_kg=72)
        b = BodyMeasurement(user_id=user.id, measured_at=datetime(2024, 1, 2), weight_kg=73)
        db.add_all([a, b])
        db.commit()
        page = bp.weight_history_page(db, user.id, limit=1)
        assert page["state"] == "AVAILABLE"
        assert page["unit"] == "kg"
        assert page["legacy_profile_included"] is False
        row = page["entries"][0]
        assert row["measurement_id"] == b.id
        assert row["value"] == 73
        assert row["measured_at"] == "2024-01-02T00:00:00+00:00"
        assert row["recorded_at"] != row["measured_at"]
        assert row["provenance"] == {
            "origin": "UNKNOWN",
            "acquisition": "UNKNOWN",
            "source_ref": f"body_measurements/{b.id}/weight_kg",
        }
        assert page["next_cursor"] == [row["measured_at"], b.id]
        assert db.query(BodyMeasurement).count() == 2
        assert user.weight_kg == 97


def test_weight_page_requires_existing_explicit_consent_and_keeps_empty_distinct(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services import body_profile as bp

    with SessionLocal() as db:
        user = db.query(User).filter_by(username="testuser").one()
        user.weight_kg = 80
        db.commit()
        assert bp.weight_history_page(db, user.id)["state"] == "CONSENT_REQUIRED"
        assert bp.get_consent(db, user.id) is None
        bp.set_consent(db, user.id, True)
        page = bp.weight_history_page(db, user.id)
        assert page["state"] == "EMPTY"
        assert page["entries"] == []
        assert page["next_cursor"] is None
        bp.set_consent(db, user.id, False)
        assert bp.weight_history_page(db, user.id)["state"] == "CONSENT_REQUIRED"


@pytest.mark.parametrize(
    "value,quality", [(0, "LEGACY_OUTSIDE_CURRENT_BOUNDS"), (float("inf"), "INVALID_NONFINITE")]
)
def test_legacy_quality_is_reported_without_rewriting_or_silently_hiding_the_row(
    client, value, quality
):
    import math

    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement
    from app.models.user import User
    from app.services import body_profile as bp

    with SessionLocal() as db:
        user = db.query(User).filter_by(username="testuser").one()
        bp.set_consent(db, user.id, True)
        row = BodyMeasurement(user_id=user.id, measured_at=datetime(2025, 1, 1), weight_kg=value)
        db.add(row)
        db.commit()
        projected = bp.weight_history_page(db, user.id)["entries"][0]
        assert projected["quality"] == quality
        if math.isfinite(value):
            assert projected["value"] == value
        else:
            assert projected["value"] is None
            assert projected["raw_value_repr"] == "inf"
        assert db.get(BodyMeasurement, row.id).weight_kg == value


def test_equivalent_offset_cursors_have_identical_pages(client):
    from datetime import timedelta, timezone

    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement
    from app.models.user import User
    from app.services import body_profile as bp

    with SessionLocal() as db:
        user = db.query(User).filter_by(username="testuser").one()
        older = BodyMeasurement(
            user_id=user.id, measured_at=datetime(2026, 1, 1, 11, 30), weight_kg=72
        )
        boundary = BodyMeasurement(
            user_id=user.id, measured_at=datetime(2026, 1, 1, 12), weight_kg=73
        )
        db.add_all([older, boundary])
        db.commit()
        utc = datetime(2026, 1, 1, 12, tzinfo=UTC)
        offset = datetime(2026, 1, 1, 13, tzinfo=timezone(timedelta(hours=1)))
        a = bp.list_weight_measurements(db, user.id, before=(utc, boundary.id))
        b = bp.list_weight_measurements(db, user.id, before=(offset, boundary.id))
        assert [r.id for r in a] == [older.id]
        assert [r.id for r in b] == [older.id]
