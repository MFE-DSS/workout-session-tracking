"""Sb_DECISION_ANALYTICS_RUNTIME_01 — collecteur aval de traces de décision.

Ce module **observe des sorties déjà calculées**. Il ne participe à aucun choix,
et c'est vérifiable plutôt que déclaratif : il n'appelle aucun moteur, il reçoit
leurs valeurs de retour.

Trois règles gouvernent tout ce qui suit.

**La pureté des moteurs est un actif, pas un détail.** `build_weekly_plan` ne
prend ni `db` ni `user_id`, et c'est ce qui rend l'isolation démontrable. Le
collecteur vit donc **en aval**, aux frontières qui touchent déjà la base
(`build_weekly_plan_for_user`, `materialize_weekly_plan`). Aucune signature pure
n'est contaminée.

**L'observabilité n'est pas une dépendance de disponibilité.** Si la persistance
d'une trace échoue, le plan reste le plan et le brouillon reste le brouillon :
`observe_*` avale l'erreur, la journalise, et rend `None`. Une décision produit
valide n'est jamais annulée parce que l'observation a raté.

**Une source n'est jamais reclassée pour arranger l'affichage.** Les sept
natures de `Sx_DECISION_ANALYTICS_01_SPEC` sont conservées dans des champs
distincts jusqu'en base. Une évidence réelle mais inclassable est marquée
`UNCLASSIFIED` — jamais rangée dans une classe qui lui irait à peu près.
"""
from __future__ import annotations

import hashlib
import json
import logging
import uuid
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

DECISION_ANALYTICS_VERSION = 1

logger = logging.getLogger(__name__)

# ── Types de décision (granularité tranchée par l'opérateur, OQ-4) ───────────

VOLUME_BAND = "VOLUME_BAND"                    # par zone, par génération
ZONE_ALLOCATION = "ZONE_ALLOCATION"            # par zone
SLOT_SELECTION = "SLOT_SELECTION"              # par occurrence planifiée
SET_PRESCRIPTION = "SET_PRESCRIPTION"          # par occurrence planifiée
CONTRIBUTION_CREDIT = "CONTRIBUTION_CREDIT"    # agrégé par zone, jamais par série
REPLAN_DELTA = "REPLAN_DELTA"                  # par changement significatif
MATERIALIZATION = "MATERIALIZATION"            # une par tentative
RECOVERY_ASSESSMENT = "RECOVERY_ASSESSMENT"    # seulement si consommée

# `MORPHOLOGY_DESCRIPTOR` existe dans la spec mais **n'est pas persisté en V1** :
# tant que la morphologie n'alimente aucune décision aval, une trace ne
# prouverait rien qu'un rendu de `/profile` n'établisse déjà.

# ── Taxonomie des sources — NORMATIVE, jamais fusionnée ──────────────────────

USER_DECLARED = "USER_DECLARED"
MEASURED_FACT = "MEASURED_FACT"
DERIVED_FACT = "DERIVED_FACT"
PRODUCT_POLICY = "PRODUCT_POLICY"
MORPHOLOGY_INFERENCE = "MORPHOLOGY_INFERENCE"
RECOVERY_ESTIMATE = "RECOVERY_ESTIMATE"
CATALOG_CONSTRAINT = "CATALOG_CONSTRAINT"
UNCLASSIFIED = "UNCLASSIFIED"

SOURCE_CLASSES = frozenset({
    USER_DECLARED, MEASURED_FACT, DERIVED_FACT, PRODUCT_POLICY,
    MORPHOLOGY_INFERENCE, RECOVERY_ESTIMATE, CATALOG_CONSTRAINT, UNCLASSIFIED,
})

# Noms des colonnes-familles, nommés une fois : S1192 se déclenche à trois
# répétitions et un seul MAJOR (poids 15) casse le gate new-code (seuil 14).
BUCKET_CONSTRAINT = "constraint_sources"
BUCKET_PREFERENCE = "preference_sources"
BUCKET_MORPHOLOGY = "morphology_sources"
BUCKET_RECOVERY = "recovery_sources"

# Quelle famille de colonnes reçoit quelle nature. `MEASURED_FACT` et
# `DERIVED_FACT` rejoignent les contraintes faute de colonne dédiée — mais leur
# `kind` reste intact dans la charge utile, donc la nature n'est jamais perdue.
_BUCKET = {
    USER_DECLARED: BUCKET_PREFERENCE,
    MORPHOLOGY_INFERENCE: BUCKET_MORPHOLOGY,
    RECOVERY_ESTIMATE: BUCKET_RECOVERY,
}

_EQUIPMENT_REF = "available_equipment"
_FINGERPRINT_ATTR = "fingerprint"

SOURCE_TAXONOMY_GUARD = (
    "Les sept natures de source restent distinctes jusqu'en base. Une evidence "
    "reelle mais inclassable est marquee UNCLASSIFIED ; elle n'est jamais rangee "
    "dans une classe approchante, et aucune n'est fondue dans un champ unique."
)


@dataclass(frozen=True)
class SourceRef:
    """Une évidence consommée par une décision, avec sa nature."""

    kind: str
    ref: str
    value: object | None = None

    def as_payload(self) -> dict:
        out: dict = {"kind": self.kind, "ref": self.ref}
        if self.value is not None:
            out["value"] = self.value
        return out


@dataclass(frozen=True)
class DraftTrace:
    """Une trace avant persistance. Purement en mémoire, sans identité."""

    decision_type: str
    policy_version: str
    selected_output: dict
    basis: tuple[str, ...] = ()
    sources: tuple[SourceRef, ...] = ()
    rejected_alternatives: tuple[dict, ...] = ()
    confidence: str | None = None
    # Clé locale au groupe, utilisée pour recomposer les arêtes réelles.
    key: str | None = None
    upstream_keys: tuple[str, ...] = ()
    extras: dict = field(default_factory=dict)


def _bucketed(sources: tuple[SourceRef, ...]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {
        BUCKET_CONSTRAINT: [], BUCKET_PREFERENCE: [],
        BUCKET_MORPHOLOGY: [], BUCKET_RECOVERY: [],
    }
    for s in sources:
        out[_BUCKET.get(s.kind, BUCKET_CONSTRAINT)].append(s.as_payload())
    return out


def decision_fingerprint(draft: DraftTrace, upstream_fingerprints: tuple[str, ...]) -> str:
    """Identité de CONTENU, déterministe et sans horodatage.

    Deux exécutions portant les mêmes évidences et le même résultat produisent
    la **même** empreinte et des `decision_id` **différents** — c'est ce qui
    permet de reconnaître « la même décision, prise une seconde fois » au lieu
    de confondre l'événement et son contenu.

    `created_at`, `decision_id` et `trace_group_id` sont délibérément exclus.
    Même sérialisation triée que `weekly_planner._fingerprint`.
    """
    payload = json.dumps(
        {
            "analytics_version": DECISION_ANALYTICS_VERSION,
            "decision_type": draft.decision_type,
            "policy_version": draft.policy_version,
            "selected_output": draft.selected_output,
            "basis": list(draft.basis),
            "sources": [s.as_payload() for s in draft.sources],
            "rejected_alternatives": list(draft.rejected_alternatives),
            "confidence": draft.confidence,
            "upstream": sorted(upstream_fingerprints),
        },
        sort_keys=True, ensure_ascii=False, default=str,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# ── Construction des brouillons à partir de sorties DÉJÀ calculées ───────────


@dataclass(frozen=True)
class _Declared:
    """Ce que l'utilisateur a déclaré, isolé pour rester lisible comme tel."""

    cadence: int | None
    equipment: tuple[str, ...]


def _volume_band_drafts(budget, declared: _Declared) -> list[DraftTrace]:
    drafts: list[DraftTrace] = []
    declared_cadence = declared.cadence
    for zb in getattr(budget, "zones", ()):
        sources = [SourceRef(PRODUCT_POLICY, "weekly_volume_policy", zb.policy_version)]
        if zb.priority_rank is not None:
            # La priorité vient de l'utilisateur : c'est une déclaration, pas
            # une mesure, et surtout pas une inférence morphologique.
            sources.append(SourceRef(
                USER_DECLARED, f"focus_priority:{zb.zone_code}", zb.priority_rank))
        if declared_cadence is not None:
            sources.append(SourceRef(USER_DECLARED, "sessions_per_week", declared_cadence))
        drafts.append(DraftTrace(
            decision_type=VOLUME_BAND,
            policy_version=zb.policy_version,
            selected_output={
                "zone_code": zb.zone_code,
                "planning_low_sets": zb.planning_low_sets,
                "baseline_sets": zb.baseline_sets,
                "planning_high_sets": zb.planning_high_sets,
                "source": zb.source,
            },
            basis=tuple(zb.basis),
            sources=tuple(sources),
            key=f"{VOLUME_BAND}:{zb.zone_code}",
        ))
    return drafts


def _zone_allocation_drafts(plan, declared: _Declared) -> list[DraftTrace]:
    drafts: list[DraftTrace] = []
    declared_equipment = declared.equipment
    for cov in getattr(plan, "zone_coverage", ()):
        sources = [SourceRef(PRODUCT_POLICY, "capacity_allocator", plan.planner_version)]
        if cov.unmet_reason:
            sources.append(SourceRef(
                CATALOG_CONSTRAINT, f"unmet:{cov.zone_code}", cov.unmet_reason))
        if declared_equipment:
            sources.append(SourceRef(
                USER_DECLARED, _EQUIPMENT_REF, list(declared_equipment)))
        drafts.append(DraftTrace(
            decision_type=ZONE_ALLOCATION,
            policy_version=str(plan.planner_version),
            selected_output={
                "zone_code": cov.zone_code,
                "planned_slots": cov.planned_slots,
                "planned_sets": cov.planned_sets,
                "target_sets": cov.target_sets,
                "reaches_planning_low": getattr(cov, "reaches_planning_low", None),
                "overshoot_kind": cov.overshoot_kind,
                "unmet_reason": cov.unmet_reason,
            },
            basis=tuple(cov.allocation_basis),
            sources=tuple(sources),
            key=f"{ZONE_ALLOCATION}:{cov.zone_code}",
            upstream_keys=(f"{VOLUME_BAND}:{cov.zone_code}",),
        ))
    return drafts


def _occurrence_drafts(plan, declared: _Declared) -> list[DraftTrace]:
    """SLOT_SELECTION puis SET_PRESCRIPTION — par OCCURRENCE.

    Une même identité d'exercice peut revenir dans plusieurs séances (stabilité
    des identités), donc `slot_id` n'est pas unique : la clé est qualifiée par le
    rang de l'occurrence, sans quoi les arêtes seraient ambiguës.
    """
    drafts: list[DraftTrace] = []
    declared_equipment = declared.equipment
    for i, pres in enumerate(getattr(plan, "prescriptions", ())):
        occ = f"{pres.slot_id}#{i}"
        sel_sources = [SourceRef(CATALOG_CONSTRAINT, f"exercise:{pres.exercise_name}", None)]
        if declared_equipment:
            sel_sources.append(SourceRef(
                USER_DECLARED, _EQUIPMENT_REF, list(declared_equipment)))
        drafts.append(DraftTrace(
            decision_type=SLOT_SELECTION,
            policy_version=str(plan.planner_version),
            selected_output={
                "slot_id": pres.slot_id,
                "exercise_name": pres.exercise_name,
                "zone_code": pres.zone_code,
                "intent_id": pres.intent_id,
            },
            basis=(pres.rationale,),
            sources=tuple(sel_sources),
            # Le moteur ne conserve pas les candidats écartés à ce stade :
            # `[]` plutôt qu'une reconstruction plausible (OQ-2).
            rejected_alternatives=(),
            key=f"{SLOT_SELECTION}:{occ}",
            upstream_keys=(f"{ZONE_ALLOCATION}:{pres.zone_code}",),
        ))
        drafts.append(DraftTrace(
            decision_type=SET_PRESCRIPTION,
            policy_version=pres.policy_version,
            selected_output={
                "slot_id": pres.slot_id,
                "planned_sets": pres.planned_sets,
                "min_reps": pres.min_reps,
                "max_reps": pres.max_reps,
                "rep_target_source": pres.rep_target_source,
            },
            basis=(pres.budget_source,),
            sources=(SourceRef(PRODUCT_POLICY, "set_allocation_policy", pres.policy_version),),
            key=f"{SET_PRESCRIPTION}:{occ}",
            upstream_keys=(f"{SLOT_SELECTION}:{occ}",),
        ))
    return drafts


def _contribution_drafts(plan) -> list[DraftTrace]:
    """AGRÉGÉ par zone — jamais une trace par série physique (OQ-4)."""
    drafts: list[DraftTrace] = []
    for cov in getattr(plan, "zone_coverage", ()):
        if not cov.contribution_basis:
            continue
        upstream = tuple(
            f"{SET_PRESCRIPTION}:{p.slot_id}#{i}"
            for i, p in enumerate(getattr(plan, "prescriptions", ()))
            if p.zone_code == cov.zone_code
        )
        drafts.append(DraftTrace(
            decision_type=CONTRIBUTION_CREDIT,
            policy_version=str(plan.planner_version),
            selected_output={
                "zone_code": cov.zone_code,
                "direct_sets": cov.direct_sets,
                "indirect_sets": cov.indirect_sets,
                "effective_units": cov.effective_units,
            },
            basis=tuple(cov.contribution_basis),
            sources=(SourceRef(PRODUCT_POLICY, "set_contribution_policy", None),),
            key=f"{CONTRIBUTION_CREDIT}:{cov.zone_code}",
            upstream_keys=upstream,
        ))
    return drafts


def plan_generation_drafts(budget, plan, preferences) -> tuple[DraftTrace, ...]:
    """Transforme un `WeeklyVolumeBudget` + un `WeeklyPlan` en brouillons.

    Aucun moteur n'est appelé ici : tout provient des valeurs de retour. Les
    `basis` sont **repris tels quels** — la trace cite, elle ne reformule pas.

    L'ordre importe : les décisions amont sont écrites avant leurs consommatrices
    pour que les arêtes se résolvent dans le groupe.
    """
    declared = _Declared(
        cadence=getattr(preferences, "sessions_per_week", None),
        equipment=tuple(getattr(preferences, "available_equipment", ()) or ()),
    )
    return tuple(
        _volume_band_drafts(budget, declared)
        + _zone_allocation_drafts(plan, declared)
        + _occurrence_drafts(plan, declared)
        + _contribution_drafts(plan)
    )


def materialization_draft(plan, readiness, program=None) -> DraftTrace:
    """Une décision par tentative de matérialisation (OQ-4)."""
    return DraftTrace(
        decision_type=MATERIALIZATION,
        policy_version=str(getattr(readiness, "version", "1")),
        selected_output={
            "status": getattr(readiness, "status", None),
            "program_id": getattr(program, "id", None),
            "plan_fingerprint": getattr(plan, _FINGERPRINT_ATTR, None),
        },
        basis=tuple(getattr(readiness, "basis", ()) or ()),
        sources=(SourceRef(PRODUCT_POLICY, "materialization_policy", None),),
        key=f"{MATERIALIZATION}:{getattr(plan, _FINGERPRINT_ATTR, '')}",
    )


# ── Persistance ──────────────────────────────────────────────────────────────


def persist_traces(
    db: Session,
    user_id: int,
    drafts: tuple[DraftTrace, ...],
    *,
    plan_fingerprint: str | None = None,
    program_id: int | None = None,
    program_version: int | None = None,
    trace_group_id: str | None = None,
) -> str:
    """Écrit les brouillons et rend l'identifiant de groupe.

    Les arêtes amont sont résolues **à l'intérieur du groupe** via les clés
    locales : un lien n'est écrit que si la décision amont existe réellement
    dans ce groupe. Rien n'est relié parce que « ça se ressemble ».
    """
    from app.models.decision_trace import DecisionTrace

    group = trace_group_id or uuid.uuid4().hex
    id_by_key: dict[str, str] = {}
    fp_by_key: dict[str, str] = {}

    for draft in drafts:
        upstream_ids = [id_by_key[k] for k in draft.upstream_keys if k in id_by_key]
        upstream_fps = tuple(fp_by_key[k] for k in draft.upstream_keys if k in fp_by_key)

        decision_id = uuid.uuid4().hex
        fingerprint = decision_fingerprint(draft, upstream_fps)
        buckets = _bucketed(draft.sources)

        db.add(DecisionTrace(
            decision_id=decision_id,
            trace_group_id=group,
            user_id=user_id,
            decision_type=draft.decision_type,
            policy_version=str(draft.policy_version),
            decision_fingerprint=fingerprint,
            upstream_decision_ids=json.dumps(upstream_ids),
            constraint_sources=json.dumps(buckets[BUCKET_CONSTRAINT], ensure_ascii=False),
            preference_sources=json.dumps(buckets[BUCKET_PREFERENCE], ensure_ascii=False),
            morphology_sources=json.dumps(buckets[BUCKET_MORPHOLOGY], ensure_ascii=False),
            recovery_sources=json.dumps(buckets[BUCKET_RECOVERY], ensure_ascii=False),
            selected_output=json.dumps(draft.selected_output, ensure_ascii=False, default=str),
            rejected_alternatives=json.dumps(
                list(draft.rejected_alternatives), ensure_ascii=False, default=str),
            basis=json.dumps(list(draft.basis), ensure_ascii=False),
            confidence=draft.confidence,
            plan_fingerprint=plan_fingerprint,
            program_id=program_id,
            program_version=program_version,
        ))

        if draft.key:
            id_by_key[draft.key] = decision_id
            fp_by_key[draft.key] = fingerprint

    db.commit()
    return group


def observe_plan_generation(
    db: Session, user_id: int, budget, plan, preferences
) -> str | None:
    """Observe une génération de plan. **Ne lève jamais.**

    L'analytique de décision n'est pas une dépendance de disponibilité du
    produit : si l'écriture échoue, le plan reste valide et l'utilisateur
    continue. On journalise, on rend `None`, et surtout **on ne simule pas un
    succès** — l'absence de trace doit rester visible.
    """
    try:
        drafts = plan_generation_drafts(budget, plan, preferences)
        if not drafts:
            return None
        return persist_traces(
            db, user_id, drafts,
            plan_fingerprint=getattr(plan, _FINGERPRINT_ATTR, None),
        )
    # Capture volontairement large : c'est le point où l'observabilité cesse de
    # pouvoir nuire au produit. Voir la docstring.
    except Exception:  # noqa: BLE001
        logger.exception("decision-trace collection failed; product output untouched")
        try:
            db.rollback()
        # Le rollback lui-même ne doit pas casser l'opération produit.
        except Exception:  # noqa: BLE001
            logger.exception("decision-trace rollback failed")
        return None


def observe_plan_generation_for_user(db: Session, user_id: int, plan) -> str | None:
    """Observe un plan déjà calculé, sans toucher au chemin produit.

    Le budget est **re-dérivé** ici plutôt que passé par l'appelant. C'est
    volontaire : `build_weekly_volume_budget` est pur et déterministe, donc la
    re-dérivation rend exactement le budget que le planificateur a utilisé, et
    le chemin produit reste **littéralement inchangé** — une seule ligne
    d'observation ajoutée au routeur, aucune restructuration de l'appel qui
    produit le plan. C'est ce qui rend la preuve de retirabilité crédible.

    Tout est confiné dans le `try` de `observe_plan_generation`, y compris cette
    lecture : une préférence illisible ne doit pas casser une matérialisation.
    """
    try:
        from app.services.training_preferences import get_training_preferences
        from app.services.weekly_volume_budget import build_weekly_volume_budget

        prefs = get_training_preferences(db, user_id)
        budget = build_weekly_volume_budget(prefs)
    # Même raison que plus bas : l'observation ne peut pas nuire au produit.
    except Exception:  # noqa: BLE001
        logger.exception("decision-trace preflight failed; product output untouched")
        return None
    return observe_plan_generation(db, user_id, budget, plan, prefs)


def traces_for_group(db: Session, user_id: int, trace_group_id: str) -> list:
    """Lecture scopée au propriétaire : le groupe d'un autre est introuvable."""
    from sqlalchemy import select

    from app.models.decision_trace import DecisionTrace

    return list(db.execute(
        select(DecisionTrace)
        .where(DecisionTrace.user_id == user_id)
        .where(DecisionTrace.trace_group_id == trace_group_id)
        .order_by(DecisionTrace.id)
    ).scalars().all())


def latest_trace_group(db: Session, user_id: int, decision_type: str | None = None):
    """Dernier groupe écrit pour ce propriétaire, ou `None`."""
    from sqlalchemy import select

    from app.models.decision_trace import DecisionTrace

    stmt = select(DecisionTrace).where(DecisionTrace.user_id == user_id)
    if decision_type is not None:
        stmt = stmt.where(DecisionTrace.decision_type == decision_type)
    row = db.execute(
        stmt.order_by(DecisionTrace.id.desc()).limit(1)
    ).scalars().first()
    return row.trace_group_id if row is not None else None
