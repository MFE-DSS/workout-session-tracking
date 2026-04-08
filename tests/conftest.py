"""Test fixtures: run each test against an isolated on-disk SQLite."""
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

    # Reset cached settings + module-level engine so the new DATABASE_URL sticks.
    # We must reload every module that captured the previous `Base` / engine at
    # import time, in the right order, so models re-register on the new Base.
    import importlib
    import sys

    for mod_name in [
        "app.routers.pages",
        "app.routers.health",
        "app.services.seed",
        "app.models.session",
        "app.models.catalog",
        "app.models",
        "app.database",
        "app.config",
        "app.main",
    ]:
        sys.modules.pop(mod_name, None)

    from app import config  # noqa: F401

    from app import main as main_mod

    with TestClient(main_mod.app) as c:
        yield c

    try:
        os.unlink(db_path)
    except OSError:
        pass
