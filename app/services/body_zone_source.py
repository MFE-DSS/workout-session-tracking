"""Sb_32.4 — the canonical body-zone read contract.

One adapter, one query path. Heavy consumers ask *this* module which body zones
an exercise trains, instead of each reaching for its own taxonomy lookup.

Why a contract rather than "call the DB from everywhere":

* the DB query already exists once, in
  ``muscle_mapping._classify_exercise_by_lookup`` — this module **reuses** it
  rather than writing a second one (Sb_32.4: "Do NOT duplicate DB query logic
  across consumers");
* the fallback to the historical substring classifier must be **visible**, not
  silent, so every answer carries how it was obtained;
* the two mapping errors the audit identified are corrected **here**, once,
  from a reviewed and machine-testable list — not re-frozen in each consumer.

``body_map_descriptor`` is deliberately **not** rebuilt or routed through this
module. It is the existing narrow DB-backed path and it keeps working exactly
as before; this adapter is the contract for the *heavy analytics* consumers.

Identity note: ``ExerciseMuscleMapping.exercise_code`` holds the exercise
**name** (the catalog has no stable per-exercise code — ``code`` in
``reference_split.json`` is a training-day slot like ``E1``, reused across
exercises). ``SessionExercise.exercise_code_snapshot`` is therefore NOT the
lookup key; the name from ``actual_exercise_name`` is.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from app.services.muscle_mapping import (
    _classify_exercise_by_lookup,
    _classify_exercise_by_patterns,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


# ── Reviewed divergence list ───────────────────────────────────────────────
#
# Sb_32.4 requires that known mapping errors are not silently re-frozen, and
# that every legacy→formal divergence is classified. Both entries below are
# category 1 — "intentional correction supported by canonical evidence" — and
# the evidence is repo data, not opinion. Any consumer reading through this
# adapter gets the corrected attribution; the historical migration rows and the
# `classify_exercise` baseline are left untouched, so invariance-vs-baseline
# stays provable for what it was written to prove.
#
# This list is short by design. It is not a place to park guesses: an
# unexplained divergence is a HARD STOP, not a new entry here.

@dataclass(frozen=True)
class ZoneCorrection:
    """A reviewed, evidence-backed override of the inherited classification."""

    exercise_name: str
    legacy_primary: str
    legacy_secondary: tuple[str, ...]
    primary: str
    secondary: tuple[str, ...]
    evidence: str


KNOWN_MAPPING_CORRECTIONS: tuple[ZoneCorrection, ...] = (
    ZoneCorrection(
        exercise_name="Rear delt fly machine (pec deck inversé)",
        legacy_primary="pecs",
        legacy_secondary=("triceps",),
        primary="delt_post",
        secondary=(),
        evidence=(
            "The substring classifier scans an ORDERED list and the `pecs` group "
            "(index 0) contains 'pec deck', so the parenthetical decides before the "
            "`delt_post` group (index 2) is ever reached. The repo contradicts that "
            "result with itself: the EKB entry carries machine_slug "
            "'rear-delt-fly-machine' and machine_family "
            "'shoulders-lateral-posterior' — byte-identical to the bare 'Rear delt "
            "fly machine' entry, which the EKB classifies zone_primary 'delt_post'. "
            "Same machine, same family, two verdicts: the difference is a naming "
            "artifact, not anatomy."
        ),
    ),
    ZoneCorrection(
        exercise_name="Relevé de jambes suspendu",
        legacy_primary="calves",
        legacy_secondary=(),
        primary="core",
        secondary=(),
        evidence=(
            "The `calves` group (index 9) contains the bare token 'relevé', which "
            "prefixes 'relevé de jambes'; the `core` group (index 10) lists both "
            "'relevé de jambe' and 'hanging' but is never reached. The catalog "
            "settles it: reference_split.json places this exercise in template "
            "'liss-abs', whose focus is literally 'Core / Abdos' "
            "(== ZONE_LABELS['core']), alongside ab wheel rollout, cable crunch and "
            "Pallof press — all three of which classify as `core`."
        ),
    ),
    ZoneCorrection(
        exercise_name="Calf press leg press",
        legacy_primary="quads",
        legacy_secondary=(),
        primary="calves",
        secondary=(),
        evidence=(
            "The substring classifier scans an ORDERED list and the `quads` group "
            "contains 'leg press', which matches before the `calves` group is ever "
            "reached — the same ordered-list artifact as the two corrections above. "
            "The repo contradicts that result with itself: exercise_properties.json "
            "gives this exercise muscle_group 'calves' (the field that exists "
            "precisely to disambiguate the overloaded `lower` region), and the EKB "
            "classifies it zone_primary 'calves'. Two curated sources say calves; "
            "only the name matcher says quads. "
            "Adjudicated by the operator for this EXACT canonical identity. It is "
            "NOT a statement about 'leg press' in general: the ordinary leg press "
            "entries keep their quads attribution, and a mapping diff over the whole "
            "referential proves this exercise is the only one that moves. "
            "The classification is a PROGRAMMING attribution: this movement is "
            "programmed as a calf-target exercise, and the record says only that. "
            "It carries no claim about muscle physiology."
        ),
    ),
)

_CORRECTIONS_BY_NAME: dict[str, ZoneCorrection] = {
    c.exercise_name: c for c in KNOWN_MAPPING_CORRECTIONS
}

# How an answer was obtained. Kept explicit so a consumer — or a test — can
# assert that a migrated path really read the formal mapping instead of
# quietly falling back.
PATH_CORRECTION = "reviewed_correction"
PATH_DB = "db_lookup"
PATH_SUBSTRING = "substring_fallback"
PATH_UNKNOWN = "unknown"


@dataclass(frozen=True)
class ZoneResolution:
    """What an exercise trains, and how we know."""

    primary: str
    secondary: tuple[str, ...] = ()
    resolution_path: str = PATH_UNKNOWN

    @property
    def is_known(self) -> bool:
        return self.primary != "unknown"

    @property
    def from_formal_mapping(self) -> bool:
        """True when the answer did NOT come from substring matching."""
        return self.resolution_path in (PATH_DB, PATH_CORRECTION)

    def as_legacy_tuple(self) -> tuple[str, list[str]]:
        """Shape-compatible with ``classify_exercise`` for drop-in migration."""
        return self.primary, list(self.secondary)


def resolve_exercise_zones(db: Session | None, exercise_name: str) -> ZoneResolution:
    """Resolve an exercise to its body zones through the canonical contract.

    Order: reviewed correction → formal ``ExerciseMuscleMapping`` row →
    historical substring classifier. The fallback is retained on purpose (the
    referential is not fully covered, and non-migrated consumers still rely on
    it) but it can never *override* the formal mapping — it only runs when the
    formal mapping has nothing to say.

    ``db=None`` is accepted so pure/offline callers degrade to the substring
    path instead of crashing; the returned ``resolution_path`` says so.
    """
    name = (exercise_name or "").strip()
    if not name:
        return ZoneResolution(primary="unknown", resolution_path=PATH_UNKNOWN)

    correction = _CORRECTIONS_BY_NAME.get(name)
    if correction is not None:
        return ZoneResolution(
            primary=correction.primary,
            secondary=correction.secondary,
            resolution_path=PATH_CORRECTION,
        )

    if db is not None:
        looked_up = _classify_exercise_by_lookup(db, name)
        if looked_up is not None:
            primary, secondary = looked_up
            return ZoneResolution(
                primary=primary,
                secondary=tuple(secondary),
                resolution_path=PATH_DB,
            )

    primary, secondary = _classify_exercise_by_patterns(name)
    if primary == "unknown":
        return ZoneResolution(primary="unknown", resolution_path=PATH_UNKNOWN)
    return ZoneResolution(
        primary=primary,
        secondary=tuple(secondary),
        resolution_path=PATH_SUBSTRING,
    )


@dataclass(frozen=True)
class ParityReport:
    """Legacy vs formal comparison over the whole canonical referential."""

    total: int = 0
    exact_matches: int = 0
    intentional_divergences: list[str] = field(default_factory=list)
    unexplained_divergences: list[str] = field(default_factory=list)
    missing_formal_mapping: list[str] = field(default_factory=list)
    ambiguous_mappings: list[str] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        """Acceptance: no unexplained divergence, nothing ambiguous."""
        return not self.unexplained_divergences and not self.ambiguous_mappings

    def as_lines(self) -> list[str]:
        return [
            f"total exercises        : {self.total}",
            f"exact matches          : {self.exact_matches}",
            f"intentional divergences: {len(self.intentional_divergences)}",
            f"unexplained divergences: {len(self.unexplained_divergences)}",
            f"missing formal mapping : {len(self.missing_formal_mapping)}",
            f"ambiguous mappings     : {len(self.ambiguous_mappings)}",
        ]


def find_ambiguous_mappings(db: Session, exercise_names: list[str]) -> list[str]:
    """Names carrying more than one ACTIVE ``primary`` row.

    The unique constraint is ``(exercise_code, body_zone_code, role)``, so two
    *different* zones can both be stored as ``primary`` for one exercise. The
    lookup would then silently pick whichever sorts first by ``position, id`` —
    a stable answer, but an arbitrary one. That is a data-integrity fault, so
    it is surfaced rather than resolved.

    A dedicated aggregate query, not a second classification path: this asks
    about the *shape* of the reference data, not about what an exercise trains.
    """
    from sqlalchemy import func, select

    from app.models.exercise_muscle_mapping import ExerciseMuscleMapping

    rows = db.execute(
        select(ExerciseMuscleMapping.exercise_code)
        .where(
            ExerciseMuscleMapping.exercise_code.in_(exercise_names),
            ExerciseMuscleMapping.role == "primary",
            ExerciseMuscleMapping.is_active.is_(True),
        )
        .group_by(ExerciseMuscleMapping.exercise_code)
        .having(func.count(ExerciseMuscleMapping.id) > 1)
    ).scalars().all()
    return sorted(rows)


def build_parity_report(db: Session, exercise_names: list[str]) -> ParityReport:
    """Compare the legacy classifier against the formal contract, name by name.

    An *intentional* divergence is one the reviewed list explains, and it must
    match that entry exactly — a correction that no longer produces what it
    claims is reported as unexplained rather than waved through.
    """
    exact = 0
    intentional: list[str] = []
    unexplained: list[str] = []
    missing: list[str] = []
    ambiguous = find_ambiguous_mappings(db, exercise_names)

    for name in exercise_names:
        legacy_primary, legacy_secondary = _classify_exercise_by_patterns(name)
        resolved = resolve_exercise_zones(db, name)

        if _classify_exercise_by_lookup(db, name) is None and name not in _CORRECTIONS_BY_NAME:
            missing.append(name)

        same = (
            resolved.primary == legacy_primary
            and list(resolved.secondary) == legacy_secondary
        )
        if same:
            exact += 1
            continue

        correction = _CORRECTIONS_BY_NAME.get(name)
        explained = (
            correction is not None
            and correction.legacy_primary == legacy_primary
            and list(correction.legacy_secondary) == legacy_secondary
            and correction.primary == resolved.primary
            and correction.secondary == resolved.secondary
        )
        (intentional if explained else unexplained).append(name)

    return ParityReport(
        total=len(exercise_names),
        exact_matches=exact,
        intentional_divergences=intentional,
        unexplained_divergences=unexplained,
        missing_formal_mapping=missing,
        ambiguous_mappings=ambiguous,
    )
