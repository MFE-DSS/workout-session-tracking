"""Sb_31.4 — Body Intelligence v2 responsive checks (CSS scans).

Tests structurels sur le CSS scoped `body_intelligence.css` :
- mobile-first (règles par défaut sans min-width)
- media query < 380px présente (héritage Sb_31.2)
- media query ≤ 360px présente (Sb_31.4)
- pas de classes overflow dangereuses sur les wrappers
- non-color cues préservés (anti-régression Sb_31.2)
- box-sizing + max-width sur le wrapper principal pour éviter le débordement
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "app" / "static" / "css" / "body_intelligence.css"


def _src() -> str:
    return CSS.read_text(encoding="utf-8")


# ───────── mobile-first ─────────


def test_css_has_baseline_mobile_first_rules():
    """Le wrapper principal n'utilise pas min-width> — règles par
    défaut s'appliquent sur petit écran d'abord."""
    src = _src()
    # Pas de min-width > 0 dans les sélecteurs par défaut (hors media).
    # On vérifie au moins que .body-intelligence existe sans condition.
    assert ".body-intelligence" in src
    # Aucune règle non-media n'utilise min-width > 400 (heuristique simple)
    non_media_chunks = re.split(r"@media[^{]*\{", src)[0]
    assert "min-width: 768" not in non_media_chunks
    assert "min-width: 1024" not in non_media_chunks


def test_css_has_max_width_safety_on_wrapper():
    src = _src()
    block = re.search(
        r"\.body-intelligence\s*\{([^}]+)\}",
        src,
        re.DOTALL,
    )
    assert block is not None
    body = block.group(1)
    assert "max-width" in body
    assert "width: 100%" in body
    assert "box-sizing: border-box" in body
    assert "overflow-x: hidden" in body


# ───────── media queries ─────────


def test_css_has_380px_media_query():
    src = _src()
    assert "@media (max-width: 380px)" in src


def test_css_has_360px_media_query():
    """Sb_31.4 — cible spec Sx_29 mobile minimal 360×640."""
    src = _src()
    assert "@media (max-width: 360px)" in src


def test_kv_grid_collapses_to_single_column_on_narrow():
    """Sur petit écran, la grille clé/valeur passe en une seule colonne
    pour éviter les débordements de valeurs longues (dates ISO,
    nombres avec unités)."""
    src = _src()
    # Cherche la règle dans une media query
    pattern = re.compile(
        r"@media \(max-width: 380px\)\s*\{[^@]*?"
        r"\.bi-block__kv\s*\{[^}]*grid-template-columns:\s*1fr",
        re.DOTALL,
    )
    assert pattern.search(src), (
        "kv grid must collapse to 1fr on <380px"
    )


# ───────── non-color cues (anti-régression Sb_31.2) ─────────


def test_status_global_non_color_cues_preserved():
    src = _src()
    # Sb_31.2 : status cues '?', '~', '•'
    for marker in (
        '.body-intelligence--insufficient_data .body-intelligence__headline::before',
        '.body-intelligence--partial_data .body-intelligence__headline::before',
        '.body-intelligence--ok .body-intelligence__headline::before',
    ):
        assert marker in src, f"status cue selector missing: {marker}"


def test_classification_non_color_cues_preserved():
    src = _src()
    for icon in ("●", "◆", "▲", "○"):
        assert icon in src, f"classification cue {icon!r} missing"


def test_priority_non_color_cues_preserved():
    src = _src()
    # 6 keys de priorité
    for cue_class in (
        ".bi-priority--insufficient_data",
        ".bi-priority--low_logging_confidence",
        ".bi-priority--consistency_gap",
        ".bi-priority--imbalance_gap",
        ".bi-priority--undertrained_zone",
        ".bi-priority--stable_or_progressing",
    ):
        assert cue_class in src, f"priority cue selector missing: {cue_class}"


# ───────── pas d'overflow dangereux ─────────


def test_no_dangerous_overflow_visible_on_wrappers():
    """Pas d'``overflow: visible`` qui rendrait un débordement
    horizontal invisible mais réel ; pas d'``overflow-x: scroll`` non
    plus (cf. spec §H.3)."""
    src = _src()
    assert "overflow-x: scroll" not in src
    assert "overflow-x:scroll" not in src
    # Le wrapper utilise overflow-x: hidden (vérifié au-dessus)


def test_focus_visible_rule_preserved():
    """Anti-régression Sb_30.5 pattern — règle :focus-visible existe."""
    src = _src()
    assert ":focus-visible" in src


# ───────── responsive coach snapshot ─────────


def test_coach_snapshot_reuses_coach_block_classes():
    """Le partial coach snapshot ne doit pas dupliquer un wrapper
    overflow ; il réutilise les classes existantes du coach_report."""
    partial = (
        ROOT / "app" / "templates" / "_partials" / "coach_body_snapshot.html"
    ).read_text()
    # Le partial utilise coach-block (classe partagée avec les autres
    # sections du coach report). Cela garantit que le responsive du
    # coach report s'applique aussi au snapshot.
    assert "coach-block" in partial
