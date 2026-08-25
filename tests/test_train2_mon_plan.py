"""`UX4_02` / TRAIN 2 — **Mon plan**.

CE QUE CES GARDES FERMENT
--------------------------
`OPERATOR_DECISION` C8 nomme trois destinations — Mon plan, Mes programmes,
Explorer — et pose une contrainte de fond : **aucun moteur de recommandation
opaque, contexte de plan explicite uniquement**.

Trois objets vivaient séparés et ne pouvaient pas se lire l'un sans l'autre :
la déclaration d'entraînement (sur le Profil, à un emplacement que le gabarit
déclarait lui-même transitoire), le plan qu'elle produit et l'explication de ce
plan (tous deux sur « Mes programmes », qui répond à une autre question).

Les gardes portent sur les quatre points où cette tranche peut se défaire :

  1. LE FORMULAIRE SE DUPLIQUE — il n'a jamais existé qu'à un endroit, et
     deux éditeurs de la même préférence divergeraient en silence.
  2. UN CONTRAT DE SOUMISSION BOUGE — la route et les noms de champs sont des
     contrats ; les renommer casserait des signets et des tests sans que rien
     ne le signale au rendu.
  3. UN PLAN APPARAÎT SANS DÉCLARATION — ce serait le moteur opaque que C8
     interdit.
  4. LE PLAN RETOURNE SUR « MES PROGRAMMES » — la surface répondrait de
     nouveau à deux questions.
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "app/templates"
PLAN_TPL = TEMPLATES / "user_programs/plan.html"
LIST_TPL = TEMPLATES / "user_programs/list.html"
PROFILE_TPL = TEMPLATES / "profile.html"
BASE_TPL = TEMPLATES / "base.html"

PLAN_URL = "/plan"
PREFS_FORM = "profile_preferences_submit"
# Route de SOUMISSION — contrat inchangé par le déménagement.
PREFS_POST = "/profile/preferences"


def _uncommented(src: str) -> str:
    return re.sub(r"\{#.*?#\}", " ", src, flags=re.S)


def _submit_form(html: str) -> str:
    """Le `<form>` qui poste vers `/profile/preferences`, rendu."""
    forms = re.findall(r"<form\b[\s\S]*?</form>", html)
    hosts = [f for f in forms if PREFS_POST in f]
    assert len(hosts) == 1, f"{len(hosts)} formulaire(s) de préférences rendus"
    return hosts[0]


def _active_bottom_labels(html: str) -> list[str]:
    """Onglets de la barre basse marqués actifs, en exigeant l'ACCORD des deux
    marqueurs — la classe `is-active` (ce que l'œil voit) et `aria-current`
    (ce que la synthèse vocale annonce).

    Le gabarit les pose par DEUX conditions Jinja distinctes sur la même ligne.
    Elles peuvent donc diverger, et une garde qui n'en lit qu'une reste verte
    pendant que l'autre se trompe d'onglet : c'est arrivé en plantant le défaut
    sur cette tranche même.

    Extracteur repris de `test_app_shell_navigation` : chaque item est isolé
    AVANT de chercher le libellé. Une expression qui relie le marqueur au
    libellé par une distance bornée échoue en silence — l'icône SVG intercalée
    fait à elle seule plus de 300 caractères."""
    nav = html.split('class="app-bottom-nav"', 1)[1]
    out = []
    for item in re.findall(r'<a class="app-bottom-nav__item[^>]*>.*?</a>', nav,
                           re.DOTALL):
        marks = ("is-active" in item, 'aria-current="page"' in item)
        m = re.search(r'__label">([^<]+)<', item)
        label = m.group(1) if m else "?"
        assert marks[0] == marks[1], (
            f"onglet « {label} » : classe active={marks[0]}, "
            f"aria-current={marks[1]} — les deux marqueurs divergent")
        if marks[0]:
            out.append(label)
    return out


def _declare(db, uid, **kw):
    from app.services.training_preferences import save_training_preferences

    save_training_preferences(db, uid, **kw)


# ═════════ LA SURFACE EXISTE ET RÉUNIT LES TROIS OBJETS ═════════


def test_mon_plan_is_served(client):
    r = client.get(PLAN_URL)
    assert r.status_code == 200
    assert "Mon plan" in r.text


def test_mon_plan_carries_the_declaration_the_plan_and_the_editor(client):
    """Les trois objets sur une seule surface — c'est le sujet de la tranche.
    Le plan lui-même n'apparaît qu'avec une déclaration ; on vérifie ici les
    deux qui ne dépendent d'aucune donnée."""
    body = _uncommented(PLAN_TPL.read_text(encoding="utf-8"))
    assert "Ce que tu as déclaré" in body
    assert PREFS_FORM in body
    assert "weekly_plan_proposal" in body
    assert "plan_explanation" in body


def test_the_preferences_editor_exists_exactly_once_in_the_whole_product():
    """Deux éditeurs de la même préférence divergeraient en silence. Le
    formulaire n'a jamais existé qu'à UN endroit — il a déménagé, pas
    proliféré."""
    hosts = [p.name for p in TEMPLATES.rglob("*.html")
             if PREFS_FORM in _uncommented(p.read_text(encoding="utf-8"))]
    assert hosts == ["plan.html"], f"éditeur présent dans : {hosts}"


# ═════════ LES CONTRATS DE SOUMISSION NE BOUGENT PAS ═════════


def test_the_submit_route_is_unchanged():
    """La route de soumission est un CONTRAT : des signets, des tests et des
    formulaires historiques en dépendent. Le déménagement d'un formulaire ne
    justifie pas de la renommer."""
    from app.main import app

    paths = {getattr(r, "path", "") for r in app.routes}
    assert PREFS_POST in paths


def test_the_field_names_are_unchanged(client):
    """Même raison : `save_training_preferences` distingue « non déclaré » de
    « déclaré vide » grâce au marqueur `equipment_declared`. Renommer un champ
    effacerait cette distinction sans erreur visible.

    La garde lit le RENDU, pas le gabarit : `sessions_per_week` et `equipment`
    n'apparaissent nulle part en clair dans `plan.html` — leurs `<input>` sont
    produits par les macros `choice_row` / `select_shell`. Une garde posée sur
    la source aurait accusé un renommage inexistant, et surtout n'aurait pas vu
    un renommage réel survenu dans la macro."""
    form = _submit_form(client.get(PLAN_URL).text)
    for field in ("sessions_per_week", "focus_1", "focus_2", "focus_3",
                  "equipment", "equipment_declared"):
        assert f'name="{field}"' in form, f"champ renommé : {field}"


def test_the_editor_still_sits_behind_an_explicit_gesture(client):
    """La propriété voyage AVEC le formulaire. Sur le Profil, `UX4_01` avait
    mesuré 6,6 écrans et 641 mots parce que les formulaires ÉTAIENT la page ;
    la réponse fut de les mettre derrière un geste. Réinstaller ce formulaire
    déplié sur Mon plan rejouerait le même défaut sur un écran neuf — et
    noierait le plan, qui est le sujet de la surface."""
    body = PLAN_TPL.read_text(encoding="utf-8")
    assert 'class="pstate__edit"' in body, "l'éditeur n'est plus derrière un geste"
    assert "pstate__edit\" open" not in body
    assert 'open class="pstate__edit"' not in body


def test_every_field_offers_its_options(client):
    """LE DÉFAUT QUE CETTE TRANCHE A RÉELLEMENT PRODUIT. Les trois
    vocabulaires (`sessions_range`, `focus_vocab`, `equipment_vocab`) sont du
    CONTEXTE DE ROUTE : déplacer le gabarit ne les déplace pas. Oubliés, Jinja
    itère sur `Undefined` **sans lever** — le formulaire rend ses légendes et
    zéro option.

    La garde sur les noms de champs ne suffit pas : les trois menus `focus_N`
    sont produits par une boucle sur le littéral `[1, 2, 3]`, donc leurs `name`
    survivent intacts à un vocabulaire absent. Ce sont les OPTIONS qui
    disparaissent. On compte donc les choix offerts, pas les champs présents."""
    form = _submit_form(client.get(PLAN_URL).text)
    cadence = len(re.findall(r'name="sessions_per_week"', form))
    equipment = len(re.findall(r'name="equipment"', form))
    focus = len(re.findall(r'<option value="(?!")[^"]+"', form))
    assert cadence >= 2, f"grille de cadence : {cadence} option(s)"
    assert equipment >= 2, f"familles de matériel : {equipment} option(s)"
    assert focus >= 3, f"priorités : {focus} option(s) sur 3 menus"


def test_saving_preferences_lands_back_on_the_plan(client):
    """La redirection suit le formulaire — sinon on enregistre sur Mon plan et
    on atterrit sur le Profil, qui ne montre plus rien de ces réglages."""
    r = client.post(PREFS_POST,
                    data={"sessions_per_week": "3", "equipment_declared": "1"},
                    follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"].startswith(PLAN_URL)


# ═════════ AUCUN MOTEUR OPAQUE (C8) ═════════


def test_no_plan_is_proposed_without_a_declaration(client):
    """LE CŒUR DE C8. Sans déclaration, il n'y a pas de plan — et c'est DIT,
    pas comblé par une proposition devinée."""
    r = client.get(PLAN_URL)
    assert "Programme proposé" not in r.text
    assert "Aucun plan proposé" in r.text


def test_the_plan_appears_once_the_declaration_exists(client):
    """Le pendant : une garde qui ne teste que l'absence laisserait passer une
    surface qui ne propose jamais rien."""
    from app.database import SessionLocal
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    with SessionLocal() as db:
        _declare(db, uid, sessions_per_week=4,
                 focus_priorities=["back_width"], available_equipment=None)

    r = client.get(PLAN_URL)
    assert "4 / semaine" in r.text
    assert "Dos largeur" in r.text


def test_the_plan_is_built_from_declarations_only():
    """`build_weekly_plan_for_user` ne lit que les préférences déclarées. La
    garde vise le PRODUCTEUR : une surface honnête devant un moteur qui devine
    resterait un moteur qui devine."""
    src = (ROOT / "app/routers/user_programs.py").read_text(encoding="utf-8")
    block = src.split("def _weekly_plan_proposal", 1)[1].split("\ndef ", 1)[0]
    assert "get_training_preferences" in block
    assert "if preferences is None or not preferences.sessions_per_week" in block
    assert "return None" in block


def test_the_explanation_names_its_sources():
    """« Pourquoi ce plan ? » cite une source par élément. C'est ce qui
    distingue un contexte explicite d'une recommandation opaque."""
    body = _uncommented(PLAN_TPL.read_text(encoding="utf-8"))
    assert "item.source_label" in body


# ═════════ LES SURFACES VOISINES ONT CÉDÉ CE QUI N'ÉTAIT PAS À ELLES ═════════


def test_the_plan_left_mes_programmes():
    """« Mes programmes » répond à « qu'est-ce que j'ai créé ». La proposition
    hebdomadaire répond à « comment je veux m'entraîner »."""
    body = _uncommented(LIST_TPL.read_text(encoding="utf-8"))
    assert "weekly_plan_proposal" not in body
    assert "plan_explanation" not in body


def test_mes_programmes_still_lists_the_programs(client):
    """`CLAUDE.md §5.3` — la surface n'est pas vidée, elle est recentrée."""
    r = client.get("/programs")
    assert r.status_code == 200
    assert "Créer un programme" in r.text


def test_the_profile_no_longer_hosts_training_configuration():
    body = _uncommented(PROFILE_TPL.read_text(encoding="utf-8"))
    assert PREFS_FORM not in body
    assert "Cadence souhaitée" not in body


def test_the_transitional_marker_is_gone_because_it_was_honoured():
    """Le gabarit annonçait : « `UX4_02` doit accueillir cet éditeur ; tant que
    ce n'est pas fait, cet emplacement est TRANSITIONNEL ». C'est fait — la
    mention doit partir avec le formulaire, sinon elle promet un déménagement
    déjà survenu."""
    rendered = _uncommented(PROFILE_TPL.read_text(encoding="utf-8"))
    assert "Emplacement transitionnel" not in rendered


# ═════════ NAVIGATION ═════════


def test_the_programmes_tab_groups_its_three_destinations():
    body = _uncommented(BASE_TPL.read_text(encoding="utf-8"))
    m = re.search(r"set is_programs = ([^%]+)%\}", body)
    assert m, "la définition de `is_programs` a disparu"
    grouping = m.group(1)
    assert "/library" in grouping
    assert "/programs" in grouping
    assert "is_plan" in grouping


def test_mon_plan_is_reachable_from_the_shell(client):
    r = client.get("/")
    assert "Mon plan" in r.text
    assert PLAN_URL in r.text


def test_mon_plan_lights_the_programmes_tab(client):
    """Un onglet exactement, et le bon : une surface qui n'allume rien laisse
    l'utilisateur sans repère, une surface qui en allume deux ment sur sa
    place dans la hiérarchie."""
    assert _active_bottom_labels(client.get(PLAN_URL).text) == ["Programmes"]


def test_the_neighbours_still_light_their_own_tab(client):
    """Le pendant : `is_programs` a été élargi pour accueillir `/plan`. Un
    élargissement trop large allumerait Programmes depuis le Profil."""
    assert _active_bottom_labels(client.get("/programs").text) == ["Programmes"]
    assert _active_bottom_labels(client.get("/profile").text) == ["Profil"]
