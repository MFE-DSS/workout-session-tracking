# Physique Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a muscle development KPI dashboard at `/physique` with a radar hexagon SVG, composite scoring per zone, confidence levels, and detailed analytical cards.

**Architecture:** 3 new service files (mapping, scoring, radar SVG) + 1 new route + 1 new template. Score composite = 50% performance proxy (tonnage trends) + 30% exposure (volume vs targets) + 20% anthropometry (body measurements). Radar is server-rendered SVG. Tour de taille re-added to measurements.

**Tech Stack:** Python 3.14, FastAPI, SQLAlchemy 2.0, Jinja2, SVG (server-rendered), CSS

---

## File Structure

| Action | File | Responsibility |
|--------|------|----------------|
| Create | `app/services/muscle_mapping.py` | Exercise→zone mapping, zone/axis definitions |
| Create | `app/services/muscle_scoring.py` | Score computation, confidence, PhysiqueDashboard |
| Create | `app/services/radar.py` | Hexagon SVG builder |
| Create | `app/templates/physique.html` | Dashboard page template |
| Create | `tests/test_muscle_scoring.py` | Mapping + scoring + integration tests |
| Modify | `app/routers/pages.py` | Add GET /physique route |
| Modify | `app/templates/base.html` | Add "Physique" nav link |
| Modify | `app/services/measurements.py` | Re-add waist_cm to MEASUREMENT_FIELDS |
| Modify | `app/routers/auth_routes.py` | Re-add waist_cm to POST /profile/measurements |
| Modify | `app/static/css/app.css` | Zone card, radar, progress bar styles |

---

### Task 1: Muscle mapping service

**Files:**
- Create: `app/services/muscle_mapping.py`
- Create: `tests/test_muscle_scoring.py`

- [ ] **Step 1: Write failing tests for mapping**

```python
# tests/test_muscle_scoring.py
"""Tests for muscle mapping, scoring, and dashboard."""
from __future__ import annotations

from app.services.muscle_mapping import (
    RADAR_AXES,
    ZONE_LABELS,
    classify_exercise,
)


def test_zone_labels_has_11_zones():
    assert len(ZONE_LABELS) == 11


def test_radar_axes_has_6():
    assert len(RADAR_AXES) == 6


def test_classify_chest_press():
    zone, secondary = classify_exercise("Chest Press machine")
    assert zone == "pecs"
    assert "triceps" in secondary


def test_classify_incline_smith():
    zone, _ = classify_exercise("Incline Smith Press")
    assert zone == "pecs"


def test_classify_lateral_raise():
    zone, _ = classify_exercise("Élévations latérales câble")
    assert zone == "delt_lat"


def test_classify_face_pull():
    zone, _ = classify_exercise("Face pull câble")
    assert zone == "delt_post"


def test_classify_lat_pulldown():
    zone, secondary = classify_exercise("Tirage poulie haute prise neutre")
    assert zone == "lats"
    assert "biceps" in secondary


def test_classify_rowing():
    zone, _ = classify_exercise("Rowing machine chest-supported")
    assert zone == "upper_back"


def test_classify_curl():
    zone, _ = classify_exercise("Curl incliné haltères")
    assert zone == "biceps"


def test_classify_triceps():
    zone, _ = classify_exercise("Triceps extension poulie haute")
    assert zone == "triceps"


def test_classify_hack_squat():
    zone, _ = classify_exercise("Hack Squat machine")
    assert zone == "quads"


def test_classify_rdl():
    zone, _ = classify_exercise("Romanian Deadlift haltères")
    assert zone == "posterior"


def test_classify_calf():
    zone, _ = classify_exercise("Relevés mollets debout")
    assert zone == "calves"


def test_classify_ab_wheel():
    zone, _ = classify_exercise("Roulette abdominale (ab wheel rollout)")
    assert zone == "core"


def test_classify_unknown():
    zone, secondary = classify_exercise("Exercice inconnu xyz")
    assert zone == "unknown"
    assert secondary == []


def test_classify_butterfly():
    zone, _ = classify_exercise("Butterfly pec machine")
    assert zone == "pecs"


def test_classify_dips():
    zone, _ = classify_exercise("Dips pectoraux (buste penché)")
    assert zone == "pecs"


def test_classify_skull_crushers():
    zone, _ = classify_exercise("Skull crushers EZ-bar")
    assert zone == "triceps"


def test_classify_leg_curl():
    zone, _ = classify_exercise("Leg curls assis")
    assert zone == "posterior"


def test_classify_leg_extension():
    zone, _ = classify_exercise("Leg extensions assises")
    assert zone == "quads"


def test_classify_hip_thrust():
    zone, _ = classify_exercise("Hip thrust Smith machine")
    assert zone == "posterior"


def test_classify_shoulder_press():
    zone, _ = classify_exercise("Machine shoulder press")
    assert zone == "delt_lat"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_muscle_scoring.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement muscle_mapping.py**

```python
# app/services/muscle_mapping.py
"""Exercise-to-muscle-zone mapping for the physique dashboard.

Maps exercise names (substring match, case-insensitive) to
muscle zones for scoring. Two levels:
  - 11 detailed zones (analytical view)
  - 6 radar axes (macro view, aggregation of detailed zones)
"""
from __future__ import annotations


# --- 11 detailed zones ---

ZONE_LABELS: dict[str, str] = {
    "pecs": "Pectoraux",
    "delt_lat": "Deltoïdes latéraux",
    "delt_post": "Deltoïdes postérieurs",
    "lats": "Dos largeur",
    "upper_back": "Dos épaisseur",
    "biceps": "Biceps",
    "triceps": "Triceps",
    "quads": "Quadriceps",
    "posterior": "Ischios / Fessiers",
    "calves": "Mollets",
    "core": "Core / Abdos",
}

# Zone → associated body measurement field (if any)
ZONE_MEASUREMENT: dict[str, str | None] = {
    "pecs": "chest_cm",
    "delt_lat": None,
    "delt_post": None,
    "lats": None,
    "upper_back": None,
    "biceps": "arm_cm",
    "triceps": "arm_cm",
    "quads": "thigh_cm",
    "posterior": "thigh_cm",
    "calves": None,
    "core": "waist_cm",  # inverse logic (decrease = good)
}

# Zone → weekly volume target (hard sets) for exposure scoring
ZONE_VOLUME_TARGET: dict[str, int] = {
    "pecs": 16,
    "delt_lat": 18,
    "delt_post": 10,
    "lats": 16,
    "upper_back": 16,
    "biceps": 10,
    "triceps": 10,
    "quads": 16,
    "posterior": 16,
    "calves": 10,
    "core": 10,
}

# --- 6 radar axes (aggregate detailed zones) ---

RADAR_AXES: dict[str, dict] = {
    "pecs": {"label": "Pectoraux", "zones": ["pecs"]},
    "shoulders": {"label": "Épaules", "zones": ["delt_lat", "delt_post"]},
    "back_width": {"label": "Dos largeur", "zones": ["lats"]},
    "back_thickness": {"label": "Dos épaisseur", "zones": ["upper_back"]},
    "arms": {"label": "Bras", "zones": ["biceps", "triceps"]},
    "lower": {"label": "Bas du corps", "zones": ["quads", "posterior", "calves"]},
}

RADAR_AXIS_ORDER = ["pecs", "shoulders", "back_width", "back_thickness", "arms", "lower"]

# --- Exercise classification ---

# (keywords in exercise name, case-insensitive) → (primary zone, secondary zones)
_EXERCISE_PATTERNS: list[tuple[list[str], str, list[str]]] = [
    # Pecs
    (["chest press", "presse pectorale", "butterfly", "écarté pec",
      "développé couché", "développé incliné", "incline smith",
      "dips pec", "dips pectora", "pec deck", "cable cross",
      "cross-over"], "pecs", ["triceps"]),
    # Delts lat
    (["shoulder press", "presse épaule", "presse à épaule",
      "élévation latérale", "lateral raise", "élévations latérales",
      "tirage front", "upright row"], "delt_lat", []),
    # Delts post
    (["face pull", "rear delt", "écarté arrière", "reverse fly",
      "oiseau", "arrière d'épaule"], "delt_post", []),
    # Lats (back width)
    (["tirage vertical", "tirage poulie haute", "lat pulldown",
      "pulldown", "pullover câble", "pullover cable",
      "straight-arm", "traction"], "lats", ["biceps"]),
    # Upper back (thickness)
    (["rowing", "seated row", "tirage horizontal", "t-bar",
      "shrug"], "upper_back", ["biceps"]),
    # Biceps
    (["curl", "biceps"], "biceps", []),
    # Triceps
    (["triceps", "skull", "skull crusher",
      "extension overhead", "pushdown", "kickback",
      "extension poulie"], "triceps", []),
    # Quads
    (["hack squat", "leg press", "leg extension",
      "squat", "leg ext"], "quads", []),
    # Posterior chain
    (["leg curl", "rdl", "romanian", "hip thrust",
      "deadlift", "good morning", "adduction"], "posterior", []),
    # Calves
    (["mollet", "calf", "relevé", "relevés mollet"], "calves", []),
    # Core
    (["abdo", "crunch", "roulette", "ab wheel", "pallof",
      "relevé de jambe", "relevé jambe", "hanging"], "core", []),
]


def classify_exercise(name: str) -> tuple[str, list[str]]:
    """Classify an exercise name into (primary_zone, secondary_zones).

    Uses case-insensitive substring matching against known patterns.
    Returns ("unknown", []) if no pattern matches.
    """
    name_lower = name.lower()
    for keywords, primary, secondary in _EXERCISE_PATTERNS:
        if any(kw in name_lower for kw in keywords):
            return primary, secondary
    return "unknown", []
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_muscle_scoring.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add app/services/muscle_mapping.py tests/test_muscle_scoring.py
git commit -m "feat: add muscle mapping service — exercise→zone classification"
```

---

### Task 2: Scoring service

**Files:**
- Create: `app/services/muscle_scoring.py`
- Modify: `tests/test_muscle_scoring.py` (add tests)

- [ ] **Step 1: Write failing tests for scoring**

Append to `tests/test_muscle_scoring.py`:

```python
from datetime import datetime, timedelta, timezone
from tests.helpers import get_test_user_id


def _add_session_with_sets(client, user_id, exercise_name, sets_data, days_ago=0):
    """Insert a completed session with specific exercises and sets."""
    from app.database import SessionLocal
    from app.models.session import WorkoutSession, SessionExercise, SetLog

    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        s = WorkoutSession(
            user_id=user_id,
            template_slug_snapshot="test",
            template_name_snapshot="Test",
            started_at=now - timedelta(days=days_ago),
            status="completed",
        )
        se = SessionExercise(
            exercise_code_snapshot="E1",
            exercise_name_snapshot=exercise_name,
            position=1,
        )
        for i, (weight, reps) in enumerate(sets_data, 1):
            se.set_logs.append(SetLog(
                kind="work", set_index=i, completed=True,
                weight_kg=weight, reps=reps,
            ))
        s.session_exercises.append(se)
        db.add(s)
        db.commit()


def test_compute_dashboard_empty(client):
    """User with no sessions gets a dashboard with zero scores."""
    from app.database import SessionLocal
    from app.services.muscle_scoring import compute_physique_dashboard

    uid = get_test_user_id()
    with SessionLocal() as db:
        dash = compute_physique_dashboard(db, uid)

    assert dash.global_score >= 0
    assert len(dash.zone_scores) == 11
    assert len(dash.radar_axes) == 6
    assert dash.radar_svg  # non-empty SVG string
    for z in dash.zone_scores:
        assert z.confidence == "faible"


def test_compute_dashboard_with_data(client):
    """User with sessions gets computed scores."""
    from app.database import SessionLocal
    from app.services.muscle_scoring import compute_physique_dashboard

    uid = get_test_user_id()
    # Add chest sessions over 4 weeks
    for d in [28, 21, 14, 7, 3, 1]:
        _add_session_with_sets(client, uid, "Chest Press machine",
                               [(60, 10), (60, 10), (60, 10)], days_ago=d)

    with SessionLocal() as db:
        dash = compute_physique_dashboard(db, uid)

    pecs = next(z for z in dash.zone_scores if z.zone == "pecs")
    assert pecs.score > 0
    assert pecs.hard_sets > 0
    assert len(pecs.top_exercises) > 0


def test_radar_axes_aggregate_zones(client):
    """Radar axes should aggregate their component zones."""
    from app.database import SessionLocal
    from app.services.muscle_scoring import compute_physique_dashboard

    uid = get_test_user_id()
    # Add biceps + triceps sessions
    for d in [14, 7, 1]:
        _add_session_with_sets(client, uid, "Curl incliné haltères",
                               [(15, 12), (15, 12)], days_ago=d)
        _add_session_with_sets(client, uid, "Triceps pushdown",
                               [(30, 12), (30, 12)], days_ago=d)

    with SessionLocal() as db:
        dash = compute_physique_dashboard(db, uid)

    arms = next(a for a in dash.radar_axes if a.axis == "arms")
    assert arms.score > 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_muscle_scoring.py::test_compute_dashboard_empty -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement muscle_scoring.py**

```python
# app/services/muscle_scoring.py
"""Composite muscle development scoring for the physique dashboard.

Score = 50% performance proxy + 30% exposure + 20% anthropometry.
If anthropometry unavailable: 60% performance + 40% exposure.

Each zone gets a confidence level (élevée/moyenne/faible) based
on data availability.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload

from app.models.measurement import BodyMeasurement
from app.models.session import SessionExercise, SetLog, WorkoutSession
from app.services.muscle_mapping import (
    RADAR_AXES,
    RADAR_AXIS_ORDER,
    ZONE_LABELS,
    ZONE_MEASUREMENT,
    ZONE_VOLUME_TARGET,
    classify_exercise,
)
from app.services.radar import build_radar_svg


@dataclass
class ZoneScore:
    zone: str
    label: str
    score: float
    trend: str  # "up", "down", "stable"
    confidence: str  # "élevée", "moyenne", "faible"
    hard_sets: int
    session_count: int
    top_exercises: list[str]
    measurement_label: Optional[str] = None
    measurement_trend: Optional[str] = None


@dataclass
class RadarAxis:
    axis: str
    label: str
    score: float
    confidence: str


@dataclass
class PhysiqueDashboard:
    global_score: float
    global_grade: str
    zone_scores: list[ZoneScore]
    radar_axes: list[RadarAxis]
    radar_svg: str
    window_days: int


def _compute_tonnage_by_zone(
    db: Session, user_id: int, window_start: datetime
) -> dict[str, list[dict]]:
    """Get per-session tonnage grouped by zone."""
    sessions = db.execute(
        select(WorkoutSession)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == "completed",
            WorkoutSession.excluded_from_stats.is_(False),
            WorkoutSession.started_at >= window_start,
        )
        .order_by(WorkoutSession.started_at.asc())
        .options(
            selectinload(WorkoutSession.session_exercises)
            .selectinload(SessionExercise.set_logs)
        )
    ).scalars().all()

    # zone → list of {date, tonnage, exercise_name}
    zone_data: dict[str, list[dict]] = defaultdict(list)

    for s in sessions:
        for se in s.session_exercises:
            primary, secondary = classify_exercise(se.exercise_name_snapshot)
            if primary == "unknown":
                continue

            work_sets = [sl for sl in se.set_logs
                         if sl.kind == "work" and sl.completed]
            tonnage = sum(
                (sl.weight_kg or 0) * (sl.reps or 0) for sl in work_sets
            )
            hard_set_count = len(work_sets)

            if tonnage > 0 or hard_set_count > 0:
                entry = {
                    "date": s.started_at,
                    "tonnage": tonnage,
                    "hard_sets": hard_set_count,
                    "exercise": se.exercise_name_snapshot,
                }
                zone_data[primary].append(entry)
                # Secondary zones get 30% weight
                for sec in secondary:
                    zone_data[sec].append({
                        **entry,
                        "tonnage": tonnage * 0.3,
                        "hard_sets": round(hard_set_count * 0.3),
                    })

    return dict(zone_data)


def _score_performance(entries: list[dict]) -> tuple[float, str]:
    """Score performance proxy from tonnage entries. Returns (score, trend)."""
    if not entries:
        return 0.0, "stable"

    # Split into recent half and older half
    mid = len(entries) // 2
    if mid == 0:
        return 50.0, "stable"

    old_tonnage = sum(e["tonnage"] for e in entries[:mid])
    new_tonnage = sum(e["tonnage"] for e in entries[mid:])

    if old_tonnage == 0:
        return 50.0 if new_tonnage == 0 else 70.0, "up" if new_tonnage > 0 else "stable"

    change = (new_tonnage - old_tonnage) / old_tonnage

    if change <= -0.10:
        return 20.0, "down"
    elif change <= 0.02:
        return 50.0, "stable"
    elif change <= 0.10:
        return 70.0, "up"
    elif change <= 0.20:
        return 85.0, "up"
    else:
        return 95.0, "up"


def _score_exposure(hard_sets: int, zone: str, window_days: int) -> float:
    """Score exposure based on hard sets vs weekly target."""
    target = ZONE_VOLUME_TARGET.get(zone, 12)
    weeks = window_days / 7
    expected = target * weeks
    if expected == 0:
        return 0.0
    ratio = hard_sets / expected
    return min(100.0, ratio * 100)


def _score_anthropo(
    db: Session, user_id: int, zone: str, window_start: datetime
) -> tuple[float | None, str | None]:
    """Score anthropometry for a zone. Returns (score, trend_label) or (None, None)."""
    field = ZONE_MEASUREMENT.get(zone)
    if not field:
        return None, None

    col = getattr(BodyMeasurement, field)
    rows = db.execute(
        select(BodyMeasurement.measured_at, col)
        .where(BodyMeasurement.user_id == user_id)
        .where(col.is_not(None))
        .where(BodyMeasurement.measured_at >= window_start)
        .order_by(BodyMeasurement.measured_at.asc())
    ).all()

    if len(rows) < 2:
        return None, None

    first_val = rows[0][1]
    last_val = rows[-1][1]
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
    unit = " kg" if field == "weight_kg" else " cm"
    label = f"{sign}{diff:.1f}{unit}"

    return score, label


def _compute_confidence(
    hard_sets: int, session_count: int,
    has_anthropo: bool, has_weight: bool, has_waist: bool,
) -> str:
    """Compute confidence level from data availability signals."""
    signals = 0
    if hard_sets >= 4:
        signals += 1
    if session_count >= 2:
        signals += 1
    if has_anthropo:
        signals += 1
    if has_weight:
        signals += 1
    if has_waist:
        signals += 1

    if signals >= 4:
        return "élevée"
    elif signals >= 2:
        return "moyenne"
    return "faible"


def _top_exercises(entries: list[dict], n: int = 3) -> list[str]:
    """Get top N most frequent exercises from entries."""
    counts: dict[str, int] = defaultdict(int)
    for e in entries:
        counts[e["exercise"]] += 1
    sorted_exs = sorted(counts.items(), key=lambda x: -x[1])
    return [name for name, _ in sorted_exs[:n]]


def compute_physique_dashboard(
    db: Session, user_id: int, window_days: int = 30
) -> PhysiqueDashboard:
    """Compute the full physique dashboard for a user."""
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(days=window_days)

    # Get performance data
    zone_data = _compute_tonnage_by_zone(db, user_id, window_start)

    # Check for body measurement data availability
    weight_count = db.execute(
        select(func.count(BodyMeasurement.id))
        .where(BodyMeasurement.user_id == user_id)
        .where(BodyMeasurement.weight_kg.is_not(None))
    ).scalar_one() or 0
    waist_count = db.execute(
        select(func.count(BodyMeasurement.id))
        .where(BodyMeasurement.user_id == user_id)
        .where(BodyMeasurement.waist_cm.is_not(None))
    ).scalar_one() or 0

    has_weight = weight_count >= 2
    has_waist = waist_count >= 1

    # Compute per-zone scores
    zone_scores: list[ZoneScore] = []

    for zone, label in ZONE_LABELS.items():
        entries = zone_data.get(zone, [])
        hard_sets = sum(e["hard_sets"] for e in entries)
        session_dates = {e["date"].date() for e in entries}
        session_count = len(session_dates)

        # Pillar 1: Performance
        perf_score, trend = _score_performance(entries)

        # Pillar 2: Exposure
        expo_score = _score_exposure(hard_sets, zone, window_days)

        # Pillar 3: Anthropometry
        anthropo_score, anthropo_label = _score_anthropo(
            db, user_id, zone, window_start
        )

        # Composite score
        if anthropo_score is not None:
            score = 0.50 * perf_score + 0.30 * expo_score + 0.20 * anthropo_score
        else:
            score = 0.60 * perf_score + 0.40 * expo_score

        # Confidence
        has_anthropo = anthropo_score is not None
        confidence = _compute_confidence(
            hard_sets, session_count, has_anthropo, has_weight, has_waist
        )

        # Measurement label
        meas_field = ZONE_MEASUREMENT.get(zone)
        from app.services.measurements import MEASUREMENT_LABELS
        meas_label = MEASUREMENT_LABELS.get(meas_field) if meas_field else None

        zone_scores.append(ZoneScore(
            zone=zone,
            label=label,
            score=round(score, 1),
            trend=trend,
            confidence=confidence,
            hard_sets=hard_sets,
            session_count=session_count,
            top_exercises=_top_exercises(entries),
            measurement_label=meas_label,
            measurement_trend=anthropo_label,
        ))

    # Aggregate to radar axes
    radar_axes: list[RadarAxis] = []
    for axis_key in RADAR_AXIS_ORDER:
        axis_def = RADAR_AXES[axis_key]
        child_scores = [z for z in zone_scores if z.zone in axis_def["zones"]]
        if child_scores:
            avg_score = sum(z.score for z in child_scores) / len(child_scores)
            # Worst confidence among children
            conf_order = {"faible": 0, "moyenne": 1, "élevée": 2}
            worst_conf = min(child_scores, key=lambda z: conf_order.get(z.confidence, 0))
            conf = worst_conf.confidence
        else:
            avg_score = 0.0
            conf = "faible"

        radar_axes.append(RadarAxis(
            axis=axis_key,
            label=axis_def["label"],
            score=round(avg_score, 1),
            confidence=conf,
        ))

    # Global score
    global_score = sum(a.score for a in radar_axes) / len(radar_axes) if radar_axes else 0
    global_score = round(global_score, 1)

    if global_score >= 75:
        global_grade = "A"
    elif global_score >= 50:
        global_grade = "B"
    else:
        global_grade = "C"

    # Radar SVG
    radar_svg = build_radar_svg(radar_axes)

    return PhysiqueDashboard(
        global_score=global_score,
        global_grade=global_grade,
        zone_scores=zone_scores,
        radar_axes=radar_axes,
        radar_svg=radar_svg,
        window_days=window_days,
    )
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_muscle_scoring.py -v`
Expected: FAIL because `app.services.radar` doesn't exist yet. That's expected — Task 3 creates it. For now, create a minimal stub so tests can pass:

Create `app/services/radar.py` with just:
```python
def build_radar_svg(axes, size=300):
    return "<svg></svg>"
```

Then run: `pytest tests/test_muscle_scoring.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add app/services/muscle_scoring.py app/services/radar.py tests/test_muscle_scoring.py
git commit -m "feat: add muscle scoring service — composite score + confidence"
```

---

### Task 3: Radar SVG builder

**Files:**
- Rewrite: `app/services/radar.py` (replace stub)

- [ ] **Step 1: Write failing test**

Append to `tests/test_muscle_scoring.py`:

```python
from app.services.radar import build_radar_svg
from app.services.muscle_scoring import RadarAxis


def test_radar_svg_renders():
    axes = [
        RadarAxis(axis="pecs", label="Pectoraux", score=80, confidence="élevée"),
        RadarAxis(axis="shoulders", label="Épaules", score=60, confidence="moyenne"),
        RadarAxis(axis="back_width", label="Dos largeur", score=70, confidence="élevée"),
        RadarAxis(axis="back_thickness", label="Dos épaisseur", score=50, confidence="faible"),
        RadarAxis(axis="arms", label="Bras", score=65, confidence="moyenne"),
        RadarAxis(axis="lower", label="Bas du corps", score=55, confidence="faible"),
    ]
    svg = build_radar_svg(axes)
    assert "<svg" in svg
    assert "polygon" in svg
    assert "Pectoraux" in svg
    assert "viewBox" in svg


def test_radar_svg_zero_scores():
    axes = [
        RadarAxis(axis=f"a{i}", label=f"L{i}", score=0, confidence="faible")
        for i in range(6)
    ]
    svg = build_radar_svg(axes)
    assert "<svg" in svg
```

- [ ] **Step 2: Implement full radar.py**

Replace `app/services/radar.py`:

```python
# app/services/radar.py
"""Server-rendered SVG hexagonal radar chart for physique dashboard.

Produces a self-contained <svg> with:
  - Hexagonal grid (3 concentric rings at 33/66/100%)
  - Axis lines from center to vertices
  - Labels at each vertex
  - Score polygon (filled accent, semi-transparent)
  - Interactive hover points (CSS .chart-point pattern)
  - Global score centered
"""
from __future__ import annotations

import math


def build_radar_svg(axes: list, size: int = 300) -> str:
    """Build a hexagonal radar SVG from RadarAxis objects.

    Each axis has .label (str) and .score (0-100).
    Returns a self-contained SVG string.
    """
    if not axes:
        return ""

    n = len(axes)
    cx = size / 2
    cy = size / 2
    radius = size / 2 - 40  # padding for labels
    angle_step = 2 * math.pi / n
    # Start from top (–π/2)
    start_angle = -math.pi / 2

    def polar(angle: float, r: float) -> tuple[float, float]:
        return cx + r * math.cos(angle), cy + r * math.sin(angle)

    parts: list[str] = []

    parts.append(
        f'<svg viewBox="0 0 {size} {size}" '
        f'xmlns="http://www.w3.org/2000/svg" '
        f'class="chart--interactive" '
        f'style="width:100%;max-width:{size}px;height:auto;" '
        f'role="img" aria-label="Radar physique">'
    )

    # Background
    parts.append(
        f'<rect x="0" y="0" width="{size}" height="{size}" '
        f'fill="#161a22" rx="8"/>'
    )

    # Concentric hexagons (33%, 66%, 100%)
    for pct in [0.33, 0.66, 1.0]:
        r = radius * pct
        hex_points = " ".join(
            f"{polar(start_angle + i * angle_step, r)[0]:.1f},"
            f"{polar(start_angle + i * angle_step, r)[1]:.1f}"
            for i in range(n)
        )
        parts.append(
            f'<polygon points="{hex_points}" fill="none" '
            f'stroke="#232834" stroke-width="1"/>'
        )

    # Axis lines
    for i in range(n):
        angle = start_angle + i * angle_step
        x2, y2 = polar(angle, radius)
        parts.append(
            f'<line x1="{cx:.1f}" y1="{cy:.1f}" '
            f'x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="#232834" stroke-width="1"/>'
        )

    # Score polygon
    score_points = []
    for i, axis in enumerate(axes):
        angle = start_angle + i * angle_step
        r = radius * (axis.score / 100) if axis.score > 0 else 0
        x, y = polar(angle, r)
        score_points.append(f"{x:.1f},{y:.1f}")

    polygon_str = " ".join(score_points)
    parts.append(
        f'<polygon points="{polygon_str}" '
        f'fill="#f25f3a" fill-opacity="0.15" '
        f'stroke="#f25f3a" stroke-width="2" '
        f'stroke-linejoin="round"/>'
    )

    # Data points (interactive)
    for i, axis in enumerate(axes):
        angle = start_angle + i * angle_step
        r = radius * (axis.score / 100) if axis.score > 0 else 0
        x, y = polar(angle, r)
        score_txt = f"{axis.score:.0f}"

        parts.append(f'<g class="chart-point">')
        parts.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="14" '
            f'fill="transparent" class="chart-point__hit"/>'
        )
        parts.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" '
            f'fill="#f25f3a" class="chart-point__dot"/>'
        )
        # Value label
        label_r = r + 12 if r > 20 else 20
        lx, ly = polar(angle, label_r)
        parts.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" '
            f'text-anchor="middle" dominant-baseline="middle" '
            f'fill="#e8ecf1" font-size="11" font-weight="600" '
            f'font-family="\'JetBrains Mono\',monospace" '
            f'class="chart-point__label">{score_txt}</text>'
        )
        parts.append(f'<title>{axis.label}: {score_txt}/100</title>')
        parts.append('</g>')

    # Axis labels (outside the hexagon)
    for i, axis in enumerate(axes):
        angle = start_angle + i * angle_step
        label_r = radius + 22
        lx, ly = polar(angle, label_r)

        # Adjust text-anchor based on position
        if abs(lx - cx) < 5:
            anchor = "middle"
        elif lx < cx:
            anchor = "end"
        else:
            anchor = "start"

        parts.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" '
            f'text-anchor="{anchor}" dominant-baseline="middle" '
            f'fill="#9aa3ad" font-size="11" '
            f'font-family="\'Inter\',system-ui,sans-serif">'
            f'{axis.label}</text>'
        )

    # Global score center
    global_avg = sum(a.score for a in axes) / len(axes) if axes else 0
    parts.append(
        f'<text x="{cx:.1f}" y="{cy:.1f}" '
        f'text-anchor="middle" dominant-baseline="middle" '
        f'fill="#e8ecf1" font-size="28" font-weight="700" '
        f'font-family="\'JetBrains Mono\',monospace">'
        f'{global_avg:.0f}</text>'
    )

    parts.append("</svg>")
    return "\n".join(parts)
```

- [ ] **Step 3: Run tests**

Run: `pytest tests/test_muscle_scoring.py -v`
Expected: All PASS

- [ ] **Step 4: Commit**

```bash
git add app/services/radar.py tests/test_muscle_scoring.py
git commit -m "feat: add radar hexagon SVG builder for physique dashboard"
```

---

### Task 4: Re-add waist_cm to measurements

**Files:**
- Modify: `app/services/measurements.py`
- Modify: `app/routers/auth_routes.py`

- [ ] **Step 1: Add waist_cm to MEASUREMENT_FIELDS**

In `app/services/measurements.py`, add `waist_cm` to the 3 dicts and update MEASUREMENT_FIELDS:

Add between `arm_cm` and `thigh_cm` in each dict:
```python
# In MEASUREMENT_MUSCLE_MAP:
    "waist_cm": ["abdos", "abs", "cardio"],

# In MEASUREMENT_LABELS:
    "waist_cm": "Tour de taille (cm)",

# In MEASUREMENT_UNITS:
    "waist_cm": " cm",
```

- [ ] **Step 2: Add waist_cm to POST endpoint**

In `app/routers/auth_routes.py`, in the `profile_measurements_submit` function:
- Add `waist_cm: Annotated[str, Form()] = "",` parameter
- Add `waist = _float_or_none(waist_cm, 10.0, 200.0)` parsing
- Add `waist` to the skip-if-all-empty check
- Add `waist` to the upsert logic (update + create)

- [ ] **Step 3: Update test**

In `tests/test_measurements.py`, update `test_muscle_map_has_all_fields`:
```python
    assert set(MEASUREMENT_MUSCLE_MAP.keys()) == {
        "weight_kg", "chest_cm", "arm_cm", "waist_cm", "thigh_cm",
    }
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_measurements.py tests/test_profile_measurements.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add app/services/measurements.py app/routers/auth_routes.py tests/test_measurements.py
git commit -m "feat: re-add waist_cm to body measurements for physique scoring"
```

---

### Task 5: Route + template + CSS + nav

**Files:**
- Modify: `app/routers/pages.py`
- Create: `app/templates/physique.html`
- Modify: `app/templates/base.html`
- Modify: `app/static/css/app.css`

- [ ] **Step 1: Add route to pages.py**

Add at the end of `app/routers/pages.py`:

```python
@router.get("/physique", response_class=HTMLResponse)
def physique(
    request: Request,
    db: DbSession,
    user: CurrentUser,
    window: int = Query(30),
) -> HTMLResponse:
    from app.services.muscle_scoring import compute_physique_dashboard

    window = window if window in (30, 60, 90) else 30
    dashboard = compute_physique_dashboard(db, user.id, window_days=window)

    return templates.TemplateResponse(
        request,
        "physique.html",
        {
            "page_title": "Physique",
            "dashboard": dashboard,
            "window": window,
            "active_session": latest_open_session(db, user.id),
        },
    )
```

- [ ] **Step 2: Create physique.html template**

Create `app/templates/physique.html` with:
- Page title "Physique"
- Global score (JetBrains Mono 32px, grade badge A/B/C)
- Cockpit grid: left = radar SVG + window selector, right = zone cards
- Window selector: 3 links (30j/60j/90j) as `.filter-bar` pills
- Zone cards: `.zone-card` with bar, confidence dot, details
- Mobile: all stacked

```html
{% extends "base.html" %}
{% block content %}
<h1 class="page-title">Physique</h1>

<div class="cockpit-grid">
  <div class="cockpit-main">
    <div class="card" style="text-align:center;">
      <span class="global-score">{{ "%.0f"|format(dashboard.global_score) }}</span>
      <span class="grade-badge grade-badge--{{ dashboard.global_grade|lower }}">{{ dashboard.global_grade }}</span>
      <div class="radar-wrap">{{ dashboard.radar_svg|safe }}</div>
    </div>

    <nav class="filter-bar" style="margin-top:var(--space-md);">
      <a class="filter-bar__item {% if window == 30 %}is-active{% endif %}"
         href="{{ url_for('physique') }}?window=30">30j</a>
      <a class="filter-bar__item {% if window == 60 %}is-active{% endif %}"
         href="{{ url_for('physique') }}?window=60">60j</a>
      <a class="filter-bar__item {% if window == 90 %}is-active{% endif %}"
         href="{{ url_for('physique') }}?window=90">90j</a>
    </nav>
  </div>

  <div class="cockpit-side">
    <h2 class="section-header">Détail par zone</h2>
    {% for z in dashboard.zone_scores %}
    <div class="zone-card">
      <div class="zone-card__header">
        <span class="zone-card__label">{{ z.label }}</span>
        <span class="zone-confidence zone-confidence--{{ z.confidence.split(' ')[-1] if ' ' not in z.confidence else z.confidence }}"
              title="Confiance : {{ z.confidence }}"></span>
      </div>
      <div class="zone-bar">
        <div class="zone-bar__fill" style="width:{{ z.score|round|int }}%"></div>
      </div>
      <div class="zone-card__score">
        <span class="text-mono">{{ "%.0f"|format(z.score) }}/100</span>
        <span class="trend-indicator trend-indicator--{{ z.trend }}">
          {% if z.trend == 'up' %}↑{% elif z.trend == 'down' %}↓{% else %}→{% endif %}
        </span>
      </div>
      <div class="zone-meta">
        {{ z.hard_sets }} hard sets · {{ z.session_count }} séance{% if z.session_count > 1 %}s{% endif %}
      </div>
      {% if z.top_exercises %}
        <div class="zone-meta" style="color:var(--fg-dim);">{{ z.top_exercises|join(', ') }}</div>
      {% endif %}
      {% if z.measurement_trend %}
        <div class="zone-meta">{{ z.measurement_label }}: {{ z.measurement_trend }}</div>
      {% endif %}
    </div>
    {% endfor %}
  </div>
</div>
{% endblock %}
```

- [ ] **Step 3: Add "Physique" nav link to base.html**

In `app/templates/base.html`, add between "Historique" and "Board":

```html
        <a class="topbar__link" href="{{ url_for('physique') }}">Physique</a>
```

- [ ] **Step 4: Add CSS for zone cards and radar**

Append to `app/static/css/app.css` before the desktop media query block:

```css
/* ---------- Physique dashboard ---------- */
.global-score {
  font-family: var(--font-mono);
  font-size: 32px;
  font-weight: 700;
  margin-right: var(--space-sm);
}
.radar-wrap {
  max-width: 320px;
  margin: var(--space-md) auto;
}
.zone-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: var(--space-sm) var(--space-md);
  margin-bottom: var(--space-sm);
}
.zone-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-xs);
}
.zone-card__label {
  font-size: 13px;
  font-weight: 600;
}
.zone-confidence {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}
.zone-confidence--élevée { background: var(--ok); }
.zone-confidence--moyenne { background: var(--warn); }
.zone-confidence--faible { background: var(--fg-dim); }
.zone-bar {
  height: 6px;
  background: var(--surface-2);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: var(--space-xs);
}
.zone-bar__fill {
  height: 100%;
  background: var(--accent);
  border-radius: 3px;
  transition: width 0.3s;
}
.zone-card__score {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  margin-bottom: 2px;
}
.zone-meta {
  font-size: 12px;
  color: var(--fg-muted);
  line-height: 1.4;
}
```

- [ ] **Step 5: Run tests**

Run: `pytest tests/test_muscle_scoring.py -v`
Expected: All PASS

Also run: `pytest tests/test_session_flow.py -v` to verify no nav breakage.

- [ ] **Step 6: Commit**

```bash
git add app/routers/pages.py app/templates/physique.html app/templates/base.html app/static/css/app.css
git commit -m "feat: add /physique dashboard page — radar, zone cards, nav link"
```

---

### Task 6: Integration test + final verification

- [ ] **Step 1: Add integration test**

Append to `tests/test_muscle_scoring.py`:

```python
def test_physique_page_renders(client):
    r = client.get("/physique")
    assert r.status_code == 200
    assert "Physique" in r.text
    assert "radar" in r.text.lower() or "svg" in r.text.lower()
    assert "zone-card" in r.text


def test_physique_page_window_param(client):
    r = client.get("/physique?window=60")
    assert r.status_code == 200
    assert "60j" in r.text or 'is-active' in r.text


def test_physique_page_requires_auth(client):
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()
    r = client.get("/physique", follow_redirects=False)
    assert r.status_code == 303
```

- [ ] **Step 2: Run full test suite**

Run: `pytest --tb=short -q`
Expected: All tests PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_muscle_scoring.py
git commit -m "test: add integration tests for physique dashboard page"
```
