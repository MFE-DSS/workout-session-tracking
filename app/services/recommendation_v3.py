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
from app.services.zone_recovery import LIMITANT, NON_LIMITANT, PARTIEL

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

#: `REC-ROLLOUT-01` (D14) — à bande de récupération égale, la force passe avant
#: le cardio. Le cardio est le PLAN B : il ne gagne que lorsqu'aucune séance de
#: force n'est dans une bande au moins aussi bonne.
FORCE, CARDIO = 0, 1

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


#: `TRAIN A` — la décision canonique, rangée dans les trois bandes que ce
#: classement utilise déjà. Correspondance exacte, aucune granularité neuve.
_BANDE_PAR_DECISION = {
    NON_LIMITANT: RECUPEREE,
    PARTIEL: PARTIELLE,
    LIMITANT: INSUFFISANTE,
}


@dataclass(frozen=True)
class RecuperationCanonique:
    """Les deux cartes que la politique servie lit — décision et preuve.

    ═══════════════════════════════════════════════════════════════════════
    `TRAIN A` — POURQUOI CE CALCUL VIT ICI ET NON DANS `recommendation.py`.

    Première écriture : les deux cartes étaient des champs de `Signals`, et
    `_compute_signals` appelait le contrat canonique. **Deux gardes de gel
    ont rougi**, et elles avaient raison sur les deux points.

    `test_recommendation_py_is_not_modified` interdit à
    `recommendation.py` de connaître `zone_recovery` : la dépendance va du
    contrat VERS le moteur hérité, jamais l'inverse, sinon les deux
    modèles se referment l'un sur l'autre.

    `test_the_recommendation_engine_may_be_corrected_but_never_grow`
    épingle les champs de `Signals` — le contrat d'ENTRÉE du scoring, que
    `V2` partage. Y ajouter des champs que seul `V3` lit aurait fait
    grossir un contrat commun pour un besoin qui ne l'est pas.

    Les deux gardes pointaient la même chose : **c'est la POLITIQUE SERVIE
    qui migre, pas le socle de signaux.** Le calcul appartient donc à ce
    module. `recommendation.py` n'est pas touché d'une ligne.
    ═══════════════════════════════════════════════════════════════════════
    """

    #: `{zone: non_limitant | partiel | limitant}` — ce que le rang lit.
    decision: dict[str, str] = field(default_factory=dict)
    #: `{zone: bool}` — preuve POSITIVE de récupération. Ce que
    #: l'explication lit, et que le rang ignore délibérément.
    preuve: dict[str, bool] = field(default_factory=dict)
    #: `REC-ROLLOUT-01` — `{zone: heures depuis la dernière charge}`, `None`
    #: pour une zone jamais chargée. Un FAIT horodaté, pas l'estimation 0–1.
    heures: dict[str, float | None] = field(default_factory=dict)


#: Repli neutre : aucune carte. Utilisé quand la chaîne d'évidence est
#: indisponible — une panne ne doit pas se lire comme une autorisation.
_SANS_RECUPERATION = RecuperationCanonique()


def recuperation_canonique(db: Session, user_id: int,
                           now: datetime) -> RecuperationCanonique:
    """Lit le contrat canonique. Dégrade en silence, jamais en faveur.

    L'import est différé : le contrat tire toute la chaîne d'évidence, et
    ce module est sur un chemin chaud.
    """
    try:
        from app.services.zone_recovery import (
            build_zone_recovery,
            decisions_par_zone,
            preuves_par_zone,
        )
        estimations = build_zone_recovery(db, user_id, now=now)
        return RecuperationCanonique(
            decision=decisions_par_zone(estimations),
            preuve=preuves_par_zone(estimations),
            heures={e.zone_code: e.hours_since_last_load for e in estimations},
        )
    except Exception:
        return _SANS_RECUPERATION


def _preuve_de_recuperation(zones: tuple[str, ...],
                            recup: RecuperationCanonique) -> bool:
    """Y a-t-il une preuve POSITIVE que toutes ces zones sont récupérées ?

    `False` dès qu'UNE zone n'en fournit pas — une seule inconnue suffit à
    retirer le droit d'affirmer. Et `False` quand la carte est absente : une
    panne de la chaîne d'évidence ne crée pas une preuve.
    """
    if not zones or not recup.preuve:
        return False
    return all(recup.preuve.get(z, False) for z in zones)


def _bande_de_recuperation(zones: tuple[str, ...],
                           recup: RecuperationCanonique) -> int:
    """La bande de récupération d'un gabarit, depuis le contrat CANONIQUE.

    On prend le **pire** sur les zones : un gabarit n'est pas récupéré si
    une seule de ses zones ne l'est pas. La moyenne, elle, laisserait une zone
    à plat se faire compenser par une zone fraîche.

    ═══════════════════════════════════════════════════════════════════════
    `TRAIN A` — CETTE FONCTION LISAIT `availability_by_zone`, UN RATIO 0–1.

    Le ratio portait un défaut d'une seule ligne : une zone **jamais
    entraînée** y valait `1.0`, donc `RECUPEREE` — le classement affirmait
    une récupération pleine là où il n'avait aucune observation. Le contrat
    canonique dit `UNKNOWN / confiance NONE` sur ce même cas.

    ⚠ ET POURTANT LA BANDE NE CHANGE PAS POUR CE CAS, DÉLIBÉRÉMENT.
    L'arbitrage opérateur a tranché : « sans charge observée » est NON
    LIMITANT — il n'y a aucune preuve qui doive écarter ce candidat. Il
    occupe donc le même RANG qu'une zone connue disponible, sans partager sa
    PREUVE. La distinction vit dans `recovery_evidence_by_zone`, que
    l'explication lit et que le classement ignore.

    Mesuré avant d'écrire : pénaliser le « sans charge observée » aurait
    changé **9 gagnants sur 10**. Migrer l'autorité en le gardant non
    limitant en change **0 sur 60**.

    ⚠ REPLI. Carte absente — récupération canonique indisponible — on rend
    `PARTIELLE`, le neutre. Jamais `RECUPEREE` : une panne de la chaîne
    d'évidence ne doit pas se lire comme une autorisation.
    ═══════════════════════════════════════════════════════════════════════
    """
    if not zones or not recup.decision:
        return PARTIELLE
    return max(
        _BANDE_PAR_DECISION.get(recup.decision.get(z, PARTIEL), PARTIELLE)
        for z in zones
    )


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


def _bande_de_plan_b(template: WorkoutTemplate) -> int:
    """La force d'abord ; le cardio en plan B.

    ⚠ `REC-ROLLOUT-01` (D14) — CE CRITÈRE REMPLACE « LA MODALITÉ DÉLAISSÉE ».

    Mesuré avant d'écrire : après une première séance `push-a`, cinq séances de
    force étaient **pleinement récupérées** et égales sur la couverture et la
    répétition ; la modalité délaissée les départageait toutes en faveur du
    cardio. Pour qui n'a jamais fait de cardio, `days_since_last_cardio = None`
    valait « le plus ancien de tous » : le cardio gagnait CHAQUE égalité.

    La leçon de `REC-CP2` reste juste — V2 offrait trente points permanents au
    cardio — et elle est tenue plus fermement : le cardio n'a plus de bonus du
    tout. Placé juste après la récupération, ce critère ne départage qu'à bande
    ÉGALE ; si toute la force récupère encore, le cardio gagne par la bande
    elle-même. C'est le plan B voulu par l'opérateur.
    """
    return CARDIO if template.kind == "cardio" else FORCE


def _zones_en_recuperation(zones: tuple[str, ...],
                           recup: RecuperationCanonique) -> int:
    """Combien de zones du gabarit récupèrent encore — moins, c'est mieux.

    `REC-ROLLOUT-01` (D14) : « la deuxième séance la plus logique est celle où
    il reste le moins de muscles à récupérer ». La bande ne lit que la PIRE
    zone ; deux gabarits en `PARTIELLE` y sont égaux même si l'un n'a qu'une
    zone à reprendre et l'autre quatre.

    ⚠ UN COMPTE, PAS LA DISPONIBILITÉ FINE. L'estimation 0–1 du contrat est
    une estimation, pas une mesure ; départager 0,85 et 1,0 serait une fausse
    précision, et rendrait la couverture muette dans toute la bande récupérée.
    Une zone sans charge observée est NON LIMITANTE (`TRAIN A`) : elle ne
    compte pas. Carte absente : zéro, le neutre — jamais une pénalité inventée.
    """
    if not recup.decision:
        return 0
    return sum(1 for z in zones if recup.decision.get(z, PARTIEL) != NON_LIMITANT)


def _repos_minimal(zones: tuple[str, ...], recup: RecuperationCanonique) -> float:
    """Depuis combien d'heures la zone la MOINS reposée du gabarit n'a pas été
    chargée — plus, c'est mieux. Jamais chargée : `inf`, la plus reposée.

    `REC-ROLLOUT-01` (D14) : « la séance la plus logique est celle où il n'a
    sollicité aucun muscle ». C'est le départage qui manquait une fois la
    modalité retirée — mesuré : sans lui, 67 % des décisions du corpus
    tombaient sur l'ordre du catalogue.

    ⚠ UN FAIT, PAS L'ESTIMATION. Des heures depuis une charge enregistrée, non
    la disponibilité 0–1. Placé APRÈS la couverture : l'équilibre sur quatorze
    jours décide d'abord, le repos départage ensuite.
    Carte absente ou gabarit sans zone : `inf`, le neutre — aucune pénalité.
    """
    vus = [recup.heures.get(z) for z in zones]
    connues = [h for h in vus if h is not None]
    return min(connues) if connues else float("inf")


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
    1 bis. **plan B** (`REC-ROLLOUT-01`) — à bande égale, la force passe avant
       le cardio.
    1 ter. **le moins sollicité** (`REC-ROLLOUT-01`) — moins de zones encore en
       récupération d'abord.
    2. **couverture longitudinale** — le plus sous-servi d'abord. C'est le
       signal que le moteur calculait sans jamais le lire.
    3. **justification de répétition** — refaire le même gabarit, ou la même
       famille, passe après — **sauf** si la couverture le porte, auquel cas la
       répétition est justifiée et la pénalité tombe.
    3 bis. **les muscles les plus reposés** (`REC-ROLLOUT-01`) — heures depuis
       la dernière charge de la zone la moins reposée.
    ~~4. modalité délaissée~~ — retirée par `REC-ROLLOUT-01`, remplacée par 1 bis.
    5. **ancienneté du gabarit**, puis **de la famille** — le départage que la
       spec promet depuis l'origine et que le code n'a jamais lu.
    6. **ordre de catalogue** — dernier recours déterministe. Aucun aléatoire.
    """
    signaux = _compute_signals(db, user_id, now)
    # `TRAIN A` — la récupération CANONIQUE, lue une fois pour tout le
    # classement. C'est la politique servie qui migre ; `recommendation.py`
    # n'est pas touché (voir `RecuperationCanonique`).
    recup = recuperation_canonique(db, user_id, now)
    dernier_passage, passage_famille, dernier_slug = _derniers_passages(
        db, user_id, now)
    eligibles = _eligibles(db, signaux)

    deficits = {t.slug: _deficit_de_couverture(z, signaux)
                for t, z in eligibles}
    # `REPEAT_REQUIRES_EVIDENCE` — la répétition redevient permise, mais
    # seulement portée par la couverture, jamais par une égalité, un
    # `display_order`, un `slug` ou une donnée manquante.
    deficit_max = max(deficits.values(), default=0.0)

    bandes = {t.slug: _bande_de_recuperation(z, recup) for t, z in eligibles}
    # `REC-ROLLOUT-01` — la meilleure bande qu'offre la force. Le cardio n'est
    # le plan B que s'il fait strictement mieux : sinon, la force passe.
    meilleure_force = min((bandes[t.slug] for t, _ in eligibles
                           if _bande_de_plan_b(t) == FORCE), default=None)

    verdicts: list[Verdict] = []
    for t, zones in eligibles:
        deficit = deficits[t.slug]
        repetition = _penalite_de_repetition(t, dernier_slug)
        justifiee = repetition != NOUVEAU and deficit >= deficit_max > 0.0
        if justifiee:
            repetition = NOUVEAU

        recuperation = bandes[t.slug]
        plan_b = _bande_de_plan_b(t)
        en_recuperation = _zones_en_recuperation(zones, recup)
        repos = _repos_minimal(zones, recup)
        vu_gabarit = dernier_passage.get(t.slug, JAMAIS)
        vu_famille = passage_famille.get(famille_de(t.slug) or "", JAMAIS)

        verdicts.append(Verdict(
            template=t,
            zones=zones,
            rang=(recuperation, plan_b, en_recuperation, -deficit, repetition,
                  -repos, vu_gabarit, vu_famille, t.display_order, t.slug),
            facteurs={
                "recuperation": recuperation,
                # `TRAIN A §2` — LE RANG NE SUFFIT PAS À AUTORISER LA PHRASE.
                #
                # `recuperation == RECUPEREE` signifie « aucune preuve ne
                # limite ce candidat ». Cela couvre DEUX états très
                # différents : une zone connue disponible, et une zone dont
                # on ne sait rien. Dire « zones récupérées » sur la seconde
                # serait une affirmation physiologique inventée — le défaut
                # même que la migration d'autorité corrige.
                #
                # Ce booléen est donc la CONDITION de la phrase, et il est
                # séparé du rang exprès : le classement les traite pareil,
                # l'explication ne le peut pas.
                "preuve_recuperation": _preuve_de_recuperation(zones, recup),
                "deficit_couverture": round(deficit, 3),
                "repetition": repetition,
                "repetition_justifiee": justifiee,
                # vrai seulement quand le cardio sert parce que la force,
                # elle, récupère encore — la phrase du plan B en dépend
                "plan_b": plan_b == CARDIO and (
                    meilleure_force is None or recuperation < meilleure_force),
                "zones_en_recuperation": en_recuperation,
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


#: ⚠ LES LIBELLÉS DE FACTEUR SONT DES CONSTANTES, ET CE N'EST PAS COSMÉTIQUE.
#:
#: Ils sont ÉCRITS par `expliquer` et RECONNUS par `_en_tete`, qui remonte en
#: première position celui qui a décidé. Deux orthographes du même facteur
#: casseraient cette remontée **en silence** : l'explication resterait
#: plausible, simplement dans le mauvais ordre.
FACTEUR_NOUVEAUTE = "jamais fait"
FACTEUR_RECUPERATION = "zones récupérées"
#: `REC-ROLLOUT-01` — vraies par construction : elles ne s'énoncent que quand le
#: rang montre ce qu'elles disent.
FACTEUR_PLAN_B = "tout le reste récupère encore : séance cardio"
FACTEUR_MOINS_SOLLICITE = "le moins de zones encore en récupération"
FACTEUR_REPOS = "les muscles les plus reposés"
#: Les facteurs qui ne s'énoncent que lorsque le rang montre qu'ils ont décidé.
_FACTEUR_SI_DECISIF = {
    "zones_en_recuperation": (FACTEUR_MOINS_SOLLICITE,),
    "repos": (FACTEUR_REPOS,),
}

#: Les composantes de la clé lexicographique, dans l'ordre exact où
#: `classer_candidats` les range. ⚠ Cette table ne décide de RIEN : elle NOMME
#: ce que le rang a déjà décidé. La modifier sans modifier la clé ferait dire
#: à l'explication le contraire de ce que le moteur a fait.
CRITERES_DU_RANG = (
    "recuperation",
    "plan_b",
    "zones_en_recuperation",
    "couverture",
    "repetition",
    "repos",
    "recence_gabarit",
    "recence_famille",
    "ordre_catalogue",
    "slug",
)

#: Tolérance de comparaison du déficit, qui est un flottant. Les déficits sont
#: arrondis à trois décimales dans `facteurs` ; on compare au même grain.
_EPSILON = 1e-9


def _en_tete(gagnants: list[str], decisif: str | None,
             zones: list[str]) -> list[str]:
    """Remonte en première position le facteur qui a réellement décidé.

    ⚠ ON NE RÉÉCRIT RIEN, ON RÉORDONNE. Le `§3` demande que la cause la plus
    forte vienne d'abord ; il n'autorise pas à fabriquer une cause. Si le
    critère décisif n'a pas de facteur énoncé — l'ordre du catalogue, par
    exemple, qui n'est pas une raison — l'ordre naturel reste.
    """
    if not decisif or len(gagnants) < 2:
        return gagnants
    reperes = {
        "couverture": ", ".join(zones[:2]),
        "plan_b": FACTEUR_PLAN_B,
        "zones_en_recuperation": FACTEUR_MOINS_SOLLICITE,
        "repos": FACTEUR_REPOS,
        "recence_gabarit": FACTEUR_NOUVEAUTE,
        "recence_famille": FACTEUR_NOUVEAUTE,
        "recuperation": FACTEUR_RECUPERATION,
    }
    repere = reperes.get(decisif)
    if not repere:
        return gagnants
    for i, facteur in enumerate(gagnants):
        if repere in facteur:
            return [facteur, *gagnants[:i], *gagnants[i + 1:]]
    return gagnants


def critere_decisif(gagnant: Verdict, dauphin: Verdict | None) -> str | None:
    """Le premier critère qui a réellement séparé le gagnant de son dauphin.

    ⚠ `REC-CP5` — CE N'EST PAS UNE HEURISTIQUE D'EXPLICATION, C'EST UNE
    LECTURE DU RANG.

    V3 range par précédence lexicographique. Le critère qui décide est donc,
    littéralement, **le premier rang où les deux clés diffèrent**. On ne
    devine pas ce qui « a dû » compter : on lit ce qui a compté.

    C'est ce qui permet au `§3` d'être tenu sans inventer de pondération —
    « jamais fait » ne devient une raison que s'il a effectivement départagé,
    et jamais quand une preuve plus forte l'a précédé.
    """
    if dauphin is None:
        return None
    # `strict=True` : deux clés de rang de longueurs différentes seraient un
    # défaut de construction, pas un cas à traiter en silence.
    for i, (a, b) in enumerate(zip(gagnant.rang, dauphin.rang, strict=True)):
        if isinstance(a, float) and isinstance(b, float):
            if abs(a - b) > _EPSILON:
                return CRITERES_DU_RANG[i]
            continue
        if a != b:
            return CRITERES_DU_RANG[i]
    return None


def _facteur_de_couverture(deficit: float, zones: list[str]) -> tuple[str, bool]:
    """La couverture, TOUJOURS dite, graduée.

    ⚠ LE DÉFAUT QUE `REC-CP5` CORRIGE, ET IL ÉTAIT DANS CETTE FONCTION.

    La couverture est le critère PRIMAIRE du classement de V3. Elle n'était
    pourtant énoncée qu'aux deux extrêmes — au-dessus de 0,75 ou en dessous de
    0,25 — donc **muette dans toute la bande médiane**, qui est la plus
    fréquente. Mesuré sur un compte réel de huit séances : V3 rendait la même
    recommandation que V2 en n'expliquant plus que « La modalité la plus
    délaissée. » et « Jamais fait. »

    Le classement n'est pas touché : seul l'énoncé l'est. Rendre `True` en
    second signifie « c'est un facteur GAGNANT », `False` « limitant ».
    """
    libelles = ", ".join(zones[:2])
    if deficit >= 0.75:
        return f"{libelles} : le moins servi sur {HORIZON_OBSERVATION}", True
    if deficit >= 0.5:
        return f"{libelles} : peu servi sur {HORIZON_OBSERVATION}", True
    if deficit > 0.25:
        return (f"{libelles} : servi moins que la moyenne sur "
                f"{HORIZON_OBSERVATION}"), True
    return f"{libelles} : déjà bien servi sur {HORIZON_OBSERVATION}", False


def expliquer(verdict: Verdict, rang: int = 0,
              decisif: str | None = None) -> dict[str, Any]:
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

    # ── 1. LA CAUSE LA PLUS FORTE D'ABORD (`§3`).
    #
    # La couverture est le critère primaire du classement : elle parle
    # toujours, graduée, et elle passe en tête quand c'est elle qui a décidé.
    zones = [_libelle_zone(z) for z in verdict.zones]
    if zones:
        texte, gagnant = _facteur_de_couverture(f["deficit_couverture"], zones)
        (gagnants if gagnant else limitants).append(texte)

    # ── 2. LA CONTRAINTE MATÉRIELLE / RÉCUPÉRATION.
    #
    # ⚠ `TRAIN A §2` — LA PREUVE CONDITIONNE LA PHRASE, PAS LE RANG.
    #
    # `RECUPEREE` veut dire « rien ne limite ce candidat ». Sur une zone
    # jamais chargée, c'est vrai ET sans preuve : l'affirmation « zones
    # récupérées » y serait inventée. Le silence est la seule sortie
    # honnête — et il est explicitement autorisé.
    if f["recuperation"] == RECUPEREE and f.get("preuve_recuperation"):
        gagnants.append(FACTEUR_RECUPERATION)
    elif f["recuperation"] == INSUFFISANTE:
        limitants.append("une zone n'a pas fini de récupérer")

    # `REC-ROLLOUT-01` — le moins sollicité et le repos ne se disent que s'ils
    # ont départagé.
    gagnants.extend(_FACTEUR_SI_DECISIF.get(decisif, ()))

    # ── 3. LA NOUVEAUTÉ — SEULEMENT SI ELLE A MATÉRIELLEMENT CONTRIBUÉ.
    #
    # ⚠ « Jamais fait » était ajouté à CHAQUE candidat jamais effectué, qu'il
    # ait départagé ou non. Sur un compte où la couverture se taisait, il
    # devenait l'explication ENTIÈRE d'une décision qu'il n'avait pas prise —
    # exactement ce que le `§3` proscrit.
    #
    # Il ne parle plus que lorsque le rang montre qu'il a séparé le gagnant de
    # son dauphin, ou qu'aucune autre preuve n'existe.
    if f["dernier_passage"] is None and (
            decisif in ("recence_gabarit", "recence_famille")
            or not gagnants):
        gagnants.append(FACTEUR_NOUVEAUTE)

    # L'ordre d'énonciation suit le critère qui a réellement décidé.
    gagnants = _en_tete(gagnants, decisif, zones)

    # `REC-ROLLOUT-01` — LE PLAN B EST TOUJOURS LA PREMIÈRE RAISON.
    #
    # Un cardio servi en plan B l'est parce que la force récupère encore ; c'est
    # la cause, quel que soit le critère qui le sépare d'un autre cardio. Dire
    # d'abord « Core : le moins servi » laisserait croire à un choix de zone.
    if f.get("plan_b"):
        gagnants = [FACTEUR_PLAN_B, *gagnants]

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

    # `Sb_TRAIN_A_ENV_ACT_01` — LA PORTE D'ENVIRONNEMENT, ici et nulle part
    # ailleurs. C'est le seul endroit du graphe servi où la liste ORDONNÉE
    # COMPLÈTE existe : filtrer plus loin porterait sur `top + 2`, et
    # rendrait vide alors qu'un quatrième candidat était servable.
    #
    # Elle ne CLASSE pas. Elle retire les candidats prouvés infaisables et
    # laisse l'ordre survivant intact — l'équipement est une faisabilité,
    # pas une préférence, et en faire un signal de score le rendrait
    # négociable. Sur environnement non déclaré, elle est inerte.
    from app.services.environment_activation import appliquer

    environnement = appliquer(db, user_id, verdicts)
    verdicts = list(environnement.candidats)
    if not verdicts:
        # Aucun candidat servable ET aucun incertain : l'état produit est
        # NOMMÉ par le contexte, il ne se déduit pas d'une absence.
        return {
            "top": None,
            "alternatives": [],
            "context": {
                "politique": "v3",
                "cold_start": False,
                "departage_par_catalogue": False,
                "environnement_actif": True,
                "environnement_etat": environnement.etat_catalogue,
                "environnement_identite": environnement.identite,
                "environnement_adapte": False,
            },
        }

    tete, *reste = verdicts

    def _candidat(v: Verdict, rang: int) -> dict:
        # `REC-CP5` — chaque candidat est expliqué par rapport à CELUI QUI LE
        # SUIT. Pour la tête c'est le dauphin ; pour une alternative, le
        # candidat suivant. Comparer tout le monde au dauphin de la tête
        # ferait dire à une alternative pourquoi ELLE N'A PAS gagné, ce qui
        # n'est pas ce qu'on lui demande d'expliquer.
        suivant = verdicts[rang + 1] if rang + 1 < len(verdicts) else None
        explication = expliquer(v, rang, critere_decisif(v, suivant))
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
            # `REC-ROLLOUT-01` — égalité dont AUCUNE zone des deux candidats n'a
            # d'historique de charge (repos infini des deux côtés) : aucun fait
            # ne peut les séparer, l'ordre du catalogue est le seul recours
            # honnête. Nommé pour que la mesure distingue ce cas d'une égalité
            # que l'historique aurait dû trancher.
            "departage_sans_historique": bool(
                reste and tete.rang_sans_catalogue == reste[0].rang_sans_catalogue
                and tete.rang[CRITERES_DU_RANG.index("repos")] == float("-inf")
            ),
            "environnement_actif": environnement.actif,
            "environnement_etat": environnement.etat_catalogue,
            "environnement_identite": environnement.identite,
            # Le FAIT, pas la liste : Mission n'énumère jamais les
            # substitutions. La lignée complète vit dans le détail de séance.
            "environnement_adapte": bool(
                environnement.adaptations.get(tete.template.slug)
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
