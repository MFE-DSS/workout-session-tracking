"""Exercise substitution helpers.

Substitution is catalogue-driven: each TemplateExercise can carry
a JSON list of substitute exercise names. The user picks one before
their first completed set. After that, the choice is locked.
"""
from __future__ import annotations

import json


def actual_exercise_name(session_exercise) -> str:
    """Return the exercise name that was actually performed."""
    return session_exercise.substituted_name or session_exercise.exercise_name_snapshot


def get_substitutes(template_exercise) -> list[str]:
    """Return the list of substitute names, or empty list."""
    if template_exercise is None:
        return []
    raw = getattr(template_exercise, "substitutes_json", None)
    if not raw:
        return []
    try:
        result = json.loads(raw)
        return result if isinstance(result, list) else []
    except (json.JSONDecodeError, TypeError):
        return []


def can_substitute(session_exercise) -> bool:
    """True if no work set has been completed yet."""
    for sl in session_exercise.set_logs:
        if sl.kind == "work" and sl.completed:
            return False
    return True
