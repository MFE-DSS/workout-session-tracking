"""Pure SlotIntent layer (Sb_PROGRAM_SLOT_INTENT_01, spec `Sx_MORPHO_PROGRAM_01` §7-§8).

The first morphology→programming bridge. A `SlotIntent` describes **what an exercise slot must
accomplish** (target zone, movement pattern, intent, priority, acceptable/forbidden
substitutions) — entirely over the **existing** taxonomy (`exercise_properties.json` /
`muscle_mapping` zones + `substitution.PatternMotor`). It is PURE and ADDITIVE:

- **It never mutates** a catalog template, a substitution, a session, or any file/DB.
- **It reuses `substitution.compute_proximity` READ-ONLY** to score a candidate against a slot
  (import + call). It does **not** modify `substitution.py`; N1/N2/N3 runtime behaviour and the
  "different pattern ⇒ never N1/N2" guarantee are untouched — the slot only biases the *choice
  before* substitution, never the substitution engine itself.
- **No generator, no program generation, no Martin program** here (later builds).

Zones are carried at two granularities, both from existing structures:
- `primary_zone` — the DETAILED zone (`muscle_mapping` 11-zone taxonomy: delt_lat, pecs, …).
- `target_region` — the MACRO region used by `exercise_properties.json` (`muscle_mapping`
  RADAR_AXES: shoulders, pecs, lower, …), derived from `primary_zone` for proximity matching.
"""
from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass

from app.services.muscle_mapping import RADAR_AXES
from app.services.substitution import VALID_PATTERN_MOTORS, compute_proximity

SLOT_INTENT_ENGINE_VERSION = 1

# Detailed zone (muscle_mapping) -> macro region (exercise_properties zone_primary),
# derived read-only from the existing RADAR_AXES — never redefined.
DETAILED_TO_REGION: dict[str, str] = {
    zone: axis for axis, spec in RADAR_AXES.items() for zone in spec["zones"]
}

# Detailed zones that carry a curated exercise_properties `muscle_group` (sparse taxonomy).
_ZONE_MUSCLE_GROUP: dict[str, str] = {"quads": "quadriceps", "posterior": "hamstrings"}


@dataclass(frozen=True)
class SlotIntent:
    """A slot's intended target + substitution guardrails, over existing taxonomy."""

    slot_id: str
    intent_id: str
    primary_zone: str
    target_region: str
    secondary_zones: tuple[str, ...]
    movement_pattern: str
    chain: str
    priority_level: int
    preferred_exercise_name: str | None
    acceptable_substitution_families: tuple[str, ...]
    forbidden_substitution_patterns: tuple[str, ...]
    rationale: str
    source_descriptors: tuple[str, ...] = ()
    engine_version: int = SLOT_INTENT_ENGINE_VERSION

    def to_dict(self) -> dict:
        return asdict(self)


# ── Intent registry (8 canonical intents, spec §7 examples) ──────────────────
# Each value: (primary_zone, secondary_zones, movement_pattern, chain,
#              forbidden_substitution_patterns, acceptable_substitution_families, rationale)
_INTENT_SPECS: dict[str, dict] = {
    "upper_chest_primary_press": {
        "primary_zone": "pecs", "secondary_zones": ("triceps",),
        "movement_pattern": "push_horizontal", "chain": "compound",
        "forbidden": ("push_vertical",),
        "families": ("barbell", "dumbbell", "machine", "smith"),
        "rationale": "Presse orientée haut des pectoraux (horizontale/inclinée) — jamais une presse épaules.",
    },
    "upper_back_depth_row": {
        "primary_zone": "upper_back", "secondary_zones": ("delt_post", "biceps"),
        "movement_pattern": "pull_horizontal", "chain": "compound",
        "forbidden": ("pull_vertical",),
        "families": ("machine", "cable", "barbell", "dumbbell"),
        "rationale": "Rowing épaisseur du haut du dos (horizontal) — pas un tirage largeur.",
    },
    "quad_minimum_effective_dose": {
        "primary_zone": "quads", "secondary_zones": ("posterior", "calves"),
        "movement_pattern": "squat", "chain": "compound",
        "forbidden": (),
        "families": ("machine", "smith", "barbell"),
        "rationale": "Dose minimale efficace quadriceps — maintien, ne pas sur-spécialiser.",
    },
    "posterior_chain_hinge": {
        "primary_zone": "posterior", "secondary_zones": ("upper_back", "calves"),
        "movement_pattern": "hinge", "chain": "compound",
        "forbidden": ("isolation_lower",),
        "families": ("barbell", "dumbbell", "machine"),
        "rationale": "Hinge chaîne postérieure — leg curl (isolation) seulement en dernier recours.",
    },
    "lateral_delt_priority": {
        "primary_zone": "delt_lat", "secondary_zones": (),
        "movement_pattern": "isolation_upper", "chain": "isolation",
        "forbidden": ("push_vertical", "push_horizontal"),
        "families": ("cable", "machine", "dumbbell"),
        "rationale": "Priorité deltoïde latéral — isolation stricte, pas une presse composée.",
    },
    "rear_delt_upper_back_accessory": {
        "primary_zone": "delt_post", "secondary_zones": ("upper_back",),
        "movement_pattern": "isolation_upper", "chain": "isolation",
        "forbidden": ("pull_vertical",),
        "families": ("cable", "machine", "dumbbell"),
        "rationale": "Accessoire delts postérieurs / haut du dos — isolation, pas un tirage largeur.",
    },
    "calves_gastrocnemius_priority": {
        "primary_zone": "calves", "secondary_zones": (),
        "movement_pattern": "isolation_lower", "chain": "isolation",
        "forbidden": (),
        "families": ("machine", "smith", "dumbbell"),
        "rationale": "Mollets gastrocnémien — jambe tendue, étirement complet.",
    },
    "calves_soleus_priority": {
        "primary_zone": "calves", "secondary_zones": (),
        "movement_pattern": "isolation_lower", "chain": "isolation",
        "forbidden": (),
        "families": ("machine",),
        "rationale": "Mollets soléaire — genoux fléchis, étirement complet.",
    },
}

# Training-priority vocabulary (spec §6) -> ordered intent_ids.
PRIORITY_TO_INTENTS: dict[str, tuple[str, ...]] = {
    "lateral_delts": ("lateral_delt_priority",),
    "upper_chest": ("upper_chest_primary_press",),
    "rear_delts_upper_back": ("rear_delt_upper_back_accessory",),
    "calves": ("calves_gastrocnemius_priority", "calves_soleus_priority"),
    "back": ("upper_back_depth_row",),
    "quads_maintenance": ("quad_minimum_effective_dose",),
    "posterior_chain": ("posterior_chain_hinge",),
}

# Morphology priority-candidate descriptor_id (Sb_MORPHO_PROFILE_01) -> intent_id.
DESCRIPTOR_TO_INTENT: dict[str, str] = {
    "lateral_delts_priority_candidate": "lateral_delt_priority",
    "upper_chest_priority_candidate": "upper_chest_primary_press",
    "rear_delts_upper_back_priority_candidate": "rear_delt_upper_back_accessory",
}

KNOWN_INTENT_IDS: frozenset[str] = frozenset(_INTENT_SPECS)

# Module-load invariants: every intent uses valid, existing taxonomy values.
# Raise (not assert) — matches substitution.py's load-time validation and survives `python -O`.
for _iid, _spec in _INTENT_SPECS.items():
    if _spec["movement_pattern"] not in VALID_PATTERN_MOTORS:
        raise ValueError(f"slot_intent: intent {_iid!r} has invalid movement_pattern")
    if any(p not in VALID_PATTERN_MOTORS for p in _spec["forbidden"]):
        raise ValueError(f"slot_intent: intent {_iid!r} has an invalid forbidden pattern")
    if _spec["primary_zone"] not in DETAILED_TO_REGION:
        raise ValueError(f"slot_intent: intent {_iid!r} has an unknown primary_zone")


# ── Builders ─────────────────────────────────────────────────────────────


def build_slot_intent(
    intent_id: str,
    *,
    slot_id: str,
    priority_level: int,
    preferred_exercise_name: str | None = None,
    source_descriptors: Iterable[str] = (),
) -> SlotIntent | None:
    """Build one `SlotIntent` from a registered intent_id. Unknown intent_id → ``None``."""
    spec = _INTENT_SPECS.get(intent_id)
    if spec is None:
        return None
    return SlotIntent(
        slot_id=slot_id,
        intent_id=intent_id,
        primary_zone=spec["primary_zone"],
        target_region=DETAILED_TO_REGION[spec["primary_zone"]],
        secondary_zones=tuple(spec["secondary_zones"]),
        movement_pattern=spec["movement_pattern"],
        chain=spec["chain"],
        priority_level=priority_level,
        preferred_exercise_name=preferred_exercise_name,
        acceptable_substitution_families=tuple(spec["families"]),
        forbidden_substitution_patterns=tuple(spec["forbidden"]),
        rationale=spec["rationale"],
        source_descriptors=tuple(source_descriptors),
    )


def build_slot_intents_from_priorities(
    priorities: Sequence[tuple[str, int]],
) -> tuple[SlotIntent, ...]:
    """Map (priority_key, rank) pairs to slot intents. Unknown priority keys are skipped
    (no fabrication). Slot ids are `slot{n}` in emission order."""
    out: list[SlotIntent] = []
    for priority_key, level in priorities:
        for intent_id in PRIORITY_TO_INTENTS.get(priority_key, ()):
            si = build_slot_intent(
                intent_id, slot_id=f"slot{len(out) + 1}", priority_level=level,
                source_descriptors=(f"priority:{priority_key}",),
            )
            if si is not None:
                out.append(si)
    return tuple(out)


def build_slot_intents_from_descriptors(descriptors: Iterable) -> tuple[SlotIntent, ...]:
    """Map morphology priority-candidate descriptors (Sb_MORPHO_PROFILE_01) to slot intents.

    A descriptor produces a slot intent ONLY when it is a mapped priority candidate AND its
    confidence is not `not_deductible` (guarded). Facts, other inferences, and guarded
    descriptors produce NO slot intent (§2/§3)."""
    out: list[SlotIntent] = []
    for d in descriptors:
        intent_id = DESCRIPTOR_TO_INTENT.get(getattr(d, "descriptor_id", None))
        if intent_id is None or getattr(d, "confidence", None) == "not_deductible":
            continue
        si = build_slot_intent(
            intent_id, slot_id=f"slot{len(out) + 1}", priority_level=len(out) + 1,
            source_descriptors=tuple(getattr(d, "evidence", ())) or (d.descriptor_id,),
        )
        if si is not None:
            out.append(si)
    return tuple(out)


# ── Read-only reuse of the substitution proximity contract ──────────────────


def target_props(intent: SlotIntent) -> dict:
    """The `exercise_properties`-shaped props a candidate is scored against — MACRO region,
    pattern, chain, and (sparse) muscle_group. Consumed by `compute_proximity` READ-ONLY."""
    props = {
        "zone_primary": intent.target_region,
        "pattern_motor": intent.movement_pattern,
        "chain": intent.chain,
    }
    mg = _ZONE_MUSCLE_GROUP.get(intent.primary_zone)
    if mg is not None:
        props["muscle_group"] = mg
    return props


def score_candidate(intent: SlotIntent, candidate_props: dict) -> int:
    """Proximity score (0-105) of a candidate's `exercise_properties` against the slot's target,
    via the EXISTING `substitution.compute_proximity` (read-only; substitution engine unchanged)."""
    return compute_proximity(target_props(intent), candidate_props)


def candidate_pattern_forbidden(intent: SlotIntent, candidate_props: dict) -> bool:
    """True if a candidate's `pattern_motor` is on the slot's forbidden list (would break the
    intent). A pure guard used at the SLOT-choice stage — never applied to runtime N1/N2/N3."""
    return candidate_props.get("pattern_motor") in intent.forbidden_substitution_patterns
