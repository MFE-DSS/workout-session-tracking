"""PRIVATE DOGFOOD FIXTURE — Martin's morphology facts (Sb_MORPHO_PROFILE_01).

⚠️ PRIVATE / TEST-ONLY. This is the operator-provided morphology sample for Martin,
dated 2026-08-09. It exists **only** as a private test fixture / documented dogfood sample:
- it is NOT global template data,
- it is NOT exposed in any runtime UI or `/library`,
- it must never be rendered to another user.

Values are kept as approximations ("≈") and modelled as bounded facts/observations — no
femur/insertion/posture/medical claim (spec §13 hard constraints).
"""
from __future__ import annotations

from app.services.morphology_profile import BodyObservation, MorphologyFacts

MARTIN_SOURCE = "operator morphology report 2026-08-09 (private dogfood)"


def martin_morphology_facts() -> MorphologyFacts:
    """Martin's facts as a pure `MorphologyFacts` input (private dogfood only)."""
    return MorphologyFacts(
        height_cm=179.0,
        wingspan_cm=183.0,
        ape_index_cm=4.0,   # ≈ +4 cm, not extreme
        waist_cm=83.0,
        chest_cm=100.0,
        thigh_cm=55.5,      # ≈ 55–56
        calf_cm=34.5,       # ≈ 34–35
        observations=(
            BodyObservation("clavicular_width", "favorable", MARTIN_SOURCE),
            BodyObservation("quads", "relatively_strong", MARTIN_SOURCE),
            BodyObservation("calves", "relative_lag", MARTIN_SOURCE),
            BodyObservation("lats", "acceptable", MARTIN_SOURCE),
        ),
        focus_candidates=(
            "lateral_delts",
            "upper_chest",
            "rear_delts_upper_back",
            "calves",
        ),
        source=MARTIN_SOURCE,
        notes="longiligne-athletic; avoid over-specializing quadriceps.",
    )
