#!/usr/bin/env python3
"""Sb_26.6 — performance baseline benchmark via TestClient.

Hits each route in `_ROUTES` N times, computes min / median / p95 / max
latency, and writes a structured JSON to `docs/performance/PERFORMANCE_BASELINE_V1.json`.

The script does NOT touch network. It uses FastAPI's `TestClient` against
a fresh test DB — same fixture pattern as `tests/conftest.py`, so results
are reproducible (modulo CPU jitter).

Usage:
    python scripts/perf_baseline.py                 # full N=50 run, write JSON
    python scripts/perf_baseline.py --smoke         # N=5 quick run
    python scripts/perf_baseline.py --check-budget  # also fail if any p95 > budget
    python scripts/perf_baseline.py --no-write      # don't update the JSON

Output JSON schema (stable):
    {
      "generated_at": "<ISO-8601 UTC>",
      "git_sha": "<short>",
      "environment": "<dev|ci|prod>",
      "python_version": "...",
      "iterations": N,
      "routes": [
        {
          "route": "/healthz",
          "method": "GET",
          "expected_status": 200,
          "count": 50,
          "min_ms": ...,
          "median_ms": ...,
          "p95_ms": ...,
          "max_ms": ...,
          "status_observed": 200
        },
        ...
      ]
    }

Budget format (`.performance-budget.json`):
    {
      "model": "p95_below_budget",
      "iterations_recommended": 50,
      "smoke_iterations": 5,
      "routes": {
        "GET /healthz": { "p95_ms_budget": 50 },
        "GET /":        { "p95_ms_budget": 1500 },
        ...
      }
    }
"""
from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PERF_DIR = ROOT / "docs" / "performance"
DEFAULT_OUT = PERF_DIR / "PERFORMANCE_BASELINE_V1.json"
BUDGET_PATH = ROOT / ".performance-budget.json"


# Routes measured. `auth_required=True` means an unauthenticated GET is
# expected to redirect (303/307) — we still measure the redirect itself.
# `auth_with_fixture=True` means we log in once via the test user the
# conftest pattern creates, then hit the route inside the session cookie.
_ROUTES: list[dict] = [
    {"method": "GET", "path": "/healthz", "expected": 200, "auth": False},
    {"method": "GET", "path": "/healthz/strict", "expected": 200, "auth": False},
    {"method": "GET", "path": "/welcome", "expected": 200, "auth": False},
    {"method": "GET", "path": "/login", "expected": 200, "auth": False},
    {"method": "GET", "path": "/register", "expected": 200, "auth": False},
    {"method": "GET", "path": "/forgot-password", "expected": 200, "auth": False},
    # Authenticated routes — once the test client is logged in:
    {"method": "GET", "path": "/", "expected": 200, "auth": True},
    {"method": "GET", "path": "/history", "expected": 200, "auth": True},
    {"method": "GET", "path": "/progress", "expected": 200, "auth": True},
    {"method": "GET", "path": "/dashboard", "expected": 200, "auth": True},
]


def _git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _build_client():
    """Create an isolated TestClient against a temp SQLite, with the test
    user logged in. Mirrors `tests/conftest.py::client` but stand-alone."""
    import os

    tmp_dir = tempfile.mkdtemp(prefix="perf-baseline-")
    db_path = Path(tmp_dir) / "perf.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    os.environ["APP_ENV"] = "test"
    os.environ["APP_SECRET_KEY"] = "perf-baseline-secret"  # noqa: S105
    # Make sure the rate limiter doesn't fight the 50-iteration loop.
    os.environ["RATE_LIMIT_ENABLED"] = "0"

    for mod_name in tuple(m for m in sys.modules if m == "app" or m.startswith("app.")):
        sys.modules.pop(mod_name, None)

    from fastapi.testclient import TestClient

    from app import main as main_mod
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.auth import hash_password

    client = TestClient(main_mod.app)
    client.__enter__()
    with SessionLocal() as db:
        db.add(User(username="perfuser", password_hash=hash_password("perfpass")))
        db.commit()
    r = client.post(
        "/login",
        data={"username": "perfuser", "password": "perfpass"},  # noqa: S106
        follow_redirects=False,
    )
    assert r.status_code == 303, f"perf baseline login failed: {r.status_code}"
    return client


def _measure_route(client, route: dict, iterations: int) -> dict:
    samples_ms: list[float] = []
    statuses: list[int] = []
    method = route["method"]
    path = route["path"]
    for _ in range(iterations):
        t0 = time.perf_counter()
        if method == "GET":
            r = client.get(path, follow_redirects=False)
        else:
            r = client.request(method, path, follow_redirects=False)
        samples_ms.append((time.perf_counter() - t0) * 1000.0)
        statuses.append(r.status_code)

    samples_sorted = sorted(samples_ms)
    p95_index = max(0, int(len(samples_sorted) * 0.95) - 1)
    return {
        "route": path,
        "method": method,
        "expected_status": route["expected"],
        "status_observed": max(set(statuses), key=statuses.count),
        "count": len(samples_ms),
        "min_ms": round(min(samples_ms), 3),
        "median_ms": round(statistics.median(samples_ms), 3),
        "p95_ms": round(samples_sorted[p95_index], 3),
        "max_ms": round(max(samples_ms), 3),
    }


def percentile(samples: list[float], p: float) -> float:
    """Exposed for tests — same semantics as the inline computation."""
    if not samples:
        return 0.0
    s = sorted(samples)
    idx = max(0, int(len(s) * p) - 1) if p < 1.0 else len(s) - 1
    return s[idx]


def _load_budget() -> dict | None:
    if not BUDGET_PATH.exists():
        return None
    return json.loads(BUDGET_PATH.read_text(encoding="utf-8"))


def _check_budget(report: dict, budget: dict) -> tuple[bool, list[str]]:
    routes_budget = budget.get("routes", {})
    violations: list[str] = []
    for r in report["routes"]:
        key = f"{r['method']} {r['route']}"
        b = routes_budget.get(key)
        if not b:
            continue
        budget_p95 = b.get("p95_ms_budget")
        if budget_p95 is None:
            continue
        if r["p95_ms"] > budget_p95:
            violations.append(
                f"  {key}: p95={r['p95_ms']}ms > budget={budget_p95}ms"
            )
    return (len(violations) == 0), violations


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true", help="N=5 instead of 50")
    parser.add_argument("--iterations", type=int, default=None)
    parser.add_argument("--check-budget", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--environment", default="dev")
    args = parser.parse_args()

    budget = _load_budget()
    if args.iterations is not None:
        iterations = args.iterations
    elif args.smoke:
        iterations = (budget or {}).get("smoke_iterations", 5)
    else:
        iterations = (budget or {}).get("iterations_recommended", 50)

    print(f"=== perf baseline (iterations={iterations}) ===")
    client = _build_client()
    try:
        per_route = [_measure_route(client, r, iterations) for r in _ROUTES]
    finally:
        client.__exit__(None, None, None)

    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "git_sha": _git_sha(),
        "environment": args.environment,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "iterations": iterations,
        "routes": per_route,
    }

    print()
    print(f"{'route':<28} {'method':<6} {'count':>6} {'med':>8} {'p95':>8} {'max':>8}")
    for r in per_route:
        print(
            f"{r['route']:<28} {r['method']:<6} {r['count']:>6} "
            f"{r['median_ms']:>8.2f} {r['p95_ms']:>8.2f} {r['max_ms']:>8.2f}"
        )

    if not args.no_write:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        try:
            display = args.out.relative_to(ROOT)
        except ValueError:
            display = args.out
        print(f"\n[perf] wrote {display}")

    if args.check_budget:
        if budget is None:
            print("[perf] WARN: no .performance-budget.json — skipping budget check")
            return 0
        ok, violations = _check_budget(report, budget)
        if not ok:
            print()
            print(f"FAIL: {len(violations)} route(s) exceed p95 budget:")
            for v in violations:
                print(v)
            return 1
        print("\n[perf] OK: all routes within p95 budget.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
