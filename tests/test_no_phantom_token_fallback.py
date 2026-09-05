"""Aucun repli ne doit peindre à la place d'un token qui n'existe pas.

`CLAUDE.md §5.4` l'interdit nommément :

> **Interdit** : `var(--token-inexistant, #hex)` — le repli masque l'absence.

Le mécanisme est sournois parce qu'il **fonctionne**. Rien ne casse, rien ne
s'affiche en noir : une couleur est bien peinte. Simplement, ce n'est pas celle
de la palette, elle n'a jamais été mesurée sur le fond réel, et elle vient
souvent d'une génération antérieure du produit.

Mesuré au moment d'écrire cette garde : **166 replis** dans la feuille, dont
**150 morts** — le token existe, le repli ne se déclenche jamais. Ceux-là sont
de la dette de style, pas un défaut visuel. Les **16 autres** peignaient
réellement, et deux d'entre eux étaient de vrais défauts :

* `--success` → `#2e7d32` à **3,41:1** sur la surface, sous AA, alors que
  `--ok` existait à 5,69:1 ;
* `--bg-elev` → un voile **noir** sur un produit sombre : l'élément rendu plus
  sombre que sa surface, quand son nom dit « élevé ».

La garde ne traque donc QUE les tokens fantômes. Elle laisse les replis morts
tranquilles : les compter comme des fautes noierait les deux défauts réels dans
cent-cinquante broutilles — c'est la leçon des findings jumelles, prise à
l'envers.
"""
from __future__ import annotations

import re
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
CSS = RACINE / "app" / "static" / "css"
GABARITS = RACINE / "app" / "templates"

_DEFINITION = re.compile(r"^\s*(--[a-z0-9-]+)\s*:", re.M)
_USAGE_AVEC_REPLI = re.compile(r"var\(\s*(--[a-z0-9-]+)\s*,")

#: Fantômes tolérés, chacun avec la raison qui le tolère. Un repli n'entre ici
#: que s'il est INOFFENSIF ou INTOUCHABLE — jamais parce qu'il est pénible.
EXEMPTES: dict[str, str] = {
    "app.css::--mf-frames": (
        "ce n'est pas une couleur mais un COMPTEUR de cadres du filmstrip "
        "BodyMap — `calc(var(--mf-frames, 1) * 100%)`. Un cadre est le bon "
        "défaut quand la variable n'est pas posée par le gabarit."
    ),
    "session_focus.css::--bg-elev": (
        "feuille du viseur intra-séance, seul objet validé au rendu par "
        "l'opérateur. Toucher sa couleur, c'est le modifier sans exposition."
    ),
    "session_focus.css::--t-fg-dim": (
        "même feuille, même raison. Son repli est `var(--fg-dim)`, un token "
        "réel : le rendu est correct, seule l'indirection est douteuse."
    ),
}


def _tokens_definis() -> set[str]:
    definis: set[str] = set()
    for f in CSS.rglob("*.css"):
        definis |= set(_DEFINITION.findall(f.read_text(encoding="utf-8")))
    return definis


def _fantomes() -> dict[str, int]:
    """Rend {« fichier::--token »: occurrences} pour les tokens jamais définis."""
    definis = _tokens_definis()
    trouves: dict[str, int] = {}
    for f in [*CSS.rglob("*.css"), *GABARITS.rglob("*.html")]:
        for token in _USAGE_AVEC_REPLI.findall(f.read_text(encoding="utf-8")):
            if token not in definis:
                trouves[f"{f.name}::{token}"] = trouves.get(f"{f.name}::{token}", 0) + 1
    return trouves


def test_aucun_repli_ne_peint_a_la_place_dun_token_absent():
    restants = {c: n for c, n in _fantomes().items() if c not in EXEMPTES}
    assert not restants, (
        "des replis peignent à la place de tokens qui n'existent pas — "
        "`CLAUDE.md §5.4`. Soit le token est déclaré avec son contraste mesuré "
        "sur le fond réel, soit l'usage pointe vers le token qui porte déjà "
        f"cette sémantique : {restants}"
    )


def test_la_sonde_voit_bien_les_deux_formes():
    """Garde de la garde : la sonde reconnaît-elle encore un fantôme ?

    Une garde qui ne trouve rien parce que sa regex a cessé de mordre est
    indiscernable d'une garde satisfaite. On lui plante les deux écritures
    réellement rencontrées — repli hexadécimal et repli `var()` imbriqué.
    """
    definis = {"--reel"}
    faux = "a { color: var(--fantome, #2e7d32); background: var(--absent, var(--reel)); }"
    vus = [t for t in _USAGE_AVEC_REPLI.findall(faux) if t not in definis]
    assert vus == ["--fantome", "--absent"], (
        f"la sonde ne reconnaît plus les deux formes de repli : {vus}"
    )


def test_aucune_exemption_perimee():
    """Une exemption qui ne correspond plus à rien doit disparaître.

    Sans ce test, la liste devient un cimetière : elle grossit, plus personne
    ne sait lesquelles mordent encore, et la première vraie régression s'y
    glisse sans bruit.
    """
    vivants = set(_fantomes())
    perimees = sorted(set(EXEMPTES) - vivants)
    assert not perimees, (
        f"ces exemptions ne correspondent plus à aucun usage : {perimees}. "
        "Les retirer — une exemption sans objet est une porte ouverte."
    )


def test_chaque_exemption_porte_une_raison():
    muettes = [c for c, r in EXEMPTES.items() if len(r.strip()) < 40]
    assert not muettes, (
        f"exemptions sans justification lisible : {muettes}. Une exemption "
        "sans raison écrite est une exemption que personne ne pourra rouvrir."
    )
