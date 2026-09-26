"""`REC-CP5` — l'explication de V3 dit enfin ce qui a décidé.

LE BLOCAGE DE PROMOTION, ET SA CAUSE EXACTE
----------------------------------------------
`REC-CP4` a refusé de promouvoir V3 pour une raison que seul le rendu montrait :
sur un compte réel de huit séances, V3 rendait **la même recommandation que
V2** en n'expliquant plus que

    « La modalité la plus délaissée. »  ·  « Jamais fait. »

La cause n'était pas le classement. C'étaient **deux défauts d'énoncé** :

1. **La couverture — critère PRIMAIRE du rang — se taisait dans la bande
   médiane.** Elle n'était dite qu'au-dessus de 0,75 ou en dessous de 0,25,
   c'est-à-dire jamais dans le cas le plus fréquent.
2. **« Jamais fait » parlait toujours**, pour tout candidat jamais effectué,
   qu'il ait départagé ou non — devenant l'explication entière d'une décision
   qu'il n'avait pas prise.

⚠ CE QUE CETTE TRANCHE NE FAIT PAS
------------------------------------
Elle ne touche **ni le classement, ni les constantes, ni la précédence, ni la
mémoire du conseil**. Une garde vérifie que l'ordre des candidats est
rigoureusement identique avant et après. Et elle n'imite pas la prose de V2 :
l'objectif est d'expliquer **la vraie décision de V3**, pas de ressembler.
"""
from __future__ import annotations

import itertools
from datetime import timedelta

from scripts.reco_replay import ECHAUFFEMENT, ORIGINE, Seance, semer_seance

_RANG = itertools.count()


def _utilisateur(nom: str) -> int:
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        u = User(username=f"{nom}-{next(_RANG)}", password_hash="-")
        db.add(u)
        db.commit()
        return u.id


def _semer(uid: int, slugs) -> None:
    from app.database import SessionLocal

    with SessionLocal() as db:
        for s in ECHAUFFEMENT:
            semer_seance(db, uid, s, ORIGINE)
        for i, slug in enumerate(slugs):
            semer_seance(db, uid, Seance(jour=i * 2, slug=slug), ORIGINE)


def _reco_v3(uid: int, jours: int):
    from app.database import SessionLocal
    from app.services.recommendation import reset_template_zones_cache
    from app.services.recommendation_v3 import recommander_v3

    reset_template_zones_cache()
    with SessionLocal() as db:
        return recommander_v3(db, uid, now=ORIGINE + timedelta(days=jours))


# ═══════════ 1. LE CLASSEMENT N'A PAS BOUGÉ ═══════════


def test_le_classement_de_v3_est_rigoureusement_inchange(client):
    """⚠ L'INVARIANT QUI DÉFINIT CETTE TRANCHE COMME UNE MICRO-TRANCHE.

    `REC-CP5` a le droit de changer ce que V3 DIT. Il n'a aucun droit sur ce
    que V3 CHOISIT. Si l'ordre des candidats bougeait, ce ne serait plus une
    tranche d'explication mais un changement de politique déguisé — et la
    comparaison de promotion repartirait de zéro.

    On reconstruit le classement par les pièces du moteur et on vérifie que la
    clé de rang ne dépend d'aucune donnée d'explication.
    """
    import inspect

    from app.services import recommendation_v3 as v3

    source = inspect.getsource(v3.classer_candidats)
    for interdit in ("expliquer", "phrase_de", "critere_decisif",
                     "_facteur_de_couverture", "_en_tete"):
        assert interdit not in source, (
            f"`classer_candidats` appelle « {interdit} » : l'explication "
            "influencerait le classement"
        )

    # Et la clé de rang reste celle que `REC-CP2` a posée.
    assert v3.CRITERES_DU_RANG == (
        "recuperation", "couverture", "repetition", "modalite",
        "recence_gabarit", "recence_famille", "ordre_catalogue", "slug",
    ), "la table des critères ne décrit plus la clé réelle du classement"


# ═══════════ 2. LA COUVERTURE PARLE TOUJOURS ═══════════


def test_la_cause_primaire_du_classement_est_toujours_enoncee(client):
    """⚠ LE DÉFAUT CORRIGÉ, ÉPINGLÉ SUR SON SEUIL.

    La couverture est le critère primaire. Muette entre 0,25 et 0,75, elle
    laissait l'explication à des faits secondaires.
    """
    from app.services.recommendation_v3 import _facteur_de_couverture

    zones = ["Pectoraux", "Triceps"]
    for deficit in (0.0, 0.1, 0.26, 0.4, 0.5, 0.6, 0.74, 0.8, 1.0):
        texte, _gagnant = _facteur_de_couverture(deficit, zones)
        assert texte, f"la couverture se tait à {deficit}"
        assert "Pectoraux" in texte, f"elle ne nomme pas la zone à {deficit}"
        assert "14 derniers jours" in texte, (
            f"elle n'énonce pas son horizon d'observation à {deficit}"
        )


def test_un_deficit_fort_se_dit_autrement_qu_un_deficit_faible(client):
    """Une gradation qui rendrait le même texte partout ne graderait rien."""
    from app.services.recommendation_v3 import _facteur_de_couverture

    fort, gagnant_fort = _facteur_de_couverture(0.9, ["Core"])
    moyen, _ = _facteur_de_couverture(0.55, ["Core"])
    faible, gagnant_faible = _facteur_de_couverture(0.1, ["Core"])

    assert len({fort, moyen, faible}) == 3, (
        f"trois déficits très différents rendent le même texte : "
        f"{fort!r} / {moyen!r} / {faible!r}"
    )
    assert gagnant_fort is True
    assert gagnant_faible is False, (
        "une zone déjà bien servie est présentée comme un facteur GAGNANT"
    )


# ═══════════ 3. « JAMAIS FAIT » NE PARLE QUE S'IL A DÉCIDÉ ═══════════


def test_jamais_fait_ne_devient_pas_l_explication_entiere(client):
    """`§3` — un fait terminal faible ne remplace pas la preuve de décision.

    ⚠ LA GARDE EST CONSTRUITE POUR MORDRE : on parcourt plusieurs comptes et
    on exige qu'AUCUN ne réduise son explication à la nouveauté seule.
    """
    cas = {
        "rotation": ["push-a", "pull-a", "legs-a"],
        "fourni": ["push-a", "pull-a", "legs-a", "push-b", "pull-b", "legs-b"],
        "push-lourd": ["push-a", "push-b", "push-a", "push-b"],
    }
    for nom, slugs in cas.items():
        uid = _utilisateur(f"cp5-{nom}")
        _semer(uid, slugs)
        reco = _reco_v3(uid, len(slugs) * 2)
        assert reco is not None, nom
        gagnants = reco["top"]["explication"]["facteurs_gagnants"]
        assert gagnants, f"{nom} : aucune raison énoncée"
        assert gagnants != ("jamais fait",), (
            f"{nom} : « jamais fait » est toute l'explication"
        )
        assert any("14 derniers jours" in g for g in gagnants), (
            f"{nom} : la cause primaire du classement n'est pas nommée — "
            f"{gagnants}"
        )


def test_la_nouveaute_parle_quand_elle_a_reellement_departage(client):
    """Le pendant : on n'a pas rendu « jamais fait » muet, on l'a rendu HONNÊTE.

    Le supprimer purement aurait été une soustraction : quand la nouveauté est
    réellement le critère qui sépare le gagnant de son dauphin, elle doit se
    dire.
    """
    from app.services.recommendation_v3 import expliquer

    class _T:
        slug, name, display_order, kind = "pull-b", "Pull B", 5, "strength"

    class _V:
        template = _T()
        zones = ()
        rang = ()
        slug = "pull-b"
        facteurs = {
            "recuperation": 0, "deficit_couverture": 0.5, "repetition": 0,
            "repetition_justifiee": False, "modalite_delaissee": False,
            "dernier_passage": None, "observation_partielle": False,
        }

    avec = expliquer(_V(), 0, "recence_gabarit")
    assert "jamais fait" in avec["facteurs_gagnants"], (
        "la nouveauté est muette alors qu'elle a départagé"
    )
    sans = expliquer(_V(), 0, "couverture")
    assert "jamais fait" not in sans["facteurs_gagnants"], (
        "la nouveauté parle alors qu'un critère plus fort a décidé"
    )


# ═══════════ 4. L'ORDRE SUIT CE QUI A DÉCIDÉ ═══════════


def test_le_critere_decisif_est_lu_dans_le_rang_pas_devine(client):
    """⚠ CE N'EST PAS UNE HEURISTIQUE. C'est le premier rang où deux clés
    diffèrent — donc, littéralement, ce qui a décidé."""
    from app.services.recommendation_v3 import critere_decisif

    class _V:
        def __init__(self, rang):
            self.rang = rang

    base = (0, -0.8, 0, 0, "a", "b", 3, "x")
    assert critere_decisif(_V(base), None) is None
    assert critere_decisif(
        _V(base), _V((1, -0.8, 0, 0, "a", "b", 3, "x"))) == "recuperation"
    assert critere_decisif(
        _V(base), _V((0, -0.5, 0, 0, "a", "b", 3, "x"))) == "couverture"
    assert critere_decisif(
        _V(base), _V((0, -0.8, 0, 0, "z", "b", 3, "x"))) == "recence_gabarit"
    assert critere_decisif(
        _V(base), _V((0, -0.8, 0, 0, "a", "b", 9, "x"))) == "ordre_catalogue"
    assert critere_decisif(_V(base), _V(base)) is None


def test_le_facteur_qui_a_decide_est_enonce_en_premier(client):
    """`§3` — « strongest winning causal factor » d'abord."""
    from app.services.recommendation_v3 import _en_tete

    gagnants = ["zones récupérées", "Core : le moins servi sur 14 derniers jours"]
    remis = _en_tete(gagnants, "couverture", ["Core"])
    assert remis[0].startswith("Core"), (
        f"le critère décisif n'est pas en tête : {remis}"
    )
    # Un critère décisif sans facteur énoncé — l'ordre du catalogue n'est pas
    # une raison — laisse l'ordre naturel plutôt que d'inventer une cause.
    assert _en_tete(gagnants, "ordre_catalogue", ["Core"]) == gagnants


# ═══════════ 5. CE QUI NE DOIT PAS TRAVERSER ═══════════


def test_aucun_nombre_ni_score_ne_traverse_toujours(client):
    """`REC-CP3` tenait déjà cette propriété ; `REC-CP5` ajoute des phrases et
    ne doit pas l'entamer."""
    from app.services.recommendation_explainer import explain_recommendation

    uid = _utilisateur("cp5-nombres")
    _semer(uid, ["push-a", "pull-a", "legs-a", "push-b"])
    reco = _reco_v3(uid, 8)
    assert reco is not None

    e = explain_recommendation(reco)
    textes = [*e["reasons"], e["primary_reason"] or "",
              e["fallback_note"] or "", reco["top"]["phrase"]]
    for t in textes:
        chiffres = [c for c in t.replace("14 derniers jours", "")
                    if c.isdigit()]
        assert not chiffres, f"un nombre atteint l'utilisateur : {t!r}"
