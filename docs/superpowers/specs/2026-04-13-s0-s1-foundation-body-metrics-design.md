# S0+S1 Design Spec — Foundation Freeze & Body Metrics Readiness

**Date:** 2026-04-13
**Sprints:** S0_foundation_freeze_catalog_integrity + S1_body_metrics_readiness_lite
**Status:** Approved

---

## Context

SPIGNOS is a private, mobile-first workout tracking app (FastAPI SSR + Jinja2 + SQLite + Alembic).
The physique dashboard, muscle scoring, and body measurements were recently added (Apr 8-13).
Before building more analytics (S2+), we need to:

1. **S0** — Stabilize the exercise catalog as a reliable foundation for analytics
2. **S1** — Add lateralized body metrics + daily readiness tracking

These two sprints form a single **design** unit because S1's migration depends on S0's catalog being clean.
However, they are **separate delivery units**: two merges, two sprint reports, independent rollback possible on S1 without reopening S0.

## Decisions Log

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Body measurement lateralization | Option B — full migration to left/right + hip/neck | Clean foundation now, avoid tech debt later |
| Readiness scale | 1-5 integers, 5=best always | Matches existing segmented controls, good granularity for trend detection |
| UX placement | Readiness widget on Home, body metrics in Profile (S1) | Readiness = daily ritual (Home), metrics = weekly measurement (Profile for now) |
| Execution order | Sequential: S0 fully complete before S1 starts | Stable catalog before touching data models |
| Delivery separation | Two independent merges, two sprint reports | Rollback S1 without reopening S0 catalog work |
| Focus field role | Editorial/UI only, NOT analytical truth | Analytics uses exercise→zone mapping, not focus text |
| Lateralized measurements | left/right = source of truth, avg = derived view only | Preserves raw data for future asymmetry/correlation work (S2+) |
| Readiness date model | `recorded_on` DATE + UNIQUE(user_id, recorded_on) | Avoids timezone/midnight ambiguity vs extracting date from datetime |
| Body metrics UX roadmap | Profile is S1 compromise; dedicated `/body` route planned post-S1 | Profile works for MVP, but body metrics deserve their own progression space |

---

## S0 — Catalog Integrity

### S0.1 — Automated Catalog QA Script

**File:** `scripts/catalog_qa.py`

Reads `data/reference_split.json` and produces a structured report. Checks:

1. **Schema validation** — every template has: slug, name, kind, focus, catalog_section, display_order, >=1 exercise. Every exercise has: position, code, name, set_scheme, >=1 rep_target.
2. **Code uniqueness per template** — no duplicate E-codes within a single template.
3. **Position sequentiality** — positions form 1, 2, 3... with no gaps.
4. **Rep target coherence** — min_reps <= max_reps, technique in {null, "RP", "DS"}.
5. **Focus vs actual exercises** — each muscle zone mentioned in `focus` should have at least 1 exercise classifiable to that zone via `muscle_mapping.classify_exercise()`. This is a **warning**, not a hard error — focus is editorial, mapping is analytical. The check ensures they don't drift too far apart.
6. **Exercise classifiability** — flag any exercise returning `("unknown", [])` from the classifier. This IS a hard error — every loggable exercise must be classifiable for analytics.
7. **Slug uniqueness** — no duplicate slugs across all templates.

**Output:** JSON report + human-readable markdown at `docs/strategy/SPIGNOS_CATALOG_QA_REPORT.md`.

### S0.2 — Catalog Corrections

#### Corrections to apply in `reference_split.json`:

1. **`liss-abs` focus** — change from "Cardio bas regime + Core" to "Core / Abdos" (the loggable exercises are all core; cardio is captured in `cardio_note` only).

2. **Add ", Core" to legs template focus fields:**
   - `legs-a`: "Quadriceps, Adducteurs, Mollets, Core" (has E7 Roulette abdominale)
   - `legs-b`: "Ischio-jambiers, Fessiers, Mollets, Core" (has E7 Crunch cable)
   - `lower-quad-bias`: "Quadriceps, Mollets, Core" (has E6 Roulette abdominale)
   - `lower-posterior-bias`: "Ischio-jambiers, Fessiers, Mollets, Core" (has E6 Crunch cable)

3. **Bump version** to `2026-04-13.v6` after corrections.

#### Corrections to `app/services/muscle_mapping.py`:

4. **Verify all 95+ exercises** in the catalog are classifiable. Add any missing patterns.

#### Documented anomalies (intentional, not corrected):

5. **pull-a has no direct biceps isolation** — by design (width focus). Vertical pulls contribute biceps as secondary zone. Documented in governance doc.

6. **push-a E6 "Ecarte arriere d'epaule cable"** is a pull-pattern movement in a push template — common PPL practice for complete shoulder coverage on push day. Documented.

7. **Archived templates overlap with core templates** — by design (pre-PPL-split legacy). Retained for users who started sessions with them. Documented.

### S0.3 — Catalog Governance Document

**File:** `docs/strategy/SPIGNOS_CATALOG_GOVERNANCE.md`

Contents:
- **Source of truth:** `data/reference_split.json` is the single source of truth for the exercise catalog
- **Versioning convention:** `YYYY-MM-DD.vN` — bump on every change
- **Modification workflow:** edit JSON -> bump version -> run `scripts/catalog_qa.py` -> verify report clean -> commit -> seed will auto-update on next deploy
- **Seed mechanism:** `app/services/seed.py` is idempotent, keyed on version string. New version = full re-seed of catalog tables
- **Focus field role:** the `focus` field is **editorial** — it serves the UI (library display, template cards) and human readability. It is NOT the analytical truth. The analytical truth is `muscle_mapping.classify_exercise()` which maps exercise names to muscle zones. The focus field and the mapping should be directionally aligned, but the mapping is what drives scores, dashboards, and analytics. Do not encode scoring logic into the focus text.
- **Analytics impact policy:** scoring uses exercise names captured at session creation time (immutable snapshots in `session_exercises.name_snapshot`). Changing catalog focus/mapping affects future scores only, never historical data
- **Known structural decisions:** documents the 3 intentional anomalies listed above

### S0.4 — Catalog Integrity Tests

**File:** `tests/test_catalog_integrity.py`

Runs the same checks as the QA script but as pytest assertions:
- Schema validation
- Code uniqueness per template
- Position sequentiality
- Rep target coherence
- Focus-exercise alignment
- Exercise classifiability (zero unknowns)
- Slug uniqueness

These tests run in CI and block merges on catalog regressions.

### S0 Artifacts

| Artifact | Path |
|----------|------|
| QA script | `scripts/catalog_qa.py` |
| QA report | `docs/strategy/SPIGNOS_CATALOG_QA_REPORT.md` |
| Governance doc | `docs/strategy/SPIGNOS_CATALOG_GOVERNANCE.md` |
| Integrity tests | `tests/test_catalog_integrity.py` |
| Sprint report | `docs/SPRINT_S0_REPORT.md` |

### S0 Files Modified

| File | Action |
|------|--------|
| `data/reference_split.json` | Modify (focus corrections, version bump) |
| `app/services/muscle_mapping.py` | Modify (add missing patterns if any) |
| `scripts/catalog_qa.py` | **New** |
| `tests/test_catalog_integrity.py` | **New** |
| `docs/strategy/SPIGNOS_CATALOG_GOVERNANCE.md` | **New** |
| `docs/strategy/SPIGNOS_CATALOG_QA_REPORT.md` | **New** (generated) |
| `docs/SPRINT_S0_REPORT.md` | **New** |

### S0 Risks

| Risk | Mitigation |
|------|------------|
| Focus changes affect existing physique dashboard scores | Scores use exercise names (immutable snapshots), not template focus. Only the focus→zone mapping for analytics label display changes. |
| Seed re-runs on version bump | Seed is idempotent and uses ON DELETE SET NULL for session FKs. Existing sessions are unaffected. |

### S0 Acceptance Criteria

- [ ] All templates remain available in the UI
- [ ] QA script runs clean (zero errors)
- [ ] All exercises in catalog are classifiable (zero unknowns)
- [ ] Focus fields accurately reflect loggable exercises
- [ ] Governance doc explains source of truth, versioning, and modification rules
- [ ] Tests pass
- [ ] No existing behavior is broken

---

## S1 — Body Metrics + Readiness Lite

### S1.1 — Migration: Body Measurements v2

**Single Alembic migration** that:

1. **Adds new columns:**
   - `arm_cm_left` (Float, nullable)
   - `arm_cm_right` (Float, nullable)
   - `thigh_cm_left` (Float, nullable)
   - `thigh_cm_right` (Float, nullable)
   - `hip_cm` (Float, nullable)
   - `neck_cm` (Float, nullable)

2. **Migrates data:**
   - Copy `arm_cm` -> `arm_cm_left` AND `arm_cm_right`
   - Copy `thigh_cm` -> `thigh_cm_left` AND `thigh_cm_right`

3. **Drops old columns:**
   - `arm_cm`
   - `thigh_cm`

4. **Creates new table `readiness_entries`** (see S1.2)

SQLite requires `batch_alter_table` for column operations (consistent with existing migrations).

### S1.2 — New Model: ReadinessEntry

**File:** `app/models/readiness.py`

```
readiness_entries
├── id                INTEGER PK
├── user_id           INTEGER FK -> users.id (CASCADE)
├── recorded_on       DATE NOT NULL        -- calendar day, no timezone ambiguity
├── sleep_quality     INTEGER NOT NULL      -- 1-5, 5=excellent
├── fatigue_level     INTEGER NOT NULL      -- 1-5, 5=very fresh
├── soreness_level    INTEGER NOT NULL      -- 1-5, 5=no soreness
├── stress_level      INTEGER NOT NULL      -- 1-5, 5=very relaxed
├── motivation_level  INTEGER NOT NULL      -- 1-5, 5=very motivated
├── resting_hr        INTEGER nullable
├── note              TEXT nullable
├── created_at        DATETIME(tz) server_default=now()
├── UNIQUE(user_id, recorded_on)            -- one entry per user per day, DB-enforced
└── INDEX(user_id, recorded_on)
```

**Scale semantics (uniform: 5 = always best):**

| Value | sleep_quality | fatigue_level | soreness_level | stress_level | motivation_level |
|-------|---------------|---------------|----------------|--------------|-----------------|
| 1 | Tres mauvais | Epuise | Tres douloureux | Tres stresse | Aucune |
| 2 | Mauvais | Fatigue | Douloureux | Stresse | Faible |
| 3 | Correct | Normal | Modere | Moyen | Normale |
| 4 | Bon | En forme | Leger | Detendu | Bonne |
| 5 | Excellent | Tres frais | Aucune douleur | Tres detendu | Tres motive |

**Constraint:** one entry per user per calendar day, enforced by UNIQUE(user_id, recorded_on) at the DB level. Uses DATE type (not DATETIME) to eliminate timezone/midnight-crossing ambiguity. Upsert semantics on INSERT OR REPLACE.

### S1.3 — Updated Model: BodyMeasurement

**File:** `app/models/measurement.py` (modified)

Final schema:
```
body_measurements
├── id              INTEGER PK
├── user_id         INTEGER FK -> users.id (CASCADE)
├── measured_at     DATETIME(tz) NOT NULL
├── weight_kg       Float nullable
├── chest_cm        Float nullable
├── arm_cm_left     Float nullable   -- was: arm_cm
├── arm_cm_right    Float nullable   -- was: arm_cm
├── waist_cm        Float nullable
├── thigh_cm_left   Float nullable   -- was: thigh_cm
├── thigh_cm_right  Float nullable   -- was: thigh_cm
├── hip_cm          Float nullable   -- NEW
├── neck_cm         Float nullable   -- NEW
├── calf_cm         Float nullable
├── created_at      DATETIME(tz) server_default=now()
└── INDEX(user_id, measured_at)
```

### S1.4 — Physique Dashboard Adaptation

**`app/services/muscle_mapping.py`** — ZONE_MEASUREMENT updated:

| Zone | Before | After |
|------|--------|-------|
| pecs | `chest_cm` | `chest_cm` (unchanged) |
| biceps | `arm_cm` | computed via `compute_zone_measurement()` |
| triceps | `arm_cm` | computed via `compute_zone_measurement()` |
| quads | `thigh_cm` | computed via `compute_zone_measurement()` |
| posterior | `thigh_cm` | computed via `compute_zone_measurement()` |
| core | `waist_cm` | `waist_cm` (unchanged) |

**Source of truth doctrine:** `arm_cm_left`, `arm_cm_right`, `thigh_cm_left`, `thigh_cm_right` are the **source of truth**. The averaged values used by the physique dashboard are **derived views** for backward compatibility only. All future features (asymmetry detection in S2+, photo/measurement correlation in S5+) must work from the raw lateralized columns, never from the averages.

**Implementation approach:** ZONE_MEASUREMENT values change from direct column names to zone keys. A new function `compute_zone_measurement(measurement, zone)` in `app/services/measurements.py` handles the resolution:
- For zones mapped to a single column (pecs->chest_cm, core->waist_cm): return that column's value directly
- For zones mapped to lateralized columns (biceps/triceps->arm, quads/posterior->thigh): compute average of left/right if both present, return single side if only one, None if neither

**`app/services/measurements.py`** — new helpers:
- `compute_arm_avg(m: BodyMeasurement) -> float | None` — average of left/right if both present, single side if only one, None if neither
- `compute_thigh_avg(m: BodyMeasurement) -> float | None` — same logic
- `compute_zone_measurement(m: BodyMeasurement, zone: str) -> float | None` — dispatches to the right column or avg helper based on zone

**`app/services/muscle_scoring.py`** — calls `compute_zone_measurement()` instead of `getattr(measurement, field_name)`.

### S1.5 — Routes & Templates

#### Readiness Widget on Home (`GET /`)

Added to `app/routers/pages.py` home route:
- Query today's readiness entry for current user
- Pass to template: `readiness_today` (entry or None), `readiness_labels` (scale labels dict)

**Template `app/templates/index.html`** — new section at top:
- **If no entry today:** compact inline form with 5 segmented controls (reuse `_macros.html` segmented_control pattern) + optional resting_hr number input + optional note textarea + submit button
- **If entry exists:** summary card showing 5 values as colored badges + resting_hr if present + "Modifier" link
- Visual style: consistent with existing KPI cards (dark theme, mobile-first)
- **Hard constraint:** the readiness widget must stay compact and never push the session action (open session tile / start workout) below the fold on mobile. The Home page's primary job remains "start or resume a workout". Readiness is secondary. The widget should be collapsible or very short (single row of badges when filled).

#### Readiness POST (`POST /readiness`)

**New file:** `app/routers/readiness.py`
- Validates: all 5 fields required, each 1-5
- Validates: resting_hr optional, if present must be 30-200
- Upserts entry for today (recorded_on = date.today(), DB UNIQUE constraint handles conflict)
- Redirects to `/` on success

#### Readiness History (`GET /readiness/history`)

**New file:** `app/templates/readiness_history.html`
- Chronological list of entries (most recent first)
- Each entry: date, 5 values as colored badges, resting_hr, note
- Optional: 30-day sparkline trend per dimension (reuse `timeline.py` SVG pattern)
- Accessible via link from Home readiness widget (no new nav entry — per Option C decision)

#### Body Metrics in Profile (`GET /profile`)

**Modified template `app/templates/profile.html`:**
- Measurement form updated: `arm_cm` field replaced by `arm_cm_left` + `arm_cm_right` side by side
- Same for `thigh_cm` -> `thigh_cm_left` + `thigh_cm_right`
- New fields: `hip_cm`, `neck_cm`
- Visual grouping: "Bras gauche / Bras droit" on same row (responsive: stack on very small screens)

**UX roadmap note:** Profile is the S1 compromise for body metrics. Post-S1, body metrics deserve a dedicated `/body` route with its own progression space (trend charts, measurement history, protocol tips). This is consistent with how Hevy and MacroFactor treat body measurements as a first-class feature, not a profile sub-form.

**Modified `app/routers/pages.py`** profile route:
- Handle new field names in form parsing
- Pass updated fields to template

### S1.6 — Services

#### New: `app/services/readiness.py`

- `save_readiness(db, user_id, data: dict) -> ReadinessEntry` — upsert by UNIQUE(user_id, recorded_on). Uses `date.today()` for recorded_on.
- `get_today_readiness(db, user_id) -> ReadinessEntry | None` — queries by recorded_on = date.today()
- `get_readiness_history(db, user_id, days: int = 30) -> list[ReadinessEntry]` — ordered by recorded_on DESC

#### Modified: `app/services/measurements.py`

- Update `upsert_measurement()` for new fields (arm_cm_left/right, thigh_cm_left/right, hip_cm, neck_cm)
- Add `compute_arm_avg()`, `compute_thigh_avg()` helpers
- Update form field validation for lateralized inputs

### S1.7 — Tests

| Test File | What's Tested |
|-----------|---------------|
| `tests/test_readiness.py` | **New.** Model creation, scale validation (reject 0, 6), upsert per day, history query |
| `tests/test_readiness_routes.py` | **New.** POST validation, widget rendering on Home (no entry vs existing), history page, auth required |
| `tests/test_measurements.py` | **Modified.** Lateralized fields, hip/neck, avg computation helpers |
| `tests/test_profile_measurements.py` | **Modified.** New form fields in profile |
| `tests/test_muscle_scoring.py` | **Modified.** arm_cm_avg / thigh_cm_avg integration |
| `tests/test_physique_dashboard.py` | **Modified.** Dashboard still works with lateralized measurements |

### S1 Artifacts

| Artifact | Path |
|----------|------|
| Migration | `migrations/versions/YYYYMMDD_body_measurements_v2_readiness.py` |
| Readiness model | `app/models/readiness.py` |
| Readiness service | `app/services/readiness.py` |
| Readiness router | `app/routers/readiness.py` |
| Readiness history template | `app/templates/readiness_history.html` |
| Spec doc | `docs/strategy/SPIGNOS_BODY_METRICS_READINESS_SPEC.md` |
| Sprint report | `docs/SPRINT_S1_REPORT.md` |

### S1 Files Modified (exhaustive)

| File | Action |
|------|--------|
| `app/models/measurement.py` | Modify (lateralize + hip/neck) |
| `app/models/readiness.py` | **New** |
| `app/models/__init__.py` | Modify (import ReadinessEntry) |
| `app/services/measurements.py` | Modify (avg helpers, new fields) |
| `app/services/readiness.py` | **New** |
| `app/services/muscle_mapping.py` | Modify (ZONE_MEASUREMENT keys) |
| `app/services/muscle_scoring.py` | Modify (use avg helpers) |
| `app/routers/pages.py` | Modify (Home readiness widget, readiness history route) |
| `app/routers/readiness.py` | **New** |
| `app/templates/index.html` | Modify (readiness widget) |
| `app/templates/readiness_history.html` | **New** |
| `app/templates/profile.html` | Modify (lateralized + hip/neck) |
| `migrations/versions/...` | **New** |
| `tests/test_readiness.py` | **New** |
| `tests/test_readiness_routes.py` | **New** |
| `tests/test_measurements.py` | Modify |
| `tests/test_profile_measurements.py` | Modify |
| `tests/test_muscle_scoring.py` | Modify |
| `docs/strategy/SPIGNOS_BODY_METRICS_READINESS_SPEC.md` | **New** |
| `docs/SPRINT_S1_REPORT.md` | **New** |

### S1.8 — Measurement Protocol (UI help text)

A brief in-app guidance (tooltip or help section in Profile measurement form) covering:
- **When:** same time of day (morning, fasted preferred), same conditions
- **Frequency:** weekly at most for circumference, daily OK for weight
- **How:** relaxed muscle, tape flat against skin, same landmarks each time
- **Partial entries are OK:** missing fields don't generate false signals — better to skip than guess
- **Lateralized:** measure both sides even if similar; differences become useful in S2+

This is NOT a full protocol document — it's 5-6 lines of help text in the measurement form. A more detailed protocol doc (`docs/strategy/SPIGNOS_MEASUREMENT_PROTOCOL.md`) can follow in S2 if needed.

### S1.9 — Signal Confidence Policy (foundational rules)

Even though S1 does not compute composite scores, these rules must be established now to prevent garbage analytics in S2:
- **No trend displayed** for a dimension with fewer than 3 data points
- **No muscle zone score** if fewer than 2 relevant sessions in the scoring window
- **No readiness trend** if fewer than 5 entries in the last 30 days
- **Partial measurement entries** degrade gracefully: zones without measurement data fall back to training-only scoring (already handled by muscle_scoring.py's weight split: 60% performance + 40% exposure when no anthropometry)

These rules are documented in the spec and enforced in the service layer. They don't need UI yet — just backend guards that return None/insufficient instead of a misleading number.

### S1 Risks

| Risk | Mitigation |
|------|------------|
| SQLite column rename requires table rebuild | Use `batch_alter_table` (proven pattern in existing migrations) |
| Physique dashboard breaks during migration | Single migration handles both schema change and data copy. Tests verify dashboard still renders. |
| Readiness upsert race condition | One entry per user per day enforced at service level. SQLite serializes writes anyway. |
| Profile form gets too long on mobile | Group lateralized fields side-by-side. All fields remain nullable (partial entry). |

### S1 Acceptance Criteria

- [ ] User can enter and review lateralized body measurements (left/right arms, thighs)
- [ ] User can enter hip_cm and neck_cm
- [ ] User can fill in daily readiness (5 dimensions + optional HR + note) from Home page
- [ ] User can review readiness history
- [ ] Physique dashboard works correctly with averaged lateralized measurements
- [ ] Existing session flow is completely unaffected
- [ ] All data is properly historized
- [ ] All tests pass (existing + new)
- [ ] No existing routes or behaviors are broken

---

## PLANNED POST-S1 (near-term, not in scope)

- Dedicated `/body` route with measurement trends and progression charts
- Detailed measurement protocol document (`docs/strategy/SPIGNOS_MEASUREMENT_PROTOCOL.md`)
- Readiness → session correlation (does readiness predict session quality?)

## DO NOT BUILD (deferred to S2+)

- Composite readiness score (S2)
- Asymmetry detection/alerting from left/right differences (S2+)
- Any AI/ML on readiness data
- Photo-based morphology (S5+)
- Social features (S3+)
- Body fat estimation from measurements (neck/waist/hip formulas exist but are too imprecise to ship without proper confidence framing)
