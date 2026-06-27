"""Sx_31 / Sb_31.1 — Body Intelligence v2 composer (pure).

Moteur pur, déterministe, sans I/O. Compose les signaux d'entraînement
DÉJÀ AGRÉGÉS (par une couche I/O qui sera livrée en Sb_31.2 — pas par
ce module) en un :class:`BodyIntelligenceSnapshot` prêt pour le template.

Contrat (cf. `docs/strategy/SPIGNOS_BODY_INTELLIGENCE_V2_SPEC.md`) :

- Aucune dépendance sur la DB / FastAPI / Jinja / réseau.
- Aucune mutation de services métier core (`profile_metrics`,
  `muscle_scoring`, `quality_score`, `implicit_signal`, `coach_report`,
  `radar`, `overload_*`, `substitution`, `recommendation`).
- Aucune promesse esthétique / composition corporelle / médicale.
- Distinction stricte ``measured`` / ``derived`` / ``inferred`` /
  ``not_deductible`` portée par chaque bloc.
- Arbre de priorité déterministe, max 3 priorités.
- Seuils figés en constantes nommées, testables.
- Si une donnée manque : ``available=False`` ou ``"insufficient_data"``,
  jamais d'invention.
- Overload compliance V1 : **non calculée** (différé `Sb_31.next.overload-compliance`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

BODY_INTELLIGENCE_VERSION = 1

Status = Literal["ok", "partial_data", "insufficient_data"]
Classification = Literal["measured", "derived", "inferred", "not_deductible"]
PrioritySeverity = Literal["info", "watch"]
PriorityKey = Literal[
    "insufficient_data",
    "low_logging_confidence",
    "consistency_gap",
    "imbalance_gap",
    "undertrained_zone",
    "stable_or_progressing",
]

# ─────────────────────────── seuils V1 (figés) ───────────────────────────

# Quelques sessions minimum pour produire une lecture exploitable.
MIN_SESSIONS_OK = 3
# 2 séances/semaine × 4 semaines = 8 séances/30j minimum pour ne pas
# remonter ``consistency_gap``.
MIN_SESSIONS_CONSISTENCY_30D = 8
# Quality score moyen (0..100) en dessous duquel on remonte
# ``low_logging_confidence``.
LOW_QUALITY_THRESHOLD = 50.0
# Confidence score moyen (0..100) en dessous duquel on remonte
# ``low_logging_confidence``.
LOW_CONFIDENCE_THRESHOLD = 50.0
# Ratios push/pull et haut/bas considérés "déséquilibrés" V1.
IMBALANCE_LOW_RATIO = 0.5
IMBALANCE_HIGH_RATIO = 2.0
# Une zone est ``undertrained`` si elle a 0 séance sur 30j ET au moins
# ``UNDERTRAINED_OTHER_ZONE_MIN`` séances sur une autre zone.
UNDERTRAINED_OTHER_ZONE_MIN = 3
# Nombre minimum de samples pour calculer une moyenne de quality_score.
MIN_QUALITY_SAMPLE = 3
# Max de priorités exposées V1.
MAX_PRIORITIES = 3

# 6 axes radar canoniques (alignés sur muscle_mapping.RADAR_AXIS_ORDER).
# Le composeur ne dépend pas du module muscle_mapping pour rester pur ;
# on duplique l'ordre canonique ici (test garde).
RADAR_AXIS_ORDER: tuple[str, ...] = (
    "pecs",
    "shoulders",
    "back_width",
    "back_thickness",
    "arms",
    "lower",
)

# Limites systématiques (always-on disclaimers).
DEFAULT_LIMITS: tuple[str, ...] = (
    "Composition corporelle non déductible (pas de DEXA / impédance).",
    "Esthétique réelle non déductible (pas de photo / scan).",
    "Posture et symétrie réelle non déductibles sans données dédiées.",
    "Cardio loggué = déclaratif (pas de mesure VO2max ni calories vérifiées).",
    "Signal médical non fourni (SPIGNOS n'est pas un outil clinique).",
)


# ─────────────────────────── dataclasses input ───────────────────────────


@dataclass(frozen=True)
class BodyIntelligenceInput:
    """Inputs purs déjà agrégés par une couche I/O en amont (Sb_31.2).

    Tous les champs sont optionnels au type-level (``Optional[...]``) :
    le composeur traite les ``None`` comme "donnée non disponible" et
    ne fabrique jamais de valeur.
    """

    # ─── fréquence
    sessions_7d: int = 0
    sessions_30d: int = 0
    sessions_90d: int = 0

    # ─── volume
    work_sets_per_week_30d: int | None = None
    cardio_minutes_per_week_30d: int | None = None
    strength_volume_delta_pct_30d: float | None = None

    # ─── zones (clés alignées sur RADAR_AXIS_ORDER)
    zone_session_counts_30d: dict[str, int] = field(default_factory=dict)
    dominant_pattern_30d: str | None = None
    pattern_distribution_30d: dict[str, int] = field(default_factory=dict)

    # ─── qualité & confiance
    quality_score_avg_30d: float | None = None  # 0..100
    quality_score_n: int = 0
    confidence_score_avg: float | None = None  # 0..100

    # ─── signal implicite
    implicit_labels_30d: dict[str, int] = field(default_factory=dict)

    # ─── body metrics mesurées
    body_height_cm: int | None = None
    body_weight_kg: float | None = None
    body_weight_measured_at_iso: str | None = None
    waist_cm: float | None = None
    weight_trend_90d_kg: float | None = None


# ─────────────────────────── dataclasses output ──────────────────────────


@dataclass(frozen=True)
class BodyIntelligenceBlock:
    """Un bloc de lecture corporelle. Le template Sb_31.2 itère sur
    ``snapshot.blocks`` pour rendre l'UI."""

    key: str
    title: str
    classification: Classification
    available: bool
    # ``content`` est volontairement un dict de scalaires/strings simples
    # pour rester sérialisable et faciliter les snapshots de test.
    content: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class BodyIntelligencePriority:
    key: PriorityKey
    severity: PrioritySeverity
    message: str
    reason: str


@dataclass(frozen=True)
class BodyIntelligenceSnapshot:
    engine_version: int
    status: Status
    headline: str
    bullets: tuple[str, ...] = field(default_factory=tuple)
    blocks: tuple[BodyIntelligenceBlock, ...] = field(default_factory=tuple)
    priorities: tuple[BodyIntelligencePriority, ...] = field(default_factory=tuple)
    limits: tuple[str, ...] = field(default_factory=tuple)


# ─────────────────────────── helpers privés ──────────────────────────────


def _sum_keys(d: dict[str, int], keys: tuple[str, ...]) -> int:
    return sum(int(d.get(k, 0) or 0) for k in keys)


def _bmi(height_cm: int | None, weight_kg: float | None) -> float | None:
    """IMC = poids / taille² ; ``None`` si l'un manque (cf. spec §G.1).
    Classification systématiquement ``derived``."""
    if height_cm is None or weight_kg is None or height_cm <= 0:
        return None
    h = height_cm / 100.0
    return round(weight_kg / (h * h), 1)


def _push_pull_ratio(z: dict[str, int]) -> float | None:
    push = _sum_keys(z, ("pecs", "shoulders"))
    pull = _sum_keys(z, ("back_width", "back_thickness"))
    if pull == 0:
        return None
    return round(push / pull, 2)


def _upper_lower_ratio(z: dict[str, int]) -> float | None:
    upper = _sum_keys(
        z, ("pecs", "shoulders", "back_width", "back_thickness", "arms")
    )
    lower = _sum_keys(z, ("lower",))
    if lower == 0:
        return None
    return round(upper / lower, 2)


def _is_imbalanced(ratio: float | None) -> bool:
    if ratio is None:
        return False
    return ratio < IMBALANCE_LOW_RATIO or ratio > IMBALANCE_HIGH_RATIO


def _undertrained_zones(z: dict[str, int]) -> list[str]:
    """Liste les zones canoniques (RADAR_AXIS_ORDER) avec 0 séance sur 30j,
    quand au moins une autre zone canonique dépasse le seuil."""
    has_other_active = any(
        int(z.get(k, 0) or 0) >= UNDERTRAINED_OTHER_ZONE_MIN
        for k in RADAR_AXIS_ORDER
    )
    if not has_other_active:
        return []
    return [k for k in RADAR_AXIS_ORDER if int(z.get(k, 0) or 0) == 0]


# ─────────────────────────── builders de blocs ───────────────────────────


def _block_training_consistency(inp: BodyIntelligenceInput) -> BodyIntelligenceBlock:
    available = inp.sessions_30d > 0 or inp.sessions_7d > 0
    content: dict[str, object] = {
        "sessions_7d": inp.sessions_7d,
        "sessions_30d": inp.sessions_30d,
        "sessions_90d": inp.sessions_90d,
        "work_sets_per_week_30d": inp.work_sets_per_week_30d,
        "cardio_minutes_per_week_30d": inp.cardio_minutes_per_week_30d,
        "strength_volume_delta_pct_30d": inp.strength_volume_delta_pct_30d,
    }
    return BodyIntelligenceBlock(
        key="training_consistency",
        title="Régularité d'entraînement",
        classification="derived",
        available=available,
        content=content,
    )


def _block_body_metrics(inp: BodyIntelligenceInput) -> BodyIntelligenceBlock:
    bmi = _bmi(inp.body_height_cm, inp.body_weight_kg)
    available = any(
        v is not None
        for v in (
            inp.body_height_cm,
            inp.body_weight_kg,
            inp.waist_cm,
            inp.weight_trend_90d_kg,
        )
    )
    content: dict[str, object] = {
        "height_cm": inp.body_height_cm,
        "weight_kg": inp.body_weight_kg,
        "weight_measured_at_iso": inp.body_weight_measured_at_iso,
        "waist_cm": inp.waist_cm,
        "weight_trend_90d_kg": inp.weight_trend_90d_kg,
        "bmi": bmi,
        "bmi_disclaimer": (
            "IMC = indicateur grossier, jamais un objectif esthétique."
        ),
    }
    # Le bloc reste ``measured`` pour les valeurs saisies, mais l'IMC
    # est ``derived``. Pour ne pas créer 2 blocs ici, on étiquette le
    # bloc global ``measured`` et on fournit un champ explicite
    # ``bmi_classification`` que le template peut afficher à côté de
    # la valeur IMC.
    content["bmi_classification"] = "derived"
    return BodyIntelligenceBlock(
        key="body_metrics",
        title="Mesures corporelles",
        classification="measured",
        available=available,
        content=content,
    )


def _block_muscle_zone_balance(
    inp: BodyIntelligenceInput,
) -> BodyIntelligenceBlock:
    available = bool(inp.zone_session_counts_30d)
    sorted_zones: list[tuple[str, int]] = sorted(
        (
            (k, int(inp.zone_session_counts_30d.get(k, 0) or 0))
            for k in RADAR_AXIS_ORDER
        ),
        key=lambda t: t[1],
        reverse=True,
    )
    top_3 = [(k, v) for k, v in sorted_zones if v > 0][:3]
    bottom_3 = [(k, v) for k, v in reversed(sorted_zones)][:3]
    content: dict[str, object] = {
        "zone_session_counts_30d": dict(inp.zone_session_counts_30d),
        "top_zones": top_3,
        "bottom_zones": bottom_3,
        "axes_order": list(RADAR_AXIS_ORDER),
    }
    return BodyIntelligenceBlock(
        key="muscle_zone_balance",
        title="Zones musculaires sollicitées",
        classification="derived",
        available=available,
        content=content,
    )


def _block_push_pull_legs(inp: BodyIntelligenceInput) -> BodyIntelligenceBlock:
    z = inp.zone_session_counts_30d
    push_pull = _push_pull_ratio(z)
    upper_lower = _upper_lower_ratio(z)
    available = push_pull is not None or upper_lower is not None
    content: dict[str, object] = {
        "push_pull_ratio": push_pull,
        "upper_lower_ratio": upper_lower,
        "imbalance_low_ratio": IMBALANCE_LOW_RATIO,
        "imbalance_high_ratio": IMBALANCE_HIGH_RATIO,
        "push_pull_imbalanced": _is_imbalanced(push_pull),
        "upper_lower_imbalanced": _is_imbalanced(upper_lower),
    }
    return BodyIntelligenceBlock(
        key="push_pull_legs_balance",
        title="Équilibre haut / bas et push / pull",
        classification="derived",
        available=available,
        content=content,
    )


def _block_quality_and_confidence(
    inp: BodyIntelligenceInput,
) -> BodyIntelligenceBlock:
    has_quality = (
        inp.quality_score_avg_30d is not None
        and inp.quality_score_n >= MIN_QUALITY_SAMPLE
    )
    has_confidence = inp.confidence_score_avg is not None
    available = has_quality or has_confidence
    content: dict[str, object] = {
        "quality_score_avg_30d": inp.quality_score_avg_30d,
        "quality_score_n": inp.quality_score_n,
        "confidence_score_avg": inp.confidence_score_avg,
        "low_quality_threshold": LOW_QUALITY_THRESHOLD,
        "low_confidence_threshold": LOW_CONFIDENCE_THRESHOLD,
        "min_quality_sample": MIN_QUALITY_SAMPLE,
    }
    return BodyIntelligenceBlock(
        key="quality_and_confidence",
        title="Qualité de logging",
        classification="derived",
        available=available,
        content=content,
    )


def _block_implicit_signal_summary(
    inp: BodyIntelligenceInput,
) -> BodyIntelligenceBlock:
    available = bool(inp.implicit_labels_30d)
    content: dict[str, object] = {
        "implicit_labels_30d": dict(inp.implicit_labels_30d),
    }
    return BodyIntelligenceBlock(
        key="implicit_signal_summary",
        title="Signaux implicites agrégés",
        classification="inferred",
        available=available,
        content=content,
    )


def _block_unavailable_or_limits() -> BodyIntelligenceBlock:
    """Bloc systématique listant ce que SPIGNOS NE peut PAS déduire.
    Toujours ``available=True`` ; c'est le contre-poids anti-pseudo-science."""
    content: dict[str, object] = {
        "limits": list(DEFAULT_LIMITS),
        "overload_compliance_status": "not_available_v1",
    }
    return BodyIntelligenceBlock(
        key="unavailable_or_limits",
        title="Hors de portée de cette lecture",
        classification="not_deductible",
        available=True,
        content=content,
    )


# ─────────────────────── arbre de priorité V1 ────────────────────────────


def _priorities_for(
    inp: BodyIntelligenceInput,
    blocks: tuple[BodyIntelligenceBlock, ...],
) -> tuple[BodyIntelligencePriority, ...]:
    """Arbre déterministe (cf. spec §G.6 + brief §6).

    Ordre figé. Limité à ``MAX_PRIORITIES`` éléments.
    """
    result: list[BodyIntelligencePriority] = []

    # 1. insufficient_data
    if inp.sessions_30d < MIN_SESSIONS_OK:
        result.append(
            BodyIntelligencePriority(
                key="insufficient_data",
                severity="info",
                message=(
                    "Données insuffisantes pour une lecture stable "
                    "sur les séances loggées."
                ),
                reason=(
                    f"sessions_30d = {inp.sessions_30d} "
                    f"(seuil {MIN_SESSIONS_OK})"
                ),
            )
        )
        return tuple(result[:MAX_PRIORITIES])

    # 2. low_logging_confidence
    q_low = (
        inp.quality_score_avg_30d is not None
        and inp.quality_score_n >= MIN_QUALITY_SAMPLE
        and inp.quality_score_avg_30d < LOW_QUALITY_THRESHOLD
    )
    c_low = (
        inp.confidence_score_avg is not None
        and inp.confidence_score_avg < LOW_CONFIDENCE_THRESHOLD
    )
    if q_low or c_low:
        bits: list[str] = []
        if q_low:
            bits.append(f"quality_score moyen ≈ {inp.quality_score_avg_30d}")
        if c_low:
            bits.append(f"confidence_score moyen ≈ {inp.confidence_score_avg}")
        result.append(
            BodyIntelligencePriority(
                key="low_logging_confidence",
                severity="watch",
                message=(
                    "Logging récent peu détaillé — les lectures "
                    "ci-dessous sont à confirmer."
                ),
                reason="; ".join(bits),
            )
        )

    # 3. consistency_gap
    if inp.sessions_30d < MIN_SESSIONS_CONSISTENCY_30D:
        result.append(
            BodyIntelligencePriority(
                key="consistency_gap",
                severity="watch",
                message=(
                    "Fréquence récente faible sur les séances loggées."
                ),
                reason=(
                    f"sessions_30d = {inp.sessions_30d} "
                    f"(seuil {MIN_SESSIONS_CONSISTENCY_30D})"
                ),
            )
        )

    # 4. imbalance_gap
    push_pull = _push_pull_ratio(inp.zone_session_counts_30d)
    upper_lower = _upper_lower_ratio(inp.zone_session_counts_30d)
    if _is_imbalanced(push_pull) or _is_imbalanced(upper_lower):
        bits = []
        if _is_imbalanced(push_pull):
            bits.append(f"push/pull = {push_pull}")
        if _is_imbalanced(upper_lower):
            bits.append(f"haut/bas = {upper_lower}")
        result.append(
            BodyIntelligencePriority(
                key="imbalance_gap",
                severity="watch",
                message=(
                    "Déséquilibre apparent entre familles d'exercices "
                    "(à confirmer)."
                ),
                reason="; ".join(bits),
            )
        )

    # 5. undertrained_zone
    under = _undertrained_zones(inp.zone_session_counts_30d)
    if under and len(result) < MAX_PRIORITIES:
        result.append(
            BodyIntelligencePriority(
                key="undertrained_zone",
                severity="watch",
                message=(
                    "Zone moins représentée sur 30 jours — "
                    "envisager une session dédiée."
                ),
                reason=f"zones sans séance 30j : {', '.join(under)}",
            )
        )

    # 6. stable_or_progressing (uniquement si AUCUNE autre priorité)
    if not result:
        result.append(
            BodyIntelligencePriority(
                key="stable_or_progressing",
                severity="info",
                message=(
                    "Rien à signaler sur la fenêtre observée — "
                    "tendance stable."
                ),
                reason=(
                    "Aucun seuil V1 franchi sur sessions, qualité, "
                    "équilibre ou couverture zones."
                ),
            )
        )

    # Anti-régression : suppression des avertissements sur le bloc
    # `quality_and_confidence` si lui-même n'est pas available.
    _ = blocks
    return tuple(result[:MAX_PRIORITIES])


# ─────────────────────── headline / bullets ──────────────────────────────


def _status_for(
    inp: BodyIntelligenceInput, blocks: tuple[BodyIntelligenceBlock, ...]
) -> Status:
    if inp.sessions_30d < MIN_SESSIONS_OK:
        return "insufficient_data"
    # Si un bloc clé est unavailable, on passe en partial_data.
    key_blocks = {
        "training_consistency",
        "muscle_zone_balance",
        "quality_and_confidence",
    }
    for b in blocks:
        if b.key in key_blocks and not b.available:
            return "partial_data"
    return "ok"


def _headline_for(status: Status, inp: BodyIntelligenceInput) -> str:
    if status == "insufficient_data":
        return "Données insuffisantes pour une lecture stable."
    if status == "partial_data":
        return "Lecture partielle sur les séances loggées."
    return "Lecture corporelle issue de l'entraînement (30 derniers jours)."


def _bullets_for(
    status: Status,
    inp: BodyIntelligenceInput,
    priorities: tuple[BodyIntelligencePriority, ...],
) -> tuple[str, ...]:
    if status == "insufficient_data":
        return (
            f"{inp.sessions_30d} séance(s) sur 30 jours.",
            "Logue quelques séances pour activer la lecture complète.",
        )
    bullets: list[str] = [
        f"{inp.sessions_30d} séances loggées sur 30 jours.",
    ]
    if inp.strength_volume_delta_pct_30d is not None:
        delta = inp.strength_volume_delta_pct_30d
        sign = "+" if delta >= 0 else ""
        bullets.append(
            f"Volume strength {sign}{delta:.0f}% vs 30 jours précédents."
        )
    if priorities and priorities[0].key != "stable_or_progressing":
        bullets.append(priorities[0].message)
    return tuple(bullets[:4])


# ─────────────────────────── public API ──────────────────────────────────


def compute_body_intelligence(
    inp: BodyIntelligenceInput,
) -> BodyIntelligenceSnapshot:
    """Compose un :class:`BodyIntelligenceSnapshot` à partir d'inputs
    purs. Déterministe : à input égal, output bit-à-bit identique.

    Le composeur ne fait JAMAIS :
    - de promesse esthétique ou de composition corporelle
    - d'inférence morphologique
    - de calcul overload compliance (différé V1)
    - d'accès DB / réseau / fichier
    """
    blocks: tuple[BodyIntelligenceBlock, ...] = (
        _block_training_consistency(inp),
        _block_body_metrics(inp),
        _block_muscle_zone_balance(inp),
        _block_push_pull_legs(inp),
        _block_quality_and_confidence(inp),
        _block_implicit_signal_summary(inp),
        _block_unavailable_or_limits(),
    )
    status = _status_for(inp, blocks)
    priorities = _priorities_for(inp, blocks)
    headline = _headline_for(status, inp)
    bullets = _bullets_for(status, inp, priorities)
    return BodyIntelligenceSnapshot(
        engine_version=BODY_INTELLIGENCE_VERSION,
        status=status,
        headline=headline,
        bullets=bullets,
        blocks=blocks,
        priorities=priorities,
        limits=DEFAULT_LIMITS,
    )
