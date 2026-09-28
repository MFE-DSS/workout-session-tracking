"""Résolution d'environnement — créneau puis gabarit (`Sb_TRAIN_A_ENV_02`).

Ce module répond à **une** question : dans un environnement concret, ce
créneau est-il exécutable, et si non, un substitut **déjà autorisé** l'est-il ?

**Il n'a aucune autorité sur le service.** Aucun module de décision ne
l'importe, et une garde le vérifie. Il ne sera branché qu'à l'ouverture de la
dernière porte.

**Ce qu'il ne fait jamais** — et c'est ce qui le rend sûr à construire avant
l'activation :

* il n'invente aucun substitut : la liste lui est **fournie**, dans l'ordre
  que le moteur de substitution a produit (`N1` puis `N2` puis `N3`, chacun
  trié par proximité) ;
* il n'élargit aucune équivalence et ne touche pas aux priorités : il
  **choisit le premier** de la liste dont l'exécution est prouvée, et
  s'arrête là ;
* il ne rend aucun score. Quatre états nommés, pas un continuum.

**Pourquoi `ADAPTABLE` prime sur `UNKNOWN`.** Un substitut dont l'exécution
est *prouvée* rend le créneau servable, que d'autres chemins restent
inconnus ou non : l'incertitude résiduelle ne retire rien à une certitude
acquise. L'inverse — refuser d'adapter parce qu'un autre chemin est flou —
punirait l'utilisateur pour un trou de curation.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.services.equipment_model import (
    FEASIBLE,
    UNKNOWN,
    feasibility,
    missing_capabilities,
    requirements_for_exercise,
)

#: États de créneau (§12). Quatre chaînes, jamais un nombre.
NATIVE_FEASIBLE = "native_feasible"
ADAPTABLE = "adaptable"
SLOT_UNKNOWN = "unknown"
NOT_FEASIBLE = "not_feasible"

#: États de gabarit (§13).
SERVABLE = "servable"
TEMPLATE_UNKNOWN = "unknown"
TEMPLATE_NOT_FEASIBLE = "not_feasible"


@dataclass(frozen=True)
class SlotResolution:
    """Le verdict d'UN créneau, et la trace de ce qui l'a produit."""

    prescribed: str
    state: str
    #: Ce qui sera réellement exécuté. Égal à `prescribed` sauf en
    #: `ADAPTABLE` ; `None` quand aucun chemin n'est prouvé.
    chosen: str | None = None
    #: Capacités manquantes pour le PRESCRIT — sert à expliquer, jamais à
    #: décider. Vide si le prescrit n'est pas connu infaisable.
    missing: tuple[str, ...] = ()
    #: Chemins autorisés dont l'exigence reste inconnue. C'est la dette de
    #: curation, nommée, et non un silence.
    unknown_paths: tuple[str, ...] = ()
    #: Vrai quand le seul substitut exécutable était DÉJÀ retenu ailleurs
    #: dans la même séance. Le créneau reste servable — refuser ici
    #: annoncerait « infaisable » une exécution qui, elle, est possible —
    #: mais le produit doit pouvoir le voir.
    duplicate: bool = False

    @property
    def adapted(self) -> bool:
        return self.state == ADAPTABLE


@dataclass(frozen=True)
class TemplateResolution:
    """Le verdict d'un gabarit et la trace de chacun de ses créneaux."""

    template_slug: str
    state: str
    slots: tuple[SlotResolution, ...] = field(default_factory=tuple)

    @property
    def adapted_slots(self) -> tuple[SlotResolution, ...]:
        return tuple(s for s in self.slots if s.adapted)

    @property
    def blocking_slots(self) -> tuple[SlotResolution, ...]:
        return tuple(s for s in self.slots if s.state == NOT_FEASIBLE)


def resolve_slot(
    prescribed: str,
    authorized_substitutes,
    declared_items: tuple[str, ...] | None,
    already_used=(),
) -> SlotResolution:
    """Résout un créneau (§12).

    `authorized_substitutes` est l'ordre du moteur de substitution, tel
    quel. Le premier substitut **prouvé exécutable** gagne : c'est ainsi que
    la priorité existante est respectée sans être recalculée ici.

    `already_used` porte ce que la séance retient déjà. Le harnais de preuve
    a montré le besoin : dans `push-a`, deux créneaux distincts se
    résolvaient vers `Développé couché haltères`, donnant une séance qui
    prescrit deux fois le même mouvement. Choisir parmi des substituts
    **déjà autorisés** est explicitement permis ; éviter un doublon en est
    un cas, et n'élargit aucune équivalence.

    La préférence n'est pas un refus : si le seul substitut exécutable est
    déjà pris, il est **repris quand même** et le créneau porte
    `duplicate=True`. Annoncer « infaisable » une exécution possible serait
    un mensonge plus coûteux qu'un doublon visible.
    """
    exigences = requirements_for_exercise(prescribed)
    verdict = feasibility(exigences, declared_items)
    if verdict == FEASIBLE:
        return SlotResolution(prescribed, NATIVE_FEASIBLE, chosen=prescribed)

    inconnus: list[str] = [prescribed] if verdict == UNKNOWN else []
    manquantes = missing_capabilities(exigences, declared_items)
    pris = set(already_used)
    replis: list[str] = []

    for substitut in authorized_substitutes:
        sub_verdict = feasibility(
            requirements_for_exercise(substitut), declared_items
        )
        if sub_verdict == FEASIBLE:
            if substitut in pris:
                replis.append(substitut)
                continue
            return SlotResolution(
                prescribed, ADAPTABLE, chosen=substitut,
                missing=manquantes, unknown_paths=tuple(inconnus),
            )
        if sub_verdict == UNKNOWN:
            inconnus.append(substitut)

    if replis:
        return SlotResolution(
            prescribed, ADAPTABLE, chosen=replis[0], missing=manquantes,
            unknown_paths=tuple(inconnus), duplicate=True,
        )
    if inconnus:
        return SlotResolution(
            prescribed, SLOT_UNKNOWN, missing=manquantes,
            unknown_paths=tuple(inconnus),
        )
    return SlotResolution(prescribed, NOT_FEASIBLE, missing=manquantes)


def resolve_template(
    template_slug: str,
    slots,
    declared_items: tuple[str, ...] | None,
) -> TemplateResolution:
    """Résout un gabarit (§13).

    `slots` est une suite de `(prescrit, substituts_autorisés)`. **Tous les
    créneaux d'un gabarit AUREN sont obligatoires** : le catalogue ne porte
    aucune notion de créneau facultatif, et l'inventer ici reviendrait à
    décider qu'un exercice peut sauter — une décision de produit, pas de
    résolveur.

    Un gabarit n'est jamais écarté parce que son exercice d'origine est
    incompatible : si un substitut autorisé passe, le gabarit reste servable.
    """
    slots = list(slots)
    # Les noms PRESCRITS comptent dès le départ : un substitut qui reprend
    # un exercice déjà prescrit ailleurs dans la séance produit le même
    # doublon qu'un substitut repris deux fois.
    retenus: set[str] = {prescrit for prescrit, _ in slots}
    resolus_l: list[SlotResolution] = []
    for prescrit, substituts in slots:
        r = resolve_slot(prescrit, substituts, declared_items, retenus)
        if r.chosen:
            retenus.add(r.chosen)
        resolus_l.append(r)
    resolus = tuple(resolus_l)
    etats = {s.state for s in resolus}
    if NOT_FEASIBLE in etats:
        etat = TEMPLATE_NOT_FEASIBLE
    elif SLOT_UNKNOWN in etats:
        etat = TEMPLATE_UNKNOWN
    else:
        etat = SERVABLE
    return TemplateResolution(template_slug, etat, resolus)


#: §G8 — l'état produit quand AUCUN gabarit n'est servable. Il est nommé
#: plutôt que représenté par une liste vide : « rien à proposer » et « rien
#: n'a été calculé » ne doivent pas se ressembler à l'écran.
NO_SERVABLE_CANDIDATE = "no_servable_candidate"


@dataclass(frozen=True)
class CatalogueResolution:
    """Ce que l'environnement rend du catalogue entier."""

    servable: tuple[TemplateResolution, ...] = ()
    unknown: tuple[TemplateResolution, ...] = ()
    not_feasible: tuple[TemplateResolution, ...] = ()

    @property
    def state(self) -> str:
        """`SERVABLE` · `TEMPLATE_UNKNOWN` · `NO_SERVABLE_CANDIDATE`."""
        if self.servable:
            return SERVABLE
        if self.unknown:
            return TEMPLATE_UNKNOWN
        return NO_SERVABLE_CANDIDATE


def resolve_catalogue(resolutions) -> CatalogueResolution:
    """Répartit des gabarits déjà résolus. §G8.

    `NO_SERVABLE_CANDIDATE` n'est atteint que si **aucun** gabarit n'est
    servable **et** aucun n'est seulement inconnu : un doute laisse le
    produit proposer, un refus généralisé doit se dire.
    """
    resolutions = tuple(resolutions)
    return CatalogueResolution(
        servable=tuple(r for r in resolutions if r.state == SERVABLE),
        unknown=tuple(r for r in resolutions if r.state == TEMPLATE_UNKNOWN),
        not_feasible=tuple(
            r for r in resolutions if r.state == TEMPLATE_NOT_FEASIBLE),
    )


def materialization_plan(resolution: TemplateResolution):
    """§14 — ce qu'il faut écrire AVANT `START`, pas pendant la séance.

    Rend la suite des `(position, prescrit, exécuté)` à matérialiser. La
    lignée reste entière : le prescrit n'est pas effacé, il est **porté à
    côté** de l'exécuté, exactement comme une substitution manuelle.

    La fonction ne matérialise rien elle-même : brancher ce plan sur
    `session_builder` est l'étape d'**activation**, et elle attend les neuf
    portes. Le plan existe pour que cette étape soit une pose, pas une
    conception.
    """
    return tuple(
        (position, s.prescribed, s.chosen)
        for position, s in enumerate(resolution.slots, start=1)
        if s.adapted and s.chosen
    )


def identite_materielle_environnement(resolutions) -> str:
    """§16 / G9 — l'identité de l'environnement **telle qu'elle a compté**.

    Ce n'est **pas** la liste du matériel déclaré. Deux environnements
    différents qui produisent exactement les mêmes exécutions sont, du point
    de vue de la décision, le même environnement : déclarer une machine
    qu'aucun créneau n'utilise ne doit pas périmer un refus. C'est la même
    doctrine que `empreinte_de_contexte`, qui quantifie en bandes plutôt que
    de prendre des continus bruts.

    Symétriquement, un changement qui **modifie une exécution servie**
    change cette identité — et peut donc légitimement périmer un épisode non
    résolu.

    ⚠ Rien n'inclut encore ceci dans l'empreinte, et c'est voulu : le §16
    l'interdit tant que le résolveur n'affecte pas le résultat servi. Une
    garde vérifie que l'empreinte ignore l'environnement aujourd'hui.
    """
    import hashlib

    pieces = []
    for r in sorted(resolutions, key=lambda x: x.template_slug):
        pieces.append(r.template_slug)
        pieces.append(r.state)
        for s in r.slots:
            pieces.append(f"{s.prescribed}>{s.chosen or ''}")
    brut = "|".join(pieces)
    return hashlib.sha256(brut.encode("utf-8")).hexdigest()[:16]


def adaptation_notice(resolution: TemplateResolution) -> str | None:
    """§15 — un fait bref, ou rien.

    Ni la liste des substitutions, ni un décompte : la lignée complète
    `prescrit → réalisé` vit déjà dans le détail de séance. Mission n'en
    porte que le fait, et seulement s'il a eu lieu.
    """
    return "Adapté à ton équipement." if resolution.adapted_slots else None


__all__ = [
    "ADAPTABLE",
    "NO_SERVABLE_CANDIDATE",
    "CatalogueResolution",
    "adaptation_notice",
    "identite_materielle_environnement",
    "materialization_plan",
    "resolve_catalogue",
    "NATIVE_FEASIBLE",
    "NOT_FEASIBLE",
    "SERVABLE",
    "SLOT_UNKNOWN",
    "TEMPLATE_NOT_FEASIBLE",
    "TEMPLATE_UNKNOWN",
    "SlotResolution",
    "TemplateResolution",
    "resolve_slot",
    "resolve_template",
]
