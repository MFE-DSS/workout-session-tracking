"""`UX4_01` — Profil : de l'administration de données à l'état lisible.

CE QUE CETTE TRANCHE APPLIQUE, ET RIEN D'AUTRE
-----------------------------------------------
Le `PRODUCT PLACEMENT & ACQUISITION LEDGER` (`AUREN_UI_BLUEPRINT §5ter`) dit
que **seules les lignes `OPERATOR_DECISION` sont normatives pour un build**.
Sur le Profil, il y en a **une** :

    Tension artérielle → REMOVE_NO_ASK de l'acquisition courante
                       · données existantes PRÉSERVÉES
                       · aucune permission connectée demandée

Taille, poids, FC repos et morphométrie restent des **candidats**. Cette
tranche n'y touche pas — un candidat n'est pas une décision.

POURQUOI UNE SOUSTRACTION NE PART PAS SEULE (`CLAUDE.md §5.3`)
---------------------------------------------------------------
Retirer deux champs laisserait le Profil exactement aussi long : 6,6 écrans,
641 mots, 39 contrôles. La suppression voyage donc avec ce qui la remplace —
**l'état lisible**, qui répond « qu'est-ce qu'AUREN sait de moi ? » avant de
proposer de le modifier.

LE PIÈGE QUE LA PHASE 2 A DÉJÀ ENSEIGNÉ
-----------------------------------------
`profile_body_submit` écrivait `user.bp_systolic = _int_or_none(bp_systolic)`
avec `bp_systolic: Form() = ""`. **Retirer le champ du gabarit suffisait donc à
EFFACER la valeur stockée au prochain enregistrement.** C'est le même piège de
sérialisation que les champs masqués de la console de séance : un champ absent
du DOM ne vaut pas « inchangé », il vaut « vide ».

La décision dit « données existantes préservées ». La garde le prouve plutôt
que de l'espérer.
"""
from __future__ import annotations

import pathlib
import re

TEMPLATE = (pathlib.Path(__file__).resolve().parent.parent
            / "app/templates/profile.html")
ROUTER = (pathlib.Path(__file__).resolve().parent.parent
          / "app/routers/auth_routes.py")


def _set_blood_pressure(username: str, systolic: int, diastolic: int) -> None:
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.execute(
            select(User).where(User.username == username)).scalar_one()
        user.bp_systolic = systolic
        user.bp_diastolic = diastolic
        db.commit()


def _blood_pressure(username: str) -> tuple[int | None, int | None]:
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.execute(
            select(User).where(User.username == username)).scalar_one()
        return user.bp_systolic, user.bp_diastolic


# ───────────── la décision opérateur : REMOVE_NO_ASK ─────────────


def test_blood_pressure_is_no_longer_requested(client):
    """`OPERATOR_DECISION` — retirée de l'acquisition courante.

    Mesuré avant la tranche : la tension traverse `providers.py` et
    `coach_report.py` jusqu'à un gabarit, sans jamais atteindre
    `recommendation.py` ni `zone_recovery.py`. Elle est affichée, elle ne
    décide rien — la justification de la demander est donc faible et non
    démontrée.
    """
    body = client.get("/profile").text
    for field in ('name="bp_systolic"', 'name="bp_diastolic"'):
        assert field not in body, f"{field} est encore demandé"


def test_existing_blood_pressure_survives_a_profile_save(client):
    """**La garde qui compte.** « Données existantes préservées » n'est pas une
    intention : c'est un comportement, et il se prouve en enregistrant.

    Sans elle, retirer les champs effacerait silencieusement l'historique de
    tout utilisateur qui touche à son profil.
    """
    _set_blood_pressure("testuser", 128, 82)

    resp = client.post("/profile/body",
                       data={"email": "", "height_cm": "180",
                             "resting_hr": "58"},
                       follow_redirects=False)
    assert resp.status_code in (200, 302, 303)

    assert _blood_pressure("testuser") == (128, 82), (
        "un enregistrement de profil a effacé la tension stockée"
    )


def test_the_handler_no_longer_writes_the_blood_pressure_columns():
    """Garde structurelle : tant que le handler ASSIGNE ces colonnes, un champ
    absent vaut `None`. Ne pas les assigner est ce qui rend la préservation
    vraie, pas un heureux hasard."""
    src = ROUTER.read_text(encoding="utf-8")
    handler = src.split("async def profile_body_submit", 1)[1].split(
        "\n@router.", 1)[0]
    # Le handler EXPLIQUE en docstring pourquoi il n'assigne plus ces colonnes,
    # donc la chaîne apparaît dans sa propre justification. Une garde qui lit
    # la prose rougirait sur l'explication du correctif — quatrième occurrence
    # de ce motif dans ce dépôt.
    code = re.sub(r'""".*?"""', " ", handler, flags=re.S)
    for banned in ("user.bp_systolic =", "user.bp_diastolic ="):
        assert banned not in code, (
            f"{banned} réintroduit : un champ absent effacerait la valeur"
        )


def test_stored_blood_pressure_is_still_readable_elsewhere():
    """`REMOVE_NO_ASK` porte sur l'ACQUISITION, pas sur la donnée. Le rapport
    coach continue de la rendre — la retirer de là serait une soustraction que
    personne n'a décidée."""
    coach = (pathlib.Path(__file__).resolve().parent.parent
             / "app/services/coach_report.py").read_text(encoding="utf-8")
    assert "bp_systolic" in coach


def test_no_connected_health_permission_is_requested():
    """La décision dit explicitement : aucune permission connectée tant qu'un
    consommateur produit n'est pas démontré. Google Play soumet
    `READ_BLOOD_PRESSURE` à un contrôle renforcé, et AUREN n'a pas la
    justification."""
    root = pathlib.Path(__file__).resolve().parent.parent
    for pattern in ("READ_BLOOD_PRESSURE", "health_connect", "HealthKit"):
        hits = [p for p in (root / "app").rglob("*.py")
                if pattern.lower() in p.read_text(encoding="utf-8").lower()]
        assert not hits, f"{pattern} apparaît dans {hits}"


# ───────────── ce que la soustraction emmène avec elle (§5.3) ─────────────


def _uncommented(src: str) -> str:
    """Sans les commentaires Jinja — une garde qui lit sa propre prose ne
    garde rien, et ce dépôt s'y est fait prendre trois fois."""
    return re.sub(r"\{#.*?#\}", " ", src, flags=re.S)


def test_the_profile_opens_on_what_auren_knows(client):
    """L'état lisible précède l'édition. C'est ce qui remplace la
    soustraction : le Profil répond « qu'est-ce qu'AUREN sait de moi ? » avant
    de proposer de le modifier.

    `UI-CP1` — CETTE GARDE ENCODAIT L'ANCIENNE ONTOLOGIE, ET IL FAUT LE DIRE.

    Elle exigeait `body.count('class="pstate') >= 3` : **trois domaines**, à
    savoir Corps, Entraînement et Compte. C'était le comptage d'un MOYEN — une
    classe — et il gravait dans un test la structure même que BODY_LEDGER
    défait : un instrument répond à UNE question, et le compte n'y est plus au
    repos. Laisser cette garde aurait interdit la direction que l'opérateur a
    approuvée, sans protéger l'invariant qu'elle prétendait tenir.

    L'INVARIANT, lui, ne bouge pas : **la page répond avant de demander**. Il
    est désormais vérifié directement sur l'ordre du document, ce qui ne
    dépend d'aucune convention de classe et vaut sur les trois états de
    données — y compris le profil vide, où la réponse est « non pesé ».
    """
    body = client.get("/profile").text
    assert 'class="body-ledger"' in body, "aucun instrument corporel rendu"
    # ⚠ SCOPÉ À L'INSTRUMENT. La coque rend un `form` de déconnexion AVANT
    # `main` : mesuré ici même, la première écriture de cette garde comparait
    # la réponse primaire à ce formulaire-là et accusait le cockpit d'un
    # défaut appartenant au rail de navigation.
    instrument = body[body.index('class="body-ledger"'):]
    assert "bl-answer__readout" in instrument, "aucune réponse primaire rendue"
    assert instrument.index("bl-answer__readout") < instrument.index("<form"), (
        "un formulaire précède la lecture — la page demande avant de répondre"
    )


def test_every_acquisition_form_sits_behind_an_explicit_update(client):
    """Les quatre formulaires ne sont plus le contenu de la page : ils sont
    ouverts par un geste. Mesuré avant : 6,6 écrans, 641 mots, 39 contrôles."""
    src = _uncommented(TEMPLATE.read_text(encoding="utf-8"))
    # Le QUICK_LOG est délibérément hors disclosure : une donnée volatile qu'on
    # doit pouvoir corriger vite ne se note pas derrière un geste
    # supplémentaire. C'est la décision opérateur, pas un oubli.
    acquisition = src.count('<form method="post"') - src.count('class="quicklog"')
    # `Sb_UI_DISCLOSURE_01` — COMPTAGE PAR JETON, PLUS PAR CHAÎNE EXACTE.
    # Ce comptage cherchait `class="pstate__edit"` au caractère près. Adopter le
    # composant partagé a fait de l'attribut `class="disclosure pstate__edit"`,
    # et la garde est tombée — alors que l'invariant qu'elle protège, « chaque
    # formulaire est derrière un geste », n'avait pas bougé d'un pouce.
    #
    # C'est la faute que ce dépôt paie en boucle : épingler une ÉCRITURE au lieu
    # d'une PROPRIÉTÉ interdit le refactoring sans rien garder de plus.
    # ⚠ `UI-CP1` — LE COMPTAGE NE TENAIT PAS L'INVARIANT QU'IL ANNONÇAIT, et
    # c'est une PLANTATION DU DÉFAUT qui l'a montré, pas une relecture.
    #
    # L'invariant était `disclosures >= acquisition`. Il compare deux TOTAUX,
    # donc il ne dit rien sur l'imbrication : un tiroir SANS formulaire — le
    # tiroir « Compte », arrivé avec BODY_LEDGER — gonfle le membre de gauche
    # et paie pour un formulaire resté à découvert. Mesuré : en sortant le
    # formulaire de données de référence de son tiroir, le compte tombait de
    # 3 à 2 pour 2 formulaires, et la garde restait VERTE.
    #
    # La propriété réelle est l'IMBRICATION. On la vérifie en suivant la
    # profondeur des `details` : tout formulaire d'acquisition doit s'ouvrir
    # à une profondeur d'au moins un.
    profondeur = 0
    decouverts = []
    for m in re.finditer(r"<details\b|</details>|<form\b[^>]*>", src):
        jeton = m.group(0)
        if jeton == "<details":
            profondeur += 1
        elif jeton == "</details>":
            profondeur = max(profondeur - 1, 0)
        elif 'class="quicklog"' not in jeton and profondeur == 0:
            decouverts.append(src[m.start():m.start() + 80].replace("\n", " "))
    assert acquisition >= 2, f"seulement {acquisition} formulaires d'acquisition"
    assert not decouverts, (
        f"{len(decouverts)} formulaire(s) d'acquisition hors tiroir : {decouverts}"
    )


def test_no_acquisition_form_is_open_by_default(client):
    """Un `details` ouvert rendrait le regroupement décoratif.

    `UI-CP1` — la garde cherchait deux ÉCRITURES exactes autour du jeton
    `pstate__edit`. Ce jeton ayant disparu avec la refonte, elle serait
    devenue verte pour la mauvaise raison : elle n'aurait plus rien trouvé,
    donc plus rien gardé. C'est la quatorzième forme relevée dans ce dépôt de
    « garde qui ne garde rien ».

    Elle interdit désormais TOUT `details` ouvert sur la surface, quelle que
    soit la classe et quel que soit l'ordre des attributs — ce qui est à la
    fois plus large et exactement la règle du cockpit : l'édition n'apparaît
    qu'après une intention explicite.
    """
    body = client.get("/profile").text
    ouverts = re.findall(r"<details[^>]*\sopen[\s>]", body)
    assert not ouverts, f"{len(ouverts)} tiroir(s) ouvert(s) au repos : {ouverts}"


def test_nothing_was_removed_except_the_decided_field(client):
    """`§5.3` — la tranche ne retire QUE ce qui a été tranché. Les candidats
    du registre restent demandés tels quels."""
    body = client.get("/profile").text
    for kept in ('name="height_cm"', 'name="resting_hr"', 'name="email"',
                 'name="weight_kg"'):
        assert kept in body, f"{kept} a disparu sans décision"


# ───────── les cinq décisions du 2026-08-20 ─────────


def test_body_analytics_left_the_profile(client):
    """**1 — BODY ANALYTICS.** « Évolution corporelle » appartient à
    `PROGRESSION / BODY`.

    Mesuré avant retrait : **neuf cartes encadrées disant toutes « pas encore
    de données »**, chacune suivie de son paragraphe de programmes associés —
    environ deux des 4,2 écrans. Un cadre par module futur, pour zéro
    information.
    """
    body = client.get("/profile").text
    assert "Évolution corporelle" not in body
    assert "measurement-grid" not in body
    assert body.count("pas encore de données") <= 1, (
        f"{body.count('pas encore de données')} états vides — un seul par "
        "domaine, jamais un par module futur"
    )


def test_no_link_promises_a_destination_that_does_not_exist(client):
    """**1bis — pas de lien menteur.** `PROGRESSION / BODY` n'a pas de route.
    Y renvoyer serait promettre une surface inexistante."""
    body = client.get("/profile").text
    for absent in ('href="/progress/body"', 'href="/body/evolution"'):
        assert absent not in body, f"lien vers une destination inexistante : {absent}"


def test_progress_analytics_left_the_profile(client):
    """**5 — EMPTY ANALYTICS + question cible.** Le Profil ne répond pas à
    « comment est-ce que je progresse ? ».

    « Mes 30 derniers jours » rendait `0` comme une valeur mesurée — fatigue 0,
    régularité 0, série 0, tendance « en baisse » — alors qu'aucune observation
    ne les soutenait. Un zéro dérivé de rien n'est pas une mesure.
    """
    body = client.get("/profile").text
    assert "Mes 30 derniers jours" not in body
    for banned in ("kpi__value", "jours de série", "régularité"):
        assert banned not in body, f"analytique résiduelle sur le Profil : {banned}"


def test_training_configuration_left_level_one_but_stays_editable(client):
    """**2 — TRAINING CONFIGURATION.** `TRAIN1-D` / C2 — LE RÉSUMÉ QUITTE LE
    NIVEAU 1.

    `UX4_01` exigeait ici un résumé en lecture seule. Il rendait trois lignes
    dont les trois valaient `—` sur un compte neuf — trois des six tirets nus
    de la page. Et il répondait à « comment je veux m'entraîner », qui est la
    question de **Mon plan**, pas celle du Profil.

    L'éditeur RESTE : `weekly_planner` et `user_programs` consomment
    `sessions_per_week`, `focus_priorities` et `available_equipment`. Retirer
    la lecture sans garder l'écriture aurait rendu les entrées du
    planificateur inatteignables.

    `UX4_02` / TRAIN 2 A TENU LA PROMESSE. Ce test disait : « l'emplacement
    reste déclaré transitionnel — c'est `TRAIN2` qui lui donne son domicile ».
    C'est fait : l'éditeur est sur **Mon plan**, avec la déclaration qu'il
    produit. La garde suit le déménagement au lieu de le refuser — et elle
    vérifie toujours les DEUX moitiés, dont la seconde compte le plus : un
    éditeur retiré d'un écran sans réapparaître ailleurs rendrait les entrées
    du planificateur inatteignables.
    """
    body = client.get("/profile").text
    assert "Cadence souhaitée" not in body, (
        "la configuration est remontée au niveau 1"
    )
    assert "Modifier mes préférences" not in body, (
        "l'éditeur est resté sur le Profil"
    )
    assert "transitionnel" not in body.lower(), (
        "la mention transitionnelle promet un déménagement déjà survenu"
    )
    plan = client.get("/plan")
    assert plan.status_code == 200
    assert "Modifier mes préférences" in plan.text, (
        "l'éditeur a disparu du produit : soustraction seule (`§5.3`)"
    )


def test_the_preferences_editor_is_not_duplicated(client):
    """La décision interdit de dupliquer le formulaire d'édition. Elle vaut
    maintenant à l'échelle du PRODUIT, pas d'un gabarit : le compter dans le
    seul `profile.html` rendrait la garde verte pour la mauvaise raison — en
    lisant zéro éditeur là où il n'y en a plus."""
    src = _uncommented(TEMPLATE.read_text(encoding="utf-8"))
    assert src.count("url_for('profile_preferences_submit')") == 0
    hosts = [p.name for p in TEMPLATE.parent.rglob("*.html")
             if "profile_preferences_submit"
             in _uncommented(p.read_text(encoding="utf-8"))]
    assert hosts == ["plan.html"], f"éditeur présent dans : {hosts}"


def test_body_weight_has_a_quick_log(client):
    """**3 — BODY WEIGHT → `QUICK_LOG`.** Le poids se note là où il se lit,
    sans ouvrir le formulaire de morphométrie complet."""
    body = client.get("/profile").text
    assert 'class="quicklog"' in body
    assert 'id="quicklog_weight"' in body


def test_the_quick_log_uses_the_canonical_writer(client):
    """Un second écrivain sur `body_measurements` a déjà coûté une tranche
    (`Sb_MORPHO_PROFILE_RUNTIME_01` : deux écrivains, une table, deux contrats
    temporels). Le quick-log poste vers la MÊME route."""
    src = _uncommented(TEMPLATE.read_text(encoding="utf-8"))
    quicklog = src.split('class="quicklog"', 1)[0].rsplit("<form", 1)[1]
    assert "profile_measurements_submit" in quicklog


def test_no_connected_health_channel_is_implemented(client):
    """**3bis** — `CONNECTED_FUTURE` est une DIRECTION, pas une
    implémentation. Aucune intégration santé dans cette tranche."""
    body = client.get("/profile").text
    for banned in ("Health Connect", "Apple Health", "HealthKit", "Connecter"):
        assert banned not in body, f"canal connecté annoncé : {banned}"


def test_morphometry_is_labelled_as_a_fallback(client):
    """**4 — MORPHOMETRY.** Le grand formulaire est un mécanisme de repli
    hérité, pas l'architecture cible. L'assistant guidé n'est PAS construit."""
    body = client.get("/profile").text
    assert "saisie complète" in body, (
        "le formulaire hérité n'est pas signalé comme mécanisme de repli"
    )
    for wizard in ("étape 1", "wizard", 'data-step="'):
        assert wizard not in body, f"assistant guidé construit hors périmètre : {wizard}"


# ───────── audit de nécessité des cartes ─────────


def test_no_boxed_region_is_a_pure_grouping(client):
    """Le Profil doit se lire comme un petit nombre de sections cohérentes,
    pas comme un tableau de bord de conteneurs bordés.

    Mesuré : 18 régions encadrées après la première passe — j'avais réduit les
    contrôles ET ajouté des boîtes. Les états purs n'ont plus de cadre : le
    titre et l'espace expriment le groupe mieux qu'une bordure de plus.
    """
    body = client.get("/profile").text
    # ⚠ `body.count('class="card')` compte AUSSI `card__title` et
    # `card__actions` : la première écriture rendait 9 là où le navigateur en
    # mesure 4. Compter une sous-chaîne n'est pas compter un objet — le motif
    # que cette session a payé quatre fois sur ses propres instruments.
    boxed = len(re.findall(r'class="card[ "]', body))
    assert boxed <= 6, f"{boxed} régions encadrées — le cadre doit se justifier"


def test_every_state_section_is_flat(client):
    """Un état sans contrôle ne mérite pas de boîte.

    `UI-CP1` — la garde tolérait UNE carte d'état (`class="card pstate"`) et
    interdisait les suivantes. BODY_LEDGER n'en garde aucune : la structure
    est faite de bandes, de filets et de blanc, et « un cockpit ne doit pas
    devenir une grande carte contenant de petites cartes ».

    Le seuil descend donc de « au plus une » à « aucune ». Une garde qui se
    resserre n'est pas une garde qu'on affaiblit.
    """
    body = client.get("/profile").text
    encadrees = re.findall(r'class="card[ "]', body)
    assert not encadrees, (
        f"{len(encadrees)} région(s) encadrée(s) sur un instrument qui n'en "
        "prévoit aucune"
    )
