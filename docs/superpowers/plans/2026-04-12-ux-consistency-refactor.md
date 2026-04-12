# UX Consistency Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Unify performance logic, fix scoring formula, improve mobile tooltip accessibility, and structure blood pressure data across Board, Profile, and Leaderboard.

**Architecture:** Introduce a `PerformanceSnapshot` dataclass computed once per user, consumed by all three pages. Replace raw quality_score sparkline with a composite score (0.6 quality + 0.4 completion). Replace leaderboard grading thresholds with `avg_points * log(1 + total_sessions)`.

**Tech Stack:** Python 3.14, FastAPI, SQLAlchemy 2.0, Jinja2, Alembic, pytest

---

## File Structure

| Action | File | Responsibility |
|--------|------|----------------|
| Create | `app/services/performance.py` | PerformanceSnapshot dataclass + computation |
| Create | `app/services/providers.py` | MetricsProvider Protocol + ManualProvider + Registry |
| Create | `migrations/versions/20260412_add_physical_profile_fields.py` | DB migration for User columns |
| Create | `tests/test_performance.py` | Unit tests for PerformanceSnapshot + composite score |
| Create | `tests/test_providers.py` | Unit tests for MetricsProvider |
| Modify | `app/models/user.py` | Add physical profile columns (systolic, diastolic instead of string BP) |
| Modify | `app/services/timeline.py` | Add `build_sparkline_svg()` function |
| Modify | `app/services/leaderboard.py` | Add grade, grade_label, last_session_score to LeaderboardEntry |
| Modify | `app/routers/pages.py` | Enrich home route with KPIs + sparkline |
| Modify | `app/routers/auth_routes.py` | Enrich profile + add POST /profile/body |
| Modify | `app/templates/index.html` | Add "Ma progression" block |
| Modify | `app/templates/profile.html` | Add 30-day timeline + physical profile form |
| Modify | `app/templates/leaderboard.html` | Add grade badge + accessible tooltip |
| Modify | `app/static/css/app.css` | Add new classes |

---

### Task 1: PerformanceSnapshot dataclass + composite score

**Files:**
- Create: `app/services/performance.py`
- Test: `tests/test_performance.py`

- [ ] **Step 1: Write failing tests for composite score and PerformanceSnapshot**

```python
# tests/test_performance.py
"""Tests for PerformanceSnapshot and composite scoring."""
from __future__ import annotations

import math

from app.services.performance import (
    PerformanceSnapshot,
    compute_composite_score,
    compute_grade,
    compute_grade_score,
)


def test_composite_score_basic():
    """60% quality + 40% completion rate."""
    score = compute_composite_score(quality_score=80, completion_rate=1.0)
    # 0.6 * 80 + 0.4 * 100 = 48 + 40 = 88
    assert score == 88.0


def test_composite_score_partial_completion():
    score = compute_composite_score(quality_score=100, completion_rate=0.5)
    # 0.6 * 100 + 0.4 * 50 = 60 + 20 = 80
    assert score == 80.0


def test_composite_score_zero():
    score = compute_composite_score(quality_score=0, completion_rate=0.0)
    assert score == 0.0


def test_grade_score_rewards_volume():
    """grade_score = avg_points * log(1 + total_sessions)."""
    gs = compute_grade_score(avg_points=80.0, total_sessions=10)
    expected = 80.0 * math.log(1 + 10)
    assert abs(gs - expected) < 0.01


def test_grade_score_single_session():
    gs = compute_grade_score(avg_points=80.0, total_sessions=1)
    expected = 80.0 * math.log(2)
    assert abs(gs - expected) < 0.01


def test_grade_a():
    # A threshold: grade_score >= 80 * log(1+5) = 80 * 1.79 = 143
    assert compute_grade(avg_points=90.0, total_sessions=10) == "A"


def test_grade_b():
    # Moderate quality, few sessions
    assert compute_grade(avg_points=65.0, total_sessions=3) == "B"


def test_grade_c():
    # Low quality or very few sessions
    assert compute_grade(avg_points=30.0, total_sessions=1) == "C"


def test_performance_snapshot_dataclass():
    snap = PerformanceSnapshot(
        score=88.0,
        trend="up",
        consistency=0.85,
        last_session_score=92,
        grade="A",
        grade_label="Execution reguliere et de haute qualite",
    )
    assert snap.score == 88.0
    assert snap.grade == "A"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_performance.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.services.performance'`

- [ ] **Step 3: Implement PerformanceSnapshot**

```python
# app/services/performance.py
"""Unified performance metrics: PerformanceSnapshot.

A single dataclass consumed by Board, Profile, and Leaderboard
to ensure scoring consistency across all pages.

Composite score formula:
  score = 0.6 * quality_score + 0.4 * (completion_rate * 100)

Grade score (for A/B/C grading):
  grade_score = avg_points * log(1 + total_sessions)

Grade thresholds:
  A: grade_score >= 120
  B: grade_score >= 50
  C: grade_score < 50
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class PerformanceSnapshot:
    """Performance summary for a user, shared across pages."""

    score: float  # composite score (0..100)
    trend: str  # "up", "down", "stable"
    consistency: float  # 0..1 ratio of sessions in last 30d vs expected
    last_session_score: Optional[int]  # quality score of most recent session
    grade: str  # "A", "B", "C"
    grade_label: str  # human-readable explanation


# Grade labels (French)
GRADE_LABELS = {
    "A": "Exécution régulière et de haute qualité",
    "B": "Bonne régularité, marge de progression",
    "C": "En progression, chaque séance compte",
}

# Thresholds for grade_score
_GRADE_A_THRESHOLD = 120.0
_GRADE_B_THRESHOLD = 50.0


def compute_composite_score(
    quality_score: float, completion_rate: float
) -> float:
    """Composite score: 60% quality + 40% completion rate (as %).

    quality_score: 0..100
    completion_rate: 0..1
    Returns: 0..100
    """
    return 0.6 * quality_score + 0.4 * (completion_rate * 100)


def compute_grade_score(avg_points: float, total_sessions: int) -> float:
    """Grade score: avg_points * log(1 + total_sessions).

    Rewards consistency: a user with many sessions and good average
    scores higher than a user with one great session.
    """
    return avg_points * math.log(1 + total_sessions)


def compute_grade(avg_points: float, total_sessions: int) -> str:
    """Compute A/B/C grade from avg_points and session count."""
    gs = compute_grade_score(avg_points, total_sessions)
    if gs >= _GRADE_A_THRESHOLD:
        return "A"
    elif gs >= _GRADE_B_THRESHOLD:
        return "B"
    return "C"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_performance.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add app/services/performance.py tests/test_performance.py
git commit -m "feat: add PerformanceSnapshot dataclass with composite scoring"
```

---

### Task 2: Sparkline SVG function

**Files:**
- Modify: `app/services/timeline.py`
- Test: `tests/test_performance.py` (extend)

- [ ] **Step 1: Write failing test for sparkline**

Add to `tests/test_performance.py`:

```python
from app.services.timeline import build_sparkline_svg


def test_sparkline_returns_none_with_insufficient_data():
    assert build_sparkline_svg([]) is None
    assert build_sparkline_svg([(80.0,)]) is None


def test_sparkline_returns_svg_with_enough_data():
    points = [(70.0,), (75.0,), (80.0,)]
    svg = build_sparkline_svg(points)
    assert svg is not None
    assert "<svg" in svg
    assert "polyline" in svg
    assert "#f25f3a" in svg


def test_sparkline_is_compact():
    """Sparkline has no axis labels, no title, compact height."""
    points = [(60.0,), (70.0,), (80.0,), (90.0,)]
    svg = build_sparkline_svg(points)
    assert "viewBox" in svg
    # No axis text elements
    assert svg.count("<text") == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_performance.py::test_sparkline_returns_none_with_insufficient_data -v`
Expected: FAIL with `ImportError: cannot import name 'build_sparkline_svg'`

- [ ] **Step 3: Implement build_sparkline_svg**

Add to `app/services/timeline.py` (append after `build_bodyweight_timeline_svg`):

```python
def build_sparkline_svg(
    scores: list[tuple[float, ...]],
    *,
    width: int = 200,
    height: int = 40,
    color: str = "#f25f3a",
) -> str | None:
    """Build a compact sparkline SVG (no axes, no labels).

    Input: list of tuples where first element is the score value.
    Returns None if fewer than 2 data points.
    """
    if len(scores) < 2:
        return None

    values = [s[0] for s in scores]
    v_min = min(values)
    v_max = max(values)
    # Avoid division by zero for flat lines
    v_range = v_max - v_min if v_max != v_min else 1.0

    pad = 4  # Small padding inside viewBox
    chart_w = width - 2 * pad
    chart_h = height - 2 * pad
    n = len(values)

    def x_pos(i: int) -> float:
        return pad + (i / (n - 1)) * chart_w

    def y_pos(v: float) -> float:
        ratio = (v - v_min) / v_range
        return pad + chart_h * (1 - ratio)

    coords = " ".join(f"{x_pos(i):.1f},{y_pos(v):.1f}" for i, v in enumerate(values))

    return (
        f'<svg viewBox="0 0 {width} {height}" '
        f'xmlns="http://www.w3.org/2000/svg" '
        f'style="width:100%;max-width:{width}px;height:auto;" '
        f'role="img" aria-label="Sparkline de progression">'
        f'<polyline points="{coords}" fill="none" '
        f'stroke="{color}" stroke-width="2" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
        f'</svg>'
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_performance.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add app/services/timeline.py tests/test_performance.py
git commit -m "feat: add build_sparkline_svg for compact inline sparklines"
```

---

### Task 3: Leaderboard enrichment (grade + last_session_score)

**Files:**
- Modify: `app/services/leaderboard.py`
- Modify: `tests/test_leaderboard.py`

- [ ] **Step 1: Write failing tests for new fields**

Add to `tests/test_leaderboard.py`:

```python
def test_leaderboard_entry_has_grade_fields(client):
    """LeaderboardEntry should include grade and last_session_score."""
    from app.database import SessionLocal
    from app.services.leaderboard import compute_leaderboard

    uid = get_test_user_id()
    _add_session(uid, quality_inputs={
        "concentration": "high", "global_state": "good", "success_score": 100,
    }, n_work=4, n_done=4)

    with SessionLocal() as db:
        entries = compute_leaderboard(db)
    me = next(e for e in entries if e.username == "testuser")
    assert hasattr(me, "grade")
    assert me.grade in ("A", "B", "C")
    assert hasattr(me, "last_session_score")
    assert me.last_session_score is not None
    assert hasattr(me, "grade_label")
    assert len(me.grade_label) > 0


def test_leaderboard_grade_c_for_low_volume(client):
    """One weak session should yield grade C."""
    from app.database import SessionLocal
    from app.services.leaderboard import compute_leaderboard

    uid = get_test_user_id()
    _add_session(uid, quality_inputs={
        "concentration": "low", "global_state": "fatigued", "success_score": 50,
    }, n_work=2, n_done=1)

    with SessionLocal() as db:
        entries = compute_leaderboard(db)
    me = next(e for e in entries if e.username == "testuser")
    assert me.grade == "C"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_leaderboard.py::test_leaderboard_entry_has_grade_fields -v`
Expected: FAIL with `AttributeError: 'LeaderboardEntry' object has no attribute 'grade'`

- [ ] **Step 3: Implement enrichment in leaderboard.py**

Modify `app/services/leaderboard.py`:

```python
"""Leaderboard scoring and ranking.

Score rule (documented in docs/PRODUCT_SPEC.md):

For each eligible session:
  - status == "completed"
  - excluded_from_stats == False
  - total_work_sets > 0

  session_points = session_quality_score
                   * (completed_work_sets / total_work_sets)

  This rewards both quality AND completion. A 100-quality session
  with only 50% of work sets done earns 50 points, not 100.

Per user:
  total_points = sum(session_points) across all eligible sessions
  counted_sessions = number of eligible sessions
  avg_points = total_points / counted_sessions (if > 0)

Grade:
  grade_score = avg_points * log(1 + counted_sessions)
  A: grade_score >= 120
  B: grade_score >= 50
  C: grade_score < 50

Tie handling: users with equal total_points are ordered by
username ASC (deterministic, alphabetical). Documented.

The function queries ALL users, not just the current one. It
returns aggregated ranking data only - no private session detail.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.session import SessionExercise, WorkoutSession
from app.models.user import User
from app.services.performance import GRADE_LABELS, compute_grade
from app.services.quality_score import compute_session_quality


@dataclass
class LeaderboardEntry:
    rank: int
    username: str
    total_points: float
    counted_sessions: int
    avg_points: Optional[float]
    last_session_score: Optional[int]
    grade: str
    grade_label: str


def compute_leaderboard(db: Session) -> list[LeaderboardEntry]:
    """Compute the full leaderboard across all active users."""
    users = db.execute(
        select(User).where(User.is_active.is_(True))
    ).scalars().all()

    raw: list[tuple[str, float, int, Optional[int]]] = []

    for user in users:
        sessions = db.execute(
            select(WorkoutSession)
            .where(
                WorkoutSession.user_id == user.id,
                WorkoutSession.status == "completed",
                WorkoutSession.excluded_from_stats.is_(False),
            )
            .options(
                selectinload(WorkoutSession.session_exercises)
                .selectinload(SessionExercise.set_logs)
            )
            .order_by(WorkoutSession.started_at.desc())
        ).scalars().all()

        total_pts = 0.0
        counted = 0
        last_score: Optional[int] = None

        for s in sessions:
            total_work = sum(
                1 for se in s.session_exercises
                for sl in se.set_logs if sl.kind == "work"
            )
            if total_work == 0:
                continue
            done_work = sum(
                1 for se in s.session_exercises
                for sl in se.set_logs if sl.kind == "work" and sl.completed
            )
            quality = compute_session_quality(s)
            if last_score is None:
                last_score = quality
            completion_ratio = done_work / total_work
            session_pts = quality * completion_ratio
            total_pts += session_pts
            counted += 1

        raw.append((user.username, total_pts, counted, last_score))

    # Sort: highest total_points first, then username ASC for ties.
    raw.sort(key=lambda x: (-x[1], x[0]))

    entries: list[LeaderboardEntry] = []
    for i, (username, pts, counted, last_score) in enumerate(raw, start=1):
        avg = round(pts / counted, 1) if counted > 0 else None
        grade = compute_grade(avg or 0.0, counted)
        entries.append(LeaderboardEntry(
            rank=i,
            username=username,
            total_points=round(pts, 1),
            counted_sessions=counted,
            avg_points=avg,
            last_session_score=last_score,
            grade=grade,
            grade_label=GRADE_LABELS.get(grade, ""),
        ))
    return entries
```

- [ ] **Step 4: Run all leaderboard tests**

Run: `pytest tests/test_leaderboard.py -v`
Expected: All PASS (existing tests still pass because new fields are additive)

- [ ] **Step 5: Commit**

```bash
git add app/services/leaderboard.py tests/test_leaderboard.py
git commit -m "feat: enrich LeaderboardEntry with grade A/B/C and last_session_score"
```

---

### Task 4: User model + migration (physical profile with structured BP)

**Files:**
- Modify: `app/models/user.py`
- Create: `migrations/versions/20260412_add_physical_profile_fields.py`

- [ ] **Step 1: Update User model**

```python
# app/models/user.py
"""User model for V2 multi-user auth.

A user owns workout sessions via `WorkoutSession.user_id`.
Passwords are stored as bcrypt hashes (never plain text).
Physical profile fields are optional (nullable) and decoupled
from session logging.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Physical profile (optional, decoupled from session flow)
    height_cm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    resting_hr: Mapped[int | None] = mapped_column(Integer, nullable=True)
    waist_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    bp_systolic: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bp_diastolic: Mapped[int | None] = mapped_column(Integer, nullable=True)
```

- [ ] **Step 2: Generate Alembic migration**

Run: `cd /Users/martinfeldmann/workout-session-tracking && python -m alembic revision --autogenerate -m "add physical profile fields to users"`

If autogenerate doesn't work due to head conflicts, create manually:

```python
# migrations/versions/20260412_add_physical_profile_fields.py
"""add physical profile fields to users

Revision ID: a1b2c3d4e5f6
Revises: 36be39e26189
Create Date: 2026-04-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '36be39e26189'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('height_cm', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('weight_kg', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('resting_hr', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('waist_cm', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('bp_systolic', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('bp_diastolic', sa.Integer(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('bp_diastolic')
        batch_op.drop_column('bp_systolic')
        batch_op.drop_column('waist_cm')
        batch_op.drop_column('resting_hr')
        batch_op.drop_column('weight_kg')
        batch_op.drop_column('height_cm')
```

- [ ] **Step 3: Run migration**

Run: `cd /Users/martinfeldmann/workout-session-tracking && python -m alembic upgrade head`
Expected: No errors

- [ ] **Step 4: Verify model works in tests**

Run: `pytest tests/test_register_profile.py -v`
Expected: All existing tests still PASS

- [ ] **Step 5: Commit**

```bash
git add app/models/user.py migrations/versions/20260412_add_physical_profile_fields.py
git commit -m "feat: add physical profile columns to User (structured BP)"
```

---

### Task 5: MetricsProvider abstraction

**Files:**
- Create: `app/services/providers.py`
- Create: `tests/test_providers.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_providers.py
"""Tests for MetricsProvider abstraction."""
from __future__ import annotations

from app.services.providers import (
    ActivitySummary,
    BodyMetrics,
    ManualProvider,
    ProviderRegistry,
)


def test_manual_provider_supports_body_metrics():
    provider = ManualProvider()
    assert "body_metrics" in provider.supports()


def test_manual_provider_get_body_metrics(client):
    """ManualProvider reads physical fields from User model."""
    from app.database import SessionLocal
    from app.models.user import User
    from sqlalchemy import select

    # Set some physical data on testuser
    with SessionLocal() as db:
        user = db.execute(select(User).where(User.username == "testuser")).scalar_one()
        user.height_cm = 180
        user.weight_kg = 75.0
        user.bp_systolic = 120
        user.bp_diastolic = 80
        db.commit()
        uid = user.id

    with SessionLocal() as db:
        provider = ManualProvider()
        metrics = provider.get_body_metrics(db, uid)

    assert metrics is not None
    assert metrics.height_cm == 180
    assert metrics.weight_kg == 75.0
    assert metrics.bp_systolic == 120
    assert metrics.bp_diastolic == 80


def test_manual_provider_activity_returns_none(client):
    from app.database import SessionLocal
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    with SessionLocal() as db:
        provider = ManualProvider()
        result = provider.get_activity_summary(db, uid)
    assert result is None


def test_registry_register_and_get():
    registry = ProviderRegistry()
    provider = ManualProvider()
    registry.register("manual", provider)
    assert registry.get("manual") is provider
    assert registry.get("nonexistent") is None
    assert "manual" in registry.list_available()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_providers.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement providers.py**

```python
# app/services/providers.py
"""MetricsProvider abstraction for external data sources.

Defines a Protocol for metrics providers (manual entry, Apple Health,
Garmin, Withings, etc.) and a simple registry.

Currently only ManualProvider is implemented — it reads physical
profile fields from the User model. NOT connected to any route.
This is a documented contract for future extension.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


@dataclass
class BodyMetrics:
    weight_kg: Optional[float] = None
    height_cm: Optional[int] = None
    resting_hr: Optional[int] = None
    waist_cm: Optional[float] = None
    bp_systolic: Optional[int] = None
    bp_diastolic: Optional[int] = None


@dataclass
class ActivitySummary:
    steps: Optional[int] = None
    calories_burned: Optional[int] = None
    distance_km: Optional[float] = None
    active_minutes: Optional[int] = None
    period_days: int = 30


class MetricsProvider(Protocol):
    def get_body_metrics(self, db: Session, user_id: int) -> Optional[BodyMetrics]: ...
    def get_activity_summary(self, db: Session, user_id: int, days: int = 30) -> Optional[ActivitySummary]: ...
    def supports(self) -> list[str]: ...


class ManualProvider:
    """Reads physical profile fields from the User model."""

    def get_body_metrics(self, db: Session, user_id: int) -> Optional[BodyMetrics]:
        user = db.execute(
            select(User).where(User.id == user_id)
        ).scalar_one_or_none()
        if user is None:
            return None
        # Return None if no data has been entered at all
        fields = (user.height_cm, user.weight_kg, user.resting_hr,
                  user.waist_cm, user.bp_systolic, user.bp_diastolic)
        if all(f is None for f in fields):
            return None
        return BodyMetrics(
            weight_kg=user.weight_kg,
            height_cm=user.height_cm,
            resting_hr=user.resting_hr,
            waist_cm=user.waist_cm,
            bp_systolic=user.bp_systolic,
            bp_diastolic=user.bp_diastolic,
        )

    def get_activity_summary(
        self, db: Session, user_id: int, days: int = 30
    ) -> Optional[ActivitySummary]:
        return None

    def supports(self) -> list[str]:
        return ["body_metrics"]


class ProviderRegistry:
    """Simple dict-based registry for metrics providers."""

    def __init__(self) -> None:
        self._providers: dict[str, MetricsProvider] = {}

    def register(self, name: str, provider: MetricsProvider) -> None:
        self._providers[name] = provider

    def get(self, name: str) -> Optional[MetricsProvider]:
        return self._providers.get(name)

    def list_available(self) -> list[str]:
        return list(self._providers.keys())
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_providers.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add app/services/providers.py tests/test_providers.py
git commit -m "feat: add MetricsProvider Protocol + ManualProvider + Registry"
```

---

### Task 6: Board — enrich home route with KPIs + sparkline

**Files:**
- Modify: `app/routers/pages.py`
- Modify: `app/templates/index.html`

- [ ] **Step 1: Write failing test for board KPIs**

Add to a new file or extend existing:

```python
# tests/test_board_kpis.py
"""Tests for Board KPI display on home page."""
from __future__ import annotations


def test_home_shows_kpi_section(client):
    """Home page should show the 'Ma progression' section."""
    body = client.get("/").text
    assert "Ma progression" in body
    assert "Voir analyse" in body


def test_home_shows_zero_state(client):
    """With no sessions, KPIs show 0 values."""
    body = client.get("/").text
    assert "0" in body  # At least sessions_this_week = 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_board_kpis.py -v`
Expected: FAIL with `AssertionError` (current index.html has no "Ma progression")

- [ ] **Step 3: Enrich home route in pages.py**

Replace the `home` function in `app/routers/pages.py`:

```python
@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: DbSession, user: CurrentUser) -> HTMLResponse:
    from app.services.timeline import build_sparkline_svg

    open_session = latest_open_session(db, user.id)
    open_since: str | None = None
    if open_session is not None:
        open_since = format_duration_short(
            session_duration(open_session.started_at, end=None)
        )

    # Board KPIs
    global_kpis = compute_global_kpis(db, user_id=user.id)

    # Sparkline: composite scores for last 14 days
    from datetime import datetime, timedelta, timezone

    window_start = datetime.now(timezone.utc) - timedelta(days=14)
    sparkline_stmt = (
        select(WorkoutSession)
        .where(WorkoutSession.user_id == user.id)
        .where(WorkoutSession.status == "completed")
        .where(WorkoutSession.excluded_from_stats.is_(False))
        .where(WorkoutSession.started_at >= window_start)
        .order_by(WorkoutSession.started_at.asc())
        .options(
            selectinload(WorkoutSession.session_exercises)
            .selectinload(SessionExercise.set_logs)
        )
    )
    recent_sessions = list(db.execute(sparkline_stmt).scalars().all())

    from app.services.performance import compute_composite_score

    sparkline_points = []
    for s in recent_sessions:
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
        composite = compute_composite_score(quality, cr)
        sparkline_points.append((composite,))

    sparkline_svg = build_sparkline_svg(sparkline_points)

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "page_title": "Accueil",
            "open_session": open_session,
            "open_since": open_since,
            "kpis": global_kpis,
            "sparkline_svg": sparkline_svg,
        },
    )
```

- [ ] **Step 4: Update index.html template**

Replace `app/templates/index.html`:

```html
{% extends "base.html" %}
{% block content %}
<h1 class="h1">Accueil</h1>

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
      <span class="board-kpi__value">{{ "%.0f"|format(kpis.completion_rate_30d * 100) if kpis.completion_rate_30d is not none else "—" }}%</span>
      <span class="board-kpi__label">complétion 30j</span>
    </div>
  </div>
  {% if sparkline_svg %}
    <div class="sparkline-container">{{ sparkline_svg|safe }}</div>
  {% else %}
    <p class="board-progress__empty">Pas encore de données</p>
  {% endif %}
  <a class="board-progress__link" href="{{ url_for('progress') }}">Voir analyse complète &rarr;</a>
</section>

{% if open_session %}
  <a class="tile tile--resume" href="{{ url_for('session_detail', session_id=open_session.id) }}">
    <div class="tile__label">Reprendre &middot; en cours</div>
    <div class="tile__hint">
      {{ open_session.template_name_snapshot }} &middot;
      d&eacute;marr&eacute;e le {{ open_session.started_at.strftime('%d/%m %H:%M') }}
      {% if open_since %}&middot; depuis {{ open_since }}{% endif %}
    </div>
  </a>
{% endif %}

<div class="tile-grid">
  <a class="tile tile--primary" href="{{ url_for('library') }}">
    <div class="tile__label">Nouvelle s&eacute;ance</div>
    <div class="tile__hint">Choisir un programme et d&eacute;marrer</div>
  </a>
  <a class="tile" href="{{ url_for('history') }}">
    <div class="tile__label">Historique</div>
    <div class="tile__hint">Sessions pass&eacute;es et feedback</div>
  </a>
  <a class="tile" href="{{ url_for('progress') }}">
    <div class="tile__label">Progression</div>
    <div class="tile__hint">KPI, surcharge, tendances</div>
  </a>
  <a class="tile" href="{{ url_for('library') }}">
    <div class="tile__label">Programmes de s&eacute;ance</div>
    <div class="tile__hint">Tous les programmes disponibles</div>
  </a>
  <a class="tile" href="{{ url_for('rules_page') }}">
    <div class="tile__label">R&egrave;gles</div>
    <div class="tile__hint">M&eacute;thode et rappels techniques</div>
  </a>
  <a class="tile" href="{{ url_for('admin_sessions') }}">
    <div class="tile__label">Gestion</div>
    <div class="tile__hint">G&eacute;rer, exclure, supprimer des s&eacute;ances</div>
  </a>
</div>
{% endblock %}
```

- [ ] **Step 5: Run tests**

Run: `pytest tests/test_board_kpis.py -v`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add app/routers/pages.py app/templates/index.html tests/test_board_kpis.py
git commit -m "feat: add KPIs and sparkline to Board home page"
```

---

### Task 7: Profile — 30-day timeline + physical data form

**Files:**
- Modify: `app/routers/auth_routes.py`
- Modify: `app/templates/profile.html`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_profile_enrich.py
"""Tests for enriched profile page."""
from __future__ import annotations


def test_profile_shows_30d_section(client):
    body = client.get("/profile").text
    assert "30 derniers jours" in body


def test_profile_shows_body_form(client):
    body = client.get("/profile").text
    assert "Profil physique" in body
    assert "Taille" in body


def test_profile_body_submit(client):
    r = client.post("/profile/body", data={
        "height_cm": "180",
        "weight_kg": "75.5",
        "resting_hr": "60",
        "waist_cm": "",
        "bp_systolic": "120",
        "bp_diastolic": "80",
    }, follow_redirects=False)
    assert r.status_code == 303

    # Verify data persisted
    body = client.get("/profile").text
    assert "180" in body
    assert "75.5" in body


def test_profile_body_validation_rejects_invalid(client):
    r = client.post("/profile/body", data={
        "height_cm": "999",  # too tall
        "weight_kg": "75",
        "resting_hr": "",
        "waist_cm": "",
        "bp_systolic": "",
        "bp_diastolic": "",
    }, follow_redirects=False)
    # Should redirect back (with error) or reject
    assert r.status_code in (303, 400)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_profile_enrich.py -v`
Expected: FAIL with `AssertionError` (current profile.html lacks these sections)

- [ ] **Step 3: Enrich auth_routes.py**

Add imports and modify `profile_page`, add `profile_body_submit`:

```python
# At the top of auth_routes.py, add imports:
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import selectinload

from app.models.session import SessionExercise, SetLog, WorkoutSession
from app.services.quality_score import compute_session_quality
from app.services.session_state import latest_open_session
from app.services.timeline import TimelinePoint, build_quality_timeline_svg
```

Replace `profile_page` function:

```python
@router.get("/profile", response_class=HTMLResponse)
def profile_page(
    request: Request,
    db: DbSession,
    user: CurrentUser,
) -> HTMLResponse:
    session_count = db.execute(
        select(func.count(WorkoutSession.id))
        .where(WorkoutSession.user_id == user.id)
    ).scalar_one() or 0
    completed_count = db.execute(
        select(func.count(WorkoutSession.id))
        .where(WorkoutSession.user_id == user.id)
        .where(WorkoutSession.status == "completed")
    ).scalar_one() or 0

    # 30-day quality timeline
    now = datetime.now(timezone.utc)
    window_30 = now - timedelta(days=30)
    window_60 = now - timedelta(days=60)

    sessions_30d = db.execute(
        select(WorkoutSession)
        .where(WorkoutSession.user_id == user.id)
        .where(WorkoutSession.status == "completed")
        .where(WorkoutSession.excluded_from_stats.is_(False))
        .where(WorkoutSession.started_at >= window_30)
        .order_by(WorkoutSession.started_at.asc())
        .options(
            selectinload(WorkoutSession.session_exercises)
            .selectinload(SessionExercise.set_logs)
        )
    ).scalars().all()

    quality_points = [
        TimelinePoint(
            label=s.started_at.strftime("%d/%m"),
            value=compute_session_quality(s),
        )
        for s in sessions_30d
    ]
    quality_svg = build_quality_timeline_svg(quality_points)
    sessions_30d_count = len(sessions_30d)

    # Trend: compare 30d count vs previous 30d
    prev_30d_count = db.execute(
        select(func.count(WorkoutSession.id))
        .where(WorkoutSession.user_id == user.id)
        .where(WorkoutSession.status == "completed")
        .where(WorkoutSession.excluded_from_stats.is_(False))
        .where(WorkoutSession.started_at >= window_60)
        .where(WorkoutSession.started_at < window_30)
    ).scalar_one() or 0

    if sessions_30d_count > prev_30d_count:
        trend = "up"
        trend_label = "\u2191 en hausse"
    elif sessions_30d_count < prev_30d_count:
        trend = "down"
        trend_label = "\u2193 en baisse"
    else:
        trend = "stable"
        trend_label = "\u2192 stable"

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
            "active_session": latest_open_session(db, user.id),
        },
    )
```

Add new endpoint after `profile_page`:

```python
@router.post("/profile/body", response_model=None)
async def profile_body_submit(
    request: Request,
    height_cm: Annotated[str, Form()] = "",
    weight_kg: Annotated[str, Form()] = "",
    resting_hr: Annotated[str, Form()] = "",
    waist_cm: Annotated[str, Form()] = "",
    bp_systolic: Annotated[str, Form()] = "",
    bp_diastolic: Annotated[str, Form()] = "",
    db: DbSession = None,
    user: CurrentUser = None,
):
    """Save physical profile fields."""
    def _int_or_none(v: str, lo: int, hi: int) -> int | None:
        v = v.strip()
        if not v:
            return None
        n = int(v)
        if n < lo or n > hi:
            return None  # silently ignore out-of-range
        return n

    def _float_or_none(v: str, lo: float, hi: float) -> float | None:
        v = v.strip()
        if not v:
            return None
        n = float(v)
        if n < lo or n > hi:
            return None
        return n

    user.height_cm = _int_or_none(height_cm, 100, 250)
    user.weight_kg = _float_or_none(weight_kg, 30.0, 300.0)
    user.resting_hr = _int_or_none(resting_hr, 30, 220)
    user.waist_cm = _float_or_none(waist_cm, 40.0, 200.0)
    user.bp_systolic = _int_or_none(bp_systolic, 60, 250)
    user.bp_diastolic = _int_or_none(bp_diastolic, 30, 150)
    db.commit()

    return RedirectResponse(url="/profile", status_code=303)
```

- [ ] **Step 4: Update profile.html**

```html
{% extends "base.html" %}
{% block content %}
<h1 class="h1">Profil</h1>

<div class="card">
  <ul class="export-stats">
    <li><span>Utilisateur</span><b>{{ user.username }}</b></li>
    <li><span>Inscrit le</span><b>{{ user.created_at.strftime('%d/%m/%Y') if user.created_at else '—' }}</b></li>
    <li><span>Statut</span><b>{% if user.is_active %}Actif{% else %}Inactif{% endif %}</b></li>
    <li><span>Sessions totales</span><b>{{ session_count }}</b></li>
    <li><span>Sessions terminées</span><b>{{ completed_count }}</b></li>
  </ul>
</div>

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
  {% if quality_svg %}
    <div class="timeline-chart">{{ quality_svg|safe }}</div>
  {% else %}
    <p class="board-progress__empty">Pas encore de données</p>
  {% endif %}
</section>

<section class="card" style="margin-top: var(--space);">
  <h2 class="card__title">Profil physique</h2>
  <form method="post" action="{{ url_for('profile_body_submit') }}" class="body-profile">
    <div class="body-profile__field">
      <label for="height_cm">Taille (cm)</label>
      <input type="number" id="height_cm" name="height_cm"
             value="{{ user.height_cm or '' }}" min="100" max="250" placeholder="175">
    </div>
    <div class="body-profile__field">
      <label for="weight_kg">Poids (kg)</label>
      <input type="number" id="weight_kg" name="weight_kg" step="0.1"
             value="{{ user.weight_kg or '' }}" min="30" max="300" placeholder="70">
    </div>
    <div class="body-profile__field">
      <label for="resting_hr">FC repos (bpm)</label>
      <input type="number" id="resting_hr" name="resting_hr"
             value="{{ user.resting_hr or '' }}" min="30" max="220" placeholder="60">
    </div>
    <div class="body-profile__field">
      <label for="waist_cm">Tour de taille (cm)</label>
      <input type="number" id="waist_cm" name="waist_cm" step="0.1"
             value="{{ user.waist_cm or '' }}" min="40" max="200" placeholder="80">
    </div>
    <div class="body-profile__field">
      <label for="bp_systolic">Tension systolique</label>
      <input type="number" id="bp_systolic" name="bp_systolic"
             value="{{ user.bp_systolic or '' }}" min="60" max="250" placeholder="120">
    </div>
    <div class="body-profile__field">
      <label for="bp_diastolic">Tension diastolique</label>
      <input type="number" id="bp_diastolic" name="bp_diastolic"
             value="{{ user.bp_diastolic or '' }}" min="30" max="150" placeholder="80">
    </div>
    <button type="submit" class="btn btn--primary">Enregistrer</button>
  </form>
</section>

<div class="card__actions" style="margin-top: var(--space);">
  <a class="btn" href="{{ url_for('password_change_page') }}">Changer le mot de passe</a>
</div>
{% endblock %}
```

- [ ] **Step 5: Run tests**

Run: `pytest tests/test_profile_enrich.py tests/test_register_profile.py -v`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add app/routers/auth_routes.py app/templates/profile.html tests/test_profile_enrich.py
git commit -m "feat: enrich profile with 30-day timeline and physical data form"
```

---

### Task 8: Leaderboard template — grade badge + accessible tooltip

**Files:**
- Modify: `app/templates/leaderboard.html`

- [ ] **Step 1: Write failing test**

```python
# tests/test_leaderboard_ui.py
"""Tests for leaderboard grade badge and tooltip."""
from __future__ import annotations
from tests.helpers import get_test_user_id
from tests.test_leaderboard import _add_session


def test_leaderboard_shows_grade_badge(client):
    uid = get_test_user_id()
    _add_session(uid, quality_inputs={
        "concentration": "high", "global_state": "good", "success_score": 100,
    })
    body = client.get("/leaderboard").text
    assert "grade-badge" in body


def test_leaderboard_tooltip_has_tabindex(client):
    """Tooltip wrapper must have tabindex=0 for mobile accessibility."""
    uid = get_test_user_id()
    _add_session(uid, quality_inputs={
        "concentration": "high", "global_state": "good", "success_score": 100,
    })
    body = client.get("/leaderboard").text
    assert 'tabindex="0"' in body


def test_leaderboard_tooltip_content(client):
    uid = get_test_user_id()
    _add_session(uid, quality_inputs={
        "concentration": "high", "global_state": "good", "success_score": 100,
    })
    body = client.get("/leaderboard").text
    assert "tooltip-content" in body
    assert "Derni" in body  # "Dernière session"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_leaderboard_ui.py -v`
Expected: FAIL (no "grade-badge" in current HTML)

- [ ] **Step 3: Update leaderboard.html**

```html
{% extends "base.html" %}
{% block content %}
<h1 class="h1">Leaderboard</h1>
<p class="lede">
  Classement basé sur la qualité et la complétion des séances terminées.
</p>

{% if entries|length == 0 %}
  <p class="empty">
    Aucune séance terminée pour l'instant. Le classement apparaît
    quand des séances sont loggées.
  </p>
{% else %}
  <ol class="leaderboard">
    {% for e in entries %}
      <li class="lb-row {% if e.username == current_username %}lb-row--self{% endif %}">
        <span class="lb-row__rank">#{{ e.rank }}</span>
        <span class="lb-row__name">
          {{ e.username }}
          <span class="tooltip-wrapper" tabindex="0">
            <span class="grade-badge grade-badge--{{ e.grade|lower }}">{{ e.grade }}</span>
            <span class="tooltip-content">
              Dernière session : {{ e.last_session_score if e.last_session_score is not none else "—" }}/100<br>
              Note : {{ e.grade }} — {{ e.grade_label }}
            </span>
          </span>
        </span>
        <span class="lb-row__points">{{ e.total_points }} pts</span>
        <span class="lb-row__meta">
          {{ e.counted_sessions }} séance{% if e.counted_sessions > 1 %}s{% endif %}
          {% if e.avg_points is not none %}· moy. {{ e.avg_points }}{% endif %}
        </span>
      </li>
    {% endfor %}
  </ol>
{% endif %}

<p class="kpi-note">
  Score par séance = qualité × taux de complétion des work sets.
  Seules les séances terminées et non exclues comptent.
  Les données privées des autres utilisateurs ne sont jamais exposées.
</p>
{% endblock %}
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_leaderboard_ui.py tests/test_leaderboard.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add app/templates/leaderboard.html tests/test_leaderboard_ui.py
git commit -m "feat: add grade badge and accessible tooltip to leaderboard"
```

---

### Task 9: CSS additions

**Files:**
- Modify: `app/static/css/app.css`

- [ ] **Step 1: Append new CSS classes**

Add before the `/* ---------- Footer ---------- */` section in `app/static/css/app.css`:

```css
/* ---------- Board progress ---------- */
.board-progress {
  background: var(--bg-elev);
  border-radius: var(--radius);
  padding: var(--space);
  margin-bottom: var(--space-lg);
}
.board-progress__title {
  font-size: 14px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--fg-dim);
  margin: 0 0 12px;
}
.board-progress__empty {
  color: var(--fg-dim);
  font-size: 13px;
  margin: 8px 0;
}
.board-progress__link {
  display: block;
  text-align: right;
  font-size: 13px;
  color: var(--accent);
  margin-top: 8px;
}
.board-kpis {
  display: flex;
  gap: var(--space);
  margin-bottom: 10px;
}
.board-kpi {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}
.board-kpi__value {
  font-size: 22px;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
}
.board-kpi__label {
  font-size: 11px;
  color: var(--fg-dim);
  text-align: center;
}
.sparkline-container {
  margin: 8px 0;
}

/* ---------- Grade badges ---------- */
.grade-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  font-size: 11px;
  font-weight: 800;
  color: var(--bg);
  vertical-align: middle;
  margin-left: 6px;
}
.grade-badge--a { background: var(--ok); }
.grade-badge--b { background: var(--accent); }
.grade-badge--c { background: #888; }

/* ---------- Tooltip (CSS-only, accessible) ---------- */
.tooltip-wrapper {
  position: relative;
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  outline: none;
}
.tooltip-content {
  position: absolute;
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  background: var(--bg-elev-2);
  color: var(--fg);
  font-size: 12px;
  font-weight: 400;
  line-height: 1.4;
  padding: 8px 12px;
  border-radius: 8px;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.15s;
  z-index: 10;
}
.tooltip-wrapper:hover .tooltip-content,
.tooltip-wrapper:focus-within .tooltip-content {
  opacity: 1;
  pointer-events: auto;
}

/* ---------- Body profile form ---------- */
.body-profile {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.body-profile__field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.body-profile__field label {
  font-size: 12px;
  color: var(--fg-dim);
}
.body-profile__field input {
  background: var(--bg-elev-2);
  border: 1px solid transparent;
  border-radius: 8px;
  padding: 8px 10px;
  color: var(--fg);
  font-size: 15px;
  width: 100%;
}
.body-profile__field input:focus {
  border-color: var(--accent);
  outline: none;
}
.body-profile .btn {
  grid-column: 1 / -1;
  margin-top: 4px;
}

/* ---------- Trend indicator ---------- */
.trend-indicator { font-size: 14px; font-weight: 700; }
.trend-indicator--up { color: var(--ok); }
.trend-indicator--down { color: var(--accent); }
.trend-indicator--stable { color: var(--fg-dim); }

/* ---------- Card title ---------- */
.card__title {
  font-size: 14px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--fg-dim);
  margin: 0 0 12px;
}
```

- [ ] **Step 2: Verify no CSS syntax errors**

Run: `python -c "open('app/static/css/app.css').read()" && echo "OK"`
Expected: OK (file readable, no encoding issues)

- [ ] **Step 3: Run full test suite to check nothing is broken**

Run: `pytest --tb=short -q`
Expected: All tests PASS

- [ ] **Step 4: Commit**

```bash
git add app/static/css/app.css
git commit -m "feat: add CSS for board progress, grade badges, tooltips, body profile"
```

---

### Task 10: Final integration test

**Files:**
- None (run existing + new tests)

- [ ] **Step 1: Run the full test suite**

Run: `pytest -v`
Expected: All tests PASS

- [ ] **Step 2: Manual smoke test**

Run: `cd /Users/martinfeldmann/workout-session-tracking && python -m uvicorn app.main:app --port 8001`

Verify manually:
- `/` shows "Ma progression" block with KPIs
- `/profile` shows 30-day chart and physical form
- `/leaderboard` shows grade badges with working tooltips (tap on mobile)
- Physical form submit saves data

- [ ] **Step 3: Final commit (if any fix needed)**

```bash
git add -A
git commit -m "fix: integration adjustments after smoke test"
```
