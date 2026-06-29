"""Sb_31.X — Body Intelligence v2 flag gate hardening.

BODY_INTELLIGENCE_ENABLED (separate from BODY_ASSESSMENT_ENABLED) must
make the whole Body Intelligence v2 surface invisible when OFF:
  * /body/intelligence → 404 before auth (anon AND authenticated)
  * /coach-report renders NO Body Intelligence snapshot
  * profile page shows NO Body Intelligence link
Flag ON restores the existing behavior. The Manual Body Profile gate
(#17) stays independent.
"""
from __future__ import annotations

import contextlib
import os
import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Distinctive markers rendered only when Body Intelligence is shown.
SNAPSHOT_MARKER = "Snapshot Body Intelligence"  # coach_body_snapshot.html <h2>
PROFILE_LINK_MARKER = "Voir Body Intelligence"   # profile.html discovery link


def _fresh_app_modules() -> None:
    import sys

    for mod_name in [m for m in list(sys.modules) if m == "app" or m.startswith("app.")]:
        sys.modules.pop(mod_name, None)


@contextlib.contextmanager
def _make_client(
    monkeypatch: pytest.MonkeyPatch,
    *,
    bi_enabled: bool,
    body_enabled: bool = False,
    login: bool,
) -> Iterator[TestClient]:
    tmp_dir = tempfile.mkdtemp(prefix="workout-bi-test-")
    db_path = Path(tmp_dir) / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("APP_SECRET_KEY", "test-secret-key-for-signing")
    if bi_enabled:
        monkeypatch.setenv("BODY_INTELLIGENCE_ENABLED", "1")
    else:
        monkeypatch.delenv("BODY_INTELLIGENCE_ENABLED", raising=False)
    if body_enabled:
        monkeypatch.setenv("BODY_ASSESSMENT_ENABLED", "1")
    else:
        monkeypatch.delenv("BODY_ASSESSMENT_ENABLED", raising=False)

    _fresh_app_modules()
    from app import main as main_mod  # noqa: E402

    # Enter the TestClient context so lifespan (init_db + seed) runs
    # BEFORE we create the test user.
    with TestClient(main_mod.app) as c:
        if login:
            from app.database import SessionLocal
            from app.models.user import User
            from app.services.auth import hash_password

            with SessionLocal() as db:
                db.add(
                    User(username="testuser", password_hash=hash_password("testpass"))
                )
                db.commit()
            r = c.post(
                "/login",
                data={"username": "testuser", "password": "testpass"},
                follow_redirects=False,
            )
            assert r.status_code == 303
        yield c

    try:
        os.unlink(db_path)
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Flag OFF — Body Intelligence v2 fully invisible.
# ---------------------------------------------------------------------------


def test_bi_off_anonymous_intelligence_404(monkeypatch: pytest.MonkeyPatch) -> None:
    with _make_client(monkeypatch, bi_enabled=False, login=False) as c:
        assert c.get("/body/intelligence", follow_redirects=False).status_code == 404


def test_bi_off_authenticated_intelligence_404(monkeypatch: pytest.MonkeyPatch) -> None:
    with _make_client(monkeypatch, bi_enabled=False, login=True) as c:
        assert c.get("/body/intelligence", follow_redirects=False).status_code == 404


def test_bi_off_coach_report_has_no_snapshot(monkeypatch: pytest.MonkeyPatch) -> None:
    with _make_client(monkeypatch, bi_enabled=False, login=True) as c:
        r = c.get("/coach-report")
        assert r.status_code == 200
        assert SNAPSHOT_MARKER not in r.text


def test_bi_off_profile_has_no_link(monkeypatch: pytest.MonkeyPatch) -> None:
    with _make_client(monkeypatch, bi_enabled=False, login=True) as c:
        r = c.get("/profile")
        assert r.status_code == 200
        assert PROFILE_LINK_MARKER not in r.text


# ---------------------------------------------------------------------------
# Flag ON — existing behavior restored.
# ---------------------------------------------------------------------------


def test_bi_on_anonymous_redirects_to_login(monkeypatch: pytest.MonkeyPatch) -> None:
    with _make_client(monkeypatch, bi_enabled=True, login=False) as c:
        r = c.get("/body/intelligence", follow_redirects=False)
        assert r.status_code == 303
        assert "/login" in r.headers.get("location", "")


def test_bi_on_authenticated_intelligence_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    with _make_client(monkeypatch, bi_enabled=True, login=True) as c:
        assert c.get("/body/intelligence").status_code == 200


def test_bi_on_coach_report_has_snapshot(monkeypatch: pytest.MonkeyPatch) -> None:
    with _make_client(monkeypatch, bi_enabled=True, login=True) as c:
        r = c.get("/coach-report")
        assert r.status_code == 200
        assert SNAPSHOT_MARKER in r.text


def test_bi_on_profile_has_link(monkeypatch: pytest.MonkeyPatch) -> None:
    with _make_client(monkeypatch, bi_enabled=True, login=True) as c:
        r = c.get("/profile")
        assert r.status_code == 200
        assert PROFILE_LINK_MARKER in r.text


# ---------------------------------------------------------------------------
# Independence of the two flags + non-regression.
# ---------------------------------------------------------------------------


def test_flags_are_independent(monkeypatch: pytest.MonkeyPatch) -> None:
    # BI ON but Manual Body Profile OFF: /body stays 404 (#17), while
    # /body/intelligence is reachable (auth-gated).
    with _make_client(
        monkeypatch, bi_enabled=True, body_enabled=False, login=True
    ) as c:
        assert c.get("/body").status_code == 404
        assert c.get("/body/intelligence").status_code == 200

    # Manual Body Profile ON but BI OFF: /body reachable, /body/intelligence 404.
    with _make_client(
        monkeypatch, bi_enabled=False, body_enabled=True, login=True
    ) as c:
        assert c.get("/body").status_code == 200
        assert c.get("/body/intelligence", follow_redirects=False).status_code == 404


def test_bi_off_existing_routes_unchanged(monkeypatch: pytest.MonkeyPatch) -> None:
    with _make_client(monkeypatch, bi_enabled=False, login=False) as c:
        assert c.get("/login").status_code == 200
        for path in ("/history", "/progress", "/physique"):
            r = c.get(path, follow_redirects=False)
            assert r.status_code == 303 and "/login" in r.headers.get("location", ""), path
