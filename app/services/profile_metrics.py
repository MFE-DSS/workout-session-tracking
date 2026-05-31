"""Sb_22b — profile metrics primitives.

Pure read-only helpers consumed by the L2 preview card and the L3
profile page. Also reusable by Sb_23 (Coach Report). Every function
takes ``(db, user_id, days=30)`` and returns a small typed payload.

Spec contract (SPIGNOS_PROFILE_SYNTHESIS_SPEC_v2 §A.bis hierarchy):
* L1 (leaderboard line) doesn't call these — uses LeaderboardEntry.
* L2 (preview card) uses ``streak``, ``cardio_minutes_per_week``,
  ``volume_delta_pct``.
* L3 (profile page) uses ``top_zone``, ``neglected_zone``,
  ``dominant_pattern``, ``last_session_summary`` in addition.

All windows are aligned to UTC midnight buckets — same convention as
the rest of the analytics services.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.session import SessionExercise, SetLog, WorkoutSession
from app.services.muscle_mapping import RADAR_AXIS_ORDER, classify_exercise

_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


# ---------------------------------------------------------------------------
# Internal cached registry for pattern_motor (re-uses Sb_22a data)
# ---------------------------------------------------------------------------

_PROPERTIES_CACHE: dict | None = None


def _load_properties() -> dict:
    global _PROPERTIES_CACHE
    if _PROPERTIES_CACHE is None:
        path = _DATA_DIR / "exercise_properties.json"
        if path.exists():
            _PROPERTIES_CACHE = json.loads(path.read_text(encoding="utf-8")).get(
                "exercises", {}
            )
        else:
            _PROPERTIES_CACHE = {}
    return _PROPERTIES_CACHE


# ---------------------------------------------------------------------------
# Streak
# ---------------------------------------------------------------------------


def streak_days(db: Session, user_id: int) -> int:
    """Consecutive days (UTC) with ≥ 1 completed session, ending today
    or yesterday (so a streak doesn't break if the day isn't over yet
    in the user's local tz). Returns 0 if no eligible session."""
    sessions = db.execute(
        select(WorkoutSession.started_at)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == "completed",
            WorkoutSession.excluded_from_stats.is_(False),
        )
        .order_by(WorkoutSession.started_at.desc())
    ).scalars().all()
    if not sessions:
        return 0
    dates = sorted({s.date() for s in sessions}, reverse=True)
    today = datetime.now(timezone.utc).date()
    # Start from today OR yesterday so we don't lose a streak before
    # midnight UTC (common timezone offset).
    if dates[0] == today:
        expected = today
    elif dates[0] == today - timedelta(days=1):
        expected = today - timedelta(days=1)
    else:
        return 0
    streak = 0
    for d in dates:
        if d == expected:
            streak += 1
            expected = expected - timedelta(days=1)
        elif d < expected:
            break
    return streak


# ---------------------------------------------------------------------------
# Cardio minutes per week
# ---------------------------------------------------------------------------


def cardio_minutes_per_week(db: Session, user_id: int, days: int = 30) -> int:
    """Average cardio minutes/week computed from the last ``days``.

    Sums ``WorkoutSession.cardio_duration_min`` across eligible sessions
    in the window. cardio_duration_min is set on the feedback form for
    cardio templates (Sb_cardio_capture). Sessions without that value
    don't contribute — no synthetic duration.
    """
    window_start = datetime.now(timezone.utc) - timedelta(days=days)
    rows = db.execute(
        select(WorkoutSession.cardio_duration_min)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == "completed",
            WorkoutSession.excluded_from_stats.is_(False),
            WorkoutSession.started_at >= window_start,
            WorkoutSession.cardio_duration_min.is_not(None),
        )
    ).all()
    total_minutes = sum(r[0] or 0 for r in rows)
    weeks = max(days / 7, 1)
    return round(total_minutes / weeks)


# ---------------------------------------------------------------------------
# Strength volume delta
# ---------------------------------------------------------------------------


def strength_volume_delta_pct(
    db: Session, user_id: int, days: int = 30
) -> int | None:
    """Pct change of completed strength work sets between the last
    ``days`` window and the prior window of equal length. Returns None
    if the prior window is empty (no baseline).
    """
    now = datetime.now(timezone.utc)
    curr_start = now - timedelta(days=days)
    prev_start = now - timedelta(days=days * 2)

    def _count(start, end) -> int:
        # "strength" sessions = those without a cardio_duration_min set.
        # Sb_22b — we don't filter via template.kind because the FK is
        # nullable (SET NULL on template delete) and the snapshot already
        # tells us the answer indirectly (cardio sessions log a duration).
        rows = db.execute(
            select(SetLog)
            .join(SetLog.session_exercise)
            .join(SessionExercise.session)
            .where(
                WorkoutSession.user_id == user_id,
                WorkoutSession.cardio_duration_min.is_(None),
                WorkoutSession.status == "completed",
                WorkoutSession.excluded_from_stats.is_(False),
                WorkoutSession.started_at >= start,
                WorkoutSession.started_at < end,
                SetLog.kind == "work",
                SetLog.completed.is_(True),
            )
        ).all()
        return len(rows)

    curr = _count(curr_start, now)
    prev = _count(prev_start, curr_start)
    if prev == 0:
        return None
    return round(100 * (curr - prev) / prev)


# ---------------------------------------------------------------------------
# Zones / patterns
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ZoneRanking:
    zone: str
    sessions: int


def _eligible_sessions_in_window(
    db: Session, user_id: int, days: int
) -> list[WorkoutSession]:
    window_start = datetime.now(timezone.utc) - timedelta(days=days)
    return list(
        db.execute(
            select(WorkoutSession)
            .where(
                WorkoutSession.user_id == user_id,
                WorkoutSession.status == "completed",
                WorkoutSession.excluded_from_stats.is_(False),
                WorkoutSession.started_at >= window_start,
            )
            .options(selectinload(WorkoutSession.session_exercises))
        ).scalars()
    )


def _zone_session_counts(
    db: Session, user_id: int, days: int = 30
) -> dict[str, int]:
    """Count sessions that include at least one exercise of each zone."""
    sessions = _eligible_sessions_in_window(db, user_id, days)
    counts: dict[str, int] = dict.fromkeys(RADAR_AXIS_ORDER, 0)
    for s in sessions:
        zones_in_session: set[str] = set()
        for se in s.session_exercises:
            primary, _ = classify_exercise(
                se.substituted_name or se.exercise_name_snapshot or ""
            )
            if primary:
                zones_in_session.add(primary)
        for z in zones_in_session:
            if z in counts:
                counts[z] += 1
    return counts


def top_zone(db: Session, user_id: int, days: int = 30) -> ZoneRanking | None:
    counts = _zone_session_counts(db, user_id, days)
    if not counts or max(counts.values()) == 0:
        return None
    zone, n = max(counts.items(), key=lambda kv: (kv[1], -RADAR_AXIS_ORDER.index(kv[0])))
    return ZoneRanking(zone=zone, sessions=n)


def neglected_zone(
    db: Session, user_id: int, days: int = 30
) -> ZoneRanking | None:
    counts = _zone_session_counts(db, user_id, days)
    if not counts:
        return None
    # Lowest count wins; tie-break by RADAR_AXIS_ORDER for determinism.
    zone, n = min(counts.items(), key=lambda kv: (kv[1], RADAR_AXIS_ORDER.index(kv[0])))
    return ZoneRanking(zone=zone, sessions=n)


def dominant_pattern(
    db: Session, user_id: int, days: int = 30
) -> tuple[str, int] | None:
    """Most-used pattern_motor in the window, as (pattern, percentage).

    Percentage = (sets matching this pattern) / (total registered sets) × 100.
    Only sets whose exercise is in exercise_properties.json contribute
    to the denominator — sets on unregistered exos are ignored.
    """
    props = _load_properties()
    if not props:
        return None
    window_start = datetime.now(timezone.utc) - timedelta(days=days)
    rows = db.execute(
        select(SetLog, SessionExercise)
        .join(SessionExercise, SetLog.session_exercise_id == SessionExercise.id)
        .join(WorkoutSession, SessionExercise.session_id == WorkoutSession.id)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.cardio_duration_min.is_(None),
            WorkoutSession.status == "completed",
            WorkoutSession.excluded_from_stats.is_(False),
            WorkoutSession.started_at >= window_start,
            SetLog.kind == "work",
            SetLog.completed.is_(True),
        )
    ).all()
    counts: dict[str, int] = {}
    total = 0
    for _sl, se in rows:
        name = se.substituted_name or se.exercise_name_snapshot
        entry = props.get(name)
        if not entry:
            continue
        pm = entry.get("pattern_motor")
        if not pm:
            continue
        counts[pm] = counts.get(pm, 0) + 1
        total += 1
    if total == 0:
        return None
    pattern, n = max(counts.items(), key=lambda kv: kv[1])
    return pattern, round(100 * n / total)


# ---------------------------------------------------------------------------
# Last session summary
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LastSession:
    template_name: str
    score: int | None
    days_ago: int


def last_session_summary(db: Session, user_id: int) -> LastSession | None:
    from app.services.quality_score import compute_session_quality
    s = db.execute(
        select(WorkoutSession)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == "completed",
            WorkoutSession.excluded_from_stats.is_(False),
        )
        .options(
            selectinload(WorkoutSession.session_exercises)
            .selectinload(SessionExercise.set_logs)
        )
        .order_by(WorkoutSession.started_at.desc())
    ).scalars().first()
    if s is None:
        return None
    today = datetime.now(timezone.utc).date()
    days_ago = (today - s.started_at.date()).days
    return LastSession(
        template_name=s.template_name_snapshot or "—",
        score=compute_session_quality(s),
        days_ago=days_ago,
    )


# ---------------------------------------------------------------------------
# Preview payload (L2) + Page payload (L3) — orchestration
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Sb_23 — discipline + ratios + multi-window primitives for Coach Report
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DisciplineRates:
    """All ratios are in [0, 100] (percentage). Computed on the last
    ``days`` window of eligible completed sessions. None values mean
    "no denominator" (no session in window)."""
    sessions_total: int
    completion_rate: int | None
    with_free_note_rate: int | None
    with_bodyweight_rate: int | None
    with_sensation_rate: int | None
    avg_quality_score: int | None


def discipline_rates(db: Session, user_id: int, days: int = 30) -> DisciplineRates:
    """Compute the 5 discipline ratios used by the Coach Report bloc 6.

    Each ratio = (sessions matching the criterion / total eligible) × 100.

    ``completion_rate`` counts sessions with status == "completed". The
    denominator includes also sessions in 'in_progress' and 'abandoned'
    states in the window to surface abandonment behaviour.
    """
    from app.services.quality_score import compute_session_quality
    window_start = datetime.now(timezone.utc) - timedelta(days=days)
    # Denominator for completion = all sessions started in window
    all_started = db.execute(
        select(WorkoutSession)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.excluded_from_stats.is_(False),
            WorkoutSession.started_at >= window_start,
        )
        .options(
            selectinload(WorkoutSession.session_exercises)
            .selectinload(SessionExercise.set_logs)
        )
    ).scalars().all()
    total_started = len(all_started)
    completed = [s for s in all_started if s.status == "completed"]
    n_completed = len(completed)
    if total_started == 0:
        return DisciplineRates(0, None, None, None, None, None)
    # Rates measured on COMPLETED sessions only (note / bodyweight /
    # sensation are saved at end-of-session via feedback form).
    if n_completed == 0:
        return DisciplineRates(
            sessions_total=total_started,
            completion_rate=0,
            with_free_note_rate=None,
            with_bodyweight_rate=None,
            with_sensation_rate=None,
            avg_quality_score=None,
        )
    n_note = sum(1 for s in completed if (s.free_note or "").strip())
    n_bw = sum(1 for s in completed if s.bodyweight_kg is not None)
    n_sens = sum(
        1 for s in completed
        if any((se.muscle_sensation or "").strip() for se in s.session_exercises)
    )
    quality_scores = [compute_session_quality(s) for s in completed]
    return DisciplineRates(
        sessions_total=total_started,
        completion_rate=round(100 * n_completed / total_started),
        with_free_note_rate=round(100 * n_note / n_completed),
        with_bodyweight_rate=round(100 * n_bw / n_completed),
        with_sensation_rate=round(100 * n_sens / n_completed),
        avg_quality_score=round(sum(quality_scores) / len(quality_scores)),
    )


@dataclass(frozen=True)
class StrengthCardioRatio:
    """Frequency-based split between strength and cardio sessions.

    Spec §C.3 V1 = ratio sur fréquence, pas sur temps (plus stable)."""
    total_sessions: int
    strength_sessions: int
    cardio_sessions: int
    strength_pct: int
    cardio_pct: int


def strength_cardio_ratio(
    db: Session, user_id: int, days: int = 30
) -> StrengthCardioRatio:
    window_start = datetime.now(timezone.utc) - timedelta(days=days)
    sessions = db.execute(
        select(WorkoutSession)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == "completed",
            WorkoutSession.excluded_from_stats.is_(False),
            WorkoutSession.started_at >= window_start,
        )
    ).scalars().all()
    total = len(sessions)
    if total == 0:
        return StrengthCardioRatio(0, 0, 0, 0, 0)
    # Cardio = session with cardio_duration_min set, strength otherwise.
    n_cardio = sum(1 for s in sessions if s.cardio_duration_min is not None)
    n_strength = total - n_cardio
    return StrengthCardioRatio(
        total_sessions=total,
        strength_sessions=n_strength,
        cardio_sessions=n_cardio,
        strength_pct=round(100 * n_strength / total),
        cardio_pct=round(100 * n_cardio / total),
    )


def zone_session_counts(
    db: Session, user_id: int, days: int = 30
) -> dict[str, int]:
    """Public wrapper around _zone_session_counts for the Coach Report."""
    return _zone_session_counts(db, user_id, days)


def pattern_distribution(
    db: Session, user_id: int, days: int = 30
) -> dict[str, int]:
    """Distribution % of work sets by pattern_motor. Returns dict mapping
    pattern → percentage (sums to 100 across registered patterns)."""
    props = _load_properties()
    if not props:
        return {}
    window_start = datetime.now(timezone.utc) - timedelta(days=days)
    rows = db.execute(
        select(SetLog, SessionExercise)
        .join(SessionExercise, SetLog.session_exercise_id == SessionExercise.id)
        .join(WorkoutSession, SessionExercise.session_id == WorkoutSession.id)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.cardio_duration_min.is_(None),
            WorkoutSession.status == "completed",
            WorkoutSession.excluded_from_stats.is_(False),
            WorkoutSession.started_at >= window_start,
            SetLog.kind == "work",
            SetLog.completed.is_(True),
        )
    ).all()
    counts: dict[str, int] = {}
    total = 0
    for _sl, se in rows:
        entry = props.get(se.substituted_name or se.exercise_name_snapshot)
        if not entry:
            continue
        pm = entry.get("pattern_motor")
        if not pm:
            continue
        counts[pm] = counts.get(pm, 0) + 1
        total += 1
    if total == 0:
        return {}
    return {pm: round(100 * n / total) for pm, n in counts.items()}


@dataclass(frozen=True)
class PreviewPayload:
    """L2 preview card — 3-4 short KPIs alongside the mini-radar.

    Spec §A.bis : score NEVER appears at L2 (the grade badge does the
    job). Radar is silhouette only, no center.
    """
    sessions_30d: int
    streak: int
    cardio_min_per_week: int
    volume_delta_pct: int | None  # None if no baseline


def build_preview(db: Session, user_id: int, sessions_30d: int) -> PreviewPayload:
    return PreviewPayload(
        sessions_30d=sessions_30d,
        streak=streak_days(db, user_id),
        cardio_min_per_week=cardio_minutes_per_week(db, user_id),
        volume_delta_pct=strength_volume_delta_pct(db, user_id),
    )


@dataclass(frozen=True)
class PagePayload:
    """L3 profile page — aggregates the L2 KPIs and adds activity blocks."""
    preview: PreviewPayload
    top_zone: ZoneRanking | None
    neglected_zone: ZoneRanking | None
    dominant_pattern: tuple[str, int] | None
    last_session: LastSession | None


def build_page(db: Session, user_id: int, sessions_30d: int) -> PagePayload:
    return PagePayload(
        preview=build_preview(db, user_id, sessions_30d),
        top_zone=top_zone(db, user_id),
        neglected_zone=neglected_zone(db, user_id),
        dominant_pattern=dominant_pattern(db, user_id),
        last_session=last_session_summary(db, user_id),
    )
