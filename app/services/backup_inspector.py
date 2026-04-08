"""Read-only helper that reports on the local nightly backup
directory.

Used by the `/export` landing page so the user can see whether
the backup cron / systemd timer is alive without leaving the
app. Pure file system inspection — never touches the DB.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

# What the nightly backup script writes. Both JSON and CSV
# dumps share the `sessions-` prefix.
BACKUP_GLOBS = ("sessions-*.json", "sessions-*.csv")


@dataclass
class BackupInfo:
    name: str
    path: str
    size_bytes: int
    modified_at: datetime


def latest_backup_info(backup_dir: Union[str, Path]) -> Optional[BackupInfo]:
    """Return info about the most recent backup file, or None if
    the directory is missing or empty."""
    p = Path(backup_dir)
    if not p.is_dir():
        return None
    files: list[Path] = []
    for pattern in BACKUP_GLOBS:
        files.extend(p.glob(pattern))
    if not files:
        return None
    latest = max(files, key=lambda f: f.stat().st_mtime)
    stat = latest.stat()
    return BackupInfo(
        name=latest.name,
        path=str(latest),
        size_bytes=stat.st_size,
        modified_at=datetime.fromtimestamp(stat.st_mtime),
    )


def list_backups(backup_dir: Union[str, Path]) -> list[BackupInfo]:
    """All matching backup files, newest first."""
    p = Path(backup_dir)
    if not p.is_dir():
        return []
    files: list[Path] = []
    for pattern in BACKUP_GLOBS:
        files.extend(p.glob(pattern))
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    out: list[BackupInfo] = []
    for f in files:
        stat = f.stat()
        out.append(
            BackupInfo(
                name=f.name,
                path=str(f),
                size_bytes=stat.st_size,
                modified_at=datetime.fromtimestamp(stat.st_mtime),
            )
        )
    return out
