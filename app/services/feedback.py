"""Feedback scoring for individual session exercises.

compute_success_score derives an integer success score (100 | 80 | 50)
for a SessionExercise based on how well the logged sets matched the
prescribed rep targets from the corresponding TemplateExercise.

Algorithm:
  1. Filter to work sets only (sl.kind == "work")
  2. Filter to completed sets (sl.completed)
  3. If no completed work sets → return None
  4. Build rep target lookup: {set_index: (min_reps, max_reps)}
  5. Score each completed set:
       - target exists AND reps is not None:
           reps >= max_reps → 100
           reps >= min_reps → 80
           else            → 50
       - no target or reps is None → 80 (conservative default)
  6. completion_ratio = len(completed) / len(work_sets)
  7. raw = mean(set_scores) * completion_ratio
  8. Snap: raw >= 90 → 100, raw >= 65 → 80, else → 50
"""
from __future__ import annotations

from statistics import mean
from typing import Optional


def compute_success_score(session_exercise, template_exercise) -> Optional[int]:
    """Return a snapped success score (100 | 80 | 50) or None.

    Parameters
    ----------
    session_exercise:
        A SessionExercise ORM object (or compatible mock) with a
        `set_logs` iterable of SetLog objects having `.kind`,
        `.completed`, `.set_index`, and `.reps` attributes.
    template_exercise:
        A TemplateExercise ORM object (or None) with a `rep_targets`
        iterable of RepTarget objects having `.set_index`, `.min_reps`,
        and `.max_reps` attributes.
    """
    # Step 1: work sets only
    work_sets = [sl for sl in session_exercise.set_logs if sl.kind == "work"]

    # Step 2: completed work sets
    completed = [sl for sl in work_sets if sl.completed]

    # Step 3: guard — nothing scored
    if not completed:
        return None

    # Step 4: build rep target lookup
    rep_target_lookup: dict[int, tuple[int, int]] = {}
    if template_exercise is not None and template_exercise.rep_targets:
        for rt in template_exercise.rep_targets:
            rep_target_lookup[rt.set_index] = (rt.min_reps, rt.max_reps)

    # Step 5: score each completed set
    set_scores: list[int] = []
    for sl in completed:
        target = rep_target_lookup.get(sl.set_index)
        if target is not None and sl.reps is not None:
            min_reps, max_reps = target
            if sl.reps >= max_reps:
                set_scores.append(100)
            elif sl.reps >= min_reps:
                set_scores.append(80)
            else:
                set_scores.append(50)
        else:
            # No target or reps unknown → conservative default
            set_scores.append(80)

    # Step 6 & 7: completion ratio and raw score
    completion_ratio = len(completed) / len(work_sets)
    raw = mean(set_scores) * completion_ratio

    # Step 8: snap to discrete values
    if raw >= 90:
        return 100
    elif raw >= 65:
        return 80
    else:
        return 50
