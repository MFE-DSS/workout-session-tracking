"""Réalisation en SÉRIES d'un plan hebdomadaire (Sb_WEEKLY_PLAN_SET_ALLOCATION_01).

Tranche 2/4 du train `AUREN_WEEKLY_PLAN_PRODUCTIZATION_01`.

## Le décalage d'unité que cette tranche ferme

`WeeklyVolumeBudget` parle en **séries par semaine**. `WeeklyPlan` ne parlait
qu'en **créneaux par semaine**. Comparer les deux revenait à confondre « un
exercice de pectoraux est programmé » et « le volume pectoraux est couvert » —
un créneau unique ne peut pas porter seize séries.

**La satisfaction du budget s'évalue donc sur `planned_sets`, jamais sur un
nombre d'exercices.**

## Bornes — mesurées dans le dépôt, pas choisies

`reference_split.json` prescrit entre **2 et 4 séries par exercice** (modale
**3** : 89 entrées sur 106), pour des séances de 7–8 exercices et 20–24 séries.
Ces trois nombres ne sont pas une opinion sur l'entraînement : ce sont les
bornes que le **catalogue déjà validé** respecte, et les emprunter évite
d'inventer une politique de dosage que rien n'appuierait.

## Ce que cette tranche NE fait pas

**Elle ne fabrique aucun créneau.** Quand le budget d'une zone dépasse ce que
ses créneaux existants peuvent porter, le manque sort en `UNMET_VOLUME` — il
n'est pas comblé en dupliquant un exercice ni en synthétisant des intentions.
Multiplier les créneaux est une **décision produit** (elle change la forme des
séances), pas un détail d'implémentation : elle est remontée, chiffrée, non
prise ici.

**Elle ne persiste rien** et n'introduit **aucune comptabilité fractionnaire** :
l'unité reste la série entière du dépôt.

## Sources de répétitions — hiérarchie, et repli toujours visible

1. `reference_split.json`, **par exercice** — la prescription canonique.
2. La prescription **par intention** de `morpho_program_draft_mapper`, dont
   seule la **plage de répétitions** est reprise : son nombre de séries
   appartenait à un autre modèle, et c'est désormais le budget qui le décide.
3. Un **défaut produit nommé**, et seulement si personne d'autre ne parle.

Huit exercices du pool portent des plages **contradictoires** selon le template
du catalogue. Une source qui se contredit n'est pas une source : on descend d'un
niveau et `basis` le dit, plutôt que de trancher en silence par ordre de lecture.
"""
from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass, field
from functools import lru_cache

from app.config import BASE_DIR
from app.services.morpho_program_draft_mapper import (
    _DEFAULT_PRESCRIPTION,
    _INTENT_PRESCRIPTION,
)

ALLOCATION_POLICY_VERSION = "set-allocation-v1"

#: Bornes observées dans `reference_split.json` — jamais une thèse de dosage.
SETS_PER_SLOT_MIN = 2
SETS_PER_SLOT_MAX = 4

#: Origine d'une plage de répétitions, nommée pour être lisible sans deviner.
REP_SOURCE_CATALOG = "reference_split_exercise"
REP_SOURCE_INTENT = "intent_prescription"
REP_SOURCE_PRODUCT_DEFAULT = "product_default"

#: Défaut produit **explicite**, utilisé seulement si ni le catalogue ni
#: l'intention ne prescrivent quoi que ce soit. Repris du défaut déjà en place
#: dans le mapper de brouillon pour ne pas introduire un second chiffre.
PRODUCT_DEFAULT_REPS = (_DEFAULT_PRESCRIPTION[1], _DEFAULT_PRESCRIPTION[2])

#: Manque de volume : les créneaux existants ne peuvent pas porter la borne
#: basse de la bande. Distinct d'une absence de candidat — ici l'exercice est
#: là, c'est la capacité en séries qui manque.
UNMET_VOLUME = "planning_low_sets_not_reachable_with_available_slots"

_REFERENCE_SPLIT_PATH = BASE_DIR / "data" / "reference_split.json"


@lru_cache(maxsize=1)
def _catalog_rep_ranges() -> dict[str, tuple[int, int]]:
    """Plage de répétitions canonique par exercice — **uniquement si elle est unique**.

    Un exercice que deux templates prescrivent différemment est **absent** de
    cette table : le catalogue ne tranche pas, donc cette fonction ne tranche
    pas non plus. L'appelant descend d'un niveau et le consigne.
    """
    payload = json.loads(_REFERENCE_SPLIT_PATH.read_text(encoding="utf-8"))
    seen: dict[str, set[tuple[int, int]]] = {}
    for template in payload.get("templates", []):
        for exercise in template.get("exercises", []):
            targets = exercise.get("rep_targets") or []
            if not targets:
                continue
            span = (targets[0]["min_reps"], targets[0]["max_reps"])
            seen.setdefault(exercise["name"], set()).add(span)
    return {name: spans.pop() for name, spans in seen.items() if len(spans) == 1}


def resolve_rep_target(
    exercise_name: str | None,
    intent_id: str,
) -> tuple[int, int, str]:
    """`(min_reps, max_reps, source)` selon la hiérarchie documentée en tête.

    Le niveau 2 ne reprend **que** la plage de répétitions de la prescription
    par intention : son nombre de séries venait d'un modèle où le budget
    n'existait pas, et le réutiliser réintroduirait une seconde vérité de
    volume.
    """
    if exercise_name:
        catalog = _catalog_rep_ranges().get(exercise_name)
        if catalog is not None:
            return (*catalog, REP_SOURCE_CATALOG)
    intent = _INTENT_PRESCRIPTION.get(intent_id)
    if intent is not None:
        return (intent[1], intent[2], REP_SOURCE_INTENT)
    return (*PRODUCT_DEFAULT_REPS, REP_SOURCE_PRODUCT_DEFAULT)


@dataclass(frozen=True)
class ExercisePrescription:
    """Un exercice prescrit — l'unité que la matérialisation pourra exécuter."""

    slot_id: str
    exercise_name: str
    zone_code: str
    intent_id: str
    planned_sets: int
    min_reps: int
    max_reps: int
    rep_target_source: str
    rationale: str
    budget_source: str
    policy_version: str = ALLOCATION_POLICY_VERSION

    @property
    def set_scheme(self) -> str:
        """Format déjà utilisé par le catalogue et le brouillon Custom Program."""
        return f"{self.planned_sets}x {self.min_reps}-{self.max_reps}"


@dataclass(frozen=True)
class ZoneSetAllocation:
    """Ce qu'une zone reçoit en séries, face à sa bande de planification."""

    zone_code: str
    planned_sets: int
    planning_low_sets: int
    baseline_sets: int
    planning_high_sets: int
    target_sets: int
    slot_capacity_sets: int
    priority_rank: int | None = None
    unmet_reason: str | None = None
    basis: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_within_band(self) -> bool:
        return self.planning_low_sets <= self.planned_sets <= self.planning_high_sets


def target_sets_for(zone) -> int:
    """Point visé dans la bande. Priorité ⇒ côté haut, **jamais au-delà**.

    Une priorité déclarée oriente le choix à l'intérieur de la bande — c'est
    exactement ce que `Sb_WEEKLY_VOLUME_BUDGET_01` avait laissé au planificateur
    en refusant de le décider trop tôt.
    """
    if zone.priority_rank is not None:
        return zone.planning_high_sets
    return zone.baseline_sets


def distribute_sets(total: int, slot_count: int) -> tuple[int, ...]:
    """Répartit `total` séries sur `slot_count` créneaux, chacun borné à `[MIN, MAX]`.

    Déterministe et sans reste caché : les séries excédentaires de la division
    vont aux **premiers** créneaux, dans l'ordre déjà fixé par le planificateur.
    Le total rendu peut être inférieur à `total` — c'est le cas où la capacité
    manque, et l'appelant doit le nommer plutôt que l'absorber.
    """
    if slot_count <= 0 or total <= 0:
        return ()
    capped = min(total, slot_count * SETS_PER_SLOT_MAX)
    base, remainder = divmod(capped, slot_count)
    out = [base + (1 if i < remainder else 0) for i in range(slot_count)]
    # Un créneau sous le plancher du catalogue ne serait pas une prescription
    # crédible : on le retire plutôt que de prescrire une série isolée.
    return tuple(n for n in out if n >= SETS_PER_SLOT_MIN)


def allocate_zone(zone, slots: Sequence) -> tuple[ZoneSetAllocation, tuple[ExercisePrescription, ...]]:
    """Alloue les séries d'UNE zone sur ses créneaux remplis.

    La cadence n'est **pas** un paramètre : le budget est hebdomadaire, donc le
    dosage l'est aussi. Un test structurel vérifie que cette signature ne la
    reçoit pas — c'est le seul moyen sûr d'empêcher qu'elle s'y glisse, la
    capacité plafonnant souvent avant qu'une fuite ne devienne visible.
    """
    filled = [s for s in slots if s.exercise_name]
    target = target_sets_for(zone)
    capacity = len(filled) * SETS_PER_SLOT_MAX
    per_slot = distribute_sets(target, len(filled))

    prescriptions: list[ExercisePrescription] = []
    for slot, sets in zip(filled, per_slot, strict=False):
        min_reps, max_reps, source = resolve_rep_target(slot.exercise_name, slot.intent_id)
        prescriptions.append(ExercisePrescription(
            slot_id=slot.slot_id,
            exercise_name=slot.exercise_name,
            zone_code=zone.zone_code,
            intent_id=slot.intent_id,
            planned_sets=sets,
            min_reps=min_reps,
            max_reps=max_reps,
            rep_target_source=source,
            rationale=slot.rationale,
            budget_source=zone.policy_version,
        ))

    planned = sum(p.planned_sets for p in prescriptions)
    basis = [
        f"cible {target} séries — "
        + ("côté haut de la bande (priorité déclarée)" if zone.priority_rank
           else "base de la bande"),
        f"capacité {capacity} séries "
        f"({len(filled)} créneau(x) × {SETS_PER_SLOT_MAX} séries max, "
        "borne observée dans le catalogue)",
    ]
    fallbacks = {p.rep_target_source for p in prescriptions} - {REP_SOURCE_CATALOG}
    for source in sorted(fallbacks):
        basis.append(
            f"répétitions issues du repli « {source} » — le catalogue ne "
            "prescrit rien d'unique pour au moins un exercice de cette zone"
        )

    unmet = None
    if planned < zone.planning_low_sets:
        unmet = UNMET_VOLUME
        basis.append(
            f"{planned} série(s) planifiée(s) pour une borne basse à "
            f"{zone.planning_low_sets} — manque de {zone.planning_low_sets - planned}, "
            "non comblé : aucun exercice n'est dupliqué pour atteindre un chiffre"
        )

    return ZoneSetAllocation(
        zone_code=zone.zone_code,
        planned_sets=planned,
        planning_low_sets=zone.planning_low_sets,
        baseline_sets=zone.baseline_sets,
        planning_high_sets=zone.planning_high_sets,
        target_sets=target,
        slot_capacity_sets=capacity,
        priority_rank=zone.priority_rank,
        unmet_reason=unmet,
        basis=tuple(basis),
    ), tuple(prescriptions)


__all__ = [
    "ALLOCATION_POLICY_VERSION",
    "PRODUCT_DEFAULT_REPS",
    "REP_SOURCE_CATALOG",
    "REP_SOURCE_INTENT",
    "REP_SOURCE_PRODUCT_DEFAULT",
    "SETS_PER_SLOT_MAX",
    "SETS_PER_SLOT_MIN",
    "UNMET_VOLUME",
    "ExercisePrescription",
    "ZoneSetAllocation",
    "allocate_zone",
    "distribute_sets",
    "resolve_rep_target",
    "target_sets_for",
]
