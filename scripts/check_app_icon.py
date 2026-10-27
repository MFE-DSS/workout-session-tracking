"""DA-03.3 — AUREN-APP-ICON-V1 visual gate: Apple's own renderer, zero-pixel tolerance.

The app icon is an Icon Composer document (clients/mobile/assets/AurenAppIcon.icon). Its
masking, Liquid Glass, shadows and appearances are drawn by the system, so its baselines can
only be produced by Apple's renderer, `ictool` (Xcode → Icon Composer). It is deterministic
(same document + same ictool version → same bytes), so the gate compares byte for byte.

    python3 scripts/check_app_icon.py check     # re-render, compare to the approved baselines
    python3 scripts/check_app_icon.py approve   # OPERATOR ONLY: rewrite the baselines

macOS with Xcode only: elsewhere the gate REFUSES to run instead of passing. CI checks the
source document and the recorded hashes (tests/test_auren_app_icon_v1.py), never pixels.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCUMENT = ROOT / "clients" / "mobile" / "assets" / "AurenAppIcon.icon"
BASELINES = ROOT / "clients" / "mobile" / "visual-contract" / "app-icon" / "baselines"
MANIFEST = BASELINES / "manifest.json"
ICTOOL = Path("/Applications/Xcode.app/Contents/Applications/Icon Composer.app/Contents/Executables/ictool")

# (id, rendition, points, scale) — the seven appearances at 1024, then the system sizes @3x
RENDERS = [
    ("app-icon-v1-default", "Default", 1024, 1),
    ("app-icon-v1-dark", "Dark", 1024, 1),
    ("app-icon-v1-mono", "Mono", 1024, 1),
    ("app-icon-v1-clear-light", "ClearLight", 1024, 1),
    ("app-icon-v1-clear-dark", "ClearDark", 1024, 1),
    ("app-icon-v1-tinted-light", "TintedLight", 1024, 1),
    ("app-icon-v1-tinted-dark", "TintedDark", 1024, 1),
    ("app-icon-v1-default-60pt", "Default", 60, 3),
    ("app-icon-v1-default-40pt", "Default", 40, 3),
    ("app-icon-v1-default-29pt", "Default", 29, 3),
]
# a demonstration tint for the Tinted appearances (the user's tint replaces it on a device)
TINT = ["--tint-color", "0.58", "--tint-strength", "0.75"]


def ictool_version() -> str:
    out = subprocess.run([str(ICTOOL), "--version"], capture_output=True, text=True, check=True).stdout
    return json.loads(out)["short-bundle-version"]


def render(rendition: str, points: int, scale: int, out: Path) -> None:
    args = [str(ICTOOL), str(DOCUMENT), "--export-image", "--output-file", str(out), "--platform", "iOS",
            "--rendition", rendition, "--width", str(points), "--height", str(points), "--scale", str(scale)]
    if rendition.startswith("Tinted"):
        args += TINT
    subprocess.run(args, capture_output=True, text=True, check=True)
    if not out.is_file():
        raise SystemExit(f"ictool produced no image for {rendition} {points}pt @{scale}x")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(manifest: dict, version: str) -> int:
    recorded = manifest.get("renderer", {}).get("ictool")
    if recorded != version:
        print(f"app-icon gate: baselines were rendered with ictool {recorded}, this machine has {version} — "
              "a renderer change, not an icon change: re-approve with the operator.")
        return 1
    expected = {b["id"]: b["sha256"] for b in manifest["baselines"]}
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        for rid, rendition, points, scale in RENDERS:
            out = Path(tmp) / f"{rid}.png"
            render(rendition, points, scale, out)
            ok = sha(out) == expected.get(rid) == sha(BASELINES / f"{rid}.png")
            print(f"  {'✓' if ok else '✗'} {rid}")
            if not ok:
                failures.append(rid)
    print(f"app-icon gate: {len(RENDERS) - len(failures)} / {len(RENDERS)} identical to the approved baselines")
    return 1 if failures else 0


def approve() -> int:
    BASELINES.mkdir(parents=True, exist_ok=True)
    for rid, rendition, points, scale in RENDERS:
        render(rendition, points, scale, BASELINES / f"{rid}.png")
        print(f"  wrote {rid}.png")
    print("app-icon gate: baselines rewritten — update manifest.json (sha256, approval) before committing.")
    return 0


def main(mode: str) -> int:
    if sys.platform != "darwin" or not ICTOOL.is_file():
        print("app-icon gate: Apple's ictool (Xcode, macOS) is required — refusing to run rather than pass.")
        return 2
    if mode == "check":
        return check(json.loads(MANIFEST.read_text(encoding="utf-8")), ictool_version())
    if mode == "approve":
        return approve()
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else ""))
