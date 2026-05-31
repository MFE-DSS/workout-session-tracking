"""Sb_23 — Coach Report inference (blocks 7, 8, 9).

Deterministic rule set producing the ``Inféré`` blocks of the report
(points forts probables / points faibles probables / axes de travail
suggérés). No ML, no probabilities — fully explainable conditions.

Contract Sx_23 v1.1 §B.bis :
* Vocabulary is bounded — never claim "you are X", always "X probable".
* No aesthetic appreciation ("bel équilibre", "physique harmonieux").
* No morphological prognosis ("vous prenez/perdez du gras/muscle").
* No performance verdict ("vous êtes fort/faible").
* No inter-user comparison.

Output dataclasses are flat strings to keep the templating layer
trivial. The rationale (the *why*) is folded into the sentence so a
coach reads one self-contained line per item.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.services.coach_report import CoachReport
from app.services.muscle_mapping import RADAR_AXES

# Thresholds — V1 deterministic, easy to tune.
TOP_ZONE_MIN_SESSIONS = 3        # a zone is a probable strength point only if ≥ 3 sessions
NEGLECTED_ZONE_MAX_SESSIONS = 1  # ≤ 1 session in 30d = neglected
CARDIO_LOW_MIN_PER_WEEK = 90     # < 90'/week is "low" (OMS reco = 150')
DOMINANT_PATTERN_OVERWEIGHT_PCT = 35  # > 35 % of work sets on one pattern = unbalanced
DISCIPLINE_WEAK_THRESHOLD = 50   # any rate < 50 % surfaces in axes
LOW_VOLUME_SESSIONS_30D = 4      # < 4 sessions in 30d = low volume context


@dataclass(frozen=True)
class InferredBlocks:
    """The three Inféré blocks of the report (each list is 0..N short
    sentences). All sentences end with no period and use the qualifier
    "probable" / "suggéré" — never assertive."""
    strong_points: list[str]
    weak_points: list[str]
    suggested_axes: list[str]


def _axis_label(key: str) -> str:
    return RADAR_AXES.get(key, {}).get("label", key)


def strong_points(report: CoachReport) -> list[str]:
    """Rule : a zone is a "probable strength point" if it appears in
    top_zones with ≥ TOP_ZONE_MIN_SESSIONS over 30d. Capped to 2 lines."""
    out: list[str] = []
    for key, label, n in report.zones.top_zones:
        if n >= TOP_ZONE_MIN_SESSIONS:
            out.append(
                f"Zone travaillée fréquemment : **{label}** "
                f"({n} séances/30j) — point fort probable"
            )
        if len(out) >= 2:
            break
    return out


def weak_points(report: CoachReport) -> list[str]:
    """Rule : a zone with ≤ NEGLECTED_ZONE_MAX_SESSIONS over 30d
    surfaces as a probable weak point. Capped to 2 lines."""
    out: list[str] = []
    for key, label, n in report.zones.neglected_zones:
        if n <= NEGLECTED_ZONE_MAX_SESSIONS:
            out.append(
                f"Zone peu travaillée : **{label}** "
                f"({n} séance{'s' if n != 1 else ''}/30j) — point faible probable"
            )
        if len(out) >= 2:
            break
    return out


def suggested_axes(report: CoachReport) -> list[str]:
    """Rule set : produces 0..3 short suggested axes. Order = priority.

    Heuristics V1:
      1. neglected zone rebalance (if any)
      2. cardio increase to OMS reco (if < CARDIO_LOW_MIN_PER_WEEK)
      3. pattern rebalance (if any > DOMINANT_PATTERN_OVERWEIGHT_PCT)
      4. discipline reminder (if any rate < DISCIPLINE_WEAK_THRESHOLD)
      5. volume warning (if sessions_30d < LOW_VOLUME_SESSIONS_30D)
    """
    out: list[str] = []

    # (1) Neglected zone rebalance
    for key, label, n in report.zones.neglected_zones:
        if n <= NEGLECTED_ZONE_MAX_SESSIONS:
            out.append(
                f"Rééquilibrer **{label}** : viser 2 séances/sem sur 4 semaines"
            )
            break  # one zone is enough — don't pile up

    # (2) Cardio low
    if 0 <= report.volume.cardio_minutes_per_week < CARDIO_LOW_MIN_PER_WEEK:
        out.append(
            f"Augmenter le volume cardio : actuellement "
            f"{report.volume.cardio_minutes_per_week}'/sem — cible OMS 150'/sem"
        )

    # (3) Pattern overweighted
    if (
        report.patterns.dominant
        and report.patterns.dominant[1] > DOMINANT_PATTERN_OVERWEIGHT_PCT
    ):
        pat, pct = report.patterns.dominant
        out.append(
            f"Diversifier les patterns moteurs : **{pat}** représente {pct}% "
            "des sets travail — intégrer plus de variétés"
        )

    # (4) Discipline reminder
    disc = report.discipline
    if (
        disc.with_bodyweight_rate is not None
        and disc.with_bodyweight_rate < DISCIPLINE_WEAK_THRESHOLD
    ):
        out.append(
            f"Logger le poids de corps plus systématiquement "
            f"(actuellement {disc.with_bodyweight_rate}% des séances) — "
            "indispensable pour suivre le trend"
        )

    # (5) Volume context
    if report.volume.sessions_30d < LOW_VOLUME_SESSIONS_30D:
        out.append(
            f"Augmenter la fréquence d'entraînement : "
            f"{report.volume.sessions_30d} séances/30j sur la fenêtre — "
            "viser 2-3 séances/sem comme socle"
        )

    return out[:3]  # spec V1 = max 3 axes


def build_inference(report: CoachReport) -> InferredBlocks:
    return InferredBlocks(
        strong_points=strong_points(report),
        weak_points=weak_points(report),
        suggested_axes=suggested_axes(report),
    )
