"""Sprint 7: backup integrity verifier + strict health + first-deploy checklist.

Covers:
- verifier happy path on a real backup produced by the builder
- verifier failures: missing file, unreadable JSON, bad shape,
  missing / wrong schema_version, count mismatch
- live_session_count is reported when a DB session is passed
- /healthz stays unchanged (public liveness probe)
- /healthz/strict returns 200 "ok" on a healthy state with no
  backups yet
- /healthz/strict returns 200 "ok" when a valid backup exists
- /healthz/strict returns 503 "degraded" when a corrupt backup
  exists
- /export renders the integrity OK badge when a valid backup
  exists
- /export renders the integrity FAIL badge when a corrupt backup
  exists
- CHECKLISTS.md exists and mentions every critical step
- workout-backup-verify.service + .timer exist and point at the
  verify script
- scripts/verify_backup.py runs end to end and exits 0 / 1
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# verify_latest_backup: happy path
# ---------------------------------------------------------------------------


def _write_valid_backup(backup_dir: Path, *, count: int = 0, name: str = "sessions-20260408_0330.json") -> Path:
    from app.services.export_builder import SCHEMA_VERSION
    backup_dir.mkdir(parents=True, exist_ok=True)
    path = backup_dir / name
    path.write_text(
        json.dumps(
            {
                "schema_version": SCHEMA_VERSION,
                "exported_at": "2026-04-08T03:30:00+00:00",
                "count": count,
                "sessions": [{} for _ in range(count)],
            }
        ),
        encoding="utf-8",
    )
    return path


def test_verifier_ok_on_valid_empty_backup(client, tmp_path):
    from app.services.backup_verifier import verify_latest_backup

    backup_dir = tmp_path / "backups"
    _write_valid_backup(backup_dir, count=0)
    from app.services.export_builder import SCHEMA_VERSION
    result = verify_latest_backup(backup_dir)
    assert result.ok is True
    assert result.schema_version == SCHEMA_VERSION
    assert result.exported_count == 0
    assert result.errors == []
    assert "ok" in result.summary


def test_verifier_ok_with_live_db_count(client, tmp_path):
    """When a db session is provided, live_session_count is reported
    as an informational field — NOT a hard check."""
    from app.database import SessionLocal
    from app.services.backup_verifier import verify_latest_backup

    backup_dir = tmp_path / "backups"
    _write_valid_backup(backup_dir, count=0)
    with SessionLocal() as db:
        result = verify_latest_backup(backup_dir, db=db)
    assert result.ok is True
    assert result.live_session_count == 0


# ---------------------------------------------------------------------------
# verify_latest_backup: failure branches
# ---------------------------------------------------------------------------


def test_verifier_fails_when_no_backup_file(client, tmp_path):
    from app.services.backup_verifier import verify_latest_backup

    result = verify_latest_backup(tmp_path / "empty")
    assert result.ok is False
    assert any("no JSON backup file found" in e for e in result.errors)
    assert result.file_name is None


def test_verifier_fails_on_broken_json(client, tmp_path):
    from app.services.backup_verifier import verify_latest_backup

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    (backup_dir / "sessions-20260408_0330.json").write_text("{not json")
    result = verify_latest_backup(backup_dir)
    assert result.ok is False
    assert any("cannot parse JSON" in e for e in result.errors)


def test_verifier_fails_on_non_object_payload(client, tmp_path):
    from app.services.backup_verifier import verify_latest_backup

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    (backup_dir / "sessions-20260408_0330.json").write_text("[1, 2, 3]")
    result = verify_latest_backup(backup_dir)
    assert result.ok is False
    assert any("not a JSON object" in e for e in result.errors)


def test_verifier_fails_on_wrong_schema_version(client, tmp_path):
    from app.services.backup_verifier import verify_latest_backup

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    (backup_dir / "sessions-20260408_0330.json").write_text(
        json.dumps(
            {"schema_version": 999, "count": 0, "sessions": []}
        )
    )
    result = verify_latest_backup(backup_dir)
    assert result.ok is False
    assert any("schema_version is 999" in e for e in result.errors)


def test_verifier_fails_on_missing_schema_version(client, tmp_path):
    from app.services.backup_verifier import verify_latest_backup

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    (backup_dir / "sessions-20260408_0330.json").write_text(
        json.dumps({"count": 0, "sessions": []})
    )
    result = verify_latest_backup(backup_dir)
    assert result.ok is False
    assert any("schema_version missing" in e for e in result.errors)


def test_verifier_fails_on_count_sessions_mismatch(client, tmp_path):
    from app.services.backup_verifier import verify_latest_backup

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    from app.services.export_builder import SCHEMA_VERSION
    (backup_dir / "sessions-20260408_0330.json").write_text(
        json.dumps(
            {"schema_version": SCHEMA_VERSION, "count": 5, "sessions": [{}, {}]}
        )
    )
    result = verify_latest_backup(backup_dir)
    assert result.ok is False
    assert any("does not match count" in e for e in result.errors)


def test_verifier_ok_on_builder_output(client, tmp_path):
    """The round-trip: builder -> file -> verifier -> ok."""
    from app.database import SessionLocal
    from app.services.backup_verifier import verify_latest_backup
    from app.services.export_builder import build_json_payload

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    with SessionLocal() as db:
        payload = build_json_payload(db)
    (backup_dir / "sessions-20260408_0330.json").write_text(
        json.dumps(payload), encoding="utf-8"
    )
    with SessionLocal() as db:
        result = verify_latest_backup(backup_dir, db=db)
    assert result.ok is True
    assert result.errors == []


def test_verifier_picks_json_not_csv_when_csv_is_newer(client, tmp_path):
    """Regression: when the CSV mtime is newer than the JSON mtime
    the verifier must still pick the JSON file, not try to parse
    the CSV as JSON."""
    from app.services.backup_verifier import verify_latest_backup

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    json_file = backup_dir / "sessions-20260408_0330.json"
    csv_file = backup_dir / "sessions-20260408_0330.csv"
    from app.services.export_builder import SCHEMA_VERSION
    json_file.write_text(
        json.dumps({"schema_version": SCHEMA_VERSION, "count": 0, "sessions": []})
    )
    csv_file.write_text("session_id,started_at\n")
    # Force CSV to be newer by touching it
    os.utime(json_file, (1_000_000, 1_000_000))
    os.utime(csv_file, (2_000_000, 2_000_000))

    result = verify_latest_backup(backup_dir)
    assert result.ok is True, f"errors: {result.errors}"
    assert result.file_name.endswith(".json")


# ---------------------------------------------------------------------------
# /healthz (unchanged)
# ---------------------------------------------------------------------------


def test_healthz_public_still_simple(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# /healthz/strict
# ---------------------------------------------------------------------------


def _clear_settings_cache() -> None:
    from app import config

    config.get_settings.cache_clear()


def test_healthz_strict_ok_when_no_backups_yet(client, tmp_path, monkeypatch):
    # Fresh deploy: BACKUP_DIR doesn't even exist yet. The strict
    # endpoint must still report "ok" so operators don't get a
    # spurious 503 on day 1.
    backup_dir = tmp_path / "never-created"
    monkeypatch.setenv("BACKUP_DIR", str(backup_dir))
    _clear_settings_cache()

    r = client.get("/healthz/strict")
    assert r.status_code == 200
    payload = r.json()
    assert payload["status"] == "ok"
    assert payload["db"]["ok"] is True
    assert payload["backup_dir"]["exists"] is False
    assert payload["backup"]["present"] is False
    assert payload["backup"]["valid"] is None


def test_healthz_strict_ok_with_valid_backup(client, tmp_path, monkeypatch):
    backup_dir = tmp_path / "backups"
    _write_valid_backup(backup_dir, count=0)
    monkeypatch.setenv("BACKUP_DIR", str(backup_dir))
    _clear_settings_cache()

    r = client.get("/healthz/strict")
    assert r.status_code == 200
    payload = r.json()
    assert payload["status"] == "ok"
    assert payload["backup"]["present"] is True
    assert payload["backup"]["valid"] is True
    from app.services.export_builder import SCHEMA_VERSION
    assert payload["backup"]["schema_version"] == SCHEMA_VERSION
    assert payload["backup"]["exported_count"] == 0
    assert payload["backup"]["live_session_count"] == 0
    assert payload["backup"]["errors"] == []


def test_healthz_strict_degraded_with_corrupt_backup(client, tmp_path, monkeypatch):
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    (backup_dir / "sessions-20260408_0330.json").write_text("{corrupt")
    monkeypatch.setenv("BACKUP_DIR", str(backup_dir))
    _clear_settings_cache()

    r = client.get("/healthz/strict")
    assert r.status_code == 503
    payload = r.json()
    assert payload["status"] == "degraded"
    assert payload["db"]["ok"] is True
    assert payload["backup"]["present"] is True
    assert payload["backup"]["valid"] is False
    assert any("cannot parse JSON" in e for e in payload["backup"]["errors"])


def test_healthz_strict_payload_shape_contract(client, tmp_path, monkeypatch):
    """Lock the top-level JSON shape so monitoring scripts can rely on it."""
    backup_dir = tmp_path / "never"
    monkeypatch.setenv("BACKUP_DIR", str(backup_dir))
    _clear_settings_cache()

    payload = client.get("/healthz/strict").json()
    assert set(payload.keys()) == {
        "status",
        "checked_at",
        "db",
        "backup_dir",
        "backup",
    }
    assert set(payload["db"].keys()) == {"ok", "detail"}
    assert "exists" in payload["backup_dir"]
    expected_backup_keys = {
        "present",
        "valid",
        "file",
        "age_seconds",
        "schema_version",
        "exported_count",
        "live_session_count",
        "errors",
    }
    assert expected_backup_keys == set(payload["backup"].keys())


# ---------------------------------------------------------------------------
# /export integrity surfacing
# ---------------------------------------------------------------------------


def test_export_landing_shows_integrity_ok_when_backup_valid(
    client, tmp_path, monkeypatch
):
    backup_dir = tmp_path / "backups"
    _write_valid_backup(backup_dir, count=0)
    monkeypatch.setenv("BACKUP_DIR", str(backup_dir))
    _clear_settings_cache()

    body = client.get("/export").text
    assert "Intégrité" in body
    assert "integrity-ok" in body
    # Age label: on a just-written file we expect "à l'instant"
    assert "à l&#39;instant" in body or "à l'instant" in body or "il y a 0 min" in body


def test_export_landing_shows_integrity_fail_when_backup_corrupt(
    client, tmp_path, monkeypatch
):
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    (backup_dir / "sessions-20260408_0330.json").write_text("{corrupt")
    monkeypatch.setenv("BACKUP_DIR", str(backup_dir))
    _clear_settings_cache()

    body = client.get("/export").text
    assert "integrity-fail" in body
    assert "integrity-errors" in body
    assert "cannot parse JSON" in body


# ---------------------------------------------------------------------------
# scripts/verify_backup.py end to end
# ---------------------------------------------------------------------------


def _run_verifier_script(env: dict[str, str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "scripts.verify_backup"],
        cwd=str(REPO_ROOT),
        env={**os.environ, **env},
        capture_output=True,
        text=True,
    )


def test_verify_backup_script_succeeds_on_valid_backup(client, tmp_path):
    backup_dir = tmp_path / "backups"
    _write_valid_backup(backup_dir, count=0)

    result = _run_verifier_script(
        {
            "BACKUP_DIR": str(backup_dir),
            "DATABASE_URL": os.environ["DATABASE_URL"],
        }
    )
    assert result.returncode == 0, result.stderr
    assert "verify_backup: [OK ]" in result.stdout
    from app.services.export_builder import SCHEMA_VERSION
    assert f"schema_version     : {SCHEMA_VERSION}" in result.stdout


def test_verify_backup_script_fails_on_missing_backup(client, tmp_path):
    backup_dir = tmp_path / "empty"

    result = _run_verifier_script(
        {
            "BACKUP_DIR": str(backup_dir),
            "DATABASE_URL": os.environ["DATABASE_URL"],
        }
    )
    assert result.returncode == 1
    assert "verify_backup: [FAIL]" in result.stdout
    assert "no backup found" in result.stdout or "no JSON backup file found" in result.stdout


def test_verify_backup_script_fails_on_corrupt_backup(client, tmp_path):
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    (backup_dir / "sessions-20260408_0330.json").write_text("{corrupt")

    result = _run_verifier_script(
        {
            "BACKUP_DIR": str(backup_dir),
            "DATABASE_URL": os.environ["DATABASE_URL"],
        }
    )
    assert result.returncode == 1
    assert "[FAIL]" in result.stdout
    assert "cannot parse JSON" in result.stdout


# ---------------------------------------------------------------------------
# Deploy artefacts: CHECKLISTS.md + systemd verify units
# ---------------------------------------------------------------------------


def test_checklists_file_exists_and_covers_required_steps():
    path = REPO_ROOT / "deploy" / "CHECKLISTS.md"
    assert path.is_file(), "deploy/CHECKLISTS.md missing"
    text = path.read_text()
    for heading in [
        "First deploy",
        "Update",
        "Backup verification",
        "Restore",
    ]:
        assert heading in text, f"missing section: {heading}"
    # Mentions the critical commands
    assert "alembic upgrade head" in text
    assert "check_alembic_drift" in text
    assert "verify_backup" in text
    assert "workout-backup.timer" in text
    assert "workout-backup-verify.timer" in text
    assert "/healthz/strict" in text


def test_systemd_verify_units_exist_and_point_at_script():
    deploy = REPO_ROOT / "deploy"
    service = deploy / "workout-backup-verify.service"
    timer = deploy / "workout-backup-verify.timer"
    assert service.is_file()
    assert timer.is_file()
    assert "scripts.verify_backup" in service.read_text()
    timer_text = timer.read_text()
    assert "OnCalendar" in timer_text
    assert "Persistent=true" in timer_text


# ---------------------------------------------------------------------------
# relative_hours_ago helper
# ---------------------------------------------------------------------------


def test_relative_hours_ago_buckets():
    from app.services.time_format import relative_hours_ago

    now = datetime(2026, 4, 8, 12, 0, 0, tzinfo=timezone.utc)
    assert relative_hours_ago(now, now) == "à l'instant"
    assert relative_hours_ago(now, now - timedelta(seconds=30)) == "à l'instant"
    assert relative_hours_ago(now, now - timedelta(minutes=5)) == "il y a 5 min"
    assert relative_hours_ago(now, now - timedelta(hours=2)) == "il y a 2 h"
    assert relative_hours_ago(now, now - timedelta(days=1)) == "hier"
    assert relative_hours_ago(now, now - timedelta(days=3)) == "il y a 3 j"
    assert relative_hours_ago(now, now - timedelta(days=60)) == "il y a 2 mois"


def test_relative_hours_ago_naive_then_safe():
    """SQLite strips tzinfo; coerce instead of raising."""
    from app.services.time_format import relative_hours_ago

    aware_now = datetime(2026, 4, 8, 12, 0, 0, tzinfo=timezone.utc)
    naive_then = datetime(2026, 4, 8, 11, 0, 0)  # 1 hour ago
    assert relative_hours_ago(aware_now, naive_then) == "il y a 1 h"
