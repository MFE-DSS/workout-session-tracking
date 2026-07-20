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


def test_licenses_dir_holds_exactly_readme_and_tabler():
    """After Sb_ASSET_02.1 LICENSES holds exactly README + the official Tabler
    MIT text — and nothing else (no Health Icons, no fabricated license)."""
    files = sorted(p.name for p in (AUREN / "LICENSES").iterdir() if p.is_file())
    assert files == ["README.md", "tabler-MIT.txt"], f"LICENSES must hold exactly README + tabler-MIT.txt, found: {files}"


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
    """No reconstructed generic license, and NO Health Icons license ingested."""
    for name in ("MIT.txt", "CC-BY-4.0.txt", "CC0-1.0.txt", "Apache-2.0.txt",
                 "health-icons-MIT.txt", "health-icons-CC0.txt", "healthicons-CC0-1.0.txt"):
        assert not (AUREN / "LICENSES" / name).exists(), f"forbidden license file: {name}"


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
# the ten Tabler v3.45.0 outline P0 icons — and NOTHING else.
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

# Structured contract files explicitly allowed (exact repo-relative paths).
ALLOWED_STRUCTURED_FILES = {
    "design/auren/source/bodymap/auren_bodymap_mapping.yaml",
    "design/auren/source/icons/auren_icon_subset.yaml",
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
    assert actual == ALLOWED_VENDOR_SVGS, (
        f"SVG set drift.\n  missing: {ALLOWED_VENDOR_SVGS - actual}\n  extra: {actual - ALLOWED_VENDOR_SVGS}"
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
    for rel in ALLOWED_VENDOR_SVGS:
        p = ROOT / rel
        assert p.is_file(), f"allowlisted vendor SVG missing: {rel}"
        assert p.suffix.lower() == ".svg"
        assert not p.is_symlink(), f"vendor SVG must be a regular file: {rel}"


def test_no_master_files_exist():
    for master in ("source/bodymap/auren_bodymap_master.svg",
                   "source/brand/auren_mark_master.svg",
                   "source/brand/auren_wordmark_master.svg",
                   "source/brand/auren_app_icon_master.svg"):
        assert not (AUREN / master).exists(), f"forbidden master present: {master}"


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
