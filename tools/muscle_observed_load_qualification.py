"""Isolated, read-only prequalification evidence; never activates or certifies QA.

Run inside the explicitly authorized disposable target. Linux witnesses do not
replace the full HTTP/SQL/concurrency campaign, and this tool cannot export an
operational QUALIFIED profile. No target configuration, source or DB is written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sqlite3
import stat
import subprocess  # nosec B404
import sys
import time
from pathlib import Path


def _metadata(descriptor, trusted_uids):
    info = os.fstat(descriptor)
    if info.st_uid not in trusted_uids or info.st_mode & 0o022:
        raise ValueError("untrusted_permissions")
    return info


def inspect_relative(
    root_descriptor, relative, expected_digest, *, trusted_uids=frozenset({0}), cap=131072
):
    """Caller supplies an already trusted root FD; every descendant stays anchored.

    Accepting a UID is a trust decision, not an HTTP input. The CLI admits only
    root-owned authorities. Explicit alternate UIDs are for isolated test roots.
    ACL/mount/namespace and digest-configuration trust remain separate evidence.
    """
    parts = relative.split("/")
    if not relative or relative.startswith("/") or any(p in {"", ".", ".."} for p in parts):
        raise ValueError("invalid_path")
    if cap <= 0 or cap > 16 * 1024 * 1024:
        raise ValueError("invalid_cap")
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise ValueError("safe_open_unavailable")
    parent = os.dup(root_descriptor)
    chain = []
    try:
        for part in parts[:-1]:
            current = _metadata(parent, trusted_uids)
            chain.append(
                dict(
                    uid=current.st_uid, gid=current.st_gid, mode=oct(stat.S_IMODE(current.st_mode))
                )
            )
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            os.close(parent)
            parent = child
        _metadata(parent, trusted_uids)
        leaf = os.open(parts[-1], os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW, dir_fd=parent)
        try:
            before = _metadata(leaf, trusted_uids)
            if not stat.S_ISREG(before.st_mode) or before.st_size > cap:
                raise ValueError("authority_not_bounded_regular_file")
            with os.fdopen(os.dup(leaf), "rb") as file:
                raw = file.read(cap + 1)
            after = _metadata(leaf, trusted_uids)
            if len(raw) > cap or (before.st_ino, before.st_size, before.st_mtime_ns) != (
                after.st_ino,
                after.st_size,
                after.st_mtime_ns,
            ):
                raise ValueError("authority_changed")
            actual = hashlib.sha256(raw).hexdigest()
            if actual != expected_digest:
                raise ValueError("digest_mismatch")
            return dict(
                sha256=actual,
                bytes=len(raw),
                uid=after.st_uid,
                gid=after.st_gid,
                mode=oct(stat.S_IMODE(after.st_mode)),
                checked_parent_descriptors=chain,
                acl_and_mount_qualification="NOT_PROVEN_BY_MODE_BITS",
            )
        finally:
            os.close(leaf)
    finally:
        os.close(parent)


def inspect_absolute(path, expected_digest):
    # Start at / and never resolve a symlink away before checking its components.
    if not path.startswith("/"):
        raise ValueError("absolute_authority_path_required")
    root = os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        return inspect_relative(root, path[1:], expected_digest)
    finally:
        os.close(root)


def _bounded_text(path, cap=131072):
    try:
        with open(path, "rb") as file:
            raw = file.read(cap + 1)
        return raw.decode("utf-8", errors="strict") if len(raw) <= cap else None
    except (OSError, UnicodeError):
        return None


def inspect_runtime(expected_python="3.11.14", expected_sqlite=None):
    reasons = ["FULL_TARGET_CAMPAIGN_NOT_EXECUTED", "IMAGE_AND_SOURCE_PROFILE_NOT_ATTESTED"]
    fingerprint = dict(
        platform=sys.platform,
        machine=platform.machine(),
        python=platform.python_version(),
        sqlite=sqlite3.sqlite_version,
    )
    if sys.platform != "linux":
        reasons.append("LINUX_REQUIRED")
    if fingerprint["python"] != expected_python:
        reasons.append("PYTHON_TARGET_MISMATCH")
    if expected_sqlite is None:
        reasons.append("SQLITE_TARGET_NOT_SPECIFIED")
    elif fingerprint["sqlite"] != expected_sqlite:
        reasons.append("SQLITE_TARGET_MISMATCH")
    mounts = _bounded_text("/proc/self/mountinfo") if sys.platform == "linux" else None
    return dict(
        contract="muscle-observed-load-isolated-qualification/1.0.0",
        runtime="HOLD",
        path_security="HOLD",
        reader="NOT_QUALIFIED",
        fingerprint=fingerprint,
        os_release=_bounded_text("/etc/os-release", 8192) if sys.platform == "linux" else None,
        identity=dict(uid=os.getuid(), gid=os.getgid(), groups=os.getgroups()),
        cgroup=dict(
            memory_max=_bounded_text("/sys/fs/cgroup/memory.max", 128),
            cpu_max=_bounded_text("/sys/fs/cgroup/cpu.max", 128),
            pids_max=_bounded_text("/sys/fs/cgroup/pids.max", 128),
        )
        if sys.platform == "linux"
        else None,
        mount_evidence_available=mounts is not None,
        # Only namespace mountpoint/type/options, no backing source or credentials.
        mounts=[
            dict(
                point=line.split()[4],
                options=line.split()[5],
                filesystem=line.split(" - ", 1)[1].split()[0],
            )
            for line in (mounts or "").splitlines()
            if " - " in line
        ],
        measurements=dict(
            http_latency=None,
            sql_statements=None,
            sql_vm_steps=None,
            sql_seconds=None,
            cpu_seconds=None,
            peak_rss_bytes=None,
            address_space_bytes=None,
            output_bytes=None,
            concurrency=None,
            snapshot_integrity=None,
            owner_isolation=None,
            worker_witnesses=None,
        ),
        reasons=reasons,
    )


def probe_worker(root):
    """Actual limited child witnesses, only on Linux; never run stress on the Mac."""
    if sys.platform != "linux":
        return dict(state="NOT_EXECUTED", reason="LINUX_REQUIRED")
    # This fixed entrypoint is supplied by the pinned candidate checkout, not a bundle.
    worker = Path(root) / "app/services/muscle_observed_load/worker.py"
    from app.services.muscle_observed_load.supervisor import collect_child

    results = {}
    for mode in ("--qualify-limits", "--qualify-cpu"):
        start = time.monotonic()
        child = subprocess.Popen(  # noqa: S603  # nosec B603
            [sys.executable, "-I", "-B", str(worker), mode],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env={"PATH": os.defpath, "LANG": "C.UTF-8", "PYTHONDONTWRITEBYTECODE": "1"},
        )
        try:
            raw = collect_child(child, b"", max_bytes=4096, deadline=start + 6)
            result = dict(output=json.loads(raw), outcome="RETURNED")
        except Exception as error:
            result = dict(outcome=type(error).__name__)
        result.update(
            returncode=child.returncode,
            reaped=child.poll() is not None,
            total_elapsed_seconds=time.monotonic() - start,
        )
        results[mode] = result
    return dict(state="OBSERVED_WITNESSES_NOT_TARGET_QUALIFICATION", results=results)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-python", default="3.11.14")
    parser.add_argument("--expected-sqlite")
    parser.add_argument("--authority")
    parser.add_argument("--authority-sha256")
    parser.add_argument("--probe-worker", action="store_true")
    args = parser.parse_args(argv)
    report = inspect_runtime(args.expected_python, args.expected_sqlite)
    if bool(args.authority) != bool(args.authority_sha256):
        parser.error("authority and its independently trusted digest are required together")
    if args.authority:
        try:
            report["authority"] = inspect_absolute(args.authority, args.authority_sha256)
        except (OSError, ValueError):
            report["authority"] = dict(state="HOLD", reason="TRUSTED_PATH_OR_DIGEST_NOT_PROVEN")
        report["reasons"].append("ACL_MOUNTS_AND_EXPECTED_DIGEST_ORIGIN_REQUIRE_TARGET_PROOF")
    if args.probe_worker:
        if report["fingerprint"]["python"] == args.expected_python:
            report["measurements"]["worker_witnesses"] = probe_worker(
                Path(__file__).resolve().parents[1]
            )
        else:
            report["reasons"].append("WORKER_NOT_RUN_ON_DIFFERENT_PYTHON_TARGET")
    print(json.dumps(report, ensure_ascii=False, allow_nan=False, separators=(",", ":")))
    return 2  # HOLD is a deliberate non-success exit, never operational readiness.


if __name__ == "__main__":
    raise SystemExit(main())
