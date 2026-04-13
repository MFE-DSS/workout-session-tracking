# Sprint S0 Report — Foundation Freeze & Catalog Integrity

**Date:** 2026-04-13
**Status:** Complete
**Tests:** 367 passed, 0 failed

## Objective

Stabilize the exercise catalog as a reliable, auditable foundation for
future analytics (physique dashboard, body engineering, muscle scoring).

## Deliverables

| Artifact | Path | Status |
|----------|------|--------|
| QA script | `scripts/catalog_qa.py` | Done — 7 structural checks |
| QA report | `docs/strategy/SPIGNOS_CATALOG_QA_REPORT.md` | Generated, PASS (0 errors, 0 warnings) |
| Governance doc | `docs/strategy/SPIGNOS_CATALOG_GOVERNANCE.md` | Done |
| Integrity tests | `tests/test_catalog_integrity.py` | Done — 10 assertions, all pass |

## Changes Made

### Catalog Corrections (`data/reference_split.json`)
- `liss-abs` focus: "Cardio bas régime + Core" → "Core / Abdos"
- `legs-a` focus: added ", Core" (has E7 Roulette abdominale)
- `legs-b` focus: added ", Core" (has E7 Crunch câble)
- `lower-quad-bias` focus: added ", Core" (has E6 Roulette abdominale)
- `lower-posterior-bias` focus: added ", Core" (has E6 Crunch câble)
- Version bumped from v5 to `2026-04-13.v6`

### Muscle Mapping (`app/services/muscle_mapping.py`)
- Verified all 97 exercises are classifiable — zero unknowns
- No pattern additions needed (all exercises already matched)

### Test Fixes
- Fixed 21 tests broken by the v6 re-seed (template name assertions, liss-abs exercise expectations, slug references)

## Documented Anomalies (intentional, not corrected)
- pull-a: no direct biceps isolation (width focus by design)
- push-a E6: rear delt on push day (PPL convention)
- Archived templates overlap with core (pre-split legacy)

## Verification Commands

```bash
python scripts/catalog_qa.py                    # PASS, 0 errors
pytest tests/test_catalog_integrity.py -v       # 10/10 pass
pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q  # 367 passed
```

## Files Modified

| File | Action |
|------|--------|
| `data/reference_split.json` | Modified (focus corrections, version bump to v6) |
| `scripts/catalog_qa.py` | New (7 structural checks) |
| `tests/test_catalog_integrity.py` | New (10 CI-blocking assertions) |
| `docs/strategy/SPIGNOS_CATALOG_GOVERNANCE.md` | New |
| `docs/strategy/SPIGNOS_CATALOG_QA_REPORT.md` | New (generated) |
| `tests/test_csv_export.py` | Fixed (template name, liss-abs) |
| `tests/test_export.py` | Fixed (template name, liss-abs) |
| `tests/test_session_flow.py` | Fixed (template name, slugs) |
| `tests/test_session_builder.py` | Fixed (rep targets, liss-abs) |
| `tests/test_session_schema.py` | Fixed (template name, slugs) |
| `tests/test_history_upgrade.py` | Fixed (slugs) |
| `tests/test_ownership.py` | Fixed (slugs) |
| `tests/test_progression_hint.py` | Fixed (exercise index) |

## Gaps for S1

- Body measurements need lateralization (arm_cm → left/right, thigh_cm → left/right)
- New fields needed: hip_cm, neck_cm
- No readiness tracking yet
- Focus field now editorial-clean; mapping is analytical-clean — ready for enhanced scoring
