"""`Sb_TRAIN_A_ENVIRONMENT_ACTIVATION_01` — la frontière d'activation.

Les gardes portent sur le **comportement servi**, jamais sur une chaîne de
code. Chacune a été écrite ROUGE avant le service qu'elle décrit.

Le fait le plus important est le premier : sur un environnement `NULL` — ce
que porte **tout** utilisateur actuel — le chemin servi doit être identique
au bit près à celui d'avant. Mesuré : sans cette règle, la porte retirerait
16 gabarits sur 18.
"""
from __future__ import annotations

import ast
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.services.environment_activation import (
    CandidatsEnvironnement,
    filtrer_par_environnement,
    identite_pour_empreinte,
    plan_de_materialisation,
)
from app.services.environment_resolution import NO_SERVABLE_CANDIDATE

_ROOT = Path(__file__).resolve().parents[1]

# Identités réelles du catalogue, jamais inventées.
_SMITH_INCLINE = "Incline Smith Press"
_DB_INCLINE = "Développé incliné haltères 30°"
_MOLLETS = "Relevés mollets debout"
_PALLOF = "Pallof press câble"
_LEG_PRESS = "Leg Press (pieds bas)"

_MAISON = ("adjustable_bench", "dumbbells")


class _Faux:
    """Un candidat minimal : le filtre ne lit que le slug et les créneaux."""

    def __init__(self, slug, creneaux):
        self.slug = slug
        self.creneaux = creneaux


def _candidats(*paires):
    return [_Faux(slug, creneaux) for slug, creneaux in paires]


def _creneaux(*paires):
    return list(paires)


# ───────── §1 / G7 — l'environnement non déclaré ne filtre RIEN ─────────


def test_an_undeclared_environment_changes_nothing_at_all():
    """Le cas de TOUS les utilisateurs actuels.

    Sans cette règle, la porte retirerait 16 gabarits sur 18 — mesuré. Ce
    n'est pas une précaution, c'est la seule lecture compatible avec `G7`
    et avec « effective DECLARED environment ».
    """
    entree = _candidats(
        ("push-a", _creneaux((_SMITH_INCLINE, [_DB_INCLINE]))),
        ("legs-a", _creneaux((_LEG_PRESS, []))),
    )
    sortie = filtrer_par_environnement(entree, None)
    assert sortie.actif is False
    assert sortie.candidats == entree
    assert sortie.adaptations == {}
    assert sortie.etat_catalogue is None


def test_an_undeclared_environment_preserves_order_identically():
    entree = _candidats(
        ("a", _creneaux((_MOLLETS, []))),
        ("b", _creneaux((_LEG_PRESS, []))),
        ("c", _creneaux((_SMITH_INCLINE, []))),
    )
    sortie = filtrer_par_environnement(entree, None)
    assert [c.slug for c in sortie.candidats] == ["a", "b", "c"]


# ───────── §1.A — seul le prouvé gagne ─────────


def test_a_declared_environment_keeps_only_servable_candidates():
    entree = _candidats(
        ("impossible", _creneaux((_LEG_PRESS, []))),
        ("servable", _creneaux((_MOLLETS, []))),
    )
    sortie = filtrer_par_environnement(entree, _MAISON)
    assert sortie.actif is True
    assert [c.slug for c in sortie.candidats] == ["servable"]


def test_a_not_feasible_candidate_can_never_win():
    entree = _candidats(("impossible", _creneaux((_LEG_PRESS, []))))
    sortie = filtrer_par_environnement(entree, _MAISON)
    assert sortie.candidats == []


def test_the_surviving_order_is_the_engine_order_untouched():
    """La porte RETIRE, elle ne reclasse pas. Sans quoi elle deviendrait une
    seconde politique de recommandation."""
    entree = _candidats(
        ("premier", _creneaux((_MOLLETS, []))),
        ("impossible", _creneaux((_LEG_PRESS, []))),
        ("second", _creneaux((_SMITH_INCLINE, [_DB_INCLINE]))),
    )
    sortie = filtrer_par_environnement(entree, _MAISON)
    assert [c.slug for c in sortie.candidats] == ["premier", "second"]


def test_an_adaptable_candidate_survives_and_is_annotated():
    entree = _candidats(("adapte", _creneaux((_SMITH_INCLINE, [_DB_INCLINE]))))
    sortie = filtrer_par_environnement(entree, _MAISON)
    assert [c.slug for c in sortie.candidats] == ["adapte"]
    assert sortie.adaptations["adapte"] == ((1, _SMITH_INCLINE, _DB_INCLINE),)


# ───────── §1.B — l'incertitude n'est pas une impossibilité ─────────


def test_when_nothing_is_provable_the_legacy_list_is_preserved():
    """Zéro servable mais au moins un inconnu : on ne fabrique pas de
    faisabilité, et on ne bloque pas non plus."""
    entree = _candidats(("incertain", _creneaux((_PALLOF, []))))
    sortie = filtrer_par_environnement(entree, _MAISON)
    assert [c.slug for c in sortie.candidats] == ["incertain"]
    assert sortie.adaptations == {}


def test_an_unknown_path_is_never_reported_as_feasible():
    entree = _candidats(("incertain", _creneaux((_PALLOF, []))))
    sortie = filtrer_par_environnement(entree, _MAISON)
    assert sortie.etat_catalogue != "servable"


def test_no_unproven_substitution_is_ever_materialized():
    entree = _candidats(("incertain", _creneaux((_SMITH_INCLINE, [_PALLOF]))))
    sortie = filtrer_par_environnement(entree, _MAISON)
    assert sortie.adaptations == {}


# ───────── §1.C — le vrai cas bloqué ─────────


def test_zero_servable_and_zero_unknown_reaches_the_blocked_state():
    entree = _candidats(("impossible", _creneaux((_LEG_PRESS, []))))
    sortie = filtrer_par_environnement(entree, _MAISON)
    assert sortie.etat_catalogue == NO_SERVABLE_CANDIDATE
    assert sortie.candidats == []


def test_the_blocked_state_is_distinct_from_an_empty_calculation():
    """« rien à proposer » et « rien n'a été calculé » ne doivent pas se
    ressembler : l'un porte un état nommé, l'autre non."""
    bloque = filtrer_par_environnement(
        _candidats(("x", _creneaux((_LEG_PRESS, [])))), _MAISON)
    inerte = filtrer_par_environnement([], None)
    assert bloque.etat_catalogue == NO_SERVABLE_CANDIDATE
    assert inerte.etat_catalogue is None


# ───────── §10 — rien n'est inventé ─────────


def test_an_unauthorized_but_feasible_exercise_is_never_selected():
    """`Relevés mollets debout` est exécutable partout, mais il n'est PAS
    dans la liste autorisée de ce créneau. Il ne doit jamais être retenu."""
    entree = _candidats(("x", _creneaux((_SMITH_INCLINE, [_LEG_PRESS]))))
    sortie = filtrer_par_environnement(entree, _MAISON)
    assert sortie.adaptations == {}
    assert sortie.candidats == []


def test_the_first_authorized_executable_wins_and_priority_is_not_recomputed():
    entree = _candidats(
        ("x", _creneaux((_SMITH_INCLINE, [_DB_INCLINE, _MOLLETS]))))
    assert filtrer_par_environnement(entree, _MAISON).adaptations["x"] == (
        (1, _SMITH_INCLINE, _DB_INCLINE),)


# ───────── §2 / G6 — le plan de matérialisation ─────────


def test_the_plan_names_position_planned_and_executed():
    entree = _candidats(
        ("x", _creneaux((_MOLLETS, []), (_SMITH_INCLINE, [_DB_INCLINE]))))
    sortie = filtrer_par_environnement(entree, _MAISON)
    assert plan_de_materialisation(sortie, "x") == (
        (2, _SMITH_INCLINE, _DB_INCLINE),)


def test_a_template_without_adaptation_has_an_empty_plan():
    entree = _candidats(("x", _creneaux((_MOLLETS, []))))
    sortie = filtrer_par_environnement(entree, _MAISON)
    assert plan_de_materialisation(sortie, "x") == ()


def test_an_inactive_gate_never_produces_a_plan():
    entree = _candidats(("x", _creneaux((_SMITH_INCLINE, [_DB_INCLINE]))))
    sortie = filtrer_par_environnement(entree, None)
    assert plan_de_materialisation(sortie, "x") == ()


# ───────── §6 / G9 — l'identité matérielle ─────────


def test_equipment_that_changed_no_execution_does_not_change_the_identity():
    creneaux = _creneaux((_MOLLETS, []), (_SMITH_INCLINE, [_DB_INCLINE]))
    maigre = filtrer_par_environnement(_candidats(("x", creneaux)), _MAISON)
    enrichi = filtrer_par_environnement(
        _candidats(("x", creneaux)),
        (*_MAISON, "leg_press", "butterfly_machine"))
    assert identite_pour_empreinte(maigre) == identite_pour_empreinte(enrichi)


def test_equipment_that_changed_an_execution_changes_the_identity():
    creneaux = _creneaux((_SMITH_INCLINE, [_DB_INCLINE]))
    adapte = filtrer_par_environnement(_candidats(("x", creneaux)), _MAISON)
    natif = filtrer_par_environnement(
        _candidats(("x", creneaux)), (*_MAISON, "smith_machine"))
    assert identite_pour_empreinte(adapte) != identite_pour_empreinte(natif)


def test_an_inactive_gate_contributes_nothing_to_the_fingerprint():
    """`G9` — l'empreinte ne devient environnementale qu'à l'activation
    CAUSALE. Un utilisateur `NULL` ne doit pas voir ses refus périmer."""
    entree = _candidats(("x", _creneaux((_SMITH_INCLINE, [_DB_INCLINE]))))
    assert identite_pour_empreinte(
        filtrer_par_environnement(entree, None)) is None


# ───────── le résolveur est UNIQUE ─────────


def test_no_second_resolver_was_introduced():
    """§0 — « NO second resolver ». Le module d'activation doit consommer
    `environment_resolution`, jamais réimplémenter un verdict."""
    src = (_ROOT / "app" / "services" / "environment_activation.py").read_text(
        encoding="utf-8")
    arbre = ast.parse(src)
    importe = {n.module for n in ast.walk(arbre)
               if isinstance(n, ast.ImportFrom) and n.module}
    assert any("environment_resolution" in m for m in importe)
    # Aucune constante d'état redéfinie ici : elles viennent du résolveur.
    assignes = {t.id for n in ast.walk(arbre)
                if isinstance(n, ast.Assign)
                for t in n.targets if isinstance(t, ast.Name)}
    for interdit in ("SERVABLE", "NATIVE_FEASIBLE", "ADAPTABLE",
                     "NOT_FEASIBLE", "NO_SERVABLE_CANDIDATE"):
        assert interdit not in assignes, interdit


def test_the_gate_result_carries_no_numeric_score():
    sortie = filtrer_par_environnement(
        _candidats(("x", _creneaux((_MOLLETS, [])))), _MAISON)
    assert isinstance(sortie, CandidatsEnvironnement)
    for valeur in (sortie.etat_catalogue,):
        if valeur is not None:
            with pytest.raises(ValueError):
                float(valeur)


def test_the_clock_is_not_read_by_the_gate():
    """La porte ne dépend d'aucun temps : deux appels identiques rendent la
    même chose, sinon une empreinte périmerait toute seule."""
    entree = _candidats(("x", _creneaux((_SMITH_INCLINE, [_DB_INCLINE]))))
    avant = identite_pour_empreinte(filtrer_par_environnement(entree, _MAISON))
    datetime.now(UTC)
    apres = identite_pour_empreinte(filtrer_par_environnement(entree, _MAISON))
    assert avant == apres
