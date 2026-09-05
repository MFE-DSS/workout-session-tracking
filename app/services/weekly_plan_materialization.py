"""Matérialisation d'un plan hebdomadaire en brouillon Custom Program
(Sb_WEEKLY_PLAN_MATERIALIZATION_01).

Tranche 4/4 du train `AUREN_WEEKLY_PLAN_PRODUCTIZATION_01`. Le pont qui manquait :
jusqu'ici `WeeklyPlan` était une **proposition** que rien ne pouvait exécuter.

## Aucun cycle de vie parallèle

Le brouillon est créé par les services **existants** — `create_draft`,
`replace_draft_tree`, `validate_draft`, `compute_quality_preview` — et rien
d'autre. Pas de nouvelle machine à états, pas de table, pas de chemin de
publication concurrent. Publier reste `user_program_publish`, sur action
explicite de l'utilisateur, et **une version publiée n'est jamais mutée** :
une replanification produira un nouveau brouillon, comme n'importe quelle
autre modification.

## Ce qui est repris du mapper morpho, et ce qui ne l'est pas

**Repris** : la forme de l'arbre de brouillon, l'enrichissement EKB, la
convention `source_reason`, le refus de fabriquer, les limites Custom Program.

**PAS repris** : sa table `_INTENT_PRESCRIPTION` comme source de volume. Le
nombre de séries vient désormais du **plan**, qui le tient du budget. Réutiliser
la table réintroduirait la seconde vérité de volume que la tranche 2 s'est
employée à supprimer.

## Les créneaux vides ne deviennent pas des exercices

Un créneau sans exercice (`core` aujourd'hui) n'a rien d'exécutable : il est
**écarté de l'arbre**, et une séance qui n'en contiendrait que de tels créneaux
est écartée aussi — `validate_draft` refuse à juste titre une séance sans
exercice. Le manque ne disparaît pas pour autant : il reste dans le plan et
ressort dans le statut de matérialisation.

## Le statut dit la vérité, y compris quand elle est partielle

Un plan dont **une priorité déclarée par l'utilisateur** n'est pas servable du
tout ne peut pas être présenté comme prêt : il sort en `CONSTRAINT_UNMET`. Un
plan qui laisse un manque de volume structurel sort en `PARTIAL`. Seul un plan
sans lacune sort en `READY`. Le brouillon reste **créable** dans les trois cas —
c'est l'utilisateur qui décide — mais il n'est jamais annoncé comme complet
quand il ne l'est pas.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from app.services.user_program_exercise_catalog import enrich
from app.services.weekly_planner import WeeklyPlan

MATERIALIZATION_VERSION = 1

#: Traçabilité, alignée sur `generated:reference_split:{slug}` et
#: `generated:morpho:{intent}` déjà en place.
SOURCE_REASON_PREFIX = "generated:weekly_plan"

#: Titre par défaut du programme produit. Nommé, jamais deviné depuis le contenu.
DEFAULT_PROGRAM_TITLE = "Programme hebdomadaire proposé"


class MaterializationStatus(StrEnum):
    """Ce que vaut le plan **avant** d'en faire un brouillon."""

    READY = "ready"
    #: Manque de volume structurel : exécutable, mais incomplet — et le dire.
    PARTIAL = "partial"
    #: Une priorité DÉCLARÉE n'est pas servable du tout : ne pas présenter
    #: le plan comme prêt.
    CONSTRAINT_UNMET = "constraint_unmet"
    #: Rien d'exécutable : pas de cadence, ou aucun exercice prescrit.
    BLOCKED = "blocked"


#: Raisons de blocage, nommées pour qu'un consommateur n'analyse pas du texte.
BLOCKED_NO_CADENCE = "no_declared_cadence"
BLOCKED_NO_SESSION = "no_session_with_a_prescribed_exercise"
BLOCKED_NO_PRESCRIPTION = "no_exercise_carries_a_set_prescription"


@dataclass(frozen=True)
class SessionSummary:
    """Ce qu'UNE séance proposée travaille, et à quelle dose.

    `Sb_UI_PLAN_01` — CE RÉSUMÉ EXISTE PARCE QUE LA STRUCTURE ÉTAIT JETÉE.

    Le planificateur produit `WeeklyPlan.sessions` — quatre séances, chacune
    avec ses créneaux et ses prescriptions. `_prescribed_sessions()` les
    reconstitue en ne gardant que les créneaux exécutables. Puis
    `MaterializationReadiness` n'en gardait que le NOMBRE, et l'écran écrivait
    « 4 séances/semaine ».

    La structure était calculée, puis jetée trois fois avant d'atteindre
    l'utilisateur. L'écran n'était pas pauvre parce que la donnée l'était.
    """

    index: int
    #: Les zones travaillées, dédupliquées, DANS L'ORDRE DES CRÉNEAUX — cet
    #: ordre est celui du planificateur, il porte la structure de la séance.
    #: Trier alphabétiquement le détruirait.
    zone_labels: tuple[str, ...] = ()
    exercises: int = 0
    planned_sets: int = 0


@dataclass(frozen=True)
class MaterializationReadiness:
    """Verdict de matérialisation — jamais un simple booléen.

    Un booléen forcerait à choisir entre « prêt » et « refusé » là où la
    réponse honnête est souvent « exécutable, mais voici ce qui manque ».
    """

    status: MaterializationStatus
    blocked_reasons: tuple[str, ...] = ()
    unmet_zones: tuple[str, ...] = ()
    unserved_priorities: tuple[str, ...] = ()
    sessions: int = 0
    exercises: int = 0
    planned_sets: int = 0
    #: `Sb_UI_PLAN_01` — les séances elles-mêmes, pas seulement leur compte.
    #: Additif : `sessions` reste, ses consommateurs ne bougent pas.
    session_summaries: tuple[SessionSummary, ...] = ()
    basis: tuple[str, ...] = field(default_factory=tuple)

    @property
    def can_materialize(self) -> bool:
        """Un plan partiel reste matérialisable — c'est l'utilisateur qui tranche."""
        return self.status is not MaterializationStatus.BLOCKED


def _prescribed_sessions(plan: WeeklyPlan) -> list[tuple[int, list]]:
    """Séances ne gardant que les créneaux **exécutables**, vides écartées.

    `validate_draft` refuse une séance sans exercice : y laisser un créneau
    `core` sans exercice rendrait tout le brouillon invalidable, pour une
    lacune que le plan signale déjà par ailleurs.
    """
    out: list[tuple[int, list]] = []
    for session in plan.sessions:
        slots = [s for s in session.slots if s.is_prescribed]
        if slots:
            out.append((session.index, slots))
    return out


def assess_materialization(plan: WeeklyPlan) -> MaterializationReadiness:
    """Ce que vaut ce plan comme programme — dit avant d'écrire quoi que ce soit."""
    sessions = _prescribed_sessions(plan)
    exercises = sum(len(slots) for _, slots in sessions)
    planned_sets = sum(
        slot.planned_sets for _, slots in sessions for slot in slots)

    blocked: list[str] = []
    if not plan.requested_sessions:
        blocked.append(BLOCKED_NO_CADENCE)
    if not sessions:
        blocked.append(BLOCKED_NO_SESSION)
    elif not planned_sets:
        blocked.append(BLOCKED_NO_PRESCRIPTION)

    unmet_zones = tuple(z.zone_code for z in plan.unmet_budget)
    unserved = tuple(plan.unmet_constraints)

    if blocked:
        status = MaterializationStatus.BLOCKED
    elif unserved:
        # Une priorité déclarée non servable prime : c'est la promesse faite à
        # l'utilisateur qui n'est pas tenue, pas seulement un chiffre en deçà.
        status = MaterializationStatus.CONSTRAINT_UNMET
    elif unmet_zones:
        status = MaterializationStatus.PARTIAL
    else:
        status = MaterializationStatus.READY

    basis = [
        f"{len(sessions)} séance(s) exécutable(s), {exercises} exercice(s), "
        f"{planned_sets} série(s) prescrite(s)",
    ]
    if unmet_zones:
        basis.append(
            f"{len(unmet_zones)} zone(s) sous leur bande de planification — "
            "le programme reste exécutable, il n'est pas complet"
        )
    if unserved:
        basis.append(
            "une priorité déclarée n'est pas servable — le programme n'est "
            "pas présenté comme prêt"
        )
    empty = len(plan.sessions) - len(sessions)
    if empty:
        basis.append(
            f"{empty} séance(s) sans exercice exécutable écartée(s) du "
            "brouillon — la lacune reste visible dans le plan"
        )

    # `Sb_UI_PLAN_01` — on garde ce qu'on vient de calculer.
    # `sessions` porte déjà (index, créneaux exécutables) ; en tirer les zones
    # ne coûte rien et évite que l'écran ait à redemander le plan.
    resumes = tuple(
        SessionSummary(
            index=index,
            zone_labels=tuple(dict.fromkeys(
                slot.zone_label for slot in slots if slot.zone_label
            )),
            exercises=len(slots),
            planned_sets=sum(slot.planned_sets for slot in slots),
        )
        for index, slots in sessions
    )

    return MaterializationReadiness(
        status=status,
        blocked_reasons=tuple(blocked),
        session_summaries=resumes,
        unmet_zones=unmet_zones,
        unserved_priorities=unserved,
        sessions=len(sessions),
        exercises=exercises,
        planned_sets=planned_sets,
        basis=tuple(basis),
    )


def _exercise_payload(slot, position: int) -> dict:
    """Un créneau prescrit → une charge utile `replace_draft_tree`.

    La dose vient du **plan** : `planned_sets` répétitions de la plage retenue.
    L'enrichissement EKB est celui du picker manuel — correspondance de nom
    canonique **exacte**, `{}` sinon, aucun rapprochement approximatif.
    """
    return {
        **enrich(slot.exercise_name),
        "position": position,
        "exercise_name": slot.exercise_name,
        "set_scheme": f"{slot.planned_sets}x {slot.min_reps}-{slot.max_reps}",
        "notes": slot.rationale,
        "source_reason": f"{SOURCE_REASON_PREFIX}:{slot.intent_id}"[:255],
        "rep_targets": [
            {"min_reps": slot.min_reps, "max_reps": slot.max_reps}
            for _ in range(slot.planned_sets)
        ],
    }


def plan_to_draft_tree(plan: WeeklyPlan) -> list[dict]:
    """`WeeklyPlan` → arbre de séances pour `replace_draft_tree`. Pur.

    Les positions sont recalculées en 1..N après écarte­ment des créneaux vides :
    `replace_draft_tree` exige des positions contiguës, et conserver l'index
    d'origine y laisserait des trous.
    """
    tree: list[dict] = []
    for position, (index, slots) in enumerate(_prescribed_sessions(plan), start=1):
        zones = sorted({slot.zone_label for slot in slots})
        tree.append({
            "position": position,
            "name": f"Séance {index}",
            "kind": "strength",
            "focus": " · ".join(zones),
            "notes": None,
            "exercises": [
                _exercise_payload(slot, i)
                for i, slot in enumerate(slots, start=1)
            ],
        })
    return tree


def materialize_weekly_plan(db, user_id: int, plan: WeeklyPlan, *, title: str, slug_base: str):
    """Crée un brouillon Custom Program à partir du plan. **Rien de publié.**

    Renvoie `(programme, verdict)`. Le programme sort en statut `draft` par le
    cycle de vie existant — c'est ensuite à l'utilisateur de valider puis de
    publier, par les services déjà en place.

    Un plan **bloqué** lève : il n'y a rien d'exécutable à écrire. Un plan
    partiel, lui, est matérialisé — accompagné de son verdict, pour que
    l'appelant puisse le présenter tel qu'il est.

    Les erreurs de quota et de collision de slug remontent telles quelles
    depuis `create_draft` : ce service n'invente aucune politique de nommage.
    """
    from app.services.user_program_drafts import (
        UserProgramDraftError,
        create_draft,
        replace_draft_tree,
    )

    readiness = assess_materialization(plan)
    if not readiness.can_materialize:
        raise UserProgramDraftError(
            "Ce plan n'a rien d'exécutable à programmer pour l'instant — "
            + ", ".join(readiness.blocked_reasons)
        )

    program = create_draft(db, user_id, title, slug_base)
    replace_draft_tree(db, user_id, program.id, plan_to_draft_tree(plan))
    return program, readiness


__all__ = [
    "BLOCKED_NO_CADENCE",
    "BLOCKED_NO_PRESCRIPTION",
    "BLOCKED_NO_SESSION",
    "DEFAULT_PROGRAM_TITLE",
    "MATERIALIZATION_VERSION",
    "SOURCE_REASON_PREFIX",
    "MaterializationReadiness",
    "MaterializationStatus",
    "assess_materialization",
    "materialize_weekly_plan",
    "plan_to_draft_tree",
]
