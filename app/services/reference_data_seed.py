"""Sb_32.4 — application-level reference-data seed.

## Why this exists (proven at preflight, not assumed)

``app.database.init_db`` calls ``Base.metadata.create_all``, and
``app/models/__init__.py`` imports ``body_zone``, ``muscle`` and
``exercise_muscle_mapping``. So **any app boot creates the reference tables
empty**, and the Alembic backfills — which are guarded on "did I just CREATE
this table?" — can then never fill them.

Measured on this repo:

* alembic-only database → ``body_zones=11``, ``exercise_muscle_mappings=87``;
* ``create_all()`` first → ``0`` / ``0``, and a subsequent ``alembic upgrade``
  does not even reach head (it aborts on an earlier revision re-creating a
  table that ``create_all`` already made);
* under the real ``client`` fixture, i.e. a genuine app boot, the counts are
  ``0 / 0 / 0``.

That last one is the decisive fact: without this seed, migrating a consumer to
the formal mapping would migrate it to an **empty table**, so it would fall
back to substring matching in 100 % of the test suite and on every environment
where the app creates its own schema. The migration would be inert and
unprovable. Production is only correct today by accident of ordering
(``deploy_prod.sh`` runs alembic before the app starts).

## Contract (the guardrails this seed is authorised under)

* **deterministic** — same inputs, same rows, no clock, no randomness;
* **idempotent** — safe to run on every boot and every deploy;
* **reference-data only** — writes ``body_zones`` and
  ``exercise_muscle_mappings``, nothing else, ever;
* **derived from canonical repository taxonomy** — zone rows come from the
  ``muscle_mapping`` dicts (exactly what the Alembic backfill derives them
  from), exercise rows from the canonical classifier over the canonical
  referential. No value is invented to fill coverage: an exercise the
  classifier cannot place is **left uncovered**;
* **never destructive** — it INSERTs missing rows and reconciles the reviewed
  correction list. It never deletes, never truncates, and never writes outside
  those two tables. It cannot touch users, sessions, set logs or custom
  programs — there is no code path from here to them.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

from app.services.body_zone_source import KNOWN_MAPPING_CORRECTIONS
from app.services.muscle_mapping import (
    RADAR_AXES,
    ZONE_LABELS,
    ZONE_MEASUREMENT,
    ZONE_VOLUME_TARGET,
    _classify_exercise_by_patterns,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

_DATA_DIR = Path(__file__).resolve().parents[2] / "data"
_EKB_PATH = _DATA_DIR / "exercise_knowledge_base.json"
_PROPERTIES_PATH = _DATA_DIR / "exercise_properties.json"

# Provenance recorded on each row. `baseline` mirrors what the Alembic backfill
# used; `manual` marks the reviewed corrections so a curator can tell them
# apart in the table itself.
SOURCE_BASELINE = "baseline"
SOURCE_MANUAL = "manual"


def _zone_to_radar_axis(zone: str) -> str | None:
    for axis, spec in RADAR_AXES.items():
        if zone in spec["zones"]:
            return axis
    return None


def zone_rows() -> list[dict]:
    """The 11 canonical body zones, derived from ``muscle_mapping``.

    Same derivation the Alembic backfill performs, so the two agree by
    construction rather than by a copied literal. ``core`` legitimately has no
    radar axis and gets ``None``.
    """
    return [
        {
            "code": code,
            "label": label,
            "measurement_field": ZONE_MEASUREMENT.get(code),
            "radar_axis": _zone_to_radar_axis(code),
            "volume_target": ZONE_VOLUME_TARGET.get(code),
            "is_active": True,
        }
        for code, label in ZONE_LABELS.items()
    ]


@lru_cache(maxsize=1)
def canonical_exercise_referential() -> tuple[str, ...]:
    """Every exercise name the app can be asked to classify.

    Union of the two canonical data files. Sorted, so the seed is deterministic
    and the parity report reads the same on every machine.
    """
    names: set[str] = set()
    for path in (_EKB_PATH, _PROPERTIES_PATH):
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        entries = payload.get("exercises", payload)
        if isinstance(entries, dict):
            names.update(k for k in entries if not k.startswith("_"))
        elif isinstance(entries, list):
            names.update(e["name"] for e in entries if isinstance(e, dict) and "name" in e)
    return tuple(sorted(names))


def mapping_rows() -> list[dict]:
    """Rows for the exercise→zone table, derived, never invented.

    Values come from the canonical substring classifier — the same source the
    Alembic backfill list was originally produced from — then the reviewed
    corrections are applied on top. An exercise the classifier returns
    ``unknown`` for is **skipped**: filling it in would be inventing a mapping
    to raise a coverage number, which Sb_32.4 forbids.
    """
    corrections = {c.exercise_name: c for c in KNOWN_MAPPING_CORRECTIONS}
    rows: list[dict] = []
    for name in canonical_exercise_referential():
        correction = corrections.get(name)
        if correction is not None:
            primary, secondary = correction.primary, list(correction.secondary)
            source = SOURCE_MANUAL
        else:
            primary, secondary = _classify_exercise_by_patterns(name)
            source = SOURCE_BASELINE
        if primary == "unknown":
            continue
        rows.append({
            "exercise_code": name, "body_zone_code": primary,
            "role": "primary", "source": source, "position": 0,
        })
        rows.extend(
            {
                "exercise_code": name, "body_zone_code": zone,
                "role": "secondary", "source": source, "position": i,
            }
            for i, zone in enumerate(secondary, start=1)
        )
    return rows


def seed_reference_data(db: Session) -> dict[str, int]:
    """Populate the reference tables. Idempotent; returns what it changed.

    Insert-only for zones and mappings, plus a narrow reconciliation limited to
    the reviewed correction list — because a database already populated by the
    Alembic backfill carries the two known-wrong rows, and insert-only would
    leave them in place forever.

    The reconciliation is deliberately NOT a general "make the table match the
    derivation" pass: that would silently wipe any future hand-curated row. It
    only ever rewrites the exercises named in ``KNOWN_MAPPING_CORRECTIONS``.
    """
    from app.models.body_zone import BodyZone
    from app.models.exercise_muscle_mapping import ExerciseMuscleMapping

    stats = {"zones_inserted": 0, "mappings_inserted": 0, "corrections_applied": 0}

    existing_zones = {z for (z,) in db.query(BodyZone.code).all()}
    for row in zone_rows():
        if row["code"] in existing_zones:
            continue
        db.add(BodyZone(**row))
        stats["zones_inserted"] += 1

    existing_keys = {
        (code, zone, role)
        for code, zone, role in db.query(
            ExerciseMuscleMapping.exercise_code,
            ExerciseMuscleMapping.body_zone_code,
            ExerciseMuscleMapping.role,
        ).all()
    }
    for row in mapping_rows():
        key = (row["exercise_code"], row["body_zone_code"], row["role"])
        if key in existing_keys:
            continue
        db.add(ExerciseMuscleMapping(**row, is_active=True))
        existing_keys.add(key)
        stats["mappings_inserted"] += 1

    # `SessionLocal` is built with autoflush=False, so the rows queued above are
    # invisible to a query until they are flushed. Without this the
    # reconciliation below would see no rows for a corrected exercise, re-add
    # one, and hit the (exercise_code, body_zone_code, role) unique constraint.
    db.flush()

    stats["corrections_applied"] = _reconcile_corrections(db)
    db.commit()
    return stats


def _reconcile_corrections(db: Session) -> int:
    """Make the reviewed corrections true in the table, and nothing else.

    Scoped by ``exercise_code.in_(<the reviewed names>)``: a row for any other
    exercise cannot be reached from here. Deactivates rather than deletes, so
    the historical attribution stays auditable in the table.
    """
    from app.models.exercise_muscle_mapping import ExerciseMuscleMapping

    applied = 0
    for correction in KNOWN_MAPPING_CORRECTIONS:
        wanted = {(correction.primary, "primary")}
        wanted |= {(z, "secondary") for z in correction.secondary}

        rows = (
            db.query(ExerciseMuscleMapping)
            .filter(ExerciseMuscleMapping.exercise_code == correction.exercise_name)
            .all()
        )
        for row in rows:
            should_be_active = (row.body_zone_code, row.role) in wanted
            if row.is_active != should_be_active:
                row.is_active = should_be_active
                row.source = SOURCE_MANUAL
                applied += 1

        present = {(r.body_zone_code, r.role) for r in rows}
        for i, (zone, role) in enumerate(sorted(wanted)):
            if (zone, role) in present:
                continue
            db.add(ExerciseMuscleMapping(
                exercise_code=correction.exercise_name, body_zone_code=zone,
                role=role, source=SOURCE_MANUAL, position=i, is_active=True,
            ))
            applied += 1
    return applied
