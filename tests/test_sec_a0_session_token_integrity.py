"""Sb_SEC_A0_SESSION_TOKEN_INTEGRITY_01 — invariants I1 à I9 du contrat de jeton web.

Chaque invariant est prouvé par une requête HTTP réelle sur le produit et un état relu — jamais
par une lecture du code (spec §3). Dépôt public : ces tests énoncent des invariants, pas une
procédure.
"""

from __future__ import annotations

import ast
from pathlib import Path

from itsdangerous import URLSafeTimedSerializer
from sqlalchemy import select

from tests.helpers import get_test_user_id

ROOT = Path(__file__).resolve().parents[1]
PASSWORD = "testpass"
NEW_PASSWORD = "nouveau-mot-de-passe-solide"


def _cookie(client) -> str:
    from app.services.auth import SESSION_COOKIE

    token = client.cookies.get(SESSION_COOKIE)
    assert token
    return token


def _authenticated_with(client, token: str) -> bool:
    """Présente `token` comme session et dit si le produit sert une page privée."""
    from app.services.auth import SESSION_COOKIE

    client.cookies.clear()
    client.cookies.set(SESSION_COOKIE, token)
    response = client.get("/profile", follow_redirects=False)
    return response.status_code == 200


def _user(uid):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        return db.execute(select(User).where(User.id == uid)).scalar_one()


# ── I1 / I2 / I3 : le type d'un jeton est vérifié à la lecture


def test_reset_credential_never_authenticates_a_session(client):
    from app.services.auth import create_reset_token

    uid = get_test_user_id()
    reset = create_reset_token(uid, _user(uid).session_epoch)
    assert _authenticated_with(client, reset) is False
    home = client.get("/", follow_redirects=False)
    assert home.status_code in (302, 303, 307)
    assert "testuser" not in home.text


def test_session_credential_never_authorizes_a_reset(client):
    session = _cookie(client)
    page = client.get(f"/reset/{session}")
    assert page.status_code == 200
    submit = client.post(f"/reset/{session}", data={"new_password": NEW_PASSWORD,
                                                    "new_password_confirm": NEW_PASSWORD})
    assert submit.status_code == 400


def test_token_without_known_purpose_is_refused(client):
    from app.services.auth import SESSION_SALT

    uid = get_test_user_id()
    secret = "test-secret-key-for-signing"
    signer = URLSafeTimedSerializer(secret, salt=SESSION_SALT)
    for payload in ({"user_id": uid, "epoch": 0}, {"user_id": uid, "epoch": 0, "purpose": "other"},
                    {"user_id": uid, "epoch": 0, "purpose": "reset"}):
        assert _authenticated_with(client, signer.dumps(payload)) is False, payload


def test_usages_are_separated_at_the_signature_itself():
    """Défense en profondeur : le champ `purpose` suffit à tenir I2/I3 (contre-preuve du
    2026-10-24), donc le sel par usage n'est observable par aucune requête. Cette garde le tient
    explicitement — un jeton d'un usage ne se VÉRIFIE même pas sous l'autre, ni sous le sel
    d'avant ce contrat."""
    import pytest
    from itsdangerous import BadSignature

    from app.services import auth

    reset = auth.create_reset_token(1, 0)
    session = auth._sign(auth.PURPOSE_SESSION, 1, 0)
    assert auth.SESSION_SALT != auth.RESET_SALT
    assert "itsdangerous" not in (auth.SESSION_SALT, auth.RESET_SALT)
    session_signer = auth._serializer(auth.PURPOSE_SESSION)
    reset_signer = auth._serializer(auth.PURPOSE_RESET)
    with pytest.raises(BadSignature):
        session_signer.loads(reset)
    with pytest.raises(BadSignature):
        reset_signer.loads(session)


def test_a_genuine_session_is_still_accepted(client):
    assert _authenticated_with(client, _cookie(client)) is True


# ── I4 / I5 : changement de mot de passe ⇒ révocation, la session courante est ré-émise


def test_password_change_revokes_prior_sessions(client):
    other_device = _cookie(client)
    response = client.post("/profile/password", data={"current_password": PASSWORD,
                                                      "new_password": NEW_PASSWORD,
                                                      "new_password_confirm": NEW_PASSWORD})
    assert response.status_code == 200
    reissued = _cookie(client)
    assert reissued != other_device
    assert _authenticated_with(client, other_device) is False
    assert _authenticated_with(client, reissued) is True


# ── I4 / I6 : réinitialisation ⇒ révocation, et le lien ne sert qu'une fois


def test_password_reset_revokes_sessions_and_is_single_use(client):
    from app.services.auth import create_reset_token

    uid = get_test_user_id()
    session = _cookie(client)
    link = create_reset_token(uid, _user(uid).session_epoch)
    client.cookies.clear()
    first = client.post(f"/reset/{link}", data={"new_password": NEW_PASSWORD,
                                                "new_password_confirm": NEW_PASSWORD},
                        follow_redirects=False)
    assert first.status_code == 303
    assert _authenticated_with(client, session) is False
    client.cookies.clear()
    again = client.post(f"/reset/{link}", data={"new_password": "encore-un-autre-secret",
                                                "new_password_confirm": "encore-un-autre-secret"})
    assert again.status_code == 400
    assert client.get(f"/reset/{link}").status_code == 200


def test_a_used_reset_link_resolves_to_nobody(client):
    from app.database import SessionLocal
    from app.services.auth import create_reset_token, resolve_reset_user

    uid = get_test_user_id()
    link = create_reset_token(uid, _user(uid).session_epoch)
    client.post(f"/reset/{link}", data={"new_password": NEW_PASSWORD, "new_password_confirm": NEW_PASSWORD})
    with SessionLocal() as db:
        assert resolve_reset_user(db, link) is None


# ── I4 / I7 : déconnexion ⇒ révocation côté serveur


def test_logout_revokes_the_presented_session_server_side(client):
    """Forme E (choix opérateur) : la déconnexion ferme toutes les sessions web de l'utilisateur,
    y compris le jeton copié avant, rejoué après."""
    copied = _cookie(client)
    client.post("/logout", follow_redirects=False)
    assert _authenticated_with(client, copied) is False


def test_logging_in_again_after_logout_works(client):
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()
    response = client.post("/login", data={"username": "testuser", "password": PASSWORD}, follow_redirects=False)
    assert response.status_code == 303
    assert _authenticated_with(client, _cookie(client)) is True


# ── §2.2 T1 : tout jeton émis avant le déploiement est refusé


def test_tokens_issued_before_deploy_are_refused(client):
    uid = get_test_user_id()
    legacy = URLSafeTimedSerializer("test-secret-key-for-signing")
    for payload in ({"user_id": uid}, {"user_id": uid, "purpose": "reset"}):
        assert _authenticated_with(client, legacy.dumps(payload)) is False, payload


# ── I8 : un compte inactif n'est jamais authentifié


def test_inactive_user_is_never_authenticated(client):
    from app.database import SessionLocal
    from app.models.user import User

    token = _cookie(client)
    with SessionLocal() as db:
        user = db.execute(select(User).where(User.id == get_test_user_id())).scalar_one()
        user.is_active = False
        db.commit()
    assert _authenticated_with(client, token) is False


# ── I9 : aucune décision d'authentification ne lit une heure fournie par le client


def test_auth_never_reads_client_time():
    tree = ast.parse((ROOT / "app" / "services" / "auth.py").read_text(encoding="utf-8"))
    attributes = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    assert not attributes & {"headers", "query_params", "form", "json"}
    keywords = [k for n in ast.walk(tree) if isinstance(n, ast.Call) for k in n.keywords if k.arg == "max_age"]
    assert keywords
    for kw in keywords:
        assert isinstance(kw.value, ast.Name), ast.unparse(kw.value)
