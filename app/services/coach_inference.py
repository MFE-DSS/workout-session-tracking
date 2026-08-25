"""Sb_23 — Coach Report inference (blocs 7 et 8) + couverture et références.

Jeu de règles déterministe. Aucun apprentissage, aucune probabilité — des
conditions entièrement explicables.

Contrat Sx_23 v1.1 §B.bis :
* Vocabulaire borné — jamais « tu es X », toujours « X probable ».
* Aucune appréciation esthétique, aucun pronostic morphologique.
* Aucun verdict de performance, aucune comparaison entre utilisateurs.

`TRAIN1-D` / C1 — LE BLOC 9 « AXES DE TRAVAIL SUGGÉRÉS » EST RETIRÉ
--------------------------------------------------------------------
Il produisait cinq prescriptions d'entraînement que rien dans le dépôt ne
soutient :

    « Rééquilibrer X : viser 2 séances/sem sur 4 semaines »
    « Augmenter le volume cardio : … cible OMS 150'/sem »
    « Diversifier les patterns moteurs : intégrer plus de variétés »
    « Augmenter la fréquence : viser 2-3 séances/sem comme socle »
    « Logger le poids de corps plus systématiquement — indispensable … »

Les quatre premières fixent des **objectifs chiffrés** (2 séances/sem, 4
semaines, 150'/sem, 2-3 séances/sem) qu'aucune source du dépôt ne justifie —
la même faute que le « % de cible » retiré de `/physique` par `TRAIN1-C`, mais
en phrases.

CE QU'ELLES DEVIENNENT (ordre opérateur : *factual signals, or removed*) :

* **Retirées** — les quatre prescriptions de volume, de fréquence et
  d'équilibrage. Les FAITS sur lesquels elles reposaient restent tous à
  l'écran : le bloc 2 dit le volume, le bloc 4 la répartition par zone, le
  bloc 5 les patterns. Rien n'est perdu ; seule la consigne disparaît.
* **Converties en couverture** — la discipline de logging n'est pas une règle
  d'entraînement mais un fait sur la **complétude des données**. Elle devient
  `coverage_gaps`, sur l'axe `COVERAGE` du modèle épistémique canonique.
* **Conservée comme RÉFÉRENCE** — la recommandation de l'OMS. Une
  recommandation de santé publique est une référence légitime ; ce qui ne
  l'était pas, c'est de la convertir en **cible individuelle calculée** pour
  quelqu'un dont le produit ignore l'âge, l'état de santé et le contexte.
  Elle est donc citée, attribuée, et explicitement détachée du cas personnel.

Les blocs 7 et 8 (points forts / faibles **probables**) restent : ce sont des
inférences, pas des prescriptions, et l'ordre opérateur demande de préserver la
provenance mesuré / inféré, pas de la supprimer.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.services.coach_report import CoachReport
from app.services.muscle_mapping import RADAR_AXES

# Seuils — V1 déterministes. Ce sont des CHOIX DE PRODUIT, et c'est
# exactement pourquoi ce qu'ils produisent est étiqueté `INFERRED` et non
# `DERIVED` : un comptage est reproductible, un seuil est une décision.
TOP_ZONE_MIN_SESSIONS = 3        # ≥ 3 séances/30 j → point fort probable
NEGLECTED_ZONE_MAX_SESSIONS = 1  # ≤ 1 séance/30 j → point faible probable
DISCIPLINE_WEAK_THRESHOLD = 50   # < 50 % → lacune de couverture signalée

#: `TRAIN1-D` / C1 — RÉFÉRENCE EXTERNE, JAMAIS UNE CIBLE INDIVIDUELLE.
#:
#: 150 min/semaine d'activité d'endurance est une recommandation de santé
#: publique de l'OMS, adressée à une population adulte générale. Le produit
#: ignore l'âge, l'état de santé, les traitements et le contexte de la personne
#: qui lit l'écran : il n'a rien qui lui permette de convertir cette
#: recommandation en objectif calculé pour elle.
#:
#: Elle est donc citée comme référence attribuée, et détachée du cas personnel.
#: La version précédente écrivait « cible OMS 150'/sem » à côté du volume réel,
#: ce qui en faisait un écart à combler.
OMS_ENDURANCE_MIN_PER_WEEK = 150


@dataclass(frozen=True)
class InferredBlocks:
    """Les blocs non factuels du rapport.

    `strong_points` / `weak_points` — INFÉRÉS. Phrases bornées, toujours
    qualifiées « probable », jamais assertives.

    `coverage_gaps` — FACTUELS, sur l'axe COUVERTURE : ce que les données ne
    couvrent pas. Aucune consigne, aucun objectif.

    `external_references` — RÉFÉRENCES attribuées. Ni cibles, ni écarts.
    """
    strong_points: list[str]
    weak_points: list[str]
    coverage_gaps: list[str]
    external_references: list[str]


def _axis_label(key: str) -> str:
    return RADAR_AXES.get(key, {}).get("label", key)


def strong_points(report: CoachReport) -> list[str]:
    """Rule : a zone is a "probable strength point" if it appears in
    top_zones with ≥ TOP_ZONE_MIN_SESSIONS over 30d. Capped to 2 lines."""
    out: list[str] = []
    for _key, label, n in report.zones.top_zones:
        if n >= TOP_ZONE_MIN_SESSIONS:
            # `TRAIN1-D` / C10 — les astérisques Markdown ont disparu. Elles
            # s'affichaient littéralement : « **Dos épaisseur** ». Le gabarit
            # ne rend pas de Markdown, et il n'a pas à le faire — c'est au
            # producteur de rendre du texte, pas du balisage.
            out.append(
                f"Zone travaillée fréquemment : {label} "
                f"({n} séances/30j) — point fort probable"
            )
        if len(out) >= 2:
            break
    return out


def weak_points(report: CoachReport) -> list[str]:
    """Rule : a zone with ≤ NEGLECTED_ZONE_MAX_SESSIONS over 30d
    surfaces as a probable weak point. Capped to 2 lines."""
    out: list[str] = []
    for _key, label, n in report.zones.neglected_zones:
        if n <= NEGLECTED_ZONE_MAX_SESSIONS:
            out.append(
                f"Zone peu travaillée : {label} "
                f"({n} séance{'s' if n != 1 else ''}/30j) — point faible probable"
            )
        if len(out) >= 2:
            break
    return out


def coverage_gaps(report: CoachReport) -> list[str]:
    """Ce que les données ne couvrent pas — des FAITS, aucune consigne.

    Remplace la « discipline reminder » du bloc 9, qui disait « Logger le poids
    de corps plus systématiquement — indispensable pour suivre le trend ».
    Deux problèmes dans une seule phrase : un impératif, et une affirmation
    (« indispensable ») que rien n'établit.

    Ce qui reste est le fait : sur quelle proportion des séances la donnée est
    présente. Un lecteur en tire ce qu'il veut ; le produit ne le lui dit pas.
    """
    out: list[str] = []
    disc = report.discipline
    for rate, what in (
        (disc.with_bodyweight_rate, "Poids de corps"),
        (disc.with_free_note_rate, "Note libre"),
        (disc.with_sensation_rate, "Sensation musculaire"),
    ):
        if rate is not None and rate < DISCIPLINE_WEAK_THRESHOLD:
            out.append(f"{what} : renseigné sur {rate}% des séances (30 j)")
    return out


def external_references(report: CoachReport) -> list[str]:
    """Références externes attribuées — jamais des cibles individuelles.

    La recommandation de l'OMS n'est pas retirée : c'est une référence de santé
    publique légitime, et un rapport destiné à un tiers a des raisons de la
    citer. Ce qui est retiré, c'est sa conversion en objectif calculé pour une
    personne dont le produit ignore l'âge, l'état de santé et le contexte.

    Rendue **inconditionnellement** dès qu'il y a du cardio à situer : une
    référence qui n'apparaît que lorsqu'on est « en dessous » n'est pas une
    référence, c'est un reproche déclenché par un seuil.
    """
    if report.volume.cardio_minutes_per_week < 0:
        return []
    return [
        f"OMS — {OMS_ENDURANCE_MIN_PER_WEEK} min d'activité d'endurance par "
        "semaine, recommandation de santé publique pour une population adulte "
        "générale. AUREN ne connaît ni ton âge ni ton état de santé : ce "
        "nombre n'est pas un objectif calculé pour toi."
    ]


def build_inference(report: CoachReport) -> InferredBlocks:
    return InferredBlocks(
        strong_points=strong_points(report),
        weak_points=weak_points(report),
        coverage_gaps=coverage_gaps(report),
        external_references=external_references(report),
    )
