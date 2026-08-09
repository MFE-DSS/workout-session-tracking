"""PRIVATE DOGFOOD FIXTURE — Martin's DERIVED morphology-aware program (Sb_MARTIN_PROGRAM_01).

⚠️ PRIVATE / TEST-ONLY. This derives Martin's concrete program **proposal** from his private
morphology fixture (`martin_morphology`, Sb_MORPHO_PROFILE_01) via the delivered deterministic
generator (`morpho_program_generator`, Sb_MORPHO_PROGRAM_GENERATOR_01). It exists **only** as a
private test fixture / documented dogfood sample:
- it is NOT global template data, NOT a catalog program, NOT a Custom Program,
- it is NOT persisted (no DB), NOT exposed in any runtime UI or `/library`,
- it must never be rendered to another user.

This is the 4ᵗʰ build of the `Sx_MORPHO_PROGRAM_01` queue: **derive** Martin's program (pure,
in-memory). Feeding it through the real Custom-Program cycle is the **next** build
(`Sb_MORPHO_DOGFOOD_01`) — NOT here. Martin-specific choices (his training priorities, his gym's
availability) live ONLY in this private fixture, never in the global generator logic.
"""
from __future__ import annotations

from martin_morphology import MARTIN_SOURCE, martin_morphology_facts

from app.services.morpho_program_generator import GeneratedProgram, generate_program

MARTIN_PROGRAM_SOURCE = "operator dogfood program derivation 2026-08-09 (private)"

# Martin's declared training priorities (private): his 4 morphotype-focus priorities (ranked from
# his morphology focus candidates) + 3 maintenance priorities for the rest of the body. This is
# operator-specific data — it belongs in this private fixture, NEVER in the global generator.
_MARTIN_MORPHOTYPE_PRIORITIES: tuple[tuple[str, int], ...] = (
    ("lateral_delts", 1),
    ("upper_chest", 2),
    ("rear_delts_upper_back", 3),
    ("calves", 4),
)
_MARTIN_MAINTENANCE_PRIORITIES: tuple[tuple[str, int], ...] = (
    ("back", 5),
    ("quads_maintenance", 6),
    ("posterior_chain", 7),
)

# Martin's gym (Fitness Park) equipment families — availability filters the generation, never the
# substitution engine (spec §9). Broad commercial-gym coverage.
_MARTIN_AVAILABILITY: frozenset[str] = frozenset(
    {"machine", "cable", "dumbbell", "barbell", "smith", "bodyweight"}
)


def martin_training_priorities() -> tuple[tuple[str, int], ...]:
    """Martin's ranked training priorities (private): morphotype focus + maintenance."""
    return _MARTIN_MORPHOTYPE_PRIORITIES + _MARTIN_MAINTENANCE_PRIORITIES


def martin_availability() -> frozenset[str]:
    """Martin's gym equipment availability (private)."""
    return _MARTIN_AVAILABILITY


def martin_program() -> GeneratedProgram:
    """Martin's derived program proposal (pure, in-memory, deterministic).

    Composes his private morphology facts → descriptors → slot intents, plus his declared
    training priorities, filtered by his gym availability, through the delivered generator.
    Nothing is persisted; the catalog/properties are never mutated."""
    return generate_program(
        facts=martin_morphology_facts(),
        priorities=martin_training_priorities(),
        availability=martin_availability(),
    )


# Re-export the morphology source tag so callers can assert this stays private/test-only.
__all__ = [
    "MARTIN_PROGRAM_SOURCE",
    "MARTIN_SOURCE",
    "martin_availability",
    "martin_program",
    "martin_training_priorities",
]
