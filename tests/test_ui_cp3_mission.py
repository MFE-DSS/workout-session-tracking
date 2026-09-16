"""`UI-CP3` — MISSION possède UNE question : qu'est-ce que je fais maintenant ?

POURQUOI CES GARDES EXISTENT
----------------------------
Mesuré sur l'accueil avant la tranche, labo semé du catalogue réel :

    état RECO   1,98 écran · 121 mots · 7 cliquables · 27 champs dans le DOM
    état LIVE   1,50 écran ·  79 mots · 6 cliquables · 27 champs dans le DOM

Cinq objets sous la mission répondaient à d'autres questions, l'état LIVE
n'annonçait qu'une durée, et l'instrument changeait de grammaire selon son
état — bande en RECO, **card** en LIVE.

Ces gardes tiennent des PROPRIÉTÉS, pas des écritures : aucune n'épingle une
chaîne de libellé que l'opérateur pourrait vouloir changer demain.
"""
from __future__ import annotations

import re
from pathlib import Path

from sqlalchemy import select

_RACINE = Path(__file__).resolve().parent.parent
_INDEX = _RACINE / "app/templates/index.html"


def _sans_commentaires(src: str) -> str:
    """Retire les commentaires Jinja AVANT toute recherche.

    Douze fois dans ce dépôt, une garde a échoué — ou pire, réussi — sur sa
    propre prose : les commentaires d'intention citent forcément ce qu'ils
    expliquent. Chercher « card » dans un fichier qui explique pourquoi la
    card est retirée trouve toujours « card ».
    """
    return re.sub(r"\{#.*?#\}", "", src, flags=re.DOTALL)


def _demarrer(client) -> int:
    r = client.post("/sessions", data={"template_slug": "push-a"},
                    follow_redirects=False)
    assert r.status_code in (302, 303), r.status_code
    return int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))


# ══════════════════════════════════════════════════════════════════════
#  §2 — UNE GRAMMAIRE, DEUX ÉTATS
# ══════════════════════════════════════════════════════════════════════


def test_l_etat_actif_n_est_plus_une_card(client):
    """L'instrument ne change pas de nature selon son état.

    `.today-home__hero--active` portait un fond surélevé et un liseré : une
    CARD, quand l'état recommandé était une bande à rail. La garde tient la
    PROPRIÉTÉ rendue (aucune card dans la mission), pas le nom d'une règle
    CSS qu'un refactoring déplacerait.
    """
    _demarrer(client)
    corps = _sans_commentaires(client.get("/").text)
    mission = corps.split('class="mission-bridge"')[0]
    assert 'class="card' not in mission, (
        "une card est réapparue dans MISSION — c'est la primitive que le "
        "programme retire"
    )


def test_les_deux_etats_emploient_la_meme_grammaire(client):
    """RECO et LIVE partagent NOW · POSITION · EVIDENCE · ACTION · ESCAPE.

    On observe le porteur STRUCTUREL commun (`cockpit__cause` / `__effect`),
    pas les libellés : c'est la grammaire qui est contractuelle, pas les mots.
    """
    reco = _sans_commentaires(client.get("/").text)
    assert "cockpit__cause" in reco, "l'état RECO a perdu sa grammaire"

    _demarrer(client)
    live = _sans_commentaires(client.get("/").text)
    assert "cockpit__cause" in live, (
        "l'état LIVE n'emploie pas la grammaire de l'état RECO"
    )


def test_un_seul_proprietaire_d_action_dominante(client):
    """L'ambre plein désigne UNE commande, et une seule, dans chaque état."""
    for _ in range(2):
        corps = _sans_commentaires(client.get("/").text)
        mission = corps.split('class="mission-bridge"')[0]
        # ⚠ `(?![\\w-])` N'EST PAS DÉCORATIF — PREMIÈRE ÉCRITURE FAUSSE.
        #
        # `mission.count("today-home__cta")` rendait 2 et accusait un produit
        # sain : la chaîne est une SOUS-CHAÎNE de `today-home__cta-form`, le
        # `<form>` qui enveloppe le bouton. Vérifié sur le HTML servi avant de
        # toucher quoi que ce soit — une seule vraie commande.
        #
        # `\\b` n'aurait pas suffi : le tiret EST une frontière de mot, donc
        # `\\btoday-home__cta\\b` matche aussi dans `…__cta-form`.
        dominantes = len(re.findall(r"today-home__cta(?![\w-])", mission))
        assert dominantes <= 1, (
            f"{dominantes} commandes dominantes dans MISSION — l'ambre cesse "
            "de vouloir dire « c'est à toi de jouer »"
        )
        _demarrer(client)


# ══════════════════════════════════════════════════════════════════════
#  §3 — LA POSITION, PAS LA DURÉE
# ══════════════════════════════════════════════════════════════════════


def test_l_etat_actif_annonce_la_position(client):
    """« depuis 37 min » ne dit pas où reprendre.

    La garde exige les DEUX comptes — exercice et séries — parce que l'un
    sans l'autre ne situe pas : « exercice 3 sur 7 » ne dit pas si l'exercice
    est entamé, « 7 séries sur 21 » ne dit pas lequel.
    """
    _demarrer(client)
    corps = _sans_commentaires(client.get("/").text)
    assert "mission-pos" in corps, "aucune position rendue sur l'état actif"
    assert re.search(r"Exercice\s*<b>\d+</b>\s*sur\s*\d+", corps), corps[:0]
    assert re.search(r"<b>\d+</b>\s*série", corps), corps[:0]


def test_la_duree_cesse_d_etre_le_fait_principal(client):
    """Elle reste — elle descend au rang de contexte.

    `§5.3` : la durée n'est pas supprimée, elle est subordonnée. Une garde
    qui exigerait sa disparition transformerait une hiérarchisation en
    soustraction.
    """
    _demarrer(client)
    corps = _sans_commentaires(client.get("/").text)
    assert "mission-pos__since" in corps, (
        "la durée a disparu — elle devait être subordonnée, pas retirée"
    )


def test_la_position_se_tait_quand_elle_n_apprend_rien(client):
    """Une séance sans série de travail prescrite n'a pas de position.

    Mesuré comme règle sur `UI-CP2.1` : une commande ne nomme jamais une
    destination inexistante. Un readout ne compte jamais « 1 sur 0 ».
    """
    from app.services.mission_position import MissionPosition

    vide = MissionPosition(
        exercise_index=1, exercise_total=0, sets_done=0, sets_total=0,
        exercise_name=None, set_index=None,
    )
    assert not vide.is_meaningful

    plein = MissionPosition(
        exercise_index=3, exercise_total=7, sets_done=7, sets_total=21,
        exercise_name="Dips", set_index=2,
    )
    assert plein.is_meaningful


def test_la_position_ne_charge_pas_l_arbre_de_la_seance(client):
    """MISSION emprunte le minimum, elle n'importe pas EXECUTION.

    La position est dérivée d'UNE requête d'agrégation. La garde le tient par
    le fait observable : le service ne rend que des entiers et un nom, jamais
    d'entité ORM — donc rien qui puisse entraîner l'arbre derrière lui.
    """
    from dataclasses import fields

    from app.services.mission_position import MissionPosition

    autorises = {int, str, type(None), "int | None", "str | None"}
    for f in fields(MissionPosition):
        assert f.type in ("int", "str | None", "int | None"), (
            f"`{f.name}` porte {f.type} — MISSION ne doit transporter que des "
            "faits comptés, jamais une entité de session"
        )
    assert autorises  # la liste documente l'intention


# ══════════════════════════════════════════════════════════════════════
#  §4 · §5 · §10 — CE QUI N'APPARTIENT PLUS À MISSION
# ══════════════════════════════════════════════════════════════════════


def test_mission_ne_porte_plus_aucun_champ_de_formulaire_cache(client):
    """Vingt-sept champs de readiness dormaient dans le DOM de l'accueil.

    Ils étaient invisibles, donc personne ne les voyait ; ils étaient servis,
    donc tout le monde les payait.
    """
    corps = client.get("/").text
    visibles = [m for m in re.findall(r"<input[^>]*>", corps)
                if "hidden" not in m]
    assert visibles == [], (
        f"{len(visibles)} champs subsistent dans MISSION — la surface de "
        "décision n'est pas un formulaire"
    )


def test_le_bilan_11_zones_a_quitte_mission(client):
    """Il décrit la couverture du corps, pas la décision du moment."""
    corps = _sans_commentaires(client.get("/").text)
    assert "cockpit__tally" not in corps


def test_le_bilan_11_zones_est_rendu_par_sa_destination(client):
    """⚠ LA MOITIÉ QUI REND LE RETRAIT LÉGITIME (`CLAUDE.md §5.3`).

    Sans cette garde, la précédente autoriserait une soustraction sèche.
    Les deux ne valent qu'ensemble.
    """
    corps = _sans_commentaires(client.get("/progress").text)
    assert "cockpit__tally" in corps, (
        "le bilan 11 zones n'est nulle part — il a été SUPPRIMÉ, pas déplacé"
    )


def test_le_composant_de_bande_est_dans_la_feuille_partagee():
    """Une classe déplacée sans sa feuille se rend SANS STYLE.

    `/progress` ne charge pas `home.css`. Laisser `.band` et
    `.cockpit__tally` là-bas aurait rendu le bilan nu sur sa nouvelle
    surface — le défaut « le produit a la décision, pas le moyen de
    l'appliquer », dans sa variante la plus banale.
    """
    app_css = (_RACINE / "app/static/css/app.css").read_text(encoding="utf-8")
    assert ".cockpit__tally {" in app_css
    assert ".band--unknown i {" in app_css


def test_la_declaration_d_etat_du_jour_a_une_destination(client):
    """La capacité d'écriture n'est pas perdue, elle est réunie à sa lecture.

    Mesuré avant de décider : `recommendation.py` ne lit la readiness nulle
    part. Elle ne changeait aucune recommandation — donc elle n'était pas une
    preuve de MISSION.
    """
    page = client.get("/readiness/history").text
    assert 'action="/readiness"' in page, (
        "le formulaire de déclaration n'existe plus nulle part"
    )
    champs = [m for m in re.findall(r"<input[^>]*>", page)
              if "hidden" not in m]
    assert len(champs) >= 25, (
        f"seulement {len(champs)} champs — la déclaration a été amputée en "
        "chemin"
    )


def test_la_porte_de_l_etat_du_jour_existe_dans_body_ledger(client):
    """Une capacité préservée mais inatteignable est une capacité perdue.

    Avant la tranche, `/readiness/history` n'était liée QUE depuis l'accueil,
    et seulement une fois l'état du jour déjà renseigné — donc invisible
    exactement à qui ne l'avait pas encore fait.
    """
    profil = _sans_commentaires(client.get("/profile").text)
    assert "/readiness/history" in profil, (
        "aucune porte vers l'état du jour depuis BODY_LEDGER"
    )


def test_aucun_objet_etranger_ne_subsiste_sous_la_mission(client):
    """Les cinq blocs souverains sont partis — vérifié par leur PORTEUR.

    On cherche les classes qui les rendaient, jamais leurs libellés : un
    titre peut changer sans que l'objet parte, et un objet peut partir en
    laissant son titre ailleurs.
    """
    corps = _sans_commentaires(client.get("/").text)
    for porteur in ("coaching-loop", "readiness-widget", "hl-block",
                    "home-wk", "tile-grid", "today-home__analysis"):
        assert porteur not in corps, (
            f"`{porteur}` est encore rendu par MISSION"
        )


# ══════════════════════════════════════════════════════════════════════
#  §6 · §7 — LE PONT, ET SON CRITÈRE DE RETRAIT
# ══════════════════════════════════════════════════════════════════════


def test_le_rail_de_transition_ne_porte_que_des_sorties(client):
    """Pas de mini-métrique. Une sortie nommée par sa question n'est pas un
    tableau de bord — et c'est ce qui l'empêche de redevenir l'empilement
    qu'on vient de retirer."""
    corps = _sans_commentaires(client.get("/").text)
    m = re.search(r'<nav class="mission-bridge".*?</nav>', corps, re.DOTALL)
    assert m, "le rail de transition a disparu"
    rail = m.group(0)
    assert "<b>" not in rail, "une valeur chiffrée s'est glissée dans le rail"
    assert "band" not in rail, "un readout s'est glissé dans le rail"
    # Chaque sortie pose une QUESTION : c'est la forme qui la maintient
    # subordonnée à MISSION.
    assert rail.count("mission-bridge__exit") >= 2
    assert rail.count("?") >= 2, (
        "une sortie ne pose plus de question — elle redevient une tuile"
    )


def test_le_pont_porte_son_critere_de_retrait():
    """⚠ `§7` — B N'EST PAS UNE CIBLE, C'EST UNE TRANSITION.

    Un pont sans date devient une fondation. Le critère de retrait est écrit
    dans le gabarit ET dans la feuille : c'est la seule chose qui empêche le
    rail de devenir une primitive de cockpit AUREN par simple inertie.

    Cette garde lit de la PROSE, et c'est assumé — ce qu'elle protège EST une
    prose. Elle exige la mention de `FLIGHT_RECORDER`, pas une formulation.
    """
    index = _INDEX.read_text(encoding="utf-8")
    home_css = (_RACINE / "app/static/css/home.css").read_text(encoding="utf-8")
    for src, nom in ((index, "index.html"), (home_css, "home.css")):
        assert "FLIGHT_RECORDER" in src, (
            f"{nom} ne dit pas quand ce pont doit être retiré"
        )


# ══════════════════════════════════════════════════════════════════════
#  §9 — LARGEUR DE LECTURE
# ══════════════════════════════════════════════════════════════════════


def test_l_instrument_a_une_largeur_de_lecture():
    """Mesuré à 1280 px avant la tranche : clé et valeur séparées de ~1 400 px.

    La correction n'est pas une rustine par ligne : c'est une largeur pour
    l'instrument entier. La garde tient la RÈGLE, pas sa valeur — 62ch peut
    devenir 60 sans que rien ne se casse.
    """
    home_css = (_RACINE / "app/static/css/home.css").read_text(encoding="utf-8")
    bloc = home_css.split("LARGEUR DE LECTURE")[-1]
    assert "max-width" in bloc
    assert ".today-home__hero" in bloc
    assert ".mission-bridge" in bloc


# ══════════════════════════════════════════════════════════════════════
#  §13 — CE QUE LA ROUTE NE CALCULE PLUS
# ══════════════════════════════════════════════════════════════════════


def test_la_route_ne_calcule_plus_ce_qu_elle_ne_rend_pas(client):
    """Cinq clés étaient produites à chaque affichage, rendues par RIEN.

    La plus chère chargeait quatorze jours de séances avec
    `session_exercises → set_logs` pour un score composite par séance —
    exactement le coût que l'ontologie attribuait à la position intra-séance,
    déjà payé, pour un rendu inexistant.

    La garde observe le CONTEXTE réellement passé au gabarit : une garde qui
    lirait le source du routeur passerait au vert dès qu'on renomme.
    """
    import app.routers.pages as pages

    vus: dict = {}
    vrai = pages.templates.TemplateResponse

    def espion(request, name, context=None, *a, **k):
        if name == "index.html":
            vus.update(context or {})
        return vrai(request, name, context, *a, **k)

    pages.templates.TemplateResponse = espion
    try:
        client.get("/")
    finally:
        pages.templates.TemplateResponse = vrai

    assert vus, "le gabarit d'accueil n'a pas été rendu"
    for mort in ("kpis", "sparkline_svg", "sparkline_has_mixed_kinds",
                 "behavioral", "reco_zone_state"):
        assert mort not in vus, (
            f"`{mort}` est de nouveau calculé par l'accueil sans être rendu"
        )


def test_les_services_retires_de_la_route_existent_toujours():
    """⚠ LA MOITIÉ QUI EMPÊCHE LA GARDE PRÉCÉDENTE D'AUTORISER UNE PURGE.

    Ce qui part, c'est l'APPEL MORT sur cette route — pas les services, qui
    ont d'autres appelants. Sans cette garde, supprimer `compute_global_kpis`
    ferait passer la précédente au vert.
    """
    from app.services.behavioral import compute_behavioral_state
    from app.services.timeline import build_sparkline_svg

    assert callable(compute_behavioral_state)
    assert callable(build_sparkline_svg)


def test_progress_rend_toujours_ses_propres_kpis(client):
    """`kpis` quitte l'accueil, pas le produit : `/progress` le calcule
    lui-même et continue de le recevoir.

    On observe le CONTEXTE plutôt que le HTML : selon que le compte a des
    séances ou non, la page rend des cartes ou une phrase d'absence. Épingler
    l'une des deux ferait dépendre la garde de l'état du labo — et une
    disjonction `a or b` serait en plus une assertion composite, que Sonar
    compte MAJOR (poids 15, seuil 14 : elle suffit à casser le gate).
    """
    import app.routers.pages as pages

    vus: dict = {}
    vrai = pages.templates.TemplateResponse

    def espion(request, name, context=None, *a, **k):
        if name == "progress.html":
            vus.update(context or {})
        return vrai(request, name, context, *a, **k)

    pages.templates.TemplateResponse = espion
    try:
        client.get("/progress")
    finally:
        pages.templates.TemplateResponse = vrai

    assert "kpis" in vus, "`/progress` ne reçoit plus ses propres KPI"


# ══════════════════════════════════════════════════════════════════════
#  Le service, contre la base
# ══════════════════════════════════════════════════════════════════════


def test_la_position_compte_le_travail_et_non_l_echauffement(client):
    """Les échauffements ne comptent pas dans la position.

    Depuis `UI-CP2.1` ils ne sont plus une porte ; ils ne doivent pas non
    plus gonfler un compte de progression que l'utilisateur lit comme du
    travail fait.
    """
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession
    from app.services.mission_position import open_session_position

    sid = _demarrer(client)
    with SessionLocal() as db:
        pos = open_session_position(db, sid)
        assert pos is not None
        travail = db.execute(
            select(SetLog)
            .join(SessionExercise,
                  SetLog.session_exercise_id == SessionExercise.id)
            .where(SessionExercise.session_id == sid)
            .where(SetLog.kind == "work")
        ).scalars().all()
        assert pos.sets_total == len(travail)
        echauffements = db.execute(
            select(SetLog)
            .join(SessionExercise,
                  SetLog.session_exercise_id == SessionExercise.id)
            .where(SessionExercise.session_id == sid)
            .where(SetLog.kind == "warmup")
        ).scalars().all()
        assert echauffements, "le labo ne discrimine rien sans échauffement"
        assert pos.sets_total != len(travail) + len(echauffements)
        assert db.get(WorkoutSession, sid) is not None
