"""CLI to force a (re)seed of the reference catalog.

Usage:
  python -m scripts.seed_db
"""
from __future__ import annotations

from app.database import SessionLocal, init_db
from app.services.seed import seed_reference_split


def main() -> int:
    init_db()
    with SessionLocal() as db:
        changed = seed_reference_split(db)
    print("Reference catalog:", "seeded" if changed else "unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
