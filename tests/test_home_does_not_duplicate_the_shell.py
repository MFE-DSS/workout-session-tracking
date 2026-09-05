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


def _tile_routes() -> set[str]:
    src = re.sub(
        r"\{#.*?#\}", "", (TEMPLATES / "index.html").read_text(encoding="utf-8"),
        flags=re.DOTALL,
    )
    m = re.search(r'<div class="tile-grid">(.*?)</div>\s*</div>', src, re.DOTALL)
    assert m, "la grille de tuiles est introuvable dans index.html"
    return _routes_in(m.group(1))


def test_the_probe_finds_both_surfaces():
    """Garde de la garde : deux ensembles vides se croiseraient sans conflit,
    et le test passerait en annonçant l'absence de doublon."""
    shell, tiles = _shell_routes(), _tile_routes()
    assert len(shell) >= 3, f"seulement {len(shell)} destinations de coque lues"
    assert len(tiles) >= 2, f"seulement {len(tiles)} tuiles lues"


def test_no_home_tile_leads_where_the_shell_already_leads():
    """L'INVARIANT. Pas « trois tuiles » — aucune répétition.

    Épingler un nombre aurait interdit d'ajouter une destination utile ; ce
    qui est interdit, c'est de doubler un chemin qui existe déjà à l'écran.
    """
    doublons = sorted(_tile_routes() & _shell_routes())
    assert doublons == [], (
        f"l'accueil répète la coque : {doublons}. Ces destinations sont déjà "
        "dans la barre basse, visible sur le même écran — la tuile n'ajoute "
        "pas un accès, elle ajoute une répétition."
    )


def test_the_remaining_tiles_are_reachable_nowhere_else_in_the_shell():
    """Ce qui reste doit MÉRITER sa place.

    Une tuile qui survit parce qu'on ne l'a pas regardée est le prochain
    doublon. Chacune doit mener quelque part que la coque n'atteint pas.
    """
    tiles = _tile_routes()
    assert tiles, "toutes les tuiles ont disparu — c'est une soustraction, pas un tri"
    for route in sorted(tiles):
        assert route not in _shell_routes(), route


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
