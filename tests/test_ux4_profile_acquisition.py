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
    de proposer de le modifier."""
    body = client.get("/profile").text
    assert "pstate" in body, "aucun bloc d'état lisible rendu"
    # Trois domaines, pas un bloc unique : Corps, Entraînement, Compte.
    #
    # ⚠ Le message d'échec passait par une f-string avec échappement et
    # réutilisation du guillemet extérieur : valide en 3.12+, SYNTAXE INVALIDE
    # sur le Python 3.11 de la CI. Le poste tourne en 3.14, donc les tests
    # passaient en local et la CI aurait cassé à la collecte.
    domains = body.count('class="pstate')
    assert domains >= 3, f"seulement {domains} domaine(s) d'état lisible"


def test_every_acquisition_form_sits_behind_an_explicit_update(client):
    """Les quatre formulaires ne sont plus le contenu de la page : ils sont
    ouverts par un geste. Mesuré avant : 6,6 écrans, 641 mots, 39 contrôles."""
    src = _uncommented(TEMPLATE.read_text(encoding="utf-8"))
    # Le QUICK_LOG est délibérément hors disclosure : une donnée volatile qu'on
    # doit pouvoir corriger vite ne se note pas derrière un geste
    # supplémentaire. C'est la décision opérateur, pas un oubli.
    acquisition = src.count('<form method="post"') - src.count('class="quicklog"')
    disclosures = src.count('class="pstate__edit"')
    # `UX4_02` / TRAIN 2 — le seuil passe de 3 à 2 : l'éditeur de préférences a
    # quitté le Profil pour **Mon plan**. Ce n'est PAS un assouplissement de la
    # règle — la règle est l'invariant `disclosures >= acquisition` juste en
    # dessous, inchangé, et il vaut aussi sur `/plan` (garde jumelle dans
    # `test_train2_mon_plan`). Le seuil, lui, reste un cliquet : il interdit
    # qu'un formulaire disparaisse en silence du Profil.
    assert acquisition >= 2, f"seulement {acquisition} formulaires d'acquisition"
    assert disclosures >= acquisition, (
        f"{acquisition} formulaires pour {disclosures} déclencheurs — un "
        "formulaire est resté à découvert"
    )


def test_no_acquisition_form_is_open_by_default(client):
    """Un `<details open>` rendrait le regroupement décoratif."""
    body = client.get("/profile").text
    assert "pstate__edit\" open" not in body
    assert 'open class="pstate__edit"' not in body


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
    """Un état sans contrôle ne mérite pas de boîte."""
    body = client.get("/profile").text
    assert "pstate--flat" in body
    assert 'class="card pstate' not in body.replace('class="card pstate"', "", 1), (
        "plus d'un état lisible porte encore un cadre"
    )
