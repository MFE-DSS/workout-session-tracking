# Sb_01 — Feedback Signal Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace manual success_score input with automatic derivation from set data, hide execution_quality/reps_target from the default form, and make muscle_sensation visually optional — reducing inputs per exercise from ~27 to ~16.

**Architecture:** New `app/services/feedback.py` computes success_score from completed sets vs rep_targets. The router stops parsing success_score/execution_quality/reps_target from the form and calls the derivation instead. Template changes remove/collapse the corresponding UI elements. Zero read-side changes — all consumers continue reading the same `success_score` column.

**Tech Stack:** Python (pure computation), FastAPI form handling, Jinja2 template edits, pytest

---

## File Structure

| File | Responsibility |
|------|---------------|
| `app/services/feedback.py` | **New** — `compute_success_score(session_exercise, template_exercise) -> int \| None` |
| `app/routers/sessions.py` | **Modify** — remove form parsing for 3 fields, call derivation |
| `app/templates/session_detail.html` | **Modify** — remove/collapse UI elements |
| `tests/test_feedback.py` | **New** — derivation algorithm tests |
| Various test files | **Modify** — remove success_score from form POST data |

---

### Task 1: compute_success_score Service

**Files:**
- Create: `app/services/feedback.py`
- Create: `tests/test_feedback.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_feedback.py`:

```python
"""Tests for automatic success_score derivation."""
from __future__ import annotations

from unittest.mock import MagicMock


def _make_set_log(set_index, reps, completed=True, kind="work"):
    sl = MagicMock()
    sl.kind = kind
    sl.set_index = set_index
    sl.reps = reps
    sl.completed = completed
    sl.weight_kg = 60.0
    return sl


def _make_rep_target(set_index, min_reps, max_reps):
    rt = MagicMock()
    rt.set_index = set_index
    rt.min_reps = min_reps
    rt.max_reps = max_reps
    return rt


def _make_session_exercise(set_logs):
    se = MagicMock()
    se.set_logs = set_logs
    return se


def _make_template_exercise(rep_targets):
    if rep_targets is None:
        return None
    te = MagicMock()
    te.rep_targets = rep_targets
    return te


def test_all_sets_hit_max_reps():
    """All 3 work sets completed at top of range → 100."""
    from app.services.feedback import compute_success_score
    se = _make_session_exercise([
        _make_set_log(1, 10),
        _make_set_log(2, 10),
        _make_set_log(3, 10),
    ])
    te = _make_template_exercise([
        _make_rep_target(1, 6, 10),
        _make_rep_target(2, 6, 10),
        _make_rep_target(3, 6, 10),
    ])
    assert compute_success_score(se, te) == 100


def test_all_sets_in_range():
    """All sets completed within range but not at max → 80."""
    from app.services.feedback import compute_success_score
    se = _make_session_exercise([
        _make_set_log(1, 8),
        _make_set_log(2, 7),
        _make_set_log(3, 8),
    ])
    te = _make_template_exercise([
        _make_rep_target(1, 6, 10),
        _make_rep_target(2, 6, 10),
        _make_rep_target(3, 6, 10),
    ])
    assert compute_success_score(se, te) == 80


def test_all_sets_below_range():
    """All sets completed but below min_reps → 50."""
    from app.services.feedback import compute_success_score
    se = _make_session_exercise([
        _make_set_log(1, 4),
        _make_set_log(2, 5),
        _make_set_log(3, 3),
    ])
    te = _make_template_exercise([
        _make_rep_target(1, 6, 10),
        _make_rep_target(2, 6, 10),
        _make_rep_target(3, 6, 10),
    ])
    assert compute_success_score(se, te) == 50


def test_no_completed_sets_returns_none():
    """No completed sets → None (same as 'not rated')."""
    from app.services.feedback import compute_success_score
    se = _make_session_exercise([
        _make_set_log(1, None, completed=False),
        _make_set_log(2, None, completed=False),
    ])
    te = _make_template_exercise([
        _make_rep_target(1, 6, 10),
        _make_rep_target(2, 6, 10),
    ])
    assert compute_success_score(se, te) is None


def test_partial_completion_reduces_score():
    """2/3 sets completed at max reps → score reduced by completion ratio."""
    from app.services.feedback import compute_success_score
    se = _make_session_exercise([
        _make_set_log(1, 10),
        _make_set_log(2, 10),
        _make_set_log(3, None, completed=False),
    ])
    te = _make_template_exercise([
        _make_rep_target(1, 6, 10),
        _make_rep_target(2, 6, 10),
        _make_rep_target(3, 6, 10),
    ])
    # mean([100,100]) * (2/3) = 100 * 0.667 = 66.7 → snaps to 80
    assert compute_success_score(se, te) == 80


def test_no_template_exercise_defaults_to_80():
    """No template exercise (detached) → all sets score 80."""
    from app.services.feedback import compute_success_score
    se = _make_session_exercise([
        _make_set_log(1, 10),
        _make_set_log(2, 10),
    ])
    assert compute_success_score(se, None) == 80


def test_no_rep_targets_defaults_to_80():
    """Template exercise with empty rep_targets → all sets score 80."""
    from app.services.feedback import compute_success_score
    se = _make_session_exercise([
        _make_set_log(1, 10),
        _make_set_log(2, 10),
    ])
    te = _make_template_exercise([])
    assert compute_success_score(se, te) == 80


def test_reps_none_on_completed_set_defaults_to_80():
    """Completed set but reps not entered → that set scores 80."""
    from app.services.feedback import compute_success_score
    se = _make_session_exercise([
        _make_set_log(1, None, completed=True),
        _make_set_log(2, 10, completed=True),
    ])
    te = _make_template_exercise([
        _make_rep_target(1, 6, 10),
        _make_rep_target(2, 6, 10),
    ])
    # set1: no reps → 80, set2: 10 >= 10 → 100. mean=90, ratio=1.0 → 100
    assert compute_success_score(se, te) == 100


def test_warmup_sets_are_ignored():
    """Warmup sets don't participate in scoring."""
    from app.services.feedback import compute_success_score
    se = _make_session_exercise([
        _make_set_log(1, 5, kind="warmup"),
        _make_set_log(1, 10, kind="work"),
        _make_set_log(2, 10, kind="work"),
    ])
    te = _make_template_exercise([
        _make_rep_target(1, 6, 10),
        _make_rep_target(2, 6, 10),
    ])
    assert compute_success_score(se, te) == 100


def test_mixed_scores_snap_correctly():
    """Mix of scores snaps to nearest {100, 80, 50}."""
    from app.services.feedback import compute_success_score
    # 1 at max (100), 1 in range (80), 1 below (50) → mean=76.7, ratio=1.0 → 80
    se = _make_session_exercise([
        _make_set_log(1, 10),
        _make_set_log(2, 8),
        _make_set_log(3, 4),
    ])
    te = _make_template_exercise([
        _make_rep_target(1, 6, 10),
        _make_rep_target(2, 6, 10),
        _make_rep_target(3, 6, 10),
    ])
    assert compute_success_score(se, te) == 80
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_feedback.py -v`
Expected: FAIL (ImportError)

- [ ] **Step 3: Implement compute_success_score**

Create `app/services/feedback.py`:

```python
"""Automatic success_score derivation from set-level data.

Replaces manual 100/80/50 input. The score is computed from
completed work sets vs their rep targets, then snapped to
{100, 80, 50} for backward compatibility with all consumers.

Called by update_exercise_card() after saving set data.
"""
from __future__ import annotations

from statistics import mean
from typing import Optional


def compute_success_score(
    session_exercise,
    template_exercise,
) -> Optional[int]:
    """Derive success_score from completed work sets vs rep targets.

    Returns 100, 80, 50, or None (if no completed work sets).
    """
    work_sets = [sl for sl in session_exercise.set_logs if sl.kind == "work"]
    completed = [sl for sl in work_sets if sl.completed]

    if not completed:
        return None

    # Build rep target lookup: set_index → (min_reps, max_reps)
    targets: dict[int, tuple[int, int]] = {}
    if template_exercise and template_exercise.rep_targets:
        for rt in template_exercise.rep_targets:
            targets[rt.set_index] = (rt.min_reps, rt.max_reps)

    # Score each completed set
    set_scores: list[int] = []
    for sl in completed:
        target = targets.get(sl.set_index)
        if target and sl.reps is not None:
            min_r, max_r = target
            if sl.reps >= max_r:
                set_scores.append(100)
            elif sl.reps >= min_r:
                set_scores.append(80)
            else:
                set_scores.append(50)
        else:
            # No target available or reps not entered → conservative default
            set_scores.append(80)

    # Factor in completion ratio
    completion_ratio = len(completed) / len(work_sets)
    raw = mean(set_scores) * completion_ratio

    # Snap to {100, 80, 50}
    if raw >= 90:
        return 100
    elif raw >= 65:
        return 80
    else:
        return 50
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_feedback.py -v`
Expected: All PASS (11 tests).

- [ ] **Step 5: Commit**

```bash
git add app/services/feedback.py tests/test_feedback.py
git commit -m "feat(sb01): compute_success_score — derive from set data, snap to {100,80,50}"
```

---

### Task 2: Wire Derivation into Router

**Files:**
- Modify: `app/routers/sessions.py`

- [ ] **Step 1: Modify update_exercise_card**

In `app/routers/sessions.py`, modify the `update_exercise_card` function (line 274+).

Replace the exercise-level feedback section (lines 297-300):
```python
    # Exercise-level feedback
    se.success_score = enum_int(form.get("success_score"), _SUCCESS_SCORE)
    se.muscle_sensation = enum_str(form.get("muscle_sensation"), _MUSCLE_SENSATION)
    se.free_note = clean_str(form.get("free_note"), max_length=140)
```

With:
```python
    # Exercise-level feedback
    # success_score is now derived from set data (Sb_01)
    se.muscle_sensation = enum_str(form.get("muscle_sensation"), _MUSCLE_SENSATION)
    se.free_note = clean_str(form.get("free_note"), max_length=140)
```

Then, after the set loop (after line 312) and BEFORE `db.commit()`, add the derivation call:

```python
    # Derive success_score from set data
    from app.services.feedback import compute_success_score
    se.success_score = compute_success_score(se, se.template_exercise)
```

Also, in the set loop (lines 303-312), remove the parsing of `execution_quality` and `reps_target`:

Replace:
```python
    for sl in se.set_logs:
        p = f"set_{sl.id}_"
        sl.weight_kg = to_float(form.get(p + "weight_kg"))
        sl.reps = to_int(form.get(p + "reps"))
        sl.completed = checkbox(form.get(p + "completed"))
        if sl.kind == "work":
            sl.execution_quality = enum_str(
                form.get(p + "execution_quality"), _EXECUTION_QUALITY
            )
            sl.reps_target = enum_str(form.get(p + "reps_target"), _REPS_TARGET)
```

With:
```python
    for sl in se.set_logs:
        p = f"set_{sl.id}_"
        sl.weight_kg = to_float(form.get(p + "weight_kg"))
        sl.reps = to_int(form.get(p + "reps"))
        sl.completed = checkbox(form.get(p + "completed"))
```

- [ ] **Step 2: Run existing session tests**

Run: `pytest tests/test_session_flow.py tests/test_session_schema.py -v`
Expected: Some may fail because they POST `success_score` in form data and check the stored value. We'll fix those in Task 4.

- [ ] **Step 3: Commit**

```bash
git add app/routers/sessions.py
git commit -m "feat(sb01): wire compute_success_score into exercise card save, remove manual parsing"
```

---

### Task 3: Template Changes — Remove/Collapse UI

**Files:**
- Modify: `app/templates/session_detail.html`

- [ ] **Step 1: Remove execution_quality and reps_target from work set rows**

In `app/templates/session_detail.html`, find the work set section (lines 264-279) and remove the two `set-row__mini` divs:

Remove these lines from each work set `<li>`:
```html
            <div class="set-row__mini">
              <span class="set-row__mini-label">Exécution</span>
              {{ segmented(
                "set_" ~ sl.id ~ "_execution_quality",
                [("clean", "clean"), ("acceptable", "accept."), ("degraded", "degrad.")],
                sl.execution_quality
              ) }}
            </div>
            <div class="set-row__mini">
              <span class="set-row__mini-label">Target reps</span>
              {{ segmented(
                "set_" ~ sl.id ~ "_reps_target",
                [("target_hit", "hit"), ("target_near", "near"), ("target_missed", "missed")],
                sl.reps_target
              ) }}
            </div>
```

- [ ] **Step 2: Remove success_score radio from exercise feedback**

Find the "Feedback exercice" section (lines 287-291) and remove the success_score block:

Remove:
```html
    <div class="field-block">
      <span class="field__label">Score</span>
      {{ segmented("success_score", [100, 80, 50], se.success_score) }}
    </div>
```

- [ ] **Step 3: Make muscle_sensation collapsed/optional**

Replace the muscle_sensation block (lines 293-299):

```html
    <div class="field-block">
      <span class="field__label">Muscle cible</span>
      {{ segmented(
        "muscle_sensation",
        [("strong", "Strong"), ("partial", "Partial"), ("weak", "Weak")],
        se.muscle_sensation
      ) }}
    </div>
```

With a collapsed version:
```html
    <details class="field-block field-block--optional">
      <summary class="field__label" style="cursor:pointer;font-size:13px;color:var(--fg-dim);">
        Sensation musculaire (optionnel)
      </summary>
      {{ segmented(
        "muscle_sensation",
        [("strong", "Strong"), ("partial", "Partial"), ("weak", "Weak")],
        se.muscle_sensation
      ) }}
    </details>
```

- [ ] **Step 4: Verify the page renders**

Run: `pytest tests/test_session_flow.py::test_session_detail_renders_exercise_cards -v`
Expected: PASS (template renders without error).

- [ ] **Step 5: Commit**

```bash
git add app/templates/session_detail.html
git commit -m "feat(sb01): simplify exercise card UI — hide eq/rt, remove score radio, collapse sensation"
```

---

### Task 4: Fix Existing Tests

**Files:**
- Modify: multiple test files that POST `success_score` in form data

- [ ] **Step 1: Identify and fix all tests that send success_score in form data**

The tests that POST to `/sessions/{id}/exercises/{se_id}` currently include `"success_score": "80"` in the form data. Since the router no longer reads this field, the tests need to:
1. Remove `success_score` from the POST data
2. Change assertions from "check that the stored value matches what we sent" to "check that the stored value is derived correctly"

Similarly, tests that send `execution_quality` or `reps_target` — remove those from POST data.

Key test files to check and fix:
- `tests/test_session_flow.py` — exercise card POST
- `tests/test_session_schema.py` — schema validation tests
- `tests/test_session_management.py` — session management
- `tests/test_mobile_polish.py` — mobile polish tests
- `tests/test_past_session_readability.py` — readability tests
- `tests/test_last_time.py` — last time tests
- `tests/test_export.py` — export tests
- `tests/test_csv_export.py` — CSV export tests

For each file: grep for `success_score`, `execution_quality`, `reps_target` in form POST data and remove them. If the test asserts a specific `success_score` value, change to assert it's one of {100, 80, 50, None} (derived value).

- [ ] **Step 2: Run full test suite**

Run: `pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q`
Expected: All pass.

- [ ] **Step 3: Commit**

```bash
git add tests/
git commit -m "test(sb01): adapt tests for derived success_score — remove manual score from form POSTs"
```

---

### Task 5: Final Verification + Sprint Report

**Files:**
- Create: `docs/SPRINT_Sb01_REPORT.md`

- [ ] **Step 1: Run full test suite**

Run: `pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q`
Expected: All pass.

- [ ] **Step 2: Write sprint report**

Create `docs/SPRINT_Sb01_REPORT.md`:

```markdown
# Sprint Sb_01 Report — Feedback Signal Refactor

**Date:** 2026-04-14
**Status:** Complete
**Spec:** docs/strategy/SPIGNOS_EXERCISE_FEEDBACK_RATIONALIZATION.md

## Objective

Replace manual success_score with automatic derivation, hide
execution_quality/reps_target, make muscle_sensation optional.
Reduce inputs per exercise from ~27 to ~16.

## Deliverables

| Artifact | Path | Status |
|----------|------|--------|
| Derivation service | `app/services/feedback.py` | Done |
| Router changes | `app/routers/sessions.py` | Done |
| Template changes | `app/templates/session_detail.html` | Done |
| Derivation tests | `tests/test_feedback.py` | Done |

## Changes

- `compute_success_score()` derives 100/80/50 from set data vs rep targets
- Router no longer parses success_score, execution_quality, reps_target from form
- Template: removed score radio, removed eq/rt per-set radios, collapsed sensation
- Zero read-side changes (quality_score, kpis, delta, history, export all unchanged)
- Zero migration (columns preserved, historical values intact)

## Verification

```bash
pytest tests/test_feedback.py -v
pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q
```

## Unblocks

- Sx_02 (mobile exercise entry UX) can now design against the reduced 16-input form
```

- [ ] **Step 3: Commit**

```bash
git add docs/SPRINT_Sb01_REPORT.md
git commit -m "docs(sb01): sprint report — feedback signal refactor complete"
```
