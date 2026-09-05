"""Le relevé souverain de `Progression` — `AUREN_VISUAL_BACKBONE §4`.

CE QUE CES GARDES TIENNENT, ET POURQUOI ELLES EXISTENT

L'écran s'appelle « Progression ». Mesuré au rendu avant cette tranche, ses
cinq plus grosses typographies étaient des **comptages** :

    « 3 zones touchées »              34 px
    « 3 » « 10 » « 100 % » « 4 »      28 px
    ────────────────────────────────────────
    « Tirage front câble 66 → 72 »    13 px
    « +6 kg »                         11 px   ← le plus petit texte de la page

Un rapport de 1 à 3, à l'envers. Aucune garde du dépôt ne regardait cela : ni
un test de rendu, ni Sonar, ni la CI — c'est un fait de HIÉRARCHIE, et la
hiérarchie ne se lit que dans les tailles comparées entre elles.

Ces gardes comparent donc des tailles, pas des pixels rendus. Elles n'ont pas
besoin d'un navigateur, et elles mordent sur la seule chose qui puisse
réintroduire le défaut : quelqu'un qui remonte un comptage ou descend le
relevé.
"""
from __future__ import annotations

import pathlib
import re
from datetime import UTC, datetime, timedelta

from app.services.progression_facts import (
    KEEP_OCCURRENCES,
    ExerciseProgression,
    Performance,
    ProgressionFacts,
)
from app.services.progression_view import build_progression_view, format_trace

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = ROOT / "app/static/css/app.css"
PARTIAL = ROOT / "app/templates/_partials/progression.html"


def _perf(w, r, *, sid=1, days=0):
    return Performance(
        session_id=sid, at=datetime.now(UTC) - timedelta(days=days),
        weight=w, reps=r, score=None, template="Push A",
    )


def _prog(slug="x", name="X", perfs=()):
    from app.services.progression_facts import _attach_delta

    p = ExerciseProgression(slug=slug, name=name, occurrences=list(perfs))
    _attach_delta(p)
    return p


def _font_size(selector: str) -> int:
    """La taille déclarée pour ce sélecteur, en pixels.

    On lit le bloc qui SUIT le sélecteur jusqu'à l'accolade fermante, et non
    tout le fichier : `.ze__n` et `.ze__n--partial` partagent un préfixe, et
    une recherche naïve rendait la taille du second pour le premier.
    """
    src = CSS.read_text(encoding="utf-8")
    # Le sélecteur exact, suivi éventuellement d'espaces puis de `{`.
    m = re.search(
        re.escape(selector) + r"\s*\{(.*?)\}", src, flags=re.S,
    )
    assert m, f"sélecteur introuvable dans app.css : {selector}"
    f = re.search(r"font-size:\s*(\d+)px", m.group(1))
    assert f, f"aucun font-size déclaré pour {selector}"
    return int(f.group(1))


# ───────────── la hiérarchie, qui EST la décision ─────────────

#: Le rang `SECTION` du socle typographique (`§3.2`), déclaré 22 px. Un
#: comptage y vit ou plus bas ; le rang `DISPLAY` (32 px) est au readout.
RANG_SECTION_PX = 22


def test_no_count_reaches_the_rank_below_the_sovereign_readout():
    """Un comptage vit au rang `SECTION` (22 px) ou plus bas, jamais entre.

    ⚠ CETTE GARDE A ÉTÉ RÉÉCRITE PARCE QUE LA PREMIÈRE NE MORDAIT PAS.

    Elle demandait seulement `readout > comptage`. En replantant le défaut
    d'origine — `.kpi-card__value` remis à 28 px — elle est restée **verte** :
    28 est bien inférieur à 32. Or 28 contre 32 n'est pas une hiérarchie,
    c'est une égalité de fait à l'œil, et c'est très exactement l'écran que la
    tranche corrige.

    Une garde qui n'interdit que l'inversion stricte laisse revenir
    l'écrasement, qui produit le même défaut. Le seuil est donc accroché à
    l'échelle documentée plutôt qu'à une comparaison relative : il n'est pas
    négociable par un pixel.
    """
    readout = _font_size(".lead__value")
    for compteur in (".kpi-card__value", ".ze__n"):
        taille = _font_size(compteur)
        assert taille <= RANG_SECTION_PX, (
            f"{compteur} vaut {taille}px : entre le rang SECTION "
            f"({RANG_SECTION_PX}px) et le relevé souverain ({readout}px), "
            f"il n'y a pas de rang — le comptage redispute le premier regard"
        )
        assert readout > taille, f"{compteur} dépasse le relevé souverain"


def test_the_partial_marker_stays_smaller_than_the_count_it_qualifies():
    """« partielle » est un MOT posé à la place d'un chiffre : lui donner la
    taille du compte rendrait un minimum observé aussi affirmatif qu'un
    dénombrement exhaustif.

    Cette garde existe parce que descendre `.ze__n` de 34 à 22 px aurait
    silencieusement effacé l'écart avec `--partial`, resté à 20 px.
    """
    for variante in (".ze__n--partial", ".ze__n--unknown"):
        assert _font_size(variante) < _font_size(".ze__n"), variante


def test_the_readout_matches_the_viseur_metric_rank():
    """32 px — la même valeur que `--font-size-metric-lg` du viseur.

    Le même rôle typographique reçoit le même rang d'une surface à l'autre,
    sans quoi « relevé souverain » ne veut rien dire en dehors de la séance.
    """
    focus = (ROOT / "app/static/css/session_focus.css").read_text(encoding="utf-8")
    m = re.search(r"--font-size-metric-lg:\s*(\d+)px", focus)
    assert m, "le viseur ne déclare plus `--font-size-metric-lg`"
    assert _font_size(".lead__value") == int(m.group(1))


# ───────────── la promotion n'est PAS un classement ─────────────

def test_the_lead_is_the_most_recent_not_the_largest_delta():
    """Promouvoir « le plus gros progrès » déciderait que l'écart est un
    mérite — ce que `build_progression_rows` interdit explicitement. Et cela
    exigerait de comparer des kilos entre exercices, l'addition sans référent
    que la voie cardio refuse déjà entre deux machines.

    Ici le second exercice a un écart six fois plus grand ; c'est le PREMIER,
    le plus récemment pratiqué, qui est promu.
    """
    view = build_progression_view(ProgressionFacts(exercises=[
        _prog(slug="a", name="Récent, petit écart",
              perfs=[_perf(24.0, 10), _perf(25.0, 10)]),
        _prog(slug="b", name="Ancien, gros écart",
              perfs=[_perf(72.0, 10, days=9), _perf(66.0, 10, days=16)]),
    ]))
    assert view["lead"]["slug"] == "a"


def test_the_promoted_row_leaves_the_list():
    """Le rendre deux fois ferait passer une promotion pour une duplication.

    Vu au rendu : la première maquette laissait la ligne dans la liste, et
    l'exercice apparaissait en relevé souverain PUIS en tête de liste.
    """
    view = build_progression_view(ProgressionFacts(exercises=[
        _prog(slug="a", perfs=[_perf(24.0, 10), _perf(25.0, 10)]),
        _prog(slug="b", perfs=[_perf(72.0, 10), _perf(66.0, 10)]),
    ]))
    assert view["lead"]["slug"] == "a"
    assert [r["slug"] for r in view["rows"]] == ["b"]


def test_no_lead_when_nothing_is_comparable():
    """Un seul passage ne compare rien : le relevé n'a pas d'objet et ne doit
    pas rendre un cadre vide."""
    view = build_progression_view(ProgressionFacts(exercises=[
        _prog(perfs=[_perf(14.0, 12)]),
    ]))
    assert view["lead"] is None
    assert view["awaiting"]


# ───────────── la trace : ce qui était calculé puis jeté ─────────────

def test_the_trace_returns_the_occurrences_that_were_being_discarded():
    """`KEEP_OCCURRENCES` en retient six ; `latest`/`previous` n'en lisaient
    que deux. Les quatre autres étaient calculées, puis perdues avant la vue.
    """
    charges = [30.0, 29.0, 26.0, 25.0, 24.0, 23.0]
    # Le service range du plus récent au plus ancien.
    p = _prog(perfs=[_perf(w, 10, days=i)
                     for i, w in enumerate(reversed(charges))])
    assert len(p.occurrences) == KEEP_OCCURRENCES
    # La trace se lit du plus ancien au plus récent, comme une chronologie.
    assert format_trace(p) == ["30", "29", "26", "25", "24", "23"]


def test_the_trace_says_something_the_delta_cannot():
    """Le point de la trace, énoncé comme un fait vérifiable.

    `−1 kg` décrit les deux dernières séances. Il est IDENTIQUE pour une
    décrue régulière et pour un accident isolé — la trace, elle, les sépare.
    """
    regulier = _prog(perfs=[_perf(w, 10, days=i) for i, w in
                            enumerate([23.0, 24.0, 25.0, 26.0])])
    accident = _prog(perfs=[_perf(w, 10, days=i) for i, w in
                            enumerate([23.0, 24.0, 24.0, 24.0])])
    assert regulier.delta.weight_delta == accident.delta.weight_delta
    assert format_trace(regulier) != format_trace(accident)


def test_the_trace_carries_no_verdict():
    """Ni seuil, ni tendance nommée, ni couleur : la trace est une suite de
    charges. Le dernier segment se distingue par une BORDURE — un état porte
    toujours une forme (`no-color-only-state`)."""
    src = CSS.read_text(encoding="utf-8")
    m = re.search(r"\.lead__occ\.is-latest\s*\{(.*?)\}", src, flags=re.S)
    assert m, "le marqueur du dernier segment a disparu"
    assert "border-color" in m.group(1), (
        "le dernier segment ne se distingue plus que par la couleur"
    )


# ───────────── le patron d'instrument, tenu ─────────────

def test_the_rank_two_affordance_lives_on_the_title():
    """`§4.2` règle 5 — « le rang 2 vit sur le titre, pas dans un bouton
    concurrent ». Ma maquette posait « Les 6 occurrences → » sous les puits ;
    le socle l'interdit, et c'est le socle qui a raison.
    """
    src = re.sub(r"\{#.*?#\}", " ", PARTIAL.read_text(encoding="utf-8"),
                 flags=re.S)
    m = re.search(r'<a class="lead__title"[^>]*href="\{\{ ?L\.href ?\}\}"', src)
    assert m, "le titre du relevé ne porte plus le lien vers l'historique"


def test_the_reference_is_system_blue_not_a_verdict_colour():
    """`§4.1` — « référence : la dernière fois, en bleu système ». Le bleu dit
    la PROVENANCE. Distinguer « avant » de « maintenant » par une teinte de
    jugement aurait fait lire une charge allégée comme un échec."""
    src = CSS.read_text(encoding="utf-8")
    m = re.search(r"\.lead__ref\s*\{(.*?)\}", src, flags=re.S)
    assert m, ".lead__ref a disparu"
    assert "--role-origin-system" in m.group(1), (
        "la référence n'est plus rendue avec le rôle de provenance"
    )
