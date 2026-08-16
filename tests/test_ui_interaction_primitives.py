"""Sb_UI_INTERACTION_PRIMITIVES_01 — la grammaire d'interaction, épinglée.

Les propriétés testées ici sont celles qu'un rendu « joli » peut détruire sans
que rien ne casse : un input retiré du clavier, une sélection lisible seulement
en couleur, une cible tactile de 16 px, une bordure par enfant.

Le dogfood réel a rapporté « boîtes dans des boîtes » et « la sélection ne se
voit pas » — ces tests existent pour que la correction ne régresse pas.
"""
from __future__ import annotations

import pathlib
import re

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = REPO_ROOT / "app" / "static" / "css" / "interaction.css"
MACROS = REPO_ROOT / "app" / "templates" / "_macros.html"


def _css() -> str:
    return CSS.read_text(encoding="utf-8")


def _macros() -> str:
    return MACROS.read_text(encoding="utf-8")


def _rule(selector: str) -> str:
    """The declaration block of the rule whose selector STARTS a line.

    A plain `find()` matched substrings: asking for `.choice-row {` returned
    the block of `.choice-group .choice-row + .choice-row {`, so three tests
    were reading the wrong declarations. Anchoring on the line start makes the
    lookup mean what it says.
    """
    wanted = selector.rstrip(" {")
    text = _css()
    pattern = re.compile(
        r"^" + re.escape(wanted) + r"\s*\{(.*?)\}", re.MULTILINE | re.DOTALL)
    match = pattern.search(text)
    assert match, f"no rule whose selector begins the line: {wanted}"
    return match.group(1)


def _render(template: str, **ctx) -> str:
    from app.templating import templates

    return templates.get_template("_render_probe.html") if False else \
        templates.env.from_string(template).render(**ctx)


# ── Sémantique native préservée ──────────────────────────────────────────────


def test_the_operable_input_is_never_display_none():
    """`display:none` retirerait le seul contrôle opérable du clavier."""
    css = _css()
    block = _rule(".a11y-input")
    assert "display: none" not in block
    assert "visibility: hidden" not in block
    # Le masquage accessible canonique.
    assert "clip-path" in block or "clip" in block
    assert "position: absolute" in block
    # Et la famille n'introduit nulle part le motif interdit sur un input.
    assert not re.search(r"__input[^{]*\{[^}]*display:\s*none", css)


def test_choice_rows_use_native_radio_and_checkbox():
    src = _macros()
    assert 'type="{{ kind }}"' in src
    assert 'kind="radio"' in src
    # Aucun combobox ARIA maison.
    assert 'role="combobox"' not in src
    assert 'role="listbox"' not in src


def test_the_disclosure_uses_native_details():
    src = _macros()
    assert "<details class=\"disclosure\"" in src
    assert "<summary class=\"disclosure__summary\"" in src


def test_the_select_shell_wraps_a_native_select():
    src = _macros()
    assert "<select class=\"select-shell__control\"" in src


# ── Règle 2 — l'état sélectionné se lit sans couleur ─────────────────────────


def test_the_selected_state_has_at_least_two_non_colour_cues():
    css = _css()
    # (1) le marqueur porte un glyphe, (2) le libellé passe en gras,
    # (3) une arête inset apparaît.
    assert ":checked ~ .choice-row__marker" in css
    weight = re.search(
        r":checked ~ \.choice-row__body \.choice-row__label\s*\{[^}]*font-weight:\s*600",
        css)
    assert weight, "selected label must change weight, not only colour"
    assert "box-shadow: inset 2px 0 0" in css


def test_the_marker_glyph_is_real_text_not_a_background_image():
    src = _macros()
    assert "●" in src
    assert "✓" in src
    assert "background-image" not in _css()


def test_amber_is_never_a_full_surface_fill_on_a_selected_row():
    block = _rule(".choice-row:has(.choice-row__input:checked)")
    # Fond doux + arête, jamais `background: var(--accent)` plein.
    assert "var(--accent-soft)" in block
    assert "background: var(--accent);" not in block


def test_no_gradient_and_no_decorative_shadow():
    css = _css()
    assert "gradient" not in css
    # La seule ombre autorisée est l'arête `inset` de l'état sélectionné.
    for shadow in re.findall(r"box-shadow:[^;]+;", css):
        assert "inset" in shadow, shadow


def test_no_second_accent_colour_is_introduced():
    css = _css()
    hexes = {h.lower() for h in re.findall(r"#[0-9a-fA-F]{3,8}", css)}
    assert hexes == set(), f"raw colours bypass the token system: {hexes}"


# ── Règle 3 — cible tactile ──────────────────────────────────────────────────


@pytest.mark.parametrize(
    "selector", [".choice-row {", ".disclosure__summary {", ".select-shell__control {"])
def test_interactive_rows_meet_the_44px_product_target(selector):
    block = _rule(selector)
    assert "min-height: 44px" in block


def test_the_whole_row_is_the_pointer_target_not_just_the_marker(client):
    """Asserted on the RENDERED row, not on template source.

    The source version sliced to the first `</label>` in the file, which
    belongs to the pre-existing `segmented` macro further up — so it compared
    an empty string and would have passed on anything.
    """
    html = _render(
        '{% from "_macros.html" import choice_row %}'
        '{{ choice_row("focus", "shoulders", "Épaules", meta="haut du corps") }}')
    row = html[html.index('<label class="choice-row"'):html.rindex("</label>")]
    # L'input, le marqueur ET le libellé vivent tous DANS le label.
    assert "choice-row__input" in row
    assert "choice-row__marker" in row
    assert "Épaules" in row
    assert "haut du corps" in row
    assert "cursor: pointer" in _rule(".choice-row {")


# ── Focus visible ────────────────────────────────────────────────────────────


def test_every_interactive_primitive_exposes_a_visible_focus():
    css = _css()
    assert ".choice-row:focus-within" in css
    assert ".disclosure__summary:focus-visible" in css
    assert ".select-shell__control:focus-visible" in css
    for block in re.findall(r":focus(?:-visible|-within)\s*\{[^}]*\}", css):
        assert "outline" in block
        assert "outline: none" not in block


# ── Règle 1 — un cadre par groupe sémantique ─────────────────────────────────


def test_the_group_is_framed_once_and_children_use_separators():
    group = _rule(".choice-group {")
    assert "border: 1px solid" in group
    # Les rangées n'ont pas leur propre bordure/rayon/ombre.
    row = _rule(".choice-row {")
    assert "border:" not in row
    assert "border-radius" not in row
    assert "box-shadow" not in row
    # La séparation est un filet ENTRE rangées.
    assert ".choice-group .choice-row + .choice-row" in _css()


def test_an_open_disclosure_does_not_frame_its_content_again():
    panel = _rule(".disclosure__panel")
    assert "border-top: 1px solid" in panel
    assert "border-radius" not in panel
    assert "box-shadow" not in panel
    # Ouvrir ne repeint pas toute la bordure en ambre.
    css = _css()
    open_rules = re.findall(r"\.disclosure\[open\][^{]*\{[^}]*\}", css)
    assert open_rules
    for block in open_rules:
        assert "border-color: var(--accent)" not in block


def test_the_disclosure_open_state_is_exposed_without_colour_only():
    css = _css()
    assert "font-weight: 600" in _rule(".disclosure[open] > .disclosure__summary")
    assert "rotate(180deg)" in css


# ── Disabled ─────────────────────────────────────────────────────────────────


def test_disabled_really_disables_and_looks_disabled():
    src = _macros()
    assert "{% if disabled %}disabled{% endif %}" in src
    css = _css()
    assert ".choice-row:has(.choice-row__input:disabled)" in css
    assert "cursor: not-allowed" in css
    assert ".select-shell__control:disabled" in css


# ── Rang (primitive B) ───────────────────────────────────────────────────────


def test_the_rank_stays_visible_after_selection():
    css = _css()
    assert ".choice-row__rank" in css
    # Le rang est du TEXTE dans le libellé, donc il survit à la sélection.
    src = _macros()
    assert 'class="choice-row__rank"' in src
    # Et la place est réservée quand il est vide, pour que les libellés ne
    # sautent pas lorsqu'une sélection est retirée.
    assert ".choice-row__rank:empty::before" in css


def test_the_rank_is_monospaced_so_columns_align():
    assert "var(--font-mono)" in _rule(".choice-row__rank {")


# ── Gouvernance CSS ──────────────────────────────────────────────────────────


def test_the_primitives_are_loaded_by_the_base_template():
    base = (REPO_ROOT / "app" / "templates" / "base.html").read_text(encoding="utf-8")
    assert "css/interaction.css" in base
    assert base.index("css/app.css") < base.index("css/interaction.css")


def test_no_global_element_selector_can_touch_unrelated_forms():
    """A bare `input {}` or `select {}` here would mutate legacy admin forms.

    The first version only inspected lines that *ended* with `{`, so a
    single-line rule — `select { border: 1px solid red; }` — slipped straight
    through. Planting exactly that left all 29 tests green. Selectors are now
    extracted from the stylesheet structurally, whatever the formatting.
    """
    text = re.sub(r"/\*.*?\*/", "", _css(), flags=re.DOTALL)
    selectors: list[str] = []
    for block in re.finditer(r"([^{}]+)\{[^{}]*\}", text):
        raw = block.group(1).strip()
        if not raw or raw.startswith("@") or raw.startswith("to ") or raw == "from":
            continue
        selectors.extend(part.strip() for part in raw.split(","))

    assert selectors, "no selectors parsed — the guard would be vacuous"
    for part in selectors:
        if not part:
            continue
        # Every compound must be anchored on a class, pseudo-class or attribute.
        assert re.search(r"[.\[:]", part), (
            f"unscoped selector would leak globally: {part!r}")


def test_the_family_stays_small():
    """Six primitives, not twenty variants.

    Counts primitive ROOTS, not BEM parts: `.choice-row__marker` is a piece of
    `.choice-row`, not a separate component. The first version counted every
    `__part` and `--modifier` and therefore measured verbosity, not family size.
    """
    roots = {
        m.split("__")[0].split("--")[0]
        for m in re.findall(r"^\.([a-z0-9_-]+)", _css(), re.MULTILINE)
    }
    #: Les primitives réutilisables — ce que ce test protège de la prolifération.
    primitives = {
        "a11y-input", "choice-group", "choice-row", "choice-grid",
        "disclosure", "select-shell",
    }
    #: Agencement d'une page précise, pas des primitives : ces classes ne sont
    #: pas destinées à être réutilisées ailleurs et ne comptent donc pas comme
    #: des variantes de la famille. Elles restent listées explicitement pour
    #: que leur ajout soit un geste conscient.
    layout = {"prefs-form", "prefs-block", "prefs-fallback"}
    assert roots <= primitives | layout, sorted(roots - (primitives | layout))
    assert len(primitives) == 6


def test_reduced_motion_is_respected():
    assert "prefers-reduced-motion" in _css()


# ── Rendu réel des macros ────────────────────────────────────────────────────


def test_a_rendered_choice_row_keeps_the_input_operable(client):
    html = _render(
        '{% from "_macros.html" import choice_row %}'
        '{{ choice_row("focus", "shoulders", "Épaules", checked=True, rank="01") }}')
    assert 'type="radio"' in html
    assert 'name="focus"' in html
    assert 'value="shoulders"' in html
    assert "checked" in html
    assert "a11y-input" in html
    assert "01" in html
    assert "display:none" not in html.replace(" ", "")


def test_a_rendered_checkbox_row_uses_checkbox_semantics(client):
    html = _render(
        '{% from "_macros.html" import choice_row %}'
        '{{ choice_row("equipment", "barbell", "Barre", kind="checkbox") }}')
    assert 'type="checkbox"' in html
    assert "choice-row__marker--check" in html


def test_a_rendered_disclosure_is_native_and_closed_by_default(client):
    html = _render(
        '{% from "_macros.html" import disclosure %}'
        '{% call disclosure("Détails machine") %}contenu{% endcall %}')
    assert "<details" in html
    assert "<summary" in html
    assert " open" not in html.split(">")[0]
    assert "contenu" in html


def test_a_rendered_select_shell_marks_the_selected_option(client):
    html = _render(
        '{% from "_macros.html" import select_shell %}'
        '{{ select_shell("sessions_per_week", [1,2,3], selected=2,'
        ' empty_label="Non renseigné") }}')
    assert '<option value="2" selected>' in html
    assert '<option value="">Non renseigné</option>' in html


def test_rendered_rows_carry_no_inline_style(client):
    html = _render(
        '{% from "_macros.html" import choice_row %}'
        '{{ choice_row("a", "b", "Label") }}')
    assert "style=" not in html
