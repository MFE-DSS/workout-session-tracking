"""Allocateur de capacité hebdomadaire (Sb_WEEKLY_PLAN_CAPACITY_ALLOCATOR_01).

Tranche 3/4 du train `AUREN_EFFECTIVE_VOLUME_COMPLETION_01`.

## Le constat qui motive cette tranche

Avant elle, le planificateur produisait **48 séries physiques quelle que soit
la cadence** — simplement étalées plus finement à mesure que les séances se
multipliaient :

| Cadence | Exercices/séance | Séries/séance |
|---|---|---|
| 2 | 6 | 24 |
| 4 | 3 | 12 |
| 6 | 2 | 8 |

Le catalogue curé, lui, prescrit **6 à 8 exercices et 18 à 24 séries par
séance**. À cadence 4, la capacité déclarée par l'utilisateur permettait donc
~96 séries ; le plan en utilisait 48. **La capacité n'était pas allouée, elle
était subie.**

## Ce que cet allocateur optimise — et ce qu'il n'optimise pas

`Σ planning_low = 126` **n'est pas une cible physiologique**. C'est l'agrégat de
onze valeurs produit héritées du référentiel de zones. L'objectif n'est donc
pas « faire passer tous les compteurs au-dessus », mais **produire le meilleur
programme faisable sous contraintes**.

**Contraintes DURES** — jamais violées : cadence déclarée · matériel ·
identité canonique des candidats (aucune fabrication) · limites structurelles
du cycle de vie Custom Program · plafonds `planning_high` · déterminisme.

**Objectifs SOUPLES, par ordre lexicographique** :

1. maximiser le nombre de zones recevant un volume effectif **significatif** ;
2. remonter les zones les moins couvertes vers `planning_low` ;
3. minimiser le plus grand **déficit relatif** ;
4. rapprocher les zones de `baseline` s'il reste de la capacité ;
5. favoriser les priorités déclarées **à l'intérieur de leurs bandes** ;
6. minimiser le nombre d'**identités** d'exercice ;
7. minimiser l'encombrement inutile des séances.

## Le ratio de couverture

`effective_sets / planning_low_sets` — **un ratio de planification**.

Ce n'est **pas** une récupération physiologique, pas un pourcentage
d'hypertrophie, pas une activation musculaire, pas une probabilité de
progresser. Il ordonne des décisions d'allocation, rien d'autre, et n'est
**jamais** affiché comme une métrique corporelle.

## Stabilité des exercices

**Une même identité d'exercice peut revenir dans PLUSIEURS séances.** Un
« Lat pulldown » à 4 séries en séance 1 et 4 en séance 3, ce sont deux
*occurrences* d'un seul exercice — pas deux exercices. C'est préférable à
inventer deux tirages équivalents pour faire du volume.

Une **seconde identité** pour la même zone exige une raison de planification
réelle : capacité du premier exercice épuisée, intention distincte, faisabilité
matérielle, ou classement déterministe du générateur. Jamais de variété pour la
variété.

## Forme de séance — convention PRODUIT, pas seuil physiologique

Les bornes souples viennent d'un **audit du catalogue** (15 templates
`strength`) : 6–8 exercices (médiane 7) et 18–24 séries (médiane 20) par
séance. Elles sont donc un **précédent mesuré du dépôt**, versionné comme tel.

Ce n'est **pas** « 24 séries par séance est optimal ». Le plafond technique du
cycle de vie (`MAX_EXERCISES_PER_SESSION`) reste, lui, une contrainte dure.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from app.services.set_contribution import (
    UNITS_PER_DIRECT_SET,
    ContributionRole,
    exercise_roles,
    units_for_sets,
)
from app.services.user_program_drafts import MAX_EXERCISES_PER_SESSION
from app.services.weekly_set_allocation import (
    SETS_PER_SLOT_MAX,
    SETS_PER_SLOT_MIN,
)

CAPACITY_ALLOCATOR_VERSION = "capacity-allocator-v1"

#: Convention PRODUIT de forme de séance, **mesurée sur le catalogue curé**
#: (15 templates `strength` : 6–8 exercices, médiane 7 ; 18–24 séries,
#: médiane 20). Bornes souples : l'allocateur évite de les dépasser, mais rien
#: ici n'affirme qu'elles seraient physiologiquement optimales.
SESSION_SHAPE_CONVENTION_VERSION = "session-shape-v1"
SOFT_MAX_EXERCISES_PER_SESSION = 8
SOFT_MAX_SETS_PER_SESSION = 24

#: Volume effectif en deçà duquel une zone n'est pas « servie de façon
#: significative » — une seule série effective n'est pas une programmation.
#: Convention produit, alignée sur le plancher de série du catalogue.
MEANINGFUL_EFFECTIVE_UNITS = units_for_sets(SETS_PER_SLOT_MIN)

#: Rappel versionné, comme pour la politique de contribution.
COVERAGE_RATIO_GUARD = (
    "effective_sets / planning_low_sets is a PLANNER COVERAGE RATIO used to "
    "order allocation decisions. It is not physiological recovery, not a "
    "hypertrophy percentage, not muscle activation, and not a probability of "
    "growth. It is never displayed to users as a body metric."
)


class CadenceFeasibility(StrEnum):
    """Ce qu'une cadence permet — dit, jamais jugé « bon » ou « mauvais »."""

    #: Toutes les zones servables atteignent leur bande produit.
    FULL_PRODUCT_BAND = "full_product_band"
    #: Meilleur résultat atteignable ; la capacité est le facteur limitant.
    BEST_FEASIBLE = "best_feasible"
    #: Une contrainte externe (matériel, candidats) borne le résultat.
    CONSTRAINT_LIMITED = "constraint_limited"
    #: Rien d'exécutable.
    BLOCKED = "blocked"


@dataclass(frozen=True)
class Occurrence:
    """Une apparition d'un exercice dans UNE séance.

    L'identité (`exercise_name`) peut se répéter d'une séance à l'autre : ce
    sont alors plusieurs occurrences d'un seul exercice.
    """

    exercise_name: str
    zone_code: str
    intent_id: str
    session_index: int
    planned_sets: int


@dataclass(frozen=True)
class CapacityReport:
    """Ce que la cadence déclarée permet réellement, chiffré."""

    cadence: int
    feasibility: CadenceFeasibility
    physical_sets: int = 0
    effective_units: int = 0
    zones_with_volume: int = 0
    zones_at_planning_low: int = 0
    zones_at_baseline: int = 0
    worst_relative_deficit: float = 0.0
    median_relative_coverage: float = 0.0
    exercise_identities: int = 0
    occurrences_per_session: tuple[int, ...] = ()
    sets_per_session: tuple[int, ...] = ()
    unresolved: tuple[str, ...] = field(default_factory=tuple)


def coverage_ratio(effective_units: int, planning_low_sets: int) -> float:
    """Ratio de planification. Voir `COVERAGE_RATIO_GUARD`.

    Une borne basse nulle rendrait le ratio indéfini ; la zone est alors
    considérée servie (rien n'est demandé), ce qui la met en fin de file.
    """
    if planning_low_sets <= 0:
        return 1.0
    return effective_units / units_for_sets(planning_low_sets)


def _session_room(sessions_load, index: int) -> bool:
    """Vrai si la séance peut encore accueillir une occurrence.

    La borne souple protège la forme de séance ; le plafond dur du cycle de vie
    reste vérifié séparément et n'est jamais franchi.
    """
    occurrences, sets = sessions_load[index]
    return (
        occurrences < SOFT_MAX_EXERCISES_PER_SESSION
        and occurrences < MAX_EXERCISES_PER_SESSION
        and sets + SETS_PER_SLOT_MIN <= SOFT_MAX_SETS_PER_SESSION
    )


def _sets_that_fit(sessions_load, index: int, headroom_units: int) -> int:
    """Combien de séries placer ici : bornée par la séance ET par la bande.

    `headroom_units` est la marge restante avant `planning_high`, en unités.
    Une occurrence directe consomme 2 unités par série, donc on ne place jamais
    plus que ce que la bande autorise — le plafond n'est pas une suggestion.
    """
    _, sets = sessions_load[index]
    room = SOFT_MAX_SETS_PER_SESSION - sets
    by_band = headroom_units // 2
    return max(0, min(SETS_PER_SLOT_MAX, room, by_band))


def _rank_zone(state, zone_code: str) -> tuple:
    """Clé d'ordonnancement lexicographique. Le plus petit passe en premier.

    L'ordre encode les objectifs souples du brief, dans l'ordre :

    1. une zone **sans aucun volume significatif** passe avant tout — mieux
       vaut onze zones servies qu'une zone parfaite et trois à zéro ;
    2. puis le **ratio de couverture** le plus faible, ce qui minimise
       mécaniquement le plus grand déficit relatif ;
    3. puis, à égalité, une **priorité déclarée** ;
    4. puis le code de zone, pour que deux exécutions donnent le même plan.

    Une priorité ne « double » donc jamais une zone encore à zéro : elle
    départage à couverture comparable. C'est la règle d'équité du brief —
    aucune zone prioritaire ne rafle la capacité pendant que d'autres restent
    près de zéro.
    """
    zone = state.zones[zone_code]
    units = state.units.get(zone_code, 0)
    has_direct = zone_code in state.identities
    return (
        # 1. TOUTE zone servable reçoit d'abord UNE occurrence directe.
        #
        #    Sans cette clé, une zone entièrement couverte par du crédit
        #    indirect n'obtient jamais d'exercice : un utilisateur déclarant
        #    « Bras » recevait un programme **sans le moindre curl**, ses
        #    compteurs étant remplis par les tirages et les presses. Les
        #    chiffres semblaient bons et le programme ne servait pas la
        #    demande — exactement ce que la porte de sortie interdit.
        has_direct,
        # 2. À égalité, servir d'abord les zones qui ne reçoivent RIEN
        #    indirectement : le crédit qu'elles génèrent au passage est
        #    ainsi connu avant que les zones receveuses ne soient dosées.
        zone_code in state.indirect_receiving,
        units >= MEANINGFUL_EFFECTIVE_UNITS,
        coverage_ratio(units, zone.planning_low_sets),
        zone.priority_rank is None,
        zone.priority_rank if zone.priority_rank is not None else 0,
        zone_code,
    )


class OvershootKind(StrEnum):
    """Trois états distincts — jamais confondus (décision opérateur §D)."""

    NONE = "none"
    #: Défaut d'allocateur : du volume DIRECT a été ajouté au-delà de la bande.
    #: Doit rester à **zéro**.
    PREVENTABLE = "preventable"
    #: Crédit reçu en servant d'autres zones. Autorisé, explicite, n'invalide
    #: pas le plan.
    INCIDENTAL = "incidental_secondary_contribution"


def classify_overshoot(zone, effective_units: int, allocated_sets: int) -> OvershootKind:
    """Au-dessus de la bande : par sur-allocation, ou par ricochet ?

    `planning_high` est une **bande de planification produit**, pas un plafond
    de sécurité physiologique. La distinction qui compte n'est donc pas
    « au-dessus / en dessous » mais **qui l'a mis là** :

    - `PREVENTABLE` — l'allocateur a attribué du volume direct au-delà de la
      bande. C'est un défaut, et il doit rester à zéro.
    - `INCIDENTAL` — la zone reçoit du crédit parce que d'autres zones sont
      servies. Retirer du travail primaire à `lats` pour faire redescendre un
      compteur de `biceps` appauvrirait une zone sous-servie au profit d'une
      zone que personne n'entraîne directement. Autorisé, et **dit**.
    """
    high_units = units_for_sets(zone.planning_high_sets)
    if effective_units <= high_units:
        return OvershootKind.NONE
    if allocated_sets * UNITS_PER_DIRECT_SET > high_units:
        return OvershootKind.PREVENTABLE
    return OvershootKind.INCIDENTAL


def indirect_receiving_zones(candidates) -> frozenset[str]:
    """Zones susceptibles de recevoir du crédit **indirect** des candidats.

    **Dérivé** de `body_zone_source` via la politique de contribution — aucune
    table écrite à la main du type « le dos donne du biceps ». Si la curation
    des zones secondaires s'élargit, cet ensemble suit tout seul.
    """
    receiving: set[str] = set()
    for ranked in candidates.values():
        for name, _intent in ranked:
            for zone, role in exercise_roles(name).items():
                if role is ContributionRole.INDIRECT:
                    receiving.add(zone)
    return frozenset(receiving)


def incidental_overshoot(zone, effective_units: int, allocated_sets: int) -> bool:
    """Vrai si la zone dépasse sa bande **sans** avoir été sur-allouée.

    `planning_high` plafonne ce que l'allocateur **attribue** à une zone, pas le
    crédit qu'elle reçoit incidemment en servant d'autres zones.

    Le cas se produit réellement : servir `lats` et `upper_back` crédite
    `biceps` en secondaire, ce qui peut le porter au-dessus de sa bande alors
    que **4 séries seulement** lui ont été attribuées en direct. Refuser de
    programmer le dos pour protéger un plafond de biceps affamerait deux zones
    afin d'en préserver une troisième que personne n'entraîne directement —
    c'est le contraire de ce que la bande cherche à éviter.

    Le dépassement est donc **signalé**, jamais empêché.
    """
    allocated_units = allocated_sets * 2
    return (
        effective_units > units_for_sets(zone.planning_high_sets)
        and allocated_units <= units_for_sets(zone.planning_high_sets)
    )


def _headroom_units(state, zone_code: str) -> int:
    """Marge avant `planning_high` pour l'allocation. Contrainte DURE.

    Elle borne ce que l'allocateur **attribue**. Voir `incidental_overshoot`
    pour le crédit indirect, qui n'est pas de l'allocation.
    """
    zone = state.zones[zone_code]
    return max(
        0, units_for_sets(zone.planning_high_sets) - state.units.get(zone_code, 0))


def _credit(state, exercise_name: str, sets: int) -> None:
    """Applique la contribution effective d'une occurrence, zones secondaires
    comprises — la même politique que partout ailleurs, jamais recodée."""
    for zone, role in exercise_roles(exercise_name).items():
        per_set = 2 if role is ContributionRole.DIRECT else 1
        state.units[zone] = state.units.get(zone, 0) + per_set * sets


@dataclass
class _State:
    """État mutable de l'allocation. Interne, jamais exposé."""

    zones: dict
    candidates: dict[str, list[tuple[str, str]]]
    indirect_receiving: frozenset[str] = frozenset()
    units: dict[str, int] = field(default_factory=dict)
    occurrences: list[Occurrence] = field(default_factory=list)
    identities: dict[str, set[str]] = field(default_factory=dict)


def _next_exercise(state, zone_code: str) -> tuple[str, str] | None:
    """Prochain exercice pour cette zone — **stabilité d'abord**.

    On réutilise l'identité déjà retenue tant qu'elle peut resservir dans une
    autre séance. Une seconde identité n'apparaît que si la première est déjà
    présente dans **toutes** les séances où il reste de la place — c'est la
    « raison de planification réelle » exigée, pas de la variété gratuite.
    """
    ranked = state.candidates.get(zone_code) or []
    used = state.identities.get(zone_code) or set()
    for name, intent_id in ranked:
        if name in used:
            return (name, intent_id)
    return ranked[0] if ranked else None


def _placeable_session(state, sessions_load, exercise_name: str) -> int | None:
    """Séance où poser l'occurrence : la plus vide qui ne duplique pas.

    Un même exercice n'apparaît **jamais deux fois dans la même séance** ; il
    peut revenir dans une autre. À défaut, la séance la moins chargée gagne, ce
    qui répartit au lieu d'entasser.
    """
    taken = {
        occurrence.session_index for occurrence in state.occurrences
        if occurrence.exercise_name == exercise_name
    }
    order = sorted(
        range(len(sessions_load)),
        key=lambda i: (sessions_load[i][1], sessions_load[i][0], i),
    )
    for index in order:
        if index + 1 in taken:
            continue
        if _session_room(sessions_load, index):
            return index
    return None


def allocate_capacity(budget_zones, candidates, cadence: int):
    """Répartit la capacité déclarée sur les zones. Déterministe et pur.

    `budget_zones` : les `ZoneVolumeBudget` du budget.
    `candidates` : `{zone_code: [(exercise_name, intent_id), …]}`, déjà classés
    et filtrés par le générateur fermé — cet allocateur ne range **aucun**
    exercice lui-même et n'en invente aucun.

    Renvoie `(occurrences, effective_units)`.

    La boucle sert, à chaque tour, la zone la plus mal couverte qui peut encore
    l'être. Elle s'arrête quand plus aucune zone ne peut progresser — jamais sur
    un quota de séries, puisque `Σ planning_low` n'est pas une cible.
    """
    state = _State(
        zones={z.zone_code: z for z in budget_zones}, candidates=candidates,
        indirect_receiving=indirect_receiving_zones(candidates))
    if cadence <= 0:
        return (), {}

    sessions_load = [[0, 0] for _ in range(cadence)]
    servable = [z for z in state.zones if candidates.get(z)]
    # Borne de sûreté : chaque tour place au moins une série, et la capacité
    # totale est finie. Elle protège d'une boucle infinie si un jour une
    # contrainte devenait non monotone.
    max_rounds = cadence * SOFT_MAX_SETS_PER_SESSION + 1

    # UNE seule passe ordonnée : toute la politique vit dans `_rank_zone`.
    #
    # Une première version séparait l'allocation en deux phases pour que les
    # zones recevant du crédit indirect soient dosées en dernier. Elle a
    # produit un défaut plus grave que celui qu'elle corrigeait : la phase 1
    # consommait **toute** la capacité de séance, et un utilisateur déclarant
    # « Bras » recevait un programme sans le moindre exercice de bras. Le
    # classement ordonné obtient l'effet voulu sans jamais affamer personne.
    for _ in range(max_rounds):
        ordered = sorted(servable, key=lambda z: _rank_zone(state, z))
        if not any(_serve_zone(state, sessions_load, z) for z in ordered):
            break

    return tuple(state.occurrences), dict(state.units)


def _serve_zone(state, sessions_load, zone_code: str) -> bool:
    """Tente UNE occurrence pour cette zone. `False` si rien n'est plaçable.

    Extrait de la boucle : la garde de complexité l'exigeait, et le découpage
    rend surtout lisible la liste des raisons pour lesquelles une zone peut
    rester non servie — bande pleine, aucun candidat, aucune séance libre,
    place insuffisante pour un minimum crédible.
    """
    headroom = _headroom_units(state, zone_code)
    if headroom <= 0:
        return False
    chosen = _next_exercise(state, zone_code)
    if chosen is None:
        return False
    name, intent_id = chosen
    index = _placeable_session(state, sessions_load, name)
    if index is None:
        return False
    sets = _sets_that_fit(sessions_load, index, headroom)
    if sets < SETS_PER_SLOT_MIN:
        return False

    state.occurrences.append(Occurrence(
        exercise_name=name, zone_code=zone_code, intent_id=intent_id,
        session_index=index + 1, planned_sets=sets,
    ))
    state.identities.setdefault(zone_code, set()).add(name)
    sessions_load[index][0] += 1
    sessions_load[index][1] += sets
    _credit(state, name, sets)
    return True


__all__ = [
    "CAPACITY_ALLOCATOR_VERSION",
    "COVERAGE_RATIO_GUARD",
    "MEANINGFUL_EFFECTIVE_UNITS",
    "SESSION_SHAPE_CONVENTION_VERSION",
    "SOFT_MAX_EXERCISES_PER_SESSION",
    "SOFT_MAX_SETS_PER_SESSION",
    "CadenceFeasibility",
    "CapacityReport",
    "Occurrence",
    "OvershootKind",
    "classify_overshoot",
    "indirect_receiving_zones",
    "allocate_capacity",
    "coverage_ratio",
]
