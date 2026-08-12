"""Sb_TRAINING_STATE_AGGREGATOR_01 — read-only assembly of the live evidence.

Spec: `docs/strategy/Sx_RECOVERY_READINESS_01_SPEC.md` §2.5, §4, §12bis.

This service **gathers and normalises evidence**. It does not estimate per-zone
recovery, does not decide anything, does not rank, and does not produce user
text. Every value it emits comes from a canonical normaliser in
:mod:`app.services.recovery_contract`; this module owns the *queries* and the
*assembly*, never a formula.

Hard properties, each pinned by a test:

* **read-only** — no add, no delete, no commit, no flush, no ORM mutation;
* **deterministic** for a fixed database state and a fixed ``now``;
* **no global score** — `TrainingState` exposes primitives, `FatigueSignal`
  keeps its three components separate (OQ-3);
* **no fabricated favourable value** — a missing input stays missing, and more
  missing evidence can only lower confidence;
* **bounded queries** — a fixed number of statements regardless of how many
  sessions, exercises or repeated exercise names are in scope.

## Two findings from the active-code audit that a consumer must know

**1. The repository has no load-derived fatigue producer.**
`behavioral.compute_behavioral_state` computes `fatigue_score` from
``global_state`` / ``concentration`` — *declared feelings*, not tonnage, sets or
volume. So :attr:`FatigueSignal.strength_component` here is the canonical
**accumulated subjective** producer, not a mechanical load reading.

**2. That producer is not strength-filtered.**
Its "last 3 completed sessions" query applies no ``kind`` filter, so a cardio
session's declared feeling feeds it too.

Both are recorded in the signal's ``basis`` rather than hidden. The two
subjective-origin components differ in *shape*, which is why they stay separate:
``strength_component`` is the producer's 3-session weighting, while
``subjective_component`` is the single most recent declaration. Since
`FatigueSignal` has no aggregate, they are never summed — the overlap is
information for a reader, not double counting in a number.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.enums import SessionStatus
from app.models.readiness import ReadinessEntry
from app.models.session import WorkoutSession
from app.services.body_zone_source import resolve_exercise_zones
from app.services.recovery_contract import (
    Confidence,
    FatigueSignal,
    ReadinessSignal,
    Sufficiency,
    TrainingState,
    cardio_load_estimate,
    cardio_zone_exposure,
    mean_of_present,
    normalize_cardio_modality,
    normalize_legacy_fatigue,
    normalize_readiness_scale,
    normalize_session_feedback,
    readiness_sufficiency_for_age,
)
from app.services.substitution import actual_exercise_name

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

TRAINING_STATE_AGGREGATOR_VERSION = 1

#: Window of "recent training" this aggregator considers.
#:
#: 30 days is the window this repository already uses for recent training —
#: `profile_metrics._eligible_sessions_in_window` and every `days: int = 30`
#: default around it. Reusing it keeps one notion of "recent" instead of adding
#: a sixth. It is a **scope** choice, not a decay curve: nothing fades inside the
#: window and nothing is weighted by age. Temporal decay belongs to
#: `Sb_ZONE_RECOVERY_ESTIMATE_01`.
TRAINING_STATE_LOOKBACK_DAYS = 30

#: Readiness dimensions, in the order `ReadinessSignal` declares them.
_READINESS_FIELDS = (
    "sleep_quality", "soreness_level", "stress_level",
    "motivation_level", "fatigue_level",
)


@dataclass
class _ZoneEvidence:
    """Raw per-zone facts gathered for the NEXT slice. **No estimate here.**"""

    zone_code: str
    last_strength_load_at: datetime | None = None
    strength_occurrences: int = 0
    cardio_exposure_modalities: set[str] = field(default_factory=set)
    resolution_paths: set[str] = field(default_factory=set)


def _readiness_signal(
    db: Session, user_id: int, *, now: datetime
) -> ReadinessSignal:
    """Most recent `ReadinessEntry`, normalised. Never back-filled.

    A historical declaration is never presented as today's: its age drives
    :func:`readiness_sufficiency_for_age`, and an old entry can only be context
    (OQ-6). No entry at all leaves every value ``None``.
    """
    entry = db.execute(
        select(ReadinessEntry)
        .where(ReadinessEntry.user_id == user_id)
        .order_by(ReadinessEntry.recorded_on.desc())
        .limit(1)
    ).scalar_one_or_none()

    if entry is None:
        return ReadinessSignal(
            sufficiency=Sufficiency.INSUFFICIENT,
            basis=("no readiness entry recorded",),
        )

    age_days = (now.date() - entry.recorded_on).days
    values = {
        name: normalize_readiness_scale(getattr(entry, name, None))
        for name in _READINESS_FIELDS
    }
    dimensions = tuple(values[name] for name in _READINESS_FIELDS)

    sufficiency = readiness_sufficiency_for_age(age_days)
    if all(v is None for v in dimensions):
        # A row exists but nothing in it is usable — that is not a declaration.
        sufficiency = Sufficiency.INSUFFICIENT

    return ReadinessSignal(
        declared_on=entry.recorded_on,
        age_days=age_days,
        sleep=values["sleep_quality"],
        soreness=values["soreness_level"],
        stress=values["stress_level"],
        motivation=values["motivation_level"],
        # Persisted as `fatigue_level`, where 5 means "Très frais". Exposed
        # under its true direction so nothing downstream reads it as fatigue.
        self_reported_freshness=values["fatigue_level"],
        overall=mean_of_present(dimensions),
        sufficiency=sufficiency,
        basis=(f"readiness_entry {entry.recorded_on.isoformat()} ({age_days}d old)",),
    )


#: How many recent sessions `behavioral` folds into its fatigue figure. Mirrored
#: here to *detect fabrication*, never to recompute the value.
_PRODUCER_SESSION_REACH = 3


def _has_recent_declaration(
    db: Session, user_id: int, *, window_start: datetime
) -> bool:
    """Did any **recent** session the producer looks at carry a declaration?

    **This gate exists because the producer fabricates a number out of nothing,
    and the fabrication is not detectable from its output.** Measured on the
    live code:

    * an empty history returns ``_DEFAULT_FATIGUE`` = **50.0**, a value no real
      combination of declarations can produce (the producible set is
      {15, 30, 45, 60, 75} and their convex combinations);
    * sessions with **no** declaration return **45.0** — and 45.0 *is* producible
      from a real declaration (``good`` + ``low``). So the value alone cannot
      distinguish "the athlete told us they felt fine" from "nobody answered".

    A value sentinel therefore cannot work, and passing the number through would
    turn silence into evidence — precisely the fail-open §4 forbids. The
    presence of a declaration is checked instead.

    This mirrors the producer's *selection* (its last three completed,
    non-excluded sessions) purely to ask that question. It does not recompute,
    reweight or duplicate its formula.

    **The window applies here too.** `behavioral` has no date filter of its own,
    so without this bound a single declaration from 400 days ago would still
    populate `strength_component` and count as present evidence — lifting an
    otherwise empty state to PARTIAL. That directly contradicts the rule this
    module enforces for readiness, where a stale declaration is deliberately not
    counted. Abandoned training must not present as current fatigue evidence.

    **Residual, stated rather than hidden:** once a recent declaration exists,
    the producer's own three-session reach may still fold in a session older
    than the window. That is the canonical producer's semantics, and
    reimplementing its selection to trim it would duplicate the formula this
    slice must not touch. What the gate guarantees is that the producer is only
    *consulted* when recent declared evidence exists.
    """
    rows = db.execute(
        select(WorkoutSession.global_state, WorkoutSession.concentration)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == SessionStatus.COMPLETED,
            WorkoutSession.excluded_from_stats.is_(False),
            WorkoutSession.started_at >= window_start,
        )
        .order_by(WorkoutSession.started_at.desc())
        .limit(_PRODUCER_SESSION_REACH)
    ).all()
    return any(
        global_state is not None or concentration is not None
        for global_state, concentration in rows
    )


def _strength_component(
    db: Session, user_id: int, *, window_start: datetime
) -> tuple[float | None, str]:
    """Accumulated fatigue from the canonical producer, normalised once.

    Delegates to `behavioral.compute_behavioral_state` and converts with
    `normalize_legacy_fatigue` — the formula is neither copied nor re-derived.

    A raising producer yields ``None``. `recommendation.py` degrades the same
    failure to ``0.0``; that sentinel is below the producible floor, so
    `normalize_fatigue_score` already refuses it. Either way the failure never
    becomes "fresh".
    """
    # Deferred: `behavioral` is a heavy ORM consumer and this keeps the module
    # import-light, matching how `recovery_contract` reaches production code.
    from app.services.behavioral import compute_behavioral_state

    if not _has_recent_declaration(db, user_id, window_start=window_start):
        return None, "no declaration in window behind the accumulated producer"

    try:
        state = compute_behavioral_state(db, user_id)
    except Exception as exc:  # noqa: BLE001 — any producer failure is "unknown"
        return None, f"behavioral producer unavailable ({type(exc).__name__})"

    value = normalize_legacy_fatigue(state.fatigue_score)
    if value is None:
        return None, "behavioral fatigue_score unusable"
    return value, (
        "behavioral accumulated fatigue over its last 3 completed sessions — "
        "declared feeling, not measured load, and not filtered to strength"
    )


def _subjective_component(
    sessions: list[WorkoutSession],
) -> tuple[float | None, str]:
    """Most recent post-session declaration, normalised.

    The single latest declaration, deliberately not an average: averaging would
    be a formula this contract has no basis for. Both fields absent yields
    ``None`` — `compute_session_fatigue` would substitute its 50/40 defaults, and
    "the user answered nothing" is not a neutral reading.
    """
    for session in sessions:  # already ordered newest first
        if session.global_state is None and session.concentration is None:
            continue
        value = normalize_session_feedback(
            session.global_state, session.concentration)
        if value is not None:
            return value, (
                f"post-session declaration of {session.started_at.date().isoformat()}"
            )
    return None, "no post-session declaration recorded"


def _cardio_component(
    sessions: list[WorkoutSession],
) -> tuple[float | None, Confidence, tuple[str, ...], WorkoutSession | None]:
    """Exposure of the **most recent** cardio session in the window.

    A *selection* rule, not an aggregation. Neither the spec nor the active code
    defines how to combine several cardio sessions into one scalar, and
    inventing weights would be inventing cumulative physiology — so the latest
    observation is taken, exactly as readiness takes the latest entry. How many
    others were in scope is recorded rather than folded in.
    """
    cardio = [s for s in sessions if s.cardio_duration_min is not None]
    if not cardio:
        return None, Confidence.NONE, ("no cardio session in window",), None

    latest = cardio[0]  # newest first
    value, confidence, basis = cardio_load_estimate(
        machine_type=latest.cardio_machine_type,
        duration_min=latest.cardio_duration_min,
        bpm_avg=latest.cardio_bpm_avg,
    )
    basis = (
        f"most recent of {len(cardio)} cardio session(s) in window "
        f"({latest.started_at.date().isoformat()}) — selection, not aggregation",
        *basis,
    )
    return value, confidence, basis, latest


def _entry_for(evidence: dict[str, _ZoneEvidence], zone_code: str) -> _ZoneEvidence:
    return evidence.setdefault(zone_code, _ZoneEvidence(zone_code=zone_code))


def _resolve_cached(db: Session, name: str, cache: dict[str, object]) -> object:
    """Resolve once per distinct name, for this invocation only."""
    if name not in cache:
        cache[name] = resolve_exercise_zones(db, name)
    return cache[name]


def _record_strength_zones(
    evidence: dict[str, _ZoneEvidence], resolution: object, started_at: datetime
) -> None:
    """Fold one resolved exercise occurrence into the per-zone facts."""
    for zone_code in (resolution.primary, *resolution.secondary):
        item = _entry_for(evidence, zone_code)
        item.strength_occurrences += 1
        item.resolution_paths.add(resolution.resolution_path)
        if (item.last_strength_load_at is None
                or started_at > item.last_strength_load_at):
            item.last_strength_load_at = started_at


def _record_cardio_zones(
    evidence: dict[str, _ZoneEvidence], latest_cardio: WorkoutSession
) -> None:
    """Note which zones the latest cardio session plausibly exposed."""
    modality, _ = normalize_cardio_modality(latest_cardio.cardio_machine_type)
    exposure = cardio_zone_exposure(modality)
    for zone_code in (*exposure.primary_zones, *exposure.secondary_zones):
        _entry_for(evidence, zone_code).cardio_exposure_modalities.add(
            exposure.modality.value)


def _zone_evidence(
    db: Session,
    sessions: list[WorkoutSession],
    latest_cardio: WorkoutSession | None,
) -> tuple[dict[str, _ZoneEvidence], int]:
    """Raw per-zone facts. **Deliberately no estimate, no band, no decay.**

    Attribution goes through the `Sb_32.4` formal contract, keyed on the
    exercise **name** — `SessionExercise.exercise_code_snapshot` is a
    training-day slot (`E1`…`E7`) reused across exercises and is not the lookup
    key.

    Resolution is memoised per distinct name **for this invocation only**: a
    module-level cache over DB-backed state would go stale the moment the
    reference tables change. Returns the resolution count so a test can prove
    it is bounded by the number of distinct names, not by occurrences.
    """
    evidence: dict[str, _ZoneEvidence] = {}
    cache: dict[str, object] = {}

    for session in sessions:
        for exercise in session.session_exercises:
            name = actual_exercise_name(exercise)
            if not name:
                continue
            resolution = _resolve_cached(db, name, cache)
            if resolution.is_known:
                _record_strength_zones(evidence, resolution, session.started_at)

    if latest_cardio is not None:
        _record_cardio_zones(evidence, latest_cardio)

    return evidence, len(cache)


def _compose_sufficiency(
    readiness: ReadinessSignal, fatigue: FatigueSignal
) -> tuple[Sufficiency, Confidence]:
    """Categorical composition over evidence completeness. **Not a score.**

    Counts how many of the four independent pieces of evidence exist — the
    readiness declaration and the three fatigue components — and maps the count
    to a qualifier. There is no arithmetic on the values themselves: a `None`
    never enters an average, and a missing component is never read as zero.

    The rules the spec imposes, and how each is satisfied:

    * *more missing evidence can only maintain or reduce confidence* — the
      mapping is monotonic in the count;
    * *stale readiness can only maintain or reduce* — a non-current declaration
      is not counted as present evidence at all;
    * *cardio alone can never reach HIGH* — `HIGH` is unreachable from this
      function, full stop;
    * *no single optimistic signal upgrades an insufficient state* — the count
      ignores the values, so a flattering number cannot lift anything.

    `Confidence.HIGH` is never produced. Distinguishing "high" from "medium"
    would need an accuracy claim nothing here supports, and the spec says to
    take the more conservative option when no defensible distinction exists.
    """
    present = sum((
        readiness.is_decision_relevant,
        fatigue.strength_component is not None,
        fatigue.cardio_component is not None,
        fatigue.subjective_component is not None,
    ))
    if present == 0:
        return Sufficiency.INSUFFICIENT, Confidence.NONE
    if present == 1:
        return Sufficiency.PARTIAL, Confidence.LOW
    return Sufficiency.SUFFICIENT, Confidence.MEDIUM


def build_training_state(
    db: Session,
    user_id: int,
    *,
    now: datetime,
    lookback_days: int = TRAINING_STATE_LOOKBACK_DAYS,
) -> TrainingState:
    """Assemble the live evidence into a `TrainingState`. Read-only.

    ``now`` is required, not defaulted to a clock read: the result must be
    reproducible for a fixed database state, and a hidden clock would make it
    untestable.

    ``zone_recovery`` is returned **empty on purpose**. Producing a
    `ZoneRecoveryEstimate` means producing an estimate, a band and a temporal
    model, and all three belong to `Sb_ZONE_RECOVERY_ESTIMATE_01`. The raw facts
    that slice will need are gathered and exposed as
    :attr:`TrainingState.basis` counts rather than dressed up as estimates —
    fabricating placeholder numbers here would be exactly the fail-open §4
    forbids.
    """
    window_start = now - timedelta(days=lookback_days)

    # One statement for the whole window, with children eager-loaded: the
    # per-zone pass below then runs entirely in memory.
    sessions = list(db.execute(
        select(WorkoutSession)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == SessionStatus.COMPLETED,
            WorkoutSession.excluded_from_stats.is_(False),
            WorkoutSession.started_at >= window_start,
        )
        .order_by(WorkoutSession.started_at.desc())
        .options(selectinload(WorkoutSession.session_exercises))
    ).scalars())

    readiness = _readiness_signal(db, user_id, now=now)
    strength_value, strength_basis = _strength_component(
        db, user_id, window_start=window_start)
    subjective_value, subjective_basis = _subjective_component(sessions)
    cardio_value, cardio_confidence, cardio_basis, latest_cardio = (
        _cardio_component(sessions))

    fatigue = FatigueSignal(
        strength_component=strength_value,
        cardio_component=cardio_value,
        subjective_component=subjective_value,
        sufficiency=(
            Sufficiency.INSUFFICIENT
            if strength_value is None and subjective_value is None
            and cardio_value is None
            else Sufficiency.PARTIAL
        ),
        confidence=cardio_confidence if cardio_value is not None else Confidence.LOW,
        basis=(strength_basis, subjective_basis, *cardio_basis),
    )

    evidence, resolutions = _zone_evidence(db, sessions, latest_cardio)
    sufficiency, confidence = _compose_sufficiency(readiness, fatigue)

    return TrainingState(
        computed_at=now,
        readiness=readiness,
        fatigue=fatigue,
        # Empty by design — see the docstring. The next slice owns estimates.
        zone_recovery=(),
        zone_suitability=(),
        # No authoritative equipment source exists at this boundary:
        # `program_quality_engine.UserProfile.available_equipment` is an input
        # dataclass with no persistence and no constructor in the app. A gym
        # profile is not manufactured here.
        equipment=None,
        # No persisted schedule source exists in V1.
        schedule=None,
        sufficiency=sufficiency,
        confidence=confidence,
        basis=(
            f"window: {lookback_days}d ending {now.date().isoformat()}",
            f"{len(sessions)} completed session(s) in window",
            f"zone evidence gathered for {len(evidence)} zone(s) "
            f"from {resolutions} distinct exercise name(s)",
            "zone_recovery deliberately empty — estimates belong to "
            "Sb_ZONE_RECOVERY_ESTIMATE_01",
        ),
    )


def zone_evidence_for(
    db: Session, user_id: int, *, now: datetime,
    lookback_days: int = TRAINING_STATE_LOOKBACK_DAYS,
) -> dict[str, _ZoneEvidence]:
    """The raw per-zone facts, for the next slice to build estimates on.

    Exposed separately from `TrainingState` precisely so that nothing in the
    public state object looks like a recovery reading. These are facts —
    timestamps and counts — not conclusions.
    """
    window_start = now - timedelta(days=lookback_days)
    sessions = list(db.execute(
        select(WorkoutSession)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == SessionStatus.COMPLETED,
            WorkoutSession.excluded_from_stats.is_(False),
            WorkoutSession.started_at >= window_start,
        )
        .order_by(WorkoutSession.started_at.desc())
        .options(selectinload(WorkoutSession.session_exercises))
    ).scalars())
    cardio = [s for s in sessions if s.cardio_duration_min is not None]
    evidence, _ = _zone_evidence(db, sessions, cardio[0] if cardio else None)
    return evidence


__all__ = [
    "TRAINING_STATE_AGGREGATOR_VERSION",
    "TRAINING_STATE_LOOKBACK_DAYS",
    "build_training_state",
    "zone_evidence_for",
]
