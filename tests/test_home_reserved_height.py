"""Une hauteur réservée produit du vide, et une correction scopée se perd.

POURQUOI CETTE GARDE EXISTE
---------------------------
`Sx_UIV3_01 Q5` a retiré le `min-height` du hero de l'accueil. Sa prose, dans
`home.css`, dit exactement ceci :

    « Il réservait `min-height: 44vh` et n'en remplissait pas les trois
      quarts : mesuré à 390 × 844, 422 px dont 115 vides […] Plus de
      `min-height`. »

**La règle de base a bien été corrigée. La règle MOBILE, non.** Et c'est la
seule qui s'applique à la cible que la prose cite : à 390 px de large,
`@media (max-width: 400px) { min-height: 50vh }` vaut exactement 422 px.

Deux conséquences, mesurées au navigateur le 2026-09-05 :

* la correction n'a jamais atteint le viewport qu'elle nommait ;
* **le vide avait AUGMENTÉ** — 50vh > 44vh — de 115 à **152 px**, soit 36 %
  du bloc.

Après retrait : hero 422 → 288 px, vide 152 → 18 px (le seul padding), page
1,87 → 1,71 écrans.

C'est la deuxième fois que ce dépôt voit un bloc scopé conserver en silence ce
que la règle universelle a retiré — un `@media (prefers-reduced-motion)`
désarmait déjà une garde universelle. **Le motif compte plus que le cas :
une garde qui ne lit que les règles de premier niveau ne garde rien.**
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

CSS = Path(__file__).resolve().parent.parent / "app" / "static" / "css" / "home.css"

#: Blocs dont aucune déclaration ne doit réserver de hauteur.
#: Le hero est le seul aujourd'hui ; la liste existe pour que l'ajout d'un
#: second soit un geste, pas un oubli.
NO_RESERVED_HEIGHT = (".today-home__hero",)


def _media_spans(css: str) -> list[tuple[int, int]]:
    """Étendue de chaque `@media`, accolades appariées.

    Une regex ne peut pas apparier des accolades ; s'en remettre à elle
    ferait exactement l'erreur que cette garde existe pour empêcher.
    """
    spans = []
    for m in re.finditer(r"@media[^{]*\{", css):
        depth, i = 1, m.end()
        while i < len(css) and depth:
            depth += {"{": 1, "}": -1}.get(css[i], 0)
            i += 1
        spans.append((m.start(), i))
    return spans


def _rules_for(css: str, selector: str) -> list[tuple[str, str, bool]]:
    """`(contexte, corps, dans_une_media)` pour chaque règle du sélecteur.

    ⚠ On parcourt TOUTE la feuille, requêtes média comprises. Se limiter au
    premier niveau est précisément le défaut d'origine.
    """
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    spans = _media_spans(css)
    out = []
    for m in re.finditer(
        rf"(?<![\w-]){re.escape(selector)}(?![\w-])[^{{}}]*\{{([^}}]*)\}}", css
    ):
        inside = next(
            (css[a:b].split("{", 1)[0].strip() for a, b in spans if a <= m.start() < b),
            None,
        )
        out.append((inside or "(premier niveau)", m.group(1), inside is not None))
    return out


@pytest.fixture(scope="module")
def css() -> str:
    return CSS.read_text(encoding="utf-8")


def test_the_probe_actually_reaches_inside_media_queries(css):
    """Garde de la garde, et elle n'est pas décorative.

    Si le parcours cessait de descendre dans les `@media`, tous les tests
    ci-dessous passeraient à vide — c'est-à-dire exactement l'état dans lequel
    le défaut a vécu.
    """
    rules = _rules_for(css, ".today-home__hero")
    assert rules, "aucune règle de hero trouvée — le sélecteur a dérivé"
    assert any(scoped for _ctx, _body, scoped in rules), (
        "aucune règle de hero trouvée DANS une requête média — or la feuille "
        "en contient : le parcours ne descend plus dans les `@media`"
    )


@pytest.mark.parametrize("selector", NO_RESERVED_HEIGHT)
def test_no_reserved_height_anywhere_including_media_queries(selector, css):
    """L'invariant : le hero fait la hauteur de ce qu'il contient.

    « Partout » inclut les requêtes média, et c'est tout le propos : la
    correction d'origine s'y était perdue.
    """
    offenders = [
        f"{ctx} → {decl.strip()}"
        for ctx, body, _scoped in _rules_for(css, selector)
        for decl in re.findall(r"[^;{}]*\bmin-height\s*:[^;{}]*", body)
    ]
    assert offenders == [], (
        f"{selector} réserve une hauteur : {offenders}. Une hauteur réservée "
        "produit du vide dès que le contenu est court — et le contenu de ce "
        "bloc EST court, c'est l'objet de `Q5`."
    )


def test_no_viewport_height_is_reserved_on_the_home_surface(css):
    """`vh` est le vrai coupable, pas `min-height` en soi.

    Une hauteur en pixels se remarque à la lecture ; `50vh` ne dit rien tant
    qu'on ne l'a pas multiplié par la hauteur d'un écran réel. C'est ce
    calcul-là que personne ne fait, et c'est pour cela que « 422 px dont 152
    vides » a survécu à sa propre correction.
    """
    stripped = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    offenders = re.findall(r"min-height\s*:\s*[\d.]+vh", stripped)
    assert offenders == [], (
        f"hauteur réservée en unités de viewport : {offenders}"
    )
