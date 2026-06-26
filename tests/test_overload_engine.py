"""Sb_30.1 — Tests unitaires du Progressive Overload Engine V1.

Couvre les 5 états, les incréments par catégorie, le deload, le versioning,
la limite de 3 raisons, le déterminisme et l'interdiction de langage
autoritaire (Sx_30 §6/§9/§10).

Aucun accès DB. Aucune dépendance sur les services métier core
(recommendation/quality_score/implicit_signal/coach_*/body_*/substitution).
"""

from __future__ import annotations

import pytest

from app.services.overload_engine import (
    OVERLOAD_ENGINE_VERSION,
    HistoricalSetSignal,
    OverloadHint,
    OverloadInput,
    compute_overload_hint,
)

# ───────── helpers ─────────


def _h(weight: float, reps: int, q: float | None = 0.8, fatigue: bool = False):
    return HistoricalSetSignal(
        weight_kg=weight, reps=reps, quality_score=q, fatigue_signal=fatigue
    )


def _inp(category: str, tmin: int, tmax: int, *history: HistoricalSetSignal):
    return OverloadInput(
        exercise_category=category,
        target_min=tmin,
        target_max=tmax,
        history=tuple(history),
    )


# ───────── unknown ─────────


def test_unknown_when_history_empty():
    hint = compute_overload_hint(_inp("compound", 6, 10))
    assert hint.state == "unknown"
    assert hint.target_weight_kg is None
    assert hint.target_reps_min is None
    assert hint.target_reps_max is None
    assert hint.engine_version == OVERLOAD_ENGINE_VERSION
    assert "historique insuffisant" in hint.reasons


# ───────── progress ─────────


def test_progress_two_sessions_at_top_range_quality_ok():
    hint = compute_overload_hint(
        _inp(
            "compound",
            6,
            10,
            _h(100.0, 10, 0.85),
            _h(100.0, 10, 0.80),
        )
    )
    assert hint.state == "progress"
    assert hint.target_weight_kg == 102.5  # 100 + 2.5
    assert hint.target_reps_min == 6
    assert hint.target_reps_max == 10


def test_progress_two_sessions_above_top_range_also_triggers():
    hint = compute_overload_hint(
        _inp(
            "compound",
            6,
            10,
            _h(100.0, 12, 0.9),
            _h(100.0, 11, 0.85),
        )
    )
    assert hint.state == "progress"


def test_progress_blocked_by_fatigue_signal_falls_back():
    hint = compute_overload_hint(
        _inp(
            "compound",
            6,
            10,
            _h(100.0, 10, 0.85, fatigue=True),
            _h(100.0, 10, 0.85),
        )
    )
    # Fatigue tue le progress mais ne déclenche pas seul deload : on
    # retombe sur consolidate (reps == target_max, dans la range).
    assert hint.state == "consolidate"


def test_progress_blocked_by_quality_below_threshold():
    hint = compute_overload_hint(
        _inp(
            "compound",
            6,
            10,
            _h(100.0, 10, 0.74),
            _h(100.0, 10, 0.74),
        )
    )
    # Quality 0.74 < 0.75 mais > 0.55 → ni progress ni deload → consolidate.
    assert hint.state == "consolidate"


def test_progress_with_no_quality_score_still_triggers():
    """quality_score=None → on n'exige pas le seuil ; trigger top + no fatigue suffit."""
    hint = compute_overload_hint(
        _inp(
            "compound",
            6,
            10,
            _h(100.0, 10, None),
            _h(100.0, 10, None),
        )
    )
    assert hint.state == "progress"


# ───────── consolidate ─────────


def test_consolidate_in_range_but_not_top():
    hint = compute_overload_hint(
        _inp(
            "compound",
            6,
            10,
            _h(100.0, 8, 0.8),
            _h(100.0, 8, 0.8),
        )
    )
    assert hint.state == "consolidate"
    assert hint.target_weight_kg == 100.0
    assert hint.target_reps_min == 6
    assert hint.target_reps_max == 10


# ───────── top-range ─────────


def test_top_range_when_last_under_min():
    hint = compute_overload_hint(
        _inp(
            "compound",
            6,
            10,
            _h(100.0, 4, 0.8),
        )
    )
    assert hint.state == "top-range"
    assert hint.target_weight_kg == 100.0  # mêmes kg
    assert hint.target_reps_min == 6
    assert hint.target_reps_max == 10


# ───────── deload ─────────


def test_deload_when_quality_score_below_055():
    hint = compute_overload_hint(
        _inp(
            "compound",
            6,
            10,
            _h(100.0, 10, 0.50),
            _h(100.0, 10, 0.50),
        )
    )
    assert hint.state == "deload"
    # -10% → 90.0, floor à 2.5 = 90.0
    assert hint.target_weight_kg == 90.0
    assert hint.target_reps_min == 6
    assert hint.target_reps_max == 6  # viser target_min


def test_deload_when_two_consecutive_reps_declines():
    hint = compute_overload_hint(
        _inp(
            "compound",
            6,
            10,
            _h(100.0, 6, 0.8),
            _h(100.0, 7, 0.8),
            _h(100.0, 9, 0.8),
        )
    )
    assert hint.state == "deload"


def test_deload_priority_over_progress():
    """Même si les reps sont au top range, un quality_score effondré
    force le deload (priorité spec §9)."""
    hint = compute_overload_hint(
        _inp(
            "compound",
            6,
            10,
            _h(100.0, 10, 0.40),
            _h(100.0, 10, 0.45),
        )
    )
    assert hint.state == "deload"


def test_deload_rounds_down_compound_to_25():
    # 87.5 * 0.9 = 78.75 → floor à 2.5 = 77.5
    hint = compute_overload_hint(
        _inp(
            "compound",
            6,
            10,
            _h(87.5, 10, 0.4),
            _h(87.5, 10, 0.4),
        )
    )
    assert hint.target_weight_kg == 77.5


def test_deload_rounds_down_isolation_free_to_1():
    # 20 * 0.9 = 18.0 → floor à 1.0 = 18.0
    hint = compute_overload_hint(
        _inp(
            "isolation_free",
            8,
            12,
            _h(20.0, 12, 0.4),
            _h(20.0, 12, 0.4),
        )
    )
    assert hint.target_weight_kg == 18.0


def test_deload_isolation_free_non_round_floor():
    # 17.5 * 0.9 = 15.75 → floor à 1.0 = 15.0
    hint = compute_overload_hint(
        _inp(
            "isolation_free",
            8,
            12,
            _h(17.5, 12, 0.4),
            _h(17.5, 12, 0.4),
        )
    )
    assert hint.target_weight_kg == 15.0


# ───────── incréments par catégorie ─────────


def test_progress_increment_compound_25():
    hint = compute_overload_hint(
        _inp("compound", 6, 10, _h(100.0, 10, 0.9), _h(100.0, 10, 0.9))
    )
    assert hint.target_weight_kg == 102.5


def test_progress_increment_isolation_free_1():
    hint = compute_overload_hint(
        _inp("isolation_free", 8, 12, _h(15.0, 12, 0.9), _h(15.0, 12, 0.9))
    )
    assert hint.target_weight_kg == 16.0


def test_progress_increment_isolation_machine_25():
    hint = compute_overload_hint(
        _inp(
            "isolation_machine",
            8,
            12,
            _h(40.0, 12, 0.9),
            _h(40.0, 12, 0.9),
        )
    )
    assert hint.target_weight_kg == 42.5


def test_unknown_category_falls_back_to_smallest_increment():
    """Catégorie non répertoriée : fallback +1.0 kg (conservateur)."""
    hint = compute_overload_hint(
        _inp("strongman_event", 6, 10, _h(100.0, 10, 0.9), _h(100.0, 10, 0.9))
    )
    assert hint.state == "progress"
    assert hint.target_weight_kg == 101.0


# ───────── reasons ─────────


def test_max_3_reasons_progress():
    hint = compute_overload_hint(
        _inp("compound", 6, 10, _h(100.0, 10, 0.9), _h(100.0, 10, 0.9))
    )
    assert len(hint.reasons) <= 3


def test_max_3_reasons_deload():
    hint = compute_overload_hint(
        _inp(
            "compound",
            6,
            10,
            _h(100.0, 6, 0.40),
            _h(100.0, 7, 0.40),
            _h(100.0, 9, 0.40),
        )
    )
    # quality + reps decline → 2 triggers + new kg reason = 3 max
    assert len(hint.reasons) <= 3


@pytest.mark.parametrize(
    "hint",
    [
        compute_overload_hint(_inp("compound", 6, 10)),
        compute_overload_hint(
            _inp("compound", 6, 10, _h(100.0, 10, 0.9), _h(100.0, 10, 0.9))
        ),
        compute_overload_hint(
            _inp("compound", 6, 10, _h(100.0, 8, 0.8), _h(100.0, 8, 0.8))
        ),
        compute_overload_hint(_inp("compound", 6, 10, _h(100.0, 4, 0.8))),
        compute_overload_hint(
            _inp("compound", 6, 10, _h(100.0, 10, 0.4), _h(100.0, 10, 0.4))
        ),
    ],
)
def test_no_authoritative_language_in_reasons(hint: OverloadHint):
    """Aucune raison ne doit contenir un langage autoritaire."""
    forbidden = ("tu dois", "il faut absolument", "obligatoire")
    for reason in hint.reasons:
        low = reason.lower()
        for token in forbidden:
            assert token not in low, (
                f"forbidden authoritative token {token!r} in reason: {reason!r}"
            )


def test_reasons_deduplicated():
    """Sanity : les raisons ne contiennent pas de doublons."""
    hint = compute_overload_hint(
        _inp("compound", 6, 10, _h(100.0, 10, 0.9), _h(100.0, 10, 0.9))
    )
    assert len(hint.reasons) == len(set(hint.reasons))


# ───────── déterminisme ─────────


def test_output_is_deterministic_for_same_inputs():
    inp = _inp(
        "compound",
        6,
        10,
        _h(100.0, 10, 0.85),
        _h(100.0, 10, 0.85),
    )
    a = compute_overload_hint(inp)
    b = compute_overload_hint(inp)
    assert a == b


def test_engine_version_is_one():
    hint = compute_overload_hint(_inp("compound", 6, 10))
    assert hint.engine_version == 1
    assert OVERLOAD_ENGINE_VERSION == 1


# ───────── conservative fallback ─────────


def test_history_with_only_one_session_does_not_trigger_progress():
    hint = compute_overload_hint(_inp("compound", 6, 10, _h(100.0, 10, 0.9)))
    # 1 séance ≥ top range mais besoin de 2 pour progress → consolidate.
    assert hint.state == "consolidate"


def test_single_session_below_min_still_top_range():
    hint = compute_overload_hint(_inp("compound", 6, 10, _h(100.0, 4, 0.9)))
    assert hint.state == "top-range"


def test_quality_none_does_not_break_deload_check():
    """quality_score=None → mean retourne None → pas de trigger deload
    sur ce critère seul. Si reps stables, on ne fait pas deload non plus."""
    hint = compute_overload_hint(
        _inp("compound", 6, 10, _h(100.0, 8, None), _h(100.0, 8, None))
    )
    assert hint.state == "consolidate"


# ───────── output structure ─────────


def test_overload_hint_is_immutable_dataclass():
    hint = compute_overload_hint(_inp("compound", 6, 10))
    with pytest.raises(Exception):
        hint.state = "progress"  # type: ignore[misc]


def test_overload_input_is_immutable():
    inp = _inp("compound", 6, 10)
    with pytest.raises(Exception):
        inp.target_min = 8  # type: ignore[misc]
