#!/usr/bin/env python3
"""Resolve the on-disk SQLite file behind a DATABASE_URL (Sb_OPS_DEPLOY_SAFETY_01).

`scripts/deploy_prod.sh` used to hardcode `${APP_DIR}/var/workout.db` when taking the
pre-migration backup. If the real `DATABASE_URL` pointed anywhere else the file was simply not
found, the script only WARNED, and the deploy proceeded to `alembic upgrade head` **with no
backup at all**. `/healthz/strict` does not assert backup presence either, so the gap was
invisible. This module removes the guesswork so the caller can fail closed.

Contract — exit codes are the API:

    0  a real SQLite FILE was resolved; the absolute path is printed on stdout
    3  the URL is not SQLite (PostgreSQL & co) — the caller must skip the SQLite backup
    4  the URL is SQLite but has no usable file (in-memory, or empty path)
    2  usage error

Pure standard library on purpose: it runs on the production host *before* `pip install`, using
only the venv interpreter.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

NOT_SQLITE = 3
NO_FILE = 4

# `sqlite`, but also `sqlite+pysqlite`, `sqlite+aiosqlite`, …
_SQLITE_SCHEMES = ("sqlite",)
_MEMORY_MARKERS = (":memory:", "")


def is_sqlite_url(database_url: str) -> bool:
    """True for any SQLite dialect, including a `+driver` suffix."""
    scheme = urlsplit(database_url.strip()).scheme.lower()
    return scheme.split("+", 1)[0] in _SQLITE_SCHEMES


def resolve_sqlite_path(database_url: str, app_dir: str | Path) -> Path | None:
    """Absolute path of the SQLite file, or None when the URL has no file.

    SQLAlchemy encodes the path in the part after `sqlite://`:
      - `sqlite:///relative/x.db`  → relative to the application directory
      - `sqlite:////absolute/x.db` → absolute
      - `sqlite://` / `sqlite:///:memory:` → in-memory, no file
    Query parameters (`?check_same_thread=False`) are ignored.

    Raises ValueError when the URL is not SQLite — callers should test `is_sqlite_url` first.
    """
    url = database_url.strip()
    if not is_sqlite_url(url):
        raise ValueError(f"not a SQLite URL: {url!r}")

    parts = urlsplit(url)
    # urlsplit puts everything after `sqlite://` into netloc+path. A well-formed SQLite URL has
    # an empty netloc; anything else (e.g. `sqlite://host/x.db`) is not something we can back up.
    if parts.netloc:
        return None

    raw = unquote(parts.path)
    if raw in _MEMORY_MARKERS or raw.lstrip("/") in _MEMORY_MARKERS:
        return None

    # `sqlite:///x.db` → path `/x.db` (relative); `sqlite:////x.db` → path `//x.db` (absolute).
    if raw.startswith("//"):
        candidate = Path(raw[1:])
    else:
        candidate = Path(raw.lstrip("/"))

    if not candidate.is_absolute():
        candidate = Path(app_dir) / candidate

    # `./var/x.db` → `var/x.db`; never resolve symlinks (the file may not exist yet).
    return Path(candidate.as_posix()).resolve(strict=False)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database-url", required=True)
    parser.add_argument(
        "--app-dir",
        required=True,
        help="Base directory a relative SQLite path is resolved against.",
    )
    args = parser.parse_args(argv)

    if not is_sqlite_url(args.database_url):
        print("DATABASE_URL is not SQLite — no file-level backup applies", file=sys.stderr)
        return NOT_SQLITE

    resolved = resolve_sqlite_path(args.database_url, args.app_dir)
    if resolved is None:
        print(
            "DATABASE_URL is SQLite but resolves to no file (in-memory or empty path)",
            file=sys.stderr,
        )
        return NO_FILE

    print(str(resolved))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
