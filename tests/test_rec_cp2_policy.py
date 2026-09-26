"""`REC-CP2` — la politique V3, et sa comparaison en ombre avec V2.

CE QUE CE MODULE N'AUTORISE PAS
---------------------------------
V3 ne pilote **rien**. Une garde de ce fichier le vérifie explicitement : aucune
surface, aucune route, aucune création de séance ne lit `recommendation_v3`.
La promotion passe par la porte du `§12`, pas par une importation discrète.

CE QU'IL COMPARE, ET CE QU'IL REFUSE DE CONCLURE
--------------------------------------------------
⚠ **La variété n'est pas la justesse** (`§11`). Ce module n'affirme nulle part
que V3 est meilleur parce qu'il propose des séances plus variées.

Ce qu'il affirme est plus étroit et démontrable : `REC-CP1` a mesuré une
défaillance précise — *quatre histoires opposées produisent la même séquence de
décisions* — et V3 doit la corriger. Exiger que `push-lourd` et `pull-lourd`
divergent n'est pas un culte de la variété : c'est la réparation du défaut
prouvé. Aucune garde ici ne dit quelle séance « devrait » gagner.
"""
from __future__ import annotations

import itertools
from datetime import timedelta

from scripts.reco_replay import (
    CORPUS,
    ORIGINE,
    Seance,
    Trajectoire,
    rejouer,
    resumer,
    semer_seance,
)

_RANG = itertools.count()


def _utilisateur(nom: str) -> int:
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        u = User(username=f"{nom}-{next(_RANG)}", password_hash="x")
        db.add(u)
        db.commit()
        return u.id


def _rejouer(traj: Trajectoire, nom_politique: str):
    """Un utilisateur NEUF par rejeu — deux trajectoires sur le même compte
    empileraient leurs historiques et la seconde mesurerait la somme."""
    from app.database import SessionLocal

    uid = _utilisateur(f"cp2-{traj.nom}")
    with SessionLocal() as db:
        return rejouer(db, uid, traj, nom_politique=nom_politique)


def _par_nom(nom: str) -> Trajectoire:
    for t in CORPUS:
        if t.nom == nom:
            return t
    raise AssertionError(f"trajectoire absente du corpus : {nom}")


# ═══════════ 1. V3 NE PILOTE RIEN ═══════════


def test_la_politique_servie_est_declaree_en_un_seul_endroit():
    """⚠ REPOINTÉE PAR `REC-CP4` — ON ÉPINGLE CE QUI SERT, PAS CE QUI S'IMPORTE.

    Cette garde interdisait toute IMPORTATION de V3 hors du banc. C'était le
    bon proxy tant qu'aucune composition n'existait : importer, c'était servir.

    `REC-CP4` introduit un point d'entrée unique — `advice_memory.recommander`
    — qui compose une politique et une mémoire. Il référence forcément les
    deux politiques, et pourtant il n'en sert qu'une, nommée par une constante.

    Épingler cette constante est **plus fort** que l'ancien proxy : un import
    ne dit rien de ce qui arrive à l'utilisateur, une constante de service dit
    tout. Le « basculement silencieux » que le `§12` interdit est devenu
    impossible sans venir modifier cette ligne.
    """
    from app.services import advice_memory

    assert advice_memory.POLITIQUE_SERVIE in advice_memory.POLITIQUES
    assert advice_memory.POLITIQUE_SERVIE == "v3", (
        "la politique servie a changé — c'est la porte de promotion, et elle "
        "doit être franchie explicitement, preuves à l'appui"
    )


def test_v3_n_est_reference_que_par_le_banc_et_la_composition():
    """Le registre unique des lecteurs de V3.

    On cherche les IMPORTATIONS réelles, pas une impression de propreté. Le
    harnais de mesure, ses tests et le point de composition sont les seuls
    lecteurs légitimes — et `advice_memory` n'en sert V3 que si la constante
    ci-dessus le dit.
    """
    import pathlib

    racine = pathlib.Path(__file__).resolve().parents[1]
    # ⚠ LE REGISTRE UNIQUE DES LECTEURS AUTORISÉS DE V3.
    #
    # Il n'en existe pas de second : `REC-CP3` a d'abord écrit sa propre copie
    # de cette liste, et deux registres du même fait divergent toujours. Un
    # nouveau lecteur se déclare ICI, et la garde l'exige en rougissant.
    autorises = {
        "scripts/reco_replay.py",
        "tests/test_rec_cp2_policy.py",
        # `REC-CP3` — lit la trace d'explication produite par V3.
        "tests/test_rec_cp3_explication.py",
        "app/services/recommendation_v3.py",
        # `REC-CP4` — le point de composition unique. Il RÉFÉRENCE les deux
        # politiques et n'en SERT qu'une, nommée par `POLITIQUE_SERVIE`, que
        # la garde précédente épingle.
        "app/services/advice_memory.py",
        "tests/test_rec_cp4_comparaison.py",
        "tests/test_rec_cp4_memoire_conseil.py",
        # `REC-CP5` — parité d'explication. Lit la trace de V3, ne touche
        # jamais son classement : une garde de ce module l'épingle.
        "tests/test_rec_cp5_parite_explication.py",
    }
    coupables = []
    for f in list((racine / "app").rglob("*.py")) + \
            list((racine / "tests").rglob("*.py")) + \
            list((racine / "scripts").rglob("*.py")):
        rel = f.relative_to(racine).as_posix()
        if rel in autorises:
            continue
        if "recommendation_v3" in f.read_text(encoding="utf-8"):
            coupables.append(rel)

    assert not coupables, (
        "V3 est référencé hors du banc de mesure — la promotion passe par la "
        f"porte du §12, pas par une importation : {coupables}"
    )


# ═══════════ 2. LA CAUSALITÉ DE LA NOUVELLE ENTRÉE ═══════════


def test_le_dernier_passage_ne_voit_jamais_le_futur(client):
    """⚠ `REC-CP2` BRANCHE UNE NOUVELLE REQUÊTE DANS LE MOTEUR.

    `compute_template_kpis` alimente désormais le départage par ancienneté. Elle
    n'avait **aucune borne haute** : rejouée à une date passée, elle aurait rendu
    la dernière séance FUTURE, et le départage aurait tranché sur le futur —
    exactement la fuite que `REC-CP0a` a fermée ailleurs.
    """
    from app.database import SessionLocal
    from app.services.kpis import compute_template_kpis

    uid = _utilisateur("kpis-causal")
    with SessionLocal() as db:
        semer_seance(db, uid, Seance(jour=0, slug="push-a"), ORIGINE)
        semer_seance(db, uid, Seance(jour=10, slug="pull-a"), ORIGINE)

    decision = ORIGINE + timedelta(days=5)
    with SessionLocal() as db:
        borne = {k.slug: k.last_done_at
                 for k in compute_template_kpis(db, user_id=uid,
                                                until=decision)}
        libre = {k.slug: k.last_done_at
                 for k in compute_template_kpis(db, user_id=uid)}

    assert "push-a" in borne, "prémisse : la séance passée est bien vue"
    assert "pull-a" not in borne, (
        f"une décision au J+5 voit une séance du J+10 : {borne}"
    )
    assert "pull-a" in libre, (
        "prémisse : sans borne, la séance future est bien visible — sinon "
        "cette garde ne mesurerait pas la borne"
    )


# ═══════════ 3. LES PROPRIÉTÉS SÉMANTIQUES DE V3 ═══════════


def test_une_meme_histoire_rend_toujours_la_meme_decision_v3(client):
    """`SAME_HISTORY => SAME_RECOMMENDATION`. Aucun aléatoire (`§10`)."""
    traj = _par_nom("push-pull-legs")
    a = _rejouer(traj, "v3")
    b = _rejouer(traj, "v3")
    assert [(d.gagnant, d.score) for d in a] == [(d.gagnant, d.score) for d in b]


def test_une_seance_exclue_ne_pese_sur_aucune_decision_v3(client):
    """`EXCLUDED_FROM_STATS_IS_RESPECTED`, y compris sur la nouvelle entrée.

    `compute_template_kpis` filtre déjà les séances exclues — cette garde le
    vérifie **à travers V3** plutôt que de faire confiance à la lecture.
    """
    from app.database import SessionLocal

    avec = _par_nom("seance-exclue")
    sans = Trajectoire(
        nom="seance-exclue-temoin-v3",
        tension="témoin : la séance exclue simplement absente",
        seances=tuple(s for s in avec.seances if not s.exclue),
        echauffement=avec.echauffement,
    )

    empreintes = []
    for traj in (avec, sans):
        uid = _utilisateur(f"cp2-excl-{traj.nom}")
        with SessionLocal() as db:
            ds = rejouer(db, uid, traj, nom_politique="v3")
        empreintes.append({
            d.jour: (d.gagnant, d.score,
                     tuple(sorted(d.expo_14j.items())))
            for d in ds
        })

    a, b = empreintes
    communs = set(a) & set(b)
    assert communs, "prémisse : des jours de décision comparables"
    assert any(sum(dict(a[j][2]).values()) > 0 for j in communs), (
        "prémisse : la fenêtre d'exposition n'est jamais peuplée"
    )
    divergents = {j: (a[j], b[j]) for j in communs if a[j] != b[j]}
    assert not divergents, (
        f"une séance EXCLUE des KPI a pesé sur la décision V3 : {divergents}"
    )


def test_un_exercice_illisible_ne_fabrique_pas_un_deficit_maximal(client):
    """⚠ LE PIÈGE SYMÉTRIQUE DE `REC-CP0b`, DU CÔTÉ DE LA COUVERTURE.

    `REC-CP0b` a corrigé « zone inconnue ⇒ fraîcheur maximale ». Le critère de
    couverture de V3 porte le même risque **en miroir** : une zone à zéro série
    parce qu'un nom d'exercice est illisible passerait pour la plus
    sous-servie, et épinglerait la recommandation dans l'autre sens.

    Ne pas savoir doit rester neutre, jamais maximal.
    """
    from app.services.recommendation import Signals
    from app.services.recommendation_v3 import (
        DEFICIT_INCONNU,
        _deficit_de_couverture,
    )

    def _signaux(**kw):
        base = dict(
            cold_start=False, availability_by_zone={}, hours_since_last_by_zone={},
            last_strength_session_zones=[], recent_strength_zones_by_session=[],
            hard_sets_by_zone_recent={}, hard_sets_by_zone_24h={},
            kinds_recent=[], days_since_last_cardio=None,
            days_since_last_strength=None, fatigue_score=0.0, soft_restart=False,
            median_hard_sets_14d=10.0, hard_sets_14d_by_zone={},
            observation_partielle=False,
        )
        base.update(kw)
        return Signals(**base)

    zones = ("pecs",)
    mesure = _signaux(hard_sets_14d_by_zone={"lats": 10})
    ignorance = _signaux(hard_sets_14d_by_zone={"lats": 10},
                         observation_partielle=True)

    assert _deficit_de_couverture(zones, mesure) == 1.0, (
        "prémisse : une zone RÉELLEMENT à zéro est en déficit maximal"
    )
    assert _deficit_de_couverture(zones, ignorance) == DEFICIT_INCONNU, (
        "une zone à zéro par ignorance est traitée comme un déficit mesuré"
    )
    assert DEFICIT_INCONNU < 1.0, "l'ignorance ne doit jamais valoir la mesure"


def test_sans_base_de_comparaison_le_critere_de_couverture_se_tait(client):
    """Une médiane nulle ne doit pas déclarer tout le monde en déficit maximal.

    C'est le cas du tout premier jour : aucune exposition, donc aucune base.
    Un critère qui crierait « tout manque » y prendrait le pas sur la
    récupération et la récence, qui elles ont du sens.
    """
    from app.services.recommendation import Signals
    from app.services.recommendation_v3 import _deficit_de_couverture

    vide = Signals(
        cold_start=True, availability_by_zone={}, hours_since_last_by_zone={},
        last_strength_session_zones=[], recent_strength_zones_by_session=[],
        hard_sets_by_zone_recent={}, hard_sets_by_zone_24h={}, kinds_recent=[],
        days_since_last_cardio=None, days_since_last_strength=None,
        fatigue_score=0.0, soft_restart=False, median_hard_sets_14d=0.0,
        hard_sets_14d_by_zone={}, observation_partielle=False,
    )
    assert _deficit_de_couverture(("pecs", "triceps"), vide) == 0.0


def test_la_repetition_reste_possible_mais_doit_etre_portee(client):
    """`REPEAT_REQUIRES_EVIDENCE`, et son pendant.

    Interdire la répétition serait aussi faux que l'imposer. V3 la pénalise par
    défaut et **lève** la pénalité quand la couverture la porte. On vérifie les
    deux branches de cette règle, pas seulement la commode.
    """
    from app.services.recommendation_v3 import (
        MEME_FAMILLE,
        MEME_GABARIT,
        NOUVEAU,
        _penalite_de_repetition,
    )

    class _T:
        def __init__(self, slug):
            self.slug = slug

    assert _penalite_de_repetition(_T("push-a"), "push-a") == MEME_GABARIT
    assert _penalite_de_repetition(_T("push-b"), "push-a") == MEME_FAMILLE
    assert _penalite_de_repetition(_T("pull-a"), "push-a") == NOUVEAU
    # Aucun historique : rien à répéter, donc aucune pénalité.
    assert _penalite_de_repetition(_T("push-a"), None) == NOUVEAU


def test_une_zone_a_plat_n_est_pas_compensee_par_une_zone_fraiche(client):
    """La récupération prend le MINIMUM sur les zones, pas la moyenne.

    Une moyenne laisserait un gabarit dont une zone est à plat passer pour prêt
    grâce à ses autres zones — ce qui est précisément le cas qu'un filtre de
    récupération existe pour attraper.
    """
    from app.services.recommendation import Signals
    from app.services.recommendation_v3 import (
        INSUFFISANTE,
        RECUPEREE,
        _bande_de_recuperation,
    )

    def _s(dispo):
        return Signals(
            cold_start=False, availability_by_zone=dispo,
            hours_since_last_by_zone={}, last_strength_session_zones=[],
            recent_strength_zones_by_session=[], hard_sets_by_zone_recent={},
            hard_sets_by_zone_24h={}, kinds_recent=[],
            days_since_last_cardio=None, days_since_last_strength=None,
            fatigue_score=0.0, soft_restart=False, median_hard_sets_14d=0.0,
            hard_sets_14d_by_zone={}, observation_partielle=False,
        )

    zones = ("pecs", "triceps")
    assert _bande_de_recuperation(
        zones, _s({"pecs": 1.0, "triceps": 1.0})) == RECUPEREE
    assert _bande_de_recuperation(
        zones, _s({"pecs": 0.0, "triceps": 1.0})) == INSUFFISANTE, (
        "une zone à plat a été compensée par une zone fraîche"
    )


# ═══════════ 4. LA COMPARAISON EN OMBRE ═══════════


def test_comparaison_en_ombre_v2_contre_v3(client, capsys):
    """⚠ LE BANC DE COMPARAISON — MÊME CORPUS, MÊMES AGRÉGATS.

    Il n'affirme PAS que V3 est meilleur parce qu'il varie davantage (`§11`).
    Il vérifie que les deux défaillances **mesurées** par `REC-CP1` sont
    corrigées, et rien de plus :

    `B` — quatre histoires opposées rendaient la MÊME séquence.
    `A` — une fois `B` retiré, 72 % des décisions tombaient sur `display_order`.

    Corriger l'une sans l'autre était le demi-correctif à éviter.
    """
    resultats = {}
    for nom_politique in ("v2", "v3"):
        lignes = []
        for traj in CORPUS:
            lignes.append(resumer(traj.nom, _rejouer(traj, nom_politique)))
        resultats[nom_politique] = lignes

    with capsys.disabled():
        for nom_politique, lignes in resultats.items():
            print(f"\n─── politique {nom_politique} ───")
            print(f"{'trajectoire':22s} {'déc':>4s} {'srT':>4s} {'conc':>6s} "
                  f"{'cata':>6s} gagnants")
            for r in lignes:
                print(f"{r['trajectoire']:22s} {r['prises']:4d} "
                      f"{r['serie_gabarit_max']:4d} "
                      f"{r['concentration_gagnant']:6.2f} "
                      f"{r['part_egalites']:6.2f} "
                      f"{', '.join(f'{k}×{v}' for k, v in r['gagnants'].items())}")

    # `A` — la part de décisions tranchées par l'ordre du catalogue.
    def _part_catalogue(lignes):
        prises = sum(r["prises"] for r in lignes)
        tranchees = sum(round(r["part_egalites"] * r["prises"])
                        for r in lignes)
        return tranchees / prises if prises else 0.0

    part_v3 = _part_catalogue(resultats["v3"])
    assert part_v3 <= 0.15, (
        f"{part_v3:.0%} des décisions V3 sont tranchées par l'ordre du "
        "catalogue — c'est le défaut `A` que `REC-CP1` a trouvé sous `B`, "
        "et le corriger était la moitié du travail"
    )

    # `B` — trois histoires opposées ne doivent plus rendre la même séquence.
    sequences = {
        nom: tuple(d.gagnant for d in _rejouer(_par_nom(nom), "v3"))
        for nom in ("push-lourd", "pull-lourd", "legs-lourd")
    }
    assert len(set(sequences.values())) > 1, (
        "V3 reproduit la défaillance mesurée : push-lourd, pull-lourd et "
        f"legs-lourd rendent encore la MÊME séquence.\n  {sequences}"
    )


def test_en_boucle_fermee_v2_se_bloque_et_v3_se_deplace(client, capsys):
    """⚠ LA MESURE QUI CORRESPOND ENFIN À LA PLAINTE DE DOGFOOD.

    « La recommandation reste bloquée sur le même type de séance au lieu de
    refléter la trajectoire récente. »

    Les dix-sept trajectoires sont en boucle **ouverte** : le conseil n'y est
    jamais suivi. Elles mesurent la sensibilité à l'histoire, pas l'évolution —
    et elles exagèrent le blocage, puisqu'un gabarit recommandé mais jamais
    effectué reste éternellement le plus ancien au départage.

    Ici l'utilisateur **exécute** chaque recommandation. Une politique saine se
    déplace alors d'elle-même : la zone qu'elle vient de servir cesse d'être la
    plus délaissée. Une politique qui répète encore répète pour de bon.
    """
    from app.database import SessionLocal
    from scripts.reco_replay import rejouer_en_boucle

    resultats = {}
    for nom_politique in ("v2", "v3"):
        uid = _utilisateur(f"boucle-{nom_politique}")
        with SessionLocal() as db:
            ds = rejouer_en_boucle(db, uid, nom_politique=nom_politique, nb=10)
        resultats[nom_politique] = resumer(nom_politique, ds)

    with capsys.disabled():
        print("\n─── boucle fermée, 10 décisions suivies ───")
        for nom_politique, r in resultats.items():
            print(f"{nom_politique}: série max={r['serie_gabarit_max']} "
                  f"conc={r['concentration_gagnant']:.2f} "
                  f"catalogue={r['part_egalites']:.2f} "
                  f"{r['gagnants']}")

    v2, v3 = resultats["v2"], resultats["v3"]

    # ⚠ CE QUE CETTE MESURE A RÉVÉLÉ, ET QUI CORRIGE `REC-CP1`.
    #
    # J'attendais que V2 se bloque ici aussi. Il ne se bloque PAS : série
    # maximale 1, six gabarits différents sur dix décisions. Le blocage mesuré
    # en boucle ouverte était donc, pour une large part, l'effet d'un corpus qui
    # ne suit jamais le conseil.
    #
    # Les deux modes restent vrais, et leur ÉCART est le vrai énoncé du défaut :
    #
    #   conseil suivi   → V2 tourne correctement
    #   conseil décliné → V2 répète le même conseil indéfiniment
    #
    # V2 n'est pas « épinglé » : il n'a aucune notion d'avoir déjà donné un
    # conseil que l'utilisateur a écarté. C'est une caractérisation plus étroite
    # et plus juste, et c'est elle qui doit guider la suite.
    #
    # On n'affirme donc RIEN sur V2 ici — la boucle fermée ne lui reproche rien.
    assert v2["serie_gabarit_max"] <= 2, (
        "V2 se bloque désormais en boucle fermée alors qu'il ne le faisait pas "
        f"— le constat de `REC-CP2` a changé : {v2['gagnants']}"
    )

    # Ce que V3 doit tenir : ne pas introduire un blocage que V2 n'avait pas.
    assert v3["serie_gabarit_max"] <= 2, (
        "V3 répète le même gabarit alors que l'utilisateur SUIT ses conseils — "
        f"la zone servie devrait cesser d'être la plus délaissée : "
        f"{v3['gagnants']}"
    )


def test_quand_v3_repete_c_est_porte_par_une_preuve(client):
    """⚠ CETTE GARDE A REMPLACÉ CELLE QUE JE VOULAIS ÉCRIRE, ET C'EST LE §11.

    J'avais d'abord écrit : « V3 ne doit pas répéter le même gabarit sur toute
    une trajectoire ». Elle échouait sur sept trajectoires — et elle avait tort,
    pas V3.

    En boucle **ouverte**, l'utilisateur décline le conseil : la zone reste
    réellement la plus délaissée, donc la redonner est honnête. Exiger la
    variété là aurait été exactement le travers que le `§11` proscrit — juger
    une politique meilleure parce qu'elle varie davantage.

    L'invariant réel est `REPEAT_REQUIRES_EVIDENCE` : répéter est permis, mais
    **porté par la couverture**, jamais par une égalité, un `display_order`, un
    `slug` ou une donnée manquante. C'est cela qu'on vérifie.
    """
    from app.database import SessionLocal
    from app.services.recommendation_v3 import classer_candidats
    from scripts.reco_replay import HEURE_DECISION

    traj = _par_nom("push-lourd")
    uid = _utilisateur("preuve-repetition")
    with SessionLocal() as db:
        for s in traj.echauffement + traj.seances:
            semer_seance(db, uid, s, ORIGINE)
        quand = ORIGINE + timedelta(days=10) + HEURE_DECISION
        verdicts = classer_candidats(db, uid, quand)

    assert len(verdicts) >= 6, "prémisse : un vrai pool de candidats"
    tete = verdicts[0]
    deficit_max = max(v.facteurs["deficit_couverture"] for v in verdicts)

    assert tete.facteurs["deficit_couverture"] >= deficit_max, (
        "le gagnant n'est pas celui dont les zones sont les plus délaissées — "
        "la répétition ne serait alors portée par aucune preuve : "
        f"{tete.slug} à {tete.facteurs['deficit_couverture']} "
        f"contre un maximum de {deficit_max}"
    )
    assert tete.facteurs["recuperation"] == 0, (
        f"le gagnant n'est pas récupéré : {tete.facteurs}"
    )
