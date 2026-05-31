"""Sb_24.2 — Implicit signal detection (Sx_24 §D).

Pure deterministic classifier over the work-set trajectory of a single
SessionExercise. No DB access, no side effects — given a list of work
sets, returns one of 5 labels (or None).

Hard contracts inherited from Sx_24 spec:
* Only WORK sets contribute (warmup ignored at the caller).
* Requires ≥ MIN_WORK_SETS = 3 work sets — else returns None (signal
  too poor to classify).
* Sets are ordered by ``set_index`` ascending.
* `weight_kg is None` is treated as 0 (bodyweight exercises rely on
  reps alone — uniform constant-weight detection still works).
* `reps is None` is treated as 0.
* The function is **pure** — same input always yields the same output.
  This is what makes the persist-once-at-completion contract
  (Sx_24 §C, §D.2) safe : recomputing later would yield the same value,
  so the cached label in the DB is authoritative.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence


# ---------------------------------------------------------------------------
# Enum — verrouillé, exposé publiquement
# ---------------------------------------------------------------------------

class ImplicitLabel(str, Enum):
    """Five qualitative trajectory labels (Sx_24 §D.1).

    Inherits ``str`` so it serializes naturally to the BD column
    ``session_exercises.implicit_label`` (VARCHAR(32)).
    """

    RESERVE_PROBABLE = "reserve_probable"
    TRAJECTOIRE_COHERENTE = "trajectoire_coherente"
    PYRAMIDAL_ASCENDANT = "pyramidal_ascendant"
    PYRAMIDAL_DESCENDANT = "pyramidal_descendant"
    INCOHERENT = "incoherent"


# Contribution to the V2 quality score per label (Sx_24 §F.2).
# Centralised here so the formula in services/quality_score.py
# (Sb_24.5) is data-driven, not magic numbers in two files.
LABEL_SCORE_CONTRIBUTION: dict[ImplicitLabel, int] = {
    ImplicitLabel.RESERVE_PROBABLE: 30,
    ImplicitLabel.INCOHERENT: 50,
    ImplicitLabel.PYRAMIDAL_ASCENDANT: 70,
    ImplicitLabel.PYRAMIDAL_DESCENDANT: 75,
    ImplicitLabel.TRAJECTOIRE_COHERENTE: 90,
}

MIN_WORK_SETS = 3


# ---------------------------------------------------------------------------
# Input shape — accept anything that walks the duck
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class WorkSetPoint:
    """A minimal projection of one work SetLog. Caller is responsible for
    filtering ``kind == "work"`` and ordering by ``set_index``."""
    weight_kg: float | None
    reps: int | None


def _coerce(point) -> WorkSetPoint:
    """Accept either a WorkSetPoint, a SetLog ORM row, or a (w, r) tuple."""
    if isinstance(point, WorkSetPoint):
        return point
    if isinstance(point, tuple) and len(point) == 2:
        return WorkSetPoint(weight_kg=point[0], reps=point[1])
    # ORM-shaped duck
    return WorkSetPoint(
        weight_kg=getattr(point, "weight_kg", None),
        reps=getattr(point, "reps", None),
    )


# ---------------------------------------------------------------------------
# Helpers — strictly increasing / decreasing / equal-or-direction
# ---------------------------------------------------------------------------

def _all_equal_or_increasing(seq: Sequence[float]) -> bool:
    return all(seq[i + 1] >= seq[i] for i in range(len(seq) - 1))


def _strictly_increasing(seq: Sequence[float]) -> bool:
    return all(seq[i + 1] > seq[i] for i in range(len(seq) - 1))


def _strictly_decreasing(seq: Sequence[float]) -> bool:
    return all(seq[i + 1] < seq[i] for i in range(len(seq) - 1))


def _all_equal(seq: Sequence[float]) -> bool:
    return all(v == seq[0] for v in seq)


# ---------------------------------------------------------------------------
# Public API — the classifier
# ---------------------------------------------------------------------------

def detect_intra_set_label(work_sets) -> ImplicitLabel | None:
    """Classify the trajectory of a single exercise's work sets.

    Spec Sx_24 §D.1 — V1.1 intra-exercise only.

    Returns ``None`` if:
      * fewer than ``MIN_WORK_SETS`` (= 3) work sets, or
      * pattern doesn't match any of the 5 labels (defensive fallthrough,
        in practice INCOHERENT catches everything not classified above)

    Returns one of :class:`ImplicitLabel` otherwise.
    """
    points = [_coerce(p) for p in work_sets]
    if len(points) < MIN_WORK_SETS:
        return None

    # Treat None as 0 so bodyweight (weight=None) becomes a constant
    # weight trajectory, leaving only reps to discriminate.
    ws = [float(p.weight_kg) if p.weight_kg is not None else 0.0 for p in points]
    rs = [int(p.reps) if p.reps is not None else 0 for p in points]

    # Precompute booleans once — each label rule reads them.
    w_eq = _all_equal(ws)
    r_eq = _all_equal(rs)
    w_eq_or_inc = _all_equal_or_increasing(ws)
    r_eq_or_inc = _all_equal_or_increasing(rs)
    w_strict_inc = _strictly_increasing(ws)
    w_strict_dec = _strictly_decreasing(ws)
    r_dec = rs[-1] < rs[0]
    r_inc = rs[-1] > rs[0]

    # ----- Rule order = specificity. Most specific patterns are checked
    # FIRST so a more informative label wins over a broader one. The spec
    # §D.1 lists conditions but does not impose an order — the natural
    # disambiguation is by specificity. -----

    # 1. Trajectoire cohérente — weight constant + reps strictly down.
    if w_eq and r_dec:
        return ImplicitLabel.TRAJECTOIRE_COHERENTE

    # 2. Pyramidal ascendant — weight strictly up, reps constant or down.
    #    Checked before reserve_probable because (w_strict_inc, r_eq)
    #    also matches (w_eq_or_inc, r_eq_or_inc), and the pyramid label
    #    is the more informative one.
    if w_strict_inc and (r_eq or r_dec):
        return ImplicitLabel.PYRAMIDAL_ASCENDANT

    # 3. Pyramidal descendant — weight strictly down, reps constant or up.
    if w_strict_dec and (r_eq or r_inc):
        return ImplicitLabel.PYRAMIDAL_DESCENDANT

    # 4. Réserve probable — both axes equal or increasing simultaneously.
    #    Per spec §D.1 verbatim : "(w constant OU croissant) ET (r constant
    #    OU croissant) sur tous les sets". A pure flat 3×10×60kg satisfies
    #    this and IS reserve_probable by design (contribution 30) — the
    #    intent : effort didn't drop where it should have.
    if w_eq_or_inc and r_eq_or_inc:
        return ImplicitLabel.RESERVE_PROBABLE

    # 5. Tout le reste — oscillation, mix non classable.
    return ImplicitLabel.INCOHERENT


__all__ = [
    "ImplicitLabel",
    "LABEL_SCORE_CONTRIBUTION",
    "MIN_WORK_SETS",
    "WorkSetPoint",
    "detect_intra_set_label",
]
