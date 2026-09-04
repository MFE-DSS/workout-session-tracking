"""`AUREN_UI_U2_CHASSIS` — le relief, et ce qu'il remplace.

POURQUOI CETTE GARDE EXISTE
---------------------------
`Q1=C` demandait « le fond dit où on est, le délimiteur dit qu'on change ».
**La moitié « fond » était vide, et c'est mesurable** :

* L1 est la référence et ne bouge pas ;
* L3 est PLAFONNÉ — `support-error` (#C67D7D) y vaut 4,51 pour un seuil de 4,5,
  soit **0,01 de marge**. Monter L3 d'un cran rend un message d'erreur illisible ;
* L0 poussé au noir pur ne gagne que 1,065 → 1,127.

La plage de luminance est **épuisée**. Le relief n'assiste donc pas le
contraste : il fait le travail que le contraste ne peut plus faire. Une tranche
future qui « creuserait un peu les fonds » casserait un seuil sans le voir —
d'où `test_the_ladder_has_no_headroom_left`, qui échoue le jour où quelqu'un
essaie.

LE MODÈLE, CORRIGÉ PAR LE CODE
------------------------------
`--t-void` (L0) n'a qu'**un seul** consommateur dans tout le produit : le fond
du champ de saisie d'une série. Ce n'est pas un sol de cockpit, c'est un
**puits**. Le modèle réel n'est donc pas une échelle à quatre degrés mais
**trois élévations et un creux**, le creux étant orthogonal — taillé dans le
niveau où il se trouve, jamais un cinquième degré.

L'élévation encode la **volatilité** (`Q2=A`) :
champ = ne change jamais · logement = entre deux séances · plaque = pendant.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
APP_CSS = ROOT / "app" / "static" / "css" / "app.css"

LEVELS = (".lvl-field", ".lvl-housing", ".lvl-plate", ".lvl-well")

#: Les avant-plans les plus serrés sur L3, avec leur seuil.
#: Ce sont eux qui PLAFONNENT l'échelle.
TIGHT_ON_L3 = {
    "#C67D7D": 4.5,   # support-error
    "#C97F59": 4.5,   # support-warning
    "#7695AD": 4.5,   # support-information
    "#6E9E7A": 4.5,   # support-success
    "#8A94A0": 4.5,   # text-muted
}


def _media_spans(css: str) -> list[tuple[int, int]]:
    """Étendue de chaque bloc `@media`, accolades appariées.

    Une regex ne peut pas apparier des accolades ; s'en remettre à elle ferait
    passer un `:root` conditionnel pour un `:root` de base.
    """
    spans = []
    for m in re.finditer(r"@media[^{]*\{", css):
        depth, i = 1, m.end()
        while i < len(css) and depth:
            if css[i] == "{":
                depth += 1
            elif css[i] == "}":
                depth -= 1
            i += 1
        spans.append((m.start(), i))
    return spans


def _root_blocks(css: str, *, conditional: bool = False) -> list[str]:
    """Blocs `:root`, en séparant les DÉFAUTS des SURCHARGES conditionnelles.

    Fusionner les deux est un défaut réel : le `:root` de
    `@media (prefers-contrast: more)` met `--texture-grain` à 0, et une lecture
    naïve conclurait que le grain est désarmé par défaut. La garde dirait alors
    l'inverse de ce que voit un utilisateur ordinaire.
    """
    spans = _media_spans(css)

    def inside(pos: int) -> bool:
        return any(a <= pos < b for a, b in spans)

    return [
        m.group(1)
        for m in re.finditer(r"(?<![\w-]):root\s*\{(.*?)\n?\s*\}", css, re.DOTALL)
        if inside(m.start()) is conditional
    ]


def _lum(hex_colour: str) -> float:
    h = hex_colour.lstrip("#")
    total = 0.0
    for pair, weight in zip((h[0:2], h[2:4], h[4:6]), (0.2126, 0.7152, 0.0722)):
        c = int(pair, 16) / 255
        c = c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        total += c * weight
    return total


def _ratio(a: str, b: str) -> float:
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


@pytest.fixture(scope="module")
def css() -> str:
    return APP_CSS.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def tokens(css) -> dict[str, str]:
    merged: dict[str, str] = {}
    for block in _root_blocks(css):
        for m in re.finditer(r"(--[\w-]+)\s*:\s*([^;]+);", block):
            merged[m.group(1)] = m.group(2).strip()
    return merged


@pytest.fixture(scope="module")
def rules(css) -> dict[str, str]:
    stripped = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    out = {}
    for m in re.finditer(r"([^{}]+)\{([^}]*)\}", stripped):
        out[m.group(1).strip()] = m.group(2)
    return out


# ───────────────── le relief existe et porte un SENS ─────────────────


def test_the_four_levels_are_declared(rules):
    missing = [lvl for lvl in LEVELS if lvl not in rules]
    assert missing == [], f"niveaux absents : {missing}"


def test_raised_and_carved_are_opposite(tokens):
    """La dichotomie tient à l'ORDRE des deux traits, pas à leur existence.

    Un relief surélevé pose la lumière EN HAUT à l'intérieur et l'ombre à
    l'extérieur. Un relief creusé fait l'inverse : l'ombre tombe à l'intérieur.
    Si les deux valeurs devenaient identiques, la dichotomie disparaîtrait sans
    qu'aucun autre test ne bronche — l'écran resterait « en relief » partout.
    """
    raised = tokens["--relief-raised"]
    carved = tokens["--relief-carved"]
    assert raised != carved, "surélevé et creusé rendent le même relief"
    # le creusé pose l'OMBRE à l'intérieur ; le surélevé y pose la LUMIÈRE
    assert "inset 0 1px 2px var(--role-edge-shadow)" in carved, carved
    assert "inset 0 1px 0 var(--role-edge-lit)" in raised, raised


def test_the_well_is_carved_and_the_plate_is_raised(rules):
    """Le puits est creusé DANS son parent — il n'est pas un 5e fond.

    C'est la correction que le code a imposée : `--t-void` n'a qu'un seul
    consommateur réel, le champ de saisie d'une série. Un puits qui recevrait
    `--relief-raised` redeviendrait un degré d'empilement, et le modèle
    « trois élévations + un creux » s'effondrerait en silence.
    """
    assert "var(--relief-carved)" in rules[".lvl-well"]
    assert "var(--relief-raised)" in rules[".lvl-plate"]
    assert "var(--relief-carved)" not in rules[".lvl-plate"]


def test_the_field_carries_no_relief(rules):
    """On ne surélève pas le sol : on pose dessus.

    Donner un relief au champ ferait de chaque page une plaque flottante au
    dessus de rien, et la marche L1→L2 cesserait de vouloir dire quoi que ce
    soit.
    """
    assert "box-shadow" not in rules[".lvl-field"], rules[".lvl-field"]


def test_live_is_a_state_not_a_level(rules):
    """`state-active` ne déplace aucun fond (`BACKBONE §2`).

    Le 4e niveau produit — « en vol » — n'est pas un 5e fond : c'est un état
    posé sur un niveau. S'il changeait `background`, il inventerait une
    profondeur de plus, non mesurée.
    """
    live = rules[".lvl-plate.is-live"]
    assert "background" not in live, live
    assert "--role-state-active" in live


# ───────────────── ce que la mesure interdit ─────────────────


def test_the_ladder_has_no_headroom_left(tokens):
    """**L3 est plafonné par les couleurs de support, à 0,01 près.**

    Cette garde existe pour une tranche future qui voudrait « creuser un peu
    les fonds » pour mieux séparer les niveaux. C'est impossible sans casser un
    message d'erreur, et l'échec doit le dire ICI plutôt que de laisser
    quelqu'un le découvrir en production.
    """
    l3 = tokens["--t-raised"]
    for value, need in TIGHT_ON_L3.items():
        got = _ratio(value, l3)
        assert got >= need, (
            f"{value} sur L3 ({l3}) = {got:.2f}:1 < {need}. "
            "L3 a été éclairci : la plage de luminance était déjà épuisée, "
            "c'est au RELIEF de séparer les niveaux, pas au fond."
        )


def test_edges_are_alpha_not_hex(tokens):
    """Une arête doit fonctionner sur les quatre fonds sans être remesurée.

    Un hex fixe la rendrait juste sur un fond et fausse sur les trois autres —
    et comme elle ne porte pas de texte, aucun seuil de contraste ne viendrait
    le signaler.
    """
    for name in ("--role-edge-lit", "--role-edge-shadow"):
        assert tokens[name].startswith("rgba("), f"{name} = {tokens[name]}"


def test_the_grain_token_actually_commands_the_grain(css, tokens):
    """Remplace `test_grain_is_declared_but_disarmed` — `Q3=A` est tranché.

    L'ancienne garde prouvait que la texture ne partait pas avant arbitrage.
    L'opérateur a tranché sur rendu le 2026-09-04 ; elle tombe **par la spec**.

    Ce qui la remplace protège l'invariant qui ne périme pas : **le token doit
    RÉELLEMENT commander**. Un `--texture-grain` déclaré à côté d'opacités
    écrites en dur serait une variable décorative — on croirait pouvoir
    éteindre le grain, et `prefers-contrast: more` ne l'éteindrait pas.
    C'est la forme de garde creuse que ce dépôt a déjà payée trois fois.
    """
    assert tokens["--texture-grain"] == "1", tokens["--texture-grain"]
    stripped = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    layers = re.findall(
        r"\.lvl-(?:field|housing|plate)::(?:before|after)\s*\{([^}]*)\}", stripped
    )
    # `opacity` en DÉCLARATION, pas en sous-chaîne : le data-URI du bruit
    # contient `opacity='.5'` dans son SVG et serait compté comme une couche.
    decl = re.compile(r"(?:^|;)\s*opacity\s*:")
    opacities = [b for b in layers if decl.search(b)]
    assert len(opacities) == 6, f"6 couches attendues, {len(opacities)} trouvées"
    for body in opacities:
        assert "var(--texture-grain)" in body, (
            f"opacité écrite hors du multiplicateur : {body.strip()}"
        )


def test_grain_density_decreases_with_elevation(tokens):
    """`Q3=A` : ce qui est proche est net.

    Si l'ordre s'inversait, la texture cesserait d'encoder la profondeur — et
    comme elle resterait « jolie », rien ne le signalerait.
    """
    field = float(tokens["--grain-field"])
    housing = float(tokens["--grain-housing"])
    plate = float(tokens["--grain-plate"])
    assert field > housing > plate, (
        f"densités non décroissantes : champ {field} · logement {housing} "
        f"· plaque {plate}"
    )


def test_grain_is_disarmed_under_prefers_contrast(css):
    """Le grain réduit le contraste : il s'éteint quand on en demande plus.

    ⚠ `prefers-reduced-motion` ne s'applique PAS ici — le grain est statique.
    L'invoquer serait un alibi d'accessibilité, pas une mesure.
    """
    stripped = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    m = re.search(
        r"@media\s*\(\s*prefers-contrast\s*:\s*more\s*\)\s*\{(.*?)\n\}",
        stripped, re.DOTALL,
    )
    assert m, "aucun bloc `prefers-contrast: more`"
    assert re.search(r"--texture-grain\s*:\s*0", m.group(1)), m.group(1)


def test_content_sits_above_the_grain(css):
    """Le texte passe au-dessus des scanlines.

    Sans empilement explicite, la contrainte de premier rang — « le texte doit
    rester très simple et lisible » — serait perdue par un défaut de z-index,
    pas par un choix.
    """
    stripped = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    m = re.search(
        r"\.lvl-field\s*>\s*\*,\s*\.lvl-housing\s*>\s*\*,\s*\.lvl-plate\s*>\s*\*\s*\{([^}]*)\}",
        stripped, re.DOTALL,
    )
    assert m, "le contenu des niveaux n'est pas empilé au-dessus du grain"
    assert "z-index: 1" in m.group(1), m.group(1)


def test_levels_do_not_clip_their_children(css):
    """`overflow: hidden` sur un niveau rognerait un enfant `sticky`.

    Le CTA collant du mode séance en est un. Le clip du grain passe par
    `border-radius: inherit` sur la surcouche, pas par un `overflow`.
    """
    stripped = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    for m in re.finditer(r"(\.lvl-[^{}]*)\{([^}]*)\}", stripped):
        selector, body = m.group(1).strip(), m.group(2)
        if "::before" in selector or "::after" in selector or ">" in selector:
            continue
        assert "overflow" not in body, f"{selector} rogne ses enfants : {body.strip()}"


def test_the_primitive_is_not_applied_yet(css):
    """`U2` construit et EXPOSE ; elle n'applique pas.

    Tier T5 — expire quand `U3` applique le châssis à la séance. L'application
    surface par surface exige sa propre exposition (`§5.1`), et les grouper
    ferait juger d'un coup ce qui doit l'être une surface à la fois.
    """
    templates = (ROOT / "app" / "templates").rglob("*.html")
    users = []
    for tpl in templates:
        text = tpl.read_text(encoding="utf-8")
        users += [f"{tpl.name}:{lvl}" for lvl in LEVELS if lvl.lstrip(".") in text]
    assert users == [], f"la primitive est déjà appliquée : {users}"
