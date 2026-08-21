"""Exposition musculaire factuelle sur la fenêtre de Progression (`UX4_03D`).

UNE SEULE QUESTION
    « Où ai-je travaillé pendant les mêmes quatorze jours ? »

La fenêtre est celle de `progress_facts` — deux instruments côte à côte sur des
fenêtres différentes rouvriraient la contradiction que l'écrémage a fermée.

CE QUE CE MODULE NE DIRA JAMAIS
    sous-entraîné · sur-entraîné · optimal · % de cible · N / cible séries
    aucune revendication d'activation physiologique
Tous supposent une CIBLE. Le dépôt ne produit que des bandes de
**planification** (`weekly_volume_budget`), dont l'en-tête précise qu'« aucune
littérature n'est invoquée » pour justifier ses bornes.

POURQUOI CE COMPTAGE N'EST PAS CELUI DE `profile_metrics`
----------------------------------------------------------
`_zone_session_counts` projette sur les **six axes radar** et documente sa
propre perte : « zone with no radar axis (``core``) or unclassified
(``unknown``). Dropped rather than forced onto an arbitrary axis. »

`core` est pourtant l'une des **onze zones canoniques**. Compter au niveau
détaillé n'est donc pas une approximation du comptage existant : c'est le
comptage **plus fidèle**, celui qui ne perd pas une zone en route.

TROIS ÉTATS, ET LES CONFONDRE MENTIRAIT
----------------------------------------
``known``    des séances existent et au moins un exercice est classable
``zero``     des séances existent, aucune n'a touché les onze zones — le cas
             d'un compte qui n'a fait que du cardio. C'est un FAIT.
``unknown``  soit aucune séance, soit des exercices qu'aucun motif ne reconnaît
             — AUREN ne peut rien attribuer. C'est une ABSENCE DE PREUVE.

Rendre `unknown` comme un zéro ferait passer une ignorance pour une mesure.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.session import WorkoutSession
from app.services.muscle_mapping import ZONE_LABELS, classify_exercise

#: Même fenêtre que `progress_facts`. Le dire ici plutôt que de l'importer
#: garde les deux modules indépendants ; une garde vérifie qu'ils s'accordent.
WINDOW_DAYS = 14

STATE_KNOWN = "known"
STATE_ZERO = "zero"
STATE_UNKNOWN = "unknown"

#: 11 zones canoniques → 6 macro-régions de la silhouette.
#:
#: ⚠ Cette table **duplique** celle de `_partials/worked_area_body_map.html`,
#: où elle vit inline en Jinja. La sortir du gabarit reviendrait à modifier une
#: surface partagée par la carte d'exercice — hors périmètre de cette tranche.
#: Le doublon est donc assumé et **gardé** : un test compare les deux et rougit
#: si l'une dérive. Un doublon surveillé vaut mieux qu'un refactor non demandé
#: sur un gabarit qu'aucune mesure de cette tranche ne couvre.
ZONE_TO_REGION: dict[str, str] = {
    "pecs": "chest",
    "delt_lat": "shoulders", "delt_post": "shoulders",
    "lats": "back", "upper_back": "back",
    "biceps": "arms", "triceps": "arms",
    "quads": "legs", "posterior": "legs", "calves": "legs",
    "core": "core",
}


@dataclass(frozen=True)
class ZoneExposure:
    """Faits d'exposition. **Aucune cible, aucun score, aucune bande.**"""

    state: str = STATE_UNKNOWN
    #: zone canonique → nombre de séances l'ayant touchée. Une séance compte
    #: au plus une fois par zone, même si elle contient trois exercices qui la
    #: sollicitent : la question est « ce jour-là, oui ou non », pas « combien ».
    counts: dict[str, int] = field(default_factory=dict)
    sessions: int = 0

    @property
    def touched(self) -> int:
        return sum(1 for n in self.counts.values() if n)


def build_zone_exposure(
    db: Session, user_id: int, *, now: datetime | None = None
) -> ZoneExposure:
    """Lecture seule, déterministe. Une requête."""
    now = now or datetime.now(UTC)
    window_start = now - timedelta(days=WINDOW_DAYS)

    sessions = db.execute(
        select(WorkoutSession)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == "completed",
            WorkoutSession.excluded_from_stats.is_(False),
            WorkoutSession.started_at >= window_start,
        )
        .options(selectinload(WorkoutSession.session_exercises))
    ).scalars().all()

    if not sessions:
        return ZoneExposure(state=STATE_UNKNOWN)

    counts = dict.fromkeys(ZONE_LABELS, 0)
    exercises = 0
    classified = 0
    for s in sessions:
        zones: set[str] = set()
        for se in s.session_exercises:
            exercises += 1
            primary, _ = classify_exercise(
                se.substituted_name or se.exercise_name_snapshot or ""
            )
            if primary in counts:
                classified += 1
                zones.add(primary)
        for z in zones:
            counts[z] += 1

    # Des exercices existent mais AUCUN n'est reconnu : l'attribution est
    # impossible, pas nulle. Un compte dont tous les exercices sont inconnus
    # n'a pas « travaillé zéro zone » — on ne sait simplement pas lesquelles.
    if exercises and not classified:
        return ZoneExposure(state=STATE_UNKNOWN, sessions=len(sessions))

    # Des séances sans aucun exercice — du cardio, typiquement — ont bel et
    # bien touché zéro zone de force. C'est un fait, pas une ignorance.
    state = STATE_KNOWN if classified else STATE_ZERO
    return ZoneExposure(state=state, counts=counts, sessions=len(sessions))


def build_zone_exposure_view(exp: ZoneExposure) -> dict:
    """Vue-modèle. **Ne calcule rien** : elle projette et met en forme.

    `rows` n'est rendu que dans l'état `known`, et c'est une décision, pas un
    oubli : **une affordance de détail n'existe que si le niveau suivant
    contient une information supplémentaire.** Onze lignes disant chacune `0`
    n'en contiennent aucune, et « 0 zone touchée » répond déjà entièrement à
    la question posée.
    """
    if exp.state == STATE_UNKNOWN:
        return {
            "state": STATE_UNKNOWN,
            "regions": dict.fromkeys(set(ZONE_TO_REGION.values()), "unknown"),
            "rows": [],
            "sr": ("Exposition des quatorze derniers jours : inconnue. "
                   "Aucune séance exploitable sur la fenêtre — ce n'est pas "
                   "zéro séance par zone, c'est une absence de preuve."),
        }

    regions = dict.fromkeys(set(ZONE_TO_REGION.values()), "zero")
    for zone, n in exp.counts.items():
        if n:
            regions[ZONE_TO_REGION[zone]] = "on"

    if exp.state == STATE_ZERO or not exp.touched:
        return {
            "state": STATE_ZERO, "regions": regions, "rows": [],
            "sr": ("Exposition des quatorze derniers jours : aucune zone "
                   "touchée. Les séances de la fenêtre n'ont porté sur aucune "
                   "des onze zones suivies."),
        }

    rows = [(ZONE_LABELS[z], exp.counts.get(z, 0)) for z in ZONE_LABELS]
    hit = ", ".join(f"{lab} {n}" for lab, n in rows if n)
    idle = ", ".join(lab for lab, n in rows if not n)
    return {
        "state": STATE_KNOWN, "regions": regions, "rows": rows,
        "touched": exp.touched,
        "sr": (f"Exposition des quatorze derniers jours : {exp.touched} zones "
               f"touchées — {hit}."
               + (f" Zones à zéro séance : {idle}." if idle else "")),
    }


__all__ = [
    "STATE_KNOWN",
    "STATE_UNKNOWN",
    "STATE_ZERO",
    "WINDOW_DAYS",
    "ZONE_TO_REGION",
    "ZoneExposure",
    "build_zone_exposure",
    "build_zone_exposure_view",
]
