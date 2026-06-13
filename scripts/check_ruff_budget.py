#!/usr/bin/env python3
"""Sb_26.1 — ruff budget check.

Exécute `ruff check .` et compare le total contre la baseline figée dans
`.ruff-budget.json`. Échoue (exit 1) si :
* total > baseline_warnings, ou
* (mode strict, à activer en Sb_26.next) un fichier touché dans le PR
  voit son count augmenter — pas couvert dans cette V1, mais la place
  est laissée pour extension.

Usage :
    python scripts/check_ruff_budget.py            # check baseline
    python scripts/check_ruff_budget.py --measure  # affiche le total actuel sans gate

Contrats (Sx_26 §19bis + HC-RUFF-*) :
* `.ruff-budget.json` est la source de vérité unique pour la baseline.
* Le script ne modifie JAMAIS la baseline — seule une PR explicite peut
  le faire avec justification dans le commit message.
* Une diminution naturelle (cleanup en passant) ne fait pas échouer la
  CI mais doit pousser à mettre à jour la baseline dans une PR dédiée.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUDGET_FILE = ROOT / ".ruff-budget.json"


def _run_ruff() -> tuple[int, dict[str, int]]:
    """Run `ruff check . --output-format=json` and return (total, by_rule)."""
    result = subprocess.run(
        ["ruff", "check", ".", "--output-format=json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    # Ruff exits non-zero when there are warnings — that's expected.
    # Only treat it as a tool error if stderr is non-empty AND stdout is empty.
    if not result.stdout and result.stderr:
        print(f"FATAL: ruff failed to run.\n{result.stderr}", file=sys.stderr)
        sys.exit(2)
    try:
        items = json.loads(result.stdout or "[]")
    except json.JSONDecodeError as e:
        print(f"FATAL: ruff did not return valid JSON: {e}", file=sys.stderr)
        sys.exit(2)
    by_rule: dict[str, int] = {}
    for item in items:
        code = item.get("code", "?")
        by_rule[code] = by_rule.get(code, 0) + 1
    return len(items), by_rule


def _load_budget() -> dict:
    if not BUDGET_FILE.exists():
        print(
            f"FATAL: {BUDGET_FILE} missing. Cannot enforce ruff budget.",
            file=sys.stderr,
        )
        sys.exit(2)
    return json.loads(BUDGET_FILE.read_text(encoding="utf-8"))


def _print_top_rules(by_rule: dict[str, int], n: int = 10) -> None:
    sorted_rules = sorted(by_rule.items(), key=lambda kv: -kv[1])
    for code, count in sorted_rules[:n]:
        print(f"    {code}: {count}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--measure",
        action="store_true",
        help="Just print the current count without enforcing the budget.",
    )
    args = parser.parse_args()

    total, by_rule = _run_ruff()
    budget = _load_budget()
    baseline = int(budget["baseline_warnings"])

    print("=== ruff budget check ===")
    print(f"  current : {total} warnings")
    print(f"  baseline: {baseline} warnings (frozen {budget.get('baseline_date')})")
    print(f"  delta   : {total - baseline:+d}")
    print("  top rules:")
    _print_top_rules(by_rule)

    if args.measure:
        return 0

    if total > baseline:
        print()
        print(
            f"FAIL: total ruff warnings ({total}) exceeds baseline ({baseline}). "
            f"Cleanup the {total - baseline} extra warning(s) or bump the "
            f"baseline EXPLICITLY in .ruff-budget.json (with justification "
            f"in the commit message)."
        )
        return 1

    if total < baseline:
        print()
        print(
            f"WARN: total ruff warnings ({total}) is BELOW baseline ({baseline}). "
            f"Update .ruff-budget.json to lock the improvement (ratchet down). "
            f"This is not a failure — just a reminder to keep the baseline tight."
        )

    print()
    print(f"OK: ruff budget respected ({total} ≤ {baseline}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
