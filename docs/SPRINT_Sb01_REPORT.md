# Sprint Sb_01 Report — Feedback Signal Refactor

**Date:** 2026-04-14
**Status:** Complete
**Spec:** docs/strategy/SPIGNOS_EXERCISE_FEEDBACK_RATIONALIZATION.md
**Tests:** 453 passed, 0 failed

## Objective

Replace manual success_score with automatic derivation, hide
execution_quality/reps_target from default form, make muscle_sensation
visually optional. Reduce inputs per exercise from ~27 to ~16.

## Deliverables

| Artifact | Path | Status |
|----------|------|--------|
| Derivation service | `app/services/feedback.py` | Done — `compute_success_score()` |
| Derivation tests | `tests/test_feedback.py` | Done — 10 tests |
| Router changes | `app/routers/sessions.py` | Done — derivation wired, manual parsing removed |
| Template changes | `app/templates/session_detail.html` | Done — simplified |

## Changes

### Service layer
- `compute_success_score(session_exercise, template_exercise) -> int | None`
- Derives 100/80/50 from completed work sets vs rep targets
- Fallback to 80 when no targets or reps unavailable
- Snap to {100, 80, 50} for backward compatibility

### Router
- `update_exercise_card()` no longer parses success_score from form
- No longer parses execution_quality or reps_target from form
- Calls `compute_success_score()` after saving set data, before commit
- Muscle_sensation still parsed from form (unchanged)

### Template
- Removed success_score radio (3 options) from exercise feedback
- Removed execution_quality segmented control per work set
- Removed reps_target segmented control per work set
- Muscle_sensation wrapped in `<details>` (collapsed by default, optional)

### Zero read-side changes
- `quality_score.py` — reads success_score column, unchanged
- `kpis.py` — reads success_score column, unchanged
- `delta.py` — reads success_score column, unchanged
- `exercise_history.py` — reads success_score column, unchanged
- `export_builder.py` — exports columns as-is, unchanged
- `behavioral.py` — uses quality_score transitively, unchanged
- `leaderboard.py` — uses quality_score transitively, unchanged

### Zero migration
- No columns added or removed
- Historical values preserved
- execution_quality/reps_target will be NULL for new sessions

## Verification

```bash
pytest tests/test_feedback.py -v          # 10 derivation tests
pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q  # 453 passed
```

## UX Impact

| Metric | Before | After |
|--------|--------|-------|
| Inputs per exercise (5 work sets) | ~27 | ~16 |
| Inputs per session (7 exercises) | ~189 | ~112 |
| Reduction | | **-41%** |

## Unblocks

- **Sx_02** (mobile exercise entry UX) can now design against the reduced 16-input form
- **Sx_03** (exercise substitution graph) unaffected
