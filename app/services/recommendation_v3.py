"""`REC-CP2` — politique de recommandation V3, à précédence explicite.

⚠ CE MODULE NE PILOTE RIEN EN PRODUCTION.
------------------------------------------
MISSION, la création de séance et toute surface utilisateur lisent encore
`recommendation.recommend_next_session` (V2). V3 existe ici pour être **comparé
à V2 sur le corpus de `REC-CP1`**, et ne sera promu qu'après la porte du `§12`.
Un basculement silencieux de politique est explicitement interdit.

POURQUOI UNE PRÉCÉDENCE, ET PAS DE NOUVEAUX POIDS
---------------------------------------------------
`REC-CP1` a mesuré, pas supposé. Trois faits gouvernent cette conception.

1. **La somme pondérée fabrique les égalités.** V2 additionne six termes et
   borne le résultat à un entier 0-100. Mutation `WEIGHT_ALTERNATION` → 0 :
   le gagnant ne bouge pas, mais **72 %** des décisions passent à égalité,
   tranchées par `display_order` puis `slug`. L'épinglage par ordre de
   catalogue est réel — simplement masqué aujourd'hui.

2. **Le plus gros poids ne discrimine pas.** `WEIGHT_AVAILABILITY` vaut 35
   points, soit le tiers du barème, et rend la MÊME valeur pour tous les
   candidats : la récupération sature en trois jours et devient plate.

3. **Le moteur mesure la couverture sur quatorze jours et ne s'en sert pas
   pour classer.** `hard_sets_by_zone_recent` (7 j) n'a AUCUN lecteur.
   `hard_sets_14d_by_zone` n'en a qu'un, `_is_specialization_justified`, un
   booléen qui ne touche jamais le score d'un `push-*`/`pull-*`/`legs-*`.

V3 ne re-calibre donc aucune constante — ce que le `§5` interdisait d'ailleurs
comme point de départ. Il change la **forme** de la décision : des critères
nommés, ordonnés, chacun capable d'expliquer son verdict.

CE QU'IL N'INVENTE PAS
-----------------------
Aucun seuil physiologique universel. Le déficit de couverture est **relatif à
la médiane de l'utilisateur lui-même** : rien n'y déclare qu'une zone « doit »
recevoir N séries. Quatorze jours reste un horizon d'**observation** (`§8`), pas
une vérité biologique. Les cibles de récupération 24/36/48/72 h restent les
heuristiques de V2, réutilisées telles quelles et non re-réglées.

Aucun apprentissage automatique (`§15`). Aucun aléatoire (`§10`).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.catalog import WorkoutTemplate
from app.models.session import WorkoutSession
from app.services.kpis import compute_template_kpis
from app.services.recommendation import (
    AVAILABILITY_INCONNUE,
    Signals,
    _compute_signals,
    _load_templates,
    _passes_fatigue_filter,
    _passes_redundancy_filter,
    template_primary_zones,
)

#: Un gabarit jamais effectué est, pour le départage par ancienneté, le plus
#: ancien de tous. Ce n'est pas une valeur magique : c'est la borne inférieure
#: du type, choisie pour que « jamais » ordonne avant « il y a longtemps ».
JAMAIS = datetime.min.replace(tzinfo=UTC)

#: Déficit attribué à une zone dont l'observation est PARTIELLE — un exercice
#: de la fenêtre n'a pas pu être classé, donc « zéro série » est une ignorance
#: et non une mesure.
#:
#: On réutilise la convention déjà nommée par `REC-CP0b` au lieu d'en créer une
#: seconde. Neutre, pas maximal : sans cela, un nom d'exercice illisible ferait
#: passer sa zone pour la plus sous-servie et épinglerait la recommandation
#: dans l'autre sens.
DEFICIT_INCONNU = AVAILABILITY_INCONNUE

#: Bandes de récupération. Elles ne re-règlent rien : elles discrétisent la
#: disponibilité que V2 calcule déjà, pour qu'elle serve de PRÉCÉDENCE au lieu
#: d'un tiers du barème.
RECUPEREE, PARTIELLE, INSUFFISANTE = 0, 1, 2

#: Pénalités de répétition, avant application de `REPEAT_REQUIRES_EVIDENCE`.
NOUVEAU, MEME_FAMILLE, MEME_GABARIT = 0, 1, 2

#: Les familles de mouvement, lues dans la nomenclature du catalogue. Ce n'est
#: pas une ontologie nouvelle — le dépôt en a déjà assez qui se ressemblent.
PREFIXES_FAMILLE = ("push", "pull", "legs", "liss", "short", "catch-up",
                    "full-body")


def famille_de(slug: str | None) -> str | None:
    """La famille d'un gabarit, dérivée de son slug."""
    if not slug:
        return None
    for prefixe in PREFIXES_FAMILLE:
        if slug.startswith(prefixe):
            return prefixe
    return slug


@dataclass(frozen=True)
class Verdict:
    """Un candidat, son rang, et **pourquoi** il est à ce rang.

    `facteurs` n'est pas décoratif : `REC-CP3` doit pouvoir expliquer une
    décision sans re-dériver quoi que ce soit depuis un contexte appauvri —
    c'est précisément le défaut de `recommendation_explainer.py` aujourd'hui.
    """

    template: WorkoutTemplate
    zones: tuple[str, ...]
    #: La clé lexicographique. Croissante : plus petit = meilleur.
    rang: tuple
    facteurs: dict[str, Any] = field(default_factory=dict)

    @property
    def slug(self) -> str:
        return self.template.slug

    @property
    def rang_sans_catalogue(self) -> tuple:
        """Le rang privé de ses deux derniers recours déterministes.

        Deux candidats égaux ici n'ont PAS été départagés par une preuve : ils
        l'ont été par l'ordre du catalogue. C'est la mesure comparable à la
        part d'égalités de V2, et elle doit rester basse.
        """
        return self.rang[:-2]


def _deficit_de_couverture(
    zones: tuple[str, ...], signaux: Signals
) -> float:
    """À quel point les zones de ce gabarit sont sous-servies sur l'horizon.

    Relatif à la médiane de l'utilisateur : `1.0` = zone jamais servie sur
    l'horizon alors que d'autres le sont ; `0.0` = zone déjà au moins à la
    médiane. Aucun volume cible absolu n'est déclaré ici.
    """
    if not zones:
        # Un gabarit sans zone résolue ne prétend ni manquer ni abonder.
        return DEFICIT_INCONNU
    mediane = signaux.median_hard_sets_14d
    if mediane <= 0:
        # Pas de base de comparaison : ce critère se tait plutôt que de
        # déclarer tout le monde en déficit maximal.
        return 0.0

    total = 0.0
    for z in zones:
        vu = signaux.hard_sets_14d_by_zone.get(z, 0)
        if vu == 0 and signaux.observation_partielle:
            total += DEFICIT_INCONNU
        else:
            total += max(0.0, min(1.0, 1.0 - vu / mediane))
    return total / len(zones)


def _bande_de_recuperation(zones: tuple[str, ...], signaux: Signals) -> int:
    """Discrétise la disponibilité que V2 calcule déjà.

    On prend le **minimum** sur les zones : un gabarit n'est pas récupéré si
    une seule de ses zones ne l'est pas. La moyenne, elle, laisserait une zone
    à plat se faire compenser par une zone fraîche.
    """
    if not zones:
        return PARTIELLE
    mini = min(
        signaux.availability_by_zone.get(z, AVAILABILITY_INCONNUE)
        for z in zones
    )
    if mini >= 1.0:
        return RECUPEREE
    if mini >= 0.5:
        return PARTIELLE
    return INSUFFISANTE


def _penalite_de_repetition(
    template: WorkoutTemplate, dernier_slug: str | None
) -> int:
    if dernier_slug is None:
        return NOUVEAU
    if template.slug == dernier_slug:
        return MEME_GABARIT
    if famille_de(template.slug) == famille_de(dernier_slug):
        return MEME_FAMILLE
    return NOUVEAU


def _bande_de_modalite(
    template: WorkoutTemplate, signaux: Signals
) -> int:
    """Préférer la modalité la moins récemment pratiquée.

    ⚠ CE CRITÈRE REMPLACE DEUX BONUS PERMANENTS DE V2, ET C'EST VOULU.

    V2 accordait `WEIGHT_ALTERNATION = 20` dès que les deux dernières séances
    étaient de la force — une condition **vraie en permanence** pour quiconque
    s'entraîne en force — puis `+10` de plus si le cardio manquait depuis sept
    jours, sans expiration. Ensemble : trente points constants offerts au
    cardio, qui suffisent à lui faire gagner **toutes** les décisions du corpus.

    Ici la modalité n'est plus un supplément : c'est la même règle de récence
    que partout ailleurs, appliquée au couple force/cardio. Elle ne peut pas
    s'installer, parce qu'elle s'annule dès que la modalité a été pratiquée.
    """
    depuis_cardio = signaux.days_since_last_cardio
    depuis_force = signaux.days_since_last_strength
    if depuis_cardio is None and depuis_force is None:
        return 0
    # `None` = jamais pratiquée, donc la plus ancienne de toutes.
    c = float("inf") if depuis_cardio is None else depuis_cardio
    f = float("inf") if depuis_force is None else depuis_force
    if c == f:
        return 0
    delaissee = "cardio" if c > f else "strength"
    kind = "cardio" if template.kind == "cardio" else "strength"
    return 0 if kind == delaissee else 1


def _en_utc(quand: datetime | None) -> datetime:
    """Normalise un horodatage venu de la base.

    SQLite rend des datetimes **naïfs** ; le sentinel `JAMAIS` et `now` sont
    conscients. Les comparer directement lève, et le départage par ancienneté
    — tout l'objet de ce critère — tomberait sur cette erreur plutôt que sur
    une décision.
    """
    if quand is None:
        return JAMAIS
    return quand if quand.tzinfo is not None else quand.replace(tzinfo=UTC)


def _derniers_passages(
    db: Session, user_id: int, now: datetime
) -> tuple[dict[str, datetime], dict[str, datetime], str | None]:
    """Quand chaque gabarit, et chaque famille, ont été pratiqués pour la
    dernière fois **avant** `now`.

    Lu depuis `kpis.compute_template_kpis`, que la spec désigne depuis
    l'origine comme la source de `last_done_at` — le moyen existait, le moteur
    ne l'avait jamais branché.
    """
    par_gabarit = {
        k.slug: _en_utc(k.last_done_at)
        for k in compute_template_kpis(db, user_id=user_id, until=now)
        if k.slug and k.last_done_at is not None
    }
    par_famille: dict[str, datetime] = {}
    for slug, quand in par_gabarit.items():
        f = famille_de(slug)
        if f and quand > par_famille.get(f, JAMAIS):
            par_famille[f] = quand
    dernier = max(par_gabarit, key=par_gabarit.get, default=None)
    return par_gabarit, par_famille, dernier


def _eligibles(
    db: Session, signaux: Signals
) -> list[tuple[WorkoutTemplate, tuple[str, ...]]]:
    """Les filtres de V2, inchangés. Un filtre de sécurité n'est pas une
    préférence : il n'a donc rien à faire dans la précédence."""
    retenus = []
    for t in _load_templates(db):
        if not _passes_fatigue_filter(t, signaux.fatigue_score):
            continue
        zones = tuple(template_primary_zones(t))
        if not _passes_redundancy_filter(list(zones),
                                         signaux.hard_sets_by_zone_24h):
            continue
        retenus.append((t, zones))
    return retenus


def classer_candidats(
    db: Session, user_id: int, now: datetime
) -> list[Verdict]:
    """Le classement V3 complet, du meilleur au moins bon.

    La précédence, dans l'ordre et sans somme pondérée :

    0. **éligibilité** — filtres de V2, inchangés (archivé, fatigue,
       redondance 24 h). Un filtre de sécurité n'est pas une préférence.
    1. **récupération** — un gabarit dont une zone n'est pas récupérée passe
       après un gabarit prêt.
    2. **couverture longitudinale** — le plus sous-servi d'abord. C'est le
       signal que le moteur calculait sans jamais le lire.
    3. **justification de répétition** — refaire le même gabarit, ou la même
       famille, passe après — **sauf** si la couverture le porte, auquel cas la
       répétition est justifiée et la pénalité tombe.
    4. **modalité délaissée** — récence appliquée au couple force/cardio.
    5. **ancienneté du gabarit**, puis **de la famille** — le départage que la
       spec promet depuis l'origine et que le code n'a jamais lu.
    6. **ordre de catalogue** — dernier recours déterministe. Aucun aléatoire.
    """
    signaux = _compute_signals(db, user_id, now)
    dernier_passage, passage_famille, dernier_slug = _derniers_passages(
        db, user_id, now)
    eligibles = _eligibles(db, signaux)

    deficits = {t.slug: _deficit_de_couverture(z, signaux)
                for t, z in eligibles}
    # `REPEAT_REQUIRES_EVIDENCE` — la répétition redevient permise, mais
    # seulement portée par la couverture, jamais par une égalité, un
    # `display_order`, un `slug` ou une donnée manquante.
    deficit_max = max(deficits.values(), default=0.0)

    verdicts: list[Verdict] = []
    for t, zones in eligibles:
        deficit = deficits[t.slug]
        repetition = _penalite_de_repetition(t, dernier_slug)
        justifiee = repetition != NOUVEAU and deficit >= deficit_max > 0.0
        if justifiee:
            repetition = NOUVEAU

        recuperation = _bande_de_recuperation(zones, signaux)
        modalite = _bande_de_modalite(t, signaux)
        vu_gabarit = dernier_passage.get(t.slug, JAMAIS)
        vu_famille = passage_famille.get(famille_de(t.slug) or "", JAMAIS)

        verdicts.append(Verdict(
            template=t,
            zones=zones,
            rang=(recuperation, -deficit, repetition, modalite,
                  vu_gabarit, vu_famille, t.display_order, t.slug),
            facteurs={
                "recuperation": recuperation,
                "deficit_couverture": round(deficit, 3),
                "repetition": repetition,
                "repetition_justifiee": justifiee,
                "modalite_delaissee": modalite == 0,
                "dernier_passage": None if vu_gabarit is JAMAIS else vu_gabarit,
                "observation_partielle": signaux.observation_partielle,
            },
        ))

    verdicts.sort(key=lambda v: v.rang)
    return verdicts


#: Ce que l'horizon de couverture EST. `§8` : « quatorze jours est une
#: mémoire, pas une vérité physiologique ». La phrase le dit à l'utilisateur
#: dans ces termes, plutôt que de laisser croire à un cycle biologique.
HORIZON_OBSERVATION = "14 derniers jours"

#: Libellés lisibles des zones, empruntés au référentiel du corps. On ne crée
#: pas un second vocabulaire : `ZONE_LABELS` est déjà celui du produit.
def _libelle_zone(zone: str) -> str:
    from app.services.muscle_mapping import ZONE_LABELS

    return ZONE_LABELS.get(zone, zone)


def expliquer(verdict: Verdict, rang: int = 0) -> dict[str, Any]:
    """La trace d'explication d'un candidat — **structurée, pas re-dérivée**.

    ⚠ C'EST LE POINT DE `REC-CP3`.

    `recommendation_explainer.py` reconstruit aujourd'hui ses raisons à partir
    d'un contexte appauvri : quatre clés (`cold_start`, `fallback`,
    `days_since_last_*`, `fatigue_score`) plus la phrase déjà écrite. Il
    re-devine donc ce que le moteur savait déjà et n'a pas transmis — et deux
    logiques parallèles finissent toujours par diverger.

    Ici le moteur **dit** ce qui a décidé. Rien à re-dériver.

    Aucun nombre n'en sort : ni score 0-100, ni déficit. Un utilisateur n'a pas
    à recevoir la mécanique interne comme une vérité sur son corps.
    """
    f = verdict.facteurs
    gagnants: list[str] = []
    limitants: list[str] = []

    zones = [_libelle_zone(z) for z in verdict.zones]
    if f["deficit_couverture"] >= 0.75 and zones:
        gagnants.append(
            f"{', '.join(zones[:2])} : le moins servi sur {HORIZON_OBSERVATION}")
    elif f["deficit_couverture"] <= 0.25 and zones:
        limitants.append(
            f"{', '.join(zones[:2])} : déjà bien servi sur "
            f"{HORIZON_OBSERVATION}")

    if f["recuperation"] == RECUPEREE:
        gagnants.append("zones récupérées")
    elif f["recuperation"] == INSUFFISANTE:
        limitants.append("une zone n'a pas fini de récupérer")

    if f["modalite_delaissee"]:
        gagnants.append("la modalité la plus délaissée")

    if f["dernier_passage"] is None:
        gagnants.append("jamais fait")

    justification = None
    if f["repetition"] == MEME_GABARIT:
        limitants.append("c'est la séance qui vient d'être faite")
    elif f["repetition"] == MEME_FAMILLE:
        limitants.append("même famille que la dernière séance")
    elif f["repetition_justifiee"]:
        justification = (
            "Reproposé parce que ces zones restent les moins servies, "
            "pas par défaut.")

    return {
        "facteurs_gagnants": tuple(gagnants),
        "facteurs_limitants": tuple(limitants),
        "horizon": HORIZON_OBSERVATION,
        "famille": famille_de(verdict.slug),
        "justification_repetition": justification,
        # `REC-CP0b` — la même grammaire que `zone_exposure`, pas une seconde.
        "provenance": "partielle" if f["observation_partielle"] else "mesurée",
        "rang": rang,
    }


def phrase_de(explication: dict[str, Any]) -> str:
    """La phrase compacte, dérivée de la trace — jamais écrite en parallèle.

    Le `§` de `REC-CP3` conserve la phrase courte. Elle doit rester une
    **lecture** de l'explication structurée : deux rédactions indépendantes
    divergeraient, ce qui est exactement le défaut qu'on corrige.
    """
    gagnants = explication["facteurs_gagnants"]
    if gagnants:
        phrase = gagnants[0][:1].upper() + gagnants[0][1:] + "."
    else:
        phrase = "Aucun signal ne se détache — choix par ordre du catalogue."

    if explication["provenance"] == "partielle":
        phrase += " Lecture partielle : un exercice n'a pas pu être classé."
    return phrase[:140]


def recommander_v3(
    db: Session, user_id: int, now: datetime | None = None
) -> dict | None:
    """Même forme de retour que V2, pour que le corpus compare l'un à l'autre.

    ⚠ `score` N'EST PAS COMPARABLE À CELUI DE V2. V3 ne produit pas de somme
    pondérée ; l'entier exposé ici n'est qu'une lecture du déficit de
    couverture, présente pour que la forme du dictionnaire reste identique.
    Comparer les deux nombres n'aurait aucun sens — la comparaison licite porte
    sur les gagnants, les séries, et la part de décisions tranchées par l'ordre
    du catalogue.
    """
    now = now or datetime.now(UTC)
    # Séance ouverte → pas de recommandation, même règle et même borne
    # causale que V2 (`recommendation.py:958`). On rejoue la requête plutôt
    # que d'appeler V2 en entier : faire tourner le moteur qu'on cherche à
    # remplacer, juste pour lire un booléen, fausserait la comparaison autant
    # que son coût.
    ouverte = db.execute(
        select(WorkoutSession)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == "in_progress",
            WorkoutSession.started_at < now,
        )
        .limit(1)
    ).scalar_one_or_none()
    if ouverte is not None:
        return None

    verdicts = classer_candidats(db, user_id, now)
    if not verdicts:
        return None

    tete, *reste = verdicts

    def _candidat(v: Verdict, rang: int) -> dict:
        explication = expliquer(v, rang)
        return {
            "template": v.template,
            # ⚠ `score` N'EST PAS UNE VÉRITÉ UTILISATEUR. Il n'existe que pour
            # que la forme du dictionnaire reste comparable à celle de V2 dans
            # le banc de mesure. Aucune surface ne le rend, et une garde de
            # `REC-CP3` vérifie qu'aucun nombre ne traverse l'explication.
            "score": int(round(v.facteurs["deficit_couverture"] * 100)),
            "phrase": phrase_de(explication),
            "primary_zones": list(v.zones),
            "facteurs": v.facteurs,
            "explication": explication,
        }

    return {
        "top": _candidat(tete, 0),
        "alternatives": [_candidat(v, i) for i, v in enumerate(reste[:2], 1)],
        "context": {
            "politique": "v3",
            "cold_start": signaux_froids(verdicts),
            "departage_par_catalogue": bool(
                reste and tete.rang_sans_catalogue == reste[0].rang_sans_catalogue
            ),
        },
    }


def signaux_froids(verdicts: list[Verdict]) -> bool:
    """V3 n'a pas de court-circuit de démarrage à froid.

    V2 en a un, et `REC-CP1` a montré qu'il domine les premières décisions :
    sous trois séances, le scoring est **entièrement ignoré** et `core[0]` est
    rendu avec un score fixe et zéro alternative. Ici le classement s'applique
    dès la première décision — avec une couverture inconnue, donc un critère 2
    muet, et la décision retombe sur la récence et l'ordre de catalogue.

    La fonction existe pour que la clé `cold_start` du dictionnaire garde un
    sens dans la comparaison : elle dit « aucune preuve de couverture ».
    """
    return not any(v.facteurs["deficit_couverture"] > 0.0 for v in verdicts)
