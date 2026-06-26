"""Sb_30.2 — Tests unitaires de l'explainer overload.

Couvre la traduction d'un :class:`OverloadHint` en payload de template
sans réimplémentation de la logique métier (Sx_30 §6).
"""

from __future__ import annotations

import pytest

from app.services.overload_engine import (
    OVERLOAD_ENGINE_VERSION,
    HistoricalSetSignal,
    OverloadInput,
    compute_overload_hint,
)
from app.services.overload_explainer import explain_overload_hint


def _h(weight: float, reps: int, q: float | None = 0.8, fatigue: bool = False):
    return HistoricalSetSignal(
        weight_kg=weight, reps=reps, quality_score=q, fatigue_signal=fatigue
    )


def _inp(category: str, tmin: int, tmax: int, *history):
    return OverloadInput(
        exercise_category=category,
        target_min=tmin,
        target_max=tmax,
        history=tuple(history),
    )


# ───────── clés de sortie ─────────


def test_payload_has_stable_keys_for_all_states():
    expected = {
        "state",
        "intent_label",
        "target_summary",
        "reasons",
        "engine_version",
        "is_silent",
    }
    for inp in (
        _inp("compound", 6, 10),  # unknown
        _inp("compound", 6, 10, _h(100.0, 10, 0.9), _h(100.0, 10, 0.9)),  # progress
        _inp("compound", 6, 10, _h(100.0, 8, 0.8), _h(100.0, 8, 0.8)),  # consolidate
        _inp("compound", 6, 10, _h(100.0, 4, 0.8)),  # top-range
        _inp("compound", 6, 10, _h(100.0, 10, 0.4), _h(100.0, 10, 0.4)),  # deload
    ):
        payload = explain_overload_hint(compute_overload_hint(inp))
        assert set(payload.keys()) == expected


# ───────── is_silent ─────────


def test_unknown_is_silent():
    payload = explain_overload_hint(compute_overload_hint(_inp("compound", 6, 10)))
    assert payload["state"] == "unknown"
    assert payload["is_silent"] is True


@pytest.mark.parametrize(
    "inp",
    [
        _inp("compound", 6, 10, _h(100.0, 10, 0.9), _h(100.0, 10, 0.9)),
        _inp("compound", 6, 10, _h(100.0, 8, 0.8), _h(100.0, 8, 0.8)),
        _inp("compound", 6, 10, _h(100.0, 4, 0.8)),
        _inp("compound", 6, 10, _h(100.0, 10, 0.4), _h(100.0, 10, 0.4)),
    ],
)
def test_non_unknown_states_are_not_silent(inp):
    payload = explain_overload_hint(compute_overload_hint(inp))
    assert payload["is_silent"] is False


# ───────── target_summary ─────────


def test_target_summary_none_for_unknown():
    payload = explain_overload_hint(compute_overload_hint(_inp("compound", 6, 10)))
    assert payload["target_summary"] is None


def test_target_summary_for_progress_has_kg_and_reps():
    payload = explain_overload_hint(
        compute_overload_hint(
            _inp("compound", 6, 10, _h(100.0, 10, 0.9), _h(100.0, 10, 0.9))
        )
    )
    assert payload["target_summary"] is not None
    assert "102.5 kg" in payload["target_summary"]
    assert "6-10 reps" in payload["target_summary"]


def test_target_summary_drops_zero_decimals():
    payload = explain_overload_hint(
        compute_overload_hint(
            _inp("compound", 6, 10, _h(100.0, 10, 0.5), _h(100.0, 10, 0.5))
        )
    )
    # 100 * 0.9 = 90.0 → "90 kg" (pas "90.0 kg")
    assert "90 kg" in payload["target_summary"]


def test_target_summary_collapses_equal_reps():
    """Deload : target_reps_min == target_reps_max == target_min → "6 reps"."""
    payload = explain_overload_hint(
        compute_overload_hint(
            _inp("compound", 6, 10, _h(100.0, 10, 0.4), _h(100.0, 10, 0.4))
        )
    )
    assert "6 reps" in payload["target_summary"]
    assert "-" not in payload["target_summary"].split("·")[-1]


# ───────── intent_label ─────────


@pytest.mark.parametrize(
    "state,expected_fragment",
    [
        ("unknown", "Première fois"),
        ("progress", "augmenter"),
        ("consolidate", "Consolider"),
        ("top-range", "bas de range"),
        ("deload", "Alléger"),
    ],
)
def test_intent_label_per_state(state, expected_fragment):
    inputs = {
        "unknown": _inp("compound", 6, 10),
        "progress": _inp("compound", 6, 10, _h(100.0, 10, 0.9), _h(100.0, 10, 0.9)),
        "consolidate": _inp("compound", 6, 10, _h(100.0, 8, 0.8), _h(100.0, 8, 0.8)),
        "top-range": _inp("compound", 6, 10, _h(100.0, 4, 0.8)),
        "deload": _inp("compound", 6, 10, _h(100.0, 10, 0.4), _h(100.0, 10, 0.4)),
    }
    payload = explain_overload_hint(compute_overload_hint(inputs[state]))
    assert payload["state"] == state
    assert expected_fragment.lower() in payload["intent_label"].lower()


def test_intent_label_never_authoritative():
    forbidden = ("tu dois", "il faut absolument", "obligatoire")
    for inp in (
        _inp("compound", 6, 10),
        _inp("compound", 6, 10, _h(100.0, 10, 0.9), _h(100.0, 10, 0.9)),
        _inp("compound", 6, 10, _h(100.0, 8, 0.8), _h(100.0, 8, 0.8)),
        _inp("compound", 6, 10, _h(100.0, 4, 0.8)),
        _inp("compound", 6, 10, _h(100.0, 10, 0.4), _h(100.0, 10, 0.4)),
    ):
        payload = explain_overload_hint(compute_overload_hint(inp))
        low = payload["intent_label"].lower()
        for token in forbidden:
            assert token not in low, f"forbidden token {token!r} in intent_label"


# ───────── engine_version propagated ─────────


def test_engine_version_propagated():
    payload = explain_overload_hint(compute_overload_hint(_inp("compound", 6, 10)))
    assert payload["engine_version"] == OVERLOAD_ENGINE_VERSION


# ───────── reasons propagated, ≤ 3 ─────────


def test_reasons_propagated_and_capped():
    payload = explain_overload_hint(
        compute_overload_hint(
            _inp(
                "compound",
                6,
                10,
                _h(100.0, 6, 0.40),
                _h(100.0, 7, 0.40),
                _h(100.0, 9, 0.40),
            )
        )
    )
    assert isinstance(payload["reasons"], tuple)
    assert len(payload["reasons"]) <= 3


# ───────── déterminisme ─────────


def test_explain_is_deterministic():
    hint = compute_overload_hint(
        _inp("compound", 6, 10, _h(100.0, 10, 0.85), _h(100.0, 10, 0.85))
    )
    a = explain_overload_hint(hint)
    b = explain_overload_hint(hint)
    assert a == b


# ───────── no re-implementation of compute_overload_hint ─────────


def test_explainer_does_not_import_engine_internals():
    """Garde : l'explainer ne doit pas réimplémenter la logique de
    décision. Il doit uniquement importer les types publics + state enum,
    pas les helpers internes (`_hint_*`, `_increment_for`, etc.)."""
    import inspect

    from app.services import overload_explainer

    src = inspect.getsource(overload_explainer)
    forbidden_internals = (
        "_hint_unknown",
        "_hint_deload",
        "_hint_progress",
        "_hint_top_range",
        "_hint_consolidate",
        "_increment_for",
        "_deload_weight",
        "_is_consecutive_reps_decline",
        "compute_overload_hint",  # explainer must NOT re-call the engine
    )
    for tok in forbidden_internals:
        assert tok not in src, (
            f"overload_explainer must not reference engine internal {tok!r}"
        )
