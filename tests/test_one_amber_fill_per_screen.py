"""Les aplats ambre ne prolifèrent plus — cliquet, arbitré le 2026-09-06.

L'ambre désigne LA décision d'un écran. Sur `user_programs/detail.html` il y en
avait **cinq** rendus en même temps — trois « Ajouter l'exercice », « Ajouter
une séance », « Valider le brouillon ». Répété cinq fois, il ne désigne plus
rien : il redevient un fond parmi d'autres.

⚠ POURQUOI CE N'EST PAS LA GARDE QUE L'OPÉRATEUR A DEMANDÉE

Il a demandé « une garde qui compte les aplats par gabarit et refuse le
second ». Je l'ai écrite. **Elle accusait cinq gabarits sains.**

Vérifié à la main avant publication, comme la règle l'exige désormais :

* `index.html` porte QUATRE `today-home__cta` — dans des branches Jinja
  **mutuellement exclusives** (`{% if open_session %}` / `{% else %}`). Une
  seule rend. Mesuré au navigateur sur les trois états de l'accueil :
  **un seul aplat visible** ;
* `user_programs/detail.html` en porte trois, dans des branches de statut
  (`validated` / `published` / brouillon) — et trois autres dans des
  `<details>`, invisibles tant que le tiroir est fermé. Cet écran est
  CONFORME depuis sa refonte.

« Un aplat par écran » n'est pas décidable depuis le texte d'un gabarit :
branches, boucles et tiroirs décident de ce qui rend. Une garde statique qui
prétend le vérifier accuse du code juste — et se fait désarmer, à raison. C'est
la sixième occurrence de ce mode d'échec dans ce dépôt.

CE QUE CETTE GARDE FAIT À LA PLACE

Un **cliquet par gabarit**, comme pour les styles inline : le nombre
d'occurrences est gelé, et il ne peut pas augmenter. Elle n'affirme pas
« un seul rendu » — elle empêche la dérive qui a produit les cinq.

La vraie règle appartient à un **harnais de rendu**, qui compte les aplats
réellement peints sur une page réelle. Dette nommée, pas oubliée.
"""
from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "app/templates"
BASELINE = pathlib.Path(__file__).parent / "amber_fill_baseline.json"

#: Les classes qui posent un APLAT ambre. Le CONTOUR ambre (`pd-rank2`) est
#: explicitement permis au rang 2 — c'est un trait, pas un aplat.
APLAT = re.compile(r'class="[^"]*\b(?:btn--primary|today-home__cta)\b')

JINJA_COMMENT = re.compile(r"\{#.*?#\}", re.S)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)


def _compte(f: pathlib.Path) -> int:
    src = HTML_COMMENT.sub(" ", JINJA_COMMENT.sub(" ", f.read_text(encoding="utf-8")))
    return len(APLAT.findall(src))


def _recense() -> dict[str, int]:
    return {
        str(f.relative_to(TEMPLATES)): n
        for f in sorted(TEMPLATES.rglob("*.html"))
        if (n := _compte(f))
    }


def test_the_sweep_finds_amber_fills():
    """Une garde qui ne trouve rien ne garde rien."""
    assert sum(_recense().values()) >= 10, (
        "moins de dix aplats ambre recensés — la sonde ne porte sur rien"
    )


def test_no_template_gains_an_amber_fill():
    """Le cliquet, dans les deux sens."""
    reel = _recense()
    attendu = json.loads(BASELINE.read_text(encoding="utf-8"))["per_template"]

    aggraves = {
        k: (attendu.get(k, 0), v) for k, v in reel.items() if v > attendu.get(k, 0)
    }
    assert not aggraves, (
        "aplat(s) ambre AJOUTÉ(s). L'ambre désigne LA décision d'un écran ; "
        "répété, il ne désigne plus rien.\n"
        "  Rang 2 : un TRAIT, pas un aplat (`AUREN_VISUAL_BACKBONE §4.2` "
        "règle 3). Ou replier la commande dans un `<details>`, où elle est "
        "l'action de son tiroir.\n"
        + "\n".join(f"  {k} : {a} → {b}" for k, (a, b) in sorted(aggraves.items()))
    )

    ameliores = {
        k: (v, reel.get(k, 0)) for k, v in attendu.items() if reel.get(k, 0) < v
    }
    assert not ameliores, (
        "aplats ambre RETIRÉS mais ligne de base non mise à jour — la serrer "
        "dans `tests/amber_fill_baseline.json`.\n"
        + "\n".join(f"  {k} : {a} → {b}" for k, (a, b) in sorted(ameliores.items()))
    )


def test_the_baseline_records_why_it_is_not_one_per_screen():
    """La ligne de base doit porter la raison de sa forme.

    Sans elle, quelqu'un la lira comme « le produit autorise quatre aplats sur
    l'accueil » — alors qu'il en rend UN, et que le chiffre compte des branches
    exclusives.
    """
    note = json.loads(BASELINE.read_text(encoding="utf-8")).get("_comment", "")
    assert "branche" in note.lower(), (
        "la ligne de base n'explique pas pourquoi ses nombres ne sont pas "
        "des comptes d'écran"
    )
