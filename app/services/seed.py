"""Idempotent seed of the workout template library.

Reads `data/reference_split.json`, upserts `ReferenceDoc` by
`version`, and rebuilds the template catalog ONLY when the
version changes. Safe to call on every boot.

Rebuilds are safe for history: `session_exercises` snapshot the
`exercise_code_snapshot` / `exercise_name_snapshot` fields at log
time, and the FKs to the catalog are `ON DELETE SET NULL`.

Wipe-guard (Sb_CUSTOM_PROGRAM_LAUNCH_01, Sx_CUSTOM_PROGRAM_05 §4):
`catalog_section == "user"` is the reserved namespace of user-created
custom templates. The reseed only ever deletes SYSTEM rows — a version
bump must never destroy a custom template or its children.
"""
from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.config import BASE_DIR
from app.models.catalog import (
    MethodRule,
    ReferenceDoc,
    RepTarget,
    TemplateExercise,
    WorkoutTemplate,
)

REFERENCE_PATH = BASE_DIR / "data" / "reference_split.json"
METHOD_RULES_PATH = BASE_DIR / "data" / "method_rules.json"

# Reserved catalog_section of user-created custom templates. Rows in this
# namespace are NEVER touched by the system reseed, and the system seed
# payload is NEVER allowed to claim it.
CUSTOM_CATALOG_SECTION = "user"


def load_reference_payload(path: Path = REFERENCE_PATH) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def load_method_rules_payload(path: Path = METHOD_RULES_PATH) -> dict:
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

    # Input guard: the system payload must never claim the custom namespace.
    if any(
        tpl.get("catalog_section") == CUSTOM_CATALOG_SECTION
        for tpl in payload["templates"]
    ):
        raise ValueError(
            f"catalog_section '{CUSTOM_CATALOG_SECTION}' is reserved for "
            "user-created templates and must never appear in the system seed"
        )

    # Wipe-guard: only SYSTEM rows are deleted; custom templates and their
    # children survive every reseed. Children are resolved by join before
    # their parents are removed.
    system_template_ids = select(WorkoutTemplate.id).where(
        WorkoutTemplate.catalog_section != CUSTOM_CATALOG_SECTION
    )
    system_exercise_ids = select(TemplateExercise.id).where(
        TemplateExercise.template_id.in_(system_template_ids)
    )
    db.execute(
        delete(RepTarget).where(
            RepTarget.template_exercise_id.in_(system_exercise_ids)
        )
    )
    db.execute(
        delete(TemplateExercise).where(TemplateExercise.id.in_(system_exercise_ids))
    )
    db.execute(
        delete(WorkoutTemplate).where(WorkoutTemplate.id.in_(system_template_ids))
    )

    for tpl in payload["templates"]:
        template = WorkoutTemplate(
            slug=tpl["slug"],
            name=tpl["name"],
            kind=tpl["kind"],
            focus=tpl.get("focus", ""),
            cardio_note=tpl.get("cardio_note"),
            suggested_label=tpl.get("suggested_label"),
            catalog_section=tpl.get("catalog_section", "core"),
            display_order=tpl.get("display_order", 0),
        )
        for ex in tpl.get("exercises", []):
            exercise = TemplateExercise(
                position=ex["position"],
                code=ex["code"],
                name=ex["name"],
                set_scheme=ex["set_scheme"],
                notes=ex.get("notes"),
                substitutes_json=json.dumps(ex["substitutes"]) if ex.get("substitutes") else None,
                machine_slug=ex.get("machine_slug"),
                machine_family=ex.get("machine_family"),
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


def seed_method_rules(db: Session, payload: dict | None = None) -> int:
    """Seed / re-seed the method_rules table.

    Method rules are small static cards (8 in V1), cheap to rewrite on
    every boot. We simply wipe and reinsert — no version tracking needed,
    the table has no inbound FKs.

    Returns the number of rules inserted.
    """
    payload = payload or load_method_rules_payload()
    db.execute(delete(MethodRule))
    count = 0
    for rule in payload["rules"]:
        db.add(
            MethodRule(
                slug=rule["slug"],
                position=rule["position"],
                title=rule["title"],
                body=rule["body"],
            )
        )
        count += 1
    db.commit()
    return count
