"""La carte « Semaine planifiée » de l'accueil dit, elle ne compte plus.

LE CONSTAT

Sa ligne souveraine était `4 séances proposées` — un COMPTAGE, en 16 px gras —
tandis que les six créneaux de la première séance, **déjà présents dans la
charge utile**, tenaient en 13 px dessous, sous l'intertitre « Prochaine séance
proposée ».

Même inversion que sur `/plan`, un rang plus bas : le produit avait la
substance et rendait le nombre.

Arbitrage opérateur : variante **F**, compacte. Les noms d'exercices quittent
l'accueil — `Mon plan` les rend correctement depuis sa refonte — et la carte
passe de **306 px à 153 px**, moitié moins. Le service décrit lui-même cette
carte comme du CONTEXTE qui « ne remplace pas la décision du jour » : elle ne
doit pas disputer le hero.
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
PARTIAL = ROOT / "app/templates/_partials/home_coaching_loop.html"
CSS = ROOT / "app/static/css/home.css"
JINJA_COMMENT = re.compile(r"\{#.*?#\}", re.S)


def _corps() -> str:
    """Le gabarit sans ses commentaires.

    Il EXPLIQUE en commentaire ce qu'il ne rend plus (« 4 séances proposées »,
    les noms d'exercices) : une garde qui lit la prose rougirait sur la
    justification du choix. Neuvième occurrence du motif dans ce dépôt.
    """
    return JINJA_COMMENT.sub(" ", PARTIAL.read_text(encoding="utf-8"))


def _font_size(selector: str) -> int:
    src = CSS.read_text(encoding="utf-8")
    m = re.search(re.escape(selector) + r"\s*\{(.*?)\}", src, flags=re.S)
    assert m, f"sélecteur introuvable dans home.css : {selector}"
    f = re.search(r"font-size:\s*(\d+)px", m.group(1))
    assert f, f"aucun font-size déclaré pour {selector}"
    return int(f.group(1))


def test_the_zones_are_the_sovereign_line_not_the_count():
    """Ce que la semaine TRAVAILLE passe devant COMBIEN elle compte."""
    src = _corps()
    zones = src.find("home-wk__zones")
    dose = src.find("home-wk__dose")
    assert zones != -1, "la ligne des zones a disparu"
    assert dose != -1, "la ligne de dose a disparu"
    assert zones < dose, (
        "le comptage repasse devant les zones — c'est l'inversion que la "
        "tranche corrige"
    )


def test_the_count_is_demoted_below_the_zones():
    """Le comptage reste — `CLAUDE.md §5.3` interdit une soustraction seule —
    mais il cesse d'être la ligne souveraine de la carte."""
    assert _font_size(".home-wk__dose") < _font_size(".home-wk__zones")


def test_the_card_stays_below_the_hero():
    """La carte est du CONTEXTE. Le hero de l'accueil porte la décision du
    jour à 24 px ; la carte doit rester sous ce rang, sans quoi deux objets se
    disputent le premier regard."""
    assert _font_size(".home-wk__zones") < 24


def test_the_card_carries_no_inline_style():
    """Six attributs `style` statiques partaient avec la refonte plutôt que
    dans une tranche de nettoyage séparée (`AUREN_VISUAL_BACKBONE §5`).

    La garde est locale à la carte : le cliquet global compte le gabarit
    entier, celle-ci vérifie que ce bloc précis ne les réintroduit pas.
    """
    src = _corps()
    debut = src.find("home-wk")
    # ⚠ Ancré sur une EXPRESSION VIVANTE, pas sur le commentaire « This week »
    # qui délimitait la section : ce commentaire est retiré par `_corps()`,
    # donc l'ancre disparaissait avec lui. Une garde ne peut pas s'orienter
    # sur ce qu'elle vient d'effacer.
    fin = src.find("home.week ")
    assert debut != -1, "le bloc de la carte est introuvable"
    assert fin > debut, "la borne de fin du bloc est introuvable"
    bloc = src[debut:fin]
    assert 'style="' not in bloc, (
        "un style inline est revenu dans la carte « Semaine planifiée »"
    )


def test_zones_are_deduplicated_in_the_service():
    """Une séance peut travailler deux fois la même zone. « Pectoraux ·
    Pectoraux » ne dit rien de plus que « Pectoraux », et gaspille la moitié
    d'une ligne souveraine qui n'en compte que trois."""
    from app.services import home as home_service

    src = pathlib.Path(home_service.__file__).read_text(encoding="utf-8")
    assert "dict.fromkeys" in src, (
        "les zones ne sont plus dédupliquées côté service"
    )


def test_the_empty_case_still_says_something():
    """Aucun créneau exploitable : la carte ne rend pas un cadre vide, elle
    dit le nombre — qui reste vrai. `A4` : jamais un cadre sans contenu."""
    src = _corps()
    bloc = src[src.find("home-wk__zones"):src.find("This week")]
    assert "{% else %}" in bloc, "le cas sans zone n'a plus de branche"
    apres_else = bloc[bloc.find("{% else %}"):]
    assert "pluriel" in apres_else, (
        "la branche vide ne rend plus le nombre de séances"
    )
