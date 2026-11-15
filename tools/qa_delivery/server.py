"""Supervised synthetic QA: canonical loopback API plus bounded public facade."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import shutil
import signal
import socket
import sqlite3
import stat
import subprocess
import sys
import tempfile
import time
from contextlib import asynccontextmanager, closing
from dataclasses import dataclass, field
from pathlib import Path

import httpx
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from tools.qa_delivery.database import ROOT, SCHEMA, _expected_schema, _schema, connect_readonly
from tools.qa_delivery.identity import read_version
from tools.qa_delivery.ownership import load_anchor, verify_ownership
from tools.qa_delivery.releases import FEATURE_PROFILES
from tools.release_qa_gateway import WindowBudget, allowed_path, create_gateway, failure


@dataclass(frozen=True)
class QAConfig:
    db_path: Path
    bundle_root: Path
    environment_id: str
    source_sha: str
    access: dict = field(default_factory=dict)
    backend_port: int = 8140
    ownership_anchor: dict = field(default_factory=dict)
    ownership_anchor_sha256: str = ""
    feature_environment: dict = field(default_factory=dict, repr=False)
    feature_profiles: dict = field(default_factory=dict)


async def _liveness_only(request, call_next):
    # Process signal only: never database/science/readiness evidence.
    if request.method == "GET" and request.url.path == "/__qa_liveness":
        return JSONResponse(
            {"alive": True, "data_ready": False}, headers={"Cache-Control": "no-store"}
        )
    return await call_next(request)


def create_qa_app(config: QAConfig) -> Starlette:
    gateway = create_gateway({}, backend_port=config.backend_port, access=config.access)
    stopped, active = False, 0
    budget = WindowBudget()

    def version():
        return read_version(
            config.db_path,
            environment_id=config.environment_id,
            source_sha=config.source_sha,
            bundle_root=config.bundle_root,
            ownership_anchor=config.ownership_anchor,
            ownership_anchor_sha256=config.ownership_anchor_sha256,
            feature_profiles=config.feature_profiles,
        )

    # Full attestation once before exposing this app. No startup seeds/migrations.
    version()
    expected_schema = _expected_schema()

    def schema_available():
        with closing(connect_readonly(config.db_path)) as db:
            db.execute("BEGIN")
            verify_ownership(
                db,
                config.ownership_anchor,
                environment_id=config.environment_id,
                expected_digest=config.ownership_anchor_sha256,
            )
            if (
                db.execute("SELECT version_num FROM alembic_version").fetchall() != [(SCHEMA,)]
                or _schema(db) != expected_schema
            ):
                raise ValueError("qa_schema_unavailable")

    @asynccontextmanager
    async def lifespan(app):
        nonlocal stopped
        try:
            yield
        finally:
            stopped = True

    async def identity(request):
        return JSONResponse(request.state.qa_version, headers={"Cache-Control": "no-store"})

    async def health(request):
        try:
            async with httpx.AsyncClient(
                timeout=2, trust_env=False, follow_redirects=False
            ) as client:
                response = await client.get(f"http://127.0.0.1:{config.backend_port}/healthz")
                if response.status_code != 200:
                    return failure(503, "qa_upstream_unavailable")
        except httpx.HTTPError:
            return failure(503, "qa_upstream_unavailable")
        return JSONResponse(
            {"status": "ok", "transport_only": True}, headers={"Cache-Control": "no-store"}
        )

    app = Starlette(
        lifespan=lifespan,
        routes=[
            Route("/__qa_version", identity),
            Route("/__qa_health", health),
            Mount("/", gateway),
        ],
    )

    async def readiness(request, call_next):
        nonlocal active
        raw_path = request.scope.get("raw_path", b"").decode("ascii", errors="replace")
        if not allowed_path(raw_path) and (
            request.url.path not in {"/__qa_version", "/__qa_health"} or request.method != "GET"
        ):
            return failure(404, "not_found")
        if stopped or active >= 8:
            return failure(503, "qa_capacity_unavailable")
        if not budget.allow(time.monotonic()):
            return failure(429, "qa_rate_limited")
        active += 1
        try:
            try:
                if request.url.path in {"/__qa_version", "/__qa_health"}:
                    request.state.qa_version = await asyncio.to_thread(version)
                else:
                    # Canonical V3 guards read current authority on business calls.
                    # Do not spawn a science worker or hash all journal rows here.
                    await asyncio.to_thread(schema_available)
            except (OSError, ValueError, sqlite3.Error):
                return failure(503, "qa_dependency_unavailable")
            return await call_next(request)
        finally:
            active -= 1

    app.add_middleware(BaseHTTPMiddleware, dispatch=readiness)
    app.add_middleware(BaseHTTPMiddleware, dispatch=_liveness_only)
    return app


def _safe_environment():
    """Reject inherited sensitive features, then construct child env from scratch."""
    disabled = {"", "0", "false", "off", "no"}
    for key, value in os.environ.items():
        name = key.upper()
        if name.startswith(("BODY_", "SMTP_", "SENTRY_", "PERF_")) or name in {
            "SQLALCHEMY_ECHO",
            "SQL_ECHO",
        }:
            if value.lower() not in disabled:
                raise ValueError("qa_unsafe_environment")


def _source_sha():
    marker = ROOT / ".qa-source-sha"
    if marker.is_file():
        value = marker.read_text().strip()
    else:
        git = shutil.which("git")
        if git is None:
            raise ValueError("qa_source_unavailable")
        result = subprocess.run(  # noqa: S603 — fixed read-only Git command
            [git, "-C", str(ROOT), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode:
            raise ValueError("qa_source_unavailable")
        value = result.stdout.strip()
    if not re.fullmatch("[0-9a-f]{40}", value):
        raise ValueError("qa_source_unavailable")
    return value


FEATURE_PREFIXES = {"NUT": "NUTRITION", "LIBRARY": "LIBRARY", "BUILDER": "PROGRAM_BUILDER"}


def _closed_pairs(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("qa_feature_duplicate_key")
        value[key] = item
    return value


def _private_feature_text(path):
    """Read only current-user, nonlinked 0600 file in private 0700 directory."""
    path = Path(path)
    if not path.is_absolute() or any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError("qa_feature_private_reference_required")
    parent = path.parent.stat()
    if parent.st_uid != os.getuid() or stat.S_IMODE(parent.st_mode) != 0o700:
        raise ValueError("qa_feature_private_directory_required")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd) as stream:
        info = os.fstat(stream.fileno())
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_uid != os.getuid()
            or stat.S_IMODE(info.st_mode) != 0o600
            or info.st_size > 16384
        ):
            raise ValueError("qa_feature_private_reference_required")
        return stream.read(16385)


def load_feature_config(path):
    """Optional synthetic capability config. Never creates consent or rotates keys."""
    try:
        raw = json.loads(_private_feature_text(path), object_pairs_hook=_closed_pairs)
        if (
            set(raw) != {"schema_version", "included_features", "signatures"}
            or raw["schema_version"] != "qa-feature-config/1.0.0"
        ):
            raise ValueError
        included = raw["included_features"]
        if (
            not isinstance(included, list)
            or not included
            or any(not isinstance(x, str) for x in included)
            or len(set(included)) != len(included)
            or not set(included) <= set(FEATURE_PROFILES)
            or ("BUILDER" in included and "LIBRARY" not in included)
            or set(raw["signatures"]) != set(included) - {"BODY"}
        ):
            raise ValueError
        env, identities, keys = {}, set(), set()
        for name in included:
            if name == "BODY":
                env["BODY_ASSESSMENT_ENABLED"] = "true"
                continue
            reference = raw["signatures"][name]
            if set(reference) != {"identity", "signing_key_file"}:
                raise ValueError
            identity = reference["identity"]
            key = _private_feature_text(reference["signing_key_file"]).strip()
            if (
                not isinstance(identity, str)
                or not re.fullmatch(r"qa-[a-z0-9_-]{5,60}", identity)
                or len(key) < 32
                or len(key) > 4096
                or "\n" in key
                or identity in identities
                or key in keys
            ):
                raise ValueError
            identities.add(identity)
            keys.add(key)
            prefix = FEATURE_PREFIXES[name]
            flag = "NUTRITION_MANUAL" if name == "NUT" else prefix
            env[flag + "_CONTROLLED_TEST_ENABLED"] = "true"
            env[prefix + "_BACKEND_IDENTITY"] = identity
            env[prefix + "_SIGNING_KEY"] = key
        return env, {name: FEATURE_PROFILES[name] for name in sorted(included)}
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        raise ValueError("qa_feature_configuration_refused") from None


def _facade_environment():
    return {
        "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
        "PYTHONPATH": str(ROOT),
        "PYTHONDONTWRITEBYTECODE": "1",
        "APP_ENV": "test",
    }


def _load_config(path):
    _safe_environment()
    raw = json.loads(path.read_text(), object_pairs_hook=_closed_pairs)
    expected = {
        "db_path",
        "bundle_root",
        "environment_id",
        "source_sha",
        "access_file",
        "secret_file",
        "data_scope",
        "ownership_anchor_file",
        "ownership_anchor_sha256",
    }
    if (
        set(raw) not in (expected, expected | {"feature_config_file"})
        or raw["data_scope"] != "SYNTHETIC_ONLY"
    ):
        raise ValueError("qa_config_invalid")
    paths = {
        key: Path(raw[key])
        for key in ("db_path", "bundle_root", "access_file", "secret_file", "ownership_anchor_file")
    }
    if any(not p.is_absolute() for p in paths.values()):
        raise ValueError("qa_config_invalid")
    if raw["source_sha"] != _source_sha():
        raise ValueError("qa_source_mismatch")
    # Private references only: never accept inline auth material or log its contents.
    for key in ("access_file", "secret_file"):
        if paths[key].stat().st_mode & 0o077:
            raise ValueError("qa_private_reference_required")
    secret = paths["secret_file"].read_text().strip()
    if len(secret) < 32 or "\n" in secret:
        raise ValueError("qa_secret_invalid")
    feature_env, profiles = (
        load_feature_config(raw["feature_config_file"])
        if "feature_config_file" in raw
        else ({}, {})
    )
    config = QAConfig(
        db_path=paths["db_path"],
        bundle_root=paths["bundle_root"],
        environment_id=raw["environment_id"],
        source_sha=raw["source_sha"],
        access=json.loads(paths["access_file"].read_text()),
        feature_environment=feature_env,
        feature_profiles=profiles,
        ownership_anchor=load_anchor(
            paths["ownership_anchor_file"],
            environment_id=raw["environment_id"],
            expected_digest=raw["ownership_anchor_sha256"],
        ),
        ownership_anchor_sha256=raw["ownership_anchor_sha256"],
    )
    create_gateway({}, access=config.access)  # Validate assigned synthetic names.
    read_version(
        config.db_path,
        environment_id=config.environment_id,
        source_sha=config.source_sha,
        bundle_root=config.bundle_root,
        ownership_anchor=config.ownership_anchor,
        ownership_anchor_sha256=config.ownership_anchor_sha256,
        feature_profiles=config.feature_profiles,
    )
    return config, secret


def _child_environment(config, secret):
    env = {
        "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
        "PYTHONPATH": str(ROOT),
        "PYTHONDONTWRITEBYTECODE": "1",
        "APP_ENV": "test",
        "APP_SECRET_KEY": secret,
        "DATABASE_URL": f"sqlite:///{config.db_path}",
        "PLAN_V3_BUNDLE_PATH": str(config.bundle_root),
        "APP_HOST": "127.0.0.1",
        "APP_PORT": "8140",
    }
    for key in ("CONTROLLED_TEST", "ACQUISITION", "EVALUATION", "CREATION", "GUIDANCE"):
        env[f"PLAN_V3_{key}_ENABLED"] = "true"
    env.update(config.feature_environment)
    return env


def _require_free_loopback(port):
    # A pre-existing writer must never accidentally become this facade's upstream.
    try:
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", port))
    except OSError:
        raise ValueError("qa_loopback_port_in_use") from None


def supervise(config, secret, config_path, port):
    """Own both child processes; loss of either stops the other and fails service."""
    # Re-admit immediately before starting the canonical writer.
    with closing(connect_readonly(config.db_path)) as db:
        db.execute("BEGIN")
        verify_ownership(
            db,
            config.ownership_anchor,
            environment_id=config.environment_id,
            expected_digest=config.ownership_anchor_sha256,
        )
    _require_free_loopback(8140)
    children, stopping = [], False

    def stop(signum, frame):
        nonlocal stopping
        stopping = True

    previous = {s: signal.signal(s, stop) for s in (signal.SIGINT, signal.SIGTERM)}
    try:
        # Settings reads .env relative to cwd; private empty cwd prevents ambient config.
        with tempfile.TemporaryDirectory(prefix="auren-qa-runtime-") as runtime:
            env = _child_environment(config, secret)
            commands = [
                [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "app.main:app",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "8140",
                    "--workers",
                    "1",
                    "--lifespan",
                    "off",
                    "--no-access-log",
                    "--no-proxy-headers",
                    "--timeout-keep-alive",
                    "5",
                    "--timeout-graceful-shutdown",
                    "10",
                    "--limit-concurrency",
                    "12",
                ],
                [
                    sys.executable,
                    "-m",
                    "tools.qa_delivery.server",
                    "--config",
                    str(config_path),
                    "--facade-only",
                    "--port",
                    str(port),
                ],
            ]
            for index, command in enumerate(commands):
                children.append(
                    subprocess.Popen(  # noqa: S603 — fixed interpreter/modules, no shell
                        command,
                        cwd=runtime,
                        env=env if index == 0 else _facade_environment(),
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                )
            while not stopping and all(child.poll() is None for child in children):
                time.sleep(0.1)
            if not stopping:
                print("qa_owned_child_exited_service_stopped", file=sys.stderr)
            return 0 if stopping else 1
    finally:
        for child in children:
            if child.poll() is None:
                child.terminate()
        deadline = time.monotonic() + 12
        for child in children:
            try:
                child.wait(timeout=max(0.01, deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()
        for sig, handler in previous.items():
            signal.signal(sig, handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--facade-only", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--port", default=os.environ.get("PORT", "8080"))
    args = parser.parse_args()
    try:
        _safe_environment()
        if (
            not re.fullmatch(r"[0-9]{1,5}", args.port)
            or not 1 <= int(args.port) <= 65535
            or int(args.port) == 8140
        ):
            raise ValueError("qa_port_invalid")
        config, secret = _load_config(args.config.resolve())
        if args.validate_only:
            print("QA_CONFIG_VALIDATED_NO_SERVICE_STARTED")
            return
        if args.facade_only:
            import uvicorn

            uvicorn.run(
                create_qa_app(config),
                host="0.0.0.0",
                port=int(args.port),
                workers=1,
                access_log=False,
                proxy_headers=False,
                timeout_keep_alive=5,
                limit_concurrency=12,
                timeout_graceful_shutdown=10,
                log_level="critical",
            )
        else:
            raise SystemExit(supervise(config, secret, args.config.resolve(), int(args.port)))
    except (OSError, ValueError, TypeError, KeyError):
        parser.exit(1, "qa_unsafe_environment_or_configuration_refused\n")


if __name__ == "__main__":
    main()
