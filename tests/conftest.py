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

    # Reset module-level engine + Base so the new DATABASE_URL sticks.
    # Any `app.*` module that captured the old engine or Base at import
    # time must be dropped so the re-imports pick up the new ones. We
    # purge the whole `app` namespace to avoid fragile hand-maintained
    # module lists.
    import sys

    for mod_name in [m for m in list(sys.modules) if m == "app" or m.startswith("app.")]:
        sys.modules.pop(mod_name, None)

    from app import main as main_mod  # noqa: E402

    with TestClient(main_mod.app) as c:
        yield c

    try:
        os.unlink(db_path)
    except OSError:
        pass
