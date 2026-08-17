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


def get_machine_by_name(name: str | None) -> dict[str, Any] | None:
    """Sb_22a.next2 — resolve an atlas machine by display name or alias.

    Walks every family and matches ``machine.name`` then ``machine.aliases``
    (case-insensitive). Used when only a substituted exercise NAME is
    available (no ``machine_slug``), so that the execution cues panel
    follows the actually performed exercise — not the prescribed one.

    Returns the first match or ``None``.
    """
    if not name:
        return None
    needle = name.strip().lower()
    cache = _load()
    for machine in cache["machines_by_slug"].values():
        if machine.get("name", "").strip().lower() == needle:
            return machine
        for alias in machine.get("aliases", []) or []:
            if alias.strip().lower() == needle:
                return machine
    return None


def get_for_session_exercise(session_exercise) -> dict[str, Any] | None:
    """Sb_22a.next2 — resolve atlas entry for a SessionExercise, following
    the actually performed exercise (the *réalisé*).

    Priority order:
      1. If ``substituted_name`` is set, try to find the matching machine
         in the atlas by name/aliases. If found, return it (the cues panel
         will follow the substitute).
      2. Otherwise (or if the substitute isn't in the atlas), fall back to
         the prescribed ``template_exercise``.

    The prescribed exercise stays available elsewhere (substitute-badge in
    the card already shows "Substitué : X (prescrit : Y)") — this function
    only controls which execution-cue payload the rendering layer consumes.
    """
    if session_exercise is None:
        return None
    sub_name = getattr(session_exercise, "substituted_name", None)
    if sub_name:
        machine = get_machine_by_name(sub_name)
        if machine is not None:
            family = family_of_machine(machine.get("slug"))
            return {"machine": machine, "family": family}

    resolved = get_for_template_exercise(
        getattr(session_exercise, "template_exercise", None)
    )
    if resolved and resolved.get("machine"):
        return resolved

    # Sb_ATLAS_COVERAGE_01 — dernier recours : le NOM figé de l'exercice.
    #
    # `machine_slug` / `machine_family` sont nuls pour une partie du
    # catalogue, et les remplir passerait par `reference_split.json`, dont le
    # seed est verrouillé sur la version du payload. Bumper cette version
    # déclenche un wipe des lignes SYSTEM : mesuré sur copie jetable, le lien
    # `template_exercise` des séances passées tombe de 7/7 à 0/7 et leurs cues
    # de 4/7 à 0/7, `ondelete="SET NULL"` faisant son travail. Couvrir trois
    # exercices en retirant les cues de tout l'historique serait un très
    # mauvais échange.
    #
    # Le snapshot de nom, lui, est justement conçu pour survivre au reseed. Le
    # résoudre ici rend la couverture INDÉPENDANTE du seed et rétroactive :
    # une séance déjà enregistrée gagne son cue sans qu'aucune ligne ne bouge.
    #
    # Correspondance exacte nom/alias, insensible à la casse — aucun
    # rapprochement approximatif : un cue qui ne correspond pas à la machine
    # serait pire que le silence.
    machine = get_machine_by_name(
        getattr(session_exercise, "exercise_name_snapshot", None)
    )
    if machine is not None:
        return {"machine": machine, "family": family_of_machine(machine.get("slug"))}
    return resolved


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
