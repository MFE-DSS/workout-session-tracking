# SPIGNOS Exercise Feedback Rationalization Spec

**Sprint:** Sx_01_exercise_feedback_rationalization_spec
**Date:** 2026-04-13
**Status:** Spec approved, pending build

---

## 1. Audit Summary

### Current feedback fields in the codebase

The session logging flow captures feedback at 3 levels:

**Session level** (`workout_sessions`):
- `concentration` — STR high/medium/low (feeds quality_score 10pts, behavioral fatigue)
- `global_state` — STR good/flat/fatigued (feeds quality_score 10pts, behavioral fatigue)
- `bodyweight_kg` — FLOAT (per-session snapshot)
- `free_note` — STR max 280 chars (not consumed by analytics)

**Exercise level** (`session_exercises`):
- `success_score` — INT 100/80/50 (feeds quality_score 40pts, KPIs avg, deltas, exercise history, leaderboard indirectly)
- `muscle_sensation` — STR strong/partial/weak (feeds stats display, exercise history display, export only)
- `free_note` — STR max 140 chars (not consumed by analytics)

**Set level** (`set_logs`):
- `weight_kg` — FLOAT
- `reps` — INT
- `completed` — BOOL (feeds quality_score 40pts, KPIs completion_rate, delta first_set, progression_hint, leaderboard)
- `execution_quality` — STR clean/acceptable/degraded (**feeds ONLY export**)
- `reps_target` — STR target_hit/target_near/target_missed (**feeds ONLY export**)

### Key findings

1. **`execution_quality` and `reps_target` are analytically orphaned.** They cost 2 radio inputs per work set (10 inputs per exercise for 5 sets) but feed nothing except CSV/JSON export. No KPI, no scoring, no delta, no dashboard consumes them.

2. **`success_score` is the backbone of the analytics chain.** It's consumed by `quality_score.py` (40/100 pts), `kpis.py` (avg_success_score_30d, template avg), `delta.py` (score_trend), `exercise_history.py` (per-row display), `export_builder.py`, `progress.html` (template KPI). It's the most connected field in the codebase.

3. **`success_score` is a subjective global proxy** — the user says "it went well / ok / poorly". It correlates with but is NOT derived from objective set data (reps vs targets, completion). This creates a gap: the user can hit all targets but rate 50, or miss targets but rate 100.

4. **`muscle_sensation` is orthogonal and unique** — no other field captures "did I feel the target muscle working?" It has future value for physique dashboard correlation (zone → sensation mapping) but currently feeds only display.

5. **Current UX cost: ~27 inputs per exercise (5 work sets).** With 7 exercises: ~189 inputs per session. Disproportionate given that `execution_quality` + `reps_target` generate zero analytical value.

---

## 2. Decision Log

| Decision | Choice | Rationale |
|----------|--------|-----------|
| `execution_quality` + `reps_target` | **Hide from default form, keep in DB** | Immediate UX gain (-10 inputs/exercise). Columns preserved for future use or expert mode. No migration needed. |
| `success_score` | **Derive automatically from set data** | Removes 1 subjective input, replaces with objective signal. Stored in same column at save time — zero read-side refactor. Historical values preserved. |
| `muscle_sensation` | **Visually optional (collapsed/discrete)** | Unique physiological signal worth preserving. But must not block the flow — collapsed by default, no pre-selection. |

---

## 3. Target Model: Before → After

### Inputs per exercise card (5 work sets)

| Input | Before | After | Change |
|-------|--------|-------|--------|
| completed (checkbox) x5 | 5 | 5 | — |
| weight_kg (number) x5 | 5 | 5 | — |
| reps (number) x5 | 5 | 5 | — |
| execution_quality (radio) x5 | 5 | 0 | **Hidden** |
| reps_target (radio) x5 | 5 | 0 | **Hidden** |
| success_score (radio) | 1 | 0 | **Derived** |
| muscle_sensation (radio) | 1 | ~0.5 | **Optional/collapsed** |
| **Total** | **27** | **~16** | **-41%** |

Over 7 exercises: ~189 → ~112 inputs per session.

### Data model changes

**No columns added or removed.** All changes are behavioral:

| Column | DB change | Behavior change |
|--------|-----------|-----------------|
| `session_exercises.success_score` | None | Written by `compute_success_score()` at save time instead of form input |
| `session_exercises.muscle_sensation` | None | Still writable from form, but form renders it collapsed/optional |
| `set_logs.execution_quality` | None | Not parsed from default form. Column stays nullable. |
| `set_logs.reps_target` | None | Not parsed from default form. Column stays nullable. |

---

## 4. Derived `success_score` Algorithm

### Computation

Called by `update_exercise_card()` after saving set data, BEFORE `db.commit()`.

```
function compute_success_score(session_exercise, template_exercise) -> int | None:
    
    work_sets = [sl for sl in session_exercise.set_logs if sl.kind == "work"]
    completed = [sl for sl in work_sets if sl.completed]
    
    if not completed:
        return None  # No data → NULL (same as current "not rated")
    
    # Get rep targets from catalog (if available)
    rep_targets = {}  # set_index → (min_reps, max_reps)
    if template_exercise and template_exercise.rep_targets:
        for rt in template_exercise.rep_targets:
            rep_targets[rt.set_index] = (rt.min_reps, rt.max_reps)
    
    # Score each completed set
    set_scores = []
    for sl in completed:
        target = rep_targets.get(sl.set_index)
        if target and sl.reps is not None:
            min_r, max_r = target
            if sl.reps >= max_r:
                set_scores.append(100)  # Top of range
            elif sl.reps >= min_r:
                set_scores.append(80)   # In range
            else:
                set_scores.append(50)   # Below range
        else:
            set_scores.append(80)  # No target available → conservative default
    
    # Factor in completion ratio
    completion_ratio = len(completed) / len(work_sets)
    raw = mean(set_scores) * completion_ratio
    
    # Snap to {100, 80, 50} for backward compatibility
    if raw >= 90:
        return 100
    elif raw >= 65:
        return 80
    else:
        return 50
```

### Why snap to {100, 80, 50}

Every consumer of `success_score` expects an INT in {100, 80, 50, NULL}:
- `quality_score.py`: `(avg_score / 100) * 40` — works with any of {100, 80, 50}
- `kpis.py`: `func.avg(SessionExercise.success_score)` — aggregates integers
- `delta.py`: compares current vs prior as up/flat/down
- `exercise_history.py`: displays the value directly
- `ExerciseSuccessScore` enum in `app/enums.py`: defines S100=100, S80=80, S50=50

By snapping to the same 3 values, **zero read-side code changes are needed.** The derived value is indistinguishable from a manually entered one.

### Fallback behavior

| Situation | Behavior |
|-----------|----------|
| No completed work sets | `success_score = NULL` |
| No template_exercise (detached after reseed) | Each set scores 80 (conservative) |
| No rep_targets on template_exercise | Each set scores 80 (conservative) |
| Reps not entered on a completed set | That set scores 80 (conservative) |
| All sets completed, all hit max_reps | 100 |
| All sets completed, all in range | 80 |
| Half sets completed, all below range | 50 |

### Historical compatibility

**Existing `success_score` values are never modified.** The derivation runs only on new saves going forward. Historical sessions retain their manually entered values. This means:
- Deltas comparing old (manual) vs new (derived) are valid — same scale, same meaning
- KPI averages mix manual and derived — acceptable, both represent "how well did the exercise go"
- Export shows the stored value regardless of source

---

## 5. UI Changes

### Exercise card — set rows

**Before:** Each work set row shows: checkbox + weight + reps + execution_quality radio (3 options) + reps_target radio (3 options)

**After:** Each work set row shows: checkbox + weight + reps

`execution_quality` and `reps_target` radios are removed from the default form. The columns remain in DB (nullable, will be NULL for new sessions).

### Exercise card — exercise feedback section

**Before:** success_score radio (3 options) + muscle_sensation radio (3 options) + free_note textarea

**After:**
- success_score radio **removed** (derived automatically)
- muscle_sensation rendered as **collapsed optional section** — a small "Sensation musculaire" link/button that expands to show the 3-option radio. No pre-selection. If the user ignores it, `muscle_sensation = NULL`.
- free_note textarea **unchanged**

### Session feedback form

**Unchanged.** concentration, global_state, bodyweight_kg, free_note remain as-is.

---

## 6. Files Impacted

### Must change (build Sb_01)

| File | Change |
|------|--------|
| `app/services/feedback.py` | **New.** `compute_success_score(session_exercise, template_exercise) -> int \| None` |
| `app/routers/sessions.py` | **Modify.** In `update_exercise_card()`: remove `success_score` form parsing, remove `execution_quality`/`reps_target` form parsing, call `compute_success_score()` after set save. |
| `app/templates/session_detail.html` | **Modify.** Remove success_score radios, remove execution_quality/reps_target radios per set, make muscle_sensation collapsed/optional. |
| `tests/test_feedback.py` | **New.** Test `compute_success_score()` with various scenarios. |
| Tests touching session form | **Modify.** Remove `success_score` from form POST data in tests. Adapt assertions. |

### No change needed (read-side untouched)

| File | Why unchanged |
|------|---------------|
| `app/services/quality_score.py` | Reads `success_score` column — same values |
| `app/services/kpis.py` | Reads `success_score` column — same values |
| `app/services/delta.py` | Reads `success_score` column — same values |
| `app/services/exercise_history.py` | Reads `success_score` column — same values |
| `app/services/stats.py` | Reads `success_score` + `muscle_sensation` — same columns |
| `app/services/progression_hint.py` | Uses weight/reps only — unaffected |
| `app/services/export_builder.py` | Exports columns as-is — execution_quality/reps_target will be NULL for new sessions |
| `app/models/session.py` | All columns preserved — no migration |
| `app/services/leaderboard.py` | Uses quality_score which uses success_score — transitive, unchanged |
| `app/services/behavioral.py` | Uses quality_score — transitive, unchanged |

---

## 7. Migration Strategy

**No Alembic migration required.**

- No columns added or removed
- No schema changes
- success_score continues to be written to the same column
- execution_quality and reps_target columns remain but will be NULL for new sessions
- Historical data fully preserved

---

## 8. Acceptance Criteria — Spec

- [x] Audit table produced: champ / niveau / consumer / doublon / decision
- [x] Every consumer of success_score identified and impact assessed
- [x] Derivation algorithm defined with fallback behavior
- [x] Snap-to-{100,80,50} compatibility proven
- [x] Historical compatibility strategy defined (no data migration)
- [x] UI changes specified (which inputs removed, which collapsed)
- [x] Files impacted listed with change type
- [x] Zero read-side changes confirmed
- [x] Risks documented

## 9. Acceptance Criteria — Build (Sb_01)

- [ ] `compute_success_score()` implemented and tested
- [ ] `update_exercise_card()` calls derivation instead of reading form input
- [ ] execution_quality and reps_target radios removed from session_detail.html
- [ ] success_score radios removed from session_detail.html
- [ ] muscle_sensation rendered as collapsed/optional
- [ ] All existing tests pass (quality_score, kpis, delta, exercise_history, leaderboard)
- [ ] New tests cover derivation scenarios (all targets hit, partial, no targets, no sets)
- [ ] Export still includes execution_quality/reps_target columns (NULL for new sessions)
- [ ] Input count per exercise reduced from ~27 to ~16

---

## 10. Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Derived score diverges from user expectation | Medium | Snap to {100,80,50} is coarse — limits surprise. Score logic is simple and documented in scoring rules. |
| Templates without rep_targets (archived) | Low | Fallback to 80 per set. Conservative, not penalizing. |
| Tests that POST success_score in form data | Low | Update tests to not send it; verify derived value instead. |
| Export consumers expect non-null execution_quality | Low | Export already handles NULL. New sessions will have NULL — documented. |
| Users who liked rating exercises manually | Medium | muscle_sensation remains as the subjective outlet. success_score was often auto-piloted (always 100). |

---

## 11. Blockers for Sx_02

Before the mobile exercise UX refactor (Sx_02) can proceed:
- This spec must be validated (done)
- The build (Sb_01) must implement the feedback changes so that Sx_02 designs against the **reduced input form**, not the current 27-input form
- If Sb_01 is deferred, Sx_02 must be designed for BOTH the current and target input sets, which doubles the UX work

**Recommendation:** Build Sb_01 before designing Sx_02.
