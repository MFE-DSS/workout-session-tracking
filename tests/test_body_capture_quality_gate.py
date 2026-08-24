"""Sb_Body_02.1 — Capture Quality shell flag gate.

``BODY_CAPTURE_QUALITY_ENABLED`` (séparé de ``BODY_ASSESSMENT_ENABLED``
ET ``BODY_INTELLIGENCE_ENABLED``) doit rendre ``/body/capture-quality``
**invisible** quand OFF :
- 404 avant auth (anonyme ET authentifié)
- aucun lien "capture-quality" exposé nulle part dans l'app

Quand ON :
- anonyme → 303 vers ``/login``
- authentifié → 200 sur le shell statique

Shell strict : aucun ``<script>``, aucun MediaPipe, aucun CDN, aucun
``<form>``, aucun upload, aucun stockage, aucun wording corporel jugeant.
"""
from __future__ import annotations

import contextlib
import os
import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

CAPTURE_LINK_MARKER = "capture-quality"


def _fresh_app_modules() -> None:
    import sys

    for mod_name in [m for m in list(sys.modules) if m == "app" or m.startswith("app.")]:
        sys.modules.pop(mod_name, None)


@contextlib.contextmanager
def _make_client(
    monkeypatch: pytest.MonkeyPatch,
    *,
    capture_enabled: bool,
    body_enabled: bool = False,
    bi_enabled: bool = False,
    login: bool,
) -> Iterator[TestClient]:
    tmp_dir = tempfile.mkdtemp(prefix="workout-capq-test-")
    db_path = Path(tmp_dir) / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("APP_SECRET_KEY", "test-secret-key-for-signing")

    if capture_enabled:
        monkeypatch.setenv("BODY_CAPTURE_QUALITY_ENABLED", "1")
    else:
        monkeypatch.delenv("BODY_CAPTURE_QUALITY_ENABLED", raising=False)
    if body_enabled:
        monkeypatch.setenv("BODY_ASSESSMENT_ENABLED", "1")
    else:
        monkeypatch.delenv("BODY_ASSESSMENT_ENABLED", raising=False)
    if bi_enabled:
        monkeypatch.setenv("BODY_INTELLIGENCE_ENABLED", "1")
    else:
        monkeypatch.delenv("BODY_INTELLIGENCE_ENABLED", raising=False)

    _fresh_app_modules()
    from app import main as main_mod  # noqa: E402

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
# 1. Flag OFF — surface entièrement invisible
# ---------------------------------------------------------------------------


def test_capq_off_anonymous_returns_404(monkeypatch: pytest.MonkeyPatch) -> None:
    with _make_client(monkeypatch, capture_enabled=False, login=False) as c:
        r = c.get("/body/capture-quality", follow_redirects=False)
        # Le gate flag tombe AVANT l'auth : 404, jamais 303.
        assert r.status_code == 404


def test_capq_off_authenticated_returns_404(monkeypatch: pytest.MonkeyPatch) -> None:
    with _make_client(monkeypatch, capture_enabled=False, login=True) as c:
        r = c.get("/body/capture-quality", follow_redirects=False)
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# 2. Flag ON — comportement nominal
# ---------------------------------------------------------------------------


def test_capq_on_anonymous_redirects_to_login(monkeypatch: pytest.MonkeyPatch) -> None:
    with _make_client(monkeypatch, capture_enabled=True, login=False) as c:
        r = c.get("/body/capture-quality", follow_redirects=False)
        assert r.status_code == 303
        assert "/login" in r.headers.get("location", "")


def test_capq_on_authenticated_returns_200(monkeypatch: pytest.MonkeyPatch) -> None:
    with _make_client(monkeypatch, capture_enabled=True, login=True) as c:
        r = c.get("/body/capture-quality", follow_redirects=False)
        assert r.status_code == 200
        assert "Qualité de capture" in r.text


# ---------------------------------------------------------------------------
# 3. Indépendance vs les autres flags Body
# ---------------------------------------------------------------------------


def test_capq_off_with_body_assessment_on_still_404(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """BODY_ASSESSMENT_ENABLED=true ne doit PAS activer la capture-quality."""
    with _make_client(
        monkeypatch, capture_enabled=False, body_enabled=True, login=True
    ) as c:
        r = c.get("/body/capture-quality", follow_redirects=False)
        assert r.status_code == 404


def test_capq_off_with_bi_on_still_404(monkeypatch: pytest.MonkeyPatch) -> None:
    """BODY_INTELLIGENCE_ENABLED=true ne doit PAS activer la capture-quality."""
    with _make_client(
        monkeypatch, capture_enabled=False, bi_enabled=True, login=True
    ) as c:
        r = c.get("/body/capture-quality", follow_redirects=False)
        assert r.status_code == 404


def test_capq_on_with_body_assessment_off_still_works(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """BODY_CAPTURE_QUALITY_ENABLED suit son propre flag, indépendamment
    de BODY_ASSESSMENT_ENABLED."""
    with _make_client(
        monkeypatch, capture_enabled=True, body_enabled=False, login=True
    ) as c:
        r = c.get("/body/capture-quality", follow_redirects=False)
        assert r.status_code == 200


def test_capq_on_with_bi_off_still_works(monkeypatch: pytest.MonkeyPatch) -> None:
    """BODY_CAPTURE_QUALITY_ENABLED suit son propre flag, indépendamment
    de BODY_INTELLIGENCE_ENABLED."""
    with _make_client(
        monkeypatch, capture_enabled=True, bi_enabled=False, login=True
    ) as c:
        r = c.get("/body/capture-quality", follow_redirects=False)
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# 4. Non-exposition — aucun lien quand flag OFF
# ---------------------------------------------------------------------------


def test_capq_off_no_link_on_profile(monkeypatch: pytest.MonkeyPatch) -> None:
    """Aucun lien capture-quality ne doit apparaître sur /profile quand
    le flag est OFF (sécurité de non-exposition)."""
    with _make_client(monkeypatch, capture_enabled=False, login=True) as c:
        r = c.get("/profile", follow_redirects=False)
        assert r.status_code == 200
        assert "/body/capture-quality" not in r.text
        assert CAPTURE_LINK_MARKER not in r.text.lower().replace("/body/", "")


def test_capq_off_no_link_on_body_intelligence_when_bi_on(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Activer Body Intelligence ne doit JAMAIS exposer un lien
    capture-quality si le flag dédié est OFF."""
    with _make_client(
        monkeypatch, capture_enabled=False, bi_enabled=True, login=True
    ) as c:
        r = c.get("/body/intelligence", follow_redirects=False)
        assert r.status_code == 200
        assert "/body/capture-quality" not in r.text


# ---------------------------------------------------------------------------
# 5. Privacy / static-only — shell respecte ses non-goals
# ---------------------------------------------------------------------------


def _shell_body(monkeypatch: pytest.MonkeyPatch) -> str:
    with _make_client(monkeypatch, capture_enabled=True, login=True) as c:
        r = c.get("/body/capture-quality", follow_redirects=False)
        assert r.status_code == 200
        return r.text


def test_shell_has_no_script_tag(monkeypatch: pytest.MonkeyPatch) -> None:
    body = _shell_body(monkeypatch)
    assert "<script" not in body.lower()


def test_shell_has_no_mediapipe_reference(monkeypatch: pytest.MonkeyPatch) -> None:
    body = _shell_body(monkeypatch).lower()
    for tok in ("mediapipe", "@mediapipe", "tasks-vision", "pose_landmarker"):
        assert tok not in body, f"forbidden MediaPipe reference: {tok!r}"


def test_shell_has_no_cdn_reference(monkeypatch: pytest.MonkeyPatch) -> None:
    body = _shell_body(monkeypatch).lower()
    for tok in ("jsdelivr", "unpkg", "cdn.", "cdnjs"):
        assert tok not in body, f"forbidden CDN reference: {tok!r}"


def test_shell_has_no_upload_form(monkeypatch: pytest.MonkeyPatch) -> None:
    body = _shell_body(monkeypatch).lower()
    assert 'enctype="multipart/form-data"' not in body
    assert "<input" not in body or 'type="file"' not in body


def test_shell_has_no_file_input(monkeypatch: pytest.MonkeyPatch) -> None:
    body = _shell_body(monkeypatch).lower()
    assert 'type="file"' not in body


def test_shell_wording_is_neutral(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tokens strictement interdits (jamais légitimes, même en dénégation
    explicite). Le brief liste aussi "score corporel"/"diagnostic" comme
    interdits, MAIS exige aussi les états "Aucun diagnostic médical" /
    "Aucun score corporel" — des dénégations explicites anti-pseudo-science.
    On scanne donc ces 2 tokens uniquement en dehors d'un contexte de
    dénégation ``aucun … X``/``pas de … X``."""
    import re

    body = _shell_body(monkeypatch).lower()

    strictly_forbidden = (
        "body fat",
        "morphotype",
        "mauvaise posture",
        "taux de gras",
        "tu es gras",
        "tu es sec",
    )
    for tok in strictly_forbidden:
        assert tok not in body, (
            f"forbidden wording {tok!r} on capture-quality shell"
        )

    # ``score corporel`` et ``diagnostic`` : interdits comme PROMESSES,
    # autorisés UNIQUEMENT comme dénégations explicites ("aucun …").
    for tok in ("score corporel", "diagnostic"):
        # Tous les contextes où le token apparaît
        all_occurrences = re.findall(rf"\S*\s+{re.escape(tok)}|^{re.escape(tok)}", body)
        # Seules les occurrences sans "aucun" / "pas de" en amont (≤ 30 chars)
        # sont considérées comme des promesses.
        offending = re.findall(
            rf"(?<!aucun )(?<!pas de )(?<!sans ){re.escape(tok)}", body
        )
        # Filter : si le token n'apparaît jamais SANS un dénégateur dans
        # les 30 caractères précédents, on accepte. Sinon, on échoue.
        for match in re.finditer(re.escape(tok), body):
            start = max(0, match.start() - 30)
            ctx = body[start:match.start()]
            if not re.search(r"\b(aucun(e)?|pas de|sans)\b", ctx):
                raise AssertionError(
                    f"{tok!r} appears as a positive claim without an "
                    f"explicit negation in context: ...{ctx!r}{tok!r}..."
                )
        _ = all_occurrences, offending


def test_shell_contains_expected_placeholder(monkeypatch: pytest.MonkeyPatch) -> None:
    body = _shell_body(monkeypatch)
    assert "Qualité de capture" in body
    assert "cadrage" in body.lower() and "capture" in body.lower()
    assert "Caméra non" in body or "Caméra" in body
    # Non-actif explicite
    for marker in (
        "Aucune image envoyée",
        "Aucune image stockée",
        "Aucun landmark stocké",
        "Aucun diagnostic médical",
        "Aucun score corporel",
    ):
        assert marker in body, f"expected placeholder marker missing: {marker!r}"


# ---------------------------------------------------------------------------
# 6. Non-régression — gates #17 et #19 toujours intacts
# ---------------------------------------------------------------------------


def test_non_reg_body_assessment_gate_still_404(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Activer Capture Quality ne doit pas activer Body Manual Profile."""
    with _make_client(
        monkeypatch, capture_enabled=True, body_enabled=False, login=True
    ) as c:
        r = c.get("/body", follow_redirects=False)
        assert r.status_code == 404


def test_non_reg_body_intelligence_gate_still_404(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Activer Capture Quality ne doit pas activer Body Intelligence."""
    with _make_client(
        monkeypatch, capture_enabled=True, bi_enabled=False, login=True
    ) as c:
        r = c.get("/body/intelligence", follow_redirects=False)
        assert r.status_code == 404


def test_non_reg_progress_still_200(monkeypatch: pytest.MonkeyPatch) -> None:
    with _make_client(monkeypatch, capture_enabled=False, login=True) as c:
        r = c.get("/progress", follow_redirects=False)
        assert r.status_code == 200


def test_non_reg_physique_still_served(monkeypatch: pytest.MonkeyPatch) -> None:
    """`TRAIN1-C` — `/physique` redirige vers `/progress`. Ce que cette garde
    vérifie est inchangé : le drapeau Capture Quality ne casse pas cette
    route. 303 est servi, pas 404 ni 500."""
    with _make_client(monkeypatch, capture_enabled=False, login=True) as c:
        r = c.get("/physique", follow_redirects=False)
        assert r.status_code == 303
