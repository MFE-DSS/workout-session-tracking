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

#: Une déclaration de propriété personnalisée, **où qu'elle soit sur sa ligne**.
#:
#: Le premier jet exigeait un début de ligne (`^\s*--nom:`). Il a manqué les
#: quatre déclarations de `--mf-frames`, écrites sur la même ligne que leur
#: sélecteur (`.muscle-focus__plate-area--frames-2 { --mf-frames: 2; }`), et a
#: donc déclaré fantôme un token parfaitement défini. Une garde qui se trompe
#: de côté accuse le sain et laisse passer le malade.
_DEFINITION = re.compile(r"(--[a-z0-9-]+)\s*:")

#: Les deux formes, et la seconde est la PIRE.
#:
#: `var(--fantome, #hex)` peint la mauvaise couleur. `var(--fantome)` tout court
#: rend la déclaration **invalide au calcul** : la propriété n'est pas appliquée
#: du tout. Vu en vrai — `color: var(--good)` sur « Préférences enregistrées »,
#: qui restait grise faute de vert.
_USAGE_AVEC_REPLI = re.compile(r"var\(\s*(--[a-z0-9-]+)\s*,")
_USAGE_SANS_REPLI = re.compile(r"var\(\s*(--[a-z0-9-]+)\s*\)")

#: Commentaires CSS et Jinja. Une sonde qui lit la prose comme du code
#: s'accuse elle-même : ce fichier cite `--success` en le documentant, et la
#: première version de la garde comptait la citation comme un usage.
_COMMENTAIRES = re.compile(r"/\*.*?\*/|\{#.*?#\}", re.DOTALL)


def _sans_commentaires(source: str) -> str:
    return _COMMENTAIRES.sub(" ", source)

#: Fantômes tolérés, chacun avec la raison qui le tolère. Un usage n'entre ici
#: que s'il est INOFFENSIF ou INTOUCHABLE — jamais parce qu'il est pénible.
EXEMPTES: dict[str, str] = {
    "session_focus.css::--bg-elev": (
        "feuille du viseur intra-séance, seul objet validé au rendu par "
        "l'opérateur. Toucher sa couleur, c'est le modifier sans exposition."
    ),
    "session_focus.css::--t-fg-dim": (
        "même feuille, même raison. Son repli est `var(--fg-dim)`, un token "
        "réel : le rendu est correct, seule l'indirection est douteuse."
    ),
    "session_focus.css::--color-fg": (
        "même feuille, même raison — et c'est la forme GRAVE, sans repli : la "
        "déclaration est invalide au calcul. Signalé à l'opérateur, non touché."
    ),
}


def _sources() -> list[tuple[str, str]]:
    """Rend [(nom de fichier, source sans commentaires)] pour tout le rendu."""
    return [
        (f.name, _sans_commentaires(f.read_text(encoding="utf-8")))
        for f in [*CSS.rglob("*.css"), *GABARITS.rglob("*.html")]
    ]


def _tokens_definis(sources: list[tuple[str, str]]) -> set[str]:
    """Un gabarit qui pose `style="--mf-frames: 3"` DÉFINIT le token."""
    definis: set[str] = set()
    for _, src in sources:
        definis |= set(_DEFINITION.findall(src))
    return definis


def _fantomes() -> dict[str, int]:
    """Rend {« fichier::--token »: occurrences} pour les tokens jamais définis.

    Les DEUX formes comptent : avec repli (mauvaise couleur) et sans repli
    (aucune couleur). La seconde est la plus grave et manquait au premier jet.
    """
    sources = _sources()
    definis = _tokens_definis(sources)
    trouves: dict[str, int] = {}
    for nom, src in sources:
        for rx in (_USAGE_AVEC_REPLI, _USAGE_SANS_REPLI):
            for token in rx.findall(src):
                if token not in definis:
                    cle = f"{nom}::{token}"
                    trouves[cle] = trouves.get(cle, 0) + 1
    return trouves


def test_aucun_repli_ne_peint_a_la_place_dun_token_absent():
    restants = {c: n for c, n in _fantomes().items() if c not in EXEMPTES}
    assert not restants, (
        "des usages désignent des tokens qui n'existent pas — "
        "`CLAUDE.md §5.4`. Avec repli, c'est la mauvaise couleur qui est "
        "peinte ; sans repli, la déclaration est invalide et RIEN n'est peint. "
        "Soit le token est déclaré avec son contraste mesuré sur le fond réel, "
        "soit l'usage pointe vers le token qui porte déjà cette sémantique : "
        f"{restants}"
    )


def test_la_sonde_voit_les_trois_ecritures_dusage():
    """Garde de la garde : la sonde reconnaît-elle encore un fantôme ?

    Une garde qui ne trouve rien parce que sa regex a cessé de mordre est
    indiscernable d'une garde satisfaite. On lui plante les trois écritures
    réellement rencontrées : repli hexadécimal, repli `var()` imbriqué, et
    **usage nu** — cette dernière manquait au premier jet, alors que c'est la
    plus grave.
    """
    faux = (
        "a { color: var(--fantome, #2e7d32);"
        "    background: var(--absent, var(--reel));"
        "    border-color: var(--nu); }"
    )
    avec = _USAGE_AVEC_REPLI.findall(faux)
    sans = _USAGE_SANS_REPLI.findall(faux)
    assert avec == ["--fantome", "--absent"], f"formes à repli manquées : {avec}"
    assert "--nu" in sans, f"la forme NUE n'est plus vue : {sans}"


def test_la_sonde_ne_prend_pas_un_commentaire_pour_du_code():
    """Ce fichier CITE des tokens fantômes en les documentant.

    La première version comptait la citation comme un usage et s'accusait
    elle-même. Même mode d'échec qu'une sonde d'accents qui lisait la balise
    `<details>` comme le mot « détails ».
    """
    src = (
        "/* jadis on écrivait var(--vieux-fantome, #abc) ici */\n"
        "{# et le gabarit le citait aussi : var(--autre-fantome) #}\n"
        "a { color: var(--vivant, #fff); }"
    )
    propre = _sans_commentaires(src)
    assert "--vieux-fantome" not in propre
    assert "--autre-fantome" not in propre
    assert _USAGE_AVEC_REPLI.findall(propre) == ["--vivant"]


def test_une_declaration_sur_la_ligne_de_son_selecteur_compte():
    """`.foo { --n: 2; }` définit `--n`, même écrit sur une seule ligne.

    Le premier jet exigeait un début de ligne et déclarait donc fantôme
    `--mf-frames`, défini quatre fois de cette façon. Une garde qui se trompe
    de côté accuse le sain et laisse passer le malade.
    """
    src = ".muscle-focus__plate-area--frames-2 { --mf-frames: 2; }"
    assert "--mf-frames" in set(_DEFINITION.findall(src))


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
