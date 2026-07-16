"""Sb_CUSTOM_PROGRAM_LAUNCH_01 — Seed Wipe-Guard.

`seed_reference_split` used to DELETE the whole catalog tree
(WorkoutTemplate → TemplateExercise → RepTarget) without any filter on
every version bump. Custom templates (`catalog_section == "user"`, the
reserved namespace of Sx_CUSTOM_PROGRAM_05 §4/§9) would have been
destroyed by the first system reseed.

These tests pin the guard:
- custom template + children SURVIVE a version bump reseed;
- system templates are still fully torn down and rebuilt;
- the idempotent no-op path is unchanged;
- the system payload can never claim the "user" namespace.

Constraint honoured: NO UserProgram* model is created anywhere here —
the custom row is a plain WorkoutTemplate in the reserved section, which
is exactly what the future materializer will produce (spec 05 §6).
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _payload(version: str, slugs: tuple[str, ...] = ("sys-a", "sys-b")) -> dict:
    """Minimal synthetic system payload (never uses the 'user' section)."""
    return {
        "version": version,
        "title": f"Test catalog {version}",
        "templates": [
            {
                "slug": slug,
                "name": slug.title(),
                "kind": "strength",
                "catalog_section": "core",
                "exercises": [
                    {
                        "position": 1,
                        "code": "E1",
                        "name": f"{slug} exercise",
                        "set_scheme": "3x 8-12",
                        "rep_targets": [{"min_reps": 8, "max_reps": 12}],
                    }
                ],
            }
            for slug in slugs
        ],
    }


def _insert_custom_template(db):
    """Insert a custom template tree the way the future materializer will:
    plain catalog rows in the reserved 'user' section."""
    from app.models.catalog import RepTarget, TemplateExercise, WorkoutTemplate

    tpl = WorkoutTemplate(
        slug="up1-mon-programme-v1-s1",
        name="Mon programme — Séance 1",
        kind="strength",
        catalog_section="user",
    )
    ex = TemplateExercise(
        position=1,
        code="E1",
        name="Développé couché haltères",
        set_scheme="3x 8-12",
    )
    ex.rep_targets.append(RepTarget(set_index=1, min_reps=8, max_reps=12))
    tpl.exercises.append(ex)
    db.add(tpl)
    db.commit()
    return tpl.id


def _reseed(db, version: str) -> bool:
    from app.services.seed import seed_reference_split

    return seed_reference_split(db, _payload(version))


# ───────── survie du custom au bump de version ─────────


def test_custom_template_survives_reseed(client):
    from app.database import SessionLocal
    from app.models.catalog import WorkoutTemplate

    with SessionLocal() as db:
        custom_id = _insert_custom_template(db)
        assert _reseed(db, "wipe-guard-test-v2") is True
        survived = db.get(WorkoutTemplate, custom_id)
        assert survived is not None
        assert survived.catalog_section == "user"
        assert survived.slug == "up1-mon-programme-v1-s1"


def test_custom_template_exercises_survive_reseed(client):
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.catalog import TemplateExercise

    with SessionLocal() as db:
        custom_id = _insert_custom_template(db)
        _reseed(db, "wipe-guard-test-v2")
        exercises = db.execute(
            select(TemplateExercise).where(TemplateExercise.template_id == custom_id)
        ).scalars().all()
        assert len(exercises) == 1
        assert exercises[0].name == "Développé couché haltères"


def test_custom_rep_targets_survive_reseed(client):
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.catalog import RepTarget, TemplateExercise

    with SessionLocal() as db:
        custom_id = _insert_custom_template(db)
        _reseed(db, "wipe-guard-test-v2")
        exercise = db.execute(
            select(TemplateExercise).where(TemplateExercise.template_id == custom_id)
        ).scalar_one()
        targets = db.execute(
            select(RepTarget).where(RepTarget.template_exercise_id == exercise.id)
        ).scalars().all()
        assert len(targets) == 1
        assert (targets[0].min_reps, targets[0].max_reps) == (8, 12)


def test_no_custom_template_deleted_by_reseed(client):
    """Several custom templates, several reseeds — the custom count never drops."""
    from sqlalchemy import func, select

    from app.database import SessionLocal
    from app.models.catalog import WorkoutTemplate

    with SessionLocal() as db:
        _insert_custom_template(db)
        second = WorkoutTemplate(
            slug="up2-autre-programme-v1-s1",
            name="Autre programme",
            kind="strength",
            catalog_section="user",
        )
        db.add(second)
        db.commit()

        for bump in ("wipe-guard-multi-v2", "wipe-guard-multi-v3"):
            _reseed(db, bump)
            n_custom = db.execute(
                select(func.count())
                .select_from(WorkoutTemplate)
                .where(WorkoutTemplate.catalog_section == "user")
            ).scalar_one()
            assert n_custom == 2


# ───────── le système reste intégralement reconstruit ─────────


def test_system_templates_rebuilt_on_version_bump(client):
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.catalog import WorkoutTemplate

    with SessionLocal() as db:
        _insert_custom_template(db)
        assert _reseed(db, "wipe-guard-test-v2") is True
        system_slugs = {
            t.slug
            for t in db.execute(
                select(WorkoutTemplate).where(
                    WorkoutTemplate.catalog_section != "user"
                )
            ).scalars()
        }
        # Old system catalog fully torn down, replaced by the new payload.
        assert system_slugs == {"sys-a", "sys-b"}


def test_system_children_fully_replaced(client):
    """No orphan system TemplateExercise/RepTarget survives the rebuild."""
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.catalog import TemplateExercise, WorkoutTemplate

    with SessionLocal() as db:
        custom_id = _insert_custom_template(db)
        _reseed(db, "wipe-guard-test-v2")
        non_custom_exercises = db.execute(
            select(TemplateExercise)
            .join(WorkoutTemplate, WorkoutTemplate.id == TemplateExercise.template_id)
            .where(WorkoutTemplate.catalog_section != "user")
        ).scalars().all()
        # Exactly the exercises of the 2 synthetic system templates remain,
        # plus nothing dangling from the boot catalog.
        assert {e.name for e in non_custom_exercises} == {
            "sys-a exercise",
            "sys-b exercise",
        }
        assert all(e.template_id != custom_id for e in non_custom_exercises)


# ───────── comportement existant inchangé ─────────


def test_seed_idempotent_same_version_is_noop(client):
    """Same version twice → second call returns False and touches nothing
    (pre-existing contract, must survive the guard)."""
    from sqlalchemy import func, select

    from app.database import SessionLocal
    from app.models.catalog import WorkoutTemplate

    with SessionLocal() as db:
        assert _reseed(db, "wipe-guard-idem-v2") is True
        count_before = db.execute(
            select(func.count()).select_from(WorkoutTemplate)
        ).scalar_one()
        assert _reseed(db, "wipe-guard-idem-v2") is False
        count_after = db.execute(
            select(func.count()).select_from(WorkoutTemplate)
        ).scalar_one()
        assert count_after == count_before


def test_boot_catalog_unchanged_without_custom_rows(client):
    """The real boot seed (reference_split.json) still produces the system
    catalog exactly as before — and contains zero 'user' rows."""
    from sqlalchemy import func, select

    from app.database import SessionLocal
    from app.models.catalog import WorkoutTemplate

    with SessionLocal() as db:
        n_user = db.execute(
            select(func.count())
            .select_from(WorkoutTemplate)
            .where(WorkoutTemplate.catalog_section == "user")
        ).scalar_one()
        assert n_user == 0
        n_total = db.execute(
            select(func.count()).select_from(WorkoutTemplate)
        ).scalar_one()
        assert n_total > 0  # boot seed ran normally


# ───────── garde d'entrée du namespace ─────────


def test_seed_payload_claiming_user_section_is_rejected(client):
    import pytest as _pytest

    from app.database import SessionLocal
    from app.services.seed import seed_reference_split

    bad = _payload("wipe-guard-bad-v2")
    bad["templates"][0]["catalog_section"] = "user"
    with SessionLocal() as db:
        with _pytest.raises(ValueError, match="reserved"):
            seed_reference_split(db, bad)


def test_reference_split_json_never_uses_user_section():
    payload = json.loads(
        (ROOT / "data" / "reference_split.json").read_text(encoding="utf-8")
    )
    sections = {t.get("catalog_section", "core") for t in payload["templates"]}
    assert "user" not in sections
