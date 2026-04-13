# S2 Design Spec — Body Engineering Dashboard V1

**Date:** 2026-04-13
**Sprint:** S2_body_engineering_dashboard_v1
**Status:** Approved

---

## Context

S0 stabilized the catalog. S1 added lateralized body metrics and daily readiness tracking. SPIGNOS now has three rich data streams — training logs, body measurements, readiness — but they live in silos: `/physique` (muscle zones), Home (behavioral + readiness widget), `/progress` (KPIs + timelines).

S2 creates the first unified synthesis: a Body Engineering Dashboard that scores the user across 5 axes, degrading gracefully when data is incomplete.

## Decisions Log

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Dashboard placement | New `/dashboard` page (Option B) | `/physique` is already dense (radar + 11 zone cards). Synthesis needs its own space. |
| Scoring model | Score global + confiance + degradation (Option C) | Consistent with S1 signal confidence policy. No false precision on sparse data. |
| Visual rendering | KPI cards per axis + hero score (Option C) | Mobile-first, consistent with existing design system. No confusion with physique radar. |

---

## Architecture

**No new models. No migrations. No JS. Pure synthesis on existing data.**

| Component | Responsibility |
|-----------|---------------|
| `app/services/dashboard.py` | Compute 5 axis scores + global score + confidence |
| `app/routers/pages.py` | `GET /dashboard?window=30` route |
| `app/templates/dashboard.html` | SSR rendering: hero score + 5 axis cards |
| `docs/strategy/SPIGNOS_SCORING_RULES_V1.md` | Documented scoring rules |

Data sources consumed (read-only):
- `WorkoutSession` + `SessionExercise` + `SetLog` (training volume, frequency)
- `BodyMeasurement` (circumference trends)
- `ReadinessEntry` (daily 1-5 scales)
- `muscle_scoring.compute_physique_dashboard()` (zone scores for balance axis)

---

## The 5 Axes

### Axis 1: Training Consistency (0-100)

**What it measures:** Regularity of training over the scoring window.

**Data source:** `WorkoutSession` (completed, not excluded).

**Computation:**
- Count completed sessions in window
- Target: 4 sessions/week (constant `WEEKLY_SESSION_TARGET = 4`)
- `expected_sessions = WEEKLY_SESSION_TARGET * (window_days / 7)`
- `score = min(100, actual_sessions / expected_sessions * 100)`
- Trend: compare session count in first half vs second half of window
  - second_half > first_half * 1.1 → "up"
  - second_half < first_half * 0.9 → "down"
  - else → "stable"

**Confidence minimum:** >= 2 sessions in window. Below: axis greyed out.

**Detail text:** "{N} sessions en {window}j (cible: {expected})"

### Axis 2: Overload / Progression (0-100)

**What it measures:** Are training loads progressing across active muscle zones?

**Data source:** Reuses tonnage computation from `muscle_scoring._compute_tonnage_by_zone()` and `_score_performance()`.

**Computation:**
- For each zone with >= 2 session entries: compute `_score_performance()` (returns score + trend)
- Filter to "active zones" (zones with `hard_sets >= 4` in the window)
- `score = mean(performance_scores of active zones)`
- Trend: majority vote of zone trends (most common among up/down/stable)

**Confidence minimum:** >= 4 sessions in window with >= 2 active zones. Below: axis greyed out.

**Detail text:** "{N} zones actives, tonnage {trend_label}"

### Axis 3: Body Trend (0-100)

**What it measures:** Are body measurements moving in the right direction?

**Data source:** `BodyMeasurement` within the window.

**Computation:**
- For each measurement site with >= 2 data points in window: compute first vs last value
- Sites scored: chest_cm, arm_avg (compute_arm_avg), thigh_avg (compute_thigh_avg), waist_cm
- Per-site scoring (same as `_score_anthropo` logic):
  - pct_change <= -2%: 30 (regression)
  - pct_change <= 0.5%: 50 (stable)
  - pct_change <= 2%: 70 (progress)
  - pct_change > 2%: 90 (strong progress)
  - waist_cm is inverse (decrease = positive)
- `score = mean(site_scores for sites with data)`
- Trend: overall direction of the majority of sites

**Confidence minimum:** >= 3 measurement entries in window AND >= 2 sites with data. Below: axis greyed out.

**Detail text:** "{N} sites mesures, tendance {trend_label}"

### Axis 4: Recovery / Readiness (0-100)

**What it measures:** Current recovery state from daily self-assessment.

**Data source:** `ReadinessEntry` within the last 7 days (regardless of scoring window — readiness is always "recent").

**Computation:**
- Collect readiness entries from last 7 days
- For each entry: compute entry_avg = mean of 5 scale fields
- `raw_avg = mean(entry_avgs)`
- `score = (raw_avg - 1) / 4 * 100` (maps 1-5 → 0-100)
- Trend: compare avg of last 3 entries vs avg of entries 4-7 days ago
  - recent > older + 0.3 → "up"
  - recent < older - 0.3 → "down"
  - else → "stable"

**Confidence minimum:** >= 5 readiness entries in last 30 days. Below: axis greyed out.

**Detail text:** "Moy. {raw_avg:.1f}/5 sur {N} jours"

### Axis 5: Muscular Balance (0-100)

**What it measures:** How evenly developed are the active muscle zones?

**Data source:** Zone scores from `compute_physique_dashboard()`.

**Computation:**
- Get zone_scores from physique dashboard (same window)
- Filter to active zones: zones with `hard_sets > 0`
- If < 4 active zones: insufficient data
- Compute coefficient of variation: `cv = stdev(zone_scores) / mean(zone_scores)` (if mean > 0)
- `score = max(0, 100 - cv * 200)` — cv of 0 = perfect balance (100), cv of 0.5 = score 0
- Trend: always "stable" in V1. Computing CV trend would require running the physique dashboard twice (sub-windows), which doubles the query cost. Deferred to V2 if users want it.

**Confidence minimum:** >= 4 active zones. Below: axis greyed out.

**Detail text:** "{N} zones actives, dispersion {cv_label}"

---

## Global Score

```python
active_axes = [axis for axis in axes if axis.confidence != "insuffisante"]
if not active_axes:
    global_score = None  # "Pas assez de données"
else:
    global_score = mean(axis.score for axis in active_axes)
```

All axes weighted equally. If an axis is insufficient, it's excluded and doesn't drag the score down — the score simply becomes "based on N axes out of 5".

**Grade:** A (>= 75), B (>= 50), C (< 50).

**Global confidence:** worst confidence among active axes.

---

## Confidence Levels

Reuse the existing 3-tier pattern from physique dashboard:

| Level | French label | Meaning |
|-------|-------------|---------|
| High | "élevée" | All data sources present, sufficient history |
| Medium | "moyenne" | Some data sources present, limited history |
| Low | "faible" | Minimal data, interpret with caution |
| Insufficient | "insuffisante" | Axis greyed out, not scored |

Per-axis confidence computation:
- Insufficient: below the minimum threshold (axis-specific, documented above)
- Faible: at or just above the minimum threshold
- Moyenne: 2x the minimum threshold
- Élevée: 3x the minimum threshold or more

---

## Degradation Matrix

| Data available | Active axes | Score based on |
|---------------|-------------|----------------|
| Nothing | 0 | "Pas assez de données" — no score |
| 2 sessions | 1 (Consistency) | 1 axis — score displayed with "confiance: faible" |
| 4+ sessions | 2 (Consistency + Progression) | 2 axes |
| Sessions + readiness | 3 (+ Recovery) | 3 axes |
| Sessions + measurements | 3 (+ Body Trend) | 3 axes |
| Sessions + readiness + measurements | 4 | 4 axes |
| All + 4 active zones | 5 | Full score, confiance élevée |

Each greyed card shows what's needed: "Renseigner vos mesures (Profil)" or "Remplir la readiness (Accueil)" or "Enregistrer plus de séances".

---

## Template Layout (dashboard.html)

```
┌─────────────────────────────────────────────┐
│ Body Engineering                     30j ▾  │
├─────────────────────────────────────────────┤
│                                             │
│    HERO CARD                                │
│    Score: 72 / 100    Grade: B              │
│    Confiance: moyenne                       │
│    Basé sur 4 axes sur 5                    │
│                                             │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─ Training Consistency ────────── 85 ─┐  │
│  │ ████████████████████░░  ↑            │  │
│  │ Confiance: élevée                    │  │
│  │ 14 sessions en 30j (cible: 17)       │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  ┌─ Overload / Progression ──────── 68 ─┐  │
│  │ ████████████████░░░░░░  →            │  │
│  │ Confiance: moyenne                   │  │
│  │ 6 zones actives, tonnage stable      │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  ┌─ Body Trend ──────────────────── — ──┐  │
│  │ ░░░░░░░░░░░░░░░░░░░░░░              │  │
│  │ Données insuffisantes                │  │
│  │ → Renseigner vos mesures (Profil)    │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  ┌─ Recovery / Readiness ────────── 74 ─┐  │
│  │ ██████████████████░░░░  ↑            │  │
│  │ Confiance: moyenne                   │  │
│  │ Moy. 3.9/5 sur 5 jours              │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  ┌─ Muscular Balance ───────────── 81 ─┐  │
│  │ ████████████████████░  →             │  │
│  │ Confiance: élevée                    │  │
│  │ 8 zones actives, bonne homogénéité   │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  Voir détail musculaire → (/physique)       │
│  Voir historique readiness →                │
│  Voir progression → (/progress)             │
├─────────────────────────────────────────────┤
│ Règles de calcul                            │
│ (collapsible <details> with scoring rules)  │
└─────────────────────────────────────────────┘
```

Window selector: 30j / 60j / 90j tabs (same segmented control pattern as `/physique`).

Navigation: add "Dashboard" entry between "Physique" and "Board" in base.html navbar.

---

## Scoring Rules Transparency

A collapsible `<details>` section at the bottom of the dashboard page that documents:
- What each axis measures
- What data it uses
- How the score is computed (simplified, not full formula)
- What "confiance" means

Also produced as `docs/strategy/SPIGNOS_SCORING_RULES_V1.md` for reference.

---

## Files to Create/Modify

| File | Action |
|------|--------|
| `app/services/dashboard.py` | **New** — 5 axis computations + global score |
| `app/routers/pages.py` | Modify — add `/dashboard` route |
| `app/templates/dashboard.html` | **New** — hero + 5 axis cards |
| `app/templates/base.html` | Modify — add "Dashboard" to navbar |
| `tests/test_dashboard.py` | **New** — service tests (each axis, degradation, confidence) |
| `tests/test_dashboard_routes.py` | **New** — route tests (renders, window param, auth, empty data) |
| `docs/strategy/SPIGNOS_SCORING_RULES_V1.md` | **New** |
| `docs/strategy/SPIGNOS_BODY_ENGINEERING_DASHBOARD_V1.md` | **New** |
| `docs/SPRINT_S2_REPORT.md` | **New** |

---

## Risks

| Risk | Mitigation |
|------|------------|
| Dashboard computation is slow (queries 3 tables + physique dashboard) | Cache-nothing for V1. Physique dashboard is already computed per-request and takes < 200ms. Dashboard adds 2 more lightweight queries. Profile if needed. |
| Balance axis CV computation could be noisy with few zones | Minimum 4 active zones threshold. CV capped at 0.5 (score floor at 0). |
| Readiness "last 7 days" doesn't match the scoring window | Intentional — readiness is always "how am I right now", not a 90-day average. Documented in scoring rules. |
| Users confuse dashboard score with physique score | Different pages, different labels. Dashboard = "Body Engineering Score". Physique = "Score Physique". |

---

## Acceptance Criteria

- [ ] `/dashboard` renders with hero score + 5 axis cards
- [ ] Window selector works (30/60/90 days)
- [ ] Each axis computes correctly from its data source
- [ ] Axes with insufficient data are greyed out with guidance text
- [ ] Global score adjusts to active axes count
- [ ] Confidence levels display correctly per axis
- [ ] Scoring rules are visible in collapsible section
- [ ] Auth required
- [ ] Nav updated
- [ ] Existing pages unaffected
- [ ] All tests pass

---

## DO NOT BUILD

- Readiness → session correlation analytics (deferred)
- Adaptive volume targets (deferred)
- Zone-specific recovery recommendations (deferred to S2.5 or S3)
- Any AI/ML scoring
- Trend sparklines per axis (nice-to-have, not V1)
