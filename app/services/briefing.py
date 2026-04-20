"""Pre-session briefing (Sb_11a).

Builds two compact payloads consumed by ``session_detail.html`` :

- **chip** — one-liner inserted in the ``<summary>`` of every *future*
  card. Carries the compact rep scheme and the last-time chiffré.
- **peek** — a small block rendered at the bottom of the *active* card
  preparing the next exercise: scheme + last-time + up to 2 execution
  cues from the atlas.

No new DB data, no new derivation. All inputs come from:
- ``TemplateExercise.rep_targets``
- ``last_time_by_exercise_code`` (``_summarise_prior``)
- ``machine_atlas.get_for_template_exercise``
- ``session.template.kind`` for strength / cardio arbitration

No duplication of the delta block, the common-mistakes list, or the
muscle_sensation — those stay on the active card by design.
"""
from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Format helpers
# ---------------------------------------------------------------------------


def _fmt_weight(w: float | None) -> str:
    if w is None:
        return ""
    if w == int(w):
        return str(int(w))
    return f"{w:g}"


def _compact_scheme(template_exercise) -> str | None:
    """Render a compact rep scheme (e.g. ``3×8-12``, ``4×6-10 RP``).

    Returns None if the slot has no rep_targets — used by the caller to
    decide whether to omit the chip entirely.
    """
    if template_exercise is None:
        return None
    rts = list(getattr(template_exercise, "rep_targets", None) or [])
    if not rts:
        return None

    count = len(rts)
    mins = {rt.min_reps for rt in rts}
    maxs = {rt.max_reps for rt in rts}
    techs = {rt.technique for rt in rts if getattr(rt, "technique", None)}

    if len(mins) == 1 and len(maxs) == 1:
        lo = next(iter(mins))
        hi = next(iter(maxs))
        scheme = f"{count}×{lo}" if lo == hi else f"{count}×{lo}-{hi}"
    else:
        scheme = f"{count}×var"

    if techs:
        scheme += " " + "/".join(sorted(techs))
    return scheme


def _last_time_chip(prior_summary: dict | None) -> str:
    """Return ``"dernière fois 60 kg × 10"`` or ``"première fois"``."""
    if not prior_summary:
        return "première fois"
    first = prior_summary.get("first_set")
    if not first:
        return "première fois"
    w = first.get("weight_kg")
    r = first.get("reps")
    if w is None or r is None:
        return "première fois"
    return f"dernière fois {_fmt_weight(w)} kg × {r}"


# ---------------------------------------------------------------------------
# Public builders
# ---------------------------------------------------------------------------


def build_chip(
    template_exercise,
    prior_summary: dict | None,
    template_kind: str | None = None,
) -> dict[str, Any] | None:
    """Build the chip payload for a future card.

    Returns ``None`` if the slot has no rep_targets — the template uses
    that signal to omit the chip. Cardio templates without exercise
    slots never reach this function (no card is rendered).
    """
    scheme = _compact_scheme(template_exercise)
    if scheme is None:
        return None
    return {
        "scheme": scheme,
        "last_time": _last_time_chip(prior_summary),
        "kind": template_kind or "strength",
    }


def build_peek(
    next_se,
    prior_summary: dict | None,
    atlas_entry: dict | None,
    template_kind: str | None = None,
) -> dict[str, Any] | None:
    """Build the peek payload for the bottom of the active card.

    Parameters mirror what ``session_detail`` already computes per
    exercise: ``prior_summary`` is ``last_time.get(next_code)``, and
    ``atlas_entry`` is ``atlas_data.get(next_se.id)``.

    Returns ``None`` when there is no next exercise (active card is the
    last of the session) or when the next slot has no rep scheme to
    compose from.
    """
    if next_se is None:
        return None
    te = getattr(next_se, "template_exercise", None)
    scheme = _compact_scheme(te)
    if scheme is None:
        return None

    cues: list[str] = []
    if atlas_entry and atlas_entry.get("machine"):
        cues = list(atlas_entry["machine"].get("execution_cues") or [])[:2]

    display_name = (
        getattr(next_se, "substituted_name", None)
        or getattr(next_se, "exercise_name_snapshot", "")
    )

    return {
        "code": getattr(next_se, "exercise_code_snapshot", ""),
        "name": display_name,
        "scheme": scheme,
        "last_time": _last_time_chip(prior_summary),
        "cues": cues,
        "kind": template_kind or "strength",
    }
