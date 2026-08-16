"""Sb_ORCHESTRATOR_EXPLAINER_01 — « Pourquoi ce plan ? », en lecture seule.

Cette couche **lit des traces déjà écrites** et les rend lisibles. Elle ne
calcule aucune décision, n'en modifie aucune, et ne génère aucune prose : les
formulations sont un **dictionnaire fermé**, choisi par type de source.

Trois règles la gouvernent.

**La distinction épistémique survit à l'affichage.** « Tu as demandé 4 séances »
et « Auren planifie par fourchettes » ne sont pas la même sorte d'énoncé. Le
premier est une **déclaration de l'utilisateur**, le second une **convention
produit**. Les fondre en « voici pourquoi » détruirait ce que quatre tranches
ont payé pour établir. Chaque explication porte donc son étiquette de source, en
français lisible, jamais le jeton d'énumération.

**La morphologie n'est pas une raison de plan.** Le profil peut afficher des
descripteurs morphologiques ; le planificateur ne les consomme pas. Les faire
apparaître ici affirmerait un lien causal qui n'existe pas. Le filtre est
explicite et testé, y compris par plantation.

**Une trace absente n'est pas une raison inventée.** Sans trace, la surface dit
qu'elle n'a rien à montrer. Elle ne reconstruit pas une justification
plausible à partir du plan : ce serait exactement la fabrication que la chaîne
de traces existe pour rendre impossible.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.services.decision_analytics import (
    CATALOG_CONSTRAINT,
    MORPHOLOGY_INFERENCE,
    PRODUCT_POLICY,
    RECOVERY_ESTIMATE,
    USER_DECLARED,
    VOLUME_BAND,
    ZONE_ALLOCATION,
)

EXPLAINER_VERSION = 1

logger = logging.getLogger(__name__)

#: Nombre maximum d'explications rendues. Au-delà, la page cesse d'expliquer et
#: commence à lister.
MAX_EXPLANATIONS = 5

#: Étiquettes de source, en français. Le jeton d'énumération n'est jamais rendu.
SOURCE_LABELS = {
    USER_DECLARED: "Selon tes préférences",
    PRODUCT_POLICY: "Convention de planification",
    CATALOG_CONSTRAINT: "Contrainte du catalogue",
    RECOVERY_ESTIMATE: "Estimation de récupération",
}

#: Les seules natures pour lesquelles une confiance a un sens. Une préférence
#: déclarée n'a pas de « confiance » : l'utilisateur l'a dite.
CONFIDENCE_BEARING = frozenset({RECOVERY_ESTIMATE})

#: La morphologie est délibérément absente : le planificateur ne la consomme
#: pas, donc elle ne peut pas être une raison de plan (voir le module docstring).
EXCLUDED_FROM_PLAN_REASONS = frozenset({MORPHOLOGY_INFERENCE})

PLANNER_INDEPENDENCE_NOTICE = (
    "Ces éléments décrivent comment le plan a été construit, pas un jugement "
    "sur toi."
)

UNAVAILABLE_NOTICE = (
    "Aucune trace de décision n'est encore enregistrée pour ce plan. "
    "Les explications apparaîtront après la création d'un brouillon."
)

MORPHOLOGY_GUARD = (
    "La morphologie est visible sur le profil et n'entre dans aucune decision "
    "de planification. Elle est donc absente de cette page, ou elle "
    "affirmerait un lien de cause a effet qui n'existe pas."
)


@dataclass(frozen=True)
class ExplanationItem:
    """Une explication rendue. Déterministe, sans prose générée.

    `source_kind` porte le jeton d'origine (jamais rendu) et `source_label` la
    formulation française (seule rendue). Les deux existent parce que le filtre
    d'exclusion doit s'appliquer sur la **nature**, pas sur une chaîne
    d'affichage : ma première version comparait `source_label` à un jeton, donc
    elle ne filtrait rien du tout.
    """

    source_kind: str
    source_label: str
    text: str
    detail: str | None = None
    confidence_label: str | None = None


@dataclass(frozen=True)
class PlanExplanation:
    items: tuple[ExplanationItem, ...]
    available: bool
    notice: str = PLANNER_INDEPENDENCE_NOTICE
    unavailable_notice: str = UNAVAILABLE_NOTICE
    version: int = EXPLAINER_VERSION


def _loads(raw: str | None) -> list:
    try:
        value = json.loads(raw or "[]")
    except (TypeError, ValueError):
        return []
    return value if isinstance(value, list) else []


def _cadence_item(traces) -> ExplanationItem | None:
    """La cadence déclarée — la raison la plus directe qu'un plan puisse avoir."""
    for row in traces:
        for src in _loads(row.preference_sources):
            if src.get("ref") == "sessions_per_week" and src.get("value"):
                sessions = src["value"]
                return ExplanationItem(
                    source_kind=USER_DECLARED,
                    source_label=SOURCE_LABELS[USER_DECLARED],
                    text=f"Tu as demandé {sessions} séances par semaine.",
                    detail="Le plan est construit pour ce nombre de séances.",
                )
    return None


def _priority_items(traces) -> list[ExplanationItem]:
    """Les priorités déclarées, dans l'ordre de rang."""
    from app.services.training_preferences import focus_priority_label

    ranked: list[tuple[int, str]] = []
    for row in traces:
        if row.decision_type != VOLUME_BAND:
            continue
        for src in _loads(row.preference_sources):
            ref = src.get("ref", "")
            if ref.startswith("focus_priority:") and src.get("value"):
                ranked.append((int(src["value"]), ref.split(":", 1)[1]))

    out: list[ExplanationItem] = []
    for _rank, zone in sorted(set(ranked)):
        try:
            label = focus_priority_label(zone)
        except Exception:  # noqa: BLE001 - un libellé manquant ne casse pas la page
            label = zone
        out.append(ExplanationItem(
            source_kind=USER_DECLARED,
            source_label=SOURCE_LABELS[USER_DECLARED],
            text=f"Tu as placé {label} parmi tes priorités.",
            detail="Cette zone reçoit davantage de séries que les autres.",
        ))
    return out


def _policy_item(traces) -> ExplanationItem | None:
    """La convention de fourchette — énoncée comme produit, jamais comme biologie."""
    for row in traces:
        if row.decision_type != VOLUME_BAND:
            continue
        for src in _loads(row.constraint_sources):
            if src.get("kind") == PRODUCT_POLICY:
                return ExplanationItem(
                    source_kind=PRODUCT_POLICY,
                    source_label=SOURCE_LABELS[PRODUCT_POLICY],
                    text=(
                        "Auren planifie chaque zone dans une fourchette de "
                        "volume hebdomadaire, et répartit les séries dans la "
                        "capacité des séances que tu as déclarées."
                    ),
                    detail=(
                        "C'est une convention de planification du produit — "
                        "une façon de répartir le travail, pas une mesure te "
                        "concernant."
                    ),
                )
    return None


def _constraint_items(traces) -> list[ExplanationItem]:
    """Les contraintes qui ont réellement empêché quelque chose."""
    seen: set[str] = set()
    out: list[ExplanationItem] = []
    for row in traces:
        if row.decision_type != ZONE_ALLOCATION:
            continue
        output = {}
        try:
            output = json.loads(row.selected_output or "{}")
        except (TypeError, ValueError):
            output = {}
        reason = output.get("unmet_reason")
        zone = output.get("zone_code")
        if not reason or zone in seen:
            continue
        seen.add(zone)
        out.append(ExplanationItem(
            source_kind=CATALOG_CONSTRAINT,
            source_label=SOURCE_LABELS[CATALOG_CONSTRAINT],
            text=(
                f"La zone « {zone} » n'a pas pu être servie complètement avec "
                "le matériel déclaré."
            ),
            detail="Déclarer davantage de matériel ouvrirait d'autres exercices.",
        ))
    return out


def _recovery_items(traces) -> list[ExplanationItem]:
    """La récupération n'apparaît que si elle a réellement pesé sur la décision."""
    out: list[ExplanationItem] = []
    for row in traces:
        sources = _loads(row.recovery_sources)
        if not sources:
            continue
        out.append(ExplanationItem(
            source_kind=RECOVERY_ESTIMATE,
            source_label=SOURCE_LABELS[RECOVERY_ESTIMATE],
            text="Un état de récupération a été pris en compte pour ce plan.",
            detail=None,
            confidence_label=(row.confidence or "estimation"),
        ))
    return out


def build_plan_explanation(db: Session, user_id: int) -> PlanExplanation:
    """Assemble « Pourquoi ce plan ? » à partir des traces du propriétaire.

    Lecture seule et scopée au propriétaire. Ne lève jamais : une page produit
    ne doit pas tomber parce que son explication est indisponible.
    """
    try:
        traces = _owned_latest_group(db, user_id)
    except Exception:  # noqa: BLE001 - l'explication ne casse jamais /programs
        logger.exception("plan explanation unavailable; page unaffected")
        return PlanExplanation(items=(), available=False)

    if not traces:
        return PlanExplanation(items=(), available=False)

    items: list[ExplanationItem] = []
    cadence = _cadence_item(traces)
    if cadence is not None:
        items.append(cadence)
    items.extend(_priority_items(traces))
    policy = _policy_item(traces)
    if policy is not None:
        items.append(policy)
    items.extend(_constraint_items(traces))
    items.extend(_recovery_items(traces))

    # L'exclusion s'applique sur la NATURE, et **avant** la troncature.
    #
    # Ma première version filtrait sur `source_label` (une chaîne française)
    # contre un jeton : elle ne retirait rien. Et comme la troncature venait
    # après, une raison interdite ajoutée en fin de liste disparaissait
    # simplement en tombant au-delà du plafond — invisible pour la mauvaise
    # raison. Une plantation l'a montré : la morphologie affichée en clair
    # laissait les 26 tests verts.
    allowed = [
        item for item in items
        if item.source_kind not in EXCLUDED_FROM_PLAN_REASONS
    ]
    kept = tuple(allowed[:MAX_EXPLANATIONS])

    return PlanExplanation(items=kept, available=bool(kept))


def _owned_latest_group(db: Session, user_id: int) -> list:
    """Le dernier groupe de traces du propriétaire, ou une liste vide."""
    from sqlalchemy import select

    from app.models.decision_trace import DecisionTrace

    latest = db.execute(
        select(DecisionTrace.trace_group_id)
        .where(DecisionTrace.user_id == user_id)
        .order_by(DecisionTrace.id.desc())
        .limit(1)
    ).scalars().first()
    if latest is None:
        return []
    return list(db.execute(
        select(DecisionTrace)
        .where(DecisionTrace.user_id == user_id)
        .where(DecisionTrace.trace_group_id == latest)
        .order_by(DecisionTrace.id)
    ).scalars().all())
