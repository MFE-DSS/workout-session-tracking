# Behavioral Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic behavioral engine that transforms raw workout data into fatigue, consistency, readiness, streak, and rule-based recommendations — integrated into Board and Profile pages.

**Architecture:** Single service file `app/services/behavioral.py` containing all scoring functions and the `BehavioralState` dataclass. Pure Python, no DB migration, no new routes. Integration via enriching existing route handlers and templates.

**Tech Stack:** Python 3.14, FastAPI, SQLAlchemy 2.0, Jinja2, pytest

---

## File Structure

| Action | File | Responsibility |
|--------|------|----------------|
| Create | `app/services/behavioral.py` | BehavioralState dataclass, all scoring functions, recommendation rules |
| Create | `tests/test_behavioral.py` | Unit tests for scoring + integration tests for routes |
| Modify | `app/routers/pages.py` | Add behavioral state to home route context |
| Modify | `app/routers/auth_routes.py` | Add behavioral state to profile route context |
| Modify | `app/templates/index.html` | 4th KPI (readiness) + recommendation text |
| Modify | `app/templates/profile.html` | Fatigue/consistency/streak KPIs |
| Modify | `app/static/css/app.css` | `.board-progress__reco` class |

---

### Task 1: BehavioralState dataclass + pure scoring functions (no DB)

**Files:**
- Create: `app/services/behavioral.py`
- Create: `tests/test_behavioral.py`

- [ ] **Step 1: Write failing tests for pure scoring functions**

```python
# tests/test_behavioral.py
"""Tests for behavioral engine scoring logic."""
from __future__ import annotations


from app.services.behavioral import (
    BehavioralState,
    compute_session_fatigue,
    compute_weighted_fatigue,
    compute_consistency,
    compute_readiness,
    compute_trend,
    compute_recommendation,
)


# --- Session fatigue ---

def test_session_fatigue_high():
    """fatigued + low concentration = high fatigue."""
    f = compute_session_fatigue(global_state="fatigued", concentration="low")
    # (80 + 70) / 2 = 75
    assert f == 75.0


def test_session_fatigue_low():
    """good + high concentration = low fatigue."""
    f = compute_session_fatigue(global_state="good", concentration="high")
    # (20 + 10) / 2 = 15
    assert f == 15.0


def test_session_fatigue_null_defaults():
    """None values use neutral defaults."""
    f = compute_session_fatigue(global_state=None, concentration=None)
    # (50 + 40) / 2 = 45
    assert f == 45.0


def test_session_fatigue_mixed():
    """flat + high concentration."""
    f = compute_session_fatigue(global_state="flat", concentration="high")
    # (50 + 10) / 2 = 30
    assert f == 30.0


# --- Weighted fatigue ---

def test_weighted_fatigue_three_sessions():
    fatigue_scores = [75.0, 30.0, 15.0]  # most recent first
    result = compute_weighted_fatigue(fatigue_scores)
    # 0.5 * 75 + 0.3 * 30 + 0.2 * 15 = 37.5 + 9 + 3 = 49.5
    assert abs(result - 49.5) < 0.01


def test_weighted_fatigue_two_sessions():
    result = compute_weighted_fatigue([60.0, 30.0])
    # 0.6 * 60 + 0.4 * 30 = 36 + 12 = 48
    assert abs(result - 48.0) < 0.01


def test_weighted_fatigue_one_session():
    result = compute_weighted_fatigue([75.0])
    assert result == 75.0


def test_weighted_fatigue_no_sessions():
    result = compute_weighted_fatigue([])
    assert result == 50.0  # neutral default


# --- Consistency ---

def test_consistency_daily():
    assert compute_consistency(sessions_14d=14) == 100.0


def test_consistency_none():
    assert compute_consistency(sessions_14d=0) == 0.0


def test_consistency_partial():
    result = compute_consistency(sessions_14d=3)
    assert abs(result - 21.43) < 0.1


def test_consistency_capped():
    """Even if >14 sessions, capped at 100."""
    assert compute_consistency(sessions_14d=20) == 100.0


# --- Readiness ---

def test_readiness_formula():
    r = compute_readiness(fatigue=30.0, consistency=80.0, performance=90.0)
    # 0.5 * (100-30) + 0.3 * 80 + 0.2 * 90 = 35 + 24 + 18 = 77
    assert abs(r - 77.0) < 0.01


def test_readiness_high_fatigue():
    r = compute_readiness(fatigue=90.0, consistency=50.0, performance=50.0)
    # 0.5 * 10 + 0.3 * 50 + 0.2 * 50 = 5 + 15 + 10 = 30
    assert abs(r - 30.0) < 0.01


# --- Trend ---

def test_trend_up():
    assert compute_trend(last_7=4, prev_7=2) == "up"


def test_trend_down():
    assert compute_trend(last_7=1, prev_7=3) == "down"


def test_trend_stable():
    assert compute_trend(last_7=2, prev_7=2) == "stable"


# --- Recommendations (priority system) ---

def test_reco_fatigue_critical():
    """Priority 1: fatigue >= 75."""
    state = BehavioralState(
        performance_score=80, consistency_score=70, fatigue_score=80,
        trend_direction="stable", streak_days=2, readiness_score=40,
        recommendation="",
    )
    reco = compute_recommendation(state)
    assert "repos" in reco.lower() or "fatigue" in reco.lower()


def test_reco_streak_fatigue():
    """Priority 2: streak >= 5 and fatigue >= 60."""
    state = BehavioralState(
        performance_score=70, consistency_score=60, fatigue_score=65,
        trend_direction="up", streak_days=6, readiness_score=50,
        recommendation="",
    )
    reco = compute_recommendation(state)
    assert "récupérer" in reco.lower() or "serie" in reco.lower() or "série" in reco.lower()


def test_reco_low_consistency():
    """Priority 3: consistency < 30."""
    state = BehavioralState(
        performance_score=50, consistency_score=20, fatigue_score=40,
        trend_direction="stable", streak_days=0, readiness_score=45,
        recommendation="",
    )
    reco = compute_recommendation(state)
    assert "régularité" in reco.lower() or "regularite" in reco.lower()


def test_reco_high_readiness():
    """Priority 5: readiness >= 80."""
    state = BehavioralState(
        performance_score=85, consistency_score=70, fatigue_score=20,
        trend_direction="up", streak_days=2, readiness_score=85,
        recommendation="",
    )
    reco = compute_recommendation(state)
    assert "pousser" in reco.lower() or "intensité" in reco.lower()


def test_reco_fallback():
    """Priority 8: no other rule matches."""
    state = BehavioralState(
        performance_score=40, consistency_score=35, fatigue_score=45,
        trend_direction="stable", streak_days=1, readiness_score=45,
        recommendation="",
    )
    reco = compute_recommendation(state)
    assert "chaque" in reco.lower() or "séance" in reco.lower() or "seance" in reco.lower()


def test_behavioral_state_dataclass():
    state = BehavioralState(
        performance_score=88.0, consistency_score=71.4, fatigue_score=35.0,
        trend_direction="up", streak_days=3, readiness_score=72.0,
        recommendation="Bonne condition.",
    )
    assert state.readiness_score == 72.0
    assert state.streak_days == 3
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_behavioral.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.services.behavioral'`

- [ ] **Step 3: Implement behavioral.py (pure functions only, no DB)**

```python
# app/services/behavioral.py
"""Deterministic behavioral engine for SPIGNOS.

Transforms raw workout data into actionable user feedback using
simple, interpretable formulas. No AI, no randomness.

Scoring:
  - Performance: composite score from most recent session
  - Consistency: sessions_14d / 14 * 100 (capped at 100)
  - Fatigue: weighted avg of subjective feedback (last 3 sessions)
  - Readiness: 0.5*(100-fatigue) + 0.3*consistency + 0.2*performance
  - Streak: consecutive calendar days with sessions
  - Trend: session count last 7d vs previous 7d

Recommendations: priority-based rules, first match wins.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BehavioralState:
    """Complete behavioral snapshot for a user."""

    performance_score: float  # 0..100
    consistency_score: float  # 0..100
    fatigue_score: float  # 0..100
    trend_direction: str  # "up", "down", "stable"
    streak_days: int  # consecutive days
    readiness_score: float  # 0..100
    recommendation: str  # French text


# --- Fatigue mappings (subjective feedback → 0..100) ---

_GLOBAL_STATE_FATIGUE = {"fatigued": 80.0, "flat": 50.0, "good": 20.0}
_CONCENTRATION_FATIGUE = {"low": 70.0, "medium": 40.0, "high": 10.0}

_DEFAULT_GLOBAL_STATE_FATIGUE = 50.0
_DEFAULT_CONCENTRATION_FATIGUE = 40.0
_DEFAULT_FATIGUE = 50.0  # neutral when no sessions


def compute_session_fatigue(
    *, global_state: str | None, concentration: str | None
) -> float:
    """Fatigue score for a single session from subjective feedback."""
    gs = _GLOBAL_STATE_FATIGUE.get(global_state or "", _DEFAULT_GLOBAL_STATE_FATIGUE)
    co = _CONCENTRATION_FATIGUE.get(concentration or "", _DEFAULT_CONCENTRATION_FATIGUE)
    return (gs + co) / 2


def compute_weighted_fatigue(fatigue_scores: list[float]) -> float:
    """Weighted average of per-session fatigue scores (most recent first).

    3 sessions: 0.5 / 0.3 / 0.2
    2 sessions: 0.6 / 0.4
    1 session:  1.0
    0 sessions: neutral default (50)
    """
    n = len(fatigue_scores)
    if n == 0:
        return _DEFAULT_FATIGUE
    if n == 1:
        return fatigue_scores[0]
    if n == 2:
        return 0.6 * fatigue_scores[0] + 0.4 * fatigue_scores[1]
    return 0.5 * fatigue_scores[0] + 0.3 * fatigue_scores[1] + 0.2 * fatigue_scores[2]


def compute_consistency(sessions_14d: int) -> float:
    """Consistency score: how often the user trains in a 14-day window."""
    return min(100.0, (sessions_14d / 14) * 100)


def compute_readiness(
    fatigue: float, consistency: float, performance: float
) -> float:
    """Readiness to train: weighted combo of recovery, regularity, level."""
    return 0.5 * (100 - fatigue) + 0.3 * consistency + 0.2 * performance


def compute_trend(last_7: int, prev_7: int) -> str:
    """Compare session counts: last 7 days vs previous 7 days."""
    if last_7 > prev_7:
        return "up"
    if last_7 < prev_7:
        return "down"
    return "stable"


# --- Recommendation rules (priority order, first match wins) ---

_RULES: list[tuple[str, str]] = []  # filled by _build_rules


def compute_recommendation(state: BehavioralState) -> str:
    """Apply priority rules to produce a single recommendation."""
    if state.fatigue_score >= 75:
        return "Fatigue élevée détectée. Privilégie le repos ou une séance légère."
    if state.streak_days >= 5 and state.fatigue_score >= 60:
        return "Belle série ! Mais pense à récupérer pour maintenir la qualité."
    if state.consistency_score < 30:
        return "La régularité est la clé. Vise au moins 2 séances cette semaine."
    if state.trend_direction == "down" and state.performance_score >= 60:
        return "Tendance en baisse malgré un bon niveau. Un boost de régularité suffirait."
    if state.readiness_score >= 80:
        return "Excellente forme. C'est le moment de pousser l'intensité."
    if state.readiness_score >= 50:
        return "Bonne condition générale. Continue sur ta lancée."
    if state.streak_days >= 3:
        return "Série en cours, garde le rythme !"
    return "Chaque séance compte. Lance-toi quand tu es prêt."
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_behavioral.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add app/services/behavioral.py tests/test_behavioral.py
git commit -m "feat: add BehavioralState dataclass with scoring and recommendation rules"
```

---

### Task 2: compute_behavioral_state DB function

**Files:**
- Modify: `app/services/behavioral.py` (append function)
- Modify: `tests/test_behavioral.py` (add integration tests)

- [ ] **Step 1: Write failing integration tests**

Append to `tests/test_behavioral.py`:

```python
from datetime import datetime, timezone, timedelta
from tests.helpers import get_test_user_id


def _add_completed_session(user_id, *, concentration="high", global_state="good",
                           success_score=100, n_work=2, n_done=2, started_at=None):
    """Insert a completed session with controlled inputs."""
    from app.database import SessionLocal
    from app.models.session import WorkoutSession, SessionExercise, SetLog

    with SessionLocal() as db:
        s = WorkoutSession(
            user_id=user_id,
            template_slug_snapshot="push-a",
            template_name_snapshot="Push A",
            started_at=started_at or datetime.now(timezone.utc),
            status="completed",
            concentration=concentration,
            global_state=global_state,
        )
        se = SessionExercise(
            exercise_code_snapshot="E1",
            exercise_name_snapshot="Ex",
            position=1,
            success_score=success_score,
        )
        for i in range(1, n_work + 1):
            se.set_logs.append(SetLog(
                kind="work", set_index=i,
                completed=(i <= n_done),
                weight_kg=60.0, reps=10,
            ))
        s.session_exercises.append(se)
        db.add(s)
        db.commit()
        return s.id


def test_compute_behavioral_state_no_sessions(client):
    """New user with no sessions gets neutral defaults."""
    from app.database import SessionLocal
    from app.services.behavioral import compute_behavioral_state

    uid = get_test_user_id()
    with SessionLocal() as db:
        state = compute_behavioral_state(db, uid)

    assert state.performance_score == 0.0
    assert state.consistency_score == 0.0
    assert state.fatigue_score == 50.0  # neutral
    assert state.streak_days == 0
    assert state.trend_direction == "stable"
    assert state.readiness_score > 0  # 0.5*50 + 0.3*0 + 0.2*0 = 25
    assert len(state.recommendation) > 0


def test_compute_behavioral_state_with_sessions(client):
    """User with sessions gets computed values."""
    from app.database import SessionLocal
    from app.services.behavioral import compute_behavioral_state

    uid = get_test_user_id()
    now = datetime.now(timezone.utc)

    # Add 3 sessions on consecutive days
    for i in range(3):
        _add_completed_session(
            uid, concentration="high", global_state="good",
            started_at=now - timedelta(days=i),
        )

    with SessionLocal() as db:
        state = compute_behavioral_state(db, uid)

    assert state.performance_score > 0
    assert state.consistency_score > 0
    assert state.fatigue_score < 50  # good + high = low fatigue
    assert state.streak_days >= 3
    assert state.readiness_score > 50


def test_compute_behavioral_state_streak_breaks(client):
    """Streak breaks when there's a gap day."""
    from app.database import SessionLocal
    from app.services.behavioral import compute_behavioral_state

    uid = get_test_user_id()
    now = datetime.now(timezone.utc)

    # Session today and yesterday, then gap, then 3 days ago
    _add_completed_session(uid, started_at=now)
    _add_completed_session(uid, started_at=now - timedelta(days=1))
    # Skip day 2
    _add_completed_session(uid, started_at=now - timedelta(days=3))

    with SessionLocal() as db:
        state = compute_behavioral_state(db, uid)

    assert state.streak_days == 2  # today + yesterday
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_behavioral.py::test_compute_behavioral_state_no_sessions -v`
Expected: FAIL with `ImportError: cannot import name 'compute_behavioral_state'`

- [ ] **Step 3: Implement compute_behavioral_state**

Append to `app/services/behavioral.py`:

```python
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.session import SessionExercise, WorkoutSession
from app.services.performance import compute_composite_score
from app.services.quality_score import compute_session_quality


def compute_behavioral_state(db: Session, user_id: int) -> BehavioralState:
    """Compute the full behavioral state for a user from DB data."""
    now = datetime.now(timezone.utc)
    today = now.date()

    _uf = WorkoutSession.user_id == user_id
    _completed = WorkoutSession.status == "completed"
    _not_excluded = WorkoutSession.excluded_from_stats.is_(False)

    # --- Last 3 completed sessions (for fatigue + performance) ---
    last_3 = list(
        db.execute(
            select(WorkoutSession)
            .where(_uf, _completed, _not_excluded)
            .order_by(WorkoutSession.started_at.desc())
            .limit(3)
            .options(
                selectinload(WorkoutSession.session_exercises)
                .selectinload(SessionExercise.set_logs)
            )
        ).scalars().all()
    )

    # Performance: composite score of most recent session
    performance = 0.0
    if last_3:
        s = last_3[0]
        quality = compute_session_quality(s)
        total_work = sum(
            1 for se in s.session_exercises
            for sl in se.set_logs if sl.kind == "work"
        )
        done_work = sum(
            1 for se in s.session_exercises
            for sl in se.set_logs if sl.kind == "work" and sl.completed
        )
        cr = done_work / total_work if total_work > 0 else 0.0
        performance = compute_composite_score(quality, cr)

    # Fatigue: weighted average of subjective feedback
    fatigue_scores = [
        compute_session_fatigue(
            global_state=s.global_state, concentration=s.concentration
        )
        for s in last_3
    ]
    fatigue = compute_weighted_fatigue(fatigue_scores)

    # --- Consistency: sessions in last 14 days ---
    window_14 = now - timedelta(days=14)
    sessions_14d = db.execute(
        select(func.count(WorkoutSession.id))
        .where(_uf, _completed, _not_excluded)
        .where(WorkoutSession.started_at >= window_14)
    ).scalar_one() or 0
    consistency = compute_consistency(sessions_14d)

    # --- Trend: last 7 vs previous 7 ---
    window_7 = now - timedelta(days=7)
    window_14_for_trend = now - timedelta(days=14)
    last_7_count = db.execute(
        select(func.count(WorkoutSession.id))
        .where(_uf, _completed, _not_excluded)
        .where(WorkoutSession.started_at >= window_7)
    ).scalar_one() or 0
    prev_7_count = db.execute(
        select(func.count(WorkoutSession.id))
        .where(_uf, _completed, _not_excluded)
        .where(WorkoutSession.started_at >= window_14_for_trend)
        .where(WorkoutSession.started_at < window_7)
    ).scalar_one() or 0
    trend = compute_trend(last_7_count, prev_7_count)

    # --- Streak: consecutive calendar days with sessions ---
    window_30 = now - timedelta(days=30)
    recent_dates_rows = db.execute(
        select(WorkoutSession.started_at)
        .where(_uf)
        .where(WorkoutSession.started_at >= window_30)
        .order_by(WorkoutSession.started_at.desc())
    ).scalars().all()
    session_dates = {d.date() for d in recent_dates_rows}

    streak = 0
    check_date = today
    while check_date in session_dates:
        streak += 1
        check_date -= timedelta(days=1)

    # --- Readiness ---
    readiness = compute_readiness(fatigue, consistency, performance)

    # --- Build state + recommendation ---
    state = BehavioralState(
        performance_score=round(performance, 1),
        consistency_score=round(consistency, 1),
        fatigue_score=round(fatigue, 1),
        trend_direction=trend,
        streak_days=streak,
        readiness_score=round(readiness, 1),
        recommendation="",
    )
    state.recommendation = compute_recommendation(state)

    return state
```

- [ ] **Step 4: Run all behavioral tests**

Run: `pytest tests/test_behavioral.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add app/services/behavioral.py tests/test_behavioral.py
git commit -m "feat: add compute_behavioral_state DB function"
```

---

### Task 3: Board integration (home route + template)

**Files:**
- Modify: `app/routers/pages.py`
- Modify: `app/templates/index.html`
- Create: `tests/test_board_behavioral.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_board_behavioral.py
"""Tests for behavioral data on Board home page."""
from __future__ import annotations


def test_home_shows_readiness(client):
    body = client.get("/").text
    assert "disponibilit" in body.lower()


def test_home_shows_recommendation(client):
    body = client.get("/").text
    # Fallback recommendation for user with no sessions
    assert "ance" in body.lower()  # "séance" from fallback text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_board_behavioral.py -v`
Expected: FAIL with `AssertionError` (current template lacks "disponibilité")

- [ ] **Step 3: Add behavioral state to home route**

In `app/routers/pages.py`, add import inside the `home` function and pass to template. Replace lines 96-106 (the return statement) with:

```python
    from app.services.behavioral import compute_behavioral_state

    behavioral = compute_behavioral_state(db, user.id)

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "page_title": "Accueil",
            "open_session": open_session,
            "open_since": open_since,
            "kpis": global_kpis,
            "sparkline_svg": sparkline_svg,
            "behavioral": behavioral,
        },
    )
```

- [ ] **Step 4: Update index.html**

In `app/templates/index.html`, add the 4th KPI after the completion KPI (after line 19, before `</div>` on line 20):

```html
    <div class="board-kpi">
      <span class="board-kpi__value">{{ "%.0f"|format(behavioral.readiness_score) }}</span>
      <span class="board-kpi__label">disponibilité</span>
    </div>
```

Add recommendation text after the sparkline block (after line 25, before the "Voir analyse" link on line 26):

```html
  <p class="board-progress__reco">{{ behavioral.recommendation }}</p>
```

The full section (lines 5-27) should become:

```html
<section class="board-progress">
  <h2 class="board-progress__title">Ma progression</h2>
  <div class="board-kpis">
    <div class="board-kpi">
      <span class="board-kpi__value">{{ kpis.sessions_this_week }}</span>
      <span class="board-kpi__label">cette sem.</span>
    </div>
    <div class="board-kpi">
      <span class="board-kpi__value">{{ "%.0f"|format(kpis.avg_success_score_30d) if kpis.avg_success_score_30d is not none else "—" }}</span>
      <span class="board-kpi__label">score moy.</span>
    </div>
    <div class="board-kpi">
      <span class="board-kpi__value">{% if kpis.completion_rate_30d is not none %}{{ "%.0f"|format(kpis.completion_rate_30d * 100) }}%{% else %}—{% endif %}</span>
      <span class="board-kpi__label">complétion 30j</span>
    </div>
    <div class="board-kpi">
      <span class="board-kpi__value">{{ "%.0f"|format(behavioral.readiness_score) }}</span>
      <span class="board-kpi__label">disponibilité</span>
    </div>
  </div>
  {% if sparkline_svg %}
    <div class="sparkline-container">{{ sparkline_svg|safe }}</div>
  {% else %}
    <p class="board-progress__empty">Pas encore de données</p>
  {% endif %}
  <p class="board-progress__reco">{{ behavioral.recommendation }}</p>
  <a class="board-progress__link" href="{{ url_for('progress') }}">Voir analyse complète &rarr;</a>
</section>
```

- [ ] **Step 5: Run tests**

Run: `pytest tests/test_board_behavioral.py tests/test_board_kpis.py -v`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add app/routers/pages.py app/templates/index.html tests/test_board_behavioral.py
git commit -m "feat: add readiness and recommendation to Board home page"
```

---

### Task 4: Profile integration (route + template)

**Files:**
- Modify: `app/routers/auth_routes.py`
- Modify: `app/templates/profile.html`
- Create: `tests/test_profile_behavioral.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_profile_behavioral.py
"""Tests for behavioral data on Profile page."""
from __future__ import annotations


def test_profile_shows_fatigue(client):
    body = client.get("/profile").text
    assert "fatigue" in body.lower()


def test_profile_shows_consistency(client):
    body = client.get("/profile").text
    assert "gularit" in body.lower()  # "régularité"


def test_profile_shows_streak(client):
    body = client.get("/profile").text
    assert "rie" in body.lower()  # "série"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_profile_behavioral.py -v`
Expected: FAIL with `AssertionError`

- [ ] **Step 3: Add behavioral state to profile route**

In `app/routers/auth_routes.py`, add import at the top of `profile_page` function and pass to template. The `profile_page` function's return statement (lines 234-247) becomes:

```python
    from app.services.behavioral import compute_behavioral_state

    behavioral = compute_behavioral_state(db, user.id)

    return templates.TemplateResponse(
        request, "profile.html",
        {
            "page_title": "Profil",
            "user": user,
            "session_count": session_count,
            "completed_count": completed_count,
            "quality_svg": quality_svg,
            "sessions_30d_count": sessions_30d_count,
            "trend": trend,
            "trend_label": trend_label,
            "behavioral": behavioral,
            "active_session": latest_open_session(db, user.id),
        },
    )
```

- [ ] **Step 4: Update profile.html**

In `app/templates/profile.html`, add a second row of KPIs after line 26 (after the closing `</div>` of the first `board-kpis` row), before the quality_svg block:

```html
  <div class="board-kpis" style="margin-top: 8px;">
    <div class="board-kpi">
      <span class="board-kpi__value">{{ "%.0f"|format(behavioral.fatigue_score) }}</span>
      <span class="board-kpi__label">fatigue</span>
    </div>
    <div class="board-kpi">
      <span class="board-kpi__value">{{ "%.0f"|format(behavioral.consistency_score) }}</span>
      <span class="board-kpi__label">régularité</span>
    </div>
    <div class="board-kpi">
      <span class="board-kpi__value">{{ behavioral.streak_days }}</span>
      <span class="board-kpi__label">jours de série</span>
    </div>
  </div>
```

The "Mes 30 derniers jours" section (lines 15-32) should become:

```html
<section class="card" style="margin-top: var(--space);">
  <h2 class="card__title">Mes 30 derniers jours</h2>
  <div class="board-kpis">
    <div class="board-kpi">
      <span class="board-kpi__value">{{ sessions_30d_count }}</span>
      <span class="board-kpi__label">séances</span>
    </div>
    <div class="board-kpi">
      <span class="board-kpi__value trend-indicator trend-indicator--{{ trend }}">{{ trend_label }}</span>
      <span class="board-kpi__label">tendance</span>
    </div>
  </div>
  <div class="board-kpis" style="margin-top: 8px;">
    <div class="board-kpi">
      <span class="board-kpi__value">{{ "%.0f"|format(behavioral.fatigue_score) }}</span>
      <span class="board-kpi__label">fatigue</span>
    </div>
    <div class="board-kpi">
      <span class="board-kpi__value">{{ "%.0f"|format(behavioral.consistency_score) }}</span>
      <span class="board-kpi__label">régularité</span>
    </div>
    <div class="board-kpi">
      <span class="board-kpi__value">{{ behavioral.streak_days }}</span>
      <span class="board-kpi__label">jours de série</span>
    </div>
  </div>
  {% if quality_svg %}
    <div class="timeline-chart">{{ quality_svg|safe }}</div>
  {% else %}
    <p class="board-progress__empty">Pas encore de données</p>
  {% endif %}
</section>
```

- [ ] **Step 5: Run tests**

Run: `pytest tests/test_profile_behavioral.py tests/test_profile_enrich.py -v`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add app/routers/auth_routes.py app/templates/profile.html tests/test_profile_behavioral.py
git commit -m "feat: add fatigue, consistency, and streak to Profile page"
```

---

### Task 5: CSS + final integration

**Files:**
- Modify: `app/static/css/app.css`

- [ ] **Step 1: Add recommendation CSS class**

In `app/static/css/app.css`, add after the `.sparkline-container` rule (after the line `margin: 8px 0;` + closing `}`), before `/* ---------- Grade badges ---------- */`:

```css
.board-progress__reco {
  font-size: 13px;
  color: var(--fg-dim);
  margin: 8px 0 0;
  line-height: 1.4;
}
```

- [ ] **Step 2: Run full test suite**

Run: `pytest --tb=short -q`
Expected: All tests PASS (only pre-existing failures from missing .vscode files)

- [ ] **Step 3: Commit**

```bash
git add app/static/css/app.css
git commit -m "feat: add CSS for behavioral recommendation text"
```

- [ ] **Step 4: Run full test suite one more time**

Run: `pytest -v`
Expected: All new tests PASS, no regressions
