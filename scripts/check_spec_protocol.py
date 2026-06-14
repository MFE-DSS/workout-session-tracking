#!/usr/bin/env python3
"""Sb_26.5 — Robust check for the spec-driven engineering protocol.

Verifies ONLY things that can be detected without NLP:

* every new `docs/SPRINT_Sb_*_REPORT.md` (i.e. NOT in the grandfathered
  allowlist) contains at least one verdict marker;
* every new `docs/strategy/Sx_*` spec contains at least one non-goals
  marker (or "Périmètre interdit");
* the 6 required templates exist in `docs/templates/`;
* `docs/strategy/SPEC_REGISTRY.md` exists.

Policy + allowlist live in `.spec-protocol-allowlist.json`.

Exit 0 = clean, 1 = violations, 2 = config error.

Usage:
    python scripts/check_spec_protocol.py
    python scripts/check_spec_protocol.py --strict   # error on missing markers in any file
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POLICY_PATH = ROOT / ".spec-protocol-allowlist.json"
DOCS = ROOT / "docs"
STRATEGY = DOCS / "strategy"
TEMPLATES = DOCS / "templates"


def _load_policy() -> dict:
    if not POLICY_PATH.exists():
        print(f"FATAL: {POLICY_PATH} missing.", file=sys.stderr)
        sys.exit(2)
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def _file_contains_any(path: Path, markers: list[str]) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return False
    return any(m in text for m in markers)


def _check_reports(policy: dict, strict: bool) -> list[str]:
    """Each new sprint report must contain at least one verdict marker."""
    grandfathered = set(policy.get("grandfathered_reports", []))
    markers = policy["verdict_markers"]
    failures: list[str] = []
    for path in sorted(DOCS.glob("SPRINT_Sb_*_REPORT.md")):
        if not strict and path.name in grandfathered:
            continue
        if not _file_contains_any(path, markers):
            failures.append(
                f"  REPORT  {path.relative_to(ROOT)}: no verdict marker found "
                f"(expected one of {markers!r})"
            )
    return failures


def _check_specs(policy: dict, strict: bool) -> list[str]:
    """Each new Sx_* spec must contain at least one non-goals marker."""
    grandfathered = set(policy.get("grandfathered_specs", []))
    markers = policy["non_goals_markers"]
    failures: list[str] = []
    for path in sorted(STRATEGY.glob("Sx_*.md")):
        if not strict and path.name in grandfathered:
            continue
        if not _file_contains_any(path, markers):
            failures.append(
                f"  SPEC    {path.relative_to(ROOT)}: no non-goals marker found "
                f"(expected one of {markers!r})"
            )
    return failures


def _check_templates(policy: dict) -> list[str]:
    required = policy.get("required_templates", [])
    failures: list[str] = []
    for name in required:
        if not (TEMPLATES / name).exists():
            failures.append(f"  TPL     missing template: {TEMPLATES / name}")
    return failures


def _check_registry() -> list[str]:
    registry = STRATEGY / "SPEC_REGISTRY.md"
    if not registry.exists():
        return [f"  REG     missing registry: {registry}"]
    return []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Also flag grandfathered historical files (pre-Sb_26.5).",
    )
    args = parser.parse_args()

    policy = _load_policy()

    print("=== spec protocol check ===")
    print(f"  policy_version : {policy.get('policy_version', '?')}")
    print(f"  strict mode    : {args.strict}")
    print(f"  grandfathered  : "
          f"{len(policy.get('grandfathered_reports', []))} reports, "
          f"{len(policy.get('grandfathered_specs', []))} specs")
    print()

    failures: list[str] = []
    failures += _check_reports(policy, args.strict)
    failures += _check_specs(policy, args.strict)
    failures += _check_templates(policy)
    failures += _check_registry()

    if not failures:
        print("OK: spec protocol checks pass.")
        return 0

    print(f"FOUND {len(failures)} violation(s):")
    for f in failures:
        print(f)
    print()
    print(
        "Action: every new sprint report needs a verdict section; every new "
        "Sx_* spec needs a non-goals section. See "
        "docs/strategy/SPEC_DRIVEN_ENGINEERING_PROTOCOL_v1.md."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
