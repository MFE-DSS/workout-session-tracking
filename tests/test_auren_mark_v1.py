"""DA-03.2 — AUREN-MARK-V1 guard (LOCKED, operator 2026-10-27).

The three governed source drawings under design/auren/source/brand/mark/ and the runtime
geometry (clients/mobile/src/ui/brand/markGeometry.ts) must be the SAME mark, byte for byte
in their path data; the sources carry no colour; the optical-size rule is the operator's.
Standard library only.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARK = ROOT / "design" / "auren" / "source" / "brand" / "mark"
RUNTIME = ROOT / "clients" / "mobile" / "src" / "ui" / "brand" / "markGeometry.ts"
CONTRACT = ROOT / "docs" / "strategy" / "AUREN_VISUAL_CONTRACT.md"
GRIDS = {"primary": 32, "compact": 16, "micro": 12}


def _svg(name: str) -> str:
    return (MARK / f"mark-{name}.svg").read_text(encoding="utf-8")


def _runtime() -> dict[str, dict[str, str]]:
    src = RUNTIME.read_text(encoding="utf-8")
    out = {}
    for name, body in re.findall(r"(\w+): \{\s*grid: \d+,([^}]*)\}", src):
        parts = dict(re.findall(r"(cursor|marker): '([^']+)'", body))
        out[name] = parts | {"grid": re.search(rf"{name}: \{{\s*grid: (\d+)", src).group(1)}
    return out


def test_three_optical_drawings_exist_on_their_grid():
    for name, grid in GRIDS.items():
        svg = _svg(name)
        assert f'viewBox="0 0 {grid} {grid}"' in svg, name


def test_sources_carry_no_colour():
    for name in GRIDS:
        svg = _svg(name)
        assert re.findall(r'fill="([^"]+)"', svg) == ["currentColor"], name
        assert not re.search(r"#[0-9a-fA-F]{3,8}|rgb|stroke|gradient|filter|<text", svg), name


def test_sources_are_the_runtime_geometry():
    runtime = _runtime()
    assert set(runtime) == set(GRIDS)
    for name, grid in GRIDS.items():
        d = re.search(r' d="([^"]+)"', _svg(name)).group(1)
        assert d == f"{runtime[name]['cursor']} {runtime[name]['marker']}", name
        assert runtime[name]["grid"] == str(grid), name


def test_two_primitives_integer_coordinates_no_rail():
    for name in GRIDS:
        d = re.search(r' d="([^"]+)"', _svg(name)).group(1)
        assert d.count("M") == 2, f"{name}: the mark is exactly two pieces"
        nums = re.findall(r"-?\d+(?:\.\d+)?", d)
        assert all("." not in n for n in nums), f"{name}: integer coordinates only"


def test_the_operator_size_rule_is_the_runtime_rule():
    src = RUNTIME.read_text(encoding="utf-8")
    assert "MARK_MIN_SIZE = 12" in src
    assert "if (size < 16) return 'micro';" in src
    assert "if (size < 20) return 'compact';" in src
    contract = CONTRACT.read_text(encoding="utf-8")
    for rule in ("12 à 15 px", "16 à 19 px", "20 px et plus", "moins de 12 px"):
        assert rule in contract, f"contract does not state: {rule}"
