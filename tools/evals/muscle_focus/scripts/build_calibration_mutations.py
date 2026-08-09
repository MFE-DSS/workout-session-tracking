#!/usr/bin/env python3
"""Build the 12 calibration mutations — GO C2 §9. Evaluation-only mutated copies of the review
evidence, written OUTSIDE Git under <ROOT>/08_synthetic_review/calibration/mutations/. Accepted
candidates are never altered. Deterministic (PIL + text edits).

Reads AUREN_MUSCLE_FOCUS_REVIEW_ROOT (the external operator workspace root). No hardcoded path.
Evidence lives under <ROOT>/07_external_review/sb-asset-03b-2r-qualified-anatomical-review/.
"""
from __future__ import annotations

import json
import os
import pathlib

from PIL import Image

ROOT = pathlib.Path(os.environ["AUREN_MUSCLE_FOCUS_REVIEW_ROOT"])
PKG = ROOT / "07_external_review/sb-asset-03b-2r-qualified-anatomical-review"
OUT = ROOT / "08_synthetic_review/calibration/mutations"

AMBER = (246, 198, 103)   # anterior deltoid / gluteus
NEUTRAL = (238, 238, 238)
CONTEXT_MD = "context.md"
SH_COMPARE = "shoulders_front_back_comparison.png"
POST_S2P = "auren-plate-region-posterior.source-to-path.json"


def _img(rel):
    return Image.open(PKG / rel).convert("RGB")


def mirror(rel, dst):
    _img(rel).transpose(Image.FLIP_LEFT_RIGHT).save(dst)
    return str(dst)


def blank_half(rel, dst, side):
    im = _img(rel).copy()
    w, h = im.size
    box = (w // 2, 0, w, h) if side == "right" else (0, 0, w // 2, h)
    im.paste(NEUTRAL, box)
    im.save(dst)
    return str(dst)


def recolor_to_bg(rel, dst, target, tol=40):
    im = _img(rel).resize((1024, 1024), Image.NEAREST)
    px = bytearray(im.tobytes())
    for i in range(0, len(px), 3):
        if abs(px[i] - target[0]) <= tol and abs(px[i + 1] - target[1]) <= tol and abs(px[i + 2] - target[2]) <= tol:
            px[i], px[i + 1], px[i + 2] = NEUTRAL
    Image.frombytes("RGB", (1024, 1024), bytes(px)).save(dst)
    return str(dst)


def scale_one_half(rel, dst):
    im = _img(rel)
    w, h = im.size
    left = im.crop((0, 0, w // 2, h)).resize((int(w * 0.32), int(h * 0.72)), Image.LANCZOS)
    canvas = Image.new("RGB", (w, h), NEUTRAL)
    canvas.paste(im.crop((w // 2, 0, w, h)), (w // 2, 0))
    canvas.paste(left, (0, 0))
    canvas.save(dst)
    return str(dst)


def edit_json(rel, dst, fn):
    d = json.loads((PKG / rel).read_text())
    fn(d)
    pathlib.Path(dst).write_text(json.dumps(d, indent=2))
    return str(dst)


def write_text(dst, text):
    pathlib.Path(dst).write_text(text)
    return str(dst)


def _collapse_posterior_provenance(x):
    for p in x.get("paths", []):
        if p.get("sources"):
            p["sources"] = [{"name": "hamstring", "obj_sha256": "x"}]


CASES = []


def case(cid, region, desc, critical, veto_types, keywords, targets, build):
    d = OUT / cid
    d.mkdir(parents=True, exist_ok=True)
    produced = build(d)
    meta = {"case_id": cid, "region": region, "description": desc, "is_critical": bool(critical),
            "must_detect": True, "expected_veto_types": veto_types, "expected_keywords": keywords,
            "target_judges": targets, "mutated_files": [pathlib.Path(p).name for p in produced]}
    (d / "case.json").write_text(json.dumps(meta, indent=2) + "\n")
    CASES.append(meta)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    case("01_chest_mirrored", "chest", "Horizontally mirrored chest preview.", True,
         ["mirror_or_laterality_inversion"], ["mirror", "flipped", "laterality"], ["J1", "J4"],
         lambda d: [mirror("02_PREVIEWS/chest_isolated_neutral.png", d / "chest_isolated_neutral.png")])

    case("02_chest_side_removed", "chest", "One pectoralis side removed.", True,
         ["mandatory_source_structure_missing"], ["missing", "one side", "absent", "unilateral"], ["J1", "J4"],
         lambda d: [blank_half("03_DIAGNOSTICS/chest_hero_only.png", d / "chest_hero_only.png", "right")])

    case("03_chest_false_source_segmented", "chest", "Chest partition falsely marked source-segmented.", False,
         ["false_source_segmented_claim"], ["source-segmented", "separately_segmented", "partition"], ["J5", "J4"],
         lambda d: [edit_json("04_PROVENANCE/auren-plate-region-chest.source-to-path.json",
                              d / "auren-plate-region-chest.source-to-path.json",
                              lambda x: x.__setitem__("pectoralis_source_mesh_separately_segmented", True))])

    case("04_chest_partition_accepted", "chest", "Chest diagnostic partition presented as accepted for product.", True,
         ["false_professional_approval_claim"], ["partition accepted", "accepted for product", "unresolved"], ["J5", "J4"],
         lambda d: [write_text(d / CONTEXT_MD,
                               "CHEST CONTEXT (mutated): The clavicular/sternocostal partition is ACCEPTED FOR "
                               "PRODUCT USE and fully resolved. Plan-B is closed.\n")])

    case("05_shoulders_back_removed", "shoulders", "Shoulders back view removed.", False,
         ["mandatory_source_structure_missing"], ["back view", "missing view", "only front"], ["J2", "J4"],
         lambda d: [blank_half("03_DIAGNOSTICS/" + SH_COMPARE, d / SH_COMPARE, "right")])

    case("06_shoulders_labels_swapped", "shoulders", "Shoulders anterior and posterior labels swapped.", True,
         ["mirror_or_laterality_inversion"], ["anterior", "posterior", "swapped", "mapping", "label"], ["J1", "J4"],
         lambda d: [write_text(d / CONTEXT_MD,
                               "SHOULDERS CONTEXT (mutated): clavicular part -> POSTERIOR deltoid; spinal part -> "
                               "ANTERIOR deltoid (anterior/posterior mapping swapped).\n")])

    case("07_shoulders_scale_mismatch", "shoulders", "Shoulders front/back scale mismatch.", False,
         ["mandatory_source_structure_missing"], ["scale", "mismatch", "different size", "not shared"], ["J2", "J4"],
         lambda d: [scale_one_half("03_DIAGNOSTICS/" + SH_COMPARE, d / SH_COMPARE)])

    case("08_shoulders_part_hidden", "shoulders", "One deltoid source part hidden.", True,
         ["mandatory_source_structure_missing"], ["missing part", "anterior", "hidden", "deltoid part"], ["J1", "J4"],
         lambda d: [recolor_to_bg("03_DIAGNOSTICS/shoulders_front_source_part_audit.png",
                                  d / "shoulders_front_source_part_audit.png", AMBER)])

    case("09_posterior_gluteus_removed", "posterior", "Posterior gluteus maximus removed.", True,
         ["mandatory_source_structure_missing"], ["gluteus", "missing", "absent"], ["J1", "J4"],
         lambda d: [recolor_to_bg("03_DIAGNOSTICS/posterior_grouped_presentation_audit.png",
                                  d / "posterior_grouped_presentation_audit.png", AMBER)])

    case("10_posterior_hamstrings_merged", "posterior", "Posterior hamstrings falsely merged into one source muscle.", True,
         ["false_source_segmented_claim", "source_provenance_lost"],
         ["unified", "merged", "single muscle", "hamstring"], ["J5", "J4"],
         lambda d: [edit_json("04_PROVENANCE/" + POST_S2P, d / POST_S2P,
                              lambda x: x.__setitem__("hamstring_unified_source_mesh", True))])

    case("11_posterior_provenance_removed", "posterior", "Individual posterior hamstring provenance removed.", True,
         ["source_provenance_lost"], ["provenance", "individual", "collapsed", "one source"], ["J5", "J4"],
         lambda d: [edit_json("04_PROVENANCE/" + POST_S2P, d / POST_S2P, _collapse_posterior_provenance)])

    case("12_false_professional_runtime_claim", "posterior", "Runtime/professional-anatomical approval falsely asserted.", True,
         ["false_professional_approval_claim", "unsafe_runtime_claim"],
         ["professional review", "certified", "runtime approved", "medically approved"], ["J5", "J4"],
         lambda d: [write_text(d / CONTEXT_MD,
                               "GLOBAL CONTEXT (mutated): This plate has PASSED qualified professional anatomical "
                               "review and is APPROVED FOR RUNTIME and medically certified.\n")])

    (OUT.parent / "manifest.json").write_text(json.dumps(
        {"_schema": "calibration manifest", "count": len(CASES),
         "critical_count": sum(1 for c in CASES if c["is_critical"]), "cases": CASES}, indent=2) + "\n")
    print(f"calibration mutations: {len(CASES)} cases ({sum(1 for c in CASES if c['is_critical'])} critical) -> {OUT}")
    for c in CASES:
        print(f"  {c['case_id']:38} critical={c['is_critical']!s:5} targets={c['target_judges']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
