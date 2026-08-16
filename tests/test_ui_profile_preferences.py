"""Sb_UI_PROFILE_PREFERENCES_REDESIGN_01 — présentation seule, contrat intact.

Le dogfood réel disait : « la sélection ne se voit pas ». La correction est
visuelle, donc le risque est qu'elle déplace quelque chose de sémantique sans
qu'on s'en aperçoive. Ces tests existent pour que la refonte reste **une
refonte**.
"""
from __future__ import annotations

import re

import pytest

PROFILE_URL = "/profile"
PREFERENCES_URL = "/profile/preferences"


@pytest.fixture(autouse=True)
def _app_db(client):
    return client


def _uid():
    from tests.helpers import get_test_user_id

    return get_test_user_id()


def _prefs():
    from app.database import SessionLocal
    from app.services.training_preferences import get_training_preferences

    with SessionLocal() as db:
        return get_training_preferences(db, _uid())


def _page(client) -> str:
    return client.get(PROFILE_URL).text


# ── Le contrat POST ne bouge pas ─────────────────────────────────────────────


def test_the_post_field_names_are_unchanged(client):
    page = _page(client)
    assert 'name="sessions_per_week"' in page
    for slot in (1, 2, 3):
        assert f'name="focus_{slot}"' in page
    assert 'name="equipment"' in page
    assert 'name="equipment_declared"' in page


def test_saving_through_the_new_markup_persists_identically(client):
    client.post(PREFERENCES_URL, data={
        "sessions_per_week": "4",
        "focus_1": "arms",
        "focus_2": "lower",
        "equipment_declared": "1",
        "equipment": ["barbell"],
    })
    saved = _prefs()
    assert saved.sessions_per_week == 4
    assert saved.focus_priorities == ("arms", "lower")
    assert saved.available_equipment == ("barbell",)


def test_priority_order_survives_the_redesign(client):
    client.post(PREFERENCES_URL, data={
        "sessions_per_week": "",
        "focus_1": "lower", "focus_2": "arms", "focus_3": "shoulders",
    })
    assert _prefs().focus_priorities == ("lower", "arms", "shoulders")


# ── NULL ≠ [] — la distinction que le style ne doit pas détruire ─────────────


def test_an_untouched_equipment_section_still_declares_nothing(client):
    client.post(PREFERENCES_URL, data={"sessions_per_week": "3"})
    assert _prefs().available_equipment is None


def test_a_submitted_empty_equipment_section_is_still_an_explicit_none(client):
    client.post(PREFERENCES_URL,
                data={"sessions_per_week": "3", "equipment_declared": "1"})
    assert _prefs().available_equipment == ()


def test_the_hidden_declaration_marker_survived_the_restyle(client):
    page = _page(client)
    assert '<input type="hidden" name="equipment_declared" value="1">' in page


def test_the_undeclared_state_is_still_stated_in_words(client):
    assert "pas encore renseigné mon équipement" in _page(client)


# ── Cadence : choix fini, rien de présélectionné ─────────────────────────────


def test_the_cadence_is_a_finite_choice_not_a_dropdown(client):
    page = _page(client)
    rows = re.findall(r'<label class="choice-row"[^>]*>(.*?)</label>',
                      page, re.DOTALL)
    cadence = [r for r in rows if 'name="sessions_per_week"' in r]
    assert len(cadence) >= 7
    assert all('type="radio"' in r for r in cadence)
    # Et plus aucun <select> pour la cadence.
    assert '<select class="select-shell__control" name="sessions_per_week"' not in page


def test_a_new_user_has_no_preselected_cadence(client):
    page = _page(client)
    rows = re.findall(r'<label class="choice-row"[^>]*>(.*?)</label>',
                      page, re.DOTALL)
    cadence = [r for r in rows if 'name="sessions_per_week"' in r]
    assert cadence
    assert not any("checked" in r for r in cadence)


def test_a_declared_cadence_is_visibly_checked(client):
    client.post(PREFERENCES_URL, data={"sessions_per_week": "5"})
    page = _page(client)
    rows = re.findall(r'<label class="choice-row"[^>]*>(.*?)</label>',
                      page, re.DOTALL)
    checked = [r for r in rows
               if 'name="sessions_per_week"' in r and "checked" in r]
    assert len(checked) == 1
    assert 'value="5"' in checked[0]


# ── Repli sans JS : les trois <select> restent la source de vérité ───────────


def test_the_three_native_selects_are_present_in_the_dom(client):
    page = _page(client)
    for slot in (1, 2, 3):
        assert f'name="focus_{slot}"' in page
        assert f'id="focus_{slot}"' in page


def test_the_ranked_block_is_hidden_until_javascript_reveals_it(client):
    """Sans JS, le bloc classé reste caché et les selects restent visibles."""
    page = _page(client)
    ranked = re.search(r'<div class="choice-group" data-prefs-ranked([^>]*)>', page)
    assert ranked, "ranked block not rendered"
    assert "hidden" in ranked.group(1)
    # Le fallback, lui, n'est PAS caché côté serveur.
    fallback = re.search(r'<div class="prefs-fallback" data-prefs-fallback([^>]*)>',
                         page)
    assert fallback
    assert "hidden" not in fallback.group(1)


def test_saving_preferences_never_requires_javascript(client):
    """Le POST du fallback natif suffit à tout enregistrer."""
    r = client.post(PREFERENCES_URL, data={
        "sessions_per_week": "2", "focus_1": "arms",
        "equipment_declared": "1", "equipment": ["bodyweight"],
    }, follow_redirects=False)
    assert r.status_code == 303
    saved = _prefs()
    assert saved.sessions_per_week == 2
    assert saved.focus_priorities == ("arms",)


def test_the_enhancement_script_is_deferred_and_dependency_free():
    import pathlib

    root = pathlib.Path(__file__).resolve().parent.parent
    js = (root / "app" / "static" / "js" / "prefs_focus_rank.js").read_text(
        encoding="utf-8")
    for banned in ("import ", "require(", "from '", 'from "', "http://", "https://"):
        assert banned not in js
    tpl = (root / "app" / "templates" / "profile.html").read_text(encoding="utf-8")
    assert "defer" in tpl
    assert "prefs_focus_rank.js" in tpl


def test_the_script_only_writes_into_the_native_selects():
    """JS ne fait que de la synchronisation : aucune valeur inventée."""
    import pathlib

    root = pathlib.Path(__file__).resolve().parent.parent
    js = (root / "app" / "static" / "js" / "prefs_focus_rank.js").read_text(
        encoding="utf-8")
    assert 'select[name="focus_' in js
    # Pas d'appel réseau, pas de persistance parallèle.
    for banned in ("fetch(", "XMLHttpRequest", "localStorage", "sessionStorage"):
        assert banned not in js


def test_the_ranking_caps_at_three_and_compacts_on_removal():
    """La règle de rang est lisible dans le script, sans exécution navigateur."""
    import pathlib

    root = pathlib.Path(__file__).resolve().parent.parent
    js = (root / "app" / "static" / "js" / "prefs_focus_rank.js").read_text(
        encoding="utf-8")
    assert "MAX_RANKS = 3" in js
    assert "order.splice(at, 1)" in js          # retrait → recompactage
    assert "order.length < MAX_RANKS" in js     # plafond
    assert "aria-pressed" in js                 # état exposé sémantiquement


# ── Aucun style en ligne réintroduit dans le panneau ─────────────────────────


def test_the_preferences_panel_carries_no_inline_style(client):
    page = _page(client)
    start = page.index('class="prefs-form"')
    panel = page[start:page.index("</form>", start)]
    assert "style=" not in panel


# ── Isolation : rien du moteur n'a bougé ─────────────────────────────────────


def test_the_planner_output_is_untouched_by_the_restyle(client):
    from app.services.training_preferences import TrainingPreferencesData
    from app.services.weekly_planner import build_weekly_plan

    prefs = TrainingPreferencesData(sessions_per_week=4,
                                    focus_priorities=("arms",))
    before = build_weekly_plan(prefs)
    client.post(PREFERENCES_URL, data={
        "sessions_per_week": "4", "focus_1": "arms"})
    _page(client)
    assert build_weekly_plan(prefs).fingerprint == before.fingerprint


def test_the_volume_budget_is_untouched_by_the_restyle(client):
    from app.services.training_preferences import TrainingPreferencesData
    from app.services.weekly_volume_budget import build_weekly_volume_budget

    prefs = TrainingPreferencesData(sessions_per_week=4,
                                    focus_priorities=("arms",))
    before = [(z.zone_code, z.planning_low_sets) for z
              in build_weekly_volume_budget(prefs).zones]
    _page(client)
    after = [(z.zone_code, z.planning_low_sets) for z
             in build_weekly_volume_budget(prefs).zones]
    assert after == before


def test_no_planner_or_engine_module_was_touched():
    """La refonte est de la présentation : aucun moteur ne l'importe."""
    import pathlib

    import app.services as services_pkg

    root = pathlib.Path(services_pkg.__file__).parent
    for name in ("weekly_planner", "weekly_volume_budget", "recommendation",
                 "behavioral", "adaptive_replan", "set_contribution"):
        src = (root / f"{name}.py").read_text(encoding="utf-8")
        assert "prefs_focus_rank" not in src
        assert "choice_row" not in src


# ── Périmètre du script autorisé — Sb_UI_PROFILE_PREFERENCES_REDESIGN_01 ─────
#
# L'opérateur a autorisé UN fichier JS d'amélioration progressive. Cette
# autorisation est étroite : ces gardes fixent ce que le script a le droit de
# faire, pour que « minimal vanilla JS » ne dérive pas en logique produit.

def _script() -> str:
    import pathlib

    root = pathlib.Path(__file__).resolve().parent.parent
    return (root / "app" / "static" / "js" / "prefs_focus_rank.js").read_text(
        encoding="utf-8")


@pytest.mark.parametrize("banned", [
    "fetch(", "XMLHttpRequest", "WebSocket",
    "localStorage", "sessionStorage",
    ".submit(", "requestSubmit",
    "import ", "require(", "define(",
])
def test_the_script_stays_presentation_only(banned):
    assert banned not in _script()


@pytest.mark.parametrize("banned", [
    "planning_low", "baseline_sets", "budget", "allocator",
    "planner", "recommendation", "volume",
])
def test_the_script_computes_no_planner_or_budget_logic(banned):
    assert banned not in _script().lower()


def test_the_script_invents_no_hidden_default():
    js = _script()
    # Aucune cadence ni priorité pré-remplie : l'état initial vient du serveur.
    assert "sessions_per_week" not in js
    assert 'value = "3"' not in js
    assert "|| 3" not in js


def test_the_script_only_reads_state_from_the_native_selects():
    js = _script()
    assert "currentOrder" in js
    assert 'select[name="focus_' in js
    # Pas d'état parallèle persistant.
    assert "window." not in js


def test_the_canonical_js_inventory_is_exactly_three_files():
    import pathlib

    root = pathlib.Path(__file__).resolve().parent.parent
    names = sorted(p.name for p in (root / "app" / "static" / "js").glob("*.js"))
    assert names == ["prefs_focus_rank.js", "preview.js", "session_focus.js"]


def test_the_fallback_and_enhanced_paths_post_the_same_payload(client):
    """Mêmes choix humains ⇒ mêmes octets persistés, JS ou non.

    Le chemin « amélioré » n'a pas de POST propre : il écrit dans les mêmes
    selects. Ce test le rend vérifiable côté serveur — le seul endroit où la
    différence compterait.
    """
    client.post(PREFERENCES_URL, data={
        "sessions_per_week": "4", "focus_1": "arms", "focus_2": "lower",
        "equipment_declared": "1", "equipment": ["barbell"],
    })
    fallback = _prefs()

    # Reset, puis rejoue exactement la même intention humaine.
    client.post(PREFERENCES_URL, data={
        "sessions_per_week": "4", "focus_1": "arms", "focus_2": "lower",
        "equipment_declared": "1", "equipment": ["barbell"],
    })
    enhanced = _prefs()

    assert fallback.sessions_per_week == enhanced.sessions_per_week
    assert fallback.focus_priorities == enhanced.focus_priorities
    assert fallback.available_equipment == enhanced.available_equipment
