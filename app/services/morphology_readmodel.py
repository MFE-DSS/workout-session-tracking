"""Sb_MORPHO_PROFILE_READMODEL_01 — rendre le profil morphologique inspectable.

Ce module **ne décide de rien**. Il présente ce que l'adaptateur a lu et ce que
le moteur pur en a conclu, en gardant visible la seule chose qui compte pour un
lecteur : **d'où vient chaque ligne**.

Deux règles portent la surface :

**Un fait manquant est affiché comme manquant.** Une envergure non mesurée
produit « Envergure non renseignée », jamais « ape index neutre ». Silence sur
l'interprétation, explicite sur la donnée absente — la règle de la chaîne P0.4.

**Aucune promesse de conséquence.** La morphologie n'alimente aucun
planificateur aujourd'hui. La surface le dit, parce qu'une interface qui laisse
croire à un effet inexistant est une forme de fabrication.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from app.services.morphology_profile import (
    CONF_DERIVED,
    CONF_INFERRED,
    CONF_MEASURED,
    LAYER_FACT,
    build_morphology_profile,
)
from app.services.morphology_runtime import (
    PROFILE_LATEST_KNOWN_FACTS,
    build_morphology_facts,
)

MORPHOLOGY_READMODEL_VERSION = 1

# La phrase qui empêche l'interface de promettre un consommateur inexistant.
PLANNER_INFLUENCE_NOTICE = (
    "Ces éléments ne modifient pas encore automatiquement ton programme."
)

MIXED_DATE_NOTICE = (
    "Ces valeurs sont les dernières connues pour chaque mesure, prises à des "
    "dates différentes. Ce n'est pas un relevé unique."
)

# Catégories de confiance, jamais un pourcentage : « 72 % sûr » suggère une
# précision que ni la mesure ni le moteur ne possèdent.
CONFIDENCE_LABELS = {
    CONF_MEASURED: "mesuré",
    CONF_DERIVED: "calculé à partir de mesures",
    CONF_INFERRED: "lecture qualitative, étayage faible",
}

LAYER_LABELS = {LAYER_FACT: "Fait", "INFERENCE": "Lecture"}

FACT_LABELS = {
    "height_cm": "Taille",
    "wingspan_cm": "Envergure",
    "waist_cm": "Tour de taille",
    "chest_cm": "Tour de poitrine",
    "thigh_cm": "Tour de cuisse",
    "calf_cm": "Tour de mollet",
}

BASIS_LABELS = {
    "left+right mean": "moyenne gauche + droite",
    "single-side fallback (left)": "côté gauche seul",
    "single-side fallback (right)": "côté droit seul",
    "legacy calf_cm fallback": "ancienne saisie unique",
    "direct measurement": "mesure directe",
    "user profile height": "profil",
}

MISSING_LABELS = {
    "wingspan_cm": "Envergure non renseignée",
    "height_cm": "Taille non renseignée",
    "waist_cm": "Tour de taille non renseigné",
    "chest_cm": "Tour de poitrine non renseigné",
    "thigh_cm": "Tour de cuisse non renseigné",
    "calf_cm": "Tour de mollet non renseigné",
}

APE_INDEX_LABEL = "Ape index"
APE_INDEX_BASIS = "envergure − taille"


@dataclass(frozen=True)
class FactRow:
    key: str
    label: str
    value: float
    unit: str
    basis: str
    source_label: str
    measured_at: datetime | None


@dataclass(frozen=True)
class InterpretationRow:
    descriptor_id: str
    layer_label: str
    rationale: str
    confidence_label: str
    evidence: tuple[str, ...]
    guardrail: str
    is_proxy: bool


@dataclass(frozen=True)
class MorphologyReadModel:
    facts: tuple[FactRow, ...]
    ape_index: FactRow | None
    missing: tuple[str, ...]
    interpretations: tuple[InterpretationRow, ...]
    is_mixed_date: bool
    notice: str = PLANNER_INFLUENCE_NOTICE
    mixed_date_notice: str = MIXED_DATE_NOTICE
    version: int = MORPHOLOGY_READMODEL_VERSION

    @property
    def has_anything(self) -> bool:
        return bool(self.facts or self.interpretations)


def _ape_index(facts) -> FactRow | None:
    """Dérivé, affiché seulement si les deux faits existent.

    Aucun repli : sans envergure il n'y a pas d'ape index, et la ligne
    correspondante apparaît dans `missing` plutôt que sous une valeur neutre.
    """
    if facts.wingspan_cm is None or facts.height_cm is None:
        return None
    return FactRow(
        key="ape_index_cm",
        label=APE_INDEX_LABEL,
        value=round(facts.wingspan_cm - facts.height_cm, 2),
        unit="cm",
        basis=APE_INDEX_BASIS,
        source_label="calculé",
        measured_at=None,
    )


def build_morphology_readmodel(
    db: Session, user_id: int, *, as_of: datetime | None = None
) -> MorphologyReadModel:
    """Assemble la vue lisible du profil morphologique du propriétaire."""
    bundle = build_morphology_facts(db, user_id, as_of=as_of)
    facts = bundle.facts

    rows: list[FactRow] = []
    missing: list[str] = []
    for key, label in FACT_LABELS.items():
        value = getattr(facts, key, None)
        if value is None:
            missing.append(MISSING_LABELS[key])
            continue
        p = bundle.provenance_for(key)
        rows.append(FactRow(
            key=key,
            label=label,
            value=value,
            unit="cm",
            basis=BASIS_LABELS.get(p.basis if p else "", "mesure directe"),
            source_label="profil" if key == "height_cm" else "mesure",
            measured_at=p.measured_at if p else None,
        ))

    ape = _ape_index(facts)

    interpretations = tuple(
        InterpretationRow(
            descriptor_id=d.descriptor_id,
            layer_label=LAYER_LABELS.get(d.layer, d.layer),
            rationale=d.rationale,
            confidence_label=CONFIDENCE_LABELS.get(d.confidence, d.confidence),
            evidence=d.evidence,
            guardrail=d.non_medical_guardrail,
            is_proxy=d.is_proxy,
        )
        # Les descripteurs FACT dupliqueraient les lignes de faits ci-dessus :
        # seule la couche de lecture apporte quelque chose ici.
        for d in build_morphology_profile(facts)
        if d.layer != LAYER_FACT
    )

    return MorphologyReadModel(
        facts=tuple(rows),
        ape_index=ape,
        missing=tuple(missing),
        interpretations=interpretations,
        is_mixed_date=bundle.profile_kind == PROFILE_LATEST_KNOWN_FACTS,
    )
