"""`POST_CONVERGENCE_INTEGRITY_01` — intégrité après la convergence analytique.

CE QUE CES GARDES FERMENT
--------------------------
  A. Le débordement horizontal de `/` — et surtout l'angle mort qui l'a laissé
     vivre : personne ne rendait la page au-delà de 430 px.
  B. Science est devenue le **document de provenance canonique**. Une
     affirmation périmée n'y est plus une imprécision : c'est une provenance
     fausse, citée par liens profonds depuis `/progress` et le Coach Report.
  C. `rules.html` — second gabarit mort, supprimé ; la redirection survit.
  D. L'atlas est `REFERENCE_SECONDARY` : sa longueur n'est pas un défaut.

MÉTHODE. Chaque garde structurante est vérifiée en plantant son défaut.
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "app/templates"
SCIENCE = TEMPLATES / "science.html"
DIAGRAM = TEMPLATES / "_partials/science_diagram.svg"
HOME_CSS = ROOT / "app/static/css/home.css"
AUDIT = ROOT / "docs/SCIENCE_REFERENCE_AUDIT.md"

#: Les surfaces retirées par la convergence. Aucune ne doit être décrite comme
#: existante par le document de provenance.
REMOVED_SURFACES = ("Synthese", "Synthèse", "Physique")


def _uncommented(src: str) -> str:
    return re.sub(r"\{#.*?#\}", " ", src, flags=re.S)


# ═════════ A — LE DÉBORDEMENT ET SON ANGLE MORT ═════════


def test_the_action_row_can_wrap_instead_of_overflowing():
    """La cause exacte, mesurée : le CTA portait `width: 100%` (correct en
    colonne), la règle bureau passait la ligne en `row` sans jamais le défaire,
    et `nowrap` poussait le lien secondaire 39 px hors cadre."""
    # ⚠ CHERCHER DANS LE BON BLOC. La première écriture cherchait
    # `.today-home__action` dans TOUTE la feuille : elle tombait sur la règle
    # de base (mobile, `column`) et rougissait alors que le correctif était en
    # place, dans le bloc `@media`. La règle de base n'a jamais eu besoin de
    # `wrap` — c'est une colonne.
    css = HOME_CSS.read_text(encoding="utf-8")
    assert "@media (min-width: 900px)" in css
    desktop = css.split("@media (min-width: 900px)", 1)[1]
    m = re.search(r"\.today-home__action\s*\{([^}]*)\}", desktop)
    assert m, "la règle bureau de l'action a disparu"
    rule = m.group(1)
    assert "row" in rule, "la ligne n'est plus horizontale au bureau"
    assert "flex-wrap: wrap" in rule, (
        "sans `wrap`, le lien secondaire ressort de l'écran")


def test_the_measured_diagnosis_is_recorded_not_just_the_fix():
    """Un correctif sans son diagnostic est une supposition. La prochaine
    tranche doit trouver POURQUOI, pas seulement QUOI.

    ⚠ LIRE LE COMMENTAIRE, PAS LA FEUILLE. La première écriture cherchait
    `width: 100%` dans tout le fichier — et passait grâce à la DÉCLARATION
    réelle de `.today-home__cta`, pas grâce au commentaire qu'elle prétendait
    vérifier. Elle serait restée verte avec le diagnostic entièrement effacé.
    """
    css = HOME_CSS.read_text(encoding="utf-8")
    blocks = re.findall(r"/\*[\s\S]*?\*/", css)
    diag = [b for b in blocks if "POST_CONVERGENCE_INTEGRITY_01" in b]
    assert diag, "le bloc de diagnostic a disparu"
    text = diag[0]
    assert "39" in text, "la mesure du débordement n'est plus consignée"
    assert "width: 100%" in text, "la cause racine n'est plus nommée"
    assert "1280" in text, "les largeurs mesurées ne sont plus consignées"


# ═════════ B — SCIENCE, DOCUMENT DE PROVENANCE ═════════


def test_science_describes_no_removed_surface():
    """`/physique` redirige, `/dashboard` ne rend rien. Un document de
    provenance qui les décrit comme existantes rend une provenance fausse."""
    body = _uncommented(SCIENCE.read_text(encoding="utf-8"))
    for surface in REMOVED_SURFACES:
        assert surface not in body, f"Science décrit encore « {surface} »"


def test_the_architecture_diagram_describes_no_removed_surface():
    """LA GARDE QUI COMPTE LE PLUS ICI.

    Le diagramme est un partiel SVG inclus : un `grep` sur `science.html`
    seul ne le voit pas. Il rendait `Synthese` et `Physique` en boîtes de
    sortie, ET dans sa `<desc>` — donc un lecteur d'écran recevait
    l'architecture de 2026-04.
    """
    svg = DIAGRAM.read_text(encoding="utf-8")
    for surface in REMOVED_SURFACES:
        assert surface not in svg, f"le diagramme rend encore « {surface} »"
    assert "Progression" in svg


def test_the_accessible_description_names_exactly_the_drawn_boxes():
    """Une `<desc>` qui diverge du dessin est pire qu'absente : elle est la
    seule lecture possible pour qui ne voit pas le SVG.

    ⚠ VÉRIFIER LA CORRESPONDANCE, PAS LA PRÉSENCE. La première écriture
    assertait « Progression » et « Classement » quelque part dans la `<desc>` :
    elle restait verte alors qu'on avait remplacé « Historique alimente
    Progression et Classement » par « Historique alimente tout », les deux mots
    subsistant dans les phrases suivantes. Trouvé en plantant le défaut.

    On extrait donc les libellés RÉELLEMENT DESSINÉS et on exige que la
    description nomme ceux-là, et aucun autre.
    """
    svg = DIAGRAM.read_text(encoding="utf-8")
    desc = svg.split("<desc", 1)[1].split("</desc>", 1)[0]

    # Les libellés de boîte sont les `<text>` en corps 12 (la police mono).
    drawn = set(re.findall(r'font-size="12">([^<]+)</text>', svg))
    assert drawn, "aucun libellé de boîte trouvé — la garde ne mesure rien"

    for label in drawn:
        assert label in desc, (
            f"« {label} » est dessiné mais absent de la description accessible")

    # Et l'inverse : la description ne doit nommer aucune surface qui n'existe
    # plus sur le dessin.
    for removed in REMOVED_SURFACES:
        assert removed not in desc, f"la description nomme encore « {removed} »"


def test_the_scoring_thresholds_are_still_stated_exactly():
    """LE PENDANT, et il compte autant. Ces nombres décrivent fidèlement
    `quality_score.py` — les retirer aurait ôté de la provenance EXACTE au
    document dont c'est la fonction."""
    body = _uncommented(SCIENCE.read_text(encoding="utf-8"))
    for number in ("20 minutes", "115 et 135", "85 sur 100"):
        assert number in body, f"palier retiré du document de provenance : {number}"


def test_the_scoring_thresholds_are_not_presented_as_training_targets():
    """Trois tranches ont retiré le langage d'objectif des instruments. Le
    laisser sur la page de référence rouvrait la contradiction d'un cran."""
    body = _uncommented(SCIENCE.read_text(encoding="utf-8"))
    assert "cible 20 min" not in body
    assert "paliers de barème, pas des objectifs" in body


def test_the_audit_classifies_every_flagged_item():
    """L'ordre demandait un classement, pas une suppression. Cinq des six
    éléments signalés décrivaient du code vivant — le registre doit le dire."""
    doc = AUDIT.read_text(encoding="utf-8")
    for verdict in ("CURRENT", "STALE_PRODUCT_MODEL", "UNSUPPORTED_CLAIM"):
        assert verdict in doc
    assert "Cinq sur six" in doc


def test_the_stable_rule_anchors_survive(client):
    """`preserve stable rule anchors` — les liens profonds de `/progress` et du
    Coach Report en dépendent, et un `#ancre` absent ne lève aucune erreur."""
    import json

    payload = json.loads(
        (ROOT / "data/method_rules.json").read_text(encoding="utf-8"))
    body = client.get("/science").text
    for rule in payload["rules"]:
        assert f'id="rule-{rule["slug"]}"' in body, rule["slug"]


# ═════════ C — LE GABARIT MORT ═════════


def test_the_dead_rules_template_is_gone():
    assert not (TEMPLATES / "rules.html").exists()


def test_no_renderer_consumes_the_deleted_template():
    for path in list((ROOT / "app").rglob("*.py")) + list(TEMPLATES.rglob("*.html")):
        assert "rules.html" not in path.read_text(encoding="utf-8"), path.name


def test_the_legacy_redirect_survives_the_deletion(client):
    """La route est indépendante du gabarit — mais le vérifier au RENDU est le
    seul moyen de le savoir plutôt que de le croire."""
    r = client.get("/rules", follow_redirects=False)
    assert r.status_code == 301
    assert r.headers["location"] == "/science"


# ═════════ D — L'ATLAS ═════════


def test_the_atlas_status_is_recorded_with_its_reopening_condition():
    """Une longueur déclarée non-défaut sans condition de réouverture est une
    dette qui ne se rouvre jamais."""
    doc = AUDIT.read_text(encoding="utf-8")
    assert "SCIENCE_ATLAS = REFERENCE_SECONDARY" in doc
    assert "TRAIN 3" in doc
    assert "sans contexte machine connu" in doc
