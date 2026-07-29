"""Deterministic draft generation (Sb_CUSTOM_PROGRAM_WIZARD_03).

A PURE, deterministic builder: given a split style and a session count, it
assembles a full **editable** program tree by selecting curated session
templates from `data/reference_split.json` (read-only). No LLM, no randomness,
no DB, no ORM, no scoring, no seed — same input always yields the same payload.

The output is a plain payload directly consumable by `replace_draft_tree` (the
canonical tree-write path, `app/services/user_program_drafts.py`); WIZARD_02
stays the editor for correction after generation. The generator never "owns"
the deep rules (quotas 7/10, sequential positions, editable statuses) — those
stay in `replace_draft_tree`; this module only shapes a proposal.

Deliberate NON-goals (spec 01 §11, build-gate order):
- NO EKB dependency — `reference_split.json` is self-contained (names, rep
  targets, set schemes are curated there), so WIZARD_03 needs no EKB read and
  does NOT open EKB_04 or seed the DB;
- NO `WorkoutTemplate` publication, NO `session_builder` touch;
- NO `UserProgramQualityReview` write, NO automatic scoring;
- NO migration.
"""
from __future__ import annotations

import json
from functools import lru_cache

from app.config import BASE_DIR

_REFERENCE_SPLIT_PATH = BASE_DIR / "data" / "reference_split.json"

# Upper bound on generated sessions. `replace_draft_tree` (spec 04 §9) is the
# final authority (MAX_SESSIONS_PER_PROGRAM = 7); this mirrors it so the form
# and the generated proposal never exceed the quota.
MAX_SESSIONS = 7

# Deterministic split → ordered cycle of reference-template slugs. Only curated
# STRENGTH templates that actually exist in reference_split.json (verified at
# the WIZARD_03 preflight — cardio/empty templates are deliberately excluded so
# every generated session has at least one exercise and stays validatable).
_SPLIT_CYCLES: dict[str, list[str]] = {
    "ppl": ["push-a", "pull-a", "legs-a", "push-b", "pull-b", "legs-b"],
    "upper_lower": [
        "upper-pecs-delts",
        "lower-quad-bias",
        "upper-back-arms",
        "lower-posterior-bias",
    ],
}

# Human labels for the SSR form (never anatomy authored by code).
SPLIT_LABELS: dict[str, str] = {
    "ppl": "Push / Pull / Legs",
    "upper_lower": "Upper / Lower",
}


class ProgramGenerationError(Exception):
    """Readable error for invalid generation input (unknown split, sessions<1)."""


@lru_cache(maxsize=1)
def _load_templates() -> dict[str, dict]:
    """Load `reference_split.json` once, indexed by slug. Read-only: this module
    never writes the file and never seeds the DB from it."""
    data = json.loads(_REFERENCE_SPLIT_PATH.read_text(encoding="utf-8"))
    return {t["slug"]: t for t in data.get("templates", [])}


def _template_to_session(template: dict) -> dict:
    """Project a reference template into a `replace_draft_tree` session payload.

    Only fields the `UserProgram` tree persists are copied — the curated name,
    set scheme and rep targets. Machine metadata and substitutes stay in the
    reference (no EKB lookup, no invented mapping). `source_reason` traces every
    exercise back to its reference template, so the proposal is never opaque.
    """
    slug = template["slug"]
    return {
        "name": template["name"],
        "kind": template.get("kind", "strength"),
        "focus": template.get("focus", ""),
        "notes": template.get("suggested_label"),
        "exercises": [
            {
                "exercise_name": exercise["name"],
                "set_scheme": exercise["set_scheme"],
                "notes": exercise.get("notes"),
                "source_reason": f"generated:reference_split:{slug}",
                "rep_targets": [
                    {"min_reps": rt["min_reps"], "max_reps": rt["max_reps"]}
                    for rt in exercise.get("rep_targets", [])
                ],
            }
            for exercise in template.get("exercises", [])
        ],
    }


def generate_program_tree(
    split: str, sessions: int, duration: str | None = None
) -> list[dict]:
    """Deterministically assemble a program tree from reference templates.

    Pure: the same ``(split, sessions)`` always returns the same payload. No DB,
    no randomness, no scoring, no write. ``duration`` is accepted for forward
    compatibility but does NOT change the V1 output (documented). Contract:

    - unknown ``split`` -> ``ProgramGenerationError``;
    - ``sessions < 1`` -> ``ProgramGenerationError``;
    - ``sessions`` is otherwise CAPPED to ``min(sessions, MAX_SESSIONS, len(cycle))``
      (a request beyond the curated cycle simply returns the whole cycle);
    - session positions are ``1..N``, exercise positions ``1..M`` per session;
    - the output is directly consumable by ``replace_draft_tree``.
    """
    cycle = _SPLIT_CYCLES.get(split)
    if cycle is None:
        raise ProgramGenerationError(
            f"Style de split inconnu « {split} » — choix : "
            f"{', '.join(sorted(_SPLIT_CYCLES))}."
        )
    if sessions < 1:
        raise ProgramGenerationError("Le nombre de séances doit être au moins 1.")
    count = min(sessions, MAX_SESSIONS, len(cycle))
    templates = _load_templates()
    payload: list[dict] = []
    for position, slug in enumerate(cycle[:count], start=1):
        session = _template_to_session(templates[slug])
        session["position"] = position
        for exercise_position, exercise in enumerate(session["exercises"], start=1):
            exercise["position"] = exercise_position
        payload.append(session)
    return payload
