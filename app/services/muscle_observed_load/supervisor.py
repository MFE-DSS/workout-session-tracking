"""One child per HTTP process, no queue, bounded bytes/time, generic failures."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import selectors
import sqlite3
import stat
import subprocess  # nosec B404
import sys
import threading
import time
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from .contracts import ObservedLoadReadError, ObservedLoadResponse, iso
from .limits import ReadLimits
from .sqlite_source import bounded_json

WORKER_SLOT = threading.Lock()
ROOT = Path(__file__).resolve().parents[3]
PROFILE_BYTES = 131072
_REQUIRED = {
    *(
        str(path.relative_to(ROOT))
        for path in (ROOT / "app/services/muscle_observed_load").glob("*.py")
    ),
    "app/services/sci_catalogue.py",
    "app/services/sci_identity.py",
    "app/services/sci_exposure.py",
    "app/services/exercise_identity.py",
    "data/sci/exercise_catalogue.json",
    "data/sci/exercise_catalogue.schema.json",
    "data/exercise_knowledge_base.json",
    "data/sci/exposure_credit_policy.json",
    "data/sci/readiness_bodymap_projection.v1.json",
}


def fingerprint():
    return dict(
        platform=sys.platform,
        python=platform.python_version(),
        sqlite=sqlite3.sqlite_version,
        machine=platform.machine(),
    )


def load_runtime_profile(path, expected_digest, *, with_view=False):
    try:
        if sys.platform != "linux" or not path or len(expected_digest) != 64:
            raise ValueError("runtime_unqualified")
        profile_path = Path(path)
        descriptor = os.open(
            profile_path, os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0)
        )
        with os.fdopen(descriptor, "rb") as file:
            if not stat.S_ISREG(os.fstat(file.fileno()).st_mode):
                raise ValueError("runtime_profile_not_regular")
            raw = file.read(PROFILE_BYTES + 1)
        if len(raw) > PROFILE_BYTES or hashlib.sha256(raw).hexdigest() != expected_digest:
            raise ValueError("runtime_profile_mismatch")
        profile = bounded_json(raw, ReadLimits())
        if (
            set(profile)
            != {
                "qualification_state",
                "qualification_ref",
                "qualification_proof_sha256",
                "fingerprint",
                "limits",
                "source_pins",
                "http_processes",
                "container_memory_bytes",
                "source_sha",
            }
            or profile["qualification_state"] != "QUALIFIED"
            or profile["fingerprint"] != fingerprint()
            or profile["limits"] != asdict(ReadLimits())
            or not profile["qualification_ref"]
            or len(profile["qualification_proof_sha256"]) != 64
            or profile["http_processes"] != 1
            or type(profile["container_memory_bytes"]) is not int
            or profile["container_memory_bytes"] < ReadLimits().address_space
            or len(profile["source_sha"]) != 40
        ):
            raise ValueError("runtime_profile_unqualified")
        pins = profile["source_pins"]
        if type(pins) is not dict or set(pins) != _REQUIRED:
            raise ValueError("runtime_source_profile_incomplete")
        from .provenance import SourceView

        view = SourceView(ROOT, expected=pins)
        for relative, expected in pins.items():
            view.read(relative, expected)
        # Parse actual authority under the approved ceiling before a job is admitted.
        view.json("data/sci/exercise_catalogue.json")
        return (profile, view) if with_view else profile
    except (OSError, ValueError, TypeError, KeyError, OverflowError):
        raise ObservedLoadReadError() from None


def encode_job(owner_id, query, as_of):
    body = json.dumps(
        {
            "owner_id": owner_id,
            "from": iso(query.window_start),
            "until": iso(query.window_until),
            "as_of": iso(as_of),
        },
        allow_nan=False,
        separators=(",", ":"),
    ).encode()
    if len(body) > 1024:
        raise ObservedLoadReadError()
    return body


def collect_child(process, body, *, max_bytes, deadline):
    output = bytearray()
    try:
        if len(body) > 1024:
            raise ObservedLoadReadError()
        process.stdin.write(body)
        process.stdin.close()
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise ObservedLoadReadError()
                if not selector.select(min(remaining, 0.05)):
                    continue
                chunk = os.read(process.stdout.fileno(), min(4096, max_bytes + 1 - len(output)))
                if not chunk:
                    break
                output.extend(chunk)
                if len(output) > max_bytes:
                    raise ObservedLoadReadError()
        process.wait(timeout=max(0.001, deadline - time.monotonic()))
        if process.returncode:
            raise ObservedLoadReadError()
        return bytes(output)
    except (OSError, ValueError, subprocess.SubprocessError):
        raise ObservedLoadReadError() from None
    finally:
        if process.poll() is None:
            process.kill()
        process.wait(timeout=1)
        if process.stdout:
            process.stdout.close()
        if process.stdin and not process.stdin.closed:
            process.stdin.close()


def read_owned_muscle_observed_load(
    owner_id, query, *, runtime_profile, database_url, bundle_root=""
):
    started = time.monotonic()
    if not WORKER_SLOT.acquire(blocking=False):
        raise ObservedLoadReadError()
    try:
        path, expected = runtime_profile
        # All profile/source reads occur under child limits and parent deadline.
        # In particular, no FIFO/network mount can stall the HTTP parent here.
        if (
            sys.platform != "linux"
            or not path
            or len(expected) != 64
            or not database_url.startswith("sqlite:///")
            or "?" in database_url
        ):
            raise ObservedLoadReadError()
        as_of = datetime.now(UTC)
        worker = ROOT / "app/services/muscle_observed_load/worker.py"
        child = subprocess.Popen(  # noqa: S603  # nosec B603
            # Fixed interpreter/entrypoint, shell=False, server paths only; no Bearer.
            [sys.executable, "-I", "-B", str(worker), path, expected, database_url, bundle_root],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            cwd=ROOT,
            env={"PATH": os.defpath, "LANG": "C.UTF-8", "PYTHONDONTWRITEBYTECODE": "1"},
        )
        raw = collect_child(
            child,
            encode_job(owner_id, query, as_of),
            max_bytes=ReadLimits().output_bytes,
            deadline=started + ReadLimits().wall_seconds,
        )
        response = ObservedLoadResponse.model_validate(bounded_json(raw, ReadLimits()))
        data = response.model_dump()
        if (
            data.get("owner_id") != owner_id
            or data.get("window")
            != {
                "from": iso(query.window_start),
                "until": iso(query.window_until),
                "time_zone": "UTC",
            }
            or data.get("as_of") != iso(as_of)
            or data["consistency"]["runtime_profile_digest"] != expected
        ):
            raise ObservedLoadReadError()
        return response
    except (OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError):
        raise ObservedLoadReadError() from None
    finally:
        WORKER_SLOT.release()
