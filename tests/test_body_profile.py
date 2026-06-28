"""Sb_Body_01 — Manual Body Profile MVP tests.

Covers: feature flag OFF, consent gate, ownership, hard-delete, export,
plausibility bounds, ratio fallback/confidence, wording guard, and a
non-regression smoke for the session mode.
"""
from __future__ import annotations

import os
import tempfile
from datetime import UTC
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


def _fresh_app_modules() -> None:
    import sys

    for mod_name in [m for m in list(sys.modules) if m == "app" or m.startswith("app.")]:
        sys.modules.pop(mod_name, None)


@pytest.fixture()
def body_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Like the default `client` fixture but with the Body Assessment
    feature flag ON, so the /body routes are reachable."""
    tmp_dir = tempfile.mkdtemp(prefix="workout-body-test-")
    db_path = Path(tmp_dir) / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("APP_SECRET_KEY", "test-secret-key-for-signing")
    monkeypatch.setenv("BODY_ASSESSMENT_ENABLED", "1")

    _fresh_app_modules()
    from app import main as main_mod  # noqa: E402

    with TestClient(main_mod.app) as c:
        from app.database import SessionLocal
        from app.models.user import User
        from app.services.auth import hash_password

        with SessionLocal() as db:
            db.add(User(username="testuser", password_hash=hash_password("testpass")))
            db.commit()

        login_r = c.post(
            "/login",
            data={"username": "testuser", "password": "testpass"},
            follow_redirects=False,
        )
        assert login_r.status_code == 303
        yield c

    try:
        os.unlink(db_path)
    except OSError:
        pass


def _anon_client(monkeypatch: pytest.MonkeyPatch, *, flag_on: bool) -> TestClient:
    """Build an UN-authenticated TestClient with the Body flag on/off.

    No login is performed, so requests are anonymous — used to assert the
    flag gate fires before the auth layer (Sb_Body_01.1)."""
    tmp_dir = tempfile.mkdtemp(prefix="workout-body-anon-")
    db_path = Path(tmp_dir) / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("APP_SECRET_KEY", "test-secret-key-for-signing")
    if flag_on:
        monkeypatch.setenv("BODY_ASSESSMENT_ENABLED", "1")
    else:
        monkeypatch.delenv("BODY_ASSESSMENT_ENABLED", raising=False)
    _fresh_app_modules()
    from app import main as main_mod  # noqa: E402

    return TestClient(main_mod.app)


@pytest.fixture()
def anon_client_flag_off(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    with _anon_client(monkeypatch, flag_on=False) as c:
        yield c


@pytest.fixture()
def anon_client_flag_on(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    with _anon_client(monkeypatch, flag_on=True) as c:
        yield c


def _current_user_id() -> int:
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        u = db.execute(select(User).where(User.username == "testuser")).scalar_one()
        return u.id


def _grant_consent(c: TestClient) -> None:
    r = c.post("/body/consent", data={"action": "grant"}, follow_redirects=False)
    assert r.status_code == 303


def _count_measurements(user_id: int | None = None) -> int:
    from sqlalchemy import func, select

    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement

    with SessionLocal() as db:
        stmt = select(func.count()).select_from(BodyMeasurement)
        if user_id is not None:
            stmt = stmt.where(BodyMeasurement.user_id == user_id)
        return db.execute(stmt).scalar_one()


# ---------------------------------------------------------------------------
# Feature flag OFF — default client fixture (flag defaults to False).
# ---------------------------------------------------------------------------


def test_feature_flag_off_returns_404(client: TestClient) -> None:
    # Authenticated + flag OFF → 404 on every /body route.
    for path in ("/body", "/body/measurements/new", "/body/export.json"):
        assert client.get(path).status_code == 404
    assert client.post("/body/measurements", data={"waist_cm": "80"}).status_code == 404
    assert client.post("/body/consent", data={"action": "grant"}).status_code == 404


# ---------------------------------------------------------------------------
# Sb_Body_01.1 — flag gate must run BEFORE auth: anonymous + flag OFF → 404
# (not a 303 login redirect), so the feature is fully invisible.
# ---------------------------------------------------------------------------


def test_flag_off_anonymous_all_body_routes_404(anon_client_flag_off: TestClient) -> None:
    c = anon_client_flag_off
    for path in ("/body", "/body/export.json", "/body/measurements/new"):
        assert c.get(path, follow_redirects=False).status_code == 404, path
    assert c.post(
        "/body/consent", data={"action": "grant"}, follow_redirects=False
    ).status_code == 404
    assert c.post(
        "/body/measurements", data={"waist_cm": "80"}, follow_redirects=False
    ).status_code == 404
    # parametrized measurement routes too
    assert c.get(
        "/body/measurements/1/edit", follow_redirects=False
    ).status_code == 404
    assert c.post(
        "/body/measurements/1/delete", follow_redirects=False
    ).status_code == 404


def test_flag_on_anonymous_redirects_to_login(anon_client_flag_on: TestClient) -> None:
    # Flag ON: the feature exists; the auth layer redirects anonymous to
    # /login (existing behavior preserved — NOT a 404).
    r = anon_client_flag_on.get("/body", follow_redirects=False)
    assert r.status_code == 303
    assert "/login" in r.headers.get("location", "")
    assert anon_client_flag_on.get(
        "/body/export.json", follow_redirects=False
    ).status_code == 303


def test_flag_off_does_not_affect_other_routes(anon_client_flag_off: TestClient) -> None:
    # Non-/body routes keep their behavior with the Body flag OFF.
    assert anon_client_flag_off.get("/login").status_code == 200
    for path in ("/history", "/progress", "/physique"):
        r = anon_client_flag_off.get(path, follow_redirects=False)
        assert r.status_code == 303 and "/login" in r.headers.get("location", ""), path


# ---------------------------------------------------------------------------
# Consent gate.
# ---------------------------------------------------------------------------


def test_consent_required_blocks_create(body_client: TestClient) -> None:
    # No consent yet → overview renders the consent prompt.
    r = body_client.get("/body")
    assert r.status_code == 200
    assert "Consentement requis" in r.text

    # POST without consent must not create a row.
    r = body_client.post(
        "/body/measurements", data={"waist_cm": "80"}, follow_redirects=False
    )
    assert r.status_code == 303
    assert _count_measurements() == 0

    # The new-measurement form also redirects away without consent.
    r = body_client.get("/body/measurements/new", follow_redirects=False)
    assert r.status_code == 303


def test_consent_grant_then_create(body_client: TestClient) -> None:
    _grant_consent(body_client)
    assert body_client.get("/body/measurements/new").status_code == 200

    r = body_client.post(
        "/body/measurements",
        data={"waist_cm": "82", "weight_kg": "78", "shoulder_width_cm": "48"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert _count_measurements() == 1

    overview = body_client.get("/body")
    assert overview.status_code == 200
    assert "Épaules / taille" in overview.text


# ---------------------------------------------------------------------------
# Plausibility bounds.
# ---------------------------------------------------------------------------


def test_plausibility_bounds_reject(body_client: TestClient) -> None:
    _grant_consent(body_client)
    r = body_client.post(
        "/body/measurements", data={"weight_kg": "9999"}, follow_redirects=False
    )
    assert r.status_code == 400
    assert _count_measurements() == 0

    # Non-numeric also rejected.
    r = body_client.post(
        "/body/measurements", data={"waist_cm": "abc"}, follow_redirects=False
    )
    assert r.status_code == 400
    assert _count_measurements() == 0


# ---------------------------------------------------------------------------
# Ownership + hard-delete.
# ---------------------------------------------------------------------------


def _make_other_users_measurement() -> int:
    from datetime import datetime

    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement
    from app.models.user import User
    from app.services.auth import hash_password

    with SessionLocal() as db:
        other = User(username="otheruser", password_hash=hash_password("x"))
        db.add(other)
        db.commit()
        db.refresh(other)
        m = BodyMeasurement(
            user_id=other.id, measured_at=datetime.now(UTC), waist_cm=90
        )
        db.add(m)
        db.commit()
        db.refresh(m)
        return m.id


def test_ownership_blocks_foreign_measurement(body_client: TestClient) -> None:
    _grant_consent(body_client)
    foreign_id = _make_other_users_measurement()

    assert body_client.get(f"/body/measurements/{foreign_id}/edit").status_code == 404
    r = body_client.post(
        f"/body/measurements/{foreign_id}/delete", follow_redirects=False
    )
    assert r.status_code == 404
    # Foreign row still present.
    assert _count_measurements() == 1


def test_hard_delete_removes_row(body_client: TestClient) -> None:
    _grant_consent(body_client)
    uid = _current_user_id()
    body_client.post(
        "/body/measurements", data={"waist_cm": "80"}, follow_redirects=False
    )
    assert _count_measurements(uid) == 1

    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement

    with SessionLocal() as db:
        mid = db.execute(
            select(BodyMeasurement.id).where(BodyMeasurement.user_id == uid)
        ).scalar_one()

    r = body_client.post(f"/body/measurements/{mid}/delete", follow_redirects=False)
    assert r.status_code == 303
    assert _count_measurements(uid) == 0


# ---------------------------------------------------------------------------
# Export (user-scoped).
# ---------------------------------------------------------------------------


def test_export_is_user_scoped(body_client: TestClient) -> None:
    _grant_consent(body_client)
    _make_other_users_measurement()  # belongs to otheruser
    body_client.post(
        "/body/measurements", data={"waist_cm": "81"}, follow_redirects=False
    )

    r = body_client.get("/body/export.json")
    assert r.status_code == 200
    payload = r.json()
    assert payload["schema_version"] == 1
    # Only the logged-in user's single measurement.
    assert len(payload["measurements"]) == 1
    assert payload["measurements"][0]["waist_cm"] == 81
    assert any(c["consent_type"] == "body_measurements" for c in payload["consents"])


# ---------------------------------------------------------------------------
# Ratio fallback / confidence (pure logic).
# ---------------------------------------------------------------------------


def test_ratio_fallback_and_confidence() -> None:
    from types import SimpleNamespace

    from app.services.body_profile import compute_ratios

    def by_key(ratios):
        return {r.key: r for r in ratios}

    # Full inputs → shoulder/waist available, not proxy.
    full = SimpleNamespace(
        waist_cm=80, chest_cm=100, shoulder_width_cm=48,
        arm_cm_left=38, arm_cm_right=39,
        thigh_cm_left=58, thigh_cm_right=58,
        calf_cm_left=38, calf_cm_right=38,
    )
    r = by_key(compute_ratios(full, height_cm=180))
    assert r["shoulder_to_waist_ratio"].available is True
    assert r["shoulder_to_waist_ratio"].is_proxy is False
    assert r["shoulder_to_waist_ratio"].confidence == "ok"
    assert r["waist_to_height_ratio"].available is True
    assert r["upper_lower_balance_proxy"].available is True
    assert r["upper_lower_balance_proxy"].is_proxy is False

    # Shoulder missing but chest present → proxy.
    proxy = SimpleNamespace(
        waist_cm=80, chest_cm=100, shoulder_width_cm=None,
        arm_cm_left=None, arm_cm_right=None,
        thigh_cm_left=None, thigh_cm_right=None,
        calf_cm_left=None, calf_cm_right=None,
    )
    r = by_key(compute_ratios(proxy, height_cm=None))
    assert r["shoulder_to_waist_ratio"].available is True
    assert r["shoulder_to_waist_ratio"].is_proxy is True
    assert r["shoulder_to_waist_ratio"].confidence == "proxy"
    # No height → waist/height not computable, no invented value.
    assert r["waist_to_height_ratio"].available is False
    assert r["waist_to_height_ratio"].value is None

    # Empty measurement → nothing computable.
    r = by_key(compute_ratios(None, None))
    assert all(not res.available for res in r.values())


# ---------------------------------------------------------------------------
# Wording guard (non-medical, non-discriminatory).
# ---------------------------------------------------------------------------


def test_wording_guard() -> None:
    from app.services.body_profile import (
        all_user_facing_strings,
        assert_no_forbidden_wording,
    )

    for s in all_user_facing_strings():
        assert_no_forbidden_wording(s)  # must not raise

    for bad in ("Diagnostic de masse grasse", "Type morphotype endomorphe"):
        with pytest.raises(ValueError):
            assert_no_forbidden_wording(bad)


# ---------------------------------------------------------------------------
# Non-regression: session mode still works with the flag ON.
# ---------------------------------------------------------------------------


def test_session_mode_non_regression(body_client: TestClient) -> None:
    # Core pages still render with the Body feature enabled.
    assert body_client.get("/").status_code == 200
    assert body_client.get("/physique").status_code == 200
    assert body_client.get("/history").status_code == 200
