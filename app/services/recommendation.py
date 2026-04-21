"""Next-session recommendation engine (Sb_12).

Deterministic, explainable, zero-ML. Composes a recommendation from
signals already computed by the rest of the app:

- last N completed sessions (ordered desc) from ``WorkoutSession``
- per-zone hard-sets over a 7-day window via ``muscle_scoring``
- per-zone hard-sets over a 48-hour window (redundancy filter)
- ``behavioral.compute_behavioral_state`` for global fatigue
- ``classify_exercise`` for each template exercise → primary zones map
- ``quality_score.session_kind`` for strength / cardio alternation

Public API:

    recommend_next_session(db, user_id, now) -> dict | None

Returns None when the user has an open session (the home view hides
the block in that case). Otherwise returns::

    {
        "top": {"template": WorkoutTemplate, "score": int, "phrase": str},
        "alternatives": [{"template": ..., "score": ..., "phrase": ...}, ...],
        "context": {"cold_start": bool, ...},
    }

Calibration constants are grouped at module top so dogfooding-driven
tuning stays a single-file edit.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Any, Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.catalog import TemplateExercise, WorkoutTemplate
from app.models.session import SessionExercise, SetLog, WorkoutSession
from app.services.muscle_mapping import classify_exercise
from app.services.muscle_scoring import _compute_tonnage_by_zone
from app.services.substitution import actual_exercise_name


# ---------------------------------------------------------------------------
# Calibration — tweak post-dogfooding, ideally without touching logic.
# ---------------------------------------------------------------------------

# Fenêtre principale staleness (Sx_12 §H.2)
STALENESS_WINDOW_DAYS = 7

# Fenêtre redundancy (filtre sécurité)
REDUNDANCY_WINDOW_HOURS = 48

# Composants de score (Sx_12 §H.3)
WEIGHT_STALENESS = 40
WEIGHT_ALTERNATION = 20
WEIGHT_REDUNDANCY_PENALTY = -5  # coefficient appliqué à (hard_sets_48h / 4)
AFFINITY_CORE = 15
AFFINITY_UTILITY = 10
AFFINITY_SPECIALIZATION_OK = 20  # si justifiée
AFFINITY_SPECIALIZATION_SKIP = -1  # sentinelle d'exclusion

# Seuil hard_sets → staleness = 0 (saturation)
STALENESS_SATURATION_HARD_SETS = 8

# Seuil hard_sets dans la fenêtre redundancy au-delà duquel la zone est exclue
REDUNDANCY_HARD_SETS_CUTOFF = 4

# Fatigue élevée → on ne recommande que des sessions courtes
FATIGUE_HIGH_THRESHOLD = 70

# Cold start
COLD_START_LIFETIME_SESSIONS = 3

# Cardio absent sur N jours → bonus LISS
CARDIO_ABSENT_BONUS_DAYS = 7

# Alternatives à afficher
ALTERNATIVES_COUNT = 2

# Spécialisation valide quand la zone ciblée a < RATIO * median sur 14j
SPECIALIZATION_STALE_RATIO = 0.5
SPECIALIZATION_WINDOW_DAYS = 14

# Seuil gap "reprise soft" — si dernière séance > ce nombre de jours, on dégrade
SOFT_RESTART_GAP_DAYS = 14


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class Signals:
    """Signals précalculés et passés aux sous-composants du scoring."""
    cold_start: bool
    staleness_by_zone: dict[str, float]
    hard_sets_by_zone_recent: dict[str, int]  # 7j
    hard_sets_by_zone_48h: dict[str, int]
    kinds_recent: list[str]  # N dernières sessions, du plus récent au plus ancien
    days_since_last_cardio: int | None
    days_since_last_strength: int | None
    fatigue_score: float
    soft_restart: bool
    median_hard_sets_14d: float
    hard_sets_14d_by_zone: dict[str, int]


@dataclass
class Candidate:
    template: WorkoutTemplate
    primary_zones: list[str]
    score: int
    phrase: str


# ---------------------------------------------------------------------------
# Template → zones primaires (cache applicatif)
# ---------------------------------------------------------------------------


def _primary_zones_of(exercise_names: tuple[str, ...]) -> list[str]:
    """Core classification — extracted so the cache key is hashable."""
    counts: Counter[str] = Counter()
    for name in exercise_names:
        primary, _secondary = classify_exercise(name)
        if primary != "unknown":
            counts[primary] += 1
    if not counts:
        return []
    # On garde les zones qui représentent >=25% des exos du template,
    # ou au moins la/les plus fréquente(s).
    total = sum(counts.values())
    threshold = max(1, total // 4)
    return [z for z, n in counts.most_common() if n >= threshold]


@lru_cache(maxsize=128)
def _primary_zones_cached(exercise_names_tuple: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(_primary_zones_of(exercise_names_tuple))


def template_primary_zones(template: WorkoutTemplate) -> list[str]:
    """Return the primary zones of a template, cached by exercise list."""
    names = tuple(ex.name for ex in sorted(template.exercises, key=lambda e: e.position))
    return list(_primary_zones_cached(names))


def reset_template_zones_cache() -> None:
    """Test helper — clear the lru_cache between tests that rebuild templates."""
    _primary_zones_cached.cache_clear()


# ---------------------------------------------------------------------------
# Derivations
# ---------------------------------------------------------------------------


def _staleness_from_hard_sets(hard_sets: int) -> float:
    """Map hard sets in the 7-day window to a 0..1 staleness score.

    0 hard sets → 1.0 (fully stale, ready to hit)
    STALENESS_SATURATION_HARD_SETS+ → 0.0 (saturated, avoid)
    linear in between.
    """
    if hard_sets <= 0:
        return 1.0
    if hard_sets >= STALENESS_SATURATION_HARD_SETS:
        return 0.0
    return 1.0 - (hard_sets / STALENESS_SATURATION_HARD_SETS)


def _compute_signals(db: Session, user_id: int, now: datetime) -> Signals:
    """Gather all the signals scored templates will consult."""
    # ── Lifetime total for cold start detection
    lifetime_total = db.execute(
        select(WorkoutSession)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == "completed",
        )
    ).scalars().all()
    lifetime_count = len(lifetime_total)
    cold_start = lifetime_count < COLD_START_LIFETIME_SESSIONS

    # ── Recent sessions (5 latest desc) — used for kinds + days_since_*
    recent_stmt = (
        select(WorkoutSession)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == "completed",
            WorkoutSession.excluded_from_stats.is_(False),
        )
        .order_by(WorkoutSession.started_at.desc())
        .limit(5)
        .options(
            selectinload(WorkoutSession.template),
        )
    )
    recent_sessions: list[WorkoutSession] = list(
        db.execute(recent_stmt).scalars().all()
    )

    def _as_aware(dt: datetime | None) -> datetime | None:
        """SQLite round-trips naive datetimes — re-attach UTC so we can
        subtract from ``now`` (always aware)."""
        if dt is None:
            return None
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    kinds_recent: list[str] = []
    days_since_last_cardio: int | None = None
    days_since_last_strength: int | None = None
    last_session_at: datetime | None = _as_aware(
        recent_sessions[0].started_at if recent_sessions else None
    )
    for s in recent_sessions:
        k = "cardio" if (s.template and s.template.kind == "cardio") else "strength"
        kinds_recent.append(k)
        started = _as_aware(s.started_at)
        delta_days = max(0, (now - started).days) if started else 0
        if k == "cardio" and days_since_last_cardio is None:
            days_since_last_cardio = delta_days
        if k == "strength" and days_since_last_strength is None:
            days_since_last_strength = delta_days

    soft_restart = False
    if last_session_at is not None:
        soft_restart = (now - last_session_at).days > SOFT_RESTART_GAP_DAYS

    # ── Hard sets par zone — fenêtre 7j (staleness)
    window_7d_start = now - timedelta(days=STALENESS_WINDOW_DAYS)
    zone_data_7d = _compute_tonnage_by_zone(db, user_id, window_7d_start)
    hard_sets_by_zone_recent = {
        zone: sum(int(e["hard_sets"]) for e in entries)
        for zone, entries in zone_data_7d.items()
    }

    # ── Hard sets par zone — fenêtre 48h (redundancy)
    window_48h_start = now - timedelta(hours=REDUNDANCY_WINDOW_HOURS)
    zone_data_48h = _compute_tonnage_by_zone(db, user_id, window_48h_start)
    hard_sets_by_zone_48h = {
        zone: sum(int(e["hard_sets"]) for e in entries)
        for zone, entries in zone_data_48h.items()
    }

    # ── Hard sets par zone — fenêtre 14j (spécialisation justifiée)
    window_14d_start = now - timedelta(days=SPECIALIZATION_WINDOW_DAYS)
    zone_data_14d = _compute_tonnage_by_zone(db, user_id, window_14d_start)
    hard_sets_14d_by_zone = {
        zone: sum(int(e["hard_sets"]) for e in entries)
        for zone, entries in zone_data_14d.items()
    }
    non_zero_14d = [v for v in hard_sets_14d_by_zone.values() if v > 0]
    median_hard_sets_14d = (
        sorted(non_zero_14d)[len(non_zero_14d) // 2] if non_zero_14d else 0.0
    )

    # ── Staleness par zone (toutes zones connues)
    from app.services.muscle_mapping import ZONE_LABELS
    staleness_by_zone = {
        zone: _staleness_from_hard_sets(hard_sets_by_zone_recent.get(zone, 0))
        for zone in ZONE_LABELS
    }

    # ── Fatigue globale via behavioral
    from app.services.behavioral import compute_behavioral_state
    try:
        state = compute_behavioral_state(db, user_id)
        fatigue_score = float(state.fatigue_score)
    except Exception:
        # Si pour une raison x behavioral échoue (tests limités), on dégrade
        # silencieusement — la reco reste fonctionnelle.
        fatigue_score = 0.0

    return Signals(
        cold_start=cold_start,
        staleness_by_zone=staleness_by_zone,
        hard_sets_by_zone_recent=hard_sets_by_zone_recent,
        hard_sets_by_zone_48h=hard_sets_by_zone_48h,
        kinds_recent=kinds_recent,
        days_since_last_cardio=days_since_last_cardio,
        days_since_last_strength=days_since_last_strength,
        fatigue_score=fatigue_score,
        soft_restart=soft_restart,
        median_hard_sets_14d=float(median_hard_sets_14d),
        hard_sets_14d_by_zone=hard_sets_14d_by_zone,
    )


# ---------------------------------------------------------------------------
# Candidate pool + filters (§H.1 étape 3)
# ---------------------------------------------------------------------------


def _load_templates(db: Session) -> list[WorkoutTemplate]:
    return list(
        db.execute(
            select(WorkoutTemplate)
            .where(WorkoutTemplate.catalog_section != "archived")
            .order_by(WorkoutTemplate.display_order.asc())
            .options(
                selectinload(WorkoutTemplate.exercises)
                .selectinload(TemplateExercise.rep_targets),
            )
        ).scalars().all()
    )


def _passes_redundancy_filter(zones: list[str], hard_sets_48h: dict[str, int]) -> bool:
    """Reject a template if any primary zone has too many hard sets in 48h."""
    for zone in zones:
        if hard_sets_48h.get(zone, 0) > REDUNDANCY_HARD_SETS_CUTOFF * 2:
            # saturation franche → excluded
            return False
    return True


def _passes_fatigue_filter(template: WorkoutTemplate, fatigue_score: float) -> bool:
    """High-fatigue users only see short + cardio templates."""
    if fatigue_score <= FATIGUE_HIGH_THRESHOLD:
        return True
    if template.kind == "cardio":
        return True
    return template.slug.startswith("short-")


def _is_specialization_justified(
    template: WorkoutTemplate, signals: Signals
) -> bool:
    if template.catalog_section != "specialization":
        return True  # not a specialization, irrelevant
    if signals.median_hard_sets_14d <= 0:
        return False
    zones = template_primary_zones(template)
    if not zones:
        return False
    for z in zones:
        ratio = signals.hard_sets_14d_by_zone.get(z, 0) / signals.median_hard_sets_14d
        if ratio < SPECIALIZATION_STALE_RATIO:
            return True
    return False


# ---------------------------------------------------------------------------
# Scoring & phrasing
# ---------------------------------------------------------------------------


_KIND_TO_ZONE_GROUP: dict[str, set[str]] = {
    "push": {"pecs", "delt_lat", "triceps"},
    "pull": {"lats", "upper_back", "delt_post", "biceps"},
    "legs": {"quads", "posterior", "calves"},
}


def _movement_kind(zones: Iterable[str]) -> str | None:
    """Return 'push' / 'pull' / 'legs' if the template is dominantly one of those."""
    zs = set(zones)
    best: tuple[int, str] | None = None
    for kind, group in _KIND_TO_ZONE_GROUP.items():
        overlap = len(zs & group)
        if overlap == 0:
            continue
        if best is None or overlap > best[0]:
            best = (overlap, kind)
    return best[1] if best else None


def _score_template(
    template: WorkoutTemplate, signals: Signals
) -> Candidate:
    zones = template_primary_zones(template)
    score = 0.0

    # 1. Staleness (40 pts)
    if zones:
        staleness = sum(signals.staleness_by_zone.get(z, 1.0) for z in zones) / len(zones)
    else:
        staleness = 0.5  # inconnu → neutre
    score += WEIGHT_STALENESS * staleness

    # 2. Alternation (20 / 10 pts)
    last_two = signals.kinds_recent[:2]
    if last_two == ["strength", "strength"] and template.kind == "cardio":
        score += WEIGHT_ALTERNATION
    elif signals.kinds_recent and signals.kinds_recent[0] == "cardio" and template.kind == "strength":
        score += WEIGHT_ALTERNATION // 2

    # 3. Redundancy penalty (dégressif si zones proches saturation)
    if zones:
        recent_48h = max(signals.hard_sets_by_zone_48h.get(z, 0) for z in zones)
        if recent_48h > 0:
            score += WEIGHT_REDUNDANCY_PENALTY * (recent_48h / REDUNDANCY_HARD_SETS_CUTOFF)

    # 4. Catalog affinity
    section = template.catalog_section or "core"
    if section == "core":
        score += AFFINITY_CORE
    elif section == "utility":
        score += AFFINITY_UTILITY
    elif section == "specialization":
        if _is_specialization_justified(template, signals):
            score += AFFINITY_SPECIALIZATION_OK
        else:
            score = float(AFFINITY_SPECIALIZATION_SKIP)  # exclut du top

    # 5. Bonus cardio absent
    if (
        template.kind == "cardio"
        and (
            signals.days_since_last_cardio is None
            or signals.days_since_last_cardio >= CARDIO_ABSENT_BONUS_DAYS
        )
    ):
        score += 10

    clamped = max(0, min(100, int(round(score))))
    phrase = _build_phrase(template, zones, signals, staleness)

    return Candidate(
        template=template, primary_zones=zones, score=clamped, phrase=phrase,
    )


def _format_days(d: int | None) -> str:
    if d is None:
        return "longtemps"
    if d <= 0:
        return "aujourd'hui"
    if d == 1:
        return "1 j"
    return f"{d} j"


def _zone_labels_short(zones: list[str]) -> str:
    """Human-readable concatenation like 'pecs · delts · triceps'."""
    from app.services.muscle_mapping import ZONE_LABELS
    labels = [ZONE_LABELS.get(z, z).split(" / ")[0].lower() for z in zones[:3]]
    return " / ".join(labels)


def _build_phrase(
    template: WorkoutTemplate,
    zones: list[str],
    signals: Signals,
    staleness: float,
) -> str:
    """Compose a ≤140 char explanation from the spec slots (Sx_12 §J)."""
    focus_fragment = template.focus or template.name

    # Cold start — overrides everything
    if signals.cold_start:
        return f"Bon premier template pour démarrer : {template.name}."

    # High fatigue short / LISS reasoning
    if signals.fatigue_score > FATIGUE_HIGH_THRESHOLD:
        if template.kind == "cardio":
            return "Charge récente élevée → LISS suggéré pour récupérer."
        if template.slug.startswith("short-"):
            return "Charge récente élevée → séance courte recommandée."

    # Soft restart
    if signals.soft_restart:
        if template.kind == "cardio":
            return f"Pas de séance depuis plus de {SOFT_RESTART_GAP_DAYS} j → LISS pour reprendre."
        if template.slug.startswith("short-"):
            return f"Pas de séance depuis plus de {SOFT_RESTART_GAP_DAYS} j → reprise douce."

    # Cardio absent — dominant signal when it triggers
    if (
        template.kind == "cardio"
        and signals.days_since_last_cardio is not None
        and signals.days_since_last_cardio >= CARDIO_ABSENT_BONUS_DAYS
    ):
        return f"Pas de cardio depuis {_format_days(signals.days_since_last_cardio)} → LISS suggéré pour équilibrer."
    if (
        template.kind == "cardio"
        and signals.days_since_last_cardio is None
    ):
        return "Pas de cardio récent → LISS suggéré pour équilibrer."

    # Specialization — zone-stale wording
    if template.catalog_section == "specialization" and zones:
        zone_label = _zone_labels_short(zones)
        return f"{zone_label.capitalize()} sous-travaillé(e) → {template.name} recommandé."

    # Strength — alternation or staleness
    kind_ = _movement_kind(zones)
    last_kind_mvmt: str | None = None
    if signals.kinds_recent:
        # Try to infer the last strength session's movement group via its template
        # — we don't have template on recent_sessions here, use zones_recent proxy.
        last_kind_mvmt = None  # we kept it simple: drop this enrichment for V1
    if kind_ and signals.days_since_last_strength is not None:
        if staleness >= 0.7:
            return (
                f"{focus_fragment} peu travaillé récemment → {template.name} recommandé."
            )
        if signals.days_since_last_strength <= 1:
            return f"Dernière séance hier → {template.name} conseillé pour alterner."

    # Generic fallback — always populated
    if zones:
        return f"Suite naturelle après ton historique récent → {template.name}."
    return f"{template.name} — bon compromis pour l'état actuel."


# ---------------------------------------------------------------------------
# Fallback
# ---------------------------------------------------------------------------


def _fallback_candidate(templates: list[WorkoutTemplate], cold_start: bool) -> Candidate | None:
    """Return a guaranteed candidate when filters empty the pool."""
    if not templates:
        return None
    if cold_start:
        # Core, smallest display_order
        core = [t for t in templates if t.catalog_section == "core"]
        pick = core[0] if core else templates[0]
        return Candidate(
            template=pick,
            primary_zones=template_primary_zones(pick),
            score=50,
            phrase=f"Bon premier template pour démarrer : {pick.name}.",
        )
    liss = next((t for t in templates if t.slug.startswith("liss-")), None)
    if liss is not None:
        return Candidate(
            template=liss,
            primary_zones=template_primary_zones(liss),
            score=50,
            phrase=f"Séance de récupération suggérée : {liss.name}.",
        )
    # Really edge: no core, no LISS — return whatever exists.
    pick = templates[0]
    return Candidate(
        template=pick,
        primary_zones=template_primary_zones(pick),
        score=50,
        phrase=f"{pick.name} — choix par défaut.",
    )


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def recommend_next_session(
    db: Session, user_id: int, now: datetime | None = None
) -> dict[str, Any] | None:
    """Produce a {top, alternatives, context} dict or None when the user has
    an open session.
    """
    # Short-circuit when a session is open — the home view hides the
    # block in that case anyway.
    open_session = db.execute(
        select(WorkoutSession)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == "in_progress",
        )
        .limit(1)
    ).scalar_one_or_none()
    if open_session is not None:
        return None

    now = now or datetime.now(timezone.utc)
    signals = _compute_signals(db, user_id, now)
    templates = _load_templates(db)

    # Pool filter (§H.1 step 3)
    pool: list[WorkoutTemplate] = []
    for t in templates:
        if not _passes_fatigue_filter(t, signals.fatigue_score):
            continue
        zones = template_primary_zones(t)
        if not _passes_redundancy_filter(zones, signals.hard_sets_by_zone_48h):
            continue
        pool.append(t)

    # Cold start → always fall back immediately (ignore scoring noise)
    if signals.cold_start:
        fb = _fallback_candidate(templates, cold_start=True)
        if fb is None:
            return None
        return {
            "top": {
                "template": fb.template,
                "score": fb.score,
                "phrase": fb.phrase,
                "primary_zones": fb.primary_zones,
            },
            "alternatives": [],
            "context": {"cold_start": True},
        }

    candidates = [_score_template(t, signals) for t in pool]
    # Remove excluded specializations (score was forced to sentinel)
    candidates = [c for c in candidates if c.score >= 0]

    if not candidates:
        fb = _fallback_candidate(templates, cold_start=False)
        if fb is None:
            return None
        return {
            "top": {
                "template": fb.template,
                "score": fb.score,
                "phrase": fb.phrase,
                "primary_zones": fb.primary_zones,
            },
            "alternatives": [],
            "context": {"cold_start": False, "fallback": True},
        }

    # Tie-break: higher score, then display_order, then older last_done_at
    candidates.sort(
        key=lambda c: (
            -c.score,
            c.template.display_order,
            c.template.slug,
        )
    )

    top = candidates[0]
    alternatives = candidates[1 : 1 + ALTERNATIVES_COUNT]

    return {
        "top": {
            "template": top.template,
            "score": top.score,
            "phrase": top.phrase,
            "primary_zones": top.primary_zones,
        },
        "alternatives": [
            {
                "template": c.template,
                "score": c.score,
                "phrase": c.phrase,
                "primary_zones": c.primary_zones,
            }
            for c in alternatives
        ],
        "context": {
            "cold_start": False,
            "fatigue_score": signals.fatigue_score,
            "days_since_last_cardio": signals.days_since_last_cardio,
            "days_since_last_strength": signals.days_since_last_strength,
        },
    }
