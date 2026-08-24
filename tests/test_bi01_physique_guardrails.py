"""Sb_BI_01.3 — Physique Surface Guardrails · **CONTRAT RENVERSÉ PAR `TRAIN1-C`**.

CE QUE CE FICHIER GARDAIT
--------------------------
`Sb_BI_01.3` avait choisi l'« Option B prudente » : encadrer le score de
`/physique` **sans le retirer**. Un de ses tests s'appelait littéralement
`test_physique_keeps_score_grade_radar`, et il exigeait que le score sur 100,
la lettre A/B/C et le radar restent rendus.

CE QUI L'A RENVERSÉ
--------------------
Ordre opérateur `TRAIN1-C` : `/physique` cesse d'être un second produit
analytique. Les trois objets sont retirés, la route redirige vers `/progress`.

La prudence de `Sb_BI_01.3` était cohérente à sa date — mais la microcopie
qu'elle ajoutait (« Score indicatif, non médical ») ne relativisait pas la
doctrine : elle la légitimait en la commentant. Le pilier d'exposition du score
valait `hard_sets / (cible × semaines) × 100`, soit exactement le « % de
cible » que `zone_exposure` s'interdit de dire. Un avertissement ne corrige pas
un calcul.

CE FICHIER RESTE, ET NE SE CONTENTE PAS DE CONSTATER. Deux propriétés de sûreté
qu'il portait n'ont pas de raison de mourir avec la surface — le vocabulaire
interdit et l'absence de script — et elles suivent le contenu là où il a
atterri : `progress.html` et ses partiels.

Les gardes de la convergence elle-même vivent dans
`test_train1c_progression_consolidation.py`.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "app" / "templates"
PROGRESS_TEMPLATE = TEMPLATES / "progress.html"
MUSCLE_SCORING = ROOT / "app" / "services" / "muscle_scoring.py"
LEADERBOARD_SVC = ROOT / "app" / "services" / "leaderboard.py"
USER_PROFILE_TPL = TEMPLATES / "user_profile.html"
INDEX_TPL = TEMPLATES / "index.html"
BI_TEMPLATE = TEMPLATES / "body_intelligence.html"

GUARDRAIL_MARKER = "physique-guardrails"


def _progression_surfaces() -> list[Path]:
    """La page et les partiels QU'ELLE INCLUT — dérivés, pas listés à la main."""
    body = re.sub(r"\{#.*?#\}", " ", PROGRESS_TEMPLATE.read_text(encoding="utf-8"),
                  flags=re.S)
    return [PROGRESS_TEMPLATE] + [
        TEMPLATES / name for name in re.findall(r'include\s+"([^"]+)"', body)
    ]


# ───────── 1. le renversement, nommé ─────────


def test_the_physique_surface_no_longer_exists():
    """`test_physique_keeps_score_grade_radar` exigeait le contraire.

    Il est conservé sous forme renversée plutôt que supprimé : quelqu'un qui
    lit `Sb_BI_01.3` doit tomber sur ce qui l'a annulé, pas sur un vide.
    """
    assert not (TEMPLATES / "physique.html").exists()


def test_the_guardrail_microcopy_left_with_the_score_it_qualified(client):
    """Une mise en garde sur un objet absent est de la prose. Elle part avec
    lui — et pas seulement de la page : de tout le dépôt rendu."""
    for path in TEMPLATES.rglob("*.html"):
        src = path.read_text(encoding="utf-8")
        assert "Score indicatif, non médical" not in src, path.name
        assert GUARDRAIL_MARKER not in src, path.name


# ───────── 2. Body Intelligence n'est pas orpheline ─────────


def test_body_intelligence_keeps_an_entry_point(client):
    """Le lien vers `/body/intelligence` vivait AUSSI sur `/physique`.

    Le retirer sans vérifier aurait pu rendre une surface inatteignable —
    exactement la « soustraction seule » que `CLAUDE.md §5.3` interdit. Deux
    entrées subsistent, toutes deux derrière le même drapeau.
    """
    entries = [
        p for p in TEMPLATES.rglob("*.html")
        if p.name != "body_intelligence.html"
        and "url_for('body_intelligence')" in p.read_text(encoding="utf-8")
    ]
    assert len(entries) >= 2, f"entrées restantes : {[p.name for p in entries]}"


def test_no_dead_link_to_body_intelligence_when_the_flag_is_off(client):
    """Jamais un lien mort vers un 404 : c'était la moitié saine du contrat
    `Sb_BI_01.3`, et elle survit intacte.

    ⚠ VÉRIFIÉE AU RENDU, PAS DANS LA SOURCE. La première écriture cherchait
    `body_intelligence_enabled` avant le lien dans chaque gabarit — et rougissait
    sur `coach_body_snapshot.html`, qui est gardé **par son parent**
    (`{% if body_snapshot %}`, lui-même produit sous drapeau). Le gabarit avait
    raison, la garde avait tort : elle vérifiait UN mécanisme au lieu de la
    propriété. On sert les deux surfaces et on regarde ce qui sort.
    """
    for path in ("/profile", "/coach-report"):
        r = client.get(path, follow_redirects=True)
        assert r.status_code == 200, f"{path} -> {r.status_code}"
        assert "/body/intelligence" not in r.text, path


# ───────── 3. non-régression : le service partagé et ses consommateurs ─────────


def test_muscle_scoring_not_modified_by_guardrails():
    """The guardrails must not touch compute_physique_dashboard."""
    src = MUSCLE_SCORING.read_text(encoding="utf-8")
    assert GUARDRAIL_MARKER not in src
    assert "Lecture synthétique" not in src


def test_leaderboard_and_userprofile_untouched():
    lb = LEADERBOARD_SVC.read_text(encoding="utf-8")
    up = USER_PROFILE_TPL.read_text(encoding="utf-8")
    for src in (lb, up):
        assert GUARDRAIL_MARKER not in src


def test_home_and_bi_templates_untouched_by_guardrails():
    home = INDEX_TPL.read_text(encoding="utf-8")
    bi = BI_TEMPLATE.read_text(encoding="utf-8")
    assert GUARDRAIL_MARKER not in home
    assert GUARDRAIL_MARKER not in bi


# ───────── 4. les deux propriétés de sûreté SUIVENT LE CONTENU ─────────


def test_no_js_on_the_progression_surfaces():
    """`test_no_js_added_to_physique`, déplacé sur la surface qui a absorbé le
    contenu. La propriété n'avait rien de spécifique à Physique : tout ce
    train est SSR sans une ligne de script."""
    for path in _progression_surfaces():
        src = path.read_text(encoding="utf-8")
        for token in ("<script", "onclick", "addEventListener"):
            assert token not in src, f"{path.name} introduit du script"


def test_no_forbidden_wording_on_the_progression_surfaces():
    """`test_no_forbidden_wording_in_physique`, déplacé de même.

    Le vocabulaire interdit — diagnostic, composition corporelle, bilan
    médical — l'était parce que le produit ne le mesure pas. Rien de cela ne
    dépendait de la page où il aurait pu apparaître : laisser cette liste
    mourir avec `physique.html` aurait retiré une garde de fond en effaçant
    une surface.
    """
    forbidden = (
        "diagnostic", "body fat", "morphotype", "attractivité",
        "pathologie", "score de santé", "vérité corporelle",
        "composition corporelle", "bilan médical",
    )
    for path in _progression_surfaces():
        src = path.read_text(encoding="utf-8").lower()
        for tok in forbidden:
            assert tok not in src, f"forbidden token {tok!r} in {path.name}"
