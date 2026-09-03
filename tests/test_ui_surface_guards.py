"""`Sx_CI_UI_SURFACE_GUARDS_01` — trois défauts UI que la CI ne voyait pas.

CE QUE CES GARDES FERMENT
-------------------------
Dix défauts UI réels ont été plantés dans la console de séance et joués contre
les 293 fichiers de test. **Trois n'ont fait rougir personne** :

    plancher de 44 px abaissé à 24        →  AVEUGLE
    marqueur d'un <summary> supprimé      →  AVEUGLE
    sélecteur renommé dans un script      →  AVEUGLE

La cause est assumée et documentée — `pyproject.toml` (`Sb_UI_11.1`) : Playwright
n'est **jamais** installé en CI, qui « ne valide que la matrice et la logique CLI
sans lancer de navigateur ». Le signal UI y est donc entièrement textuel.

Ces trois gardes n'y changent rien : elles sont en Python pur, sans navigateur
et sans dépendance neuve. Elles ne mesurent pas des pixels — elles mesurent des
**invariants de source** que les trois défauts violent tous.

POURQUOI DES CLIQUETS, ET PAS DES SEUILS
-----------------------------------------
Neuf règles posent déjà un plancher sous 44 px, et treize règles `<summary>`
changent déjà leur `display`. Toutes ne sont pas fautives : `.ze-row` n'est pas
une cible tactile, `.coach-ratio__strength` est une barre.

Une garde qui exigerait « tout ≥ 44 » serait **rouge sur du code sain** — donc
inutile — ou m'obligerait à retoucher des surfaces acceptées, ce que
`CLAUDE.md §5.5` interdit et que `UIV3_TARGETS_44_01` a déjà tranché dans son
propre périmètre.

D'où le motif de `.ruff-budget.json` : un **inventaire gelé**. Ce qui existe est
recensé ; rien de neuf ne passe. Un `44px` abaissé à `24px` crée une entrée
nouvelle — c'est exactement le défaut planté, et il rougit.
"""
from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS_DIR = ROOT / "app/static/css"
JS_DIR = ROOT / "app/static/js"
TPL_DIR = ROOT / "app/templates"
INVENTORY = pathlib.Path(__file__).with_name("ui_surface_inventory.json")
#: Hoisté : `errors=_ERR` revenait 3 fois → `S1192`.
_ERR = "ignore"

PRODUCT_FLOOR_PX = 44
_RULE = re.compile(r"([^{}]+)\{([^}]*)\}", re.S)
_FLOOR = re.compile(r"min-(?:height|width)\s*:\s*([\d.]+)px")
_DISPLAY = re.compile(r"(?<![\w-])display\s*:\s*([\w-]+)")
_DATA_ATTR = re.compile(r"\[\s*(data-[\w-]+)")


def _strip_comments(src: str) -> str:
    """Un commentaire CSS n'est pas une règle.

    `DF-C` a payé l'inverse : une garde naïve trouvait `.console` dans le
    commentaire qui explique pourquoi la feuille ne touche pas la console, et
    rougissait sur l'explication.
    """
    return re.sub(r"/\*.*?\*/", " ", src, flags=re.S)


def _rules():
    for sheet in sorted(CSS_DIR.glob("*.css")):
        src = _strip_comments(sheet.read_text(encoding="utf-8"))
        for m in _RULE.finditer(src):
            yield sheet.name, " ".join(m.group(1).split()), m.group(2)


def _under_floor() -> set[str]:
    """`feuille::sélecteur::déclaration` pour tout plancher sous 44 px."""
    found = set()
    for sheet, sel, body in _rules():
        for m in _FLOOR.finditer(body):
            if float(m.group(1)) < PRODUCT_FLOOR_PX:
                found.add(f"{sheet}::{sel}::{m.group(0)}")
    return found


def summary_classes() -> set[str]:
    """Les classes RÉELLEMENT portées par un `<summary>`, lues dans les gabarits.

    ⚠ POURQUOI PAS LE NOM. Une première version cherchait « summary » dans le
    sélecteur CSS. Elle a été trouvée CREUSE en plantant : `.overload-hint__why-toggle`
    EST un `<summary>` — c'est le « Pourquoi ? » de la console — et son nom ne
    contient pas « summary ». La garde ne le voyait pas, et le défaut passait.

    Le nom d'une classe est une convention ; le gabarit est la source. On lit
    donc le gabarit.
    """
    rx = re.compile(r'<summary[^>]*class="([^"]+)"', re.S)
    # Un `class="{% if x %}a{% endif %}"` laisse traîner les mots-clés Jinja.
    jinja = {"if", "endif", "else", "elif", "is_active", "not", "and", "or"}
    found = set()
    for tpl in TPL_DIR.rglob("*.html"):
        for m in rx.finditer(tpl.read_text(encoding="utf-8", errors=_ERR)):
            for cls in m.group(1).split():
                if "{" not in cls and "}" not in cls and cls not in jinja:
                    found.add(cls)
    return found


def _summary_display() -> set[str]:
    """Règles retirant son `display: list-item` à un élément qui EST un `<summary>`.

    C'est LA façon dont un marqueur natif disparaît : `display: flex` supprime
    le triangle sans qu'aucune propriété ne le dise. Le défaut a été livré deux
    fois dans ce dépôt (`Q5`, puis « Filtrer par zone »).
    """
    classes = summary_classes()
    found = set()
    for sheet, sel, body in _rules():
        if "::" in sel:
            continue
        touches = "summary" in sel or any(f".{c}" in sel for c in classes)
        if not touches:
            continue
        d = _DISPLAY.search(body)
        if d and d.group(1) != "list-item":
            found.add(f"{sheet}::{sel}::display:{d.group(1)}")
    return found


def _inventory() -> dict:
    return json.loads(INVENTORY.read_text(encoding="utf-8"))


# ═════════ GARDE 1 — le plancher tactile ne se relâche pas ═════════


def test_no_new_target_falls_below_the_product_floor():
    """CLIQUET. 44 est le standard PRODUIT d'AUREN, pas le seuil WCAG (24).

    L'inventaire recense ce qui existe. Toute entrée NOUVELLE est un plancher
    abaissé ou une règle neuve sous 44 — les deux exigent une décision, pas un
    passage silencieux.
    """
    known = set(_inventory()["under_floor"])
    current = _under_floor()
    new = sorted(current - known)
    assert not new, (
        f"plancher tactile sous {PRODUCT_FLOOR_PX} px introduit : {new}. "
        "Si c'est délibéré (barre, ligne, chrome non tactile), l'ajouter à "
        "`ui_surface_inventory.json` AVEC sa raison."
    )


def test_the_floor_inventory_does_not_rot():
    """Une entrée disparue doit sortir de l'inventaire.

    Sans quoi le cliquet se relâche en silence : on garderait la permission
    d'un défaut qui n'existe plus, et le prochain la réutiliserait.
    """
    known = set(_inventory()["under_floor"])
    stale = sorted(known - _under_floor())
    assert not stale, (
        f"entrées périmées dans l'inventaire : {stale} — les retirer, sinon "
        "elles autorisent d'avance un défaut futur."
    )


# ═════════ GARDE 2 — un <summary> ne perd pas son marqueur en silence ═════════


def test_no_new_summary_loses_its_native_marker():
    """CLIQUET. Un `<summary>` en `display: flex` PERD son marqueur natif.

    Mesuré sur les styles calculés de trois déclencheurs de la même page : le
    témoin qui marche rend `list-item`. Rien dans la feuille ne signale la
    perte — c'est pour cela qu'elle a été livrée deux fois.
    """
    known = set(_inventory()["summary_display"])
    new = sorted(_summary_display() - known)
    assert not new, (
        f"`<summary>` privé de `display: list-item` sans décision : {new}. "
        "Restituer un marqueur explicite, ou inscrire l'entrée avec sa raison."
    )


def test_the_summary_inventory_does_not_rot():
    known = set(_inventory()["summary_display"])
    stale = sorted(known - _summary_display())
    assert not stale, f"entrées périmées : {stale}"


# ═════════ GARDE 3 — un script ne lit pas un attribut que le HTML n'émet pas ═════


def test_every_selector_a_script_reads_exists_in_a_template():
    """LE VERSANT ENCORE OUVERT DE `DF-03`.

    L'incident du dogfood — minuteur figé sur `1:30`, contrôles `±15 s` absents
    — venait d'un script cherchant `[data-start-rest]` quand le HTML n'émettait
    plus que `[data-rest-started]`. Zéro racine trouvée, sortie par un `return`
    silencieux, **aucune erreur, aucun 404**.

    `STATIC_ASSET_COHERENCE_01` a fermé le versant « asset périmé » par
    l'empreinte d'URL. Le versant « sélecteur incohérent » restait ouvert :
    mesuré, renommer un attribut dans le script ne fait rougir aucun des 293
    fichiers de test.
    """
    templates = "\n".join(
        p.read_text(encoding="utf-8", errors=_ERR) for p in TPL_DIR.rglob("*.html")
    )
    orphans = []
    for js in sorted(JS_DIR.rglob("*.js")):
        src = js.read_text(encoding="utf-8", errors=_ERR)
        for attr in sorted(set(_DATA_ATTR.findall(src))):
            if attr not in templates:
                orphans.append(f"{js.name} lit [{attr}]")
    assert not orphans, (
        "un script lit un attribut qu'aucun gabarit n'émet — il ne trouvera "
        f"aucune racine et sortira sans rien dire : {orphans}"
    )


def test_this_guard_would_have_caught_the_dogfood_incident():
    """⚠ Une garde verte ne prouve rien tant qu'on ne l'a pas vue rougir.

    On rejoue le couple exact de l'incident, sans toucher au dépôt.
    """
    js = "document.querySelectorAll('[data-start-rest]')"
    html_ancien = '<div data-start-rest="1"></div>'
    html_actuel = '<div data-rest-started="1"></div>'
    attrs = set(_DATA_ATTR.findall(js))
    assert attrs == {"data-start-rest"}
    assert all(a in html_ancien for a in attrs), "faux positif sur le HTML d'époque"
    assert not all(a in html_actuel for a in attrs), (
        "la garde ne verrait PAS la divergence qui a causé `DF-03`"
    )
