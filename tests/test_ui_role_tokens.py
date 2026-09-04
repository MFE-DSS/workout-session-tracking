"""`AUREN_UI_U1_ROLE_TOKENS` — la couche de rôles, et ce qu'elle empêche.

POURQUOI CETTE GARDE EXISTE
---------------------------
Trois défauts, dont deux étaient déjà dans le dépôt et qu'aucun test ne voyait.

1. **Un emploi sans nom ne peut pas diverger.** `--t-amber` est documenté
   « action utilisateur · objet actif » : deux emplois sous un seul nom. Le jour
   où l'objet actif doit cesser de ressembler à un bouton, aucun sélecteur ne
   permet de les séparer — le CSS n'a jamais su lesquels étaient lesquels.

2. **Trois couleurs de support étaient illisibles sur le fond le plus clair.**
   Mesurées à l'époque sur `--bg` seul, elles tombaient sur L3 `--t-raised` :

       --danger #B85C5C → 3,21:1    un message d'erreur est du TEXTE
       --info   #6E8FA8 → 4,19:1
       --warn   #C77B54 → 4,35:1

   C'est le défaut `--t-blue-line` (#4A7FB5 : 4,43 sur base, **3,40 sur L3**)
   reproduit une génération plus tard. `test_uiv3_cockpit_ladder` l'avait
   attrapé pour la palette cockpit — mais il ne regarde que les 19 tokens
   `--t-*`, et ces quatre-là vivent dans la génération héritée.

3. **La garde de palette ne lisait qu'UN SEUL bloc `:root`.** `app.css` en
   déclare deux (`:root` ligne 14, et un second pour les tokens de rail).
   `_root_block()` fait un `re.search`, donc s'arrête au premier : un token de
   palette redéclaré dans le second bloc aurait été **invisible à toutes les
   mesures de contraste**. Aucune valeur n'est aujourd'hui dans ce cas — la
   garde existe pour que cela reste vrai.

Ces tests lisent le CSS, pas des pixels : ils pinnent les **causes**. La preuve
de rendu (deux captures identiques, la tranche étant additive) est produite par
le harnais et consignée au rapport, conformément à `CLAUDE.md §5.1`.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
APP_CSS = ROOT / "app" / "static" / "css" / "app.css"
HOME_CSS = ROOT / "app" / "static" / "css" / "home.css"
FOCUS_CSS = ROOT / "app" / "static" / "css" / "session_focus.css"

#: Les quatre fonds réels. Un seuil se mesure sur le PIRE, jamais sur `--t-base`.
DEPTH = ("--t-void", "--t-base", "--t-surface", "--t-raised")

#: Les rôles de surface : ils SONT les fonds, ils ne se mesurent pas contre eux.
SURFACE_ROLES = {
    "--role-surface-chassis": "--t-void",
    "--role-surface-canvas": "--t-base",
    "--role-surface-group": "--t-surface",
    "--role-surface-instrument": "--t-raised",
}

#: rôle -> seuil sur le pire fond réel.
#: 4,5 texte · 4,0 porteur de sens · 3,0 non-texte (`Sx_UIV3_04 §5`).
ROLE_THRESHOLDS = {
    "--role-text-primary": 4.5,
    "--role-text-secondary": 4.5,
    "--role-text-muted": 4.5,
    "--role-action-primary": 4.0,
    "--role-action-hover": 4.5,
    "--role-action-terminal": 4.0,
    "--role-action-dim": 3.0,
    "--role-state-active": 4.0,
    "--role-focus": 4.0,
    "--role-origin-system": 4.5,
    "--role-origin-system-data": 4.0,
    "--role-origin-system-line": 4.0,
    "--role-data-unknown": 4.0,
    "--role-glyph-decorative": 3.0,
    # Support : ils portent du TEXTE (message d'erreur, libellé de succès).
    "--role-support-success": 4.5,
    "--role-support-warning": 4.5,
    "--role-support-error": 4.5,
    "--role-support-information": 4.5,
}

#: Filets structurels — exempts du seuil de sens, pas de celui d'exister.
STRUCTURAL_ROLES = ("--role-border-subtle", "--role-border-emphasis")

#: Le couple avant-plan / arrière-plan est un contrat, pas une propriété.
ON_ACTION = ("--role-text-on-action", "--role-action-primary", 4.5)

#: Les valeurs corrigées par cette tranche, avec leur mesure sur L3.
CORRECTED = {
    "--role-support-warning": "#c97f59",
    "--role-support-error": "#c67d7d",
    "--role-support-information": "#7695ad",
}

#: Tout ce que le second bloc `:root` n'a pas le droit de redéclarer.
PALETTE = (
    "--t-void", "--t-base", "--t-surface", "--t-raised",
    "--t-line", "--t-line-strong",
    "--t-fg", "--t-fg-2", "--t-fg-muted", "--t-fg-faint",
    "--t-amber", "--t-amber-hover", "--t-amber-dim", "--t-amber-weak",
    "--t-on-amber",
    "--t-blue-fg", "--t-blue-line", "--t-blue-mid",
    "--t-unknown",
)


# ───────────────────────── outillage ─────────────────────────


def _root_blocks(css: str) -> list[str]:
    """TOUS les blocs `:root`, pas seulement le premier.

    C'est la différence avec `test_uiv3_cockpit_ladder._root_block`, et c'est
    le défaut 3 de la docstring de module.
    """
    return [
        m.group(1)
        for m in re.finditer(r"(?<![\w-]):root\s*\{(.*?)\n?\s*\}", css, re.DOTALL)
    ]


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


def _resolve(name: str, tokens: dict[str, str], seen: frozenset[str] = frozenset()) -> str:
    """Suit les `var(--x)` jusqu'à un hex. Détecte les cycles.

    Un alias non résolu rendrait la mesure vide et le test vert pour rien —
    exactement la forme de garde creuse que `guards-that-guard-nothing`
    recense.
    """
    assert name not in seen, f"cycle d'alias sur {name}"
    raw = tokens[name]
    if raw.startswith("#"):
        return raw
    m = re.fullmatch(r"var\(\s*(--[\w-]+)\s*\)", raw)
    assert m, (
        f"{name} = {raw!r} : ni hex ni alias simple. "
        "Un repli `var(--x, #hex)` est interdit par CLAUDE.md §5.4."
    )
    return _resolve(m.group(1), tokens, seen | {name})


@pytest.fixture(scope="module")
def css() -> str:
    return APP_CSS.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def tokens(css) -> dict[str, str]:
    merged: dict[str, str] = {}
    for block in _root_blocks(css):
        merged.update(_tokens_of(block))
    return merged


@pytest.fixture(scope="module")
def backgrounds(tokens) -> list[str]:
    return [_resolve(n, tokens) for n in DEPTH]


# ───────────────── la couche existe et est complète ─────────────────


def test_every_role_is_declared(tokens):
    expected = (
        set(SURFACE_ROLES)
        | set(ROLE_THRESHOLDS)
        | set(STRUCTURAL_ROLES)
        | {ON_ACTION[0]}
    )
    missing = sorted(r for r in expected if r not in tokens)
    assert missing == [], f"rôles absents de app.css : {missing}"


def test_the_outillage_actually_finds_the_roles(tokens):
    """Garde de la garde.

    Si le parseur cessait de trouver les blocs `:root`, `tokens` serait vide et
    TOUS les tests ci-dessous passeraient en boucle vide. On ancre donc un
    plancher : le défaut d'outillage doit échouer ici, pas se taire ailleurs.
    """
    roles = [n for n in tokens if n.startswith("--role-")]
    assert len(roles) >= 24, f"seulement {len(roles)} rôles lus — parseur suspect"


# ───────────────── ce que la couche empêche ─────────────────


def test_three_amber_roles_are_three_distinct_declarations(tokens):
    """`action-primary` ≠ `state-active` ≠ `focus`.

    Ils aliasent aujourd'hui la MÊME valeur, et c'est admis. Ce qui ne l'est
    pas, c'est qu'ils n'aient qu'un seul nom : des tokens distincts peuvent
    diverger, une valeur employée à trois fins ne le peut pas.
    """
    for role in ("--role-action-primary", "--role-state-active", "--role-focus"):
        assert role in tokens, role


def test_origin_system_is_never_support_information(tokens):
    """La provenance n'est pas une nature de retour (`BACKBONE §3.1`).

    `origin-system` dit « le moteur a produit ceci ». `support-information` dit
    « voici un retour sur ton opération ». Les confondre ferait lire une
    recommandation comme un message d'interface.
    """
    origin = _resolve("--role-origin-system", tokens).lower()
    info = _resolve("--role-support-information", tokens).lower()
    assert origin != info, (
        f"origin-system et support-information partagent {origin} — "
        "la distinction n'existe que sur le papier"
    )


def test_no_role_uses_a_fallback_value(tokens):
    """`var(--token-inexistant, #hex)` est interdit (`CLAUDE.md §5.4`).

    Le repli masque l'absence : la page rend juste et le token n'existe pas.
    """
    for name, raw in tokens.items():
        if not name.startswith("--role-"):
            continue
        assert "," not in raw or not raw.startswith("var("), (
            f"{name} = {raw!r} — repli interdit"
        )


# ───────────────── contrastes sur le fond RÉEL ─────────────────


@pytest.mark.parametrize("role", sorted(ROLE_THRESHOLDS))
def test_role_meets_its_threshold_on_every_real_background(
    role, tokens, backgrounds
):
    """Mesuré sur les QUATRE fonds, jamais sur `--t-base` seul.

    C'est la garde qui attrape `#B85C5C` : 4,19 sur base, **3,21 sur L3**.
    """
    value = _resolve(role, tokens)
    worst = min(_ratio(value, bg) for bg in backgrounds)
    need = ROLE_THRESHOLDS[role]
    assert worst >= need, (
        f"{role} ({value}) : pire cas {worst:.2f}:1 < {need} exigé"
    )


def test_text_on_action_is_legible_over_the_action(tokens):
    """Le contraste est un contrat de COUPLE, pas une propriété d'un token."""
    fg, bg, need = ON_ACTION
    got = _ratio(_resolve(fg, tokens), _resolve(bg, tokens))
    assert got >= need, f"{fg} sur {bg} = {got:.2f}:1 < {need}"


def test_structural_roles_stay_visible(tokens):
    """Exempts du seuil de sens, pas de celui d'exister.

    Sous 1,2:1 sur le fond le plus clair, un filet ne sépare plus rien.
    """
    raised = _resolve("--role-surface-instrument", tokens)
    for role in STRUCTURAL_ROLES:
        assert _ratio(_resolve(role, tokens), raised) >= 1.2, role


def test_surface_roles_map_onto_the_measured_ladder(tokens):
    """Les 4 niveaux produit ne sont pas une échelle neuve.

    Ce sont les 4 fonds déjà mesurés par `UIV3_COCKPIT_LADDER_01`, auxquels la
    structure produit donne un sens. Réinventer une échelle aurait produit une
    seconde profondeur, non mesurée.
    """
    for role, expected in SURFACE_ROLES.items():
        assert tokens[role] == f"var({expected})", (
            f"{role} devrait aliaser {expected}, vaut {tokens[role]!r}"
        )


def test_the_corrected_support_values_are_the_measured_ones(tokens):
    """Pin des trois valeurs corrigées.

    Elles ne sont pas décoratives : chacune remonte un contraste sous seuil, à
    teinte et saturation constantes. Les rechanger sans remesurer rouvrirait
    précisément le défaut.
    """
    for role, expected in CORRECTED.items():
        assert tokens[role].lower() == expected, (
            f"{role} = {tokens[role]} ≠ {expected} (valeur mesurée)"
        )


# ───────────────── autorité unique, TOUS blocs confondus ─────────────────


def test_no_palette_token_hides_in_a_secondary_root_block(css):
    """Défaut 3 — la garde d'origine ne lit qu'UN bloc `:root`.

    `app.css` en déclare deux. `_root_block()` de `test_uiv3_cockpit_ladder`
    fait un `re.search` : il s'arrête au premier. Un token de palette redéclaré
    dans le second aurait échappé à TOUTES les mesures de contraste.
    """
    blocks = _root_blocks(css)
    assert len(blocks) >= 2, (
        "app.css ne déclare plus qu'un bloc :root — cette garde vérifiait "
        "qu'un second ne cache rien ; si le second a disparu, la retirer "
        "explicitement plutôt que de la laisser passer à vide"
    )
    offenders = []
    for block in blocks[1:]:
        declared = _tokens_of(block)
        offenders += [
            n for n in declared
            if n in PALETTE or n.startswith("--role-")
        ]
    assert offenders == [], (
        f"second bloc :root redéclare {offenders} — invisible aux mesures"
    )


@pytest.mark.parametrize("sheet", (HOME_CSS, FOCUS_CSS))
def test_no_stylesheet_redeclares_a_role(sheet):
    """Une seconde autorité ferait diverger deux surfaces en silence."""
    css = re.sub(r"/\*.*?\*/", "", sheet.read_text(encoding="utf-8"), flags=re.DOTALL)
    redeclared = sorted(set(re.findall(r"(--role-[\w-]+)\s*:", css)))
    assert redeclared == [], f"{sheet.name} redéclare {redeclared}"


# ───────────────── périmètre de la tranche ─────────────────


def test_the_role_layer_rewires_no_consumer():
    """**Tier T5 — cette garde EXPIRE quand `U2` migre les consommateurs.**

    Elle prouve la propriété qui rend `U1` sûre : la tranche ajoute des noms et
    ne déplace pas un pixel. Le rendu identique avant/après n'est pas une
    espérance, c'est une conséquence vérifiable.

    Le jour où `U2` fait consommer ces rôles, cette garde tombe — **le jour où
    la spec la remplace, pas avant** (`AUREN_UIUX_V3_GUARD_MIGRATION_REGISTER`,
    même procédure que `test_no_new_token_consumer_outside_the_approved_scope`).
    """
    consumers = []
    for sheet in (APP_CSS, HOME_CSS, FOCUS_CSS):
        css = re.sub(
            r"/\*.*?\*/", "", sheet.read_text(encoding="utf-8"), flags=re.DOTALL
        )
        # une déclaration `--role-x: …` n'est pas une consommation
        css = re.sub(r"--role-[\w-]+\s*:\s*[^;]+;", "", css)
        consumers += [
            f"{sheet.name}:{m}" for m in re.findall(r"var\(\s*(--role-[\w-]+)", css)
        ]
    assert consumers == [], (
        f"`U1` est censée être inerte, or ces rôles sont consommés : {consumers}"
    )
