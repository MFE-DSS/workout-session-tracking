"""`AUREN_UI_U3_SESSION` — la séance était restée sur l'ancienne échelle.

POURQUOI CETTE GARDE EXISTE
---------------------------
Trois défauts, tous invisibles au dépôt, tous sur la **surface souveraine**.

1. **La correction de profondeur n'a jamais atteint la séance.**
   `UIV3_COCKPIT_LADDER_01` a corrigé l'échelle dans `app.css` — L2 de
   `#151A21` à `#191F27`, L3 à `#232B36`, marches mesurées **1,124** et
   **1,161**. `session_focus.css` déclarait ses PROPRES valeurs, restées aux
   anciennes : marches **1,067** et **1,070**, sous le plancher de **1,120**
   que le dépôt s'est fixé.

   `test_session_css_still_declares_no_palette_token` ne l'a pas vu, et il
   avait raison de ne pas le voir : il vérifie que `--t-*` n'est pas
   redéclaré. La divergence passait par une **génération `--color-*`
   entière**, juste à côté. Une garde qui protège une famille de tokens
   pendant qu'une famille parallèle fait le dégât ne garde rien.

2. **L'élévation était inversée.** La carte ACTIVE prenait `#151A21` et les
   cartes EN ATTENTE `#1B2029`, **plus clair**. Les exercices qu'on ne fait
   pas flottaient au-dessus de celui qu'on fait — l'inverse exact de `Q2=A`,
   où l'élévation encode la volatilité.

3. **`--shadow-sm` et `--shadow-md` valaient `none`** alors que trois règles
   écrivent `box-shadow: var(--shadow-sm)`, dont l'en-tête collant et la barre
   collante, qui doivent se détacher du contenu défilant dessous. Une
   déclaration qui se lit comme une intention et rend zéro est pire qu'une
   absence : personne ne la cherche.

Ces tests lisent le CSS et **résolvent les alias jusqu'à la valeur**. Une
garde qui s'arrêterait au nom du token laisserait repasser exactement le
défaut 1.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
APP_CSS = ROOT / "app" / "static" / "css" / "app.css"
FOCUS_CSS = ROOT / "app" / "static" / "css" / "session_focus.css"

#: Plancher de perception que le dépôt s'est fixé (`Sx_UIV3_04`).
PERCEPTION_FLOOR = 1.12

#: Tokens de surface de la séance qui doivent être des ALIAS, jamais des valeurs.
SESSION_SURFACES = (
    "--color-bg-base",
    "--color-bg-elevated",
    "--color-surface",
    "--color-surface-alt",
    "--color-surface-sunken",
    "--color-border-subtle",
    "--color-border-default",
    "--color-border-strong",
    "--shadow-sm",
    "--shadow-md",
)


def _strip(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)


def _declarations(css: str, scope: str) -> dict[str, str]:
    """Déclarations d'un bloc de scope donné (`:root`, `.session-focus`)."""
    m = re.search(rf"(?<![\w-]){re.escape(scope)}\s*\{{(.*?)\n\}}", css, re.DOTALL)
    assert m, f"bloc {scope} introuvable"
    return {
        d.group(1): d.group(2).strip()
        for d in re.finditer(r"(--[\w-]+)\s*:\s*([^;]+);", m.group(1))
    }


@pytest.fixture(scope="module")
def app_tokens() -> dict[str, str]:
    return _declarations(_strip(APP_CSS.read_text(encoding="utf-8")), ":root")


@pytest.fixture(scope="module")
def session_tokens() -> dict[str, str]:
    return _declarations(_strip(FOCUS_CSS.read_text(encoding="utf-8")), ".session-focus")


def _resolve(value: str, tables: tuple[dict[str, str], ...], depth: int = 0) -> str:
    """Suit les `var(--x)` jusqu'à une valeur concrète.

    S'arrêter au nom du token est précisément ce qui a laissé passer le
    défaut 1 : `--color-surface` avait le bon NOM et la mauvaise VALEUR.
    """
    assert depth < 10, f"alias trop profond : {value}"
    m = re.fullmatch(r"var\(\s*(--[\w-]+)\s*\)", value.strip())
    if not m:
        return value.strip()
    name = m.group(1)
    for table in tables:
        if name in table:
            return _resolve(table[name], tables, depth + 1)
    raise AssertionError(f"{name} n'est déclaré nulle part — var() sans repli")


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


# ───────────────── autorité unique, TOUTES générations ─────────────────


@pytest.mark.parametrize("token", SESSION_SURFACES)
def test_session_surface_tokens_are_aliases_not_values(token, session_tokens):
    """Défaut 1 — une génération parallèle est une seconde autorité.

    Peu importe qu'elle s'appelle `--color-*` plutôt que `--t-*` : si elle
    porte des VALEURS, la séance peut diverger de l'échelle sans qu'aucune
    garde de palette ne bronche. C'est arrivé, et pendant des mois.
    """
    value = session_tokens[token]
    assert value.startswith("var(--"), (
        f"{token} = {value!r} — valeur propre, donc seconde autorité. "
        "La séance a déjà dérivé de l'échelle mesurée par ce chemin."
    )
    assert "," not in value, f"{token} = {value!r} — repli interdit (§5.4)"


def test_the_session_ladder_is_the_measured_one(app_tokens, session_tokens):
    """Les marches de la séance, RÉSOLUES, franchissent le plancher.

    C'est la garde qui aurait attrapé 1,067 et 1,070 : elle ne regarde pas
    les noms, elle résout jusqu'à la valeur et mesure.
    """
    tables = (session_tokens, app_tokens)
    rungs = [
        _resolve(session_tokens[n], tables)
        for n in ("--color-bg-base", "--color-bg-elevated", "--color-surface")
    ]
    for i in range(len(rungs) - 1):
        step = _ratio(rungs[i], rungs[i + 1])
        assert step >= PERCEPTION_FLOOR, (
            f"marche {rungs[i]}→{rungs[i+1]} = {step:.3f} < {PERCEPTION_FLOOR}. "
            "La séance est repartie sur une échelle non perceptible."
        )


def test_the_active_card_sits_above_the_pending_ones(app_tokens, session_tokens):
    """Défaut 2 — l'élévation encode la volatilité (`Q2=A`).

    La carte active doit être PLUS CLAIRE que les cartes en attente. Elle
    était plus sombre : les exercices qu'on ne fait pas flottaient au-dessus
    de celui qu'on fait, et rien ne le signalait.
    """
    tables = (session_tokens, app_tokens)
    active = _resolve(session_tokens["--color-surface"], tables)
    pending = _resolve(session_tokens["--color-bg-elevated"], tables)
    assert _lum(active) > _lum(pending), (
        f"actif {active} n'est pas au-dessus de l'attente {pending} — "
        "élévation inversée"
    )


def test_the_well_is_the_deepest(app_tokens, session_tokens):
    """Le puits est sous le champ : c'est ce dans quoi on saisit."""
    tables = (session_tokens, app_tokens)
    well = _resolve(session_tokens["--color-surface-sunken"], tables)
    field = _resolve(session_tokens["--color-bg-base"], tables)
    assert _lum(well) < _lum(field), f"puits {well} pas plus creux que {field}"


# ───────────────── ce qui rendait zéro ─────────────────


@pytest.mark.parametrize("token", ("--shadow-sm", "--shadow-md"))
def test_shadows_are_no_longer_neutralised(token, app_tokens, session_tokens):
    """Défaut 3 — `none` sur un token que trois règles consomment.

    L'en-tête collant et la barre collante doivent se détacher du contenu qui
    défile dessous. Ils écrivaient `box-shadow: var(--shadow-sm)` et rendaient
    `none` : l'intention était dans le code, l'effet nulle part.
    """
    resolved = _resolve(session_tokens[token], (session_tokens, app_tokens))
    assert resolved != "none", (
        f"{token} vaut `none` — les règles qui le consomment ne rendent rien"
    )
    assert "inset" in resolved or "px" in resolved, resolved


def test_the_shadow_consumers_still_exist():
    """Garde de la garde.

    Si plus personne ne consommait `--shadow-sm`, la garde ci-dessus
    protégerait un token mort et passerait à vide.
    """
    css = _strip(FOCUS_CSS.read_text(encoding="utf-8"))
    consumers = re.findall(r"box-shadow:\s*var\(--shadow-(?:sm|md)\)", css)
    assert len(consumers) >= 3, f"{len(consumers)} consommateurs — garde à vide ?"


# ───────────────── le grain, sans seconde autorité ─────────────────


def test_the_session_declares_no_grain_density_of_its_own():
    """Les densités viennent d'`app.css`.

    Les redéclarer ici recréerait exactement la divergence que cette tranche
    ferme — une feuille qui décide seule de ce que la profondeur vaut.
    """
    css = _strip(FOCUS_CSS.read_text(encoding="utf-8"))
    local = sorted(set(re.findall(r"(--grain-[\w-]+|--texture-grain)\s*:", css)))
    assert local == [], f"session_focus.css redéclare {local}"


def test_the_session_grain_passes_through_the_multiplier():
    """Une opacité écrite en dur échapperait à `prefers-contrast: more`."""
    css = _strip(FOCUS_CSS.read_text(encoding="utf-8"))
    layers = re.findall(
        r"\.session-focus(?:__cockpit[^{]*)?::(?:before|after)\s*\{([^}]*)\}", css
    )
    decl = re.compile(r"(?:^|;)\s*opacity\s*:")
    for body in (b for b in layers if decl.search(b)):
        assert "var(--texture-grain)" in body, body.strip()


def test_the_session_levels_do_not_clip_their_sticky_children():
    """`overflow: hidden` rognerait l'en-tête et la barre collants.

    Les deux sont `position: sticky` dans cette page. Le clip du grain passe
    par `border-radius: inherit` sur la surcouche.
    """
    css = _strip(FOCUS_CSS.read_text(encoding="utf-8"))
    m = re.search(
        r"\.session-focus,\s*\n\.session-focus__cockpit \.session-focus__card\s*\{([^}]*)\}",
        css,
    )
    assert m, "bloc de positionnement du grain introuvable"
    assert "overflow" not in m.group(1), m.group(1)
