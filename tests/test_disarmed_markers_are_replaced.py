"""Un marqueur de dépliant désarmé doit être REMPLACÉ, pas seulement retiré.

CE QUE LE DÉPÔT NE VÉRIFIAIT PAS

Deux gardes encadrent déjà les dépliants, et aucune ne couvre ce cas :

* `test_no_disclosure_relies_on_the_browser_default` vérifie qu'un `<details>`
  **est stylé** — qu'il adopte le composant ou qu'un sélecteur CSS atteigne son
  `<summary>`. Elle ne regarde pas ce que ce style **fait** ;
* `test_no_new_summary_loses_its_native_marker` (inventaire des surfaces)
  demande « restituer un marqueur explicite **ou** inscrire l'entrée avec sa
  raison ». L'inscription suffit : c'est un journal de décisions, pas un
  contrôle fonctionnel.

Vérifié par plantation le 2026-09-05 : en remplaçant `content: "›"` par
`content: ""` sur `.pd-drawer > summary::after` — donc en livrant un dépliant
**sans aucun marqueur visible** — les deux gardes sont restées **VERTES**.

Un dépliant sans marqueur n'annonce pas qu'il s'ouvre. C'est une affordance
perdue, et elle est invisible à la relecture : le CSS a l'air complet, il
désarme proprement les deux pseudo-éléments natifs.

CE QUE CETTE GARDE VÉRIFIE, ET CE QU'ELLE REFUSE DE DEVINER

⚠ SA PREMIÈRE ÉCRITURE ACCUSAIT QUINZE IMPLÉMENTATIONS SAINES.

Elle exigeait un `content` **non vide**. Or le marqueur canonique du dépôt —
documenté dans `app.css` sous « MARQUEUR DE DIVULGATION — un repli doit AVOIR
L'AIR de s'ouvrir » — est un **triangle dessiné en bordures** :

    .why-plan__summary::before {
      content: "";
      border-left: 5px solid currentColor;
      border-top: 4px solid transparent;
      border-bottom: 4px solid transparent;
    }

`content: ""` et pourtant parfaitement visible. Une garde qui l'aurait accusé
aurait été désarmée dans la semaine, à raison.

« Un marqueur est visible » n'est pas décidable depuis le texte d'une feuille
de style : le contenu, une bordure, un fond, une image ou un élément du
gabarit peuvent tous le porter. Cette garde ne le tente donc pas.

Elle vérifie le sous-ensemble **décidable** : un pseudo-élément déclaré
**vide de tout** — pas de contenu, pas de bordure, pas de fond, pas de
dimension — ne dessine rien, et c'est toujours une erreur. C'est exactement la
plantation qui est passée verte devant les deux gardes existantes.
"""
from __future__ import annotations

import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS_DIR = ROOT / "app/static/css"

#: Les trois façons de retirer le marqueur natif d'un `<summary>`.
#: `list-style: none` agit sur Firefox et les moteurs récents ;
#: `::-webkit-details-marker` sur Chromium et Safari ; `::marker` sur les deux.
DESARME = (
    re.compile(r"list-style\s*:\s*none"),
    re.compile(r"display\s*:\s*(?!list-item)"),
)

COMMENTAIRE = re.compile(r"/\*.*?\*/", re.S)


def _regles(src: str) -> list[tuple[str, str]]:
    """(sélecteur, corps) de chaque règle, commentaires retirés.

    Les commentaires partent AVANT le découpage : ce fichier et les feuilles
    du dépôt expliquent en prose ce qu'ils désarment, et une garde qui lit sa
    propre justification rougit sur du texte. Dixième occurrence du motif ici.
    """
    src = COMMENTAIRE.sub(" ", src)
    return [
        (m.group(1).strip(), m.group(2))
        for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", src)
    ]


#: Toute propriété par laquelle un pseudo-élément peut dessiner quelque chose.
#: `content` non vide, mais aussi une bordure, un fond, une image, ou des
#: dimensions — le triangle canonique du dépôt n'utilise que des bordures.
PEINT = re.compile(
    r"\b(?:border(?:-[a-z]+)?|background(?:-[a-z]+)?|box-shadow|outline"
    r"|width|height|min-width|min-height|mask|clip-path|transform)\s*:",
)

CONTENU = re.compile(r'content\s*:\s*(?:"([^"]*)"|\'([^\']*)\'|([^;}]+))')


def _pseudos_de_summary() -> list[tuple[str, str, str]]:
    """(fichier, sélecteur, corps) de chaque `::before`/`::after` de summary."""
    trouves = []
    for f in sorted(CSS_DIR.glob("*.css")):
        for sel, corps in _regles(f.read_text(encoding="utf-8")):
            s = sel.strip()
            if "summary" not in s:
                continue
            if not (s.endswith("::before") or s.endswith("::after")):
                continue
            trouves.append((f.name, s, corps))
    return trouves


def _dessine_rien(corps: str) -> bool:
    """Le pseudo-élément est-il déclaré VIDE DE TOUT ?

    Vide de tout = un `content` vide (ou `none`) **et** aucune propriété par
    laquelle il pourrait dessiner. C'est le seul cas où l'on peut affirmer,
    depuis la feuille seule, que rien n'est peint.
    """
    m = CONTENU.search(corps)
    if m is None:
        return False                     # pas de `content` : hors sujet
    valeur = (m.group(1) or m.group(2) or m.group(3) or "").strip()
    if valeur and valeur.lower() != "none":
        return False                     # il y a du contenu
    return not PEINT.search(corps)       # …et rien pour dessiner


PSEUDOS = _pseudos_de_summary()


def test_the_sweep_finds_summary_pseudo_elements():
    """Une garde qui ne trouve rien ne garde rien."""
    assert len(PSEUDOS) >= 3, (
        f"{len(PSEUDOS)} pseudo-éléments de `<summary>` trouvés — le balayage "
        "ne porte sur rien, vérifier le découpage des règles"
    )


@pytest.mark.parametrize(
    ("fichier", "selecteur", "corps"), PSEUDOS,
    ids=[f"{f}::{s[:52]}" for f, s, _ in PSEUDOS],
)
def test_no_summary_marker_is_declared_empty_of_everything(
    fichier: str, selecteur: str, corps: str,
) -> None:
    assert not _dessine_rien(corps), (
        f"{fichier} — `{selecteur}` ne dessine rien : `content` vide et aucune "
        f"bordure, fond ni dimension. Le dépliant a perdu son marqueur, et "
        f"aucune des deux gardes existantes ne le voit — l'une vérifie que le "
        f"`<summary>` est stylé, l'autre qu'une décision est inscrite.\n"
        f"  Remettre un contenu (un chevron suffit), ou dessiner la forme "
        f"comme le fait `.why-plan__summary::before`."
    )
