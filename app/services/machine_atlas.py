"""Machine atlas loader — in-memory index over data/machine_atlas.json.

The atlas groups gym machines into families (pecs-press, back-vertical, ...)
and exposes lookups by machine slug, family slug, or by reverse-resolution
from a template exercise (via machine_slug / machine_family fields set in
reference_split.json).

The atlas is loaded once on first access and cached. Lookups are O(1).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_DATA_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "machine_atlas.json"

_cache: dict[str, Any] | None = None


def _load() -> dict[str, Any]:
    global _cache
    if _cache is not None:
        return _cache

    with open(_DATA_FILE, encoding="utf-8") as f:
        raw = json.load(f)

    families = raw.get("families", [])
    machines_by_slug: dict[str, dict[str, Any]] = {}
    family_by_slug: dict[str, dict[str, Any]] = {}
    family_by_machine: dict[str, dict[str, Any]] = {}

    for family in families:
        fslug = family.get("slug")
        if not fslug:
            continue
        family_by_slug[fslug] = family
        for machine in family.get("machines", []):
            mslug = machine.get("slug")
            if not mslug:
                continue
            machines_by_slug[mslug] = machine
            family_by_machine[mslug] = family

    _cache = {
        "version": raw.get("version"),
        "title": raw.get("title"),
        "families": families,
        "machines_by_slug": machines_by_slug,
        "family_by_slug": family_by_slug,
        "family_by_machine": family_by_machine,
    }
    return _cache


def reset_cache() -> None:
    """Clear the in-memory cache (test helper)."""
    global _cache
    _cache = None


def atlas_version() -> str | None:
    return _load().get("version")


def all_families() -> list[dict[str, Any]]:
    """Return the list of families (ordered as in the JSON)."""
    return list(_load()["families"])


def get_family(family_slug: str | None) -> dict[str, Any] | None:
    if not family_slug:
        return None
    return _load()["family_by_slug"].get(family_slug)


def get_machine(machine_slug: str | None) -> dict[str, Any] | None:
    if not machine_slug:
        return None
    return _load()["machines_by_slug"].get(machine_slug)


def family_of_machine(machine_slug: str | None) -> dict[str, Any] | None:
    if not machine_slug:
        return None
    return _load()["family_by_machine"].get(machine_slug)


def get_for_template_exercise(template_exercise) -> dict[str, Any] | None:
    """Resolve atlas entry for a TemplateExercise.

    Prefers ``machine_slug`` (specific machine) and falls back to
    ``machine_family`` (family only, when the exercise is not tied to a
    specific machine, e.g. free weight movements).

    Returns a dict ``{"machine": ..., "family": ...}`` where ``machine`` may
    be None if only a family is linked; or None if no link.
    """
    if template_exercise is None:
        return None

    machine_slug = getattr(template_exercise, "machine_slug", None)
    family_slug = getattr(template_exercise, "machine_family", None)

    machine = get_machine(machine_slug)
    family = get_family(family_slug) or family_of_machine(machine_slug)

    if machine is None and family is None:
        return None

    return {"machine": machine, "family": family}
