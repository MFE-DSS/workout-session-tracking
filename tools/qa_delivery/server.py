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
from tools.release_qa_gateway import WindowBudget, allowed_path, create_gateway, failure


@dataclass(frozen=True)
class QAConfig:
    db_path: Path
    bundle_root: Path
    environment_id: str
    source_sha: str
    access: dict = field(default_factory=dict)
    backend_port: int = 8140


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
        )

    # Full attestation once before exposing this app. No startup seeds/migrations.
    version()
    expected_schema = _expected_schema()

    def schema_available():
        with closing(connect_readonly(config.db_path)) as db:
            db.execute("BEGIN")
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


def _load_config(path):
    _safe_environment()
    raw = json.loads(path.read_text())
    expected = {
        "db_path",
        "bundle_root",
        "environment_id",
        "source_sha",
        "access_file",
        "secret_file",
        "data_scope",
    }
    if set(raw) != expected or raw["data_scope"] != "SYNTHETIC_ONLY":
        raise ValueError("qa_config_invalid")
    paths = {
        key: Path(raw[key]) for key in ("db_path", "bundle_root", "access_file", "secret_file")
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
    config = QAConfig(
        db_path=paths["db_path"],
        bundle_root=paths["bundle_root"],
        environment_id=raw["environment_id"],
        source_sha=raw["source_sha"],
        access=json.loads(paths["access_file"].read_text()),
    )
    create_gateway({}, access=config.access)  # Validate assigned synthetic names.
    read_version(
        config.db_path,
        environment_id=config.environment_id,
        source_sha=config.source_sha,
        bundle_root=config.bundle_root,
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
            for command in commands:
                children.append(
                    subprocess.Popen(  # noqa: S603 — fixed interpreter/modules, no shell
                        command,
                        cwd=runtime,
                        env=env,
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
