"""Runtime selectors and qualified projection, never scientific admission rules."""

from __future__ import annotations

import json

from app.services.plan_v3.transactions import RuntimeFailure

INVENTORY = "plan-calibration-inventory/2.0.0"


def inventory(authorities, requested):
    if requested is None:
        return None
    value = authorities.get("calibration_inventory")
    if requested != INVENTORY or not value or value["version"] != requested:
        raise RuntimeFailure("calibration_inventory_not_supported", 406)
    return value


def profile(authorities, context, requested):
    value = inventory(authorities, requested)
    if value is None:
        policy = authorities["encounter"]["policy"]
        if context["canonical_exercise_id"] != policy["scope"]["candidate_id"]:
            raise RuntimeFailure("calibration_inventory_required", 406)
        return None
    found = next(
        (p for p in value["profiles"] if p["candidate_id"] == context["canonical_exercise_id"]),
        None,
    )
    if found is None or found["realization_ref"] != context["realization_ref"]:
        raise RuntimeFailure("calibration_profile_not_supported", 406)
    # UNKNOWN remains valid for opening help, never fabricated as a supported setting.
    if context["side"] != "BILATERAL" or context["load_semantics"] not in {
        found["load_semantics"],
        "UNKNOWN",
    }:
        raise RuntimeFailure("calibration_profile_not_supported", 406)
    return found


def selected_encounters(rows):
    chosen = {}
    for row in rows:
        payload = json.loads(row.payload_json)
        if (
            row.kind == "CALIBRATION_ENCOUNTER_OPENED"
            and payload.get("inventory_version") == INVENTORY
        ):
            chosen[payload["context"]["canonical_exercise_id"]] = row.id
        elif row.kind == "CALIBRATION_ENCOUNTER_SELECTED":
            chosen[payload["candidate_id"]] = payload["encounter_ref"]
    return chosen


def runtime_identity(operational, authorities):
    value = authorities.get("calibration_inventory")
    return {
        "inventory_version": value["version"] if value else None,
        "inventory_bundle_digest": value["bundle_digest"] if value else None,
        "packaging_digest": operational.packaging_digest,
        "authority_generation": operational.generation,
        "pilot_bundle_digest": authorities["encounter"]["bundle_digest"],
    }


def project_qualified(rows, owner, as_of, episodes, operational, authorities):
    from app.services.plan_v3.calibration import _request
    from app.services.plan_v3.packaging import execute_science

    chosen = selected_encounters(rows)
    guided = {}
    for row in rows:
        if row.kind == "CALIBRATION_ENCOUNTER_OPENED":
            data = json.loads(row.payload_json)
            guided.setdefault(data["context"]["canonical_exercise_id"], []).append(row.id)
    # A single historical guided encounter needs no invented selection event.
    for candidate, refs in guided.items():
        if candidate not in chosen and len(refs) == 1:
            chosen[candidate] = refs[0]
    kept, proofs, missing = [], [], []
    for ep in episodes:
        candidate = ep["context"]["canonical_exercise_id"]
        if candidate not in guided:
            if authorities.get("calibration_inventory"):
                missing.append(
                    ep["episode_id"]
                )  # Facts remain in the ledger, not inventory2 admission.
            else:
                kept.append(ep)  # Legacy runtime and replay preserve their admitted profile.
            continue
        if chosen.get(candidate) != ep["episode_id"]:
            continue
        raw = _request(rows, owner, ep["episode_id"], as_of)
        result = execute_science("calibration", raw, expected_digest=operational.packaging_digest)
        if result["state"] != "QUALIFIED" or result.get("portable_episode") is None:
            missing.append(ep["episode_id"])
        else:
            kept.append(result["portable_episode"])
            proofs.append(
                {
                    "encounter_ref": ep["episode_id"],
                    "input_digest": result["input_digest"],
                    "as_of": as_of,
                    "policy_ref": result["policy_ref"],
                }
            )
    for candidate, refs in guided.items():
        if candidate not in chosen:
            missing.extend(refs)
    return (
        kept,
        missing,
        {
            **runtime_identity(operational, authorities),
            "selected_encounters": chosen,
            "qualified_encounters": proofs,
        },
    )


def assert_snapshot_runtime(db, snapshot_id, operational, authorities):
    from app.models.first_plan_runtime import OwnedBlueprintSnapshot

    snapshot = db.get(OwnedBlueprintSnapshot, snapshot_id)
    if snapshot is None:
        raise RuntimeFailure("not_found", 404)
    captured = json.loads(snapshot.snapshot_json).get("calibration_runtime")
    if captured is None:
        # Old snapshots retain their original semantics only on a legacy runtime.
        if authorities.get("calibration_inventory"):
            raise RuntimeFailure("snapshot_calibration_runtime_changed")
        return
    current = runtime_identity(operational, authorities)
    if any(captured.get(k) != v for k, v in current.items()):
        raise RuntimeFailure("snapshot_calibration_runtime_changed")


def current_selection(rows, encounter_ref, candidate):
    chosen = selected_encounters(rows)
    if candidate in chosen:
        return chosen[candidate] == encounter_ref
    refs = [
        r.id
        for r in rows
        if r.kind == "CALIBRATION_ENCOUNTER_OPENED"
        and json.loads(r.payload_json)["context"]["canonical_exercise_id"] == candidate
    ]
    return refs == [encounter_ref]


def projection_context(episodes):
    contexts = {e["context"]["context_ref"] for e in episodes}
    return (
        next(iter(contexts))
        if len(contexts) == 1 and None not in contexts
        else "environment:unknown"
    )
