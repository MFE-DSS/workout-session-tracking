"""`Sb_TRAIN_A_ENVIRONMENT_EXPERIENCE_01` — les dix preuves produit du `§8`.

Ce fichier ne garde pas une implémentation : il **rejoue le produit**. Chaque
cas passe par une vraie route HTTP ou par le service servi, jamais par une
fonction interne appelée à la main pour arranger le verdict.

Les quatre classes d'environnement sont celles que TRAIN A a établies, et
leurs verdicts sont **mesurés**, pas choisis : un environnement n'est déclaré
« riche » ici que parce que le résolveur le rend réellement servable.
"""
from __future__ import annotations

from app.services.environment_activation import (
    ADAPTABLE,
    INCERTAIN,
    NATIF,
    NON_APPLICABLE,
    REFUSE,
    preparer_demarrage,
)
from tests.helpers import get_test_user_id


def _vocabulaire():
    from app.services.equipment_model import equipment_item_vocabulary

    return list(equipment_item_vocabulary())


#: Salle commerciale équipée — l'inventaire **complet du registre**, dérivé et
#: non recopié : un inventaire écrit à la main dérive du vocabulaire réel, et
#: c'est exactement ce qui a fait échouer la première version de ce fichier.
_SALLE_COMPLETE = _vocabulaire()

#: Salle privée / limitée — tout sauf le Smith et les deux poulies réglables.
#: Mesuré : rend des gabarits servables **par adaptation**.
_SANS = {"smith_machine", "dual_adjustable_pulley", "single_adjustable_pulley",
         "assisted_pull_up", "lateral_raise_machine"}
_SALLE_LIMITEE = [objet for objet in _SALLE_COMPLETE if objet not in _SANS]

#: Maison — haltères et banc, rien d'autre.
_MAISON = ["dumbbells", "adjustable_bench"]

#: Mesuré : avec la seule roulette abdominale, ces gabarits sont réellement
#: prouvés incompatibles. Aucun verdict n'est fabriqué.
_QUASI_RIEN = ["ab_wheel"]

_SANS_MATERIEL = "no-equipment-full-body"
_ROUTE_SEANCES = "/sessions"
_ROUTE_PLAN = "/plan"
_CHAMP_GABARIT = "template_slug"


# ───────────────────────── outillage de mesure ─────────────────────────


def _declarer(uid, objets):
    from app.database import SessionLocal
    from app.services.training_preferences import save_available_equipment_items

    with SessionLocal() as db:
        save_available_equipment_items(db, uid, objets)


def _lu(uid):
    from app.database import SessionLocal
    from app.services.training_preferences import get_training_preferences

    with SessionLocal() as db:
        return get_training_preferences(db, uid)


def _gabarit(slug):
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    from app.database import SessionLocal
    from app.models.catalog import TemplateExercise, WorkoutTemplate

    with SessionLocal() as db:
        return db.execute(
            select(WorkoutTemplate).where(WorkoutTemplate.slug == slug)
            .options(selectinload(WorkoutTemplate.exercises)
                     .selectinload(TemplateExercise.rep_targets))
        ).scalar_one()


def _preparer(uid, slug):
    from app.database import SessionLocal

    with SessionLocal() as db:
        return preparer_demarrage(db, uid, _gabarit(slug))


def _recommander(uid):
    """La recommandation **SERVIE**, par le point de composition unique.

    Pas la politique que j'aurais choisie : celle que `pages.py` sert
    réellement, lue à la même source (`POLITIQUE_SERVIE` / `MEMOIRE_SERVIE`).
    Importer une politique nommée en dur aurait mesuré un module choisi par le
    test, et fait rougir la garde `§12` qui interdit exactement ça.
    """
    from app.database import SessionLocal
    from app.services import advice_memory

    with SessionLocal() as db:
        return advice_memory.recommander(
            db, uid,
            politique=advice_memory.POLITIQUE_SERVIE,
            avec_memoire=advice_memory.MEMOIRE_SERVIE,
        )


def _seances():
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    with SessionLocal() as db:
        return list(db.execute(select(WorkoutSession.id)).scalars())


def _lignes(sid):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    with SessionLocal() as db:
        s = db.get(WorkoutSession, sid)
        return [(se.position, se.exercise_name_snapshot, se.substituted_name)
                for se in sorted(s.session_exercises, key=lambda x: x.position)]


def _un_etat(uid, candidats):
    """Trouve un gabarit réel dont l'état de préflight est l'un des attendus.

    Choisir le cas plutôt que le fabriquer : si aucun gabarit du catalogue ne
    produit l'état cherché, la preuve échoue au lieu de se contenter d'un
    environnement inventé pour elle.
    """
    for slug in ("push-a", "push-b", "pull-a", "pull-b", "legs-a", "legs-b",
                 "upper-pecs-delts", "lower-quad-bias", "lower-posterior-bias",
                 "liss-abs", "catch-up-shoulders", _SANS_MATERIEL):
        preparation = _preparer(uid, slug)
        if preparation.etat in candidats:
            return slug, preparation
    return None, None


# ───── cas 1 — environnement NULL : la recommandation et START inchangés ─────


def test_case_1_a_null_environment_leaves_the_recommendation_untouched(client):
    """Porte inerte : elle ne s'annonce même pas dans le contexte servi."""
    reco = _recommander(get_test_user_id())
    assert reco is not None
    assert reco["top"] is not None
    assert reco["context"].get("environnement_actif") is not True


def test_case_1_b_null_environment_leaves_direct_start_untouched(client):
    uid = get_test_user_id()
    assert _lu(uid).available_equipment_items is None
    assert _preparer(uid, "push-a").etat == NON_APPLICABLE

    avant = _seances()
    reponse = client.post(_ROUTE_SEANCES, data={_CHAMP_GABARIT: "push-a"},
                          follow_redirects=False)
    assert reponse.status_code == 303
    apres = [sid for sid in _seances() if sid not in avant]
    assert len(apres) == 1
    # Chemin hérité : rien n'a été substitué, parce que rien n'a été consulté.
    assert [sub for _, _, sub in _lignes(apres[0]) if sub] == []


# ───── cas 2 — `[]` explicite : la porte s'active, le sans-matériel reste ─────


def test_case_2_a_empty_declaration_activates_the_gate(client):
    uid = get_test_user_id()
    _declarer(uid, [])
    assert _lu(uid).available_equipment_items == ()
    reco = _recommander(uid)
    assert reco["context"]["environnement_actif"] is True


def test_case_2_b_the_no_equipment_template_stays_usable(client):
    uid = get_test_user_id()
    _declarer(uid, [])
    preparation = _preparer(uid, _SANS_MATERIEL)
    assert preparation.etat != REFUSE
    assert preparation.autorise is True

    reponse = client.post(_ROUTE_SEANCES, data={_CHAMP_GABARIT: _SANS_MATERIEL},
                          follow_redirects=False)
    assert reponse.status_code == 303
    assert "depart_bloque" not in reponse.headers["location"]
    assert len(_seances()) == 1


# ───── cas 3 — salle équipée : la recommandation reste consciente du lieu ─────


def test_case_3_an_equipped_gym_keeps_an_environment_aware_recommendation(client):
    uid = get_test_user_id()
    _declarer(uid, _SALLE_COMPLETE)
    reco = _recommander(uid)
    contexte = reco["context"]

    assert reco["top"] is not None
    assert contexte["environnement_actif"] is True
    # L'identité matérielle est l'empreinte causale `G9` : elle existe, et elle
    # ne peut pas être celle d'un autre environnement.
    assert contexte["environnement_identite"]
    _declarer(uid, _MAISON)
    assert (_recommander(uid)["context"]["environnement_identite"]
            != contexte["environnement_identite"])


def test_case_3_b_the_four_environment_classes_are_distinguishable(client):
    """Le tableau du `§8` : quatre classes, quatre lectures mesurées."""
    uid = get_test_user_id()
    releve = {}
    for nom, objets in (("salle_complete", _SALLE_COMPLETE),
                        ("salle_limitee", _SALLE_LIMITEE),
                        ("maison", _MAISON),
                        ("sans_materiel", [])):
        _declarer(uid, objets)
        contexte = _recommander(uid)["context"]
        releve[nom] = (contexte["environnement_actif"],
                       contexte.get("environnement_etat"),
                       contexte["environnement_identite"])

    assert all(actif is True for actif, _, _ in releve.values())
    # Quatre environnements distincts produisent quatre empreintes distinctes :
    # l'identité ne se replie pas sur une valeur commode.
    assert len({identite for _, _, identite in releve.values()}) == 4


# ───── cas 4 — gabarit adaptable : START persiste TOUTE la correspondance ─────


def test_case_4_an_adaptable_start_persists_every_planned_to_executed_pair(client):
    uid = get_test_user_id()
    _declarer(uid, _SALLE_LIMITEE)
    slug, preparation = _un_etat(uid, {ADAPTABLE})
    assert slug is not None, "aucun gabarit adaptable : la prémisse est fausse"
    attendu = {position: (prescrit, execute)
               for position, prescrit, execute in preparation.plan}
    assert attendu

    reponse = client.post(_ROUTE_SEANCES, data={_CHAMP_GABARIT: slug},
                          follow_redirects=False)
    assert reponse.status_code == 303
    assert "depart_bloque" not in reponse.headers["location"]

    pose = {position: (prescrit, sub)
            for position, prescrit, sub in _lignes(_seances()[0]) if sub}
    assert pose == attendu


# ───── cas 5 — prouvé infaisable : aucune séance, et une sortie habitable ─────


def test_case_5_a_refused_start_commits_nothing(client):
    uid = get_test_user_id()
    _declarer(uid, _QUASI_RIEN)
    slug, _ = _un_etat(uid, {REFUSE})
    assert slug is not None, "aucun gabarit refusé : la prémisse est fausse"

    reponse = client.post(_ROUTE_SEANCES, data={_CHAMP_GABARIT: slug},
                          follow_redirects=False)
    assert reponse.status_code == 303
    assert _seances() == []


def test_case_5_b_the_user_lands_on_a_usable_recovery_surface(client):
    uid = get_test_user_id()
    _declarer(uid, _QUASI_RIEN)
    slug, _ = _un_etat(uid, {REFUSE})

    reponse = client.post(_ROUTE_SEANCES, data={_CHAMP_GABARIT: slug},
                          follow_redirects=False)
    destination = reponse.headers["location"]
    assert destination.startswith("/plan?depart_bloque=")
    assert destination.endswith("#equipement")

    page = client.get(destination)
    assert page.status_code == 200
    texte = page.text
    # La sortie nomme l'action possible, et n'emprunte aucun registre médical
    # ni aucune métaphore de danger.
    assert "Effacer ma déclaration" in texte
    for interdit in ("blessure", "danger", "impossible de t'entraîner",
                     "contre-indiqu"):
        assert interdit not in texte.lower()


# ───── cas 6 — UNKNOWN : non bloquant, contrat TRAIN A `§1.B` ─────


def test_case_6_an_uncertain_start_is_never_blocked(client):
    uid = get_test_user_id()
    _declarer(uid, _MAISON)
    slug, preparation = _un_etat(uid, {INCERTAIN})
    assert slug is not None, "aucun gabarit incertain : la prémisse est fausse"
    assert preparation.autorise is True
    # L'incertain ne fabrique AUCUNE adaptation : on ne devine pas un substitut
    # pour un fait qu'on ne connaît pas.
    assert preparation.plan == ()

    reponse = client.post(_ROUTE_SEANCES, data={_CHAMP_GABARIT: slug},
                          follow_redirects=False)
    assert reponse.status_code == 303
    assert "depart_bloque" not in reponse.headers["location"]
    assert len(_seances()) == 1


# ───── cas 7 — les familles grossières ne touchent PAS l'inventaire concret ─────


def test_case_7_changing_only_coarse_families_leaves_the_inventory_intact(client):
    uid = get_test_user_id()
    _declarer(uid, _MAISON)
    avant = _lu(uid).available_equipment_items

    reponse = client.post("/profile/preferences",
                          data={"equipment_declared": "1",
                                "equipment": ["cable", "machines"]},
                          follow_redirects=False)
    assert reponse.status_code == 303

    apres = _lu(uid)
    assert apres.available_equipment_items == avant
    # Et la réciproque de la non-dérivation : cocher « cable » n'a inventé
    # aucun appareil à poulie concret.
    assert "dual_adjustable_pulley" not in (apres.available_equipment_items or ())


# ───── cas 8 — écrire l'inventaire n'écrase ni cadence, ni focus, ni familles ─────


def test_case_8_saving_the_inventory_overwrites_no_legacy_field(client):
    uid = get_test_user_id()
    client.post("/profile/preferences",
                data={"sessions_per_week": "4",
                      "focus_1": "chest", "focus_2": "back",
                      "equipment_declared": "1",
                      "equipment": ["dumbbells", "barbell"]},
                follow_redirects=False)
    avant = _lu(uid)

    reponse = client.post("/plan/equipement",
                          data={"equipement_declared": "1",
                                "equipement": ["dumbbells", "adjustable_bench"]},
                          follow_redirects=False)
    assert reponse.status_code == 303

    apres = _lu(uid)
    assert apres.sessions_per_week == avant.sessions_per_week
    assert apres.focus_priorities == avant.focus_priorities
    assert apres.available_equipment == avant.available_equipment
    # L'ordre stocké est celui du registre, pas celui de la soumission : le
    # contrat normalise pour que deux déclarations identiques se comparent.
    assert set(apres.available_equipment_items) == {"dumbbells", "adjustable_bench"}
    assert apres.available_equipment_items == ("adjustable_bench", "dumbbells")


# ───── cas 9 — le formulaire hérité n'efface PAS l'inventaire concret ─────


def test_case_9_the_legacy_form_never_erases_the_inventory(client):
    uid = get_test_user_id()
    _declarer(uid, _SALLE_LIMITEE)

    # Soumission la plus destructrice possible du formulaire hérité : tout vide,
    # marqueur présent — c'est-à-dire « je déclare explicitement aucun matériel ».
    client.post("/profile/preferences",
                data={"sessions_per_week": "", "focus_1": "",
                      "equipment_declared": "1"},
                follow_redirects=False)

    assert _lu(uid).available_equipment == ()
    assert _lu(uid).available_equipment_items == tuple(_SALLE_LIMITEE)


def test_case_9_b_the_legacy_form_posts_to_a_different_route(client):
    """La garde de forme derrière le cas 9 : deux points d'écriture séparés.

    `Sb_TRAIN_2` a déjà perdu des données par **remplacement partiel** ; la
    séparation des routes est ce qui empêche la troisième instance.
    """
    page = client.get(_ROUTE_PLAN)
    assert "/plan/equipement\"" in page.text
    assert "/profile/preferences\"" in page.text


# ───── cas 10 — propriété : l'environnement d'autrui est hors d'atteinte ─────


def _second_utilisateur(client):
    from starlette.responses import Response

    from app.database import SessionLocal
    from app.models.user import User
    from app.services.auth import create_session_cookie
    from tests.helpers import TESTPASS_BCRYPT_HASH

    with SessionLocal() as db:
        autre = User(username="voisin", password_hash=TESTPASS_BCRYPT_HASH)
        db.add(autre)
        db.commit()
        db.refresh(autre)
        uid = autre.id

    sonde = Response()
    create_session_cookie(sonde, uid)
    return uid, sonde.headers["set-cookie"]


def test_case_10_a_user_can_never_write_another_users_environment(client):
    import httpx

    mien, voisin_cookie = get_test_user_id(), None
    voisin, voisin_cookie = _second_utilisateur(client)
    _declarer(mien, _SALLE_LIMITEE)
    _declarer(voisin, _MAISON)

    client.cookies.clear()
    client.cookies.extract_cookies(httpx.Response(
        200, headers=[("set-cookie", voisin_cookie)],
        request=httpx.Request("GET", str(client.base_url))))

    client.post("/plan/equipement",
                data={"equipement_declared": "1", "equipement": ["ab_wheel"]},
                follow_redirects=False)

    # Le voisin a écrit le SIEN, et rien d'autre : la route n'accepte aucun
    # `user_id` de formulaire, le propriétaire vient du cookie authentifié.
    assert _lu(voisin).available_equipment_items == ("ab_wheel",)
    assert _lu(mien).available_equipment_items == tuple(_SALLE_LIMITEE)


def test_case_10_b_a_user_never_reads_another_users_environment(client):
    import httpx

    mien = get_test_user_id()
    voisin, voisin_cookie = _second_utilisateur(client)
    _declarer(mien, ["smith_machine", "leg_press"])
    _declarer(voisin, [])

    client.cookies.clear()
    client.cookies.extract_cookies(httpx.Response(
        200, headers=[("set-cookie", voisin_cookie)],
        request=httpx.Request("GET", str(client.base_url))))

    page = client.get(_ROUTE_PLAN)
    assert page.status_code == 200
    # Le voisin déclare `[]` : aucune case ne doit être rendue cochée.
    assert 'value="smith_machine" checked' not in page.text
    assert 'value="leg_press" checked' not in page.text
    # Et son propre préflight se calcule sur SON environnement.
    assert _preparer(voisin, _SANS_MATERIEL).etat in {NATIF, ADAPTABLE, INCERTAIN}
