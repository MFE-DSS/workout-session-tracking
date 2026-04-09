"""Validate that V1 local-acceptance artifacts are present and
coherent. These are file-level sanity checks, not integration
tests against a running server.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# VSCode config
# ---------------------------------------------------------------------------


def test_vscode_launch_json_exists_and_valid():
    path = REPO_ROOT / ".vscode" / "launch.json"
    assert path.is_file()
    data = json.loads(path.read_text())
    assert "configurations" in data
    names = [c["name"] for c in data["configurations"]]
    assert "Run app" in names
    assert "Run app (LAN)" in names
    assert "Debug app" in names
    assert "Run tests" in names


def test_vscode_launch_run_app_uses_uvicorn():
    data = json.loads((REPO_ROOT / ".vscode" / "launch.json").read_text())
    run_app = next(c for c in data["configurations"] if c["name"] == "Run app")
    assert run_app["module"] == "uvicorn"
    assert "app.main:app" in run_app["args"]
    assert "--reload" in run_app["args"]


def test_vscode_launch_lan_binds_0000():
    data = json.loads((REPO_ROOT / ".vscode" / "launch.json").read_text())
    lan = next(c for c in data["configurations"] if c["name"] == "Run app (LAN)")
    assert "0.0.0.0" in lan["args"]


def test_vscode_settings_json_exists():
    path = REPO_ROOT / ".vscode" / "settings.json"
    assert path.is_file()
    data = json.loads(path.read_text())
    assert "python.defaultInterpreterPath" in data
    assert ".venv" in data["python.defaultInterpreterPath"]
    assert data.get("python.testing.pytestEnabled") is True


# ---------------------------------------------------------------------------
# V1 acceptance checklist
# ---------------------------------------------------------------------------


def test_v1_acceptance_checklist_exists():
    path = REPO_ROOT / "docs" / "V1_ACCEPTANCE_CHECKLIST.md"
    assert path.is_file()


def test_v1_acceptance_checklist_covers_critical_steps():
    text = (REPO_ROOT / "docs" / "V1_ACCEPTANCE_CHECKLIST.md").read_text()
    for keyword in [
        "alembic upgrade head",
        "pytest",
        "check_alembic_drift",
        "uvicorn",
        "/healthz",
        "/library",
        "/sessions",
        "/history",
        "/progress",
        "/export",
        "backup_sessions",
        "verify_backup",
        "0.0.0.0",
        "Verdict",
    ]:
        assert keyword in text, f"V1 checklist missing: {keyword}"


def test_v1_acceptance_checklist_has_phone_section():
    text = (REPO_ROOT / "docs" / "V1_ACCEPTANCE_CHECKLIST.md").read_text()
    assert "téléphone" in text.lower() or "phone" in text.lower()
    assert "0.0.0.0" in text


# ---------------------------------------------------------------------------
# README local runbook coherence
# ---------------------------------------------------------------------------


def test_readme_has_vscode_section():
    text = (REPO_ROOT / "README.md").read_text()
    assert "VSCode" in text or "vscode" in text
    assert "launch.json" in text


def test_readme_has_phone_on_lan_section():
    text = (REPO_ROOT / "README.md").read_text()
    assert "0.0.0.0" in text
    assert "téléphone" in text.lower() or "phone" in text.lower()


def test_readme_links_v1_checklist():
    text = (REPO_ROOT / "README.md").read_text()
    assert "V1_ACCEPTANCE_CHECKLIST" in text
