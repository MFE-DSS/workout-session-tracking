"""Nutrition purpose is never inherited from BODY consent."""

from datetime import UTC, datetime

import pytest
from nutrition_helpers import nutrition_db, nutrition_environment, proof


@pytest.fixture()
def db(tmp_path):
    with nutrition_db(tmp_path) as session:
        yield session


@pytest.fixture(autouse=True)
def controlled_environment(monkeypatch):
    with nutrition_environment(monkeypatch):
        yield


def test_nutrition_flag_is_closed_by_default(monkeypatch):
    from app.config import Settings

    monkeypatch.delenv("NUTRITION_MANUAL_CONTROLLED_TEST_ENABLED")
    assert Settings(_env_file=None).nutrition_manual_controlled_test_enabled is False


def test_body_consent_does_not_grant_nutrition_and_old_wording_is_not_current(db):
    from app.models.body_consent import BodyConsent
    from app.services.nutrition_commands import NutritionError
    from app.services.nutrition_consent import read_consent, require_consent

    db.add(BodyConsent(user_id=1, consent_type="body_measurements", granted=True))
    db.commit()
    assert read_consent(db, 1)["state"] == "ABSENT"
    with pytest.raises(NutritionError, match="consent_required"):
        require_consent(db, 1)
    db.add(BodyConsent(user_id=1, consent_type="nutrition_manual", granted=True,
                       consent_version=0))
    db.commit()
    with pytest.raises(NutritionError, match="consent_required"):
        require_consent(db, 1)


def test_consent_aba_under_frozen_clock_never_reaccepts_an_old_token(db):
    from app.services.nutrition_commands import NutritionError
    from app.services.nutrition_consent import read_consent, set_consent

    now = datetime(2026, 11, 12, tzinfo=UTC)
    initial = read_consent(db, 1)
    first = set_consent(db, 1, initial["consent_token"], True, 1, auth_proof=proof(db), now=now)
    revoked = set_consent(db, 1, first["consent_token"], False, 1, auth_proof=proof(db), now=now)
    again = set_consent(db, 1, revoked["consent_token"], True, 1, auth_proof=proof(db), now=now)
    assert len({initial["consent_token"], first["consent_token"],
                revoked["consent_token"], again["consent_token"]}) == 4
    assert again["granted_at"] > revoked["withdrawn_at"] > first["granted_at"]
    with pytest.raises(NutritionError, match="stale_consent"):
        set_consent(db, 1, first["consent_token"], False, 1, auth_proof=proof(db), now=now)
    assert read_consent(db, 1)["granted"] is True


def test_two_connections_and_stale_auth_cannot_win_consent(db):
    from sqlalchemy.orm import Session

    from app.services.nutrition_commands import NutritionError
    from app.services.nutrition_consent import read_consent, set_consent

    token = read_consent(db, 1)["consent_token"]
    owner_proof = proof(db)
    db.rollback()
    with Session(db.get_bind()) as other:
        result = set_consent(other, 1, token, True, 1, auth_proof=owner_proof)
    with pytest.raises(NutritionError, match="stale_consent"):
        set_consent(db, 1, token, True, 1, auth_proof=owner_proof)
    assert read_consent(db, 1)["consent_token"] == result["consent_token"]
    with pytest.raises(NutritionError, match="authentication_changed"):
        set_consent(db, 1, result["consent_token"], False, 1,
                    auth_proof={**owner_proof, "expected_epoch": 999})
    assert read_consent(db, 1)["granted"] is True


def test_flag_closed_blocks_grant_but_preserves_revocation(db):
    from app.config import get_settings
    from app.services.nutrition_commands import NutritionError
    from app.services.nutrition_consent import read_consent, set_consent

    token = read_consent(db, 1)["consent_token"]
    first = set_consent(db, 1, token, True, 1, auth_proof=proof(db))
    get_settings().nutrition_manual_controlled_test_enabled = False
    revoked = set_consent(db, 1, first["consent_token"], False, 1, auth_proof=proof(db))
    assert revoked["granted"] is False
    with pytest.raises(NutritionError, match="acquisition_unavailable"):
        set_consent(db, 1, revoked["consent_token"], True, 1, auth_proof=proof(db))


def test_unicode_consent_token_is_a_rejection_not_a_server_error(db):
    from app.services.nutrition_commands import NutritionError
    from app.services.nutrition_consent import read_consent, set_consent

    with pytest.raises(NutritionError):
        set_consent(db, 1, "\N{FIRE}", True, 1, auth_proof=proof(db))
    assert read_consent(db, 1)["state"] == "ABSENT"
