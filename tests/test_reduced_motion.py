"""Sb_UI_09.1 — Reduced-Motion Global (1st build of Sx_UI_09).

The global stylesheet (app.css) gains a `@media (prefers-reduced-motion: reduce)`
block that neutralises decorative transitions/animations across the whole shell
(universal WCAG 2.2 AA pattern). The repo's transitions are decorative only
(opacity/color/background/border/width), so no information is lost when reduced.
CSS-only — no template/route/service/JS/colour change; existing scoped
reduced-motion blocks (session_focus, body_intelligence) are preserved.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_CSS = ROOT / "app" / "static" / "css" / "app.css"
FOCUS_CSS = ROOT / "app" / "static" / "css" / "session_focus.css"


def _app_css() -> str:
    return APP_CSS.read_text(encoding="utf-8")


# ───────── global reduced-motion block ─────────


def test_app_css_has_reduced_motion_block():
    assert "@media (prefers-reduced-motion: reduce)" in _app_css()


def test_reduced_motion_targets_universal_selector():
    """The global block applies to *, *::before, *::after (not a fragile list)."""
    css = _app_css()
    m = re.search(
        r"@media \(prefers-reduced-motion: reduce\)\s*\{(.*?)\}\s*\}",
        css, re.DOTALL,
    )
    assert m, "reduced-motion block not found"
    body = m.group(1)
    assert "*" in body
    assert "::before" in body
    assert "::after" in body


def test_reduced_motion_neutralises_transitions_and_animations():
    css = _app_css()
    block = css[css.index("Sb_UI_09.1 — Reduced-Motion Global"):]
    assert "transition-duration: 0.01ms" in block
    assert "animation-duration: 0.01ms" in block
    assert "animation-iteration-count: 1" in block


def test_reduced_motion_uses_important():
    """!important is required to override component transitions."""
    css = _app_css()
    block = css[css.index("Sb_UI_09.1 — Reduced-Motion Global"):]
    assert block.count("!important") >= 3


# ───────── non-regression ─────────


def test_scoped_reduced_motion_blocks_preserved():
    """Existing session_focus reduced-motion block is untouched."""
    focus = FOCUS_CSS.read_text(encoding="utf-8")
    assert "@media (prefers-reduced-motion: reduce)" in focus


def test_no_new_hex_colour_in_reduced_motion():
    css = _app_css()
    block = css[css.index("Sb_UI_09.1 — Reduced-Motion Global"):]
    assert not re.search(r"#[0-9a-fA-F]{3,6}", block), "raw hex in reduced-motion block"


def test_reduced_motion_no_display_or_layout_change():
    """The block must not hide content or change layout (motion only)."""
    css = _app_css()
    block = css[css.index("Sb_UI_09.1 — Reduced-Motion Global"):]
    assert "display: none" not in block
    assert "visibility: hidden" not in block


def test_existing_transitions_still_present():
    """The build only ADDS a reduced-motion guard; base transitions remain
    (they animate at full speed when the user has no reduced-motion pref)."""
    css = _app_css()
    # the reduced-motion block lives at the very end; base transitions precede it
    head = css[: css.index("Sb_UI_09.1 — Reduced-Motion Global")]
    assert "transition:" in head


def test_page_renders_with_reduced_motion_css(client):
    """Smoke: the stylesheet is served and a page renders (no CSS parse break)."""
    r = client.get("/", follow_redirects=False)
    assert r.status_code == 200
    css_resp = client.get("/static/css/app.css")
    assert css_resp.status_code == 200
    assert "prefers-reduced-motion" in css_resp.text
