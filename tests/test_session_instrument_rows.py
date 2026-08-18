"""D5_SESSION_INSTRUMENT_ROWS_01 — la ligne de série est un instrument.

POURQUOI CES TESTS EXISTENT
---------------------------
La page `/sessions/{id}` était cassée à 390 px et **aucune garde du dépôt ne
l'a vue** : les 4 898 tests passaient. Ils lisaient tous du HTML, et le défaut
n'était pas dans le HTML — il était dans le rapport entre une piste de grille
de 40 px et un contenu de 101 px.

Ces tests ne peuvent pas mesurer un pixel non plus. Ils pinnent donc les
**causes structurelles** du débordement, celles qu'un futur commit pourrait
réintroduire sans s'en apercevoir :

- un libellé de ligne qui redevient une phrase plutôt qu'un code ;
- une piste de grille à largeur fixe qui ne peut pas contenir son contenu ;
- une ligne d'action qui ne peut pas revenir à la ligne ;
- un bouton primaire qui rétrécit avant ses voisins.

La preuve en pixels est produite par le harnais de rendu et consignée dans
`docs/SPRINT_D5_SESSION_INSTRUMENT_ROWS_01_REPORT.md` (CLAUDE.md §5.1).
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CARD = ROOT / "app" / "templates" / "_partials" / "exercise_card.html"
APP_CSS = ROOT / "app" / "static" / "css" / "app.css"
FOCUS_CSS = ROOT / "app" / "static" / "css" / "session_focus.css"


def _rule(css: str, selector: str) -> str:
    """The declaration block of `selector`, or '' when absent."""
    m = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", css)
    return m.group(1) if m else ""


def _start(client, slug: str = "push-a") -> int:
    r = client.post("/sessions", data={"template_slug": slug}, follow_redirects=False)
    return int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))


# ───────── le libellé est un code, plus une phrase ─────────


def test_set_rows_are_labelled_with_a_compact_code(client):
    """« Série #1 » → « S1 », « Échauf. #1 » → « É1 »."""
    sid = _start(client)
    body = client.get(f"/sessions/{sid}").text
    codes = re.findall(r'<span class="set-row__code">([^<]+)</span>', body)
    assert codes, "no set-row code rendered"
    for code in codes:
        assert re.fullmatch(r"[SÉ]\d+", code), f"not a compact code: {code!r}"


def test_the_row_label_no_longer_contains_a_sentence(client):
    """La régression exacte à empêcher.

    Le contenu du label est ce qui doit tenir dans la piste étroite. Y
    réintroduire un mot — « Série », « actif », « dernière » — recrée le
    débordement mesuré, sans qu'aucun autre test ne bronche.
    """
    sid = _start(client)
    body = client.get(f"/sessions/{sid}").text
    labels = re.findall(
        r'<div class="set-row__label[^"]*">(.*?)</div>', body, re.DOTALL
    )
    assert labels, "no set-row label rendered"
    for label in labels:
        text = re.sub(r"<[^>]+>", " ", label)
        words = [w for w in re.findall(r"[A-Za-zÀ-ÿ]{3,}", text)]
        assert words == [], f"prose came back into the row label: {words}"


def test_the_active_marker_is_visual_and_still_named(client):
    """« actif » (30 px dans une piste de 40) devient un point ambre.

    Substitution, pas soustraction (CLAUDE.md §5.3) : le nom accessible
    survit. Un span vide sans `role` ne serait annoncé par aucun lecteur
    d'écran — c'est le piège que cette assertion garde.
    """
    sid = _start(client)
    body = client.get(f"/sessions/{sid}").text
    m = re.search(r'<span class="session-focus__console-badge"[^>]*>', body)
    assert m, "active marker missing"
    tag = m.group(0)
    assert 'role="img"' in tag, tag
    assert 'aria-label="Série active"' in tag, tag

    rule = _rule(FOCUS_CSS.read_text(encoding="utf-8"),
                 ".session-focus__console-badge")
    assert "border-radius: 50%" in rule, "the marker must read as a dot"
    assert "text-transform" not in rule, "leftover text styling on a dot"


# ───────── ce qui a quitté la piste étroite y est toujours ─────────


def test_what_left_the_narrow_column_lives_in_the_annex(client):
    """§5.3 — la technique et le rappel de charge descendent, ils ne partent pas."""
    src = CARD.read_text(encoding="utf-8")
    annex = re.findall(
        r'<div class="set-row__annex">(.*?)</div>', src, re.DOTALL
    )
    assert len(annex) == 2, "both the work row and the warm-up row need an annex"
    joined = "".join(annex)
    assert 'class="tag"' in joined, "the technique tag was dropped, not moved"
    assert "session-focus__console-row-prev" in joined, (
        "the previous-load hint was dropped, not moved"
    )


def test_the_annex_spans_the_whole_row():
    """Sinon elle hérite de la piste étroite et le défaut revient intact."""
    rule = _rule(APP_CSS.read_text(encoding="utf-8"), ".set-row__annex")
    assert rule, ".set-row__annex is not styled"
    assert "grid-column: 1 / -1" in rule, rule


def test_the_annex_is_not_rendered_empty(client):
    """Un conteneur vide serait une carte de plus pour ne rien dire."""
    sid = _start(client)
    body = client.get(f"/sessions/{sid}").text
    empties = re.findall(
        r'<div class="set-row__annex">\s*</div>', body
    )
    assert empties == [], f"{len(empties)} empty annex containers rendered"


# ───────── les causes structurelles du débordement ─────────


def test_the_label_track_can_never_be_smaller_than_its_content():
    """La cause racine : `grid-template-columns: 40px …` avec 101 px dedans.

    `auto` dimensionne la piste sur son contenu. Réintroduire une largeur
    fixe recrée exactement le défaut mesuré.
    """
    rule = _rule(APP_CSS.read_text(encoding="utf-8"), ".set-row")
    assert rule, ".set-row is not styled"
    m = re.search(r"grid-template-columns:\s*([^;]+);", rule)
    assert m, rule
    first_track = m.group(1).split()[0]
    assert not re.match(r"^\d", first_track), (
        f"the label track is a fixed size again: {first_track!r}"
    )


def test_the_action_row_can_wrap_instead_of_overlapping():
    """Deux boutons sur une ligne trop courte s'imprimaient l'un sur l'autre."""
    rule = _rule(APP_CSS.read_text(encoding="utf-8"), ".card__actions--exercise")
    assert rule, ".card__actions--exercise is not styled"
    assert "flex-wrap: wrap" in rule, rule


def test_the_primary_cta_is_not_the_first_to_shrink():
    """`flex: 1` (base 0) faisait du bouton principal le premier candidat au
    rétrécissement — l'inverse exact de son rang."""
    css = APP_CSS.read_text(encoding="utf-8")
    rule = _rule(css, ".card__actions--exercise .btn--primary")
    assert rule, "primary CTA flex rule missing"
    m = re.search(r"flex:\s*([^;]+);", rule)
    assert m, rule
    assert m.group(1).strip() != "1", (
        "flex:1 means flex-basis:0 — the CTA shrinks before its neighbours"
    )
    assert "auto" in m.group(1), m.group(1)


def test_the_session_title_is_no_longer_truncated_to_one_line():
    """« Push A — Pecs épaisseur + Delts + Triceps » devenait « Push A — Pecs épa… »."""
    css = FOCUS_CSS.read_text(encoding="utf-8")
    rule = _rule(css, ".session-focus .session-focus__header-title-row .page-title")
    assert rule, "page-title rule missing"
    assert "white-space: nowrap" not in rule, rule
    m = re.search(r"[^-]line-clamp:\s*(\d+)", rule)
    assert m, rule
    assert int(m.group(1)) >= 3, (
        "measured: two lines still ended at « … + Delts… » on a 233px track"
    )


# ───────── non-régressions du périmètre ─────────


def test_the_primary_cta_stays_compact_and_names_its_destination(client):
    sid = _start(client)
    body = client.get(f"/sessions/{sid}").text
    m = re.search(
        r'<button[^>]*class="[^"]*session-focus__cta-primary[^"]*"[^>]*>(.*?)</button>',
        body, re.DOTALL,
    )
    assert m, "primary CTA not rendered"
    label = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip()
    assert re.fullmatch(r"Valider(?: · (?:fin|E\d+))?", label), label


def test_no_javascript_was_introduced():
    """A6 — la page reste entièrement server-rendered."""
    js_dir = ROOT / "app" / "static" / "js"
    assert sorted(p.name for p in js_dir.glob("*.js")) == [
        "prefs_focus_rank.js", "preview.js", "session_focus.js",
    ]
    src = CARD.read_text(encoding="utf-8")
    for marker in ("onclick=", "onchange=", "<script"):
        assert marker not in src, f"{marker!r} appeared in the exercise card"


def test_no_font_size_below_the_readable_floor():
    """Interdit explicite du sprint : pas de cache-misère par police minuscule."""
    for path in (APP_CSS, FOCUS_CSS):
        css = path.read_text(encoding="utf-8")
        for rule_name in (".set-row__code", ".set-row__annex"):
            sizes = re.findall(r"font-size:\s*(\d+)px", _rule(css, rule_name))
            for size in sizes:
                assert int(size) >= 11, f"{rule_name} in {path.name}: {size}px"


def test_no_overflow_hidden_was_used_to_mask_the_defect():
    """Interdit explicite : masquer n'est pas réparer."""
    css = APP_CSS.read_text(encoding="utf-8")
    for rule_name in (".set-row", ".set-row__label", ".set-row__annex"):
        assert "overflow: hidden" not in _rule(css, rule_name), rule_name
