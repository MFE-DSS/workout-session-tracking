"""Sb_ASSET_01.1 — Auren Asset Governance guard.

Inspects the `design/auren/` governance scaffold with the standard library only
(no external dependency). Enforces the invariants of Sx_ASSET_01:
  - the scaffold documents exist;
  - the manifest documents the normative fields + the 8 bounded statuses;
  - no initial asset is `approved`; the BodyMap is prototype/provisional; PWA
    assets are provisional; the Auren name gate is mentioned;
  - provenance documents the required fields, allows explicit UNKNOWN, and
    declares NO third-party intake;
  - NO binary/asset file (svg/png/…) lives under `design/auren/`;
  - NO anatomical/brand master file exists;
  - `LICENSES/` holds only the README (no third-party license text yet);
  - the governance build touches NO `app/**` file.

Governance before assets. Docs/scaffold/test only.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUREN = ROOT / "design" / "auren"


def _read(rel: str) -> str:
    return (AUREN / rel).read_text(encoding="utf-8")


# ───────── scaffold exists ─────────


def test_scaffold_files_exist():
    for name in (
        "README.md",
        "AUREN_VISUAL_ASSET_MANIFEST.md",
        "AUREN_STYLE_RULES.md",
        "AUREN_ASSET_PROVENANCE.md",
        "AUREN_ASSET_INTAKE_CHECKLIST.md",
        "LICENSES/README.md",
    ):
        assert (AUREN / name).is_file(), f"missing scaffold file: design/auren/{name}"


def test_readme_states_gate_blocked_and_identity():
    src = _read("README.md")
    assert "SPIGNOS" in src and "Auren" in src
    assert "BLOCKED" in src
    assert "not started" in src.lower() or "not_started" in src.lower()
    # presence in design/auren/ != authorized in app/static/
    assert "app/static/" in src


# ───────── manifest ─────────


def test_manifest_documents_normative_fields():
    src = _read("AUREN_VISUAL_ASSET_MANIFEST.md")
    for field in ("id", "version", "type", "status", "format", "source_file",
                  "runtime_file", "semantic_contract", "surfaces", "accessibility",
                  "license", "provenance", "review", "budgets", "consumers",
                  "deprecated_by"):
        assert field in src, f"manifest missing normative field: {field}"


def test_manifest_documents_eight_statuses():
    src = _read("AUREN_VISUAL_ASSET_MANIFEST.md")
    for status in ("draft", "provisional", "human-review-required",
                   "anatomical-review-required", "legal-review-required",
                   "approved", "deprecated", "rejected"):
        assert status in src, f"manifest missing status: {status}"


def test_manifest_distinguishes_unknown_values():
    src = _read("AUREN_VISUAL_ASSET_MANIFEST.md")
    assert "NOT APPLICABLE" in src
    assert "UNKNOWN — MANUAL VERIFICATION REQUIRED" in src
    assert "NOT YET" in src  # NOT YET REVIEWED / NOT YET PRODUCED


def test_no_initial_asset_is_approved():
    """No manifest ENTRY may carry status: approved. Match YAML entry lines
    (indented `status: approved`), not prose mentioning the word — e.g. the
    line documenting that `approved` appears on no entry, which is fine."""
    src = _read("AUREN_VISUAL_ASSET_MANIFEST.md")
    entry_lines = re.findall(r"(?m)^\s*status:\s*approved\b", src)
    assert not entry_lines, f"an entry is approved: {entry_lines}"


def test_bodymap_entry_is_prototype_or_provisional():
    src = _read("AUREN_VISUAL_ASSET_MANIFEST.md")
    assert "auren.runtime.bodymap.prototype" in src
    assert "anatomical-map-prototype" in src
    assert "status: provisional" in src


def test_pwa_assets_are_provisional():
    src = _read("AUREN_VISUAL_ASSET_MANIFEST.md")
    assert "auren.runtime.pwa.mark" in src
    assert "brand-runtime-asset" in src or "brand-mark" in src
    assert "provisional" in src
    # the initial entries reference runtime files without copying them
    assert "app/static/icons/auren-mark.svg" in src


def test_manifest_mentions_name_clearance_gate():
    src = _read("AUREN_VISUAL_ASSET_MANIFEST.md")
    assert "CLEARANCE" in src.upper()
    assert "INTEGRATION GATE" in src.upper()


def test_runtime_entries_reference_not_copy():
    """Entries point at app/static / templates (runtime), proving no copy."""
    src = _read("AUREN_VISUAL_ASSET_MANIFEST.md")
    assert "app/templates/_partials/worked_area_body_map.html" in src
    assert "app/static/icons/" in src


# ───────── provenance ─────────


def test_provenance_documents_required_fields():
    src = _read("AUREN_ASSET_PROVENANCE.md")
    for field in ("asset_id", "author", "owner", "source_project", "source_version",
                  "source_type", "access_date", "source_reference", "license_spdx",
                  "license_text_location", "attribution_required", "usage_nature",
                  "modifications", "tooling", "reviewer", "review_date", "evidence",
                  "status"):
        assert field in src, f"provenance missing field: {field}"


def test_provenance_allows_explicit_unknown():
    src = _read("AUREN_ASSET_PROVENANCE.md")
    assert "UNKNOWN" in src
    assert "manual-verification-required" in src


def test_provenance_records_tabler_intake_only():
    """After Sb_ASSET_02.1 the provenance records the Tabler MIT intake and
    explicitly declares Health Icons ABSENT (no undisclosed third party)."""
    src = _read("AUREN_ASSET_PROVENANCE.md")
    assert "tabler/tabler-icons" in src
    assert "975920ff99c12c4dc9e3fe61a03738330600f9b2" in src
    assert "HEALTH ICONS : ABSENT" in src or "Health Icons" in src and "ABSENT" in src


def test_provenance_does_not_invent_upstream_for_repo_assets():
    """Repository-authored assets must not claim a third-party source project."""
    src = _read("AUREN_ASSET_PROVENANCE.md")
    assert "repository-authored" in src
    # shell icons explicitly NOT Tabler/Health (no invented library)
    assert "PAS Tabler" in src or "NOT APPLICABLE" in src


# ───────── licenses ─────────


def test_licenses_dir_holds_exactly_allowlisted():
    """LICENSES holds exactly the allowlisted files. Sb_ASSET_02.1: README +
    official Tabler MIT. Sb_ASSET_03.2 governed evolution: the OFFICIAL verbatim
    CC BY 4.0 text + the BodyParts3D and Servier Medical Art attribution
    notices (BodyMap design-source intake). No Health Icons, no fabricated
    generic license."""
    files = sorted(p.name for p in (AUREN / "LICENSES").iterdir() if p.is_file())
    expected = sorted([
        "README.md", "tabler-MIT.txt", "CC-BY-4.0.txt",
        "bodyparts3d-NOTICE.md", "servier-medical-art-NOTICE.md",
    ])
    assert files == expected, f"LICENSES drift, found: {files}"


def test_tabler_license_is_official_mit():
    src = _read("LICENSES/tabler-MIT.txt")
    assert "MIT License" in src
    assert "Paweł Kuna" in src  # official upstream attribution preserved


def test_licenses_readme_records_tabler_intake():
    src = _read("LICENSES/README.md")
    assert "tabler-MIT.txt" in src
    # Health Icons must remain declared absent
    assert "Health Icons ABSENT" in src or "Health Icons" in src and "ABSENT" in src


def test_no_fabricated_or_health_icons_license():
    """No reconstructed generic license, and NO Health Icons license ingested.
    NOTE: CC-BY-4.0.txt is now ALLOWED — but only as the OFFICIAL verbatim text
    (governed BodyMap intake), verified by test_cc_by_40_is_official below."""
    for name in ("MIT.txt", "CC0-1.0.txt", "Apache-2.0.txt",
                 "health-icons-MIT.txt", "health-icons-CC0.txt", "healthicons-CC0-1.0.txt"):
        assert not (AUREN / "LICENSES" / name).exists(), f"forbidden license file: {name}"


def test_cc_by_40_is_official():
    """The CC BY 4.0 text must be the official verbatim license, not fabricated."""
    src = _read("LICENSES/CC-BY-4.0.txt")
    assert "Attribution 4.0 International" in src
    assert "Creative Commons Corporation" in src
    assert len(src) > 10000  # full legal code, not a stub


# ───────── security: evolving governance guard under design/auren/ ─────────
#
# The zero-asset BINARY guard is PERMANENT (no svg/png/... may ever live under
# design/auren/ without a governed intake).
#
# The zero-STRUCTURED-file guard was specific to Sb_ASSET_01.1. From
# Sb_ASSET_01.2 onwards, structured contract files are allowed by an EXPLICIT
# ALLOWLIST only. From Sb_ASSET_02.1 onwards, SVG files are allowed ONLY when
# they are on the exact vendored-icon allowlist (Tabler P0 subset). Any other
# SVG/YAML/JSON, and every raster/font/binary format, is still denied.
# Future SVG intake (Health Icons, BodyMap master, new vendors) requires a NEW
# governed evolution of this test (extend the allowlist + provenance + license).

# Raster/font/binary extensions — PERMANENTLY forbidden under design/auren/.
FORBIDDEN_BINARY_SUFFIXES = {
    ".png", ".webp", ".ico", ".jpg", ".jpeg", ".gif",
    ".woff", ".woff2", ".ttf", ".otf", ".blend", ".fig",
}

# Vendored SVGs explicitly allowed (exact repo-relative paths). Sb_ASSET_02.1:
# the ten Tabler v3.45.0 outline P0 icons.
_TABLER = "design/auren/source/icons/vendor/tabler/v3.45.0/outline"
ALLOWED_VENDOR_SVGS = {
    f"{_TABLER}/arrows-exchange.svg",
    f"{_TABLER}/player-play.svg",
    f"{_TABLER}/player-pause.svg",
    f"{_TABLER}/rotate.svg",
    f"{_TABLER}/chevron-down.svg",
    f"{_TABLER}/chevron-up.svg",
    f"{_TABLER}/bulb.svg",
    f"{_TABLER}/alert-triangle.svg",
    f"{_TABLER}/check.svg",
    f"{_TABLER}/menu-2.svg",
}

# Sb_ASSET_03.2 GOVERNED EVOLUTION: the BodyMap design-source master + compact,
# derived from BodyParts3D (CC BY 4.0) + Servier Medical Art (CC BY 4.0),
# technically validated and independently reproduced (package v2). NOT AUTHORIZED
# FOR APP INTEGRATION. Detailed guard: tests/test_auren_bodymap_master.py.
ALLOWED_BODYMAP_SVGS = {
    "design/auren/source/bodymap/auren_bodymap_master.svg",
    "design/auren/exports/svg/auren_bodymap_compact.svg",
}

# Sb_ASSET_03B.2R-D1 GOVERNED EVOLUTION: the three frozen P0 Muscle Focus Regional Plate candidates,
# derived from BodyParts3D 4.0 (CC BY 4.0), internal-synthetic-review-accepted + owner-decided
# (ACCEPT_WITH_CONSTRAINTS). NOT AUTHORIZED FOR APP INTEGRATION; NOT a professional anatomical review.
# Detailed guard: tests/test_auren_muscle_focus_plates.py.
_MF = "design/auren/source/muscle-focus"
ALLOWED_MUSCLE_FOCUS_SVGS = {
    f"{_MF}/auren-plate-region-chest.svg",
    f"{_MF}/auren-plate-region-shoulders.svg",
    f"{_MF}/auren-plate-region-posterior.svg",
}

# Full SVG allowlist under design/auren/ = vendored icons + governed BodyMap + P0 Muscle Focus plates.
ALLOWED_SVGS = ALLOWED_VENDOR_SVGS | ALLOWED_BODYMAP_SVGS | ALLOWED_MUSCLE_FOCUS_SVGS

# Structured contract files explicitly allowed (exact repo-relative paths).
ALLOWED_STRUCTURED_FILES = {
    "design/auren/source/bodymap/auren_bodymap_mapping.yaml",
    "design/auren/source/bodymap/auren_bodymap_source.yaml",
    "design/auren/source/icons/auren_icon_subset.yaml",
    # Sb_ASSET_03B.2R-D1 — P0 Muscle Focus plate descriptor registry (governed evolution).
    "design/auren/source/muscle-focus/auren_muscle_focus_registry.yaml",
}

STRUCTURED_SUFFIXES = {".yaml", ".yml", ".json"}


def test_no_asset_binaries_under_design_auren():
    """PERMANENT guard: no raster/font/binary file may live under design/auren/."""
    offenders = [
        str(p.relative_to(ROOT))
        for p in AUREN.rglob("*")
        if p.is_file() and p.suffix.lower() in FORBIDDEN_BINARY_SUFFIXES
    ]
    assert not offenders, f"asset/binary files under design/auren/: {offenders}"


def test_svgs_match_vendor_allowlist_exactly():
    """The set of SVGs under design/auren/ MUST equal the vendored allowlist —
    equality (not subset) so a MISSING file also fails, not only an intruder."""
    actual = {
        str(p.relative_to(ROOT))
        for p in AUREN.rglob("*.svg")
        if p.is_file()
    }
    assert actual == ALLOWED_SVGS, (
        f"SVG set drift.\n  missing: {ALLOWED_SVGS - actual}\n  extra: {actual - ALLOWED_SVGS}"
    )


def test_structured_files_only_via_allowlist():
    """Only allowlisted structured files are permitted; any other
    .yaml/.yml/.json under design/auren/ is denied (no blanket YAML/JSON)."""
    offenders = [
        rel
        for p in AUREN.rglob("*")
        if p.is_file() and p.suffix.lower() in STRUCTURED_SUFFIXES
        and (rel := str(p.relative_to(ROOT))) not in ALLOWED_STRUCTURED_FILES
    ]
    assert not offenders, f"non-allowlisted structured files under design/auren/: {offenders}"


def test_allowlisted_files_present_and_correct_kind():
    """Allowlisted contracts and vendored SVGs all exist and are the right kind."""
    for rel in ALLOWED_STRUCTURED_FILES:
        p = ROOT / rel
        assert p.is_file(), f"allowlisted contract missing: {rel}"
        assert p.suffix.lower() in STRUCTURED_SUFFIXES
    for rel in ALLOWED_SVGS:
        p = ROOT / rel
        assert p.is_file(), f"allowlisted SVG missing: {rel}"
        assert p.suffix.lower() == ".svg"
        assert not p.is_symlink(), f"SVG must be a regular file: {rel}"


def test_no_brand_master_files_exist():
    """Brand masters remain forbidden. The BodyMap master is NO LONGER here:
    Sb_ASSET_03.2 introduced it by governed intake (allowlisted above,
    guarded by tests/test_auren_bodymap_master.py). Brand identity masters
    (mark/wordmark/app-icon) are still unproduced and forbidden."""
    for master in ("source/brand/auren_mark_master.svg",
                   "source/brand/auren_wordmark_master.svg",
                   "source/brand/auren_app_icon_master.svg"):
        assert not (AUREN / master).exists(), f"forbidden brand master present: {master}"


def test_style_rules_and_intake_have_content():
    assert len(_read("AUREN_STYLE_RULES.md")) > 500
    assert "ACCEPTED FOR DESIGN SOURCE" in _read("AUREN_ASSET_INTAKE_CHECKLIST.md")


# ───────── application untouched ─────────


def test_no_runtime_asset_moved_or_removed():
    """The audited runtime assets still exist untouched (referenced, not moved)."""
    for rel in ("app/static/icons/auren-mark.svg",
                "app/static/icons/favicon.svg",
                "app/static/icons/icon-192.png",
                "app/static/icons/icon-512.png",
                "app/static/icons/icon-maskable-512.png",
                "app/static/icons/apple-touch-icon.png",
                "app/templates/_partials/worked_area_body_map.html"):
        assert (ROOT / rel).is_file(), f"runtime asset missing (must stay in place): {rel}"
