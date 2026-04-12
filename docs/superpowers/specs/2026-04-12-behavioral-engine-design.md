# SPIGNOS Behavioral Engine — Design Spec

**Date:** 2026-04-12
**Scope:** Deterministic behavioral state engine with rule-based recommendations

## Decisions

- Fatigue: subjective feedback (concentration + global_state), not quality score
- Recommendations: priority-based rule system (~8 rules), first match wins
- Integration: 4th KPI on Board + recommendation text, 3 extra KPIs on Profile
- No new routes, no JS, no migration

## Constraints

- Pure Python, deterministic outputs, no external dependencies
- No modification to existing route signatures or session logic
- Additive template changes only (enrich existing sections)
- All text in French

---

## 1. BehavioralState Dataclass

**File:** `app/services/behavioral.py`

```python
@dataclass
class BehavioralState:
    performance_score: float   # 0..100, composite score
    consistency_score: float   # 0..100
    fatigue_score: float       # 0..100
    trend_direction: str       # "up", "down", "stable"
    streak_days: int           # consecutive days with session
    readiness_score: float     # 0..100
    recommendation: str        # French text
```

---

## 2. Scoring Formulas

### Performance

Reuses `compute_composite_score()` from `app/services/performance.py` applied to the user's most recent completed session. If no sessions exist, defaults to 0.

### Consistency

```
consistency = (sessions_last_14_days / 14) * 100
```

Capped at 100. A user training every day scores 100. A user training 3 times in 14 days scores ~21.

### Fatigue

**Step 1: Per-session fatigue from subjective feedback**

```
global_state_fatigue:  fatigued=80, flat=50, good=20, null=50
concentration_fatigue: low=70, medium=40, high=10, null=40

session_fatigue = (global_state_fatigue + concentration_fatigue) / 2
```

**Step 2: Weighted average over last N completed sessions (max 3)**

- 3 sessions: `0.5 * s1 + 0.3 * s2 + 0.2 * s3` (s1 = most recent)
- 2 sessions: `0.6 * s1 + 0.4 * s2`
- 1 session: `1.0 * s1`
- 0 sessions: fatigue defaults to 50 (neutral)

### Readiness

```
readiness = 0.5 * (100 - fatigue) + 0.3 * consistency + 0.2 * performance
```

Range: 0..100. High readiness = low fatigue + good consistency + good performance.

### Streak

Starting from today, count consecutive calendar days (UTC) where at least one session was started. A day with no session breaks the streak.

- Today has a session + yesterday has a session + day before has none → streak = 2
- No session today → streak = 0

### Trend

Compare session count in last 7 days vs previous 7 days (days 8-14):

- last_7 > prev_7 → "up"
- last_7 < prev_7 → "down"
- last_7 == prev_7 → "stable"

---

## 3. Recommendation Rules (Priority System)

Evaluated in order. First matching rule wins.

| Priority | Condition | Text |
|----------|-----------|------|
| 1 | `fatigue >= 75` | "Fatigue elevee detectee. Privilegie le repos ou une seance legere." |
| 2 | `streak >= 5 and fatigue >= 60` | "Belle serie ! Mais pense a recuperer pour maintenir la qualite." |
| 3 | `consistency < 30` | "La regularite est la cle. Vise au moins 2 seances cette semaine." |
| 4 | `trend == "down" and performance >= 60` | "Tendance en baisse malgre un bon niveau. Un boost de regularite suffirait." |
| 5 | `readiness >= 80` | "Excellente forme. C'est le moment de pousser l'intensite." |
| 6 | `readiness >= 50` | "Bonne condition generale. Continue sur ta lancee." |
| 7 | `streak >= 3` | "Serie en cours, garde le rythme !" |
| 8 | *(fallback)* | "Chaque seance compte. Lance-toi quand tu es pret." |

All texts use proper French accents in the actual implementation. The table above uses ASCII for readability.

**Design principles:**
- Fatigue/safety rules first (priority 1-2)
- Consistency/regularity next (priority 3-4)
- Positive reinforcement last (priority 5-8)
- Never culpabilizing, always encouraging
- Fallback covers new users with no data

---

## 4. compute_behavioral_state Function

**Signature:**

```python
def compute_behavioral_state(db: Session, user_id: int) -> BehavioralState:
```

**Queries needed (all from existing models, no migration):**

1. Last 3 completed non-excluded sessions (for fatigue + performance)
   - Need: `concentration`, `global_state`, eager-loaded exercises + sets
2. Session count last 14 days (for consistency)
3. Session count last 7 days + previous 7 days (for trend)
4. Sessions by date, last 30 days (for streak)

All queries filter on `user_id`, `status == "completed"`, `excluded_from_stats == False`.

**Computation order:**
1. Performance (from most recent session via composite_score)
2. Consistency (count query)
3. Fatigue (from last 3 sessions' feedback)
4. Readiness (derived from fatigue + consistency + performance)
5. Streak (date scan)
6. Trend (two count queries)
7. Recommendation (rule evaluation)

---

## 5. Integration — Board

**`app/routers/pages.py`** — `home()` function:

Add call to `compute_behavioral_state(db, user.id)` and pass `behavioral` to template context.

**`app/templates/index.html`** — "Ma progression" section:

Add 4th KPI in the `board-kpis` row:
```html
<div class="board-kpi">
  <span class="board-kpi__value">{{ "%.0f"|format(behavioral.readiness_score) }}</span>
  <span class="board-kpi__label">disponibilite</span>
</div>
```

Add recommendation text after sparkline (before "Voir analyse" link):
```html
<p class="board-progress__reco">{{ behavioral.recommendation }}</p>
```

CSS for `.board-progress__reco`: `font-size: 13px; color: var(--fg-dim); margin: 8px 0 0;`

---

## 6. Integration — Profile

**`app/routers/auth_routes.py`** — `profile_page()` function:

Add call to `compute_behavioral_state(db, user.id)` and pass `behavioral` to template context.

**`app/templates/profile.html`** — "Mes 30 derniers jours" section:

Add a second row of KPIs after the existing sessions/trend row:
```html
<div class="board-kpis" style="margin-top: 8px;">
  <div class="board-kpi">
    <span class="board-kpi__value">{{ "%.0f"|format(behavioral.fatigue_score) }}</span>
    <span class="board-kpi__label">fatigue</span>
  </div>
  <div class="board-kpi">
    <span class="board-kpi__value">{{ "%.0f"|format(behavioral.consistency_score) }}</span>
    <span class="board-kpi__label">regularite</span>
  </div>
  <div class="board-kpi">
    <span class="board-kpi__value">{{ behavioral.streak_days }}</span>
    <span class="board-kpi__label">jours de serie</span>
  </div>
</div>
```

---

## 7. Files Summary

| Action | File |
|--------|------|
| Create | `app/services/behavioral.py` — BehavioralState + compute function + rules |
| Create | `tests/test_behavioral.py` — unit tests for all scoring + rules |
| Modify | `app/routers/pages.py` — add behavioral state to home route |
| Modify | `app/routers/auth_routes.py` — add behavioral state to profile route |
| Modify | `app/templates/index.html` — 4th KPI + recommendation text |
| Modify | `app/templates/profile.html` — fatigue/consistency/streak KPIs |
| Modify | `app/static/css/app.css` — `.board-progress__reco` class |
