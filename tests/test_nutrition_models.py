"""Real SQLite constraints for the proposed two nutrition revision tables."""

import importlib.util

import pytest
from nutrition_helpers import nutrition_db
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


def test_nutrition_revision_models_exist():
    assert importlib.util.find_spec("app.models.nutrition") is not None


@pytest.fixture()
def db(tmp_path):
    with nutrition_db(tmp_path) as session:
        yield session


def target(**changes):
    from app.models.nutrition import NutritionTargetRevision

    return NutritionTargetRevision(**{
        "user_id": 1, "variant": "STANDARD", "effective_from": "2026-11-12",
        "revision": 1, "parent_ref": None, "enabled": True, "kcal_milli": 2000000,
        "request_id": "target-1", "command_digest": "a" * 64,
        "receipt": {"state": "APPLIED"}, "provenance": {}, **changes,
    })


def day(**changes):
    from app.models.nutrition import NutritionDayRevision

    return NutritionDayRevision(**{
        "user_id": 1, "local_day": "2026-11-12", "timezone": "Europe/Paris",
        "revision": 1, "parent_ref": None, "state": "ACTIVE", "declared_complete": False,
        "kcal_milli": 0, "request_id": "day-1", "command_digest": "b" * 64,
        "receipt": {"state": "APPLIED"}, "provenance": {}, **changes,
    })


def test_foreign_target_ref_is_rejected_but_own_reference_and_account_cascade_work(db):
    from app.models.nutrition import NutritionDayRevision, NutritionTargetRevision
    from app.models.user import User

    preset = target()
    db.add(preset)
    db.commit()
    preset_id = preset.id
    db.add(day(user_id=2, target_ref=preset_id))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()
    db.add(day(target_ref=preset_id))
    db.commit()
    db.delete(db.get(User, 1))
    db.commit()
    assert list(db.scalars(select(NutritionDayRevision))) == []
    assert list(db.scalars(select(NutritionTargetRevision))) == []


@pytest.mark.parametrize("changes", [
    {"kcal_milli": -1}, {"kcal_milli": 1.5}, {"kcal_milli": 1000000000},
    {"revision": 2}, {"command_digest": "x" * 64}, {"request_id": ""},
    {"state": "WITHDRAWN", "kcal_milli": 0},
    {"state": "ACTIVE", "kcal_milli": None},
])
def test_sql_refuses_invalid_day_storage(db, changes):
    db.add(day(**changes))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_revisions_have_one_successor_and_one_command_per_namespace(db):
    original = day()
    db.add(original)
    db.commit()
    parent_id = original.id
    db.add(day(revision=2, parent_ref=parent_id, request_id="day-2", kcal_milli=1800000))
    db.commit()
    # A fork cannot claim the same parent even under another logical date.
    db.add(day(local_day="2026-11-11", revision=2, parent_ref=parent_id, request_id="fork"))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()
    # Same request ID is distinct in TARGET, but cannot be duplicated within DAY.
    db.add(target(request_id="day-1"))
    db.commit()
    db.add(day(local_day="2026-11-11"))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()
    assert original.kcal_milli == 0
