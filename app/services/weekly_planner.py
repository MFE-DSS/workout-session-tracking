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

## La limite structurelle que ce sprint met au jour

Le registre `SlotIntent` est **fermé** et couvre **7 zones sur 11** en primaire.
`biceps` et `triceps` ne sont atteignables qu'en **secondaire** ; `lats` et
`core` ne sont atteignables **par aucune intention**.

Traduit en axes déclarables par l'utilisateur — ceux que
`Sb_TRAINING_PREFERENCES_01` lui propose — **deux des six ne sont pas
servables** :

| Axe déclarable | Zones | Servable |
|---|---|---|
| `back_width` (Dos largeur) | `lats` | **aucune intention** |
| `arms` (Bras) | `biceps`, `triceps` | **secondaire seulement** |

Un utilisateur peut donc **déclarer une priorité que le planificateur ne sait
pas programmer**. La réponse correcte est de le **dire**, pas d'inventer une
intention : fabriquer un slot pour `lats` reviendrait à créer une taxonomie
d'exercice que personne n'a validée. Chaque zone non servie sort donc dans
`unmet_budget` avec sa raison, et chaque axe déclaré non servable sort dans
`unmet_constraints`.

## Ce que le planificateur ne fait pas

Il ne fabrique aucun exercice · ne dépasse aucune borne du budget · n'exige
aucun échec musculaire · ne traite pas la fréquence comme une qualité · ne
modifie pas la recommandation du jour · ne mute aucun programme publié.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field

from app.services.morpho_program_generator import generate_program
from app.services.muscle_mapping import RADAR_AXES, ZONE_LABELS
from app.services.slot_intent import _INTENT_SPECS, PRIORITY_TO_INTENTS
from app.services.training_preferences import TrainingPreferencesData
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
    basis: tuple[str, ...] = field(default_factory=tuple)
    fingerprint: str = ""

    @property
    def is_feasible(self) -> bool:
        """Aucun trou de budget **et** aucune contrainte non satisfaite."""
        return not self.unmet_budget and not self.unmet_constraints


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


def _unservable_axes(preferences: TrainingPreferencesData) -> list[str]:
    """Axes DÉCLARÉS dont aucune zone n'est servable en primaire.

    Cette information n'a de valeur que parce que l'utilisateur a explicitement
    demandé ces axes : signaler une lacune sur un axe qu'il n'a pas réclamé
    serait du bruit.
    """
    servable = zones_servable_as_primary()
    out: list[str] = []
    for axis_key in preferences.focus_priorities or ():
        axis = RADAR_AXES.get(axis_key)
        if axis and not any(z in servable for z in axis["zones"]):
            out.append(axis_key)
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
    """Pourquoi une zone n'est pas couverte — nommé, jamais deviné."""
    if zone_code not in servable:
        return UNMET_NO_INTENT
    if planned:
        return None
    return UNMET_EQUIPMENT if equipment_declared else UNMET_NO_CANDIDATE


def _coverage(budget, slots_by_zone, servable, equipment_declared):
    """Couverture par zone face à sa bande, et la liste des manques."""
    coverage: list[ZoneCoverage] = []
    unmet: list[ZoneCoverage] = []
    for zone in budget.zones:
        planned = slots_by_zone.get(zone.zone_code, [])
        reason = _unmet_reason(
            zone.zone_code, planned, servable, equipment_declared)
        entry = ZoneCoverage(
            zone_code=zone.zone_code,
            zone_label=zone.zone_label,
            planned_slots=len(planned),
            planning_low_sets=zone.planning_low_sets,
            baseline_sets=zone.baseline_sets,
            planning_high_sets=zone.planning_high_sets,
            priority_rank=zone.priority_rank,
            unmet_reason=reason,
        )
        coverage.append(entry)
        if reason is not None:
            unmet.append(entry)
    return tuple(coverage), tuple(unmet)


def _constraints(prefs: TrainingPreferencesData, cadence: int | None) -> tuple[str, ...]:
    """Contraintes non satisfaites, dites plutôt que contournées."""
    out: list[str] = []
    if not cadence:
        out.append(UNMET_NO_CADENCE)
    for axis_key in _unservable_axes(prefs):
        label = RADAR_AXES[axis_key]["label"]
        out.append(
            f"priorité déclarée « {label} » : aucune intention de créneau ne vise "
            "ses zones — aucun exercice n'est inventé pour combler ce manque"
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
    sessions = _distribute(slots_by_zone, prefs.sessions_per_week)
    coverage, unmet = _coverage(
        weekly_budget, slots_by_zone, servable, prefs.available_equipment)

    return WeeklyPlan(
        requested_sessions=prefs.sessions_per_week,
        sessions=sessions,
        zone_coverage=coverage,
        unmet_budget=unmet,
        unmet_constraints=_constraints(prefs, prefs.sessions_per_week),
        equipment_declared=prefs.available_equipment,
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
