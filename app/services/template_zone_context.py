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


@dataclass(frozen=True)
class TemplateZones:
    """Les zones d'UN gabarit. Vide = rien à dire, pas « ne travaille rien »."""

    zones: tuple[ZoneMark, ...] = ()

    @property
    def declared(self) -> tuple[ZoneMark, ...]:
        return tuple(z for z in self.zones if z.is_declared)

    def shown(self, active_zone: str | None = None) -> tuple[ZoneMark, ...]:
        """Les zones qui MÉRITENT d'être rendues sur la carte.

        `Sb_UI_BIBLIO_01` — la carte rendait ses quatre zones, dont trois
        redisaient son titre (« Pecs épaisseur + Delts + Triceps » contre
        « Pectoraux · Deltoïdes latéraux · Deltoïdes postérieurs · Triceps »).
        Le signal — la zone DÉCLARÉE en priorité, en ambre — se noyait dans sa
        propre redite.

        Deux zones méritent d'être dites, et deux seulement :

        * celle que l'utilisateur a **déclarée en priorité** — le titre ne la
          porte pas, elle est personnelle ;
        * celle sur laquelle il **filtre en ce moment** — sinon le filtre garde
          des cartes sans dire pourquoi. La garde
          `test_every_template_kept_by_the_filter_really_works_that_zone` le
          formule mieux : « un filtre qui garde un gabarit sans la zone demandée
          ment deux fois ». Ma première écriture ne gardait que les déclarées,
          et c'est cette garde qui l'a arrêtée.

        Rien d'autre : le titre le dit déjà.
        """
        return tuple(
            z for z in self.zones if z.is_declared or z.code == active_zone
        )

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


def annotate_templates(db: Session, templates, focus_priorities=None
                       ) -> dict[int, TemplateZones]:
    """Annote chaque gabarit des zones qu'il travaille, indexé par `id`.

    Les résolutions sont mémoïsées **par appel**, sur le nom d'exercice : le
    catalogue en répète beaucoup d'un gabarit à l'autre, et un cache qui ne
    survit pas à la requête ne peut pas devenir périmé quand le référentiel
    change. Mesuré sans mémoïsation : 80 exercices, 160 requêtes, ~20 ms.
    """
    declared = priority_zones(focus_priorities)
    seen: dict[str, str | None] = {}
    out: dict[int, TemplateZones] = {}

    for tpl in templates:
        codes: list[str] = []
        for ex in tpl.exercises:
            name = ex.name
            if name not in seen:
                seen[name] = resolve_zone(db, name).zone
            zone = seen[name]
            # `None` = aucune autorité ne reconnaît l'exercice. On ne le compte
            # pas, et on n'invente pas de zone voisine.
            if zone is not None and zone not in codes:
                codes.append(zone)

        # Ordre canonique de `ZONE_LABELS`, pas l'ordre d'apparition dans le
        # gabarit : deux gabarits aux mêmes zones doivent se lire pareil.
        ordered = [c for c in ZONE_LABELS if c in codes]
        out[tpl.id] = TemplateZones(tuple(
            ZoneMark(code=c, label=ZONE_LABELS[c], declared_as=declared.get(c))
            for c in ordered
        ))
    return out
