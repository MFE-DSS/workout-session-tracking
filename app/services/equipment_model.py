"""Modèle d'environnement à trois couches (`Sb_TRAIN_A_ENV_01`).

    OBJET D'ÉQUIPEMENT  →  CAPACITÉ INTERNE  →  EXIGENCE D'EXERCICE

L'utilisateur déclare des **choses physiques** (« un banc inclinable », « une
poulie double réglable »). Le moteur consomme des **affordances** (« un
dossier inclinable », « deux colonnes chargées indépendamment »). Les deux
vocabulaires sont distincts et ce module est le seul endroit qui les relie.

**Pourquoi trois couches et pas deux.** Les deux raccourcis ont été mesurés
et écartés :

* un `cable` global ne prouve rien — la documentation constructeur montre
  qu'un *Dual Adjustable Pulley* et une station de tirage vertical sont deux
  produits différents, avec chacun leur colonne de charge ;
* une case à cocher par slug d'exercice ferait déclarer à l'utilisateur des
  mouvements et non du matériel, et ferait porter à `machine_slug` une
  sémantique qu'il n'a pas — le dépôt le prouve : le champ `equipment` de
  `machine_atlas.json` ne porte que la MODALITÉ.

**Ce que ce module ne fait pas.** Il ne filtre rien. Aucun appelant du chemin
servi ne l'importe encore : l'activation du filtre dur est la dernière porte
et elle n'est pas ouverte. Une garde vérifie cette absence d'appelant.

**Trois valeurs, jamais deux.** `FEASIBLE`, `NOT_FEASIBLE`, `UNKNOWN`.
L'ignorance n'est pas une permission : une exigence inconnue rend `UNKNOWN`,
jamais `FEASIBLE`. Symétriquement elle ne rend pas `NOT_FEASIBLE` — ne pas
savoir n'est pas un refus.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parents[2] / "data"
_REGISTRY_PATH = _DATA_DIR / "equipment_registry.json"
_CURATION_PATH = _DATA_DIR / "equipment_curation.json"
_EKB_PATH = _DATA_DIR / "exercise_knowledge_base.json"

#: Clé portée par les entrées d'EKB curées. Son **absence** vaut `None`
#: (exigence inconnue) et jamais `[]` — un champ absent ne déclare rien.
EKB_REQUIREMENTS_KEY = "equipment_requirements"

FEASIBLE = "feasible"
NOT_FEASIBLE = "not_feasible"
UNKNOWN = "unknown"


class EquipmentModelError(ValueError):
    """Donnée de référence incohérente — jamais corrigée en silence."""


# ---------------------------------------------------------------------------
# Chargement du référentiel
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EquipmentItem:
    """Un objet physique déclarable. `capabilities` est ce qu'il établit."""

    item_id: str
    label: str
    capabilities: frozenset[str]
    provenance: str


@lru_cache(maxsize=1)
def _registry() -> dict:
    return json.loads(_REGISTRY_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def capability_vocabulary() -> dict[str, str]:
    """Capacité → description. **Vocabulaire interne**, jamais affiché."""
    return dict(_registry()["capabilities"])


@lru_cache(maxsize=1)
def equipment_items() -> dict[str, EquipmentItem]:
    """Objets déclarables, indexés par `item_id`."""
    vocab = capability_vocabulary()
    items: dict[str, EquipmentItem] = {}
    for raw in _registry()["items"]:
        unknown = sorted(set(raw["capabilities"]) - set(vocab))
        if unknown:
            raise EquipmentModelError(
                f"objet {raw['item_id']!r} : capacités hors vocabulaire "
                f"{unknown}"
            )
        items[raw["item_id"]] = EquipmentItem(
            item_id=raw["item_id"],
            label=raw["label"],
            capabilities=frozenset(raw["capabilities"]),
            provenance=raw["provenance"],
        )
    return items


@lru_cache(maxsize=1)
def equipment_item_vocabulary() -> tuple[str, ...]:
    """Identifiants d'objets, ordre canonique — c'est ce qui est persisté."""
    return tuple(sorted(equipment_items()))


@lru_cache(maxsize=1)
def curation_rows() -> dict[str, dict]:
    """Provenance ligne à ligne des 68 exercices prescrits."""
    return dict(json.loads(_CURATION_PATH.read_text(encoding="utf-8"))["rows"])


# ---------------------------------------------------------------------------
# Objet → capacités
# ---------------------------------------------------------------------------


def capabilities_for_items(item_ids) -> frozenset[str]:
    """Union des affordances établies par les objets déclarés.

    Un identifiant inconnu **lève** : une déclaration illisible ne doit pas
    se dégrader en un environnement plus pauvre que la réalité, ce qui
    rendrait faisable-vers-infaisable sans que personne ne le voie.
    """
    items = equipment_items()
    derived: set[str] = set()
    for item_id in item_ids:
        item = items.get(item_id)
        if item is None:
            raise EquipmentModelError(f"objet d'équipement inconnu {item_id!r}")
        derived |= item.capabilities
    return frozenset(derived)


# ---------------------------------------------------------------------------
# Exercice → exigences
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def _ekb_exercises() -> dict:
    return json.loads(_EKB_PATH.read_text(encoding="utf-8"))["exercises"]


def requirements_for_exercise(name: str) -> tuple[str, ...] | None:
    """Exigences **conjonctives**, ou `None` si elles sont inconnues.

    `None` et `()` sont deux faits différents et le restent : `()` dit « cet
    exercice n'exige aucun matériel externe », `None` dit « on ne sait pas ».
    Un exercice absent de l'EKB rend `None` — l'absence n'affirme rien.
    """
    entry = _ekb_exercises().get(name)
    if entry is None:
        return None
    value = entry.get(EKB_REQUIREMENTS_KEY)
    if value is None:
        return None
    return tuple(sorted(value))


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------


def feasibility(
    requirements: tuple[str, ...] | None,
    declared_items: tuple[str, ...] | None,
) -> str:
    """`FEASIBLE` · `NOT_FEASIBLE` · `UNKNOWN`.

    | environnement \\ exigence | inconnue | aucune | listée |
    |---|---|---|---|
    | **non déclaré** (`None`) | `UNKNOWN` | `FEASIBLE` | `UNKNOWN` |
    | **aucun** (`()`)         | `UNKNOWN` | `FEASIBLE` | `NOT_FEASIBLE` |
    | **déclaré**              | `UNKNOWN` | `FEASIBLE` | couverture |

    Deux lignes de cette table portent tout le contrat. « Exigence inconnue »
    ne descend jamais en `FEASIBLE`, quelle que soit la richesse de
    l'environnement. Et « n'exige aucun matériel » reste faisable même quand
    l'environnement n'est pas déclaré : c'est le seul cas où l'absence de
    déclaration ne bloque rien, parce qu'il n'y a rien à posséder.
    """
    if requirements is None:
        return UNKNOWN
    if not requirements:
        return FEASIBLE
    if declared_items is None:
        return UNKNOWN
    derived = capabilities_for_items(declared_items)
    return FEASIBLE if set(requirements) <= derived else NOT_FEASIBLE


def missing_capabilities(
    requirements: tuple[str, ...] | None,
    declared_items: tuple[str, ...] | None,
) -> tuple[str, ...]:
    """Ce qui manque, pour expliquer un refus. Vide si le verdict n'est pas
    `NOT_FEASIBLE` — on n'énumère pas un manque qu'on n'a pas constaté."""
    if feasibility(requirements, declared_items) != NOT_FEASIBLE:
        return ()
    derived = capabilities_for_items(declared_items or ())
    return tuple(sorted(set(requirements or ()) - derived))


__all__ = [
    "EKB_REQUIREMENTS_KEY",
    "FEASIBLE",
    "NOT_FEASIBLE",
    "UNKNOWN",
    "EquipmentItem",
    "EquipmentModelError",
    "capabilities_for_items",
    "capability_vocabulary",
    "curation_rows",
    "equipment_item_vocabulary",
    "equipment_items",
    "feasibility",
    "missing_capabilities",
    "requirements_for_exercise",
]
