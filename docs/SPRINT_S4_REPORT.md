# Sprint S4 Report — Challenges, Compare Mode, Template Sharing

**Date:** 2026-04-14
**Status:** Complete
**Prerequisites:** S3 (private squads)

## Objective

Add engagement loops to squads: time-boxed challenges (4 metrics),
1:1 compare mode, template recommendations, and anonymized session sharing.
Share cards dropped by design (no value in private product).

## Deliverables

| Feature | Files | Status |
|---------|-------|--------|
| Challenges (4 metrics) | challenge.py model + service, 3 templates | Done |
| Compare mode (1:1) | compare.py service, 1 template | Done |
| Template recommendations | sharing.py model + service | Done |
| Anonymized session sharing | sharing.py model + service | Done |
| Privacy enforcement | test_s4_privacy.py | Done |
| Squad detail enrichment | squad_detail.html + routes | Done |

## Verification

```
pytest tests/test_challenge.py tests/test_compare.py tests/test_sharing.py tests/test_s4_privacy.py -v
pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q
```

## Privacy

Challenge standings: rank + username + value only.
Shared sessions: exercises (code + name + score) only — no weights, reps, notes.
Compare mode: leaderboard metrics only — no body/readiness data.

## Gaps for future

- No challenge notifications / reminders
- No recurring challenges
- No share cards (dropped)
- No cross-squad features
