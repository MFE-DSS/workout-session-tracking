"""`REC-CP4 §12` — les quatre systèmes, sur le même corpus causal.

    V2 · V2 + MÉMOIRE · V3 · V3 + MÉMOIRE

⚠ LA MÉTRIQUE DÉCISIVE
------------------------
`REPEATED_AFTER_EXPLICIT_DECLINE`, dans un contexte matériellement inchangé.
Cible : **zéro**, sauf le cas prouvé « aucune alternative valable ».

Tout le reste est du contexte. La variété n'est pas la justesse (`§11` de
`REC-CP2`), et une politique plus récente ne se promeut pas parce qu'elle est
plus récente (`§13`).
"""
from __future__ import annotations

import itertools

from scripts.reco_replay import CORPUS, rejouer, rejouer_en_boucle, resumer

_RANG = itertools.count()

SYSTEMES = (
    ("V2", "v2", False),
    ("V2+M", "v2", True),
    ("V3", "v3", False),
    ("V3+M", "v3", True),
)


def _utilisateur(nom: str) -> int:
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        u = User(username=f"{nom}-{next(_RANG)}", password_hash="x")
        db.add(u)
        db.commit()
        return u.id


def _mesurer_refus(politique: str, memoire: bool) -> dict:
    """La boucle où l'utilisateur DÉCLINE — celle qui porte la métrique."""
    from app.database import SessionLocal
    from scripts.reco_replay import rejouer_en_declinant

    uid = _utilisateur(f"declin-{politique}-{int(memoire)}")
    with SessionLocal() as db:
        ds = rejouer_en_declinant(
            db, uid, politique=politique, avec_memoire=memoire, nb=8)

    prises = [d for d in ds if d.gagnant]
    return {
        "prises": len(prises),
        "repete_apres_refus": sum(1 for d in prises if d.repropose_apres_refus),
        "sans_alternative": sum(1 for d in prises if d.sans_alternative),
        "gagnants": len({d.gagnant for d in prises}),
    }


def _mesurer_boucle_fermee(politique: str, memoire: bool) -> dict:
    """Le conseil est SUIVI. La mémoire ne doit rien y casser."""
    from app.database import SessionLocal

    uid = _utilisateur(f"ferme-{politique}-{int(memoire)}")
    with SessionLocal() as db:
        if memoire:
            ds = _boucle_avec(db, uid, politique)
        else:
            ds = rejouer_en_boucle(db, uid, nom_politique=politique, nb=10)
    return resumer(politique, ds)


def _boucle_avec(db, uid: int, politique: str):
    """Boucle fermée passant par la composition à mémoire.

    Identique à `rejouer_en_boucle`, au point d'entrée près : on veut vérifier
    que brancher la mémoire ne dégrade pas le cas où le conseil est suivi.
    """
    from datetime import timedelta

    from app.services import advice_memory
    from app.services.recommendation import (
        _compute_signals,
        reset_template_zones_cache,
    )
    from scripts.reco_replay import (
        ECHAUFFEMENT,
        HEURE_DECISION,
        ORIGINE,
        Seance,
        _decision_de,
        semer_seance,
    )

    for s in ECHAUFFEMENT:
        semer_seance(db, uid, s, ORIGINE)

    vu_g: dict[str, int] = {}
    vu_f: dict[str, int] = {}
    out = []
    for i in range(10):
        jour = i * 2
        quand = ORIGINE + timedelta(days=jour) + HEURE_DECISION
        reset_template_zones_cache()
        reco = advice_memory.recommander(
            db, uid, now=quand, politique=politique, avec_memoire=True)
        signaux = _compute_signals(db, uid, quand)
        d = _decision_de(jour, reco, signaux, vu_g, vu_f)
        out.append(d)
        if d.gagnant is None:
            continue
        semer_seance(db, uid, Seance(jour=jour, slug=d.gagnant), ORIGINE)
        vu_g[d.gagnant] = jour
        if d.famille:
            vu_f[d.famille] = jour
    return out


def _mesurer_boucle_ouverte(politique: str, memoire: bool) -> dict:
    """Le corpus des dix-sept trajectoires, conseil jamais suivi ni écarté.

    La mémoire n'y a rien à mordre — aucun refus n'y est jamais déclaré. C'est
    le TÉMOIN : elle ne doit rien y changer.
    """
    from app.database import SessionLocal

    lignes = []
    for traj in CORPUS:
        uid = _utilisateur(f"ouvert-{politique}-{int(memoire)}-{traj.nom}")
        with SessionLocal() as db:
            ds = rejouer(db, uid, traj, nom_politique=politique)
        lignes.append(resumer(traj.nom, ds))
    prises = sum(r["prises"] for r in lignes)
    return {
        "prises": prises,
        "tranchees_catalogue": sum(
            round(r["part_egalites"] * r["prises"]) for r in lignes),
        "concentration_moyenne": round(sum(
            r["concentration_gagnant"] for r in lignes) / len(lignes), 3),
    }


def test_comparaison_des_quatre_systemes(client, capsys):
    """⚠ LE BANC. Même corpus, mêmes gestes, quatre compositions."""
    refus = {nom: _mesurer_refus(p, m) for nom, p, m in SYSTEMES}
    ferme = {nom: _mesurer_boucle_fermee(p, m) for nom, p, m in SYSTEMES}

    with capsys.disabled():
        print("\n─── boucle de REFUS : l'utilisateur écarte le conseil ───")
        print(f"{'système':8s} {'déc':>4s} {'REPETE_APRES_REFUS':>19s} "
              f"{'sans_alt':>9s} {'gagnants':>9s}")
        for nom, _p, _m in SYSTEMES:
            r = refus[nom]
            print(f"{nom:8s} {r['prises']:4d} {r['repete_apres_refus']:19d} "
                  f"{r['sans_alternative']:9d} {r['gagnants']:9d}")

        print("\n─── boucle FERMÉE : le conseil est suivi ───")
        print(f"{'système':8s} {'série':>6s} {'conc':>6s} {'catalogue':>10s}")
        for nom, _p, _m in SYSTEMES:
            f = ferme[nom]
            print(f"{nom:8s} {f['serie_gabarit_max']:6d} "
                  f"{f['concentration_gagnant']:6.2f} "
                  f"{f['part_egalites']:10.2f}")

    # ── La métrique décisive du `§12`.
    for nom in ("V2+M", "V3+M"):
        r = refus[nom]
        assert r["prises"] >= 4, f"{nom} : corpus trop maigre ({r['prises']})"
        assert r["repete_apres_refus"] == 0, (
            f"{nom} repropose {r['repete_apres_refus']} fois un conseil "
            "explicitement écarté, dans un contexte matériellement inchangé — "
            "c'est exactement le défaut rapporté en dogfood"
        )

    # ── Et la PRÉMISSE : sans mémoire, le défaut est bien présent.
    #
    # ⚠ Sans cette moitié, la garde ne prouverait rien : un zéro peut venir
    # d'un dispositif qui marche, ou d'un corpus qui ne produit jamais le cas.
    sans_memoire = refus["V2"]["repete_apres_refus"] + refus["V3"]["repete_apres_refus"]
    assert sans_memoire > 0, (
        "sans mémoire, aucun conseil n'est reproposé après refus — le corpus "
        f"ne produit donc pas le cas mesuré : {refus['V2']}, {refus['V3']}"
    )

    # ── La mémoire ne dégrade pas le cas où le conseil est SUIVI.
    for base, avec in (("V2", "V2+M"), ("V3", "V3+M")):
        assert ferme[avec]["serie_gabarit_max"] <= ferme[base]["serie_gabarit_max"], (
            f"{avec} répète davantage que {base} quand le conseil est suivi : "
            f"{ferme[avec]['gagnants']}"
        )


#: Cinq histoires de départ différentes. ⚠ UNE SEULE BOUCLE DE DIX DÉCISIONS
#: NE SUFFIT PAS À PROMOUVOIR UNE POLITIQUE DE PRODUCTION : 0,40 contre 0,10,
#: c'est quatre décisions contre une. On regarde si l'écart tient.
AMORCES = {
    "rotation": ["push-a", "pull-a", "legs-a"],
    "push-lourd": ["push-a", "push-b", "push-a"],
    "pull-lourd": ["pull-a", "pull-b", "pull-a"],
    "legs-lourd": ["legs-a", "legs-b", "legs-a"],
    "apres-cardio": ["push-a", "pull-a", "liss-only"],
}


def _boucle_fermee_depuis(nom: str, slugs, politique: str) -> dict:

    from app.database import SessionLocal
    from scripts.reco_replay import Seance, rejouer_en_boucle

    amorce = tuple(
        Seance(jour=-30 + i * 2, slug=s) for i, s in enumerate(slugs))
    uid = _utilisateur(f"robuste-{nom}-{politique}")
    with SessionLocal() as db:
        ds = rejouer_en_boucle(
            db, uid, nom_politique=politique, nb=10, amorce=amorce)
    return resumer(nom, ds)


def test_l_avantage_de_v3_tient_il_sur_plusieurs_histoires(client, capsys):
    """⚠ LA GARDE QUI DÉCIDE DE LA PROMOTION, ET QUI PEUT DIRE NON.

    Le `§13` est explicite : « si `V2 + MÉMOIRE` résout le défaut de dogfood
    mais que V3 n'apporte aucune valeur ÉTAYÉE, ne pas promouvoir V3 au seul
    motif qu'il est plus récent. Rendre les preuves. »

    La valeur candidate de V3 est la réduction de la dépendance à l'ordre du
    catalogue — le défaut `A` de `REC-CP1`. **Pas** sa plus grande variété :
    le `§11` de `REC-CP2` interdit expressément cet argument.

    Cette garde ne fixe pas de seuil de promotion : elle MESURE, sur cinq
    histoires de départ, et laisse le rapport conclure. Elle épingle seulement
    que la comparaison reste faisable — un banc qui ne produit plus de
    décisions ne prouverait rien.
    """
    resultats = {}
    for nom, slugs in AMORCES.items():
        resultats[nom] = {
            p: _boucle_fermee_depuis(nom, slugs, p) for p in ("v2", "v3")
        }

    with capsys.disabled():
        print("\n─── boucle fermée, cinq histoires de départ ───")
        print(f"{'amorce':14s} {'catalogue v2':>13s} {'catalogue v3':>13s} "
              f"{'série v2':>9s} {'série v3':>9s}")
        for nom, r in resultats.items():
            print(f"{nom:14s} {r['v2']['part_egalites']:13.2f} "
                  f"{r['v3']['part_egalites']:13.2f} "
                  f"{r['v2']['serie_gabarit_max']:9d} "
                  f"{r['v3']['serie_gabarit_max']:9d}")
        moy2 = sum(r["v2"]["part_egalites"] for r in resultats.values()) / len(resultats)
        moy3 = sum(r["v3"]["part_egalites"] for r in resultats.values()) / len(resultats)
        print(f"{'MOYENNE':14s} {moy2:13.2f} {moy3:13.2f}")

    for nom, r in resultats.items():
        assert r["v2"]["prises"] >= 8, f"{nom} : banc dégénéré côté v2"
        assert r["v3"]["prises"] >= 8, f"{nom} : banc dégénéré côté v3"


def test_la_memoire_est_inerte_quand_aucun_refus_n_a_ete_declare(client, capsys):
    """⚠ LE TÉMOIN — sans quoi on ne saurait pas ce que la mémoire change.

    Sur les dix-sept trajectoires en boucle ouverte, aucun refus n'est jamais
    déclaré. Brancher la mémoire ne doit donc **rien** y changer : si elle y
    déplaçait une décision, elle agirait sur autre chose qu'un refus.
    """
    sans = _mesurer_boucle_ouverte("v2", False)
    avec = _mesurer_boucle_ouverte("v2", True)

    with capsys.disabled():
        print(f"\ntémoin boucle ouverte — sans mémoire : {sans}")
        print(f"témoin boucle ouverte — avec mémoire : {avec}")

    assert sans == avec, (
        "la mémoire modifie des décisions alors qu'aucun refus n'existe — "
        "elle agit sur autre chose que ce qu'elle prétend mémoriser"
    )
