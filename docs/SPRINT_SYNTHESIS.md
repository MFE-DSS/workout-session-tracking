# SPIGNOS — Sprint Synthesis for Prompt Engineer Handoff

**Date:** 2026-04-14
**Branch:** `claude/sprint-reporting-fitness-app-V7Qr6`
**Tests:** 478 passed, 0 failed
**Commits:** 42 commits across 13 sprints (7 builds + 4 specs + 2 polish)

---

## Stack & Architecture (unchanged)

FastAPI SSR + Jinja2 + SQLite + Alembic + Nginx/systemd.
Mobile-first, no SPA, no JS framework, minimal vanilla JS.
Private by default, deterministic scoring, no AI/ML.

---

## What Was Delivered

### Foundation Sprints (S0-S2): Single-User Body Engineering

| Sprint | What | Key Deliverables |
|--------|------|-----------------|
| **S0** — Catalog Integrity | Stabilize exercise catalogue as analytics foundation | QA script (7 checks), 10 CI-blocking tests, governance doc, 5 focus corrections, version v6 |
| **S1** — Body Metrics + Readiness | First body engineering data layer | Lateralized measurements (arm/thigh L/R + hip + neck), readiness lite (5 dimensions 1-5), Home widget, `/readiness/history` |
| **S2** — Body Engineering Dashboard | Unified synthesis across 3 data streams | `/dashboard` with 5-axis scoring (consistency, progression, body trend, recovery, balance), per-axis confidence, graceful degradation |

### Social Sprints (S3-S4): Private Squads & Engagement

| Sprint | What | Key Deliverables |
|--------|------|-----------------|
| **S3** — Private Squads | First social layer | Squad CRUD, invite codes (SPGN-XXXX, 48h expiry), scoped leaderboard, strict privacy model (training activity visible, body/readiness never) |
| **S4** — Challenges, Compare, Sharing | Engagement loops | Time-boxed challenges (4 metrics: sessions/score/tonnage/streak), 1:1 compare mode, template recommendations, anonymized session sharing |

### Exercise System Sprints (Sx/Sb): Signal + UX + Substitution

| Sprint | Type | What | Key Deliverables |
|--------|------|------|-----------------|
| **Sx_01** | Spec | Feedback rationalization | Audit of all feedback fields, decision: success_score derived, eq/rt hidden, sensation optional |
| **Sb_01** | Build | Feedback signal refactor | `compute_success_score()` (snap to {100,80,50}), -41% inputs per exercise (27→16) |
| **Sx_02** | Spec | Mobile exercise entry UX | `<details>` accordion design, compact summary, feedback at bottom |
| **Sb_02** | Build | Mobile session flow | Exercise cards in `<details>`, server-side `?active=` routing, zero JS |
| **Sx_03** | Spec | Exercise substitution graph | JSON catalogue substitutes, additive `substituted_name` field, lock after first set |
| **Sb_03** | Build | Substitution graph | Migration, catalogue v7 (10 exercises with substitutes), select UI, `actual_exercise_name()` for muscle_scoring |
| **Sx_04** | Spec | Exercise system consolidation | Cross-spec alignment, build queue, dependency analysis |

### UX Polish

| Fix | Change |
|-----|--------|
| Substitution UI | Segmented radios (design system) instead of dropdown, collapsed in `<details>` |
| Warmup logic | 2 warmup sets for first exercise only, 1 for the rest |
| History layout | Proper card spacing, no visual overlap |
| Physique grid | Zone cards in responsive 2-column grid instead of vertical stack |
| Feedback labels | French with micro-descriptions ("Focalisé/Correct/Distrait", "En forme/Moyen/Fatigué") |

---

## Current Product State

### Pages

| Route | Function |
|-------|----------|
| `/` | Home — readiness widget, behavioral state, KPIs, sparkline |
| `/dashboard` | Body Engineering — 5-axis synthesis, global score, confidence |
| `/physique` | Physique — radar SVG, 11 zone cards (responsive grid) |
| `/library` | Catalogue — templates grouped by section |
| `/library/{slug}` | Template detail — start session |
| `/sessions/{id}` | Session — `<details>` accordion, substitution, derived scoring |
| `/history` | Session history — clean cards, status filters |
| `/progress` | Progression — KPIs, timelines |
| `/readiness/history` | Readiness — 90-day history |
| `/profile` | Profile — lateralized measurements, protocol tips |
| `/squads` | Squad list — create, join |
| `/squads/{id}` | Squad detail — leaderboard, challenges, activity, compare, share |
| `/squads/{id}/challenges` | Challenge list |
| `/squads/{id}/challenges/{cid}` | Challenge standings |
| `/squads/{id}/compare` | 1:1 member comparison |
| `/leaderboard` | Global leaderboard |
| `/export` | Backup — JSON + CSV |

### Data Model (post all migrations)

| Table | Added by |
|-------|----------|
| `workout_sessions` | V1 |
| `session_exercises` | V1 (+`substituted_name` by Sb_03) |
| `set_logs` | V1 |
| `workout_templates` | V1 (+`catalog_section`, `display_order`) |
| `template_exercises` | V1 (+`substitutes_json` by Sb_03) |
| `rep_targets` | V1 |
| `users` | V1 |
| `body_measurements` | S1 (lateralized: arm_cm_left/right, thigh_cm_left/right, hip_cm, neck_cm) |
| `readiness_entries` | S1 (5 dimensions 1-5, recorded_on DATE, unique per user/day) |
| `squads` | S3 |
| `squad_memberships` | S3 |
| `squad_invite_codes` | S3 |
| `squad_challenges` | S4 |
| `squad_template_recommendations` | S4 |
| `squad_shared_sessions` | S4 |

### Key Architectural Patterns

- **Snapshot resilience**: sessions snapshot template/exercise names at creation. Catalogue can reseed without breaking history.
- **Derived success_score**: computed from set data vs rep_targets, snapped to {100,80,50}. Zero read-side changes — all consumers read the same column.
- **Privacy model**: squads share training activity (score, sessions, streak, templates). Never: body measurements, readiness, weights/reps, notes.
- **Graceful degradation**: dashboard axes activate as data becomes available. Insufficient data = greyed out with guidance, not zero.
- **Focus = editorial, mapping = analytical**: catalogue `focus` field is for UI. `classify_exercise()` is the analytical truth for zone scoring.

---

## Documentation Produced

### Specs (in `docs/strategy/`)

| File | Purpose |
|------|---------|
| `SPIGNOS_CATALOG_GOVERNANCE.md` | Source of truth, versioning, modification workflow |
| `SPIGNOS_CATALOG_QA_REPORT.md` | Generated QA report (PASS) |
| `SPIGNOS_BODY_METRICS_READINESS_SPEC.md` | Body metrics + readiness spec |
| `SPIGNOS_SCORING_RULES_V1.md` | Dashboard scoring formulas |
| `SPIGNOS_BODY_ENGINEERING_DASHBOARD_V1.md` | Dashboard feature spec |
| `SPIGNOS_SQUADS_SPEC.md` | Squads feature spec |
| `SPIGNOS_SQUADS_PRIVACY_MODEL.md` | Privacy enforcement rules |
| `SPIGNOS_EXERCISE_FEEDBACK_RATIONALIZATION.md` | Feedback field audit + decisions |
| `SPIGNOS_MOBILE_EXERCISE_ENTRY_UX.md` | Mobile UX spec |
| `SPIGNOS_EXERCISE_SUBSTITUTION_GRAPH_SPEC.md` | Substitution spec |
| `SPIGNOS_EXERCISE_SYSTEM_CONSOLIDATION_SPEC.md` | Cross-spec alignment |
| `SPIGNOS_EXERCISE_SYSTEM_ROADMAP.md` | Exercise system roadmap |
| `SPIGNOS_SUPERPOWER_SPRINT_QUEUE.md` | Sprint tracking |

### Sprint Reports (in `docs/`)

S0, S1, S2, S3, S4, Sb_01, Sb_02, Sb_03 — each with deliverables, verification commands, files modified, gaps.

---

## Remaining Build Queue

| Sprint | Status | Scope |
|--------|--------|-------|
| **Sb_04** — History & Analytics Alignment | Pending | exercise_history shows actual name, export includes substituted_name, QA validates substitutes |
| **S5** — Photo Pipeline | Deferred | Progress photos, capture protocol, storage abstraction (experimental branch) |
| **S6** — Image Anthropometry | Deferred | Experimental estimation provider, feature flag, stub/mock (experimental branch) |

---

## Constraints to Maintain

1. **No SPA** — SSR only, no JS framework
2. **No public data** — squads are private, no feed, no global rankings beyond leaderboard
3. **No AI/ML claims** — deterministic scoring, documented formulas
4. **No body data in social** — measurements, readiness, weights/reps never exposed to squad members
5. **No photo as source of truth** — photos are supplementary, manual measurements are canonical
6. **Snapshot resilience** — catalogue can reseed without breaking session history
7. **Mobile-first** — one hand, gym context, minimal inputs

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Tests | 478 passing |
| Commits | 42 |
| New tables | 9 (across S1-S4) |
| New services | 12 |
| New templates | 15 |
| Specs written | 13 |
| Sprint reports | 8 |
| Inputs/exercise | 27 → 16 (-41%) |
| Pages | 17 routes |
