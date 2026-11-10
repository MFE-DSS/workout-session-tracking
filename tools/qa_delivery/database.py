"""Private, whole-database SQLite backups and restores into new paths only."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import tempfile
import time
from contextlib import closing
from pathlib import Path

SCHEMA = "plan_v3_20261107_01"
ROOT = Path(__file__).resolve().parents[2]


def connect_readonly(path: Path) -> sqlite3.Connection:
    path = path.resolve(strict=True)
    return sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=2)


def _schema(db):
    return [
        (kind, name, " ".join(sql.split()))
        for kind, name, sql in db.execute(
            "SELECT type,name,sql FROM sqlite_master WHERE sql IS NOT NULL "
            "AND name NOT LIKE 'sqlite_%' AND name!='alembic_version' ORDER BY type,name"
        )
    ]


def _expected_schema():
    lines = (ROOT / "data/schema_snapshot.sql").read_text().splitlines()
    statements = sorted(
        (s for s in lines if s.startswith("CREATE ")),
        key=lambda s: not s.startswith("CREATE TABLE"),
    )
    with closing(sqlite3.connect(":memory:")) as db:
        db.executescript("\n".join(statements))
        return _schema(db)


def _encoded(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=lambda v: {"blob_hex": v.hex()},
    ).encode()


def verify_database(path: Path) -> dict:
    """Return only counts/digests; inspect all data within one read transaction."""
    try:
        with closing(connect_readonly(path)) as db:
            db.execute("BEGIN")
            if db.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
                raise ValueError
            if db.execute("PRAGMA foreign_key_check").fetchone() is not None:
                raise ValueError
            if db.execute("SELECT version_num FROM alembic_version").fetchall() != [(SCHEMA,)]:
                raise ValueError
            schema = _schema(db)
            if schema != _expected_schema():
                raise ValueError
            tables = {}
            names = db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ).fetchall()
            for (name,) in names:
                quoted = '"' + name.replace('"', '""') + '"'
                columns = len(db.execute(f"SELECT * FROM {quoted} LIMIT 0").description)  # noqa: S608 — exact validated schema, quoted identifier
                digest, count = hashlib.sha256(), 0
                order = ",".join(str(i + 1) for i in range(columns))
                for row in db.execute(f"SELECT * FROM {quoted} ORDER BY {order}"):  # noqa: S608 — quoted validated identifier, integer ordinals
                    digest.update(_encoded(row) + b"\n")
                    count += 1
                tables[name] = {"rows": count, "sha256": digest.hexdigest()}
            return {
                "schema_version": "qa-database/1.0.0",
                "server_schema": SCHEMA,
                "schema_digest": hashlib.sha256(_encoded(schema)).hexdigest(),
                "tables": tables,
                "continuity_digest": hashlib.sha256(_encoded(tables)).hexdigest(),
            }
    except (OSError, sqlite3.Error, ValueError, TypeError):
        raise ValueError("qa_database_invalid") from None


def _copy_pages(source, target):
    deadline = time.monotonic() + 30

    def progress(status, remaining, total):
        if time.monotonic() > deadline:
            raise ValueError("qa_backup_timeout")

    source.backup(target, pages=128, progress=progress, sleep=0.05)


def backup_database(source: Path, destination: Path) -> dict:
    """Publish a verified private snapshot exclusively; restore uses the same path."""
    destination = destination.absolute()
    manifest_path = destination.with_name(destination.name + ".manifest.json")
    if (
        destination.exists()
        or destination.is_symlink()
        or manifest_path.exists()
        or manifest_path.is_symlink()
    ):
        raise ValueError("qa_destination_exists")
    before = verify_database(source)
    temporary = None
    published = []
    manifest_tmp = None
    try:
        fd, name = tempfile.mkstemp(prefix=".qa-backup-", dir=destination.parent)
        os.close(fd)
        temporary = Path(name)
        with closing(connect_readonly(source)) as src, closing(sqlite3.connect(temporary)) as dst:
            _copy_pages(src, dst)
            # WAL source frames are merged into a standalone, journal-free snapshot.
            dst.execute("PRAGMA journal_mode=DELETE")
        receipt = verify_database(temporary)
        if receipt != before or verify_database(source) != before:
            raise ValueError("qa_source_changed_during_capture")
        receipt["database_sha256"] = hashlib.sha256(temporary.read_bytes()).hexdigest()
        fd, name = tempfile.mkstemp(prefix=".qa-manifest-", dir=destination.parent)
        manifest_tmp = Path(name)
        with os.fdopen(fd, "wb") as stream:
            stream.write(_encoded(receipt) + b"\n")
            stream.flush()
            os.fsync(stream.fileno())
        with temporary.open("rb") as stream:
            os.fsync(stream.fileno())
        # Same-filesystem hard links give atomic, no-overwrite publication.
        os.link(manifest_tmp, manifest_path)
        published.append(manifest_path)
        os.link(temporary, destination)
        published.append(destination)
        return receipt
    except BaseException:
        for path in reversed(published):
            path.unlink(missing_ok=True)
        raise
    finally:
        for path in (temporary, manifest_tmp):
            if path is not None:
                path.unlink(missing_ok=True)


def _verify_backup(path: Path) -> dict:
    try:
        expected = json.loads(path.with_name(path.name + ".manifest.json").read_text())
        actual = verify_database(path)
        actual["database_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        if expected != actual:
            raise ValueError
        return actual
    except (OSError, ValueError, TypeError):
        raise ValueError("qa_backup_manifest_invalid") from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["backup", "restore", "verify"])
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path, nargs="?")
    args = parser.parse_args()
    try:
        if args.operation == "verify":
            receipt = verify_database(args.source)
        elif args.destination is None:
            parser.error("a new destination is required")
        else:
            if args.operation == "restore":
                _verify_backup(args.source)
            receipt = backup_database(args.source, args.destination)
        print(json.dumps(receipt, sort_keys=True))
    except (OSError, ValueError, sqlite3.Error):
        parser.exit(1, "qa_database_operation_refused\n")


if __name__ == "__main__":
    main()
