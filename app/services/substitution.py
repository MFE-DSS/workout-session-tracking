"""Exercise substitution helpers.

Substitution is catalogue-driven: each TemplateExercise carries a JSON
list of explicit substitute names (N1 — curated). Sb_22a extends this
with two derived levels driven by ``data/exercise_properties.json`` and
``data/cross_pattern_substitutions.json``:

* **N1 — Équivalence stricte** : explicit curated list (existing behaviour).
* **N2 — Fallback très proche** : same ``pattern_motor`` and proximity ≥ 50.
* **N3 — Fallback zone-only** : same ``zone_primary`` but different
  ``pattern_motor``, OR cross-pattern bridge entry.

Hard contract (spec Sx_22a v1.1 §C.1, §C.3) — a suggestion whose
``pattern_motor`` differs from the origin can never appear at N1/N2.
``compute_suggestions`` validates this and raises ``ValueError`` if any
mismatch is detected, which protects against accidental zone-only
suggestions being promoted.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Literal

# ---------------------------------------------------------------------------
# Pattern moteur — enum verrouillé Sx_22a §C.2bis
# ---------------------------------------------------------------------------

PatternMotor = Literal[
    "push_horizontal",
    "push_vertical",
    "pull_horizontal",
    "pull_vertical",
    "squat",
    "hinge",
    "lunge",
    "isolation_upper",
    "isolation_lower",
    "core",
    "cardio",
]

VALID_PATTERN_MOTORS: frozenset[str] = frozenset(
    [
        "push_horizontal",
        "push_vertical",
        "pull_horizontal",
        "pull_vertical",
        "squat",
        "hinge",
        "lunge",
        "isolation_upper",
        "isolation_lower",
        "core",
        "cardio",
    ]
)

# Suggestion level — N1 strict equivalence, N2 close fallback, N3 zone-only.
SuggestionLevel = Literal["N1", "N2", "N3"]

# Badge labels — single source of truth (Sx_22a v1.1 §C.1).
BADGE_N1 = "Équivalent"
BADGE_N2 = "Proche"
BADGE_N3 = "Élargi"

# Hard limits on derived suggestions per level (avoid drawer overload).
MAX_N2 = 5
MAX_N3 = 5
PROXIMITY_THRESHOLD_N2 = 50


@dataclass(frozen=True)
class Suggestion:
    """One alternative offered in the drawer.

    ``level`` is N1/N2/N3 as defined in spec Sx_22a v1.1 §C.1.
    ``badge`` is the short label shown to the user.
    ``rationale`` is a one-line UI hint (cross-pattern intent, same machine, etc.).
    """

    name: str
    level: SuggestionLevel
    badge: str
    rationale: str | None = None


# ---------------------------------------------------------------------------
# Existing helpers (kept untouched — historic contract preserved)
# ---------------------------------------------------------------------------


def actual_exercise_name(session_exercise) -> str:
    """Return the exercise name that was actually performed."""
    return session_exercise.substituted_name or session_exercise.exercise_name_snapshot


def get_substitutes(template_exercise) -> list[str]:
    """Return the curated (N1) substitute names, or empty list."""
    if template_exercise is None:
        return []
    raw = getattr(template_exercise, "substitutes_json", None)
    if not raw:
        return []
    try:
        result = json.loads(raw)
        return result if isinstance(result, list) else []
    except (json.JSONDecodeError, TypeError):
        return []


def can_substitute(session_exercise) -> bool:
    """True if no work set has been completed yet."""
    for sl in session_exercise.set_logs:
        if sl.kind == "work" and sl.completed:
            return False
    return True


# ---------------------------------------------------------------------------
# Sb_22a — heuristic suggestions
# ---------------------------------------------------------------------------

_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


@lru_cache(maxsize=1)
def load_exercise_properties() -> dict[str, dict]:
    """Read ``data/exercise_properties.json`` (cached).

    The registry covers exclusively the Sb_22a MVP families. Absence
    from this map is expected for exercises outside scope and is NOT
    an error — it just means heuristic N2/N3 are unavailable for them.
    """
    path = _DATA_DIR / "exercise_properties.json"
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    props = raw.get("exercises", {})
    # Validate every entry's pattern_motor against the locked enum (§C.2bis).
    for name, entry in props.items():
        pm = entry.get("pattern_motor")
        if pm not in VALID_PATTERN_MOTORS:
            raise ValueError(
                f"exercise_properties.json: '{name}' has invalid pattern_motor "
                f"'{pm}'. Allowed: {sorted(VALID_PATTERN_MOTORS)}"
            )
    return props


@lru_cache(maxsize=1)
def load_cross_pattern_bridges() -> list[dict]:
    """Read ``data/cross_pattern_substitutions.json`` (cached)."""
    path = _DATA_DIR / "cross_pattern_substitutions.json"
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw.get("bridges", [])


def compute_proximity(props_a: dict, props_b: dict) -> int:
    """Score 0-100 entre deux exercices (spec §C.3).

    Composantes :
    * +50 zone_primary identique
    * +20 pattern_motor identique
    * +15 equipment_family identique
    * +10 chain identique (compound/isolation)
    """
    score = 0
    if props_a.get("zone_primary") == props_b.get("zone_primary"):
        score += 50
    if props_a.get("pattern_motor") == props_b.get("pattern_motor"):
        score += 20
    if props_a.get("equipment_family") == props_b.get("equipment_family"):
        score += 15
    if props_a.get("chain") == props_b.get("chain"):
        score += 10
    return score


def _classify_suggestion(
    origin_props: dict,
    candidate_props: dict,
) -> tuple[SuggestionLevel, str, str | None]:
    """Return (level, badge, rationale) for a candidate against an origin.

    Spec §C.3 v1.1 garde-fou : si ``pattern_motor`` diffère, le résultat
    est forcément N3. Aucune promotion possible.
    """
    same_pattern = origin_props.get("pattern_motor") == candidate_props.get(
        "pattern_motor"
    )
    same_zone = origin_props.get("zone_primary") == candidate_props.get(
        "zone_primary"
    )
    same_equipment = origin_props.get("equipment_family") == candidate_props.get(
        "equipment_family"
    )
    same_chain = origin_props.get("chain") == candidate_props.get("chain")

    score = compute_proximity(origin_props, candidate_props)

    # N1 strict equivalence : 4 dimensions identiques (curated OR perfect match)
    if same_pattern and same_zone and same_equipment and same_chain:
        return "N1", BADGE_N1, None
    # N2 close fallback : pattern identique obligatoire, proximity ≥ seuil
    if same_pattern and score >= PROXIMITY_THRESHOLD_N2:
        equip_bit = "même équipement" if same_equipment else "autre équipement"
        chain_bit = "" if same_chain else ", chaîne différente"
        return "N2", BADGE_N2, f"même pattern · {equip_bit}{chain_bit}"
    # N3 zone-only : pattern différent OR proximity < seuil
    return "N3", BADGE_N3, None


def _empty_suggestions() -> dict[str, list[Suggestion]]:
    return {"N1": [], "N2": [], "N3": []}


def _add_curated_suggestion(
    sub_name: str,
    origin_props: dict | None,
    props: dict[str, dict],
    out: dict[str, list[Suggestion]],
) -> None:
    """Classify one curated substitute into N1 or N3 (cross-pattern demotion).

    Pure helper — `out` is mutated in place.
    """
    if origin_props is None or sub_name not in props:
        out["N1"].append(
            Suggestion(name=sub_name, level="N1", badge=BADGE_N1, rationale=None)
        )
        return
    level, badge, rationale = _classify_suggestion(origin_props, props[sub_name])
    if level == "N3":
        # Curated cross-pattern legacy (e.g. catalog v13 C2 fix). Demote
        # silently to N3 instead of raising — preserves the prévu/réalisé
        # contract. catalog_pattern_qa.py flags these for migration to
        # cross_pattern_substitutions.json.
        out["N3"].append(
            Suggestion(
                name=sub_name,
                level="N3",
                badge=BADGE_N3,
                rationale="via curation (cross-pattern)",
            )
        )
    else:
        out["N1"].append(
            Suggestion(name=sub_name, level=level, badge=badge, rationale=rationale)
        )


def _collect_n2_candidates(
    origin_name: str,
    origin_props: dict,
    props: dict[str, dict],
    seen: set[str],
) -> list[tuple[int, Suggestion]]:
    """Build the N2 candidate list — same pattern, proximity ≥ threshold."""
    candidates: list[tuple[int, Suggestion]] = []
    origin_pattern = origin_props.get("pattern_motor")
    for name, cand_props in props.items():
        if name in seen:
            continue
        if cand_props.get("pattern_motor") != origin_pattern:
            continue
        score = compute_proximity(origin_props, cand_props)
        if score < PROXIMITY_THRESHOLD_N2:
            continue
        level, badge, rationale = _classify_suggestion(origin_props, cand_props)
        # Defense-in-depth invariant: same pattern can never land in N3.
        if level == "N3":
            raise ValueError(
                f"N2 candidate '{name}' for '{origin_name}' demoted to N3 "
                "despite same pattern_motor — classifier inconsistency."
            )
        candidates.append((score, Suggestion(name=name, level=level, badge=badge, rationale=rationale)))
    candidates.sort(key=lambda t: -t[0])
    return candidates


def _collect_n3_zone_candidates(
    origin_props: dict,
    props: dict[str, dict],
    seen: set[str],
) -> list[tuple[int, Suggestion]]:
    """Build the N3 zone-only candidate list — same zone, different pattern."""
    candidates: list[tuple[int, Suggestion]] = []
    origin_pattern = origin_props.get("pattern_motor")
    origin_zone = origin_props.get("zone_primary")
    for name, cand_props in props.items():
        if name in seen:
            continue
        if cand_props.get("zone_primary") != origin_zone:
            continue
        if cand_props.get("pattern_motor") == origin_pattern:
            continue  # belongs to N2 (rejected by score); excluded from N3
        score = compute_proximity(origin_props, cand_props)
        candidates.append(
            (
                score,
                Suggestion(
                    name=name,
                    level="N3",
                    badge=BADGE_N3,
                    rationale="même zone · autre pattern",
                ),
            )
        )
    return candidates


def _collect_bridge_candidates(
    origin_name: str,
    origin_pattern: str | None,
    bridges: list[dict],
    seen: set[str],
) -> list[tuple[int, Suggestion]]:
    """Collect N3 suggestions from cross-pattern bridges (rowing↔tirage vertical)."""
    candidates: list[tuple[int, Suggestion]] = []
    for bridge in bridges:
        if bridge.get("from_pattern") != origin_pattern:
            continue
        if origin_name not in bridge.get("exercises_from", []):
            continue
        intent = bridge.get("intent", "")
        for target_name in bridge.get("exercises_to", []):
            if target_name in seen:
                continue
            seen.add(target_name)
            candidates.append(
                (
                    -1,
                    Suggestion(
                        name=target_name,
                        level="N3",
                        badge=BADGE_N3,
                        rationale=f"intention proche : {intent}",
                    ),
                )
            )
    return candidates


def compute_suggestions(template_exercise) -> dict[str, list[Suggestion]]:
    """Build the N1/N2/N3 suggestion sets for one template_exercise.

    Returns a dict ``{"N1": [...], "N2": [...], "N3": [...]}`` ordered
    by descending proximity inside each level.

    The function NEVER mutates ``template_exercise`` nor any session
    record. It only reads catalog and data/* registries — preserving
    the spec §D.bis "prévu/réalisé" contract.

    Hard guarantee (spec §C.3 v1.1) : every N2 suggestion's pattern_motor
    matches the origin's. A mismatch raises ``ValueError``. Curated
    cross-pattern entries are demoted to N3 instead of raising.
    """
    if template_exercise is None:
        return _empty_suggestions()

    origin_name = template_exercise.name
    props = load_exercise_properties()
    bridges = load_cross_pattern_bridges()
    origin_props = props.get(origin_name)

    out = _empty_suggestions()
    seen: set[str] = {origin_name}

    # --- N1 — curated explicit list (existing behaviour) -----------------
    for sub_name in get_substitutes(template_exercise):
        if sub_name in seen:
            continue
        seen.add(sub_name)
        _add_curated_suggestion(sub_name, origin_props, props, out)

    # Without origin properties, only N1 (curated) is available.
    if origin_props is None:
        return out

    # --- N2 — derived from registry, same pattern_motor ------------------
    for _, sug in _collect_n2_candidates(origin_name, origin_props, props, seen)[:MAX_N2]:
        out[sug.level].append(sug)
        seen.add(sug.name)

    # --- N3 — zone-only fallback + cross-pattern bridges -----------------
    origin_pattern = origin_props.get("pattern_motor")
    n3_pool = _collect_n3_zone_candidates(origin_props, props, seen)
    n3_pool.extend(_collect_bridge_candidates(origin_name, origin_pattern, bridges, seen))
    n3_pool.sort(key=lambda t: -t[0])
    for _, sug in n3_pool[:MAX_N3]:
        out["N3"].append(sug)
        seen.add(sug.name)

    return out


def all_suggestions_flat(template_exercise) -> list[Suggestion]:
    """Convenience flat list N1+N2+N3 in display order."""
    grouped = compute_suggestions(template_exercise)
    return grouped["N1"] + grouped["N2"] + grouped["N3"]
