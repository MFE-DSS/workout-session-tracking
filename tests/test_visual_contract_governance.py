"""DA-GOV-01 — governance of the visual contract gate (docs/strategy/AUREN_VISUAL_CONTRACT.md).

The pixel comparison itself runs in the CI job `visual-contract` (Playwright, pinned image).
This guard protects what makes that comparison trustworthy:

* a baseline never changes silently: every PNG is in the manifest with its sha256 and
  the operator's approval; a PNG without an entry, or an entry without its PNG, fails;
* every governed fixture has a baseline, and every baseline belongs to a fixture;
* the gate can never write a baseline by itself (`updateSnapshots: 'none'`, no
  `--update-snapshots` in CI);
* local runs and CI render in the SAME pinned image, and Playwright stays a dev-only
  dependency at the image's exact version;
* the contract names every baseline and every LOCKED visual id.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MOBILE = ROOT / "clients" / "mobile"
GATE = MOBILE / "visual-contract"
BASELINES = GATE / "baselines"
MANIFEST = json.loads((BASELINES / "manifest.json").read_text(encoding="utf-8"))
CONTRACT = (ROOT / "docs" / "strategy" / "AUREN_VISUAL_CONTRACT.md").read_text(encoding="utf-8")
CI = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
RUN_SH = (GATE / "run.sh").read_text(encoding="utf-8")
CONFIG = (GATE / "playwright.config.ts").read_text(encoding="utf-8")
FIXTURES_TS = (MOBILE / "src" / "ui" / "contract" / "fixtures.ts").read_text(encoding="utf-8")
PACKAGE = json.loads((MOBILE / "package.json").read_text(encoding="utf-8"))

IMAGE = MANIFEST["renderer"]["image"]
LOCKED_IDS = ("CALIBRATION-LINE-V1", "REFERENCE-MARKER-V1", "ACTIVE-CURSOR-V1", "FRAME-C-V1", "SEMANTIC-TOKENS-V1",
              "INSTRUMENT-SURFACE-B1", "INSTRUMENT-SURFACE-B2", "INSTRUMENT-CONTROLS-B3", "RECESSED-WINDOW-V1",
              "NUMERIC-READOUT-V1", "SESSION-CARD-R1", "AUREN-MARK-V1", "PUSH-A-BODYMAP-TRIPTYCH-V1")


def _fixture_ids() -> set[str]:
    return set(re.findall(r"\{ id: '([a-z0-9-]+)', contract:", FIXTURES_TS))


def test_every_baseline_png_is_in_the_manifest_with_its_exact_hash():
    on_disk = {p.name for p in BASELINES.glob("*.png")}
    listed = {b["file"] for b in MANIFEST["baselines"]}
    assert on_disk == listed, f"unlisted: {on_disk - listed} · missing: {listed - on_disk}"
    for b in MANIFEST["baselines"]:
        digest = hashlib.sha256((BASELINES / b["file"]).read_bytes()).hexdigest()
        assert digest == b["sha256"], (
            f"{b['file']} changed without an approved manifest entry — "
            "a new baseline is an operator decision (AUREN_VISUAL_CONTRACT §5)")


def test_every_baseline_records_its_approval():
    for b in MANIFEST["baselines"]:
        assert b["approved_by"].startswith("operator"), b["id"]
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", b["approved_on"]), b["id"]
        assert b["visual_id"] in LOCKED_IDS, b["id"]


def test_fixtures_and_baselines_are_the_same_set():
    ids = _fixture_ids()
    assert ids, "no fixture parsed from fixtures.ts"
    assert ids == {b["id"] for b in MANIFEST["baselines"]}
    assert all(b["file"] == f"{b['id']}.png" for b in MANIFEST["baselines"])


def test_the_minimum_calibration_line_set_is_registered():
    required = {"calibration-line-320-target", "calibration-line-390-target",
                "calibration-line-390-push", "calibration-line-390-high-cost"}
    assert required <= _fixture_ids()


def test_the_gate_can_never_write_a_baseline_by_itself():
    assert "updateSnapshots: 'none'" in CONFIG
    assert "maxDiffPixels: 0" in CONFIG
    assert "--update-snapshots" not in CI, "CI must compare, never approve"
    assert 'approve) EXTRA="--update-snapshots=all"' in RUN_SH, "approval stays an explicit mode"


def test_local_and_ci_render_in_the_same_pinned_image():
    assert re.fullmatch(r"mcr\.microsoft\.com/playwright:v[\d.]+-noble@sha256:[0-9a-f]{64}", IMAGE)
    assert f'IMAGE="{IMAGE}"' in RUN_SH
    assert f"image: {IMAGE}" in CI
    assert "--platform linux/amd64" in RUN_SH


def test_playwright_is_a_dev_only_dependency_at_the_image_version():
    version = re.search(r"playwright:v([\d.]+)-", IMAGE).group(1)
    assert PACKAGE["devDependencies"].get("@playwright/test") == version
    assert "@playwright/test" not in PACKAGE.get("dependencies", {})
    assert "playwright" not in PACKAGE.get("dependencies", {})
    assert MANIFEST["renderer"]["playwright"] == version


def test_the_local_gate_verifies_its_dependencies_instead_of_trusting_npm():
    """npm ci on the shared volume exited 0 with missing files one pass in two (2026-10-25).

    The local gate must reuse only an install that matches the lock, verify every install with
    `npm ls`, and retry from an emptied node_modules — never run npm ci unchecked again.
    """
    install = (GATE / "install-deps.sh").read_text(encoding="utf-8")
    assert "bash visual-contract/install-deps.sh" in RUN_SH
    assert "npm ci" not in RUN_SH, "the install goes through install-deps.sh only"
    assert "cmp -s package-lock.json" in install
    assert install.count("npm ls --depth=0") == 2, "both the reused and the fresh install are verified"
    assert "for attempt in 1 2 3" in install


def test_ci_runs_the_visual_gate():
    assert re.search(r"^  visual-contract:\n", CI, re.M), "CI job `visual-contract` missing"
    assert "npx playwright test -c visual-contract/playwright.config.ts" in CI
    assert "EXPO_PUBLIC_GALLERY: contract" in CI


def test_the_contract_names_every_baseline_and_every_locked_id():
    for b in MANIFEST["baselines"]:
        assert b["id"] in CONTRACT, b["id"]
    for vid in LOCKED_IDS:
        assert vid in CONTRACT, vid
    for word in ("LOCKED", "CONSTRAINED", "EXPLORATION", "MUST PRESERVE", "MUST NEVER", "MAY CHANGE"):
        assert word in CONTRACT, word


def test_a_candidate_is_reviewed_never_compared_until_the_operator_approves_it():
    """DA-02.4B.1 — a candidate (candidates.ts) is captured for review, never gated, never a baseline."""
    candidates_ts = (MOBILE / "src" / "ui" / "contract" / "candidates.ts").read_text(encoding="utf-8")
    kinds = set(re.findall(r"candidate: '([A-Z0-9-]+)'", candidates_ts))
    assert kinds, "no candidate parsed from candidates.ts"
    assert not kinds & set(LOCKED_IDS), "a LOCKED element is governed by a baseline, never left as a candidate"
    assert "candidates" not in (GATE / "visual.spec.ts").read_text(encoding="utf-8")
    review_spec = (GATE / "review.spec.ts").read_text(encoding="utf-8")
    assert ".toHaveScreenshot(" not in review_spec, "a review capture compares nothing"
    assert "'baselines'" not in review_spec, "a review capture never writes under baselines/"
    assert 'review) EXTRA="" ; CONFIG="visual-contract/review.config.ts"' in RUN_SH


def test_no_raster_baseline_lives_under_design_auren():
    """The design tree forbids rasters (test_auren_asset_governance); baselines live elsewhere."""
    assert not any((ROOT / "design" / "auren").rglob("*.png"))
    assert BASELINES.is_dir()
