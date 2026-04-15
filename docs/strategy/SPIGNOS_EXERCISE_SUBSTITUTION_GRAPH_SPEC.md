# SPIGNOS Exercise Substitution Graph Spec

**Sprint:** Sx_03_exercise_substitution_graph_spec
**Date:** 2026-04-14
**Status:** **BUILT (Sb_03)** — Option 1 (JSON-based substitution) en production
**Prerequisites:** Sb_01 (feedback refactor), Sx_02 spec (mobile UX)
**Analyse comparative + refinements strategiques :** voir [SPIGNOS_EXERCISE_SUBSTITUTION_GRAPH_REFINEMENTS.md](SPIGNOS_EXERCISE_SUBSTITUTION_GRAPH_REFINEMENTS.md) (Sx_03.1 — Option 1 vs Option 2, 6 triggers de migration, 3 gaps observables)
**Canonical `Exercise` entity (Option 2) :** DEFERRED — migration conditionnee aux triggers documentes dans Sx_03.1 §5.
**Consolidation transverse :** voir [SPIGNOS_EXERCISE_SYSTEM_CONSOLIDATION_SPEC.md](SPIGNOS_EXERCISE_SYSTEM_CONSOLIDATION_SPEC.md) (Sx_04)

---

## 1. Problem Statement

At the gym, equipment is sometimes occupied. The user wants to swap a prescribed exercise for an equivalent without leaving the session flow. Today there is no substitution mechanism — if the Chest Press machine is taken, the user either waits or logs the prescribed exercise with wrong data.

Additionally, analytics (muscle_scoring, physique dashboard) classify exercises by name. If the user manually logs a different exercise name, the muscle zone classification may be wrong.

## 2. Decision Log

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Substitution model | Static list in JSON catalogue (Option B) | Governed by existing catalog pipeline. ~97 exercises, no need for canonical Exercise entity. Incrementally migrable to DB entity later if needed. |
| Prescribed vs actual tracking | Additive `substituted_name` field, snapshot unchanged (Option C) | Zero breaking change. Existing consumers read `exercise_name_snapshot` (prescribed). New consumers use `actual_exercise_name()` helper. |
| UX trigger | In exercise card, locked after first completed set (Option C) | Natural gym moment. Irreversible once sets are logged for data integrity. |

---

## 3. Data Model Changes

### 3.1 reference_split.json — new field per exercise

```json
{
  "position": 2,
  "code": "E2",
  "name": "Chest Press machine",
  "set_scheme": "3x 8-12",
  "substitutes": ["Développé couché haltères", "Développé incliné haltères 30°"],
  "rep_targets": [...]
}
```

- `substitutes` is optional (absent = no substitutes available)
- List of exercise name strings
- Names don't need to exist as TemplateExercise elsewhere in the catalogue
- Each name must be classifiable by `classify_exercise()` (enforced by QA script)

### 3.2 TemplateExercise — new column

```
substitutes_json   TEXT nullable
```

Stores the JSON-serialized list of substitute names. Populated by the seed from `reference_split.json`. Read by the session detail template to render the select dropdown.

### 3.3 SessionExercise — new column

```
substituted_name   VARCHAR(255) nullable
```

- `NULL` = no substitution, the prescribed exercise was performed
- Non-null = name of the exercise actually performed

### 3.4 Helper function

```python
def actual_exercise_name(se: SessionExercise) -> str:
    """Return the exercise name that was actually performed."""
    return se.substituted_name or se.exercise_name_snapshot
```

---

## 4. Substitution Rules

### Who can substitute
- The user logging the session (owner)

### When
- Only while the exercise has ZERO completed sets
- Once any set is marked `completed=True`, the substitution is locked

### How
- A `<select>` dropdown appears in the exercise card header
- Options: prescribed name (default, value="") + each substitute
- On form submit, `substituted_name` is parsed and stored
- If value is "" or absent → `substituted_name = NULL`

### Lock mechanism
- Template checks: `has_completed_sets = any(sl.completed for sl in work_sets)`
- If `has_completed_sets`: show static badge instead of select
- Router checks: if `substituted_name` is submitted but exercise already has completed sets, ignore the substitution (keep existing value)

### Reverting
- Before any set is complete: select "prescribed" option → clears `substituted_name`
- After sets are complete: cannot revert (locked)

---

## 5. Catalogue: Initial Substitution Lists

Focus on compound machine exercises commonly occupied at the gym:

| Template | Code | Prescribed | Substitutes |
|----------|------|-----------|-------------|
| push-a | E1 | Incline Smith Press | Développé incliné haltères 30° |
| push-a | E2 | Chest Press machine | Développé couché haltères, Dips pectoraux (buste penché) |
| push-a | E4 | Neutral Grip Shoulder Press machine | Machine shoulder press, Développé militaire haltères |
| push-b | E2 | Développé couché haltères | Chest Press machine, Incline Smith Press |
| pull-a | E4 | Rear delt fly machine (pec deck inversé) | Écarté arrière d'épaule câble, Face pull câble |
| pull-b | E1 | Rowing machine chest-supported | Rowing haltère un bras (banc), Rowing câble assis prise neutre |
| legs-a | E1 | Hack Squat machine | Squat Smith machine (pieds avancés), Leg Press (pieds bas, serrés) |
| legs-a | E2 | Leg Press (pieds bas, serrés) | Hack Squat machine, Squat Smith machine (pieds avancés) |
| legs-b | E4 | Hip thrust Smith machine | Hip thrust haltères |

Not every exercise needs substitutes. Cable/isolation exercises are rarely occupied. This list can grow incrementally via catalog updates.

---

## 6. Consumer Impact

### Must change

| Consumer | Change | Reason |
|----------|--------|--------|
| `muscle_scoring.py` line 88 | `classify_exercise(actual_exercise_name(se))` instead of `classify_exercise(se.exercise_name_snapshot)` | Zone classification must reflect the ACTUAL exercise performed |
| `exercise_history.py` | Display `actual_exercise_name(se)` in history entries | User sees what was actually done |
| `export_builder.py` | Add `substituted_name` column to JSON and CSV | Data completeness |
| `session_detail.html` | Add substitution select/badge | UX |
| `routers/sessions.py` | Parse `substituted_name` from form, enforce lock | |
| `seed.py` | Read `substitutes` from JSON, store as `substitutes_json` | |
| `session_builder.py` | No change needed — `substituted_name` defaults to NULL | |

### Unchanged (by design)

| Consumer | Why unchanged |
|----------|---------------|
| `stats.py` / `last_time_by_exercise_code()` | Compares by SLOT (template_slug + exercise_code), not by exercise name. "Last time you did E2" is the right question regardless of substitution. |
| `delta.py` | Compares first sets of the same slot. Substitution doesn't affect slot identity. |
| `progression_hint.py` | Uses weight/reps from prior slot, not exercise name. |
| `kpis.py` | Aggregates success_score by template, not by exercise name. |
| `quality_score.py` | Uses success_score (derived from sets), not exercise name. |
| `feedback.py` | Uses set data vs rep_targets, not exercise name. |

### Design rationale: slot-based vs exercise-based analytics

**Slot-based** (last_time, delta, progression_hint): "How did I do on E2 of Push A last time?" — this is the programme perspective. Substitution doesn't change the slot.

**Exercise-based** (muscle_scoring, physique dashboard): "Which muscle zones did I work?" — this must reflect the actual exercise. If I did Cable Fly instead of Chest Press, the zone is still pecs but the secondary zones may differ.

Both perspectives are valuable. The additive `substituted_name` field supports both without breaking either.

---

## 7. Migration

**Single Alembic migration:**
1. Add `substitutes_json` (TEXT, nullable) to `template_exercises`
2. Add `substituted_name` (VARCHAR 255, nullable) to `session_exercises`

**Catalogue update:**
- Add `substitutes` field to ~10 exercises in `reference_split.json`
- Bump version → reseed populates `substitutes_json`

**QA script update:**
- Add check: every substitute name must be classifiable by `classify_exercise()`
- Warning (not error) if a substitute name doesn't match any pattern

---

## 8. Files Impacted

| File | Change |
|------|--------|
| `data/reference_split.json` | Add `substitutes` to ~10 exercises, bump version |
| `app/models/catalog.py` | Add `substitutes_json` (TEXT nullable) to TemplateExercise |
| `app/models/session.py` | Add `substituted_name` (VARCHAR 255 nullable) to SessionExercise |
| `app/services/seed.py` | Read `substitutes` from JSON, serialize to `substitutes_json` |
| `app/services/substitution.py` | **New** — `actual_exercise_name()`, `get_substitutes()`, `can_substitute()` |
| `app/routers/sessions.py` | Parse `substituted_name`, enforce lock rule |
| `app/templates/session_detail.html` | Add select dropdown / static badge |
| `app/services/muscle_scoring.py` | Use `actual_exercise_name()` for classify |
| `app/services/exercise_history.py` | Display actual name |
| `app/services/export_builder.py` | Add `substituted_name` to export |
| `scripts/catalog_qa.py` | Add substitute classifiability check |
| `tests/test_catalog_integrity.py` | Add substitute classifiability test |
| `migrations/versions/...` | 1 migration (2 columns) |
| `tests/test_substitution.py` | **New** — service tests |
| `tests/test_substitution_routes.py` | **New** — route/UX tests |

---

## 9. Acceptance Criteria — Spec

- [x] Substitution model defined (JSON catalogue, not DB entity)
- [x] Prescribed vs actual tracking defined (additive field)
- [x] Lock mechanism defined (after first completed set)
- [x] Consumer impact audited per-file
- [x] Slot-based vs exercise-based analytics distinction documented
- [x] Initial substitution lists provided
- [x] Migration strategy defined (2 columns, no data migration)

## 10. Acceptance Criteria — Build (Sb_03)

- [ ] `substitutes` field parsed from catalogue JSON and stored in TemplateExercise
- [ ] `substituted_name` column exists on SessionExercise
- [ ] Select dropdown appears for exercises with substitutes (before first set)
- [ ] Dropdown locked after first completed set
- [ ] `actual_exercise_name()` helper works correctly
- [ ] muscle_scoring uses actual exercise name for zone classification
- [ ] Exercise history displays actual name
- [ ] Export includes substituted_name
- [ ] QA script validates substitute classifiability
- [ ] All existing tests pass
- [ ] New tests cover substitution flow

---

## 11. Risks

| Risk | Mitigation |
|------|------------|
| Substitute name typo in JSON → unclassifiable | QA script check + catalog integrity test |
| User substitutes then muscle zone changes | By design — the physique dashboard should reflect actual work |
| Delta compares different exercises under same slot code | By design — slot-based progression is programme-level, not exercise-level |
| Substitution list grows unwieldy | Keep it short (2-3 per exercise max). Governed by catalogue version control. |

---

## 12. DO NOT BUILD

- Canonical `Exercise` entity in DB (deferred — Option C from design discussion)
- User-created custom exercises
- Bidirectional substitution graph (A→B implies B→A) in DB
- Substitution history / analytics ("how often do users substitute E2?")
- Substitution across templates ("use Pull A's E1 in Push A")
