"""`UIV3_COCKPIT_LADDER_01` (B0) — la palette cockpit a une autorité unique.

POURQUOI CETTE GARDE EXISTE
---------------------------
Deux défauts, tous deux invisibles au dépôt jusqu'à ce qu'on les mesure :

1. **La palette n'était atteignable que depuis la Home.** Les tokens `--t-*`
   étaient déclarés sous `.today-home` ; `app.css` et `session_focus.css` en
   comptaient **zéro occurrence**. La convergence Home × Session exigée par
   `Sx_UIV3_04 §14` — même profondeur, même chromie sur les deux surfaces —
   était littéralement impossible à écrire.

2. **Les contrastes étaient documentés sur `--t-base` seul.** Un token bleu
   « validé » de cette façon (#4A7FB5, 4,43:1 sur base) tombait à **3,40:1**
   sur `--t-raised`, sous la cible AUREN de 4:1. C'est l'erreur que
   `CLAUDE.md §5.4` interdit, commise un étage au-dessus.

Ces tests lisent le CSS, pas des pixels : ils pinnent les **causes**. La
preuve navigateur (tokens calculés identiques depuis les deux documents,
absence de régression horizontale) est produite par le harnais de rendu et
consignée dans le rapport de tranche, conformément à `CLAUDE.md §5.1`.

Tier : **T2** pour les seuils de contraste, **T4** pour les valeurs.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
APP_CSS = ROOT / "app" / "static" / "css" / "app.css"
HOME_CSS = ROOT / "app" / "static" / "css" / "home.css"
FOCUS_CSS = ROOT / "app" / "static" / "css" / "session_focus.css"

#: Les 19 tokens de la palette cockpit (`Sx_UIV3_04 §1bis C8`).
PALETTE = (
    "--t-void", "--t-base", "--t-surface", "--t-raised",
    "--t-line", "--t-line-strong",
    "--t-fg", "--t-fg-2", "--t-fg-muted", "--t-fg-faint",
    "--t-amber", "--t-amber-hover", "--t-amber-dim", "--t-amber-weak",
    "--t-on-amber",
    "--t-blue-fg", "--t-blue-line", "--t-blue-mid",
    "--t-unknown",
)

DEPTH = ("--t-void", "--t-base", "--t-surface", "--t-raised")

#: token -> seuil applicable sur le PIRE fond réel.
#: 4,5 texte · 4,0 filet porteur de sens (`Sx_UIV3_04 §5`) · 3,0 non-texte.
THRESHOLDS = {
    "--t-fg": 4.5, "--t-fg-2": 4.5, "--t-fg-muted": 4.5,
    "--t-amber-hover": 4.5, "--t-blue-fg": 4.5,
    "--t-amber": 4.0, "--t-blue-mid": 4.0, "--t-blue-line": 4.0,
    "--t-unknown": 4.0,
    "--t-fg-faint": 3.0, "--t-amber-dim": 3.0,
}

#: `--t-line*` sont STRUCTURELS : ils séparent, ils n'affirment rien.
#: Les soumettre au seuil des porteurs de sens reviendrait à exiger d'une
#: gouttière qu'elle soit lisible.
STRUCTURAL_EXEMPT = ("--t-line", "--t-line-strong")


# ───────────────────────── outillage ─────────────────────────


def _root_block() -> str:
    css = APP_CSS.read_text(encoding="utf-8")
    m = re.search(r":root\s*\{(.*?)\n\}", css, re.DOTALL)
    assert m, "app.css has no :root block"
    return m.group(1)


def _tokens_of(block: str) -> dict[str, str]:
    return {
        m.group(1): m.group(2).strip()
        for m in re.finditer(r"(--[\w-]+)\s*:\s*([^;]+);", block)
    }


def _relative_luminance(hex_colour: str) -> float:
    h = hex_colour.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    total = 0.0
    for pair, weight in zip((h[0:2], h[2:4], h[4:6]), (0.2126, 0.7152, 0.0722)):
        c = int(pair, 16) / 255
        c = c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        total += c * weight
    return total


def _ratio(a: str, b: str) -> float:
    la, lb = _relative_luminance(a), _relative_luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


@pytest.fixture(scope="module")
def tokens() -> dict[str, str]:
    return _tokens_of(_root_block())


@pytest.fixture(scope="module")
def backgrounds(tokens) -> list[str]:
    """Les quatre fonds L0–L3 réellement déclarés."""
    return [tokens[name] for name in DEPTH]


# ───────────────── autorité unique ─────────────────


def test_the_whole_palette_is_declared_on_root(tokens):
    missing = [name for name in PALETTE if name not in tokens]
    assert missing == [], f"absents de app.css :root : {missing}"


def test_home_css_no_longer_declares_the_palette():
    """La régression exacte à empêcher : une seconde autorité.

    Redéclarer un seul de ces tokens sous `.today-home` fait diverger la Home
    de la Session sans qu'aucun autre test ne bronche.
    """
    css = HOME_CSS.read_text(encoding="utf-8")
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    redeclared = [
        name for name in PALETTE
        if re.search(rf"{re.escape(name)}\s*:", css)
    ]
    assert redeclared == [], (
        f"home.css redéclare {redeclared} — seconde autorité de token"
    )


def test_the_palette_is_reachable_from_every_surface(tokens):
    """`:root` est le seul scope que la Home ET la Session atteignent.

    Avant B0, la palette vivait sous `.today-home` : la console de séance ne
    pouvait pas la lire, et la convergence n'était qu'une intention.
    """
    block = _root_block()
    for name in DEPTH:
        assert re.search(rf"{re.escape(name)}\s*:", block), name


# ───────────────── escalier de profondeur ─────────────────


def test_adjacent_depth_steps_are_perceptible(backgrounds):
    """L1→L2 et L2→L3 ≥ 1,12:1.

    L'ancien escalier valait 1,051 / 1,067 / 1,070 : une profondeur déclarée
    par des tokens distincts et jamais rendue à l'œil.
    """
    for i in (1, 2):
        step = _ratio(backgrounds[i], backgrounds[i + 1])
        assert step >= 1.12, (
            f"L{i}→L{i+1} = {step:.3f}:1 — sous le plancher de perception"
        )


def test_the_depth_ladder_is_monotonic(backgrounds):
    lums = [_relative_luminance(b) for b in backgrounds]
    assert lums == sorted(lums), f"escalier non monotone : {backgrounds}"


# ───────────────── contrastes sur le fond RÉEL ─────────────────


@pytest.mark.parametrize("token", sorted(THRESHOLDS))
def test_token_meets_its_threshold_on_every_real_background(
    token, tokens, backgrounds
):
    """Mesuré sur les QUATRE fonds, pas sur `--t-base` seul.

    C'est la garde qui aurait attrapé `--t-blue-line: #4A7FB5` : conforme sur
    base (4,43) et fautif sur L3 (3,40).
    """
    value = tokens[token]
    assert value.startswith("#"), f"{token} n'est pas un hex : {value}"
    worst = min(_ratio(value, bg) for bg in backgrounds)
    need = THRESHOLDS[token]
    assert worst >= need, (
        f"{token} ({value}) : pire cas {worst:.2f}:1 < {need} exigé"
    )


def test_structural_lines_are_exempt_and_stay_structural(tokens):
    """Un filet structurel ne porte pas de sens — mais il doit rester visible.

    Exempt du seuil 4:1, il n'est pas exempt d'exister : sous 1,2:1 sur le
    fond le plus clair, il ne sépare plus rien.
    """
    raised = tokens["--t-raised"]
    for name in STRUCTURAL_EXEMPT:
        assert _ratio(tokens[name], raised) >= 1.2, name


def test_on_amber_is_legible_over_amber(tokens):
    assert _ratio(tokens["--t-on-amber"], tokens["--t-amber"]) >= 4.5


# ───────────────── valeurs approuvées ─────────────────


def test_the_corrected_values_are_the_approved_ones(tokens):
    """`Sx_UIV3_04 §1bis` C6 et C7 — valeurs tranchées par l'opérateur."""
    assert tokens["--t-blue-line"].lower() == "#5a93c9"
    assert tokens["--t-unknown"].lower() == "#828e9e"
    assert tokens["--t-base"].lower() == "#0f1318", "L1 est la référence"


def test_faint_is_no_longer_a_body_text_token():
    """D — `--t-fg-faint` ne peut plus porter de texte.

    Il reste légitime sur des glyphes décoratifs (`content: "· "`), d'où la
    vérification ciblée sur les règles de COULEUR DE TEXTE et non sur toute
    occurrence du token.
    """
    css = HOME_CSS.read_text(encoding="utf-8")
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    offenders = []
    for m in re.finditer(r"([^{}]+)\{([^}]*)\}", css):
        selector, body = m.group(1).strip(), m.group(2)
        if "--t-fg-faint" not in body:
            continue
        if "content:" in body or "::before" in selector or "::after" in selector:
            continue  # glyphe décoratif — non-texte
        if re.search(r"(?<!-)\bcolor\s*:\s*var\(--t-fg-faint\)", body):
            offenders.append(selector.splitlines()[-1].strip())
    assert offenders == [], (
        f"--t-fg-faint porte encore du texte : {offenders}"
    )


# ───────────────── périmètre de la tranche ─────────────────


def test_no_new_token_consumer_outside_the_approved_scope():
    """Preuve 5 — B0 DÉCLARE la palette, elle ne la consomme nulle part de neuf.

    Les tokens introduits par cette tranche (`--t-blue-*`, `--t-unknown`) ne
    doivent avoir AUCUN consommateur : les câbler serait commencer le
    redesign, ce que le périmètre interdit explicitement.
    """
    introduced = ("--t-blue-fg", "--t-blue-line", "--t-blue-mid", "--t-unknown")
    consumers = []
    for path in (APP_CSS, HOME_CSS, FOCUS_CSS):
        css = path.read_text(encoding="utf-8")
        css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
        for name in introduced:
            if f"var({name}" in css:
                consumers.append(f"{path.name}: var({name})")
    assert consumers == [], f"consommateurs prématurés : {consumers}"


def test_session_css_still_declares_no_palette_token():
    """`session_focus.css` consomme `:root`, il ne redéclare rien."""
    css = FOCUS_CSS.read_text(encoding="utf-8")
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    redeclared = [n for n in PALETTE if re.search(rf"{re.escape(n)}\s*:", css)]
    assert redeclared == [], redeclared
