#!/usr/bin/env python3
"""Sb_26.7 — robust presence-check for auth scope docs.

Verifies, without any NLP, that the three artefacts the Sb_26.7 sprint
introduced still exist and carry the expected key markers:

* `docs/AUTH_SCOPE_MATRIX.md` exists
* `docs/MULTI_TENANT_READINESS.md` exists
* `docs/SPRINT_Sb_26_7_REPORT.md` exists and contains a verdict marker

Designed to be required-CI safe: zero text analysis, only string-in-file
checks. Exit 0 = clean, 1 = missing.

Usage:
    python scripts/check_auth_scope_matrix.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES: list[tuple[Path, list[str]]] = [
    (ROOT / "docs" / "AUTH_SCOPE_MATRIX.md", []),
    (ROOT / "docs" / "MULTI_TENANT_READINESS.md", []),
    (
        ROOT / "docs" / "SPRINT_Sb_26_7_REPORT.md",
        ["Verdict", "PRÊT"],
    ),
]


def main() -> int:
    failures: list[str] = []
    for path, markers in REQUIRED_FILES:
        if not path.exists():
            failures.append(f"missing: {path.relative_to(ROOT)}")
            continue
        if markers:
            text = path.read_text(encoding="utf-8")
            for m in markers:
                if m not in text:
                    failures.append(
                        f"{path.relative_to(ROOT)}: missing marker {m!r}"
                    )

    print("=== auth scope matrix check ===")
    print(f"  files checked : {len(REQUIRED_FILES)}")
    if not failures:
        print("OK: all auth scope artefacts present.")
        return 0

    print(f"FOUND {len(failures)} violation(s):")
    for f in failures:
        print(f"  {f}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
