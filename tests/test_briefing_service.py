"""Unit tests for app.services.briefing (Sb_11a)."""
from __future__ import annotations

from types import SimpleNamespace

from app.services.briefing import (
    _compact_scheme,
    _last_time_chip,
    build_chip,
    build_peek,
)


def _te(rep_targets):
    """Lightweight TemplateExercise stand-in."""
    return SimpleNamespace(rep_targets=rep_targets)


def _rt(min_reps: int, max_reps: int, technique: str | None = None):
    return SimpleNamespace(min_reps=min_reps, max_reps=max_reps, technique=technique)


# ---- _compact_scheme --------------------------------------------------


def test_compact_scheme_uniform_rep_targets():
    te = _te([_rt(8, 12), _rt(8, 12), _rt(8, 12)])
    assert _compact_scheme(te) == "3×8-12"


def test_compact_scheme_collapses_when_min_equals_max():
    te = _te([_rt(5, 5), _rt(5, 5)])
    assert _compact_scheme(te) == "2×5"


def test_compact_scheme_variable_uses_var_marker():
    te = _te([_rt(6, 8), _rt(10, 12)])
    assert _compact_scheme(te) == "2×var"


def test_compact_scheme_appends_technique():
    te = _te([_rt(8, 10, technique="RP"), _rt(8, 10, technique="RP")])
    assert _compact_scheme(te) == "2×8-10 RP"


def test_compact_scheme_no_rep_targets_returns_none():
    assert _compact_scheme(_te([])) is None
    assert _compact_scheme(None) is None


# ---- _last_time_chip --------------------------------------------------


def test_last_time_chip_formats_integer_weights_cleanly():
    prior = {"first_set": {"weight_kg": 60.0, "reps": 10}}
    assert _last_time_chip(prior) == "dernière fois 60 kg × 10"


def test_last_time_chip_preserves_decimal_weights():
    prior = {"first_set": {"weight_kg": 52.5, "reps": 8}}
    assert _last_time_chip(prior) == "dernière fois 52.5 kg × 8"


def test_last_time_chip_falls_back_to_premiere_fois():
    assert _last_time_chip(None) == "première fois"
    assert _last_time_chip({}) == "première fois"
    assert _last_time_chip({"first_set": None}) == "première fois"
    assert _last_time_chip({"first_set": {"weight_kg": None, "reps": 10}}) == "première fois"


# ---- build_chip -------------------------------------------------------


def test_build_chip_returns_none_when_no_scheme():
    te = _te([])
    assert build_chip(te, None, "strength") is None


def test_build_chip_strength_happy_path():
    te = _te([_rt(8, 12), _rt(8, 12), _rt(8, 12)])
    prior = {"first_set": {"weight_kg": 60.0, "reps": 10}}
    chip = build_chip(te, prior, "strength")
    # D5_SESSION_INSTRUMENT_ROWS_01 — `has_prior` s'ajoute au contrat de la
    # puce. L'égalité EXACTE est conservée volontairement : c'est elle qui a
    # signalé l'ajout de clé pendant le broad sweep, et une clé silencieuse
    # dans un contrat de rendu est exactement ce qu'il faut voir arriver.
    assert chip == {
        "scheme": "3×8-12",
        "last_time": "dernière fois 60 kg × 10",
        "has_prior": True,
        "kind": "strength",
    }


def test_build_chip_passes_through_cardio_kind():
    te = _te([_rt(12, 15), _rt(12, 15)])
    chip = build_chip(te, None, "cardio")
    assert chip["kind"] == "cardio"
    assert chip["scheme"] == "2×12-15"
    assert chip["last_time"] == "première fois"


# ---- build_peek -------------------------------------------------------


def _next_se(code="E3", name="Chest Press machine", rep_targets=None, substituted=None):
    return SimpleNamespace(
        exercise_code_snapshot=code,
        exercise_name_snapshot=name,
        substituted_name=substituted,
        template_exercise=_te(rep_targets or []),
    )


def test_build_peek_returns_none_when_next_is_none():
    assert build_peek(None, None, None, "strength") is None


def test_build_peek_returns_none_when_no_scheme():
    next_se = _next_se(rep_targets=[])
    assert build_peek(next_se, None, None, "strength") is None


def test_build_peek_without_atlas_has_empty_cues():
    next_se = _next_se(rep_targets=[_rt(8, 12), _rt(8, 12)])
    peek = build_peek(next_se, None, None, "strength")
    assert peek is not None
    assert peek["cues"] == []
    assert peek["code"] == "E3"
    assert peek["scheme"] == "2×8-12"
    assert peek["last_time"] == "première fois"


def test_build_peek_caps_cues_at_two():
    next_se = _next_se(rep_targets=[_rt(8, 12)])
    atlas = {
        "machine": {
            "execution_cues": ["cue 1", "cue 2", "cue 3", "cue 4"],
        },
    }
    peek = build_peek(next_se, None, atlas, "strength")
    assert peek is not None
    assert peek["cues"] == ["cue 1", "cue 2"]


def test_build_peek_shows_substituted_name_when_set():
    next_se = _next_se(
        name="Incline Smith Press",
        substituted="Développé incliné haltères",
        rep_targets=[_rt(6, 10)],
    )
    peek = build_peek(next_se, None, None, "strength")
    assert peek["name"] == "Développé incliné haltères"


def test_build_peek_merges_prior_last_time():
    next_se = _next_se(rep_targets=[_rt(6, 10), _rt(6, 10), _rt(6, 10)])
    prior = {"first_set": {"weight_kg": 80.0, "reps": 8}}
    peek = build_peek(next_se, prior, None, "strength")
    assert peek["last_time"] == "dernière fois 80 kg × 8"
    assert peek["scheme"] == "3×6-10"
