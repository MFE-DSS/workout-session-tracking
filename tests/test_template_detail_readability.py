"""Sx_UI_07.4 — Template Detail Readability.

Template-only readability pass on /library/{slug} (template_detail.html):
additive microcopy only. All programme data preserved — exercise codes/names/
set_scheme/notes/rep_targets, focus, cardio note, suggested_label, back link,
empty state. No POST form (none existed, none added), no route/service/data/JS
change.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TPL = ROOT / "app" / "templates" / "template_detail.html"
PAGES_ROUTER = ROOT / "app" / "routers" / "pages.py"
SESSIONS_ROUTER = ROOT / "app" / "routers" / "sessions.py"


def _render(client, slug="push-a"):
    r = client.get(f"/library/{slug}", follow_redirects=False)
    assert r.status_code == 200, r.text[:300]
    return r.text


# ───────── 1. additive microcopy present ─────────


def test_detail_has_fiche_programme_note(client):
    html = _render(client)
    assert "Fiche programme" in html
    assert "structure prévue avant lancement" in html


def test_detail_has_structure_label_and_final_note(client):
    html = _render(client)
    assert "Structure de séance" in html
    assert "Les charges et reps réelles se saisissent dans la séance active." in html


# ───────── 2. preserved contract ─────────


def test_detail_keeps_back_link_and_title(client):
    html = _render(client)
    assert "← Programmes" in html
    # exercise structure preserved (codes / set schemes rendered)
    assert "exercise__code" in html
    assert "exercise__scheme" in html


def test_detail_keeps_exercise_data_and_rep_ranges(client):
    """Exercise codes, names, schemes and rep ranges still render."""
    html = _render(client)
    assert "exercise-list" in html
    assert "sets__range" in html  # rep ranges rendered
    # at least one known push-a exercise word present (from real catalog)
    assert "incliné" in html.lower() or "lourd" in html.lower() or "développé" in html.lower()


def test_strength_detail_still_hides_cardio_prefix(client):
    """Regression: a strength template must not show the 'Cardio :' prefix
    (existing test_library invariant preserved)."""
    html = _render(client, "push-a")
    assert "Cardio :" not in html
    assert "suggested_label" not in html  # raw key must not leak


# ───────── 3. non-regression: no form, routes/services untouched ─────────


def test_start_cta_form_present():
    """Sx_TPL_01 reversed the Sx_UI_07.4 decision: the fiche is now
    ACTIONABLE. A single start-session POST form is present and legitimate
    (was `test_no_post_form_added` — re-oriented to the new truth, never
    weakened; the CTA is a real, intended behaviour)."""
    src = TPL.read_text(encoding="utf-8")
    assert "<form" in src
    assert 'method="post"' in src
    assert "create_session" in src
    assert "Démarrer cette séance" in src
    # exactly one start form (single CTA — no double-start)
    assert src.count('action="{{ url_for(\'create_session\') }}"') == 1


def test_pages_router_not_modified():
    src = PAGES_ROUTER.read_text(encoding="utf-8")
    assert "Fiche programme · structure prévue avant lancement." not in src


def test_sessions_router_not_modified():
    src = SESSIONS_ROUTER.read_text(encoding="utf-8")
    assert "Fiche programme · structure prévue avant lancement." not in src


# ───────── 4. non-goals: no JS, no BI/physique link, no data change ─────────


def test_no_js_or_bi_physique_link_in_detail():
    src = TPL.read_text(encoding="utf-8")
    assert "<script" not in src
    assert "addEventListener" not in src
    assert "/body/intelligence" not in src
    assert "/physique" not in src


def test_detail_diff_is_additive_only():
    """The template still renders all data-bound fields (no field removed)."""
    src = TPL.read_text(encoding="utf-8")
    for token in (
        "template.name", "template.focus", "template.cardio_note",
        "template.suggested_label", "ex.code", "ex.name", "ex.set_scheme",
        "ex.notes", "ex.rep_targets", "rt.min_reps", "rt.max_reps",
    ):
        assert token in src, f"data-bound field removed: {token}"


def test_no_forbidden_wording():
    src = TPL.read_text(encoding="utf-8").lower()
    for tok in (
        "diagnostic", "médical", "score de santé", "vérité corporelle",
        "programme optimal",
    ):
        assert tok not in src, f"forbidden token {tok!r}"
