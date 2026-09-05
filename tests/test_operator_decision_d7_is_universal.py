"""`OPERATOR_DECISION D7` — appliquée PARTOUT, pas seulement où c'était commode.

D7 (`UX4_03B`) a retiré « Streak ». Le motif écrit dans le dépôt est un motif
PRODUIT :

    « Le compteur de jours consécutifs punissait un jour de repos correctement
      pris, et venait d'un second producteur aux règles différentes de celui du
      moteur comportemental. »

Deux gardes existaient déjà — et **chacune ne regardait qu'un seul gabarit** :

* `test_coach_report.py`            → bannit « Streak » du rapport coach
* `test_ux4_progress_signals.py`    → le bannit de `/progress`

Pendant ce temps, **quatre** surfaces le rendaient toujours : `squad_detail`,
`squad_compare`, `_partials/profile_preview` et `user_profile`. Toutes les
quatre sont des surfaces SOCIALES — ce que les autres voient de vous. Le motif
produit y est pire qu'ailleurs : sur un classement d'escouade, un compteur qui
punit un repos bien pris fait du repos un désavantage compétitif public.

C'est le motif « garde aveugle par périmètre » : **la garde existe, elle ne
regarde pas où est le défaut.** Ce fichier la rend universelle — il balaie TOUS
les gabarits, pas une liste.

Ce qui N'EST PAS gardé ici, délibérément : `BehavioralState.streak_days`. Le
moteur comportemental garde son compteur, qui n'est pas rendu et que
`test_streak_days_is_still_computed` protège déjà. Ne pas rendre n'est pas
supprimer.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

TEMPLATES = Path(__file__).resolve().parents[1] / "app" / "templates"
SERVICES = Path(__file__).resolve().parents[1] / "app" / "services"

#: `python:S1192` — quatre copies suffisent à déclencher la règle, et ce
#: dépôt trébuche dessus assez souvent pour que l'éviter coûte moins cher
#: que la diagnostiquer.
_ENC = "utf-8"


def _uncommented(src: str) -> str:
    """Retire les commentaires Jinja.

    Un commentaire `{# … #}` qui ÉNONCE la décision doit pouvoir nommer
    « Streak » — sinon la garde interdirait d'expliquer pourquoi on l'a retiré.
    C'est déjà la convention de `test_ux4_progress_signals`.
    """
    return re.sub(r"\{#.*?#\}", "", src, flags=re.DOTALL)


def _visible_text(src: str) -> str:
    """Le texte réellement rendu entre balises, hors commentaires.

    ⚠ CETTE FONCTION AVAIT UN ANGLE MORT, ET IL A COÛTÉ UNE OCCURRENCE.

    Elle extrayait avec `>([^<>{}]+)<`, c'est-à-dire en EXCLUANT les accolades
    du jeu de caractères. Conséquence : toute phrase visible **coupée par une
    expression Jinja** devenait invisible à la garde, puisque le motif ne
    pouvait plus atteindre le `<` suivant.

    Le cas trouvé, sur le classement :

        Dernière session : {{ e.last_session_score ... }}/100<br>

    « session » est rendu à l'écran, dans une infobulle, et la garde ne le
    voyait pas. Mesuré sur tout le dépôt : l'angle mort ne coûtait qu'UNE
    occurrence — mais c'est la même faute que celles que ce fichier traque,
    commise dans le fichier qui les traque : **borner ce qu'on a pensé à
    regarder**.

    La correction ne consiste pas à élargir le jeu de caractères — il faut
    NEUTRALISER Jinja d'abord, puis extraire :

    * `{% … %}` devient un saut de ligne : un bloc de contrôle COUPE
      réellement le texte rendu, le remplacer par du vide souderait deux
      phrases qui ne se touchent jamais à l'écran ;
    * `{{ … }}` devient `·` : une expression rend quelque chose, donc elle ne
      coupe pas la phrase — la remplacer par du vide ferait apparaître des mots
      collés qui n'existent pas.
    """
    src = _uncommented(src)
    src = re.sub(r"\{%.*?%\}", "\n", src, flags=re.DOTALL)
    src = re.sub(r"\{\{.*?\}\}", "·", src, flags=re.DOTALL)
    return " ".join(re.findall(r">([^<>]+)<", src))


ALL_TEMPLATES = sorted(TEMPLATES.rglob("*.html"))


def test_the_sweep_actually_sees_the_templates():
    """Un balayage qui ne trouve aucun fichier est vert pour rien.

    C'est la 5e forme de « garde qui ne garde rien » : borner ce qu'on a pensé
    à regarder sans vérifier qu'on regarde quelque chose.
    """
    assert len(ALL_TEMPLATES) > 40, (
        f"{len(ALL_TEMPLATES)} gabarits trouvés — le balayage ne porte sur rien"
    )


@pytest.mark.parametrize("tpl", ALL_TEMPLATES, ids=lambda p: p.name)
def test_no_template_renders_a_daily_streak(tpl: Path):
    """AUCUN gabarit ne rend un compteur de jours consécutifs.

    Universel par construction : la liste est le résultat d'un `rglob`, pas une
    énumération. Un gabarit ajouté demain est couvert sans rien éditer ici.
    """
    visible = _visible_text(tpl.read_text(encoding=_ENC)).lower()
    for banned in ("streak", "jours de série", "série en cours", "🔥"):
        assert banned not in visible, (
            f"{tpl.name} rend « {banned} » — `OPERATOR_DECISION D7` a retiré le "
            f"compteur de jours consécutifs : il punit un repos correctement pris"
        )


@pytest.mark.parametrize("tpl", ALL_TEMPLATES, ids=lambda p: p.name)
def test_no_template_reads_a_streak_attribute(tpl: Path):
    """Ne pas AFFICHER le mot ne suffit pas : ne pas LIRE la donnée.

    Une garde qui n'interdit que le libellé laisse passer une colonne renommée
    « Constance » qui rendrait la même valeur.
    """
    src = _uncommented(tpl.read_text(encoding=_ENC))
    assert not re.search(r"\.streak\b", src), (
        f"{tpl.name} lit encore un attribut `streak` — D7 retire la MÉTRIQUE, "
        f"pas seulement son libellé"
    )


def test_only_the_behavioral_engine_still_computes_a_streak():
    """Un seul producteur, et c'est celui qui n'est pas rendu.

    La décision D7 soupçonnait « un second producteur ». Il y en avait TROIS :
    `behavioral.BehavioralState.streak_days` (conservé, non rendu),
    `profile_metrics.streak_days` et `squad._compute_streak`. Les deux derniers
    n'existaient que pour alimenter l'affichage.
    """
    producers = []
    for py in sorted(SERVICES.rglob("*.py")):
        tree = ast.parse(py.read_text(encoding=_ENC))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if "streak" in node.name.lower():
                    producers.append(f"{py.name}:{node.name}")

    assert producers == [], (
        "un producteur de streak destiné à l'affichage subsiste : "
        f"{producers} — D7 n'en laisse qu'un, le champ du moteur comportemental, "
        "qui n'est pas une fonction et n'est pas rendu"
    )


def test_the_behavioral_field_is_still_there():
    """Ne pas rendre n'est pas supprimer — l'autre moitié de la décision."""
    import dataclasses

    from app.services.behavioral import BehavioralState

    fields = {f.name for f in dataclasses.fields(BehavioralState)}
    assert "streak_days" in fields, (
        "le moteur comportemental a perdu son compteur : D7 retire un AFFICHAGE, "
        "elle ne demande pas de cesser de mesurer"
    )


# ---------------------------------------------------------------------------
# Vocabulaire — « séance », jamais « session »
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tpl", ALL_TEMPLATES, ids=lambda p: p.name)
def test_no_template_labels_a_count_in_english(tpl: Path):
    """« Sessions 30j » est un anglicisme, et il a survécu à sa propre correction.

    Le commentaire de D7 dans `coach_report.html` affirme « même vocabulaire que
    Progression » — deux lignes sous un libellé « Sessions 30j ». Écrire qu'on a
    aligné le vocabulaire ne l'aligne pas.
    """
    visible = _visible_text(tpl.read_text(encoding=_ENC))
    offenders = re.findall(r"\b[Ss]essions?\b(?!\s*/)", visible)
    assert not offenders, (
        f"{tpl.name} rend {offenders} — le produit dit « séance », "
        f"comme Progression depuis `fc786a2`"
    )
