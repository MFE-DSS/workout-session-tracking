"""Planificateur hebdomadaire déterministe (Sb_WEEKLY_PLANNER_01).

Tranche 2/3 du train `AUREN_CORE_ORCHESTRATION_01`.

**Moteur de PROPOSITION.** Ce n'est pas `recommendation.py` : il ne choisit pas
la séance du jour, il répartit un budget sur une semaine déclarée. Les deux
coexistent et ne se lisent pas l'un l'autre — un test le vérifie.

**Rien n'est reconstruit.** La sélection d'exercice appartient au générateur
fermé `morpho_program_generator.generate_program`, qui possède déjà le
classement, les départages déterministes, le filtre d'équipement et la
distinction entre *manque de couverture* et *manque de disponibilité*. Le
planificateur lui fournit des intentions et interprète ses lacunes ; il ne
range aucun exercice lui-même.

**Aucune correspondance nouvelle.** Les zones à servir viennent du budget
(taxonomie `BodyZone` canonique). Les clés de priorité passées au générateur
sont **dérivées** en inversant les tables existantes
(`PRIORITY_TO_INTENTS` × `primary_zone`), jamais écrites à la main : si le
registre d'intentions bouge, la dérivation suit.

## Couverture des zones — état depuis `Sb_SLOT_INTENT_COVERAGE_01`

Le registre `SlotIntent` couvre désormais **11 zones sur 11** en primaire, et
les six axes déclarables sont tous atteignables. La limite documentée ici
auparavant (`lats` et `core` sans intention, `biceps`/`triceps` en secondaire
seulement) est **fermée**.

Il reste **une** lacune, et elle est de données, pas de registre : `core` a une
intention (`trunk_core_direct`) mais **aucun candidat programmable** — les huit
exercices de tronc du référentiel sont absents de `exercise_properties.json` et
marqués `coverage_status: gap` dans l'EKB, sans `movement_pattern` ni
`equipment_family`. Elle ressort en `UNMET_NO_CANDIDATE`, pas en
`UNMET_NO_INTENT` : la distinction dit à quel mur on est.

**Un axe partiellement servi n'est pas servi.** `arms` n'est satisfait que si
`biceps` **et** `triceps` le sont — ce qui n'est pas acquis sous restriction de
matériel, les cinq candidats triceps du référentiel étant tous à la poulie.

Un utilisateur peut donc encore **déclarer une priorité que le planificateur ne
sait pas servir**. La réponse correcte est de le **dire**, jamais d'inventer un
exercice : chaque zone non servie sort dans `unmet_budget` avec sa raison
nommée, et chaque axe déclaré incomplet sort dans `unmet_constraints` en
nommant les zones qui manquent.

## Ce que le planificateur ne fait pas

Il ne fabrique aucun exercice · ne dépasse aucune borne du budget · n'exige
aucun échec musculaire · ne traite pas la fréquence comme une qualité · ne
modifie pas la recommandation du jour · ne mute aucun programme publié.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field, replace

from app.services.morpho_program_generator import GAP_AVAILABILITY, generate_program
from app.services.muscle_mapping import RADAR_AXES, ZONE_LABELS
from app.services.slot_intent import _INTENT_SPECS, PRIORITY_TO_INTENTS
from app.services.training_preferences import TrainingPreferencesData
from app.services.weekly_set_allocation import ExercisePrescription, allocate_zone
from app.services.weekly_volume_budget import (
    WeeklyVolumeBudget,
    build_weekly_volume_budget,
)

PLANNER_VERSION = 1

#: Raisons de non-couverture, nommées pour qu'un consommateur puisse les
#: distinguer sans analyser du texte.
UNMET_NO_INTENT = "no_slot_intent_covers_this_zone"
UNMET_NO_CANDIDATE = "no_candidate_exercise_for_the_intent"
UNMET_EQUIPMENT = "no_candidate_within_declared_equipment"
UNMET_NO_CADENCE = "no_declared_cadence_to_distribute_into"

#: Raisons de **SERVABILITÉ** : la zone n'a pas d'exercice programmable du tout.
#:
#: `UNMET_VOLUME` en est délibérément absent. Un manque de dose n'est pas un
#: manque d'exercice : dire à l'utilisateur qu'« aucun exercice ne peut servir
#: ses biceps » alors qu'un curl est bien prescrit serait faux. Le déficit de
#: séries se lit zone par zone dans `unmet_budget`, là où il est exact — et
#: comme il touche aujourd'hui presque toutes les zones, le remonter en
#: contrainte d'axe noierait le signal réel sous du bruit.
_SERVABILITY_REASONS = frozenset(
    {UNMET_NO_INTENT, UNMET_NO_CANDIDATE, UNMET_EQUIPMENT}
)


def zones_servable_as_primary() -> frozenset[str]:
    """Zones qu'une intention peut viser **en primaire**. Dérivé, jamais écrit."""
    return frozenset(spec["primary_zone"] for spec in _INTENT_SPECS.values())


def priority_keys_for_zones(zone_codes: frozenset[str]) -> tuple[str, ...]:
    """Clés de priorité dont **au moins une** intention vise l'une de ces zones.

    Inversion des tables existantes plutôt qu'une correspondance nouvelle : la
    vérité reste `PRIORITY_TO_INTENTS` et `_INTENT_SPECS`. Ordre alphabétique
    pour que la sortie du générateur soit reproductible.
    """
    keys: set[str] = set()
    for priority_key, intent_ids in PRIORITY_TO_INTENTS.items():
        for intent_id in intent_ids:
            spec = _INTENT_SPECS.get(intent_id)
            if spec and spec["primary_zone"] in zone_codes:
                keys.add(priority_key)
                break
    return tuple(sorted(keys))


@dataclass(frozen=True)
class PlannedSlot:
    """Un créneau proposé — l'exercice vient du générateur fermé, ou manque."""

    slot_id: str
    intent_id: str
    zone_code: str
    zone_label: str
    exercise_name: str | None
    rationale: str
    warning: str | None = None
    #: Raison nommée d'un créneau vide (`morpho_program_generator.GAP_*`).
    gap_kind: str | None = None
    #: Dose réalisée — 0 tant qu'aucune série n'est allouée au créneau.
    planned_sets: int = 0
    min_reps: int | None = None
    max_reps: int | None = None
    rep_target_source: str | None = None

    @property
    def is_filled(self) -> bool:
        """Un créneau ne compte que s'il porte un exercice réel."""
        return self.exercise_name is not None

    @property
    def is_prescribed(self) -> bool:
        """Un créneau n'est exécutable que s'il porte aussi une dose."""
        return self.is_filled and self.planned_sets > 0


@dataclass(frozen=True)
class PlannedSession:
    """Une séance proposée. L'index est 1-based, comme le compte l'utilisateur."""

    index: int
    slots: tuple[PlannedSlot, ...] = ()


@dataclass(frozen=True)
class ZoneCoverage:
    """Ce que le plan couvre pour une zone, face à sa bande de planification."""

    zone_code: str
    zone_label: str
    planned_slots: int
    planning_low_sets: int
    baseline_sets: int
    planning_high_sets: int
    priority_rank: int | None = None
    unmet_reason: str | None = None
    #: **La couverture du budget se juge ici**, pas sur `planned_slots` : un
    #: créneau unique ne peut pas porter seize séries.
    planned_sets: int = 0
    target_sets: int = 0
    slot_capacity_sets: int = 0
    allocation_basis: tuple[str, ...] = ()

    @property
    def is_within_band(self) -> bool:
        return self.planning_low_sets <= self.planned_sets <= self.planning_high_sets


@dataclass(frozen=True)
class WeeklyPlan:
    """Proposition hebdomadaire déterministe. **Jamais persistée par ce service.**"""

    planner_version: int = PLANNER_VERSION
    requested_sessions: int | None = None
    sessions: tuple[PlannedSession, ...] = ()
    zone_coverage: tuple[ZoneCoverage, ...] = ()
    unmet_budget: tuple[ZoneCoverage, ...] = ()
    unmet_constraints: tuple[str, ...] = ()
    equipment_declared: tuple[str, ...] | None = None
    #: Les exercices prescrits, dose comprise — l'unité qu'une matérialisation
    #: pourra exécuter. Ordonnées par zone puis par créneau, donc stables.
    prescriptions: tuple[ExercisePrescription, ...] = ()
    basis: tuple[str, ...] = field(default_factory=tuple)
    fingerprint: str = ""

    @property
    def is_feasible(self) -> bool:
        """Aucun trou de budget **et** aucune contrainte non satisfaite."""
        return not self.unmet_budget and not self.unmet_constraints

    @property
    def planned_sets_total(self) -> int:
        """Séries hebdomadaires réellement prescrites, toutes zones confondues."""
        return sum(p.planned_sets for p in self.prescriptions)


def _fingerprint(sessions, coverage, unmet) -> str:
    """Empreinte déterministe du contenu, pour comparer deux plans sans les lire.

    `sha256` d'une sérialisation triée : deux plans identiques donnent la même
    empreinte sur n'importe quelle machine, ce qu'un `hash()` Python ne
    garantirait pas d'une exécution à l'autre.
    """
    payload = json.dumps(
        {
            "sessions": [asdict(s) for s in sessions],
            "coverage": [asdict(c) for c in coverage],
            "unmet": [c.zone_code for c in unmet],
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _unservable_axes(
    preferences: TrainingPreferencesData,
    unmet_by_zone: dict[str, str],
) -> list[tuple[str, tuple[str, ...]]]:
    """Axes DÉCLARÉS dont **au moins une** zone n'est pas servie, et lesquelles.

    Cette information n'a de valeur que parce que l'utilisateur a explicitement
    demandé ces axes : signaler une lacune sur un axe qu'il n'a pas réclamé
    serait du bruit.

    **Un axe partiellement servi n'est pas servi.** `arms` couvre `biceps` et
    `triceps` : programmer les seuls biceps et déclarer l'axe satisfait ferait
    passer une moitié manquante pour une réussite. La règle vaut pour l'absence
    d'intention comme pour l'absence de candidat — un axe dont une zone n'a
    aucun exercice disponible n'est pas davantage servi qu'un axe sans
    intention.
    """
    out: list[tuple[str, tuple[str, ...]]] = []
    for axis_key in preferences.focus_priorities or ():
        axis = RADAR_AXES.get(axis_key)
        if axis is None:
            continue
        missing = tuple(
            z for z in axis["zones"]
            if unmet_by_zone.get(z) in _SERVABILITY_REASONS
        )
        if missing:
            out.append((axis_key, missing))
    return out


def _distribute(slots_by_zone: dict[str, list[PlannedSlot]], cadence: int | None):
    """Répartit les créneaux sur la cadence déclarée, en tourniquet.

    Sans cadence, aucune séance n'est fabriquée : inventer « 3 » transformerait
    une absence de déclaration en fait utilisateur, ce que la tranche des
    préférences interdit.
    """
    if not cadence:
        return ()
    buckets: list[list[PlannedSlot]] = [[] for _ in range(cadence)]
    flat = [s for zone in sorted(slots_by_zone) for s in slots_by_zone[zone]]
    for position, slot in enumerate(flat):
        buckets[position % cadence].append(slot)
    return tuple(
        PlannedSession(index=i + 1, slots=tuple(b)) for i, b in enumerate(buckets)
    )


def _unmet_reason(
    zone_code: str,
    planned: list[PlannedSlot],
    servable: frozenset[str],
    equipment_declared: tuple[str, ...] | None,
) -> str | None:
    """Pourquoi une zone n'est pas couverte — nommé, jamais deviné.

    **Un créneau vide ne couvre rien.** Le générateur émet un créneau pour toute
    intention retenue, y compris quand aucun exercice ne peut le remplir : ne
    compter que les créneaux *remplis* évite qu'une zone sans le moindre
    exercice ressorte comme couverte — la lacune se lirait alors comme une
    réussite. C'est ce que `core` met au jour depuis
    `Sb_SLOT_INTENT_COVERAGE_01` : une intention existe, aucun candidat n'a de
    propriétés programmables.

    La raison vient du `gap_kind` **nommé** par le générateur, jamais déduite de
    la simple présence d'une déclaration de matériel : une zone sans candidat du
    tout n'est pas une zone bloquée par le matériel, même sous restriction.
    """
    if zone_code not in servable:
        return UNMET_NO_INTENT
    if any(slot.is_filled for slot in planned):
        return None
    if any(slot.gap_kind == GAP_AVAILABILITY for slot in planned):
        return UNMET_EQUIPMENT
    if planned:
        return UNMET_NO_CANDIDATE
    return UNMET_EQUIPMENT if equipment_declared else UNMET_NO_CANDIDATE


def _allocate(budget, slots_by_zone):
    """Alloue les séries zone par zone, **avant** toute répartition en séances.

    L'ordre importe : allouer d'abord garantit qu'une cadence différente
    déplace des créneaux sans jamais changer le total hebdomadaire de séries.
    """
    allocations: dict[str, object] = {}
    prescribed: dict[str, dict[str, object]] = {}
    for zone in budget.zones:
        allocation, prescriptions = allocate_zone(
            zone, slots_by_zone.get(zone.zone_code, []))
        allocations[zone.zone_code] = allocation
        prescribed[zone.zone_code] = {p.slot_id: p for p in prescriptions}
    return allocations, prescribed


def _apply_prescriptions(slots_by_zone, prescribed):
    """Recopie la dose allouée sur les créneaux. Un créneau non doté reste à 0."""
    out: dict[str, list[PlannedSlot]] = {}
    for zone_code, slots in slots_by_zone.items():
        by_slot = prescribed.get(zone_code, {})
        out[zone_code] = [
            replace(
                slot,
                planned_sets=p.planned_sets,
                min_reps=p.min_reps,
                max_reps=p.max_reps,
                rep_target_source=p.rep_target_source,
            ) if (p := by_slot.get(slot.slot_id)) is not None else slot
            for slot in slots
        ]
    return out


def _coverage(budget, slots_by_zone, servable, equipment_declared, allocations):
    """Couverture par zone face à sa bande, et la liste des manques."""
    coverage: list[ZoneCoverage] = []
    unmet: list[ZoneCoverage] = []
    for zone in budget.zones:
        planned = slots_by_zone.get(zone.zone_code, [])
        allocation = allocations[zone.zone_code]
        # Un manque de candidat prime sur un manque de volume : dire « il
        # manque des séries » alors qu'aucun exercice n'existe désignerait le
        # mauvais mur.
        reason = _unmet_reason(
            zone.zone_code, planned, servable, equipment_declared
        ) or allocation.unmet_reason
        entry = ZoneCoverage(
            zone_code=zone.zone_code,
            zone_label=zone.zone_label,
            # Créneaux REMPLIS : un créneau sans exercice n'est pas une couverture.
            planned_slots=sum(1 for slot in planned if slot.is_filled),
            planning_low_sets=zone.planning_low_sets,
            baseline_sets=zone.baseline_sets,
            planning_high_sets=zone.planning_high_sets,
            priority_rank=zone.priority_rank,
            unmet_reason=reason,
            planned_sets=allocation.planned_sets,
            target_sets=allocation.target_sets,
            slot_capacity_sets=allocation.slot_capacity_sets,
            allocation_basis=allocation.basis,
        )
        coverage.append(entry)
        if reason is not None:
            unmet.append(entry)
    return tuple(coverage), tuple(unmet)


def _constraints(
    prefs: TrainingPreferencesData,
    cadence: int | None,
    unmet_by_zone: dict[str, str],
) -> tuple[str, ...]:
    """Contraintes non satisfaites, dites plutôt que contournées."""
    out: list[str] = []
    if not cadence:
        out.append(UNMET_NO_CADENCE)
    for axis_key, missing in _unservable_axes(prefs, unmet_by_zone):
        label = RADAR_AXES[axis_key]["label"]
        zones = ", ".join(ZONE_LABELS.get(z, z) for z in missing)
        cause = (
            "aucune intention de créneau ne les vise"
            if all(unmet_by_zone[z] == UNMET_NO_INTENT for z in missing)
            else "aucun exercice disponible ne peut les servir"
        )
        out.append(
            f"priorité déclarée « {label} » : {zones} — {cause}, et aucun "
            "exercice n'est inventé pour combler ce manque"
        )
    return tuple(out)


def _basis(budget, servable, prefs, generated) -> tuple[str, ...]:
    out = [
        f"budget {budget.policy_version} — bandes de planification",
        f"{len(servable)} zone(s) servables sur {len(budget.zones)} "
        "dans le registre d'intentions fermé",
    ]
    if prefs.available_equipment is not None:
        out.append(
            f"{len(prefs.available_equipment)} famille(s) de matériel déclarée(s)")
    else:
        out.append("matériel non déclaré — aucune contrainte appliquée")
    out.extend(generated.warnings)
    return tuple(out)


def _slots_by_zone(generated) -> dict[str, list[PlannedSlot]]:
    out: dict[str, list[PlannedSlot]] = {}
    for selection in generated.selections:
        out.setdefault(selection.primary_zone, []).append(PlannedSlot(
            slot_id=selection.slot_id,
            intent_id=selection.intent_id,
            zone_code=selection.primary_zone,
            zone_label=ZONE_LABELS.get(
                selection.primary_zone, selection.primary_zone),
            exercise_name=selection.preferred_exercise,
            rationale=selection.rationale,
            warning=selection.warning,
            gap_kind=selection.gap_kind,
        ))
    return out


def build_weekly_plan(
    preferences: TrainingPreferencesData | None = None,
    budget: WeeklyVolumeBudget | None = None,
    pool: dict[str, dict] | None = None,
) -> WeeklyPlan:
    """Plan hebdomadaire déterministe. Pur : aucune I/O, aucune horloge, aucun aléa."""
    prefs = preferences or TrainingPreferencesData()
    weekly_budget = budget or build_weekly_volume_budget(prefs)
    servable = zones_servable_as_primary()

    target_zones = frozenset(
        z.zone_code for z in weekly_budget.zones if z.zone_code in servable)
    generated = generate_program(
        priorities=[(key, rank) for rank, key in enumerate(
            priority_keys_for_zones(target_zones), start=1)],
        availability=prefs.available_equipment,
        pool=pool,
    )

    slots_by_zone = _slots_by_zone(generated)
    allocations, prescribed = _allocate(weekly_budget, slots_by_zone)
    slots_by_zone = _apply_prescriptions(slots_by_zone, prescribed)
    sessions = _distribute(slots_by_zone, prefs.sessions_per_week)
    coverage, unmet = _coverage(
        weekly_budget, slots_by_zone, servable, prefs.available_equipment,
        allocations)
    unmet_by_zone = {c.zone_code: c.unmet_reason for c in unmet if c.unmet_reason}
    prescriptions = tuple(
        p for zone_code in sorted(prescribed)
        for _, p in sorted(prescribed[zone_code].items())
    )

    return WeeklyPlan(
        requested_sessions=prefs.sessions_per_week,
        sessions=sessions,
        zone_coverage=coverage,
        unmet_budget=unmet,
        unmet_constraints=_constraints(
            prefs, prefs.sessions_per_week, unmet_by_zone),
        equipment_declared=prefs.available_equipment,
        prescriptions=prescriptions,
        basis=_basis(weekly_budget, servable, prefs, generated),
        fingerprint=_fingerprint(sessions, coverage, unmet),
    )


def build_weekly_plan_for_user(db, user_id: int, pool=None) -> WeeklyPlan:
    """Commodité base de données : lit les préférences, puis planifie. Lecture seule."""
    from app.services.training_preferences import get_training_preferences

    return build_weekly_plan(get_training_preferences(db, user_id), pool=pool)


__all__ = [
    "PLANNER_VERSION",
    "UNMET_EQUIPMENT",
    "UNMET_NO_CADENCE",
    "UNMET_NO_CANDIDATE",
    "UNMET_NO_INTENT",
    "PlannedSession",
    "PlannedSlot",
    "WeeklyPlan",
    "ZoneCoverage",
    "build_weekly_plan",
    "build_weekly_plan_for_user",
    "priority_keys_for_zones",
    "zones_servable_as_primary",
]
