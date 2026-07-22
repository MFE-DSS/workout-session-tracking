"""Sb_CUSTOM_PROGRAM_SCORING_01 — moteur pur de scoring qualité programme.

Pins le contrat du moteur (spec Sx_CUSTOM_PROGRAM_03) : pureté (zéro DB/ORM/LLM),
déterminisme, versionnement, les 4 sous-scores calculables, les 4 déclarés
manquants (jamais notés 0, exclus de la moyenne), la confiance dégradée par la
couverture EKB, et le plafond de grade à B en V1.
"""
from __future__ import annotations

import inspect
import json
from collections import defaultdict

import pytest

from app.services import program_quality_engine as engine
from app.services.program_quality_engine import (
    COMPUTABLE_SUBSCORES,
    MISSING_SUBSCORES,
    PROGRAM_QUALITY_SCORING_VERSION,
    ExerciseKnowledgeBase,
    ExerciseSlot,
    ProgramDefinition,
    SessionPlan,
    UserProfile,
    score_program,
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
    """PPL cohérent : les 3 familles représentées, zones variées."""
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
    """Programme très déséquilibré : une seule famille, une seule séance."""
    return ProgramDefinition(
        "Tout poussée",
        (_session("Push only", 1, by_pattern["push_horizontal"][:4]),),
    )


# ───────── pureté / déterminisme / versionnement ─────────


def test_engine_module_has_no_db_or_orm_import():
    source = inspect.getsource(engine)
    for forbidden in ("sqlalchemy", "app.database", "app.models", "Session("):
        assert forbidden not in source, f"import interdit dans le moteur : {forbidden}"


def test_scoring_is_deterministic(balanced, ekb):
    first = score_program(balanced, ekb)
    second = score_program(balanced, ekb)
    assert first == second
    assert first.to_dict() == second.to_dict()


def test_result_is_json_serialisable(balanced, ekb):
    payload = json.dumps(score_program(balanced, ekb).to_dict(), ensure_ascii=False)
    assert "grade" in payload


def test_versions_are_exposed(balanced, ekb):
    result = score_program(balanced, ekb)
    assert result.scoring_version == PROGRAM_QUALITY_SCORING_VERSION == 1
    assert result.ekb_version == ekb.version
    assert result.ekb_version.startswith("Sb_CUSTOM_PROGRAM_EKB_02")


# ───────── sous-scores calculables vs manquants ─────────


def test_four_computable_subscores_present(balanced, ekb):
    keys = tuple(s.key for s in score_program(balanced, ekb).subscores)
    assert keys == COMPUTABLE_SUBSCORES
    assert len(keys) == 4


def test_four_missing_subscores_declared_and_never_scored_zero(balanced, ekb):
    result = score_program(balanced, ekb)
    assert len(result.missing_data) == 4
    scored_keys = {s.key for s in result.subscores}
    for key in MISSING_SUBSCORES:
        assert any(key in entry for entry in result.missing_data)
        # jamais noté : un faux 0 serait de la pseudo-science
        assert key not in scored_keys


def test_missing_subscores_excluded_from_average(balanced, ekb):
    result = score_program(balanced, ekb)
    computed = [s.score for s in result.subscores]
    assert result.global_score == round(sum(computed) / len(computed))
    # la moyenne porte bien sur 4 valeurs, pas 8
    assert len(computed) == 4


# ───────── grade : plafonné à B en V1 ─────────


def test_balanced_program_gets_b_never_a(balanced, ekb, by_pattern):
    equipment = tuple(
        {
            (ekb.lookup(slot.exercise_name) or {}).get("equipment_family")
            for session in balanced.sessions
            for slot in session.exercises
        }
        - {None}
    )
    result = score_program(
        balanced, ekb, UserProfile("intermediate", equipment, sessions_per_week=3)
    )
    assert result.grade == "B"
    assert result.grade_cap_reason is not None
    assert "plafonné" in result.grade_cap_reason


def test_lopsided_program_gets_c(lopsided, ekb):
    result = score_program(lopsided, ekb)
    assert result.grade == "C"


def test_grade_is_never_a_in_v1(balanced, lopsided, ekb):
    for definition in (balanced, lopsided):
        assert score_program(definition, ekb).grade in {"B", "C"}


def test_engine_never_blocks_publication(lopsided, ekb):
    result = score_program(lopsided, ekb)
    payload = result.to_dict()
    assert "blocked" not in payload
    assert result.grade == "C"  # C reste publiable (OQ-SCORE-C)


# ───────── robustesse aux gaps EKB ─────────


def test_unknown_exercise_does_not_break_engine(ekb):
    definition = ProgramDefinition(
        "Inconnus", (_session("S1", 1, ["Exercice totalement inconnu XYZ"]),)
    )
    result = score_program(definition, ekb)
    assert result.grade in {"B", "C"}
    assert any("hors EKB" in a for a in result.assumptions)


def test_unknown_exercises_reduce_confidence(balanced, ekb, by_pattern):
    good = score_program(balanced, ekb)
    polluted = ProgramDefinition(
        balanced.title,
        balanced.sessions
        + (_session("Inconnus", 9, ["Inconnu A", "Inconnu B", "Inconnu C"]),),
    )
    degraded = score_program(polluted, ekb)
    # la couverture baisse dès qu'un slot n'est pas résolu par l'EKB
    assert degraded.coverage_ratio < good.coverage_ratio
    assert good.confidence == "moderate"


def test_mostly_unknown_program_drops_confidence(balanced, ekb):
    """Couverture EKB majoritairement absente ⇒ confiance explicitement basse."""
    mostly_unknown = ProgramDefinition(
        "Surtout inconnus",
        (_session("S1", 1, [f"Inconnu {i}" for i in range(8)]),) + balanced.sessions[:1],
    )
    result = score_program(mostly_unknown, ekb)
    assert result.coverage_ratio < 0.5
    assert result.confidence == "very_low"


def test_empty_program_does_not_crash(ekb):
    result = score_program(ProgramDefinition("Vide", ()), ekb)
    assert result.grade == "C"
    assert result.coverage_ratio == 0.0


def test_missing_profile_produces_assumptions(balanced, ekb):
    result = score_program(balanced, ekb, profile=None)
    assert result.assumptions
    assert any("Niveau non déclaré" in a for a in result.assumptions)


# ───────── microcopy (contraintes dures spec §8) ─────────


def _all_strings(result) -> list[str]:
    out: list[str] = []
    for sub in result.subscores:
        out.extend(sub.reasons)
    out.extend(a["message"] for a in result.alerts)
    out.extend(s["message"] for s in result.suggestions)
    out.extend(result.assumptions)
    out.extend(result.missing_data)
    if result.grade_cap_reason:
        out.append(result.grade_cap_reason)
    out.append(result.disclaimer)
    return out


def test_no_medical_or_hormonal_claims(balanced, lopsided, ekb):
    forbidden = (
        "blessure", "pathologie", "tendinite", "diagnostic",
        "hormonal", "testostérone", "anabolisme", "cortisol",
    )
    for definition in (balanced, lopsided):
        for text in _all_strings(score_program(definition, ekb)):
            lowered = text.lower()
            for word in forbidden:
                assert word not in lowered, f"lexique interdit : {word!r} dans {text!r}"


def test_no_injunctions_in_microcopy(balanced, lopsided, ekb):
    for definition in (balanced, lopsided):
        for text in _all_strings(score_program(definition, ekb)):
            lowered = text.lower()
            assert "tu dois" not in lowered
            assert "optimal" not in lowered
            assert "parfait" not in lowered


def test_disclaimer_always_present(balanced, ekb):
    result = score_program(balanced, ekb)
    assert "pas une vérité médicale" in result.disclaimer
