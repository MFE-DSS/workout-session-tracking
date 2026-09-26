"""`UI-CP7.5A` — le consentement vit à l'INTENTION, et il était ouvert.

⚠ LE DÉFAUT ÉTAIT RÉEL, ET IL ÉTAIT EN PRODUCTION.

`app/models/body_consent.py` modélise un consentement explicite, versionné,
horodaté et retirable. `body_profile.has_active_consent` l'interroge. Une
seule route l'appliquait : `POST /body/consent`, sur le routeur `/body`.

Or `/body` est ÉTEINT en production — mesuré par requête HTTP sur
spignos.com, `/body` et `/body/measurements/new` rendent **404**
(`body_assessment_enabled` est OFF). Donc :

* le consentement n'avait **aucune porte atteignable** ;
* `POST /profile/measurements`, elle, était atteignable et **n'interrogeait
  pas le consentement du tout**.

Le contrat écrit disait « collection requires active consent ». Le produit
écrivait sans jamais demander. Ce n'est pas un défaut d'interface : c'est un
contrat de données non tenu.

⚠ L'ARBITRAGE INTERDIT DE RALLUMER `/body` (« Do NOT revive /body … NOT
restored as a second user destination »). La sémantique du service est donc
réutilisée telle quelle — même table, même versionnement — et seule la PORTE
est replacée dans le parcours canonique.
"""
from __future__ import annotations

import re


def _uid() -> int:
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        return db.query(User).first().id


def _consentir(accorde: bool) -> None:
    from app.database import SessionLocal
    from app.services import body_profile as bp

    with SessionLocal() as db:
        bp.set_consent(db, _uid(), accorde)


def _mesures() -> list:
    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement

    with SessionLocal() as db:
        return list(
            db.query(BodyMeasurement).filter_by(user_id=_uid()).all()
        )


# ───────── LE GARDE SERVEUR ─────────


def test_sans_consentement_la_route_refuse_d_ecrire(client):
    """⚠ LA MOITIÉ QUI COMPTE. Router l'intention dans l'interface sans
    fermer l'endpoint aurait été du théâtre : le formulaire masqué, la porte
    grande ouverte."""
    _consentir(False)
    avant = len(_mesures())

    r = client.post("/profile/measurements", data={"waist_cm": "84.5"},
                    follow_redirects=False)

    assert r.status_code == 303
    assert "consent_required=1" in r.headers["location"]
    assert len(_mesures()) == avant, (
        "une mesure a été écrite sans consentement actif"
    )


def test_avec_consentement_la_route_ecrit(client):
    """La contrepartie : le garde ne doit pas bloquer l'utilisateur qui a
    consenti. Une garde qui refuse tout le monde n'est pas un garde."""
    _consentir(True)
    avant = len(_mesures())

    r = client.post("/profile/measurements", data={"waist_cm": "84.5"},
                    follow_redirects=False)

    assert r.status_code == 303
    assert "measure_saved=1" in r.headers["location"]
    assert len(_mesures()) == avant + 1


def test_le_retrait_du_consentement_ne_supprime_rien(client):
    """`§3` — le consentement porte la COLLECTE, pas la lecture.

    « It is not required for: reading already-held data / export /
    deletion. » Retirer son autorisation ne doit donc rien effacer : la
    donnée reste lisible et supprimable à la demande de son propriétaire.
    """
    _consentir(True)
    client.post("/profile/measurements", data={"waist_cm": "84.5"},
                follow_redirects=False)
    assert len(_mesures()) == 1

    _consentir(False)
    assert len(_mesures()) == 1, (
        "retirer le consentement a détruit des données — il gouverne la "
        "collecte, jamais la conservation"
    )
    # Et le relevé reste LISIBLE.
    page = client.get("/profile").text
    assert "84,5" in page, "BODY_LEDGER n'est plus lisible sans consentement"


# ───────── LA PORTE, DANS LE PARCOURS CANONIQUE ─────────


def test_la_porte_de_consentement_vit_dans_le_profil_pas_dans_body(client):
    """⚠ `/body` N'EST PAS RALLUMÉ POUR RÉCUPÉRER SA PAGE."""
    _consentir(False)
    page = client.get("/profile").text

    assert "/profile/consent" in page, (
        "aucune porte de consentement dans le parcours canonique"
    )
    assert "/body/consent" not in page, (
        "le profil pointe vers la surface héritée `/body`, que l'arbitrage "
        "§2 interdit de revivifier"
    )


def test_le_consentement_n_est_pas_un_panneau_au_repos(client):
    """`§3` — « Do NOT permanently place a large consent panel at rest. »

    L'étape de consentement vit DANS la feuille d'acquisition, donc derrière
    le geste qui la déclenche. Au repos, le relevé n'en dit qu'une ligne.
    """
    _consentir(False)
    page = client.get("/profile").text

    invite = "J'autorise l'enregistrement de mes mesures"
    assert invite in page, "l'étape de consentement n'existe pas"

    # Chaque occurrence de l'invite est à l'intérieur d'un `<details>` fermé.
    for bloc in re.findall(r"<details class=\"bl-fait\".*?</details>",
                           page, flags=re.S):
        if invite in bloc:
            assert "<details class=\"bl-fait\" id=" in bloc
            assert " open" not in bloc.split(">", 1)[0], (
                "une feuille portant l'étape de consentement est ouverte au "
                "repos — c'est le panneau que §3 interdit"
            )


def test_le_consentement_n_est_pas_empaquete_dans_enregistrer(client):
    """`§3` — « Do NOT bundle consent invisibly into "Save". »

    Sans consentement, la feuille ne montre PAS de champ de saisie : elle
    montre l'action explicite. L'acquisition devient disponible ensuite.
    """
    _consentir(False)
    page = client.get("/profile").text
    releve = page[page.index('id="bl-releve"'):page.index("bl-drawers")]

    assert 'name="waist_cm"' not in releve, (
        "un champ de saisie est offert alors que le consentement manque — "
        "« Enregistrer » emporterait le consentement avec lui"
    )

    _consentir(True)
    page = client.get("/profile").text
    releve = page[page.index('id="bl-releve"'):page.index("bl-drawers")]
    assert 'name="waist_cm"' in releve, (
        "consentement accordé et l'acquisition reste indisponible"
    )


def test_le_releve_reste_lisible_sans_consentement(client):
    """`§3` — « If consent is absent: BODY_LEDGER remains readable. »"""
    _consentir(True)
    client.post("/profile/measurements", data={"chest_cm": "104"},
                follow_redirects=False)
    _consentir(False)

    page = client.get("/profile").text
    assert "Tour de poitrine" in page
    assert "104" in page


def test_l_ancre_de_retour_ne_peut_pas_etre_choisie_par_le_client(client):
    """Un fragment de redirection venu du formulaire est un paramètre
    contrôlé par le client. Il est borné aux ancres connues du relevé."""
    _consentir(False)
    r = client.post(
        "/profile/consent",
        data={"granted": "1", "retour": "//evil.example/x"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert "evil.example" not in r.headers["location"]
    assert r.headers["location"] == "/profile?consent_saved=1"
