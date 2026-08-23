"""Les FAITS de séance dont la surface Progression a besoin (`UX4_03B`).

POURQUOI CE MODULE EXISTE PLUTÔT QUE CINQ CHAMPS DANS `behavioral`
-------------------------------------------------------------------
La première version de cette tranche ajoutait ces valeurs à `BehavioralState`.
C'était tentant : le moteur les calcule déjà, puis les **jette** pour ne garder
que les scores qui en dérivent.

`test_no_decision_engine_was_touched` a rougi, et elle avait raison.

Depuis `e8614bd`, trois moteurs de décision sont **gelés** — `substitution`,
`recommendation`, `behavioral` — au nom d'un invariant simple :
**la présentation ne décide de rien.** `UX4_03B` est une tranche de
présentation. Faire grossir un moteur gelé pour qu'une surface soit servie
inverse exactement la dépendance que ce gel protège, et l'argument « ce n'est
qu'additif » est celui que la garde existe pour refuser : un champ additif
aujourd'hui est une lecture couplée demain.

Le gel était intact sur la canonique — vérifié, `git diff e8614bd` vide sur les
trois fichiers. L'échec ne venait que de cette tranche.

CE QUE CE MODULE PRODUIT, ET CE QU'IL NE PRODUIT PAS
------------------------------------------------------
Des **faits** : des comptages de séances et une déclaration recopiée. Aucun
score, aucun seuil, aucune interprétation. L'audit `UX4_03A` a montré que les
trois interprétations que le moteur produit sur ces mêmes faits ne sont pas
présentables telles quelles :

    min(100, n / 14 × 100)   pose UNE SÉANCE PAR JOUR comme le 100 %,
                             donc rend « 21/100 » pour un rythme sain
    compute_trend(0, 0)      rend « stable » à qui n'a jamais rien enregistré
    fatigue par défaut       rend 45,0 pour une ABSENCE de déclaration

La surface lit donc les faits, et les rend tels quels.

SUR LA DUPLICATION DU FILTRE D'ÉLIGIBILITÉ
--------------------------------------------
« séance terminée, non exclue des stats » est déjà écrit deux fois dans le
dépôt (`behavioral`, `profile_metrics`). Ce module en fait une troisième.
C'est assumé plutôt que masqué : la seule alternative sans toucher au moteur
gelé serait d'importer un helper **privé** d'un autre module, ce qui échange
une duplication visible contre un couplage invisible.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.session import WorkoutSession
from app.models.user import User


def _offset(started_at: datetime, now: datetime) -> int:
    """Index de la trace, 0 = le plus ancien jour de la fenêtre.

    ⚠ SQLite rend des datetimes NAÏFS même pour une colonne déclarée
    `DateTime(timezone=True)`. Comparer directement à un `now` conscient lève
    un `TypeError` — c'est arrivé, et seuls les tests qui rendaient la page
    l'avaient attrapé. On normalise donc avant de soustraire.
    """
    if started_at.tzinfo is None:
        started_at = started_at.replace(tzinfo=now.tzinfo)
    return WINDOW_DAYS - 1 - (now.date() - started_at.date()).days

#: Fenêtre de comptage, en jours. Deux semaines : c'est la fenêtre que le
#: produit utilise déjà partout ailleurs pour parler de rythme récent.
WINDOW_DAYS = 14

#: Demi-fenêtre pour la cadence — les sept derniers jours contre les sept
#: précédents.
HALF_WINDOW_DAYS = 7

#: Profondeur du balayage de déclarations. Identique à celle du moteur : on ne
#: change pas la sémantique de « la dernière déclaration » en passant d'un
#: producteur à l'autre. Sans cette borne, un ressenti vieux de six mois
#: pourrait remonter à l'écran.
DECLARATION_LOOKBACK_SESSIONS = 3


@dataclass(frozen=True)
class DayTrace:
    """Un jour de la fenêtre. Une trace, pas un jugement.

    `state` distingue **quatre** natures, et les confondre mentirait :

        ``done``    séance terminée ce jour-là
        ``rest``    l'utilisateur pouvait s'entraîner, il ne l'a pas fait
        ``active``  une séance est OUVERTE — elle n'est pas faite
        ``none``    hors historique : le compte n'existait pas encore

    `kind` vaut ``None`` quand le type est **inconnu**, jamais « musculation
    par défaut ». `quality_score.session_kind` retombe sur ``"strength"`` quand
    le template a été supprimé — un repli sûr pour un SCORE, un mensonge pour
    un AFFICHAGE qui prétend dire ce qu'était la séance.
    """

    offset: int
    label: str
    state: str
    kind: str | None = None
    name: str | None = None

    #: `TRAIN1-A` — la séance terminée de ce jour-là, quand il y en a une.
    #:
    #: C'est ce qui rend le niveau 2 du rail possible **sans nouvelle route** :
    #: une trace `done` pointe vers la surface de séance qui existe déjà
    #: (`/sessions/{id}/done`). Une trace `rest` n'a rien à ouvrir, et n'ouvre
    #: donc rien — un lien vers le vide se lit comme une promesse.
    session_id: int | None = None


@dataclass(frozen=True)
class ProgressFacts:
    """Faits bruts. **Aucun score, aucune bande, aucun seuil.**"""

    #: Les 14 jours, du plus ancien au plus récent. Le rail les rend tels
    #: quels ; il ABSORBE de ce fait la cadence — les sept dernières cellules
    #: contre les sept précédentes disent le même écart, sans objet de plus.
    days: tuple[DayTrace, ...] = ()

    sessions_14d: int = 0
    sessions_last_7: int = 0
    sessions_prev_7: int = 0

    #: État global **déclaré** lors de la séance la plus récente qui en porte
    #: un — `"good"` / `"flat"` / `"fatigued"`, ou `None`. `None` veut dire
    #: « il n'a rien dit », JAMAIS « il va moyen ».
    declared_state: str | None = None

    #: Date de la séance qui porte cette déclaration, et si c'est bien la
    #: séance terminée la plus récente.
    #:
    #: Remonter jusqu'à la dernière déclaration RÉELLE est correct : se taire
    #: parce que la dernière séance a été terminée sans répondre perdrait une
    #: information vraie. Mais la présenter comme si elle datait de la dernière
    #: séance **fabriquerait une fraîcheur** — le défaut du 45,0 déplacé du
    #: contenu vers le temps. D'où de quoi la dater, et seulement en cas
    #: d'écart.
    declared_at: datetime | None = None
    declared_is_latest: bool = False


def _occupant(rows, now: datetime) -> dict[int, WorkoutSession]:
    """Quelle séance occupe chaque jour de la fenêtre.

    Une séance OUVERTE occupe son jour sans le compter : elle est visible sur
    le rail — l'utilisateur sait qu'elle existe — et absente des comptages,
    parce qu'elle n'est pas faite.
    """
    by_day: dict[int, WorkoutSession] = {}
    for s in rows:
        if s.status == "completed" and not s.excluded_from_stats:
            by_day[_offset(s.started_at, now)] = s
        elif s.status == "in_progress":
            by_day.setdefault(_offset(s.started_at, now), s)
    return by_day


def _first_known_offset(created_at: datetime | None, now: datetime) -> int:
    """Premier jour de la fenêtre où le compte existait.

    `TRAIN1-A` — LE RAIL AFFIRMAIT DU REPOS AVANT L'EXISTENCE DU COMPTE.
    `DayTrace` documente quatre natures depuis le premier jour, dont
    ``none`` — « hors historique : le compte n'existait pas encore ». La
    vue-modèle sait la rendre : classe `rail__c--void`, titre « hors
    historique », phrase dédiée dans l'équivalent textuel.

    **Ce producteur ne l'a jamais émise.** Mesuré : un compte créé la veille
    rendait **quatorze traces `rest`**, c'est-à-dire treize affirmations
    « il pouvait s'entraîner, il ne l'a pas fait » sur des jours où il n'avait
    pas de compte. C'est le défaut que toute cette surface combat — une absence
    habillée en mesure — et il survivait dans l'objet censé la rendre visible.

    Trois chemins de code et une phrase du lecteur d'écran étaient donc morts,
    et aucune garde ne l'avait vu : elles éprouvaient l'état ``none`` via une
    fabrique de test, jamais via le producteur réel.
    """
    if created_at is None:
        return 0
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=now.tzinfo)
    return max(0, min(WINDOW_DAYS, _offset(created_at, now)))


def _day_traces(rows, now: datetime, first_known: int = 0) -> list[DayTrace]:
    """Les 14 traces, du plus ancien jour au plus récent.

    Extrait de `build_progress_facts` : `python:S3776` a mesuré une complexité
    cognitive de 20 pour 15 autorisés, et la règle avait raison — la fonction
    faisait deux requêtes, deux comptages, un regroupement et une projection.
    """
    by_day = _occupant(rows, now)
    days = []
    for off in range(WINDOW_DAYS):
        s = by_day.get(off)
        sid = None
        if s is None and off < first_known:
            # Le compte n'existait pas : ni repos, ni séance. Rien à dire.
            #
            # ⚠ LA DONNÉE PASSE AVANT LA BORNE. Une séance enregistrée ce
            # jour-là PROUVE que le compte existait, quoi qu'en dise
            # `created_at` — un import, une reprise de données ou une horloge
            # de travers ne doivent pas effacer une séance réelle. Tester
            # `s is None` d'abord n'est pas un détail d'écriture : la première
            # version testait la borne en premier et faisait disparaître des
            # séances antérieures à la création du compte.
            state, kind, name = "none", None, None
        elif s is None:
            state, kind, name = "rest", None, None
        elif s.status == "in_progress":
            state, kind, name = "active", None, None
        else:
            # `kind is None` quand le template a été supprimé : le type est
            # INCONNU, pas « musculation par défaut ».
            state = "done"
            kind = s.template.kind if s.template else None
            name = s.template_name_snapshot
            sid = s.id
        days.append(DayTrace(
            offset=off,
            label=(now - timedelta(days=WINDOW_DAYS - 1 - off)).strftime("%d/%m"),
            state=state, kind=kind, name=name, session_id=sid,
        ))
    return days


def build_progress_facts(
    db: Session, user_id: int, *, now: datetime | None = None
) -> ProgressFacts:
    """Lecture seule, déterministe. Deux requêtes, aucune par signal."""
    now = now or datetime.now(UTC)

    eligible = (
        WorkoutSession.user_id == user_id,
        WorkoutSession.status == "completed",
        WorkoutSession.excluded_from_stats.is_(False),
    )

    # ⚠ LES BORNES SE COMPARENT EN SQL, PAS EN PYTHON.
    #
    # La première version chargeait les dates de la fenêtre et dérivait la
    # demi-fenêtre en mémoire — une requête au lieu de deux. Elle a planté :
    # SQLite rend des datetimes **naïfs** même pour une colonne déclarée
    # `DateTime(timezone=True)`, et `naïf >= aware` lève un `TypeError`.
    #
    # Les tests unitaires de la vue-modèle ne pouvaient pas le voir : ils
    # court-circuitent la base. Seuls les tests qui rendent réellement la page
    # l'ont attrapé.
    #
    # Le moteur comparait déjà en SQL. Ce n'était pas un détail d'écriture.
    window_start = now - timedelta(days=WINDOW_DAYS)
    half_start = now - timedelta(days=HALF_WINDOW_DAYS)

    def _count(since: datetime) -> int:
        return db.execute(
            select(func.count(WorkoutSession.id))
            .where(*eligible, WorkoutSession.started_at >= since)
        ).scalar_one() or 0

    sessions_14d = _count(window_start)
    last_7 = _count(half_start)

    # ── les 14 traces ────────────────────────────────────────────────────
    # Une requête pour la fenêtre, avec le template chargé : sans lui, le type
    # serait inconnu pour TOUTES les séances, et le rail ne pourrait rien dire.
    rows = db.execute(
        select(WorkoutSession)
        .where(WorkoutSession.user_id == user_id,
               WorkoutSession.started_at >= window_start)
        .options(selectinload(WorkoutSession.template))
    ).scalars().all()

    # `TRAIN1-A` — jusqu'où l'historique de ce compte remonte-t-il ?
    # Sans cette borne, le rail affirme du repos sur des jours antérieurs à la
    # création du compte : une absence de données rendue comme un choix de
    # l'utilisateur.
    created_at = db.execute(
        select(User.created_at).where(User.id == user_id)
    ).scalar_one_or_none()
    days = _day_traces(rows, now, _first_known_offset(created_at, now))

    recent = db.execute(
        select(WorkoutSession.started_at, WorkoutSession.global_state)
        .where(*eligible)
        .order_by(WorkoutSession.started_at.desc())
        .limit(DECLARATION_LOOKBACK_SESSIONS)
    ).all()

    declared = next((r for r in recent if r.global_state is not None), None)

    return ProgressFacts(
        days=tuple(days),
        sessions_14d=sessions_14d,
        sessions_last_7=last_7,
        sessions_prev_7=sessions_14d - last_7,
        declared_state=declared.global_state if declared else None,
        declared_at=declared.started_at if declared else None,
        declared_is_latest=bool(declared is not None and declared is recent[0]),
    )


__all__ = [
    "DECLARATION_LOOKBACK_SESSIONS",
    "HALF_WINDOW_DAYS",
    "WINDOW_DAYS",
    "ProgressFacts",
    "build_progress_facts",
]
