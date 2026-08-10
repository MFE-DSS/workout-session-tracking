"""Pin the auth fast path of the generic `client` fixture (Sb_CI_02_2_AUTH_FIXTURE_FASTPATH).

The fixture stopped calling `hash_password("testpass")` and `POST /login` — two bcrypt(cost 12)
operations per authenticated test. It now stores a precomputed hash of the same password and
mints the cookie through the production `create_session_cookie` contract.

That is a safe optimisation ONLY if all of the following stay true, so each is pinned here:
the client really is authenticated as the real user, the cookie is the production signed cookie,
a tampered or missing cookie is still rejected, logout still works, the REAL login route still
runs the full hash/verify path, and every test still gets its own pristine database with no
state carried over from the previous one.
"""
from __future__ import annotations

from helpers import TESTPASS_BCRYPT_HASH, TESTPASS_PLAIN

# ─────────────────── the precomputed hash is genuine ───────────────────


def test_precomputed_hash_really_is_testpass():
    """If passlib/bcrypt ever stops accepting this digest, fail loudly here rather than
    silently breaking every real-login test."""
    from app.services.auth import verify_password

    assert verify_password(TESTPASS_PLAIN, TESTPASS_BCRYPT_HASH) is True
    assert verify_password("wrong-password", TESTPASS_BCRYPT_HASH) is False
    assert TESTPASS_BCRYPT_HASH.startswith("$2b$12$")


def test_fixture_user_is_stored_with_that_exact_hash(client):
    """The DB row must carry a real bcrypt hash — not a placeholder — so the login route
    behaves exactly as in production."""
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        stored = db.execute(
            select(User.password_hash).where(User.username == "testuser")
        ).scalar_one()
    assert stored == TESTPASS_BCRYPT_HASH


# ─────────────────── the client is genuinely authenticated ───────────────────


def test_generic_client_is_authenticated(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 200


def test_cookie_carries_the_real_user_id(client):
    """The minted cookie must decode, through the production reader, to the actual row id."""
    from sqlalchemy import select
    from starlette.requests import Request

    from app.database import SessionLocal
    from app.models.user import User
    from app.services.auth import SESSION_COOKIE, get_user_id_from_cookie

    with SessionLocal() as db:
        expected = db.execute(select(User.id).where(User.username == "testuser")).scalar_one()

    token = client.cookies.get(SESSION_COOKIE)
    assert token

    scope = {
        "type": "http",
        "headers": [(b"cookie", f"{SESSION_COOKIE}={token}".encode())],
    }
    assert get_user_id_from_cookie(Request(scope)) == expected


# ─────────────────── rejection paths are unchanged ───────────────────


def test_missing_cookie_is_still_rejected(client):
    client.cookies.clear()
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_forged_cookie_signed_with_another_secret_is_rejected(client):
    """A token whose payload is perfectly well-formed but signed with the wrong key must not
    authenticate. Deterministic by construction — unlike flipping a character of the base64
    signature, whose trailing character carries unused bits and can decode to the same bytes."""
    from itsdangerous import URLSafeTimedSerializer

    from app.services.auth import SESSION_COOKIE

    forged = URLSafeTimedSerializer("not-the-app-secret").dumps({"user_id": 1})
    client.cookies.clear()
    client.cookies.set(SESSION_COOKIE, forged)

    response = client.get("/", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_truncated_cookie_is_still_rejected(client):
    """Dropping the signature segment leaves the payload unverifiable."""
    from app.services.auth import SESSION_COOKIE

    token = client.cookies.get(SESSION_COOKIE)
    payload_only = token.split(".")[0]
    client.cookies.clear()
    client.cookies.set(SESSION_COOKIE, payload_only)

    response = client.get("/", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_garbage_cookie_is_still_rejected(client):
    from app.services.auth import SESSION_COOKIE

    client.cookies.clear()
    client.cookies.set(SESSION_COOKIE, "not-a-signed-token")
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 303


def test_logout_still_clears_the_session(client):
    logout = client.post("/logout", follow_redirects=False)
    assert logout.status_code in (303, 302)

    after = client.get("/", follow_redirects=False)
    assert after.status_code == 303
    assert after.headers["location"] == "/login"


# ─────────────────── the REAL login route still runs bcrypt ───────────────────


def test_real_login_route_still_succeeds_with_the_plain_password(client):
    """The production path is untouched: the stored hash verifies against the plain password."""
    client.cookies.clear()
    response = client.post(
        "/login",
        data={"username": "testuser", "password": TESTPASS_PLAIN},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert "session_token" in response.headers.get("set-cookie", "")


def test_real_login_route_still_rejects_a_wrong_password(client):
    client.cookies.clear()
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "definitely-wrong"},
        follow_redirects=False,
    )
    assert response.status_code == 401


def test_login_route_still_calls_verify_password(client, monkeypatch):
    """Guard against a future 'optimisation' that bypasses bcrypt in the production route."""
    import app.routers.auth_routes as auth_routes

    calls: list[tuple[str, str]] = []
    real = auth_routes.verify_password

    def _spy(plain: str, hashed: str) -> bool:
        calls.append((plain, hashed))
        return real(plain, hashed)

    monkeypatch.setattr(auth_routes, "verify_password", _spy)

    client.cookies.clear()
    client.post(
        "/login",
        data={"username": "testuser", "password": TESTPASS_PLAIN},
        follow_redirects=False,
    )
    assert len(calls) == 1
    assert calls[0] == (TESTPASS_PLAIN, TESTPASS_BCRYPT_HASH)


# ─────────────────── isolation: one DB per test, no leakage ───────────────────


def test_owner_isolation_unchanged_non_owner_is_rejected(client):
    """A second user's data must stay invisible to the fixture user."""
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.user import User
    from app.services.user_program_drafts import create_draft

    with SessionLocal() as db:
        other = User(username="fastpath-other", password_hash=TESTPASS_BCRYPT_HASH)
        db.add(other)
        db.commit()
        db.refresh(other)
        other_id = other.id
        foreign = create_draft(db, other_id, "Programme d'un autre", "fastpath-foreign")
        foreign_id = foreign.id
        me = db.execute(select(User.id).where(User.username == "testuser")).scalar_one()

    assert me != other_id
    response = client.get(f"/programs/{foreign_id}", follow_redirects=False)
    assert response.status_code == 404


def test_this_test_writes_a_marker_user(client):
    """Paired with the next test: if databases were shared, the marker would survive."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        db.add(User(username="fastpath-leak-marker", password_hash=TESTPASS_BCRYPT_HASH))
        db.commit()


def test_database_is_pristine_no_marker_from_another_test(client):
    """Order-independent: whichever of the pair runs first, each test owns a fresh DB, so the
    marker must never be visible here."""
    from sqlalchemy import func, select

    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        marker = db.execute(
            select(func.count()).select_from(User).where(User.username == "fastpath-leak-marker")
        ).scalar_one()
        usernames = db.execute(select(User.username)).scalars().all()

    assert marker == 0
    assert usernames == ["testuser"]


def test_cookie_state_does_not_leak_between_tests(client):
    """The previous test cleared/tampered cookies; this one must start authenticated again."""
    from app.services.auth import SESSION_COOKIE

    assert client.cookies.get(SESSION_COOKIE)
    assert client.get("/", follow_redirects=False).status_code == 200
