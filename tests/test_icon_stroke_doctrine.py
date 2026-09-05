"""`N-04` — le poids de trait des icônes, enfin tranché.

POURQUOI CETTE GARDE EXISTE
---------------------------
J'avais d'abord écrit que le trait de la coque « diverge du contrat ». **C'était
faux, et vérifié au code** : `Sx_ASSET_02 §50` documente `1.7` pour la coque,
`§42`/`§146` documentent `2` pour le subset vendeur, et **`§208` diffère
explicitement la valeur canonique « au build »**.

Le dépôt était donc fidèle à sa spec. Ce qui manquait n'était pas une
correction, c'était une DÉCISION — la valeur n'avait jamais été tranchée, et
une valeur non tranchée dérive.

`N-04 = C` (opérateur, 2026-09-04) : **deux rôles, deux poids.**
`1.7` pour la coque, `2` pour le contenu, écrits au contrat.

⚠ CE QUE LE COMPTAGE NAÏF FAIT CROIRE. Un inventaire de tous les
`stroke-width` du dépôt rend CINQ valeurs — 1, 1.4, 1.7, 2 — et suggère un
désordre qui n'existe pas. Les autres appartiennent à des DIAGRAMMES : des
rectangles pointillés dans l'illustration de l'accueil public, un tick dans
l'exposition de zones. Ce ne sont pas des icônes.

Le discriminant n'est pas la classe CSS — elle varie — mais
`stroke="currentColor"` : **une icône fonctionnelle hérite la couleur du
texte, un diagramme pose ses propres hex.** Cette distinction est le contenu
réel de la garde ; sans elle, elle signalerait une illustration.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "app" / "templates"

#: Rôle → poids canonique. `N-04 = C`.
DOCTRINE = {"coque": "1.7", "contenu": "2"}

#: Les icônes de coque se reconnaissent à leur classe ; tout le reste des
#: icônes fonctionnelles est du contenu.
SHELL_ICON = re.compile(r'class="[^"]*(?:app-rail__icon|app-bottom-nav__icon)')


def _functional_icons() -> list[tuple[str, str, str | None]]:
    """`(fichier, balise, poids)` pour chaque `<svg>` en `currentColor`."""
    out = []
    for p in sorted(TEMPLATES.rglob("*.html")):
        src = re.sub(r"\{#.*?#\}", "", p.read_text(encoding="utf-8"), flags=re.DOTALL)
        for tag in re.findall(r"<svg[^>]*>", src):
            if 'stroke="currentColor"' not in tag:
                continue          # diagramme, pas icône
            w = re.search(r'stroke-width="([0-9.]+)"', tag)
            out.append((p.name, tag, w.group(1) if w else None))
    return out


def test_the_probe_separates_icons_from_diagrams():
    """Garde de la garde, et elle porte le vrai contenu du test.

    Sans le discriminant `currentColor`, l'inventaire rend cinq poids et la
    garde signalerait des rectangles d'illustration. Avec, elle ne voit que
    des icônes.
    """
    icons = _functional_icons()
    assert len(icons) >= 8, f"seulement {len(icons)} icônes lues — sonde suspecte"

    all_widths = set()
    for p in TEMPLATES.rglob("*.html"):
        all_widths |= set(re.findall(r'stroke-width="([0-9.]+)"', p.read_text(encoding="utf-8")))
    icon_widths = {w for _f, _t, w in icons if w}
    assert icon_widths < all_widths, (
        "le discriminant ne filtre rien : la garde regarde aussi les diagrammes"
    )


@pytest.mark.parametrize("role", sorted(DOCTRINE))
def test_each_role_uses_exactly_one_stroke_weight(role):
    """`N-04 = C` — deux rôles, deux poids. Pas trois.

    Une valeur non tranchée dérive : c'est pour cela que `§208` la différait
    « au build », et pour cela qu'elle est fixée ici.
    """
    attendu = DOCTRINE[role]
    offenders = []
    for fichier, tag, poids in _functional_icons():
        est_coque = bool(SHELL_ICON.search(tag))
        if (role == "coque") != est_coque:
            continue
        if poids is None:
            continue          # poids hérité de la feuille — vérifié ailleurs
        if poids != attendu:
            offenders.append(f"{fichier} → {poids} (attendu {attendu})")
    assert offenders == [], (
        f"le rôle « {role} » emploie plusieurs poids : {offenders}"
    )


def test_no_functional_icon_borrows_a_diagram_weight():
    """Les poids de diagramme — 1 et 1.4 — n'appartiennent pas aux icônes.

    Ils existent légitimement dans l'illustration publique et dans
    l'exposition de zones. Les voir apparaître sur une icône signalerait
    qu'un dessin a été recyclé en contrôle.
    """
    interdits = {"1", "1.4"}
    offenders = [
        f"{f} → {w}" for f, _t, w in _functional_icons() if w in interdits
    ]
    assert offenders == [], (
        f"une icône emploie un poids de diagramme : {offenders}"
    )


def test_the_shell_icons_are_all_present_and_uniform():
    """Huit icônes de coque — rail desktop et barre basse, quatre chacun.

    Si l'une disparaissait, le test de doctrine ci-dessus passerait sur les
    sept restantes sans rien dire de la huitième.
    """
    shell = [w for _f, t, w in _functional_icons() if SHELL_ICON.search(t)]
    assert len(shell) == 8, f"8 icônes de coque attendues, {len(shell)} trouvées"
    assert set(shell) == {DOCTRINE["coque"]}, set(shell)
