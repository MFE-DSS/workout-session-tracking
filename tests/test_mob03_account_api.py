"""MOB-03 — account JSON contracts through the real app and database."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest

API = "/api/mobile/v1"
PASSWORD = "a-test-passphrase"


def register(client, **overrides):
    body = {
        "username": "mobile-new",
        "password": PASSWORD,
        "password_confirm": PASSWORD,
        "email": "",
        "device_label": "test iPhone",
    }
    body.update(overrides)
    return client.post(f"{API}/auth/register", json=body)


def user_count(username):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        return db.query(User).filter_by(username=username).count()


def test_register_creates_one_account_with_bearer_pair_and_no_web_cookie(client):
    response = register(client)
    assert response.status_code == 201
    result = response.json()
    assert set(result) == {
        "token_type",
        "access_token",
        "access_expires_in",
        "refresh_token",
        "server_now",
        "user",
    }
    assert result["token_type"] == "Bearer"
    assert result["user"]["username"] == "mobile-new"
    assert result["access_expires_in"] == 900
    assert "set-cookie" not in response.headers
    assert response.headers["cache-control"] == "no-store"
    assert user_count("mobile-new") == 1
    client.cookies.clear()
    me = client.get(f"{API}/auth/me", headers={"Authorization": "Bearer " + result["access_token"]})
    assert me.status_code == 200
    assert me.json() == result["user"]


def test_register_normalizes_username_and_optional_email_without_profile_defaults(client):
    response = register(client, username="  mobile-new  ", email="  QA@EXAMPLE.COM ")
    assert response.status_code == 201
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.auth import verify_password

    with SessionLocal() as db:
        user = db.query(User).filter_by(username="mobile-new").one()
        assert user.email == "qa@example.com"
        assert user.height_cm is None and user.weight_kg is None
        assert user.password_hash != PASSWORD
        assert verify_password(PASSWORD, user.password_hash)


@pytest.mark.parametrize(
    ("overrides", "code"),
    [
        ({"username": "ab"}, "username_too_short"),
        ({"username": "a" * 65}, "username_too_long"),
        ({"username": "héllo"}, "invalid_username"),
        ({"username": "bad/name"}, "invalid_username"),
        ({"password": "short", "password_confirm": "short"}, "invalid_password"),
        ({"password": "a" * 73, "password_confirm": "a" * 73}, "invalid_password"),
        ({"password": "é" * 37, "password_confirm": "é" * 37}, "invalid_password"),
        ({"password_confirm": "different"}, "password_mismatch"),
        ({"email": "not-an-email"}, "invalid_email"),
    ],
)
def test_register_rejects_invalid_canonical_fields_without_creating_user(client, overrides, code):
    response = register(client, **overrides)
    assert response.status_code == 400
    assert response.json()["detail"]["error"] == code
    assert "access_token" not in response.json()
    assert user_count(overrides.get("username", "mobile-new").strip()) == 0


def test_replayed_registration_never_creates_another_identity_and_login_recovers(client):
    original = register(client)
    assert original.status_code == 201
    replay = register(client)
    assert replay.status_code == 409
    assert replay.json()["detail"]["error"] == "username_unavailable"
    assert user_count("mobile-new") == 1
    login = client.post(f"{API}/auth/login", json={"username": "mobile-new", "password": PASSWORD})
    assert login.status_code == 200
    assert login.json()["user"] == original.json()["user"]


def test_duplicate_email_is_refused_without_claiming_a_new_account(client):
    assert register(client, email="qa@example.com").status_code == 201
    other = register(client, username="mobile-other", email="QA@EXAMPLE.COM")
    assert other.status_code == 409
    assert other.json()["detail"]["error"] == "email_unavailable"
    assert user_count("mobile-other") == 0


def test_registration_cannot_set_identity_or_physical_fields(client):
    response = register(client, user_id=1, is_active=True, weight_kg=90)
    assert response.status_code == 422
    assert user_count("mobile-new") == 0


def test_registration_uses_same_ip_quota_as_web_signup(client, monkeypatch):
    from app.config import get_settings
    from app.main import _rate_limit_reset_for_tests

    settings = get_settings()
    monkeypatch.setattr(settings, "rate_limit_enabled", True)
    monkeypatch.setattr(settings, "rate_limit_register_max", 1)
    _rate_limit_reset_for_tests()
    web = client.post(
        "/register", data={"username": "ab", "password": PASSWORD, "password_confirm": PASSWORD}
    )
    assert web.status_code == 400
    response = register(client)
    assert response.status_code == 429
    assert int(response.headers["retry-after"]) > 0
    assert user_count("mobile-new") == 0


def test_registration_does_not_log_plaintext_secret(client, caplog):
    secret = "private-signup-sentinel"
    with caplog.at_level("DEBUG"):
        response = register(client, password=secret, password_confirm=secret)
    assert response.status_code == 201
    assert secret not in caplog.text


def test_concurrent_registrations_hit_real_unique_constraint_without_a_500(client, monkeypatch):
    from app.services import account_lifecycle

    barrier = Barrier(2)
    real_hash = account_lifecycle.hash_password

    def simultaneous_hash(password):
        hashed = real_hash(password)
        barrier.wait(timeout=15)
        return hashed

    monkeypatch.setattr(account_lifecycle, "hash_password", simultaneous_hash)
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(register, client) for _ in range(2)]
        responses = [future.result(timeout=25) for future in futures]
    assert sorted(response.status_code for response in responses) == [201, 409]
    assert user_count("mobile-new") == 1


def login(client, password="testpass"):
    response = client.post(f"{API}/auth/login", json={"username": "testuser", "password": password})
    assert response.status_code == 200
    return response.json()


def change(client, token, **overrides):
    body = {
        "current_password": "testpass",
        "new_password": "new-test-passphrase",
        "new_password_confirm": "new-test-passphrase",
    }
    body.update(overrides)
    return client.post(
        f"{API}/auth/password",
        json=body,
        headers={"Authorization": "Bearer " + token} if token else {},
    )


def test_password_change_revokes_all_old_credentials_and_reissues_caller_pair(client):
    first, second = login(client), login(client)
    response = change(client, first["access_token"])
    assert response.status_code == 200
    updated = response.json()
    assert updated["user"] == first["user"]
    assert updated["access_token"] != first["access_token"]
    assert response.headers["cache-control"] == "no-store"
    assert "set-cookie" not in response.headers
    for old in (first, second):
        assert (
            client.get(
                f"{API}/auth/me", headers={"Authorization": "Bearer " + old["access_token"]}
            ).status_code
            == 401
        )
        assert (
            client.post(
                f"{API}/auth/refresh", json={"refresh_token": old["refresh_token"]}
            ).status_code
            == 401
        )
    web = client.get("/profile", follow_redirects=False)
    assert web.status_code == 303 and web.headers["location"] == "/login"
    assert (
        client.get(
            f"{API}/auth/me", headers={"Authorization": "Bearer " + updated["access_token"]}
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"{API}/auth/login", json={"username": "testuser", "password": "testpass"}
        ).status_code
        == 401
    )
    assert login(client, "new-test-passphrase")["user"] == first["user"]


@pytest.mark.parametrize(
    ("overrides", "code"),
    [
        ({"current_password": "wrong"}, "invalid_current_password"),
        ({"new_password": "short", "new_password_confirm": "short"}, "invalid_password"),
        ({"new_password": "é" * 37, "new_password_confirm": "é" * 37}, "invalid_password"),
        ({"new_password_confirm": "different"}, "password_mismatch"),
    ],
)
def test_refused_password_change_preserves_password_epoch_and_access(client, overrides, code):
    original = login(client)
    response = change(client, original["access_token"], **overrides)
    assert response.status_code == 400
    assert response.json()["detail"]["error"] == code
    assert (
        client.get(
            f"{API}/auth/me", headers={"Authorization": "Bearer " + original["access_token"]}
        ).status_code
        == 200
    )
    assert login(client)["user"] == original["user"]


def test_overlong_current_password_is_rejected_before_bcrypt(client, monkeypatch):
    original = login(client)
    from app.services import account_lifecycle

    def forbidden_verify(*args):
        pytest.fail("overlong secret must never reach bcrypt")

    monkeypatch.setattr(account_lifecycle, "verify_password", forbidden_verify)
    response = change(client, original["access_token"], current_password="é" * 37)
    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "invalid_current_password"


def test_legacy_short_current_password_can_be_replaced(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.auth import hash_password

    with SessionLocal() as db:
        user = db.query(User).filter_by(username="testuser").one()
        user.password_hash = hash_password("old")
        db.commit()
    original = login(client, "old")
    response = change(client, original["access_token"], current_password="old")
    assert response.status_code == 200
    assert login(client, "new-test-passphrase")["user"] == original["user"]


def test_password_change_requires_bearer_even_with_valid_web_cookie(client):
    assert client.get("/profile").status_code == 200
    response = change(client, None)
    assert response.status_code == 401
    assert login(client)["user"]["username"] == "testuser"


def test_password_change_rejects_foreign_identity_fields(client):
    original = login(client)
    response = change(client, original["access_token"], user_id=999, username="someone-else")
    assert response.status_code == 422
    assert login(client)["user"] == original["user"]


def test_password_change_shares_login_guessing_quota(client, monkeypatch):
    original = login(client)
    from app.config import get_settings
    from app.main import _rate_limit_reset_for_tests

    settings = get_settings()
    monkeypatch.setattr(settings, "rate_limit_enabled", True)
    monkeypatch.setattr(settings, "rate_limit_login_max", 1)
    _rate_limit_reset_for_tests()
    assert change(client, original["access_token"], current_password="wrong").status_code == 400
    blocked = client.post(
        f"{API}/auth/login", json={"username": "testuser", "password": "testpass"}
    )
    assert blocked.status_code == 429
    assert int(blocked.headers["retry-after"]) > 0


def test_password_change_does_not_log_plaintext_secret(client, caplog):
    original = login(client)
    secret = "private-change-sentinel"
    with caplog.at_level("DEBUG"):
        response = change(
            client, original["access_token"], new_password=secret, new_password_confirm=secret
        )
    assert response.status_code == 200
    assert secret not in caplog.text


def test_concurrent_password_changes_cannot_reissue_credentials_at_a_stale_epoch(
    client, monkeypatch
):
    first, second = login(client), login(client)
    from app.services import account_lifecycle

    barrier = Barrier(2)
    real_hash = account_lifecycle.hash_password

    def simultaneous_hash(password):
        hashed = real_hash(password)
        barrier.wait(timeout=15)
        return hashed

    monkeypatch.setattr(account_lifecycle, "hash_password", simultaneous_hash)
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [
            pool.submit(
                change,
                client,
                pair["access_token"],
                new_password=f"new-passphrase-{i}",
                new_password_confirm=f"new-passphrase-{i}",
            )
            for i, pair in enumerate((first, second))
        ]
        responses = [future.result(timeout=25) for future in futures]
    assert sorted(response.status_code for response in responses) == [200, 409]
    winner = next(response.json() for response in responses if response.status_code == 200)
    loser = next(response.json() for response in responses if response.status_code == 409)
    assert loser["detail"]["error"] == "credentials_changed"
    assert (
        client.get(
            f"{API}/auth/me", headers={"Authorization": "Bearer " + winner["access_token"]}
        ).status_code
        == 200
    )
    for old in (first, second):
        assert (
            client.get(
                f"{API}/auth/me", headers={"Authorization": "Bearer " + old["access_token"]}
            ).status_code
            == 401
        )


@pytest.mark.parametrize("case", ["missing", "invalid_type", "unexpected"])
def test_registration_validation_errors_do_not_reflect_raw_credentials(client, caplog, case):
    secret = "private-register-validation-sentinel"
    body = {"username": "mobile-new", "password": secret, "password_confirm": secret}
    if case == "missing":
        body.pop("username")
    elif case == "invalid_type":
        body["password"] = {"nested": secret}
    else:
        body["unexpected"] = secret
    with caplog.at_level("DEBUG"):
        response = client.post(f"{API}/auth/register", json=body)
    assert response.status_code == 422
    assert secret not in response.text
    assert secret not in caplog.text
    assert response.headers["cache-control"] == "no-store"
    for error in response.json()["detail"]:
        assert error["loc"][0] == "body"
        assert "type" in error and "msg" in error
        assert "input" not in error and "ctx" not in error
    assert user_count("mobile-new") == 0


@pytest.mark.parametrize("case", ["missing", "invalid_type", "unexpected"])
def test_password_validation_errors_do_not_reflect_raw_credentials(client, caplog, case):
    original = login(client)
    secret = "private-change-validation-sentinel"
    body = {"current_password": secret, "new_password": secret, "new_password_confirm": secret}
    if case == "missing":
        body.pop("new_password_confirm")
    elif case == "invalid_type":
        body["current_password"] = {"nested": secret}
    else:
        body["unexpected"] = secret
    with caplog.at_level("DEBUG"):
        response = client.post(
            f"{API}/auth/password",
            json=body,
            headers={"Authorization": "Bearer " + original["access_token"]},
        )
    assert response.status_code == 422
    assert secret not in response.text
    assert secret not in caplog.text
    assert response.headers["cache-control"] == "no-store"
    for error in response.json()["detail"]:
        assert error["loc"][0] == "body"
        assert "input" not in error and "ctx" not in error
    assert (
        client.get(
            f"{API}/auth/me", headers={"Authorization": "Bearer " + original["access_token"]}
        ).status_code
        == 200
    )
