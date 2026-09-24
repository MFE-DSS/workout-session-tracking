"""`REC-CP3` — l'explication structurée, lue et non re-dérivée.

CE QUE CETTE TRANCHE CORRIGE
------------------------------
`recommendation_explainer.py` reconstruisait ses raisons depuis un contexte
appauvri : `cold_start`, `fallback`, `days_since_last_*`, `fatigue_score`, plus
la phrase déjà écrite. Il re-devinait donc ce que le moteur savait et n'avait
pas transmis.

Tant qu'aucune politique ne produisait de trace, c'était le seul moyen. V3 en
produit une. La reconstruction devient alors nuisible : deux logiques
parallèles divergent, et c'est celle qui devine qui a tort.

⚠ CE QUE CETTE TRANCHE NE FAIT PAS
------------------------------------
Elle ne promeut pas V3. Le chemin de re-dérivation reste **intact** pour V2,
qui est toujours la politique de production. Une garde le vérifie.
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
        u = User(username=f"{nom}-{next(_RANG)}", password_hash="x")
        db.add(u)
        db.commit()
        return u.id


def _reco_v3(slugs: list[str], *, substitution: str | None = None):
    """Rend la sortie V3 réelle après une trajectoire donnée."""
    from app.database import SessionLocal
    from app.services.recommendation_v3 import recommander_v3

    uid = _utilisateur("cp3")
    with SessionLocal() as db:
        for e in ECHAUFFEMENT:
            semer_seance(db, uid, e, ORIGINE)
        for i, slug in enumerate(slugs):
            semer_seance(
                db, uid,
                Seance(jour=i * 2, slug=slug,
                       substitution=substitution if i == 0 else None),
                ORIGINE)
        return recommander_v3(db, uid, now=ORIGINE + timedelta(days=len(slugs) * 2))


# ═══════════ 1. LE MOTEUR DIT CE QUI A DÉCIDÉ ═══════════


def test_la_trace_nomme_les_facteurs_au_lieu_de_les_faire_deviner(client):
    reco = _reco_v3(["push-a", "push-b", "push-a", "push-b", "push-a"])
    assert reco is not None
    trace = reco["top"]["explication"]

    assert set(trace) == {
        "facteurs_gagnants", "facteurs_limitants", "horizon", "famille",
        "justification_repetition", "provenance", "rang",
    }, f"la forme de la trace a changé — décision requise : {sorted(trace)}"

    assert trace["facteurs_gagnants"], (
        f"aucun facteur gagnant nommé : {trace}"
    )
    assert trace["famille"] is not None
    assert trace["provenance"] in {"mesurée", "partielle"}


def test_aucun_nombre_ne_traverse_l_explication(client):
    """⚠ `AUCUN SCORE 0-100 EXPOSÉ COMME VÉRITÉ UTILISATEUR.`

    Le dictionnaire V3 porte encore une clé `score`, uniquement pour que sa
    forme reste comparable à celle de V2 dans le banc de mesure. Elle ne doit
    atteindre aucune surface.

    On vérifie donc l'absence de **chiffre**, pas l'absence de la clé : c'est
    la propriété qui compte pour l'utilisateur, et elle attrape aussi un jour
    où quelqu'un écrirait « déficit 87 % » dans une phrase.
    """
    from app.services.recommendation_explainer import explain_recommendation

    reco = _reco_v3(["push-a", "pull-a", "legs-a", "push-b"])
    assert reco is not None
    explication = explain_recommendation(reco)

    textes = [explication["primary_reason"] or ""]
    textes += explication["reasons"]
    textes.append(explication["fallback_note"] or "")
    textes.append(reco["top"]["phrase"])

    # Le seul nombre toléré est l'horizon d'observation, que le `§8` impose de
    # nommer comme une mémoire et non comme un cycle biologique.
    for t in textes:
        sans_horizon = t.replace("14 derniers jours", "")
        chiffres = [c for c in sans_horizon if c.isdigit()]
        assert not chiffres, (
            f"un nombre atteint l'utilisateur : {t!r} (chiffres {chiffres})"
        )


def test_l_horizon_est_nomme_comme_une_observation(client):
    """`§8` — « 14 jours est une mémoire, pas une vérité physiologique ».

    La phrase doit parler de ce qui a été observé, jamais d'un cycle du corps.
    """
    from app.services.recommendation_v3 import HORIZON_OBSERVATION

    assert "jour" in HORIZON_OBSERVATION
    for interdit in ("cycle", "récupération complète", "optimal",
                     "physiologique", "doit"):
        assert interdit not in HORIZON_OBSERVATION.lower()


# ═══════════ 2. L'EXPLAINER LIT, IL NE DEVINE PLUS ═══════════


def test_l_explainer_suit_la_trace_et_ignore_le_contexte_qui_la_contredit():
    """⚠ LA GARDE CENTRALE DE `REC-CP3`, ET ELLE EST CONSTRUITE POUR MORDRE.

    On fabrique une charge dont la **trace** dit une chose et dont le
    **contexte** en dit une autre, incompatible. Si l'explainer re-dérivait
    encore, il produirait les raisons du contexte.

    Un test qui se contenterait d'une charge cohérente passerait aussi avec
    l'ancien chemin — il ne prouverait rien.
    """
    from app.services.recommendation_explainer import explain_recommendation

    charge = {
        "top": {
            "phrase": "Dos, biceps : le moins servi sur 14 derniers jours.",
            "primary_zones": ["lats", "biceps"],
            "explication": {
                "facteurs_gagnants": ("dos, biceps : le moins servi sur "
                                      "14 derniers jours",
                                      "zones récupérées"),
                "facteurs_limitants": (),
                "horizon": "14 derniers jours",
                "famille": "pull",
                "justification_repetition": None,
                "provenance": "mesurée",
                "rang": 0,
            },
        },
        "alternatives": [],
        # ⚠ Ce contexte déclencherait, par l'ancien chemin, la phrase de
        # démarrage à froid, la note de repli et la bande de fatigue élevée.
        "context": {
            "cold_start": True,
            "fallback": True,
            "fatigue_score": 90,
            "days_since_last_strength": 12,
        },
    }

    e = explain_recommendation(charge)

    assert e["available"] is True
    assert e["confidence"] == "ok", (
        "l'explainer a dégradé la confiance depuis le contexte alors que la "
        f"trace la donne mesurée : {e}"
    )
    assert e["fallback_note"] is None, (
        f"note de repli re-dérivée malgré une trace complète : {e}"
    )
    joint = " | ".join(e["reasons"])
    for fantome in ("Première séance", "Niveau de fatigue",
                    "basée sur ton historique récent"):
        assert fantome not in joint, (
            f"raison re-dérivée du contexte alors qu'une trace existe : {joint}"
        )
    # Insensible à la mise en forme : ce test porte sur la PROVENANCE de la
    # raison, pas sur sa capitalisation — que `_en_phrase` applique et qu'une
    # garde de rendu dédiée vérifie ailleurs.
    assert "zones récupérées" in joint.lower(), (
        f"un facteur de la trace n'a pas été rendu : {joint}"
    )


def test_la_phrase_n_est_pas_redigee_deux_fois(client):
    """La phrase compacte est une LECTURE de la trace, pas une seconde plume.

    Deux rédactions indépendantes divergeraient — c'est le défaut même que
    cette tranche corrige. On vérifie que la phrase dérive du premier facteur
    gagnant, et que l'explainer ne la compte pas deux fois.
    """
    from app.services.recommendation_explainer import explain_recommendation
    from app.services.recommendation_v3 import phrase_de

    reco = _reco_v3(["push-a", "push-b", "push-a", "push-b"])
    assert reco is not None
    trace = reco["top"]["explication"]

    assert reco["top"]["phrase"] == phrase_de(trace), (
        "la phrase n'est plus dérivée de la trace"
    )
    raisons = explain_recommendation(reco)["reasons"]
    assert len(raisons) == len(set(raisons)), f"raison dupliquée : {raisons}"


def test_une_observation_partielle_se_dit_et_ne_se_confond_pas(client):
    """⚠ « Pas assez de données » et « je n'ai pas su lire une donnée » ne
    disent pas la même chose.

    Les confondre ferait passer une lacune de CLASSEMENT pour une absence
    d'historique — et l'utilisateur corrigerait la mauvaise chose.
    """
    from app.services.recommendation_explainer import (
        _FALLBACK_NOTE,
        _NOTE_OBSERVATION_PARTIELLE,
        explain_recommendation,
    )

    reco = _reco_v3(["push-a", "pull-a", "legs-a", "push-b"],
                    substitution="Zorglub press oblique 47°")
    assert reco is not None
    assert reco["top"]["explication"]["provenance"] == "partielle", (
        "prémisse : un nom libre illisible rend bien l'observation partielle"
    )

    e = explain_recommendation(reco)
    assert e["fallback_note"] == _NOTE_OBSERVATION_PARTIELLE
    assert e["fallback_note"] != _FALLBACK_NOTE
    assert e["confidence"] == "low"


def test_ce_que_l_utilisateur_lit_reellement(client, capsys):
    """⚠ LA GARDE QUI REGARDE LE TEXTE RENDU, PAS SA STRUCTURE.

    Une explication peut être parfaitement structurée et illisible : mots
    collés, double ponctuation, phrase tronquée en plein mot. Aucune des gardes
    précédentes ne le verrait — elles vérifient des clés et des ensembles.

    Celle-ci imprime le texte (visible avec `-s`) et épingle les défauts de
    forme qu'un rendu réel exposerait immédiatement.
    """
    from app.services.recommendation_explainer import explain_recommendation

    cas = {
        "push lourd": ["push-a", "push-b", "push-a", "push-b", "push-a"],
        "rotation": ["push-a", "pull-a", "legs-a", "push-b"],
        "jambes lourdes": ["legs-a", "legs-b", "legs-a", "legs-b"],
    }
    rendus = []
    for nom, slugs in cas.items():
        reco = _reco_v3(slugs)
        assert reco is not None
        e = explain_recommendation(reco)
        rendus.append((nom, reco["top"]["template"].slug, e))

    with capsys.disabled():
        print()
        for nom, slug, e in rendus:
            print(f"── {nom} → {slug}")
            for r in e["reasons"]:
                print(f"     · {r}")
            if e["fallback_note"]:
                print(f"     ⚠ {e['fallback_note']}")

    for nom, _slug, e in rendus:
        for texte in e["reasons"]:
            assert texte == texte.strip(), f"{nom} : espace en bord — {texte!r}"
            assert "  " not in texte, f"{nom} : double espace — {texte!r}"
            assert ".." not in texte, f"{nom} : double point — {texte!r}"
            assert " ," not in texte, f"{nom} : espace avant virgule — {texte!r}"
            assert len(texte) <= 140, f"{nom} : trop long ({len(texte)})"
            assert texte[0].isupper(), f"{nom} : ne commence pas par une capitale — {texte!r}"


# ═══════════ 3. LE CHEMIN V2 RESTE INTACT ═══════════


def test_le_chemin_de_re_derivation_reste_entier_pour_v2(client):
    """V2 est **toujours** la politique de production, et il n'a pas de trace.

    Retirer la re-dérivation en même temps qu'on ajoute la lecture aurait
    silencieusement vidé l'explication de la seule politique que l'utilisateur
    voit réellement.
    """
    from app.database import SessionLocal
    from app.services.recommendation import (
        recommend_next_session,
        reset_template_zones_cache,
    )
    from app.services.recommendation_explainer import explain_recommendation

    uid = _utilisateur("cp3-v2")
    with SessionLocal() as db:
        for e in ECHAUFFEMENT:
            semer_seance(db, uid, e, ORIGINE)
        for i, slug in enumerate(["push-a", "pull-a", "legs-a"]):
            semer_seance(db, uid, Seance(jour=i * 2, slug=slug), ORIGINE)
        reset_template_zones_cache()
        reco = recommend_next_session(db, uid, now=ORIGINE + timedelta(days=6))

    assert reco is not None
    assert "explication" not in reco["top"], (
        "V2 s'est mis à produire une trace — la promotion doit être déclarée"
    )
    e = explain_recommendation(reco)
    assert e["available"] is True
    assert e["reasons"], "l'explication de V2 est vide"


# ⚠ L'INTERDIT DU `§12` N'EST PAS RÉPÉTÉ ICI, ET C'EST DÉLIBÉRÉ.
#
# `REC-CP3` rend V3 *promouvable* — il produit désormais une phrase et une
# explication — mais ne le promeut pas. La garde qui le vérifie vit dans
# `test_rec_cp2_policy.py::test_la_politique_v3_ne_pilote_aucune_surface`, et
# elle y reste SEULE.
#
# J'ai d'abord écrit ici une seconde garde avec sa propre liste de lecteurs
# autorisés. Deux listes du même registre divergent — le dépôt en porte
# plusieurs exemples. Ce module s'est donc simplement déclaré dans le registre
# existant, ce que la garde a exigé en rougissant.
