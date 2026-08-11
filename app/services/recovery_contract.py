"""Sb_RECOVERY_CONTRACT_01 — the canonical readiness/fatigue/recovery vocabulary.

Spec: `docs/strategy/Sx_RECOVERY_READINESS_01_SPEC.md` (§2 contract, §3 scales, §4 missing data,
§8 wording, §12bis resolved operator decisions).

**PURE.** No DB, no ORM, no router, no template, no HTTP, no randomness, no clock of its own, no
decision engine. Same inputs ⇒ same outputs. This module defines *what a signal means*; it does not
read one, and it does not decide anything.

Why this exists: four words — readiness, fatigue, recovery, availability — each designated several
different things in live code, on six different scales, with two of them pointing in opposite
directions under the same name. The audit is in §1 of the spec. This module is the single place
where each word gets one meaning, one scale, one direction and one missing-data policy.

Three rules run through everything here:

1. **Missing data never means "fresh."** A `None` is a `None`. It is never silently promoted to
   0.0, to 1.0, or to a comforting midpoint. See §4 of the spec.
2. **Direction is never flipped silently.** Fatigue is "higher = more fatigued", availability is
   "higher = more available", and converting between them goes through
   :func:`fatigue_to_availability` — a named function, visible at the call site.
3. **Asymmetry** (§12bis). A degraded, stale or uncertain signal may make the system *more*
   cautious. It may never make it *more* aggressive.

What this module deliberately does **not** provide:

* no global score of any kind on :class:`TrainingState` — see its docstring for why;
* no weighted aggregate on :class:`FatigueSignal` (OQ-3);
* no cardio magnitude coefficients (OQ-4) — :func:`cardio_load_estimate` is a *declared* contract
  that returns "insufficient" until `Sb_CARDIO_FATIGUE_ADAPTER_01` audits the stored vocabulary.
"""
from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum
from typing import Any

RECOVERY_CONTRACT_VERSION = 1

# ---------------------------------------------------------------------------
# Closed vocabularies
# ---------------------------------------------------------------------------
#
# These live here rather than in `app/enums.py` on purpose: that module is for
# vocabularies the user produces through the UI and that are **persisted**
# ("Stored as plain string / small int in the DB"). Nothing below is persisted
# or user-facing — these are contract-internal qualifiers.


class Sufficiency(StrEnum):
    """How much usable input stood behind a value. Spec §4.1."""

    SUFFICIENT = "sufficient"
    PARTIAL = "partial"
    INSUFFICIENT = "insufficient"
    STALE = "stale"


class Confidence(StrEnum):
    """How much weight a consumer may put on a value. Spec §4.1."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class RecoveryBand(StrEnum):
    """Qualitative band for a zone estimate.

    A band, not a number, is what a UI should show: two decimals imply a
    precision this model does not have (spec §2.3, §8).
    """

    LIKELY_AVAILABLE = "likely_available"
    PARTIALLY_RECOVERED = "partially_recovered"
    LIKELY_FATIGUED = "likely_fatigued"
    UNKNOWN = "unknown"


#: Neutral value, **named** so it can never be a bare ``0.5`` buried in a formula
#: (spec §4.3, condition 1). A neutral must always travel with a low/none
#: confidence and a basis, and may never trigger an escalation.
NEUTRAL_ESTIMATE = 0.5

#: Readiness declared this many days ago or more is :attr:`Sufficiency.STALE`
#: (OQ-6). Stale readiness may never justify a more aggressive recommendation.
READINESS_STALE_AFTER_DAYS = 3

_READINESS_MIN = 1
_READINESS_MAX = 5
_PERCENT_MAX = 100.0


# ---------------------------------------------------------------------------
# Primitive guards
# ---------------------------------------------------------------------------


def _is_real_number(value: Any) -> bool:
    """True for a usable numeric value.

    ``bool`` is excluded on purpose: it is a subclass of ``int``, so ``True``
    would otherwise sail through as ``1`` — the same trap
    `Sb_FATIGUE_SCALE_FIX_01` closed in ``normalize_fatigue_score``. NaN and the
    infinities are excluded too: NaN compares False against every bound, so a
    range check alone would let it through.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return math.isfinite(float(value))


def _is_whole_number(value: Any) -> bool:
    """True for a usable value that denotes a whole number.

    Uses ``float.is_integer()`` rather than ``float(v) != int(v)``: comparing
    floats with ``==``/``!=`` is unreliable in general and Sonar flags it
    (``python:S1244``). ``is_integer`` asks the question directly.
    """
    return _is_real_number(value) and float(value).is_integer()


def clamp_unit(value: float) -> float:
    """Clamp to the canonical 0.0–1.0 interval."""
    return max(0.0, min(1.0, value))


# ---------------------------------------------------------------------------
# The 13 legacy scale conversions (spec §3.1)
# ---------------------------------------------------------------------------


def normalize_readiness_scale(value: Any) -> float | None:
    """``ReadinessEntry`` 1–5 → 0.0–1.0, **higher = better**.

    Every dimension of the questionnaire uses 5 = best, including
    ``fatigue_level`` where 5 reads "Très frais". That field is therefore
    exposed as :attr:`ReadinessSignal.self_reported_freshness`, never as
    "fatigue" — mapping it into :class:`FatigueSignal` without complementing it
    would reproduce the direction inversion the audit found (spec §1.2 · C2).

    Anything outside integer 1–5 → ``None``.
    """
    if not _is_whole_number(value):
        return None
    v = int(value)
    if v < _READINESS_MIN or v > _READINESS_MAX:
        return None
    return (v - _READINESS_MIN) / (_READINESS_MAX - _READINESS_MIN)


def normalize_percent_scale(value: Any) -> float | None:
    """A 0–100 "higher = better" legacy score → 0.0–1.0.

    Used for the dashboard recovery axis (spec §3.1). Note this does **not**
    carry the axis's ``active=False`` state: an inactive axis must stay
    :attr:`Sufficiency.INSUFFICIENT`, not become ``0.0``.
    """
    if not _is_real_number(value):
        return None
    v = float(value)
    if v < 0.0 or v > _PERCENT_MAX:
        return None
    return v / _PERCENT_MAX


def normalize_behavioral_readiness(value: Any) -> float | None:
    """``behavioral.readiness_score`` 0–100 → 0.0–1.0, higher = better.

    Present so the §3.1 table is complete and the legacy scale is *named*.

    **No field of :class:`TrainingState` consumes it (OQ-1).**
    ``behavioral.readiness_score`` is the duplicate the audit found: it shares
    the word "readiness" with the user's declared questionnaire while measuring
    something else entirely. It stays a legacy producer with its current UI, and
    it is a candidate for visible deprecation once the new surface exists.
    """
    return normalize_percent_scale(value)


def normalize_session_feedback(
    global_state: str | None, concentration: str | None
) -> float | None:
    """Post-session subjective feedback → 0.0–1.0, **higher = more fatigued**.

    Reuses the production producer (``behavioral.compute_session_fatigue``) and
    the production normalizer (``normalize_fatigue_score``) rather than
    restating either formula. The vocabularies are the canonical
    :class:`~app.enums.SessionGlobalState` / :class:`~app.enums.SessionConcentration`.

    Both inputs ``None`` → ``None``: ``compute_session_fatigue`` would happily
    return its 50/40 defaults, but "the user told us nothing" is not a
    measurement and must not be dressed up as a neutral reading.
    """
    if global_state is None and concentration is None:
        return None
    # Deferred import: `behavioral` pulls the ORM in, and this module stays
    # import-light and pure.
    from app.services.behavioral import compute_session_fatigue

    raw = compute_session_fatigue(
        global_state=global_state, concentration=concentration
    )
    return normalize_legacy_fatigue(raw)


def hours_since_last_or_none(value: Any) -> float | None:
    """Legacy "hours since last load" → hours, with the sentinel unmasked.

    ``recommendation.build_signals`` writes ``24 * 365`` to mean "never trained".
    A number that large is arithmetically indistinguishable from a real gap, and
    downstream it becomes ``availability = 1.0`` — absence of data rendered as
    the *best* possible data (spec §1.2 · C4). Here "never" becomes ``None``.
    """
    if not _is_real_number(value):
        return None
    v = float(value)
    if v < 0.0 or v >= NEVER_TRAINED_HOURS_SENTINEL:
        return None
    return v


#: The sentinel `recommendation.build_signals` uses for "this zone was never
#: trained" (``24 * 365``). Read, never written, by this contract.
NEVER_TRAINED_HOURS_SENTINEL = 24.0 * 365.0


def days_since_last_or_none(value: Any) -> int | None:
    """``days_since_last_cardio`` / ``_strength`` → unchanged.

    Listed for completeness of the §3.1 table. The legacy producer is already
    honest here: it returns an explicit ``None`` rather than a sentinel. The only
    job left is rejecting negatives and non-integers.
    """
    if not _is_whole_number(value):
        return None
    v = int(value)
    return v if v >= 0 else None


def normalize_training_suitability(hours_since_last_load: Any, zone_code: str) -> float | None:
    """Hours since a zone's last load → 0.0–1.0, **higher = more suitable**.

    This is the renamed ``availability_by_zone`` (spec §2.4): "availability" is
    reserved for external constraints — equipment, schedule — while this is an
    *inference about the body*, so it is called suitability.

    **The fail-open is corrected here.** The legacy formula gives a
    never-trained zone ``1.0``. This returns ``None``. "I have never seen this
    zone" and "this zone is perfectly recovered" are different claims, and only
    one of them is true.
    """
    hours = hours_since_last_or_none(hours_since_last_load)
    if hours is None:
        return None
    target = recovery_target_hours(zone_code)
    if target is None or target <= 0:
        return None
    return clamp_unit(hours / target)


def recovery_target_hours(zone_code: str) -> float | None:
    """Canonical recovery target for a zone, in hours.

    Reads the existing ``recommendation.RECOVERY_HOURS_TARGET`` through a
    deferred import. Reading is explicitly allowed; ``recommendation.py`` is
    never modified (spec §7).

    **OQ-2 is resolved: this will not become a ``BodyZone`` column.** A recovery
    duration is not an intrinsic anatomical property of a zone — it depends on
    the load that was applied, the training history and the individual. Its
    eventual home is a *versioned RecoveryPolicy*, not a schema attribute, and
    that is a separate decision with its own migration question.
    """
    from app.services.recommendation import RECOVERY_HOURS_TARGET

    target = RECOVERY_HOURS_TARGET.get(zone_code)
    return float(target) if target is not None else None


def normalize_legacy_fatigue(value: Any) -> float | None:
    """Legacy 0–100 fatigue → 0.0–1.0, **higher = more fatigued**.

    **Delegates to ``recommendation_explainer.normalize_fatigue_score``.** It is
    not reimplemented, wrapped-with-tweaks, or copied: this contract owns the
    *vocabulary*, while `Sb_FATIGUE_SCALE_FIX_01` owns the *semantics* of this
    particular conversion — including the producible floor of 15.0 that makes
    the ``0.0`` failure sentinel identifiable, and the deliberately one-sided
    bound behind it. A second independent formula would be a second source of
    truth, and a test fails if one appears.
    """
    from app.services.recommendation_explainer import normalize_fatigue_score

    return normalize_fatigue_score(value)


def fatigue_to_availability(value: Any) -> float | None:
    """Complement a normalized fatigue value into a normalized availability.

    The *only* sanctioned way to change direction. Fatigue keeps "higher = more
    fatigued" everywhere; a consumer that wants the availability reading calls
    this, visibly, at the call site.

    Applied to a **single** component. There is no whole-signal complement,
    because there is no whole-signal aggregate to complement (OQ-3).
    """
    if not _is_real_number(value):
        return None
    v = float(value)
    if v < 0.0 or v > 1.0:
        return None
    return 1.0 - v


# ── Sb_CARDIO_FATIGUE_ADAPTER_01 — cardio exposure ─────────────────────────

CARDIO_ADAPTER_VERSION = 1


class CardioModality(StrEnum):
    """Closed vocabulary for the adapter, versioned with it.

    The four specific modalities plus the catalog's own catch-all, and one
    adapter-side bucket for anything the vocabulary does not cover.

    The persisted column is ``String(32)`` and the write endpoint applies **no
    allow-list** (``sessions.py`` only does ``clean_str(max_length=32)``), so a
    stored value outside this list is possible and must degrade gracefully. The
    *UI*, by contrast, is already a closed ``<select>`` — the two are different
    guarantees and the adapter relies only on the weaker one.
    """

    VELO = "velo"
    MARCHE = "marche"
    RAMEUR = "rameur"
    ELLIPTIQUE = "elliptique"
    AUTRE = "autre"
    UNKNOWN = "unknown"


#: Values the UI `<select>` in `session_detail.html` can currently produce.
CARDIO_UI_VOCABULARY: frozenset[str] = frozenset(
    {"velo", "marche", "rameur", "elliptique", "autre"}
)

#: Modalities specific enough to carry a zone distribution. ``AUTRE`` is a real
#: catalog value but says nothing about what moved, so it is not one of them.
CARDIO_SPECIFIC_MODALITIES: frozenset[CardioModality] = frozenset({
    CardioModality.VELO, CardioModality.MARCHE,
    CardioModality.RAMEUR, CardioModality.ELLIPTIQUE,
})

#: Duration at which a cardio session counts as full exposure, in minutes.
#:
#: **Taken from the product catalog, not invented and not biological.** Both
#: cardio templates in ``reference_split.json`` prescribe "20-30 min LISS"
#: (`liss-only`, `liss-abs`), so the top of the catalog's own prescribed range is
#: the natural saturation point: a session at the prescription counts as a full
#: unit of cardio exposure, and going longer cannot count for more than one.
#:
#: This is a **product normalization constant, not a biological fatigue
#: threshold.** Nothing physiological happens at 30 minutes.
#:
#: `coach_inference.CARDIO_LOW_MIN_PER_WEEK` (90) was considered and rejected: it
#: is a *weekly* volume floor derived from a public-health recommendation, the
#: wrong granularity for a per-session exposure proxy.
CARDIO_DURATION_REFERENCE_MINUTES = 30.0

#: Relative distribution weights **inside the cardio signal only**. They order
#: primary above secondary exposure; they are not percentages of anything, and
#: they are not a claim about muscle activation.
CARDIO_PRIMARY_ZONE_WEIGHT = 1.0
CARDIO_SECONDARY_ZONE_WEIGHT = 0.5


@dataclass(frozen=True)
class CardioZoneExposure:
    """Which body zones a cardio modality plausibly exposes. A **heuristic**.

    Deliberately coarse, and expressed as two classes — primary and secondary —
    rather than fake per-zone percentages. Zone codes are canonical
    ``BodyZone`` codes; this introduces no taxonomy of its own.
    """

    modality: CardioModality
    primary_zones: tuple[str, ...] = ()
    secondary_zones: tuple[str, ...] = ()
    basis: tuple[str, ...] = ()

    @property
    def is_distributed(self) -> bool:
        return bool(self.primary_zones or self.secondary_zones)

    def weights(self) -> dict[str, float]:
        """Relative weights for the exposed zones. Empty when undistributed."""
        weights = dict.fromkeys(self.primary_zones, CARDIO_PRIMARY_ZONE_WEIGHT)
        for zone in self.secondary_zones:
            weights.setdefault(zone, CARDIO_SECONDARY_ZONE_WEIGHT)
        return weights


#: Modality → zones. A **product heuristic**, versioned with the adapter.
#:
#: Not EMG, not measured activation, not tissue fatigue, not recovery. It says
#: only "this modality plausibly puts these zones under some exposure", coarsely
#: enough to be defensible without an ergometer.
#:
#: `elliptique` is deliberately lower-body only: the machine has moving handles,
#: but nothing in the captured data says whether they were used, so adding
#: upper-body zones would be inventing a fact about the session.
#
# The three lower-body-dominant modalities share one distribution, named once
# rather than repeated: cycling, inclined walking and the elliptical differ in
# how they load the legs, but nothing in the captured data distinguishes them,
# and pretending otherwise would be precision we do not have.
_LOWER_BODY_PRIMARY: tuple[str, ...] = ("quads", "posterior")
_LOWER_BODY_SECONDARY: tuple[str, ...] = ("calves",)

_CARDIO_ZONE_TABLE: dict[CardioModality, CardioZoneExposure] = {
    CardioModality.VELO: CardioZoneExposure(
        modality=CardioModality.VELO,
        primary_zones=_LOWER_BODY_PRIMARY,
        secondary_zones=_LOWER_BODY_SECONDARY,
        basis=("cycling: seated lower-body cyclic work, no upper-body load",),
    ),
    CardioModality.MARCHE: CardioZoneExposure(
        modality=CardioModality.MARCHE,
        primary_zones=_LOWER_BODY_PRIMARY,
        secondary_zones=_LOWER_BODY_SECONDARY,
        basis=("inclined walking: lower-body cyclic work, calves on the incline",),
    ),
    CardioModality.RAMEUR: CardioZoneExposure(
        modality=CardioModality.RAMEUR,
        primary_zones=(*_LOWER_BODY_PRIMARY, "lats", "upper_back"),
        secondary_zones=("biceps",),
        basis=("rowing: leg drive plus a pulling chain — the one mixed modality",),
    ),
    CardioModality.ELLIPTIQUE: CardioZoneExposure(
        modality=CardioModality.ELLIPTIQUE,
        primary_zones=_LOWER_BODY_PRIMARY,
        secondary_zones=_LOWER_BODY_SECONDARY,
        basis=(
            "elliptical: lower-body dominant; handle use is not captured, so no "
            "upper-body zone is claimed",
        ),
    ),
}


def normalize_cardio_modality(raw: Any) -> tuple[CardioModality | None, str | None]:
    """Stored ``cardio_machine_type`` → modality, plus the off-list raw value.

    Returns ``(None, None)`` when nothing was recorded — no modality is
    fabricated for an empty field.

    Normalisation is **trim and case only**. No alias table: the repository
    evidences no alias, and inventing spellings that were never observed is
    exactly the fabrication this contract forbids. An unrecognised non-empty
    value maps to :attr:`CardioModality.UNKNOWN` and is echoed back so the basis
    can name it.
    """
    if not isinstance(raw, str):
        return None, None
    cleaned = raw.strip().casefold()
    if not cleaned:
        return None, None
    if cleaned in CARDIO_UI_VOCABULARY:
        return CardioModality(cleaned), None
    return CardioModality.UNKNOWN, raw.strip()


def cardio_zone_exposure(modality: CardioModality | None) -> CardioZoneExposure:
    """Zone exposure for a modality. Undistributed when the modality is vague.

    ``AUTRE`` and ``UNKNOWN`` return an empty distribution on purpose: "some
    other machine" does not tell us what moved, and picking zones anyway to make
    coverage look complete is what §5.3 forbids.
    """
    if modality is None:
        return CardioZoneExposure(
            modality=CardioModality.UNKNOWN,
            basis=("no modality recorded",),
        )
    table_entry = _CARDIO_ZONE_TABLE.get(modality)
    if table_entry is not None:
        return table_entry
    return CardioZoneExposure(
        modality=modality,
        basis=(f"modality '{modality.value}' carries no zone distribution",),
    )


def cardio_load_estimate(
    *,
    machine_type: str | None = None,
    duration_min: Any = None,
    bpm_avg: Any = None,
) -> tuple[float | None, Confidence, tuple[str, ...]]:
    """Cardio **exposure proxy** for a single session, on 0.0–1.0.

    What the number is: ``duration / CARDIO_DURATION_REFERENCE_MINUTES``,
    clamped. One named, monotonic, bounded rule over the only quantitative input
    every usable cardio session has. Nothing else scales it.

    What the number is **not**: a percentage of physiological fatigue, a
    recovery reading, or a measurement of internal load. None of the captured
    fields observes any of those. Call it an operational cardio exposure proxy
    and nothing more.

    **Machine calories are not read** — they are not even a parameter. The
    product labels them "indicatif" in the capture form, they come from machine
    estimators of unknown calibration, and they are not an individualised load
    measure. They stay display and export information.

    **Average BPM does not scale the value.** With no individual anchor —
    measured HRmax, resting HR, HR reserve, a ventilatory or lactate threshold —
    an absolute 130 bpm is not comparable between two people. The catalog makes
    this concrete: both LISS templates prescribe the *same* "120-130 bpm" band to
    everyone, so a reading inside it carries no individual intensity
    information. BPM here is **evidence that the session was recorded more
    completely**, and it can lift confidence from LOW to MEDIUM on a specific
    modality. It can never make the load larger.

    Temporal decay is deliberately absent: this describes one session's
    exposure. When that exposure stops mattering belongs to
    ``Sb_ZONE_RECOVERY_ESTIMATE_01``.
    """
    modality, off_list = normalize_cardio_modality(machine_type)
    basis: list[str] = []

    usable_duration = (
        _is_real_number(duration_min) and float(duration_min) > 0.0
    )
    if not usable_duration:
        basis.append("no usable cardio_duration_min")
        if modality is not None:
            basis.append(f"modality: {modality.value}")
        return None, Confidence.NONE, tuple(basis)

    minutes = float(duration_min)
    value = clamp_unit(minutes / CARDIO_DURATION_REFERENCE_MINUTES)
    basis.append(
        f"{minutes:g} min vs {CARDIO_DURATION_REFERENCE_MINUTES:g} min reference "
        f"(product normalization, not a biological threshold)"
    )

    if modality is None:
        basis.append("no modality recorded")
    elif off_list is not None:
        basis.append(f"modality outside the known vocabulary: {off_list!r}")
    else:
        basis.append(f"modality: {modality.value}")

    usable_bpm = _is_real_number(bpm_avg) and float(bpm_avg) > 0.0
    if usable_bpm:
        basis.append(
            "average BPM recorded — raises evidence, never the magnitude "
            "(no individual heart-rate anchor exists)"
        )

    specific = modality in CARDIO_SPECIFIC_MODALITIES
    confidence = (
        Confidence.MEDIUM if (specific and usable_bpm) else Confidence.LOW
    )
    return value, confidence, tuple(basis)


#: Confidence this contract may never exceed for cardio, whatever the inputs
#: (OQ-4). Pinned by a test.
CARDIO_MAX_CONFIDENCE = Confidence.MEDIUM


_LEGACY_CONFIDENCE_LABELS: dict[str, Confidence] = {
    "élevée": Confidence.HIGH,
    "elevee": Confidence.HIGH,
    "moyenne": Confidence.MEDIUM,
    "faible": Confidence.LOW,
    "insuffisante": Confidence.NONE,
}


def confidence_from_legacy_label(label: Any) -> Confidence | None:
    """French confidence label (``muscle_scoring``, ``dashboard``) → :class:`Confidence`.

    ``None`` on an unknown label rather than a default: silently mapping an
    unrecognised label onto ``LOW`` would invent a confidence the producer never
    expressed.
    """
    if not isinstance(label, str):
        return None
    return _LEGACY_CONFIDENCE_LABELS.get(label.strip().casefold())


# Row 12 of the §3.1 table has **no conversion, deliberately**.
# ``ZONE_FRESHNESS_BONUS_{BASE,STEP,MIN}`` are scoring weights in points
# (base 15, step -6, floor -6) internal to ``recommendation.py``'s ranking. They
# measure nothing and have no meaning outside that formula, so normalizing them
# onto 0.0-1.0 would manufacture a quantity. The row exists in
# ``LEGACY_SCALE_CONVERSIONS`` with ``conversion=None`` so the omission is
# recorded rather than left as a gap someone later fills in.


# ---------------------------------------------------------------------------
# Machine-checkable registry of the §3.1 table
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ScaleConversion:
    """One row of the spec's legacy-scale table, bound to its implementation."""

    source: str
    legacy_scale: str
    legacy_direction: str
    target: str
    conversion: Callable[..., Any] | None
    note: str


# Shared descriptor vocabulary for the registry below. Named rather than
# repeated inline so the rows describe the same thing with the same words — and
# so a reader can tell "the same scale" from "a scale that happens to look
# similar".
_SCALE_PERCENT = "0–100"
_DIR_HIGHER_BETTER = "higher = better"
_DIR_HIGHER_OLDER = "higher = older"
_DIR_HIGHER_MORE_FATIGUED = "higher = more fatigued"
_DIR_NA = "n/a"
_UNIT_HIGHER_BETTER = "0.0–1.0, higher = better"
_UNIT_HIGHER_MORE_FATIGUED = "0.0–1.0, higher = more fatigued"

#: The 13 rows of spec §3.1, in order. A test pins the count and that every row
#: either has a callable or states why it has none — so the table and the code
#: cannot drift apart.
LEGACY_SCALE_CONVERSIONS: tuple[ScaleConversion, ...] = (
    ScaleConversion(
        "ReadinessEntry.sleep_quality / soreness_level / stress_level / motivation_level",
        "1–5 integers", "5 = best", _UNIT_HIGHER_BETTER,
        normalize_readiness_scale, "(v - 1) / 4; outside 1–5 → None",
    ),
    ScaleConversion(
        "ReadinessEntry.fatigue_level",
        "1–5 integers", "5 = VERY FRESH", "0.0–1.0, higher = fresher",
        normalize_readiness_scale,
        "exposed as self_reported_freshness — never mapped into FatigueSignal uncomplemented",
    ),
    ScaleConversion(
        "behavioral.fatigue_score",
        _SCALE_PERCENT, _DIR_HIGHER_MORE_FATIGUED, _UNIT_HIGHER_MORE_FATIGUED,
        normalize_legacy_fatigue,
        "delegates to recommendation_explainer.normalize_fatigue_score — never reimplemented",
    ),
    ScaleConversion(
        "behavioral.readiness_score",
        _SCALE_PERCENT, _DIR_HIGHER_BETTER, _UNIT_HIGHER_BETTER,
        normalize_behavioral_readiness,
        "named for completeness; NOT consumed by TrainingState (OQ-1)",
    ),
    ScaleConversion(
        "dashboard recovery axis score",
        _SCALE_PERCENT, _DIR_HIGHER_BETTER, _UNIT_HIGHER_BETTER,
        normalize_percent_scale,
        "does not carry active=False; an inactive axis stays INSUFFICIENT, not 0.0",
    ),
    ScaleConversion(
        "recommendation.availability_by_zone",
        "already 0.0–1.0", "higher = more available", "0.0–1.0 | None",
        normalize_training_suitability,
        "renamed TrainingSuitability; never-trained becomes None instead of 1.0",
    ),
    ScaleConversion(
        "recommendation.hours_since_last_by_zone",
        "hours, 24*365 = never", _DIR_HIGHER_OLDER, "float | None",
        hours_since_last_or_none, "the 24*365 sentinel becomes None",
    ),
    ScaleConversion(
        "recommendation.days_since_last_cardio / _strength",
        "days | None", _DIR_HIGHER_OLDER, "int | None",
        days_since_last_or_none, "already honest; only negatives and non-integers rejected",
    ),
    ScaleConversion(
        "recommendation.RECOVERY_HOURS_TARGET",
        "hours 24–72", _DIR_NA, "hours | None",
        recovery_target_hours,
        "read through a deferred import; no BodyZone column, no migration (OQ-2)",
    ),
    ScaleConversion(
        "WorkoutSession.global_state / concentration",
        "closed categorical", _DIR_NA, _UNIT_HIGHER_MORE_FATIGUED,
        normalize_session_feedback,
        "reuses compute_session_fatigue then normalize_fatigue_score; both None → None",
    ),
    ScaleConversion(
        "WorkoutSession cardio fields",
        "min / bpm / kcal / free text", _DIR_NA, "0.0–1.0 + confidence",
        cardio_load_estimate,
        "declared, not computed: magnitude deferred to Sb_CARDIO_FATIGUE_ADAPTER_01 (OQ-4)",
    ),
    ScaleConversion(
        "recommendation.ZONE_FRESHNESS_BONUS_*",
        "score points", "higher = fresher", "none",
        None,
        "intentionally not converted: internal ranking weights, not a measured quantity",
    ),
    ScaleConversion(
        "French confidence labels",
        "categorical FR", _DIR_NA, "Confidence",
        confidence_from_legacy_label, "unknown label → None, never a default",
    ),
)


# ---------------------------------------------------------------------------
# The semantic contract (spec §2)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ReadinessSignal:
    """What the user **declared** feeling today. Spec §2.1.

    Declared, not measured. Nothing here is presented as an objective recovery
    reading, and nothing here is derived from training load.

    ``self_reported_freshness`` carries ``ReadinessEntry.fatigue_level``, renamed
    because 5 on that field means "Très frais". The persisted column keeps its
    name — the rename lives at this boundary, so there is no migration.
    """

    declared_on: date | None = None
    age_days: int | None = None
    sleep: float | None = None
    soreness: float | None = None
    stress: float | None = None
    motivation: float | None = None
    self_reported_freshness: float | None = None
    overall: float | None = None
    sufficiency: Sufficiency = Sufficiency.INSUFFICIENT
    basis: tuple[str, ...] = ()

    @property
    def dimensions(self) -> tuple[float | None, ...]:
        """The five declared dimensions, in a stable order."""
        return (
            self.sleep, self.soreness, self.stress,
            self.motivation, self.self_reported_freshness,
        )

    @property
    def is_decision_relevant(self) -> bool:
        """Only a *today* declaration may inform a decision (OQ-6).

        And even then, asymmetrically: a good declaration can never on its own
        make a prescription more aggressive (OQ-7). This flag says the signal is
        current enough to be *considered*, never that it licenses escalation.
        """
        return self.sufficiency is Sufficiency.SUFFICIENT and self.age_days == 0


def readiness_sufficiency_for_age(age_days: Any) -> Sufficiency:
    """Age of a declaration → its sufficiency. OQ-6, spec §2.1.

    ``0`` → sufficient · ``1..2`` → partial (context only) · ``>= 3`` → stale ·
    missing or negative → insufficient.
    """
    if not _is_whole_number(age_days):
        return Sufficiency.INSUFFICIENT
    age = int(age_days)
    if age < 0:
        return Sufficiency.INSUFFICIENT
    if age == 0:
        return Sufficiency.SUFFICIENT
    if age < READINESS_STALE_AFTER_DAYS:
        return Sufficiency.PARTIAL
    return Sufficiency.STALE


def mean_of_present(values: tuple[float | None, ...]) -> float | None:
    """Mean over the values that exist. ``None`` if none of them do.

    A missing dimension is **excluded** from both numerator and denominator. It
    is never counted as ``0.0`` — that would read "the user reported the worst
    possible sleep" when in fact they reported nothing (spec §4.2).
    """
    present = [v for v in values if _is_real_number(v)]
    if not present:
        return None
    return sum(float(v) for v in present) / len(present)


@dataclass(frozen=True)
class FatigueSignal:
    """Accumulated load, kept **decomposed**. Spec §2.2, amended by OQ-3.

    There is deliberately **no aggregate**. Someone fatigued by an hour of
    cycling and someone fatigued by heavy squats are not in the same situation,
    and collapsing them into one number destroys exactly the information an
    explanation surface needs. Weighting the three components would also require
    coefficients no evidence in this repository supports.

    A consumer that genuinely needs one scalar derives it itself, owns the
    formula and documents it. Direction here is fixed: **higher = more
    fatigued**; :func:`fatigue_to_availability` is the only way to flip it.
    """

    strength_component: float | None = None
    cardio_component: float | None = None
    subjective_component: float | None = None
    sufficiency: Sufficiency = Sufficiency.INSUFFICIENT
    confidence: Confidence = Confidence.NONE
    basis: tuple[str, ...] = ()

    @property
    def components(self) -> dict[str, float | None]:
        """The three components, addressable by name."""
        return {
            "strength": self.strength_component,
            "cardio": self.cardio_component,
            "subjective": self.subjective_component,
        }

    @property
    def observed_components(self) -> dict[str, float]:
        """Only the components that actually have a value."""
        return {k: v for k, v in self.components.items() if v is not None}


@dataclass(frozen=True)
class ZoneRecoveryEstimate:
    """An **estimate** of how available one canonical BodyZone likely is.

    Spec §2.3. The wording is load-bearing: this is an estimate inferred from
    recently logged training. It is not a measurement, not a percentage of
    physiological recovery, and not a statement about muscle state (§8).

    ``zone_code`` is a canonical ``BodyZone`` code. This contract introduces no
    zone vocabulary of its own (§6).
    """

    zone_code: str
    estimate: float | None = None
    band: RecoveryBand = RecoveryBand.UNKNOWN
    confidence: Confidence = Confidence.NONE
    basis: tuple[str, ...] = ()
    last_relevant_load_at: datetime | None = None
    hours_since_last_load: float | None = None
    contributing_signals: tuple[str, ...] = ()
    staleness: Sufficiency = Sufficiency.INSUFFICIENT

    @property
    def is_informative(self) -> bool:
        """True only when there is a value, a confidence and a stated basis.

        An estimate without a basis is an assertion, and this contract does not
        make assertions about bodies.
        """
        return (
            self.estimate is not None
            and self.confidence is not Confidence.NONE
            and bool(self.basis)
        )


#: Band cut-offs, named rather than inlined. They are **presentation
#: thresholds**, not physiology: they decide which of three words a surface
#: shows, and nothing else. Moving them changes wording, never a decision.
BAND_LIKELY_AVAILABLE_FROM = 0.8
BAND_PARTIALLY_RECOVERED_FROM = 0.4


def band_for_estimate(estimate: Any) -> RecoveryBand:
    """Map an estimate onto its qualitative band. ``None`` → ``UNKNOWN``."""
    if not _is_real_number(estimate):
        return RecoveryBand.UNKNOWN
    v = float(estimate)
    if v < 0.0 or v > 1.0:
        return RecoveryBand.UNKNOWN
    if v >= BAND_LIKELY_AVAILABLE_FROM:
        return RecoveryBand.LIKELY_AVAILABLE
    if v >= BAND_PARTIALLY_RECOVERED_FROM:
        return RecoveryBand.PARTIALLY_RECOVERED
    return RecoveryBand.LIKELY_FATIGUED


def never_trained_estimate(zone_code: str) -> ZoneRecoveryEstimate:
    """The honest answer for a zone that has never been trained.

    Not ``1.0``. The legacy path reports a never-trained zone as perfectly
    available, which is absence of data dressed up as the best possible data
    (spec §1.2 · C4). Here it is unknown, with no confidence, and the basis says
    so.
    """
    return ZoneRecoveryEstimate(
        zone_code=zone_code,
        estimate=None,
        band=RecoveryBand.UNKNOWN,
        confidence=Confidence.NONE,
        basis=("no recorded load for this zone",),
        hours_since_last_load=None,
        staleness=Sufficiency.INSUFFICIENT,
    )


@dataclass(frozen=True)
class MacroAxisRecovery:
    """A macro-axis roll-up, for **presentation only**. OQ-5.

    Training decisions use detailed zones. When a compact surface needs one
    value per axis, it takes the **worst** constituent zone and names it — a
    conservative reading, and a traceable one. This value must never become a
    planner's source of truth.
    """

    axis_key: str
    estimate: float | None = None
    band: RecoveryBand = RecoveryBand.UNKNOWN
    limiting_zone_code: str | None = None
    confidence: Confidence = Confidence.NONE
    basis: tuple[str, ...] = ()


def worst_zone_rollup(
    axis_key: str, estimates: tuple[ZoneRecoveryEstimate, ...]
) -> MacroAxisRecovery:
    """Roll detailed zones up to one macro axis by taking the worst. OQ-5.

    The limiting zone is exposed, so a surface can say *which* zone is holding
    the axis back. Zones with no estimate are excluded from the minimum but
    **lower the confidence**: a partially-known axis is not a known axis.
    """
    known = [e for e in estimates if e.estimate is not None]
    if not known:
        return MacroAxisRecovery(
            axis_key=axis_key,
            basis=("no zone of this axis has a usable estimate",),
        )

    worst = min(known, key=lambda e: (e.estimate, e.zone_code))
    complete = len(known) == len(estimates)
    confidence = worst.confidence if complete else _downgrade(worst.confidence)
    basis = (f"limiting zone: {worst.zone_code}",)
    if not complete:
        missing = sorted(e.zone_code for e in estimates if e.estimate is None)
        basis += (f"no estimate for: {', '.join(missing)}",)

    return MacroAxisRecovery(
        axis_key=axis_key,
        estimate=worst.estimate,
        band=band_for_estimate(worst.estimate),
        limiting_zone_code=worst.zone_code,
        confidence=confidence,
        basis=basis,
    )


_CONFIDENCE_LADDER: tuple[Confidence, ...] = (
    Confidence.NONE, Confidence.LOW, Confidence.MEDIUM, Confidence.HIGH,
)


def _downgrade(confidence: Confidence) -> Confidence:
    """One step down the ladder; never below ``NONE``."""
    idx = _CONFIDENCE_LADDER.index(confidence)
    return _CONFIDENCE_LADDER[max(0, idx - 1)]


# ---------------------------------------------------------------------------
# Availability — the word, split into the things it actually meant (spec §2.4)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EquipmentAvailability:
    """What hardware exists where the user trains.

    An external constraint, wrapping the existing ``available_equipment``
    concept. ``None`` means "unconstrained", which is what the current callers
    already mean by it.
    """

    equipment_families: tuple[str, ...] | None = None
    basis: tuple[str, ...] = ()

    @property
    def is_constrained(self) -> bool:
        return self.equipment_families is not None


@dataclass(frozen=True)
class ScheduleAvailability:
    """Whether the user has time. **Declared, not implemented.**

    No such data exists anywhere in the codebase today. The type is defined so
    the concept has a name and cannot get folded back into one of the other
    three, and it is always ``None`` on a V1 :class:`TrainingState`.
    """

    minutes_available: int | None = None
    basis: tuple[str, ...] = ()


@dataclass(frozen=True)
class TrainingSuitability:
    """Whether training a zone now is indicated. An inference about the body.

    This is the renamed ``availability_by_zone``. It is kept apart from
    :class:`EquipmentAvailability` and :class:`ScheduleAvailability` because
    those are facts about the world, while this is a guess about a person — and
    the audit found all three sharing one word (spec §1.2 · C3).
    """

    zone_code: str
    suitability: float | None = None
    confidence: Confidence = Confidence.NONE
    basis: tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# TrainingState (spec §2.5)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TrainingState:
    """The deterministic aggregate future consumers read.

    **This class exposes no score.** No ``overall_score``, no
    ``readiness_score``, no ``recovery_percentage``, no opaque composite — and
    that is a constraint, not an omission. Any such field would become *the*
    number on the screen, and within months nobody would remember what it
    aggregated; that is precisely how the six incompatible scales in the audit
    came to exist. A consumer that needs one scalar derives it, owns the formula
    and documents it, outside this contract.

    ``sufficiency`` and ``confidence`` are categorical qualifiers of the state as
    a whole. They are not scores and cannot be read as one.

    Read-only and pure: nothing here writes, and nothing here decides.
    """

    computed_at: datetime | None = None
    readiness: ReadinessSignal = field(default_factory=ReadinessSignal)
    fatigue: FatigueSignal = field(default_factory=FatigueSignal)
    zone_recovery: tuple[ZoneRecoveryEstimate, ...] = ()
    zone_suitability: tuple[TrainingSuitability, ...] = ()
    equipment: EquipmentAvailability | None = None
    schedule: ScheduleAvailability | None = None
    sufficiency: Sufficiency = Sufficiency.INSUFFICIENT
    confidence: Confidence = Confidence.NONE
    contract_version: int = RECOVERY_CONTRACT_VERSION
    basis: tuple[str, ...] = ()

    def zone(self, zone_code: str) -> ZoneRecoveryEstimate | None:
        """The estimate for one zone, or ``None`` if this state has none."""
        for estimate in self.zone_recovery:
            if estimate.zone_code == zone_code:
                return estimate
        return None


# ---------------------------------------------------------------------------
# Wording guardrails (spec §8)
# ---------------------------------------------------------------------------

#: Vocabulary this contract is allowed to use about a body.
ALLOWED_CONTRACT_WORDING: tuple[str, ...] = (
    "estimate", "indicative", "declared", "inferred",
    "recent load", "confidence", "basis", "training suitability",
)

#: Vocabulary the contract may never use. Pinned by a test over this module's
#: own public surface — not a general prose linter over the repository.
FORBIDDEN_CONTRACT_WORDING: tuple[str, ...] = (
    "physiologically recovered",
    "measured muscle recovery",
    "measured activation",
    "diagnosis",
    "injury prediction",
    "therapeutic prescription",
)
