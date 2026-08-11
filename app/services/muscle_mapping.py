"""Exercise-to-muscle-zone mapping for the physique dashboard.

Maps exercise names (substring match, case-insensitive) to
muscle zones for scoring. Two levels:
  - 11 detailed zones (analytical view)
  - 6 radar axes (macro view, aggregation of detailed zones)

Sb_32.2 adds an OPTIONAL DB-backed classification path
(``ExerciseMuscleMapping`` lookup by ``exercise_code``) with the historical
substring matcher as fallback. The public signature stays
backward-compatible: ``classify_exercise(name)`` is byte-identical to before
(it never touches the DB). Only callers that explicitly pass ``db=`` and
``exercise_code=`` opt into the relational lookup. Invariance vs the Sb_32.1
baseline is contrainte #1 — see ``tests/fixtures/classify_exercise_baseline.json``.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


ZONE_LABELS: dict[str, str] = {
    "pecs": "Pectoraux",
    "delt_lat": "Deltoïdes latéraux",
    "delt_post": "Deltoïdes postérieurs",
    "lats": "Dos largeur",
    "upper_back": "Dos épaisseur",
    "biceps": "Biceps",
    "triceps": "Triceps",
    "quads": "Quadriceps",
    "posterior": "Ischios / Fessiers",
    "calves": "Mollets",
    "core": "Core / Abdos",
}

ZONE_MEASUREMENT: dict[str, str | None] = {
    "pecs": "chest_cm",
    "delt_lat": None,
    "delt_post": None,
    "lats": None,
    "upper_back": None,
    "biceps": "arm_avg",
    "triceps": "arm_avg",
    "quads": "thigh_avg",
    "posterior": "thigh_avg",
    "calves": None,
    "core": "waist_cm",
}

ZONE_VOLUME_TARGET: dict[str, int] = {
    "pecs": 16,
    "delt_lat": 18,
    "delt_post": 10,
    "lats": 16,
    "upper_back": 16,
    "biceps": 10,
    "triceps": 10,
    "quads": 16,
    "posterior": 16,
    "calves": 10,
    "core": 10,
}

RADAR_AXES: dict[str, dict] = {
    "pecs": {"label": "Pectoraux", "zones": ["pecs"]},
    "shoulders": {"label": "Épaules", "zones": ["delt_lat", "delt_post"]},
    "back_width": {"label": "Dos largeur", "zones": ["lats"]},
    "back_thickness": {"label": "Dos épaisseur", "zones": ["upper_back"]},
    "arms": {"label": "Bras", "zones": ["biceps", "triceps"]},
    "lower": {"label": "Bas du corps", "zones": ["quads", "posterior", "calves"]},
}

RADAR_AXIS_ORDER = ["pecs", "shoulders", "back_width", "back_thickness", "arms", "lower"]

# Sb_ZONE_COUNT_TAXONOMY_FIX_01 — canonical detailed-zone → radar-axis projection.
#
# ``RADAR_AXES`` is the architecture's canonical macro/detailed relation: it is
# what ``muscle_scoring`` iterates to aggregate zone scores onto axes, and what
# ``tests/test_auren_body_zone_contract`` pins. The inverse below is DERIVED from
# it rather than hand-written, so the two directions cannot drift apart and no
# competing vocabulary is introduced.
#
# ``core`` is deliberately absent: it is one of the 11 detailed zones but has no
# radar axis (see ``test_auren_bodymap_master``: "core" in CANONICAL_MACROS and
# "core" not in RADAR_AXIS_ORDER). Projecting it would fabricate an axis, so it
# resolves to ``None`` and callers drop it — same for "unknown".
ZONE_TO_RADAR_AXIS: dict[str, str] = {
    zone: axis_key
    for axis_key in RADAR_AXIS_ORDER
    for zone in RADAR_AXES[axis_key]["zones"]
}


def radar_axis_for_zone(zone: str) -> str | None:
    """Project a detailed zone onto its radar axis, or ``None`` if it has none.

    ``None`` means "this zone legitimately has no macro axis" (``core``) or "not
    a known detailed zone" (``unknown``, or an already-macro key passed in by
    mistake). Callers must drop those rather than invent an axis for them.
    """
    return ZONE_TO_RADAR_AXIS.get(zone)

_EXERCISE_PATTERNS: list[tuple[list[str], str, list[str]]] = [
    (["chest press", "presse pectorale", "butterfly", "écarté pec",
      "développé couché", "développé incliné", "incline smith",
      "dips pec", "dips pectora", "pec deck", "cable cross",
      "cross-over"], "pecs", ["triceps"]),
    (["shoulder press", "presse épaule", "presse à épaule",
      "élévation latérale", "lateral raise", "élévations latérales",
      "tirage front", "upright row", "arnold press"], "delt_lat", []),
    (["face pull", "rear delt", "écarté arrière", "reverse fly",
      "oiseau", "arrière d'épaule", "y-raise", "y raise"], "delt_post", []),
    (["tirage vertical", "tirage poulie haute", "lat pulldown",
      "pulldown", "pullover", "straight-arm",
      "traction", "pull-up", "pullup", "pull up"], "lats", ["biceps"]),
    (["rowing", "seated row", "tirage horizontal", "t-bar",
      "shrug"], "upper_back", ["biceps"]),
    (["leg curl", "rdl", "romanian", "hip thrust",
      "deadlift", "good morning", "adduction",
      "back extension", "hip extension", "hyperextension",
      "glute bridge"], "posterior", []),
    (["curl", "biceps"], "biceps", []),
    (["triceps", "skull", "skull crusher",
      "extension overhead", "pushdown", "kickback",
      "extension poulie"], "triceps", []),
    (["hack squat", "leg press", "leg extension",
      "squat", "leg ext", "knee extension",
      "reverse nordic", "sissy"], "quads", []),
    (["mollet", "calf", "relevé", "relevés mollet"], "calves", []),
    (["abdo", "crunch", "roulette", "ab wheel", "pallof",
      "relevé de jambe", "relevé jambe", "hanging"], "core", []),
]


def _classify_exercise_by_patterns(name: str) -> tuple[str, list[str]]:
    """Historical substring classifier (unchanged behaviour).

    Case-insensitive substring matching against known patterns.
    Returns ("unknown", []) if no pattern matches. This is the fallback
    and the single source of truth captured in the Sb_32.1 baseline.
    """
    name_lower = name.lower()
    for keywords, primary, secondary in _EXERCISE_PATTERNS:
        if any(kw in name_lower for kw in keywords):
            return primary, secondary
    return "unknown", []


def _classify_exercise_by_lookup(
    db: Session, exercise_code: str
) -> tuple[str, list[str]] | None:
    """DB-backed classification via ``ExerciseMuscleMapping``.

    Returns (primary_zone, secondary_zones) if a primary mapping row exists
    for ``exercise_code``, else ``None`` (caller falls back to substring).
    Secondary zones are ordered by ``position`` then ``id`` to reproduce the
    historical ordering deterministically. Only active rows are considered.
    """
    # Local import: keep the module import-light and avoid a hard ORM
    # dependency for the name-only path.
    from app.models.exercise_muscle_mapping import ExerciseMuscleMapping

    rows = (
        db.query(ExerciseMuscleMapping)
        .filter(
            ExerciseMuscleMapping.exercise_code == exercise_code,
            ExerciseMuscleMapping.is_active.is_(True),
        )
        .order_by(
            ExerciseMuscleMapping.position.asc(),
            ExerciseMuscleMapping.id.asc(),
        )
        .all()
    )
    if not rows:
        return None

    primary: str | None = None
    secondary: list[str] = []
    for r in rows:
        if r.role == "primary" and primary is None:
            primary = r.body_zone_code
        elif r.role == "secondary":
            secondary.append(r.body_zone_code)
    if primary is None:
        # No primary row for this code → treat as no usable mapping.
        return None
    return primary, secondary


def classify_exercise(
    name: str,
    *,
    exercise_code: str | None = None,
    db: Session | None = None,
) -> tuple[str, list[str]]:
    """Classify an exercise into (primary_zone, secondary_zones).

    Backward-compatible: ``classify_exercise(name)`` behaves exactly as
    before (pure substring matching, no DB access).

    When BOTH ``db`` and ``exercise_code`` are provided, an optional
    DB-backed lookup (``ExerciseMuscleMapping``) is tried first; on a miss
    (or if either argument is absent) the call falls back to the historical
    substring matcher. Output format is always ``tuple[str, list[str]]``.
    """
    if db is not None and exercise_code is not None:
        looked_up = _classify_exercise_by_lookup(db, exercise_code)
        if looked_up is not None:
            return looked_up
    return _classify_exercise_by_patterns(name)
