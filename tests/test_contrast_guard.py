"""Sb_UI_09.3 — Contrast Guard (3rd & final build of Sx_UI_09).

A guard test locking the WCAG 2.2 AA contrast of the Auren Terminal colour
tokens. The tokens are ALREADY AA-compliant (measured in the Sx_UI_09 spec:
e.g. --fg-dim = 6.06:1 on --bg); this test does NOT change any CSS — it reads
the real token values from app.css and asserts the ratios stay ≥ AA, so any
future change that would drop a text token below AA fails CI.

Pure stdlib (no dependency, no browser, CI-safe). No app/route/service/CSS
change; test-only.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_CSS = ROOT / "app" / "static" / "css" / "app.css"


# ───────── token parsing (from the real :root, not hard-coded) ─────────


def _tokens() -> dict[str, str]:
    """Parse `--name: #hex;` declarations from app.css :root."""
    css = APP_CSS.read_text(encoding="utf-8")
    out: dict[str, str] = {}
    for name, val in re.findall(r"(--[\w-]+):\s*(#[0-9a-fA-F]{6})\s*;", css):
        out.setdefault(name, val)  # first (root) declaration wins
    return out


def _rel_luminance(hex_colour: str) -> float:
    r, g, b = (int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5))

    def _lin(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def _ratio(fg: str, bg: str) -> float:
    l1, l2 = _rel_luminance(fg), _rel_luminance(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


AA_NORMAL = 4.5   # WCAG 2.2 — normal text
AA_LARGE = 3.0    # large text / UI components / graphical objects


# ───────── the tokens exist ─────────


def test_expected_tokens_present():
    t = _tokens()
    for name in ("--bg", "--surface", "--surface-2",
                 "--fg", "--fg-muted", "--fg-dim", "--accent", "--on-accent"):
        assert name in t, f"token {name} missing from app.css :root"


# ───────── text tokens on backgrounds — AA normal (4.5) ─────────


def test_fg_tokens_meet_aa_normal_on_backgrounds():
    t = _tokens()
    backgrounds = ("--bg", "--surface", "--surface-2")
    text = ("--fg", "--fg-muted", "--fg-dim")
    failures = []
    for tx in text:
        for bg in backgrounds:
            r = _ratio(t[tx], t[bg])
            if r < AA_NORMAL:
                failures.append(f"{tx} on {bg}: {r:.2f} < {AA_NORMAL}")
    assert not failures, "AA-normal contrast regressions:\n" + "\n".join(failures)


def test_fg_dim_specifically_locked():
    """--fg-dim (87 usages) is the tightest text token — lock it explicitly."""
    t = _tokens()
    assert _ratio(t["--fg-dim"], t["--bg"]) >= AA_NORMAL


# ───────── accent — AA (used as text/links and UI accent) ─────────


def test_accent_on_bg_meets_aa():
    t = _tokens()
    # amber accent used for links/active text on graphite bg
    assert _ratio(t["--accent"], t["--bg"]) >= AA_NORMAL


def test_on_accent_over_accent_meets_aa():
    """Text drawn on the amber accent (e.g. primary button) must be readable."""
    t = _tokens()
    assert _ratio(t["--on-accent"], t["--accent"]) >= AA_NORMAL


# ───────── borders / UI — AA large (3.0) is enough for non-text ─────────


def test_accent_meets_ui_threshold_on_surfaces():
    t = _tokens()
    for bg in ("--surface", "--surface-2"):
        assert _ratio(t["--accent"], t[bg]) >= AA_LARGE, f"--accent on {bg}"


# ───────── guard is meaningful (sanity) ─────────


def test_ratio_helper_sane():
    # black on white ~= 21, identical colours = 1
    assert round(_ratio("#000000", "#ffffff")) == 21
    assert _ratio("#123456", "#123456") == 1.0


def test_no_css_change_in_this_build():
    """Sb_UI_09.3 is test-only: it locks the acquired AA, changes no token."""
    # the tokens keep their audited values (no silent edit slipped in)
    t = _tokens()
    assert t["--fg-dim"] == "#8A94A0"
    assert t["--bg"] == "#0F1318"
    assert t["--accent"] == "#C8A24B"
