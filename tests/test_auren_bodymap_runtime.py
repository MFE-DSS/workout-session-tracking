"""DA-04.1 — the BodyMap in the mobile runtime stays the master, its attribution the registry's.

The mobile client draws the master from a generated data module
(`clients/mobile/src/ui/bodymap/masterGeometry.ts`). This guard proves, on every CI run:

- every path is the master's, byte for byte, same ids, same order, same side; the module
  names the master's sha256 (no simplified, redrawn or regenerated anatomy);
- the central attribution and the non-medical notice are the registry's, word for word;
- the three Push A cameras name existing zones and their product labels;
- the runtime authorization the code relies on is the internal one (DA-04.0b), and the
  BodyMap never reaches the web runtime.
Stdlib only.
"""
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / "design/auren/source/bodymap/auren_bodymap_master.svg"
REGISTRY = ROOT / "design/auren/source/bodymap/auren_bodymap_source.yaml"
MAPPING = ROOT / "design/auren/source/bodymap/auren_bodymap_mapping.yaml"
BODYMAP_UI = ROOT / "clients/mobile/src/ui/bodymap"
GEOMETRY_TS = BODYMAP_UI / "masterGeometry.ts"
ATTRIBUTION_TSX = BODYMAP_UI / "attribution.tsx"
PRESETS_TS = BODYMAP_UI / "viewPresets.ts"
SVG = "{http://www.w3.org/2000/svg}"
TS_PATH = re.compile(r"\{ id: (\"[^\"]+\"), side: '(front|back)', d: (\"[^\"]*\") \}")


def master_paths(svg_text):
    root = ET.fromstring(svg_text)
    return [(p.get("id"), p.get("id").split("-")[2], p.get("d")) for p in root.iter(f"{SVG}path")]


def module_paths(ts_text):
    return [(json.loads(i), side, json.loads(d)) for i, side, d in TS_PATH.findall(ts_text)]


def geometry_drift(svg_text, ts_text):
    """Return what differs between the master and the generated module (empty = identical)."""
    errs = []
    sha = hashlib.sha256(svg_text.encode("utf-8")).hexdigest()
    if f"MASTER_SHA256 = '{sha}'" not in ts_text:
        errs.append("sha-mismatch")
    master, module = master_paths(svg_text), module_paths(ts_text)
    if [m[0] for m in master] != [m[0] for m in module]:
        errs.append("ids-or-order")
    for (mid, mside, md), (_, tside, td) in zip(master, module):
        if md != td:
            errs.append(f"path-changed:{mid}")
        if mside != tside:
            errs.append(f"side-changed:{mid}")
    return errs


def _strings(ts_text):
    return set(re.findall(r"'([^'\n]+)'", ts_text))


def test_module_is_the_master_byte_for_byte():
    assert geometry_drift(MASTER.read_text(encoding="utf-8"), GEOMETRY_TS.read_text(encoding="utf-8")) == []


def test_module_carries_all_28_paths():
    assert len(module_paths(GEOMETRY_TS.read_text(encoding="utf-8"))) == 28


def test_negative_one_rounded_coordinate_is_caught():
    ts = GEOMETRY_TS.read_text(encoding="utf-8")
    first = module_paths(ts)[2][2]
    tampered = ts.replace(first, re.sub(r"\d+\.\d+", "50", first, count=1), 1)
    assert any(e.startswith("path-changed") for e in geometry_drift(MASTER.read_text(encoding="utf-8"), tampered))


def test_negative_regenerated_master_is_caught():
    svg = MASTER.read_text(encoding="utf-8").replace("</svg>", "<!-- regenerated --></svg>")
    assert "sha-mismatch" in geometry_drift(svg, GEOMETRY_TS.read_text(encoding="utf-8"))


def test_attribution_is_the_registry_word_for_word():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    strings = _strings(ATTRIBUTION_TSX.read_text(encoding="utf-8"))
    for line in registry["attribution_fr"]:
        assert line in strings, f"attribution line missing or altered: {line}"
    assert registry["non_medical_notice_fr"] in strings
    assert registry["license_url"] in strings


def test_attribution_is_mounted_in_the_journal_sheet():
    sheet = (ROOT / "clients/mobile/src/ui/LabSheet.tsx").read_text(encoding="utf-8")
    assert "<LicencesSection />" in sheet


def test_presets_name_existing_zones_with_product_labels():
    mapping = json.loads(MAPPING.read_text(encoding="utf-8"))
    labels = {z["code"]: z["label_fr"] for z in mapping["zones"]}
    src = PRESETS_TS.read_text(encoding="utf-8")
    presets = re.findall(r"id: '(push-[a-z-]+)', zone: '([a-z_]+)', side: '(front|back)'.*?label: '([^']+)'", src)
    assert [p[0] for p in presets] == ["push-pecs", "push-delt-lat", "push-triceps"]
    for _id, zone, _side, label in presets:
        assert labels[zone] == label


def test_runtime_relies_on_the_internal_authorization():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    assert registry["runtime_authorization"] == "internal-builds-with-constraints"
    assert registry["public_release_authorization"] == "blocked"


def test_bodymap_never_reaches_the_web_runtime():
    for path in (ROOT / "app").rglob("*"):
        if path.is_file() and path.suffix in {".py", ".html", ".js", ".css", ".svg"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            # the file or the generated module — a comment naming a guard is not a load
            assert "masterGeometry" not in text, path
            assert "auren_bodymap_master.svg" not in text, path
