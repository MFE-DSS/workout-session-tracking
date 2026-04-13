# SPIGNOS Body Metrics & Readiness Lite Spec

## Body Measurements

### Schema (body_measurements table)
- weight_kg, chest_cm, waist_cm, calf_cm (direct)
- arm_cm_left, arm_cm_right (lateralized — source of truth)
- thigh_cm_left, thigh_cm_right (lateralized — source of truth)
- hip_cm, neck_cm (new)

### Source of Truth Doctrine
Lateralized columns (left/right) are the source of truth.
Averaged values used by the physique dashboard are derived views.
Future features (asymmetry, correlation) must use raw lateralized data.

### Measurement Protocol (in-app guidance)
- Measure at the same time, same conditions (morning, fasted)
- Weekly at most for circumference, daily OK for weight
- Relaxed muscle, tape flat, same landmarks
- Both sides even if similar
- Partial entries are fine — missing fields don't generate false signals

## Readiness Lite

### Schema (readiness_entries table)
- recorded_on: DATE (not DATETIME) — one per user per day, DB-enforced via UNIQUE(user_id, recorded_on)
- 5 dimensions: sleep_quality, fatigue_level, soreness_level, stress_level, motivation_level
- Scale: 1-5, 5 = always best
- Optional: resting_hr (INT), note (TEXT)

### Scale Semantics

| Value | Sommeil | Fatigue | Courbatures | Stress | Motivation |
|-------|---------|---------|-------------|--------|------------|
| 1 | Très mauvais | Épuisé | Très douloureux | Très stressé | Aucune |
| 2 | Mauvais | Fatigué | Douloureux | Stressé | Faible |
| 3 | Correct | Normal | Modéré | Moyen | Normale |
| 4 | Bon | En forme | Léger | Détendu | Bonne |
| 5 | Excellent | Très frais | Aucune douleur | Très détendu | Très motivé |

### UX
- Home page widget: collapsible form (not filled) or compact badge row (filled)
- History at /readiness/history (link from Home widget, no nav entry)
- Hard constraint: widget never pushes session action below the fold

## Signal Confidence Policy
- No trend displayed with fewer than 3 data points
- No muscle zone score with fewer than 2 relevant sessions
- No readiness trend with fewer than 5 entries in 30 days
- Partial measurements degrade to training-only scoring (60% performance + 40% exposure)

## UX Roadmap
- Profile is the S1 compromise for body metrics
- Dedicated /body route planned post-S1
