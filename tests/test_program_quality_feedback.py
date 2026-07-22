"""Sb_CUSTOM_PROGRAM_SCORING_02 — couche de feedback qualité programme.

Pins le contrat du wrapper pur (spec Sx_CUSTOM_PROGRAM_03 §8/§15) : pureté,
déterminisme, restitution du plafond de grade / des dimensions non mesurables /
de la fiabilité, hiérarchie sans niveau bloquant, ordre stable et plafonné,
et la doctrine de microcopy (aucun claim médical, aucune injonction, aucune
culpabilisation).
"""
from __future__ import annotations

import inspect
import json
from collections import defaultdict

import pytest

from app.services import program_quality_feedback as feedback_module
from app.services.program_quality_engine import (
    ExerciseKnowledgeBase,
    ExerciseSlot,
    ProgramDefinition,
    SessionPlan,
    UserProfile,
    score_program,
)
from app.services.program_quality_feedback import (
    FEEDBACK_LEVELS,
    LEVEL_INFO,
    LEVEL_TIP,
    LEVEL_WARNING,
    MAX_ITEMS_PER_LEVEL,
    build_program_quality_feedback,
)


@pytest.fixture(scope="module")
def ekb() -> ExerciseKnowledgeBase:
    return ExerciseKnowledgeBase.load()


@pytest.fixture(scope="module")
def by_pattern(ekb) -> dict:
    out = defaultdict(list)
    for name, entry in ekb.entries.items():
        if entry.get("zone_primary") and entry.get("movement_pattern"):
            out[entry["movement_pattern"]].append(name)
    return out


def _session(name: str, position: int, names: list[str]) -> SessionPlan:
    return SessionPlan(
        name=name,
        position=position,
        exercises=tuple(ExerciseSlot(n, i + 1) for i, n in enumerate(names)),
    )


@pytest.fixture()
def balanced(by_pattern) -> ProgramDefinition:
    push = by_pattern["push_horizontal"][:2] + by_pattern["push_vertical"][:1]
    pull = by_pattern["pull_horizontal"][:2] + by_pattern["pull_vertical"][:1]
    legs = by_pattern["isolation_lower"][:4]
    return ProgramDefinition(
        "PPL équilibré",
        (
            _session("Push", 1, push + by_pattern["isolation_upper"][:1]),
            _session("Pull", 2, pull + by_pattern["isolation_upper"][1:2]),
            _session("Legs", 3, legs),
        ),
    )


@pytest.fixture()
def lopsided(by_pattern) -> ProgramDefinition:
    return ProgramDefinition(
        "Tout poussée",
        (_session("Push only", 1, by_pattern["push_horizontal"][:4]),),
    )


def _feedback(definition, ekb, profile=None):
    return build_program_quality_feedback(score_program(definition, ekb, profile))


def _all_strings(fb) -> list[str]:
    out = [fb.headline, fb.confidence_note, fb.disclaimer]
    if fb.grade_note:
        out.append(fb.grade_note)
    for item in fb.items:
        out.extend([item.title, item.message])
        if item.action:
            out.append(item.action)
    out.extend(fb.limitations)
    return out


# ───────── pureté / déterminisme / sérialisation ─────────


def test_module_has_no_db_or_orm_import():
    source = inspect.getsource(feedback_module)
    for forbidden in ("sqlalchemy", "app.database", "app.models", "Session("):
        assert forbidden not in source, f"import interdit : {forbidden}"


def test_feedback_is_deterministic(balanced, ekb):
    first = _feedback(balanced, ekb)
    second = _feedback(balanced, ekb)
    assert first == second
    assert first.to_dict() == second.to_dict()


def test_feedback_is_json_serialisable(balanced, ekb):
    payload = json.dumps(_feedback(balanced, ekb).to_dict(), ensure_ascii=False)
    assert "headline" in payload


def test_versions_are_carried_over(balanced, ekb):
    result = score_program(balanced, ekb)
    fb = build_program_quality_feedback(result)
    assert fb.scoring_version == result.scoring_version
    assert fb.ekb_version == result.ekb_version


# ───────── les trous de SCORING_01 comblés ─────────


def test_balanced_program_still_gets_useful_feedback(balanced, ekb, by_pattern):
    """Le moteur seul n'émettait presque rien quand tout allait bien."""
    equipment = tuple(
        {
            (ekb.lookup(slot.exercise_name) or {}).get("equipment_family")
            for session in balanced.sessions
            for slot in session.exercises
        }
        - {None}
    )
    fb = _feedback(balanced, ekb, UserProfile("intermediate", equipment, 3))
    assert fb.grade == "B"
    assert len(fb.items) >= 3
    assert fb.headline


def test_grade_cap_is_explained_when_present(balanced, ekb):
    result = score_program(balanced, ekb)
    fb = build_program_quality_feedback(result)
    assert result.grade_cap_reason is not None
    assert fb.grade_note is not None
    assert any(item.category == "grade" for item in fb.items)


def test_all_missing_dimensions_are_restituted(balanced, ekb):
    result = score_program(balanced, ekb)
    fb = build_program_quality_feedback(result)
    assert len(fb.limitations) == len(result.missing_data) == 4
    coverage = [i for i in fb.items if i.category == "coverage"]
    assert coverage, "les dimensions non mesurables doivent être exposées"


def test_confidence_and_coverage_are_verbalised(balanced, ekb):
    result = score_program(balanced, ekb)
    fb = build_program_quality_feedback(result)
    assert fb.confidence_note
    assert f"{round(result.coverage_ratio * 100)} %" in fb.confidence_note


def test_context_is_named_when_data_allows(lopsided, ekb):
    fb = _feedback(lopsided, ekb)
    messages = " ".join(i.message for i in fb.items)
    assert "poussée" in messages.lower()


# ───────── hiérarchie et ordre ─────────


def test_no_blocking_level_ever(balanced, lopsided, ekb):
    for definition in (balanced, lopsided):
        fb = _feedback(definition, ekb)
        for item in fb.items:
            assert item.level in FEEDBACK_LEVELS
            assert item.level != "blocking"
        assert "blocked" not in fb.to_dict()


def test_items_are_ordered_by_priority(lopsided, ekb):
    fb = _feedback(lopsided, ekb)
    rank = {LEVEL_WARNING: 0, LEVEL_TIP: 1, LEVEL_INFO: 2}
    levels = [rank[i.level] for i in fb.items]
    assert levels == sorted(levels)


def test_items_are_capped_per_level(lopsided, ekb):
    fb = _feedback(lopsided, ekb)
    for level in FEEDBACK_LEVELS:
        assert sum(1 for i in fb.items if i.level == level) <= MAX_ITEMS_PER_LEVEL


def test_grade_c_remains_publishable(lopsided, ekb):
    fb = _feedback(lopsided, ekb)
    assert fb.grade == "C"
    assert fb.items  # on informe…
    assert all(i.level != "blocking" for i in fb.items)  # …sans bloquer


# ───────── microcopy (spec §8) ─────────


def test_no_medical_or_hormonal_claims(balanced, lopsided, ekb):
    forbidden = (
        "blessure", "pathologie", "tendinite", "diagnostic",
        "hormonal", "testostérone", "anabolisme", "cortisol",
    )
    for definition in (balanced, lopsided):
        for text in _all_strings(_feedback(definition, ekb)):
            lowered = text.lower()
            for word in forbidden:
                assert word not in lowered, f"lexique interdit : {word!r}"


def test_no_injunctions(balanced, lopsided, ekb):
    for definition in (balanced, lopsided):
        for text in _all_strings(_feedback(definition, ekb)):
            lowered = text.lower()
            assert "tu dois" not in lowered
            assert "optimal" not in lowered
            assert "parfait" not in lowered


def test_no_guilt_inducing_wording(balanced, lopsided, ekb):
    forbidden = ("tu manques", "insuffisant", "mauvais programme", "tu as échoué")
    for definition in (balanced, lopsided):
        for text in _all_strings(_feedback(definition, ekb)):
            lowered = text.lower()
            for word in forbidden:
                assert word not in lowered, f"formulation culpabilisante : {word!r}"


def test_limitations_are_framed_as_tool_limits(balanced, ekb):
    """Sujet grammatical = l'outil, jamais l'utilisateur."""
    fb = _feedback(balanced, ekb)
    coverage = [i for i in fb.items if i.category == "coverage"]
    assert coverage
    assert "ne sont pas encore mesurables par l'outil" in coverage[0].message


def test_disclaimer_is_carried_over(balanced, ekb):
    fb = _feedback(balanced, ekb)
    assert "pas une vérité médicale" in fb.disclaimer


# ───────── robustesse ─────────


def test_empty_program_does_not_crash(ekb):
    fb = _feedback(ProgramDefinition("Vide", ()), ekb)
    assert fb.grade == "C"
    assert fb.confidence_note


def test_unknown_exercises_do_not_crash(ekb):
    definition = ProgramDefinition(
        "Inconnus", (_session("S1", 1, ["Exercice inconnu XYZ", "Autre inconnu"]),)
    )
    fb = _feedback(definition, ekb)
    assert fb.items
    assert fb.confidence_note
