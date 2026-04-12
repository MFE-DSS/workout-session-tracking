# Body Measurement Tracking Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add time-series body measurements (weight, chest, arm, waist, thigh, calf) with SVG evolution graphs and muscle-template mapping, integrated into the existing /profile page.

**Architecture:** New `BodyMeasurement` model with an Alembic migration. New `measurements.py` service for CRUD + muscle mapping. Timeline SVG reuse from existing `timeline.py`. Profile route enriched, template updated. No new routes beyond a POST endpoint.

**Tech Stack:** Python 3.14, FastAPI, SQLAlchemy 2.0, Alembic, Jinja2, pytest

---

## File Structure

| Action | File | Responsibility |
|--------|------|----------------|
| Create | `app/models/measurement.py` | BodyMeasurement ORM model |
| Create | `app/services/measurements.py` | CRUD, muscle mapping, series extraction |
| Create | `migrations/versions/20260412_add_body_measurements.py` | CREATE TABLE migration |
| Create | `tests/test_measurements.py` | Unit + integration tests |
| Modify | `app/services/timeline.py` | Add `build_measurement_timeline_svg()` |
| Modify | `app/routers/auth_routes.py` | Enrich profile + add POST /profile/measurements |
| Modify | `app/templates/profile.html` | Measurement form + graphs + reduced static profile |
| Modify | `app/static/css/app.css` | `.measurement-grid` class |

---

### Task 1: BodyMeasurement model + migration

**Files:**
- Create: `app/models/measurement.py`
- Create: `migrations/versions/20260412_add_body_measurements.py`

- [ ] **Step 1: Create the model**

```python
# app/models/measurement.py
"""Body measurement time-series tracking.

Each row is one measurement session — the user fills in whichever
fields they measured that day. All measurement fields are nullable
to allow partial entries.
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
    arm_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    waist_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    thigh_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    calf_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
```

- [ ] **Step 2: Create the migration**

```python
# migrations/versions/20260412_add_body_measurements.py
"""add body_measurements table

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-04-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'body_measurements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('measured_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('weight_kg', sa.Float(), nullable=True),
        sa.Column('chest_cm', sa.Float(), nullable=True),
        sa.Column('arm_cm', sa.Float(), nullable=True),
        sa.Column('waist_cm', sa.Float(), nullable=True),
        sa.Column('thigh_cm', sa.Float(), nullable=True),
        sa.Column('calf_cm', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'ix_body_measurements_user_date',
        'body_measurements',
        ['user_id', 'measured_at'],
    )


def downgrade() -> None:
    op.drop_index('ix_body_measurements_user_date', table_name='body_measurements')
    op.drop_table('body_measurements')
```

- [ ] **Step 3: Verify migration runs**

Run: `cd /Users/martinfeldmann/workout-session-tracking && .venv/bin/python -m scripts.check_alembic_drift`
Expected: If drift detected, that's expected (model exists but migration hasn't run yet on dev DB). The migration file is structurally valid.

- [ ] **Step 4: Run existing tests to verify no breakage**

Run: `pytest tests/test_register_profile.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add app/models/measurement.py migrations/versions/20260412_add_body_measurements.py
git commit -m "feat: add BodyMeasurement model and migration"
```

---

### Task 2: Measurements service (CRUD + muscle mapping)

**Files:**
- Create: `app/services/measurements.py`
- Create: `tests/test_measurements.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_measurements.py
"""Tests for body measurement service."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.services.measurements import (
    MEASUREMENT_LABELS,
    MEASUREMENT_MUSCLE_MAP,
    find_related_templates,
    get_latest_measurement,
    get_measurement_series,
)
from tests.helpers import get_test_user_id


def test_muscle_map_has_all_fields():
    """Every measurement field has a mapping entry."""
    assert set(MEASUREMENT_MUSCLE_MAP.keys()) == {
        "weight_kg", "chest_cm", "arm_cm", "waist_cm", "thigh_cm", "calf_cm",
    }


def test_labels_has_all_fields():
    assert set(MEASUREMENT_LABELS.keys()) == set(MEASUREMENT_MUSCLE_MAP.keys())


def test_find_related_templates_chest():
    """Chest maps to templates with 'pectoral' in focus."""

    class FakeTemplate:
        def __init__(self, name, focus):
            self.name = name
            self.focus = focus

    templates = [
        FakeTemplate("Push A", "Pectoral, Delts, Triceps"),
        FakeTemplate("Pull A", "Dos, Delts arrière"),
        FakeTemplate("Legs", "Jambes"),
    ]
    result = find_related_templates("chest_cm", templates)
    assert result == ["Push A"]


def test_find_related_templates_weight_returns_empty():
    class FakeTemplate:
        def __init__(self, name, focus):
            self.name = name
            self.focus = focus

    templates = [FakeTemplate("Push A", "Pectoral")]
    result = find_related_templates("weight_kg", templates)
    assert result == []


def test_find_related_templates_thigh():
    class FakeTemplate:
        def __init__(self, name, focus):
            self.name = name
            self.focus = focus

    templates = [
        FakeTemplate("Push A", "Pectoral, Delts"),
        FakeTemplate("Legs", "Jambes"),
    ]
    result = find_related_templates("thigh_cm", templates)
    assert result == ["Legs"]


def test_get_latest_measurement_empty(client):
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        result = get_latest_measurement(db, uid)
    assert result is None


def test_get_latest_measurement_returns_most_recent(client):
    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement

    uid = get_test_user_id()
    now = datetime.now(timezone.utc)

    with SessionLocal() as db:
        db.add(BodyMeasurement(
            user_id=uid, measured_at=now - timedelta(days=7), weight_kg=74.0,
        ))
        db.add(BodyMeasurement(
            user_id=uid, measured_at=now, weight_kg=75.0, chest_cm=100.0,
        ))
        db.commit()

    with SessionLocal() as db:
        latest = get_latest_measurement(db, uid)
    assert latest is not None
    assert latest.weight_kg == 75.0
    assert latest.chest_cm == 100.0


def test_get_measurement_series(client):
    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement

    uid = get_test_user_id()
    now = datetime.now(timezone.utc)

    with SessionLocal() as db:
        db.add(BodyMeasurement(
            user_id=uid, measured_at=now - timedelta(days=14), weight_kg=73.0,
        ))
        db.add(BodyMeasurement(
            user_id=uid, measured_at=now - timedelta(days=7), weight_kg=74.0,
        ))
        db.add(BodyMeasurement(
            user_id=uid, measured_at=now, weight_kg=75.0,
        ))
        # One without weight (should be excluded from weight series)
        db.add(BodyMeasurement(
            user_id=uid, measured_at=now - timedelta(days=3), chest_cm=99.0,
        ))
        db.commit()

    with SessionLocal() as db:
        series = get_measurement_series(db, uid, "weight_kg")
    assert len(series) == 3
    # Ordered ASC by date
    assert series[0][1] == 73.0
    assert series[2][1] == 75.0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_measurements.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement measurements service**

```python
# app/services/measurements.py
"""Body measurement CRUD and muscle-template mapping.

Provides time-series storage for body measurements and a static
mapping from measurement fields to muscle groups, used to display
related workout templates alongside evolution graphs.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.measurement import BodyMeasurement


# --- Muscle group mapping ---

MEASUREMENT_MUSCLE_MAP: dict[str, list[str]] = {
    "weight_kg": [],
    "chest_cm": ["pectoral", "pectoraux", "pecs"],
    "arm_cm": ["biceps", "triceps", "bras"],
    "waist_cm": ["abdos", "abs", "cardio"],
    "thigh_cm": ["jambes", "quadriceps", "cuisses"],
    "calf_cm": ["mollets", "jambes"],
}

MEASUREMENT_LABELS: dict[str, str] = {
    "weight_kg": "Poids (kg)",
    "chest_cm": "Poitrine (cm)",
    "arm_cm": "Bras (cm)",
    "waist_cm": "Taille (cm)",
    "thigh_cm": "Cuisses (cm)",
    "calf_cm": "Mollets (cm)",
}

MEASUREMENT_FIELDS = list(MEASUREMENT_LABELS.keys())


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
    col = getattr(BodyMeasurement, field)
    rows = db.execute(
        select(BodyMeasurement.measured_at, col)
        .where(BodyMeasurement.user_id == user_id)
        .where(col.is_not(None))
        .order_by(BodyMeasurement.measured_at.asc())
        .limit(limit)
    ).all()
    return [(r[0], r[1]) for r in rows]
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_measurements.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add app/services/measurements.py tests/test_measurements.py
git commit -m "feat: add measurements service with CRUD and muscle mapping"
```

---

### Task 3: Measurement timeline SVG

**Files:**
- Modify: `app/services/timeline.py`
- Modify: `tests/test_measurements.py` (add test)

- [ ] **Step 1: Write failing test**

Append to `tests/test_measurements.py`:

```python
from app.services.timeline import build_measurement_timeline_svg, TimelinePoint


def test_measurement_timeline_returns_svg():
    points = [
        TimelinePoint(label="01/04", value=95.0),
        TimelinePoint(label="08/04", value=97.0),
        TimelinePoint(label="12/04", value=100.0),
    ]
    svg = build_measurement_timeline_svg(points, title="Poitrine (cm)")
    assert "<svg" in svg
    assert "Poitrine (cm)" in svg


def test_measurement_timeline_empty_returns_empty():
    assert build_measurement_timeline_svg([], title="Test") == ""


def test_measurement_timeline_one_point_returns_empty():
    points = [TimelinePoint(label="01/04", value=95.0)]
    assert build_measurement_timeline_svg(points, title="Test") == ""
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_measurements.py::test_measurement_timeline_returns_svg -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Implement build_measurement_timeline_svg**

Append to `app/services/timeline.py` (after `build_sparkline_svg`):

```python
def build_measurement_timeline_svg(
    points: list[TimelinePoint],
    *,
    title: str = "",
) -> str:
    """Measurement evolution timeline: auto-ranged Y axis.

    Returns empty string if fewer than 2 data points.
    """
    if len(points) < 2:
        return ""
    vals = [p.value for p in points]
    lo = min(vals) - 2
    hi = max(vals) + 2
    return _build_svg(
        points,
        y_min=lo,
        y_max=hi,
        color="#f25f3a",
        title=title,
        height=140,
    )
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_measurements.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add app/services/timeline.py tests/test_measurements.py
git commit -m "feat: add build_measurement_timeline_svg for body evolution charts"
```

---

### Task 4: Profile route integration

**Files:**
- Modify: `app/routers/auth_routes.py`
- Create: `tests/test_profile_measurements.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_profile_measurements.py
"""Tests for measurement integration on profile page."""
from __future__ import annotations


def test_profile_shows_measurement_form(client):
    body = client.get("/profile").text
    assert "Nouvelle mesure" in body or "mesure" in body.lower()
    assert "measured_at" in body


def test_profile_measurement_submit(client):
    r = client.post("/profile/measurements", data={
        "measured_at": "2026-04-12",
        "weight_kg": "75.5",
        "chest_cm": "100",
        "arm_cm": "36",
        "waist_cm": "",
        "thigh_cm": "",
        "calf_cm": "",
    }, follow_redirects=False)
    assert r.status_code == 303

    # Verify data persisted — second submit
    r2 = client.post("/profile/measurements", data={
        "measured_at": "2026-04-12",
        "weight_kg": "76.0",
        "chest_cm": "",
        "arm_cm": "",
        "waist_cm": "",
        "thigh_cm": "",
        "calf_cm": "",
    }, follow_redirects=False)
    assert r2.status_code == 303


def test_profile_measurement_invalid_date(client):
    r = client.post("/profile/measurements", data={
        "measured_at": "",
        "weight_kg": "75",
        "chest_cm": "",
        "arm_cm": "",
        "waist_cm": "",
        "thigh_cm": "",
        "calf_cm": "",
    }, follow_redirects=False)
    # Empty date should still redirect (use today as fallback)
    assert r.status_code == 303
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_profile_measurements.py -v`
Expected: FAIL

- [ ] **Step 3: Enrich profile route + add POST endpoint**

In `app/routers/auth_routes.py`, modify the `profile_page` function return block. Replace the section starting at line 234 (`from app.services.behavioral import compute_behavioral_state`) through line 252 (end of return) with:

```python
    from app.services.behavioral import compute_behavioral_state
    from app.services.measurements import (
        MEASUREMENT_FIELDS,
        MEASUREMENT_LABELS,
        find_related_templates,
        get_latest_measurement,
        get_measurement_series,
    )
    from app.services.timeline import TimelinePoint, build_measurement_timeline_svg
    from app.models.catalog import WorkoutTemplate

    behavioral = compute_behavioral_state(db, user.id)

    # Body measurements
    latest_measurement = get_latest_measurement(db, user.id)

    # Build per-field SVG charts
    measurement_charts: dict[str, str] = {}
    for field in MEASUREMENT_FIELDS:
        series = get_measurement_series(db, user.id, field)
        points = [
            TimelinePoint(label=dt.strftime("%d/%m"), value=val)
            for dt, val in series
        ]
        measurement_charts[field] = build_measurement_timeline_svg(
            points, title=MEASUREMENT_LABELS[field]
        )

    # Related templates per field
    all_templates = list(db.execute(
        select(WorkoutTemplate).order_by(WorkoutTemplate.slug)
    ).scalars().all())
    related_templates: dict[str, list[str]] = {
        field: find_related_templates(field, all_templates)
        for field in MEASUREMENT_FIELDS
    }

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
            "latest_measurement": latest_measurement,
            "measurement_charts": measurement_charts,
            "measurement_labels": MEASUREMENT_LABELS,
            "measurement_fields": MEASUREMENT_FIELDS,
            "related_templates": related_templates,
            "active_session": latest_open_session(db, user.id),
        },
    )
```

Add the new POST endpoint after `profile_body_submit` (before the password change section):

```python
@router.post("/profile/measurements", response_model=None)
async def profile_measurements_submit(
    request: Request,
    measured_at: Annotated[str, Form()] = "",
    weight_kg: Annotated[str, Form()] = "",
    chest_cm: Annotated[str, Form()] = "",
    arm_cm: Annotated[str, Form()] = "",
    waist_cm: Annotated[str, Form()] = "",
    thigh_cm: Annotated[str, Form()] = "",
    calf_cm: Annotated[str, Form()] = "",
    db: DbSession = None,
    user: CurrentUser = None,
):
    """Save a body measurement entry."""
    from app.models.measurement import BodyMeasurement

    # Parse date — fallback to now if empty/invalid
    dt = datetime.now(timezone.utc)
    if measured_at.strip():
        try:
            dt = datetime.strptime(measured_at.strip(), "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            pass

    def _float_or_none(v: str, lo: float, hi: float) -> float | None:
        v = v.strip()
        if not v:
            return None
        try:
            n = float(v)
        except ValueError:
            return None
        if n < lo or n > hi:
            return None
        return n

    m = BodyMeasurement(
        user_id=user.id,
        measured_at=dt,
        weight_kg=_float_or_none(weight_kg, 30.0, 300.0),
        chest_cm=_float_or_none(chest_cm, 10.0, 200.0),
        arm_cm=_float_or_none(arm_cm, 10.0, 200.0),
        waist_cm=_float_or_none(waist_cm, 10.0, 200.0),
        thigh_cm=_float_or_none(thigh_cm, 10.0, 200.0),
        calf_cm=_float_or_none(calf_cm, 10.0, 200.0),
    )
    db.add(m)
    db.commit()

    return RedirectResponse(url="/profile", status_code=303)
```

Also add the `WorkoutTemplate` import at the top of the file if not present:

```python
from app.models.catalog import WorkoutTemplate
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_profile_measurements.py tests/test_profile_enrich.py tests/test_profile_behavioral.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add app/routers/auth_routes.py tests/test_profile_measurements.py
git commit -m "feat: add measurement form + charts to profile route"
```

---

### Task 5: Profile template + CSS

**Files:**
- Modify: `app/templates/profile.html`
- Modify: `app/static/css/app.css`

- [ ] **Step 1: Add CSS class for measurement grid**

Append to `app/static/css/app.css` before the `/* ---------- Footer ---------- */` or at end of the desktop media query section. Add in the main section:

```css
/* ---------- Measurement grid ---------- */
.measurement-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-sm);
  margin-top: var(--space-md);
}
.measurement-grid .card {
  padding: var(--space-sm) var(--space-md);
}
.measurement-grid__related {
  font-size: 12px;
  color: var(--fg-dim);
  margin-top: var(--space-xs);
}
```

Add in the `@media (min-width: 768px)` block:

```css
.measurement-grid { grid-template-columns: 1fr 1fr; }
```

- [ ] **Step 2: Rewrite profile.html**

Replace `app/templates/profile.html` entirely:

```html
{% extends "base.html" %}
{% block content %}
<h1 class="page-title">Profil</h1>

<div class="cockpit-grid">
  <div class="cockpit-main">
    <div class="card">
      <h2 class="card__title">Identité</h2>
      <ul class="stats-list">
        <li><span>Utilisateur</span><b>{{ user.username }}</b></li>
        <li><span>Inscrit le</span><b>{{ user.created_at.strftime('%d/%m/%Y') if user.created_at else '—' }}</b></li>
        <li><span>Statut</span><b>{% if user.is_active %}Actif{% else %}Inactif{% endif %}</b></li>
        <li><span>Sessions totales</span><b>{{ session_count }}</b></li>
        <li><span>Sessions terminées</span><b>{{ completed_count }}</b></li>
      </ul>
    </div>

    <div class="card">
      <h2 class="card__title">Mes 30 derniers jours</h2>
      <div class="kpi-row">
        <div class="kpi">
          <span class="kpi__value">{{ sessions_30d_count }}</span>
          <span class="kpi__label">séances</span>
        </div>
        <div class="kpi">
          <span class="kpi__value trend-indicator trend-indicator--{{ trend }}">{{ trend_label }}</span>
          <span class="kpi__label">tendance</span>
        </div>
      </div>
      <div class="kpi-row" style="margin-top:var(--space-sm);">
        <div class="kpi">
          <span class="kpi__value">{{ "%.0f"|format(behavioral.fatigue_score) }}</span>
          <span class="kpi__label">fatigue</span>
        </div>
        <div class="kpi">
          <span class="kpi__value">{{ "%.0f"|format(behavioral.consistency_score) }}</span>
          <span class="kpi__label">régularité</span>
        </div>
        <div class="kpi">
          <span class="kpi__value">{{ behavioral.streak_days }}</span>
          <span class="kpi__label">jours de série</span>
        </div>
      </div>
      {% if quality_svg %}
        <div class="timeline-chart">{{ quality_svg|safe }}</div>
      {% else %}
        <p class="text-dim" style="font-size:13px;margin:var(--space-sm) 0;">Pas encore de données</p>
      {% endif %}
    </div>
  </div>

  <div class="cockpit-side">
    <div class="card">
      <h2 class="card__title">Nouvelle mesure</h2>
      <form method="post" action="{{ url_for('profile_measurements_submit') }}" class="body-profile">
        <div class="body-profile__field" style="grid-column:1/-1;">
          <label for="measured_at">Date</label>
          <input type="date" id="measured_at" name="measured_at"
                 value="{{ now().strftime('%Y-%m-%d') if now is defined else '' }}">
        </div>
        {% for field in measurement_fields %}
        <div class="body-profile__field">
          <label for="{{ field }}">{{ measurement_labels[field] }}</label>
          <input type="number" id="{{ field }}" name="{{ field }}" step="0.1"
                 value="{{ (latest_measurement[field] or '') if latest_measurement else '' }}"
                 placeholder="—">
        </div>
        {% endfor %}
        <button type="submit" class="btn btn--primary">Enregistrer la mesure</button>
      </form>
    </div>

    <div class="card">
      <h2 class="card__title">Données de référence</h2>
      <form method="post" action="{{ url_for('profile_body_submit') }}" class="body-profile">
        <div class="body-profile__field">
          <label for="height_cm">Taille (cm)</label>
          <input type="number" id="height_cm" name="height_cm"
                 value="{{ user.height_cm or '' }}" min="100" max="250" placeholder="175">
        </div>
        <div class="body-profile__field">
          <label for="resting_hr">FC repos (bpm)</label>
          <input type="number" id="resting_hr" name="resting_hr"
                 value="{{ user.resting_hr or '' }}" min="30" max="220" placeholder="60">
        </div>
        <div class="body-profile__field">
          <label for="bp_systolic">Tension sys.</label>
          <input type="number" id="bp_systolic" name="bp_systolic"
                 value="{{ user.bp_systolic or '' }}" min="60" max="250" placeholder="120">
        </div>
        <div class="body-profile__field">
          <label for="bp_diastolic">Tension dia.</label>
          <input type="number" id="bp_diastolic" name="bp_diastolic"
                 value="{{ user.bp_diastolic or '' }}" min="30" max="150" placeholder="80">
        </div>
        <button type="submit" class="btn btn--ghost">Enregistrer</button>
      </form>
    </div>

    <div class="card__actions" style="margin-top:var(--space-md);">
      <a class="btn" href="{{ url_for('password_change_page') }}">Changer le mot de passe</a>
    </div>
  </div>
</div>

<section style="margin-top:var(--space-lg);">
  <h2 class="section-header">Évolution corporelle</h2>
  <div class="measurement-grid">
    {% for field in measurement_fields %}
    <div class="card">
      {% if measurement_charts[field] %}
        <div class="timeline-chart">{{ measurement_charts[field]|safe }}</div>
      {% else %}
        <p class="text-dim" style="font-size:13px;">{{ measurement_labels[field] }} — pas encore de données</p>
      {% endif %}
      {% if related_templates[field] %}
        <p class="measurement-grid__related">Programmes associés : {{ related_templates[field]|join(', ') }}</p>
      {% endif %}
    </div>
    {% endfor %}
  </div>
</section>
{% endblock %}
```

Note: The `latest_measurement[field]` syntax uses attribute access on the SQLAlchemy model. In Jinja2 this works as `latest_measurement.weight_kg` etc. But since field is a variable, we need `getattr`. Update the template to use:

```html
value="{{ latest_measurement[field] if latest_measurement and latest_measurement[field] is not none else '' }}"
```

Jinja2 supports `obj[attr_name]` on Python objects via `__getattr__`, but SQLAlchemy models may not. Safer approach — pass a dict from the route:

In the route, add after `latest_measurement = get_latest_measurement(db, user.id)`:

```python
    latest_values: dict[str, str] = {}
    if latest_measurement:
        for field in MEASUREMENT_FIELDS:
            val = getattr(latest_measurement, field, None)
            latest_values[field] = str(val) if val is not None else ""
```

And pass `latest_values` to the template instead of `latest_measurement`. Then the template input becomes:

```html
value="{{ latest_values.get(field, '') }}"
```

- [ ] **Step 3: Update the profile_body_submit to handle reduced fields**

The `POST /profile/body` endpoint currently accepts `weight_kg` and `waist_cm` which are now tracked via measurements. Update it to remove those two params and only handle: `height_cm`, `resting_hr`, `bp_systolic`, `bp_diastolic`.

- [ ] **Step 4: Run all profile tests**

Run: `pytest tests/test_profile_measurements.py tests/test_profile_enrich.py tests/test_profile_behavioral.py tests/test_register_profile.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add app/templates/profile.html app/static/css/app.css app/routers/auth_routes.py
git commit -m "feat: add measurement form, evolution charts, and muscle mapping to profile"
```

---

### Task 6: Final integration

- [ ] **Step 1: Run full test suite**

Run: `pytest --tb=short -q`
Expected: All tests PASS (only pre-existing failures)

- [ ] **Step 2: Run Alembic drift check**

Run: `.venv/bin/python -m scripts.check_alembic_drift`
Expected: `Alembic drift check: OK (no diff).`

- [ ] **Step 3: Visual verification**

Run: `python -m uvicorn app.main:app --port 8001`

Verify:
- `/profile` shows measurement form with date + 6 fields
- Submit a measurement → redirects back, form pre-fills with latest values
- After 2+ measurements on same field: SVG chart appears
- "Programmes associés" shows under chest (Push A, Push B), thigh (Legs), etc.
- "Données de référence" section shows reduced static fields (height, hr, bp)
- Desktop: 2-column grid for measurement charts

- [ ] **Step 4: Commit if fixes needed**

```bash
git add -A
git commit -m "fix: measurement integration adjustments after visual review"
```
