"""`UX4_02` / TRAIN 2 tranche B — ce qu'un gabarit travaille, et ce que
l'utilisateur en a déclaré.

CE QUE CE MODULE EST, ET CE QU'IL N'EST PAS
-------------------------------------------
`OPERATOR_DECISION` **C8** : découverte contextualisée sur un corpus commun,
**aucun moteur de recommandation opaque, contexte de plan explicite
uniquement**. Ce module tient les deux bouts :

* il **n'ordonne pas**, ne filtre pas, ne masque pas, ne note pas. Il ne rend
  aucun score et aucun classement. Le corpus reste commun et dans son ordre
  d'affichage — c'est l'appelant qui décide de ce qu'il montre ;
* il ne produit que **deux sortes d'énoncés**, tous deux attribuables :

  1. **un FAIT** — les zones qu'un gabarit travaille, résolues par
     `resolve_zone`, LE résolveur canonique, dont l'autorité est la table
     `ExerciseMuscleMapping`. Mesuré sur le catalogue réel : **80 exercices sur
     80 résolus en `DB_EXACT`**, zéro repli hérité, zéro non résolu ;
  2. **une DÉCLARATION** — parmi ces zones, celles que l'utilisateur a lui-même
     posées en priorité, via `RADAR_AXES`, la relation canonique axe → zones
     qu'utilisent déjà le planificateur et la notation.

La seconde n'est jamais un jugement : elle rappelle à l'utilisateur ce **qu'il
a dit**, à l'endroit où ça l'aide à choisir. C'est la définition même d'un
contexte explicite.

CE QUI A ÉTÉ MESURÉ PUIS ÉCARTÉ
--------------------------------
Une troisième étiquette était prévue — « zone sous le volume visé dans ton
plan », depuis `assess_materialization(...).unmet_zones`. **Mesurée avant
d'être écrite : sur une déclaration de 4 séances, 7 des 11 zones sont sous la
cible.** L'étiquette serait tombée sur presque chaque carte : du bruit, pas du
contexte. Elle n'est pas implémentée, et cette phrase est la raison.

`core` n'a délibérément **pas** d'axe radar (`ZONE_TO_RADAR_AXIS` l'omet) : un
gabarit qui ne travaille que le core ne peut donc porter aucune priorité
déclarée. Ce n'est pas un trou, c'est la taxonomie.
"""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.services.exercise_zone_resolver import resolve_zone
from app.services.muscle_mapping import RADAR_AXES, ZONE_LABELS


@dataclass(frozen=True)
class ZoneMark:
    """Une zone travaillée par un gabarit, et si elle est déclarée en priorité."""

    code: str
    label: str
    #: Libellé de l'axe déclaré (« Bras »), ou `None`. JAMAIS un score.
    declared_as: str | None = None

    @property
    def is_declared(self) -> bool:
        return self.declared_as is not None


# ── états de zone — `UI-CP4 LOADOUT §7`, et ils ne se confondent JAMAIS ────
#
# `KNOWN / INFERRED / UNKNOWN` est une grammaire de PREUVE. Ce n'est **pas** un
# remplaçant des états de domaine, et c'est exactement la correction que
# l'opérateur a portée sur la proposition CP4 : deux de ces trois états sont
# parfaitement **CONNUS**.
#
# Avant CP4, les trois rendaient le même vide à l'écran — une séance cardio
# sans exercice, une séance dont aucune zone n'intéresse l'utilisateur, et une
# séance aux exercices non reconnus se ressemblaient parfaitement.

#: Des zones cartographiées existent. Qu'aucune ne corresponde à une priorité
#: déclarée est un fait CONNU, pas une lacune — et surtout pas un reproche.
ZONES_MAPPED = "MAPPED"

#: L'objet ne prescrit aucune zone cartographiée, et le produit le SAIT : il
#: n'a aucun exercice. Le LISS pur est exactement ce cas. **KNOWN.**
ZONES_NONE_DEFINED = "NO_ZONES_DEFINED"

#: Des exercices existent, et **aucun** n'est reconnu par le référentiel. Là, et
#: là seulement, le produit manque d'information. **UNKNOWN.**
ZONES_UNKNOWN = "ZONES_UNKNOWN"


@dataclass(frozen=True)
class TemplateZones:
    """Les zones d'UNE configuration, et lequel des trois états la décrit.

    ⚠ `state` porte ce que le tuple vide ne pouvait pas dire. `zones == ()`
    restait ambigu : « aucun exercice » et « des exercices qu'on ne reconnaît
    pas » sont deux situations opposées — la première est une connaissance, la
    seconde un trou — et elles rendaient le même vide.

    Le défaut par défaut reste `MAPPED` pour que les constructions directes
    existantes gardent exactement leur sens.
    """

    zones: tuple[ZoneMark, ...] = ()
    state: str = ZONES_MAPPED

    @property
    def declared(self) -> tuple[ZoneMark, ...]:
        return tuple(z for z in self.zones if z.is_declared)

    @property
    def is_no_priority_match(self) -> bool:
        """Des zones existent, aucune n'est déclarée — et c'est un fait CONNU.

        Cet état ne produit **aucune** phrase d'absence : les zones elles-mêmes
        sont rendues, simplement sans marque. Une absence qui se lit par la
        présence de ce qui la remplace n'a pas besoin d'être écrite — l'écrire
        en ferait un reproche (`A4`).
        """
        return self.state == ZONES_MAPPED and not self.declared

    # ⚠ `shown(active_zone)` A ÉTÉ RETIRÉE PAR `UI-CP4 LOADOUT` — son dernier
    # appelant était la carte de `/library`, qui n'existe plus. Ce qu'elle
    # savait est conservé, parce que ça vaut plus que la méthode :
    #
    #   1. UNE ZONE QUI REDIT LE TITRE N'AJOUTE RIEN. « Push A — Pecs épaisseur
    #      + Delts + Triceps » face à « Pectoraux · Deltoïdes latéraux ·
    #      Deltoïdes postérieurs · Triceps » : trois pastilles pour rien, et le
    #      signal noyé dans sa propre redite. CP4 en tire la règle générale —
    #      ce que le nom porte déjà, la ligne ne le répète pas — et descend
    #      toutes les zones dans le dépli.
    #
    #   2. UN FILTRE DOIT SE JUSTIFIER SUR CHAQUE LIGNE QU'IL GARDE. C'est
    #      `test_every_row_kept_by_the_filter_says_why` (anciennement
    #      `..._every_template_kept_by_the_filter_really_works_that_zone`), et
    #      cette garde a arrêté le même défaut DEUX fois, en sens opposés : une
    #      première écriture ne rendait que les zones déclarées ; CP4 a failli
    #      n'en rendre aucune. La zone filtrée reste donc sur la ligne, seule de
    #      toutes les zones.

    def __bool__(self) -> bool:
        return bool(self.zones)


def priority_zones(focus_priorities) -> dict[str, str]:
    """Zones couvertes par les priorités déclarées → libellé de l'AXE déclaré.

    On rend le libellé de l'axe et non celui de la zone : l'utilisateur a
    déclaré « Bras », pas « Biceps ». Lui renvoyer « Biceps » comme si c'était
    son mot serait lui prêter une déclaration qu'il n'a pas faite.
    """
    out: dict[str, str] = {}
    for axis in focus_priorities or ():
        spec = RADAR_AXES.get(axis)
        if spec is None:
            # Un axe inconnu est ignoré, jamais deviné : le vocabulaire est
            # fermé, et un axe hors vocabulaire signale une donnée corrompue,
            # pas une intention à interpréter.
            continue
        for zone in spec["zones"]:
            out.setdefault(zone, spec["label"])
    return out


def zones_for_names(db: Session, names, declared: dict, seen: dict
                    ) -> TemplateZones:
    """Les zones d'une suite de noms d'exercices, et l'état qui la décrit.

    LA forme générale, et le seul endroit du produit qui résout des zones pour
    une configuration. Elle prend des **noms** et non des entités parce que les
    deux arbres ne nomment pas leur champ pareil — `TemplateExercise.name` d'un
    côté, `UserProgramExercise.exercise_name` de l'autre. Faire porter cette
    différence à l'appelant évite un second résolveur qui finirait par diverger.

    `seen` mémoïse par nom pour la durée de l'appel : le catalogue répète
    beaucoup d'exercices d'une séance à l'autre, et un cache qui ne survit pas à
    la requête ne peut pas devenir périmé quand le référentiel change. Mesuré
    sans mémoïsation : 80 exercices, 160 requêtes, ~20 ms.
    """
    names = list(names)
    if not names:
        # Rien à résoudre parce qu'il n'y a rien à résoudre : le produit le SAIT.
        return TemplateZones((), ZONES_NONE_DEFINED)

    codes: list[str] = []
    for name in names:
        if name not in seen:
            seen[name] = resolve_zone(db, name).zone
        zone = seen[name]
        # `None` = aucune autorité ne reconnaît l'exercice. On ne le compte pas,
        # et on n'invente pas de zone voisine.
        if zone is not None and zone not in codes:
            codes.append(zone)

    if not codes:
        # Des exercices existent et AUCUN n'est reconnu — le seul vrai UNKNOWN.
        return TemplateZones((), ZONES_UNKNOWN)

    # Ordre canonique de `ZONE_LABELS`, pas l'ordre d'apparition : deux
    # configurations aux mêmes zones doivent se lire pareil.
    ordered = [c for c in ZONE_LABELS if c in codes]
    return TemplateZones(
        tuple(
            ZoneMark(code=c, label=ZONE_LABELS[c], declared_as=declared.get(c))
            for c in ordered
        ),
        ZONES_MAPPED,
    )


def annotate_templates(db: Session, templates, focus_priorities=None
                       ) -> dict[int, TemplateZones]:
    """Annote chaque gabarit de catalogue des zones qu'il travaille, par `id`."""
    declared = priority_zones(focus_priorities)
    seen: dict[str, str | None] = {}
    return {
        tpl.id: zones_for_names(db, (ex.name for ex in tpl.exercises),
                                declared, seen)
        for tpl in templates
    }
