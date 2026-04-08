"""Idempotent seed for the reference training split.

Reads `data/reference_split.json`, upserts the `ReferenceDoc` row keyed by
`version`, and rebuilds the catalog if (and only if) the version changes.
Safe to call on every boot.
"""
from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.config import BASE_DIR
from app.models.catalog import Exercise, ReferenceDoc, RepRange, SplitDay

REFERENCE_PATH = BASE_DIR / "data" / "reference_split.json"


def load_reference_payload(path: Path = REFERENCE_PATH) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def seed_reference_split(db: Session, payload: dict | None = None) -> bool:
    """Seed the catalog from the reference JSON.

    Returns True if a (re)seed happened, False if it was a no-op.
    """
    payload = payload or load_reference_payload()
    version = payload["version"]
    title = payload["title"]

    existing = db.execute(
        select(ReferenceDoc).where(ReferenceDoc.version == version)
    ).scalar_one_or_none()
    if existing is not None:
        return False

    # New version: wipe the prescribed catalog and rebuild. We deliberately do
    # NOT touch workout_sessions / set_logs: those reference exercises by id,
    # so keep in mind that any catalog rebuild after Sprint 1 will need a
    # remap strategy (tracked in Risks / Next Sprint).
    db.execute(delete(RepRange))
    db.execute(delete(Exercise))
    db.execute(delete(SplitDay))

    for day in payload["split_days"]:
        split_day = SplitDay(
            weekday=day["weekday"],
            name=day["name"],
            kind=day["kind"],
            focus=day.get("focus", ""),
            cardio_note=day.get("cardio_note"),
        )
        for ex in day.get("exercises", []):
            exercise = Exercise(
                position=ex["position"],
                code=ex["code"],
                name=ex["name"],
                set_scheme=ex["set_scheme"],
                notes=ex.get("notes"),
            )
            for idx, rr in enumerate(ex.get("rep_ranges", []), start=1):
                exercise.rep_ranges.append(
                    RepRange(
                        set_index=idx,
                        min_reps=rr["min_reps"],
                        max_reps=rr["max_reps"],
                        technique=rr.get("technique"),
                    )
                )
            split_day.exercises.append(exercise)
        db.add(split_day)

    db.add(ReferenceDoc(version=version, title=title))
    db.commit()
    return True
