"""Replanification adaptative (Sb_ADAPTIVE_REPLAN_01).

Tranche 3/3 du train `AUREN_CORE_ORCHESTRATION_01`.

**Une divergence réelle, sinon rien.** Ce service ne « rafraîchit » pas un plan
chaque jour : sans écart constaté entre le plan et ce qui s'est réellement
passé, il renvoie explicitement *aucune replanification*. Une churn quotidienne
spéculative donnerait l'illusion d'un système attentif tout en rendant le plan
imprévisible.

## L'asymétrie, qui est le cœur de la tranche

Une preuve **limitante** peut réduire ou redistribuer du travail planifié.
Une preuve **favorable** ne peut rien ajouter.

Depuis `Sb_ADAPTIVE_REPLAN_SET_SEMANTICS_01` l'asymétrie porte sur les
**séries**, unité réelle de la dose : un créneau pouvant en contenir plusieurs,
un delta en créneaux ne disait plus combien de travail bougeait. Le mouvement de
créneaux reste exposé **séparément** — il décrit la *forme* de la semaine, les
séries en décrivent la *charge*.

Concrètement : une séance manquée redistribue, une récupération incomplète
reporte — mais une bonne readiness déclarée **ne crée aucune série, n'ajoute
aucune séance, n'augmente aucune charge et ne dépasse jamais le budget**. Cette
asymétrie n'est pas une prudence de façade : un signal optimiste est presque
toujours moins fiable qu'un signal limitant (un utilisateur qui se déclare frais
peut se tromper ; une séance non faite est un fait), et un système qui monte la
dose sur du déclaratif finirait par prescrire davantage à ceux qui se plaignent
le moins.

## Versionnement

Aucun plan publié n'est muté sur place. Une replanification produit une
**nouvelle version** portant son plan d'origine, la divergence constatée, le
delta déterministe et sa raison. L'historique reste lisible : on peut toujours
dire *pourquoi* la semaine a changé.

## Ce que ce service ne fait pas

Il ne lit **aucun second modèle** de fatigue ou de récupération : `TrainingState`
et `ZoneRecoveryEstimate` de P0.4 sont la seule source, consommés tels quels.
Il n'affirme aucun pourcentage de récupération, aucun délai exact, aucun risque
de blessure. Aucun LLM, aucun aléa.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from app.services.recovery_contract import Confidence, RecoveryBand, TrainingState
from app.services.weekly_planner import WeeklyPlan

REPLAN_VERSION = 1

#: Limite assumée, énoncée plutôt que contournée.
#:
#: Le brief demande que, si une preuve de séries **réellement effectuées**
#: existe, seules les séries planifiées **non effectuées** soient reconsidérées.
#: Cette preuve n'existe pas encore : rien ne persiste l'identité
#: **plan ↔ séance**, donc rien ne dit quelle séance enregistrée réalise quel
#: créneau planifié, ni combien de séries d'un exercice donné ont été faites.
#:
#: Conséquence tenue : une séance écourtée est une **divergence** (elle peut
#: déclencher une redistribution) mais **ne produit aucun delta de séries** —
#: réduire une zone reviendrait à deviner ce qui a été fait. Prétendre un
#: appariement exact serait la seule vraie faute ici.
#:
#: Levée prévue avec `Sb_WEEKLY_PLAN_MATERIALIZATION_01`, qui donne au plan une
#: existence persistée à laquelle une séance peut se rattacher.
PERFORMED_SET_IDENTITY_LIMITATION = (
    "no plan-to-session identity is persisted yet, so performed sets cannot be "
    "matched to planned sets; a shortened session diverges but never reduces a "
    "zone's sets by inference"
)


class DivergenceKind(StrEnum):
    """Les seuls déclencheurs admis. Tout le reste ne replanifie pas."""

    MISSED_SESSION = "missed_session"
    SHORTENED_SESSION = "shortened_session"
    INCOMPLETE_SESSION = "materially_incomplete_session"
    CONSTRAINT_CHANGE = "declared_constraint_change"
    LIMITING_RECOVERY = "recovery_incompatible_with_planned_work"


#: Bandes de récupération qui **limitent**. `UNKNOWN` n'en fait pas partie :
#: une absence de preuve n'est pas une preuve de contrainte.
LIMITING_BANDS = frozenset({RecoveryBand.LIKELY_FATIGUED})


@dataclass(frozen=True)
class Divergence:
    """Un écart **constaté**, jamais supposé."""

    kind: DivergenceKind
    subject: str | None = None
    detail: str = ""


@dataclass(frozen=True)
class PlanDelta:
    """Ce qui change, et pourquoi. Jamais une augmentation.

    **La dose est en SÉRIES** depuis `Sb_WEEKLY_PLAN_SET_ALLOCATION_01` : un
    créneau peut désormais en porter plusieurs, donc un delta exprimé en
    créneaux ne dit plus combien de travail bouge. « Un créneau retiré » peut
    valoir deux séries comme quatre.

    Le mouvement de créneaux **reste observable séparément** : il décrit la
    forme de la semaine (quels exercices sortent), là où les séries en décrivent
    la charge. Les deux sont utiles, et aucun ne se déduit de l'autre.
    """

    zone_code: str
    slots_before: int
    slots_after: int
    sets_before: int
    sets_after: int
    reason: str

    @property
    def is_reduction(self) -> bool:
        """Réduction sur les DEUX axes — ni la charge ni la forme n'augmentent."""
        return (
            self.sets_after <= self.sets_before
            and self.slots_after <= self.slots_before
        )

    @property
    def sets_removed(self) -> int:
        """Séries retirées de la semaine. Jamais négatif par construction."""
        return max(0, self.sets_before - self.sets_after)


@dataclass(frozen=True)
class ReplanResult:
    """Résultat déterministe : soit une nouvelle version, soit rien — dit."""

    replanned: bool
    replan_version: int = REPLAN_VERSION
    previous_fingerprint: str = ""
    new_fingerprint: str = ""
    divergences: tuple[Divergence, ...] = ()
    deltas: tuple[PlanDelta, ...] = ()
    unmet_budget_after: tuple[str, ...] = ()
    basis: tuple[str, ...] = field(default_factory=tuple)

    @property
    def sets_removed_total(self) -> int:
        """Séries retirées de la semaine, toutes zones confondues."""
        return sum(d.sets_removed for d in self.deltas)


def detect_divergences(
    plan: WeeklyPlan,
    completed_sessions: int,
    *,
    shortened_sessions: int = 0,
    constraint_changed: bool = False,
    training_state: TrainingState | None = None,
) -> tuple[Divergence, ...]:
    """Les écarts réels entre le plan et ce qui s'est passé.

    `completed_sessions` est un **fait compté**, pas une inférence : rapprocher
    une séance enregistrée d'un créneau planifié exigerait une identité
    plan↔séance que rien ne persiste encore, et la deviner produirait des
    divergences fantômes.
    """
    found: list[Divergence] = []

    planned = len(plan.sessions)
    if planned and completed_sessions < planned:
        missing = planned - completed_sessions
        found.append(Divergence(
            kind=DivergenceKind.MISSED_SESSION,
            detail=f"{missing} séance(s) planifiée(s) non réalisée(s) sur {planned}",
        ))

    if shortened_sessions > 0:
        found.append(Divergence(
            kind=DivergenceKind.SHORTENED_SESSION,
            detail=f"{shortened_sessions} séance(s) écourtée(s) — "
                   "seul le travail non effectué est reconsidéré",
        ))

    if constraint_changed:
        found.append(Divergence(
            kind=DivergenceKind.CONSTRAINT_CHANGE,
            detail="cadence ou matériel déclaré modifié depuis le plan",
        ))

    found.extend(_limiting_recovery(training_state))
    return tuple(found)


def _limiting_recovery(training_state: TrainingState | None) -> list[Divergence]:
    """Zones dont la récupération estimée contredit le travail planifié.

    Une confiance nulle ne contraint **rien** : sans preuve, pas de contrainte
    fabriquée. C'est la règle P0.4 appliquée telle quelle — et c'est la seule
    garde qui distingue « estimée chargée » de « on ne sait pas ».
    """
    if training_state is None:
        return []
    return [
        Divergence(
            kind=DivergenceKind.LIMITING_RECOVERY,
            subject=estimate.zone_code,
            detail="zone estimée encore chargée par l'entraînement récent",
        )
        for estimate in training_state.zone_recovery
        if estimate.confidence is not Confidence.NONE
        and estimate.band in LIMITING_BANDS
    ]


def replan(
    plan: WeeklyPlan,
    completed_sessions: int,
    *,
    shortened_sessions: int = 0,
    constraint_changed: bool = False,
    training_state: TrainingState | None = None,
) -> ReplanResult:
    """Replanifie **si et seulement si** une divergence réelle existe.

    Déterministe : le même état produit le même résultat, deltas compris.
    """
    divergences = detect_divergences(
        plan,
        completed_sessions,
        shortened_sessions=shortened_sessions,
        constraint_changed=constraint_changed,
        training_state=training_state,
    )

    if not divergences:
        return ReplanResult(
            replanned=False,
            previous_fingerprint=plan.fingerprint,
            new_fingerprint=plan.fingerprint,
            basis=("aucune divergence constatée — le plan reste valable",),
        )

    limiting_zones = {
        d.subject for d in divergences
        if d.kind is DivergenceKind.LIMITING_RECOVERY and d.subject
    }

    deltas: list[PlanDelta] = []
    for coverage in plan.zone_coverage:
        if coverage.zone_code not in limiting_zones:
            continue
        # Report, pas suppression : le travail sort de la semaine courante, il
        # n'est pas déclaré inutile.
        deltas.append(PlanDelta(
            zone_code=coverage.zone_code,
            slots_before=coverage.planned_slots,
            slots_after=0,
            sets_before=coverage.planned_sets,
            sets_after=0,
            reason="récupération estimée limitante — travail reporté, non supprimé",
        ))

    # Le budget non couvert AVANT reste non couvert : une replanification ne
    # comble pas un manque structurel, elle ne fait que déplacer du travail
    # réalisable.
    unmet = [c.zone_code for c in plan.unmet_budget]
    unmet.extend(d.zone_code for d in deltas if d.zone_code not in unmet)

    basis = [
        f"{len(divergences)} divergence(s) constatée(s)",
        "aucune preuve favorable n'ajoute de travail — l'adaptation ne peut que "
        "réduire ou redistribuer",
    ]
    if deltas:
        basis.append(
            f"{sum(d.sets_removed for d in deltas)} série(s) retirée(s) de la "
            "semaine et reportées — la dose se compte en séries, pas en créneaux"
        )
    if any(d.kind is DivergenceKind.SHORTENED_SESSION for d in divergences):
        basis.append(
            "séance écourtée : seul le travail non effectué serait à "
            "reconsidérer, mais aucune identité plan↔séance n'est persistée — "
            "aucune série n'est retirée par déduction"
        )
    if not deltas:
        basis.append(
            "divergence sans zone limitante identifiée — le travail restant est "
            "redistribué sans réduction de budget"
        )

    return ReplanResult(
        replanned=True,
        previous_fingerprint=plan.fingerprint,
        new_fingerprint=f"{plan.fingerprint}+r{len(divergences)}",
        divergences=divergences,
        deltas=tuple(deltas),
        unmet_budget_after=tuple(sorted(unmet)),
        basis=tuple(basis),
    )


__all__ = [
    "PERFORMED_SET_IDENTITY_LIMITATION",
    "LIMITING_BANDS",
    "REPLAN_VERSION",
    "Divergence",
    "DivergenceKind",
    "PlanDelta",
    "ReplanResult",
    "detect_divergences",
    "replan",
]
