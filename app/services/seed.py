"""Idempotent seed of the workout template library.

Reads `data/reference_split.json`, upserts `ReferenceDoc` by
`version`, and rebuilds the template catalog ONLY when the
version changes. Safe to call on every boot.

Rebuilds are safe for history: `session_exercises` snapshot the
`exercise_code_snapshot` / `exercise_name_snapshot` fields at log
time, and the FKs to the catalog are `ON DELETE SET NULL`.
"""
from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.config import BASE_DIR
from app.models.catalog import (
    ReferenceDoc,
    RepTarget,
    TemplateExercise,
    WorkoutTemplate,
)

REFERENCE_PATH = BASE_DIR / "data" / "reference_split.json"


def load_reference_payload(path: Path = REFERENCE_PATH) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def seed_reference_split(db: Session, payload: dict | None = None) -> bool:
    """Seed the template library from the reference JSON.

    Returns True if a (re)seed happened, False if the version was
    already present.
    """
    payload = payload or load_reference_payload()
    version = payload["version"]
    title = payload["title"]

    existing = db.execute(
        select(ReferenceDoc).where(ReferenceDoc.version == version)
    ).scalar_one_or_none()
    if existing is not None:
        return False

    db.execute(delete(RepTarget))
    db.execute(delete(TemplateExercise))
    db.execute(delete(WorkoutTemplate))

    for tpl in payload["templates"]:
        template = WorkoutTemplate(
            slug=tpl["slug"],
            name=tpl["name"],
            kind=tpl["kind"],
            focus=tpl.get("focus", ""),
            cardio_note=tpl.get("cardio_note"),
            suggested_label=tpl.get("suggested_label"),
        )
        for ex in tpl.get("exercises", []):
            exercise = TemplateExercise(
                position=ex["position"],
                code=ex["code"],
                name=ex["name"],
                set_scheme=ex["set_scheme"],
                notes=ex.get("notes"),
            )
            for idx, rt in enumerate(ex.get("rep_targets", []), start=1):
                exercise.rep_targets.append(
                    RepTarget(
                        set_index=idx,
                        min_reps=rt["min_reps"],
                        max_reps=rt["max_reps"],
                        technique=rt.get("technique"),
                    )
                )
            template.exercises.append(exercise)
        db.add(template)

    db.add(ReferenceDoc(version=version, title=title))
    db.commit()
    return True
