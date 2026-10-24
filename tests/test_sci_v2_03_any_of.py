"""Sb_SCI_V2_03 — exigences `any_of` dans le moteur d'équipement, sans changer aucun verdict servi.

Grammaire V1 (spec §8.1, §19.6) : conjonction de capacités atomiques et de groupes `any_of`
d'au moins deux capacités atomiques, sans imbrication. Une capacité absente du vocabulaire
servi rend `UNKNOWN`, jamais `FEASIBLE`.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.services import equipment_model as em

ROOT = Path(__file__).resolve().parents[1]
ROPE, BAR = "cable_attachment_rope", "cable_attachment_straight_bar"
NEUTRAL = "cable_attachment_neutral_grip"  # proposée par le delta SCI, absente du registre servi
FEASIBLE, NOT_FEASIBLE, UNKNOWN = "feasible", "not_feasible", "unknown"  # valeurs du contrat


# ── parité exacte avec TRAIN A sur tout l'EKB


def _legacy(requirements, items):
    """La formule d'AVANT, recopiée : la parité se juge contre elle, pas contre le code testé."""
    if requirements is None:
        return UNKNOWN, ()
    if not requirements:
        return FEASIBLE, ()
    if items is None:
        return UNKNOWN, ()
    derived = em.capabilities_for_items(items)
    if set(requirements) <= derived:
        return FEASIBLE, ()
    return NOT_FEASIBLE, tuple(sorted(set(requirements) - derived))


def _environments():
    every = tuple(sorted(em.equipment_items()))
    envs = [None, (), every]
    envs += [(i,) for i in every]
    envs += [tuple(x for x in every if x != i) for i in every]
    return envs


def test_every_served_verdict_is_unchanged():
    ekb = json.loads((ROOT / "data" / "exercise_knowledge_base.json").read_text(encoding="utf-8"))["exercises"]
    checked = 0
    for name in ekb:
        requirements = em.requirements_for_exercise(name)
        for items in _environments():
            now = (em.feasibility(requirements, items), em.missing_capabilities(requirements, items))
            assert now == _legacy(requirements, items), (name, items)
            checked += 1
    assert checked == len(ekb) * len(_environments())


def test_the_ekb_carries_no_any_of():
    ekb = json.loads((ROOT / "data" / "exercise_knowledge_base.json").read_text(encoding="utf-8"))["exercises"]
    for name in ekb:
        requirements = em.requirements_for_exercise(name)
        if requirements is not None:
            assert all(isinstance(m, str) for m in requirements), name


# ── grammaire V1


def test_a_group_needs_at_least_two_atomic_options():
    assert em.AnyOf(frozenset({ROPE, BAR})).options == frozenset({ROPE, BAR})
    for bad in (frozenset(), frozenset({ROPE})):
        with pytest.raises(em.EquipmentModelError):
            em.AnyOf(bad)


def test_a_group_cannot_nest():
    nested = frozenset({em.AnyOf(frozenset({ROPE, BAR})), ROPE})
    with pytest.raises(em.EquipmentModelError):
        em.AnyOf(nested)  # type: ignore[arg-type]


def test_catalogue_json_parses_to_atoms_and_groups():
    assert em.parse_requirements(["cable_anchor_high", {"any_of": [ROPE, BAR]}]) == (
        "cable_anchor_high", em.AnyOf(frozenset({ROPE, BAR})))
    assert em.parse_requirements([]) == ()


@pytest.mark.parametrize("raw", [
    [{"any_of": [{"any_of": [ROPE, BAR]}, ROPE]}],   # imbrication
    [{"any_of": [ROPE]}],                            # une seule option
    [{"any_of": ROPE}],                              # pas une liste
    [{"all_of": [ROPE, BAR]}],                       # opérateur hors grammaire
    [{"any_of": [ROPE, BAR], "note": "x"}],          # clé en trop
    [3],
])
def test_out_of_grammar_requirements_are_refused(raw):
    with pytest.raises(em.EquipmentModelError):
        em.parse_requirements(raw)


def test_every_scientific_catalogue_requirement_parses():
    doc = json.loads((ROOT / "data" / "sci" / "exercise_catalogue.json").read_text(encoding="utf-8"))
    groups = 0
    for record in doc["records"]:
        parsed = em.parse_requirements(record["exercise_operational"]["equipment_requirements"])
        groups += sum(isinstance(m, em.AnyOf) for m in parsed)
    assert groups >= 1


# ── verdicts avec un groupe


PULLOVER = ("cable_anchor_high", em.AnyOf(frozenset({ROPE, BAR})))


@pytest.mark.parametrize("items,verdict", [
    (("dual_adjustable_pulley",), FEASIBLE),                       # corde ET barre livrées
    (("single_adjustable_pulley", "cable_rope"), FEASIBLE),
    (("single_adjustable_pulley", "cable_straight_bar"), FEASIBLE),
    (("single_adjustable_pulley",), NOT_FEASIBLE),                 # ni corde ni barre
    (("cable_rope", "cable_straight_bar"), NOT_FEASIBLE),          # pas d'ancrage haut
    ((), NOT_FEASIBLE),
    (None, UNKNOWN),
])
def test_an_any_of_group_needs_one_option(items, verdict):
    assert em.feasibility(PULLOVER, items) == verdict


def test_an_unmet_group_is_named_in_the_missing_list():
    missing = em.missing_capabilities(PULLOVER, ("single_adjustable_pulley",))
    assert missing == (f"any_of({ROPE}|{BAR})",)


# ── capacité hors du vocabulaire servi : UNKNOWN, jamais FEASIBLE


def test_an_unknown_capability_is_never_feasible_however_rich_the_gym():
    every = tuple(sorted(em.equipment_items()))
    assert em.feasibility((NEUTRAL,), every) == UNKNOWN
    assert em.feasibility(("pulldown_seated_station", NEUTRAL), every) == UNKNOWN


def test_a_known_missing_capability_still_refuses_alongside_an_unknown_one():
    assert em.feasibility(("pulldown_seated_station", NEUTRAL), ()) == NOT_FEASIBLE
    assert em.missing_capabilities(("pulldown_seated_station", NEUTRAL), ()) == ("pulldown_seated_station",)


def test_a_group_with_an_unknown_option():
    group = (em.AnyOf(frozenset({ROPE, NEUTRAL})),)
    assert em.feasibility(group, ("cable_rope",)) == FEASIBLE          # une option connue possédée
    assert em.feasibility(group, ("dumbbells",)) == UNKNOWN            # l'option inconnue est peut-être là
    assert em.missing_capabilities(group, ("dumbbells",)) == ()        # on n'énumère pas un manque non constaté


def test_unknown_requirements_still_never_become_feasible():
    every = tuple(sorted(em.equipment_items()))
    assert em.feasibility(None, every) == UNKNOWN
