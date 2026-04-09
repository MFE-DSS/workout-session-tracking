"""Test fixtures: run each test against an isolated on-disk SQLite.

V2 auth: the fixture auto-creates a test user ('testuser' /
'testpass') and logs in via POST /login so the session cookie is
set on the client. All existing tests continue to pass without
modification because the cookie travels with every request.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


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

    with TestClient(main_mod.app) as c:
        # Auto-create a test user and log in so every subsequent
        # request carries the session cookie. This makes all V1
        # tests pass unchanged under the V2 auth layer.
        from app.database import SessionLocal
        from app.models.user import User
        from app.services.auth import hash_password

        with SessionLocal() as db:
            user = User(
                username="testuser",
                password_hash=hash_password("testpass"),
            )
            db.add(user)
            db.commit()

        # Log in via the login route to set the session cookie.
        login_r = c.post(
            "/login",
            data={"username": "testuser", "password": "testpass"},
            follow_redirects=False,
        )
        assert login_r.status_code == 303, f"login failed: {login_r.status_code}"

        yield c

    try:
        os.unlink(db_path)
    except OSError:
        pass
