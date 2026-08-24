"""Modèle épistémique canonique d'AUREN (`TRAIN1-D` / arbitrage C3).

POURQUOI CE MODULE EXISTE
--------------------------
Le meilleur objet du produit était enfermé dans sa surface la moins visitée.
Le Coach Report étiquetait chacun de ses blocs *Mesuré* ou *Inféré*, et marquait
*Non déductible* ce qu'il ne pouvait pas établir — un vocabulaire d'honnêteté
qui n'existait **nulle part ailleurs**.

Ailleurs, le dépôt avait construit un second vocabulaire, pour un autre
problème : `zone_exposure` distingue `known` / `zero` / `partial` / `unknown`,
c'est-à-dire **jusqu'où va la preuve**, pas **d'où vient le savoir**.

Les deux sont vrais et ne disent pas la même chose. Ce module les déclare
**orthogonaux** et leur donne un seul foyer.

DEUX AXES, ET LES CONFONDRE MENTIRAIT
--------------------------------------
`NATURE` — d'où vient ce que l'écran affirme :

    MEASURED        observé tel quel. Une série cochée, un poids saisi.
    DERIVED         calculé de façon **déterministe** depuis des mesures.
                    Un comptage, une somme, un écart. Reproductible à
                    l'identique ; n'ajoute aucune hypothèse.
    INFERRED        produit par une **règle** qui va au-delà des données.
                    « point faible probable » en est une : le seuil de
                    ≤ 1 séance/30 j est un choix, pas une observation.
    NOT_DEDUCIBLE   le produit ne peut pas l'établir, et le dit.

`COVERAGE` — jusqu'où va la preuve sur la fenêtre considérée :

    COMPLETE        toute la fenêtre est attribuable. **Un zéro observé en
                    est** : « aucune séance n'a touché cette zone » est une
                    couverture complète dont la valeur est nulle.
    PARTIAL         une partie seulement. Les comptages positifs restent des
                    **minima observés** ; aucun zéro ne peut être affirmé.
    UNKNOWN         rien d'attribuable. **Ce n'est pas zéro.**

⚠ LA DISTINCTION QUI COÛTE LE PLUS CHER QUAND ON LA RATE : `DERIVED` n'est pas
`MEASURED`. Le Coach Report étiquetait « Mesuré » ses blocs de volume, de
répartition par zone et de discipline — or ce sont des **comptages**, donc des
calculs. Ils sont exacts, reproductibles, et ils restent des dérivations. Les
appeler mesures faisait passer une convention de comptage (« qu'est-ce qu'une
séance qui compte ? ») pour une observation brute.

⚠ ON NE BADGE PAS TOUT (`OPERATOR_DECISION` C3). Le niveau 1 d'une surface ne
porte **aucun** badge : un écran couvert d'étiquettes épistémiques ne rend pas
le produit plus honnête, il rend la lecture impossible et transforme un signal
en bruit de fond. Le badge est réservé aux surfaces qui **assemblent des
natures différentes dans un même document** — aujourd'hui le seul Coach Report.
Ailleurs, la nature se dit par la formulation et par la provenance, pas par une
pastille.
"""
from __future__ import annotations

#: — AXE 1 : la NATURE de la connaissance ————————————————————————————
MEASURED = "measured"
DERIVED = "derived"
INFERRED = "inferred"
NOT_DEDUCIBLE = "not_deducible"

NATURES: tuple[str, ...] = (MEASURED, DERIVED, INFERRED, NOT_DEDUCIBLE)

NATURE_LABELS: dict[str, str] = {
    MEASURED: "Mesuré",
    DERIVED: "Calculé",
    INFERRED: "Inféré",
    NOT_DEDUCIBLE: "Non déductible",
}

#: Ce que chaque nature autorise à dire — cité dans la légende du rapport.
NATURE_MEANING: dict[str, str] = {
    MEASURED: "observé tel quel, sans calcul",
    DERIVED: "calculé depuis des mesures, sans hypothèse ajoutée",
    INFERRED: "produit par une règle du produit — le seuil est un choix",
    NOT_DEDUCIBLE: "AUREN ne peut pas l'établir",
}

#: — AXE 2 : la COUVERTURE de la preuve ————————————————————————————————
COMPLETE = "complete"
PARTIAL = "partial"
UNKNOWN = "unknown"

COVERAGES: tuple[str, ...] = (COMPLETE, PARTIAL, UNKNOWN)

COVERAGE_LABELS: dict[str, str] = {
    COMPLETE: "complète",
    PARTIAL: "partielle",
    UNKNOWN: "inconnue",
}

#: Les deux axes sont INDÉPENDANTS : les 4 × 3 combinaisons ont toutes un sens.
#: Un fait `INFERRED` sur une couverture `PARTIAL` est parfaitement possible —
#: et c'est précisément le cas qu'il faut savoir nommer plutôt que d'aplatir.
NATURE_X_COVERAGE_IS_ORTHOGONAL = True

#: Traduction des états historiques de `zone_exposure` vers l'axe COUVERTURE.
#:
#: `zero` devient `COMPLETE`, et ce n'est pas une approximation : « des séances
#: existent, aucune n'a touché les onze zones » est une observation ENTIÈRE dont
#: la valeur est nulle. La confondre avec `UNKNOWN` rendrait une absence de
#: preuve indiscernable d'un fait.
_ZONE_STATE_TO_COVERAGE: dict[str, str] = {
    "known": COMPLETE,
    "zero": COMPLETE,
    "partial": PARTIAL,
    "unknown": UNKNOWN,
}


def coverage_of_zone_state(state: str) -> str:
    """Couverture correspondant à un état de `zone_exposure`.

    Rend `UNKNOWN` pour un état non reconnu — jamais `COMPLETE`. Un état
    inattendu est une ignorance, et l'arrondir vers le haut fabriquerait
    exactement le mensonge que ces deux axes existent pour empêcher.
    """
    return _ZONE_STATE_TO_COVERAGE.get(state, UNKNOWN)


def label(nature: str) -> str:
    """Libellé lisible d'une nature. Une nature inconnue se dit inconnue."""
    return NATURE_LABELS.get(nature, NATURE_LABELS[NOT_DEDUCIBLE])


__all__ = [
    "COMPLETE",
    "COVERAGES",
    "COVERAGE_LABELS",
    "DERIVED",
    "INFERRED",
    "MEASURED",
    "NATURES",
    "NATURE_LABELS",
    "NATURE_MEANING",
    "NATURE_X_COVERAGE_IS_ORTHOGONAL",
    "NOT_DEDUCIBLE",
    "PARTIAL",
    "UNKNOWN",
    "coverage_of_zone_state",
    "label",
]
