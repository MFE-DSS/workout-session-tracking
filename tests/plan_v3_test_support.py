"""Explicit disposable private bundle fixture; never app runtime input data."""

import pytest


@pytest.fixture(scope="session")
def science_bundle(tmp_path_factory):
    from scripts.build_plan_v3_runtime_bundle import build_bundle

    root = tmp_path_factory.mktemp("plan-science") / "bundle"
    return root, build_bundle(root)


@pytest.fixture(autouse=True)
def plan_bundle(client, monkeypatch, science_bundle):
    from app.config import get_settings

    monkeypatch.setattr(get_settings(), "plan_v3_bundle_path", str(science_bundle[0]))
    return science_bundle


def activate_test_authority(db, science_bundle):
    from app.models.first_plan_runtime import FirstPlanRuntimeAuthority
    from app.services.plan_v3.packaging import execute_science
    from app.services.plan_v3.snapshots import canonical

    authorities = execute_science(
        "authorities", {}, root=science_bundle[0], expected_digest=science_bundle[1]
    )
    v = authorities["v3"]
    pins = {
        key: v[key]
        for key in (
            "registry_digest",
            "binding_digest",
            "bundle_digest",
            "effective_science_digest",
        )
    }
    db.add(
        FirstPlanRuntimeAuthority(
            profile_key="first-session-runtime/3.0.0",
            generation=1,
            state="ACTIVE",
            publication_json=canonical(pins),
            packaging_digest=science_bundle[1],
            approval_ref="GO_BUILD_CONTROLLED:DISPOSABLE_SYNTHETIC_FIXTURE",
        )
    )
    db.commit()
    return authorities, pins


def acquire_qualified(db, owner, authority):
    """Actual append calls with explicit synthetic observations, not READY input JSON."""
    import json
    from datetime import UTC, datetime

    from app.services.plan_v3 import snapshots as s

    s.declare(
        db,
        owner,
        request_id="minimum",
        expected_revision=0,
        fields={
            key: {"state": "KNOWN", "value": value}
            for key, value in {
                "objective": "HYPERTROPHY",
                "population_scope": "ADULT_NON_CLINICAL",
                "sessions_per_week": 2,
                "session_budgets_minutes": [60, 60],
                "limitations": [],
            }.items()
        },
    )
    db.commit()
    for pos, spec in enumerate(authority["v3"]["policy"]["selection"]):
        context = {
            "canonical_exercise_id": spec["candidate_id"],
            "realization_ref": spec["realization_ref"],
            "context_ref": "synthetic:gym",
            "equipment_ref": "synthetic:device:" + str(pos),
            "side": "BILATERAL",
            "load_semantics": "PER_IMPLEMENT" if pos == 3 else "MACHINE_DISPLAY_KG",
        }
        row = s.append_owned_observation(
            db,
            owner,
            request_id=f"open-{pos}",
            expected_revision=s.current_revision(db, owner),
            event={"kind": "CONTEXT_OPENED", "context": context, "availability": "AVAILABLE"},
        )
        ref = json.loads(row.payload_json)["episode_ref"]
        db.commit()
        load = {
            "kind": "MASS_KG",
            "value": 17.0 + pos,
            "unit": "kg",
        }  # Synthetic observed device values only.
        values = [
            {"kind": "CONTEXT_CONFIRMED", "setting": load},
            {"kind": "FAMILIARIZATION_CONFIRMED"},
            {
                "kind": "ATTEMPT_OBSERVED",
                "setting": load,
                "reps": 10,
                "completed": True,
                "successful": True,
                "technique": "ACCEPTABLE",
                "discomfort": "NO_CONCERN",
                "occurred_at": datetime.now(UTC).isoformat(),
            },
        ]
        attempt = None
        for n, event in enumerate(values):
            if event["kind"] == "ATTEMPT_OBSERVED":
                event["occurred_at"] = datetime.now(UTC).isoformat()
            row = s.append_owned_observation(
                db,
                owner,
                request_id=f"event-{pos}-{n}",
                expected_revision=s.current_revision(db, owner),
                event={"kind": "CALIBRATION_EVENT", "episode_ref": ref, "event": event},
            )
            db.commit()
            attempt = row.id
        s.append_owned_observation(
            db,
            owner,
            request_id=f"accept-{pos}",
            expected_revision=s.current_revision(db, owner),
            event={
                "kind": "CALIBRATION_EVENT",
                "episode_ref": ref,
                "event": {"kind": "SETTING_ACCEPTED", "reference_event_id": attempt},
            },
        )
        db.commit()
    snap = s.build_owned_snapshot(
        db, owner, request_id="qualified-snapshot", expected_revision=s.current_revision(db, owner)
    )
    db.commit()
    return snap
