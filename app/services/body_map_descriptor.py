"""Body-map descriptor service — Sb_32.3.

Turns an exercise classification (primary + secondary body zones) into a
**stable, JSON-serializable descriptor** meant to be consumed later by the
Worked Area UI, the coach report, body intelligence and analytics. This
sprint only provides the contract + logic; **no consumer is wired**.

Design (Sb_32.3 brainstorming, Option A) : PURE service, no persistence, no
model, no migration. It reuses the Sx_32 classification helpers so the zones
it reports are exactly those proven by the Sb_32.1 baseline / Sb_32.2 lookup
— invariance is contrainte #1.

Honest resolution path : ``classify_exercise`` itself does not expose which
path produced a result, and it is read-only for this sprint. Rather than
guess, this service re-derives the path by calling the SAME private helpers
in the SAME order as ``classify_exercise`` :

    1. ``_classify_exercise_by_lookup(db, exercise_code)``  → ``db_lookup``
    2. ``_classify_exercise_by_patterns(name)``             → ``substring_fallback``
       (or ``unknown`` when the substring matcher returns ``("unknown", [])``)

so the descriptor's zones are guaranteed identical to ``classify_exercise``
while ``resolution_path`` never lies.

No anatomy is invented : unknown yields an explicit "À qualifier" descriptor,
no fine-grained muscle, no stabilizer, no medical claim.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from app.services.muscle_mapping import (
    ZONE_LABELS,
    _classify_exercise_by_lookup,
    _classify_exercise_by_patterns,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

# Label shown for a zone that could not be resolved (never a medical term).
UNKNOWN_LABEL = "À qualifier"


def _resolve_zones(
    name: str,
    exercise_code: str | None,
    db: Session | None,
) -> tuple[str, list[str], str]:
    """Return (primary_zone, secondary_zones, resolution_path).

    Mirrors ``classify_exercise`` exactly (same helpers, same order) so the
    zones match the baseline, while reporting which path produced them.
    """
    if db is not None and exercise_code is not None:
        looked_up = _classify_exercise_by_lookup(db, exercise_code)
        if looked_up is not None:
            primary, secondary = looked_up
            return primary, list(secondary), "db_lookup"

    primary, secondary = _classify_exercise_by_patterns(name)
    if primary == "unknown":
        return "unknown", [], "unknown"
    return primary, list(secondary), "substring_fallback"


def _label_for(code: str, db: Session | None) -> str:
    """Resolve a zone label: BodyZone.label from DB when available, else the
    in-code ``ZONE_LABELS`` fallback, else the raw code (never empty)."""
    if db is not None:
        # Local import keeps the module import-light for the name-only path.
        from app.models.body_zone import BodyZone

        row = (
            db.query(BodyZone.label)
            .filter(BodyZone.code == code)
            .first()
        )
        if row is not None and row[0]:
            return row[0]
    return ZONE_LABELS.get(code, code)


def build_body_map_descriptor(
    name: str,
    *,
    exercise_code: str | None = None,
    db: Session | None = None,
) -> dict:
    """Build a stable, JSON-serializable body-map descriptor for an exercise.

    Backward-compatible with a name-only call. When ``db`` and
    ``exercise_code`` are provided, the DB-backed mapping is used (with the
    historical substring matcher as fallback), exactly like
    ``classify_exercise``.

    Shape (all fields always present)::

        {
          "status": "mapped" | "unknown",
          "primary_zone": "pecs" | ... | "unknown",
          "primary_label": "Pectoraux" | "À qualifier",
          "secondary_zones": ["triceps", ...],
          "secondary_labels": ["Triceps", ...],
          "zones": [{"code", "label", "role"}, ...],   # primary first
          "source": "db_lookup" | "substring_fallback" | "unknown",
          "resolution_path": "db_lookup" | "substring_fallback" | "unknown",
          "is_qualified": bool,
          "needs_qualification": bool,
        }
    """
    primary, secondary, resolution_path = _resolve_zones(name, exercise_code, db)

    if primary == "unknown":
        return {
            "status": "unknown",
            "primary_zone": "unknown",
            "primary_label": UNKNOWN_LABEL,
            "secondary_zones": [],
            "secondary_labels": [],
            "zones": [],
            "source": "unknown",
            "resolution_path": "unknown",
            "is_qualified": False,
            "needs_qualification": True,
        }

    # De-duplicate secondary zones, preserving order, and never let a
    # secondary duplicate the primary.
    seen = {primary}
    deduped_secondary: list[str] = []
    for code in secondary:
        if code not in seen:
            seen.add(code)
            deduped_secondary.append(code)

    primary_label = _label_for(primary, db)
    secondary_labels = [_label_for(code, db) for code in deduped_secondary]

    zones = [{"code": primary, "label": primary_label, "role": "primary"}]
    for code, label in zip(deduped_secondary, secondary_labels, strict=True):
        zones.append({"code": code, "label": label, "role": "secondary"})

    return {
        "status": "mapped",
        "primary_zone": primary,
        "primary_label": primary_label,
        "secondary_zones": deduped_secondary,
        "secondary_labels": secondary_labels,
        "zones": zones,
        "source": resolution_path,
        "resolution_path": resolution_path,
        "is_qualified": True,
        "needs_qualification": False,
    }
