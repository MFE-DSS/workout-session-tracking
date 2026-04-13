# SPIGNOS Squads Privacy Model

## Principle
Squads share training activity, never body or health data.

## Shared with Squad Members
- Username
- Aggregate score (total_points, avg_points)
- Grade (A/B/C)
- Session count
- Last session date and template used
- Streak (consecutive training days)

## Never Shared
- Body measurements (chest, arms, thighs, waist, hips, neck, calves)
- Readiness entries (sleep, fatigue, soreness, stress, motivation)
- Bodyweight (per-session or profile)
- Session notes
- Body engineering dashboard score
- Set details (weight, reps)
- Exercise feedback (success score, muscle sensation)

## Enforcement
- Service layer returns only allowed fields
- Privacy tests verify no leakage in responses
- No body/readiness data is queried in squad service
