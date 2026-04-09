"""Validate that deploy artifacts are present and internally coherent.

These are NOT integration tests against a real VPS — they're file-
level sanity checks that run in pytest to catch broken references,
missing files, or drift between the code and the deploy docs before
anything is shipped.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEPLOY = REPO_ROOT / "deploy"
SCRIPTS = REPO_ROOT / "scripts"


# ---------------------------------------------------------------------------
# File presence
# ---------------------------------------------------------------------------


def test_deploy_ovh_guide_exists():
    assert (DEPLOY / "DEPLOY_OVH.md").is_file()


def test_checklists_exists():
    assert (DEPLOY / "CHECKLISTS.md").is_file()


def test_env_production_example_exists():
    assert (REPO_ROOT / ".env.production.example").is_file()


def test_smoke_deploy_script_exists_and_executable():
    script = SCRIPTS / "smoke_deploy.sh"
    assert script.is_file()
    import os

    assert os.access(script, os.X_OK), "smoke_deploy.sh is not executable"


def test_systemd_units_all_present():
    expected = [
        "workout.service",
        "workout-backup.service",
        "workout-backup.timer",
        "workout-backup-verify.service",
        "workout-backup-verify.timer",
    ]
    for name in expected:
        assert (DEPLOY / name).is_file(), f"missing deploy/{name}"


def test_nginx_conf_example_exists():
    assert (DEPLOY / "nginx.conf.example").is_file()


# ---------------------------------------------------------------------------
# Internal coherence
# ---------------------------------------------------------------------------


def test_env_production_has_required_keys():
    text = (REPO_ROOT / ".env.production.example").read_text()
    for key in [
        "APP_ENV",
        "APP_SECRET_KEY",
        "APP_BASE_URL",
        "DATABASE_URL",
        "BACKUP_DIR",
        "BACKUP_RETENTION_DAYS",
    ]:
        assert key in text, f"missing {key} in .env.production.example"


def test_workout_service_references_uvicorn():
    text = (DEPLOY / "workout.service").read_text()
    assert "uvicorn" in text
    assert "app.main:app" in text


def test_backup_service_references_backup_script():
    text = (DEPLOY / "workout-backup.service").read_text()
    assert "scripts.backup_sessions" in text


def test_verify_service_references_verify_script():
    text = (DEPLOY / "workout-backup-verify.service").read_text()
    assert "scripts.verify_backup" in text


def test_backup_timer_has_persistent():
    text = (DEPLOY / "workout-backup.timer").read_text()
    assert "Persistent=true" in text
    assert "OnCalendar" in text


def test_verify_timer_runs_after_backup():
    """Verify timer should fire AFTER the backup timer."""
    backup_text = (DEPLOY / "workout-backup.timer").read_text()
    verify_text = (DEPLOY / "workout-backup-verify.timer").read_text()
    # Parse the OnCalendar hours. Backup should be earlier.
    import re

    backup_hour = re.search(r"OnCalendar=.*\s(\d{2}):", backup_text)
    verify_hour = re.search(r"OnCalendar=.*\s(\d{2}):", verify_text)
    assert backup_hour and verify_hour
    assert int(backup_hour.group(1)) < int(verify_hour.group(1))


def test_smoke_script_checks_healthz():
    text = (SCRIPTS / "smoke_deploy.sh").read_text()
    assert "/healthz" in text
    assert "/healthz/strict" in text
    assert "/export" in text
    assert "backup_sessions" in text
    assert "verify_backup" in text
    assert "check_alembic_drift" in text


def test_nginx_conf_has_proxy_pass():
    text = (DEPLOY / "nginx.conf.example").read_text()
    assert "proxy_pass" in text
    assert "127.0.0.1:8000" in text


def test_deploy_ovh_references_all_steps():
    text = (DEPLOY / "DEPLOY_OVH.md").read_text()
    for keyword in [
        "alembic upgrade head",
        "systemctl enable",
        "certbot",
        "htpasswd",
        "smoke_deploy",
        ".env.production",
        "workout-backup.timer",
        "workout-backup-verify.timer",
        "/healthz/strict",
        "check_alembic_drift",
    ]:
        assert keyword in text, f"DEPLOY_OVH.md missing reference to: {keyword}"


def test_deploy_readme_links_to_deploy_ovh_and_checklists():
    text = (DEPLOY / "README.md").read_text()
    assert "CHECKLISTS.md" in text
    # DEPLOY_OVH.md was added in this sprint; make sure the main
    # README or the deploy README references it
    readme = (REPO_ROOT / "README.md").read_text()
    combined = text + readme
    assert "DEPLOY_OVH" in combined
