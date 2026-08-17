"""Sb_BODYMAP_FRAME_ATLAS_01 — declarative zone → surfaces → frames contract.

WHY THIS MODULE EXISTS
----------------------
Before this build, "which view of which plate does a zone get?" was answered by
hard-coded markup: ``muscle_focus.html`` inlined two radio inputs whose ids were
literals, and ``app.css`` shifted the shoulders filmstrip with an id-specific
rule. Adding a third view meant editing a template, a stylesheet and a test.

This module makes the answer **declarative data**. A region declares the frames
its plate actually contains; the template renders whatever is declared; the CSS
is generic over N. Adding a produced frame becomes a one-line data change.

THE GOVERNING RULE (Sb_BODYMAP_FRAME_ATLAS_01, architect decision)
------------------------------------------------------------------
    The business model governs the visual. The visual never creates a zone.

Consequences, all enforced by tests:

* The eleven zones of ``muscle_mapping.ZONE_LABELS`` remain the only business
  zones. This module declares no zone of its own.
* Option A for the shoulders: there is **no** ``delt_ant`` business zone. The
  ``*-delt-anterior`` surfaces that exist inside the shoulders plate are
  depicted by the shoulders plate as a whole; they are not addressable as a
  zone and carry no separate recovery state.
* ``pecs`` stays a single zone. The clavicular / sternocostal distinction may be
  explained in prose or shown by a profile frame, never modelled as a zone.
  See ``OQ_PEC_SPLIT_01`` in docs — deliberately not built.

HONEST ABSENCE
--------------
Seven of the eleven zones have no plate at all. A zone without geometry is
reported as such: it falls back to the macro silhouette or stays neutral. It is
never coloured as if it were known, and never borrows a neighbouring region's
geometry. ``geometry_status`` in the design contract stays the source of truth
for what has actually been produced.

NON-MEDICAL
-----------
Frame labels and landmarks describe *what is visible in the drawing* so the
reader can tell one view from another. They make no claim about activation,
effort share, recovery physiology, diagnosis or injury.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.services.muscle_mapping import ZONE_LABELS

# ── frame vocabulary ────────────────────────────────────────────────────────
# Four cardinal frames, frozen for V1 (architect decision: not twelve angles).
# A frame code is a *viewpoint*, never a body zone.

FRAME_FRONT = "front"
FRAME_PROFILE = "profile"
FRAME_BACK = "back"
FRAME_TOP = "top"

#: Canonical rendering order. A plate's frames are always presented in this
#: order regardless of the order they were declared in.
FRAME_ORDER: tuple[str, ...] = (FRAME_FRONT, FRAME_PROFILE, FRAME_BACK, FRAME_TOP)

#: Short label shown on the selector control. Kept terse: the pills sit side by
#: side inside a 360 px column.
FRAME_LABELS: dict[str, str] = {
    FRAME_FRONT: "Face",
    FRAME_PROFILE: "Profil",
    FRAME_BACK: "Dos",
    FRAME_TOP: "Dessus",
}


# ── render modes ────────────────────────────────────────────────────────────
#: The zone has a regional plate: real traced geometry can be shown.
RENDER_PLATE = "plate"
#: The zone has no plate: only the schematic macro silhouette can represent it.
RENDER_MACRO = "macro"
#: No qualified zone at all. Not an anatomical state — nothing is highlighted.
RENDER_NONE = "none"


@dataclass(frozen=True)
class PlateFrame:
    """One produced viewpoint of one regional plate.

    ``landmark`` names a bony feature actually visible in *this* frame so the
    reader can tell which way the body is facing — the orientation cue validated
    during the Atlas des Cadres review. It is ``None`` when no landmark has been
    reviewed for that frame; the template then shows the label alone rather than
    inventing a cue.
    """

    code: str
    label: str
    landmark: str | None = None


@dataclass(frozen=True)
class RegionalPlate:
    """A produced SVG plate and the business zones it can depict.

    ``frames`` is ordered by :data:`FRAME_ORDER` and its length is the filmstrip
    divisor: the SVG is a horizontal strip of ``len(frames)`` equal panels, the
    viewport crops to one panel, and the selector slides between them. This is
    the mechanism that already shipped for shoulders (front|back), generalised.
    """

    region: str
    partial: str
    frames: tuple[PlateFrame, ...]
    zones: tuple[str, ...]

    @property
    def frame_count(self) -> int:
        return len(self.frames)

    @property
    def is_strip(self) -> bool:
        """True when the plate holds more than one frame and needs a selector."""
        return len(self.frames) > 1


# ── produced plates ─────────────────────────────────────────────────────────
# ONLY plates whose SVG exists in the repository today. Declaring a frame here
# that has not been produced would make the selector offer an empty panel, so
# this table is allowed to grow only when a plate genuinely gains a frame.
#
# Current geometry (measured, frozen by SHA in tests/test_auren_muscle_focus_runtime.py):
#   chest      1 panel  — front
#   shoulders  2 panels — front | back   (4096x2048, two 2048 halves)
#   posterior  1 panel  — back

REGIONAL_PLATES: tuple[RegionalPlate, ...] = (
    RegionalPlate(
        region="chest",
        partial="_partials/muscle_focus_plate_chest.svg",
        frames=(
            PlateFrame(
                FRAME_FRONT,
                FRAME_LABELS[FRAME_FRONT],
                "sternum et clavicules visibles",
            ),
        ),
        zones=("pecs",),
    ),
    RegionalPlate(
        region="shoulders",
        partial="_partials/muscle_focus_plate_shoulders.svg",
        frames=(
            PlateFrame(
                FRAME_FRONT,
                FRAME_LABELS[FRAME_FRONT],
                "clavicule et acromion visibles",
            ),
            PlateFrame(
                FRAME_BACK,
                FRAME_LABELS[FRAME_BACK],
                "épine de la scapula visible",
            ),
        ),
        # Option A: delt_lat and delt_post only. No delt_ant zone exists, even
        # though the plate holds distinct *-delt-anterior surfaces.
        zones=("delt_lat", "delt_post"),
    ),
    RegionalPlate(
        region="posterior",
        partial="_partials/muscle_focus_plate_posterior.svg",
        frames=(
            PlateFrame(
                FRAME_BACK,
                FRAME_LABELS[FRAME_BACK],
                "bassin et fémur en repères",
            ),
        ),
        zones=("posterior",),
    ),
)


@dataclass(frozen=True)
class ZoneSurface:
    """How one business zone can currently be depicted.

    ``render_mode`` is the honest answer, not an aspiration: ``plate`` only when
    traced geometry exists for that zone today.
    """

    zone: str
    label: str
    plate: RegionalPlate | None
    render_mode: str

    @property
    def has_geometry(self) -> bool:
        return self.plate is not None

    @property
    def frames(self) -> tuple[PlateFrame, ...]:
        return self.plate.frames if self.plate else ()


#: The state used when nothing is qualified. Mirrors ``unknown_state`` in the
#: design contract: not a twelfth zone, no geometry, nothing highlighted.
UNKNOWN_SURFACE = ZoneSurface(
    zone="unknown",
    label="À qualifier",
    plate=None,
    render_mode=RENDER_NONE,
)


def _zone_to_plate() -> dict[str, RegionalPlate]:
    index: dict[str, RegionalPlate] = {}
    for plate in REGIONAL_PLATES:
        for zone in plate.zones:
            index[zone] = plate
    return index


_ZONE_TO_PLATE = _zone_to_plate()


def regional_plates() -> tuple[RegionalPlate, ...]:
    """Every produced plate, in declaration order (the /science page order)."""
    return REGIONAL_PLATES


def plate_for_region(region: str) -> RegionalPlate | None:
    for plate in REGIONAL_PLATES:
        if plate.region == region:
            return plate
    return None


def resolve_zone_surface(zone: str | None) -> ZoneSurface:
    """Resolve a business zone to its current depiction.

    Anything that is not one of the eleven canonical zones — ``None``, the
    ``unknown`` qualification state, a typo, a zone invented downstream —
    resolves to :data:`UNKNOWN_SURFACE`. It never guesses a nearby region.
    """
    if zone is None or zone not in ZONE_LABELS:
        return UNKNOWN_SURFACE
    plate = _ZONE_TO_PLATE.get(zone)
    return ZoneSurface(
        zone=zone,
        label=ZONE_LABELS[zone],
        plate=plate,
        render_mode=RENDER_PLATE if plate else RENDER_MACRO,
    )


def zone_surfaces() -> tuple[ZoneSurface, ...]:
    """All eleven zones, whether or not they have geometry.

    This is the "eleven zones wired empty" socle: consumers can iterate the full
    taxonomy today and each plate produced later simply flips one entry from
    ``macro`` to ``plate`` without touching call sites.
    """
    return tuple(resolve_zone_surface(zone) for zone in ZONE_LABELS)


def geometry_coverage() -> dict[str, int]:
    """Counts for reporting: how much of the taxonomy has real geometry."""
    surfaces = zone_surfaces()
    with_plate = sum(1 for s in surfaces if s.has_geometry)
    return {
        "zones_total": len(surfaces),
        "zones_with_plate": with_plate,
        "zones_without_plate": len(surfaces) - with_plate,
        "plates_produced": len(REGIONAL_PLATES),
    }
