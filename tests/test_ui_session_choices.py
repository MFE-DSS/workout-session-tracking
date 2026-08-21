"""Sb_UI_SESSION_CHOICES_DISCLOSURES_01 — clavier rendu, décisions intactes.

Le défaut corrigé ici n'était pas visuel : `.segmented__option input` portait
`display: none`, ce qui retirait le radio natif de la navigation clavier et de
l'arbre d'accessibilité — sur **cinq** surfaces, dont les alternatives
d'exercice en séance.

Le reste du fichier existe pour que la correction de présentation ne déplace
**aucune** décision de substitution.
"""
from __future__ import annotations

import pathlib
import re

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
APP_CSS = REPO_ROOT / "app" / "static" / "css" / "app.css"
INTERACTION_CSS = REPO_ROOT / "app" / "static" / "css" / "interaction.css"
MACROS = REPO_ROOT / "app" / "templates" / "_macros.html"
EXERCISE_CARD = REPO_ROOT / "app" / "templates" / "_partials" / "exercise_card.html"

#: Inventaire complet issu du préflight — les cinq surfaces qui utilisent
#: `.segmented`. Épinglé pour qu'un sixième consommateur soit un geste conscient.
SEGMENTED_CONSUMERS = {
    "app/templates/index.html",                    # échelle de disponibilité
    "app/templates/_macros.html",                  # macro partagée
    "app/templates/session_detail.html",           # concentration + énergie
    "app/templates/_partials/exercise_card.html",  # sensation + alternatives
}


def _css() -> str:
    return APP_CSS.read_text(encoding="utf-8") + INTERACTION_CSS.read_text(
        encoding="utf-8")


# ── P0 : le radio natif est de nouveau opérable au clavier ───────────────────


def test_the_segmented_radio_is_no_longer_display_none():
    """Le défaut exact rapporté, épinglé par sa forme littérale."""
    assert ".segmented__option input { display: none; }" not in _css()
    assert not re.search(
        r"\.segmented__option input\s*\{[^}]*display:\s*none", _css())


def test_the_hiding_declaration_is_shared_not_duplicated():
    """Une seule implémentation de masquage accessible dans le dépôt."""
    text = INTERACTION_CSS.read_text(encoding="utf-8")
    assert ".a11y-input,\n.segmented__option input {" in text
    # Et le bloc conserve les propriétés qui préservent le focus.
    block = text.split(".a11y-input,\n.segmented__option input {", 1)[1]
    block = block.split("}", 1)[0]
    assert "position: absolute" in block
    assert "clip-path" in block
    assert "display: none" not in block
    assert "visibility: hidden" not in block


def test_the_focus_indicator_lands_on_the_visible_surface():
    """L'input fait 1 px : le focus doit se voir sur le libellé associé."""
    text = INTERACTION_CSS.read_text(encoding="utf-8")
    assert ".segmented__option input:focus-visible + span" in text
    block = text.split(".segmented__option input:focus-visible + span {", 1)[1]
    block = block.split("}", 1)[0]
    assert "outline" in block
    assert "var(--accent)" in block


def test_the_selected_state_carries_a_non_colour_cue():
    text = INTERACTION_CSS.read_text(encoding="utf-8")
    assert ".segmented__option input:checked + span::before" in text
    assert '"✓ "' in text or "'✓ '" in text


def test_every_segmented_consumer_is_covered_by_the_central_fix():
    """Le sélecteur est global : la correction l'est aussi, par construction."""
    # Cherche l'USAGE de la classe CSS, pas le mot. `muscle_focus.html` parle de
    # « source-segmented deltoid » dans un commentaire : c'est la terminologie
    # des données de maillage, sans rapport avec le composant.
    found = set()
    for path in (REPO_ROOT / "app" / "templates").rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        if 'class="segmented' in text or "import segmented" in text \
                or "{% macro segmented(" in text:
            found.add(str(path.relative_to(REPO_ROOT)))
    assert found == SEGMENTED_CONSUMERS, sorted(found ^ SEGMENTED_CONSUMERS)


def test_the_macro_still_renders_a_native_radio():
    src = MACROS.read_text(encoding="utf-8")
    seg = src[src.index("{% macro segmented("):src.index("{% endmacro %}")]
    assert 'type="radio"' in seg
    assert "<label class=\"segmented__option\">" in seg
    # Le label enveloppe l'input : toute la surface reste activable.
    assert seg.index("<label") < seg.index('type="radio"') < seg.index("</label>")


def test_no_hand_made_aria_radio_replaced_the_native_control():
    src = MACROS.read_text(encoding="utf-8") + EXERCISE_CARD.read_text(
        encoding="utf-8")
    for banned in ('role="radio"', 'role="radiogroup"', 'role="listbox"',
                   'role="combobox"'):
        assert banned not in src


# ── Alternatives : une seule liste groupée ───────────────────────────────────


def test_alternative_rows_do_not_each_get_full_card_chrome():
    text = INTERACTION_CSS.read_text(encoding="utf-8")
    block = text.split(".segmented--stacked .segmented__option span {", 1)[1]
    block = block.split("}", 1)[0]
    assert "border-radius: 0" in block
    assert "box-shadow" not in block
    # La séparation est un filet ENTRE options, pas une bordure par option.
    assert ".segmented--stacked .segmented__option + .segmented__option span" in text


def test_alternative_rows_meet_the_product_touch_target():
    text = INTERACTION_CSS.read_text(encoding="utf-8")
    block = text.split(".segmented--stacked .segmented__option span {", 1)[1]
    block = block.split("}", 1)[0]
    assert "min-height: 44px" in block


def test_no_gradient_or_decorative_shadow_was_introduced():
    text = INTERACTION_CSS.read_text(encoding="utf-8")
    assert "gradient" not in text
    for shadow in re.findall(r"box-shadow:[^;]+;", text):
        assert "inset" in shadow, shadow


def test_no_inline_style_was_added_to_the_alternatives_block():
    src = EXERCISE_CARD.read_text(encoding="utf-8")
    start = src.index('class="segmented segmented--stacked"')
    block = src[start:src.index("</div>", start)]
    assert "style=" not in block


# ── Parité de substitution — le cœur du gel produit ──────────────────────────


def _sub_block() -> str:
    src = EXERCISE_CARD.read_text(encoding="utf-8")
    start = src.index('class="segmented segmented--stacked"')
    return src[start:start + 4000]


def test_the_radio_name_is_unchanged():
    assert 'name="substituted_name"' in _sub_block()


def test_the_prescribed_option_still_posts_an_empty_value():
    block = _sub_block()
    assert 'name="substituted_name" value=""' in block


def test_every_candidate_still_posts_its_own_name():
    block = _sub_block()
    assert 'value="{{ s.name }}"' in block


def test_the_tier_order_is_n1_then_n2_then_n3():
    block = _sub_block()
    i1 = block.index("grouped.get('N1'")
    i2 = block.index("grouped.get('N2'")
    i3 = block.index("grouped.get('N3'")
    assert i1 < i2 < i3


def test_the_checked_candidate_is_still_the_persisted_one():
    assert "se.substituted_name == s.name" in _sub_block()


def test_the_legacy_flat_fallback_is_preserved():
    src = EXERCISE_CARD.read_text(encoding="utf-8")
    assert "total_grouped == 0" in src


def test_no_decision_engine_was_touched():
    """Aucun MOTEUR DE DÉCISION ne bouge.

    ANCIEN CONTRAT : la liste gelée incluait `app/routers/sessions.py`, parce
    que `Sb_UI_SESSION_CHOICES_DISCLOSURES_01` était une tranche de
    PRÉSENTATION — elle n'avait aucune raison de toucher au routeur.

    Sb_SESSION_SET_ACTION_01 est une tranche FONCTIONNELLE, explicitement
    autorisée à modifier ce routeur : c'est là que vit l'action de série
    (`nav=stay`), et le produit n'en avait aucune. Garder le routeur dans la
    liste reviendrait à interdire le sprint qui l'a autorisé.

    L'invariant réel — « la présentation ne décide de rien » — est CONSERVÉ
    et reste vérifié sur les trois moteurs qui le portent réellement :
    substitution, recommandation, comportement. Aucun d'eux n'est touché.

    Le routeur, lui, est couvert par des gardes dédiées : `test_session_set_action`
    vérifie que `stay` sauvegarde, ancre et n'altère ni `prev` ni `next`, et
    qu'aucune sémantique de complétion n'est introduite.
    """
    import subprocess

    out = subprocess.run(
        ["git", "diff", "--name-only", "e8614bd", "--",
         "app/services/substitution.py",
         "app/services/recommendation.py"],
        cwd=str(REPO_ROOT), capture_output=True, text=True).stdout.strip()
    assert out == "", f"decision engine touched: {out}"


def test_the_behavioural_engine_may_shrink_but_never_grow():
    """**AMENDEMENT DU GEL — `OPERATOR_DECISION` D6, 2026-08-21.**

    `behavioral.py` sort du gel par diff de fichier. Ce n'est pas un
    relâchement : c'est un **remplacement par une garde plus précise**, et il
    faut dire pourquoi les deux ne sont pas équivalentes.

    Le gel par diff a servi, cette semaine encore : il a refusé cinq champs
    additifs qu'`UX4_03B` voulait y ajouter pour servir une surface. Mais il
    interdit aussi de **retirer** ce qui est mort, et le dépôt en avait quatre
    exemples — dont un composite fabriqué et une phrase de coaching contenant
    la chaîne même que `DO_NOT_SURFACE` interdit.

    Un gel qui empêche de nettoyer une arme chargée protège mal.

    Ce qui remplace le diff est **l'invariant que le gel visait vraiment** :
    la présentation ne doit pas faire GROSSIR ce moteur. On épingle donc
    l'API — champs et fonctions publiques. Un ajout rougit ; un retrait exige
    de modifier cette liste, donc de le déclarer.

    `substitution.py` et `recommendation.py` restent gelés par diff : aucune
    décision ne les a rouverts.
    """
    import dataclasses

    import app.services.behavioral as behavioral

    assert {f.name for f in dataclasses.fields(behavioral.BehavioralState)} == {
        "performance_score", "consistency_score", "fatigue_score",
        "streak_days", "readiness_score",
    }, "l'état comportemental a changé de forme — décision requise"

    public = {n for n in vars(behavioral) if not n.startswith("_")
              and callable(getattr(behavioral, n))
              and getattr(getattr(behavioral, n), "__module__", "")
              == behavioral.__name__}
    assert public == {
        "BehavioralState",
        "compute_session_fatigue", "compute_weighted_fatigue",
        "compute_consistency", "compute_readiness", "compute_behavioral_state",
    }, "l'API du moteur a changé — décision requise"


def test_the_deprecated_composite_has_no_new_consumer():
    """`OPERATOR_DECISION` D8 — `readiness_score` est **déprécié**.

    Mesuré : sur un compte sans aucune donnée il vaut `25,0`, dont la
    **totalité** vient du défaut de fatigue. Il n'est rendu sur aucune surface,
    et cette garde existe pour que ça reste vrai — parce que le mode d'échec
    est établi : `UX4_03` a fait exactement cela avec `fatigue_score`, et
    l'opérateur a refusé le rendu.

    ⚠ La première écriture de cette garde utilisait `git grep -l` et rougissait
    sur **son propre commentaire d'avertissement** — huitième occurrence dans
    ce dépôt d'une garde qui lit de la prose au lieu du code. On dépouille donc
    les commentaires avant de chercher.

    L'invariant tenu : **aucun gabarit ne le rend**, et aucun module `app/`
    hors de la liste ne le lit.
    """
    import re as _re

    # 1. Aucune surface. C'est l'invariant qui compte : le composite peut
    #    survivre dans un service, il ne peut pas atteindre un écran.
    for tpl in (REPO_ROOT / "app" / "templates").rglob("*.html"):
        body = _re.sub(r"\{#.*?#\}", " ", tpl.read_text(encoding="utf-8"),
                       flags=_re.S)
        assert "readiness_score" not in body, (
            f"le composite déprécié est rendu par {tpl.name}"
        )

    # 2. Aucun lecteur nouveau côté application, commentaires exclus.
    readers = set()
    for src in (REPO_ROOT / "app").rglob("*.py"):
        code = _re.sub(r"#.*", " ", src.read_text(encoding="utf-8"))
        code = _re.sub(r'""".*?"""', " ", code, flags=_re.S)
        if "readiness_score" in code:
            readers.add(src.relative_to(REPO_ROOT).as_posix())

    assert readers == {
        "app/services/behavioral.py",         # le producteur, déprécié
        "app/services/recovery_contract.py",  # le normaliseur nommé, sans consommateur
    }, f"consommateur nouveau du composite déprécié : {sorted(readers)}"


# ── Disclosures ──────────────────────────────────────────────────────────────


def test_the_disclosures_remain_native_details():
    src = EXERCISE_CARD.read_text(encoding="utf-8")
    assert "<details" in src
    assert "<summary" in src
    # Aucun JS d'ouverture/fermeture ajouté.
    assert "addEventListener" not in src


def test_no_new_js_file_was_added_by_this_slice():
    names = sorted(p.name for p in (REPO_ROOT / "app" / "static" / "js").glob("*.js"))
    assert names == ["prefs_focus_rank.js", "preview.js", "session_focus.js"]


def test_the_open_disclosure_is_not_repainted_amber():
    text = INTERACTION_CSS.read_text(encoding="utf-8")
    for block in re.findall(r"\.disclosure\[open\][^{]*\{[^}]*\}", text):
        assert "border-color: var(--accent)" not in block


# ── Rendu réel ───────────────────────────────────────────────────────────────


def test_the_rendered_segmented_input_is_not_display_none(client):
    """Bout en bout : la page rend un radio réellement opérable."""
    page = client.get("/").text
    if "segmented__option" not in page:
        pytest.skip("no segmented control on this page state")
    assert 'type="radio"' in page
    assert "display:none" not in page.replace(" ", "")
