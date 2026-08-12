"""Sb_ZONE_RECOVERY_ESTIMATE_01 — per-zone recovery **estimates**.

Spec: `docs/strategy/Sx_RECOVERY_READINESS_01_SPEC.md` §2.3, §5.3, §11, §12bis.

This slice turns the facts `Sb_TRAINING_STATE_AGGREGATOR_01` gathered into
:class:`~app.services.recovery_contract.ZoneRecoveryEstimate` values. The
wording is load-bearing throughout: these are **estimates inferred from recently
logged training**. They are not measurements, not percentages of physiological
recovery, and not statements about muscle state.

## OQ-2, applied

The temporal rule lives in a **versioned :class:`RecoveryPolicy` object in
code** — not in a `BodyZone` column, and with **no migration**. A recovery
duration is not an intrinsic anatomical property of a zone: it depends on the
load applied, the history and the individual, so it belongs to a policy that can
be versioned and replaced, not to the schema.

The policy reads `RECOVERY_HOURS_TARGET` through the existing adapter
(`recovery_contract.recovery_target_hours`, a deferred import into
`recommendation.py`). Reading is allowed; `recommendation.py` is never modified.

## No new physiology

The estimate is `hours_since_last_load / target_hours`, clamped — which is the
formula the legacy path already used, reached through
`recovery_contract.normalize_training_suitability`. **Nothing is invented here.**
No exponential decay, no half-life, no "72h muscle rule". What this slice adds is
the corrected treatment of *absent* evidence, not a new curve.

## The fail-open this slice exists to close

The legacy path reports a zone it has never seen as `availability = 1.0` —
perfectly available. That is absence of data rendered as the best possible data.
Here it is `estimate=None`, `band=UNKNOWN`, `confidence=NONE`. The divergence is
deliberate, documented, and pinned by a test.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from app.services.muscle_mapping import ZONE_LABELS, radar_axis_for_zone
from app.services.recovery_contract import (
    Confidence,
    MacroAxisRecovery,
    RecoveryBand,
    Sufficiency,
    ZoneRecoveryEstimate,
    band_for_estimate,
    never_trained_estimate,
    normalize_training_suitability,
    recovery_target_hours,
    worst_zone_rollup,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.services.training_state import _ZoneEvidence

RECOVERY_POLICY_VERSION = 1

#: Attribution paths that came from the formal `Sb_32.4` mapping rather than the
#: historical substring matcher. Only these can reach `MEDIUM`.
_FORMAL_PATHS = frozenset({"db_lookup", "reviewed_correction"})

_CONFIDENCE_LADDER: tuple[Confidence, ...] = (
    Confidence.NONE, Confidence.LOW, Confidence.MEDIUM, Confidence.HIGH,
)


def _downgrade(confidence: Confidence) -> Confidence:
    """One step down the ladder; never below ``NONE``."""
    return _CONFIDENCE_LADDER[max(0, _CONFIDENCE_LADDER.index(confidence) - 1)]


@dataclass(frozen=True)
class RecoveryPolicy:
    """The temporal rule, **versioned in code** (OQ-2).

    Deliberately thin. It exists so the rule has a name, a version and a single
    place to change — not because it does anything clever. Both methods
    delegate to the canonical contract; this class owns no arithmetic.

    Replacing the rule later means shipping ``version=2``, not altering a
    schema and not editing `recommendation.py`.
    """

    version: int = RECOVERY_POLICY_VERSION

    def target_hours(self, zone_code: str) -> float | None:
        """Recovery target for a zone, read from the canonical constant."""
        return recovery_target_hours(zone_code)

    def estimate(self, hours_since_load: float | None, zone_code: str) -> float | None:
        """Hours since load → 0.0–1.0, higher = more likely available.

        The legacy formula, reached through the contract. ``None`` for an
        unusable input or an unknown zone — never a favourable default.
        """
        return normalize_training_suitability(hours_since_load, zone_code)


DEFAULT_RECOVERY_POLICY = RecoveryPolicy()


def canonical_zone_codes() -> tuple[str, ...]:
    """The 11 canonical zones, from the existing taxonomy.

    Read from `muscle_mapping.ZONE_LABELS`; this module declares no zone list of
    its own. `core` is one of them and stays one of them.
    """
    return tuple(ZONE_LABELS)


def _hours_between(earlier: datetime, now: datetime) -> float | None:
    """Whole-hours gap, tolerant of the repo's naive stored datetimes.

    `WorkoutSession.started_at` is a bare ``DateTime``, so SQLite hands it back
    without a timezone while ``now`` carries one. Comparing them directly raises;
    the stored value is aligned to ``now``'s zone rather than guessing a
    different one. A load in the future yields ``None`` instead of a negative
    gap that would read as "just trained".
    """
    if earlier.tzinfo is None and now.tzinfo is not None:
        earlier = earlier.replace(tzinfo=now.tzinfo)
    elif earlier.tzinfo is not None and now.tzinfo is None:
        now = now.replace(tzinfo=earlier.tzinfo)
    delta = (now - earlier).total_seconds() / 3600.0
    return delta if delta >= 0 else None


def estimate_for_zone(
    zone_code: str,
    evidence: _ZoneEvidence | None,
    *,
    now: datetime,
    policy: RecoveryPolicy = DEFAULT_RECOVERY_POLICY,
) -> ZoneRecoveryEstimate:
    """One zone's estimate. Pure — no database, no clock of its own.

    Cardio exposure **never raises** the estimate. It is recorded as a
    contributing signal and it **lowers** confidence, because it is evidence the
    zone was loaded in a way this contract cannot place in time. Letting it
    raise availability would be the asymmetry this train forbids: an uncertain
    signal may make the system more cautious, never more aggressive.
    """
    if evidence is None or evidence.last_strength_load_at is None:
        base = never_trained_estimate(zone_code)
        if evidence is None or not evidence.cardio_exposure_modalities:
            return base
        # Cardio touched it, but nothing places that exposure on a recovery
        # clock — so it stays unknown, and says why.
        modalities = ", ".join(sorted(evidence.cardio_exposure_modalities))
        return ZoneRecoveryEstimate(
            zone_code=zone_code,
            estimate=None,
            band=RecoveryBand.UNKNOWN,
            confidence=Confidence.NONE,
            basis=(
                "no recorded strength load for this zone",
                f"cardio exposure noted ({modalities}) but not placed in time",
            ),
            contributing_signals=("cardio_exposure",),
            staleness=Sufficiency.INSUFFICIENT,
        )

    hours = _hours_between(evidence.last_strength_load_at, now)
    value = policy.estimate(hours, zone_code)
    target = policy.target_hours(zone_code)

    if value is None:
        return ZoneRecoveryEstimate(
            zone_code=zone_code,
            band=RecoveryBand.UNKNOWN,
            confidence=Confidence.NONE,
            basis=("last load could not be placed against a recovery target",),
            last_relevant_load_at=evidence.last_strength_load_at,
            hours_since_last_load=hours,
            contributing_signals=("strength_load",),
            staleness=Sufficiency.INSUFFICIENT,
        )

    formal = bool(evidence.resolution_paths) and evidence.resolution_paths <= _FORMAL_PATHS
    confidence = Confidence.MEDIUM if formal else Confidence.LOW
    signals = ["strength_load"]
    basis = [
        f"{hours:.0f}h since last recorded load vs a {target:.0f}h target "
        f"(estimate, not a measurement)",
        f"{evidence.strength_occurrences} logged occurrence(s) in window",
    ]
    if not formal:
        basis.append(
            "attribution fell back to the substring classifier for at least one "
            "exercise"
        )
    if evidence.cardio_exposure_modalities:
        modalities = ", ".join(sorted(evidence.cardio_exposure_modalities))
        basis.append(
            f"cardio exposure also noted ({modalities}) — lowers confidence, "
            "never raises availability"
        )
        signals.append("cardio_exposure")
        confidence = _downgrade(confidence)

    return ZoneRecoveryEstimate(
        zone_code=zone_code,
        estimate=value,
        band=band_for_estimate(value),
        confidence=confidence,
        basis=tuple(basis),
        last_relevant_load_at=evidence.last_strength_load_at,
        hours_since_last_load=hours,
        contributing_signals=tuple(signals),
        staleness=Sufficiency.SUFFICIENT,
    )


def build_zone_recovery_from_evidence(
    evidence: dict[str, _ZoneEvidence],
    *,
    now: datetime,
    policy: RecoveryPolicy = DEFAULT_RECOVERY_POLICY,
) -> tuple[ZoneRecoveryEstimate, ...]:
    """Estimates for **all 11 canonical zones**, in taxonomy order. Pure.

    Every zone is always present. A zone with no evidence is returned as
    explicitly unknown rather than omitted — an absent entry would be
    indistinguishable from "not computed", and a consumer must be able to tell
    "we do not know" from "we did not look".
    """
    return tuple(
        estimate_for_zone(code, evidence.get(code), now=now, policy=policy)
        for code in canonical_zone_codes()
    )


def build_zone_recovery(
    db: Session,
    user_id: int,
    *,
    now: datetime,
    policy: RecoveryPolicy = DEFAULT_RECOVERY_POLICY,
) -> tuple[ZoneRecoveryEstimate, ...]:
    """Database convenience: gather the facts, then estimate. Read-only."""
    from app.services.training_state import zone_evidence_for

    evidence = zone_evidence_for(db, user_id, now=now)
    return build_zone_recovery_from_evidence(evidence, now=now, policy=policy)


def build_macro_recovery(
    estimates: tuple[ZoneRecoveryEstimate, ...],
) -> tuple[MacroAxisRecovery, ...]:
    """Roll detailed zones up to the radar axes — **presentation only** (OQ-5).

    Training decisions use the detailed zones. This exists so a compact surface
    can show one value per axis, and it takes the **worst** constituent zone,
    naming it, so the reading is conservative and traceable.

    Grouping reuses `muscle_mapping.radar_axis_for_zone`, the canonical
    projection derived from `RADAR_AXES` in `Sb_ZONE_COUNT_TAXONOMY_FIX_01`. It
    is not recopied here. `core` projects to no axis and is therefore **absent
    from the roll-up** while remaining fully present at the detailed level.
    """
    grouped: dict[str, list[ZoneRecoveryEstimate]] = {}
    for estimate in estimates:
        axis = radar_axis_for_zone(estimate.zone_code)
        if axis is None:
            continue
        grouped.setdefault(axis, []).append(estimate)
    return tuple(
        worst_zone_rollup(axis, tuple(members))
        for axis, members in grouped.items()
    )


#: The divergences from the legacy `recommendation.availability_by_zone` path,
#: enumerated so none of them is a surprise. Pinned by a test.
#:
#: The legacy path stays in place — `recommendation.py` is not modifiable and is
#: not modified — so the two coexist and disagree in exactly these ways.
LEGACY_DIVERGENCES: tuple[tuple[str, str, str], ...] = (
    (
        "never-trained zone",
        "legacy: availability = 1.0 (perfectly available)",
        "here: estimate=None, band=UNKNOWN, confidence=NONE — absence of data is "
        "not the best possible data",
    ),
    (
        "never-trained zone, hours",
        "legacy: hours_since_last = 24*365 sentinel",
        "here: hours_since_last_load=None — the sentinel is unmasked",
    ),
    (
        "zone with cardio exposure only",
        "legacy: cardio does not exist in this path at all",
        "here: recorded as a contributing signal, still UNKNOWN, never a raised "
        "availability",
    ),
)


__all__ = [
    "DEFAULT_RECOVERY_POLICY",
    "LEGACY_DIVERGENCES",
    "RECOVERY_POLICY_VERSION",
    "RecoveryPolicy",
    "build_macro_recovery",
    "build_zone_recovery",
    "build_zone_recovery_from_evidence",
    "canonical_zone_codes",
    "estimate_for_zone",
]
