"""`UIV3_TARGETS_44_01` — gardes de la taxonomie et de la sonde.

CE QUE CES GARDES PROTÈGENT, ET POURQUOI ELLES EXISTENT
--------------------------------------------------------
La sonde de zone tactile a menti **trois fois** avant d'être crue, et aucun de
ses défauts n'était visible en relisant le code. Chacun produisait un
inventaire **faux et crédible** :

  1. sans `scrollIntoView`, tout ce qui vit sous le pli rendait « 0 % touché »,
     y compris un lien de 202 px ;
  2. avec `at.contains(el)` dans la condition d'acceptation, le `<body>`
     contenant tout, un bouton de 30 px était déclaré conforme ;
  3. en comptant les étiquettes de champs texte comme cibles opératoires, 19
     libellés de `/profile` exigeaient 44 px — l'erreur du décompte 161 sous
     une autre forme.

Une garde qui relit la prose du module ne protège rien
(`guards-that-guard-nothing`). Celles-ci vérifient donc les **prédicats**, sur
des lignes fabriquées dont on connaît la réponse, et le **source de la sonde**
sur les trois motifs précis dont l'absence ou la présence a coûté un
inventaire faux.
"""
from __future__ import annotations

import pathlib
import re

from scripts.target_size_taxonomy import (
    CATEGORIES,
    PROBE_JS,
    PRODUCT_THRESHOLD_PX,
    TAXONOMY,
    VIEWPORTS,
    WCAG_AA_MIN_PX,
    is_violation,
    is_wcag_aa_failure,
)


def _row(**kw) -> dict:
    """Une ligne d'inventaire par défaut CONFORME — chaque test ne dégrade
    qu'un seul champ, pour qu'un échec désigne sa cause."""
    base = {
        "category": "A",
        "below_product": False,
        "below_wcag_size": False,
        "wcag_spacing_ok": True,
        "hit_full": True,
    }
    base.update(kw)
    return base


# ───────────────────── la taxonomie elle-même ─────────────────────


def test_the_five_categories_exist_and_are_unique():
    keys = [t.key for t in TAXONOMY]
    assert keys == ["A", "B", "C", "D", "E"]
    assert len(set(keys)) == 5


def test_inline_is_the_only_category_exempt_from_the_product_threshold():
    """`C` est la seule exception : WCAG 2.5.8 dispense explicitement un lien
    intégré à une phrase, et le gonfler mécaniquement casserait le texte."""
    exempt = [t.key for t in TAXONOMY if not t.must_reach_product_threshold]
    assert exempt == ["C"]


def test_the_product_threshold_is_not_presented_as_a_wcag_aa_obligation():
    """44 est un standard PRODUIT. Le seuil WCAG 2.2 AA est 24.

    Les confondre sur-déclare une conformité — faux dans le sens qui expose."""
    assert PRODUCT_THRESHOLD_PX == 44
    assert WCAG_AA_MIN_PX == 24
    assert WCAG_AA_MIN_PX < PRODUCT_THRESHOLD_PX


#: Les surfaces où le vocabulaire des seuils tactiles est écrit. Une garde qui
#: ne balaie qu'un fichier laisserait la formulation revenir par un autre.
_TARGET_SIZE_SURFACES = (
    "scripts/target_size_taxonomy.py",
    "tests/test_target_size_taxonomy.py",
    "app/static/css/target_closure.css",
    "docs/strategy/AUREN_UIUX_V3_FOUNDATION_CONTRACT.md",
    "docs/SPRINT_UIV3_TARGETS_44_REPORT.md",
)

#: Formulations INTERDITES. Chacune transforme un seuil technique en
#: affirmation juridique. VOCAB-INTERDIT — cette ligne les cite pour les
#: déclarer, elle ne les affirme pas.
_FORBIDDEN_LEGAL_CLAIMS = (
    "plancher légal", "legal floor", "legally required",      # VOCAB-INTERDIT
    "obligation légale", "exigence légale",                   # VOCAB-INTERDIT
)

#: Marqueur d'ÉCHAPPEMENT. La règle interdit d'AFFIRMER qu'un seuil WCAG est
#: une obligation juridique — pas de citer la formulation pour l'interdire.
#:
#: La première écriture cherchait une négation dans les 80 caractères
#: précédents. C'était de l'analyse de prose française, et elle a rougi sur
#: quatre fichiers qui disaient tous le contraire de ce qu'elle cherche — la garde
#: punissait sa propre doctrine. Une heuristique de langage naturel dans une
#: garde produit des faux positifs pour toujours, et les auteurs finissent par
#: se battre contre elle.
#:
#: Un marqueur mécanique n'a pas ce défaut : la ligne qui cite une formulation
#: interdite porte le token, et c'est un geste conscient.
_VOCAB_ESCAPE = "VOCAB-INTERDIT"


def _asserts_legality(text: str, phrase: str) -> bool:
    """La phrase est-elle AFFIRMÉE, ou citée sur une ligne échappée ?"""
    escape = _VOCAB_ESCAPE.lower()
    return any(phrase in line and escape not in line
               for line in text.splitlines())


def test_no_wcag_threshold_is_ever_described_as_a_legal_obligation():
    """**Correction normative de l'opérateur, 2026-08-20.**

    `24 × 24` est le **seuil WCAG 2.2 niveau AA**, et rien de plus fort.
    Le **W3C ne produit pas les lois** : les obligations varient selon la
    juridiction et passent par des textes distincts — en UE, `EN 301 549` et
    l'European Accessibility Act.

    Décrire ce seuil comme une obligation juridique inscrit dans le dépôt une
    affirmation que personne ici n'a qualité pour faire, et qui est fausse dans
    plusieurs ressorts. C'est la faute symétrique de celle qu'on évite en
    testant l'exception d'espacement : l'une sur-déclare une conformité,
    l'autre sur-déclare une obligation.

    Cette garde balaie les fichiers, pas la mémoire : la formulation est
    revenue naturellement sous plusieurs plumes dans une seule tranche.

    Une ligne qui doit citer une formulation interdite porte le token
    d'échappement — c'est un geste conscient, pas une heuristique de prose.
    """
    root = pathlib.Path(__file__).resolve().parent.parent
    offenders = []
    for rel in _TARGET_SIZE_SURFACES:
        text = (root / rel).read_text(encoding="utf-8").lower()
        for phrase in _FORBIDDEN_LEGAL_CLAIMS:
            if _asserts_legality(text, phrase):
                offenders.append(f"{rel} → « {phrase} »")
    assert not offenders, (
        "seuil WCAG AFFIRMÉ comme une obligation juridique : "
        + " · ".join(offenders)
    )


def test_the_authorised_wording_is_present_in_the_contract():
    """La correction n'est pas seulement une suppression : les deux
    formulations autorisées doivent être écrites, sinon la prochaine plume
    réinvente la sienne."""
    contract = (pathlib.Path(__file__).resolve().parent.parent
                / "docs/strategy/AUREN_UIUX_V3_FOUNDATION_CONTRACT.md"
                ).read_text(encoding="utf-8")
    assert "WCAG 2.2 AA baseline" in contract
    assert "AUREN product standard" in contract
    assert "EN 301 549" in contract, (
        "l'articulation juridique réelle doit être nommée, pas suggérée"
    )


def test_the_three_product_viewports_are_pinned():
    assert [w for w, _ in VIEWPORTS] == [360, 390, 430]


# ───────────────────── le prédicat de violation produit ─────────────────────


def test_a_target_under_the_threshold_is_a_violation():
    assert is_violation(_row(below_product=True, hit_full=False)) is True


def test_an_extended_hit_area_satisfies_the_threshold():
    """`§3.3` — zone tactile ≥ 44, PAS chrome visible ≥ 44.

    Un lien de 14 px dont un `::after` absolu étend la zone à 44 est conforme.
    C'est la forme qui préserve la densité gagnée en phase 2, et
    `getBoundingClientRect()` seul la déclarerait fautive."""
    assert is_violation(_row(below_product=True, hit_full=True)) is False


def test_an_inline_link_is_never_a_violation():
    assert is_violation(_row(category="C", below_product=True, hit_full=False)) is False


def test_an_unknown_category_is_never_a_violation():
    assert is_violation(_row(category="Z", below_product=True, hit_full=False)) is False


# ───────────────────── le prédicat de non-conformité AA ─────────────────────


def test_a_small_isolated_target_passes_aa_by_the_spacing_exception():
    """WCAG 2.2 SC 2.5.8 : sous 24 px reste CONFORME si un cercle de 24 px
    centré sur la cible n'en croise aucun autre.

    Sans ce test, l'audit rapporterait des violations légales inexistantes —
    la faute symétrique de sur-déclarer une conformité."""
    assert is_wcag_aa_failure(
        _row(below_wcag_size=True, hit_full=False, wcag_spacing_ok=True)) is False


def test_a_small_crowded_target_fails_aa():
    assert is_wcag_aa_failure(
        _row(below_wcag_size=True, hit_full=False, wcag_spacing_ok=False)) is True


def test_an_editable_field_is_not_an_aa_target_size_failure():
    """`E` — un contrôle du user-agent est une exception explicite de 2.5.8."""
    assert is_wcag_aa_failure(
        _row(category="E", below_wcag_size=True, hit_full=False,
             wcag_spacing_ok=False)) is False


def test_meeting_the_product_threshold_cannot_be_an_aa_failure():
    assert is_wcag_aa_failure(
        _row(below_wcag_size=True, hit_full=True, wcag_spacing_ok=False)) is False


# ───────────────────── les trois défauts de la sonde ─────────────────────
#
# On vérifie le SOURCE, parce que ces trois motifs ne se testent pas sans un
# navigateur — mais leur régression coûterait un inventaire faux et crédible.


def _code() -> str:
    """La sonde débarrassée de ses commentaires : une garde qui lit sa propre
    prose ne garde rien, et ce dépôt s'y est déjà fait prendre deux fois."""
    no_block = re.sub(r"/\*.*?\*/", " ", PROBE_JS, flags=re.S)
    return re.sub(r"(?m)^\s*//.*$", " ", no_block)


def test_the_probe_scrolls_before_hit_testing():
    """Défaut 1 — `elementFromPoint` travaille en coordonnées viewport."""
    assert "scrollIntoView" in _code()


def test_the_probe_never_accepts_an_ancestor_as_a_hit():
    """Défaut 2 — `at.contains(el)` déclarait conforme un bouton de 30 px,
    parce que le `<body>` contient tout."""
    code = _code()
    assert "el.contains(at)" in code, "la sonde doit accepter un descendant"
    assert "at.contains(el)" not in code, (
        "un ancêtre qui reçoit le doigt ne rend pas l'élément touchable"
    )


def test_the_probe_counts_only_the_points_it_actually_probed():
    """Défaut 1bis — compter des points sautés comme sondés rendait 0 %."""
    code = _code()
    assert "probed++" in code
    assert "partial" in code, "une sonde incomplète doit s'AVOUER indécise"


def test_the_probe_only_treats_choice_inputs_as_label_owned():
    """Défaut 3 — l'étiquette d'un champ nombre n'est pas la cible opératoire.

    19 libellés de `/profile` auraient exigé 44 px sur du texte statique."""
    code = _code()
    assert "'radio'" in code
    assert "'checkbox'" in code
    assert "clipPath" not in code, (
        "le clipping ne suffit pas à faire d'un label la cible — le TYPE le fait"
    )


def test_the_probe_skips_closed_disclosures():
    """Chromium verrouille la mise en page dans un `<details>` fermé ;
    23 faux débordements ont eu cette seule cause."""
    assert "details:not([open])" in _code()


def test_the_probe_measures_the_spacing_exception():
    code = _code()
    assert "spacingOK" in code
    assert "Math.hypot" in code, "l'exception se mesure entre CENTRES de cibles"


def test_every_category_key_used_by_the_probe_exists_in_the_taxonomy():
    """Une catégorie émise par la sonde mais absente de la taxonomie
    disparaîtrait silencieusement du décompte."""
    emitted = set(re.findall(r"category = '([A-Z])'", PROBE_JS))
    assert emitted, "la sonde n'assigne aucune catégorie"
    assert emitted <= set(CATEGORIES)


# ───────────────────── la feuille de style de fermeture ─────────────────────

CSS_DIR = pathlib.Path(__file__).resolve().parent.parent / "app/static/css"
#: La fermeture vit dans SA feuille, pas dans `interaction.css`.
#: `test_the_family_stays_small` garde ce dernier à six primitives et a refusé
#: d'y voir apparaître `btn`, `topbar`, `foot`, `method-reminder`. Elle avait
#: raison : `interaction.css` CRÉE des primitives, cette feuille FERME des
#: surfaces héritées. Deux métiers, deux fichiers.
CLOSURE = CSS_DIR / "target_closure.css"


def test_css_comment_delimiters_are_balanced():
    """Un `*/` sans `/*` avale SILENCIEUSEMENT la règle qui suit.

    Vécu pendant cette tranche : un bloc de commentaire ouvert sans `/*` a
    fait disparaître `.topbar__brand { position: relative }`. Conséquence
    mesurée — le pseudo-élément d'extension prenait le viewport pour bloc
    conteneur et faisait **844 px de haut**, et 24 cibles réparées
    redevenaient fautives d'un coup. Rien dans le fichier ne le montrait à la
    lecture ; seule la mesure au navigateur l'a rendu visible.
    """
    for sheet in sorted(CSS_DIR.glob("*.css")):
        src = sheet.read_text(encoding="utf-8")
        assert src.count("/*") == src.count("*/"), (
            f"{sheet.name} : {src.count('/*')} ouvertures pour "
            f"{src.count('*/')} fermetures — une règle est peut-être avalée"
        )


def test_the_closure_section_never_reaches_the_session_console():
    """La console de séance est un `reference consumer` : 0 violation au
    dogfood accepté, et `AUREN_UI_BLUEPRINT` lui interdit d'être retouchée par
    cette tranche. Profiter d'une passe d'accessibilité pour modifier une
    surface acceptée est le mode d'échec décrit par `CLAUDE.md §5.5`.
    """
    src = CLOSURE.read_text(encoding="utf-8")
    marker = "UIV3_TARGETS_44_01"
    assert marker in src, "feuille de fermeture introuvable"
    # On ne lit que les SÉLECTEURS, jamais la prose. Ce fichier EXPLIQUE
    # pourquoi il ne touche pas la console : une garde naïve trouverait
    # `.console` dans son propre commentaire et rougirait sur l'explication
    # — le motif `guards-that-guard-nothing` retourné contre lui-même.
    #
    # Le repère vit DANS le commentaire d'en-tête : couper à `src.index(marker)`
    # laisse un commentaire ouvert que le dépouilleur ne peut pas fermer. On
    # démarre donc après la fermeture de ce commentaire.
    head = src.index(marker)
    section = src[src.index("*/", head) + 2:]
    selectors = re.sub(r"/\*.*?\*/", " ", section, flags=re.S)
    for forbidden in (".console", ".dock", ".setline", ".session-head", ".ex-nav"):
        assert forbidden not in selectors, (
            f"la fermeture 44 px atteint {forbidden} — la console est un "
            "reference consumer, pas une cible de refonte"
        )
