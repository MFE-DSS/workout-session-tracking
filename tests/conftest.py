"""Test fixtures: run each test against an isolated on-disk SQLite.

V2 auth: the fixture auto-creates a test user ('testuser' / 'testpass') and puts the client in
an authenticated state. All existing tests continue to pass without modification because the
cookie travels with every request.

Sb_CI_02_2 — auth fast path. The fixture no longer pays bcrypt twice per test. It used to
`hash_password("testpass")` when creating the user and then `POST /login`, which runs
`verify_password` — two bcrypt(cost 12) operations, the single dominant cost of the ~1400
authenticated tests. Instead it stores a **precomputed hash of the very same password** and
mints the session cookie through the **production** `create_session_cookie` contract.

What this does NOT change: one SQLite database per test, the per-test app module reset, the
per-test `TestClient` and its lifespan, xdist, and production authentication behaviour
(including bcrypt cost). Nothing is shared between tests.

The stored hash is a genuine bcrypt hash of "testpass", so tests that exercise the REAL login
route still run the full hash/verify path — `tests/test_auth_fixture_fastpath.py` pins that,
and pins that the hash actually verifies, so a passlib/bcrypt change fails loudly.
"""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

# The auth fast-path contract lives in tests/helpers.py so conftest and its pinning tests share
# one definition. conftest is loaded by pytest under a reserved module name and cannot be
# imported by tests, hence the plain sibling module.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers import TESTPASS_BCRYPT_HASH  # noqa: E402


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    tmp_dir = tempfile.mkdtemp(prefix="workout-test-")
    db_path = Path(tmp_dir) / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("APP_SECRET_KEY", "test-secret-key-for-signing")

    # Reset module-level engine + Base so the new DATABASE_URL sticks.
    import sys

    for mod_name in [m for m in list(sys.modules) if m == "app" or m.startswith("app.")]:
        sys.modules.pop(mod_name, None)

    from app import main as main_mod  # noqa: E402

    try:
        with TestClient(main_mod.app) as c:
            # Auto-create a test user and log in so every subsequent
            # request carries the session cookie. This makes all V1
            # tests pass unchanged under the V2 auth layer.
            from starlette.responses import Response

            from app.database import SessionLocal
            from app.models.user import User
            from app.services.auth import create_session_cookie

            with SessionLocal() as db:
                # Precomputed hash of "testpass" — same password, no bcrypt call here.
                user = User(username="testuser", password_hash=TESTPASS_BCRYPT_HASH)
                db.add(user)
                db.commit()
                db.refresh(user)
                user_id = user.id

            # Establish the already-assumed authenticated state WITHOUT a login round trip.
            # The token is produced by the PRODUCTION helper, so the signing contract is never
            # duplicated here: if it changes, this fixture follows it automatically.
            # Produce the real `Set-Cookie` header with the production helper, then let httpx
            # itself parse it into the jar. This gives byte-for-byte parity with a genuine login
            # (same domain normalisation, same flags), so a later server-side `delete_cookie`
            # matches and logout still works — pinned by test_logout_still_clears_the_session.
            # Hand-setting the jar entry does NOT achieve this: httpx stores a dotless host as
            # `testserver.local` with `domain_specified=False`, which a manual `set(domain=...)`
            # cannot reproduce.
            probe = Response()
            create_session_cookie(probe, user_id)
            c.cookies.extract_cookies(
                httpx.Response(
                    200,
                    headers=[("set-cookie", probe.headers["set-cookie"])],
                    request=httpx.Request("GET", str(c.base_url)),
                )
            )

            yield c
    finally:
        # Sb_OPS_CI_RUNNER_STABILITY_01 (WS4) — remove the WHOLE directory this
        # invocation created, not just the database file inside it.
        #
        # Two defects fixed together. The old cleanup unlinked `test.db` and left
        # the `mkdtemp` directory behind — 53 765 empty directories had
        # accumulated on the development machine. And it sat AFTER the `with`
        # block, so a failing test propagated out of the generator and skipped it
        # entirely: the runs that leaked most were the ones that went wrong.
        #
        # `finally` covers the success path, the failure path and teardown errors.
        # `tmp_dir` is this invocation's own `mkdtemp` result, so the deletion can
        # never reach a shared parent, another worker's directory, or var/workout.db.
        shutil.rmtree(tmp_dir, ignore_errors=True)
