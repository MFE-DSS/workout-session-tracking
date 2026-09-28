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
    NO_SERVABLE_CANDIDATE,
    NOT_FEASIBLE,
    SERVABLE,
    SLOT_UNKNOWN,
    TEMPLATE_NOT_FEASIBLE,
    TEMPLATE_UNKNOWN,
    adaptation_notice,
    identite_materielle_environnement,
    materialization_plan,
    resolve_catalogue,
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
    assert c["closure_size"] == 109
    assert c["prescribed_size"] == 72
    assert len(c["rows"]) == 109


def test_no_curated_row_is_silently_empty():
    """`null` = inconnu, `[]` = aucune exigence : deux faits, jamais
    confondus. Une ligne vide doit être un CHOIX motivé."""
    for nom, ligne in _curation()["rows"].items():
        if ligne["requirements"] == []:
            assert ligne["evidence_level"], nom
            assert ligne["source"], nom


# ───────── §17 / G4 — le contenu sans matériel ─────────

_SANS_MATERIEL = ("Pompes", "Squat au poids du corps", "Fente avant",
                  "Pont fessier")


def _split() -> dict:
    return json.loads(
        (_DATA / "reference_split.json").read_text(encoding="utf-8"))


def _gabarit_sans_materiel() -> dict:
    return next(t for t in _split()["templates"]
                if t["slug"] == "no-equipment-full-body")


def test_a_no_equipment_strength_template_is_live():
    """G4 — « live » : dans le catalogue servi, et jamais archivé."""
    t = _gabarit_sans_materiel()
    assert t["kind"] == "strength"
    assert t["catalog_section"] != "archived"
    assert len(t["exercises"]) == 4


def test_every_exercise_of_that_template_needs_no_external_equipment():
    from app.services.equipment_model import requirements_for_exercise

    for e in _gabarit_sans_materiel()["exercises"]:
        assert requirements_for_exercise(e["name"]) == (), e["name"]


def test_that_template_is_servable_with_nothing_declared_at_all():
    """La preuve que la porte G4 sert à quelque chose : dans un
    environnement explicitement vide, ce gabarit passe."""
    t = _gabarit_sans_materiel()
    creneaux = [(e["name"], e.get("substitutes") or []) for e in t["exercises"]]
    for env in ((), None):
        r = resolve_template(t["slug"], creneaux, env)
        assert r.state == SERVABLE, env
        assert all(s.state == NATIVE_FEASIBLE for s in r.slots)


def test_no_bodyweight_pulling_movement_was_invented():
    """§17 — l'interdiction est explicite. Aucun des quatre n'est un tirage,
    et le gabarit l'assume au lieu de combler pour la symétrie."""
    zones = {e["name"]: None for e in _gabarit_sans_materiel()["exercises"]}
    ekb = json.loads(
        (_DATA / "exercise_knowledge_base.json").read_text(encoding="utf-8"))
    for nom in zones:
        z = ekb["exercises"][nom]["zone_primary"]
        assert z not in ("lats", "upper_back"), nom


def test_the_existing_substitution_graph_was_not_broadened():
    """§10, vérifié par le MÉCANISME et non par une promesse.

    `_collect_n2_candidates` et `_collect_n3_zone_candidates` n'itèrent que
    `exercise_properties`. Y écrire une entrée créerait une arête pour tous
    les exercices de même pattern ou de même zone. Aucune des quatre
    identités neuves n'y est — donc aucune arête existante n'a bougé.
    """
    props = json.loads(
        (_DATA / "exercise_properties.json").read_text(encoding="utf-8"))
    assert len(props["exercises"]) == 69
    for nom in _SANS_MATERIEL:
        assert nom not in props["exercises"], nom


# ───────── §14, §15, G8 ─────────


def test_the_materialization_plan_carries_the_full_lineage():
    """§14 — le prescrit n'est pas effacé, il est porté à côté."""
    r = resolve_template(
        "labo",
        [(_MOLLETS, []), (_SMITH_INCLINE, [_DB_INCLINE])],
        _MAISON,
    )
    plan = materialization_plan(r)
    assert plan == ((2, _SMITH_INCLINE, _DB_INCLINE),)


def test_a_template_that_needed_no_adaptation_has_an_empty_plan():
    r = resolve_template("labo", [(_MOLLETS, [])], _MAISON)
    assert materialization_plan(r) == ()


def test_the_notice_is_a_fact_and_only_when_it_happened():
    """§15 — ni la liste, ni un décompte, et rien si rien n'a changé."""
    adapte = resolve_template(
        "labo", [(_SMITH_INCLINE, [_DB_INCLINE])], _MAISON)
    intact = resolve_template("labo", [(_MOLLETS, [])], _MAISON)
    assert adaptation_notice(adapte) == "Adapté à ton équipement."
    assert adaptation_notice(intact) is None


def test_no_servable_candidate_is_a_named_state_not_an_empty_list():
    """G8 — « rien à proposer » et « rien n'a été calculé » ne doivent pas
    se ressembler."""
    impossible = resolve_template(
        "labo", [(_SMITH_INCLINE, [_LEG_PRESS])], _MAISON)
    assert resolve_catalogue([impossible]).state == NO_SERVABLE_CANDIDATE
    assert resolve_catalogue([]).state == NO_SERVABLE_CANDIDATE


def test_a_doubt_still_lets_the_product_propose():
    incertain = resolve_template("labo", [(_SMITH_INCLINE, [_PALLOF])], _MAISON)
    assert resolve_catalogue([incertain]).state == TEMPLATE_UNKNOWN


def test_one_servable_candidate_is_enough():
    servable = resolve_template("labo", [(_MOLLETS, [])], _MAISON)
    impossible = resolve_template(
        "labo", [(_SMITH_INCLINE, [_LEG_PRESS])], _MAISON)
    c = resolve_catalogue([servable, impossible])
    assert c.state == SERVABLE
    assert len(c.not_feasible) == 1


# ───────── §16 / G9 — l'empreinte n'est pas encore environnementale ─────────


def test_the_advice_memory_fingerprint_ignores_the_environment_today():
    """§16 — tant que le résolveur n'affecte pas le résultat servi,
    l'environnement n'entre PAS dans l'empreinte. Vérifié par AST sur la
    fonction elle-même, pas par relecture."""
    import ast

    source = (Path(__file__).resolve().parents[1]
              / "app" / "services" / "advice_memory.py").read_text(
                  encoding="utf-8")
    arbre = ast.parse(source)
    fn = next(n for n in ast.walk(arbre)
              if isinstance(n, ast.FunctionDef)
              and n.name == "empreinte_de_contexte")
    corps = ast.dump(fn)
    for interdit in ("available_equipment", "equipment_items",
                     "environment_resolution", "equipment_model"):
        assert interdit not in corps, interdit


def test_the_material_identity_ignores_equipment_that_changed_nothing():
    """G9 — ajouter une machine qu'aucun créneau n'utilise ne doit pas
    périmer un refus."""
    creneaux = [(_MOLLETS, []), (_SMITH_INCLINE, [_DB_INCLINE])]
    maigre = resolve_template("labo", creneaux, _MAISON)
    enrichi = resolve_template(
        "labo", creneaux, (*_MAISON, "leg_press", "butterfly_machine"))
    assert (identite_materielle_environnement([maigre])
            == identite_materielle_environnement([enrichi]))


def test_the_material_identity_changes_when_an_execution_changes():
    creneaux = [(_SMITH_INCLINE, [_DB_INCLINE])]
    adapte = resolve_template("labo", creneaux, _MAISON)
    natif = resolve_template("labo", creneaux, _AVEC_SMITH)
    assert (identite_materielle_environnement([adapte])
            != identite_materielle_environnement([natif]))
