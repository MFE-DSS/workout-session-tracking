# SPIGNOS Scoring Rules V1

## Body Engineering Dashboard

### Axes

| Axis | Data Source | Score Formula | Minimum Data |
|------|-----------|---------------|-------------|
| Training Consistency | Sessions (completed) | min(100, sessions / (4/week * window)) | >= 2 sessions |
| Overload / Progression | Set tonnage by zone | Mean of zone performance scores | >= 4 sessions, >= 2 active zones |
| Body Trend | Body measurements | Mean of per-site progression scores | >= 3 measurements, >= 2 sites |
| Recovery / Readiness | Readiness entries (7d) | (avg_readiness - 1) / 4 * 100 | >= 5 entries in 30d |
| Muscular Balance | Physique zone scores | 100 - CV * 200 | >= 4 active zones |

### Global Score
- Average of active axes (inactive axes excluded, not zero-scored)
- Grade: A (>= 75), B (>= 50), C (< 50)
- Confidence: worst among active axes

### Confidence Tiers
- Elevee: >= 3x minimum threshold
- Moyenne: >= 2x minimum threshold
- Faible: at minimum threshold
- Insuffisante: below minimum (axis greyed out)

### Trend Detection
- Consistency: session count first half vs second half of window (10% threshold)
- Progression: majority vote of zone tonnage trends
- Body Trend: majority vote of measurement site directions
- Recovery: last 3 days avg vs days 4-7 avg (+/- 0.3 threshold)
- Balance: always "stable" in V1

### Performance Scoring per Zone (reused from physique dashboard)
- Split tonnage entries into first half / second half
- Compute % change in total tonnage
- <= -10%: score 20 (down), <= +2%: score 50 (stable), <= +10%: score 70 (up), <= +20%: score 85 (up), > +20%: score 95 (up)

### Body Site Scoring
- Compute % change between first and last measurement in window
- <= -2%: score 30 (regression), <= +0.5%: score 50 (stable), <= +2%: score 70 (progress), > +2%: score 90 (strong)
- Waist is inverse (decrease = positive)

### Design Principles
- No false precision: insufficient data = no score, not zero
- All rules visible: collapsible section on dashboard page
- No AI/ML: deterministic formulas only
- Readiness is always "recent" (7 days), not window-dependent
- Degradation gracieuse: score adapts to available data without misleading
