"""Exercise-to-muscle-zone mapping for the physique dashboard.

Maps exercise names (substring match, case-insensitive) to
muscle zones for scoring. Two levels:
  - 11 detailed zones (analytical view)
  - 6 radar axes (macro view, aggregation of detailed zones)
"""
from __future__ import annotations


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

_EXERCISE_PATTERNS: list[tuple[list[str], str, list[str]]] = [
    (["chest press", "presse pectorale", "butterfly", "écarté pec",
      "développé couché", "développé incliné", "incline smith",
      "dips pec", "dips pectora", "pec deck", "cable cross",
      "cross-over"], "pecs", ["triceps"]),
    (["shoulder press", "presse épaule", "presse à épaule",
      "élévation latérale", "lateral raise", "élévations latérales",
      "tirage front", "upright row"], "delt_lat", []),
    (["face pull", "rear delt", "écarté arrière", "reverse fly",
      "oiseau", "arrière d'épaule"], "delt_post", []),
    (["tirage vertical", "tirage poulie haute", "lat pulldown",
      "pulldown", "pullover câble", "pullover cable",
      "straight-arm", "traction"], "lats", ["biceps"]),
    (["rowing", "seated row", "tirage horizontal", "t-bar",
      "shrug"], "upper_back", ["biceps"]),
    (["leg curl", "rdl", "romanian", "hip thrust",
      "deadlift", "good morning", "adduction"], "posterior", []),
    (["curl", "biceps"], "biceps", []),
    (["triceps", "skull", "skull crusher",
      "extension overhead", "pushdown", "kickback",
      "extension poulie"], "triceps", []),
    (["hack squat", "leg press", "leg extension",
      "squat", "leg ext"], "quads", []),
    (["mollet", "calf", "relevé", "relevés mollet"], "calves", []),
    (["abdo", "crunch", "roulette", "ab wheel", "pallof",
      "relevé de jambe", "relevé jambe", "hanging"], "core", []),
]


def classify_exercise(name: str) -> tuple[str, list[str]]:
    """Classify an exercise name into (primary_zone, secondary_zones).

    Uses case-insensitive substring matching against known patterns.
    Returns ("unknown", []) if no pattern matches.
    """
    name_lower = name.lower()
    for keywords, primary, secondary in _EXERCISE_PATTERNS:
        if any(kw in name_lower for kw in keywords):
            return primary, secondary
    return "unknown", []
