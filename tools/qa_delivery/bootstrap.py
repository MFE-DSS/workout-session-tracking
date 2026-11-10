"""Maintenance bootstrap: never seed data or activate on database presence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from pathlib import Path

from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from tools.qa_delivery.server import _load_config, _source_sha


def maintenance_app():
    async def respond(request):
        if request.method == "GET" and request.url.path == "/__qa_liveness":
            return JSONResponse(
                {"alive": True, "data_ready": False}, headers={"Cache-Control": "no-store"}
            )
        return JSONResponse(
            {"error": "qa_maintenance"},
            status_code=503,
            headers={"Retry-After": "30", "Cache-Control": "no-store"},
        )

    app = Starlette()
    app.add_middleware(BaseHTTPMiddleware, dispatch=lambda request, call_next: respond(request))
    return app


def _private(path):
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077 or info.st_uid != os.getuid():
        raise ValueError("qa_activation_refused")


def activation_command(marker: Path, config: Path, port: str):
    """Return fixed supervisor argv only after private marker and full validation.

    Marker creation belongs to the separately approved cutover. A marker arriving
    during maintenance has no effect until an explicit process restart.
    """
    try:
        if (
            not re.fullmatch(r"[0-9]{1,5}", port)
            or not 1 <= int(port) <= 65535
            or int(port) == 8140
        ):
            raise ValueError
        if not marker.exists() and not marker.is_symlink():
            return None
        _private(marker)
        _private(config)
        raw = json.loads(marker.read_text())
        if set(raw) != {"schema_version", "source_sha", "config_sha256"}:
            raise ValueError
        if raw["schema_version"] != "qa-activation/1.0.0" or raw["source_sha"] != _source_sha():
            raise ValueError
        if raw["config_sha256"] != hashlib.sha256(config.read_bytes()).hexdigest():
            raise ValueError
        validated, _ = _load_config(config)
        # Qualification must run as the real runtime user; no chmod/chown/root fallback.
        if validated.db_path.is_symlink() or not os.access(validated.db_path, os.R_OK | os.W_OK):
            raise ValueError
        if not os.access(validated.db_path.parent, os.W_OK | os.X_OK):
            raise ValueError
        return [
            sys.executable,
            "-m",
            "tools.qa_delivery.server",
            "--config",
            str(config),
            "--port",
            port,
        ]
    except (OSError, ValueError, TypeError, KeyError):
        raise ValueError("qa_activation_refused") from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("/run/qa/config.json"))
    parser.add_argument("--activation", type=Path, default=Path("/var/lib/qa/activation.json"))
    parser.add_argument("--port", default=os.environ.get("PORT", "8080"))
    args = parser.parse_args()
    try:
        command = activation_command(args.activation, args.config, args.port)
        if command:
            os.execv(sys.executable, command)  # noqa: S606 — fixed interpreter and module
        import uvicorn

        uvicorn.run(
            maintenance_app(),
            host="0.0.0.0",
            port=int(args.port),
            workers=1,
            access_log=False,
            proxy_headers=False,
            log_level="critical",
            limit_concurrency=12,
            timeout_keep_alive=5,
        )
    except (OSError, ValueError, TypeError):
        parser.exit(1, "qa_bootstrap_refused\n")


if __name__ == "__main__":
    main()
