"""Budget de volume hebdomadaire (Sb_WEEKLY_VOLUME_BUDGET_01).

Tranche 1/3 du train `AUREN_CORE_ORCHESTRATION_01`. **Premier consommateur réel
des préférences persistées** de `Sb_TRAINING_PREFERENCES_01`.

**Fonction pure.** Aucune table, aucune migration, aucune écriture. Un budget est
**dérivé**, pas déclaré : le stocker reviendrait à figer un calcul en fait
utilisateur, exactement ce que la tranche précédente s'est employée à rendre
impossible. Seule une préférence *déclarée* est persistée, et elle l'est déjà.

## Ce que les bornes sont, et ne sont pas

`PLANNING_TOLERANCE_SETS = 2` est une **tolérance de planification produit**.

Ce n'est **pas** un volume minimal efficace, pas un maximum récupérable, pas une
plage optimale, pas une capacité de récupération mesurée, pas un seuil
biologique. Aucune littérature n'est invoquée pour justifier ±2 — les
observations de type dose-réponse soutiennent une **sémantique** de rendements
décroissants, jamais un seuil universel par zone.

Les noms de champs le disent : `planning_low_sets` / `baseline_sets` /
`planning_high_sets`, et **jamais** `minimum_sets`, `maximum_sets`, `MEV` ou
`MRV` — des termes qui affirmeraient une propriété physiologique que ce service
n'observe pas.

La base vient du **référentiel hérité** (`ZONE_VOLUME_TARGET`, semé sur
`BodyZone.volume_target`). C'est une **baseline produit**, pas une vérité
scientifique, et chaque résultat le dit dans son `source`.

## Ce que cette tranche ne calcule PAS

**Les priorités ne créent pas de volume.** Une priorité déclarée est projetée
vers ses zones et **annotée** — rang, origine, direction préférée — sans jamais
déplacer une borne. Décider du point exact dans la bande appartient au
planificateur, qui seul connaîtra la cadence, l'équipement et la faisabilité des
créneaux. Résoudre une allocation globale ici, avant ces contraintes, produirait
un chiffre que le planificateur devrait ensuite contredire.

**La cadence ne change pas la dose.** `sessions_per_week` est un contexte de
répartition : 1, 3 ou 6 séances par semaine ne rendent pas une zone plus ou
moins « dosable ». Le planificateur distribue le budget sur la cadence déclarée ;
il ne le redimensionne pas.

**Le comptage des séries reste celui du dépôt.** Aucune comptabilité
fractionnaire directe/indirecte n'est introduite : changer l'unité de comptage
est une migration sémantique qui exige un audit des consommateurs. Voir
`SET_CONTRIBUTION_CANDIDATE`.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.services.muscle_mapping import (
    RADAR_AXES,
    ZONE_LABELS,
    ZONE_VOLUME_TARGET,
)
from app.services.training_preferences import TrainingPreferencesData

#: Version de la **politique de planification**, pas du contrat de données.
#: Elle voyage avec chaque zone pour qu'un consommateur puisse dire de quelle
#: règle un chiffre provient.
POLICY_VERSION = "weekly-volume-v1"

#: Demi-largeur de la bande de planification, en séries hebdomadaires.
#:
#: **Décision produit d'opérateur, assumée comme telle.** Le dépôt ne contient
#: qu'une valeur unique par zone et aucune bande canonique ; il fallait donc en
#: choisir une. ±2 donne une latitude exploitable par un planificateur sans
#: prétendre décrire une physiologie. La faire varier change les bandes de façon
#: déterministe, sans toucher ni `BodyZone` ni le schéma — un test le prouve.
PLANNING_TOLERANCE_SETS = 2

#: Origine de la base. Nommée pour qu'aucun consommateur n'ait à deviner si un
#: chiffre vient de l'utilisateur ou du système.
SOURCE_LEGACY_BASELINE = "legacy_zone_volume_target"

#: Origine d'une priorité : l'utilisateur l'a **déclarée**.
PRIORITY_SOURCE_USER = "USER_DECLARED"

#: Direction préférée à l'intérieur de la bande. Une **indication** pour le
#: planificateur, pas un déplacement de borne.
DIRECTION_HIGHER = "HIGHER_WITHIN_BAND"

#: Candidat futur, **volontairement non construit ici**. Introduire un poids
#: fractionnaire pour les séries indirectes changerait l'unité de comptage de
#: tout le dépôt (`muscle_scoring`, la qualité de programme, les séances
#: enregistrées). C'est une migration sémantique, pas un réglage.
SET_CONTRIBUTION_CANDIDATE = {
    "direct": 1,
    "indirect": "fractional — requires a consumer audit before it can exist",
}


@dataclass(frozen=True)
class ZoneVolumeBudget:
    """Bande de planification hebdomadaire pour **une** zone détaillée."""

    zone_code: str
    zone_label: str
    planning_low_sets: int
    baseline_sets: int
    planning_high_sets: int
    basis: tuple[str, ...]
    source: str
    policy_version: str = POLICY_VERSION

    #: Métadonnées de priorité — présentes **uniquement** si l'utilisateur a
    #: déclaré une priorité couvrant cette zone. Elles n'influencent aucune
    #: borne dans cette version.
    priority_rank: int | None = None
    priority_source: str | None = None
    preferred_direction: str | None = None

    #: `True` quand la base vient du référentiel et non d'une déclaration : le
    #: consommateur doit pouvoir distinguer « supposé » de « dit ».
    system_assumption: bool = True


@dataclass(frozen=True)
class WeeklyVolumeBudget:
    """Budget complet — **toutes** les zones canoniques, toujours.

    Une zone absente serait indiscernable d'une zone oubliée. Une zone sans
    priorité déclarée reste présente avec ses métadonnées de priorité à `None`.
    """

    zones: tuple[ZoneVolumeBudget, ...] = ()
    policy_version: str = POLICY_VERSION
    sessions_per_week: int | None = None
    basis: tuple[str, ...] = field(default_factory=tuple)

    def zone(self, zone_code: str) -> ZoneVolumeBudget | None:
        for entry in self.zones:
            if entry.zone_code == zone_code:
                return entry
        return None


def planning_band(baseline_sets: int) -> tuple[int, int, int]:
    """`(low, baseline, high)` — l'unique endroit où la bande est calculée.

    Le plancher est borné à zéro : une base faible ne doit pas produire une
    borne négative, qui n'a pas de sens en séries.
    """
    low = max(0, baseline_sets - PLANNING_TOLERANCE_SETS)
    high = baseline_sets + PLANNING_TOLERANCE_SETS
    return (low, baseline_sets, high)


def _priority_rank_by_zone(
    focus_priorities: tuple[str, ...] | None,
) -> dict[str, int]:
    """Projette des axes radar déclarés vers les zones, via la table canonique.

    Aucune correspondance nouvelle n'est inventée : `RADAR_AXES[axis]["zones"]`
    est la projection déjà utilisée par le profil et par P0.4. `core`
    n'appartient à aucun axe, donc il ne peut pas être priorisé — la même limite
    que le roll-up macro, pas une nouvelle.

    Un axe inconnu est **ignoré** plutôt que deviné : le vocabulaire est validé
    à l'écriture par `Sb_TRAINING_PREFERENCES_01`, donc un jeton hors table ici
    signifie que la taxonomie a bougé, pas que l'utilisateur a voulu autre chose.
    """
    ranks: dict[str, int] = {}
    if not focus_priorities:
        return ranks
    for position, axis_key in enumerate(focus_priorities, start=1):
        axis = RADAR_AXES.get(axis_key)
        if axis is None:
            continue
        for zone_code in axis["zones"]:
            # Premier rang gagnant : un axe mieux classé ne doit pas être
            # rétrogradé par un axe suivant qui partagerait une zone.
            ranks.setdefault(zone_code, position)
    return ranks


def build_weekly_volume_budget(
    preferences: TrainingPreferencesData | None = None,
) -> WeeklyVolumeBudget:
    """Budget hebdomadaire déterministe. **Pure** — aucune I/O, aucune horloge.

    Les mêmes entrées produisent le même objet, champ pour champ.
    """
    prefs = preferences or TrainingPreferencesData()
    ranks = _priority_rank_by_zone(prefs.focus_priorities)

    zones: list[ZoneVolumeBudget] = []
    for zone_code, baseline in ZONE_VOLUME_TARGET.items():
        low, base, high = planning_band(baseline)
        rank = ranks.get(zone_code)
        basis = [
            f"{base} séries/semaine — base du référentiel produit, non mesurée",
            f"bande de planification ±{PLANNING_TOLERANCE_SETS} "
            f"({POLICY_VERSION}) — tolérance produit, pas un seuil biologique",
        ]
        if rank is not None:
            basis.append(
                f"priorité déclarée par l'utilisateur (rang {rank}) — "
                "oriente le choix dans la bande, ne déplace aucune borne"
            )
        zones.append(
            ZoneVolumeBudget(
                zone_code=zone_code,
                zone_label=ZONE_LABELS.get(zone_code, zone_code),
                planning_low_sets=low,
                baseline_sets=base,
                planning_high_sets=high,
                basis=tuple(basis),
                source=SOURCE_LEGACY_BASELINE,
                priority_rank=rank,
                priority_source=PRIORITY_SOURCE_USER if rank else None,
                preferred_direction=DIRECTION_HIGHER if rank else None,
            )
        )

    top_basis = [
        f"politique {POLICY_VERSION} — bandes dérivées du référentiel hérité",
    ]
    if prefs.sessions_per_week is None:
        top_basis.append(
            "cadence non déclarée — le budget hebdomadaire est inchangé, "
            "seule sa répartition future en dépend"
        )
    else:
        top_basis.append(
            f"{prefs.sessions_per_week} séance(s)/semaine déclarée(s) — "
            "contexte de répartition, sans effet sur les bandes"
        )
    if prefs.focus_priorities is None:
        top_basis.append("aucune priorité déclarée")
    elif not prefs.focus_priorities:
        top_basis.append("aucune priorité particulière, déclarée explicitement")

    return WeeklyVolumeBudget(
        zones=tuple(zones),
        sessions_per_week=prefs.sessions_per_week,
        basis=tuple(top_basis),
    )


def build_weekly_volume_budget_for_user(db, user_id: int) -> WeeklyVolumeBudget:
    """Commodité base de données : lit les préférences, puis calcule. Lecture seule."""
    from app.services.training_preferences import get_training_preferences

    return build_weekly_volume_budget(get_training_preferences(db, user_id))


__all__ = [
    "DIRECTION_HIGHER",
    "PLANNING_TOLERANCE_SETS",
    "POLICY_VERSION",
    "PRIORITY_SOURCE_USER",
    "SET_CONTRIBUTION_CANDIDATE",
    "SOURCE_LEGACY_BASELINE",
    "WeeklyVolumeBudget",
    "ZoneVolumeBudget",
    "build_weekly_volume_budget",
    "build_weekly_volume_budget_for_user",
    "planning_band",
]
