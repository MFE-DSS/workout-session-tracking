# S2 — Body Engineering Dashboard V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a unified `/dashboard` page that scores the user across 5 axes (consistency, progression, body trend, recovery, balance) with per-axis confidence and graceful degradation.

**Architecture:** One new service (`dashboard.py`) computes 5 axis scores from existing data (sessions, measurements, readiness, physique zones). One new route and template render the hero score + axis cards. No migrations, no new models, no JS.

**Tech Stack:** Python (SQLAlchemy queries + statistics), FastAPI route, Jinja2 template, pytest

---

## File Structure

| File | Responsibility |
|------|---------------|
| `app/services/dashboard.py` | Compute 5 axis scores + global score + confidence |
| `app/routers/pages.py` | `GET /dashboard` route |
| `app/templates/dashboard.html` | Hero score card + 5 axis cards + scoring rules |
| `app/templates/base.html` | Add "Dashboard" nav link |
| `tests/test_dashboard.py` | Service unit tests (each axis, degradation, confidence) |
| `tests/test_dashboard_routes.py` | Route integration tests |
| `docs/strategy/SPIGNOS_SCORING_RULES_V1.md` | Documented scoring rules |
| `docs/strategy/SPIGNOS_BODY_ENGINEERING_DASHBOARD_V1.md` | Feature spec |
| `docs/SPRINT_S2_REPORT.md` | Sprint report |

---

### Task 1: Dashboard Service — Data Structures + Training Consistency Axis

**Files:**
- Create: `app/services/dashboard.py`
- Create: `tests/test_dashboard.py`

- [ ] **Step 1: Write failing tests for data structures and consistency axis**

Create `tests/test_dashboard.py`:

```python
"""Tests for body engineering dashboard service."""
from __future__ import annotations

import pytest


def test_axis_score_dataclass_exists():
    from app.services.dashboard import AxisScore
    a = AxisScore(
        key="test", label="Test", score=75.0, trend="up",
        confidence="élevée", detail="test detail", active=True,
    )
    assert a.score == 75.0
    assert a.active is True


def test_axis_score_inactive():
    from app.services.dashboard import AxisScore
    a = AxisScore(
        key="test", label="Test", score=0.0, trend="stable",
        confidence="insuffisante", detail="", active=False,
        guidance="Do something",
    )
    assert a.active is False
    assert a.guidance == "Do something"


def test_dashboard_result_dataclass():
    from app.services.dashboard import DashboardResult, AxisScore
    axes = [
        AxisScore(key="a", label="A", score=80.0, trend="up",
                  confidence="élevée", detail="", active=True),
        AxisScore(key="b", label="B", score=60.0, trend="stable",
                  confidence="moyenne", detail="", active=True),
    ]
    d = DashboardResult(
        global_score=70.0, global_grade="B",
        global_confidence="moyenne", active_count=2,
        total_count=5, axes=axes, window_days=30,
    )
    assert d.global_score == 70.0
    assert d.active_count == 2


def test_consistency_axis_with_sessions(client):
    """With 6 sessions in 30 days, score should be > 0."""
    from datetime import datetime, timedelta, timezone
    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        for i in range(6):
            db.add(WorkoutSession(
                user_id=uid,
                template_slug_snapshot="push-a",
                template_name_snapshot="Push A",
                started_at=now - timedelta(days=i * 4),
                status="completed",
            ))
        db.commit()

    from app.services.dashboard import compute_consistency_axis
    with SessionLocal() as db:
        axis = compute_consistency_axis(db, uid, window_days=30)
    assert axis.active is True
    assert axis.score > 0
    assert axis.key == "consistency"


def test_consistency_axis_empty(client):
    """With 0 sessions, axis should be inactive."""
    from app.database import SessionLocal
    from app.services.dashboard import compute_consistency_axis
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    with SessionLocal() as db:
        axis = compute_consistency_axis(db, uid, window_days=30)
    assert axis.active is False
    assert axis.confidence == "insuffisante"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_dashboard.py -v`
Expected: FAIL (ImportError)

- [ ] **Step 3: Implement data structures and consistency axis**

Create `app/services/dashboard.py`:

```python
"""Body Engineering Dashboard — 5-axis synthesis scoring.

Combines training logs, body measurements, and readiness into a
unified score with per-axis confidence and graceful degradation.

No new data capture — pure synthesis on existing tables.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from statistics import mean, stdev

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.session import WorkoutSession


WEEKLY_SESSION_TARGET = 4


@dataclass
class AxisScore:
    key: str
    label: str
    score: float
    trend: str  # "up", "down", "stable"
    confidence: str  # "élevée", "moyenne", "faible", "insuffisante"
    detail: str
    active: bool
    guidance: str = ""


@dataclass
class DashboardResult:
    global_score: float | None
    global_grade: str
    global_confidence: str
    active_count: int
    total_count: int
    axes: list[AxisScore]
    window_days: int


def _confidence_from_ratio(actual: int, minimum: int) -> str:
    """Compute confidence tier from actual vs minimum threshold."""
    if actual < minimum:
        return "insuffisante"
    ratio = actual / minimum
    if ratio >= 3:
        return "élevée"
    if ratio >= 2:
        return "moyenne"
    return "faible"


def _trend_from_halves(first_half: float, second_half: float) -> str:
    if second_half > first_half * 1.1:
        return "up"
    if second_half < first_half * 0.9:
        return "down"
    return "stable"


def compute_consistency_axis(
    db: Session, user_id: int, window_days: int = 30
) -> AxisScore:
    """Training Consistency: regularity of sessions over the window."""
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(days=window_days)
    midpoint = now - timedelta(days=window_days / 2)

    _base = (
        WorkoutSession.user_id == user_id,
        WorkoutSession.status == "completed",
        WorkoutSession.excluded_from_stats.is_(False),
        WorkoutSession.started_at >= window_start,
    )

    total = db.execute(
        select(func.count(WorkoutSession.id)).where(*_base)
    ).scalar_one() or 0

    first_half = db.execute(
        select(func.count(WorkoutSession.id))
        .where(*_base)
        .where(WorkoutSession.started_at < midpoint)
    ).scalar_one() or 0

    second_half = total - first_half

    # Minimum: 2 sessions
    if total < 2:
        return AxisScore(
            key="consistency", label="Training Consistency",
            score=0.0, trend="stable", confidence="insuffisante",
            detail="", active=False,
            guidance="Enregistrer au moins 2 séances pour activer cet axe.",
        )

    expected = WEEKLY_SESSION_TARGET * (window_days / 7)
    score = min(100.0, total / expected * 100)
    trend = _trend_from_halves(first_half, second_half)
    confidence = _confidence_from_ratio(total, 2)

    return AxisScore(
        key="consistency", label="Training Consistency",
        score=round(score, 1), trend=trend, confidence=confidence,
        detail=f"{total} sessions en {window_days}j (cible: {int(expected)})",
        active=True,
    )
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_dashboard.py -v`
Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add app/services/dashboard.py tests/test_dashboard.py
git commit -m "feat(s2): dashboard service — AxisScore/DashboardResult + consistency axis"
```

---

### Task 2: Dashboard Service — Progression Axis

**Files:**
- Modify: `app/services/dashboard.py`
- Modify: `tests/test_dashboard.py`

- [ ] **Step 1: Write failing test**

Add to `tests/test_dashboard.py`:

```python
def test_progression_axis_with_data(client):
    """With multiple sessions with sets, progression axis should be active."""
    from datetime import datetime, timedelta, timezone
    from app.database import SessionLocal
    from app.models.session import WorkoutSession, SessionExercise, SetLog
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        for d in [28, 21, 14, 7, 3, 1]:
            s = WorkoutSession(
                user_id=uid,
                template_slug_snapshot="push-a",
                template_name_snapshot="Push A",
                started_at=now - timedelta(days=d),
                status="completed",
            )
            se = SessionExercise(
                exercise_code_snapshot="E1",
                exercise_name_snapshot="Chest Press machine",
                position=1,
            )
            for i in range(3):
                se.set_logs.append(SetLog(
                    kind="work", set_index=i + 1, completed=True,
                    weight_kg=60.0, reps=10,
                ))
            s.session_exercises.append(se)
            db.add(s)
        db.commit()

    from app.services.dashboard import compute_progression_axis
    with SessionLocal() as db:
        axis = compute_progression_axis(db, uid, window_days=30)
    assert axis.active is True
    assert axis.score > 0
    assert axis.key == "progression"


def test_progression_axis_empty(client):
    from app.database import SessionLocal
    from app.services.dashboard import compute_progression_axis
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    with SessionLocal() as db:
        axis = compute_progression_axis(db, uid, window_days=30)
    assert axis.active is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_dashboard.py::test_progression_axis_with_data -v`
Expected: FAIL (ImportError)

- [ ] **Step 3: Implement progression axis**

Add to `app/services/dashboard.py`:

```python
from app.services.muscle_mapping import ZONE_LABELS, classify_exercise
from app.services.muscle_scoring import _compute_tonnage_by_zone, _score_performance


def compute_progression_axis(
    db: Session, user_id: int, window_days: int = 30
) -> AxisScore:
    """Overload / Progression: are training loads increasing across active zones?"""
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(days=window_days)

    zone_data = _compute_tonnage_by_zone(db, user_id, window_start)

    # Active zones: those with >= 4 hard sets
    active_zones = []
    zone_scores = []
    zone_trends = []
    for zone in ZONE_LABELS:
        entries = zone_data.get(zone, [])
        hard_sets = sum(e["hard_sets"] for e in entries)
        if hard_sets >= 4:
            score, trend = _score_performance(entries)
            active_zones.append(zone)
            zone_scores.append(score)
            zone_trends.append(trend)

    # Minimum: 4 sessions AND 2 active zones
    session_count = db.execute(
        select(func.count(WorkoutSession.id))
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == "completed",
            WorkoutSession.excluded_from_stats.is_(False),
            WorkoutSession.started_at >= window_start,
        )
    ).scalar_one() or 0

    if session_count < 4 or len(active_zones) < 2:
        return AxisScore(
            key="progression", label="Overload / Progression",
            score=0.0, trend="stable", confidence="insuffisante",
            detail="", active=False,
            guidance="Enregistrer au moins 4 séances avec 2+ groupes musculaires.",
        )

    avg_score = mean(zone_scores)
    # Majority trend vote
    trend_counts = {"up": 0, "down": 0, "stable": 0}
    for t in zone_trends:
        trend_counts[t] += 1
    majority_trend = max(trend_counts, key=trend_counts.get)

    confidence = _confidence_from_ratio(len(active_zones), 2)

    return AxisScore(
        key="progression", label="Overload / Progression",
        score=round(avg_score, 1), trend=majority_trend,
        confidence=confidence,
        detail=f"{len(active_zones)} zones actives, tonnage {_trend_label(majority_trend)}",
        active=True,
    )


def _trend_label(trend: str) -> str:
    return {"up": "en hausse", "down": "en baisse", "stable": "stable"}[trend]
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_dashboard.py -v`
Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add app/services/dashboard.py tests/test_dashboard.py
git commit -m "feat(s2): dashboard progression axis — zone tonnage aggregation"
```

---

### Task 3: Dashboard Service — Body Trend + Recovery + Balance Axes

**Files:**
- Modify: `app/services/dashboard.py`
- Modify: `tests/test_dashboard.py`

- [ ] **Step 1: Write failing tests for all 3 remaining axes**

Add to `tests/test_dashboard.py`:

```python
def test_body_trend_axis_insufficient(client):
    """No measurements → inactive."""
    from app.database import SessionLocal
    from app.services.dashboard import compute_body_trend_axis
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    with SessionLocal() as db:
        axis = compute_body_trend_axis(db, uid, window_days=30)
    assert axis.active is False
    assert axis.key == "body_trend"


def test_body_trend_axis_with_data(client):
    """With measurements, axis should compute."""
    from datetime import datetime, timedelta, timezone
    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement
    from app.services.dashboard import compute_body_trend_axis
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        for i in range(4):
            db.add(BodyMeasurement(
                user_id=uid,
                measured_at=now - timedelta(days=i * 7),
                chest_cm=100.0 + i,
                arm_cm_left=35.0, arm_cm_right=35.5,
                waist_cm=85.0 - i * 0.5,
            ))
        db.commit()

    with SessionLocal() as db:
        axis = compute_body_trend_axis(db, uid, window_days=30)
    assert axis.active is True
    assert axis.score > 0


def test_recovery_axis_insufficient(client):
    """No readiness entries → inactive."""
    from app.database import SessionLocal
    from app.services.dashboard import compute_recovery_axis
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    with SessionLocal() as db:
        axis = compute_recovery_axis(db, uid)
    assert axis.active is False
    assert axis.key == "recovery"


def test_recovery_axis_with_data(client):
    from datetime import date, timedelta
    from app.database import SessionLocal
    from app.models.readiness import ReadinessEntry
    from app.services.dashboard import compute_recovery_axis
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    with SessionLocal() as db:
        for i in range(7):
            db.add(ReadinessEntry(
                user_id=uid,
                recorded_on=date.today() - timedelta(days=i),
                sleep_quality=4, fatigue_level=4, soreness_level=3,
                stress_level=4, motivation_level=5,
            ))
        db.commit()

    with SessionLocal() as db:
        axis = compute_recovery_axis(db, uid)
    assert axis.active is True
    assert axis.score > 0
    assert axis.key == "recovery"


def test_balance_axis_insufficient(client):
    """With no training data, balance should be inactive."""
    from app.database import SessionLocal
    from app.services.dashboard import compute_balance_axis
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    with SessionLocal() as db:
        axis = compute_balance_axis(db, uid, window_days=30)
    assert axis.active is False
    assert axis.key == "balance"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_dashboard.py::test_body_trend_axis_insufficient -v`
Expected: FAIL (ImportError)

- [ ] **Step 3: Implement all 3 axes**

Add to `app/services/dashboard.py`:

```python
from app.models.measurement import BodyMeasurement
from app.models.readiness import ReadinessEntry
from app.services.measurements import compute_arm_avg, compute_thigh_avg


def compute_body_trend_axis(
    db: Session, user_id: int, window_days: int = 30
) -> AxisScore:
    """Body Trend: are body measurements moving in the right direction?"""
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(days=window_days)

    rows = list(db.execute(
        select(BodyMeasurement)
        .where(BodyMeasurement.user_id == user_id)
        .where(BodyMeasurement.measured_at >= window_start)
        .order_by(BodyMeasurement.measured_at.asc())
    ).scalars().all())

    if len(rows) < 3:
        return AxisScore(
            key="body_trend", label="Body Trend",
            score=0.0, trend="stable", confidence="insuffisante",
            detail="", active=False,
            guidance="Renseigner vos mesures au moins 3 fois (Profil).",
        )

    # Score each site: first vs last value
    site_scores = []
    site_trends = []

    def _score_site(first_val, last_val, inverse=False):
        if first_val is None or last_val is None or first_val == 0:
            return None, None
        diff = last_val - first_val
        if inverse:
            diff = -diff
        pct = diff / first_val * 100
        if pct <= -2:
            return 30.0, "down"
        elif pct <= 0.5:
            return 50.0, "stable"
        elif pct <= 2:
            return 70.0, "up"
        else:
            return 90.0, "up"

    sites = [
        ("chest_cm", False),
        ("arm_avg", False),
        ("thigh_avg", False),
        ("waist_cm", True),
    ]

    for site_key, inverse in sites:
        if site_key == "arm_avg":
            first_val = compute_arm_avg(rows[0])
            last_val = compute_arm_avg(rows[-1])
        elif site_key == "thigh_avg":
            first_val = compute_thigh_avg(rows[0])
            last_val = compute_thigh_avg(rows[-1])
        else:
            first_val = getattr(rows[0], site_key, None)
            last_val = getattr(rows[-1], site_key, None)

        score, trend = _score_site(first_val, last_val, inverse)
        if score is not None:
            site_scores.append(score)
            site_trends.append(trend)

    if len(site_scores) < 2:
        return AxisScore(
            key="body_trend", label="Body Trend",
            score=0.0, trend="stable", confidence="insuffisante",
            detail="", active=False,
            guidance="Renseigner au moins 2 sites de mesure (Profil).",
        )

    avg_score = mean(site_scores)
    # Majority trend
    trend_counts = {"up": 0, "down": 0, "stable": 0}
    for t in site_trends:
        trend_counts[t] += 1
    majority_trend = max(trend_counts, key=trend_counts.get)

    confidence = _confidence_from_ratio(len(rows), 3)

    return AxisScore(
        key="body_trend", label="Body Trend",
        score=round(avg_score, 1), trend=majority_trend,
        confidence=confidence,
        detail=f"{len(site_scores)} sites mesurés, tendance {_trend_label(majority_trend)}",
        active=True,
    )


def compute_recovery_axis(db: Session, user_id: int) -> AxisScore:
    """Recovery / Readiness: current recovery state from daily self-assessment.

    Always uses last 7 days regardless of scoring window — readiness is 'now'.
    Confidence threshold: >= 5 entries in last 30 days.
    """
    from datetime import date as date_type

    today = date_type.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # Count for confidence
    month_count = db.execute(
        select(func.count(ReadinessEntry.id))
        .where(ReadinessEntry.user_id == user_id)
        .where(ReadinessEntry.recorded_on >= month_ago)
    ).scalar_one() or 0

    if month_count < 5:
        return AxisScore(
            key="recovery", label="Recovery / Readiness",
            score=0.0, trend="stable", confidence="insuffisante",
            detail="", active=False,
            guidance="Remplir la readiness au moins 5 fois en 30 jours (Accueil).",
        )

    # Last 7 days
    recent = list(db.execute(
        select(ReadinessEntry)
        .where(ReadinessEntry.user_id == user_id)
        .where(ReadinessEntry.recorded_on >= week_ago)
        .order_by(ReadinessEntry.recorded_on.desc())
    ).scalars().all())

    if not recent:
        return AxisScore(
            key="recovery", label="Recovery / Readiness",
            score=0.0, trend="stable", confidence="faible",
            detail="Aucune entrée cette semaine",
            active=True,
        )

    def _entry_avg(e):
        return mean([
            e.sleep_quality, e.fatigue_level, e.soreness_level,
            e.stress_level, e.motivation_level,
        ])

    entry_avgs = [_entry_avg(e) for e in recent]
    raw_avg = mean(entry_avgs)
    score = (raw_avg - 1) / 4 * 100  # maps 1-5 → 0-100

    # Trend: last 3 vs entries 4-7 days ago
    three_days_ago = today - timedelta(days=3)
    recent_vals = [_entry_avg(e) for e in recent if e.recorded_on > three_days_ago]
    older_vals = [_entry_avg(e) for e in recent if e.recorded_on <= three_days_ago]

    if recent_vals and older_vals:
        recent_mean = mean(recent_vals)
        older_mean = mean(older_vals)
        if recent_mean > older_mean + 0.3:
            trend = "up"
        elif recent_mean < older_mean - 0.3:
            trend = "down"
        else:
            trend = "stable"
    else:
        trend = "stable"

    confidence = _confidence_from_ratio(month_count, 5)

    return AxisScore(
        key="recovery", label="Recovery / Readiness",
        score=round(score, 1), trend=trend, confidence=confidence,
        detail=f"Moy. {raw_avg:.1f}/5 sur {len(recent)} jours",
        active=True,
    )


def compute_balance_axis(
    db: Session, user_id: int, window_days: int = 30
) -> AxisScore:
    """Muscular Balance: how evenly developed are active muscle zones?"""
    from app.services.muscle_scoring import compute_physique_dashboard

    dashboard = compute_physique_dashboard(db, user_id, window_days)
    active_scores = [
        z.score for z in dashboard.zone_scores if z.hard_sets > 0
    ]

    if len(active_scores) < 4:
        return AxisScore(
            key="balance", label="Muscular Balance",
            score=0.0, trend="stable", confidence="insuffisante",
            detail="", active=False,
            guidance="Entraîner au moins 4 zones musculaires différentes.",
        )

    avg = mean(active_scores)
    if avg == 0:
        cv = 0.0
    else:
        sd = stdev(active_scores) if len(active_scores) > 1 else 0.0
        cv = sd / avg

    score = max(0.0, 100.0 - cv * 200)
    trend = "stable"  # V1: no trend computation for balance

    cv_label = "bonne homogénéité" if cv < 0.2 else "dispersion modérée" if cv < 0.35 else "déséquilibre notable"
    confidence = _confidence_from_ratio(len(active_scores), 4)

    return AxisScore(
        key="balance", label="Muscular Balance",
        score=round(score, 1), trend=trend, confidence=confidence,
        detail=f"{len(active_scores)} zones actives, {cv_label}",
        active=True,
    )
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_dashboard.py -v`
Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add app/services/dashboard.py tests/test_dashboard.py
git commit -m "feat(s2): dashboard body trend + recovery + balance axes"
```

---

### Task 4: Dashboard Service — Global Score + compute_dashboard()

**Files:**
- Modify: `app/services/dashboard.py`
- Modify: `tests/test_dashboard.py`

- [ ] **Step 1: Write failing tests**

Add to `tests/test_dashboard.py`:

```python
def test_compute_dashboard_empty(client):
    """Empty DB → no active axes, no score."""
    from app.database import SessionLocal
    from app.services.dashboard import compute_dashboard
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    with SessionLocal() as db:
        result = compute_dashboard(db, uid, window_days=30)
    assert result.global_score is None
    assert result.active_count == 0
    assert result.total_count == 5
    assert len(result.axes) == 5


def test_compute_dashboard_with_sessions_only(client):
    """Sessions only → consistency + possibly progression active."""
    from datetime import datetime, timedelta, timezone
    from app.database import SessionLocal
    from app.models.session import WorkoutSession, SessionExercise, SetLog
    from app.services.dashboard import compute_dashboard
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        for d in [28, 21, 14, 7, 3, 1]:
            s = WorkoutSession(
                user_id=uid,
                template_slug_snapshot="push-a",
                template_name_snapshot="Push A",
                started_at=now - timedelta(days=d),
                status="completed",
            )
            se = SessionExercise(
                exercise_code_snapshot="E1",
                exercise_name_snapshot="Chest Press machine",
                position=1,
            )
            for i in range(3):
                se.set_logs.append(SetLog(
                    kind="work", set_index=i + 1, completed=True,
                    weight_kg=60.0, reps=10,
                ))
            s.session_exercises.append(se)
            db.add(s)
        db.commit()

    with SessionLocal() as db:
        result = compute_dashboard(db, uid, window_days=30)
    assert result.global_score is not None
    assert result.active_count >= 1
    assert result.global_grade in ("A", "B", "C")
    # Body trend and recovery should be inactive
    body = next(a for a in result.axes if a.key == "body_trend")
    assert body.active is False
    recovery = next(a for a in result.axes if a.key == "recovery")
    assert recovery.active is False


def test_compute_dashboard_grade_boundaries(client):
    """Test grade assignment."""
    from app.services.dashboard import _compute_grade
    assert _compute_grade(80.0) == "A"
    assert _compute_grade(75.0) == "A"
    assert _compute_grade(74.9) == "B"
    assert _compute_grade(50.0) == "B"
    assert _compute_grade(49.9) == "C"
    assert _compute_grade(0.0) == "C"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_dashboard.py::test_compute_dashboard_empty -v`
Expected: FAIL (ImportError)

- [ ] **Step 3: Implement compute_dashboard and grade logic**

Add to `app/services/dashboard.py`:

```python
def _compute_grade(score: float) -> str:
    if score >= 75:
        return "A"
    if score >= 50:
        return "B"
    return "C"


def compute_dashboard(
    db: Session, user_id: int, window_days: int = 30
) -> DashboardResult:
    """Compute the full body engineering dashboard."""
    axes = [
        compute_consistency_axis(db, user_id, window_days),
        compute_progression_axis(db, user_id, window_days),
        compute_body_trend_axis(db, user_id, window_days),
        compute_recovery_axis(db, user_id),
        compute_balance_axis(db, user_id, window_days),
    ]

    active = [a for a in axes if a.active]
    active_count = len(active)
    total_count = len(axes)

    if not active:
        return DashboardResult(
            global_score=None, global_grade="—",
            global_confidence="insuffisante",
            active_count=0, total_count=total_count,
            axes=axes, window_days=window_days,
        )

    global_score = round(mean(a.score for a in active), 1)
    global_grade = _compute_grade(global_score)

    # Worst confidence among active axes
    conf_order = {"élevée": 3, "moyenne": 2, "faible": 1, "insuffisante": 0}
    worst = min(active, key=lambda a: conf_order.get(a.confidence, 0))
    global_confidence = worst.confidence

    return DashboardResult(
        global_score=global_score, global_grade=global_grade,
        global_confidence=global_confidence,
        active_count=active_count, total_count=total_count,
        axes=axes, window_days=window_days,
    )
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_dashboard.py -v`
Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add app/services/dashboard.py tests/test_dashboard.py
git commit -m "feat(s2): dashboard global score + compute_dashboard() orchestrator"
```

---

### Task 5: Dashboard Route + Template

**Files:**
- Modify: `app/routers/pages.py`
- Create: `app/templates/dashboard.html`
- Modify: `app/templates/base.html`
- Create: `tests/test_dashboard_routes.py`

- [ ] **Step 1: Write failing route tests**

Create `tests/test_dashboard_routes.py`:

```python
"""Integration tests for body engineering dashboard route."""
from __future__ import annotations


def test_dashboard_renders(client):
    r = client.get("/dashboard")
    assert r.status_code == 200
    assert "Body Engineering" in r.text


def test_dashboard_window_param(client):
    r = client.get("/dashboard?window=60")
    assert r.status_code == 200
    assert "60j" in r.text or "is-active" in r.text


def test_dashboard_invalid_window_defaults_30(client):
    r = client.get("/dashboard?window=999")
    assert r.status_code == 200


def test_dashboard_requires_auth(client):
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()
    r = client.get("/dashboard", follow_redirects=False)
    assert r.status_code == 303


def test_dashboard_shows_axis_cards(client):
    r = client.get("/dashboard")
    assert r.status_code == 200
    assert "Training Consistency" in r.text
    assert "Overload / Progression" in r.text
    assert "Body Trend" in r.text
    assert "Recovery / Readiness" in r.text
    assert "Muscular Balance" in r.text


def test_dashboard_nav_link_present(client):
    r = client.get("/dashboard")
    assert r.status_code == 200
    assert 'href="/dashboard"' in r.text or "Dashboard" in r.text
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_dashboard_routes.py::test_dashboard_renders -v`
Expected: FAIL (404)

- [ ] **Step 3: Add the route**

Add to `app/routers/pages.py`:

```python
@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: DbSession,
    user: CurrentUser,
    window: int = Query(30),
) -> HTMLResponse:
    from app.services.dashboard import compute_dashboard

    window = window if window in (30, 60, 90) else 30
    result = compute_dashboard(db, user.id, window_days=window)

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "page_title": "Body Engineering",
            "result": result,
            "window": window,
            "active_session": latest_open_session(db, user.id),
        },
    )
```

- [ ] **Step 4: Create the template**

Create `app/templates/dashboard.html`:

```html
{% extends "base.html" %}
{% block content %}
<h1 class="page-title">Body Engineering</h1>

<div class="cockpit-grid">
  <div class="cockpit-main">
    {# Hero score card #}
    <div class="card" style="text-align:center;padding:var(--space-lg);">
      {% if result.global_score is not none %}
        <span class="global-score">{{ "%.0f"|format(result.global_score) }}</span>
        <span class="grade-badge grade-badge--{{ result.global_grade|lower }}">{{ result.global_grade }}</span>
        <p class="text-dim" style="margin-top:var(--space-sm);font-size:13px;">
          Confiance : {{ result.global_confidence }} · Basé sur {{ result.active_count }} axe{% if result.active_count != 1 %}s{% endif %} sur {{ result.total_count }}
        </p>
      {% else %}
        <span class="global-score" style="opacity:0.3;">—</span>
        <p class="text-dim" style="margin-top:var(--space-sm);">Pas assez de données pour calculer un score.</p>
      {% endif %}
    </div>

    <nav class="filter-bar" style="margin-top:var(--space-md);">
      <a class="filter-bar__item {% if window == 30 %}is-active{% endif %}"
         href="/dashboard?window=30">30j</a>
      <a class="filter-bar__item {% if window == 60 %}is-active{% endif %}"
         href="/dashboard?window=60">60j</a>
      <a class="filter-bar__item {% if window == 90 %}is-active{% endif %}"
         href="/dashboard?window=90">90j</a>
    </nav>
  </div>

  <div class="cockpit-side">
    {# 5 axis cards #}
    {% for axis in result.axes %}
    <div class="zone-card{% if not axis.active %} zone-card--inactive{% endif %}">
      <div class="zone-card__header">
        <span class="zone-card__label">{{ axis.label }}</span>
        {% if axis.active %}
          <span class="zone-confidence zone-confidence--{{ axis.confidence }}"
                title="Confiance : {{ axis.confidence }}"></span>
        {% endif %}
      </div>

      {% if axis.active %}
        <div class="zone-bar">
          <div class="zone-bar__fill" style="width:{{ axis.score|round|int }}%"></div>
        </div>
        <div class="zone-card__score">
          <span class="text-mono">{{ "%.0f"|format(axis.score) }}/100</span>
          <span class="trend-indicator trend-indicator--{{ axis.trend }}">
            {% if axis.trend == 'up' %}↑{% elif axis.trend == 'down' %}↓{% else %}→{% endif %}
          </span>
        </div>
        <div class="zone-meta">{{ axis.detail }}</div>
      {% else %}
        <div class="zone-bar">
          <div class="zone-bar__fill" style="width:0%;opacity:0.2;"></div>
        </div>
        <p class="text-dim" style="font-size:13px;">Données insuffisantes</p>
        {% if axis.guidance %}
          <p class="text-dim" style="font-size:12px;">→ {{ axis.guidance }}</p>
        {% endif %}
      {% endif %}
    </div>
    {% endfor %}

    {# Navigation links #}
    <div style="margin-top:var(--space-md);">
      <a class="text-muted" href="/physique?window={{ window }}" style="display:block;font-size:13px;margin-bottom:var(--space-xs);">Voir détail musculaire →</a>
      <a class="text-muted" href="/readiness/history" style="display:block;font-size:13px;margin-bottom:var(--space-xs);">Voir historique readiness →</a>
      <a class="text-muted" href="/progress" style="display:block;font-size:13px;">Voir progression →</a>
    </div>

    {# Scoring rules #}
    <details style="margin-top:var(--space-lg);">
      <summary class="card__title" style="cursor:pointer;font-size:13px;">Règles de calcul</summary>
      <div class="card" style="margin-top:var(--space-sm);font-size:12px;">
        <p><b>Training Consistency</b> — Nombre de séances vs cible (4/semaine). ≥2 séances requises.</p>
        <p><b>Overload / Progression</b> — Évolution du tonnage par zone musculaire. ≥4 séances et ≥2 zones requises.</p>
        <p><b>Body Trend</b> — Évolution des mensurations (poitrine, bras, cuisses, taille). ≥3 mesures et ≥2 sites requis.</p>
        <p><b>Recovery / Readiness</b> — Moyenne readiness sur 7 jours (sommeil, fatigue, courbatures, stress, motivation). ≥5 entrées en 30j requises.</p>
        <p><b>Muscular Balance</b> — Homogénéité des scores entre zones musculaires actives. ≥4 zones requises.</p>
        <p style="margin-top:var(--space-sm);"><b>Score global</b> = moyenne des axes actifs. Grade : A (≥75), B (≥50), C (&lt;50).</p>
        <p><b>Confiance</b> = la plus basse des axes actifs. Axe inactif = données insuffisantes.</p>
      </div>
    </details>
  </div>
</div>
{% endblock %}
```

- [ ] **Step 5: Add Dashboard to navbar**

In `app/templates/base.html`, add a Dashboard link between Physique and Board (after line 25):

```html
        <a class="topbar__link" href="{{ url_for('dashboard') }}">Dashboard</a>
```

Between the Physique and Board links.

- [ ] **Step 6: Run tests**

Run: `pytest tests/test_dashboard_routes.py -v`
Expected: All PASS.

Run: `pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q`
Expected: Full suite passes.

- [ ] **Step 7: Commit**

```bash
git add app/routers/pages.py app/templates/dashboard.html app/templates/base.html tests/test_dashboard_routes.py
git commit -m "feat(s2): /dashboard route + template — hero score, 5 axis cards, scoring rules"
```

---

### Task 6: Documentation + Sprint Report

**Files:**
- Create: `docs/strategy/SPIGNOS_SCORING_RULES_V1.md`
- Create: `docs/strategy/SPIGNOS_BODY_ENGINEERING_DASHBOARD_V1.md`
- Create: `docs/SPRINT_S2_REPORT.md`

- [ ] **Step 1: Create scoring rules document**

Create `docs/strategy/SPIGNOS_SCORING_RULES_V1.md`:

```markdown
# SPIGNOS Scoring Rules V1

## Body Engineering Dashboard

### Axes

| Axis | Data Source | Score Formula | Minimum Data |
|------|-----------|---------------|-------------|
| Training Consistency | Sessions (completed) | min(100, sessions / (4/week * window)) | ≥2 sessions |
| Overload / Progression | Set tonnage by zone | Mean of zone performance scores | ≥4 sessions, ≥2 active zones |
| Body Trend | Body measurements | Mean of per-site progression scores | ≥3 measurements, ≥2 sites |
| Recovery / Readiness | Readiness entries (7d) | (avg_readiness - 1) / 4 * 100 | ≥5 entries in 30d |
| Muscular Balance | Physique zone scores | 100 - CV * 200 | ≥4 active zones |

### Global Score
- Average of active axes (inactive excluded)
- Grade: A (≥75), B (≥50), C (<50)
- Confidence: worst among active axes

### Confidence Tiers
- Élevée: ≥3x minimum threshold
- Moyenne: ≥2x minimum threshold
- Faible: at minimum threshold
- Insuffisante: below minimum (axis greyed out)

### Trend Detection
- Consistency: session count first half vs second half of window
- Progression: majority vote of zone tonnage trends
- Body Trend: majority vote of measurement site directions
- Recovery: last 3 days avg vs days 4-7 avg (±0.3 threshold)
- Balance: always "stable" in V1

### Design Principles
- No false precision: insufficient data = no score, not zero
- All rules visible: collapsible section on dashboard page
- No AI/ML: deterministic formulas only
- Readiness is always "recent" (7 days), not window-dependent
```

- [ ] **Step 2: Create feature spec**

Create `docs/strategy/SPIGNOS_BODY_ENGINEERING_DASHBOARD_V1.md`:

```markdown
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
1. Training Consistency — session frequency vs target
2. Overload / Progression — tonnage trend across zones
3. Body Trend — measurement evolution (chest, arms, thighs, waist)
4. Recovery / Readiness — daily self-assessment average
5. Muscular Balance — zone score homogeneity

## Key Decisions
- Separate page from /physique (avoid overloading)
- KPI cards (not radar) for mobile-first readability
- Score + confidence + degradation model (no false precision)
- Scoring rules visible in-page (transparency)
```

- [ ] **Step 3: Write sprint report**

Create `docs/SPRINT_S2_REPORT.md`:

```markdown
# Sprint S2 Report — Body Engineering Dashboard V1

**Date:** 2026-04-13
**Status:** Complete
**Prerequisite:** S0 (catalog integrity), S1 (body metrics + readiness)

## Objective

Create a unified body engineering dashboard synthesizing training,
body metrics, and readiness into a scored 5-axis view.

## Deliverables

| Artifact | Path | Status |
|----------|------|--------|
| Dashboard service | `app/services/dashboard.py` | Done |
| Dashboard template | `app/templates/dashboard.html` | Done |
| Route | `GET /dashboard?window=30\|60\|90` | Done |
| Scoring rules doc | `docs/strategy/SPIGNOS_SCORING_RULES_V1.md` | Done |
| Feature spec | `docs/strategy/SPIGNOS_BODY_ENGINEERING_DASHBOARD_V1.md` | Done |

## Verification Commands

```bash
pytest tests/test_dashboard.py -v
pytest tests/test_dashboard_routes.py -v
pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q
```

## Files Created/Modified

| File | Action |
|------|--------|
| `app/services/dashboard.py` | **New** — 5 axes + global score + confidence |
| `app/routers/pages.py` | Modified — `/dashboard` route |
| `app/templates/dashboard.html` | **New** — hero + axis cards + scoring rules |
| `app/templates/base.html` | Modified — nav link |
| `tests/test_dashboard.py` | **New** — service tests |
| `tests/test_dashboard_routes.py` | **New** — route tests |

## Gaps for S3

- No readiness → session correlation
- No zone-specific recovery recommendations
- No adaptive volume targets
- No trend sparklines per axis
- No per-zone readiness sub-scoring
```

- [ ] **Step 4: Run full test suite**

Run: `pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q`
Expected: All pass.

- [ ] **Step 5: Commit**

```bash
git add docs/strategy/SPIGNOS_SCORING_RULES_V1.md docs/strategy/SPIGNOS_BODY_ENGINEERING_DASHBOARD_V1.md docs/SPRINT_S2_REPORT.md
git commit -m "docs(s2): scoring rules + feature spec + sprint S2 report"
```
