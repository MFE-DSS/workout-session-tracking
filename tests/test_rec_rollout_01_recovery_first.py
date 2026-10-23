"""`REC-ROLLOUT-01` (D14) — la séance suivante se choisit par la récupération ;
le cardio est le plan B.

Mesuré avant d'écrire (spec `Sx_REC_ROLLOUT_01_RECOVERY_FIRST_SPEC §2`) : après
une première séance `push-a`, cinq séances de force étaient pleinement
récupérées, et « la modalité délaissée » les départageait toutes en faveur du
cardio. Sur le corpus `REC-CP`, V3 servait `liss-abs` dans 64 décisions sur 78.

Les cas sont ceux de l'opérateur, sur de vrais nouveaux utilisateurs.
"""
from __future__ import annotations

import itertools
from datetime import timedelta

from scripts.reco_replay import ORIGINE, Seance, semer_seance

_N = itertools.count()


def _nouveau(slugs: tuple[str, ...]) -> int:
    """Un nouvel utilisateur réel : AUCUN échauffement, seulement ces séances."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        u = User(username=f"rollout-{next(_N)}", password_hash="-")
        db.add(u)
        db.commit()
        uid = u.id
        for i, slug in enumerate(slugs):
            semer_seance(db, uid, Seance(jour=i, slug=slug), ORIGINE)
    return uid


def _classement(uid: int, jour: float):
    from app.database import SessionLocal
    from app.services.recommendation import reset_template_zones_cache
    from app.services.recommendation_v3 import classer_candidats

    reset_template_zones_cache()
    with SessionLocal() as db:
        return classer_candidats(db, uid, ORIGINE + timedelta(days=jour))


def _reco(uid: int, jour: float):
    from app.database import SessionLocal
    from app.services.recommendation import reset_template_zones_cache
    from app.services.recommendation_v3 import recommander_v3

    reset_template_zones_cache()
    with SessionLocal() as db:
        return recommander_v3(db, uid, now=ORIGINE + timedelta(days=jour))


def test_apres_une_premiere_seance_de_force_on_ne_part_pas_au_cardio(client):
    """Le défaut d'origine : après `push-a`, `liss-abs` était premier."""
    uid = _nouveau(("push-a",))
    tete = _classement(uid, 1)[0]
    assert tete.template.kind != "cardio", (
        f"un nouvel utilisateur part au cardio ({tete.slug}) alors que des "
        "séances de force sont pleinement récupérées"
    )
    assert tete.facteurs["recuperation"] == 0


def test_quand_toute_la_force_recupere_le_cardio_est_le_plan_b(client):
    """`full-body` charge presque tout : le cardio vient, et il dit pourquoi."""
    uid = _nouveau(("full-body-morphotype-priority-v1",))
    vs = _classement(uid, 1)
    tete = vs[0]
    assert tete.template.kind == "cardio"
    assert tete.facteurs["plan_b"] is True
    assert all(v.facteurs["recuperation"] > tete.facteurs["recuperation"]
               for v in vs if v.template.kind != "cardio"), (
        "le cardio n'est servi en plan B que si TOUTE la force fait moins bien"
    )
    phrase = _reco(uid, 1)["top"]["phrase"]
    assert phrase.startswith("Tout le reste récupère encore"), phrase


def test_apres_les_jambes_les_pectoraux(client):
    uid = _nouveau(("legs-a",))
    assert _classement(uid, 1)[0].template.kind != "cardio"


def test_a_bande_egale_la_force_passe_avant_le_cardio(client):
    """Jamais de cardio fait, tout récupéré : la force gagne — la modalité
    « délaissée » ne départage plus."""
    uid = _nouveau(("push-a", "legs-a"))
    vs = _classement(uid, 5)
    meilleure = vs[0].facteurs["recuperation"]
    cardio = [v for v in vs if v.template.kind == "cardio"
              and v.facteurs["recuperation"] == meilleure]
    force = [v for v in vs if v.template.kind != "cardio"
             and v.facteurs["recuperation"] == meilleure]
    assert force, "le scénario doit offrir de la force dans la meilleure bande"
    assert vs[0].template.kind != "cardio"
    for c in cardio:
        assert c.facteurs["plan_b"] is False
        assert vs.index(c) > vs.index(force[0])


def test_le_moins_sollicite_passe_devant_a_bande_egale(client):
    """`1 ter` — deux gabarits en bande partielle : moins de zones à reprendre
    d'abord. Pièce pure, sur la carte canonique."""
    from app.services.recommendation_v3 import RecuperationCanonique, _zones_en_recuperation
    from app.services.zone_recovery import LIMITANT, NON_LIMITANT, PARTIEL

    recup = RecuperationCanonique(
        decision={"pecs": PARTIEL, "triceps": PARTIEL, "delt_lat": NON_LIMITANT,
                  "lats": PARTIEL, "biceps": NON_LIMITANT, "quads": LIMITANT},
        preuve={})
    assert _zones_en_recuperation(("pecs", "triceps", "delt_lat"), recup) == 2
    assert _zones_en_recuperation(("lats", "biceps"), recup) == 1
    # carte absente : neutre, jamais une pénalité inventée
    assert _zones_en_recuperation(("pecs",), RecuperationCanonique()) == 0


def test_le_repos_est_un_fait_et_une_zone_jamais_chargee_est_la_plus_reposee(client):
    from app.services.recommendation_v3 import RecuperationCanonique, _repos_minimal

    recup = RecuperationCanonique(heures={"pecs": 20.0, "triceps": 70.0, "lats": None})
    assert _repos_minimal(("pecs", "triceps"), recup) == 20.0  # la moins reposée
    assert _repos_minimal(("lats",), recup) == float("inf")
    assert _repos_minimal((), recup) == float("inf")


def test_la_phrase_modalite_a_disparu(client):
    """Le critère est retiré ; sa phrase ne doit survivre nulle part."""
    import inspect

    from app.services import recommendation_v3 as v3

    assert "modalité la plus délaissée" not in inspect.getsource(v3).replace(
        "« La modalité la plus délaissée. »", "")
    assert not hasattr(v3, "_bande_de_modalite")
