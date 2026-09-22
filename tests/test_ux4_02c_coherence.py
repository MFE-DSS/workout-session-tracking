"""`UX4_02C` — les deux corrections de cohérence décidées avant l'étude.

`OPERATOR_DECISION` — deux points, et rien d'autre. Aucune refonte, aucune
fonctionnalité : l'étude qui suit doit porter sur le produit tel qu'il est, pas
sur un produit qu'on aurait retouché en même temps qu'on l'observe.

**Q5** — « Pourquoi ce plan ? » est du contenu informationnel de niveau 2. Son
traitement en carte bordée autonome est retiré ; il devient une divulgation
progressive **dans le flux**. Le CONTENU ne change pas.

**NAMING** — le domaine s'appelle **Programmes**. Ses trois enfants s'appellent
**Mon plan**, **Mes programmes**, **Explorer**. Pas « Explore » : l'interface
est en français.

CE QUE CES GARDES FERMENT
--------------------------
  1. LA CARTE REVIENT — un `class="card"` autour de l'explication suffit.
  2. LE REPLI DEVIENT UNE SUPPRESSION — le titre doit rester visible ; un
     contenu replié dont on ne voit plus le nom est un contenu retiré.
  3. LE CONTENU A ÉTÉ REFONDU EN PASSANT — l'ordre a été explicite : aucune
     refonte. Les mêmes éléments, les mêmes sources, le même avis final.
  4. UN NOM ANGLAIS ENTRE DANS L'INTERFACE FRANÇAISE.
  5. L'ENFANT ET LE DOMAINE SE CONFONDENT DE NOUVEAU.
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLAN_TPL = ROOT / "app/templates/user_programs/plan.html"
BASE_TPL = ROOT / "app/templates/base.html"
LIB_TPL = ROOT / "app/templates/library.html"

PLAN_URL = "/plan"
LIBRARY_URL = "/library"
WHY = "Pourquoi ce plan ?"


def _uncommented(src: str) -> str:
    return re.sub(r"\{#.*?#\}", " ", src, flags=re.S)


def _declare_and_materialise(client):
    """Un compte dont le plan est expliqué — sans quoi le bloc ne s'instancie
    pas et les gardes ne mesureraient rien."""
    from app.database import SessionLocal
    from app.services.training_preferences import save_training_preferences
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    with SessionLocal() as db:
        save_training_preferences(db, uid, sessions_per_week=4,
                                  focus_priorities=["back_width"])
    client.post("/programs/from-weekly-plan", follow_redirects=True)
    return client.get(PLAN_URL).text


# ═════════ Q5 — NIVEAU 2, DANS LE FLUX ═════════


def test_the_explanation_is_no_longer_a_standalone_bordered_card():
    body = _uncommented(PLAN_TPL.read_text(encoding="utf-8"))
    block = body.split("plan_explanation and plan_explanation.available", 1)[1]
    block = block.split("{% endif %}", 1)[0]
    assert 'class="card"' not in block, "la carte bordée autonome est revenue"
    assert "why-plan" in block, "le bloc n'a plus son traitement de niveau 2"


def test_the_explanation_is_an_in_flow_disclosure(client):
    """« Divulgation progressive dans le flux » — donc un `<details>`, et non
    un bloc masqué par autre chose."""
    body = _declare_and_materialise(client)
    assert '<details class="why-plan">' in body


def test_the_title_stays_visible_when_collapsed(client):
    """CE QUI DISTINGUE UN REPLI D'UNE SUPPRESSION. Un contenu replié dont on
    ne voit plus le nom n'est pas replié : il est retiré."""
    body = _declare_and_materialise(client)
    summary = re.search(r'<summary class="why-plan__summary">\s*([^<]+?)\s*</summary>',
                        body)
    assert summary, "le titre n'est plus dans le déclencheur"
    assert summary.group(1) == WHY
    assert "<details class=\"why-plan\" open>" not in body, (
        "déplié par défaut : le repli serait décoratif"
    )


def test_the_content_was_not_redesigned(client):
    """L'ORDRE ÉTAIT EXPLICITE : aucune refonte de contenu. Mêmes éléments,
    mêmes sources citées une par une, même avis final."""
    # ⚠ `html.unescape` : Jinja échappe les apostrophes en `&#39;`, et
    # l'explication en contient. Comparer le rendu brut au texte produit ferait
    # échouer la garde sur l'échappement plutôt que sur le contenu — piège déjà
    # payé sur `TRAIN1-D`.
    import html as html_mod

    body = html_mod.unescape(_declare_and_materialise(client))
    block = body.split('<details class="why-plan">', 1)[1].split("</details>", 1)[0]

    from app.database import SessionLocal
    from app.services.orchestrator_explainer import build_plan_explanation
    from tests.helpers import get_test_user_id

    with SessionLocal() as db:
        explanation = build_plan_explanation(db, get_test_user_id())

    assert explanation.available, "prémisse : l'explication doit exister"
    items = re.findall(r"<li[^>]*>\s*([^<]+?)\s*<span", block)
    assert len(items) == len(explanation.items), (
        f"{len(items)} éléments rendus pour {len(explanation.items)} produits"
    )
    for rendered, produced in zip(items, explanation.items):
        assert rendered == produced.text, (rendered, produced.text)
    assert explanation.notice in block, "l'avis final a disparu"


def test_each_item_still_names_its_source(client):
    """La citation des sources est ce qui distingue un contexte explicite d'une
    recommandation opaque (`C8`). Le repli ne l'emporte pas avec lui.

    ⚠ COMPTER LES `<span>` NE SUFFIT PAS. Ma première écriture vérifiait qu'il
    y avait au moins autant de `<span class="text-dim">` que d'éléments : en
    retirant `item.source_label`, le span RESTE — vide ou réduit au détail — et
    la garde restait verte pendant que plus aucune source n'était nommée.
    Trouvé en plantant le défaut. On compare donc aux libellés PRODUITS.
    """
    import html as html_mod

    from app.database import SessionLocal
    from app.services.orchestrator_explainer import build_plan_explanation
    from tests.helpers import get_test_user_id

    body = html_mod.unescape(_declare_and_materialise(client))
    block = body.split('<details class="why-plan">', 1)[1].split("</details>", 1)[0]

    with SessionLocal() as db:
        explanation = build_plan_explanation(db, get_test_user_id())

    assert explanation.items, "prémisse : l'explication doit avoir des éléments"
    for item in explanation.items:
        assert item.source_label, "un élément produit sans libellé de source"
        assert item.source_label in block, (
            f"source non citée au rendu : « {item.source_label} »"
        )


def test_every_flex_summary_draws_its_own_marker():
    """UN REPLI DOIT AVOIR L'AIR DE S'OUVRIR.

    Défaut MESURÉ sur les styles calculés, pas supposé : un `<summary>` en
    `display: flex` **perd son marqueur natif**. Le témoin qui fonctionne rend
    `display: list-item` ; les deux déclencheurs en `flex` ne dessinaient plus
    rien et ressemblaient à du texte inerte.

    CE QUE LA RECHERCHE GÉNÉRALE A TROUVÉ, ET CE QUI EN A ÉTÉ FAIT. En
    balayant la feuille, deux autres `summary` en `flex` sont apparus :

    * `.machine-panel__summary` — **CSS MORT**, vérifié : plus aucun
      `<summary>` ne porte cette classe. Rien à corriger, rien à garder.
    * `.substitute-picker__summary` — **défaut réel, DÉLIBÉRÉMENT NON
      CORRIGÉ**. Il vit sur l'écran de séance, surface SOUVERAINE, et porte un
      badge de compte en `space-between` : y ajouter un chevron changerait
      l'apparence d'un contrôle protégé. L'ordre du jour porte sur DEUX
      corrections ; celle-ci n'en fait pas partie. Mesurée, consignée,
      soumise à arbitrage — pas maquillée.

    La garde porte donc sur les deux replis que cette tranche possède.
    """
    css = (ROOT / "app/static/css/app.css").read_text(encoding="utf-8")
    stripped = re.sub(r"/\*[\s\S]*?\*/", " ", css)

    for sel in (".why-plan__summary", ".zone-filter__summary"):
        rule = stripped.split(sel + " {", 1)
        assert len(rule) == 2, f"{sel} a disparu de la feuille"
        assert "display: flex" in rule[1].split("}", 1)[0], (
            f"{sel} n'est plus en flex — la garde vise le mauvais défaut"
        )
        # ⚠ CHERCHER LA CHAÎNE `::before` NE SUFFIT PAS. Le sélecteur
        # réapparaît dans la règle `[open]` et dans le bloc `reduced-motion` :
        # en supprimant la règle qui DESSINE, la garde restait verte, satisfaite
        # par une de ces deux autres. Trouvé en plantant le défaut. On exige
        # donc une déclaration qui produit réellement quelque chose de visible.
        # ⚠ Le SÉLECTEUR PEUT TENIR SUR PLUSIEURS LIGNES — la règle groupe les
        # deux replis. Une expression qui n'accepte pas le saut de ligne ne
        # voyait que le dernier sélecteur du groupe, et déclarait le premier
        # sans marqueur. Elle rendait mes plantations rouges POUR LA MAUVAISE
        # RAISON ; c'est le sweep élargi qui l'a montré, pas la plantation.
        drawing = [
            body for selector, body in
            re.findall(r"([^{}]+)\{([^}]*)\}", stripped)
            if f"{sel}::before" in selector and "border-left" in body
        ]
        assert drawing, (
            f"{sel} est en flex et ne DESSINE aucun marqueur : le repli ne se "
            f"voit pas"
        )


def test_the_disclosure_trigger_is_a_reachable_target():
    """44 px = standard produit AUREN, pas WCAG 2.2."""
    css = (ROOT / "app/static/css/app.css").read_text(encoding="utf-8")
    rule = css.split(".why-plan__summary {", 1)[1].split("}", 1)[0]
    assert "min-height: 44px" in rule


# ═════════ NAMING — LE DOMAINE ET CE QU'IL CONTIENT ═════════
#
# ⚠ REPOINTÉ PAR `UI-CP4 LOADOUT`. `UX4_02C` nommait TROIS enfants — Mon plan,
# Mes programmes, Explorer. « Mes programmes » et « Explorer » ne posaient en
# réalité qu'une seule question — « avec quoi puis-je m'entraîner ? » — et
# l'onglet nommé « Programmes » menait au CATALOGUE pendant que les programmes
# de l'utilisateur étaient à deux gestes derrière un hamburger.
#
# Ils ont fusionné en un registre unique, et l'onglet primaire y mène. Ce que
# `UX4_02C` protégeait tient toujours, et ces gardes le vérifient encore :
#
#   * ce qui est NOMMÉ doit MENER quelque part (nommer sans mener est pire) ;
#   * un enfant n'est jamais nommé deux fois dans le même menu ;
#   * aucun nom anglais dans l'interface française ;
#   * l'enfant ne porte pas le nom du domaine **de façon ambiguë**.
#
# Le dernier point change de forme : la surface EST désormais le domaine et
# porte son nom, ce qui est légitime parce qu'il n'y a plus deux objets à
# distinguer. Les rangs internes disent « Mes programmes » et « Séances… »,
# jamais « Programmes » une seconde fois.


def test_the_surface_is_named_and_the_old_child_name_is_gone(client):
    body = client.get(LIBRARY_URL).text
    assert "Programmes" in body
    # Y COMPRIS DANS LE TITRE D'ONGLET. Laissé à « Explorer », il faisait passer
    # cette garde pour la bonne raison apparente — la chaîne était bien dans la
    # page — alors que la surface ne s'appelait plus ainsi nulle part à l'écran.
    assert "Explorer" not in body


def test_the_child_no_longer_wears_the_domain_name_ambiguously(client):
    """« Programmes de séance » confondait l'enfant et le domaine."""
    assert "Programmes de séance" not in client.get(LIBRARY_URL).text


def test_every_named_child_is_still_named_in_the_shell(client):
    body = client.get("/").text
    for child in ("Mon plan", "Programmes"):
        assert child in body, f"enfant non nommé dans la coque : {child}"


def test_each_child_link_leads_to_its_own_surface(client):
    """Nommer sans mener serait pire que ne pas nommer."""
    body = client.get("/").text
    pattern = r'href="[^"]*/plan"[^>]*>Mon plan<'
    assert re.search(pattern, body), "« Mon plan » ne mène pas à /plan"
    # L'onglet primaire mène au registre.
    assert re.search(r'href="[^"]*/library"', body), "l'onglet ne mène nulle part"


def test_the_merged_children_left_no_dead_link(client):
    """Les deux liens secondaires partent ; AUCUNE route n'est supprimée, et
    tout ce qu'ils atteignaient reste atteignable."""
    assert client.get("/programs", follow_redirects=False).status_code == 200
    registre = client.get(LIBRARY_URL).text
    assert "Mes programmes" in registre, "le rang absorbé a disparu"
    assert "Créer un programme" in registre, "créer est devenu inatteignable"


def test_the_domain_label_is_unchanged(client):
    """Le domaine s'appelle **Programmes** — l'onglet ne bouge pas."""
    nav = client.get("/").text.split('class="app-bottom-nav"', 1)[1]
    assert '__label">Programmes<' in nav


def test_no_english_name_enters_the_french_interface(client):
    """L'ordre est explicite : pas « Explore » dans l'interface française."""
    for url in ("/", LIBRARY_URL, PLAN_URL, "/programs"):
        body = client.get(url).text
        assert not re.search(r">\s*Explore\s*<", body), f"« Explore » sur {url}"


def test_the_shell_names_the_children_without_duplicating_them(client):
    """Un enfant nommé deux fois dans le même menu redevient ambigu.

    ⚠ REPOINTÉE PAR `UI-CP6 SHELL` — DE L'ÉCRITURE VERS LE RENDU.

    Elle lisait la SOURCE de `base.html` et y comptait des libellés
    littéraux. `UI-CP6` retire ces littéraux du gabarit : les six destinations
    secondaires étaient écrites DEUX FOIS — une par rendu — et viennent
    désormais d'un contrat unique (`app/services/shell.py`). La source ne
    contient plus que `{{ d.libelle }}`.

    La garde tombait donc sur une boucle, pas sur un défaut. Et elle serait
    devenue **pire que fausse** si on l'avait laissée verte par accident : un
    `count(...) == 0` sur une source qui ne contient plus aucun libellé passe
    tout seul.

    Ce qu'elle protège — « un enfant nommé une seule fois par menu » — se
    vérifie mieux sur le HTML SERVI, qui contient les DEUX rendus. C'est même
    plus strict : elle voit maintenant ce que le gabarit produit, pas ce qu'il
    a l'air de produire.
    """
    body = client.get("/progress", follow_redirects=True).text
    for nav_class in ("topbar__link", "app-rail__sublink"):
        links = re.findall(rf'class="{nav_class}[^"]*"[^>]*>\s*([^<]+?)\s*<', body)
        assert links, f"aucun lien lu pour {nav_class} — la sonde ne mesure rien"
        assert links.count("Mon plan") == 1, (
            f"« Mon plan » apparaît {links.count('Mon plan')} fois dans {nav_class}"
        )
        # Les deux enfants fusionnés ne doivent plus être nommés du tout dans un
        # menu secondaire : leur destination est l'onglet PRIMAIRE, et un lien
        # secondaire qui double une destination primaire est ce que la règle du
        # menu interdisait déjà.
        for parti in ("Mes programmes", "Explorer"):
            assert links.count(parti) == 0, (
                f"« {parti} » subsiste dans {nav_class} alors que sa surface a "
                f"fusionné avec l'onglet primaire"
            )
