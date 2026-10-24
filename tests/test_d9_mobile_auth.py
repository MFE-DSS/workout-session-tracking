"""`D9` — authentification des appareils : les gardes de sécurité (`§15`).

Chaque garde vise un contrat, pas une implémentation : elle passe par les routes
réelles de `/api/mobile/v1`, et compare à des LITTÉRAUX du contrat plutôt qu'aux
constantes du module — une permutation des constantes ne doit pas la laisser verte.
"""
from __future__ import annotations

import logging

import pytest

API = "/api/mobile/v1"


def _uid() -> int:
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        return db.query(User).filter_by(username="testuser").one().id


def _login(client, password: str = "testpass") -> dict:
    """Connexion RÉELLE : bcrypt compris."""
    return client.post(f"{API}/auth/login", json={
        "username": "testuser", "password": password, "device_label": "iPhone de test"})


def _mint(user_id: int | None = None) -> dict:
    """Une session d'appareil émise par le service de production, sans bcrypt."""
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.device_auth import open_device_session

    with SessionLocal() as db:
        user = db.get(User, user_id or _uid())
        issued = open_device_session(db, user, device_label="test")
        db.commit()
    return {"access_token": issued.access_token, "refresh_token": issued.refresh_token,
            "dsid": issued.device_session_id}


def _bearer(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _me(client, token: str, *, cookies: bool = False):
    if not cookies:
        client.cookies.clear()
    return client.get(f"{API}/auth/me", headers=_bearer(token))


def _refresh(client, token: str):
    return client.post(f"{API}/auth/refresh", json={"refresh_token": token})


def _revoke_all(user_id: int) -> None:
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.auth import revoke_sessions

    with SessionLocal() as db:
        revoke_sessions(db.get(User, user_id))
        db.commit()


# ───────── le parcours nominal ─────────


def test_login_returns_a_bearer_pair_and_no_internals(client):
    r = _login(client)
    assert r.status_code == 200
    body = r.json()
    assert set(body) == {"token_type", "access_token", "access_expires_in",
                         "refresh_token", "server_now", "user"}
    assert body["token_type"] == "Bearer"
    assert body["access_expires_in"] == 900          # quinze minutes, littéral du contrat
    assert body["user"] == {"id": _uid(), "username": "testuser"}
    assert body["refresh_token"].startswith("rt1.")
    assert r.headers["cache-control"] == "no-store"


def test_a_wrong_password_is_a_401_that_says_nothing_more(client):
    r = _login(client, "wrong")
    assert r.status_code == 401
    assert r.json() == {"detail": {"error": "invalid_credentials"}}


def test_an_unknown_user_gets_the_same_answer(client):
    r = client.post(f"{API}/auth/login", json={"username": "nobody", "password": "x"})
    assert r.status_code == 401
    assert r.json() == {"detail": {"error": "invalid_credentials"}}


def test_the_access_token_opens_the_api(client):
    t = _mint()
    r = _me(client, t["access_token"])
    assert r.status_code == 200
    assert r.json()["username"] == "testuser"


def test_refresh_rotates_both_tokens(client):
    t = _mint()
    r = _refresh(client, t["refresh_token"])
    assert r.status_code == 200
    neuf = r.json()
    assert neuf["refresh_token"] != t["refresh_token"]
    assert neuf["refresh_token"].split(".")[1] == t["dsid"]    # même appareil
    assert _me(client, neuf["access_token"]).status_code == 200


def test_the_refresh_secret_is_stored_only_as_a_digest(client):
    import hashlib

    from app.database import SessionLocal
    from app.models.device_session import DeviceSession

    t = _mint()
    secret = t["refresh_token"].split(".", 2)[2]
    with SessionLocal() as db:
        ds = db.get(DeviceSession, t["dsid"])
        assert ds.refresh_hash == hashlib.sha256(secret.encode()).hexdigest()
        assert secret not in (ds.refresh_hash, ds.id, ds.device_label or "")


# ───────── §15 — usages séparés ─────────


def test_an_access_token_cannot_refresh(client):
    t = _mint()
    assert _refresh(client, t["access_token"]).status_code == 401


def test_a_refresh_token_cannot_call_the_resource_api(client):
    t = _mint()
    r = _me(client, t["refresh_token"])
    assert r.status_code == 401
    assert r.headers["www-authenticate"] == "Bearer"


def test_the_web_cookie_does_not_open_the_api(client):
    """La fixture porte un cookie de session web VALIDE : il ne doit rien ouvrir ici."""
    assert client.get("/").status_code == 200, "prémisse : le cookie est valide sur le web"
    r = client.get(f"{API}/auth/me")
    assert r.status_code == 401


def test_an_access_token_does_not_open_a_web_route(client):
    t = _mint()
    client.cookies.clear()
    r = client.get("/", headers=_bearer(t["access_token"]), follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/login"


def test_a_web_session_cookie_value_is_not_an_access_token(client):
    from starlette.responses import Response

    from app.services.auth import create_session_cookie

    probe = Response()
    create_session_cookie(probe, _uid())
    cookie_value = probe.headers["set-cookie"].split(";")[0].split("=", 1)[1]
    assert _me(client, cookie_value).status_code == 401


def test_the_three_signing_salts_are_distinct():
    import importlib

    auth = importlib.import_module("app.services.auth")
    device_auth = importlib.import_module("app.services.device_auth")
    assert len({auth.SESSION_SALT, auth.RESET_SALT, device_auth.ACCESS_SALT}) == 3


# ───────── §15 — révocation ─────────


def test_a_revoked_refresh_cannot_refresh(client):
    t = _mint()
    client.cookies.clear()
    assert client.post(f"{API}/auth/logout",
                       headers=_bearer(t["access_token"])).status_code == 204
    assert _refresh(client, t["refresh_token"]).status_code == 401
    assert _me(client, t["access_token"]).status_code == 401


def test_mobile_logout_revokes_only_its_own_device(client):
    a, b = _mint(), _mint()
    client.cookies.clear()
    client.post(f"{API}/auth/logout", headers=_bearer(a["access_token"]))
    assert _me(client, a["access_token"]).status_code == 401
    assert _me(client, b["access_token"]).status_code == 200
    assert _refresh(client, b["refresh_token"]).status_code == 200


def test_mobile_logout_leaves_the_web_session_open(client):
    t = _mint()
    jar = dict(client.cookies)
    client.cookies.clear()
    client.post(f"{API}/auth/logout", headers=_bearer(t["access_token"]))
    client.cookies.update(jar)
    assert client.get("/", follow_redirects=False).status_code == 200


def test_an_old_rotated_refresh_cannot_be_reused(client):
    t = _mint()
    assert _refresh(client, t["refresh_token"]).status_code == 200
    assert _refresh(client, t["refresh_token"]).status_code == 401


def test_reusing_an_old_refresh_revokes_the_whole_device(client):
    """Le jeton ancien a été copié : la paire courante est compromise aussi."""
    t = _mint()
    second = _refresh(client, t["refresh_token"]).json()
    _refresh(client, t["refresh_token"])
    assert _refresh(client, second["refresh_token"]).status_code == 401
    assert _me(client, second["access_token"]).status_code == 401


def test_a_forged_secret_on_a_real_device_id_is_refused(client):
    t = _mint()
    forged = f"rt1.{t['dsid']}.{'A' * 43}"
    assert _refresh(client, forged).status_code == 401


@pytest.mark.parametrize("garbage", ["", "rt1", "rt1..", "rt2.x.y", "x.y.z", "rt1.nope.secret"])
def test_malformed_refresh_tokens_are_refused(client, garbage):
    r = client.post(f"{API}/auth/refresh", json={"refresh_token": garbage or "x"})
    assert r.status_code in (401, 422)


def test_the_a0_epoch_invalidates_device_sessions(client):
    t = _mint()
    _revoke_all(_uid())
    assert _me(client, t["access_token"]).status_code == 401
    assert _refresh(client, t["refresh_token"]).status_code == 401


def test_web_logout_also_closes_the_mobile_sessions(client):
    """Forme E de `A0` : « se déconnecter » ferme tout, application comprise."""
    t = _mint()
    client.post("/logout", follow_redirects=False)
    assert _me(client, t["access_token"]).status_code == 401
    assert _refresh(client, t["refresh_token"]).status_code == 401


def test_a_password_reset_invalidates_device_sessions(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.auth import create_reset_token

    t = _mint()
    with SessionLocal() as db:
        u = db.get(User, _uid())
        token = create_reset_token(u.id, u.session_epoch)
    r = client.post(f"/reset/{token}",
                    data={"new_password": "newpass123", "new_password_confirm": "newpass123"},
                    follow_redirects=False)
    assert r.status_code == 303, r.text[:300]
    with SessionLocal() as db:
        assert db.get(User, _uid()).session_epoch >= 1, "prémisse : la réinitialisation a eu lieu"
    assert _me(client, t["access_token"]).status_code == 401
    assert _refresh(client, t["refresh_token"]).status_code == 401


def test_an_inactive_user_is_rejected_everywhere(client):
    from app.database import SessionLocal
    from app.models.user import User

    t = _mint()
    with SessionLocal() as db:
        db.get(User, _uid()).is_active = False
        db.commit()
    assert _me(client, t["access_token"]).status_code == 401
    assert _refresh(client, t["refresh_token"]).status_code == 401
    assert _login(client).status_code == 401


def test_an_idle_device_must_log_in_again(client):
    from datetime import timedelta

    from app.database import SessionLocal
    from app.models.device_session import DeviceSession

    t = _mint()
    with SessionLocal() as db:
        ds = db.get(DeviceSession, t["dsid"])
        ds.last_used_at = ds.last_used_at - timedelta(days=31)
        db.commit()
    assert _refresh(client, t["refresh_token"]).status_code == 401


# ───────── §15 — le temps du serveur, seul ─────────


def test_an_expired_access_token_is_refused_by_server_time(client, monkeypatch):
    import time

    from app.services import device_auth

    vrai = time.time
    monkeypatch.setattr(time, "time", lambda: vrai() - 16 * 60)
    t = _mint()
    monkeypatch.setattr(time, "time", vrai)
    # Un client qui prétend être dans le passé ne change rien.
    r = client.get(f"{API}/auth/me", headers={**_bearer(t["access_token"]),
                                               "Date": "Mon, 01 Jan 2001 00:00:00 GMT"})
    assert r.status_code == 401
    assert device_auth.ACCESS_MAX_AGE == 900


def test_client_performed_at_cannot_affect_auth(client):
    """Une série datée n'importe comment n'ouvre ni ne ferme une session."""
    t = _mint()
    client.cookies.clear()
    r = client.put(f"{API}/sessions/999999/sets/1", headers=_bearer(t["access_token"]),
                   json={"op_id": "op-time-0001", "weight_kg": 10, "reps": 8,
                         "performed_at": "2099-01-01T00:00:00Z"})
    assert r.status_code == 404
    assert _me(client, t["access_token"]).status_code == 200
    forged = client.put(f"{API}/sessions/999999/sets/1",
                        headers=_bearer("x"), json={"op_id": "op-time-0002", "reps": 8,
                                                    "performed_at": "2001-01-01T00:00:00Z"})
    assert forged.status_code == 401


# ───────── §15 — aucun secret dans les journaux ─────────


def test_the_refresh_secret_never_appears_in_logs(client, caplog):
    caplog.set_level(logging.DEBUG)
    body = _login(client).json()
    secret = body["refresh_token"].split(".", 2)[2]
    neuf = _refresh(client, body["refresh_token"]).json()
    secret2 = neuf["refresh_token"].split(".", 2)[2]
    client.cookies.clear()
    client.post(f"{API}/auth/logout", headers=_bearer(neuf["access_token"]))
    texte = "\n".join(f"{r.getMessage()} {r.args!r}" for r in caplog.records)
    for s in (secret, secret2, "testpass"):
        assert s not in texte


def test_the_device_auth_module_writes_no_log():
    import ast
    import pathlib

    src = pathlib.Path(__file__).resolve().parents[1] / "app" / "services" / "device_auth.py"
    arbre = ast.parse(src.read_text(encoding="utf-8"))
    noms = {n.id for n in ast.walk(arbre) if isinstance(n, ast.Name)}
    assert not noms & {"logging", "logger", "print"}


# ───────── la connexion mobile partage le quota de la connexion web ─────────


def test_mobile_login_is_rate_limited(client):
    import app.main as main_mod

    assert main_mod._RATE_LIMIT_ROUTES[("POST", f"{API}/auth/login")] == "login"
