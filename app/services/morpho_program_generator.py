"""Pure morphology-aware program generator (Sb_MORPHO_PROGRAM_GENERATOR_01, spec `Sx_MORPHO_PROGRAM_01`).

Third build of the morphology-aware programming queue. Given **morphology descriptors**
(or the raw `MorphologyFacts` behind them) and optional **training priorities** +
**availability**, it produces a **deterministic program proposal** made of ordered
`SlotIntent` selections and candidate EKB exercises. It is PURE and ADDITIVE — a pure
function of its inputs (no I/O, no DB, no ORM, no HTTP, no LLM, no randomness): same inputs
⇒ same output, same fingerprint (patron éprouvé `program_quality_engine` / `overload_engine`).

It **composes existing, already-delivered layers, read-only**:
- `morphology_profile.build_morphology_profile` — facts → descriptors (Sb_MORPHO_PROFILE_01).
- `slot_intent` — descriptors/priorities → `SlotIntent`s (Sb_PROGRAM_SLOT_INTENT_01).
- `substitution.compute_proximity` (via `slot_intent.score_candidate`) — READ-ONLY candidate
  scoring against a slot. **`substitution.py` is NOT modified**; N1/N2/N3 runtime behaviour and
  the "different pattern ⇒ never N1/N2" guarantee are untouched — the generator only *chooses a
  preferred candidate BEFORE* substitution, never the substitution engine.
- `substitution.load_exercise_properties` — the READ-ONLY candidate pool (`exercise_properties.json`).

Hard frontiers (spec §0/§11, this sprint's mission):
- **No DB write, no migration, no UI, no publication lifecycle, no session flow change, no
  substitution runtime change, no `/library` exposure, no EKB expansion.** Nothing is persisted.
- **No Martin hardcoding** in the global logic — Martin is only ever a *private test fixture*.
- **No Custom Program / template creation** — the output is an in-memory *proposal* object.

Candidate-selection contract (deterministic, honest about pool coverage):
- A candidate is *forbidden* if its `pattern_motor` is on the slot's forbidden list
  (`slot_intent.candidate_pattern_forbidden`) — it would break the intent.
- A candidate *qualifies* only if its macro `zone_primary` == the slot's `target_region` AND
  it genuinely matches: by `pattern_motor` for upper-body regions, or — because the macro region
  ``lower`` bundles quads/hamstrings/adductors/**calves** — by the EXISTING `muscle_group`
  taxonomy for lower-body intents. A muscle without a pool representative (e.g. calves) therefore
  yields **no preferred exercise + an explicit coverage-gap warning**, never a false leg pick.
- `preferred_exercise` = the highest-scoring qualifying, available candidate (ties broken by name
  for determinism); the rest become `fallback_candidates`. If qualifying candidates exist but none
  pass `availability`, the slot emits an **availability-gap warning**; if none qualify at all, a
  **coverage-gap warning**. Guarded (`not_deductible`) descriptors produce **no slot**.
"""
from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass, replace

from app.services.morphology_profile import (
    MorphologyDescriptor,
    MorphologyFacts,
    build_morphology_profile,
)
from app.services.slot_intent import (
    SlotIntent,
    build_slot_intents_from_descriptors,
    build_slot_intents_from_priorities,
    candidate_pattern_forbidden,
    score_candidate,
)
from app.services.substitution import load_exercise_properties

MORPHO_PROGRAM_GENERATOR_ENGINE_VERSION = 1
_FINGERPRINT_PREFIX = "mpg1"

# Some macro regions (exercise_properties `zone_primary`) bundle several DETAILED muscle_mapping
# zones the radar merges: `lower` = quads/hamstrings/adductors/calves, `shoulders` = lateral/rear
# delts (+ presses). Disambiguate them with the EXISTING `muscle_group` taxonomy, keyed by the
# slot's DETAILED primary_zone. A detailed zone with no pool representative therefore qualifies
# nothing → explicit coverage-gap warning (never a false pick from a sibling muscle in the region).
_REGION_ZONE_MUSCLE_GROUP: dict[str, dict[str, str]] = {
    "lower": {
        "quads": "quadriceps",
        "posterior": "hamstrings",
        "calves": "calves",
    },
    "shoulders": {
        "delt_lat": "delts_lateral",
        "delt_post": "delts_rear",
    },
}

_DEFAULT_MAX_FALLBACKS = 3


# ── Output model (frozen, pure data — nothing here is persisted) ─────────────


@dataclass(frozen=True)
class SlotSelection:
    """One slot of the proposal: its `SlotIntent` + the chosen EKB candidate (or a warning)."""

    slot_id: str
    intent_id: str
    primary_zone: str
    target_region: str
    movement_pattern: str
    priority_level: int
    preferred_exercise: str | None
    preferred_score: int | None
    fallback_candidates: tuple[tuple[str, int], ...]
    rationale: str
    warning: str | None
    slot_intent: SlotIntent

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class RejectedDescriptor:
    """A descriptor that produced no slot (guarded / not_deductible), kept for traceability."""

    descriptor_id: str
    reason: str


@dataclass(frozen=True)
class GeneratedProgram:
    """A deterministic morphology-aware program proposal (in-memory only — never persisted)."""

    generated_program_id: str
    engine_version: int
    source_descriptors: tuple[str, ...]
    priorities: tuple[tuple[str, int], ...]
    availability: tuple[str, ...] | None
    selections: tuple[SlotSelection, ...]
    rejected_descriptors: tuple[RejectedDescriptor, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


# ── Candidate selection (read-only reuse of the substitution proximity contract) ──


def _qualifies(intent: SlotIntent, cand_props: dict) -> bool:
    """A candidate qualifies for a slot only on a genuine (not merely zone-level) match.

    The macro region carries the zone; a non-overloaded region additionally requires the same
    `pattern_motor`, while an overloaded region (`lower`, `shoulders`) is disambiguated by
    `muscle_group` (existing taxonomy) so a sibling muscle absent from the pool qualifies nothing."""
    if cand_props.get("zone_primary") != intent.target_region:
        return False
    zone_map = _REGION_ZONE_MUSCLE_GROUP.get(intent.target_region)
    if zone_map is not None:
        req_mg = zone_map.get(intent.primary_zone)
        if req_mg is not None:
            return cand_props.get("muscle_group") == req_mg
    return cand_props.get("pattern_motor") == intent.movement_pattern


def _rank_qualifying(intent: SlotIntent, pool: dict[str, dict]) -> list[tuple[str, int]]:
    """All non-forbidden, qualifying candidates, ranked by (score desc, name asc) — deterministic."""
    scored: list[tuple[str, int]] = []
    for name in sorted(pool):
        props = pool[name]
        if candidate_pattern_forbidden(intent, props):
            continue
        if not _qualifies(intent, props):
            continue
        scored.append((name, score_candidate(intent, props)))
    scored.sort(key=lambda item: (-item[1], item[0]))
    return scored


def _select_for_slot(
    intent: SlotIntent,
    pool: dict[str, dict],
    availability: frozenset[str] | None,
    max_fallbacks: int,
    used: set[str],
) -> SlotSelection:
    """Pick the preferred + fallback candidates for one slot, distinguishing a coverage gap
    (nothing qualifies), a distinctness gap (all qualifying already used by earlier slots — a
    program never prescribes the same exercise twice), and an availability gap (qualifies but
    nothing available). `used` accumulates the exercises already chosen (deterministic slot order)."""
    qualifying = _rank_qualifying(intent, pool)
    distinct = [c for c in qualifying if c[0] not in used]
    if availability is not None:
        available = [c for c in distinct if pool[c[0]].get("equipment_family") in availability]
    else:
        available = distinct

    preferred: str | None = None
    preferred_score: int | None = None
    fallbacks: tuple[tuple[str, int], ...] = ()
    warning: str | None = None

    if not qualifying:
        warning = (
            f"coverage gap: no pool exercise matches region '{intent.target_region}' "
            f"for intent '{intent.intent_id}' (EKB/properties coverage gap — no fabrication)"
        )
    elif not distinct:
        warning = (
            f"distinctness gap: all {len(qualifying)} qualifying exercise(s) for intent "
            f"'{intent.intent_id}' already used by earlier slots (no duplicate prescription)"
        )
    elif not available:
        warning = (
            f"availability gap: {len(distinct)} distinct qualifying exercise(s) for intent "
            f"'{intent.intent_id}' but none in availability set"
        )
    else:
        preferred, preferred_score = available[0]
        used.add(preferred)
        fallbacks = tuple(available[1 : 1 + max_fallbacks])

    return SlotSelection(
        slot_id=intent.slot_id,
        intent_id=intent.intent_id,
        primary_zone=intent.primary_zone,
        target_region=intent.target_region,
        movement_pattern=intent.movement_pattern,
        priority_level=intent.priority_level,
        preferred_exercise=preferred,
        preferred_score=preferred_score,
        fallback_candidates=fallbacks,
        rationale=intent.rationale,
        warning=warning,
        slot_intent=intent,
    )


# ── Slot-intent composition (descriptors + priorities, deduped, re-slotted) ──


def _compose_slot_intents(
    descriptors: Sequence[MorphologyDescriptor],
    priorities: Sequence[tuple[str, int]],
) -> tuple[SlotIntent, ...]:
    """Merge morphology-descriptor-derived and priority-derived slot intents, dedup by intent_id
    (first occurrence wins — descriptor evidence before explicit priority), re-slotting to stable
    `slot1..slotN` ids in final order. Guarded/non-priority descriptors already produce nothing."""
    combined = list(build_slot_intents_from_descriptors(descriptors))
    combined.extend(build_slot_intents_from_priorities(priorities))
    seen: set[str] = set()
    out: list[SlotIntent] = []
    for intent in combined:
        if intent.intent_id in seen:
            continue
        seen.add(intent.intent_id)
        out.append(replace(intent, slot_id=f"slot{len(out) + 1}"))
    return tuple(out)


def _pool_fingerprint(pool: dict[str, dict]) -> str:
    """A stable digest of the candidate pool used — so proposals built from different pools
    (e.g. a custom `pool=` argument) never collide on the same id."""
    blob = json.dumps(pool, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def _fingerprint(
    source_descriptors: Sequence[str],
    priorities: Sequence[tuple[str, int]],
    availability: frozenset[str] | None,
    selections: Sequence[SlotSelection],
    pool_digest: str,
) -> str:
    """Stable content hash of the proposal (deterministic — hashlib only, no clock/random).

    A full content-address of the discriminating output: it folds in each slot's fallback
    candidates and warning and the pool digest, so two proposals that differ only in fallbacks,
    warnings, or the pool used receive different ids (never a collision)."""
    payload = {
        "engine_version": MORPHO_PROGRAM_GENERATOR_ENGINE_VERSION,
        "source_descriptors": sorted(source_descriptors),
        "priorities": [list(p) for p in priorities],
        "availability": sorted(availability) if availability is not None else None,
        "pool": pool_digest,
        "slots": [
            [
                s.slot_id,
                s.intent_id,
                s.preferred_exercise,
                s.preferred_score,
                [list(fc) for fc in s.fallback_candidates],
                s.warning,
            ]
            for s in selections
        ],
    }
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]
    return f"{_FINGERPRINT_PREFIX}-{digest}"


# ── Public API ───────────────────────────────────────────────────────────────


def generate_program(
    *,
    facts: MorphologyFacts | None = None,
    descriptors: Sequence[MorphologyDescriptor] | None = None,
    priorities: Sequence[tuple[str, int]] = (),
    availability: Iterable[str] | None = None,
    pool: dict[str, dict] | None = None,
    max_fallbacks: int = _DEFAULT_MAX_FALLBACKS,
) -> GeneratedProgram:
    """Generate a deterministic morphology-aware program proposal.

    Inputs (all optional but at least one intent source required to be non-empty):
    - `facts` — raw `MorphologyFacts`; converted to descriptors via `build_morphology_profile`.
      Ignored when `descriptors` is passed explicitly (lets tests inject guarded descriptors).
    - `descriptors` — explicit morphology descriptors (overrides `facts`).
    - `priorities` — `(priority_key, rank)` training priorities (e.g. calves), mapped by `slot_intent`.
    - `availability` — equipment families available; filters candidates and drives availability warnings.
    - `pool` — candidate `{name: props}`; defaults READ-ONLY to `load_exercise_properties()`.

    Output: a `GeneratedProgram` (pure in-memory data). Nothing is persisted; the candidate pool,
    catalog templates, `reference_split.json` and `exercise_properties.json` are never mutated.
    Guarded (`not_deductible`) descriptors produce no slot and are surfaced in `rejected_descriptors`."""
    if descriptors is not None:
        descs: tuple[MorphologyDescriptor, ...] = tuple(descriptors)
    elif facts is not None:
        descs = build_morphology_profile(facts)
    else:
        descs = ()

    priorities = tuple(priorities)
    availability_set = frozenset(availability) if availability is not None else None
    candidate_pool = load_exercise_properties() if pool is None else pool

    slot_intents = _compose_slot_intents(descs, priorities)
    used: set[str] = set()
    selections = tuple(
        _select_for_slot(intent, candidate_pool, availability_set, max_fallbacks, used)
        for intent in slot_intents
    )

    rejected = tuple(
        RejectedDescriptor(
            descriptor_id=getattr(d, "descriptor_id", "<unknown>"),
            reason="guarded/not_deductible — no slot generated",
        )
        for d in descs
        if getattr(d, "confidence", None) == "not_deductible"
    )

    warnings: list[str] = []
    if not slot_intents:
        warnings.append("empty proposal: no morphology descriptor or training priority produced a slot")
    warnings.extend(s.warning for s in selections if s.warning is not None)

    source_ids = tuple(getattr(d, "descriptor_id", "<unknown>") for d in descs)
    fingerprint = _fingerprint(
        source_ids, priorities, availability_set, selections, _pool_fingerprint(candidate_pool)
    )

    return GeneratedProgram(
        generated_program_id=fingerprint,
        engine_version=MORPHO_PROGRAM_GENERATOR_ENGINE_VERSION,
        source_descriptors=source_ids,
        priorities=priorities,
        availability=tuple(sorted(availability_set)) if availability_set is not None else None,
        selections=selections,
        rejected_descriptors=rejected,
        warnings=tuple(warnings),
    )
