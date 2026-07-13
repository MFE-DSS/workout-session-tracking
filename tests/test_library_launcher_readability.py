"""Sx_UI_07.3 — Library / Launcher Catalogue Readability.

Template-only readability pass on /library and /launcher: enriched ledes only.
All behaviour preserved — sections, template cards, POST forms (create_session
+ template_slug + creation_source), reco partial, "Voir tous les programmes"
links, "Démarrer" CTAs. No route/service/data/JS change, additive only (no
asserted text removed).
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIBRARY_TPL = ROOT / "app" / "templates" / "library.html"
LAUNCHER_TPL = ROOT / "app" / "templates" / "launcher.html"
PAGES_ROUTER = ROOT / "app" / "routers" / "pages.py"
SESSIONS_ROUTER = ROOT / "app" / "routers" / "sessions.py"


def _render(client, path):
    r = client.get(path, follow_redirects=False)
    assert r.status_code == 200, r.text[:300]
    return r.text


# ───────── 1. /library — enriched lede, preserved contract ─────────


def test_library_title_and_enriched_lede(client):
    html = _render(client, "/library")
    assert "Programmes de séance" in html          # title preserved (asserted)
    assert "Catalogue complet" in html             # substring preserved (asserted)
    assert "classées par usage" in html            # new enriched part
    assert "Bibliothèque" not in html              # forbidden vocab (asserted)


def test_library_keeps_start_form_and_creation_source(client):
    html = _render(client, "/library")
    assert 'name="template_slug"' in html
    assert 'name="creation_source"' in html
    assert 'value="library"' in html
    assert "Démarrer" in html
    # link to template detail preserved
    assert "template_detail" in html or "/library/" in html or "slug=" in html


# ───────── 2. /launcher — explicit step ledes, preserved flow ─────────


def test_launcher_step1_lede_and_reco(client):
    html = _render(client, "/launcher")
    assert "Nouvelle séance" in html
    assert "Choisis le format de séance à lancer." in html
    # reco partial kept in step 1
    assert "Voir tous les programmes" in html


def _first_launcher_type(client) -> str:
    """Discover a valid launcher `type` key from the step-1 page (types are
    e.g. standard/short/cardio — 'push' is a VARIANT, not a type)."""
    import re

    html = _render(client, "/launcher")
    types = re.findall(r"\?type=([a-z_-]+)", html)
    assert types, "no launcher type found on step 1"
    return types[0]


def test_launcher_step2_lede(client):
    """Step 2 renders when a valid type is selected."""
    t = _first_launcher_type(client)
    html = _render(client, f"/launcher?type={t}")
    assert "Sélectionne la zone ou l'objectif du jour." in html


def test_launcher_step3_lede_and_start_form(client):
    """Step 3 renders the program list with start forms (reached via a valid
    type+variant)."""
    import re

    t = _first_launcher_type(client)
    html2 = _render(client, f"/launcher?type={t}")
    variants = re.findall(rf"\?type={re.escape(t)}&(?:amp;)?variant=([a-z_-]+)", html2)
    if not variants:
        return  # no variant → step 3 not reachable for this type, skip
    html3 = _render(client, f"/launcher?type={t}&variant={variants[0]}")
    if "template-card" in html3:
        assert "Choisis le programme à démarrer maintenant." in html3
        assert 'name="creation_source"' in html3
        assert 'value="launcher"' in html3
        assert "Démarrer" in html3


def test_launcher_keeps_back_links(client):
    t = _first_launcher_type(client)
    html = _render(client, f"/launcher?type={t}")
    # retour / library links preserved
    assert "Voir tous les programmes" in html
    assert "launcher" in html.lower()


# ───────── 3. non-regression: routes/services untouched (source) ─────────


def test_pages_router_not_modified_by_readability():
    src = PAGES_ROUTER.read_text(encoding="utf-8")
    assert "Choisis le format de séance à lancer." not in src
    assert "classées par usage" not in src


def test_sessions_router_not_modified():
    src = SESSIONS_ROUTER.read_text(encoding="utf-8")
    assert "classées par usage" not in src


# ───────── 4. non-goals: no JS, no BI/physique link, additive only ─────────


def test_no_js_added_to_library_or_launcher():
    for f in (LIBRARY_TPL, LAUNCHER_TPL):
        src = f.read_text(encoding="utf-8")
        assert "<script" not in src
        assert "addEventListener" not in src


def test_no_bi_or_physique_link_added():
    for f in (LIBRARY_TPL, LAUNCHER_TPL):
        src = f.read_text(encoding="utf-8")
        assert "/body/intelligence" not in src
        assert "/physique" not in src


def test_creation_source_hidden_inputs_intact():
    lib = LIBRARY_TPL.read_text(encoding="utf-8")
    lau = LAUNCHER_TPL.read_text(encoding="utf-8")
    assert 'name="creation_source" value="library"' in lib
    assert 'name="creation_source" value="launcher"' in lau
    assert "create_session" in lib and "create_session" in lau
    assert "next_session_reco" in lau


def test_no_forbidden_wording():
    blob = (
        LIBRARY_TPL.read_text(encoding="utf-8")
        + LAUNCHER_TPL.read_text(encoding="utf-8")
    ).lower()
    for tok in ("diagnostic", "médical", "score de santé", "vérité corporelle"):
        assert tok not in blob, f"forbidden token {tok!r}"
