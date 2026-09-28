"""TRAIN A — résolution de créneau et de gabarit (§12, §13).

Les gardes portent sur la **table d'états**, pas sur des comptes. Un test qui
compterait des créneaux resterait vert pendant que `UNKNOWN` glisserait vers
`SERVABLE` — exactement le mode d'échec que le programme combat.

Chaque garde a été vue rouge par mutation.
"""
from __future__ import annotations

import json
from pathlib import Path

from app.services.environment_resolution import (
    ADAPTABLE,
    NATIVE_FEASIBLE,
    NOT_FEASIBLE,
    SERVABLE,
    SLOT_UNKNOWN,
    TEMPLATE_NOT_FEASIBLE,
    TEMPLATE_UNKNOWN,
    resolve_slot,
    resolve_template,
)

_DATA = Path(__file__).resolve().parents[1] / "data"

# Identités réelles du catalogue, jamais inventées — un labo non
# représentatif fait conclure faux.
_SMITH_INCLINE = "Incline Smith Press"          # smith_rack + incline bench
_DB_INCLINE = "Développé incliné haltères 30°"  # dumbbells + incline bench
_HIP_THRUST = "Hip thrust Smith"                # smith_rack seul
_PALLOF = "Pallof press câble"                  # exigence INCONNUE
_MOLLETS = "Relevés mollets debout"             # exigence VIDE (§8)
_LEG_PRESS = "Leg Press (pieds bas)"            # machine_leg_press

_MAISON = ("adjustable_bench", "dumbbells")
_AVEC_SMITH = ("adjustable_bench", "dumbbells", "smith_machine")


def _curation() -> dict:
    return json.loads(
        (_DATA / "equipment_curation.json").read_text(encoding="utf-8"))


# ───────── §12 — les quatre états de créneau ─────────


def test_a_proven_prescription_is_native_and_keeps_its_exercise():
    r = resolve_slot(_SMITH_INCLINE, [_DB_INCLINE], _AVEC_SMITH)
    assert r.state == NATIVE_FEASIBLE
    assert r.chosen == _SMITH_INCLINE


def test_an_infeasible_prescription_with_a_proven_substitute_is_adaptable():
    r = resolve_slot(_SMITH_INCLINE, [_DB_INCLINE], _MAISON)
    assert r.state == ADAPTABLE
    assert r.chosen == _DB_INCLINE
    assert "smith_rack" in r.missing


def test_an_unknown_prescription_with_a_proven_substitute_is_adaptable():
    """§12 — `ADAPTABLE` couvre « infaisable OU inconnu ». Une certitude
    acquise n'est pas retirée par une incertitude voisine."""
    r = resolve_slot(_PALLOF, [_DB_INCLINE], _MAISON)
    assert r.state == ADAPTABLE
    assert r.chosen == _DB_INCLINE
    assert _PALLOF in r.unknown_paths


def test_no_proven_path_but_an_unknown_one_is_unknown_not_a_refusal():
    r = resolve_slot(_SMITH_INCLINE, [_PALLOF], _MAISON)
    assert r.state == SLOT_UNKNOWN
    assert r.chosen is None
    assert _PALLOF in r.unknown_paths


def test_every_authorized_path_known_incompatible_is_not_feasible():
    r = resolve_slot(_SMITH_INCLINE, [_LEG_PRESS], _MAISON)
    assert r.state == NOT_FEASIBLE
    assert r.chosen is None


def test_an_empty_requirement_is_executable_even_with_nothing_declared():
    """§8 — la modalité poids du corps assumée reste faisable partout."""
    assert resolve_slot(_MOLLETS, [], ()).state == NATIVE_FEASIBLE
    assert resolve_slot(_MOLLETS, [], None).state == NATIVE_FEASIBLE


def test_an_undeclared_environment_never_refuses_it_only_doubts():
    """§12 et §18-G7 — l'utilisateur hérité porte `NULL` : il ne doit voir
    aucun refus."""
    r = resolve_slot(_SMITH_INCLINE, [_DB_INCLINE], None)
    assert r.state == SLOT_UNKNOWN
    assert r.state != NOT_FEASIBLE


def test_no_state_is_a_number():
    for etat in (NATIVE_FEASIBLE, ADAPTABLE, SLOT_UNKNOWN, NOT_FEASIBLE,
                 SERVABLE, TEMPLATE_UNKNOWN, TEMPLATE_NOT_FEASIBLE):
        assert isinstance(etat, str)


# ───────── §10 — le résolveur n'invente rien ─────────


def test_the_resolver_never_looks_beyond_the_list_it_was_given():
    """Le seul substitut autorisé est infaisable ; un autre exercice du
    catalogue le serait. Le résolveur ne doit pas aller le chercher."""
    r = resolve_slot(_SMITH_INCLINE, [_LEG_PRESS], _MAISON)
    assert r.chosen is None


def test_the_resolver_respects_the_order_it_was_given():
    """§10 — les priorités N1/N2/N3 ne sont pas recalculées ici : le PREMIER
    exécutable de la liste gagne."""
    premier = resolve_slot(_SMITH_INCLINE, [_DB_INCLINE, _MOLLETS], _MAISON)
    second = resolve_slot(_SMITH_INCLINE, [_MOLLETS, _DB_INCLINE], _MAISON)
    assert premier.chosen == _DB_INCLINE
    assert second.chosen == _MOLLETS


def test_an_empty_substitute_list_cannot_produce_an_adaptation():
    assert resolve_slot(_SMITH_INCLINE, [], _MAISON).state == NOT_FEASIBLE


# ───────── doublons — un défaut trouvé par le harnais de preuve ─────────


def test_a_substitute_already_used_is_avoided_when_another_one_works():
    r = resolve_slot(_SMITH_INCLINE, [_DB_INCLINE, _MOLLETS], _MAISON,
                     already_used={_DB_INCLINE})
    assert r.chosen == _MOLLETS
    assert r.duplicate is False


def test_a_duplicate_is_reused_rather_than_declaring_a_possible_thing_impossible():
    """Refuser ici annoncerait « infaisable » une exécution qui, elle, est
    possible. Le doublon est donc repris — et SIGNALÉ."""
    r = resolve_slot(_SMITH_INCLINE, [_DB_INCLINE], _MAISON,
                     already_used={_DB_INCLINE})
    assert r.state == ADAPTABLE
    assert r.chosen == _DB_INCLINE
    assert r.duplicate is True


def test_a_template_does_not_serve_the_same_exercise_twice_when_it_can_avoid_it():
    resolution = resolve_template(
        "labo",
        [(_SMITH_INCLINE, [_DB_INCLINE, _MOLLETS]),
         (_HIP_THRUST, [_DB_INCLINE, _MOLLETS])],
        _MAISON,
    )
    choisis = [s.chosen for s in resolution.slots]
    assert len(choisis) == len(set(choisis))


# ───────── §13 — les trois états de gabarit ─────────


def test_a_template_is_servable_when_every_slot_is_native_or_adaptable():
    r = resolve_template(
        "labo",
        [(_SMITH_INCLINE, [_DB_INCLINE]), (_MOLLETS, [])],
        _MAISON,
    )
    assert r.state == SERVABLE
    assert len(r.adapted_slots) == 1


def test_a_template_is_never_discarded_because_its_origin_is_incompatible():
    """§13, dernière phrase — c'est la garantie centrale."""
    r = resolve_template("labo", [(_SMITH_INCLINE, [_DB_INCLINE])], _MAISON)
    assert r.state == SERVABLE
    assert r.slots[0].chosen == _DB_INCLINE
    assert r.slots[0].prescribed == _SMITH_INCLINE


def test_one_unknown_slot_makes_the_template_unknown():
    r = resolve_template(
        "labo",
        [(_MOLLETS, []), (_SMITH_INCLINE, [_PALLOF])],
        _MAISON,
    )
    assert r.state == TEMPLATE_UNKNOWN


def test_one_impossible_slot_makes_the_template_not_feasible():
    r = resolve_template(
        "labo",
        [(_MOLLETS, []), (_SMITH_INCLINE, [_LEG_PRESS])],
        _MAISON,
    )
    assert r.state == TEMPLATE_NOT_FEASIBLE
    assert [s.prescribed for s in r.blocking_slots] == [_SMITH_INCLINE]


def test_impossible_beats_unknown_when_both_are_present():
    """Un gabarit dont un créneau est décisivement impossible n'est pas
    « peut-être » : il est infaisable, quoi qu'on ignore par ailleurs."""
    r = resolve_template(
        "labo",
        [(_SMITH_INCLINE, [_PALLOF]), (_HIP_THRUST, [_LEG_PRESS])],
        _MAISON,
    )
    assert r.state == TEMPLATE_NOT_FEASIBLE


# ───────── la curation couvre bien la clôture ─────────


def test_the_curation_declares_the_closure_it_measured():
    c = _curation()
    assert c["closure_size"] == 105
    assert c["prescribed_size"] == 68
    assert len(c["rows"]) == 105


def test_no_curated_row_is_silently_empty():
    """`null` = inconnu, `[]` = aucune exigence : deux faits, jamais
    confondus. Une ligne vide doit être un CHOIX motivé."""
    for nom, ligne in _curation()["rows"].items():
        if ligne["requirements"] == []:
            assert ligne["evidence_level"], nom
            assert ligne["source"], nom
