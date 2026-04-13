"""Global dashboard service — 5 axes + global score + confidence + degradation.

Computes five orthogonal fitness axes from existing data (no new models):
  1. Consistency — session frequency adherence
  2. Progression — tonnage trends across active zones
  3. Body Trend — circumference evolution
  4. Recovery — readiness self-assessment
  5. Balance — evenness of zone development

Each axis degrades gracefully: if insufficient data, the axis is
marked inactive and excluded from the global score.
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.measurement import BodyMeasurement
from app.models.readiness import ReadinessEntry
from app.models.session import WorkoutSession
from app.services.measurements import compute_arm_avg, compute_thigh_avg
from app.services.muscle_scoring import (
    _compute_tonnage_by_zone,
    _score_performance,
    compute_physique_dashboard,
)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class AxisScore:
    key: str           # "consistency", "progression", "body_trend", "recovery", "balance"
    label: str         # French display name
    score: float       # 0-100
    trend: str         # "up", "down", "stable"
    confidence: str    # "élevée", "moyenne", "faible", "insuffisante"
    detail: str        # Human-readable detail line
    active: bool       # False if insufficient data
    guidance: str = "" # What user should do to activate this axis


@dataclass
class DashboardResult:
    global_score: float | None  # None if no active axes
    global_grade: str           # "A", "B", "C", or "—"
    global_confidence: str
    active_count: int
    total_count: int            # Always 5
    axes: list[AxisScore]
    window_days: int


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _confidence_from_ratio(actual: int, minimum: int) -> str:
    """Return confidence tier from actual/minimum data ratio."""
    if actual < minimum:
        return "insuffisante"
    ratio = actual / minimum if minimum > 0 else 0
    if ratio >= 3:
        return "élevée"
    if ratio >= 1.5:
        return "moyenne"
    return "faible"


def _trend_from_halves(first_half: float, second_half: float) -> str:
    """Compare two half-window values and return trend direction."""
    if second_half > first_half * 1.1:
        return "up"
    if second_half < first_half * 0.9:
        return "down"
    return "stable"


def _trend_label(trend: str) -> str:
    """Return French label for a trend direction."""
    return {"up": "en hausse", "down": "en baisse", "stable": "stable"}.get(
        trend, "stable"
    )


def _compute_grade(score: float) -> str:
    """A (>=75), B (>=50), C (<50)."""
    if score >= 75:
        return "A"
    if score >= 50:
        return "B"
    return "C"


# ---------------------------------------------------------------------------
# Axis 1 — Consistency
# ---------------------------------------------------------------------------

def compute_consistency_axis(
    db: Session, user_id: int, window_days: int = 30
) -> AxisScore:
    """Score based on session frequency relative to 4×/week target."""
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(days=window_days)

    rows = db.execute(
        select(WorkoutSession.started_at)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == "completed",
            WorkoutSession.excluded_from_stats.is_(False),
            WorkoutSession.started_at >= window_start,
        )
    ).scalars().all()

    actual = len(rows)
    expected = 4 * window_days / 7
    minimum = 2

    if actual < minimum:
        return AxisScore(
            key="consistency",
            label="Régularité",
            score=0,
            trend="stable",
            confidence="insuffisante",
            detail=f"{actual} séance(s) — données insuffisantes",
            active=False,
            guidance="Complétez au moins 2 séances pour activer cet axe.",
        )

    score = min(100.0, actual / expected * 100)

    # Trend: first half vs second half session count
    mid = window_start + timedelta(days=window_days / 2)
    # SQLite may return naive datetimes — strip tzinfo for comparison
    mid_naive = mid.replace(tzinfo=None)
    first_half = sum(1 for d in rows if d.replace(tzinfo=None) < mid_naive)
    second_half = sum(1 for d in rows if d.replace(tzinfo=None) >= mid_naive)
    trend = _trend_from_halves(first_half, second_half)

    confidence = _confidence_from_ratio(actual, minimum)

    return AxisScore(
        key="consistency",
        label="Régularité",
        score=round(score, 1),
        trend=trend,
        confidence=confidence,
        detail=f"{actual} séances / {round(expected)} attendues — {_trend_label(trend)}",
        active=True,
    )


# ---------------------------------------------------------------------------
# Axis 2 — Progression
# ---------------------------------------------------------------------------

def compute_progression_axis(
    db: Session, user_id: int, window_days: int = 30
) -> AxisScore:
    """Score based on tonnage progression across active zones."""
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(days=window_days)

    zone_data = _compute_tonnage_by_zone(db, user_id, window_start)

    # Count total sessions in window (for minimum check)
    session_count = db.execute(
        select(func.count(WorkoutSession.id))
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == "completed",
            WorkoutSession.excluded_from_stats.is_(False),
            WorkoutSession.started_at >= window_start,
        )
    ).scalar_one() or 0

    # Active zones = those with >= 4 hard sets
    active_zones = {
        zone: entries
        for zone, entries in zone_data.items()
        if sum(e["hard_sets"] for e in entries) >= 4
    }

    if session_count < 4 or len(active_zones) < 2:
        return AxisScore(
            key="progression",
            label="Progression",
            score=0,
            trend="stable",
            confidence="insuffisante",
            detail=f"{session_count} séance(s), {len(active_zones)} zone(s) active(s) — données insuffisantes",
            active=False,
            guidance="4 séances et 2 zones actives (≥4 séries) requises.",
        )

    # Score = mean of _score_performance per active zone
    scores = []
    trends = []
    for zone, entries in active_zones.items():
        s, t = _score_performance(entries)
        scores.append(s)
        trends.append(t)

    score = statistics.mean(scores)

    # Trend = majority vote
    trend_counts = {"up": 0, "down": 0, "stable": 0}
    for t in trends:
        trend_counts[t] = trend_counts.get(t, 0) + 1
    trend = max(trend_counts, key=trend_counts.get)  # type: ignore[arg-type]

    confidence = _confidence_from_ratio(len(active_zones), 2)

    return AxisScore(
        key="progression",
        label="Progression",
        score=round(score, 1),
        trend=trend,
        confidence=confidence,
        detail=f"{len(active_zones)} zones actives — tonnage {_trend_label(trend)}",
        active=True,
    )


# ---------------------------------------------------------------------------
# Axis 3 — Body Trend
# ---------------------------------------------------------------------------

def compute_body_trend_axis(
    db: Session, user_id: int, window_days: int = 30
) -> AxisScore:
    """Score based on circumference measurement evolution."""
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(days=window_days)

    rows = db.execute(
        select(BodyMeasurement)
        .where(
            BodyMeasurement.user_id == user_id,
            BodyMeasurement.measured_at >= window_start,
        )
        .order_by(BodyMeasurement.measured_at.asc())
    ).scalars().all()

    if len(rows) < 3:
        return AxisScore(
            key="body_trend",
            label="Évolution corporelle",
            score=0,
            trend="stable",
            confidence="insuffisante",
            detail=f"{len(rows)} mesure(s) — minimum 3 requises",
            active=False,
            guidance="Prenez au moins 3 mesures corporelles pour activer cet axe.",
        )

    first = rows[0]
    last = rows[-1]

    # Score each site
    site_scores = []

    def _score_site(first_val: float | None, last_val: float | None, inverse: bool = False) -> float | None:
        if first_val is None or last_val is None or first_val == 0:
            return None
        diff = last_val - first_val
        if inverse:
            diff = -diff
        pct = diff / first_val * 100
        if pct <= -2:
            return 30.0
        if pct <= 0.5:
            return 50.0
        if pct <= 2:
            return 70.0
        return 90.0

    # chest_cm
    s = _score_site(first.chest_cm, last.chest_cm)
    if s is not None:
        site_scores.append(s)

    # arm_avg
    s = _score_site(compute_arm_avg(first), compute_arm_avg(last))
    if s is not None:
        site_scores.append(s)

    # thigh_avg
    s = _score_site(compute_thigh_avg(first), compute_thigh_avg(last))
    if s is not None:
        site_scores.append(s)

    # waist_cm (inverse — lower is better)
    s = _score_site(first.waist_cm, last.waist_cm, inverse=True)
    if s is not None:
        site_scores.append(s)

    if len(site_scores) < 2:
        return AxisScore(
            key="body_trend",
            label="Évolution corporelle",
            score=0,
            trend="stable",
            confidence="insuffisante",
            detail=f"{len(rows)} mesures mais {len(site_scores)} site(s) exploitable(s) — minimum 2",
            active=False,
            guidance="Mesurez au moins 2 sites (poitrine, bras, cuisses, taille).",
        )

    score = statistics.mean(site_scores)

    # Trend: compare first half vs second half measurement count as proxy
    mid = rows[len(rows) // 2].measured_at
    first_vals = [s for s in site_scores[:len(site_scores) // 2]] if len(site_scores) > 1 else site_scores
    second_vals = [s for s in site_scores[len(site_scores) // 2:]] if len(site_scores) > 1 else site_scores
    trend = "up" if score >= 60 else ("down" if score < 40 else "stable")

    confidence = _confidence_from_ratio(len(rows), 3)

    return AxisScore(
        key="body_trend",
        label="Évolution corporelle",
        score=round(score, 1),
        trend=trend,
        confidence=confidence,
        detail=f"{len(site_scores)} sites analysés — score {_trend_label(trend)}",
        active=True,
    )


# ---------------------------------------------------------------------------
# Axis 4 — Recovery
# ---------------------------------------------------------------------------

def compute_recovery_axis(
    db: Session, user_id: int
) -> AxisScore:
    """Score based on readiness self-assessment (last 7 days, min 5 in 30d)."""
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)
    seven_days_ago = today - timedelta(days=7)

    # Check minimum: 5 entries in last 30 days
    total_entries = db.execute(
        select(func.count(ReadinessEntry.id))
        .where(
            ReadinessEntry.user_id == user_id,
            ReadinessEntry.recorded_on >= thirty_days_ago,
        )
    ).scalar_one() or 0

    if total_entries < 5:
        return AxisScore(
            key="recovery",
            label="Récupération",
            score=0,
            trend="stable",
            confidence="insuffisante",
            detail=f"{total_entries} entrée(s) sur 30j — minimum 5 requises",
            active=False,
            guidance="Remplissez le questionnaire de readiness au moins 5 fois en 30 jours.",
        )

    # Get last 7 days of entries
    recent = db.execute(
        select(ReadinessEntry)
        .where(
            ReadinessEntry.user_id == user_id,
            ReadinessEntry.recorded_on >= seven_days_ago,
        )
        .order_by(ReadinessEntry.recorded_on.asc())
    ).scalars().all()

    if not recent:
        # Has 5+ in 30d but none in last 7d — still active but low signal
        return AxisScore(
            key="recovery",
            label="Récupération",
            score=50.0,
            trend="stable",
            confidence="faible",
            detail="Aucune entrée sur les 7 derniers jours",
            active=True,
        )

    # Mean of 5 dimensions per entry, then mean across entries
    entry_means = []
    for e in recent:
        dims = [
            e.sleep_quality,
            e.fatigue_level,
            e.soreness_level,
            e.stress_level,
            e.motivation_level,
        ]
        entry_means.append(statistics.mean(dims))

    global_mean = statistics.mean(entry_means)
    score = (global_mean - 1) / 4 * 100

    # Trend: last 3 days vs days 4-7
    if len(recent) >= 4:
        last_3 = entry_means[-3:] if len(entry_means) >= 3 else entry_means
        earlier = entry_means[:-3] if len(entry_means) > 3 else entry_means[:1]
        avg_recent = statistics.mean(last_3)
        avg_earlier = statistics.mean(earlier)
        if avg_recent - avg_earlier > 0.3:
            trend = "up"
        elif avg_earlier - avg_recent > 0.3:
            trend = "down"
        else:
            trend = "stable"
    else:
        trend = "stable"

    confidence = _confidence_from_ratio(len(recent), 5)

    return AxisScore(
        key="recovery",
        label="Récupération",
        score=round(score, 1),
        trend=trend,
        confidence=confidence,
        detail=f"Moyenne readiness {global_mean:.1f}/5 — {_trend_label(trend)}",
        active=True,
    )


# ---------------------------------------------------------------------------
# Axis 5 — Balance
# ---------------------------------------------------------------------------

def compute_balance_axis(
    db: Session, user_id: int, window_days: int = 30
) -> AxisScore:
    """Score based on evenness of zone development (CV of zone scores)."""
    dashboard = compute_physique_dashboard(db, user_id, window_days)

    active_zones = [z for z in dashboard.zone_scores if z.hard_sets > 0]

    if len(active_zones) < 4:
        return AxisScore(
            key="balance",
            label="Équilibre musculaire",
            score=0,
            trend="stable",
            confidence="insuffisante",
            detail=f"{len(active_zones)} zone(s) active(s) — minimum 4 requises",
            active=False,
            guidance="Travaillez au moins 4 zones musculaires différentes.",
        )

    zone_scores_vals = [z.score for z in active_zones]
    mean_val = statistics.mean(zone_scores_vals)

    if mean_val == 0:
        cv = 0.0
    else:
        stdev = statistics.stdev(zone_scores_vals) if len(zone_scores_vals) > 1 else 0.0
        cv = stdev / mean_val

    score = max(0.0, 100 - cv * 200)
    trend = "stable"  # V1: always stable

    confidence = _confidence_from_ratio(len(active_zones), 4)

    return AxisScore(
        key="balance",
        label="Équilibre musculaire",
        score=round(score, 1),
        trend=trend,
        confidence=confidence,
        detail=f"{len(active_zones)} zones — CV {cv:.2f}",
        active=True,
    )


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def compute_dashboard(
    db: Session, user_id: int, window_days: int = 30
) -> DashboardResult:
    """Compute the full 5-axis dashboard for a user."""
    axes = [
        compute_consistency_axis(db, user_id, window_days),
        compute_progression_axis(db, user_id, window_days),
        compute_body_trend_axis(db, user_id, window_days),
        compute_recovery_axis(db, user_id),
        compute_balance_axis(db, user_id, window_days),
    ]

    active_axes = [a for a in axes if a.active]
    active_count = len(active_axes)

    if active_count == 0:
        return DashboardResult(
            global_score=None,
            global_grade="—",
            global_confidence="insuffisante",
            active_count=0,
            total_count=5,
            axes=axes,
            window_days=window_days,
        )

    global_score = statistics.mean(a.score for a in active_axes)
    global_grade = _compute_grade(global_score)

    # Confidence: worst among active axes
    conf_order = {"insuffisante": 0, "faible": 1, "moyenne": 2, "élevée": 3}
    global_confidence = min(
        (a.confidence for a in active_axes),
        key=lambda c: conf_order.get(c, 0),
    )

    return DashboardResult(
        global_score=round(global_score, 1),
        global_grade=global_grade,
        global_confidence=global_confidence,
        active_count=active_count,
        total_count=5,
        axes=axes,
        window_days=window_days,
    )
