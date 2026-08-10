"""Pure mapper: `GeneratedProgram` → Custom Program draft tree (Sb_MORPHO_DOGFOOD_01).

Final build of the `Sx_MORPHO_PROGRAM_01` queue. It bridges the deterministic morphology
generator (`morpho_program_generator`, Sb_MORPHO_PROGRAM_GENERATOR_01) to the EXISTING Custom
Program lifecycle, by emitting the very payload `user_program_drafts.replace_draft_tree` already
consumes. It is PURE and ADDITIVE — same input ⇒ same output, no I/O, no DB, no ORM:

- **It changes no lifecycle semantics.** The caller drives the *existing* services
  (`create_draft` → `replace_draft_tree` → `validate_draft` → `compute_quality_preview` →
  `publish_user_program` → launch). Nothing here publishes, validates, or writes.
- **It mutates nothing**: not the generator, not the catalog, not `reference_split.json`, not the
  EKB. It only reads a candidate's denormalised fields via the existing
  `user_program_exercise_catalog.enrich`.
- **No Martin-specific data lives here.** Titles/priorities/availability belong to the caller
  (for the dogfood, a private test-only fixture).

Prescription source (spec: "sets/reps from the existing morphotype program or deterministic
defaults"): the morpho engine prescribes **no volume** — a `SlotSelection` carries an exercise and
an intent, never sets/reps. So each intent carries the volume of its counterpart in the merged
« Full Body — Morphotype Priority » catalog program (E1-E8), declared below and pinned by a test
against `reference_split.json`. An unknown intent falls back to the repo-wide default `3x 8-12`.

Slots with **no** `preferred_exercise` (coverage/availability/distinctness gap) are **dropped**,
never faked — `UserProgramExercise.exercise_name` is NOT NULL, and inventing a name would betray
the generator's no-fabrication contract. Dropped slots are reported by `unmappable_slots()`.
"""
from __future__ import annotations

from app.services.morpho_program_generator import GeneratedProgram, SlotSelection
from app.services.user_program_exercise_catalog import enrich

MORPHO_DRAFT_MAPPER_VERSION = 1

# Traceability prefix, mirroring `user_program_generator`'s `generated:reference_split:{slug}`.
SOURCE_REASON_PREFIX = "generated:morpho"

# Mirrors `user_program_drafts.MAX_EXERCISES_PER_SESSION` (read-only constant, not imported to
# keep this module free of any service dependency).
MAX_EXERCISES_PER_SESSION = 10

DEFAULT_SESSION_NAME = "Full Body — Morphotype Priority"
DEFAULT_SESSION_KIND = "strength"

# intent_id -> (sets, min_reps, max_reps), taken from the corresponding exercise of the merged
# « Full Body — Morphotype Priority » catalog program (E1-E8). Pinned against
# `data/reference_split.json` by `test_prescriptions_match_the_catalog_program`.
_INTENT_PRESCRIPTION: dict[str, tuple[int, int, int]] = {
    "upper_chest_primary_press": (3, 6, 10),        # E1
    "upper_back_depth_row": (3, 8, 12),             # E2
    "quad_minimum_effective_dose": (2, 6, 10),      # E3 — maintenance dose, deliberately low
    "posterior_chain_hinge": (2, 6, 10),            # E4
    "lateral_delt_priority": (4, 12, 20),           # E5 — priority n°1
    "rear_delt_upper_back_accessory": (3, 12, 20),  # E6
    "calves_gastrocnemius_priority": (4, 8, 12),    # E7
    "calves_soleus_priority": (3, 12, 20),          # E8
}
_DEFAULT_PRESCRIPTION = (3, 8, 12)


def _prescription(intent_id: str) -> tuple[int, int, int]:
    return _INTENT_PRESCRIPTION.get(intent_id, _DEFAULT_PRESCRIPTION)


def mapped_selections(program: GeneratedProgram) -> tuple[SlotSelection, ...]:
    """The selections that can become an exercise: those with a preferred exercise, in slot order."""
    return tuple(s for s in program.selections if s.preferred_exercise)


def unmappable_slots(program: GeneratedProgram) -> tuple[tuple[str, str], ...]:
    """`(slot_id, reason)` for every slot dropped because it has no exercise — never silent."""
    return tuple(
        (s.slot_id, s.warning or "no preferred exercise")
        for s in program.selections
        if not s.preferred_exercise
    )


def _exercise_payload(selection: SlotSelection, position: int) -> dict:
    sets, min_reps, max_reps = _prescription(selection.intent_id)
    name = selection.preferred_exercise
    payload = {
        # Denormalised columns from the EXISTING catalog projector (exact canonical name match,
        # `{}` otherwise) — same convention as the manual picker.
        **enrich(name),
        "position": position,
        "exercise_name": name,
        "set_scheme": f"{sets}x {min_reps}-{max_reps}",
        "notes": selection.rationale,
        "source_reason": f"{SOURCE_REASON_PREFIX}:{selection.intent_id}"[:255],
        "rep_targets": [
            {"min_reps": min_reps, "max_reps": max_reps} for _ in range(sets)
        ],
    }
    return payload


def generated_program_to_draft_tree(
    program: GeneratedProgram,
    *,
    session_name: str = DEFAULT_SESSION_NAME,
    session_focus: str = "",
    session_notes: str | None = None,
) -> list[dict]:
    """`GeneratedProgram` → the `replace_draft_tree` payload (pure; nothing is persisted).

    Emits the **smallest valid structure**: a single session holding the generated exercises in
    slot order. It only splits into further sessions if the generator ever produced more slots
    than a session may hold (`MAX_EXERCISES_PER_SESSION`), which keeps the payload writable
    instead of failing at the service boundary. Slots without an exercise are dropped (see
    `unmappable_slots`); an empty result is returned as an empty list — the caller decides,
    and `validate_draft` will refuse it rather than publishing something hollow."""
    selections = mapped_selections(program)
    if not selections:
        return []

    chunks = [
        selections[i : i + MAX_EXERCISES_PER_SESSION]
        for i in range(0, len(selections), MAX_EXERCISES_PER_SESSION)
    ]
    multi = len(chunks) > 1

    tree: list[dict] = []
    for index, chunk in enumerate(chunks, start=1):
        name = f"{session_name} ({index}/{len(chunks)})" if multi else session_name
        tree.append(
            {
                "position": index,
                "name": name[:128],
                "kind": DEFAULT_SESSION_KIND,
                "focus": session_focus,
                "notes": session_notes,
                "exercises": [
                    _exercise_payload(selection, position)
                    for position, selection in enumerate(chunk, start=1)
                ],
            }
        )
    return tree
