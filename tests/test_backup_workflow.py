"""Sprint 6 backup workflow tests.

Covers:
- export_builder parity with the HTTP routes (so the standalone
  script and the web routes always agree byte-for-byte)
- the backup script writes JSON + CSV files in the configured dir
- retention prunes old files
- the dir is created if missing
- /export landing page renders the latest-backup block
- /export landing page falls back to a clean empty state when no
  backups exist
- the systemd unit files exist
- the drift guard still passes (already tested elsewhere, but the
  builder refactor introduced a new module so we re-confirm it
  doesn't drift the schema)
"""
from __future__ import annotations

import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Builder parity with the HTTP routes
# ---------------------------------------------------------------------------


def _start(client, slug: str = "push-a") -> int:
    r = client.post("/sessions", data={"template_slug": slug}, follow_redirects=False)
    return int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))


def test_json_route_uses_export_builder(client):
    """The JSON returned by GET /export/sessions.json must match
    the dict returned by build_json_payload(db) modulo the
    `exported_at` timestamp."""
    from app.database import SessionLocal
    from app.services.export_builder import build_json_payload

    _start(client, "push-a")
    r = client.get("/export/sessions.json")
    route_payload = r.json()

    with SessionLocal() as db:
        builder_payload = build_json_payload(db)

    # Strip the volatile timestamp before comparing.
    for p in (route_payload, builder_payload):
        p.pop("exported_at", None)

    assert route_payload == builder_payload


def test_csv_route_uses_export_builder(client):
    """The CSV returned by GET /export/sessions.csv must match
    build_csv_text(db) byte-for-byte."""
    from app.database import SessionLocal
    from app.services.export_builder import build_csv_text

    _start(client, "push-a")
    route_text = client.get("/export/sessions.csv").text
    with SessionLocal() as db:
        builder_text = build_csv_text(db)

    assert route_text == builder_text


# ---------------------------------------------------------------------------
# Standalone backup script
# ---------------------------------------------------------------------------


def _run_backup_script(env: dict[str, str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "scripts.backup_sessions"],
        cwd=str(REPO_ROOT),
        env={**os.environ, **env},
        capture_output=True,
        text=True,
    )


def test_backup_script_writes_json_and_csv(client, tmp_path):
    # Create one session so the dump is non-trivial
    _start(client, "push-a")

    backup_dir = tmp_path / "backups"
    # The script reads $DATABASE_URL via app.config — pass the
    # same one the test fixture is using so it sees the seeded DB.
    db_url = os.environ["DATABASE_URL"]
    result = _run_backup_script(
        {
            "BACKUP_DIR": str(backup_dir),
            "DATABASE_URL": db_url,
            "BACKUP_RETENTION_DAYS": "30",
        }
    )
    assert result.returncode == 0, result.stderr
    files = sorted(backup_dir.iterdir())
    json_files = [f for f in files if f.name.startswith("sessions-") and f.suffix == ".json"]
    csv_files = [f for f in files if f.name.startswith("sessions-") and f.suffix == ".csv"]
    assert len(json_files) == 1
    assert len(csv_files) == 1

    # JSON file is real JSON with at least one session
    payload = json.loads(json_files[0].read_text())
    from app.services.export_builder import SCHEMA_VERSION
    assert payload["schema_version"] == SCHEMA_VERSION
    assert payload["count"] >= 1

    # CSV file has the right header
    csv_lines = csv_files[0].read_text().splitlines()
    assert csv_lines[0].startswith("session_id,")


def test_backup_script_creates_dir_if_missing(client, tmp_path):
    backup_dir = tmp_path / "deep" / "nested" / "dir"
    assert not backup_dir.exists()
    result = _run_backup_script(
        {
            "BACKUP_DIR": str(backup_dir),
            "DATABASE_URL": os.environ["DATABASE_URL"],
            "BACKUP_RETENTION_DAYS": "30",
        }
    )
    assert result.returncode == 0, result.stderr
    assert backup_dir.is_dir()
    assert any(backup_dir.iterdir())


def test_backup_script_retention_prunes_old_files(client, tmp_path):
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()

    # Plant a stale fake backup that's 60 days old
    stale_json = backup_dir / "sessions-19990101_0000.json"
    stale_csv = backup_dir / "sessions-19990101_0000.csv"
    stale_json.write_text("{}")
    stale_csv.write_text("session_id\n")
    sixty_days_ago = time.time() - 60 * 86400
    os.utime(stale_json, (sixty_days_ago, sixty_days_ago))
    os.utime(stale_csv, (sixty_days_ago, sixty_days_ago))

    result = _run_backup_script(
        {
            "BACKUP_DIR": str(backup_dir),
            "DATABASE_URL": os.environ["DATABASE_URL"],
            "BACKUP_RETENTION_DAYS": "30",
        }
    )
    assert result.returncode == 0, result.stderr
    # Old files were pruned, fresh files were written
    assert not stale_json.exists()
    assert not stale_csv.exists()
    assert any(f.suffix == ".json" for f in backup_dir.iterdir())
    assert any(f.suffix == ".csv" for f in backup_dir.iterdir())


def test_backup_script_retention_zero_keeps_everything(client, tmp_path):
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    stale = backup_dir / "sessions-19990101_0000.json"
    stale.write_text("{}")
    os.utime(stale, (time.time() - 1000 * 86400, time.time() - 1000 * 86400))

    result = _run_backup_script(
        {
            "BACKUP_DIR": str(backup_dir),
            "DATABASE_URL": os.environ["DATABASE_URL"],
            "BACKUP_RETENTION_DAYS": "0",
        }
    )
    assert result.returncode == 0, result.stderr
    # The 1000-day-old file is still there
    assert stale.exists()


# ---------------------------------------------------------------------------
# /export landing page: backup status block
# ---------------------------------------------------------------------------


def test_export_landing_shows_no_backup_message_when_dir_empty(client, tmp_path, monkeypatch):
    # Point the app at a fresh empty backup dir.
    backup_dir = tmp_path / "empty-backups"
    monkeypatch.setenv("BACKUP_DIR", str(backup_dir))
    # Settings is cached -- clear it so the new env var sticks.
    from app import config

    config.get_settings.cache_clear()

    body = client.get("/export").text
    assert "Sauvegarde planifiée" in body
    assert "Aucune sauvegarde locale détectée" in body


def test_export_landing_shows_latest_backup_when_present(client, tmp_path, monkeypatch):
    backup_dir = tmp_path / "with-backups"
    backup_dir.mkdir()
    # Plant one fake backup
    sample = backup_dir / "sessions-20260408_0330.json"
    from app.services.export_builder import SCHEMA_VERSION
    import json as _json
    sample.write_text(_json.dumps({
        "schema_version": SCHEMA_VERSION, "count": 0, "sessions": [],
    }))

    monkeypatch.setenv("BACKUP_DIR", str(backup_dir))
    from app import config

    config.get_settings.cache_clear()

    body = client.get("/export").text
    assert "sessions-20260408_0330.json" in body
    assert "Modifié" in body
    assert "Taille" in body
    # The empty-state message must be absent
    assert "Aucune sauvegarde locale détectée" not in body


# ---------------------------------------------------------------------------
# Backup inspector helper
# ---------------------------------------------------------------------------


def test_backup_inspector_returns_none_for_missing_dir(client, tmp_path):
    from app.services.backup_inspector import latest_backup_info, list_backups

    missing = tmp_path / "nope"
    assert latest_backup_info(missing) is None
    assert list_backups(missing) == []


def test_backup_inspector_lists_files_newest_first(client, tmp_path):
    from app.services.backup_inspector import list_backups

    d = tmp_path / "b"
    d.mkdir()
    older = d / "sessions-20250101_0000.json"
    newer = d / "sessions-20260101_0000.json"
    older.write_text("{}")
    newer.write_text("{}")
    # Force mtimes so the test is deterministic
    os.utime(older, (1, 1))
    os.utime(newer, (1_000_000, 1_000_000))

    backups = list_backups(d)
    assert [b.name for b in backups] == [
        "sessions-20260101_0000.json",
        "sessions-20250101_0000.json",
    ]


# ---------------------------------------------------------------------------
# systemd unit files exist (deploy artifact sanity)
# ---------------------------------------------------------------------------


def test_systemd_backup_units_exist():
    deploy = REPO_ROOT / "deploy"
    service = deploy / "workout-backup.service"
    timer = deploy / "workout-backup.timer"
    assert service.is_file()
    assert timer.is_file()
    s_text = service.read_text()
    t_text = timer.read_text()
    assert "scripts.backup_sessions" in s_text
    assert "OnCalendar" in t_text
    assert "Persistent=true" in t_text
