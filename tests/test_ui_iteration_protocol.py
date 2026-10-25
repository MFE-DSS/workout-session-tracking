"""CLAUDE.md §5.6–5.9 — the four UI iteration guardrails (operator, 2026-10-25).

Every NEW sprint report of a UI slice must carry the four sections defined in
`docs/strategy/AUREN_UI_ITERATION_PROTOCOL.md`: the validated sketch, the
one-information-once inventory (with its data-contract source column), the
comparison with the validated reference, and the single change of the iteration.

A report is a UI slice when it cites `clients/mobile` or the UI delivery contract
(`§5.1`). Reports written before the rule are frozen below, exempt; the list can
only shrink — a NEW report never enters it.

What this guard cannot do, by design: judge a pixel. It makes the operator's
judgement possible and fast; it does not replace it (CLAUDE.md §5).
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
PROTOCOL = DOCS / "strategy" / "AUREN_UI_ITERATION_PROTOCOL.md"

UI_SLICE = re.compile(r"clients/mobile|§ ?5\.1|CLAUDE\.md §5")

REQUIRED_SECTIONS = (
    "## Croquis validé",
    "## Inventaire — une information, une seule fois",
    "## Comparaison avec la référence validée",
    "## Changement unique de l'itération",
)
INVENTORY_HEADER = "| Élément | Information | Source (contrat de données) | Doublon ? |"

#: UI reports that predate the rule (2026-10-25). Frozen: it may only shrink.
EXEMPT = frozenset({
    "SPRINT_Sb_DA_02_2_CALIBRATION_PRIMITIVES_REPORT.md",
    "SPRINT_Sb_DA_02_3_INSTRUMENT_FRAME_EXPLORATION_REPORT.md",
    "SPRINT_Sb_OPS_DEPLOY_FAILURE_HONESTY_01_REPORT.md",
    "SPRINT_Sb_SCI_V2_03_ANY_OF_JOIN_REPORT.md",
    "SPRINT_Sb_SCI_V2_02_IDENTITY_EXPOSURE_REPORT.md",
    "SPRINT_Sb_TRAIN_A_ENVIRONMENT_EXPERIENCE_01_REPORT.md",
    "SPRINT_Sb_TRAIN_A_ENVIRONMENT_ACTIVATION_01_REPORT.md",
    "SPRINT_Sb_UI_DATES_LOCALISEES_01_REPORT.md",
    "SPRINT_Sb_UI_HOME_COCKPIT_01_REPORT.md",
    "SPRINT_Sb_UI_JS_CAPACITY_GUARD_01_REPORT.md",
    "SPRINT_Sb_UI_HOME_WEEKLY_01_REPORT.md",
    "SPRINT_Sb_UI_PROGRAM_DETAIL_01_REPORT.md",
    "SPRINT_Sb_UI_PHANTOM_TOKENS_01_REPORT.md",
    "SPRINT_Sb_UI_PROGRAM_EDITOR_STYLES_01_REPORT.md",
    "SPRINT_Sb_UI_SECTION_RANK_01_REPORT.md",
    "SPRINT_Sb_UI_INLINE_STYLE_RATCHET_01_REPORT.md",
    "SPRINT_Sb_UI_SQUAD_FAMILLE_01_REPORT.md",
    "SPRINT_Sb_UI_PLURIEL_01_REPORT.md",
    "SPRINT_Sb_UI_SQUAD_READABILITY_01_REPORT.md",
    "SPRINT_Sb_UI_SCIENCE_ACCENTS_01_REPORT.md",
    "SPRINT_Sb_UI_PROGRESSION_SOVEREIGN_READOUT_01_REPORT.md",
    "SPRINT_Sb_UI_SEUIL_FRANCAIS_01_REPORT.md",
    "SPRINT_Sb_VNEXT_NATIVE_N0_EXPERIENCE_LAB_REPORT.md",
    "SPRINT_Sb_UI_SESSION_DONE_01_REPORT.md",
    "SPRINT_Sb_VNEXT_MOBILE_EXEC_DOGFOOD_01_REPORT.md",
    "SPRINT_Sb_VNEXT_MOBILE_D9_01_REAL_BACKEND_BRIDGE_REPORT.md",
})


def _ui_reports() -> dict[str, str]:
    return {
        p.name: text
        for p in sorted(DOCS.glob("SPRINT_Sb_*_REPORT.md"))
        if UI_SLICE.search(text := p.read_text(encoding="utf-8"))
    }


def missing_guardrails(text: str) -> list[str]:
    """The guardrail sections a report lacks (empty = compliant)."""
    missing = [s for s in REQUIRED_SECTIONS if s not in text]
    if INVENTORY_HEADER not in text:
        missing.append(f"inventory table header {INVENTORY_HEADER!r}")
    return missing


def test_every_new_ui_report_carries_the_four_guardrails():
    offenders = {
        name: missing_guardrails(text)
        for name, text in _ui_reports().items()
        if name not in EXEMPT and missing_guardrails(text)
    }
    assert not offenders, (
        "UI slice reports missing CLAUDE.md §5.6–5.9 sections "
        f"(see docs/strategy/AUREN_UI_ITERATION_PROTOCOL.md): {offenders}"
    )


def test_the_exemption_list_only_names_reports_that_exist():
    """A frozen list that names ghosts would hide nothing — and hide its own rot."""
    present = {p.name for p in DOCS.glob("SPRINT_Sb_*_REPORT.md")}
    assert EXEMPT <= present, sorted(EXEMPT - present)


def test_the_guard_bites_a_ui_report_without_the_sections():
    """Mutation: the guard must flag a UI report that skips the protocol."""
    bare = "# Sb_X\n\nTouche `clients/mobile/src/ui/X.tsx`. Rendu §5.1 soumis.\n\n**Verdict :** ok\n"
    assert UI_SLICE.search(bare)
    assert len(missing_guardrails(bare)) == len(REQUIRED_SECTIONS) + 1


def test_a_compliant_report_passes():
    full = "\n".join([*REQUIRED_SECTIONS, INVENTORY_HEADER])
    assert missing_guardrails(full) == []


def test_the_protocol_document_defines_every_required_section():
    """The guard and the protocol cannot drift: each section the guard demands is defined there."""
    text = PROTOCOL.read_text(encoding="utf-8")
    for section in REQUIRED_SECTIONS:
        assert section in text, section
    assert INVENTORY_HEADER in text


def test_claude_md_states_the_four_rules():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    for rule in ("5.6 — Croquis validé avant le code", "5.7 — Une information, une seule fois",
                 "5.8 — Comparaison avec la référence validée", "5.9 — Un changement par itération"):
        assert rule in text, rule
    assert "AUREN_UI_ITERATION_PROTOCOL.md" in text
