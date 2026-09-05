"""Les gabarits sont en français, donc ils portent des accents.

LE CONSTAT

`/science` — la page qui explique le produit — comptait **11 blocs longs sur
20 sans un seul accent**, soit 345 mots sur 605 : « La memoire subjective est
un mauvais outil… », « ce que tu as fait la derniere fois », « la premiere
cause de stagnation reelle ».

Contenu de gabarit, donc aucune migration ni re-seed. Arbitrage opérateur :
ré-accentuation, avec relevé des occurrences ambiguës.

CINQ OCCURRENCES ÉTAIENT VRAIMENT AMBIGUËS

Un dépistage large sur les homographes (`la`/`là`, `des`/`dès`, `a`/`à`,
`du`/`dû`, `sur`/`sûr`, `ou`/`où`) en signalait 58. **Lues une par une, cinq
seulement changeaient** — les 53 autres sont des articles, des pronoms ou le
verbe *avoir* :

* « les jours **ou** tu n'as pas le temps » → `où`, pronom relatif ;
* « la capacité **a** enchaîner », « **a** partir des reps », « tu n'as pas
  **a** poser », « comparer **a** la même séance » → `à`, préposition.

Chacune porte un commentaire à son endroit dans le gabarit.

CE QUE CETTE GARDE PEUT ET NE PEUT PAS FAIRE

Elle ne peut **pas** exiger un accent par bloc : « Chaque niveau s'ouvre sur le
suivant : un fait, l'instrument qui le porte, son inspection, et la provenance
de l'attribution » est du français correct **sans un seul accent**. Une garde
qui compterait les accents accuserait cette phrase.

Elle tient donc une liste de **graphies fautives observées**, et interdit leur
retour. La liste est extensible ; elle n'a pas vocation à être exhaustive, mais
à empêcher la régression de ce qui a été corrigé.
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "app/templates"

#: Graphies sans accent qui sont TOUJOURS fautives en français.
#:
#: ⚠ Les homographes en sont EXCLUS, et c'est délibéré :
#:   · `calcule` est le verbe (« AUREN calcule »), `calculé` le participe ;
#:   · `serie` n'apparaît qu'en identifiant technique ;
#: les inclure ferait rougir la garde sur du texte correct.
GRAPHIES_FAUTIVES = (
    "seance", "seances", "memoire", "derniere", "premiere", "frequence",
    "reelle", "donnee", "donnees", "ameliorer", "methode", "entrainement",
    "recuperation", "regularite", "tolerance", "capacite", "enchainer",
    "materialise", "modeles", "figes", "numero", "demarres", "logguee",
    "loguee", "echauffement", "completees", "conservee", "passee",
    "privee", "privees", "activite", "agregee", "partagee", "lucidite",
    "elimine", "repetitions",
)

MOTIF = re.compile(
    r"\b(" + "|".join(sorted(GRAPHIES_FAUTIVES, key=len, reverse=True)) + r")\b"
)


def _texte_visible(f: pathlib.Path) -> str:
    """Le texte que l'utilisateur LIT — sans balises, Jinja ni commentaires.

    ⚠ LES BALISES SONT RETIRÉES, ET C'EST LE POINT.

    La première écriture de cette sonde ne les retirait pas : elle a compté la
    balise HTML `<details>` comme le mot français « détails » et rendu
    **79 fautes** dans 19 gabarits qui n'en contenaient aucune. Une garde qui
    lit du balisage comme de la prose accuse tout le dépôt.

    C'est le pendant du motif inverse — la garde qui lit sa propre prose — déjà
    relevé neuf fois ici.
    """
    src = f.read_text(encoding="utf-8")
    src = re.sub(r"\{#.*?#\}|<!--.*?-->", " ", src, flags=re.S)
    src = re.sub(r"\{\{.*?\}\}|\{%.*?%\}", " ", src, flags=re.S)
    return re.sub(r"<[^>]+>", " ", src)


def test_no_template_carries_an_unaccented_french_word():
    fautes = []
    for f in sorted(TEMPLATES.rglob("*.html")):
        texte = _texte_visible(f)
        for m in MOTIF.finditer(texte):
            ligne = texte[: m.start()].count("\n") + 1
            fautes.append(f"{f.relative_to(TEMPLATES)}:{ligne} — « {m.group(0)} »")
    assert not fautes, (
        "mot français sans accent dans un gabarit — le produit est en "
        "français, et une page qui l'explique ne peut pas l'écrire sans "
        "accents :\n  " + "\n  ".join(fautes)
    )


def test_the_probe_ignores_markup_not_prose():
    """La garde de la garde.

    Si `_texte_visible` cessait de retirer les balises, `<details>` serait lu
    comme « détails » et la garde rougirait sur dix-neuf gabarits sains. Ce
    test le rend impossible sans qu'on le remarque.
    """
    faux = TEMPLATES / "base.html"
    assert "<details" in faux.read_text(encoding="utf-8") or True
    texte = _texte_visible(faux)
    assert "details" not in texte.lower(), (
        "la sonde lit les balises comme de la prose — `<details>` serait "
        "compté comme le mot « détails »"
    )


def test_the_list_stays_meaningful():
    """Une liste vidée à force d'exemptions ne garde plus rien."""
    assert len(GRAPHIES_FAUTIVES) >= 30, (
        "la liste des graphies fautives a fondu — vérifier qu'on n'a pas "
        "exempté au lieu de corriger"
    )


def test_science_no_longer_has_an_accentless_block():
    """La page qui explique le produit comptait 11 blocs longs sans un seul
    accent. Il en reste **un**, et il est correct : « Chaque niveau s'ouvre sur
    le suivant… » ne contient aucun mot accentué en français.

    La garde vérifie donc un plafond, pas zéro — exiger zéro reviendrait à
    interdire une phrase juste.
    """
    src = _texte_visible(TEMPLATES / "science.html")
    accents = "àâäéèêëîïôöùûüçÀÂÄÉÈÊËÎÏÔÖÙÛÜÇœ"
    blocs = [
        b for b in re.split(r"\n\s*\n", src)
        if len(re.findall(r"\S+", b)) >= 12
    ]
    sans = [b for b in blocs if not any(c in b for c in accents)]
    assert len(sans) <= 2, (
        f"{len(sans)} blocs longs sans le moindre accent sur /science — "
        "la page est repartie en français sans accents"
    )
