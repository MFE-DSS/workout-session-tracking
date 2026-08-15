"""Politique de contribution des séries (Sb_SET_CONTRIBUTION_POLICY_01).

Tranche 1/4 du train `AUREN_EFFECTIVE_VOLUME_COMPLETION_01`. Résout la frontière
sémantique laissée ouverte par `weekly_volume_budget.SET_CONTRIBUTION_CANDIDATE`.

## Le problème que ce module ferme

Comparer **44 séries planifiées** à **126 séries de bornes basses** mélangeait
deux unités : des **séries physiques** d'un côté, des **cibles par zone** de
l'autre. Une série physique de développé couché n'est pas « une série » dans
l'absolu — elle vaut pour les pectoraux, et elle vaut *aussi*, différemment,
pour les triceps.

## La convention, et ce qu'elle n'est pas

`SET_CONTRIBUTION_POLICY_VERSION = "set-contribution-v1"` :

- rôle **primaire/direct** : 1,0 série effective par série physique ;
- rôle **secondaire/indirect** : 0,5 série effective par série physique ;
- zone **inconnue ou non résolue** : **0** — jamais de crédit fabriqué.

**`0,5` est un COEFFICIENT DE COMPTABILITÉ.** Ce n'est pas 50 % d'activation
musculaire, pas la moitié d'un stimulus hypertrophique, pas une équivalence EMG,
pas une fraction physiologique mesurée. Aucune littérature n'est invoquée pour
affirmer qu'une série indirecte vaudrait exactement la moitié d'une série
directe — c'est une **règle de comptage produit**, choisie pour être
déterministe et explicable, et versionnée pour pouvoir changer.

Ce coefficient n'est **jamais** exposé à l'utilisateur comme de la physiologie.

## Unités entières : pas de flottants dans les gardes

Le crédit se compte en **demi-séries entières** (`HALF_SET_UNITS`) :

- une série directe = **2 unités** ;
- une série indirecte = **1 unité**.

Les comparaisons de budget se font donc entre entiers, ce qui évite les
tolérances arbitraires et les inégalités instables que produirait un `0.5`
binaire accumulé. `effective_sets` (= unités / 2) n'existe que pour l'affichage
et les rapports.

## D'où vient la contribution

Du **contrat canonique de lecture des zones** — `body_zone_source`, avec ses
corrections revues — appliqué à l'**exercice réellement sélectionné**, jamais à
l'intention du créneau.

La distinction est délibérée : un `SlotIntent` exprime une **intention de
programmation** (« ce créneau vise les mollets »), tandis que la table
exercice→`BodyZone` exprime ce que **l'exercice** entraîne canoniquement. Quand
les deux divergent, c'est une information — pas quelque chose à masquer en
choisissant la source la plus flatteuse.

## Garde-fous de crédit

Une zone ne peut recevoir **qu'un seul** crédit par série physique : si elle
apparaît à la fois en primaire et en secondaire du même exercice, le rôle le
plus élevé l'emporte (primaire domine). Une série physique ne peut donc jamais
créditer plus de 1,0 série effective à une zone donnée en V1.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.services.body_zone_source import resolve_exercise_zones

SET_CONTRIBUTION_POLICY_VERSION = "set-contribution-v1"

#: Unités entières par série physique, selon le rôle de la zone.
UNITS_PER_DIRECT_SET = 2
UNITS_PER_INDIRECT_SET = 1
#: Diviseur unités → séries effectives. Uniquement pour l'affichage.
UNITS_PER_SET = 2

#: Rappel versionné dans le code, pas seulement dans un rapport.
ACCOUNTING_GUARD = (
    "The 0.5 indirect coefficient is an accounting convention, not physiology: "
    "it is not 50% muscle activation, not half a hypertrophic stimulus, not EMG "
    "equivalence, and not a measured physiological fraction."
)


class ContributionRole(StrEnum):
    """Rôle d'une zone pour un exercice donné."""

    DIRECT = "direct"
    INDIRECT = "indirect"


def units_for_role(role: ContributionRole, physical_sets: int) -> int:
    per_set = (
        UNITS_PER_DIRECT_SET if role is ContributionRole.DIRECT
        else UNITS_PER_INDIRECT_SET
    )
    return per_set * physical_sets


@dataclass(frozen=True)
class ZoneContribution:
    """Ce qu'une zone reçoit, en séries physiques ET en unités effectives."""

    zone_code: str
    direct_sets: int = 0
    indirect_sets: int = 0
    effective_units: int = 0
    policy_version: str = SET_CONTRIBUTION_POLICY_VERSION

    @property
    def effective_sets(self) -> float:
        """Séries effectives — **affichage et rapports uniquement**.

        Les comparaisons de budget utilisent `effective_units`, entier.
        """
        return self.effective_units / UNITS_PER_SET

    def plus(self, role: ContributionRole, physical_sets: int) -> ZoneContribution:
        direct = self.direct_sets + (
            physical_sets if role is ContributionRole.DIRECT else 0)
        indirect = self.indirect_sets + (
            physical_sets if role is ContributionRole.INDIRECT else 0)
        return ZoneContribution(
            zone_code=self.zone_code,
            direct_sets=direct,
            indirect_sets=indirect,
            effective_units=self.effective_units + units_for_role(
                role, physical_sets),
        )


def exercise_roles(exercise_name: str) -> dict[str, ContributionRole]:
    """Zone → rôle pour UN exercice, d'après le contrat canonique.

    **Le primaire domine** : une zone listée dans les deux rôles n'est comptée
    qu'une fois, au rôle le plus élevé. Une zone inconnue (`unknown`) ou absente
    ne figure pas — l'absence de correspondance ne devient jamais un crédit
    indirect fabriqué.
    """
    resolution = resolve_exercise_zones(None, exercise_name)
    roles: dict[str, ContributionRole] = {}
    if resolution.is_known:
        roles[resolution.primary] = ContributionRole.DIRECT
    for zone in resolution.secondary:
        if zone and zone != "unknown":
            roles.setdefault(zone, ContributionRole.INDIRECT)
    return roles


def accumulate(
    contributions: dict[str, ZoneContribution],
    exercise_name: str,
    physical_sets: int,
) -> dict[str, ZoneContribution]:
    """Ajoute la contribution d'un exercice au cumul. Pur, sans effet de bord."""
    if physical_sets <= 0:
        return contributions
    out = dict(contributions)
    for zone, role in exercise_roles(exercise_name).items():
        current = out.get(zone) or ZoneContribution(zone_code=zone)
        out[zone] = current.plus(role, physical_sets)
    return out


def contributions_for(prescriptions) -> dict[str, ZoneContribution]:
    """Cumul des contributions de toutes les prescriptions d'un plan.

    Prend n'importe quel itérable d'objets portant `exercise_name` et
    `planned_sets` — les prescriptions du planificateur comme les créneaux.
    """
    out: dict[str, ZoneContribution] = {}
    for item in prescriptions:
        name = getattr(item, "exercise_name", None)
        sets = getattr(item, "planned_sets", 0) or 0
        if name and sets > 0:
            out = accumulate(out, name, sets)
    return out


def units_for_sets(sets: int) -> int:
    """Une borne de bande (en séries) convertie en unités, pour comparer juste."""
    return sets * UNITS_PER_SET


__all__ = [
    "ACCOUNTING_GUARD",
    "SET_CONTRIBUTION_POLICY_VERSION",
    "UNITS_PER_DIRECT_SET",
    "UNITS_PER_INDIRECT_SET",
    "UNITS_PER_SET",
    "ContributionRole",
    "ZoneContribution",
    "accumulate",
    "contributions_for",
    "exercise_roles",
    "units_for_role",
    "units_for_sets",
]
