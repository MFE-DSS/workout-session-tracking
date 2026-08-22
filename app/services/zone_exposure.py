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
from app.services.exercise_zone_resolver import SOURCE_DB, resolve_zone
from app.services.muscle_mapping import ZONE_LABELS

#: Même fenêtre que `progress_facts`. Le dire ici plutôt que de l'importer
#: garde les deux modules indépendants ; une garde vérifie qu'ils s'accordent.
WINDOW_DAYS = 14

STATE_KNOWN = "known"
STATE_ZERO = "zero"
#: `MUSCLE_MAPPING_TRUTH_01` — la fenêtre contient **à la fois** des exercices
#: attribuables et des exercices qui ne le sont pas.
#:
#: L'état manquant, et le plus important. Sans lui, une séance dont un exercice
#: n'était pas reconnu rendait `known` : « 2 zones touchées » et neuf lignes à
#: `0`, sans signaler l'échec d'attribution. Mesuré en contrôlé avant
#: correction — **9 zéros fabriqués sur 11 zones**.
#:
#: RÈGLE SÉMANTIQUE : en `partial`, une preuve non attribuée rend les zones
#: non observées **INCONNUES, pas nulles**. On ne sait pas ce que l'exercice
#: manquant a touché, donc **n'importe quelle** zone a pu l'être. Les comptages
#: positifs restent exposables comme des **minima observés** — ils sont vrais,
#: simplement pas exhaustifs.
STATE_PARTIAL = "partial"
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
    #:
    #: En `partial`, ces comptages sont des **minima observés** : vrais, mais
    #: non exhaustifs. Un zéro n'y signifie pas « pas travaillé ».
    counts: dict[str, int] = field(default_factory=dict)
    sessions: int = 0

    #: Exercices que ni la base ni le matcher n'ont su attribuer. C'est ce
    #: nombre qui fait basculer en `partial`, et il est **rendu à l'écran** :
    #: taire la donnée manquante serait la même faute que la compter pour zéro.
    unmapped_exercises: int = 0

    #: Combien de résolutions viennent de l'autorité cible plutôt que du repli.
    #: Non rendu — instrument de mesure de la migration.
    resolved_db: int = 0
    resolved_legacy: int = 0

    @property
    def touched(self) -> int:
        return sum(1 for n in self.counts.values() if n)


@dataclass
class _Tally:
    """Dépouillement brut de la fenêtre — sans aucune décision d'état.

    Extrait de `build_zone_exposure` pour la même raison que `_occupant` et
    `_day_traces` l'ont été de `progress_facts` : la boucle imbriquée qui
    compte et la cascade qui arbitre l'état sont deux lectures différentes, et
    les tenir dans une seule fonction coûtait 22 de complexité cognitive pour
    15 permis (`python:S3776`).
    """

    counts: dict[str, int]
    exercises: int = 0
    classified: int = 0
    unmapped: int = 0
    resolved_db: int = 0
    resolved_legacy: int = 0


def _tally(db: Session, sessions) -> _Tally:
    """Une séance compte **au plus une fois par zone** — d'où le `set` par
    séance : la question est « ce jour-là, oui ou non », pas « combien ».
    """
    t = _Tally(counts=dict.fromkeys(ZONE_LABELS, 0))
    for s in sessions:
        zones: set[str] = set()
        for se in s.session_exercises:
            t.exercises += 1
            res = resolve_zone(
                db, se.substituted_name or se.exercise_name_snapshot or "")
            if not res.mapped:
                t.unmapped += 1
                continue
            t.classified += 1
            zones.add(res.zone)
            if res.source == SOURCE_DB:
                t.resolved_db += 1
            else:
                t.resolved_legacy += 1
        for z in zones:
            t.counts[z] += 1
    return t


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

    t = _tally(db, sessions)
    common = {"sessions": len(sessions), "unmapped_exercises": t.unmapped,
              "resolved_db": t.resolved_db,
              "resolved_legacy": t.resolved_legacy}

    # Des exercices existent mais AUCUN n'est attribuable : l'attribution est
    # impossible, pas nulle. Un compte dont tous les exercices sont inconnus
    # n'a pas « travaillé zéro zone » — on ne sait simplement pas lesquelles.
    if t.exercises and not t.classified:
        return ZoneExposure(state=STATE_UNKNOWN, **common)

    # `PARTIAL` — les deux natures de preuve coexistent dans la fenêtre.
    #
    # Les comptages positifs restent VRAIS : ces zones ont bien été touchées.
    # Ce qui devient faux, c'est le reste — on ignore ce que l'exercice non
    # attribué a sollicité, donc **aucune** zone à zéro ne peut être affirmée.
    # Les `counts` sont donc des MINIMA OBSERVÉS, et la vue-modèle a
    # l'interdiction d'en rendre les zéros.
    if t.classified and t.unmapped:
        return ZoneExposure(state=STATE_PARTIAL, counts=t.counts, **common)

    # Des séances sans aucun exercice — du cardio, typiquement — ont bel et
    # bien touché zéro zone de force. C'est un fait, pas une ignorance.
    state = STATE_KNOWN if t.classified else STATE_ZERO
    return ZoneExposure(state=state, counts=t.counts, **common)


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

    # `PARTIAL` — une preuve non attribuée rend TOUT le reste inconnu.
    #
    # On ignore ce que l'exercice manquant a touché, donc n'importe quelle zone
    # a pu l'être. Le fond neutre devient donc `unknown`, jamais `zero` : sur
    # la silhouette comme dans les lignes, une zone non observée ne peut plus
    # être affirmée vide. Les zones observées restent affirmées — elles sont
    # vraies, simplement non exhaustives.
    base = "unknown" if exp.state == STATE_PARTIAL else "zero"
    regions = dict.fromkeys(set(ZONE_TO_REGION.values()), base)
    for zone, n in exp.counts.items():
        if n:
            regions[ZONE_TO_REGION[zone]] = "on"

    if exp.state == STATE_PARTIAL:
        # ⚠ AUCUNE LIGNE À ZÉRO. Le niveau 2 n'expose que les zones
        # OBSERVÉES ; rendre les autres à `0` fabriquerait exactement le
        # mensonge que cet état existe pour empêcher.
        rows = [(ZONE_LABELS[z], exp.counts[z]) for z in ZONE_LABELS
                if exp.counts.get(z)]
        hit = ", ".join(f"{lab} {n}" for lab, n in rows)
        return {
            "state": STATE_PARTIAL, "regions": regions, "rows": rows,
            "touched": exp.touched, "unmapped": exp.unmapped_exercises,
            "sr": (f"Exposition des quatorze derniers jours : partielle. "
                   f"{exp.touched} zones identifiées — {hit}. "
                   f"{exp.unmapped_exercises} exercice"
                   f"{'s' if exp.unmapped_exercises > 1 else ''} non attribué"
                   f"{'s' if exp.unmapped_exercises > 1 else ''} : les autres "
                   f"zones sont inconnues, pas à zéro."),
        }

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
    "STATE_PARTIAL",
    "WINDOW_DAYS",
    "ZONE_TO_REGION",
    "ZoneExposure",
    "build_zone_exposure",
    "build_zone_exposure_view",
]
