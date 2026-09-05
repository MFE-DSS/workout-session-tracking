"""Le cliquet de l'invariant « aucun style inline statique non contracté ».

POURQUOI CE FICHIER EXISTE

`docs/strategy/AUREN_VISUAL_BACKBONE.md §5` range cet invariant parmi les
**non négociables**, à côté de la cible tactile 44 px et du fonctionnement sans
JavaScript :

> **Aucun style inline statique non contracté** — l'inline ne survit que pour
> une valeur réellement dynamique, allowlistée. Mesuré : **5 sur 708**.

Le « 5 » est exact, et il est vérifié ici : cinq `width: N%` calculés, dans
deux gabarits, qui ne peuvent pas vivre dans une feuille de style.

Ce qui manquait, c'est le reste de la phrase. **328 styles inline statiques
vivent dans 38 gabarits sur 65**, et aucune garde ne les comptait. Un invariant
déclaré non négociable qu'aucun test ne regarde n'est pas un invariant, c'est
une intention.

CE QUE CE CLIQUET FAIT, ET CE QU'IL NE FAIT PAS

Il ne corrige rien. Il **gèle** la dette existante, gabarit par gabarit, et
interdit qu'elle grossisse. La résorption se fait ensuite surface par surface,
au fil des tranches : chacune fait baisser son entrée, et le diff le montre.

C'est le patron que le dépôt applique déjà au budget ruff — sauf que celui-ci
compare **par fichier** et non en total. Un total autorise un fichier à
empirer pendant qu'un autre s'améliore ; ici, chaque gabarit répond de lui-même.

L'ÉGALITÉ EST STRICTE, DANS LES DEUX SENS

Descendre sous la ligne de base **échoue aussi**, et c'est voulu : une ligne de
base qu'on ne met pas à jour en s'améliorant rote, et six mois plus tard elle
autorise une régression silencieuse vers un état qu'on avait déjà quitté. Le
message dit quoi écrire.
"""
from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "app/templates"
BASELINE = pathlib.Path(__file__).parent / "inline_style_baseline.json"

#: Un attribut `style` porté par le gabarit. Seule la forme à guillemets
#: doubles existe dans ce dépôt — vérifié : ni apostrophe simple, ni valeur
#: non quotée. Si une autre forme apparaît, `test_the_probe_sees_every_form`
#: rougit plutôt que de la laisser passer sous le radar.
STYLE_ATTR = re.compile(r'style="([^"]*)"')
JINJA_COMMENT = re.compile(r"\{#.*?#\}", re.S)


def _recense() -> tuple[dict[str, int], dict[str, int]]:
    """(statiques, dynamiques) par gabarit.

    ⚠ Les commentaires Jinja sont retirés AVANT de chercher. Deux gabarits
    (`history.html`, `index.html`) documentent en commentaire des styles inline
    qu'ils ont retirés ; les compter ferait rougir la garde sur la prose qui
    explique qu'on a bien fait le travail. Le motif s'est présenté neuf fois
    dans ce dépôt.
    """
    statiques: dict[str, int] = {}
    dynamiques: dict[str, int] = {}
    for f in sorted(TEMPLATES.rglob("*.html")):
        src = JINJA_COMMENT.sub(" ", f.read_text(encoding="utf-8"))
        cle = str(f.relative_to(TEMPLATES))
        for valeur in STYLE_ATTR.findall(src):
            cible = dynamiques if ("{{" in valeur or "{%" in valeur) else statiques
            cible[cle] = cible.get(cle, 0) + 1
    return statiques, dynamiques


def _baseline() -> dict:
    return json.loads(BASELINE.read_text(encoding="utf-8"))


def test_the_probe_sees_every_form_of_the_attribute():
    """La sonde ne lit que `style="…"`. Elle doit rester exhaustive.

    Une garde aveugle à `style='…'` ou à `style=foo` compterait juste et
    conclurait faux — le pire des deux mondes, puisqu'elle donnerait une
    confiance qu'elle ne mérite pas.
    """
    autres = []
    for f in TEMPLATES.rglob("*.html"):
        src = JINJA_COMMENT.sub(" ", f.read_text(encoding="utf-8"))
        # `style` suivi de `=`, mais pas de la forme que la sonde sait lire.
        for m in re.finditer(r'\bstyle\s*=\s*(?!")', src):
            autres.append(f"{f.relative_to(TEMPLATES)}:{src[:m.start()].count(chr(10)) + 1}")
    assert not autres, (
        "des attributs `style` échappent à la sonde — elle compte donc moins "
        f"que la réalité : {autres}"
    )


def test_no_template_gains_a_static_inline_style():
    """Le cliquet. Un gabarit ne peut pas empirer, ni s'améliorer en silence."""
    statiques, _ = _recense()
    attendu = _baseline()["static_debt"]

    aggraves = {
        k: (attendu.get(k, 0), v)
        for k, v in statiques.items()
        if v > attendu.get(k, 0)
    }
    assert not aggraves, (
        "styles inline statiques AJOUTÉS — l'invariant du socle "
        "(`AUREN_VISUAL_BACKBONE §5`) l'interdit. Écrire la règle dans une "
        "feuille de style, pas dans l'attribut.\n"
        + "\n".join(f"  {k} : {a} → {b}" for k, (a, b) in sorted(aggraves.items()))
    )

    ameliores = {
        k: (v, statiques.get(k, 0))
        for k, v in attendu.items()
        if statiques.get(k, 0) < v
    }
    assert not ameliores, (
        "dette RÉSORBÉE mais ligne de base non mise à jour. Serrer le cliquet "
        "dans `tests/inline_style_baseline.json`, sinon il autorisera plus tard "
        "un retour en arrière vers un état déjà quitté.\n"
        + "\n".join(f"  {k} : {a} → {b}" for k, (a, b) in sorted(ameliores.items()))
    )


def test_every_dynamic_inline_style_is_allowlisted():
    """L'inline ne survit que pour une valeur RÉELLEMENT dynamique.

    Les cinq survivants sont des `width: N%` calculés : une largeur de barre
    n'a pas de place dans une feuille de style, elle dépend de la donnée.
    """
    _, dynamiques = _recense()
    permis = _baseline()["dynamic_allowlist"]
    hors_liste = {
        k: v for k, v in dynamiques.items() if v > permis.get(k, 0)
    }
    assert not hors_liste, (
        "styles inline dynamiques hors allowlist — chacun doit être justifié "
        f"par une valeur qu'une feuille ne peut pas porter : {hors_liste}"
    )


def test_the_backbone_number_still_matches_the_code():
    """Le socle annonce **5** dynamiques. Si le code diverge, c'est le
    document qui ment, et un document qui ment sur un invariant est pire que
    pas de document."""
    _, dynamiques = _recense()
    socle = (ROOT / "docs/strategy/AUREN_VISUAL_BACKBONE.md").read_text(
        encoding="utf-8")
    assert "Mesuré : **5 sur 708**" in socle, (
        "le socle n'annonce plus 5 — mettre à jour ce test AVEC lui"
    )
    assert sum(dynamiques.values()) == 5, (
        f"le socle annonce 5 styles inline dynamiques, le code en a "
        f"{sum(dynamiques.values())}"
    )
