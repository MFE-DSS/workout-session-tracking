# Sprint S1 Report — Body Metrics + Readiness Lite

**Date:** 2026-04-13
**Status:** Complete
**Prerequisite:** S0 (catalog integrity) — complete

## Objective

Add lateralized body measurements and daily readiness tracking
to SPIGNOS without breaking the existing session flow.

## Deliverables

| Artifact | Path | Status |
|----------|------|--------|
| Migration | `migrations/versions/20260413_body_measurements_v2_readiness.py` | Applied |
| Readiness model | `app/models/readiness.py` | Done |
| Readiness service | `app/services/readiness.py` | Done |
| Readiness router | `app/routers/readiness.py` | Done |
| History template | `app/templates/readiness_history.html` | Done |
| Spec doc | `docs/strategy/SPIGNOS_BODY_METRICS_READINESS_SPEC.md` | Done |

## Changes Made

### Database
- body_measurements: `arm_cm` → `arm_cm_left` + `arm_cm_right` (data migrated to both)
- body_measurements: `thigh_cm` → `thigh_cm_left` + `thigh_cm_right` (data migrated to both)
- body_measurements: added `hip_cm`, `neck_cm`
- New table: `readiness_entries` (DATE pk, UNIQUE user+day, 5 scale fields 1-5)

### Services
- `measurements.py`: lateralized labels/maps, `compute_arm_avg`, `compute_thigh_avg`, `compute_zone_measurement()`
- `readiness.py`: new — `save_readiness`, `get_today_readiness`, `get_readiness_history`, validation, French labels
- `muscle_mapping.py`: `ZONE_MEASUREMENT` uses semantic keys (`arm_avg`, `thigh_avg`)
- `muscle_scoring.py`: `_score_anthropo` uses `compute_zone_measurement()` instead of `getattr()`

### Routes & UI
- Home page: readiness widget (compact badge row when filled, collapsible `<details>` form when not)
- `POST /readiness`: saves daily readiness with validation
- `GET /readiness/history`: 90-day history with colored badges
- Profile: lateralized measurement form with measurement protocol help text
- Profile route: dynamic form field parsing from `MEASUREMENT_FIELDS`

### Tests Added
- `test_readiness.py`: 8 tests (model, service, validation, upsert)
- `test_readiness_routes.py`: 6 tests (POST, history, auth)
- Updated `test_measurements.py`: lateralized fields + avg helper tests
- Updated `test_profile_measurements.py`: new field names

## Verification Commands

```bash
alembic current                                # Migration applied
pytest tests/test_readiness.py -v              # 8/8 pass
pytest tests/test_readiness_routes.py -v       # 6/6 pass
pytest tests/test_measurements.py -v           # All pass
pytest tests/test_muscle_scoring.py -v         # All pass
pytest tests/test_alembic_drift.py -v          # Drift-free
pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q  # 391 passed
```

## Files Modified/Created

| File | Action |
|------|--------|
| `app/models/measurement.py` | Modified (lateralized + hip/neck) |
| `app/models/readiness.py` | **New** |
| `app/models/__init__.py` | Modified (import readiness) |
| `app/database.py` | Modified (import readiness) |
| `app/services/measurements.py` | Modified (avg helpers, zone measurement, lateralized labels) |
| `app/services/readiness.py` | **New** |
| `app/services/muscle_mapping.py` | Modified (ZONE_MEASUREMENT semantic keys) |
| `app/services/muscle_scoring.py` | Modified (_score_anthropo, display labels) |
| `app/routers/pages.py` | Modified (readiness widget on Home, history route) |
| `app/routers/readiness.py` | **New** |
| `app/routers/auth_routes.py` | Modified (lateralized form parsing) |
| `app/main.py` | Modified (register readiness router) |
| `app/templates/index.html` | Modified (readiness widget) |
| `app/templates/readiness_history.html` | **New** |
| `app/templates/profile.html` | Modified (help text) |
| `migrations/versions/20260413_...` | **New** |
| `tests/test_readiness.py` | **New** |
| `tests/test_readiness_routes.py` | **New** |
| `tests/test_measurements.py` | Modified |
| `tests/test_profile_measurements.py` | Modified |

## Gaps for S2

- No composite readiness score yet
- No readiness → session correlation
- No asymmetry detection from left/right differences
- Body metrics live in Profile (dedicated /body route planned)
- No trend sparklines on readiness history (optional enhancement)
- No body fat estimation from measurements
