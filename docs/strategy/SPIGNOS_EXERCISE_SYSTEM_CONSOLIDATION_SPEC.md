# SPIGNOS Exercise System Consolidation Spec

**Sprint:** Sx_04_exercise_system_consolidation_spec
**Date:** 2026-04-14
**Status:** Complete

---

## 1. Purpose

This document aligns the three exercise system specs (Sx_01, Sx_02, Sx_03) and defines the build queue with dependency order, ensuring no spec contradicts another and the implementation path is clear.

---

## 2. Spec Cross-Reference

| Spec | Focus | Key change | Status |
|------|-------|-----------|--------|
| Sx_01 | Feedback rationalization | success_score derived, eq/rt hidden, sensation optional | Spec done, **built (Sb_01)** |
| Sx_02 | Mobile exercise entry UX | `<details>` accordion, compact summary, feedback at bottom | Spec done, **pending build (Sb_02)** |
| Sx_03 | Exercise substitution | JSON substitutes, `substituted_name` field, lock after first set | Spec done, **pending build (Sb_03)** |

---

## 3. Dependency Analysis

```
Sx_01 spec → Sb_01 build ✓ (DONE)
     ↓
Sx_02 spec ✓ (designs against reduced 16-input form)
     ↓
Sb_02 build (template refactor: <details>, compact, feedback bottom)
     ↓
Sx_03 spec ✓ (designs substitution select into the <details> card)
     ↓
Sb_03 build (substitution: migration + catalogue + router + muscle_scoring)
```

### Why this order

1. **Sb_01 before Sb_02**: The template refactor (Sb_02) must work on the simplified form (16 inputs, no eq/rt radios, no score radio). If built on the old form, the `<details>` cards would be too large.

2. **Sb_02 before Sb_03**: The substitution select (Sb_03) lives inside the `<details>` exercise card. The card structure must be finalized (Sb_02) before adding the select.

3. **Sb_03 last**: Substitution is additive — it adds a select and a field. It doesn't restructure anything. It can be built on top of the Sb_02 template.

---

## 4. Interaction Points Between Specs

### Sx_01 × Sx_02: Feedback form inside `<details>`

The exercise card feedback section (muscle_sensation collapsed, free_note) sits inside the `<details>` form. When the card is collapsed, the feedback is hidden. When open, it's at the bottom of the form before the submit button. No conflict.

### Sx_02 × Sx_03: Substitution select inside `<details>`

The substitution select (Sx_03) goes in the exercise card header area, inside the `<details>` but visible when open. Position: under the exercise name, above the last-time block. When collapsed, the compact summary shows `actual_exercise_name` (not the prescribed name if substituted). No conflict.

### Sx_01 × Sx_03: Derived success_score + substitution

`compute_success_score()` uses rep_targets from `template_exercise`. When an exercise is substituted, the template_exercise still points to the original slot (same rep_targets). This is correct: the user is still aiming for the same set/rep scheme, just on a different machine. The rep_targets don't change with substitution.

If the substitute has fundamentally different rep ranges (e.g., swap a 6-10 compound for a 12-15 isolation), the derived score may be harsh. This is an acceptable tradeoff in V1 — the user chose the substitution.

### All three × muscle_scoring

After all three builds:
- `muscle_scoring` calls `classify_exercise(actual_exercise_name(se))` (Sb_03)
- `actual_exercise_name` returns `substituted_name or exercise_name_snapshot`
- This correctly classifies the zone of the exercise that was actually performed

---

## 5. Data Model Summary (Post Sb_03)

### SessionExercise (after all builds)

| Column | Source | Changed by |
|--------|--------|-----------|
| exercise_code_snapshot | Catalogue slot code (E1, E2) | Unchanged |
| exercise_name_snapshot | Catalogue prescribed name | Unchanged |
| success_score | Derived by compute_success_score() | **Sb_01** (was manual) |
| muscle_sensation | User input (optional) | **Sb_01** (was required) |
| substituted_name | User selection (nullable) | **Sb_03** (new column) |
| free_note | User input (optional) | Unchanged |

### SetLog (after all builds)

| Column | Changed by |
|--------|-----------|
| weight_kg, reps, completed | Unchanged |
| execution_quality | **Sb_01** (hidden from form, always NULL for new sessions) |
| reps_target | **Sb_01** (hidden from form, always NULL for new sessions) |

### TemplateExercise (after Sb_03)

| Column | Changed by |
|--------|-----------|
| substitutes_json | **Sb_03** (new column, populated by seed) |

---

## 6. Build Queue

| Sprint | Depends on | Scope | Status |
|--------|-----------|-------|--------|
| **Sb_01** | Sx_01 spec | Derive success_score, hide eq/rt, collapse sensation | **DONE** |
| **Sb_02** | Sb_01, Sx_02 spec | Template `<details>` accordion, compact summary, feedback bottom | **NEXT** |
| **Sb_03** | Sb_02, Sx_03 spec | Migration (2 cols), catalogue substitutes, select UI, muscle_scoring | Pending |
| **Sb_04** | Sb_03 | History + analytics alignment (exercise_history shows actual name, export updated) | Pending |

### Sb_04 scope detail

Sb_04 is a cleanup sprint that ensures all read-side consumers handle substitution correctly:
- `exercise_history.py`: show actual name in history entries
- `export_builder.py`: add `substituted_name` to JSON/CSV
- `scripts/catalog_qa.py`: add substitute classifiability check
- `tests/test_catalog_integrity.py`: add substitute test
- Documentation updates

This is intentionally separated from Sb_03 to keep Sb_03 focused on the core mechanism (migration + UI + muscle_scoring) and Sb_04 on the ripple effects.

---

## 7. UX Input Count Evolution

| Stage | Inputs/exercise (5 work sets) | Total/session (7 exercises) |
|-------|-------------------------------|----------------------------|
| Before Sb_01 | ~27 | ~189 |
| After Sb_01 | ~16 | ~112 |
| After Sb_02 | ~16 (same, but focused view) | ~112 (same, but less scroll) |
| After Sb_03 | ~16 + 1 optional select | ~112 + 7 optional selects |

The substitution select is optional and only appears for exercises with substitutes (~10 out of ~97). It's one tap to ignore (default = prescribed).

---

## 8. Risks Across Specs

| Risk | Specs affected | Mitigation |
|------|---------------|------------|
| Template becomes complex with `<details>` + select + collapsed sensation | Sx_02 + Sx_03 | Build incrementally. Sb_02 first (structure), then Sb_03 (substitution). |
| Derived success_score changes with substitution (different rep_targets) | Sx_01 + Sx_03 | Rep_targets are slot-based (same regardless of substitute). Acceptable. |
| `<details>` browser compatibility | Sx_02 | 97%+ support. Fallback: all expanded (current behavior). |
| Substitution history lost if catalogue reseeds | Sx_03 | `substituted_name` is on SessionExercise (snapshot), not on catalogue. Reseed doesn't affect it. |

---

## 9. Sprint Queue File

For SuperPower tracking:

```yaml
exercise_system_sprints:
  specs:
    - id: Sx_01
      name: exercise_feedback_rationalization_spec
      status: done
      file: docs/strategy/SPIGNOS_EXERCISE_FEEDBACK_RATIONALIZATION.md

    - id: Sx_02
      name: mobile_exercise_entry_ux_spec
      status: done
      file: docs/strategy/SPIGNOS_MOBILE_EXERCISE_ENTRY_UX.md

    - id: Sx_03
      name: exercise_substitution_graph_spec
      status: done
      file: docs/strategy/SPIGNOS_EXERCISE_SUBSTITUTION_GRAPH_SPEC.md

    - id: Sx_04
      name: exercise_system_consolidation_spec
      status: done
      file: docs/strategy/SPIGNOS_EXERCISE_SYSTEM_CONSOLIDATION_SPEC.md

  builds:
    - id: Sb_01
      name: feedback_signal_refactor
      status: done
      depends_on: [Sx_01]
      report: docs/SPRINT_Sb01_REPORT.md

    - id: Sb_02
      name: mobile_session_flow_refactor
      status: next
      depends_on: [Sb_01, Sx_02]

    - id: Sb_03
      name: minimal_substitution_graph_build
      status: pending
      depends_on: [Sb_02, Sx_03]

    - id: Sb_04
      name: history_and_analytics_alignment
      status: pending
      depends_on: [Sb_03]
```

---

## 10. Open Questions (for future sprints)

1. **Should `last_time` eventually compare by actual exercise name?** Currently slot-based. If a user always substitutes E2, the "last time" always shows the prescribed E2, not the actual exercise. A toggle "compare by exercise" could be valuable but adds complexity.

2. **Should the physique dashboard show substitution frequency?** "You substitute E2 Chest Press 40% of the time" could be useful for programme design. Deferred.

3. **When should SPIGNOS get a canonical Exercise entity?** When: (a) users can create custom exercises, or (b) the catalogue exceeds ~200 exercises, or (c) cross-template exercise identity becomes critical (compare "Chest Press" across push-a and short-upper). Not now.
