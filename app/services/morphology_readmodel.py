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
from datetime import UTC, datetime

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
from app.services.time_format import relative_hours_ago

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
    #: `UI-CP1` — « il y a 28 j », ou `None` quand le fait n'est pas horodaté.
    #:
    #: `measured_at` traversait toute la chaîne et **mourait au gabarit** :
    #: `profile.html` rendait Mesure / Valeur / Base, jamais la date. Le champ
    #: était calculé, transporté, puis jeté à la dernière ligne.
    #:
    #: Le formatage n'est PAS écrit ici : `time_format.relative_hours_ago` sert
    #: déjà `/export` et `/healthz` avec la voix française du produit (« à
    #: l'instant », « hier », « il y a 2 mois »). Le corps est la dernière
    #: surface à en profiter, et la seule où l'âge d'une donnée change ce qu'on
    #: doit en conclure.
    age_label: str | None = None


@dataclass(frozen=True)
class MissingRow:
    """Un fait absent, avec de quoi le renseigner.

    `missing` porte des PHRASES (« Envergure non renseignée ») : lisibles, mais
    inexploitables par une interface qui doit poser l'action à côté du manque.
    Le libellé court et la clé permettent au gabarit de router chaque absence
    vers le bon formulaire — la taille vers les données de référence, le reste
    vers la saisie morphométrique.

    C'est le diagnostic répété de ce programme : *le produit a la décision, pas
    le moyen de l'appliquer*. `missing` décidait déjà quoi dire ; il manquait
    de quoi agir.
    """

    key: str
    label: str


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
    #: Les mêmes absences que `missing`, dans le même ordre, mais exploitables.
    #: `missing` reste inchangé : c'est un contrat lu ailleurs, et le remplacer
    #: aurait été une soustraction déguisée en amélioration.
    #:
    #: ⚠ Ce champ est **en dernier**, après les trois défauts existants : glissé
    #: avant eux, il aurait décalé toute construction POSITIONNELLE de cette
    #: dataclass sans qu'aucun nom de champ ne change — le genre de rupture
    #: qu'un test qui passe ne rattrape pas.
    missing_rows: tuple[MissingRow, ...] = ()

    @property
    def has_anything(self) -> bool:
        return bool(self.facts or self.interpretations)


def _age(mesure_le: datetime | None, as_of: datetime | None) -> str | None:
    """« il y a 28 j » — l'ancienneté d'un fait, ou `None` s'il n'a pas de date.

    ⚠ TROIS PIÈGES, DEUX MESURÉS DANS CE DÉPÔT.

    **La colonne ment sur son propre type.** `BodyMeasurement.measured_at` est
    déclarée `DateTime(timezone=True)` et **SQLite rend un datetime NAÏF** —
    vérifié en base. Soustraire un `datetime.now(UTC)` d'un naïf lève
    `TypeError`. `relative_hours_ago` absorbe l'écart ; c'est la raison
    principale de l'appeler plutôt que de soustraire ici.

    **Le formatage existait déjà**, et il est en service sur deux surfaces.
    En écrire un second ici aurait été la sixième copie d'un motif que ce dépôt
    duplique déjà cinq fois.

    **`as_of` n'est pas « maintenant ».** Il **borne la lecture dans le passé**
    (rejouer un profil tel qu'il était). Quand il est fourni, c'est donc lui la
    référence : un profil rejoué au 1er août ne doit pas afficher l'ancienneté
    d'aujourd'hui.
    """
    if mesure_le is None:
        return None
    return relative_hours_ago(as_of or datetime.now(UTC), mesure_le)


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
    missing_rows: list[MissingRow] = []
    for key, label in FACT_LABELS.items():
        value = getattr(facts, key, None)
        if value is None:
            missing.append(MISSING_LABELS[key])
            missing_rows.append(MissingRow(key=key, label=label))
            continue
        p = bundle.provenance_for(key)
        mesure_le = p.measured_at if p else None
        rows.append(FactRow(
            key=key,
            label=label,
            value=value,
            unit="cm",
            basis=BASIS_LABELS.get(p.basis if p else "", "mesure directe"),
            source_label="profil" if key == "height_cm" else "mesure",
            measured_at=mesure_le,
            age_label=_age(mesure_le, as_of),
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
        missing_rows=tuple(missing_rows),
    )
