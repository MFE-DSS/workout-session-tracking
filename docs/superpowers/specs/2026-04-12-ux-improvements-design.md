# SPIGNOS UX Improvements — Design Spec

**Date:** 2026-04-12
**Scope:** Board sparkline, Profile enrichment, Leaderboard grades, Physical data, MetricsProvider abstraction

## Decisions

- Board mini graph: quality score sparkline (14 jours)
- Leaderboard grading: A/B/C only (no D), based on avg_points
- Physical data: in `/profile` directly (no new route for display)
- MetricsProvider: Protocol + registry, not wired to routes

## Constraints

- No changes to existing route signatures or session business logic
- Additive layers only (read/visualization)
- No JS dependencies — CSS-only interactions, server-rendered SVG
- Mobile-first, dark theme consistent with existing design

---

## 1. Board (Home `/`)

### timeline.py — New function

`build_sparkline_svg(scores: list[tuple[date, float]], days: int = 14) -> str | None`

- Compact SVG: width 100%, height 40px, viewBox-based responsive
- Simple polyline, no axes, no labels (pure sparkline)
- Color: `#f25f3a` (accent), transparent background
- Returns `None` if fewer than 2 data points

### pages.py — Route `GET /` enriched

Fetch from existing services:
- `sessions_this_week` (from `kpis.py`)
- `avg_success_score_30d` (from `kpis.py`)
- `completion_rate_30d` (from `kpis.py`)
- Quality scores for last 14 days (query completed sessions, compute quality_score)
- Call `build_sparkline_svg()` with the scores

Pass all to template context.

### index.html — New "Ma progression" block

Positioned above the action tiles grid:

```
┌─────────────────────────────────────────┐
│ Ma progression                          │
│                                         │
│  3 séances    78/100    92% complétion  │
│  cette sem.   score moy.  taux 30j     │
│                                         │
│  ───────╱╲───╱╲╱╲──── (sparkline)      │
│                                         │
│            Voir analyse complète →      │
└─────────────────────────────────────────┘
```

- KPIs always visible (show "0" or "—" when no data)
- Sparkline appears only after 2+ completed sessions
- "Pas encore de données" message if no sparkline
- Link to `/progress`

---

## 2. Profile (`/profile`)

### Database migration

New nullable columns on `User`:
- `height_cm` — Integer
- `weight_kg` — Float (reference weight, distinct from per-session bodyweight)
- `resting_hr` — Integer
- `waist_cm` — Float
- `blood_pressure` — String (format "12/8")

### auth_routes.py — `GET /profile` enriched

Additional data passed to template:
- Quality scores for last 30 days → `build_quality_timeline_svg()` (existing function)
- Session count last 30 days
- Trend indicator: compare session count last 30 days vs previous 30 days
  - More → "↑ en hausse"
  - Equal → "→ stable"
  - Less → "↓ en baisse"

### auth_routes.py — `POST /profile/body` (new endpoint)

- Accepts form data for the 5 physical fields
- Validates: height 100-250cm, weight 30-300kg, hr 30-220bpm, waist 40-200cm, bp format regex
- Persists on User row
- Redirects to `/profile`

### profile.html — Two new sections

**Section "Mes 30 derniers jours":**
- SVG quality timeline (reuse existing `build_quality_timeline_svg`)
- Inline stats: "X séances" | trend indicator with label

**Section "Profil physique":**
- Read-only display when data exists (values or "—" for empty)
- "Modifier" button reveals inline form
- Form with 5 fields: Taille (cm), Poids (kg), FC repos (bpm), Tour de taille (cm), Tension
- All fields optional, submit button "Enregistrer"
- No connection to session flow whatsoever

---

## 3. Leaderboard (`/leaderboard`)

### leaderboard.py (service) — Enriched output

Each user entry gains:
- `last_session_score`: quality_score of most recent completed session
- `grade`: "A" if avg_points >= 80, "B" if >= 60, "C" otherwise
- `grade_label`:
  - A → "Exécution régulière et de haute qualité"
  - B → "Bonne régularité, marge de progression"
  - C → "En progression, chaque séance compte"

### leaderboard.html — Badge + tooltip

**Badge:** Letter grade next to username
- A → green (`#2ecc71`)
- B → orange (`#f25f3a`)
- C → neutral gray (`#888`)

**Tooltip (CSS-only):**
- Triggered by `:hover` (desktop) and `:focus-within` (mobile tap)
- Content: "Dernière session : XX/100" + "Note : X — [grade_label]"
- Implementation: hidden `<span>` with `position: absolute`, shown on parent hover/focus
- No JavaScript required

---

## 4. Physical Data

Covered in Section 2 (Profile). Key design choices:
- Data lives on User model, not on sessions
- Completely decoupled from workout flow
- Optional fields — never blocks any action
- Simple form, no wizard, no multi-step

---

## 5. MetricsProvider (Architecture)

### New file: `app/services/providers.py`

**Protocol `MetricsProvider`:**
```python
class MetricsProvider(Protocol):
    def get_body_metrics(self, user_id: int) -> BodyMetrics | None: ...
    def get_activity_summary(self, user_id: int, days: int = 30) -> ActivitySummary | None: ...
    def supports(self) -> list[str]: ...
```

**Dataclasses:**
```python
@dataclass
class BodyMetrics:
    weight_kg: float | None = None
    height_cm: int | None = None
    resting_hr: int | None = None
    waist_cm: float | None = None
    blood_pressure: str | None = None
    recorded_at: date | None = None

@dataclass
class ActivitySummary:
    steps: int | None = None
    calories_burned: int | None = None
    distance_km: float | None = None
    active_minutes: int | None = None
    period_days: int = 30
```

**`ManualProvider`:**
- Implements Protocol by reading User fields from DB
- `get_body_metrics()` → maps User columns to BodyMetrics
- `get_activity_summary()` → returns None
- `supports()` → `["body_metrics"]`

**`ProviderRegistry`:**
- Simple dict-based registry
- `register(name: str, provider: MetricsProvider)`
- `get(name: str) -> MetricsProvider | None`
- `list_available() -> list[str]`

**NOT connected to any route.** This is a documented contract for future extension.

---

## CSS Changes (`app/static/css/app.css`)

- `.board-progress` — Card styling for the home progression block
- `.board-kpis` — Flex row for 3 KPI items
- `.sparkline-container` — Wrapper for SVG sparkline
- `.grade-badge` — Colored letter badge (A/B/C)
- `.tooltip-wrapper` / `.tooltip-content` — CSS-only tooltip pattern
- `.body-profile` — Form layout for physical data section
- `.trend-indicator` — Inline trend with arrow

All additions, no modifications to existing classes.

---

## Files Summary

| Action | File |
|--------|------|
| Modify | `app/services/timeline.py` — add `build_sparkline_svg()` |
| Modify | `app/services/leaderboard.py` — add grade + last_session_score |
| Modify | `app/routers/pages.py` — enrich home route |
| Modify | `app/routers/auth_routes.py` — enrich profile + add POST /profile/body |
| Modify | `app/routers/leaderboard.py` — pass enriched data (if not already) |
| Modify | `app/templates/index.html` — add progression block |
| Modify | `app/templates/profile.html` — add 30j timeline + body form |
| Modify | `app/templates/leaderboard.html` — add badge + tooltip |
| Modify | `app/models/user.py` — add physical columns |
| Modify | `app/static/css/app.css` — add new classes |
| Create | `app/services/providers.py` — Protocol + ManualProvider + Registry |
| Create | `alembic/versions/XXXX_add_physical_profile.py` — migration |
