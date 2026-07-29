"""Sb_CUSTOM_PROGRAM_WIZARD_03 — pure deterministic generator tests.

No DB, no client: `generate_program_tree` is a pure function over the curated
`data/reference_split.json`. These pin determinism, exact slug selection, the
`replace_draft_tree`-compatible payload shape, and the input contract.
"""
from __future__ import annotations

import pytest

from app.services.user_program_generator import (
    MAX_SESSIONS,
    ProgramGenerationError,
    generate_program_tree,
)


def _slugs(tree: list[dict]) -> list[str]:
    return [s["exercises"][0]["source_reason"].split(":")[-1] for s in tree]


def test_ppl_three_sessions_exact_slugs():
    tree = generate_program_tree("ppl", 3)
    assert _slugs(tree) == ["push-a", "pull-a", "legs-a"]


def test_ppl_six_sessions_full_cycle():
    tree = generate_program_tree("ppl", 6)
    assert _slugs(tree) == ["push-a", "pull-a", "legs-a", "push-b", "pull-b", "legs-b"]


def test_upper_lower_four_sessions_cycle():
    tree = generate_program_tree("upper_lower", 4)
    assert _slugs(tree) == [
        "upper-pecs-delts",
        "lower-quad-bias",
        "upper-back-arms",
        "lower-posterior-bias",
    ]


def test_session_positions_are_sequential():
    tree = generate_program_tree("ppl", 4)
    assert [s["position"] for s in tree] == [1, 2, 3, 4]


def test_exercise_positions_are_sequential_per_session():
    tree = generate_program_tree("ppl", 2)
    for session in tree:
        positions = [e["position"] for e in session["exercises"]]
        assert positions == list(range(1, len(positions) + 1))


def test_rep_targets_copied_and_non_empty():
    tree = generate_program_tree("ppl", 3)
    for session in tree:
        for exercise in session["exercises"]:
            assert exercise["rep_targets"]
            for rt in exercise["rep_targets"]:
                assert rt["min_reps"] <= rt["max_reps"]


def test_source_reason_traces_the_template():
    tree = generate_program_tree("upper_lower", 2)
    for session in tree:
        for exercise in session["exercises"]:
            assert exercise["source_reason"].startswith("generated:reference_split:")


def test_deterministic_same_input_same_payload():
    assert generate_program_tree("ppl", 5) == generate_program_tree("ppl", 5)


def test_unknown_split_is_refused():
    with pytest.raises(ProgramGenerationError, match="split"):
        generate_program_tree("bro-split", 3)


def test_sessions_zero_refused_and_over_max_capped():
    with pytest.raises(ProgramGenerationError):
        generate_program_tree("ppl", 0)
    # A request beyond the curated cycle is CAPPED, never an error.
    assert len(generate_program_tree("ppl", 99)) == 6
    assert len(generate_program_tree("upper_lower", 99)) == 4


def test_no_empty_cardio_sessions_generated():
    for split in ("ppl", "upper_lower"):
        for session in generate_program_tree(split, MAX_SESSIONS):
            assert len(session["exercises"]) >= 1


def test_payload_shape_is_replace_draft_tree_compatible():
    tree = generate_program_tree("ppl", 2)
    for session in tree:
        assert {"position", "name", "exercises"} <= set(session)
        for exercise in session["exercises"]:
            assert {"position", "exercise_name", "set_scheme", "rep_targets"} <= set(
                exercise
            )
