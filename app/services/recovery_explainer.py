"""Explication utilisateur déterministe de `TrainingState` (Sb_RECOVERY_EXPLAINER_01).

Tranche 5/5 de P0.4. Couche de **présentation pure** au-dessus du contrat
canonique : elle met des mots sur des faits déjà calculés, elle n'en produit
aucun. Même rôle vis-à-vis de `recovery_contract` / `zone_recovery` que
`program_quality_feedback` vis-à-vis de `program_quality_engine` — et la même
règle : **aucun recalcul**.

Ce que cette couche ne fait pas, par construction et non par convention :

- aucune arithmétique de récupération (aucun seuil de bande, aucun roll-up
  macro : `band` et `MacroAxisRecovery` viennent des tranches précédentes) ;
- aucune décision d'entraînement — pas de choix de séance, pas de volume, pas
  de classement de séances. L'explication **décrit un état, pas une action** ;
- aucun LLM, aucun aléa, **aucune horloge** : le rendu est une fonction pure de
  l'état reçu.

Doctrine de microcopy (spec §8, non négociable) :

1. **Silence sur la physiologie, explicite sur la donnée manquante.**
   `Confidence.NONE` ⇒ **aucune** phrase de récupération, ni rassurante ni
   alarmante. Une surface détaillée peut en revanche dire explicitement que la
   donnée manque — c'est un état de DONNÉE, jamais une bande de récupération.
   Les deux vivent dans des collections séparées (`zone_items` vs
   `data_state_items`) et `recovery_rank_key` **refuse** un état de donnée :
   un « données insuffisantes » ne peut pas être trié comme s'il était une
   estimation.
2. **Confiance ordinale, jamais de fausse précision.** « Confiance faible »,
   jamais « confiance 0.42 » ni « 42 % ». Aucune chaîne rendue ne contient
   `%` ni de durée de récupération en heures.
3. **Le déclaré reste déclaré.** « Tu as déclaré te sentir moins frais »,
   jamais « ton corps est moins récupéré ».
4. **Asymétrie (OQ-7).** Une bonne readiness ne produit **jamais** de langage
   d'escalade. Elle décrit un état ; elle n'autorise rien.

**Traduction des `basis` : liste fermée, sinon silence.** Les `basis` amont sont
de la prose d'ingénierie (identifiants, noms de sentinelles, vocabulaire DB).
Aucune n'est rendue telle quelle. Les raisons produit sont dérivées des **champs
structurés** (`contributing_signals`, `band`, `confidence`, `sufficiency`) et,
pour les rares faits que seul le `basis` porte, d'une **table de marqueurs
fermée**. Un `basis` non reconnu est **omis** — jamais deviné, jamais recopié.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from app.services.muscle_mapping import (
    RADAR_AXES,
    RADAR_AXIS_ORDER,
    ZONE_LABELS,
)
from app.services.recovery_contract import (
    CardioModality,
    Confidence,
    MacroAxisRecovery,
    ReadinessSignal,
    RecoveryBand,
    Sufficiency,
    TrainingState,
    ZoneRecoveryEstimate,
    cardio_zone_exposure,
)
from app.services.zone_recovery import build_macro_recovery

#: Version de la couche de langage. Distincte de `RECOVERY_CONTRACT_VERSION` :
#: la formulation peut évoluer sans que le contrat bouge, et l'inverse.
EXPLAINER_VERSION = 1

# --- catégories sémantiques -------------------------------------------------

KIND_ZONE_RECOVERY = "zone_recovery"
KIND_MACRO_AXIS = "macro_axis"
KIND_READINESS = "readiness"
KIND_CARDIO = "cardio"
KIND_DATA_PROMPT = "data_prompt"

EXPLANATION_KINDS: tuple[str, ...] = (
    KIND_ZONE_RECOVERY,
    KIND_MACRO_AXIS,
    KIND_READINESS,
    KIND_CARDIO,
    KIND_DATA_PROMPT,
)

#: Surface détaillée : la zone est attendue, donc elle reste visible même sans
#: estimation, avec un état de donnée explicite.
SURFACE_DETAILED = "detailed"

#: Surface proactive (accueil / cockpit) : une zone sans estimation est
#: **omise**. On ne remplit pas un cockpit de « données insuffisantes ».
SURFACE_PROACTIVE = "proactive"


# ---------------------------------------------------------------------------
# Confiance affichée
# ---------------------------------------------------------------------------

#: Confiance maximale que cette couche accepte d'afficher. Le contrat déclare
#: `Confidence.HIGH`, mais **aucun producteur de P0.4 ne peut l'atteindre**
#: (`zone_recovery` plafonne à MEDIUM, le cardio aussi via
#: `CARDIO_MAX_CONFIDENCE`). Afficher « confiance élevée » annoncerait donc une
#: solidité que rien ne produit. Un `HIGH` qui arriverait quand même est rendu
#: **au niveau inférieur** : sous-estimer la confiance va dans le sens prudent
#: de l'asymétrie du train, la surestimer non. Épinglé par un test.
MAX_RENDERABLE_CONFIDENCE = Confidence.MEDIUM

CONFIDENCE_LABEL_LOW = "Confiance faible"
CONFIDENCE_LABEL_MEDIUM = "Confiance moyenne"

#: Libellé canonique de l'état « pas d'estimation possible ». Ce n'est **pas**
#: une bande de récupération.
INSUFFICIENT_DATA_LABEL = "Données insuffisantes"

CONFIDENCE_LABELS: dict[Confidence, str] = {
    Confidence.MEDIUM: CONFIDENCE_LABEL_MEDIUM,
    Confidence.LOW: CONFIDENCE_LABEL_LOW,
    Confidence.NONE: INSUFFICIENT_DATA_LABEL,
}


def renderable_confidence(confidence: Confidence) -> Confidence:
    """La confiance telle qu'elle peut être montrée, plafonnée à MEDIUM."""
    if confidence is Confidence.HIGH:
        return MAX_RENDERABLE_CONFIDENCE
    return confidence


def confidence_label(confidence: Confidence) -> str:
    """Libellé ordinal. Jamais un nombre, jamais un pourcentage."""
    return CONFIDENCE_LABELS[renderable_confidence(confidence)]


# ---------------------------------------------------------------------------
# Objets d'explication
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ExplanationItem:
    """Une explication prête à afficher, immuable et sérialisable.

    `is_estimate` porte la distinction produit centrale : `True` = une lecture
    de récupération réelle, `False` = un constat sur la **donnée** (manquante,
    trop ancienne) ou une invitation à en saisir. Un consommateur qui traite les
    deux de la même façon transforme une absence de donnée en affirmation sur le
    corps — c'est exactement ce que cette tranche interdit.

    `subject` est un **code machine** (`zone_code` ou `axis_key`) : il n'est pas
    du texte rendu et n'est donc pas soumis au garde-fou de formulation.
    `subject_label` est sa forme affichable, issue du vocabulaire canonique.
    """

    kind: str
    message: str
    is_estimate: bool
    subject: str | None = None
    subject_label: str | None = None
    confidence: Confidence | None = None
    confidence_label: str | None = None
    band: RecoveryBand | None = None
    reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.kind not in EXPLANATION_KINDS:
            raise ValueError(f"unknown explanation kind: {self.kind!r}")
        # « Toute phrase de disponibilité est accompagnée de sa confiance »
        # (spec §Sb_RECOVERY_EXPLAINER_01, DoD). Une interprétation sans
        # métadonnée de confiance est invalide, pas seulement déconseillée.
        if self.is_estimate and self.confidence is None:
            raise ValueError("an estimate explanation must carry a confidence")


@dataclass(frozen=True)
class RecoveryExplanation:
    """Vue-modèle complète d'une surface. Ordre stable, contenu déterministe.

    Les estimations et les états de donnée sont **deux collections distinctes**
    et non un champ discriminant dans une seule liste : une surface qui itère
    naïvement ne peut pas afficher « données insuffisantes » au milieu de bandes
    de récupération.
    """

    surface: str
    zone_items: tuple[ExplanationItem, ...] = ()
    data_state_items: tuple[ExplanationItem, ...] = ()
    macro_items: tuple[ExplanationItem, ...] = ()
    readiness_item: ExplanationItem | None = None
    cardio_item: ExplanationItem | None = None
    data_prompt: ExplanationItem | None = None
    version: int = EXPLAINER_VERSION

    def all_items(self) -> tuple[ExplanationItem, ...]:
        """Tous les items, dans un ordre stable. Pratique pour les garde-fous."""
        singles = [self.readiness_item, self.cardio_item, self.data_prompt]
        return (
            *self.zone_items,
            *self.macro_items,
            *self.data_state_items,
            *[item for item in singles if item is not None],
        )


# ---------------------------------------------------------------------------
# Langage des bandes de récupération
# ---------------------------------------------------------------------------

#: Une phrase par bande **réellement estimée**. `RecoveryBand.UNKNOWN` est
#: volontairement absente : il n'existe aucune phrase de récupération pour une
#: zone sans estimation, seulement un état de donnée.
BAND_MESSAGES: dict[RecoveryBand, str] = {
    RecoveryBand.LIKELY_AVAILABLE: "Cette zone semble probablement disponible.",
    RecoveryBand.PARTIALLY_RECOVERED: (
        "Récupération estimée intermédiaire pour cette zone."
    ),
    RecoveryBand.LIKELY_FATIGUED: (
        "Cette zone semble encore chargée par l'entraînement récent."
    ),
}

AXIS_BAND_MESSAGES: dict[RecoveryBand, str] = {
    RecoveryBand.LIKELY_AVAILABLE: "Cet ensemble semble probablement disponible.",
    RecoveryBand.PARTIALLY_RECOVERED: (
        "Récupération estimée intermédiaire pour cet ensemble."
    ),
    RecoveryBand.LIKELY_FATIGUED: (
        "Cet ensemble semble encore chargé par l'entraînement récent."
    ),
}

ZONE_INSUFFICIENT_MESSAGE = (
    "Pas assez de données récentes pour estimer cette zone."
)
AXIS_INSUFFICIENT_MESSAGE = (
    "Pas assez de données récentes pour estimer cet ensemble."
)

#: Un **seul** message agrégé pour une surface proactive sans aucune estimation
#: — au lieu de onze fois le même constat.
GLOBAL_INSUFFICIENT_MESSAGE = (
    "Pas encore assez de séances enregistrées pour estimer tes zones."
)


# ---------------------------------------------------------------------------
# Traduction des preuves en raisons produit
# ---------------------------------------------------------------------------

#: Signaux structurés → raison lisible. Clés = `contributing_signals` du
#: contrat, une énumération fermée côté producteur.
SIGNAL_REASONS: dict[str, str] = {
    "strength_load": (
        "Du travail en force a été enregistré récemment pour cette zone."
    ),
    "cardio_exposure": (
        "Une exposition cardio récente est prise en compte pour cette zone."
    ),
}

#: Marqueurs `basis` reconnus → raison produit. **Liste fermée.** Un `basis`
#: qui ne correspond à aucun marqueur n'est pas rendu : mieux vaut omettre un
#: détail que lui inventer un sens (et qu'exposer de la prose interne).
BASIS_MARKER_REASONS: tuple[tuple[str, str], ...] = (
    (
        "attribution fell back to the substring classifier",
        "L'attribution de certains exercices à cette zone reste approximative.",
    ),
    (
        "no recorded strength load for this zone",
        "Aucune séance de renforcement enregistrée pour cette zone.",
    ),
    (
        "last load could not be placed against a recovery target",
        "La dernière séance enregistrée n'a pas pu être située dans le temps.",
    ),
)

#: Marqueurs qui signalent qu'un `basis` parle de cardio. Le nom de la modalité
#: n'est lu **que** dans ces entrées, et **que** s'il appartient au vocabulaire
#: fermé `CardioModality`.
_CARDIO_BASIS_MARKERS: tuple[str, ...] = (
    "cardio exposure noted (",
    "modality: ",
)

MODALITY_LABELS: dict[CardioModality, str] = {
    CardioModality.VELO: "vélo",
    CardioModality.MARCHE: "marche",
    CardioModality.RAMEUR: "rameur",
    CardioModality.ELLIPTIQUE: "elliptique",
}

#: Jetons acceptés comme nom de modalité : exactement le vocabulaire fermé
#: nommable. `autre` / `unknown` n'y sont pas, donc une modalité hors liste ne
#: peut produire aucune phrase.
_NAMEABLE_MODALITIES: dict[str, CardioModality] = {
    modality.value: modality for modality in MODALITY_LABELS
}

_TOKEN_RE = re.compile(r"[a-z]+")


def recognised_modalities(basis: tuple[str, ...]) -> tuple[CardioModality, ...]:
    """Modalités cardio **nommables** trouvées dans un `basis`.

    Ce n'est pas de l'analyse de prose : on ne lit que les entrées portant un
    marqueur cardio connu, et on ne retient qu'un jeton appartenant au
    vocabulaire fermé du contrat. `autre` / `unknown` en sont absents, donc une
    modalité inconnue ne produit **aucune** affirmation de zone.
    """
    found: list[CardioModality] = []
    for entry in basis:
        if not any(marker in entry for marker in _CARDIO_BASIS_MARKERS):
            continue
        for token in _TOKEN_RE.findall(entry):
            modality = _NAMEABLE_MODALITIES.get(token)
            if modality is not None and modality not in found:
                found.append(modality)
    return tuple(found)


def _basis_reasons(basis: tuple[str, ...]) -> list[str]:
    reasons: list[str] = []
    for entry in basis:
        for marker, text in BASIS_MARKER_REASONS:
            if marker in entry and text not in reasons:
                reasons.append(text)
    return reasons


def _zone_reasons(estimate: ZoneRecoveryEstimate) -> tuple[str, ...]:
    reasons: list[str] = []
    for signal in estimate.contributing_signals:
        text = SIGNAL_REASONS.get(signal)
        if text is not None and text not in reasons:
            reasons.append(text)
    for text in _basis_reasons(estimate.basis):
        if text not in reasons:
            reasons.append(text)
    return tuple(reasons)


# ---------------------------------------------------------------------------
# Zones
# ---------------------------------------------------------------------------


def _zone_label(zone_code: str) -> str:
    return ZONE_LABELS.get(zone_code, zone_code)


def _axis_label(axis_key: str) -> str:
    axis = RADAR_AXES.get(axis_key)
    return axis["label"] if axis else axis_key


def explain_zone(estimate: ZoneRecoveryEstimate) -> ExplanationItem:
    """Une zone → une explication, ou un état de donnée.

    `RecoveryBand.UNKNOWN` et `Confidence.NONE` ne produisent **jamais** de
    lecture de récupération : ni « probablement disponible » ni « encore
    chargée ». Le seul énoncé autorisé porte sur la donnée elle-même.
    """
    confidence = renderable_confidence(estimate.confidence)
    message = BAND_MESSAGES.get(estimate.band)
    if message is None or confidence is Confidence.NONE:
        return ExplanationItem(
            kind=KIND_ZONE_RECOVERY,
            message=ZONE_INSUFFICIENT_MESSAGE,
            is_estimate=False,
            subject=estimate.zone_code,
            subject_label=_zone_label(estimate.zone_code),
            confidence=Confidence.NONE,
            confidence_label=INSUFFICIENT_DATA_LABEL,
            band=RecoveryBand.UNKNOWN,
            reasons=_zone_reasons(estimate),
        )
    return ExplanationItem(
        kind=KIND_ZONE_RECOVERY,
        message=message,
        is_estimate=True,
        subject=estimate.zone_code,
        subject_label=_zone_label(estimate.zone_code),
        confidence=confidence,
        confidence_label=confidence_label(confidence),
        band=estimate.band,
        reasons=_zone_reasons(estimate),
    )


def explain_axis(axis: MacroAxisRecovery) -> ExplanationItem:
    """Un axe radar → une explication. **Aucun roll-up n'est recalculé ici.**

    `MacroAxisRecovery` arrive déjà agrégé par `zone_recovery.build_macro_recovery`
    (OQ-5, présentation uniquement, `core` hors axes). Cette fonction met des
    mots sur `band`, `confidence` et `limiting_zone_code` — rien d'autre.
    """
    confidence = renderable_confidence(axis.confidence)
    message = AXIS_BAND_MESSAGES.get(axis.band)
    reasons: list[str] = []
    if axis.limiting_zone_code is not None:
        reasons.append(
            "Lecture la plus prudente de l'ensemble : "
            f"{_zone_label(axis.limiting_zone_code)}."
        )
    if message is None or confidence is Confidence.NONE:
        return ExplanationItem(
            kind=KIND_MACRO_AXIS,
            message=AXIS_INSUFFICIENT_MESSAGE,
            is_estimate=False,
            subject=axis.axis_key,
            subject_label=_axis_label(axis.axis_key),
            confidence=Confidence.NONE,
            confidence_label=INSUFFICIENT_DATA_LABEL,
            band=RecoveryBand.UNKNOWN,
            reasons=tuple(reasons),
        )
    return ExplanationItem(
        kind=KIND_MACRO_AXIS,
        message=message,
        is_estimate=True,
        subject=axis.axis_key,
        subject_label=_axis_label(axis.axis_key),
        confidence=confidence,
        confidence_label=confidence_label(confidence),
        band=axis.band,
        reasons=tuple(reasons),
    )


# ---------------------------------------------------------------------------
# Readiness — déclarée, jamais mesurée
# ---------------------------------------------------------------------------

#: Bandes **de formulation** pour une readiness déclarée, sur l'échelle
#: normalisée 0.0–1.0 « plus haut = mieux » du contrat. Ce sont des seuils de
#: *langage* : ils choisissent une phrase, ils ne pondèrent rien et n'entrent
#: dans aucun calcul. Épinglés par un test.
READINESS_DECLARED_LOW_BELOW = 0.4
READINESS_DECLARED_GOOD_FROM = 0.7

READINESS_STALE_MESSAGE = (
    "Ta dernière déclaration d'état n'est plus récente : elle n'est pas prise "
    "en compte comme état du jour."
)

DATA_PROMPT_MESSAGE = (
    "Renseigne ton état du jour pour améliorer l'estimation."
)

_WHEN_TODAY = "aujourd'hui"
_WHEN_RECENT = "récemment"


def explain_readiness(readiness: ReadinessSignal) -> ExplanationItem | None:
    """La readiness telle qu'elle a été **déclarée**.

    Le sujet grammatical est toujours l'utilisateur qui déclare, jamais son
    corps : « tu as déclaré te sentir moins frais », jamais « ton corps est
    moins récupéré ». Aucune déclaration ⇒ aucun item (l'invitation à saisir est
    un objet séparé, `data_prompt`).

    Asymétrie OQ-7 : une bonne déclaration décrit un état et **n'autorise
    rien** — pas de « tu peux pousser plus lourd ». Une déclaration périmée
    n'est rendue que comme contexte, jamais comme état du jour.
    """
    if readiness.sufficiency is Sufficiency.STALE:
        return ExplanationItem(
            kind=KIND_READINESS,
            message=READINESS_STALE_MESSAGE,
            is_estimate=False,
        )
    if readiness.overall is None or readiness.sufficiency is Sufficiency.INSUFFICIENT:
        return None

    when = _WHEN_TODAY if readiness.age_days == 0 else _WHEN_RECENT
    if readiness.overall < READINESS_DECLARED_LOW_BELOW:
        message = f"Tu as déclaré te sentir moins frais {when}."
    elif readiness.overall >= READINESS_DECLARED_GOOD_FROM:
        message = f"Tu as déclaré te sentir en forme {when}."
    else:
        message = f"Tu as déclaré ton état du jour {when}."
    return ExplanationItem(
        kind=KIND_READINESS,
        message=message,
        is_estimate=False,
        reasons=("Déclaration personnelle, pas une mesure.",),
    )


# ---------------------------------------------------------------------------
# Cardio — exposition récente, jamais fatigue mesurée
# ---------------------------------------------------------------------------

CARDIO_UNKNOWN_MESSAGE = (
    "Une séance cardio récente est enregistrée ; le type d'activité ne permet "
    "pas d'identifier les zones concernées."
)


def explain_cardio(state: TrainingState) -> ExplanationItem | None:
    """L'exposition cardio récente, si une modalité **nommable** est connue.

    Le cardio est une *exposition récente*, jamais une fatigue tissulaire
    mesurée ni une pénalité de récupération. Il n'y a donc ni durée, ni
    fréquence cardiaque, ni calories dans la phrase : aucun de ces champs
    n'observe une charge individuelle (voir `cardio_load_estimate`).

    Modalité absente ou hors vocabulaire ⇒ **aucune zone n'est nommée**.
    """
    modalities = recognised_modalities(state.fatigue.basis)
    if not modalities:
        if _has_cardio_evidence(state):
            return ExplanationItem(
                kind=KIND_CARDIO,
                message=CARDIO_UNKNOWN_MESSAGE,
                is_estimate=False,
            )
        return None

    names = " / ".join(MODALITY_LABELS[modality] for modality in modalities)
    zones = _cardio_zone_labels(modalities)
    if zones:
        message = (
            f"Ton activité cardio récente ({names}) est prise en compte comme "
            f"exposition récente pour : {zones}."
        )
    else:
        message = (
            f"Ton activité cardio récente ({names}) est prise en compte comme "
            "exposition récente."
        )
    return ExplanationItem(
        kind=KIND_CARDIO,
        message=message,
        is_estimate=False,
        reasons=(
            "Exposition enregistrée, pas une mesure de fatigue musculaire.",
        ),
    )


def _has_cardio_evidence(state: TrainingState) -> bool:
    return state.fatigue.cardio_component is not None


def _cardio_zone_labels(modalities: tuple[CardioModality, ...]) -> str:
    labels: list[str] = []
    for modality in modalities:
        for zone_code in cardio_zone_exposure(modality).primary_zones:
            label = _zone_label(zone_code)
            if label not in labels:
                labels.append(label)
    return ", ".join(labels)


# ---------------------------------------------------------------------------
# Assemblage des surfaces
# ---------------------------------------------------------------------------


def _macro_items(state: TrainingState) -> list[ExplanationItem]:
    axes = build_macro_recovery(state.zone_recovery)
    order = {key: index for index, key in enumerate(RADAR_AXIS_ORDER)}
    ordered = sorted(axes, key=lambda axis: order.get(axis.axis_key, len(order)))
    return [explain_axis(axis) for axis in ordered]


def build_detailed_explanation(state: TrainingState) -> RecoveryExplanation:
    """Surface détaillée : **toutes** les zones restent structurellement là.

    Une zone attendue qui disparaît est indiscernable d'une zone oubliée. Une
    zone sans estimation reste donc présente, avec un état de donnée explicite,
    dans `data_state_items` — jamais parmi les bandes de récupération.
    """
    zone_items: list[ExplanationItem] = []
    data_state: list[ExplanationItem] = []
    for estimate in state.zone_recovery:
        item = explain_zone(estimate)
        (zone_items if item.is_estimate else data_state).append(item)
    macro: list[ExplanationItem] = []
    for item in _macro_items(state):
        (macro if item.is_estimate else data_state).append(item)
    return RecoveryExplanation(
        surface=SURFACE_DETAILED,
        zone_items=tuple(zone_items),
        data_state_items=tuple(data_state),
        macro_items=tuple(macro),
        readiness_item=explain_readiness(state.readiness),
        cardio_item=explain_cardio(state),
        data_prompt=_data_prompt(state),
    )


def build_proactive_explanation(state: TrainingState) -> RecoveryExplanation:
    """Surface proactive : on n'occupe pas l'écran avec des trous de données.

    Une zone `Confidence.NONE` est **omise**, pas commentée. S'il n'y a
    strictement rien à estimer, un **unique** message agrégé le dit — au lieu
    de onze constats identiques. Une déclaration périmée n'est pas remontée
    ici : elle n'est du contexte que sur une surface qui la demande.
    """
    zone_items = [
        item for item in map(explain_zone, state.zone_recovery) if item.is_estimate
    ]
    macro = [item for item in _macro_items(state) if item.is_estimate]
    data_state: list[ExplanationItem] = []
    if not zone_items:
        data_state.append(
            ExplanationItem(
                kind=KIND_ZONE_RECOVERY,
                message=GLOBAL_INSUFFICIENT_MESSAGE,
                is_estimate=False,
                confidence=Confidence.NONE,
                confidence_label=INSUFFICIENT_DATA_LABEL,
            )
        )
    readiness = explain_readiness(state.readiness)
    if readiness is not None and state.readiness.sufficiency is Sufficiency.STALE:
        readiness = None
    return RecoveryExplanation(
        surface=SURFACE_PROACTIVE,
        zone_items=tuple(zone_items),
        data_state_items=tuple(data_state),
        macro_items=tuple(macro),
        readiness_item=readiness,
        cardio_item=explain_cardio(state),
        data_prompt=_data_prompt(state),
    )


def _data_prompt(state: TrainingState) -> ExplanationItem | None:
    """Invitation à saisir une donnée — jamais une consigne d'entraînement.

    Séparée de l'explication de récupération : c'est le seul impératif autorisé
    par la spec, et il porte sur la **collecte**, pas sur la prescription.
    """
    if state.readiness.overall is not None:
        return None
    return ExplanationItem(
        kind=KIND_DATA_PROMPT,
        message=DATA_PROMPT_MESSAGE,
        is_estimate=False,
    )


# ---------------------------------------------------------------------------
# Tri : une absence de donnée n'est pas une bande
# ---------------------------------------------------------------------------

_BAND_RANK: dict[RecoveryBand, int] = {
    RecoveryBand.LIKELY_FATIGUED: 0,
    RecoveryBand.PARTIALLY_RECOVERED: 1,
    RecoveryBand.LIKELY_AVAILABLE: 2,
}

_CONFIDENCE_RANK: dict[Confidence, int] = {
    Confidence.MEDIUM: 0,
    Confidence.LOW: 1,
}

def recovery_rank_key(item: ExplanationItem) -> tuple[int, int, str]:
    """Clé de tri **d'affichage** pour une explication d'estimation.

    Ordonne des items à l'écran ; ne choisit aucune séance, aucun volume, aucun
    exercice. Elle **refuse** un état de donnée : sans ce refus, un « données
    insuffisantes » se glisserait dans un classement de récupération et serait
    lu comme une bande — l'exacte confusion que cette tranche existe pour
    empêcher.
    """
    if not item.is_estimate:
        raise ValueError(
            "a data-state notice is not rankable as a recovery band"
        )
    confidence = item.confidence or Confidence.NONE
    return (
        _BAND_RANK[item.band],
        _CONFIDENCE_RANK.get(renderable_confidence(confidence), 2),
        item.subject or "",
    )


# ---------------------------------------------------------------------------
# Garde-fou de formulation — sur la sortie rendue (spec §8.4)
# ---------------------------------------------------------------------------

#: Formulations qu'aucune chaîne rendue ne peut contenir. Comparaison en
#: minuscules, sous-chaîne. Étendue au-delà du §8.2 avec le vocabulaire de
#: décision et les champs cardio non individualisés.
FORBIDDEN_RENDERED_WORDING: tuple[str, ...] = (
    # §8.2 — revendications physiologiques
    "physiologiquement récupéré",
    "physiologically recovered",
    "récupération musculaire mesurée",
    "measured muscle recovery",
    "activation mesurée",
    "measured activation",
    "emg",
    "diagnostic",
    "diagnosis",
    "blessure",
    "injury",
    "surentraînement",
    "overtraining",
    "prescription",
    "thérapeutique",
    # langage de décision — cette tranche explique, elle ne prescrit pas
    "tu dois",
    "repose-toi",
    "reposez-vous",
    "augmente la charge",
    "baisse la charge",
    "plus lourd",
    "grosse séance",
    "reporte",
    "ajoute des séries",
    # champs cardio qui n'observent aucune charge individuelle
    "bpm",
    "calorie",
    "kcal",
)

#: Motifs interdits : pourcentages, durées de récupération chiffrées, et toute
#: fuite d'identifiant interne (`snake_case`) depuis un `basis` amont.
FORBIDDEN_RENDERED_PATTERNS: tuple[str, ...] = (
    r"%",
    r"\d+\s*(?:h|heures?|min|minutes?)\b",
    r"\b[a-z]{2,}_[a-z]{2,}\b",
)

_COMPILED_PATTERNS = tuple(
    re.compile(pattern) for pattern in FORBIDDEN_RENDERED_PATTERNS
)


def rendered_strings(explanation: RecoveryExplanation) -> tuple[str, ...]:
    """Toutes les chaînes réellement montrées à l'utilisateur.

    Les codes machine (`subject`) en sont exclus : ils ne sont pas affichés, et
    `delt_lat` déclencherait à tort le motif anti-fuite.
    """
    strings: list[str] = []
    for item in explanation.all_items():
        strings.append(item.message)
        if item.subject_label is not None:
            strings.append(item.subject_label)
        if item.confidence_label is not None:
            strings.append(item.confidence_label)
        strings.extend(item.reasons)
    return tuple(strings)


def wording_violations(strings: tuple[str, ...]) -> tuple[tuple[str, str], ...]:
    """`(chaîne fautive, motif déclencheur)` pour chaque violation trouvée."""
    violations: list[tuple[str, str]] = []
    for text in strings:
        lowered = text.lower()
        for term in FORBIDDEN_RENDERED_WORDING:
            if term in lowered:
                violations.append((text, term))
        for pattern in _COMPILED_PATTERNS:
            if pattern.search(lowered):
                violations.append((text, pattern.pattern))
    return tuple(violations)


__all__ = [
    "BAND_MESSAGES",
    "CONFIDENCE_LABELS",
    "EXPLAINER_VERSION",
    "ExplanationItem",
    "FORBIDDEN_RENDERED_PATTERNS",
    "FORBIDDEN_RENDERED_WORDING",
    "INSUFFICIENT_DATA_LABEL",
    "MAX_RENDERABLE_CONFIDENCE",
    "RecoveryExplanation",
    "SURFACE_DETAILED",
    "SURFACE_PROACTIVE",
    "build_detailed_explanation",
    "build_proactive_explanation",
    "confidence_label",
    "explain_axis",
    "explain_cardio",
    "explain_readiness",
    "explain_zone",
    "recovery_rank_key",
    "rendered_strings",
    "wording_violations",
]
