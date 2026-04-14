# Sprint Sb_03 Report — Minimal Substitution Graph Build

**Date:** 2026-04-14
**Status:** Complete
**Spec:** docs/strategy/SPIGNOS_EXERCISE_SUBSTITUTION_GRAPH_SPEC.md

## Objective

Add exercise substitution to the session flow — swap prescribed
exercises for catalogue-defined equivalents, tracked for analytics.

## Deliverables

| Artifact | Path | Status |
|----------|------|--------|
| Migration | `migrations/versions/20260414_add_substitution.py` | Applied |
| Substitution service | `app/services/substitution.py` | Done |
| Catalogue update | `data/reference_split.json` v7 | 10 exercises with substitutes |
| Template UI | `app/templates/session_detail.html` | Select + badge |
| Muscle scoring | `app/services/muscle_scoring.py` | Uses actual_exercise_name() |
| Export | `app/services/export_builder.py` | Includes substituted_name |
| QA script | `scripts/catalog_qa.py` | Validates substitute classifiability |

## Verification

```
pytest tests/test_substitution.py -v
pytest tests/test_muscle_scoring.py -v
python scripts/catalog_qa.py
pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q
```

## Unblocks

- Sb_04 (history + analytics alignment)
