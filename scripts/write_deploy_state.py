#!/usr/bin/env python3
"""Sb_26.3 — write var/deploy_state.json after a successful deploy.

Called at the very end of `scripts/deploy_prod.sh` once health checks
pass, with the SHA that's now live in prod. The JSON is read by
/healthz/strict and by scripts/prod_state_report.py.

Schema (stable):
  {
    "sha": "<full git sha>",
    "deployed_at": "<ISO-8601 UTC>",
    "service": "<systemd unit name>",
    "app_dir": "<app dir absolute path>",
    "health_at_deploy": "<200 | 503 | unknown>"
  }

Never contains secrets, hostnames, users, or any PII. Safe to commit
to a public log channel.

Usage:
    python3 scripts/write_deploy_state.py \
        --sha "$POST_SHA" \
        --service "workout" \
        --app-dir "/opt/workout-session-tracking" \
        --health "200" \
        --out var/deploy_state.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sha", required=True)
    parser.add_argument("--service", default="workout")
    parser.add_argument("--app-dir", default=str(ROOT))
    parser.add_argument(
        "--health",
        default="unknown",
        choices=["200", "503", "unknown"],
        help="HTTP status of /healthz/strict at deploy verification",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "var" / "deploy_state.json",
    )
    args = parser.parse_args()

    payload = {
        "sha": args.sha,
        "deployed_at": datetime.now(UTC).isoformat(),
        "service": args.service,
        "app_dir": args.app_dir,
        "health_at_deploy": args.health,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"[deploy_state] wrote {args.out} sha={args.sha[:12]} health={args.health}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
