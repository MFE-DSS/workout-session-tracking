"""La pluralisation française du produit, et le filtre qui la porte.

LE CONSTAT

Dix-huit endroits écrivaient `séance{% if n > 1 %}s{% endif %}` correctement.
Neuf autres, dans trois gabarits, écrivaient `séance(s)` — la parenthèse qui
économise la condition en abîmant la phrase.

La règle était connue du produit, mais **écrite nulle part** : seulement
répétée. Une règle répétée dix-huit fois et jamais nommée finit par dériver, et
elle a dérivé neuf fois.

C'est exactement le constat de `date_fr` : la pièce existait, elle n'était pas
**atteignable** depuis un gabarit sans la connaître.
"""
from __future__ import annotations

import pathlib
import re

import pytest

from app.templating import pluriel

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "app/templates"
JINJA_COMMENT = re.compile(r"\{#.*?#\}", re.S)

#: `mot(s)` — un mot collé à une parenthèse contenant un `s` seul.
#: Ancré sur des lettres françaises pour ne pas confondre avec du code : une
#: signature `f(s)` dans un extrait, ou `url_for(s)`, ne doit pas rougir.
PLURIEL_PARENTHESE = re.compile(r"[A-Za-zÀ-ÿ]{2,}\(s\)")


def _corps(f: pathlib.Path) -> str:
    """Le gabarit SANS ses commentaires Jinja.

    Ce fichier documente `séance(s)` dans sa propre justification, et un
    gabarit qui expliquerait pourquoi il ne l'écrit plus ferait rougir la
    garde sur sa propre prose. Le motif s'est présenté neuf fois ici.
    """
    return JINJA_COMMENT.sub(" ", f.read_text(encoding="utf-8"))


def test_no_template_writes_a_parenthesised_plural():
    """« 4 séance(s) proposée(s) » n'est pas du français, c'est un aveu que la
    condition n'a pas été écrite."""
    fautes = []
    for f in sorted(TEMPLATES.rglob("*.html")):
        for m in PLURIEL_PARENTHESE.finditer(_corps(f)):
            ligne = _corps(f)[: m.start()].count("\n") + 1
            fautes.append(f"{f.relative_to(TEMPLATES)}:{ligne} — {m.group(0)}")
    assert not fautes, (
        "pluriel entre parenthèses — utiliser le filtre `pluriel` "
        "(`{{ n }} {{ \"séance\" | pluriel(n) }}`), ou deux phrases quand "
        "l'accord touche aussi le verbe :\n  " + "\n  ".join(fautes)
    )


# ───────────── le filtre lui-même ─────────────

def test_the_threshold_is_french_not_english():
    """En français le pluriel commence à 2. Le seuil anglais (`!= 1`) rendrait
    « 0 séances », qui se lit comme une faute de frappe."""
    assert pluriel("séance", 0) == "séance"
    assert pluriel("séance", 1) == "séance"
    assert pluriel("séance", 2) == "séances"


def test_the_filter_refuses_what_it_cannot_guarantee():
    """⚠ LE POINT DE CE FILTRE.

    Il ajoute un `s`. C'est correct pour les onze mots que le produit
    pluralise, et faux pour « cheval » ou « travail ». Un filtre qui devine est
    **pire** qu'une condition en ligne : il a l'air d'avoir décidé, et personne
    ne relit un pluriel.
    """
    for ambigu in ("cheval", "travail", "bureau", "bijou", "prix", "nez"):
        with pytest.raises(ValueError, match="ambiguë"):
            pluriel(ambigu, 3)


def test_travail_is_refused_and_it_took_a_planting_to_notice():
    """`travail` → `travaux` est l'irrégulier français par excellence, et il
    est passé au travers de la première écriture : la liste des terminaisons
    contenait « al » mais pas « ail », et le filtre rendait « travails ».

    La liste paraissait complète. Elle ne l'était pas, et seule une plantation
    l'a dit — la garde de gabarits, elle, était restée verte.
    """
    with pytest.raises(ValueError, match="ambiguë"):
        pluriel("travail", 2)


def test_the_filter_over_refuses_and_that_is_the_right_side_to_err_on():
    """« détail » → « détails » et « pneu » → « pneus » sont RÉGULIERS, et le
    filtre les refuse quand même : ils partagent la terminaison d'irréguliers.

    Le coût du sur-refus est d'écrire un pluriel à la main. Le coût du
    sous-refus est « travails » en production. Tenir la liste exacte des
    exceptions françaises serait une dette de maintenance pour un gain nul.
    """
    for regulier_mais_ambigu in ("détail", "pneu", "carnaval", "clou"):
        with pytest.raises(ValueError, match="ambiguë"):
            pluriel(regulier_mais_ambigu, 2)


def test_the_refusal_does_not_fire_on_the_singular():
    """Au singulier le filtre ne forme rien : il rend le mot. Lever ici
    interdirait d'écrire « 1 cheval », ce qui n'a aucun sens."""
    assert pluriel("cheval", 1) == "cheval"


def test_every_word_the_product_pluralises_is_regular():
    """La garde qui rend le refus praticable.

    Si une surface introduit un mot irrégulier, elle doit le découvrir ICI et
    non par une exception en production. La liste est celle des mots réellement
    passés au filtre dans les gabarits.
    """
    mots = set()
    appel = re.compile(r'"([A-Za-zÀ-ÿ\'-]+)"\s*\|\s*pluriel')
    for f in TEMPLATES.rglob("*.html"):
        mots.update(appel.findall(_corps(f)))
    assert mots, "aucun appel au filtre trouvé — la garde ne mesure plus rien"
    for mot in sorted(mots):
        # Ne doit pas lever.
        assert pluriel(mot, 2) == f"{mot}s", mot
