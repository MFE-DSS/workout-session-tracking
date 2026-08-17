"""OQ_POSITIONAL_CSS_01 — colour follows surface identity, never DOM rank.

WHY THIS EXISTS
---------------
Muscle colour used to be selected by the rank of a group inside the SVG
(`#auren-plate-region-shoulders .auren-mf-view-front > g:nth-of-type(3) path`).
Nothing in the repository guaranteed that rank: the frozen SHAs protect the
files against *editing*, not against a *regeneration* of the Blender → Potrace →
Inkscape pipeline emitting the same geometry in a different group order. A
regenerated plate could therefore have recoloured the wrong muscle silently —
no test would have failed, and the page would still have looked plausible.

Selection now goes through the contractual surface token carried by each path id
(`auren-plate-region-{region}--[{frame}-]{surface}-{NNN}`,
Sb_BODYMAP_IDENTITY_CONTRACT_01 §5.1). These guards keep it that way.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "app" / "static" / "css" / "app.css"
PARTIALS = ROOT / "app" / "templates" / "_partials"
CONTRACT_DOC = ROOT / "docs" / "strategy" / "Sb_BODYMAP_IDENTITY_CONTRACT_01.md"

PLATE_REGIONS = ("chest", "shoulders", "posterior")

#: Surfaces that carry a colour of their own, and the token each rule must match.
#: `delt-anterior`, `gluteus` and `hero` are deliberately absent: they keep the
#: shared fallback accent, exactly as before this build.
SURFACE_RULES = {
    "-delt-lateral-": "--accent-hover",
    "-delt-posterior-": "--accent-muted",
    "-hamstring-": "--accent-soft",
}


def _css() -> str:
    return CSS.read_text(encoding="utf-8")


def _plate_block() -> str:
    """The Muscle Focus plate-colour block, brace-matched, not sliced to EOF.

    Deliberately not `css[css.index(marker):]`: that shortcut is exactly what
    produced the false positive fixed in Sb_BODYMAP_FRAME_ATLAS_01.
    """
    css = _css()
    start = css.index("/* plate colours (tokens)")
    end = css.index("/* Sb_BODYMAP_FRAME_ATLAS_01", start)
    return css[start:end]


def _plate_declarations() -> str:
    """The same block with CSS comments stripped.

    Declaration-level guards must not read prose. The comments here deliberately
    NAME the banned constructs (`nth-of-type`, `!important`) to explain why they
    are banned; a guard that greps raw text flags its own rationale — the same
    mistake that made an anti-medical guard trip on its own disclaimer.
    """
    return re.sub(r"/\*.*?\*/", "", _plate_block(), flags=re.DOTALL)


# ───────────────── A1 — no colour by DOM rank ─────────────────

def test_a1_no_plate_rule_selects_by_nth_of_type():
    """The defect itself: a plate selector that counts group ranks."""
    stripped = re.sub(r"/\*.*?\*/", "", _css(), flags=re.DOTALL)
    offenders = [
        line.strip()
        for line in stripped.splitlines()
        if "nth-of-type" in line and "auren-plate-region" in line
    ]
    assert offenders == [], f"colour still depends on DOM rank: {offenders}"


def test_a1_no_plate_rule_selects_a_group_by_position():
    """Broader net: any `> g:nth-*` inside the plate colour block."""
    assert not re.search(r">\s*g:nth-", _plate_declarations())


def test_a1_plate_colour_block_names_no_group_rank():
    for token in ("nth-of-type", "nth-child", "first-of-type", "last-of-type"):
        assert token not in _plate_declarations(), f"positional selector {token!r} returned"


# ───────────────── A2 — colour follows identity ─────────────────

def test_a2_every_coloured_surface_is_selected_by_its_id_token():
    block = _plate_block()
    for token, colour in SURFACE_RULES.items():
        pattern = rf'path\[id\*="{re.escape(token)}"\]\s*\{{\s*fill:\s*var\({re.escape(colour)}\)'
        assert re.search(pattern, block), (
            f"surface {token!r} is not coloured by identity with {colour}"
        )


def test_a2_selected_tokens_exist_in_the_shipped_assets():
    """A rule matching nothing is worse than no rule: it looks like coverage."""
    all_ids = "".join(
        (PARTIALS / f"muscle_focus_plate_{r}.svg").read_text(encoding="utf-8")
        for r in PLATE_REGIONS
    )
    for token in SURFACE_RULES:
        assert token in all_ids, f"no shipped path id contains {token!r}"


def test_a2_each_token_resolves_to_exactly_one_surface():
    """Guards against a substring that would colour two different muscles."""
    for token in SURFACE_RULES:
        matched: set[str] = set()
        for region in PLATE_REGIONS:
            svg = (PARTIALS / f"muscle_focus_plate_{region}.svg").read_text(encoding="utf-8")
            for path_id in re.findall(r'id="([^"]+)"', svg):
                if token in path_id:
                    matched.add(re.sub(r"-\d{3}$", "", path_id).split("--", 1)[1].split("-", 1)[-1])
        assert len(matched) == 1, f"{token!r} spans several surfaces: {sorted(matched)}"


def test_a2_fallback_specificity_is_zeroed_so_order_cannot_decide():
    """`:where()` contributes 0, so per-surface rules win strictly.

    Without this, the surface rules would tie with the fallbacks (0,2,1) and the
    winner would depend on their position in the stylesheet — trading DOM order
    for source order rather than removing the fragility.
    """
    block = _plate_block()
    assert ":where(.auren-mf-context)" in block
    assert ":where(.auren-mf-hero, .auren-mf-part)" in block


def test_a2_no_important_and_no_id_selector_needed():
    block = _plate_declarations()
    assert "!important" not in block
    assert "#auren-plate-region" not in block


# ───────────────── A8 — the open question is closed ─────────────────

def test_a8_open_question_is_marked_resolved():
    doc = CONTRACT_DOC.read_text(encoding="utf-8")
    assert "OQ_POSITIONAL_CSS_01" in doc
    marker = doc[doc.index("OQ_POSITIONAL_CSS_01"):]
    assert "RESOLVED" in doc or "RÉSOLUE" in doc, "the OQ must be closed in the contract"
    assert marker  # the reference itself is kept for history


def test_a8_contract_no_longer_claims_the_defect_is_live():
    doc = CONTRACT_DOC.read_text(encoding="utf-8")
    assert "**bloquant** pour tout pilotage par la donnée" not in doc, (
        "the contract still describes the defect as live"
    )
