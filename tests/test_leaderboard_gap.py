"""`Sb_UI_CLASSEMENT_01` — l'écart au voisin, et ce qu'il remplace.

Un classement ne répond pas « combien de points » : un total absolu n'a pas
d'échelle, personne ne sait si 600 est beaucoup. Il répond « où suis-je, et à
quelle distance ». L'écart au voisin est la seule donnée qui rend la liste
actionnable, et le produit l'avait déjà — il ne la disait pas.

Ce qu'il remplace : `moy.`, une moyenne sans unité qui valait le même nombre
pour tout le monde dès que les séances se ressemblaient.

Les invariants gardés ici sont ceux qui, cassés, produisent un écran FAUX plutôt
que laid — c'est la distinction que ce dépôt a payé cher à ne pas faire.
"""
from __future__ import annotations

import re
from pathlib import Path

from app.services.leaderboard import LeaderboardEntry, _attach_gaps

TEMPLATE = Path(__file__).resolve().parents[1] / "app" / "templates" / "leaderboard.html"


def _entries(n: int) -> list[LeaderboardEntry]:
    return [
        LeaderboardEntry(
            rank=i + 1, username=f"u{i}", total_points=0.0, counted_sessions=1,
            avg_points=None, last_session_score=None, grade="A", grade_label="",
        )
        for i in range(n)
    ]


# ---------------------------------------------------------------------------
# Le signe PORTE le sens — l'inverser rend un écran faux, pas moche
# ---------------------------------------------------------------------------

def test_the_leader_sees_a_lead_and_everyone_else_sees_a_deficit():
    e = _entries(3)
    _attach_gaps(e, [600.0, 480.0, 300.0])

    assert e[0].points_gap == 120, "le premier doit voir son AVANCE, positive"
    assert e[0].gap_rank == 2, "le premier se compare au second"

    assert e[1].points_gap == -120, "le second doit voir son RETARD, négatif"
    assert e[1].gap_rank == 1

    assert e[2].points_gap == -180, "l'écart se lit au VOISIN, pas au premier"
    assert e[2].gap_rank == 2


def test_a_lone_competitor_has_no_gap_and_not_a_zero():
    """`None`, pas `0`. Zéro signifierait « à égalité », ce qui est faux."""
    e = _entries(1)
    _attach_gaps(e, [600.0])
    assert e[0].points_gap is None
    assert e[0].gap_rank is None


def test_the_gap_is_computed_on_raw_points_not_on_the_rounded_display():
    """Deux arrondis successifs déplacent l'écart d'une unité.

    600,4 et 480,4 s'affichent « 600 » et « 480 » — un lecteur attend 120.
    Arrondir CHAQUE point avant de soustraire donnerait aussi 120 ici, mais
    600,4 / 479,6 donnerait 121 au lieu de 120,8 → 121. Le piège est réel dès
    que les décimales tombent de part et d'autre de 0,5 : on garde donc la
    soustraction sur les valeurs brutes, arrondie une seule fois.
    """
    e = _entries(2)
    _attach_gaps(e, [600.4, 479.6])
    assert e[0].points_gap == 121, (
        "l'écart doit être arrondi UNE fois, sur la différence brute"
    )


def test_an_exact_tie_reads_as_zero_not_as_absent():
    """Deux ex æquo ont bien un écart, et il vaut zéro."""
    e = _entries(2)
    _attach_gaps(e, [500.0, 500.0])
    assert e[1].points_gap == 0


# ---------------------------------------------------------------------------
# Ce que la surface rend
# ---------------------------------------------------------------------------

def test_the_average_is_gone_from_the_surface():
    """`moy.` valait le même nombre pour tout le monde et n'avait pas d'unité."""
    src = re.sub(r"\{#.*?#\}", "", TEMPLATE.read_text(encoding="utf-8"), flags=re.DOTALL)
    assert "moy." not in src, (
        "la moyenne est de retour sur le classement : elle n'a pas d'échelle et "
        "ne dit pas ce que l'écran est censé répondre"
    )


def test_the_negative_sign_is_a_real_minus_not_a_hyphen():
    """Sur des chiffres tabulaires en colonne, le trait d'union décale la colonne.

    Python rend `-` ; le gabarit doit écrire U+2212 à la main.
    """
    src = re.sub(r"\{#.*?#\}", "", TEMPLATE.read_text(encoding="utf-8"), flags=re.DOTALL)
    assert "−" in src, "le signe négatif de l'écart n'est pas un vrai moins"


def test_the_score_formula_is_stated_exactly_once(client):
    """Elle l'était DEUX fois, et les deux versions divergeaient.

    En haut une version approximative, en bas la version juste — avec « work
    sets » en anglais. Une règle énoncée deux fois différemment est une règle
    qu'on ne peut pas croire.
    """
    body = client.get("/leaderboard").text
    assert body.count("Score = qualité") == 1, (
        "la formule du score est énoncée plusieurs fois, ou plus du tout"
    )
    assert "work sets" not in body, "« work sets » est encore rendu"


def test_the_privacy_badge_speaks_french(client):
    """Le badge qui rassure était le seul à parler anglais.

    `/squads` porte le même badge en français depuis toujours.
    """
    body = client.get("/leaderboard").text
    assert "Privacy first" not in body
    assert "Confidentialité" in body


def test_the_document_title_matches_the_screen(client):
    """L'écran s'appelle « Classement » ; son titre disait « Leaderboard »."""
    body = client.get("/leaderboard").text
    assert "<title>Classement" in body, (
        "le titre du document ne dit pas le nom de l'écran — c'est ce que voient "
        "l'onglet, l'historique et le partage"
    )
