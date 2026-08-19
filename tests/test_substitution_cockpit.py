"""Sb_SUBSTITUTION_COCKPIT_01 — la substitution existait déjà ; on la BORNE.

Audit préalable : le service (`can_substitute`, `compute_suggestions` N1/N2/N3),
la persistance (`substituted_name` posté au même formulaire d'exercice) et le
bloc cockpit (`.substitute-picker`) étaient **déjà en place et exposés**. Rien
de tout cela n'est reconstruit.

Le défaut mesuré était la QUANTITÉ : en liste directe (N1+N2, hors élargies),
push-a affichait 6 · 6 · 5 · 4 · 5 · 5 · 5 candidats — un mini-catalogue au
milieu d'une série, ce que le brief refuse explicitement.

Le surplus est **démis, pas supprimé** : il rejoint la disclosure « élargies »
existante. Aucun candidat ne disparaît, aucune valeur postable ne change.
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
CARD = ROOT / "app/templates/_partials/exercise_card.html"

#: Plafond de la liste directe en séance.
COCKPIT_CAP = 4

#: Un catalogue global n'a rien à faire au milieu d'une séance.
CATALOG_MARKERS = (
    'type="search"', 'name="q"', 'name="search"',
    "Rechercher un exercice", "Tous les exercices", "Catalogue complet",
)


def _card_src() -> str:
    return CARD.read_text(encoding="utf-8")


def _sub_block() -> str:
    src = _card_src()
    start = src.index('class="segmented segmented--stacked"')
    return src[start:start + 4500]


# ───────── A3 — la liste directe est bornée ─────────


def _rendered_session(client) -> str:
    r = client.post("/sessions", data={"template_slug": "push-a"},
                    follow_redirects=False)
    sid = int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))
    return client.get(f"/sessions/{sid}").text


def test_the_direct_list_is_capped_on_every_card(client):
    """Assertion RENDUE, pas une lecture de gabarit.

    Sur chaque carte : au plus 4 radios de substitution hors de la disclosure
    « élargies ». Avant plafonnement, push-a en montrait jusqu'à 6 en liste
    directe.
    """
    body = _rendered_session(client)

    # MIGRÉ — le picker est passé dans la ligne L3 : sa classe porte
    # désormais `l3__item` en tête, et il n'est plus enveloppé d'un `<div>`.
    # Le PLAFOND de 4, lui, est inchangé — c'est ce que la garde protège.
    pickers = re.findall(
        r'<details class="l3__item session-focus__alternatives.*?</details>',
        body, re.DOTALL,
    )
    assert pickers, "no substitute picker rendered"

    for index, picker in enumerate(pickers):
        elargi = re.search(r'<details class="sub-elargi">.*?</details>',
                           picker, re.DOTALL)
        hidden = elargi.group(0).count('name="substituted_name"') if elargi else 0
        total = picker.count('name="substituted_name"')
        # -1 : l'option « prescrit », qui n'est pas une alternative.
        visible = total - 1 - hidden
        assert visible <= COCKPIT_CAP, (
            f"card #{index}: {visible} alternatives shown directly, cap is "
            f"{COCKPIT_CAP} — a mid-session catalogue is what this slice removes"
        )


def test_the_cap_is_explicit_in_the_template():
    src = _sub_block()
    assert "_cap = 4" in src, "the cockpit cap must be explicit, not implicit"
    assert "_vis_n1" in src
    assert "_vis_n2" in src


def test_the_cap_slices_n1_before_n2():
    """L'ordre de proximité du service est respecté : N1 remplit d'abord."""
    src = _sub_block()
    i_n1 = src.index("_vis_n1 = _n1_all[:_cap]")
    i_room = src.index("_n2_room = _cap - (_vis_n1 | length)")
    assert i_n1 < i_room, "N1 must be sliced before N2 gets its remaining room"


def test_the_tier_order_is_still_n1_then_n2_then_n3():
    """Garde héritée : l'ordre des tiers reste lisible dans la source."""
    block = _sub_block()
    i1 = block.index("grouped.get('N1'")
    i2 = block.index("grouped.get('N2'")
    i3 = block.index("grouped.get('N3'")
    assert i1 < i2, "N1 must precede N2"
    assert i2 < i3, "N2 must precede N3"


# ───────── rien n'est perdu ─────────


def test_the_overflow_is_demoted_not_deleted():
    """Le surplus rejoint la disclosure existante — il reste postable."""
    src = _sub_block()
    assert "_overflow = _n1_all[(_vis_n1 | length):] + _n2_all[(_vis_n2 | length):] + _n3_all" in src, (
        "the overflow must carry the remainder of N1 and N2 plus all of N3"
    )
    assert "{% for s in _overflow %}" in src, "overflow must still be rendered"


def test_every_candidate_still_posts_substituted_name():
    src = _sub_block()
    assert src.count('name="substituted_name"') >= 4, (
        "prescribed option + each tier loop must post the same field"
    )
    assert 'value="{{ s.name }}"' in src


def test_the_prescribed_option_still_posts_an_empty_value():
    assert 'name="substituted_name" value=""' in _sub_block()


def test_the_checked_candidate_is_still_the_persisted_one():
    assert "se.substituted_name == s.name" in _sub_block()


# ───────── A2 / A4 — local, jamais un catalogue ─────────


def test_the_picker_lives_inside_the_exercise_card():
    """Contrôle LOCAL : il vit dans la carte, pas dans une coque globale."""
    src = _card_src()
    assert "substitute-picker" in src
    detail = (ROOT / "app/templates/session_detail.html").read_text(encoding="utf-8")
    assert "substitute-picker" not in detail, (
        "the picker must not become a session-level navigator"
    )


def test_no_global_catalog_leaks_into_the_session(client):
    src = _card_src()
    for marker in CATALOG_MARKERS:
        assert marker not in src, f"global catalog marker in the cockpit: {marker}"


# ───────── A5 — prévu vs réalisé ─────────


def test_the_planned_identity_is_never_overwritten():
    """`substituted_name` est un champ SÉPARÉ ; le snapshot prévu reste.

    Si un jour le réalisé écrasait `exercise_name_snapshot`, l'historique
    perdrait l'intention du programme — la contrainte #1 du dépôt.
    """
    router = (ROOT / "app/routers/sessions.py").read_text(encoding="utf-8")
    assert "se.substituted_name = sub_name" in router
    assert "se.exercise_name_snapshot =" not in router, (
        "the planned identity must never be reassigned at runtime"
    )


def test_the_card_shows_the_planned_name_on_the_prescribed_option():
    assert "se.exercise_name_snapshot" in _sub_block()


def test_substitution_stays_gated_on_can_substitute():
    router = (ROOT / "app/routers/sessions.py").read_text(encoding="utf-8")
    assert "if sub_name and can_substitute(se):" in router, (
        "substituting after a logged work set would rewrite a performed set"
    )


# ───────── A10 — nom accessible ─────────


def test_the_picker_summary_has_an_accessible_name():
    src = _card_src()
    match = re.search(
        r'<summary class="l3__trigger substitute-picker__summary[^>]*>', src)
    assert match, "le déclencheur du picker n'est plus rendu"
    assert "aria-label=" in match.group(0)


# ───────── A9 — sans JS ─────────


def test_the_picker_is_a_native_details_with_no_script():
    src = _card_src()
    assert '<details class="l3__item session-focus__alternatives' in src
    assert "addEventListener" not in src
    assert "onclick" not in src
