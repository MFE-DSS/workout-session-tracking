"""L'accueil ne répète pas la coque.

POURQUOI CETTE GARDE EXISTE
---------------------------
L'accueil portait une grille de CINQ tuiles de navigation. Deux d'entre elles —
« Progression » et « Programmes » — mènent exactement où mène la **barre de
navigation basse**, qui est visible *sur le même écran, en permanence*.

Le produit proposait donc deux fois la même destination, à trois centimètres
de distance, dans deux formats différents. Rien ne le signalait : chacune des
deux surfaces est correcte prise isolément, et c'est leur COEXISTENCE qui est
le défaut.

Ce n'est pas une soustraction (`§5.3`) : les deux destinations restent
atteignables, par le chemin que l'utilisateur emprunte déjà partout ailleurs.
Ce qui est retiré est la répétition, pas l'accès.

**L'invariant gardé n'est pas « il y a trois tuiles »** — ce serait épingler
un nombre. C'est : *aucune tuile de l'accueil ne mène là où la coque mène
déjà*. Il survit à l'ajout d'une destination comme à son retrait.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "app" / "templates"


def _routes_in(fragment: str) -> set[str]:
    return set(re.findall(r"url_for\(\s*['\"]([a-z_]+)['\"]", fragment))


def _shell_routes() -> set[str]:
    """Les destinations de la barre basse, lues dans `base.html`."""
    src = re.sub(
        r"\{#.*?#\}", "", (TEMPLATES / "base.html").read_text(encoding="utf-8"),
        flags=re.DOTALL,
    )
    m = re.search(r'<nav[^>]*class="[^"]*app-bottom-nav[^"]*"(.*?)</nav>', src, re.DOTALL)
    assert m, "la barre de navigation basse est introuvable dans base.html"
    return _routes_in(m.group(1))


def _shell_labels() -> list[str]:
    """Les NOMS visibles de la barre basse — « Séance », « Progression »…

    Nécessaires parce que la règle affinée porte sur le LIBELLÉ : une sortie
    qui reprend le nom d'un onglet est un doublon de navigation, même si elle
    se termine par un point d'interrogation.
    """
    src = re.sub(
        r"\{#.*?#\}", "", (TEMPLATES / "base.html").read_text(encoding="utf-8"),
        flags=re.DOTALL,
    )
    m = re.search(
        r'<nav[^>]*class="[^"]*app-bottom-nav[^"]*"(.*?)</nav>', src, re.DOTALL)
    assert m, "la barre de navigation basse est introuvable dans base.html"
    noms = re.findall(
        r'class="app-bottom-nav__label"[^>]*>([^<]+)<', m.group(1))
    assert noms, "aucun libellé d'onglet lu — la sonde ne mesure rien"
    return [n.strip() for n in noms]


def _exits() -> list[tuple[str, str]]:
    """Les sorties de l'accueil : (libellé visible, route).

    ⚠ `UI-CP3` — la grille de tuiles a disparu ; l'accueil porte désormais un
    RAIL DE TRANSITION daté. La sonde suit l'objet, pas son ancien nom : une
    sonde qui continuerait de chercher `tile-grid` échouerait sur son propre
    `assert`, ce qui ressemble à une garde vivante et n'en est plus une.
    """
    src = re.sub(
        r"\{#.*?#\}", "", (TEMPLATES / "index.html").read_text(encoding="utf-8"),
        flags=re.DOTALL,
    )
    m = re.search(
        r'<nav class="mission-bridge".*?</nav>', src, re.DOTALL)
    assert m, "le rail de transition est introuvable dans index.html"
    sorties = []
    for bloc in re.findall(r"<a\s[^>]*>.*?</a>", m.group(0), re.DOTALL):
        route = _routes_in(bloc)
        libelle = re.sub(r"<[^>]+>", " ", bloc)
        libelle = re.sub(r"\s+", " ", libelle).replace("\xa0", " ").strip()
        for r in route:
            sorties.append((libelle, r))
    assert sorties, "aucune sortie lue dans le rail"
    return sorties


def _exit_routes() -> set[str]:
    return {route for _, route in _exits()}


def test_the_probe_finds_both_surfaces():
    """Garde de la garde : deux ensembles vides se croiseraient sans conflit,
    et le test passerait en annonçant l'absence de doublon."""
    shell, sorties = _shell_routes(), _exit_routes()
    assert len(shell) >= 3, f"seulement {len(shell)} destinations de coque lues"
    assert len(sorties) >= 2, f"seulement {len(sorties)} sorties lues"


def test_no_home_exit_repeats_the_shell_by_name():
    """⚠ L'INVARIANT EST RAFFINÉ PAR `UI-CP3 §6`, PAS LEVÉ.

    Ce que la mesure d'origine a établi, et qui reste vrai : deux tuiles
    nommées « Progression » et « Programmes » répétaient, en plus gros et à
    trois centimètres, ce que la barre basse montrait déjà. Elles
    n'ajoutaient pas un accès, elles ajoutaient du bruit.

    Ce que `UI-CP3` change : MISSION ne possède plus « qu'est-ce qui a
    changé ? » ni « où en est mon corps ? ». Les blocs qui y répondaient
    QUITTENT la surface, et laissent une adresse de réexpédition. Cette
    adresse mène forcément vers une destination de la coque — c'est là que
    vit la réponse.

    La règle affinée, et testable : une sortie de l'accueil peut partager une
    destination de la coque **à condition d'être nommée par la QUESTION**
    qu'elle sert, jamais par le nom de la destination. « Progression » est un
    doublon de navigation ; « Qu'est-ce qui a changé ? » est un renvoi de
    contenu.

    ⚠ SIGNALÉ À L'OPÉRATEUR : cette garde reposait sur une MESURE, et
    l'affiner est un arbitrage, pas une évidence. Consigné dans le rapport de
    tranche.
    """
    for libelle, route in _exits():
        if route not in _shell_routes():
            continue
        assert "?" in libelle, (
            f"« {libelle} » mène vers {route}, déjà dans la barre basse, et "
            "n'est pas nommée par une question — c'est un doublon de "
            "navigation, pas un renvoi de contenu."
        )
        for nom_coque in _shell_labels():
            assert nom_coque.lower() not in libelle.lower(), (
                f"« {libelle} » reprend le nom de la coque « {nom_coque} » : "
                "un renvoi se nomme par sa question, pas par sa destination."
            )


def test_every_remaining_exit_answers_a_question():
    """Ce qui reste doit MÉRITER sa place.

    Une sortie qui survit parce qu'on ne l'a pas regardée est le prochain
    doublon. Chacune doit désigner une question que MISSION ne possède plus —
    et c'est le point d'arrêt du pont : quand `FLIGHT_RECORDER` répondra à
    « qu'est-ce qui a changé ? », la sortie n'aura plus de raison d'être.
    """
    sorties = _exits()
    assert sorties, (
        "toutes les sorties ont disparu — c'est une soustraction, pas un tri"
    )
    for libelle, _ in sorties:
        assert "?" in libelle, (
            f"« {libelle} » ne pose pas de question : elle redevient une tuile"
        )


def test_the_removed_destinations_are_still_reachable(client):
    """`§5.3` — retirer la répétition, jamais l'accès.

    Le test le plus important du fichier : il vérifie que la coque tient bien
    la promesse au nom de laquelle on a retiré les tuiles.
    """
    body = client.get("/").text
    for route, libelle in (("/progress", "Progression"), ("/library", "Programmes")):
        assert route in body, (
            f"{route} n'est plus atteignable depuis l'accueil — la tuile a été "
            f"retirée SANS que la coque la remplace ({libelle})"
        )
