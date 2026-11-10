"""Private admission of existing synthetic ownership tuples; no database writes.

This is a fixed QA continuity witness, not an unforgeable database UUID or a
lifetime identity service. Deleting/rebinding anchored rows requires separately
authorized maintenance; authentication changes and new rows do not rebind it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import stat
from contextlib import closing
from pathlib import Path

from tools.qa_delivery.database import ROOT, _encoded, connect_readonly, verify_database

VERSION = "qa-ownership-anchor/1.0.0"
# Model identities, excluding mutable auth, labels, activity and SCI authority.
# Blueprint source events are append-only; these refs bind original subjects.
TABLES = {
    "users": (
        "SELECT id,username,created_at FROM users ORDER BY id",
        "SELECT id,username,created_at FROM users WHERE id=?",
        (int, str, str),
    ),
    "device_sessions": (
        "SELECT id,user_id,created_at FROM device_sessions ORDER BY id",
        "SELECT id,user_id,created_at FROM device_sessions WHERE id=?",
        (str, int, str),
    ),
    "blueprint_source_events": (
        "SELECT id,owner_id,source_revision,request_id,body_digest,kind,recorded_at FROM blueprint_source_events ORDER BY id",
        "SELECT id,owner_id,source_revision,request_id,body_digest,kind,recorded_at FROM blueprint_source_events WHERE id=?",
        (str, int, int, str, str, str, str),
    ),
}


def anchor_digest(anchor):
    return hashlib.sha256(_encoded(anchor)).hexdigest()


def validate_anchor(anchor, environment_id, expected_digest):
    try:
        if (
            not isinstance(anchor, dict)
            or set(anchor) != {"schema_version", "environment_id", *TABLES}
            or anchor["schema_version"] != VERSION
            or anchor["environment_id"] != environment_id
            or not isinstance(environment_id, str)
            or not re.fullmatch(r"qa-[a-z0-9_-]{3,60}", environment_id)
            or not isinstance(expected_digest, str)
            or not re.fullmatch(r"[0-9a-f]{64}", expected_digest)
            or anchor_digest(anchor) != expected_digest
        ):
            raise ValueError
        users = set()
        for table, (_, _, types) in TABLES.items():
            rows = anchor[table]
            if not isinstance(rows, list) or (table != "blueprint_source_events" and not rows):
                raise ValueError
            seen = set()
            for row in rows:
                if not isinstance(row, list) or len(row) != len(types):
                    raise ValueError
                for value, kind in zip(row, types, strict=True):
                    if kind is int:
                        if type(value) is not int or value < 1:
                            raise ValueError
                    elif not isinstance(value, str) or not value or len(value) > 512:
                        raise ValueError
                if row[0] in seen or (table != "users" and row[1] not in users):
                    raise ValueError
                if table == "users" and not re.fullmatch(r"qa02-[a-z0-9_-]+", row[1]):
                    raise ValueError
                seen.add(row[0])
            if table == "users":
                users = seen
        return anchor
    except (KeyError, TypeError, ValueError):
        raise ValueError("qa_ownership_anchor_invalid") from None


def verify_ownership(db, anchor, *, environment_id, expected_digest):
    """Check the captured subset inside the caller's current read transaction."""
    validate_anchor(anchor, environment_id, expected_digest)
    for table, (_, query, _) in TABLES.items():
        for row in anchor[table]:
            try:
                actual = db.execute(query, (row[0],)).fetchone()
            except sqlite3.Error:
                raise ValueError("qa_ownership_anchor_unavailable") from None
            if actual is None or list(actual) != row:
                raise ValueError("qa_ownership_anchor_mismatch")
    return expected_digest


def load_anchor(path, *, environment_id, expected_digest):
    try:
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077 or info.st_uid != os.getuid():
            raise ValueError
        return validate_anchor(json.loads(path.read_text()), environment_id, expected_digest)
    except (OSError, ValueError, TypeError):
        raise ValueError("qa_ownership_anchor_invalid") from None


def capture_anchor(db_path, environment_id):
    """Explicit maintenance only. Never called by server, activation or publish."""
    verify_database(db_path)
    anchor = {"schema_version": VERSION, "environment_id": environment_id}
    with closing(connect_readonly(db_path)) as db:
        db.execute("BEGIN")
        for table, (query, _, _) in TABLES.items():
            anchor[table] = [list(row) for row in db.execute(query)]
    return validate_anchor(anchor, environment_id, anchor_digest(anchor))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--environment-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        output = args.output.absolute()
        parent = output.parent.stat()
        if (
            output.resolve().is_relative_to(ROOT.resolve())
            or output.parent.is_symlink()
            or parent.st_uid != os.getuid()
            or stat.S_IMODE(parent.st_mode) != 0o700
        ):
            raise ValueError
        anchor = capture_anchor(args.source, args.environment_id)
        fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(_encoded(anchor) + b"\n")
        print(json.dumps({"ownership_anchor_sha256": anchor_digest(anchor)}))
    except (OSError, ValueError, TypeError, sqlite3.Error):
        parser.exit(1, "qa_ownership_capture_refused\n")


if __name__ == "__main__":
    main()
