"""Sb_UI_10.1 — Visible Product Strings (SPIGNOS → Auren) in the app shell.

The visible product name in base.html (the authenticated shell) migrates from
« SPIGNOS » to « Auren » : <title>, apple-mobile-web-app-title, topbar brand,
footer. SPIGNOS stays the INTERNAL name (repo/code/routes/models) — no code,
route, class, manifest or asset change here. Standalone auth pages
(welcome/login/register) are OUT of scope (Sb_UI_10.3).

Template-only.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE_TPL = ROOT / "app" / "templates" / "base.html"
MANIFEST = ROOT / "app" / "static" / "manifest.webmanifest"
STATIC_DIR = ROOT / "app" / "static"


def _get(client, path="/"):
    r = client.get(path, follow_redirects=False)
    assert r.status_code == 200, f"{path} -> {r.status_code}: {r.text[:200]}"
    return r.text


# ───────── visible product name = Auren ─────────


def test_title_shows_auren(client):
    html = _get(client)
    assert "· Auren</title>" in html


def test_apple_title_is_auren(client):
    html = _get(client)
    assert re.search(
        r'<meta name="apple-mobile-web-app-title" content="Auren"\s*/?>', html
    )


def test_topbar_brand_shows_auren(client):
    html = _get(client)
    # brand link keeps its class + route, only the visible text changes
    assert re.search(r'<a class="topbar__brand"[^>]*>Auren</a>', html)


def test_footer_shows_auren(client):
    """⚠ REPOINTÉE PAR `UI-CP6 SHELL` — LE PORTEUR CHANGE, LA PROPRIÉTÉ NON.

    Cette garde lisait `<small>Auren</small>` dans le pied de page de
    l'accueil. `UI-CP6 Q3` retire le pied générique des surfaces d'INSTRUMENT :
    il coûtait 135 px sur mobile pour un mot-marque et un lien que la
    navigation secondaire offre déjà, et un pied de page est un objet de
    DOCUMENT — l'avoir sur un instrument brouille la frontière que
    `AUREN_INSTRUMENTS §2bis` demande de rendre perceptible.

    Ce que la garde protège — **le nom produit visible est « Auren »** — n'a
    pas bougé d'un pouce. Il est simplement porté ailleurs sur un instrument,
    par le mot-marque de la topbar, et le pied le porte toujours là où il
    subsiste : sur les documents.

    Les deux moitiés sont donc vérifiées, chacune là où elle vit. Épingler le
    pied sur l'accueil reviendrait à exiger son retour.
    """
    # Sur un DOCUMENT, le pied survit — et il nomme le produit.
    document = _get(client, "/export")
    assert "<small>Auren</small>" in document, (
        "le pied du document ne nomme plus le produit"
    )

    # Sur un INSTRUMENT, il n'y a plus de pied — et le nom reste visible.
    instrument = _get(client)
    assert 'class="foot"' not in instrument, (
        "le pied générique est revenu sur une surface d'instrument"
    )
    assert re.search(r'<a class="topbar__brand"[^>]*>Auren</a>', instrument), (
        "plus aucun porteur du nom produit sur un instrument"
    )


# ───────── SPIGNOS no longer visible in the shell ─────────


def test_no_visible_spignos_in_rendered_shell(client):
    """The rendered shell must not display « SPIGNOS » to the user (comments
    are stripped at render, so a rendered occurrence would be visible copy)."""
    html = _get(client)
    assert "SPIGNOS" not in html


def test_base_template_visible_strings_are_auren():
    """Source check: the 4 visible strings are Auren; SPIGNOS only remains in a
    technical comment documenting the internal name."""
    src = BASE_TPL.read_text(encoding="utf-8")
    assert '<title>{{ page_title }} · Auren</title>' in src
    assert '<meta name="apple-mobile-web-app-title" content="Auren" />' in src
    assert '>Auren</a>' in src  # topbar brand
    assert "<small>Auren</small>" in src


# ───────── invariants: routes / classes / nav / logout unchanged ─────────


def test_nav_links_and_classes_preserved(client):
    html = _get(client)
    # `TRAIN1-C` — « Physique » a quitté la liste : la surface est retirée et
    # sa route redirige vers `/progress`. Un libellé de navigation vers elle
    # serait un lien qui rebondit.
    for label in (
        "Accueil", "Programmes", "Historique", "Progression",
        "Classement", "Squads", "Profil", "Coach", "Déconnexion",
    ):
        assert label in html, f"nav label missing: {label}"
    assert "topbar__brand" in html  # class preserved
    assert "topbar__link" in html


def test_logout_post_form_preserved(client):
    html = _get(client)
    assert 'method="post"' in html


def test_active_nav_preserved(client):
    """aria-current active-nav (Sx_NAV_01) still works."""
    html = _get(client, "/library")
    assert 'aria-current="page"' in html


def test_brand_route_unchanged():
    """The brand still points at url_for('home') — no route renamed."""
    src = BASE_TPL.read_text(encoding="utf-8")
    assert "url_for('home')" in src


# ───────── non-goals: manifest / static / no Orion ─────────


def test_manifest_migrated_to_auren_by_10_2():
    """Sb_UI_10.1 left the manifest generic (« Workout Session Tracking »);
    Sb_UI_10.2 migrated it to « Auren ». This test now asserts the migrated
    state (manifest coverage lives in tests/test_auren_pwa_assets.py)."""
    src = MANIFEST.read_text(encoding="utf-8")
    assert '"name": "Auren"' in src
    assert "Workout Session Tracking" not in src


def test_no_orion_string_introduced():
    src = BASE_TPL.read_text(encoding="utf-8")
    assert "Orion" not in src
    assert "ORION" not in src


def test_no_new_asset_referenced():
    """No new static asset link added (favicon/manifest links unchanged)."""
    src = BASE_TPL.read_text(encoding="utf-8")
    # still the single existing favicon + manifest, no logo/img inserted
    assert src.count("<img") == 0
    assert "icons/favicon.svg" in src


def test_icon_pack_present_after_10_2():
    """Sb_UI_10.1 created no static file; Sb_UI_10.2 shipped the approved Auren
    PNG icon pack + master SVG. Guard that the expected set is present (exact
    dimensions/palette are covered in tests/test_auren_pwa_assets.py)."""
    icons = list((STATIC_DIR / "icons").glob("*"))
    names = {p.name for p in icons}
    assert names == {
        "favicon.svg", "auren-mark.svg",
        "icon-192.png", "icon-512.png", "icon-maskable-512.png",
        "apple-touch-icon.png",
    }, f"unexpected icons set: {names}"
