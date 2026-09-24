"""`REC-CP1` — rejeu causal déterministe du moteur de recommandation.

CE QU'IL FAIT
--------------
Il sème une trajectoire d'entraînement complète, puis évalue le moteur à chaque
instant de décision de cette trajectoire, et enregistre **pourquoi** chaque
décision est tombée comme elle est tombée.

POURQUOI IL PEUT ENFIN LE FAIRE
---------------------------------
Avant `REC-CP0a`, rejouer le moteur à une date passée était **impossible sans
mentir** : aucune des douze requêtes du chemin n'était bornée par la date de
décision. Une décision évaluée au 1er mars lisait les séances du 15 mars.

La conception de ce harnais en est directement simplifiée, et c'est la preuve
que la correction porte : **on sème toute la trajectoire d'un coup**, puis on
fait avancer `now`. Si la causalité n'était pas tenue, chaque décision verrait
l'historique entier et toutes les décisions d'une trajectoire seraient
identiques — ce qui se verrait immédiatement.

Un harnais contraint de semer incrémentalement pour éviter la fuite aurait
masqué le défaut au lieu de le mesurer.

CE QU'IL N'EST PAS
-------------------
Il n'encode **aucune vérité d'entraînement**. Il n'existe pas de réponse
universelle disant que « push → pull → push impose legs ». Les trajectoires
mettent en tension des **propriétés sémantiques** — une répétition
doit-elle s'expliquer, une égalité peut-elle s'éterniser — pas un résultat
attendu.

Il n'invente **aucun seuil**. Les agrégats servent à comparer **V2** et un
**candidat V3** sur le MÊME corpus. La variété n'est pas la justesse.
"""
from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta

# ═══════════════════════ 1. LE CORPUS ═══════════════════════

#: Origine fixe. Un harnais dont les résultats bougent avec l'horloge ne
#: compare rien d'un jour sur l'autre.
ORIGINE = datetime(2026, 3, 2, 18, 0, tzinfo=UTC)

#: Les utilisateurs de rejeu ne se connectent jamais : ils n'existent que le
#: temps d'une mesure. On ne leur calcule donc pas un vrai hachage — mais on ne
#: pose pas non plus un littéral dans un argument nommé `password_hash`, que
#: ruff (`S106`) et bandit (`B106`) signalent tous deux à raison.
HACHAGE_INUTILISABLE = "-"

#: Les séances sont posées à 18 h, les décisions prises à 12 h le même jour.
#: Une décision au jour J voit donc les séances jusqu'au jour J-1 inclus, et
#: jamais celle du jour J — ce que « je me demande quoi faire aujourd'hui »
#: signifie réellement.
HEURE_DECISION = timedelta(hours=-6)


@dataclass(frozen=True)
class Seance:
    jour: int
    slug: str
    ressenti: str = "good"
    concentration: str = "high"
    #: Nom libre substitué au premier exercice — la source vivante d'exercice
    #: illisible (`sessions.py` accepte un texte arbitraire).
    substitution: str | None = None
    exclue: bool = False


@dataclass(frozen=True)
class Trajectoire:
    nom: str
    #: Ce que cette trajectoire met en TENSION. Jamais un résultat attendu :
    #: une trajectoire qui encode sa propre réponse ne mesure rien.
    tension: str
    seances: tuple[Seance, ...]
    #: ⚠ ÉCHAUFFEMENT : semé mais **non mesuré**.
    #:
    #: Sans lui, la mesure était fausse. `recommend_next_session` court-circuite
    #: entièrement le scoring en démarrage à froid
    #: (`< COLD_START_LIFETIME_SESSIONS = 3` séances) et rend un REPLI :
    #: `core[0]`, score 50, zéro alternative. Toutes mes trajectoires partant
    #: de zéro, les trois premières décisions de chacune étaient donc ce repli
    #: — `push-a` partout, quelle que soit l'histoire.
    #:
    #: Ce n'était pas un défaut du produit : c'était mon corpus qui produisait
    #: un état non représentatif et le laissait dominer la mesure. Une
    #: trajectoire qui veut observer le CLASSEMENT doit d'abord en sortir.
    #:
    #: `demarrage-a-froid` est la seule trajectoire qui garde un échauffement
    #: vide, parce que c'est précisément l'état qu'elle observe.
    echauffement: tuple[Seance, ...] = ()


def _serie(slugs: list[str], pas: int = 2, **kw) -> tuple[Seance, ...]:
    return tuple(Seance(jour=i * pas, slug=s, **kw) for i, s in enumerate(slugs))


#: Trois séances ANTÉRIEURES à l'origine, semées mais jamais mesurées. Elles
#: font franchir `COLD_START_LIFETIME_SESSIONS` avant la première décision
#: observée, sans rien dire de la trajectoire elle-même : elles sont posées
#: assez loin (30 à 26 jours avant) pour être hors des fenêtres 7 j et 14 j.
ECHAUFFEMENT = (
    Seance(jour=-30, slug="push-a"),
    Seance(jour=-28, slug="pull-a"),
    Seance(jour=-26, slug="legs-a"),
)


#: ⚠ DIX-SEPT TRAJECTOIRES, PAS UNE HISTOIRE IDÉALISÉE.
#:
#: `§4` les nomme. Elles couvrent ce qui FAIT diverger un moteur : répétition,
#: déséquilibre, alternance de famille, reprise, substitution, exercice non
#: mappé, séance exclue, démarrage à froid, égalité.
CORPUS: tuple[Trajectoire, ...] = (
    Trajectoire("push-pull-push", "la 3e séance ré-implique les zones de la 1re",
                _serie(["push-a", "pull-a", "push-a", "pull-a", "push-a"]), ECHAUFFEMENT),
    Trajectoire("push-pull-legs", "rotation complète des trois familles",
                _serie(["push-a", "pull-a", "legs-a", "push-b", "pull-b", "legs-b"]), ECHAUFFEMENT),
    Trajectoire("push-lourd", "une famille domine l'exposition 14 j",
                _serie(["push-a", "push-b", "push-a", "push-b", "push-a"]), ECHAUFFEMENT),
    Trajectoire("pull-lourd", "idem, autre famille — le biais doit être symétrique",
                _serie(["pull-a", "pull-b", "pull-a", "pull-b", "pull-a"]), ECHAUFFEMENT),
    Trajectoire("legs-lourd", "idem, zones à récupération longue (72 h)",
                _serie(["legs-a", "legs-b", "legs-a", "legs-b", "legs-a"]), ECHAUFFEMENT),
    Trajectoire("equilibre", "exposition répartie sur les six gabarits de base",
                _serie(["push-a", "pull-a", "legs-a", "push-b", "pull-b", "legs-b",
                        "push-a", "pull-a", "legs-a"]), ECHAUFFEMENT),
    Trajectoire("meme-gabarit-repete", "le MÊME gabarit, encore et encore",
                _serie(["push-a"] * 6), ECHAUFFEMENT),
    Trajectoire("famille-ab", "alternance A/B dans une seule famille",
                _serie(["push-a", "push-b", "push-a", "push-b"]), ECHAUFFEMENT),
    Trajectoire("cardio-absent", "aucune séance cardio sur toute la fenêtre",
                _serie(["push-a", "pull-a", "legs-a", "push-b", "pull-b"]), ECHAUFFEMENT),
    Trajectoire("cardio-recent", "une séance cardio vient d'avoir lieu",
                _serie(["push-a", "pull-a", "liss-only", "legs-a"]), ECHAUFFEMENT),
    Trajectoire("reprise-longue", "trois semaines d'arrêt puis reprise",
                (Seance(0, "push-a"), Seance(2, "pull-a"),
                 Seance(25, "legs-a"), Seance(27, "push-a")), ECHAUFFEMENT),
    Trajectoire("substitutions", "noms libres illisibles par le classifieur",
                (Seance(0, "push-a", substitution="Zorglub press oblique 47°"),
                 Seance(2, "pull-a", substitution="Machin tirage bizarre"),
                 Seance(4, "legs-a"), Seance(6, "push-b")), ECHAUFFEMENT),
    Trajectoire("exercice-non-mappe", "un seul exercice illisible, le reste lisible",
                (Seance(0, "push-a"), Seance(2, "pull-a",
                                             substitution="Appareil sans nom connu"),
                 Seance(4, "legs-a"), Seance(6, "pull-b")), ECHAUFFEMENT),
    Trajectoire("seance-exclue", "une séance retirée des KPI ne doit rien peser",
                (Seance(0, "push-a"), Seance(2, "push-b", exclue=True),
                 Seance(4, "pull-a"), Seance(6, "legs-a")), ECHAUFFEMENT),
    Trajectoire("demarrage-a-froid", "moins de trois séances dans toute la vie",
                _serie(["push-a", "pull-a"])),  # PAS d'échauffement : c'est l'état observé
    Trajectoire("egalite-exacte", "deux séances anciennes, peu de signal récent",
                (Seance(0, "push-a"), Seance(1, "pull-a")), ECHAUFFEMENT),
    Trajectoire("quasi-egalite", "exposition presque symétrique entre familles",
                _serie(["push-a", "pull-a", "push-b", "pull-b"]), ECHAUFFEMENT),
)


# ═══════════════════════ 2. LE SEMIS ═══════════════════════


def semer_seance(db, user_id: int, s: Seance, origine: datetime) -> int:
    """Persiste une séance terminée, attachée au vrai gabarit du catalogue.

    ⚠ UNE SEULE IMPLÉMENTATION, utilisée par le CLI **et** par les tests. Une
    seconde version dériverait — le dépôt en a trois exemples documentés.
    """
    from sqlalchemy import select

    from app.models.catalog import WorkoutTemplate
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    quand = origine + timedelta(days=s.jour)
    tpl = db.execute(
        select(WorkoutTemplate).where(WorkoutTemplate.slug == s.slug)
    ).scalar_one()

    seance = WorkoutSession(
        user_id=user_id,
        template_id=tpl.id,
        template_slug_snapshot=tpl.slug,
        template_name_snapshot=tpl.name,
        started_at=quand,
        ended_at=quand + timedelta(hours=1),
        status="completed",
        concentration=s.concentration,
        global_state=s.ressenti,
        excluded_from_stats=s.exclue,
    )
    # ⚠ TOUS LES EXERCICES DU GABARIT, PAS LES DEUX PREMIERS.
    #
    # `REC-CP2` — la première version en posait deux, et cela rendait le corpus
    # incapable de juger une politique fondée sur la couverture.
    #
    # Mesuré : `legs-a` compte SEPT exercices, et les cinq ignorés portaient
    # tout le travail de `core` et de `calves`. Le corpus ne servait donc que
    # sept zones sur onze — `core`, `calves`, `delt_lat` et `delt_post`
    # restaient à zéro quoi que fasse l'utilisateur. Or `liss-abs` a pour
    # unique zone `core` : il était structurellement, et à jamais, « la zone la
    # plus délaissée ».
    #
    # Une séance terminée pose les exercices de son gabarit. Tronquer, c'était
    # fabriquer un déficit permanent puis le mesurer.
    for pos, ex in enumerate(sorted(tpl.exercises, key=lambda e: e.position),
                             start=1):
        se = SessionExercise(
            exercise_code_snapshot=ex.code,
            exercise_name_snapshot=ex.name,
            position=pos,
            success_score=80,
        )
        # Le nom libre ne remplace que le PREMIER exercice : une séance dont
        # tout est illisible ne distingue pas « partiel » de « inconnu ».
        if s.substitution and pos == 1:
            se.substituted_name = s.substitution
        for i in range(1, 4):
            se.set_logs.append(SetLog(kind="work", set_index=i,
                                      weight_kg=50, reps=10, completed=True))
        seance.session_exercises.append(se)

    db.add(seance)
    db.commit()
    return seance.id


# ═══════════════════════ 3. LE REJEU ═══════════════════════

#: Les familles de mouvement, dérivées du slug. Ce n'est pas une ontologie
#: nouvelle : c'est la nomenclature du catalogue, lue telle qu'elle est.
def famille_de(slug: str | None) -> str | None:
    if not slug:
        return None
    for prefixe in ("push", "pull", "legs", "liss", "short", "catch-up",
                    "full-body"):
        if slug.startswith(prefixe):
            return prefixe
    return slug


@dataclass
class Decision:
    """Une décision, et de quoi expliquer POURQUOI elle est tombée ainsi."""

    jour: int
    gagnant: str | None
    famille: str | None
    score: int | None
    alternatives: tuple[str, ...] = ()
    #: Marge avec le dauphin. `None` s'il n'y a pas de dauphin.
    marge: int | None = None
    #: ⚠ LA MÉTRIQUE QUI PORTE LE DIAGNOSTIC `P1` : le gagnant et son dauphin
    #: avaient-ils le MÊME score ? Si oui, ce n'est pas un signal qui a
    #: tranché, c'est `display_order` puis `slug`.
    egalite_en_tete: bool = False
    phrase: str | None = None
    repli: bool = False
    demarrage_a_froid: bool = False
    #: Contexte longitudinal, pour dire quelle preuve aurait PU peser.
    jours_depuis_meme_gabarit: int | None = None
    jours_depuis_meme_famille: int | None = None
    expo_14j: dict[str, int] = field(default_factory=dict)
    familles_recentes: tuple[str, ...] = ()
    observation_partielle: bool = False


def _tranchee_par_le_catalogue(reco: dict, marge: int | None) -> bool:
    """La décision a-t-elle été tranchée par l'ordre du catalogue ?

    ⚠ LA MÉTRIQUE DOIT VOULOIR DIRE LA MÊME CHOSE DES DEUX CÔTÉS, sinon la
    comparaison V2/V3 n'en est pas une.

    V2 additionne six termes en un entier borné : deux candidats à score égal
    n'ont pas été départagés par une preuve, mais par `display_order` puis
    `slug`. V3 n'a pas de somme — il rend la réponse directement, en comparant
    les clés lexicographiques privées de leurs deux derniers recours.

    Les deux mesurent donc la même propriété, par le seul moyen dont chaque
    politique dispose.
    """
    tranche = reco["context"].get("departage_par_catalogue")
    if tranche is not None:
        return bool(tranche)
    return marge == 0


def _decision_de(jour: int, reco: dict | None, signaux,
                 vu_gabarit: dict, vu_famille: dict) -> Decision:
    if reco is None:
        return Decision(jour=jour, gagnant=None, famille=None, score=None)

    top, alts = reco["top"], reco["alternatives"]
    slug = top["template"].slug
    fam = famille_de(slug)
    marge = (top["score"] - alts[0]["score"]) if alts else None
    return Decision(
        jour=jour,
        gagnant=slug,
        famille=fam,
        score=top["score"],
        alternatives=tuple(a["template"].slug for a in alts),
        marge=marge,
        egalite_en_tete=_tranchee_par_le_catalogue(reco, marge),
        phrase=top["phrase"],
        repli=not alts,  # le repli ne rend JAMAIS d'alternative
        demarrage_a_froid=bool(reco["context"].get("cold_start")),
        jours_depuis_meme_gabarit=(
            jour - vu_gabarit[slug] if slug in vu_gabarit else None),
        jours_depuis_meme_famille=(
            jour - vu_famille[fam] if fam in vu_famille else None),
        expo_14j=dict(sorted(signaux.hard_sets_14d_by_zone.items())),
        familles_recentes=tuple(
            famille_de(z[0]) if z else None
            for z in signaux.recent_strength_zones_by_session),
        observation_partielle=signaux.observation_partielle,
    )


def politique(nom: str):
    """La politique de recommandation à rejouer, par nom.

    `REC-CP2` — le harnais devient un banc à deux politiques. Résolution
    **paresseuse** : importer les moteurs au chargement du module casserait le
    corpus sous pytest, dont le conftest purge `app.*` entre les tests.
    """
    if nom == "v2":
        from app.services.recommendation import recommend_next_session
        return recommend_next_session
    if nom == "v3":
        from app.services.recommendation_v3 import recommander_v3
        return recommander_v3
    raise ValueError(f"politique inconnue : {nom!r}")


POLITIQUES = ("v2", "v3")


def rejouer(db, user_id: int, traj: Trajectoire, *,
            origine: datetime = ORIGINE,
            nom_politique: str = "v2") -> list[Decision]:
    """Sème la trajectoire, puis décide à chaque instant de décision.

    Le semis est fait **en une fois**. C'est licite depuis `REC-CP0a` — et
    c'est aussi un test de cette correction : si une borne manquait, toutes
    les décisions d'une trajectoire seraient identiques.
    """
    from app.services.recommendation import (
        _compute_signals,
        reset_template_zones_cache,
    )

    recommander = politique(nom_politique)

    for s in traj.echauffement:
        semer_seance(db, user_id, s, origine)
    for s in traj.seances:
        semer_seance(db, user_id, s, origine)

    vu_gabarit: dict[str, int] = {}
    vu_famille: dict[str, int] = {}
    decisions: list[Decision] = []

    for s in traj.seances:
        quand = origine + timedelta(days=s.jour) + HEURE_DECISION
        reset_template_zones_cache()
        reco = recommander(db, user_id, now=quand)
        signaux = _compute_signals(db, user_id, quand)
        decisions.append(_decision_de(s.jour, reco, signaux,
                                      vu_gabarit, vu_famille))

        # La séance de ce jour a eu lieu APRÈS la décision.
        vu_gabarit[s.slug] = s.jour
        f = famille_de(s.slug)
        if f:
            vu_famille[f] = s.jour

    return decisions


def rejouer_en_boucle(db, user_id: int, *, nom_politique: str = "v2",
                      nb: int = 10, pas: int = 2,
                      origine: datetime = ORIGINE,
                      amorce: tuple[Seance, ...] = ECHAUFFEMENT
                      ) -> list[Decision]:
    """⚠ BOUCLE FERMÉE : L'UTILISATEUR **SUIT** LA RECOMMANDATION.

    Pourquoi ce mode existe, et pourquoi son absence faussait la mesure.

    Les dix-sept trajectoires sont en **boucle ouverte** : l'historique est
    écrit d'avance et le conseil n'est jamais suivi. Elles mesurent donc une
    seule chose — la sensibilité de la décision à l'histoire — et elles la
    mesurent bien.

    Mais elles ne peuvent pas mesurer la plainte de dogfood, qui porte sur
    l'ÉVOLUTION : « la recommandation reste bloquée sur le même type de séance ».
    Pire, elles la simulent artificiellement : un gabarit recommandé mais jamais
    effectué reste éternellement « jamais fait », donc éternellement le plus
    ancien au départage, donc éternellement gagnant. Le blocage observé était en
    partie celui du corpus, pas celui de la politique.

    Ici, chaque décision est **exécutée** avant la suivante. Une politique saine
    doit alors se déplacer d'elle-même : la zone qu'elle vient de servir cesse
    d'être la plus délaissée. Une politique qui répète encore en boucle fermée
    répète pour de bon.
    """
    from app.services.recommendation import (
        _compute_signals,
        reset_template_zones_cache,
    )

    recommander = politique(nom_politique)
    for s in amorce:
        semer_seance(db, user_id, s, origine)

    vu_gabarit: dict[str, int] = {}
    vu_famille: dict[str, int] = {}
    decisions: list[Decision] = []

    for i in range(nb):
        jour = i * pas
        quand = origine + timedelta(days=jour) + HEURE_DECISION
        reset_template_zones_cache()
        reco = recommander(db, user_id, now=quand)
        signaux = _compute_signals(db, user_id, quand)
        d = _decision_de(jour, reco, signaux, vu_gabarit, vu_famille)
        decisions.append(d)

        if d.gagnant is None:
            continue
        # La séance a lieu APRÈS la décision, le même jour.
        semer_seance(db, user_id, Seance(jour=jour, slug=d.gagnant), origine)
        vu_gabarit[d.gagnant] = jour
        if d.famille:
            vu_famille[d.famille] = jour

    return decisions


# ═══════════════════════ 4. LES AGRÉGATS ═══════════════════════


def _serie_max(valeurs) -> int:
    """La plus longue suite consécutive de valeurs identiques."""
    plus_longue = courante = 0
    precedente = object()
    for v in valeurs:
        if v is None:
            precedente, courante = object(), 0
            continue
        courante = courante + 1 if v == precedente else 1
        precedente = v
        plus_longue = max(plus_longue, courante)
    return plus_longue


def resumer(nom: str, decisions: list[Decision]) -> dict:
    prises = [d for d in decisions if d.gagnant]
    gagnants = [d.gagnant for d in prises]
    marges = [d.marge for d in prises if d.marge is not None]
    return {
        "trajectoire": nom,
        "decisions": len(decisions),
        "prises": len(prises),
        "serie_gabarit_max": _serie_max(d.gagnant for d in decisions),
        "serie_famille_max": _serie_max(d.famille for d in decisions),
        "concentration_gagnant": (
            round(Counter(gagnants).most_common(1)[0][1] / len(gagnants), 3)
            if gagnants else 0.0),
        "part_egalites": (
            round(sum(1 for d in prises if d.egalite_en_tete) / len(prises), 3)
            if prises else 0.0),
        "marge_mediane": statistics.median(marges) if marges else None,
        "marge_min": min(marges) if marges else None,
        "gagnants": dict(Counter(gagnants)),
        "familles": dict(Counter(d.famille for d in prises)),
        "raisons": dict(Counter(d.phrase for d in prises)),
        "demarrages_a_froid": sum(1 for d in prises if d.demarrage_a_froid),
        "observations_partielles": sum(
            1 for d in prises if d.observation_partielle),
    }


# ═══════════════════════ 5. CLI ═══════════════════════


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json", action="store_true",
                   help="sortie brute, décision par décision")
    p.add_argument("--trajectoire", help="n'en rejouer qu'une, par nom")
    p.add_argument("--politique", choices=POLITIQUES, default="v2",
                   help="moteur à rejouer (défaut : v2, celui de production)")
    args = p.parse_args()

    from app.database import SessionLocal
    from app.models.user import User

    choisies = [t for t in CORPUS
                if not args.trajectoire or t.nom == args.trajectoire]
    if not choisies:
        print(f"aucune trajectoire nommée « {args.trajectoire} »")
        return 1

    tout = []
    for traj in choisies:
        # ⚠ UN UTILISATEUR NEUF PAR TRAJECTOIRE. Les réutiliser mélangerait les
        # historiques et rendrait chaque mesure dépendante de l'ordre.
        with SessionLocal() as db:
            u = User(username=f"replay-{traj.nom}",
                     password_hash=HACHAGE_INUTILISABLE)
            db.add(u)
            db.commit()
            uid = u.id
        with SessionLocal() as db:
            decisions = rejouer(db, uid, traj,
                                nom_politique=args.politique)
        tout.append((traj, decisions))

    if args.json:
        print(json.dumps(
            [{"trajectoire": t.nom, "tension": t.tension,
              "decisions": [asdict(d) for d in ds]} for t, ds in tout],
            ensure_ascii=False, indent=1))
        return 0

    print(f"{'trajectoire':22s} {'déc':>4s} {'srT':>4s} {'srF':>4s} "
          f"{'conc':>6s} {'égal':>6s} {'mMed':>5s} gagnants")
    for traj, decisions in tout:
        r = resumer(traj.nom, decisions)
        print(f"{r['trajectoire']:22s} {r['prises']:4d} "
              f"{r['serie_gabarit_max']:4d} {r['serie_famille_max']:4d} "
              f"{r['concentration_gagnant']:6.2f} {r['part_egalites']:6.2f} "
              f"{str(r['marge_mediane']):>5s} "
              f"{', '.join(f'{k}×{v}' for k, v in r['gagnants'].items())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
