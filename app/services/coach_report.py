"""Sb_23 — Coach Report orchestrator.

Builds a single ``CoachReport`` dataclass consumed by templates/coach_report.html.
Reuses ``services/profile_metrics.py`` (Sb_22b) — no duplicated query
layer. Adds two derivations specific to the Coach Report:

* weight trend over 90 days (from BodyMeasurement + Sb_17 merge)
* approximate age (from users.year_of_birth if present, else None)

Spec contract (SPIGNOS_COACH_REPORT_SPEC_v1 v1.1 §B.bis): every block of
the report carries an explicit tag in {Mesuré, Inféré, Non déductible}.
The orchestrator does NOT add interpretation — that's coach_inference's
job. This module collects raw facts only.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.measurement import BodyMeasurement
from app.models.session import WorkoutSession
from app.models.user import User
from app.services.muscle_mapping import RADAR_AXES
from app.services.profile_metrics import (
    DisciplineRates,
    LastSession,
    PreviewPayload,
    StrengthCardioRatio,
    build_preview,
    discipline_rates,
    last_session_summary,
    pattern_distribution,
    strength_cardio_ratio,
    zone_session_counts,
)


# ---------------------------------------------------------------------------
# Identity block
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class IdentityBlock:
    username: str
    report_date: str            # ISO date (no time, no tz)
    height_cm: int | None
    weight_kg: float | None
    weight_trend_kg_90d: float | None  # signed delta, None if no baseline
    waist_cm: float | None
    resting_hr: int | None
    bp_systolic: int | None
    bp_diastolic: int | None
    year_of_birth: int | None   # None V1 (column doesn't exist)


def _weight_trend_90d(db: Session, user_id: int) -> float | None:
    """Delta entre poids le plus récent et poids le plus ancien dans la
    fenêtre 90j. None si < 2 mesures. Source : BodyMeasurement +
    WorkoutSession.bodyweight_kg (Sb_17 merge — déjà unifiés au niveau
    measurements.py, mais on requête directement les 2 tables ici pour
    rester lisible et testable).
    """
    window = datetime.now(timezone.utc) - timedelta(days=90)
    points: list[tuple[datetime, float]] = []
    # BodyMeasurement
    bm_rows = db.execute(
        select(BodyMeasurement.measured_at, BodyMeasurement.weight_kg)
        .where(
            BodyMeasurement.user_id == user_id,
            BodyMeasurement.measured_at >= window,
            BodyMeasurement.weight_kg.is_not(None),
        )
    ).all()
    points.extend((r[0], float(r[1])) for r in bm_rows)
    # WorkoutSession.bodyweight_kg (Sb_17)
    ws_rows = db.execute(
        select(WorkoutSession.started_at, WorkoutSession.bodyweight_kg)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == "completed",
            WorkoutSession.excluded_from_stats.is_(False),
            WorkoutSession.started_at >= window,
            WorkoutSession.bodyweight_kg.is_not(None),
        )
    ).all()
    points.extend((r[0], float(r[1])) for r in ws_rows)
    if len(points) < 2:
        return None
    points.sort(key=lambda p: p[0])
    return round(points[-1][1] - points[0][1], 1)


def _identity(db: Session, user: User) -> IdentityBlock:
    return IdentityBlock(
        username=user.username,
        report_date=datetime.now(timezone.utc).date().isoformat(),
        height_cm=user.height_cm,
        weight_kg=user.weight_kg,
        weight_trend_kg_90d=_weight_trend_90d(db, user.id),
        waist_cm=user.waist_cm,
        resting_hr=user.resting_hr,
        bp_systolic=user.bp_systolic,
        bp_diastolic=user.bp_diastolic,
        year_of_birth=None,  # V1 — column not in users table
    )


# ---------------------------------------------------------------------------
# Volume block — counts + streak + cardio + sets
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class VolumeBlock:
    sessions_30d: int
    sessions_90d: int
    streak_days: int
    cardio_minutes_per_week: int
    work_sets_per_week: int  # average over 30d


def _work_sets_per_week(db: Session, user_id: int, days: int = 30) -> int:
    from app.models.session import SessionExercise, SetLog
    window_start = datetime.now(timezone.utc) - timedelta(days=days)
    rows = db.execute(
        select(SetLog)
        .join(SessionExercise, SetLog.session_exercise_id == SessionExercise.id)
        .join(WorkoutSession, SessionExercise.session_id == WorkoutSession.id)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == "completed",
            WorkoutSession.excluded_from_stats.is_(False),
            WorkoutSession.started_at >= window_start,
            SetLog.kind == "work",
            SetLog.completed.is_(True),
        )
    ).all()
    total = len(rows)
    weeks = max(days / 7, 1)
    return round(total / weeks)


def _sessions_in_window(db: Session, user_id: int, days: int) -> int:
    window_start = datetime.now(timezone.utc) - timedelta(days=days)
    rows = db.execute(
        select(WorkoutSession.id)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == "completed",
            WorkoutSession.excluded_from_stats.is_(False),
            WorkoutSession.started_at >= window_start,
        )
    ).all()
    return len(rows)


def _volume(db: Session, user_id: int, preview: PreviewPayload) -> VolumeBlock:
    return VolumeBlock(
        sessions_30d=preview.sessions_30d,
        sessions_90d=_sessions_in_window(db, user_id, 90),
        streak_days=preview.streak,
        cardio_minutes_per_week=preview.cardio_min_per_week,
        work_sets_per_week=_work_sets_per_week(db, user_id, 30),
    )


# ---------------------------------------------------------------------------
# Zones / patterns blocks
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ZonesBlock:
    counts: list[tuple[str, str, int]]  # [(axis_key, label, n_sessions), ...]
    top_zones: list[tuple[str, str, int]]
    neglected_zones: list[tuple[str, str, int]]


def _zones(db: Session, user_id: int) -> ZonesBlock:
    raw = zone_session_counts(db, user_id, 30)
    labelled = [
        (key, RADAR_AXES.get(key, {}).get("label", key), n)
        for key, n in raw.items()
    ]
    # Sort: descending for top, ascending for neglected.
    by_n_desc = sorted(labelled, key=lambda t: -t[2])
    by_n_asc = sorted(labelled, key=lambda t: t[2])
    return ZonesBlock(
        counts=labelled,
        top_zones=by_n_desc[:3],
        neglected_zones=by_n_asc[:2],
    )


@dataclass(frozen=True)
class PatternsBlock:
    distribution: list[tuple[str, int]]  # [(pattern_motor, pct), ...] sorted desc
    dominant: tuple[str, int] | None


def _patterns(db: Session, user_id: int) -> PatternsBlock:
    dist = pattern_distribution(db, user_id, 30)
    sorted_dist = sorted(dist.items(), key=lambda kv: -kv[1])
    dominant = sorted_dist[0] if sorted_dist else None
    return PatternsBlock(distribution=sorted_dist, dominant=dominant)


# ---------------------------------------------------------------------------
# Coach report — full payload
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CoachReport:
    identity: IdentityBlock
    volume: VolumeBlock
    ratio: StrengthCardioRatio
    zones: ZonesBlock
    patterns: PatternsBlock
    discipline: DisciplineRates
    last_session: LastSession | None


def build_report(db: Session, user: User) -> CoachReport:
    """Single-pass build of the full Coach Report for ``user``.

    Pure read. Never mutates anything. Reuses profile_metrics for all
    primitives — no duplicated query layer.
    """
    sessions_30 = _sessions_in_window(db, user.id, 30)
    preview = build_preview(db, user.id, sessions_30d=sessions_30)
    return CoachReport(
        identity=_identity(db, user),
        volume=_volume(db, user.id, preview),
        ratio=strength_cardio_ratio(db, user.id, 30),
        zones=_zones(db, user.id),
        patterns=_patterns(db, user.id),
        discipline=discipline_rates(db, user.id, 30),
        last_session=last_session_summary(db, user.id),
    )
