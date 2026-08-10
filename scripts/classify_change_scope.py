#!/usr/bin/env python3
"""Deterministic change-scope classifier for path-aware CI gating (Sb_CI_02_1).

Answers ONE question: can this set of changed files possibly affect the application at
runtime, its tests, its data, or its infrastructure?

    NON_RUNTIME       — provably cannot. Only operator documentation / agent tooling.
    RUNTIME_OR_INFRA  — anything else. **This is the default.**

Design rules, in order of importance:

1. **Fail safe.** The allow-list is closed and tiny. Any path that is not explicitly proven
   inert — including an empty change set, a path we have never seen, or a malformed input —
   classifies as `RUNTIME_OR_INFRA`. A wrong `NON_RUNTIME` would silently skip the test suite;
   a wrong `RUNTIME_OR_INFRA` only costs CI minutes. The asymmetry is deliberate.
2. **No third-party path filter.** The rule lives here, in repo-owned code, versioned and unit
   tested, so a reviewer can read the whole policy in one screen and CI cannot drift from it.
3. **Widening is a decision, never an accident.** Adding a prefix to `NON_RUNTIME_PREFIXES`
   requires an explicit audit that the path cannot reach runtime, plus a pinned test.

Usage:
    python scripts/classify_change_scope.py --files docs/a.md .claude/skills/x/SKILL.md
    git diff --name-only BASE HEAD | python scripts/classify_change_scope.py
    ... --github-output   # additionally append `runtime=true|false` to $GITHUB_OUTPUT
"""
from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Iterable

NON_RUNTIME = "NON_RUNTIME"
RUNTIME_OR_INFRA = "RUNTIME_OR_INFRA"

# CLOSED allow-list. A changed file classifies as NON_RUNTIME only if it starts with one of
# these prefixes. Every entry must be justified: it is read by humans and agents, never
# imported, executed, deployed or served by the application.
#
#   docs/            — specs, sprint reports, roadmaps, registry, dogfood notes, templates.
#   .claude/skills/  — agent skill definitions (operator tooling; never imported by `app/`).
#
# NOT allow-listed on purpose: `.claude/settings.json` (can change agent permissions),
# anything else under `.claude/`, root-level markdown such as CLAUDE.md (repo execution
# contract), and every path not listed above.
NON_RUNTIME_PREFIXES: tuple[str, ...] = (
    "docs/",
    ".claude/skills/",
)


def _normalise(path: str) -> str:
    """Git emits forward slashes and may quote paths containing spaces/UTF-8.

    Note: strip only a literal leading `./`. `str.lstrip("./")` would eat the leading dot of
    a dotfile directory and turn `.claude/skills/x` into `claude/skills/x`."""
    cleaned = path.strip().strip('"').replace("\\", "/")
    while cleaned.startswith("./"):
        cleaned = cleaned[2:]
    return cleaned


def is_non_runtime_path(path: str) -> bool:
    """True only for a path proven inert. Everything else is runtime by default."""
    cleaned = _normalise(path)
    if not cleaned:
        return False
    return cleaned.startswith(NON_RUNTIME_PREFIXES)


def classify(paths: Iterable[str]) -> str:
    """Classify a change set. Empty or unknown ⇒ RUNTIME_OR_INFRA (fail safe)."""
    seen = [p for p in (_normalise(p) for p in paths) if p]
    if not seen:
        # No file list means we could not determine the diff — never skip on ignorance.
        return RUNTIME_OR_INFRA
    if all(is_non_runtime_path(p) for p in seen):
        return NON_RUNTIME
    return RUNTIME_OR_INFRA


def runtime_paths(paths: Iterable[str]) -> list[str]:
    """The paths that forced RUNTIME_OR_INFRA — printed so CI logs explain the verdict."""
    return [p for p in (_normalise(p) for p in paths) if p and not is_non_runtime_path(p)]


def _read_paths(args: argparse.Namespace) -> list[str]:
    if args.files:
        return list(args.files)
    if sys.stdin.isatty():
        return []
    return [line for line in sys.stdin.read().splitlines() if line.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--files", nargs="*", help="Changed paths (default: read stdin).")
    parser.add_argument(
        "--github-output",
        action="store_true",
        help="Append `scope=` and `runtime=true|false` to $GITHUB_OUTPUT.",
    )
    args = parser.parse_args(argv)

    paths = _read_paths(args)
    scope = classify(paths)
    is_runtime = scope == RUNTIME_OR_INFRA

    print(f"change-scope: {scope} ({len(paths)} changed file(s))")
    if not paths:
        print("  reason: empty/undetermined change set — defaulting to RUNTIME_OR_INFRA")
    elif is_runtime:
        forcing = runtime_paths(paths)
        print(f"  reason: {len(forcing)} runtime/infra path(s), e.g.:")
        for path in forcing[:10]:
            print(f"    - {path}")
        if len(forcing) > 10:
            print(f"    … and {len(forcing) - 10} more")
    else:
        print("  reason: every changed path is documentation or agent tooling")

    if args.github_output:
        target = os.environ.get("GITHUB_OUTPUT")
        if not target:
            print("ERROR: --github-output requires $GITHUB_OUTPUT", file=sys.stderr)
            return 2
        with open(target, "a", encoding="utf-8") as handle:
            handle.write(f"scope={scope}\n")
            handle.write(f"runtime={'true' if is_runtime else 'false'}\n")

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
