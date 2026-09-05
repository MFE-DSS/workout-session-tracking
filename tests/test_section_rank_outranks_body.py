"""Un titre de section ne peut pas être plus petit que le corps qu'il introduit.

`AUREN_VISUAL_BACKBONE §3.2` documente ce défaut nommément : « body 14 px,
section-header 13 px … sur 101 usages ». Un titre de bloc plus petit que son
propre contenu ne hiérarchise rien — il ajoute du texte.

Cette garde épingle la **relation**, jamais l'écriture. Porter le rang SECTION
de 22 à 20 px reste licite ; le faire retomber sous le corps ne l'est pas.
C'est la distinction que `guards-that-guard-nothing` appelle « épingler une
VALEUR plutôt qu'une ÉCRITURE » : une garde qui fige `font-size: 22px` interdit
le réglage sans protéger l'invariant.
"""
from __future__ import annotations

import re
from pathlib import Path

CSS = Path(__file__).resolve().parents[1] / "app" / "static" / "css" / "app.css"
GABARITS = Path(__file__).resolve().parents[1] / "app" / "templates"


#: Un bloc CSS plat : sa liste de sélecteurs, puis son corps sans accolade.
_BLOC = re.compile(r"(?m)^([^\n{}]+?)\s*\{([^{}]*)\}")


def _taille(selecteur: str, source: str) -> float:
    """Rend la taille que la cascade retient pour CE sélecteur.

    Un sélecteur apparaît rarement seul : le corps du produit est déclaré par
    `html, body { … }`, et une seconde règle `body { … }` vit 4 200 lignes plus
    bas sans taille. Une sonde qui prend le PREMIER bloc trouvé lit la mauvaise
    règle et rend une garde qui ne mesure rien — c'est le mode d'échec
    « la garde ne regarde qu'un exemplaire d'une famille ».

    On collecte donc TOUS les blocs qui nomment le sélecteur, et on retient le
    dernier qui déclare une taille : c'est celui que la cascade applique.
    """
    tailles = [
        float(px.group(1))
        for liste, corps in _BLOC.findall(source)
        if selecteur in {s.strip() for s in liste.split(",")}
        if (px := re.search(r"font-size:\s*([\d.]+)px", corps))
    ]
    assert tailles, (
        f"aucun bloc nommant « {selecteur} » ne déclare de taille en px dans "
        "app.css — la garde ne mesure plus rien. La réancrer avant de la "
        "croire verte."
    )
    return tailles[-1]


def test_le_rang_section_domine_le_corps():
    source = CSS.read_text(encoding="utf-8")
    corps = _taille("body", source)
    section = _taille(".section-header", source)
    assert section > corps, (
        f"`.section-header` vaut {section:g} px et le corps {corps:g} px : le "
        "titre de bloc est plus petit que le texte qu'il introduit. C'est le "
        "défaut nommé dans AUREN_VISUAL_BACKBONE §3.2."
    )


def test_la_promotion_porte_sur_toute_la_classe():
    """La décision vaut pour les onze gabarits, pas pour la surface commode.

    `decisions-applied-where-convenient` : le mode d'échec relevé est d'appliquer
    une décision là où elle est facile. Un sélecteur d'écran qui redéclarerait
    la taille rétablirait le défaut sur une surface en laissant la garde verte.
    """
    source = CSS.read_text(encoding="utf-8")
    corps = _taille("body", source)
    redeclarations = [
        (m.group(0).strip(), float(m.group(1)))
        for m in re.finditer(
            r"(?m)^[^\n{}]*\.section-header[^\n{}]*\{[^}]*?"
            r"font-size:\s*([\d.]+)px",
            source,
            re.DOTALL,
        )
    ]
    assert redeclarations, "aucun bloc `.section-header` trouvé — sonde cassée"
    trop_petites = [(sel, px) for sel, px in redeclarations if px <= corps]
    assert not trop_petites, (
        "des sélecteurs redéclarent `.section-header` sous le corps "
        f"({corps:g} px) : {trop_petites}"
    )


def test_la_sonde_voit_bien_les_onze_gabarits():
    """Garde de la garde : la classe est-elle encore portée par les surfaces ?

    Si `.section-header` disparaissait des gabarits, les deux tests ci-dessus
    resteraient verts en ne protégeant plus rien.
    """
    porteurs = sorted(
        p.relative_to(GABARITS).as_posix()
        for p in GABARITS.rglob("*.html")
        if "section-header" in p.read_text(encoding="utf-8")
    )
    assert len(porteurs) >= 10, (
        f"`.section-header` n'est plus porté que par {len(porteurs)} gabarits "
        f"({porteurs}) — la promotion de rang ne couvre plus la classe qu'elle "
        "prétend couvrir."
    )
