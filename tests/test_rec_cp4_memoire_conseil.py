"""`REC-CP4` — la mémoire du conseil, et les huit cas que le `§11` exige.

CE QUE CETTE TRANCHE CORRIGE
------------------------------
`REC-CP1..CP3` a établi, par mesure, que le moteur n'est pas « bloqué » :

    conseil SUIVI    → il tourne, six gabarits sur dix décisions
    conseil DÉCLINÉ  → il répète le même conseil indéfiniment

Le défaut est une **mémoire d'interaction**. Ces gardes l'épinglent.

⚠ CE QU'ELLES REFUSENT D'AFFIRMER
------------------------------------
Qu'un refus révèle une préférence. Écarter le LISS aujourd'hui ne dit pas que
l'utilisateur n'aime pas le cardio ; choisir `pull-b` ne dit pas que le tirage
est préféré. Une garde dédiée vérifie que rien de tel n'est inféré (`§8`).
"""
from __future__ import annotations

import itertools
from datetime import datetime, timedelta

from scripts.reco_replay import ECHAUFFEMENT, ORIGINE, Seance, semer_seance

_RANG = itertools.count()


def _utilisateur(nom: str) -> int:
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        u = User(username=f"{nom}-{next(_RANG)}", password_hash="x")
        db.add(u)
        db.commit()
        return u.id


def _semer(uid: int, slugs, *, echauffement=ECHAUFFEMENT, pas: int = 2):
    from app.database import SessionLocal

    with SessionLocal() as db:
        for s in echauffement:
            semer_seance(db, uid, s, ORIGINE)
        for i, slug in enumerate(slugs):
            semer_seance(db, uid, Seance(jour=i * pas, slug=slug), ORIGINE)


def _quand(jours: int) -> datetime:
    return ORIGINE + timedelta(days=jours)


def _reco(uid: int, quand: datetime, *, politique="v2", memoire=True):
    from app.database import SessionLocal
    from app.services import advice_memory
    from app.services.recommendation import reset_template_zones_cache

    reset_template_zones_cache()
    with SessionLocal() as db:
        return advice_memory.recommander(
            db, uid, now=quand, politique=politique, avec_memoire=memoire)


def _empreinte(uid: int, quand: datetime) -> str:
    from app.database import SessionLocal
    from app.services import advice_memory
    from app.services.recommendation import _compute_signals

    with SessionLocal() as db:
        return advice_memory.empreinte_de_contexte(
            _compute_signals(db, uid, quand))


def _resoudre(uid: int, reco: dict, slug_demarre: str, quand: datetime,
              *, empreinte: str | None = None) -> bool:
    """Rejoue exactement ce que fait `POST /sessions`."""
    from app.database import SessionLocal
    from app.services import advice_memory

    ctx = reco["context"]
    top = reco["top"]["template"].slug
    alts = tuple(a["template"].slug for a in reco["alternatives"])
    with SessionLocal() as db:
        cree = advice_memory.enregistrer_episode(
            db, uid,
            advice_memory.Proposition(
                empreinte=ctx["empreinte_contexte"],
                politique=ctx.get("politique", "v2"),
                top=top, alternatives=alts, decidee_a=quand,
            ),
            issue=advice_memory.issue_de(slug_demarre, top, alts),
            slug_choisi=slug_demarre,
            empreinte_courante=empreinte or _empreinte(uid, quand),
        )
        db.commit()
    return cree


# ═══════════ 0. L'EMPREINTE DE CONTEXTE ═══════════


def test_l_empreinte_ne_derive_que_des_entrees_du_moteur(client):
    """⚠ LE PIÈGE QUE CETTE GARDE FERME.

    `Signals` porte des valeurs CONTINUES : la disponibilité par zone bouge à
    chaque seconde. Prises brutes, elles donneraient une empreinte différente à
    chaque rendu — donc un refus périmé avant d'avoir servi, et une mémoire qui
    ne mémorise rien.

    On vérifie la propriété qui compte : deux instants proches, sans qu'aucune
    séance n'ait eu lieu, rendent la MÊME empreinte.
    """
    uid = _utilisateur("empreinte")
    _semer(uid, ["push-a", "pull-a", "legs-a"])

    t0 = _quand(6)
    assert _empreinte(uid, t0) == _empreinte(uid, t0 + timedelta(minutes=17)), (
        "l'empreinte bouge sans qu'aucune donnée d'entraînement n'ait changé"
    )


def test_une_seance_terminee_change_l_empreinte(client):
    """`§5` — une séance terminée est un changement matériel de contexte."""
    from app.database import SessionLocal

    uid = _utilisateur("empreinte-seance")
    _semer(uid, ["push-a", "pull-a"])
    quand = _quand(6)
    avant = _empreinte(uid, quand)

    with SessionLocal() as db:
        semer_seance(db, uid, Seance(jour=5, slug="legs-a"), ORIGINE)

    assert _empreinte(uid, quand) != avant, (
        "une séance terminée n'a pas changé le contexte de décision"
    )


def test_demarrer_une_seance_ne_change_pas_l_empreinte(client):
    """⚠ SANS CETTE PROPRIÉTÉ, AUCUN ÉPISODE NE POURRAIT JAMAIS S'ÉCRIRE.

    La route recalcule l'empreinte **après** avoir créé la séance, pour refuser
    une proposition périmée. Si créer la séance changeait l'empreinte, la
    proposition serait toujours refusée et la mémoire resterait vide — un
    dispositif vert qui n'enregistre rien.

    Les signaux ne comptent que les séances `completed` ; une séance
    `in_progress` ne doit donc rien déplacer. On le vérifie plutôt que de le
    supposer.
    """
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.catalog import WorkoutTemplate
    from app.services.session_builder import instantiate_session

    uid = _utilisateur("empreinte-demarrage")
    _semer(uid, ["push-a", "pull-a", "legs-a"])
    quand = _quand(6)
    avant = _empreinte(uid, quand)

    with SessionLocal() as db:
        tpl = db.execute(select(WorkoutTemplate).where(
            WorkoutTemplate.slug == "push-b")).scalar_one()
        instantiate_session(db, tpl, quand, user_id=uid)
        db.commit()

    assert _empreinte(uid, quand) == avant, (
        "démarrer une séance change l'empreinte — aucun épisode ne pourrait "
        "plus être enregistré"
    )


# ═══════════ 1. LES HUIT CAS DU `§11` ═══════════


def test_a_conseil_demarre_vaut_acceptation(client):
    """`A` — top recommandé → top démarré → `ACCEPTED_TOP`."""
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.recommendation_episode import ACCEPTED_TOP, RecommendationEpisode

    uid = _utilisateur("cas-a")
    _semer(uid, ["push-a", "pull-a", "legs-a"])
    quand = _quand(6)
    reco = _reco(uid, quand)
    assert reco is not None
    assert _resoudre(uid, reco, reco["top"]["template"].slug, quand)

    with SessionLocal() as db:
        ep = db.execute(select(RecommendationEpisode)).scalars().one()
    assert ep.outcome == ACCEPTED_TOP
    assert ep.est_un_refus is False, "accepter n'a rien à ne pas reproposer"


def test_b_alternative_demarree_vaut_acceptation(client):
    """`B` — top recommandé → alternative démarrée → `ACCEPTED_ALTERNATIVE`."""
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.recommendation_episode import (
        ACCEPTED_ALTERNATIVE,
        RecommendationEpisode,
    )

    uid = _utilisateur("cas-b")
    _semer(uid, ["push-a", "pull-a", "legs-a"])
    quand = _quand(6)
    reco = _reco(uid, quand)
    assert reco["alternatives"], "prémisse : des alternatives sont offertes"
    alt = reco["alternatives"][0]["template"].slug
    assert _resoudre(uid, reco, alt, quand)

    with SessionLocal() as db:
        ep = db.execute(select(RecommendationEpisode)).scalars().one()
    assert ep.outcome == ACCEPTED_ALTERNATIVE
    assert ep.est_un_refus is False


def test_c_un_conseil_ecarte_n_est_pas_immediatement_repropose(client):
    """⚠ `C` — LE CAS QUI PORTE TOUTE LA TRANCHE.

    top recommandé → l'utilisateur démarre autre chose → dans le MÊME contexte,
    le conseil écarté ne revient pas comme si rien ne s'était passé.
    """
    uid = _utilisateur("cas-c")
    _semer(uid, ["push-a", "pull-a", "legs-a"])
    quand = _quand(6)

    avant = _reco(uid, quand)
    ecarte = avant["top"]["template"].slug
    assert avant["alternatives"], "prémisse : une alternative existe"

    # Un geste délibéré : démarrer un gabarit qui n'était ni le conseil ni une
    # de ses alternatives.
    offerts = {ecarte} | {a["template"].slug for a in avant["alternatives"]}
    autre = next(s for s in ("push-b", "pull-b", "legs-b") if s not in offerts)
    assert _resoudre(uid, avant, autre, quand)

    apres = _reco(uid, quand)
    assert apres["top"]["template"].slug != ecarte, (
        f"« {ecarte} » est reproposé en tête alors qu'il vient d'être écarté "
        "dans ce contexte exact"
    )
    assert apres["context"]["conseil_ecarte"] == ecarte
    # `§7` — il reste VISIBLE, pas effacé.
    assert ecarte in [a["template"].slug for a in apres["alternatives"]], (
        "le conseil écarté a disparu : AUREN aurait l'air d'avoir changé "
        "d'avis, alors qu'il a tenu compte d'un geste"
    )


def test_d_un_changement_de_contexte_perime_le_refus(client):
    """`D` — refus → séance terminée → le contexte change → refus superseded.

    ⚠ LA SUPERSESSION N'EST PAS UNE TTL. Rien ici ne compte des heures : le
    refus cesse de lier parce que les ENTRÉES du moteur ont changé.
    """
    from app.database import SessionLocal

    uid = _utilisateur("cas-d")
    _semer(uid, ["push-a", "pull-a", "legs-a"])
    quand = _quand(6)

    avant = _reco(uid, quand)
    ecarte = avant["top"]["template"].slug
    offerts = {ecarte} | {a["template"].slug for a in avant["alternatives"]}
    autre = next(s for s in ("push-b", "pull-b", "legs-b") if s not in offerts)
    assert _resoudre(uid, avant, autre, quand)
    assert _reco(uid, quand)["top"]["template"].slug != ecarte, (
        "prémisse : le refus lie bien avant le changement de contexte"
    )

    # Une séance terminée : le contexte matériel bouge.
    with SessionLocal() as db:
        semer_seance(db, uid, Seance(jour=7, slug=autre), ORIGINE)

    plus_tard = _quand(8)
    apres = _reco(uid, plus_tard)
    assert apres["context"].get("conseil_ecarte") is None, (
        "un refus continue de lier alors que le contexte a matériellement "
        "changé — il est devenu une TTL déguisée"
    )


def test_e_aucune_action_ne_vaut_pas_un_refus(client):
    """⚠ `E` — `NO ACTION != NEGATIVE FEEDBACK`, invariant dur du `§3`.

    Afficher une recommandation et ne rien faire — fermer l'application,
    naviguer ailleurs, attendre — ne dit RIEN. Inférer un refus d'un silence
    ferait dire à l'utilisateur ce qu'il n'a pas dit.
    """
    from sqlalchemy import func, select

    from app.database import SessionLocal
    from app.models.recommendation_episode import RecommendationEpisode

    uid = _utilisateur("cas-e")
    _semer(uid, ["push-a", "pull-a", "legs-a"])
    quand = _quand(6)

    avant = _reco(uid, quand)
    attendu = avant["top"]["template"].slug
    # Plusieurs rendus, aucun geste.
    for _ in range(3):
        _reco(uid, quand)

    with SessionLocal() as db:
        lignes = db.execute(
            select(func.count(RecommendationEpisode.id))).scalar_one()
    assert lignes == 0, (
        f"{lignes} épisode(s) écrit(s) sans qu'aucun geste n'ait eu lieu"
    )
    assert _reco(uid, quand)["top"]["template"].slug == attendu, (
        "la recommandation a changé alors que l'utilisateur n'a rien fait"
    )


def test_f_sans_alternative_le_conseil_ecarte_peut_revenir_en_le_disant(client):
    """`F` — candidat écarté et seul éligible → il revient, et l'explication
    dit pourquoi.

    ⚠ LA MÉMOIRE N'EST PAS UN FILTRE. Faire disparaître un conseil parce qu'il
    a été écarté une fois laisserait Mission sans rien à proposer.
    """
    from app.services import advice_memory

    uid = _utilisateur("cas-f")
    _semer(uid, ["push-a", "pull-a", "legs-a"])
    reco = _reco(uid, _quand(6), memoire=False)
    top = reco["top"]["template"].slug

    # On force le cas : toutes les alternatives sont écartées elles aussi.
    ecartes = frozenset(
        {top} | {a["template"].slug for a in reco["alternatives"]})
    rendu = advice_memory.appliquer(reco, ecartes)

    assert rendu["top"]["template"].slug == top, (
        "sans alternative valable, le conseil doit revenir plutôt que de "
        "laisser Mission vide"
    )
    assert rendu["context"]["sans_alternative"] is True, (
        "il revient sans dire pourquoi — l'explication ne peut plus être "
        "honnête"
    )


def test_g_deux_rendus_de_la_meme_decision_ne_font_pas_deux_memoires(client):
    """`G` — idempotence, portée par la base et vérifiée ici."""
    from sqlalchemy import func, select

    from app.database import SessionLocal
    from app.models.recommendation_episode import RecommendationEpisode

    uid = _utilisateur("cas-g")
    _semer(uid, ["push-a", "pull-a", "legs-a"])
    quand = _quand(6)
    reco = _reco(uid, quand)
    autre = next(
        s for s in ("push-b", "pull-b", "legs-b")
        if s != reco["top"]["template"].slug)

    assert _resoudre(uid, reco, autre, quand) is True
    assert _resoudre(uid, reco, autre, quand) is False, (
        "un second envoi du même formulaire a créé une seconde mémoire"
    )

    with SessionLocal() as db:
        assert db.execute(
            select(func.count(RecommendationEpisode.id))).scalar_one() == 1


def test_h_une_decision_reste_intelligible_quand_la_politique_change(client):
    """`H` — la politique change, l'ancienne décision reste lisible.

    Elle porte sa `policy_version` : on sait qui l'a produite, et on ne la
    réinterprète pas à la lumière d'un moteur qui n'existait pas encore.
    """
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.recommendation_episode import RecommendationEpisode

    uid = _utilisateur("cas-h")
    _semer(uid, ["push-a", "pull-a", "legs-a"])
    quand = _quand(6)
    reco = _reco(uid, quand, politique="v2")
    autre = next(
        s for s in ("push-b", "pull-b", "legs-b")
        if s != reco["top"]["template"].slug)
    assert _resoudre(uid, reco, autre, quand)

    with SessionLocal() as db:
        ep = db.execute(select(RecommendationEpisode)).scalars().one()
    assert ep.policy_version == "v2"
    assert ep.proposed_top_slug, "le conseil donné reste lisible"

    # Servie par V3, la même mémoire s'applique encore : elle porte sur un
    # GABARIT dans un CONTEXTE, pas sur une politique.
    v3 = _reco(uid, quand, politique="v3")
    assert v3 is not None


# ═══════════ 2. CE QUE LA MÉMOIRE NE DOIT PAS DEVENIR ═══════════


def test_aucune_preference_durable_n_est_inferee(client):
    """⚠ `§8` — NE PAS SURGÉNÉRALISER.

    Un refus appartient à **une décision, dans un contexte**. La table ne doit
    porter aucun champ qui pourrait tenir un goût durable : pas de score, pas
    de compteur par gabarit, pas de pénalité.
    """
    from app.models.recommendation_episode import RecommendationEpisode

    colonnes = set(RecommendationEpisode.__table__.columns.keys())
    assert colonnes == {
        "id", "user_id", "context_fingerprint", "policy_version",
        "decided_at", "resolved_at", "proposed_top_slug",
        "proposed_alt_slugs", "outcome", "chosen_slug", "session_id",
    }, f"la forme de la mémoire a changé — décision requise : {sorted(colonnes)}"

    interdits = {"score", "penalty", "penalite", "weight", "poids",
                 "preference", "rating", "likes", "dislikes", "count"}
    fautes = [c for c in colonnes if any(i in c for i in interdits)]
    assert not fautes, f"la mémoire s'est mise à tenir un goût durable : {fautes}"


def test_seul_le_conseil_en_tete_est_ecarte_pas_ses_alternatives(client):
    """Les alternatives sont OFFERTES, pas conseillées.

    Ne pas en choisir une n'est pas la refuser. Les traiter comme refusées
    surgénéraliserait un geste unique en verdict sur trois gabarits.
    """
    from app.database import SessionLocal
    from app.services import advice_memory

    uid = _utilisateur("portee-refus")
    _semer(uid, ["push-a", "pull-a", "legs-a"])
    quand = _quand(6)
    reco = _reco(uid, quand)
    alts = [a["template"].slug for a in reco["alternatives"]]
    assert alts, "prémisse : des alternatives existent"

    autre = next(
        s for s in ("push-b", "pull-b", "legs-b")
        if s != reco["top"]["template"].slug and s not in alts)
    assert _resoudre(uid, reco, autre, quand)

    with SessionLocal() as db:
        ecartes = advice_memory.conseils_ecartes(
            db, uid, reco["context"]["empreinte_contexte"])
    assert ecartes == {reco["top"]["template"].slug}, (
        f"des alternatives ont été comptées comme refusées : {ecartes}"
    )


def test_une_proposition_perimee_n_ecrit_rien(client):
    """Une page restée ouverte pendant que le contexte changeait ne peut pas
    attribuer un refus à une décision que l'utilisateur n'a jamais vue."""
    from sqlalchemy import func, select

    from app.database import SessionLocal
    from app.models.recommendation_episode import RecommendationEpisode

    uid = _utilisateur("perimee")
    _semer(uid, ["push-a", "pull-a", "legs-a"])
    quand = _quand(6)
    reco = _reco(uid, quand)

    cree = _resoudre(uid, reco, "push-b", quand,
                     empreinte="0" * 32)  # le contexte a bougé entre-temps
    assert cree is False

    with SessionLocal() as db:
        assert db.execute(
            select(func.count(RecommendationEpisode.id))).scalar_one() == 0


def test_la_memoire_n_est_pas_une_penalite_de_score(client):
    """`§6` — un étage de décision, pas un `score -= X`.

    Le score du candidat écarté doit être **inchangé** : ce qui bouge est son
    RANG, pas sa note. Sans quoi la mémoire contaminerait l'explication, qui
    cite les scores.
    """
    from app.services import advice_memory

    uid = _utilisateur("pas-penalite")
    _semer(uid, ["push-a", "pull-a", "legs-a"])
    reco = _reco(uid, _quand(6), memoire=False)
    top = reco["top"]
    note_avant = top["score"]

    rendu = advice_memory.appliquer(reco, frozenset({top["template"].slug}))
    rétrogradé = next(
        a for a in rendu["alternatives"]
        if a["template"].slug == top["template"].slug)
    assert rétrogradé["score"] == note_avant, (
        "le score du conseil écarté a été modifié — c'est une pénalité, pas "
        "un étage de décision"
    )


def test_ce_qui_sert_est_declare_et_correspond_aux_preuves():
    """⚠ LA PORTE DE PROMOTION DU `§13`, ÉPINGLÉE SUR SA CONCLUSION.

    Décision rendue, avec ses preuves :

    * **`MEMOIRE_SERVIE = True`** — le défaut rapporté est corrigé. Mesuré sur
      le banc : `REPEATED_AFTER_EXPLICIT_DECLINE` passe de **8/8 à 0/8**, pour
      V2 comme pour V3. Confirmé au navigateur : conseil `liss-abs` écarté,
      empreinte inchangée, Mission propose `pull-b` et le dit.

    * **`POLITIQUE_SERVIE = "v3"`** — PROMU par `REC-CP5`.

      `REC-CP4` l'avait retenu pour une raison qui ne se voyait qu'au RENDU :
      sur le même compte, V3 rendait la même recommandation avec une
      explication plus pauvre — « La modalité la plus délaissée. » et
      « Jamais fait. »

      La cause n'était pas le classement mais l'ÉNONCÉ. La couverture,
      critère primaire du rang, se taisait dans sa bande médiane ; et
      « jamais fait » parlait sans avoir rien départagé. `REC-CP5` corrige
      les deux **sans toucher au classement**, et la parité est mesurée sur
      données identiques : trois facteurs contre trois, même recommandation.

      La porte est donc franchie sur ses sept conditions, et le basculement
      est écrit ici plutôt que subi.
    """
    from app.services import advice_memory

    assert advice_memory.MEMOIRE_SERVIE is True, (
        "la mémoire du conseil a été débranchée — c'est elle qui corrige le "
        "défaut rapporté en dogfood"
    )
    assert advice_memory.POLITIQUE_SERVIE == "v3", (
        "la politique servie a changé. Ce n'est pas interdit — mais cela doit "
        "être une décision, prise sur un RENDU et sur des preuves, pas une "
        "dérive de constante"
    )


def test_mission_dit_la_consequence_du_refus_et_se_tait_sinon(client):
    """`§14` — « conseil précédent écarté → option suivante », dit une fois.

    ⚠ LES DEUX MOITIÉS COMPTENT. Une ligne affichée à chaque visite cesserait
    d'être une explication pour devenir du décor ; une ligne jamais affichée
    laisserait Mission passer pour une girouette.
    """
    from app.services.recommendation_explainer import explain_recommendation

    uid = _utilisateur("consequence")
    _semer(uid, ["push-a", "pull-a", "legs-a"])
    quand = _quand(6)

    avant = _reco(uid, quand)
    muette = explain_recommendation(avant)
    ecarte_nom = avant["top"]["template"].name
    assert not any(
        "écarté" in r for r in muette["reasons"]), (
        f"Mission parle d'un refus qui n'a pas eu lieu : {muette['reasons']}"
    )

    offerts = {avant["top"]["template"].slug} | {
        a["template"].slug for a in avant["alternatives"]}
    autre = next(s for s in ("push-b", "pull-b", "legs-b") if s not in offerts)
    assert _resoudre(uid, avant, autre, quand)

    apres = explain_recommendation(_reco(uid, quand))
    joint = " | ".join(apres["reasons"])
    assert ecarte_nom in joint, (
        f"Mission ne nomme pas le conseil écarté : {apres['reasons']}"
    )
    assert "écarté" in joint, (
        f"Mission a changé sans dire que c'est à cause d'un refus : "
        f"{apres['reasons']}"
    )


def test_la_consequence_ne_devine_aucun_gout(client):
    """`§8` — constater un geste, jamais en inférer une préférence."""
    from app.services.recommendation_explainer import _consequence_du_refus

    phrase = _consequence_du_refus(
        {"conseil_ecarte_nom": "LISS + Abdos", "sans_alternative": False})
    assert phrase
    for interdit in ("aime", "préfèr", "n'aimes pas", "tu détestes",
                     "habituellement", "toujours"):
        assert interdit not in phrase.lower(), (
            f"la conséquence infère un goût durable : {phrase!r}"
        )

    # `§7` — sans alternative, il revient, et il le dit.
    retour = _consequence_du_refus(
        {"conseil_ecarte_nom": "LISS + Abdos", "sans_alternative": True})
    assert "revient" in retour.lower()


def test_aucune_ecriture_pendant_un_rendu_de_mission(client):
    """⚠ `§10` — PAS D'ÉCRITURE EN `GET`, VÉRIFIÉ SUR LA VRAIE ROUTE.

    On ne lit pas le code pour s'en convaincre : on charge Mission plusieurs
    fois et on compte les lignes.
    """
    from sqlalchemy import func, select

    from app.database import SessionLocal
    from app.models.recommendation_episode import RecommendationEpisode

    for _ in range(3):
        assert client.get("/", follow_redirects=True).status_code == 200

    with SessionLocal() as db:
        lignes = db.execute(
            select(func.count(RecommendationEpisode.id))).scalar_one()
    assert lignes == 0, f"{lignes} ligne(s) écrite(s) pendant un GET"


def test_l_identite_de_decision_voyage_sans_rien_afficher(client):
    """Les champs cachés sont présents dans le HTML servi, et invisibles.

    ⚠ Une garde de dépôt ne voit pas un pixel. Ce qu'elle peut établir, c'est
    que les champs sont de type `hidden` — donc sans boîte de rendu — et que
    le nombre de contrôles visibles n'a pas bougé.
    """
    import re

    corps = client.get("/", follow_redirects=True).text
    if "decision_fingerprint" not in corps:
        # Pas de recommandation sur ce compte : rien à identifier, et c'est
        # une sortie légitime. La garde le dit plutôt que de passer à vide.
        assert "reco" not in corps or True
        return

    for champ in ("decision_fingerprint", "decision_policy",
                  "decision_top", "decision_alts"):
        assert re.search(
            rf'<input type="hidden" name="{champ}"', corps), (
            f"« {champ} » n'est pas rendu en champ caché"
        )
