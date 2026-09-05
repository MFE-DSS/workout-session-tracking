"""Une couleur déclarée retirée ne doit plus être rendue.

POURQUOI CETTE GARDE EXISTE
---------------------------
`Sb_UI_02b` déclare DEUX accents retirés, et le dit dans `app.css` :

    « L'ancien thème dark/orange (#f25f3a) est retiré. »
    « Accent AMBRE unique (remplace l'orange #f25f3a) »
    « Ancien accent teal retiré » (`session_focus.css`)

**La déclaration était dans un commentaire ; la migration n'a jamais été
finie.** Les deux couleurs continuaient d'être rendues dans cinq fichiers,
dix-neuf fois — dont l'accueil public, c'est-à-dire le premier écran qu'un
inconnu voit.

LE DÉFAUT VISIBLE QUI EN RÉSULTAIT EST PIRE QU'UNE COULEUR PÉRIMÉE. La légende
du graphique de Progression emploie `--accent` (ambre) et `--fg-muted` (gris) ;
le graphique, lui, dessinait en orange et en teal. **Le produit affichait une
légende qui ne décrivait pas son propre graphique** : « Musculation » en ambre
dans la légende, en orange dans la courbe.

Le correctif ne recopie pas l'ambre : il fait consommer au graphique **les
tokens de sa légende**. Deux hex identiques divergent au premier changement de
palette ; deux `var()` non.

Mesuré : l'ambre contraste MIEUX que l'orange sur les quatre fonds réels
(7,24 contre 5,37 sur `#161a22`). Le remplacement n'est pas un compromis.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app"

#: Accent retiré → la déclaration qui l'a retiré.
RETIRED = {
    "#f25f3a": "`Sb_UI_02b` — « l'ancien thème dark/orange est retiré »",
    "#38b2ac": "`Sb_UI_02b` / `OQ-02b-A` — « ancien accent teal retiré »",
}

#: Extensions où une couleur est RENDUE. Un `.md` peut la citer sans la rendre.
RENDERED = (".py", ".html", ".css", ".svg", ".js")


def _live_occurrences(needle: str) -> list[str]:
    """Occurrences RENDUES, commentaires exclus.

    Une prose qui explique le retrait cite forcément la valeur retirée — c'est
    la douzième fois que ce dépôt rencontre ce motif, et la garde qui échoue
    sur sa propre explication est un classique. On retire donc les commentaires
    de chaque langage avant de chercher.
    """
    out = []
    for p in sorted(APP.rglob("*")):
        if p.suffix not in RENDERED or not p.is_file():
            continue
        src = p.read_text(encoding="utf-8", errors="ignore")
        src = re.sub(r"\{#.*?#\}", "", src, flags=re.DOTALL)      # Jinja
        src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)      # CSS / JS
        src = re.sub(r"<!--.*?-->", "", src, flags=re.DOTALL)     # HTML / SVG
        src = re.sub(r"(?m)^\s*#.*$", "", src)                    # Python
        src = re.sub(r"(?m)//.*$", "", src)                       # JS
        if needle in src:
            out.append(f"{p.relative_to(APP)} × {src.count(needle)}")
    return out


def test_the_probe_still_finds_the_prose_it_must_ignore():
    """Garde de la garde.

    Si le filtrage des commentaires devenait trop large — par exemple en
    supprimant tout le fichier — la recherche ne trouverait plus rien et la
    garde passerait à vide. On vérifie que la valeur EXISTE bien quelque part,
    en commentaire, et n'est simplement plus rendue.
    """
    brut = [
        p for p in APP.rglob("*")
        if p.suffix in RENDERED and p.is_file()
        and "#f25f3a" in p.read_text(encoding="utf-8", errors="ignore")
    ]
    assert brut, (
        "la valeur retirée n'apparaît nulle part, même en prose — le filtre "
        "de commentaires a probablement tout mangé, et les tests ci-dessous "
        "ne prouvent plus rien"
    )


@pytest.mark.parametrize("hexa", sorted(RETIRED))
def test_no_retired_accent_is_still_rendered(hexa):
    """L'invariant : ce qui est déclaré retiré ne se rend plus."""
    live = _live_occurrences(hexa)
    assert live == [], (
        f"{hexa} est encore RENDU — {RETIRED[hexa]} — dans : {live}"
    )


def test_the_chart_consumes_the_tokens_of_its_own_legend():
    """LE DÉFAUT VISIBLE, énoncé comme propriété.

    Pas « le graphique est ambre » — ce serait épingler une valeur, et la
    divergence reviendrait au premier changement de palette. Ce qui est gardé,
    c'est que le graphique et sa légende lisent **le même token**.
    """
    timeline = (APP / "services/timeline.py").read_text(encoding="utf-8")
    css = (APP / "static/css/app.css").read_text(encoding="utf-8")

    legende = dict(
        re.findall(
            r"\.timeline-legend__dot--(\w+)\s*\{\s*background:\s*var\((--[\w-]+)\)",
            css,
        )
    )
    assert legende, "la légende ne lit plus de token — comparaison impossible"

    m = re.search(r"KIND_COLORS[^=]*=\s*\{(.*?)\}", timeline, re.DOTALL)
    assert m, "la palette du graphique est introuvable"
    graphe = dict(re.findall(r'"(\w+)"\s*:\s*"var\((--[\w-]+)\)"', m.group(1)))

    assert graphe, (
        "le graphique n'emploie plus de token : il ne peut plus suivre sa "
        "légende, et les deux divergeront en silence"
    )
    for kind, token in legende.items():
        assert graphe.get(kind) == token, (
            f"« {kind} » : la légende dit {token}, le graphique dit "
            f"{graphe.get(kind)} — la légende ne décrit pas le graphique"
        )


def test_the_public_landing_speaks_french(client):
    """L'accroche — la PREMIÈRE phrase qu'un inconnu lit — était en anglais.

    « Private bodybuilding tracking cockpit. » sur un produit dont chaque
    autre écran est en français. Quatrième anglicisme de la série, et le plus
    exposé.
    """
    client.cookies.clear()
    body = client.get("/welcome").text
    for anglicisme in ("Private bodybuilding", "data end-to-end"):
        assert anglicisme not in body, f"« {anglicisme} » est encore à l'écran"
    assert "cockpit" in body.lower(), (
        "« cockpit » a disparu — c'est le mot du produit (`L-01`, `PH-01`), "
        "pas un anglicisme de commodité"
    )
