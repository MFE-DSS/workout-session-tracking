"""CLI to force a (re)seed of the reference catalog.

Usage:
  python -m scripts.seed_db
"""
from __future__ import annotations

from app.database import SessionLocal, init_db
from app.services.seed import seed_reference_split
from app.services.seed_exercise_identity import seed_exercise_identity


def main() -> int:
    init_db()
    with SessionLocal() as db:
        changed = seed_reference_split(db)
        # Sb_EXERCISE_IDENTITY_01 — indépendant du versionnement de
        # `reference_split` : l'identité doit se rattraper même quand le
        # catalogue est « unchanged », sinon une base existante ne l'aurait
        # jamais.
        identity = seed_exercise_identity(db)
        db.commit()
    print("Reference catalog:", "seeded" if changed else "unchanged")
    print(
        f"Exercise identity: {identity.total} exercices "
        f"(+{identity.created_catalog} catalogue, +{identity.created_ekb} EKB), "
        f"{identity.aliases_declared} alias déclarés"
    )
    for conflict in identity.alias_conflicts:
        print(f"  ⚠ alias non appliqué : {conflict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
