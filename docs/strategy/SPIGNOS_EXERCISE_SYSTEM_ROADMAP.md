# SPIGNOS Exercise System Roadmap

**Date:** 2026-04-14

## Current State

SPIGNOS has a functional session logging flow with:
- Per-exercise card forms with weight/reps/checkbox inputs
- Derived success_score from set data (Sb_01 complete)
- Jump bar navigation between exercises
- Delta and progression hints from prior sessions
- Exercise-to-zone classification (muscle_mapping)

## Roadmap

### Phase 1: Signal Cleanup (DONE)
**Sb_01 — Feedback Signal Refactor**
- success_score derived automatically from set data
- execution_quality / reps_target hidden from default form
- muscle_sensation made optional
- Inputs reduced from ~27 to ~16 per exercise

### Phase 2: Mobile UX (NEXT)
**Sb_02 — Mobile Session Flow Refactor**
- `<details>` accordion: one exercise active at a time
- Compact summary for collapsed cards (code + name + progress + set resume)
- Session feedback moved to bottom (natural gym flow)
- Zero JS, server-side `open` attribute

### Phase 3: Substitution (PENDING)
**Sb_03 — Minimal Substitution Graph**
- Substitution lists in JSON catalogue
- `substituted_name` field on SessionExercise
- Select dropdown in exercise card (locked after first set)
- muscle_scoring uses actual exercise name

### Phase 4: Analytics Alignment (PENDING)
**Sb_04 — History & Analytics Alignment**
- Exercise history shows actual name (not just prescribed)
- Export includes substituted_name
- QA script validates substitute classifiability
- Documentation updates

### Future (not planned)
- Canonical Exercise entity in DB
- User-created custom exercises
- Cross-template exercise comparison
- Substitution frequency analytics
- Per-exercise RPE tracking
