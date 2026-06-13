#!/usr/bin/env python3
"""Sb_26.3 — strictly opt-in Discord webhook alerter.

Reads `DISCORD_WEBHOOK_URL` from env. If unset/empty, exits 0 as a
no-op WITHOUT making any network call — that's the disabled-by-default
contract.

Usage:
    DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/.../... \\
        python3 scripts/alert_discord.py --severity warning \\
        --title "Deploy failed" --message "scripts/deploy_prod.sh exited 1"

    # No env var → no-op, exit 0:
    python3 scripts/alert_discord.py --title hi --message bye

    # Dry-run (validate payload + format without POST):
    python3 scripts/alert_discord.py --dry-run --title hi --message bye

Design notes:
* No secret in the source or CLI args — webhook URL must come from env.
* Uses urllib from stdlib (no `requests` dependency added).
* Hard cap on message length so a runaway alert doesn't blow Discord's
  per-message ceiling.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from urllib import error as urlerror
from urllib import request as urlrequest

SEVERITY_COLORS = {
    "info": 0x3498DB,     # blue
    "warning": 0xF1C40F,  # yellow
    "error": 0xE74C3C,    # red
    "ok": 0x2ECC71,       # green
}
MAX_MESSAGE = 1800


def _build_payload(severity: str, title: str, message: str) -> dict:
    truncated = message if len(message) <= MAX_MESSAGE else message[:MAX_MESSAGE] + "…"
    color = SEVERITY_COLORS.get(severity, SEVERITY_COLORS["info"])
    return {
        "embeds": [
            {
                "title": f"[{severity.upper()}] {title}"[:256],
                "description": truncated,
                "color": color,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        ]
    }


def _post(url: str, payload: dict, *, timeout: int = 10) -> int:
    data = json.dumps(payload).encode("utf-8")
    # noqa S310: webhook URL is strictly opt-in via env (DISCORD_WEBHOOK_URL),
    # in practice always https, and Discord controls the surface.
    req = urlrequest.Request(  # noqa: S310
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlrequest.urlopen(req, timeout=timeout) as resp:  # noqa: S310 — see above
            return resp.status
    except urlerror.HTTPError as exc:
        return exc.code


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--severity", default="info", choices=list(SEVERITY_COLORS))
    parser.add_argument("--title", required=True)
    parser.add_argument("--message", required=True)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print payload and exit 0 without POSTing.",
    )
    args = parser.parse_args()

    webhook = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
    payload = _build_payload(args.severity, args.title, args.message)

    if args.dry_run:
        print(json.dumps(payload, indent=2))
        print("[alert_discord] dry-run — no POST issued")
        return 0

    if not webhook:
        print("[alert_discord] DISCORD_WEBHOOK_URL unset — alerter disabled, no-op")
        return 0

    status = _post(webhook, payload)
    print(f"[alert_discord] POST → status={status}")
    return 0 if 200 <= status < 300 else 1


if __name__ == "__main__":
    sys.exit(main())
