"""Tests for exercise substitution service."""
from __future__ import annotations
from unittest.mock import MagicMock


def test_actual_exercise_name_no_substitution():
    from app.services.substitution import actual_exercise_name
    se = MagicMock()
    se.substituted_name = None
    se.exercise_name_snapshot = "Chest Press machine"
    assert actual_exercise_name(se) == "Chest Press machine"


def test_actual_exercise_name_with_substitution():
    from app.services.substitution import actual_exercise_name
    se = MagicMock()
    se.substituted_name = "Développé couché haltères"
    se.exercise_name_snapshot = "Chest Press machine"
    assert actual_exercise_name(se) == "Développé couché haltères"


def test_get_substitutes_from_json():
    from app.services.substitution import get_substitutes
    te = MagicMock()
    te.substitutes_json = '["Développé couché haltères", "Dips pectoraux"]'
    assert get_substitutes(te) == ["Développé couché haltères", "Dips pectoraux"]


def test_get_substitutes_none():
    from app.services.substitution import get_substitutes
    te = MagicMock()
    te.substitutes_json = None
    assert get_substitutes(te) == []


def test_get_substitutes_no_template_exercise():
    from app.services.substitution import get_substitutes
    assert get_substitutes(None) == []


def test_can_substitute_no_completed_sets():
    from app.services.substitution import can_substitute
    se = MagicMock()
    sl1 = MagicMock(); sl1.kind = "work"; sl1.completed = False
    se.set_logs = [sl1]
    assert can_substitute(se) is True


def test_can_substitute_has_completed_set():
    from app.services.substitution import can_substitute
    se = MagicMock()
    sl1 = MagicMock(); sl1.kind = "work"; sl1.completed = True
    se.set_logs = [sl1]
    assert can_substitute(se) is False


def test_can_substitute_warmup_only_does_not_lock():
    from app.services.substitution import can_substitute
    se = MagicMock()
    sl1 = MagicMock(); sl1.kind = "warmup"; sl1.completed = True
    sl2 = MagicMock(); sl2.kind = "work"; sl2.completed = False
    se.set_logs = [sl1, sl2]
    assert can_substitute(se) is True
