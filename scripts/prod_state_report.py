#!/usr/bin/env python3
"""Sb_26.3 — prod state diagnostic report.

Aggregates everything an operator wants to see at a glance when looking
at a VPS:
* deploy state (SHA, age)
* DB reachability
* latest backup file + age
* disk usage of the DB partition
* /healthz/strict response (if URL provided)

Output is JSON on stdout — never contains secrets, suitable for piping
to a log channel.

Usage:
    python3 scripts/prod_state_report.py
    python3 scripts/prod_state_report.py --healthz http://127.0.0.1:8000/healthz/strict
    python3 scripts/prod_state_report.py --pretty
"""
from __future__ import annotations

import argparse
import json
import shutil
import socket
import sys
from datetime import UTC, datetime
from pathlib import Path
from urllib import error as urlerror
from urllib import request as urlrequest

ROOT = Path(__file__).resolve().parent.parent


def _read_deploy_state(path: Path) -> dict:
    if not path.exists():
        return {"present": False, "path": str(path)}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"present": False, "error": exc.__class__.__name__}
    raw["present"] = True
    sha = raw.get("sha")
    if isinstance(sha, str):
        raw["short_sha"] = sha[:12]
    deployed_at_raw = raw.get("deployed_at")
    if isinstance(deployed_at_raw, str):
        try:
            ts = datetime.fromisoformat(deployed_at_raw.replace("Z", "+00:00"))
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=UTC)
            raw["age_seconds"] = int((datetime.now(UTC) - ts).total_seconds())
        except ValueError:
            raw["age_seconds"] = None
    return raw


def _disk(path: Path) -> dict:
    try:
        target = path if path.exists() else path.parent
        usage = shutil.disk_usage(str(target))
        return {
            "path": str(target),
            "total_bytes": usage.total,
            "free_bytes": usage.free,
            "free_percent": round(100 * usage.free / usage.total, 1)
            if usage.total
            else None,
        }
    except OSError as exc:
        return {"path": str(path), "error": exc.__class__.__name__}


def _latest_backup(backup_dir: Path) -> dict:
    if not backup_dir.is_dir():
        return {"present": False, "dir": str(backup_dir)}
    files = sorted(backup_dir.glob("*.json"), key=lambda p: p.stat().st_mtime)
    if not files:
        return {"present": False, "dir": str(backup_dir)}
    latest = files[-1]
    age_seconds = int(
        datetime.now(UTC).timestamp() - latest.stat().st_mtime
    )
    return {
        "present": True,
        "file": latest.name,
        "size_bytes": latest.stat().st_size,
        "age_seconds": age_seconds,
    }


def _healthz(url: str) -> dict:
    # noqa S310: url is operator-supplied via --healthz CLI flag, used
    # only against the local app's /healthz/strict in practice.
    try:
        req = urlrequest.Request(url, method="GET")  # noqa: S310
        with urlrequest.urlopen(req, timeout=5) as resp:  # noqa: S310
            body = resp.read().decode("utf-8", errors="replace")
            return {"url": url, "status": resp.status, "body": json.loads(body)}
    except (urlerror.URLError, json.JSONDecodeError, OSError) as exc:
        return {"url": url, "error": exc.__class__.__name__}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--deploy-state",
        type=Path,
        default=ROOT / "var" / "deploy_state.json",
    )
    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=ROOT / "var" / "backups",
    )
    parser.add_argument(
        "--healthz",
        default="",
        help="If set, GET this URL and include the response in the report.",
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "hostname": socket.gethostname(),
        "deploy": _read_deploy_state(args.deploy_state),
        "backup": _latest_backup(args.backup_dir),
        "disk": _disk(args.backup_dir),
    }
    if args.healthz:
        report["healthz"] = _healthz(args.healthz)

    print(json.dumps(report, indent=2 if args.pretty else None, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
