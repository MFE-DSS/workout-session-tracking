"""Contrat de la garde de débordement horizontal (`POST_CONVERGENCE_INTEGRITY_01` / A).

CE QUE CE FICHIER PEUT ET NE PEUT PAS VÉRIFIER
-----------------------------------------------
La garde elle-même est **rendue** : elle ouvre un navigateur et mesure. Elle ne
peut donc pas tourner ici — Playwright n'est ni dans `requirements.txt` ni dans
le workflow CI, et l'y mettre est une décision `ci_infra` qui n'appartient pas
à cette tranche.

Ce fichier vérifie donc **le contrat**, pas le résultat :

  · la garde existe et est exécutable ;
  · elle déclare les deux paliers de largeurs exigés ;
  · elle **découvre** ses surfaces par parcours, et non par une liste écrite à
    la main — c'est le point qui compte le plus ;
  · chaque exclusion porte une raison.

POURQUOI LE PARCOURS EST LE POINT QUI COMPTE. Le débordement de `/` a survécu
des mois derrière une carte de treize surfaces choisies à la main. Une liste
mesure ce à quoi on pense. Si la garde régresse un jour vers une liste, elle
recommencera à ne pas voir ce qu'on oublie — et elle sera verte en le faisant.
"""
from __future__ import annotations

import ast
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
GATE = ROOT / "scripts/check_overflow.py"


def _module() -> ast.Module:
    return ast.parse(GATE.read_text(encoding="utf-8"))


def _assign(name: str):
    for node in _module().body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return ast.literal_eval(node.value)
    raise AssertionError(f"{name} absent de {GATE.name}")


def test_the_gate_exists_and_parses():
    assert GATE.exists(), "la garde de débordement a disparu"
    _module()


def test_every_reachable_surface_is_checked_at_both_shell_widths():
    """390 px et 1024 px encadrent le basculement de coque — le rail latéral
    apparaît à 1024, et c'est exactement là que le défaut vivait."""
    assert _assign("WIDTHS_ALL") == (390, 1024)


def test_sovereign_surfaces_are_checked_across_the_whole_scale():
    """Une dérive sur une surface souveraine est une régression. `/` a prouvé
    qu'un palier non mesuré est un palier non tenu."""
    assert _assign("WIDTHS_SOVEREIGN") == (360, 390, 430, 768, 1024, 1280)


def test_the_sovereign_set_matches_the_blueprint():
    """`AUREN_UI_BLUEPRINT` déclare Accueil et Séance `SOVEREIGN`."""
    sovereign = _assign("SOVEREIGN")
    assert "/" in sovereign
    assert any(s.startswith("/sessions/") for s in sovereign)


def test_the_gate_discovers_surfaces_by_crawling_not_by_a_hand_list():
    """LA GARDE DE LA GARDE.

    Le défaut de `/` a survécu derrière une carte de treize surfaces choisies à
    la main. Si ce script régresse vers une liste, il recommencera à ne pas
    voir ce qu'on oublie — en restant vert.
    """
    src = GATE.read_text(encoding="utf-8")
    assert "def _discover" in src
    # Un parcours, ça suit les liens et ça maintient une file.
    assert "a[href]" in src
    assert "deque" in src


def test_every_exclusion_states_a_reason():
    """Une exclusion nommée n'est pas une dette cachée ; un `skip` silencieux
    en serait une."""
    excluded = _assign("EXCLUDED")
    assert excluded, "plus aucune exclusion — le dictionnaire a-t-il changé de forme ?"
    for path, reason in excluded.items():
        assert path.startswith("/"), path
        assert len(reason) >= 8, f"raison trop vague pour {path} : {reason!r}"


def test_the_gate_says_where_it_runs_and_where_it_does_not():
    """Une garde qui ne tourne pas en CI doit le DIRE, sinon la prochaine
    tranche la croira active et s'appuiera dessus."""
    head = GATE.read_text(encoding="utf-8")[:3000]
    assert "ne tourne donc PAS en intégration continue" in head
    assert "Playwright" in head


def test_the_gate_aborts_rather_than_measure_the_login_page():
    """Un cookie refusé rend `/login` SANS échouer. Trois de mes sondes ont
    déjà mesuré la mauvaise page en silence."""
    src = GATE.read_text(encoding="utf-8")
    assert "/login" in src
    assert "ABANDON" in src
