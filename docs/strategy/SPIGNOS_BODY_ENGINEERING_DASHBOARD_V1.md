# SPIGNOS Body Engineering Dashboard V1

## Purpose
Unified synthesis of training logs, body measurements, and readiness
into 5 scored axes with per-axis confidence and graceful degradation.

## Page
`GET /dashboard?window=30|60|90`

## Architecture
- Service: `app/services/dashboard.py` — compute_dashboard()
- Template: `app/templates/dashboard.html` — hero score + 5 axis cards
- No new models, no migrations, no JS

## Axes
1. **Training Consistency** — session frequency vs 4/week target
2. **Overload / Progression** — tonnage trend across active zones
3. **Body Trend** — measurement evolution (chest, arms avg, thighs avg, waist inverse)
4. **Recovery / Readiness** — daily self-assessment mean (always last 7 days)
5. **Muscular Balance** — zone score homogeneity (CV-based)

## Key Decisions
- Separate page from /physique (avoid overloading existing dense page)
- KPI cards (not radar) for mobile-first readability
- Score + confidence + degradation model (no false precision)
- Scoring rules visible in-page (collapsible details section)
- Recovery axis is always "recent" (7 days), independent of scoring window
- Balance trend is always "stable" in V1 (computing CV trend requires double physique computation)

## Degradation Matrix
| Data available | Active axes | Notes |
|---------------|-------------|-------|
| Nothing | 0 | "Pas assez de donnees" |
| 2+ sessions | 1 (Consistency) | |
| 4+ sessions, 2+ zones | 2 (+ Progression) | |
| + 5 readiness entries/30d | 3 (+ Recovery) | |
| + 3 measurements, 2 sites | 4 (+ Body Trend) | |
| + 4 active zones | 5 (+ Balance) | Full score |
