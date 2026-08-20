"""`UIV3_VISUAL_BASELINE_01` — quelle garde bloque quoi, et pourquoi.

    Visual contracts according to surface sovereignty.

B9 n'est **pas** « prendre des captures partout ». Une capture devient un
**contrat de design** uniquement là où la souveraineté de la surface le dit.

    SOVEREIGN     Home, Session          capture BLOQUANTE + géométrie + a11y
    TRANSITIONAL  Profile, Library,      capture = PREUVE, jamais un gate
                  Progress, Dashboard,   mécanique/a11y/fonctionnel bloquants
                  History
    UTILITY       login, admin, exports  fonctionnel, a11y, mécanique
                                         pas de contrat pixel par défaut

Le statut vit dans `geometry_manifest.SURFACE_STATUS`, et une surface non
inscrite y est `TRANSITIONAL` — ce module ne fait que déduire les gates.

POURQUOI DEUX COUCHES, ET PAS UNE
----------------------------------
Elles attrapent des classes de régression **différentes**, et aucune ne
remplace l'autre :

  A — capture     hiérarchie spatiale, typographie, alignement, surfaces,
                  rythme visuel. Aveugle à une géométrie qui dérive sous des
                  pixels proches.
  B — géométrie   x/y, largeurs/hauteurs, zones tactiles, invariant de
                  non-rétrécissement. Aveugle à une couleur, une ombre, une
                  graisse de police.

Deux défauts vécus le prouvent. Un `id` dupliqué en état `CORRECTION` : aucun
pixel ne bouge. `TERMINER LA SÉANCE` rabotée de 56 à 44 px par une règle
d'accessibilité plus spécifique chargée plus tard : la garde qui lisait des
noms de sélecteurs est restée verte, la collision vivait dans la cascade.

`state coverage` ≠ `visual contract coverage`
----------------------------------------------
Ouvrir chaque `<details>` est nécessaire à l'**inventaire** — c'est le trou
que `B8` ne pouvait pas voir. Ce n'est PAS une raison de créer `2^N` captures.
Une surface souveraine ne reçoit de référence que sur ses **états nommés**.
"""
from __future__ import annotations

from typing import Final

from scripts.geometry_manifest import (
    SOVEREIGN,
    SURFACE_STATUS,
    TRANSITIONAL,
    UTILITY,
)

#: Les familles de gardes qu'une tranche peut poser sur une surface.
PIXEL: Final[str] = "pixel"                # comparaison de capture
GEOMETRY: Final[str] = "geometry"          # manifeste numérique
TARGETS: Final[str] = "targets"            # standard tactile produit
A11Y: Final[str] = "a11y"                  # contraste, nom accessible, focus
FUNCTIONAL: Final[str] = "functional"      # HTTP 200, formulaires, navigation
NO_SHRINK: Final[str] = "no_shrink"        # invariant de non-rétrécissement

#: Gardes **BLOQUANTES** par statut : leur échec rend la PR rouge.
BLOCKING_GATES: Final[dict[str, frozenset[str]]] = {
    SOVEREIGN: frozenset({PIXEL, GEOMETRY, TARGETS, A11Y, FUNCTIONAL, NO_SHRINK}),
    # Pas de PIXEL. C'est toute la décision : une refonte structurelle de
    # Profile ou Library est ATTENDUE, et ne doit jamais être classée
    # régression visuelle.
    TRANSITIONAL: frozenset({GEOMETRY, TARGETS, A11Y, FUNCTIONAL, NO_SHRINK}),
    UTILITY: frozenset({GEOMETRY, TARGETS, A11Y, FUNCTIONAL, NO_SHRINK}),
}

#: Artefacts produits **sans** valeur de contrat : preuve, comparaison
#: humaine, point de départ d'une refonte.
EVIDENCE_ARTIFACTS: Final[dict[str, frozenset[str]]] = {
    SOVEREIGN: frozenset(),
    TRANSITIONAL: frozenset({PIXEL}),
    UTILITY: frozenset({PIXEL}),
}

#: Nom du drapeau porté par une capture qui documente sans gouverner.
LEGACY_REFERENCE_FLAG: Final[str] = "legacy_reference"


def status_of(surface: str) -> str:
    """Statut d'une surface. Inconnue ⇒ `TRANSITIONAL`, jamais `SOVEREIGN`."""
    return SURFACE_STATUS.get(surface, TRANSITIONAL)


def is_blocking(surface: str, gate: str) -> bool:
    """Cette garde a-t-elle le droit de rendre une PR rouge sur cette surface ?"""
    return gate in BLOCKING_GATES[status_of(surface)]


def is_evidence_only(surface: str, gate: str) -> bool:
    """Cette garde produit-elle une preuve **sans** valeur de contrat ?"""
    return gate in EVIDENCE_ARTIFACTS[status_of(surface)]


def screenshot_flags(surface: str) -> dict[str, bool]:
    """Ce qu'une capture de cette surface affirme d'elle-même.

    `legacy_reference = True` se lit : *voici l'état de départ*, et non
    *voici le design à préserver*. C'est le drapeau qui empêche une refonte
    `UX4` de se battre contre ses propres captures.
    """
    return {LEGACY_REFERENCE_FLAG: status_of(surface) != SOVEREIGN}


# ── Gouvernance des références ──────────────────────────────────────────────

#: Ce qu'un remplacement de référence SOUVERAINE exige, sans exception.
#: Un golden n'est pas un fichier qu'on rafraîchit : c'est une **décision
#: produit**, et le diff de PR doit la rendre lisible.
SOVEREIGN_PROMOTION_EVIDENCE: Final[tuple[str, ...]] = (
    "decision_ref",   # spec ou décision opérateur qui autorise le changement
    "before",         # capture antérieure
    "after",          # capture nouvelle
    "geometry_delta", # ce que la couche B dit du même changement
    "human_verdict",  # qui a tranché
)


def promotion_blockers(surface: str, evidence: dict) -> list[str]:
    """Ce qui manque pour remplacer légitimement une référence.

    Sur une surface souveraine, faire passer un échec visuel en relançant
    l'outil avec l'option de mise à jour **n'est pas une correction** : c'est
    effacer la question. Les cinq preuves sont donc exigées, et leur absence
    est nommée une par une plutôt que résumée en « refusé ».

    Sur une surface transitionnelle, la capture **documente** l'état, elle ne
    le gouverne pas : la rafraîchir pendant une refonte est normal.
    """
    if status_of(surface) != SOVEREIGN:
        return []
    return [f for f in SOVEREIGN_PROMOTION_EVIDENCE if not evidence.get(f)]


# ── Dimensions dominantes protégées ─────────────────────────────────────────
#
# L'invariant de non-rétrécissement couvre déjà toute la géométrie. Ces
# planchers nommés existent en PLUS, parce qu'ils ont une régression RÉELLE
# derrière eux et qu'un échec doit nommer l'action, pas une clé opaque.

PROTECTED_FLOORS: Final[dict[str, dict]] = {
    "session-review-terminate": {
        "surface": "session-active",
        "selector": ".btn--end",
        "label": "TERMINER LA SÉANCE",
        "min_height_px": 56,
        "why": (
            "Commande dominante de l'état SESSION REVIEW, acceptée au dogfood "
            "de phase 2 à 56 px. Rabotée à 44 px par une règle "
            "d'accessibilité plus spécifique chargée plus tard — la garde qui "
            "lisait des noms de sélecteurs est restée verte."
        ),
    },
}


def floor_violations(measurements: dict[str, float]) -> list[str]:
    """Les planchers nommés qui ne sont plus tenus.

    `measurements` : clé de `PROTECTED_FLOORS` → hauteur mesurée.
    Une clé **absente** est signalée : un plancher qu'on ne mesure plus est
    un plancher qu'on ne garde plus.
    """
    out = []
    for key, spec in PROTECTED_FLOORS.items():
        got = measurements.get(key)
        if got is None:
            out.append(f"{key} ({spec['label']}) : NON MESURÉ")
        elif got < spec["min_height_px"]:
            out.append(
                f"{key} ({spec['label']}) : {got} px < "
                f"{spec['min_height_px']} px accepté"
            )
    return out
