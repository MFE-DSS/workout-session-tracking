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

    # zone -> list of {date, tonnage, exercise_name}
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
    from app.services.measurements import compute_zone_measurement

    field_name = ZONE_MEASUREMENT.get(zone)
    if not field_name:
        return None, None

    # Get all measurements in window
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
        meas_label = None
        if meas_field:
            _ZONE_DISPLAY_LABELS = {
                "chest_cm": "Tour de poitrine",
                "arm_avg": "Tour de bras (moy.)",
                "thigh_avg": "Tour de cuisses (moy.)",
                "waist_cm": "Tour de taille",
            }
            meas_label = _ZONE_DISPLAY_LABELS.get(meas_field)

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
