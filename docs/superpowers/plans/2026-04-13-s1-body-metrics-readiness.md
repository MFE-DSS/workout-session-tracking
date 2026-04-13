# S1 — Body Metrics + Readiness Lite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add lateralized body measurements (left/right arms, thighs + hip/neck) and daily readiness tracking (5 dimensions, 1-5 scale) — without breaking the existing session flow.

**Architecture:** One Alembic migration (body_measurements v2 + readiness_entries table). New ReadinessEntry model + service. Readiness widget on Home page (compact, above-fold). Body metrics in Profile (lateralized form). Physique dashboard adapted to use averaged lateralized values.

**Tech Stack:** SQLAlchemy 2.0, Alembic (batch_alter_table for SQLite), FastAPI, Jinja2, pytest + httpx

**Prerequisite:** S0 must be complete (catalog clean, all tests green).

---

## File Structure

| File | Responsibility |
|------|---------------|
| `migrations/versions/20260413_body_measurements_v2_readiness.py` | Schema migration: lateralize + add readiness table |
| `app/models/readiness.py` | ReadinessEntry SQLAlchemy model |
| `app/models/measurement.py` | Updated BodyMeasurement (lateralized + hip/neck) |
| `app/models/__init__.py` | Import readiness module |
| `app/services/readiness.py` | Readiness CRUD (save, get_today, get_history) |
| `app/services/measurements.py` | Updated labels/maps + avg helpers + compute_zone_measurement |
| `app/services/muscle_mapping.py` | Updated ZONE_MEASUREMENT |
| `app/services/muscle_scoring.py` | Use compute_zone_measurement instead of getattr |
| `app/routers/readiness.py` | POST /readiness route |
| `app/routers/pages.py` | Home (readiness widget), readiness history route |
| `app/routers/auth_routes.py` | Updated profile_measurements_submit |
| `app/templates/index.html` | Readiness widget |
| `app/templates/readiness_history.html` | Readiness history page |
| `app/templates/profile.html` | Lateralized measurement form |
| `tests/test_readiness.py` | Readiness model + service tests |
| `tests/test_readiness_routes.py` | Readiness route integration tests |
| `tests/test_measurements.py` | Updated for lateralized fields |
| `tests/test_muscle_scoring.py` | Updated for avg helpers |

---

### Task 1: ReadinessEntry Model

**Files:**
- Create: `app/models/readiness.py`
- Modify: `app/models/__init__.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_readiness.py`:

```python
"""Tests for readiness model and service."""
from __future__ import annotations

from datetime import date

import pytest


def test_readiness_model_exists():
    from app.models.readiness import ReadinessEntry
    assert ReadinessEntry.__tablename__ == "readiness_entries"


def test_readiness_has_recorded_on_field():
    from app.models.readiness import ReadinessEntry
    assert hasattr(ReadinessEntry, "recorded_on")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_readiness.py -v`
Expected: FAIL (module not found)

- [ ] **Step 3: Create the ReadinessEntry model**

Create `app/models/readiness.py`:

```python
"""Daily readiness self-assessment.

One entry per user per calendar day. All subjective fields use a
1-5 scale where 5 is always the best state. The unique constraint
on (user_id, recorded_on) is DB-enforced.
"""
from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ReadinessEntry(Base):
    __tablename__ = "readiness_entries"
    __table_args__ = (
        UniqueConstraint("user_id", "recorded_on", name="uq_readiness_user_day"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    recorded_on: Mapped[date] = mapped_column(Date, nullable=False)
    sleep_quality: Mapped[int] = mapped_column(Integer, nullable=False)
    fatigue_level: Mapped[int] = mapped_column(Integer, nullable=False)
    soreness_level: Mapped[int] = mapped_column(Integer, nullable=False)
    stress_level: Mapped[int] = mapped_column(Integer, nullable=False)
    motivation_level: Mapped[int] = mapped_column(Integer, nullable=False)
    resting_hr: Mapped[int | None] = mapped_column(Integer, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
```

- [ ] **Step 4: Register the model in `__init__.py`**

Modify `app/models/__init__.py`:

```python
"""ORM models package.

Import submodules here so that `Base.metadata` is populated as soon as the
package is imported (used by `init_db` and Alembic autogenerate later).
"""
from app.models import catalog, measurement, readiness, session, user  # noqa: F401
```

Also verify `app/database.py` imports: check if it imports `measurement` already — it does (line 62). Add `readiness` there too:

```python
from app.models import catalog, measurement, readiness, session  # noqa: F401
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_readiness.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add app/models/readiness.py app/models/__init__.py tests/test_readiness.py
git commit -m "feat(s1): add ReadinessEntry model — 1-5 scale, recorded_on DATE, unique per user/day"
```

---

### Task 2: Alembic Migration

**Files:**
- Create: `migrations/versions/20260413_body_measurements_v2_readiness.py`

- [ ] **Step 1: Create the migration**

Create `migrations/versions/20260413_body_measurements_v2_readiness.py`:

```python
"""Body measurements v2 (lateralized) + readiness_entries table.

Revision ID: a1b2c3d4e5f6
Revises: <FILL_IN_HEAD_REVISION>
Create Date: 2026-04-13
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "a1b2c3d4e5f6"
down_revision = "<FILL_IN_HEAD_REVISION>"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- 1. Create readiness_entries table ---
    op.create_table(
        "readiness_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recorded_on", sa.Date(), nullable=False),
        sa.Column("sleep_quality", sa.Integer(), nullable=False),
        sa.Column("fatigue_level", sa.Integer(), nullable=False),
        sa.Column("soreness_level", sa.Integer(), nullable=False),
        sa.Column("stress_level", sa.Integer(), nullable=False),
        sa.Column("motivation_level", sa.Integer(), nullable=False),
        sa.Column("resting_hr", sa.Integer(), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "recorded_on", name="uq_readiness_user_day"),
    )
    op.create_index("ix_readiness_user_date", "readiness_entries", ["user_id", "recorded_on"])

    # --- 2. Lateralize body_measurements ---
    # SQLite requires batch mode for column operations
    with op.batch_alter_table("body_measurements") as batch_op:
        # Add new columns
        batch_op.add_column(sa.Column("arm_cm_left", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("arm_cm_right", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("thigh_cm_left", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("thigh_cm_right", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("hip_cm", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("neck_cm", sa.Float(), nullable=True))

    # Copy existing data to both sides
    op.execute("UPDATE body_measurements SET arm_cm_left = arm_cm, arm_cm_right = arm_cm")
    op.execute("UPDATE body_measurements SET thigh_cm_left = thigh_cm, thigh_cm_right = thigh_cm")

    # Drop old columns (batch mode for SQLite)
    with op.batch_alter_table("body_measurements") as batch_op:
        batch_op.drop_column("arm_cm")
        batch_op.drop_column("thigh_cm")


def downgrade() -> None:
    with op.batch_alter_table("body_measurements") as batch_op:
        batch_op.add_column(sa.Column("arm_cm", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("thigh_cm", sa.Float(), nullable=True))

    # Copy left side back as the canonical value
    op.execute("UPDATE body_measurements SET arm_cm = arm_cm_left")
    op.execute("UPDATE body_measurements SET thigh_cm = thigh_cm_left")

    with op.batch_alter_table("body_measurements") as batch_op:
        batch_op.drop_column("arm_cm_left")
        batch_op.drop_column("arm_cm_right")
        batch_op.drop_column("thigh_cm_left")
        batch_op.drop_column("thigh_cm_right")
        batch_op.drop_column("hip_cm")
        batch_op.drop_column("neck_cm")

    op.drop_index("ix_readiness_user_date", "readiness_entries")
    op.drop_table("readiness_entries")
```

**Important:** Before creating this file, run `alembic heads` to get the current head revision and fill in `down_revision`. The current head should be the `20260413_add_catalog_section` migration.

- [ ] **Step 2: Update the BodyMeasurement model**

Modify `app/models/measurement.py`:

```python
"""Body measurement time-series tracking.

Each row is one measurement session — the user fills in whichever
fields they measured that day. All measurement fields are nullable
to allow partial entries.

Lateralized fields (arm, thigh) store left/right independently.
The averaged values used by the physique dashboard are derived views,
not stored columns.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class BodyMeasurement(Base):
    __tablename__ = "body_measurements"
    __table_args__ = (
        Index("ix_body_measurements_user_date", "user_id", "measured_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    measured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    chest_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    arm_cm_left: Mapped[float | None] = mapped_column(Float, nullable=True)
    arm_cm_right: Mapped[float | None] = mapped_column(Float, nullable=True)
    waist_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    thigh_cm_left: Mapped[float | None] = mapped_column(Float, nullable=True)
    thigh_cm_right: Mapped[float | None] = mapped_column(Float, nullable=True)
    hip_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    neck_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    calf_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
```

- [ ] **Step 3: Run the migration**

Run: `alembic upgrade head`
Expected: Migration applies successfully. Both the readiness_entries table is created and body_measurements is lateralized.

- [ ] **Step 4: Verify migration**

Run: `python -c "from app.database import SessionLocal; db = SessionLocal(); print('OK'); db.close()"`
Expected: No errors.

- [ ] **Step 5: Commit**

```bash
git add migrations/versions/20260413_body_measurements_v2_readiness.py app/models/measurement.py
git commit -m "feat(s1): migration — lateralize body measurements + create readiness_entries"
```

---

### Task 3: Measurement Service — Avg Helpers + Zone Measurement

**Files:**
- Modify: `app/services/measurements.py`
- Modify: `tests/test_measurements.py`

- [ ] **Step 1: Write failing tests for avg helpers**

Add to `tests/test_measurements.py`:

```python
from app.services.measurements import (
    compute_arm_avg,
    compute_thigh_avg,
    compute_zone_measurement,
)


def test_compute_arm_avg_both_sides():
    class FakeMeasurement:
        arm_cm_left = 35.0
        arm_cm_right = 36.0
    assert compute_arm_avg(FakeMeasurement()) == 35.5


def test_compute_arm_avg_left_only():
    class FakeMeasurement:
        arm_cm_left = 35.0
        arm_cm_right = None
    assert compute_arm_avg(FakeMeasurement()) == 35.0


def test_compute_arm_avg_none():
    class FakeMeasurement:
        arm_cm_left = None
        arm_cm_right = None
    assert compute_arm_avg(FakeMeasurement()) is None


def test_compute_thigh_avg_both_sides():
    class FakeMeasurement:
        thigh_cm_left = 58.0
        thigh_cm_right = 59.0
    assert compute_thigh_avg(FakeMeasurement()) == 58.5


def test_compute_zone_measurement_pecs():
    class FakeMeasurement:
        chest_cm = 100.0
    assert compute_zone_measurement(FakeMeasurement(), "pecs") == 100.0


def test_compute_zone_measurement_biceps():
    class FakeMeasurement:
        arm_cm_left = 35.0
        arm_cm_right = 36.0
    assert compute_zone_measurement(FakeMeasurement(), "biceps") == 35.5


def test_compute_zone_measurement_unknown_zone():
    class FakeMeasurement:
        pass
    assert compute_zone_measurement(FakeMeasurement(), "delt_lat") is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_measurements.py::test_compute_arm_avg_both_sides -v`
Expected: FAIL (ImportError — function doesn't exist yet)

- [ ] **Step 3: Update measurements service**

Rewrite `app/services/measurements.py`:

```python
"""Body measurement CRUD, muscle-template mapping, and zone measurement helpers.

Provides time-series storage for body measurements and a static
mapping from measurement fields to muscle groups. Zone measurement
helpers compute derived values (averages) for the physique dashboard.

Source of truth: lateralized columns (arm_cm_left/right, thigh_cm_left/right).
Averaged values are derived views for backward compatibility.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.measurement import BodyMeasurement


MEASUREMENT_MUSCLE_MAP: dict[str, list[str]] = {
    "weight_kg": [],
    "chest_cm": ["pectoral", "pectoraux", "pecs"],
    "arm_cm_left": ["biceps", "triceps", "bras"],
    "arm_cm_right": ["biceps", "triceps", "bras"],
    "waist_cm": ["abdos", "abs", "cardio"],
    "thigh_cm_left": ["jambes", "quadriceps", "cuisses"],
    "thigh_cm_right": ["jambes", "quadriceps", "cuisses"],
    "hip_cm": [],
    "neck_cm": [],
    "calf_cm": ["mollets"],
}

MEASUREMENT_LABELS: dict[str, str] = {
    "weight_kg": "Poids (kg)",
    "chest_cm": "Tour de poitrine (cm)",
    "arm_cm_left": "Bras gauche (cm)",
    "arm_cm_right": "Bras droit (cm)",
    "waist_cm": "Tour de taille (cm)",
    "thigh_cm_left": "Cuisse gauche (cm)",
    "thigh_cm_right": "Cuisse droite (cm)",
    "hip_cm": "Tour de hanches (cm)",
    "neck_cm": "Tour de cou (cm)",
    "calf_cm": "Tour de mollet (cm)",
}

MEASUREMENT_UNITS: dict[str, str] = {
    "weight_kg": " kg",
    "chest_cm": " cm",
    "arm_cm_left": " cm",
    "arm_cm_right": " cm",
    "waist_cm": " cm",
    "thigh_cm_left": " cm",
    "thigh_cm_right": " cm",
    "hip_cm": " cm",
    "neck_cm": " cm",
    "calf_cm": " cm",
}

MEASUREMENT_FIELDS = list(MEASUREMENT_LABELS.keys())


# --- Avg helpers (derived views, NOT source of truth) ---


def compute_arm_avg(m) -> float | None:
    """Average of left/right arm. Single side if only one. None if neither."""
    left = getattr(m, "arm_cm_left", None)
    right = getattr(m, "arm_cm_right", None)
    if left is not None and right is not None:
        return (left + right) / 2
    return left or right


def compute_thigh_avg(m) -> float | None:
    """Average of left/right thigh. Single side if only one. None if neither."""
    left = getattr(m, "thigh_cm_left", None)
    right = getattr(m, "thigh_cm_right", None)
    if left is not None and right is not None:
        return (left + right) / 2
    return left or right


# Zone -> measurement resolution
_ZONE_DIRECT: dict[str, str] = {
    "pecs": "chest_cm",
    "core": "waist_cm",
}

_ZONE_LATERALIZED: dict[str, str] = {
    "biceps": "arm",
    "triceps": "arm",
    "quads": "thigh",
    "posterior": "thigh",
}


def compute_zone_measurement(m, zone: str) -> float | None:
    """Resolve a zone to a measurement value.

    Direct zones (pecs, core): return the column value.
    Lateralized zones (biceps, triceps, quads, posterior): return avg of left/right.
    Other zones (delt_lat, lats, etc.): return None (no measurement mapping).
    """
    if zone in _ZONE_DIRECT:
        return getattr(m, _ZONE_DIRECT[zone], None)
    if zone in _ZONE_LATERALIZED:
        limb = _ZONE_LATERALIZED[zone]
        if limb == "arm":
            return compute_arm_avg(m)
        elif limb == "thigh":
            return compute_thigh_avg(m)
    return None


def find_related_templates(field_name: str, templates: list) -> list[str]:
    """Find catalog templates whose focus matches a measurement's muscle group."""
    keywords = MEASUREMENT_MUSCLE_MAP.get(field_name, [])
    if not keywords:
        return []
    result = []
    for t in templates:
        focus_lower = (t.focus or "").lower()
        if any(kw in focus_lower for kw in keywords):
            result.append(t.name)
    return result


def get_latest_measurement(
    db: Session, user_id: int
) -> Optional[BodyMeasurement]:
    """Return the most recent measurement for a user."""
    return db.execute(
        select(BodyMeasurement)
        .where(BodyMeasurement.user_id == user_id)
        .order_by(BodyMeasurement.measured_at.desc())
        .limit(1)
    ).scalar_one_or_none()


def get_measurement_series(
    db: Session, user_id: int, field: str, limit: int = 20
) -> list[tuple[datetime, float]]:
    """Return (measured_at, value) pairs for one field, non-null only, ASC."""
    col = getattr(BodyMeasurement, field, None)
    if col is None:
        return []
    rows = db.execute(
        select(BodyMeasurement.measured_at, col)
        .where(BodyMeasurement.user_id == user_id)
        .where(col.is_not(None))
        .order_by(BodyMeasurement.measured_at.asc())
        .limit(limit)
    ).all()
    return [(r[0], r[1]) for r in rows]
```

- [ ] **Step 4: Update existing tests in test_measurements.py**

Replace the old field-set tests at the top of the file:

```python
def test_muscle_map_has_all_fields():
    assert "weight_kg" in MEASUREMENT_MUSCLE_MAP
    assert "arm_cm_left" in MEASUREMENT_MUSCLE_MAP
    assert "arm_cm_right" in MEASUREMENT_MUSCLE_MAP
    assert "thigh_cm_left" in MEASUREMENT_MUSCLE_MAP
    assert "thigh_cm_right" in MEASUREMENT_MUSCLE_MAP
    assert "hip_cm" in MEASUREMENT_MUSCLE_MAP
    assert "neck_cm" in MEASUREMENT_MUSCLE_MAP


def test_labels_has_all_fields():
    assert set(MEASUREMENT_LABELS.keys()) == set(MEASUREMENT_MUSCLE_MAP.keys())
```

Also update the import at the top of the file to include the new functions:
```python
from app.services.measurements import (
    MEASUREMENT_LABELS,
    MEASUREMENT_MUSCLE_MAP,
    compute_arm_avg,
    compute_thigh_avg,
    compute_zone_measurement,
    find_related_templates,
    get_latest_measurement,
    get_measurement_series,
)
```

Update test fixtures that create BodyMeasurement instances — change `arm_cm=X` to `arm_cm_left=X, arm_cm_right=X` and `thigh_cm=X` to `thigh_cm_left=X, thigh_cm_right=X`.

- [ ] **Step 5: Run tests**

Run: `pytest tests/test_measurements.py -v`
Expected: All tests PASS.

- [ ] **Step 6: Commit**

```bash
git add app/services/measurements.py tests/test_measurements.py
git commit -m "feat(s1): measurement service — lateralized labels, avg helpers, compute_zone_measurement"
```

---

### Task 4: Adapt Muscle Mapping + Scoring for Lateralized Measurements

**Files:**
- Modify: `app/services/muscle_mapping.py`
- Modify: `app/services/muscle_scoring.py`
- Modify: `tests/test_muscle_scoring.py`

- [ ] **Step 1: Update ZONE_MEASUREMENT in muscle_mapping.py**

In `app/services/muscle_mapping.py`, replace the `ZONE_MEASUREMENT` dict:

```python
ZONE_MEASUREMENT: dict[str, str | None] = {
    "pecs": "chest_cm",
    "delt_lat": None,
    "delt_post": None,
    "lats": None,
    "upper_back": None,
    "biceps": "arm_avg",
    "triceps": "arm_avg",
    "quads": "thigh_avg",
    "posterior": "thigh_avg",
    "calves": None,
    "core": "waist_cm",
}
```

Note: The string values are now semantic keys, not direct column names. `muscle_scoring.py` will use `compute_zone_measurement()` instead of `getattr()`.

- [ ] **Step 2: Update _score_anthropo in muscle_scoring.py**

In `app/services/muscle_scoring.py`, replace the `_score_anthropo` function (lines 159-206):

```python
def _score_anthropo(
    db: Session, user_id: int, zone: str, window_start: datetime
) -> tuple[float | None, str | None]:
    """Score anthropometry for a zone. Returns (score, trend_label) or (None, None)."""
    from app.services.measurements import compute_zone_measurement

    field_name = ZONE_MEASUREMENT.get(zone)
    if not field_name:
        return None, None

    # Get measurements in window
    rows = db.execute(
        select(BodyMeasurement)
        .where(BodyMeasurement.user_id == user_id)
        .where(BodyMeasurement.measured_at >= window_start)
        .order_by(BodyMeasurement.measured_at.asc())
    ).scalars().all()

    # Compute zone value for each measurement
    values = []
    for m in rows:
        val = compute_zone_measurement(m, zone)
        if val is not None:
            values.append((m.measured_at, val))

    if len(values) < 2:
        return None, None

    first_val = values[0][1]
    last_val = values[-1][1]
    diff = last_val - first_val

    # For waist_cm (core zone), decrease is positive
    is_inverse = zone == "core"
    if is_inverse:
        diff = -diff

    if first_val == 0:
        return 50.0, f"{diff:+.1f} cm"

    pct_change = diff / first_val * 100

    if pct_change <= -2:
        score = 30.0
    elif pct_change <= 0.5:
        score = 50.0
    elif pct_change <= 2:
        score = 70.0
    else:
        score = 90.0

    sign = "+" if diff > 0 else ""
    label = f"{sign}{diff:.1f} cm"

    return score, label
```

- [ ] **Step 3: Update measurement label lookup in muscle_scoring.py**

In `app/services/muscle_scoring.py`, around line 300-302, update the measurement label lookup:

Replace:
```python
        meas_field = ZONE_MEASUREMENT.get(zone)
        from app.services.measurements import MEASUREMENT_LABELS
        meas_label = MEASUREMENT_LABELS.get(meas_field) if meas_field else None
```

With:
```python
        meas_field = ZONE_MEASUREMENT.get(zone)
        meas_label = None
        if meas_field:
            _ZONE_DISPLAY_LABELS = {
                "chest_cm": "Tour de poitrine",
                "arm_avg": "Tour de bras (moy.)",
                "thigh_avg": "Tour de cuisses (moy.)",
                "waist_cm": "Tour de taille",
            }
            meas_label = _ZONE_DISPLAY_LABELS.get(meas_field)
```

- [ ] **Step 4: Run scoring tests**

Run: `pytest tests/test_muscle_scoring.py -v`
Expected: All tests PASS.

- [ ] **Step 5: Run full test suite**

Run: `pytest -x -q`
Expected: All tests pass (including physique dashboard integration tests).

- [ ] **Step 6: Commit**

```bash
git add app/services/muscle_mapping.py app/services/muscle_scoring.py
git commit -m "feat(s1): adapt muscle scoring for lateralized measurements — compute_zone_measurement"
```

---

### Task 5: Readiness Service

**Files:**
- Create: `app/services/readiness.py`
- Modify: `tests/test_readiness.py`

- [ ] **Step 1: Write failing tests for readiness service**

Add to `tests/test_readiness.py`:

```python
from datetime import date

from tests.helpers import get_test_user_id


def test_save_and_get_today(client):
    from app.database import SessionLocal
    from app.services.readiness import save_readiness, get_today_readiness

    uid = get_test_user_id()
    data = {
        "sleep_quality": 4,
        "fatigue_level": 3,
        "soreness_level": 5,
        "stress_level": 4,
        "motivation_level": 5,
    }
    with SessionLocal() as db:
        entry = save_readiness(db, uid, data)
        assert entry.sleep_quality == 4
        assert entry.recorded_on == date.today()

    with SessionLocal() as db:
        today = get_today_readiness(db, uid)
        assert today is not None
        assert today.motivation_level == 5


def test_upsert_same_day(client):
    from app.database import SessionLocal
    from app.services.readiness import save_readiness, get_today_readiness

    uid = get_test_user_id()
    data1 = {
        "sleep_quality": 3,
        "fatigue_level": 3,
        "soreness_level": 3,
        "stress_level": 3,
        "motivation_level": 3,
    }
    data2 = {
        "sleep_quality": 5,
        "fatigue_level": 5,
        "soreness_level": 5,
        "stress_level": 5,
        "motivation_level": 5,
        "resting_hr": 55,
        "note": "Feeling great",
    }
    with SessionLocal() as db:
        save_readiness(db, uid, data1)
    with SessionLocal() as db:
        save_readiness(db, uid, data2)
    with SessionLocal() as db:
        today = get_today_readiness(db, uid)
        assert today.sleep_quality == 5
        assert today.resting_hr == 55
        assert today.note == "Feeling great"


def test_get_readiness_history(client):
    from datetime import timedelta
    from app.database import SessionLocal
    from app.models.readiness import ReadinessEntry
    from app.services.readiness import get_readiness_history

    uid = get_test_user_id()
    with SessionLocal() as db:
        for i in range(5):
            db.add(ReadinessEntry(
                user_id=uid,
                recorded_on=date.today() - timedelta(days=i),
                sleep_quality=3,
                fatigue_level=3,
                soreness_level=3,
                stress_level=3,
                motivation_level=3,
            ))
        db.commit()

    with SessionLocal() as db:
        history = get_readiness_history(db, uid, days=30)
    assert len(history) >= 5
    # Most recent first
    assert history[0].recorded_on >= history[-1].recorded_on


def test_reject_invalid_scale(client):
    import pytest
    from app.database import SessionLocal
    from app.services.readiness import save_readiness

    uid = get_test_user_id()
    data = {
        "sleep_quality": 0,  # invalid: must be 1-5
        "fatigue_level": 3,
        "soreness_level": 3,
        "stress_level": 3,
        "motivation_level": 6,  # invalid
    }
    with SessionLocal() as db:
        with pytest.raises(ValueError):
            save_readiness(db, uid, data)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_readiness.py::test_save_and_get_today -v`
Expected: FAIL (ImportError)

- [ ] **Step 3: Create the readiness service**

Create `app/services/readiness.py`:

```python
"""Readiness CRUD — one entry per user per calendar day.

All subjective fields use a 1-5 scale where 5 is always the best state.
"""
from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.readiness import ReadinessEntry

SCALE_FIELDS = [
    "sleep_quality",
    "fatigue_level",
    "soreness_level",
    "stress_level",
    "motivation_level",
]

READINESS_LABELS: dict[str, dict[int, str]] = {
    "sleep_quality": {1: "Très mauvais", 2: "Mauvais", 3: "Correct", 4: "Bon", 5: "Excellent"},
    "fatigue_level": {1: "Épuisé", 2: "Fatigué", 3: "Normal", 4: "En forme", 5: "Très frais"},
    "soreness_level": {1: "Très douloureux", 2: "Douloureux", 3: "Modéré", 4: "Léger", 5: "Aucune douleur"},
    "stress_level": {1: "Très stressé", 2: "Stressé", 3: "Moyen", 4: "Détendu", 5: "Très détendu"},
    "motivation_level": {1: "Aucune", 2: "Faible", 3: "Normale", 4: "Bonne", 5: "Très motivé"},
}

READINESS_FIELD_LABELS: dict[str, str] = {
    "sleep_quality": "Sommeil",
    "fatigue_level": "Fatigue",
    "soreness_level": "Courbatures",
    "stress_level": "Stress",
    "motivation_level": "Motivation",
}


def _validate_scale(data: dict) -> None:
    """Raise ValueError if any scale field is out of 1-5 range."""
    for field in SCALE_FIELDS:
        val = data.get(field)
        if val is None or not isinstance(val, int) or val < 1 or val > 5:
            raise ValueError(f"{field} must be an integer 1-5, got {val!r}")


def save_readiness(db: Session, user_id: int, data: dict) -> ReadinessEntry:
    """Upsert readiness for today. Raises ValueError on invalid scale values."""
    _validate_scale(data)

    today = date.today()

    existing = db.execute(
        select(ReadinessEntry)
        .where(ReadinessEntry.user_id == user_id)
        .where(ReadinessEntry.recorded_on == today)
    ).scalar_one_or_none()

    if existing:
        for field in SCALE_FIELDS:
            setattr(existing, field, data[field])
        existing.resting_hr = data.get("resting_hr")
        existing.note = data.get("note")
        db.commit()
        return existing

    entry = ReadinessEntry(
        user_id=user_id,
        recorded_on=today,
        sleep_quality=data["sleep_quality"],
        fatigue_level=data["fatigue_level"],
        soreness_level=data["soreness_level"],
        stress_level=data["stress_level"],
        motivation_level=data["motivation_level"],
        resting_hr=data.get("resting_hr"),
        note=data.get("note"),
    )
    db.add(entry)
    db.commit()
    return entry


def get_today_readiness(db: Session, user_id: int) -> ReadinessEntry | None:
    """Return today's readiness entry, or None."""
    return db.execute(
        select(ReadinessEntry)
        .where(ReadinessEntry.user_id == user_id)
        .where(ReadinessEntry.recorded_on == date.today())
    ).scalar_one_or_none()


def get_readiness_history(
    db: Session, user_id: int, days: int = 30
) -> list[ReadinessEntry]:
    """Return readiness entries for the last N days, most recent first."""
    cutoff = date.today() - timedelta(days=days)
    return list(
        db.execute(
            select(ReadinessEntry)
            .where(ReadinessEntry.user_id == user_id)
            .where(ReadinessEntry.recorded_on >= cutoff)
            .order_by(ReadinessEntry.recorded_on.desc())
        ).scalars().all()
    )
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_readiness.py -v`
Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add app/services/readiness.py tests/test_readiness.py
git commit -m "feat(s1): readiness service — save, get_today, get_history, validation"
```

---

### Task 6: Readiness Router (POST /readiness)

**Files:**
- Create: `app/routers/readiness.py`
- Create: `tests/test_readiness_routes.py`

- [ ] **Step 1: Write failing route tests**

Create `tests/test_readiness_routes.py`:

```python
"""Integration tests for readiness routes."""
from __future__ import annotations


def test_post_readiness_saves_and_redirects(client):
    r = client.post("/readiness", data={
        "sleep_quality": "4",
        "fatigue_level": "3",
        "soreness_level": "5",
        "stress_level": "4",
        "motivation_level": "5",
    }, follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/"


def test_post_readiness_with_optional_fields(client):
    r = client.post("/readiness", data={
        "sleep_quality": "4",
        "fatigue_level": "3",
        "soreness_level": "5",
        "stress_level": "4",
        "motivation_level": "5",
        "resting_hr": "55",
        "note": "Good morning",
    }, follow_redirects=False)
    assert r.status_code == 303


def test_post_readiness_rejects_invalid_scale(client):
    r = client.post("/readiness", data={
        "sleep_quality": "0",
        "fatigue_level": "3",
        "soreness_level": "3",
        "stress_level": "3",
        "motivation_level": "3",
    }, follow_redirects=False)
    # Should redirect back to home (graceful error)
    assert r.status_code == 303


def test_post_readiness_requires_auth(client):
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()
    r = client.post("/readiness", data={
        "sleep_quality": "4",
        "fatigue_level": "3",
        "soreness_level": "3",
        "stress_level": "3",
        "motivation_level": "3",
    }, follow_redirects=False)
    assert r.status_code == 303


def test_readiness_history_page_renders(client):
    r = client.get("/readiness/history")
    assert r.status_code == 200
    assert "Readiness" in r.text or "readiness" in r.text.lower()


def test_readiness_history_requires_auth(client):
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()
    r = client.get("/readiness/history", follow_redirects=False)
    assert r.status_code == 303
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_readiness_routes.py::test_post_readiness_saves_and_redirects -v`
Expected: FAIL (404 — route doesn't exist)

- [ ] **Step 3: Create the readiness router**

Create `app/routers/readiness.py`:

```python
"""Readiness routes — daily self-assessment."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from app.deps import CurrentUser, DbSession
from app.services.readiness import save_readiness

router = APIRouter(tags=["readiness"])


@router.post("/readiness", response_model=None)
async def readiness_submit(
    request: Request,
    sleep_quality: Annotated[str, Form()] = "",
    fatigue_level: Annotated[str, Form()] = "",
    soreness_level: Annotated[str, Form()] = "",
    stress_level: Annotated[str, Form()] = "",
    motivation_level: Annotated[str, Form()] = "",
    resting_hr: Annotated[str, Form()] = "",
    note: Annotated[str, Form()] = "",
    db: DbSession = None,
    user: CurrentUser = None,
):
    """Save or update today's readiness entry."""
    def _int(v: str, lo: int, hi: int) -> int | None:
        v = v.strip()
        if not v:
            return None
        try:
            n = int(v)
        except ValueError:
            return None
        return n if lo <= n <= hi else None

    data = {
        "sleep_quality": _int(sleep_quality, 1, 5),
        "fatigue_level": _int(fatigue_level, 1, 5),
        "soreness_level": _int(soreness_level, 1, 5),
        "stress_level": _int(stress_level, 1, 5),
        "motivation_level": _int(motivation_level, 1, 5),
    }

    # If any required field is invalid, redirect back gracefully
    if any(v is None for v in data.values()):
        return RedirectResponse(url="/", status_code=303)

    hr = _int(resting_hr, 30, 200)
    if hr is not None:
        data["resting_hr"] = hr
    note_clean = note.strip() if note.strip() else None
    if note_clean:
        data["note"] = note_clean

    save_readiness(db, user.id, data)
    return RedirectResponse(url="/", status_code=303)
```

- [ ] **Step 4: Register the router in the app**

Find where routers are included (likely `app/main.py` or similar) and add:

```python
from app.routers.readiness import router as readiness_router
app.include_router(readiness_router)
```

- [ ] **Step 5: Run tests**

Run: `pytest tests/test_readiness_routes.py -v`
Expected: All PASS.

- [ ] **Step 6: Commit**

```bash
git add app/routers/readiness.py tests/test_readiness_routes.py
git commit -m "feat(s1): readiness router — POST /readiness with validation"
```

---

### Task 7: Readiness Widget on Home Page

**Files:**
- Modify: `app/routers/pages.py` (home route)
- Modify: `app/templates/index.html`

- [ ] **Step 1: Update the home route to pass readiness data**

In `app/routers/pages.py`, modify the `home` function. Add after the `behavioral` computation (around line 106):

```python
    from app.services.readiness import (
        get_today_readiness,
        READINESS_LABELS,
        READINESS_FIELD_LABELS,
        SCALE_FIELDS,
    )

    readiness_today = get_today_readiness(db, user.id)
```

And add to the template context dict:

```python
        "readiness_today": readiness_today,
        "readiness_labels": READINESS_LABELS,
        "readiness_field_labels": READINESS_FIELD_LABELS,
        "readiness_scale_fields": SCALE_FIELDS,
```

- [ ] **Step 2: Add readiness widget to index.html**

In `app/templates/index.html`, add the widget AFTER the open_session tile (line 14) and BEFORE the cockpit-grid (line 16). The widget must be compact — never push the session tile below the fold:

```html
{# Readiness widget — compact, above-fold, never pushes session action down #}
<div class="card readiness-widget" style="margin-bottom:var(--space-md);">
  {% if readiness_today %}
    <div style="display:flex;align-items:center;justify-content:space-between;gap:var(--space-sm);flex-wrap:wrap;">
      <span class="card__title" style="margin:0;font-size:14px;">Readiness</span>
      {% for field in readiness_scale_fields %}
        {% set val = readiness_today[field] %}
        <span class="badge badge--{% if val >= 4 %}good{% elif val >= 3 %}neutral{% else %}warn{% endif %}"
              title="{{ readiness_field_labels[field] }}: {{ readiness_labels[field][val] }}">
          {{ readiness_field_labels[field][:3] }} {{ val }}
        </span>
      {% endfor %}
      {% if readiness_today.resting_hr %}
        <span class="badge" title="FC repos">{{ readiness_today.resting_hr }} bpm</span>
      {% endif %}
      <a href="/readiness/history" class="text-muted" style="font-size:12px;">Historique →</a>
    </div>
  {% else %}
    <details>
      <summary class="card__title" style="cursor:pointer;font-size:14px;margin:0;">
        Readiness du jour
      </summary>
      <form method="post" action="/readiness" style="margin-top:var(--space-sm);">
        {% for field in readiness_scale_fields %}
        <div style="margin-bottom:var(--space-xs);">
          <label style="font-size:13px;display:block;margin-bottom:2px;">{{ readiness_field_labels[field] }}</label>
          <div class="segmented">
            {% for val in [1, 2, 3, 4, 5] %}
            <label class="segmented__option">
              <input type="radio" name="{{ field }}" value="{{ val }}" {% if val == 3 %}checked{% endif %}>
              <span title="{{ readiness_labels[field][val] }}">{{ val }}</span>
            </label>
            {% endfor %}
          </div>
        </div>
        {% endfor %}
        <div style="display:flex;gap:var(--space-sm);margin-top:var(--space-sm);">
          <input type="number" name="resting_hr" placeholder="FC repos (bpm)" min="30" max="200"
                 style="flex:1;max-width:150px;">
          <input type="text" name="note" placeholder="Note (optionnel)" style="flex:2;">
        </div>
        <button type="submit" class="btn btn--ghost" style="margin-top:var(--space-sm);width:100%;">Enregistrer</button>
      </form>
    </details>
  {% endif %}
</div>
```

- [ ] **Step 3: Verify the home page renders**

Run: `pytest tests/test_board_behavioral.py -v` (or whatever tests verify home page rendering)
Expected: PASS. Also manually verify if dev server is available: `GET /` should show the readiness widget.

- [ ] **Step 4: Commit**

```bash
git add app/routers/pages.py app/templates/index.html
git commit -m "feat(s1): readiness widget on Home — compact, collapsible form, badge summary"
```

---

### Task 8: Readiness History Page

**Files:**
- Create: `app/templates/readiness_history.html`
- Modify: `app/routers/pages.py` (add history route)

- [ ] **Step 1: Add the history route**

In `app/routers/pages.py`, add a new route:

```python
@router.get("/readiness/history", response_class=HTMLResponse)
def readiness_history(
    request: Request, db: DbSession, user: CurrentUser
) -> HTMLResponse:
    from app.services.readiness import (
        get_readiness_history,
        READINESS_LABELS,
        READINESS_FIELD_LABELS,
        SCALE_FIELDS,
    )

    entries = get_readiness_history(db, user.id, days=90)

    return templates.TemplateResponse(
        request,
        "readiness_history.html",
        {
            "page_title": "Historique Readiness",
            "entries": entries,
            "readiness_labels": READINESS_LABELS,
            "readiness_field_labels": READINESS_FIELD_LABELS,
            "readiness_scale_fields": SCALE_FIELDS,
        },
    )
```

- [ ] **Step 2: Create the template**

Create `app/templates/readiness_history.html`:

```html
{% extends "base.html" %}
{% block content %}
<h1 class="page-title">Historique Readiness</h1>

{% if not entries %}
  <p class="text-dim">Aucune entrée de readiness pour les 90 derniers jours.</p>
{% else %}
  <div class="card-list">
    {% for entry in entries %}
    <div class="card" style="margin-bottom:var(--space-sm);">
      <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:var(--space-xs);">
        <b style="font-size:14px;">{{ entry.recorded_on.strftime('%d/%m/%Y') }}</b>
        {% for field in readiness_scale_fields %}
          {% set val = entry[field] %}
          <span class="badge badge--{% if val >= 4 %}good{% elif val >= 3 %}neutral{% else %}warn{% endif %}"
                title="{{ readiness_field_labels[field] }}: {{ readiness_labels[field][val] }}">
            {{ readiness_field_labels[field][:3] }} {{ val }}
          </span>
        {% endfor %}
        {% if entry.resting_hr %}
          <span class="badge">{{ entry.resting_hr }} bpm</span>
        {% endif %}
      </div>
      {% if entry.note %}
        <p class="text-dim" style="font-size:13px;margin-top:var(--space-xs);">{{ entry.note }}</p>
      {% endif %}
    </div>
    {% endfor %}
  </div>
{% endif %}

<a class="btn btn--ghost" href="/" style="margin-top:var(--space-md);display:inline-block;">← Retour</a>
{% endblock %}
```

- [ ] **Step 3: Run route tests**

Run: `pytest tests/test_readiness_routes.py::test_readiness_history_page_renders -v`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add app/templates/readiness_history.html app/routers/pages.py
git commit -m "feat(s1): readiness history page — /readiness/history with badge list"
```

---

### Task 9: Update Profile — Lateralized Body Metrics Form

**Files:**
- Modify: `app/templates/profile.html`
- Modify: `app/routers/auth_routes.py` (profile_measurements_submit)

- [ ] **Step 1: Update the profile_measurements_submit route**

In `app/routers/auth_routes.py`, replace the `profile_measurements_submit` function (line 477+). Change the form parameters and body:

Replace the old Form parameters:
```python
    arm_cm: Annotated[str, Form()] = "",
    waist_cm: Annotated[str, Form()] = "",
    thigh_cm: Annotated[str, Form()] = "",
```

With:
```python
    arm_cm_left: Annotated[str, Form()] = "",
    arm_cm_right: Annotated[str, Form()] = "",
    waist_cm: Annotated[str, Form()] = "",
    thigh_cm_left: Annotated[str, Form()] = "",
    thigh_cm_right: Annotated[str, Form()] = "",
    hip_cm: Annotated[str, Form()] = "",
    neck_cm: Annotated[str, Form()] = "",
    calf_cm: Annotated[str, Form()] = "",
```

Update the parsing and assignment logic to use the new field names:

```python
    weight = _float_or_none(weight_kg, 30.0, 300.0)
    chest = _float_or_none(chest_cm, 10.0, 200.0)
    arm_l = _float_or_none(arm_cm_left, 10.0, 100.0)
    arm_r = _float_or_none(arm_cm_right, 10.0, 100.0)
    waist = _float_or_none(waist_cm, 10.0, 200.0)
    thigh_l = _float_or_none(thigh_cm_left, 10.0, 100.0)
    thigh_r = _float_or_none(thigh_cm_right, 10.0, 100.0)
    hip = _float_or_none(hip_cm, 10.0, 200.0)
    neck = _float_or_none(neck_cm, 10.0, 100.0)
    calf = _float_or_none(calf_cm, 10.0, 100.0)

    # Skip if all measurement fields are empty
    all_none = all(v is None for v in [
        weight, chest, arm_l, arm_r, waist, thigh_l, thigh_r, hip, neck, calf
    ])
    if all_none:
        return RedirectResponse(url="/profile", status_code=303)
```

And for the upsert logic:
```python
    if existing:
        if weight is not None: existing.weight_kg = weight
        if chest is not None: existing.chest_cm = chest
        if arm_l is not None: existing.arm_cm_left = arm_l
        if arm_r is not None: existing.arm_cm_right = arm_r
        if waist is not None: existing.waist_cm = waist
        if thigh_l is not None: existing.thigh_cm_left = thigh_l
        if thigh_r is not None: existing.thigh_cm_right = thigh_r
        if hip is not None: existing.hip_cm = hip
        if neck is not None: existing.neck_cm = neck
        if calf is not None: existing.calf_cm = calf
    else:
        m = BodyMeasurement(
            user_id=user.id,
            measured_at=dt,
            weight_kg=weight,
            chest_cm=chest,
            arm_cm_left=arm_l,
            arm_cm_right=arm_r,
            waist_cm=waist,
            thigh_cm_left=thigh_l,
            thigh_cm_right=thigh_r,
            hip_cm=hip,
            neck_cm=neck,
            calf_cm=calf,
        )
        db.add(m)
```

- [ ] **Step 2: Update profile.html — measurement form**

Replace the measurement form section in `app/templates/profile.html` (lines 56-70) with the lateralized version. The form fields now use the new MEASUREMENT_FIELDS list which includes lateralized names:

```html
    <div class="card">
      <h2 class="card__title">Nouvelle mesure</h2>
      <p class="text-dim" style="font-size:12px;margin-bottom:var(--space-sm);">
        Mesurer le matin, a jeun, meme conditions. Entrer les deux cotes meme si similaires.
      </p>
      <form method="post" action="{{ url_for('profile_measurements_submit') }}" class="body-profile">
        <div class="body-profile__field" style="grid-column:1/-1;">
          <label for="measured_at">Date</label>
          <input type="date" id="measured_at" name="measured_at">
        </div>
        {% for field in measurement_fields %}
        <div class="body-profile__field">
          <label for="{{ field }}">{{ measurement_labels[field] }}</label>
          <input type="number" id="{{ field }}" name="{{ field }}" step="0.1"
                 value="{{ latest_values.get(field, '') }}"
                 placeholder="—">
        </div>
        {% endfor %}
        <button type="submit" class="btn btn--primary">Enregistrer la mesure</button>
      </form>
    </div>
```

The template loop already works because `measurement_fields` and `measurement_labels` now contain the lateralized names.

- [ ] **Step 3: Run profile-related tests**

Run: `pytest tests/test_profile_measurements.py tests/test_profile_enrich.py -v`
Expected: All PASS (update any tests that reference `arm_cm` or `thigh_cm` directly).

- [ ] **Step 4: Run full test suite**

Run: `pytest -x -q`
Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add app/routers/auth_routes.py app/templates/profile.html
git commit -m "feat(s1): lateralized body metrics form in Profile — left/right arms, thighs + hip/neck"
```

---

### Task 10: Sprint Report & Final Verification

**Files:**
- Create: `docs/SPRINT_S1_REPORT.md`
- Create: `docs/strategy/SPIGNOS_BODY_METRICS_READINESS_SPEC.md`

- [ ] **Step 1: Run the full test suite**

Run: `pytest -x -q`
Expected: All tests pass.

- [ ] **Step 2: Write the spec document**

Create `docs/strategy/SPIGNOS_BODY_METRICS_READINESS_SPEC.md`:

```markdown
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
- recorded_on: DATE (not DATETIME) — one per user per day, DB-enforced
- 5 dimensions: sleep_quality, fatigue_level, soreness_level, stress_level, motivation_level
- Scale: 1-5, 5 = always best
- Optional: resting_hr (INT), note (TEXT)

### UX
- Home page widget: collapsible form (not filled) or compact badge row (filled)
- History at /readiness/history (link from Home widget, no nav entry)
- Hard constraint: widget never pushes session action below the fold

## Signal Confidence Policy
- No trend displayed with fewer than 3 data points
- No muscle zone score with fewer than 2 relevant sessions
- No readiness trend with fewer than 5 entries in 30 days
- Partial measurements degrade to training-only scoring

## UX Roadmap
- Profile is the S1 compromise for body metrics
- Dedicated /body route planned post-S1
```

- [ ] **Step 3: Write the sprint report**

Create `docs/SPRINT_S1_REPORT.md`:

```markdown
# Sprint S1 Report — Body Metrics + Readiness Lite

**Date:** 2026-04-13
**Status:** Complete
**Prerequisite:** S0 (catalog integrity) — complete

## Objective

Add lateralized body measurements and daily readiness tracking
to SPIGNOS without breaking the existing session flow.

## Deliverables

| Artifact | Path | Status |
|----------|------|--------|
| Migration | `migrations/versions/20260413_body_measurements_v2_readiness.py` | Applied |
| Readiness model | `app/models/readiness.py` | Done |
| Readiness service | `app/services/readiness.py` | Done |
| Readiness router | `app/routers/readiness.py` | Done |
| Readiness history | `app/templates/readiness_history.html` | Done |
| Spec doc | `docs/strategy/SPIGNOS_BODY_METRICS_READINESS_SPEC.md` | Done |

## Changes Made

### Database
- body_measurements: arm_cm → arm_cm_left + arm_cm_right
- body_measurements: thigh_cm → thigh_cm_left + thigh_cm_right
- body_measurements: added hip_cm, neck_cm
- New table: readiness_entries (DATE pk, UNIQUE user+day, 5 scale fields)

### Services
- measurements.py: lateralized labels, avg helpers, compute_zone_measurement()
- readiness.py: new — save, get_today, get_history, validation
- muscle_mapping.py: ZONE_MEASUREMENT uses semantic keys
- muscle_scoring.py: uses compute_zone_measurement() instead of getattr()

### Routes & UI
- Home page: readiness widget (compact badge row or collapsible form)
- /readiness (POST): save daily readiness
- /readiness/history: history page (badge list, 90 days)
- Profile: lateralized measurement form with help text

### Tests
- test_readiness.py: model, service, validation, upsert
- test_readiness_routes.py: POST, history, auth
- test_measurements.py: updated for lateralized fields + avg helpers
- test_muscle_scoring.py: updated for compute_zone_measurement

## Verification Commands

```bash
alembic upgrade head                       # Migration applied
pytest tests/test_readiness.py -v          # Readiness tests
pytest tests/test_readiness_routes.py -v   # Route tests
pytest tests/test_measurements.py -v       # Measurement tests
pytest tests/test_muscle_scoring.py -v     # Scoring tests
pytest -x -q                               # Full suite green
```

## Files Modified

- `app/models/measurement.py` (lateralized)
- `app/models/readiness.py` (new)
- `app/models/__init__.py` (import readiness)
- `app/services/measurements.py` (avg helpers, zone measurement)
- `app/services/readiness.py` (new)
- `app/services/muscle_mapping.py` (ZONE_MEASUREMENT)
- `app/services/muscle_scoring.py` (_score_anthropo)
- `app/routers/pages.py` (readiness widget, history route)
- `app/routers/readiness.py` (new)
- `app/routers/auth_routes.py` (lateralized form)
- `app/templates/index.html` (readiness widget)
- `app/templates/readiness_history.html` (new)
- `app/templates/profile.html` (lateralized form)
- `migrations/versions/...` (new)

## Gaps for S2

- No composite readiness score yet
- No readiness → session correlation
- No asymmetry detection from left/right differences
- Body metrics live in Profile (dedicated /body route planned)
- No trend sparklines on readiness history (optional enhancement)
```

- [ ] **Step 4: Commit**

```bash
git add docs/strategy/SPIGNOS_BODY_METRICS_READINESS_SPEC.md docs/SPRINT_S1_REPORT.md
git commit -m "docs(s1): add body metrics spec and sprint S1 delivery report"
```

- [ ] **Step 5: Final full test run**

Run: `pytest -x -q`
Expected: All tests pass. S1 is complete.
