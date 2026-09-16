"""`UI-CP3.5` — CONTINUITÉ : le plan effectif se souvient d'une décision.

LE PROBLÈME QUE CE MODULE RÉSOUT
--------------------------------
MISSION était **sans mémoire** : elle recalculait à chaque affichage, et le
même moteur avec le même état produisait la même phrase pour n'importe qui.

Recalculer `replan()` à chaque rendu n'aurait rien changé — **une
recomputation pure reste sans état**. Pour que MISSION puisse dire
« ajusté samedi », il faut qu'une décision ait été PRISE à un moment, qu'elle
soit persistée, et qu'elle **change réellement** la projection du plan. Sinon
le produit ne peut dire que « proposé ».

L'ÉQUATION
----------
::

    PLAN DE BASE  +  ADAPTATIONS ACTIVES APPLICABLES  =  PLAN EFFECTIF

Le plan reste **dérivé** — rien du plan n'est stocké. `build_weekly_plan` est
pure (« aucune I/O, aucune horloge, aucun aléa ») et accepte un **budget
injecté** : il suffit donc de transformer le budget pour que le plan change.

CE QUI EST PERSISTÉ, ET CE QUI NE L'EST PAS
-------------------------------------------
Persisté : **la décision**, dans `decision_traces` — une table qui existait
déjà, qui porte l'identité d'exécution, l'identité de contenu, l'empreinte de
plan, la justification, et dont l'immuabilité est imposée par un écouteur
`before_update`. Le type `REPLAN_DELTA` y était **déclaré et jamais émis**.

Non persisté : le plan, le cycle de vie autre que l'écartement, et la
supersession — qui se **dérive** (voir `active_adaptations`).

L'INVARIANT QUI GOUVERNE LA CONSÉQUENCE
---------------------------------------
`PlanDelta.is_reduction` exige `sets_after <= sets_before` **sur les deux
axes**. Compenser ailleurs dans la semaine est donc interdit par construction.
La seule conséquence exprimable est le **report** : la cible de la zone
sous-servie descend à ce qui a réellement été couvert, le reste sort de la
semaine courante — *« travail reporté, non supprimé »*.

C'est aussi la règle d'asymétrie du contrat de récupération : un signal dégradé
peut rendre le système plus prudent, jamais plus agressif.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

from app.services.weekly_volume_budget import WeeklyVolumeBudget

#: Motif porté par le delta et par le `basis`. Repris mot pour mot du moteur de
#: replanification, qui l'emploie déjà pour la même idée : le travail SORT de la
#: semaine, il n'est pas déclaré inutile.
REASON_DEFERRED = "travail reporté, non supprimé"


@dataclass(frozen=True)
class ZoneDeferral:
    """Une zone dont la cible hebdomadaire descend à ce qui a été couvert."""

    zone_code: str
    sets_before: int
    sets_after: int

    @property
    def sets_deferred(self) -> int:
        """Jamais négatif — la garantie que ceci n'est pas une augmentation."""
        return max(0, self.sets_before - self.sets_after)


@dataclass(frozen=True)
class Adaptation:
    """Une décision prise à un moment, et qui s'applique — ou plus.

    `decided_at` et `deferrals` sont **immuables** : ils viennent d'une ligne
    de `decision_traces` que l'ORM refuse de modifier. C'est ce qui permet à
    MISSION de citer la même date à chaque rendu au lieu de raconter un
    recalcul.
    """

    decision_id: str
    decided_at: object          #: `datetime` — l'ORM en est la source
    plan_fingerprint: str       #: l'empreinte du plan de BASE au moment décidé
    deferrals: tuple[ZoneDeferral, ...]
    done: int                   #: séries faites dans la séance déclenchante
    total: int                  #: séries prescrites dans cette séance
    basis: tuple[str, ...] = ()

    @property
    def is_material(self) -> bool:
        """Une adaptation sans conséquence ne s'affiche pas.

        Sans cette garde, une décision dont tous les reports valent zéro
        produirait un bloc de continuité qui n'annonce aucun changement — le
        « bruit qui ressemble à de la mémoire ».
        """
        return any(d.sets_deferred > 0 for d in self.deferrals)


def applicable(adaptation: Adaptation, base_fingerprint: str) -> bool:
    """L'adaptation vaut-elle encore pour CE contexte de plan ?

    ⚠ LA SUPERSESSION EST DÉRIVÉE, PAS MARQUÉE.

    On compare l'empreinte du plan de **BASE** — jamais celle du plan effectif.
    Ancrer sur l'effectif créerait une boucle : l'adaptation change le plan,
    l'empreinte change, l'adaptation paraît périmée, le plan revient, et ainsi
    de suite. Le piège est réel et il est écrit ici pour qu'on ne le retrouve
    pas par l'expérience.

    Un changement de cadence, de matériel ou de catalogue change l'empreinte de
    base et périme donc automatiquement les décisions prises contre l'ancien
    contexte. **L'historique survit ; le comportement, non.**
    """
    return adaptation.plan_fingerprint == base_fingerprint


def apply_to_budget(
    budget: WeeklyVolumeBudget, adaptations: tuple[Adaptation, ...]
) -> WeeklyVolumeBudget:
    """Compose le budget EFFECTIF. Transformation **pure**.

    Aucune I/O, aucune horloge : mêmes entrées, même sortie. C'est ce qui rend
    la comparaison « plan de base vs plan effectif » vérifiable par une garde.

    La raison rejoint `basis` de la zone touchée — le type le prévoyait déjà,
    et une borne qui bouge sans dire pourquoi est exactement ce que le dépôt
    reproche aux readouts muets.

    ⚠ CE REPORT REDISTRIBUE. MESURÉ, PAS SUPPOSÉ — ET J'AI ESSAYÉ DE
    L'EMPÊCHER.

    Reporter 6 séries de pectoraux rend un plan effectif où la chaîne
    postérieure passe de **8 à 14 séries**, total conservé à 96 :
    l'allocateur sert « la zone la plus mal couverte » et place ailleurs la
    capacité libérée.

    J'ai tenté de le border par un plafond figeant chaque zone à ce que le
    plan de base lui donnait. Résultat mesuré : **biceps 4 → 0**, c'est-à-dire
    exactement le défaut que la clé de classement n° 1 de l'allocateur existe
    pour empêcher — *« un utilisateur déclarant Bras recevait un programme sans
    le moindre curl »*.

    La cause est une ERREUR DE CATÉGORIE de ma part. Le plan de base
    **n'atteint jamais la bande basse du budget** : `pecs` a une bande basse de
    14 pour 12 servis, `biceps` 8 pour 4 — la cadence borne la capacité
    en-dessous des cibles de volume. Plafonner une BANDE par une COUVERTURE
    produit une bande inversée sur huit zones sur onze. Deux échelles
    différentes.

    **Conclusion : dans ce planificateur, un report redistribue
    nécessairement.** C'est un fait d'architecture, pas une préférence, et
    aucune borne de budget ne l'exprime autrement.

    Ce que cela NE viole PAS : la charge totale est inchangée, la cadence est
    inchangée, aucune séance ne s'allonge. L'asymétrie porte sur l'agressivité
    du système, et le moteur nomme lui-même la redistribution comme une issue
    admise — *« l'adaptation ne peut que réduire ou redistribuer »*.

    Ce que la surface dira donc : **le report**, qui est certain et matériel.
    Pas la réaffectation mécanique qui en découle, qui n'est pas une décision.
    """
    if not adaptations:
        return budget

    #: Report le plus CONSERVATEUR par zone : si deux décisions actives
    #: concernent la même zone, on retient la cible la plus basse. Jamais la
    #: plus haute — ce serait une augmentation par la porte de derrière.
    cibles: dict[str, int] = {}
    for a in adaptations:
        for d in a.deferrals:
            if d.sets_deferred <= 0:
                continue
            actuel = cibles.get(d.zone_code)
            cibles[d.zone_code] = (
                d.sets_after if actuel is None else min(actuel, d.sets_after)
            )

    if not cibles:
        return budget

    zones = [
        z if z.zone_code not in cibles else replace(
            z,
            # Les TROIS bornes descendent ensemble : une bande dont le plafond
            # passe sous le plancher est incohérente, et l'allocateur en tire
            # des plans absurdes. Mesuré.
            planning_low_sets=min(z.planning_low_sets, cibles[z.zone_code]),
            baseline_sets=min(z.baseline_sets, cibles[z.zone_code]),
            planning_high_sets=min(z.planning_high_sets, cibles[z.zone_code]),
            basis=(*z.basis, REASON_DEFERRED),
        )
        for z in budget.zones
    ]
    return replace(budget, zones=tuple(zones))


def build_effective_plan(preferences, adaptations: tuple[Adaptation, ...]):
    """`(plan_de_base, plan_effectif)` — l'équation de CP3.5, en une fonction.

    Le plan de base est calculé d'abord parce qu'il fournit **deux** choses :
    l'empreinte contre laquelle l'applicabilité se juge, et le plafond par zone
    qui interdit toute augmentation.

    Rien n'est stocké. `build_weekly_plan` est pure, donc rejouer cette
    fonction avec les mêmes entrées rend exactement les mêmes plans — c'est ce
    qui permet à MISSION de répéter la même phrase sans rien mémoriser d'autre
    que la DÉCISION.
    """
    from app.services.weekly_planner import build_weekly_plan
    from app.services.weekly_volume_budget import build_weekly_volume_budget

    budget_base = build_weekly_volume_budget(preferences)
    plan_base = build_weekly_plan(preferences, budget_base)

    actives = tuple(
        a for a in adaptations
        if a.is_material and applicable(a, plan_base.fingerprint)
    )
    if not actives:
        return plan_base, plan_base

    budget_eff = apply_to_budget(budget_base, actives)
    return plan_base, build_weekly_plan(preferences, budget_eff)


def deferrals_for(
    delivered_by_zone: dict[str, int],
    planned_by_zone: dict[str, int],
) -> tuple[ZoneDeferral, ...]:
    """Ce que la séance incomplète laisse de côté, zone par zone.

    Une zone n'entre dans le résultat que si le plan en prévoyait **plus** que
    ce qui a été fait. Une zone servie au-delà de sa cible ne produit rien :
    il n'y a rien à reporter, et surtout rien à augmenter.

    Les zones absentes de `delivered_by_zone` sont traitées comme **non
    attribuées**, pas comme des zéros — on ignore ce que l'exercice non résolu
    a sollicité, et compter son absence pour zéro reporterait du travail au
    motif qu'on n'a pas su le classer.
    """
    out = []
    for zone, fait in sorted(delivered_by_zone.items()):
        prevu = planned_by_zone.get(zone)
        if prevu is None or prevu <= fait:
            continue
        out.append(ZoneDeferral(
            zone_code=zone, sets_before=prevu, sets_after=fait))
    return tuple(out)


__all__ = [
    "REASON_DEFERRED",
    "Adaptation",
    "ZoneDeferral",
    "applicable",
    "apply_to_budget",
    "deferrals_for",
]
