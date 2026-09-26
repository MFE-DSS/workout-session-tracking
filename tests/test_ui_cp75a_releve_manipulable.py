"""`UI-CP7.5A` — le relevé corporel est la PORTE de sa propre écriture.

La règle macro d'acceptation (`arbitrage §1`) : une tranche ne compte que si
elle change matériellement TOPOLOGIE D'OBJETS · MODÈLE D'INTERACTION ·
HIÉRARCHIE DE DÉCISION · PROPRIÉTÉ DE L'INFORMATION · CHROME PERSISTANT.
Déplacer les mêmes blocs ou replier l'héritage dans un `<details>` n'en est
pas un. Ces gardes épinglent les axes.

⚠ CHAQUE GARDE ICI A ÉTÉ VUE ROUGE PAR MUTATION avant d'être gardée verte.
"""
from __future__ import annotations

import pathlib
import re

RACINE = pathlib.Path(__file__).resolve().parent.parent
PROFIL = RACINE / "app/templates/profile.html"


def _consentir() -> None:
    from app.database import SessionLocal
    from app.models.user import User
    from app.services import body_profile as bp

    with SessionLocal() as db:
        bp.set_consent(db, db.query(User).first().id, True)


def _releve(client) -> str:
    page = client.get("/profile").text
    return page[page.index('id="bl-releve"'):page.index("bl-drawers")]


def _acquisition(client) -> str:
    """Toute la surface d'acquisition : le relevé ET la réponse primaire.

    ⚠ LE POIDS N'A PAS DE LIGNE, ET C'EST DÉLIBÉRÉ. Mesuré au rendu,
    « 78,4 kg » paraissait deux fois à trois lignes d'écart — une fois au
    rang `DISPLAY` dans la réponse primaire, une fois en tête du relevé. Sa
    PORTE existe déjà au repos, hors tiroir : le quick-log, que la décision
    opérateur garde là parce qu'une donnée volatile qu'on doit corriger vite
    ne se note pas derrière un geste de plus.

    Une garde qui ne regarderait que le relevé conclurait donc que le poids
    n'est pas acquérable. Elle mesurerait le mauvais objet.
    """
    page = client.get("/profile").text
    return page[page.index('class="body-ledger"'):page.index("bl-drawers")]


# ───────── AXE · MODÈLE D'INTERACTION ─────────


def test_chaque_fait_acquerable_porte_sa_propre_porte(client):
    """« USER TOUCHES THE FACT -> USER EDITS THAT FACT. »

    Le relevé et l'écriture étaient à trois écrans l'un de l'autre, sans
    aucun chemin entre eux : toucher une donnée n'ouvrait rien.
    """
    _consentir()
    releve = _releve(client)
    acquisition = _acquisition(client)

    from app.services.body_ledger import PLAN_DU_RELEVE

    for cle, libelle, _, champs in PLAN_DU_RELEVE:
        if cle == "weight_kg":
            # Sa porte est le quick-log, au repos — voir `_acquisition`.
            continue
        assert f'id="fait-{cle}"' in releve, (
            f"« {libelle} » n'a pas de ligne dans le relevé"
        )
        for champ in champs:
            assert f'name="{champ}"' in releve, (
                f"la ligne « {libelle} » n'ouvre pas la saisie de {champ!r}"
            )

    assert 'name="weight_kg"' in acquisition, (
        "le poids n'a plus aucune porte : ni ligne de relevé, ni quick-log"
    )


def test_les_treize_faits_capturables_sont_tous_joignables(client):
    """⚠ LE RELEVÉ N'EN VOYAIT QUE SIX SUR TREIZE.

    Cou, hanches, largeur d'épaules, bras, et les côtés gauche/droit des
    cuisses et mollets étaient saisissables et jamais relus — donc sans
    ligne, donc sans porte possible. C'est la moitié du corps.
    """
    _consentir()
    acquisition = _acquisition(client)

    from app.services import body_profile as bp

    manquants = [
        spec.key for spec in bp.BODY_MEASUREMENT_FIELDS
        if f'name="{spec.key}"' not in acquisition
    ]
    assert not manquants, (
        f"{len(manquants)} faits capturables sans porte dans le relevé : "
        f"{manquants}"
    )


def test_une_intention_n_ouvre_jamais_plus_de_deux_valeurs(client):
    """« One user intent must never open fourteen unrelated inputs. »

    La paire gauche/droite se comprend ensemble donc s'édite ensemble ;
    au-delà, ce n'est plus une intention, c'est une grille.
    """
    _consentir()
    releve = _releve(client)

    for bloc in re.findall(r'<details class="bl-fait" id="fait-([\w]+)">'
                           r'(.*?)</details>', releve, flags=re.S):
        cle, corps = bloc
        # `measured_at` est une précision de la même saisie, pas une valeur.
        valeurs = [n for n in re.findall(r'name="([\w]+)"', corps)
                   if n not in {"measured_at", "granted", "retour"}]
        assert len(valeurs) <= 2, (
            f"la ligne « {cle} » ouvre {len(valeurs)} valeurs : {valeurs}"
        )


def test_aucun_bouton_editer_n_est_repete_sur_chaque_ligne(client):
    """`§7` — « No duplicated "edit" button on every row if the row itself
    can truthfully own the interaction. »"""
    _consentir()
    releve = _releve(client)
    for mot in ("Éditer", "Modifier", "Corriger"):
        assert releve.count(mot) == 0, (
            f"« {mot} » est répété sur les lignes — la ligne EST l'action"
        )


def test_l_affordance_ne_depend_pas_du_style(client):
    """`§7` — « the fact that a row is editable must not depend on visual
    styling alone. »

    Le `<summary>` porte NATIVEMENT le rôle de bouton et son état déplié :
    un lecteur d'écran l'annonce même si le chevron n'était pas rendu. La
    garde vérifie que la porte est bien un élément natif, pas un `<div>`
    rendu cliquable au style.

    ⚠ Elle compte désormais les portes DES DEUX SORTES, parce que `D4` en a
    créé deux : la ligne d'un fait connu, et l'intention dans l'entrée
    d'acquisition. Un seuil fixe (« au moins dix ») dirait faux dans un état
    peu rempli — ce qui compte est que CHAQUE porte soit native.
    """
    _consentir()
    releve = _releve(client)

    portes = re.findall(r'<details class="bl-fait[^"]*" id="fait-[\w]+">\s*'
                        r'<summary', releve)
    ids = re.findall(r'<details class="bl-fait[^"]*" id="fait-([\w]+)">',
                     releve)
    assert ids, "aucune porte de fait dans le relevé"
    assert len(portes) == len(ids), (
        f"{len(ids) - len(portes)} porte(s) de fait ne commencent pas par un "
        "`<summary>` natif — l'affordance dépendrait alors du style"
    )

    # L'entrée d'acquisition elle-même est une porte native.
    assert re.search(r'<details class="bl-acquisition"[^>]*>\s*<summary',
                     releve), (
        "l'entrée d'acquisition n'est pas un contrôle natif"
    )


# ───────── AXE · TOPOLOGIE D'OBJETS ─────────


def test_le_formulaire_de_treize_champs_a_disparu(client):
    """« Do NOT merely replace the current 14-field disclosure with another
    form behind a different heading. »"""
    page = client.get("/profile").text
    assert 'class="body-profile"' not in page
    assert "saisie complète" not in page
    assert 'id="measurements"' not in page
    assert 'id="reference_data"' not in page


def test_le_releve_ne_pose_aucune_carte():
    """La contrainte centrale de `BODY_LEDGER` survit à sa manipulation."""
    src = re.sub(r"\{#.*?#\}", "", PROFIL.read_text(encoding="utf-8"),
                 flags=re.S)
    for attr in re.findall(r'class="([^"]*)"', src):
        assert "card" not in attr.split(), (
            f"une carte est apparue dans BODY_LEDGER : class=\"{attr}\""
        )


# ───────── AXE · PROPRIÉTÉ DE L'INFORMATION ─────────


def test_la_reponse_primaire_et_la_ligne_poids_ne_divergent_jamais(client):
    """⚠ LE DÉFAUT QUE L'ACQUISITION PAR LIGNE RENDAIT ATTEIGNABLE.

    La réponse primaire lisait la dernière LIGNE de mesure
    (`get_latest_measurement`) ; le relevé résout CHAMP PAR CHAMP. Tant que
    le seul écrivain postait les treize champs d'un coup, les deux
    coïncidaient. Dès qu'une feuille écrit un fait isolé, ils divergent.

    Le scénario ci-dessous est exactement celui d'un utilisateur ordinaire :
    se peser lundi, mesurer son tour de taille jeudi.
    """
    _consentir()
    client.post("/profile/measurements", data={"weight_kg": "78.4"},
                follow_redirects=False)
    client.post("/profile/measurements", data={"waist_cm": "84.5"},
                follow_redirects=False)

    page = client.get("/profile").text
    assert "Non pesé" not in page, (
        "la réponse primaire a perdu le poids parce que la mesure suivante "
        "ne le portait pas — deux lectures de la même donnée divergent"
    )
    assert "78,4" in page
    assert "84,5" in page


def test_une_paire_laterale_ne_melange_pas_deux_dates(client):
    """Les deux côtés viennent de la MÊME ligne, ou un seul côté est utilisé.

    Moyenner la cuisse gauche de mardi avec la droite de janvier
    fabriquerait une valeur qui n'a jamais été mesurée. Règle reprise de
    `morphology_runtime`, pas réinventée.
    """
    from datetime import UTC, datetime, timedelta

    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement
    from app.models.user import User
    from app.services.body_ledger import construire_releve

    with SessionLocal() as db:
        u = db.query(User).first()
        maintenant = datetime.now(UTC)
        db.add(BodyMeasurement(user_id=u.id, measured_at=maintenant,
                               arm_cm_left=38.0))
        db.add(BodyMeasurement(user_id=u.id,
                               measured_at=maintenant - timedelta(days=200),
                               arm_cm_right=42.0))
        db.commit()

        ligne = next(x for x in construire_releve(db, u.id, u)
                     if x.cle == "arm_cm")

    # « 38,0 » et non « 38 » : le dixième d'une mesure au mètre ruban a été
    # mesuré, et `nombre_fr(_, 1)` — le filtre canonique — ne l'escamote pas.
    assert ligne.valeur == "38,0", (
        f"la moyenne a mêlé deux dates : {ligne.valeur} — la ligne la plus "
        "récente ne porte que le côté gauche, c'est lui qui vaut"
    )
    assert ligne.provenance == "côté gauche seul", (
        "la provenance ne dit pas qu'un seul côté a été mesuré"
    )


def test_un_fait_absent_n_invente_pas_de_provenance(client):
    """« mesure directe » à côté d'un tiret annoncerait une mesure qui
    n'existe pas. L'ignorance est un état légitime, elle ne se déguise pas
    en méthode."""
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.body_ledger import construire_releve

    with SessionLocal() as db:
        u = db.query(User).first()
        for ligne in construire_releve(db, u.id, u):
            if not ligne.connue:
                assert ligne.provenance is None, (
                    f"« {ligne.libelle} » est absent et annonce pourtant une "
                    f"provenance : {ligne.provenance!r}"
                )
                assert ligne.age is None


def test_le_derive_n_a_pas_de_porte(client):
    """Un ape index ne s'écrit pas : il vaut ses deux sources. Une ligne qui
    s'ouvrirait sur rien serait un instrument en panne."""
    from datetime import UTC, datetime

    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement
    from app.models.user import User

    with SessionLocal() as db:
        u = db.query(User).first()
        u.height_cm = 181
        db.add(BodyMeasurement(user_id=u.id, measured_at=datetime.now(UTC),
                               wingspan_cm=186.0))
        db.commit()

    page = client.get("/profile").text
    assert "Ape index" in page
    assert 'id="fait-ape_index_cm"' not in page, (
        "le dérivé porte une porte d'écriture"
    )
    assert "bl-fait--derive" in page
