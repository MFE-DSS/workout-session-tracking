"""`Sb_UI_HISTORIQUE_01` — aucun gabarit ne rend une date dans la locale du processus.

L'historique affichait « Sat 05/09 07:54 », dix fois par écran, dans une
interface française. La cause n'était pas une faute de frappe mais un appel :

    {{ (s.started_at | local).strftime('%a %d/%m %H:%M') }}

`%a`, `%A`, `%b` et `%B` rendent les noms de la **locale du processus**. Sur le
serveur, cette locale est `C` — donc l'anglais. Rien dans le gabarit ne le
signale, rien dans la revue ne le montre : il faut regarder l'écran rendu, ou
connaître le piège.

⚠ CE QUI REND CETTE GARDE NÉCESSAIRE PLUTÔT QUE PÉDANTE. Le produit avait DÉJÀ
tout ce qu'il fallait — le filtre `local_weekday` dans `templating.py`, et la
table `WEEKDAY_LABELS`. Le gabarit a quand même écrit sa propre version, en
anglais. C'est le huitième exemplaire, dans cette session, d'une décision prise
que rien n'empêchait de contourner. Une décision sans garde n'est pas une
décision : c'est une préférence que le prochain gabarit ignorera.

La plantation le prouve : retirer le jour français du formateur ne faisait
tomber AUCUNE garde du dépôt avant ce fichier.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

TEMPLATES = Path(__file__).resolve().parents[1] / "app" / "templates"

_ENC = "utf-8"

#: Les directives `strftime` dont le rendu dépend de la locale.
#: `%p` (AM/PM) est du même bois, et n'a de toute façon rien à faire ici.
LOCALE_DEPENDENT = ("%a", "%A", "%b", "%B", "%p")

ALL_TEMPLATES = sorted(TEMPLATES.rglob("*.html"))


def _uncommented(src: str) -> str:
    """Un commentaire Jinja qui EXPLIQUE le piège ne doit pas le déclencher.

    Ce fichier a corrigé `history.html` en laissant sur place un commentaire qui
    cite `strftime('%a …')` pour dire pourquoi il a été retiré. Une garde qui
    lit sa propre justification rougirait sur l'explication du correctif —
    motif déjà rencontré plusieurs fois dans ce dépôt.
    """
    return re.sub(r"\{#.*?#\}", " ", src, flags=re.DOTALL)


def test_the_sweep_actually_reads_templates():
    assert len(ALL_TEMPLATES) > 40, "le balayage ne porte sur rien"


@pytest.mark.parametrize("tpl", ALL_TEMPLATES, ids=lambda p: p.name)
def test_no_template_formats_a_date_with_a_locale_directive(tpl: Path):
    """Universel par construction : la liste vient d'un `rglob`."""
    src = _uncommented(tpl.read_text(encoding=_ENC))
    for m in re.finditer(r"strftime\(\s*['\"]([^'\"]*)['\"]", src):
        motif = m.group(1)
        fautives = [d for d in LOCALE_DEPENDENT if d in motif]
        assert not fautives, (
            f"{tpl.name} : `strftime('{motif}')` contient {fautives}, "
            f"dont le rendu suit la locale du PROCESSUS (anglais sur le "
            f"serveur). Employer le filtre `date_fr`, ou `local_weekday` avec "
            f"`WEEKDAY_LABELS`."
        )


def test_the_french_formatter_actually_produces_french():
    """La garde ci-dessus interdit le mauvais chemin ; celle-ci vérifie le bon.

    Sans elle, remplacer `date_fr` par un formateur muet passerait : plus aucun
    `strftime` fautif, et plus aucun jour non plus.
    """
    from datetime import datetime

    from app.services.time_format import WEEKDAY_SHORT, format_date_short

    # 2026-09-05 est un samedi.
    assert format_date_short(datetime(2026, 9, 5, 7, 54)) == "Sam 05/09"
    assert set(WEEKDAY_SHORT) == {1, 2, 3, 4, 5, 6, 7}
    assert WEEKDAY_SHORT[1] == "Lun" and WEEKDAY_SHORT[7] == "Dim"


def test_the_short_labels_are_derived_not_copied():
    """Deux tables à la main divergent au premier ajout.

    C'est la faute que cette tranche corrige ailleurs — on ne l'introduit pas
    en la corrigeant.
    """
    from app.services.time_format import WEEKDAY_LABELS, WEEKDAY_SHORT

    attendu = {k: v[:3] for k, v in WEEKDAY_LABELS.items()}
    assert WEEKDAY_SHORT == attendu, (
        "les abrégés ne dérivent plus des noms complets"
    )


def test_the_history_screen_renders_a_french_day(client):
    """Bout en bout, sur l'écran qui portait le défaut."""
    from app.services.time_format import WEEKDAY_SHORT

    body = client.get("/history").text

    # ⚠ ON CHERCHE UNE DATE, PAS UN MOT. Ma première écriture testait la
    # sous-chaîne « Mon » — et le produit a un écran qui s'appelle « Mon plan »,
    # présent dans la navigation de CHAQUE page. La garde accusait donc la
    # navigation d'être en anglais. Une recherche de sous-chaîne dans du HTML
    # rendu attrape toujours autre chose que ce qu'on vise.
    anglais = re.findall(
        r"\b(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+\d{2}/\d{2}\b", body
    )
    assert not anglais, f"jours anglais rendus dans une date : {sorted(set(anglais))}"
    # Et le pendant : la page n'est pas simplement devenue muette.
    assert any(j in body for j in WEEKDAY_SHORT.values()) or "Aucune séance" in body, (
        "aucun jour français rendu — le formateur a-t-il cessé de dire le jour ?"
    )
