#!/usr/bin/env python3
"""Sb_32.4 — legacy vs formal body-zone parity, over the whole referential.

Prints the coverage/parity table and exits non-zero when the acceptance
criteria are not met:

* an **unexplained divergence** — the legacy classifier and the formal contract
  disagree and the reviewed correction list does not account for it. Sb_32.4
  treats that as a HARD STOP, not a diff to accept;
* an **ambiguous mapping** — an exercise carrying more than one active
  ``primary`` row, so the lookup answer is stable but arbitrary.

Missing formal mappings are **reported, not failed**: an exercise the canonical
classifier cannot place is left uncovered on purpose. Inventing a zone to make
the number look complete is what this sprint forbids.

Usage:
    python scripts/bodyzone_parity_qa.py            # in-memory, seeded
    python scripts/bodyzone_parity_qa.py --verbose  # list every name

The equivalent assertions run in tests/test_bodyzone_consumer_migration.py, so
CI covers this contract without a workflow change; this script exists for
operator use against a real database.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

EXIT_OK = 0
EXIT_UNEXPLAINED = 1
EXIT_AMBIGUOUS = 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--database-url",
        default=os.environ.get("DATABASE_URL", "sqlite:///:memory:"),
        help="database to audit (default: a throwaway in-memory one, seeded here)",
    )
    parser.add_argument("--verbose", action="store_true",
                        help="list the names behind each count")
    args = parser.parse_args()

    os.environ["DATABASE_URL"] = args.database_url

    import app.models  # noqa: F401  — register the tables
    from app.database import Base, engine
    from app.services.body_zone_source import build_parity_report
    from app.services.reference_data_seed import (
        canonical_exercise_referential,
        seed_reference_data,
    )

    Base.metadata.create_all(bind=engine)

    from app.database import SessionLocal

    names = list(canonical_exercise_referential())
    with SessionLocal() as db:
        seed_reference_data(db)
        report = build_parity_report(db, names)

    print("=== Sb_32.4 body-zone parity ===")
    print(f"  database: {args.database_url}")
    for line in report.as_lines():
        print(f"  {line}")

    if report.missing_formal_mapping:
        print("\n  missing formal mapping (reported, not a failure):")
        for name in report.missing_formal_mapping:
            print(f"    · {name}")

    if args.verbose and report.intentional_divergences:
        print("\n  intentional divergences (reviewed, evidence in body_zone_source):")
        for name in report.intentional_divergences:
            print(f"    · {name}")

    if report.unexplained_divergences:
        print("\n  FAIL — unexplained divergences (HARD STOP):")
        for name in report.unexplained_divergences:
            print(f"    · {name}")
        return EXIT_UNEXPLAINED

    if report.ambiguous_mappings:
        print("\n  FAIL — ambiguous mappings (>1 active primary row):")
        for name in report.ambiguous_mappings:
            print(f"    · {name}")
        return EXIT_AMBIGUOUS

    print("\nOK: zero unexplained divergence, zero ambiguous mapping.")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
