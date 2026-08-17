"""Sb_BODYMAP_ASSET_INTAKE_01 — structural gate for delivered BodyMap plates.

WHAT THIS IS
------------
A candidate SVG arrives from the external production workspace
(BodyParts3D → Blender → Potrace → Inkscape). This module answers one question:
**is it wired the way the runtime expects?** Id grammar, group structure, surface
→ zone mapping, and the runtime-safety properties that
`Sb_BODYMAP_IDENTITY_CONTRACT_01` and `OQ_POSITIONAL_CSS_01` depend on.

WHAT THIS IS NOT
----------------
It is **not an anatomical review**. A structural PASS says the file will render
and colour correctly; it says nothing about whether the shapes are anatomically
right. Only a human can say that, and the report repeats it every time.

The repository does not draw anatomy and does not run the pipeline. This is a
door, not a factory.

USAGE
-----
    python scripts/bodymap_asset_intake.py path/to/candidate.svg [more.svg ...]

Exit code 0 when every candidate passes, 1 otherwise.
"""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

SVG_NS = "http://www.w3.org/2000/svg"

#: Panels are square by contract; the filmstrip crops to aspect-ratio 1/1.
PANEL_SIZE = 2048

#: Closed V1 frame vocabulary (Sb_BODYMAP_FRAME_ATLAS_01).
FRAME_ORDER = ("front", "profile", "back", "top")

#: Surfaces that carry a state and MUST resolve to a business zone.
#: Seeded from the shipped plates; new regions extend this table on delivery,
#: which is the point — an unknown surface is a blocking error, never a guess.
SURFACE_ZONE_MAP: dict[tuple[str, str], str] = {
    ("chest", "hero"): "pecs",
    ("shoulders", "delt-lateral"): "delt_lat",
    ("shoulders", "delt-posterior"): "delt_post",
    ("posterior", "gluteus"): "posterior",
    ("posterior", "hamstring"): "posterior",
    # ORDERED, NOT PRODUCED — the surface names the profile pass must use
    # (docs/assets/AUREN_PROFILE_REGIONAL_PASS_01.md). Declaring them here is
    # what makes the order machine-checkable on delivery; it names nothing
    # anatomical that the eleven-zone taxonomy does not already name.
    ("back", "lats"): "lats",
    ("back", "upper-back"): "upper_back",
    ("arms", "biceps"): "biceps",
    ("arms", "triceps"): "triceps",
    ("legs", "quads"): "quads",
    ("legs", "calves"): "calves",
    ("core", "core"): "core",
}

#: Surfaces that legitimately map to NO zone, with the contract decision.
#: `context` is bone scenery; `delt-anterior` is Option A — depicted by the
#: shoulders plate, never addressable as a zone.
NON_ZONE_SURFACES: dict[str, str] = {
    "context": "IGNORE",
    "delt-anterior": "MERGE",
}

#: Zone codes this project refuses to introduce through an asset.
#:
#: Matched against the NORMALISED SURFACE TOKEN, exactly — never as a substring
#: of the id. A substring test looked equivalent and was not: `delt-ant` is a
#: prefix of `delt-anterior`, the surface the contract explicitly permits as
#: MERGE, so the first version of this guard rejected the shipped, approved
#: shoulders plate. A surface already adjudicated in NON_ZONE_SURFACES is exempt:
#: the contract has ruled it a surface, and a surface is not a zone.
FORBIDDEN_ZONE_CODES = frozenset({
    "delt_ant", "delt_anterior", "anterior_deltoid",
    "pec_clavicular", "pec_sternal", "pec_sternocostal",
    "upper_pec", "lower_pec",
})


def _as_zone_code(surface: str) -> str:
    """Surface tokens use hyphens, zone codes use underscores."""
    return surface.replace("-", "_")

#: Zones each ordered region is expected to serve, from
#: docs/assets/AUREN_PROFILE_REGIONAL_PASS_01.md. Used only to report which
#: expected zones a candidate does not yet cover — never to invent a surface.
REGION_EXPECTED_ZONES: dict[str, tuple[str, ...]] = {
    "chest": ("pecs",),
    "shoulders": ("delt_lat", "delt_post"),
    "posterior": ("posterior",),
    "back": ("lats", "upper_back"),
    "arms": ("biceps", "triceps"),
    "legs": ("quads", "calves"),
    "core": ("core",),
}

ID_RE = re.compile(
    r"^auren-plate-region-(?P<region>[a-z]+)--"
    r"(?:(?P<frame>front|profile|back|top)-)?"
    r"(?P<surface>[a-z][a-z-]*[a-z])-"
    r"(?P<counter>\d{3})$"
)

ROOT_ID_RE = re.compile(r"^auren-plate-region-(?P<region>[a-z]+)$")

SURFACE_GROUP_CLASSES = ("auren-mf-context", "auren-mf-hero", "auren-mf-part")


@dataclass(frozen=True)
class Finding:
    level: str  # "error" blocks intake; "warning" is reported, not blocking
    code: str
    message: str


@dataclass(frozen=True)
class SurfaceRow:
    region: str
    frame: str
    surface: str
    path_id: str
    zone: str  # a business zone, or "—" with the contract decision in brackets


@dataclass
class IntakeReport:
    path: Path
    region: str = ""
    findings: list[Finding] = field(default_factory=list)
    rows: list[SurfaceRow] = field(default_factory=list)
    unmapped_surfaces: list[str] = field(default_factory=list)
    missing_zones: list[str] = field(default_factory=list)

    def error(self, code: str, message: str) -> None:
        self.findings.append(Finding("error", code, message))

    def warn(self, code: str, message: str) -> None:
        self.findings.append(Finding("warning", code, message))

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.level == "error"]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.level == "warning"]

    @property
    def ok(self) -> bool:
        return not self.errors

    def render(self) -> str:
        out: list[str] = []
        verdict = "PASS" if self.ok else "FAIL"
        out.append(f"=== BodyMap asset intake — {verdict} ===")
        out.append(f"  file   : {self.path}")
        out.append(f"  region : {self.region or '(undetermined)'}")

        if self.errors:
            out.append(f"\n  BLOCKING ({len(self.errors)}):")
            out.extend(f"    ✗ [{f.code}] {f.message}" for f in self.errors)
        if self.warnings:
            out.append(f"\n  WARNINGS ({len(self.warnings)}):")
            out.extend(f"    ! [{f.code}] {f.message}" for f in self.warnings)

        if self.rows:
            out.append(f"\n  SURFACES ({len(self.rows)} paths):")
            out.append(f"    {'FRAME':<9} {'SURFACE':<16} {'ZONE':<12} ID")
            for row in self.rows:
                out.append(
                    f"    {row.frame:<9} {row.surface:<16} {row.zone:<12} {row.path_id}"
                )

        if self.unmapped_surfaces:
            out.append("\n  SURFACES WITHOUT A BUSINESS ZONE:")
            out.extend(f"    - {s}" for s in self.unmapped_surfaces)
        if self.missing_zones:
            out.append("\n  EXPECTED ZONES NOT COVERED BY THIS PLATE:")
            out.extend(f"    - {z}" for z in self.missing_zones)

        out.append(
            "\n  A structural PASS is NOT an anatomical review. This gate checks"
            "\n  wiring only — ids, group order, zone mapping, runtime safety."
            "\n  Anatomical correctness remains a human review and is not claimed here."
        )
        return "\n".join(out)


def _local(tag: str) -> str:
    return tag.split("}", 1)[-1]


def _classes(element: ET.Element) -> list[str]:
    return (element.get("class") or "").split()


def _check_root(root: ET.Element, report: IntakeReport) -> int:
    """Validate the svg root and return the declared panel count."""
    if _local(root.tag) != "svg":
        report.error("ROOT_NOT_SVG", f"root element is <{_local(root.tag)}>, expected <svg>")
        return 0

    root_id = root.get("id") or ""
    match = ROOT_ID_RE.match(root_id)
    if not match:
        report.error(
            "ROOT_ID",
            f"root id {root_id!r} must be auren-plate-region-{{region}}",
        )
    else:
        report.region = match.group("region")
        if report.region not in REGION_EXPECTED_ZONES:
            report.warn(
                "REGION_UNKNOWN",
                f"region {report.region!r} is not in the ordered set "
                f"({', '.join(sorted(REGION_EXPECTED_ZONES))})",
            )

    view_box = (root.get("viewBox") or "").split()
    if len(view_box) != 4:
        report.error("VIEWBOX_MISSING", "root has no usable viewBox")
        return 0
    try:
        _, _, width, height = (float(v) for v in view_box)
    except ValueError:
        report.error("VIEWBOX_INVALID", f"viewBox is not numeric: {' '.join(view_box)}")
        return 0

    if abs(height - PANEL_SIZE) > 0.5:
        report.error(
            "PANEL_NOT_SQUARE",
            f"panel height is {height:g}, expected {PANEL_SIZE} — the filmstrip "
            f"crops to aspect-ratio 1/1 and a non-square panel would be distorted",
        )
        return 0

    panels = width / PANEL_SIZE
    if abs(panels - round(panels)) > 1e-6 or round(panels) < 1:
        report.error(
            "PANEL_WIDTH",
            f"viewBox width {width:g} is not a whole multiple of {PANEL_SIZE} — "
            f"a filmstrip is N square panels side by side",
        )
        return 0
    return round(panels)


def _check_frames(root: ET.Element, report: IntakeReport, panels: int) -> list[ET.Element]:
    views = [
        g for g in root.iter(f"{{{SVG_NS}}}g")
        if any(c.startswith("auren-mf-view-") for c in _classes(g))
    ]
    if not views:
        report.error("NO_FRAME_GROUP", "no <g class=\"auren-mf-view-{frame}\"> found")
        return []

    if len(views) != panels:
        report.error(
            "FRAME_COUNT",
            f"{len(views)} frame group(s) for {panels} declared panel(s) — the "
            f"viewBox and the groups must agree",
        )

    seen: list[str] = []
    for view in views:
        cls = next(c for c in _classes(view) if c.startswith("auren-mf-view-"))
        frame = cls.removeprefix("auren-mf-view-")
        if frame not in FRAME_ORDER:
            report.error("FRAME_UNKNOWN", f"frame {frame!r} is outside the V1 vocabulary")
        if frame in seen:
            report.error("FRAME_DUPLICATE", f"frame {frame!r} appears twice")
        seen.append(frame)

    # Deliberately NOT warning when the declared order differs from FRAME_ORDER.
    # `FRAME_ORDER` puts `profile` before `back`, so a conforming `back` plate
    # (logical plane first, revealing plane second) would be flagged — and the
    # workspace would "fix" it by shipping profile first, which would make
    # profile the DEFAULT view. A validator must not nudge a decision nobody has
    # taken. The tension is recorded as an open question in
    # docs/assets/AUREN_PROFILE_REGIONAL_PASS_01.md.
    return views


def _frame_of(view: ET.Element) -> str:
    cls = next(c for c in _classes(view) if c.startswith("auren-mf-view-"))
    return cls.removeprefix("auren-mf-view-")


def _check_structure(views: list[ET.Element], report: IntakeReport) -> None:
    """view → context → surfaces, context first, stable surface order."""
    per_frame_order: dict[str, list[str]] = {}

    for view in views:
        frame = _frame_of(view)
        groups = [
            g for g in view
            if _local(g.tag) == "g" and set(_classes(g)) & set(SURFACE_GROUP_CLASSES)
        ]
        if not groups:
            report.error("FRAME_EMPTY", f"frame {frame!r} declares no surface group")
            continue

        first = set(_classes(groups[0])) & set(SURFACE_GROUP_CLASSES)
        if "auren-mf-context" not in first:
            report.error(
                "CONTEXT_NOT_FIRST",
                f"frame {frame!r}: first group is {sorted(first)}, expected "
                f"auren-mf-context — the contract fixes context at rank 1",
            )

        order: list[str] = []
        for group in groups[1:]:
            tokens = {
                m.group("surface")
                for m in (ID_RE.match(p.get("id") or "") for p in group.iter(f"{{{SVG_NS}}}path"))
                if m
            }
            order.append("+".join(sorted(tokens)) if tokens else "?")
        per_frame_order[frame] = order

    distinct = {tuple(v) for v in per_frame_order.values()}
    if len(distinct) > 1:
        report.error(
            "SURFACE_ORDER_UNSTABLE",
            f"surface order differs between frames: {per_frame_order} — the order "
            f"must be identical in every frame of a plate",
        )


def _check_id_grammar(
    path_id: str, frame: str, report: IntakeReport
) -> re.Match[str] | None:
    """Grammar, region agreement and frame agreement for one path id."""
    match = ID_RE.match(path_id)
    if not match:
        report.error(
            "ID_GRAMMAR",
            f"id {path_id!r} does not match "
            f"auren-plate-region-{{region}}--[{{frame}}-]{{surface}}-{{NNN}}",
        )
        return None

    if report.region and match.group("region") != report.region:
        report.error(
            "ID_REGION",
            f"id {path_id!r} declares region {match.group('region')!r} "
            f"inside plate {report.region!r}",
        )

    id_frame = match.group("frame")
    if id_frame and id_frame != frame:
        report.error(
            "ID_FRAME_MISMATCH",
            f"id {path_id!r} says frame {id_frame!r} but sits in frame "
            f"{frame!r} — the GROUP is authoritative",
        )
    return match


def _classify_surface(
    surface: str, report: IntakeReport, unmapped: set[str], zones_found: set[str]
) -> str:
    """Resolve a surface to a zone label, recording any contract breach."""
    if surface not in NON_ZONE_SURFACES and _as_zone_code(surface) in FORBIDDEN_ZONE_CODES:
        report.error(
            "FORBIDDEN_ZONE_TOKEN",
            f"surface {surface!r} names a business zone this project refuses "
            f"to create; rename the surface or adjudicate it in the contract",
        )

    zone = SURFACE_ZONE_MAP.get((report.region, surface))
    if zone:
        zones_found.add(zone)
        return zone
    if surface in NON_ZONE_SURFACES:
        return f"— [{NON_ZONE_SURFACES[surface]}]"
    unmapped.add(surface)
    return "— [UNDECLARED]"


def _check_paths(report: IntakeReport, views: list[ET.Element]) -> None:
    seen_ids: set[str] = set()
    unmapped: set[str] = set()
    zones_found: set[str] = set()

    for view in views:
        frame = _frame_of(view)
        for path in view.iter(f"{{{SVG_NS}}}path"):
            path_id = path.get("id") or ""
            if not path_id:
                report.error("PATH_NO_ID", f"frame {frame!r}: a <path> has no id")
                continue
            if path_id in seen_ids:
                report.error("ID_DUPLICATE", f"id {path_id!r} appears more than once")
            seen_ids.add(path_id)

            match = _check_id_grammar(path_id, frame, report)
            if match is None:
                continue

            surface = match.group("surface")
            label = _classify_surface(surface, report, unmapped, zones_found)
            report.rows.append(SurfaceRow(report.region, frame, surface, path_id, label))

    for surface in sorted(unmapped):
        report.error(
            "SURFACE_UNMAPPED",
            f"surface {surface!r} maps to no business zone and carries no contract "
            f"decision — declare it in SURFACE_ZONE_MAP or NON_ZONE_SURFACES, or "
            f"rename it. An asset may not create a zone.",
        )
    report.unmapped_surfaces = sorted(unmapped)

    expected = REGION_EXPECTED_ZONES.get(report.region, ())
    report.missing_zones = [z for z in expected if z not in zones_found]


def _check_element_safety(element: ET.Element, report: IntakeReport) -> None:
    """Runtime hazards carried by a single element."""
    tag = _local(element.tag)

    if tag == "script":
        report.error("SCRIPT", "the plate contains a <script> element")
    elif tag == "image":
        report.error("RASTER", "the plate embeds an <image>; plates must be vector")

    if "fill" in (element.get("style") or ""):
        report.error(
            "INLINE_FILL",
            f"<{tag} id={element.get('id')!r}> sets fill inline; inline style "
            f"beats the stylesheet and would take the surface out of contract "
            f"control (OQ_POSITIONAL_CSS_01)",
        )

    handlers = [a for a in element.attrib if a.lower().startswith("on")]
    for handler in handlers:
        report.error("EVENT_HANDLER", f"<{tag}> carries handler {handler!r}")

    if tag == "path" and element.get("fill"):
        report.warn(
            "PRESENTATION_FILL",
            f"path {element.get('id')!r} has a fill attribute; harmless today "
            f"(CSS wins) but it hides the real colour from a reader",
        )


def _check_runtime_safety(root: ET.Element, report: IntakeReport) -> None:
    for element in root.iter():
        _check_element_safety(element, report)


def validate(path: str | Path) -> IntakeReport:
    """Run every structural check on one candidate SVG."""
    path = Path(path)
    report = IntakeReport(path=path)

    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        report.error("NOT_FOUND", f"no such file: {path}")
        return report

    # Candidates arrive from an external workspace, so the input is untrusted.
    # Entity-expansion and external-entity attacks both require a DTD, and a
    # plate has no business carrying one — rejecting it removes the attack class
    # instead of suppressing the warning. This is why the ET.parse below is safe
    # without adding a dependency.
    lowered = raw[:4096].lower()
    if "<!doctype" in lowered or "<!entity" in lowered:
        report.error(
            "DTD_PRESENT",
            "the file declares a DTD or entities; plate assets must be plain SVG",
        )
        return report

    try:
        root = ET.fromstring(raw)  # noqa: S314 — DTD rejected above
    except ET.ParseError as exc:
        report.error("NOT_XML", f"cannot parse as XML: {exc}")
        return report

    panels = _check_root(root, report)
    if not panels:
        return report

    views = _check_frames(root, report, panels)
    if not views:
        return report

    _check_structure(views, report)
    _check_paths(report, views)
    _check_runtime_safety(root, report)
    return report


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if not args:
        print(__doc__)
        print("error: give at least one SVG path", file=sys.stderr)
        return 2

    failed = 0
    for candidate in args:
        report = validate(candidate)
        print(report.render())
        print()
        if not report.ok:
            failed += 1

    total = len(args)
    print(f"=== {total - failed}/{total} candidate(s) structurally conform ===")
    if failed:
        print("Anatomical review is a separate, human gate — not performed here.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
