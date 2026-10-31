"""DA-04.3 — the body the mobile BodyMap draws is the vendored MIT body, untouched and credited.

Since DA-04.3 the app draws react-native-body-highlighter 3.2.0 (MIT) instead of the BodyParts3D
master: its data is vendored as `clients/mobile/vendor/react-native-body-highlighter/body.json`
(slug + path strings, read as text from the package) next to its LICENSE, and the app module
`clients/mobile/src/ui/bodymap/bodyGeometry.ts` is GENERATED from it. This guard proves, on every
CI run:

- every part of the app module is the vendored data's, character for character, same order;
  the module names the vendored tarball's sha256;
- the vendored LICENSE is the MIT licence with the package's copyright, and the app's central
  credit carries that copyright and licence (MIT asks for the notice to travel with the work);
- the eleven AUREN zones all map to parts of the body, and every camera's zone exists on its side;
- the BodyMap never reaches the web runtime.
Stdlib only.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENDOR = ROOT / "clients/mobile/vendor/react-native-body-highlighter"
BODY_JSON = VENDOR / "body.json"
LICENSE = VENDOR / "LICENSE"
MAPPING = ROOT / "design/auren/source/bodymap/auren_bodymap_mapping.yaml"
REGISTRY = ROOT / "design/auren/source/bodymap/auren_bodymap_source.yaml"
BODYMAP_UI = ROOT / "clients/mobile/src/ui/bodymap"
GEOMETRY_TS = BODYMAP_UI / "bodyGeometry.ts"
ATTRIBUTION_TSX = BODYMAP_UI / "attribution.tsx"
PRESETS_TS = BODYMAP_UI / "viewPresets.ts"
TS_PART = re.compile(r'\{ slug: ("[a-z-]+"), d: (\[[^\]]*\]) \}')


def _vendor():
    return json.loads(BODY_JSON.read_text(encoding="utf-8"))


def module_parts(ts_text):
    """The parts of the generated module, front then back, in order: [(slug, [d, ...]), ...]."""
    return [(json.loads(s), json.loads(d)) for s, d in TS_PART.findall(ts_text)]


def body_drift(vendor, ts_text):
    """Return what differs between the vendored data and the generated module (empty = identical)."""
    errs = []
    if f'"tarball_sha256": "{vendor["source"]["tarball_sha256"]}"' not in ts_text:
        errs.append("tarball-sha-mismatch")
    expected = [(p["slug"], p["paths"]) for side in ("front", "back") for p in vendor[side]]
    got = module_parts(ts_text)
    if [s for s, _ in expected] != [s for s, _ in got]:
        errs.append("slugs-or-order")
    for i, ((slug, d1), (_, d2)) in enumerate(zip(expected, got)):
        if d1 != d2:
            errs.append(f"path-changed:{i}:{slug}")
    return errs


def test_module_is_the_vendored_body_character_for_character():
    assert body_drift(_vendor(), GEOMETRY_TS.read_text(encoding="utf-8")) == []


def test_the_vendored_body_is_the_male_front_and_back():
    v = _vendor()
    assert v["source"]["package"] == "react-native-body-highlighter"
    assert v["source"]["version"] == "3.2.0"
    assert v["source"]["license"] == "MIT"
    assert {"chest", "deltoids", "biceps"} <= {p["slug"] for p in v["front"]}
    assert {"trapezius", "upper-back", "gluteal"} <= {p["slug"] for p in v["back"]}


def test_negative_one_altered_coordinate_is_caught():
    ts = GEOMETRY_TS.read_text(encoding="utf-8")
    first = module_parts(ts)[0][1][0]
    tampered = ts.replace(first, re.sub(r"\d+\.\d+", "50", first, count=1), 1)
    assert any(e.startswith("path-changed") for e in body_drift(_vendor(), tampered))


def test_negative_another_package_build_is_caught():
    v = _vendor()
    v["source"]["tarball_sha256"] = "0" * 64
    assert "tarball-sha-mismatch" in body_drift(v, GEOMETRY_TS.read_text(encoding="utf-8"))


def test_the_vendored_licence_is_mit_with_the_package_copyright():
    text = LICENSE.read_text(encoding="utf-8")
    assert text.startswith("MIT License")
    assert _vendor()["source"]["copyright"] in text
    assert "Permission is hereby granted, free of charge" in text


def test_the_app_credit_carries_the_copyright_and_the_licence():
    src = ATTRIBUTION_TSX.read_text(encoding="utf-8")
    ts = GEOMETRY_TS.read_text(encoding="utf-8")
    assert "BODY_SOURCE.copyright" in src and "BODY_SOURCE.license" in src
    assert _vendor()["source"]["copyright"] in ts
    assert json.loads(REGISTRY.read_text(encoding="utf-8"))["non_medical_notice_fr"] in src


def test_attribution_is_mounted_in_the_journal_sheet():
    sheet = (ROOT / "clients/mobile/src/ui/LabSheet.tsx").read_text(encoding="utf-8")
    assert "<LicencesSection />" in sheet


def test_every_zone_maps_to_parts_of_the_body():
    codes = {z["code"] for z in json.loads(MAPPING.read_text(encoding="utf-8"))["zones"]}
    ts = GEOMETRY_TS.read_text(encoding="utf-8")
    zone_slugs = json.loads(re.search(r"export const ZONE_SLUGS = (\{.*?\}) as const", ts, re.S).group(1))
    assert set(zone_slugs) == codes
    v = _vendor()
    for zone, sides in zone_slugs.items():
        for side, slugs in sides.items():
            present = {p["slug"] for p in v[side]}
            assert set(slugs) <= present, (zone, side, slugs)


def test_presets_name_existing_zones_with_product_labels():
    mapping = json.loads(MAPPING.read_text(encoding="utf-8"))
    labels = {z["code"]: z["label_fr"] for z in mapping["zones"]}
    src = PRESETS_TS.read_text(encoding="utf-8")
    presets = re.findall(r"id: '((?:push|zone)-[a-z-]+)', zone: '([a-z_]+)', side: '(front|back)'.*?label: '([^']+)'", src)
    assert [p[0] for p in presets][:3] == ["push-pecs", "push-delt-lat", "push-triceps"]
    # DA-04.2 — exactly one camera per zone of the taxonomy
    assert sorted(p[1] for p in presets) == sorted(labels)
    for _id, zone, _side, label in presets:
        assert labels[zone] == label


def test_bodymap_never_reaches_the_web_runtime():
    for path in (ROOT / "app").rglob("*"):
        if path.is_file() and path.suffix in {".py", ".html", ".js", ".css", ".svg"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            assert "bodyGeometry" not in text, path
            assert "body-highlighter" not in text, path
