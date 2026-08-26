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


# ═════════ NAMING — UN DOMAINE, TROIS ENFANTS NOMMÉS ═════════


def test_the_child_surface_is_called_explorer(client):
    body = client.get(LIBRARY_URL).text
    assert "Explorer" in body


def test_the_child_no_longer_wears_the_domain_name(client):
    """« Programmes de séance » confondait l'enfant et le domaine : l'onglet du
    domaine menait à une page portant presque son nom."""
    assert "Programmes de séance" not in client.get(LIBRARY_URL).text


def test_the_three_children_are_all_named_in_the_shell(client):
    """Avant, « Explorer » n'existait comme mot NULLE PART : l'onglet y menait
    sans le nommer, donc aucun des trois enfants n'était désignable."""
    body = client.get("/").text
    for child in ("Mon plan", "Mes programmes", "Explorer"):
        assert child in body, f"enfant non nommé dans la coque : {child}"


def test_each_child_link_leads_to_its_own_surface(client):
    """Nommer sans mener serait pire que ne pas nommer."""
    body = client.get("/").text
    for child, url in (("Mon plan", "/plan"),
                       ("Mes programmes", "/programs"),
                       ("Explorer", "/library")):
        pattern = rf'href="[^"]*{re.escape(url)}"[^>]*>{re.escape(child)}<'
        assert re.search(pattern, body), f"« {child} » ne mène pas à {url}"


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
    """Un enfant nommé deux fois dans le même menu redevient ambigu."""
    body = _uncommented(BASE_TPL.read_text(encoding="utf-8"))
    for nav_class in ("topbar__link", "app-rail__sublink"):
        links = re.findall(rf'class="{nav_class}[^"]*"[^>]*>([^<]+)<', body)
        for child in ("Mon plan", "Mes programmes", "Explorer"):
            assert links.count(child) == 1, (
                f"« {child} » apparaît {links.count(child)} fois dans {nav_class}"
            )
