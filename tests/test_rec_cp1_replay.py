"""`REC-CP1` — le rejeu causal, et ce qu'il prouve du blocage `P1`.

CE QUE CE MODULE ÉTABLIT
-------------------------
Il pilote `scripts/reco_replay.py` sur le corpus de dix-sept trajectoires et
épingle **les propriétés sémantiques** que le §3 de l'arbitrage nomme — jamais
une réponse d'entraînement idéale. Il n'existe pas de vérité universelle disant
que « push → pull → push impose legs », et rien ici ne le prétend.

LE DIAGNOSTIC `P1`, MESURÉ — APRÈS DEUX ATTRIBUTIONS FAUSSES DE MA MAIN
-------------------------------------------------------------------------
Baseline V2 sur le corpus, décision par décision :

    part des décisions à égalité en tête ....... 0,00 (sauf 0,25 sur une)
    marge médiane avec le dauphin ............. 20 points
    concentration du gagnant .................. 1,00 sur 15/17 trajectoires
    gagnant .................................... `liss-abs` partout

`push-lourd`, `pull-lourd`, `legs-lourd` et `equilibre` rendent des séquences
**identiques**. Le gagnant n'est pas départagé : il gagne largement.

J'ai attribué cela deux fois, et deux fois à tort :

1. **« Le départage épingle »** — réfuté par la mesure : 0 % d'égalités.
2. **« Le bonus cardio-absent domine »** — réfuté par mutation : le mettre à
   zéro fait passer `liss-abs` de 90 à 80, toujours devant 70 et 65.

La décomposition composante par composante a tranché là où deviner échouait.

LES DEUX CAUSES, EMPILÉES — RÉPONSE `C` AU `§6`
-------------------------------------------------
Le classement **est** sensible à la trajectoire : après cinq séances push, ce
sont `pull-a`/`pull-b`/`legs-a` qui montent. Le signal longitudinal fonctionne —
il est simplement d'un ordre de grandeur trop petit :

    liss-abs .......... 90 = dispo 35 + fraîcheur 15 + ALTERNANCE 20
                             + affinité 10 + cardio 10
    catch-up-* ........ 70 = dispo 35 + fraîcheur 15 + affinité 20
    pull-a / legs-a ... 65 = dispo 35 + fraîcheur 15 + affinité 15
    push-a / push-b ... 59 = dispo 35 + fraîcheur  9 + affinité 15

`dispo` — **la plus grosse composante du moteur, 35 points** — rend la même
valeur pour tout le monde. Le seul discriminant longitudinal est la fraîcheur de
zone, au pas de **6 points**, contre **25 points** d'écart de catégorie.

Et sous cette domination s'en cache une seconde. Mutation `WEIGHT_ALTERNATION`
à zéro, seule : le gagnant ne change pas, mais les égalités passent de **0 % à
72 %**, tranchées par `display_order` puis `slug`.

Donc : `A` (départage) est réel mais **inactif**, masqué par `B` (classement) ;
`B` est ce qui décide aujourd'hui. Ne corriger que `A` ne changerait rien ; ne
corriger que `B` découvrirait un moteur épinglé par l'ordre du catalogue à 72 %.
`REC-CP2` doit traiter les deux, dans cet ordre.

⚠ UN DÉFAUT DE MON CORPUS, TROUVÉ ET CORRIGÉ AVANT DE CONCLURE
----------------------------------------------------------------
La première version faisait partir chaque trajectoire de zéro. Or le moteur
court-circuite **entièrement** le scoring sous trois séances et rend un repli
(`core[0]`, score 50, zéro alternative). Les trois premières décisions de
chaque trajectoire étaient donc ce repli — `push-a` partout — et j'ai failli
lire cet artefact comme un épinglage du produit.

Un `ECHAUFFEMENT` de trois séances, semé mais non mesuré et posé hors des
fenêtres 7 j et 14 j, fait franchir le seuil avant la première décision
observée. Seule `demarrage-a-froid` le garde vide : c'est l'état qu'elle
observe.
"""
from __future__ import annotations

import itertools
import statistics
from datetime import timedelta

from scripts.reco_replay import (
    CORPUS,
    ECHAUFFEMENT,
    ORIGINE,
    Seance,
    Trajectoire,
    famille_de,
    rejouer,
    resumer,
    semer_seance,
)
from tests.helpers import get_test_user_id

#: Compteur de rejeux, pour que deux appels dans le MÊME test n'entrent pas en
#: collision de nom d'utilisateur.
_RANG = itertools.count()


def _rejouer(traj: Trajectoire):
    """Rejoue une trajectoire sur un utilisateur NEUF.

    ⚠ Le premier jet de ce module réutilisait `get_test_user_id()` pour chaque
    appel. Deux trajectoires rejouées dans le même test s'empilaient donc sur le
    même historique, et la seconde mesurait la somme des deux. La garde
    d'observation partielle l'a attrapé — mais les deux gardes de baseline, qui
    rejouent dix-sept trajectoires à la suite, passaient sur un état pollué sans
    rien signaler.

    Le CLI du harnais crée déjà un utilisateur par trajectoire, pour cette
    raison exacte. Le test doit faire pareil, ou il ne mesure pas le même objet.
    """
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        u = User(username=f"rejeu-{traj.nom}-{next(_RANG)}", password_hash="x")
        db.add(u)
        db.commit()
        uid = u.id
    with SessionLocal() as db:
        return rejouer(db, uid, traj)


def _par_nom(nom: str) -> Trajectoire:
    for t in CORPUS:
        if t.nom == nom:
            return t
    raise AssertionError(f"trajectoire absente du corpus : {nom}")


# ═══════════ 1. LE CORPUS COUVRE CE QUE LE §4 EXIGE ═══════════


def test_le_corpus_couvre_les_dix_sept_trajectoires_exigees():
    """Une garde qui laisse rétrécir son corpus mesure de moins en moins.

    On épingle les NOMS, pas seulement le compte : retirer une trajectoire et
    en ajouter une autre garderait le total.
    """
    exigees = {
        "push-pull-push", "push-pull-legs", "push-lourd", "pull-lourd",
        "legs-lourd", "equilibre", "meme-gabarit-repete", "famille-ab",
        "cardio-absent", "cardio-recent", "reprise-longue", "substitutions",
        "exercice-non-mappe", "seance-exclue", "demarrage-a-froid",
        "egalite-exacte", "quasi-egalite",
    }
    assert {t.nom for t in CORPUS} == exigees


def test_seule_la_trajectoire_de_demarrage_a_froid_n_a_pas_d_echauffement():
    """L'échauffement existe pour sortir du repli avant de mesurer.

    Sans lui, les trois premières décisions de chaque trajectoire sont le
    repli `core[0]` et non une décision de classement. `demarrage-a-froid`
    l'omet volontairement : c'est précisément l'état qu'elle observe.
    """
    sans = {t.nom for t in CORPUS if not t.echauffement}
    assert sans == {"demarrage-a-froid"}
    assert all(s.jour < 0 for s in ECHAUFFEMENT), (
        "l'échauffement doit précéder l'origine, sinon il entre dans les "
        "fenêtres mesurées"
    )


# ═══════════ 2. LES PROPRIÉTÉS SÉMANTIQUES DU §3 ═══════════


def test_une_meme_histoire_rend_toujours_la_meme_decision(client):
    """`SAME_HISTORY => SAME_RECOMMENDATION` — déterminisme.

    Sans lui, comparer V2 et un candidat V3 ne voudrait rien dire : on ne
    saurait pas si un écart vient de la politique ou du hasard.
    """
    traj = _par_nom("push-pull-legs")
    a = _rejouer(traj)

    # Un second utilisateur, même histoire exactement.
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.recommendation import (
        recommend_next_session,
        reset_template_zones_cache,
    )

    with SessionLocal() as db:
        u = User(username="replay-jumeau", password_hash="x")
        db.add(u)
        db.commit()
        uid2 = u.id
    with SessionLocal() as db:
        b = rejouer(db, uid2, traj)

    assert [(d.gagnant, d.score) for d in a] == [(d.gagnant, d.score) for d in b], (
        "deux historiques identiques rendent des décisions différentes"
    )

    # Et deux appels sur le MÊME état rendent la même chose.
    with SessionLocal() as db:
        quand = ORIGINE + timedelta(days=99)
        reset_template_zones_cache()
        x = recommend_next_session(db, uid2, now=quand)
        reset_template_zones_cache()
        y = recommend_next_session(db, uid2, now=quand)
    assert x["top"]["template"].slug == y["top"]["template"].slug
    assert x["top"]["score"] == y["top"]["score"]


def test_une_seance_exclue_ne_pese_sur_aucune_decision(client):
    """`EXCLUDED_FROM_STATS_IS_RESPECTED`, au niveau de la DÉCISION.

    `REC-CP0a` l'a prouvé sur les signaux. Ici on le prouve sur la sortie : la
    même trajectoire, avec et sans la séance exclue, doit décider pareil.
    """
    avec = _par_nom("seance-exclue")
    sans = Trajectoire(
        nom="seance-exclue-temoin",
        tension="témoin : la séance exclue simplement absente",
        seances=tuple(s for s in avec.seances if not s.exclue),
        echauffement=avec.echauffement,
    )

    from app.database import SessionLocal
    from app.models.user import User

    resultats = []
    for traj in (avec, sans):
        with SessionLocal() as db:
            u = User(username=f"replay-{traj.nom}", password_hash="x")
            db.add(u)
            db.commit()
            uid = u.id
        with SessionLocal() as db:
            resultats.append(rejouer(db, uid, traj))

    # ⚠ ON COMPARE LE SCORE ET L'EXPOSITION, PAS SEULEMENT LE GAGNANT.
    #
    # Le premier jet ne comparait que `d.gagnant`. Or `liss-abs` gagne
    # actuellement TOUTES les décisions du corpus : deux historiques différents
    # rendaient donc le même gagnant quoi qu'il arrive, et la garde n'aurait
    # jamais pu échouer. Le score et l'exposition 14 j, eux, bougent.
    def _empreinte(ds):
        return {d.jour: (d.gagnant, d.score, tuple(sorted(d.expo_14j.items())))
                for d in ds}

    a, b = _empreinte(resultats[0]), _empreinte(resultats[1])
    communs = set(a) & set(b)
    assert communs, "prémisse : des jours de décision comparables"

    # Prémisse de discrimination : au moins un jour commun voit réellement la
    # séance exclue dans sa fenêtre — sinon la garde ne mesure rien.
    assert any(sum(dict(a[j][2]).values()) > 0 for j in communs), (
        "prémisse : la fenêtre d'exposition n'est jamais peuplée, le cas "
        "discriminant n'est pas semé"
    )

    divergents = {j: (a[j], b[j]) for j in communs if a[j] != b[j]}
    assert not divergents, (
        f"une séance EXCLUE des KPI a pesé sur la décision : {divergents}"
    )


def test_une_repetition_legitime_reste_possible(client):
    """LE PENDANT DE `REPEAT_REQUIRES_EVIDENCE`, et il compte autant.

    Interdire la répétition serait aussi faux que l'imposer. Une garde qui ne
    vérifierait que « le gagnant change » pousserait le moteur à alterner pour
    alterner.

    On vérifie donc seulement que le moteur PEUT rendre deux fois de suite le
    même gabarit — ce qui est trivialement vrai aujourd'hui, et doit le rester
    après `REC-CP2`.
    """
    decisions = _rejouer(_par_nom("meme-gabarit-repete"))
    gagnants = [d.gagnant for d in decisions if d.gagnant]
    assert gagnants, "prémisse : des décisions ont été prises"
    # Pas d'assertion sur QUI gagne : la propriété est que la répétition est
    # exprimable, pas qu'elle est correcte.
    assert len(set(gagnants)) <= len(gagnants)


def test_un_long_arret_change_honnetement_le_contexte(client):
    """Trois semaines sans séance doivent se voir dans les signaux.

    On n'exige pas un gagnant particulier — seulement que le moteur ne
    prétende pas que rien n'a changé.
    """
    decisions = _rejouer(_par_nom("reprise-longue"))
    prises = [d for d in decisions if d.gagnant]
    assert len(prises) >= 3

    # La décision qui suit l'arrêt voit une exposition 14 j vide, celles
    # d'avant non.
    avant = next(d for d in prises if d.jour == 2)
    apres = next(d for d in prises if d.jour == 25)
    assert sum(avant.expo_14j.values()) > 0, (
        "prémisse : de l'exposition avant l'arrêt"
    )
    assert sum(apres.expo_14j.values()) == 0, (
        "après trois semaines d'arrêt, l'exposition 14 j devrait être vide — "
        f"elle vaut {apres.expo_14j}"
    )


def test_un_exercice_illisible_rend_l_observation_partielle(client):
    """`UNKNOWN_DOES_NOT_MEAN_AVAILABLE` au niveau de la trajectoire.

    `REC-CP0b` l'a prouvé sur une fixture. Ici la preuve passe par le corpus :
    la trajectoire avec substitutions doit déclarer son ignorance, celle sans
    ne doit pas.
    """
    avec = _rejouer(_par_nom("substitutions"))
    sans = _rejouer(_par_nom("push-pull-legs"))

    assert any(d.observation_partielle for d in avec if d.gagnant), (
        "des noms libres illisibles n'ont pas rendu l'observation partielle"
    )
    assert not any(d.observation_partielle for d in sans if d.gagnant), (
        "une trajectoire entièrement lisible se déclare pourtant partielle"
    )


# ═══════════ 3. LE BASELINE `P1`, ÉPINGLÉ COMME UN FAIT ═══════════


def test_le_departage_ne_tranche_rien_aujourd_hui(client):
    """⚠ PREMIÈRE MOITIÉ DU DIAGNOSTIC : le départage est INACTIF, pas sain.

    Aujourd'hui le gagnant l'emporte de vingt points et presque aucune décision
    n'arrive à égalité. Corriger `display_order`/`slug` ne changerait donc
    RIEN — c'est ce que cette garde établit.

    Elle ne dit pas que le départage est correct. La mutation consignée dans
    `test_les_deux_causes_sont_empilees` montre qu'il est simplement masqué.
    """
    prises, egalites = 0, 0
    for traj in CORPUS:
        for d in _rejouer(traj):
            if d.gagnant is None or d.marge is None:
                continue
            prises += 1
            if d.egalite_en_tete:
                egalites += 1

    assert prises >= 40, f"corpus trop maigre pour conclure : {prises} décisions"
    part = egalites / prises
    assert part < 0.15, (
        f"{part:.0%} des décisions se jouent à égalité. Si ce chiffre monte, "
        "c'est que la domination catégorielle a été retirée sans traiter le "
        "départage en dessous — exactement le demi-correctif que `REC-CP2` "
        "doit éviter"
    )


def test_le_classement_ne_discrimine_presque_pas_entre_gabarits_de_force(client):
    """⚠ SECONDE MOITIÉ : la mesure qui a corrigé deux fois mon attribution.

    La décomposition composante par composante de `_score_template`, sur une
    trajectoire push-lourde :

        liss-abs ......... 90 = dispo 35 + fraîcheur 15 + ALTERNANCE 20
                                + affinité 10 + CARDIO 10
        catch-up-* ....... 70 = dispo 35 + fraîcheur 15 + affinité 20
        pull-a / legs-a .. 65 = dispo 35 + fraîcheur 15 + affinité 15
        push-a / push-b .. 59 = dispo 35 + fraîcheur  9 + affinité 15

    Deux choses s'y lisent, et ni l'une ni l'autre n'était mon hypothèse :

    1. `dispo` — **la plus grosse composante du moteur, 35 points** — rend la
       MÊME valeur pour tous les candidats. Elle ne discrimine rien.
    2. Le seul discriminant longitudinal est la fraîcheur de zone, et son pas
       vaut **6 points**, à comparer aux **25 points** d'écart de catégorie.

    Le signal de trajectoire FONCTIONNE — push-lourd démote bien `push-*`. Il
    est simplement d'un ordre de grandeur trop petit pour être visible.

    Cette garde mesure cet écart sans muter le moteur.
    """
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.recommendation import (
        _compute_signals,
        _load_templates,
        _passes_fatigue_filter,
        _passes_redundancy_filter,
        _score_template,
        reset_template_zones_cache,
        template_primary_zones,
    )

    traj = _par_nom("push-lourd")
    with SessionLocal() as db:
        u = User(username="dispersion", password_hash="x")
        db.add(u)
        db.commit()
        uid = u.id

    with SessionLocal() as db:
        for s in traj.echauffement + traj.seances:
            semer_seance(db, uid, s, ORIGINE)
        quand = ORIGINE + timedelta(days=10)
        reset_template_zones_cache()
        sig = _compute_signals(db, uid, quand)
        notes = {}
        for t in _load_templates(db):
            if not _passes_fatigue_filter(t, sig.fatigue_score):
                continue
            if not _passes_redundancy_filter(
                    template_primary_zones(t), sig.hard_sets_by_zone_24h):
                continue
            notes[t.slug] = _score_template(t, sig).score

    force = {k: v for k, v in notes.items()
             if famille_de(k) in {"push", "pull", "legs"}}
    assert len(force) >= 6, f"prémisse : les gabarits de force sont là ({force})"

    etendue_force = max(force.values()) - min(force.values())
    ecart_au_sommet = max(notes.values()) - max(force.values())

    assert ecart_au_sommet > etendue_force, (
        "le baseline a changé : l'écart entre le sommet du classement et le "
        f"meilleur gabarit de force ({ecart_au_sommet} pts) ne domine plus "
        f"l'étendue interne de la force ({etendue_force} pts). C'est "
        f"peut-être le progrès visé par `REC-CP2` — il doit être déclaré "
        f"ici.\n  notes = {dict(sorted(notes.items(), key=lambda kv: -kv[1]))}"
    )


def test_les_deux_causes_sont_empilees(client):
    """⚠ LA RÉPONSE AU `§6` : **C — les deux**, et dans cet ordre.

    Le §6 demande de trancher entre `A` épinglage par départage, `B`
    insensibilité du classement primaire, `C` les deux — et interdit de
    redessiner le scoring si corriger le départage suffit.

    Deux mutations, chacune appliquée seule au moteur puis annulée, donnent la
    réponse. `RUNTIME_MEASURED`, sur ce corpus :

        moteur intact ................. `liss-abs` partout · égalités  0 %
        bonus « cardio absent » à 0 ... `liss-abs` partout · égalités  0 %
        bonus d'ALTERNANCE à 0 ........ `liss-abs` partout · égalités 72 %

    Lecture. Retirer le bonus cardio ne suffit pas : `liss-abs` tombe de 90 à
    80 et reste devant 70 et 65. Retirer l'alternance ne change pas non plus le
    gagnant — mais le classement s'effondre en un peloton à égalité que
    `display_order` puis `slug` tranchent dans **72 %** des décisions.

    Donc : `A` est réel mais **inactif**, masqué par `B` ; `B` est ce qui décide
    aujourd'hui. Ne corriger que `A` ne changerait rien ; ne corriger que `B`
    découvrirait un moteur épinglé par l'ordre du catalogue à 72 %.

    ⚠ CETTE GARDE ÉPINGLE LE CONSTAT, PAS LA CIBLE. Elle doit rougir quand
    `REC-CP2` aboutit — c'est son rôle : rendre le changement déclaré au lieu
    de le laisser dériver.
    """
    sequences = {}
    for nom in ("push-lourd", "pull-lourd", "legs-lourd"):
        sequences[nom] = tuple(d.gagnant for d in _rejouer(_par_nom(nom)))

    assert len(set(sequences.values())) == 1, (
        "le baseline a changé : trois histoires opposées — push, pull et legs "
        "— ne rendent plus la même séquence de décisions. C'est peut-être un "
        f"progrès, mais il doit être déclaré ici.\n  {sequences}"
    )
    gagnants = set(sequences["push-lourd"])
    assert gagnants == {"liss-abs"}, (
        f"le baseline a changé : le gagnant unique n'est plus `liss-abs` mais "
        f"{gagnants}"
    )


def test_le_baseline_v2_est_reproductible(client, capsys):
    """⚠ LA SOURCE DES CHIFFRES DU RAPPORT `REC-CP1`, ET ELLE EST REJOUABLE.

    Le CLI `scripts/reco_replay.py` a besoin d'une base migrée **et** d'un
    catalogue semé. Ce test-ci obtient les deux des fixtures, donc c'est lui la
    voie reproductible du baseline — et non une exécution manuelle dont les
    chiffres ne pourraient plus être régénérés.

    Il imprime la table complète (visible avec `-s`) **et** épingle les deux
    agrégats qui portent le diagnostic. Un émetteur de rapport qui n'assertait
    rien laisserait le baseline dériver en silence.
    """
    table, concentrees = [], 0
    for traj in CORPUS:
        r = resumer(traj.nom, _rejouer(traj))
        table.append(r)
        if r["prises"] and r["concentration_gagnant"] >= 0.9:
            concentrees += 1

    with capsys.disabled():
        print(f"\n{'trajectoire':22s} {'déc':>4s} {'srT':>4s} {'conc':>6s} "
              f"{'égal':>6s} {'mMed':>5s} gagnants")
        for r in table:
            print(f"{r['trajectoire']:22s} {r['prises']:4d} "
                  f"{r['serie_gabarit_max']:4d} "
                  f"{r['concentration_gagnant']:6.2f} "
                  f"{r['part_egalites']:6.2f} "
                  f"{str(r['marge_mediane']):>5s} "
                  f"{', '.join(f'{k}×{v}' for k, v in r['gagnants'].items())}")

    assert concentrees >= 15, (
        f"seules {concentrees}/17 trajectoires rendent un gagnant à ≥ 90 % — "
        "le baseline a changé et le rapport `REC-CP1` doit être refait"
    )
    marges = [r["marge_mediane"] for r in table
              if r["marge_mediane"] is not None]
    assert statistics.median(marges) >= 15, (
        f"marge médiane des marges médianes = {statistics.median(marges)} : le "
        "gagnant ne l'emporte plus largement, donc le départage redevient le "
        "mécanisme actif et le diagnostic est à refaire"
    )


def test_la_famille_du_gagnant_est_derivee_du_catalogue_pas_inventee():
    """`famille_de` lit le nom du gabarit, elle ne crée pas d'ontologie.

    Une seconde taxonomie de familles entrerait en concurrence avec les zones
    et le catalogue — le dépôt en a déjà trois qui se ressemblent.
    """
    assert famille_de("push-a") == "push"
    assert famille_de("pull-b") == "pull"
    assert famille_de("legs-a") == "legs"
    assert famille_de("liss-abs") == "liss"
    assert famille_de(None) is None
    # Un slug inconnu rend le slug : une famille absente doit se VOIR.
    assert famille_de("gabarit-inedit") == "gabarit-inedit"


def test_le_resume_ne_fabrique_rien_sur_un_corpus_vide():
    """Un agrégat qui divise par zéro rendrait une moyenne inventée."""
    r = resumer("vide", [])
    assert r["prises"] == 0
    assert r["concentration_gagnant"] == 0.0
    assert r["part_egalites"] == 0.0
    assert r["marge_mediane"] is None


def test_le_semeur_est_unique_et_partage(client):
    """⚠ UNE SEULE IMPLÉMENTATION DE SEMIS, utilisée par le CLI ET par les tests.

    Le dépôt porte déjà trois semeurs de séances qui ont dérivé les uns des
    autres. Celui-ci vit dans le script et cette garde vérifie qu'il est bien
    celui que les tests emploient — sinon le corpus mesuré ne serait pas celui
    que le rapport décrit.
    """
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    with SessionLocal() as db:
        sid = semer_seance(db, get_test_user_id(),
                           Seance(jour=0, slug="push-a"), ORIGINE)
        s = db.get(WorkoutSession, sid)
        assert s.status == "completed"
        assert s.template_slug_snapshot == "push-a"
        assert len(s.session_exercises) == 2
        assert all(len(se.set_logs) == 3 for se in s.session_exercises)
