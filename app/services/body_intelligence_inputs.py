"""Sb_31.2 — Body Intelligence v2 — couche I/O lecture seule.

Construit un :class:`BodyIntelligenceInput` à partir des données déjà
persistées dans SPIGNOS, en composant les services existants
**en lecture seule** (aucune mutation, aucune migration).

Contrat (cf. spec `SPIGNOS_BODY_INTELLIGENCE_V2_SPEC.md` §K, §11) :

- Ne fait JAMAIS de logique de priorité (réservée à
  :mod:`app.services.body_intelligence`).
- Ne fait JAMAIS d'interprétation body (mêmes garde-fous).
- Ne mute aucun service métier core.
- Ne calcule pas l'overload compliance V1 (cf. spec §G.5 différé).
- Retourne ``None`` / structures vides si la donnée n'est pas disponible.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.enums import SessionStatus
from app.models.measurement import BodyMeasurement
from app.models.session import WorkoutSession
from app.models.user import User
from app.services.body_intelligence import BodyIntelligenceInput
from app.services.coach_report import _weight_trend_90d, _work_sets_per_week
from app.services.confidence import compute_confidence_score
from app.services.muscle_mapping import RADAR_AXIS_ORDER
from app.services.profile_metrics import (
    cardio_minutes_per_week,
    dominant_pattern,
    pattern_distribution,
    strength_volume_delta_pct,
    zone_session_counts,
)
from app.services.quality_score import compute_session_quality

# ────────────────────── helpers privés ──────────────────────


def _now() -> datetime:
    return datetime.now(UTC)


def _sessions_count_in_window(db: Session, user_id: int, days: int) -> int:
    window = _now() - timedelta(days=days)
    rows = db.execute(
        select(WorkoutSession.id).where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == SessionStatus.COMPLETED,
            WorkoutSession.excluded_from_stats.is_(False),
            WorkoutSession.started_at >= window,
        )
    ).all()
    return len(rows)


def _completed_sessions_30d(db: Session, user_id: int) -> list[WorkoutSession]:
    window = _now() - timedelta(days=30)
    rows = db.execute(
        select(WorkoutSession)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == SessionStatus.COMPLETED,
            WorkoutSession.excluded_from_stats.is_(False),
            WorkoutSession.started_at >= window,
        )
        .order_by(WorkoutSession.started_at.desc())
    ).scalars().all()
    return list(rows)


def _quality_avg_30d(sessions: list[WorkoutSession]) -> tuple[float | None, int]:
    """Moyenne de :func:`compute_session_quality` sur les sessions 30j.
    Retourne ``(None, 0)`` si liste vide ou exceptions ; ``(avg, n)``
    sinon.
    """
    if not sessions:
        return None, 0
    scores: list[float] = []
    for s in sessions:
        try:
            scores.append(float(compute_session_quality(s)))
        except Exception:
            continue
    if not scores:
        return None, 0
    avg = sum(scores) / len(scores)
    return round(avg, 1), len(scores)


def _confidence_avg_30d(sessions: list[WorkoutSession]) -> float | None:
    """Moyenne de :func:`compute_confidence_score` sur les sessions 30j."""
    if not sessions:
        return None
    scores: list[float] = []
    for s in sessions:
        try:
            scores.append(float(compute_confidence_score(s)))
        except Exception:
            continue
    if not scores:
        return None
    return round(sum(scores) / len(scores), 1)


def _implicit_labels_30d(sessions: list[WorkoutSession]) -> dict[str, int]:
    """Compte des ``implicit_label`` sur les SessionExercise des sessions
    30j. Ignore les labels None."""
    counts: dict[str, int] = {}
    for s in sessions:
        for se in s.session_exercises:
            label = getattr(se, "implicit_label", None)
            if label:
                counts[label] = counts.get(label, 0) + 1
    return counts


def _radar_zone_counts(
    db: Session, user_id: int, days: int = 30
) -> dict[str, int]:
    """Normalise ``profile_metrics.zone_session_counts`` sur les 6 axes radar
    canoniques, alignés sur :data:`body_intelligence.RADAR_AXIS_ORDER`.

    Sb_ZONE_COUNT_TAXONOMY_FIX_01 — cette fonction portait une **seconde
    table** zone détaillée → axe radar, écrite à la main. C'était un doublon de
    ``RADAR_AXES`` (la relation canonique), et il divergeait déjà : il déclarait
    un ``glutes`` absent des 11 zones détaillées. Surtout, la projection est
    désormais faite **une seule fois**, en amont, dans ``_zone_session_counts``
    (l'unique frontière de projection). Réappliquer une table détaillée ici
    aurait fait tomber tous les axes sauf ``pecs``. Le doublon est supprimé ;
    il ne reste qu'une normalisation de forme.

    On conserve la structure complète (axes à 0 inclus) pour que le composeur
    puisse détecter ``undertrained_zone``.
    """
    raw_counts = zone_session_counts(db, user_id, days=days)
    if not raw_counts:
        return {}
    axis_counts: dict[str, int] = dict.fromkeys(RADAR_AXIS_ORDER, 0)
    for axis_key, count in raw_counts.items():
        if axis_key in axis_counts:
            axis_counts[axis_key] += int(count or 0)
    return axis_counts


def _latest_weight_measurement(
    db: Session, user_id: int
) -> tuple[float | None, str | None]:
    """Retourne le poids le plus récent venant de :class:`BodyMeasurement`
    + sa date ISO. ``(None, None)`` si aucune mesure disponible."""
    row = db.execute(
        select(BodyMeasurement.weight_kg, BodyMeasurement.measured_at)
        .where(
            BodyMeasurement.user_id == user_id,
            BodyMeasurement.weight_kg.is_not(None),
        )
        .order_by(BodyMeasurement.measured_at.desc())
        .limit(1)
    ).first()
    if row is None:
        return None, None
    weight, dt = row
    return (
        float(weight) if weight is not None else None,
        dt.isoformat() if dt is not None else None,
    )


def _latest_waist_measurement(db: Session, user_id: int) -> float | None:
    row = db.execute(
        select(BodyMeasurement.waist_cm)
        .where(
            BodyMeasurement.user_id == user_id,
            BodyMeasurement.waist_cm.is_not(None),
        )
        .order_by(BodyMeasurement.measured_at.desc())
        .limit(1)
    ).first()
    return float(row[0]) if row else None


# ────────────────────── safe wrappers ──────────────────────


def _safe(fn, *args, **kwargs):
    """Exécute ``fn(*args, **kwargs)`` et retourne ``None`` en cas
    d'exception inattendue. Garantit que la couche I/O ne crash JAMAIS
    le router."""
    try:
        return fn(*args, **kwargs)
    except Exception:
        return None


# ────────────────────── API publique ──────────────────────


def build_body_intelligence_input(
    db: Session, user: User
) -> BodyIntelligenceInput:
    """Compose un :class:`BodyIntelligenceInput` complet depuis la DB.

    Lecture seule. Les champs manquants restent ``None`` /
    structures vides — jamais d'invention. Le composeur métier
    (le composeur métier Sb_31.1) consomme ce résultat sans
    refaire d'I/O.
    """
    user_id = user.id

    # Fréquence
    s7 = _sessions_count_in_window(db, user_id, 7)
    s30 = _sessions_count_in_window(db, user_id, 30)
    s90 = _sessions_count_in_window(db, user_id, 90)
    completed_30d = _completed_sessions_30d(db, user_id)

    # Volume
    work_sets_pw = _safe(_work_sets_per_week, db, user_id, 30)
    cardio_pw = _safe(cardio_minutes_per_week, db, user_id, days=30)
    vol_delta = _safe(strength_volume_delta_pct, db, user_id, days=30)

    # Zones (sur axes radar canoniques)
    zone_counts = _radar_zone_counts(db, user_id, days=30) or {}
    dom_pattern = _safe(dominant_pattern, db, user_id, days=30)
    pat_dist = _safe(pattern_distribution, db, user_id, days=30) or {}

    # Qualité & confiance
    quality_avg, quality_n = _quality_avg_30d(completed_30d)
    confidence_avg = _confidence_avg_30d(completed_30d)

    # Implicit signal agrégé
    implicit = _implicit_labels_30d(completed_30d)

    # Body metrics — priorité au BodyMeasurement le plus récent, fallback
    # sur users.weight_kg / users.waist_cm si pas de mesure datée.
    bm_weight, bm_weight_iso = _latest_weight_measurement(db, user_id)
    if bm_weight is None and user.weight_kg is not None:
        bm_weight = float(user.weight_kg)
        # `users.weight_kg` n'est pas daté → on n'affiche pas de date.
        bm_weight_iso = None
    waist = _latest_waist_measurement(db, user_id)
    if waist is None and user.waist_cm is not None:
        waist = float(user.waist_cm)
    weight_trend = _safe(_weight_trend_90d, db, user_id)

    return BodyIntelligenceInput(
        sessions_7d=s7,
        sessions_30d=s30,
        sessions_90d=s90,
        work_sets_per_week_30d=work_sets_pw,
        cardio_minutes_per_week_30d=cardio_pw,
        strength_volume_delta_pct_30d=(
            float(vol_delta) if isinstance(vol_delta, (int, float)) else None
        ),
        zone_session_counts_30d=zone_counts,
        dominant_pattern_30d=dom_pattern,
        pattern_distribution_30d=pat_dist,
        quality_score_avg_30d=quality_avg,
        quality_score_n=quality_n,
        confidence_score_avg=confidence_avg,
        implicit_labels_30d=implicit,
        body_height_cm=user.height_cm,
        body_weight_kg=bm_weight,
        body_weight_measured_at_iso=bm_weight_iso,
        waist_cm=waist,
        weight_trend_90d_kg=weight_trend,
    )
