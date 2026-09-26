"""`UI-CP7.5A` — le contrat d'écriture des mesures corporelles.

CE QUI BLOQUAIT, ET POURQUOI CE N'ÉTAIT PAS UN PROBLÈME DE MISE EN PAGE
--------------------------------------------------------------------------
`BODY_LEDGER` en lecture est passé en 2.0. L'ACQUISITION, non — et l'écran
montre encore la matrice des treize champs.

Ce n'était pas un choix de composition. `update_measurement` écrivait **tous**
les champs depuis `cleaned.get(clé)` : un champ absent devenait `NULL`.
Corriger son tour de taille aurait donc effacé son poids, ses bras et ses
cuisses. **La matrice entière était la seule forme que le contrat d'écriture
autorisait.**

Ces gardes prouvent les quatre propriétés que le `§7` exige, AVANT toute
refonte d'écran.

⚠ CE QU'ELLES NE FONT PAS
----------------------------
Aucun cadre `PATCH` générique pour l'application. Le contrat change pour
**cette** ressource, dont la sémantique de remplacement était le blocage.
"""
from __future__ import annotations

import itertools

# ⚠ La fixture `body_client` existe déjà et allume le drapeau de
# fonctionnalité. On l'importe : une seconde copie dériverait de l'originale,
# et le dépôt en porte assez d'exemples.
from tests.test_body_profile import body_client  # noqa: F401

_RANG = itertools.count()


def _utilisateur() -> int:
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        u = User(username=f"corps-{next(_RANG)}", password_hash="-")
        db.add(u)
        db.commit()
        return u.id


def _mesure_complete(uid: int):
    """Une mesure peuplée sur plusieurs familles de champs.

    ⚠ LE CAS DISCRIMINANT EST SEMÉ ICI. Une mesure qui ne porterait qu'un
    champ ne pourrait pas montrer qu'un autre a été préservé — la garde
    passerait à vide.
    """
    from app.database import SessionLocal
    from app.services import body_profile as bp

    valeurs = {
        "weight_kg": 78.5,
        "waist_cm": 84.0,
        "neck_cm": 38.0,
        "chest_cm": 104.0,
        "arm_cm_left": 36.0,
        "arm_cm_right": 36.5,
        "thigh_cm_left": 58.0,
        "thigh_cm_right": 58.5,
    }
    with SessionLocal() as db:
        m = bp.create_measurement(db, uid, valeurs)
        return m.id, valeurs


def _relire(uid: int, mid: int) -> dict:
    from app.database import SessionLocal
    from app.services import body_profile as bp

    with SessionLocal() as db:
        m = bp.get_owned_measurement(db, uid, mid)
        return {s.key: getattr(m, s.key) for s in bp.BODY_MEASUREMENT_FIELDS}


def _ecrire(uid: int, mid: int, soumis: dict[str, float | None]) -> None:
    """Écrit comme le fait la route : seuls les champs soumis sont écrits."""
    from app.database import SessionLocal
    from app.services import body_profile as bp

    with SessionLocal() as db:
        m = bp.get_owned_measurement(db, uid, mid)
        bp.update_measurement(
            db, m,
            {k: v for k, v in soumis.items() if v is not None},
            champs_soumis=set(soumis),
        )


# ═══════════ LES QUATRE PREUVES DU `§7` ═══════════


def test_mettre_a_jour_le_tour_de_taille_seul_preserve_tout_le_reste(client):
    """⚠ LE CAS QUI DÉFINIT LA TRANCHE."""
    uid = _utilisateur()
    mid, avant = _mesure_complete(uid)

    _ecrire(uid, mid, {"waist_cm": 82.0})
    apres = _relire(uid, mid)

    assert apres["waist_cm"] == 82.0, "la valeur soumise n'a pas été écrite"
    for cle, valeur in avant.items():
        if cle == "waist_cm":
            continue
        assert apres[cle] == valeur, (
            f"« {cle} » a été effacé alors qu'il n'était pas soumis : "
            f"{valeur} → {apres[cle]}"
        )


def test_mettre_a_jour_le_poids_seul_preserve_tout_le_reste(client):
    """Le pendant, sur un champ d'une autre famille sémantique.

    Une garde qui ne vérifierait qu'un seul champ prouverait que CE champ
    marche, pas que le contrat tient.
    """
    uid = _utilisateur()
    mid, avant = _mesure_complete(uid)

    _ecrire(uid, mid, {"weight_kg": 77.0})
    apres = _relire(uid, mid)

    assert apres["weight_kg"] == 77.0
    for cle, valeur in avant.items():
        if cle == "weight_kg":
            continue
        assert apres[cle] == valeur, f"« {cle} » perdu : {valeur} → {apres[cle]}"


def test_effacer_une_valeur_reste_un_geste_explicite_et_borne(client):
    """⚠ ON N'A PAS RENDU L'EFFACEMENT IMPOSSIBLE, ON L'A RENDU EXPLICITE.

    Un champ **soumis vide** s'efface — c'est un geste légitime. Ce qui
    disparaît est l'effacement par ABSENCE, qui n'était le geste de personne.
    """
    uid = _utilisateur()
    mid, avant = _mesure_complete(uid)

    _ecrire(uid, mid, {"neck_cm": None})
    apres = _relire(uid, mid)

    assert apres["neck_cm"] is None, "l'effacement explicite n'a pas eu lieu"
    for cle, valeur in avant.items():
        if cle == "neck_cm":
            continue
        assert apres[cle] == valeur, (
            f"l'effacement a débordé sur « {cle} » : {valeur} → {apres[cle]}"
        )


def test_la_date_de_mesure_reste_veridique(client):
    """`measured_at` dit QUAND la mesure a été prise.

    Une correction partielle ne doit pas la déplacer : sinon une valeur
    saisie il y a deux semaines se mettrait à dater d'aujourd'hui, et les
    courbes de progression mentiraient.
    """
    from app.database import SessionLocal
    from app.services import body_profile as bp

    uid = _utilisateur()
    mid, _ = _mesure_complete(uid)
    with SessionLocal() as db:
        avant = bp.get_owned_measurement(db, uid, mid).measured_at

    _ecrire(uid, mid, {"waist_cm": 83.0})

    with SessionLocal() as db:
        apres = bp.get_owned_measurement(db, uid, mid).measured_at
    assert apres == avant, (
        f"`measured_at` a bougé lors d'une correction partielle : "
        f"{avant} → {apres}"
    )


# ═══════════ CE QUE LE CHANGEMENT NE DOIT PAS CASSER ═══════════


def test_sans_champs_soumis_le_remplacement_integral_survit(client):
    """⚠ LE DÉFAUT RESTE LE COMPORTEMENT HISTORIQUE.

    Changer la sémantique par DÉFAUT ferait muter en silence tout appelant
    qu'on n'a pas relu. Un appelant qui soumet réellement l'ensemble garde
    donc le remplacement.
    """
    from app.database import SessionLocal
    from app.services import body_profile as bp

    uid = _utilisateur()
    mid, _ = _mesure_complete(uid)

    with SessionLocal() as db:
        m = bp.get_owned_measurement(db, uid, mid)
        bp.update_measurement(db, m, {"waist_cm": 80.0})

    apres = _relire(uid, mid)
    assert apres["waist_cm"] == 80.0
    assert apres["weight_kg"] is None, (
        "le remplacement intégral a disparu — des appelants non relus "
        "changeraient de sémantique en silence"
    )


def test_la_route_d_edition_ne_perd_plus_les_champs_non_soumis(body_client):
    """⚠ LA PREUVE SUR LA VRAIE ROUTE, PAS SUR LE SERVICE.

    Le service peut tenir le contrat pendant que la route le contourne :
    `_form_to_raw` fabrique les treize clés quoi qu'il arrive, en substituant
    `""` aux absentes. C'est exactement le genre d'écart qu'une garde de
    service ne verrait pas.

    ⚠ On emploie `body_client` — la fixture qui EXISTE et qui allume le
    drapeau `BODY_ASSESSMENT_ENABLED` — plutôt que d'en écrire une seconde.
    Sans le drapeau, `/body*` rend 404 avant même l'authentification, et la
    garde passerait en accusant une route qu'elle n'a jamais atteinte.
    """
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.user import User
    from app.services import body_profile as bp

    with SessionLocal() as db:
        uid = db.execute(select(User)).scalars().first().id
    with SessionLocal() as db:
        m = bp.create_measurement(
            db, uid, {"weight_kg": 80.0, "waist_cm": 85.0, "chest_cm": 100.0})
        mid = m.id

    r = body_client.post(f"/body/measurements/{mid}/edit",
                         data={"waist_cm": "83"}, follow_redirects=False)
    assert r.status_code in {303, 302}, f"{r.status_code}: {r.text[:200]}"

    apres = _relire(uid, mid)
    assert apres["waist_cm"] == 83.0
    assert apres["weight_kg"] == 80.0, (
        "la route a effacé le poids que le formulaire ne portait pas"
    )
    assert apres["chest_cm"] == 100.0, (
        "la route a effacé le tour de poitrine non soumis"
    )
