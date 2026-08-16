"""Sb_MORPHO_PROFILE_RUNTIME_01 — adaptateur entre les mesures persistées et le
moteur pur `morphology_profile`.

Ce module **n'a aucune science**. Le moteur reste seul juge des seuils, des
descripteurs et des refus ; ce fichier se contente de lui présenter, sous la
forme qu'il déclare attendre, ce que la base contient réellement — et de dire
d'où vient chaque valeur.

Trois propriétés portent tout le reste :

**1. Un fait absent reste absent.** Aucune valeur de remplacement, aucune
moyenne de population, aucune estimation depuis une mesure voisine. `None`
traverse l'adaptateur intact et le moteur baisse sa confiance en conséquence
(`Sx_MORPHO_CAPTURE_01_SPEC` §6).

**2. Chaque fait porte sa provenance.** Les champs sont lus indépendamment les
uns des autres : le tour de taille peut venir de la mesure de mardi et le tour
de poitrine de celle du mois dernier. C'est un profil de **derniers faits
connus**, pas un instantané anthropométrique. L'adaptateur le dit explicitement
(`profile_kind`) au lieu de laisser un consommateur croire à une simultanéité
qui n'existe pas.

**3. La réduction latérale est une convention, pas une physiologie.** Moyenne
des deux côtés quand les deux existent, sinon le côté disponible. Elle est
nommée, versionnée, et exposée dans le `basis`. L'écart gauche/droite n'est
jamais interprété : le lire comme un déséquilibre serait un diagnostic postural,
interdit par le §5 de la spec.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.measurement import BodyMeasurement
from app.models.user import User
from app.services.morphology_profile import MorphologyFacts

# Version de la convention d'agrégation latérale. Toute évolution de la règle
# (moyenne → autre chose) doit incrémenter cette valeur : un consommateur qui
# compare deux profils dans le temps doit pouvoir voir que la règle a changé.
LATERAL_REDUCTION_CONVENTION_VERSION = "lateral-mean-v1"

MORPHOLOGY_RUNTIME_VERSION = 1

# Provenance : d'où vient physiquement la valeur.
SOURCE_MEASUREMENT = "persisted_user_measurement"
SOURCE_USER_PROFILE = "persisted_user_profile"

# Nature temporelle du profil assemblé.
PROFILE_EMPTY = "empty"
PROFILE_SINGLE_MEASUREMENT = "single_measurement"
PROFILE_LATEST_KNOWN_FACTS = "latest_known_facts"

# Bases de réduction latérale, exposées telles quelles au consommateur.
BASIS_BILATERAL_MEAN = "left+right mean"
BASIS_SINGLE_SIDE_LEFT = "single-side fallback (left)"
BASIS_SINGLE_SIDE_RIGHT = "single-side fallback (right)"
BASIS_DIRECT = "direct measurement"
BASIS_LEGACY_CALF = "legacy calf_cm fallback"
BASIS_USER_PROFILE_HEIGHT = "user profile height"

# Garde-fou de formulation, vérifié par test. L'adaptateur agrège ; il ne
# diagnostique pas, et l'asymétrie gauche/droite n'est pas une interprétation.
AGGREGATION_GUARD = (
    "La réduction latérale est une convention d'agrégation versionnée. "
    "Elle decrit comment deux nombres deviennent un, et rien de plus : "
    "aucune lecture de symetrie, de posture ni d'equilibre n'en decoule."
)


@dataclass(frozen=True)
class FactProvenance:
    """D'où vient une valeur, et comment elle a été obtenue."""

    field: str
    value: float
    source: str
    basis: str
    measurement_id: int | None = None
    measured_at: datetime | None = None


@dataclass(frozen=True)
class MorphologyFactsBundle:
    """`MorphologyFacts` prêt pour le moteur + la traçabilité qui l'accompagne."""

    facts: MorphologyFacts
    provenance: tuple[FactProvenance, ...]
    profile_kind: str
    measurement_dates: tuple[datetime, ...]
    lateral_convention_version: str = LATERAL_REDUCTION_CONVENTION_VERSION
    runtime_version: int = MORPHOLOGY_RUNTIME_VERSION

    @property
    def is_mixed_date(self) -> bool:
        """Vrai si les faits mesurés proviennent de plusieurs dates."""
        return self.profile_kind == PROFILE_LATEST_KNOWN_FACTS

    def provenance_for(self, field: str) -> FactProvenance | None:
        for p in self.provenance:
            if p.field == field:
                return p
        return None


def _measurements(
    db: Session, user_id: int, as_of: datetime | None
) -> list[BodyMeasurement]:
    """Mesures du propriétaire, les plus récentes d'abord.

    Scopé par `user_id` : une mesure d'un autre utilisateur n'est pas
    « refusée », elle est **introuvable** (spec §7).
    """
    stmt = select(BodyMeasurement).where(BodyMeasurement.user_id == user_id)
    if as_of is not None:
        stmt = stmt.where(BodyMeasurement.measured_at <= as_of)
    return list(
        db.execute(
            stmt.order_by(
                BodyMeasurement.measured_at.desc(), BodyMeasurement.id.desc()
            )
        ).scalars().all()
    )


def _latest_non_null(
    rows: list[BodyMeasurement], field: str
) -> tuple[float, BodyMeasurement] | None:
    """Première valeur non nulle en parcourant du plus récent au plus ancien.

    Chaque champ est résolu **indépendamment** : c'est ce qui produit un profil
    de derniers faits connus plutôt qu'un instantané, et c'est exactement ce que
    `profile_kind` sert à signaler.
    """
    for row in rows:
        value = getattr(row, field, None)
        if value is not None:
            return float(value), row
    return None


def _lateral(
    rows: list[BodyMeasurement], left_field: str, right_field: str
) -> tuple[float, BodyMeasurement, str] | None:
    """Réduction latérale sur la mesure la plus récente qui porte un côté.

    Les deux côtés doivent venir de la **même ligne** : moyenner la cuisse
    gauche de mardi avec la droite de janvier fabriquerait une valeur qui n'a
    jamais été mesurée. Si la ligne la plus récente ne porte qu'un côté, ce côté
    est utilisé seul, et le `basis` le dit.
    """
    for row in rows:
        left = getattr(row, left_field, None)
        right = getattr(row, right_field, None)
        if left is not None and right is not None:
            return (float(left) + float(right)) / 2, row, BASIS_BILATERAL_MEAN
        if left is not None:
            return float(left), row, BASIS_SINGLE_SIDE_LEFT
        if right is not None:
            return float(right), row, BASIS_SINGLE_SIDE_RIGHT
    return None


def build_morphology_facts(
    db: Session, user_id: int, *, as_of: datetime | None = None
) -> MorphologyFactsBundle:
    """Assemble les derniers faits connus du propriétaire pour le moteur pur.

    `as_of` borne la lecture dans le passé (rejouer un profil tel qu'il était).
    Les faits sont lus champ par champ ; aucun trou n'est comblé.

    `focus_candidates` reste **vide**. Les priorités déclarées de
    `TrainingPreferences` ne sont délibérément pas injectées ici : une priorité
    déclarée par l'utilisateur et un candidat inféré par le moteur sont deux
    sources distinctes, et les confondre en entrée rendrait la distinction
    irrécupérable en sortie (spec §8.7).

    `observations` reste vide également : aucune surface ne capture le
    vocabulaire d'observations, et en inventer depuis des nombres serait
    exactement l'inférence que le §5 interdit. Le moteur produira donc des
    descripteurs à confiance structurellement réduite — c'est une limite
    connue, pas un oubli.
    """
    rows = _measurements(db, user_id, as_of)

    provenance: list[FactProvenance] = []
    values: dict[str, float | None] = {}

    def _record(
        field: str, resolved, basis: str
    ) -> None:
        if resolved is None:
            values[field] = None
            return
        value, row = resolved
        values[field] = value
        provenance.append(
            FactProvenance(
                field=field,
                value=value,
                source=SOURCE_MEASUREMENT,
                basis=basis,
                measurement_id=row.id,
                measured_at=row.measured_at,
            )
        )

    for field in ("wingspan_cm", "waist_cm", "chest_cm"):
        _record(field, _latest_non_null(rows, field), BASIS_DIRECT)

    thigh = _lateral(rows, "thigh_cm_left", "thigh_cm_right")
    if thigh is None:
        values["thigh_cm"] = None
    else:
        value, row, basis = thigh
        values["thigh_cm"] = value
        provenance.append(
            FactProvenance(
                field="thigh_cm", value=value, source=SOURCE_MEASUREMENT,
                basis=basis, measurement_id=row.id, measured_at=row.measured_at,
            )
        )

    # Précédence de lecture du mollet : latéralisé d'abord, colonne héritée
    # ensuite. La colonne héritée est lue, jamais écrite, jamais migrée
    # (spec §4.4) — elle vieillit en restant lisible.
    calf = _lateral(rows, "calf_cm_left", "calf_cm_right")
    if calf is not None:
        value, row, basis = calf
        values["calf_cm"] = value
        provenance.append(
            FactProvenance(
                field="calf_cm", value=value, source=SOURCE_MEASUREMENT,
                basis=basis, measurement_id=row.id, measured_at=row.measured_at,
            )
        )
    else:
        _record("calf_cm", _latest_non_null(rows, "calf_cm"), BASIS_LEGACY_CALF)

    # La taille vit sur `User`, pas sur la mesure : une seconde copie
    # divergerait (spec §4.2). Elle est donc datée par le profil, pas par une
    # ligne de mesure — d'où `measurement_id=None`.
    height = db.execute(
        select(User.height_cm).where(User.id == user_id)
    ).scalar_one_or_none()
    if height is not None:
        provenance.append(
            FactProvenance(
                field="height_cm", value=float(height),
                source=SOURCE_USER_PROFILE, basis=BASIS_USER_PROFILE_HEIGHT,
            )
        )

    dated = tuple(
        sorted({p.measured_at for p in provenance if p.measured_at is not None})
    )
    ids = {p.measurement_id for p in provenance if p.measurement_id is not None}
    if not ids:
        profile_kind = PROFILE_EMPTY
    elif len(ids) == 1:
        profile_kind = PROFILE_SINGLE_MEASUREMENT
    else:
        profile_kind = PROFILE_LATEST_KNOWN_FACTS

    facts = MorphologyFacts(
        height_cm=float(height) if height is not None else None,
        wingspan_cm=values.get("wingspan_cm"),
        # Jamais stocké, jamais pré-calculé ici : le moteur dérive l'ape index
        # de `wingspan - height` quand les deux existent, et refuse sinon.
        ape_index_cm=None,
        waist_cm=values.get("waist_cm"),
        chest_cm=values.get("chest_cm"),
        thigh_cm=values.get("thigh_cm"),
        calf_cm=values.get("calf_cm"),
        observations=(),
        focus_candidates=(),
        source=SOURCE_MEASUREMENT,
    )

    return MorphologyFactsBundle(
        facts=facts,
        provenance=tuple(provenance),
        profile_kind=profile_kind,
        measurement_dates=dated,
    )
