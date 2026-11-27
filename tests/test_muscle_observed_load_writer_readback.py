"""Real inventory2 -> evaluation -> START -> SET -> FINISH -> strict read-only DTO."""

import hashlib
import json
import os
from datetime import UTC, datetime, timedelta

from tests.test_plan_cal_01_owned import Journey, plan_bundle, science_bundle, setup_runtime

# Reuse the canonical inventory2 fixture and actual controlled HTTP journey.
# Imported fixtures are required by pytest, not mocked source authorities.
__all__ = ["plan_bundle", "science_bundle"]

PUBLIC_CONTEXT = {"context_ref", "equipment_ref", "realization_ref", "side", "load_semantics"}


def read_owned(owner, science_bundle):
    from app.services.muscle_observed_load.contracts import ObservedLoadQuery
    from app.services.muscle_observed_load.limits import ReadLimits
    from app.services.muscle_observed_load.projection import SourceView, project_capture
    from app.services.muscle_observed_load.sqlite_source import open_owned_capture

    now = datetime.now(UTC)
    query = ObservedLoadQuery(now - timedelta(days=1), now)
    source = SourceView.local()
    source.bundle_root = str(science_bundle[0])
    with open_owned_capture(os.environ["DATABASE_URL"], owner, query) as capture:
        return project_capture(
            capture, query, source, ReadLimits(), as_of=now, runtime_profile_digest="0" * 64
        ).model_dump()


def verify_digest(out):
    check = json.loads(json.dumps(out))
    expected = check["consistency"]["result_digest"]
    check["consistency"]["result_digest"] = "0" * 64
    assert (
        hashlib.sha256(
            json.dumps(
                check, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(",", ":")
            ).encode()
        ).hexdigest()
        == expected
    )


def test_actual_inventory2_completed_set_context_and_mixed_readback(
    client, monkeypatch, science_bundle
):
    h, authority, pins = setup_runtime(client, monkeypatch, science_bundle)
    j = Journey(client, h)
    fields = {
        k: {"state": "KNOWN", "value": v}
        for k, v in {
            "objective": "HYPERTROPHY",
            "population_scope": "ADULT_NON_CLINICAL",
            "sessions_per_week": 2,
            "session_budgets_minutes": [60, 60],
            "limitations": [],
        }.items()
    }
    j.revision = j.call(
        "PUT",
        "/me/blueprint/declarations",
        {"request_id": j.key(), "fields": fields},
        {"If-Match": "0"},
    )["source_revision"]
    refs = []
    for i, spec in enumerate(authority["calibration_inventory"]["profiles"]):
        refs.append(j.qualify(spec, 17.0 + i)[0])  # Explicit synthetic user observations only.
    snapshot = j.call(
        "POST", "/me/blueprint/snapshots", {"request_id": j.key(), "expected_revision": j.revision}
    )
    evaluated = j.call(
        "POST",
        "/me/first-plan/evaluations",
        {"request_id": j.key(), "snapshot_ref": snapshot["snapshot_ref"], "expected_pins": pins},
    )
    r = evaluated["recommendation"]
    assert r["scientific_readiness"] == "SCIENTIFICALLY_READY"
    assert r["start_permission"] == "REQUIRES_TIME_ACK"
    assert all(t["state"] == "BUDGET_UNCERTAIN" for t in r["time_assessments"])
    final = j.call(
        "POST",
        "/me/first-plan/evaluations/" + evaluated["evaluation_ref"] + "/time-acknowledgments",
        {
            "request_id": j.key(),
            "expected_context": {
                k: r[k]
                for k in (
                    "request_fingerprint",
                    "observation_fingerprint",
                    "plan_time_fingerprint",
                    "start_policy_ref",
                )
            },
        },
    )
    r = final["recommendation"]
    assert r["start_permission"] == "ELIGIBLE"
    command = {
        k: r[k]
        for k in (
            "request_fingerprint",
            "observation_fingerprint",
            "full_evaluation_fingerprint",
            "plan_time_fingerprint",
            "binding_ref",
            "binding_digest",
            "bundle_digest",
            "effective_science_digest",
            "engine_version",
            "policy_version",
            "contract_version",
        )
    }
    command.update(
        evaluation_ref=final["evaluation_ref"],
        snapshot_ref=snapshot["snapshot_ref"],
        source_revision=j.revision,
        registry_digest=pins["registry_digest"],
        selected_scientific_session_id=r["candidate_plan"]["sessions"][0]["session_id"],
    )
    body = {"request_id": j.key(), "command": command}
    started = j.call("POST", "/me/first-session-requests", body)
    assert started["state"] == "CREATED"
    assert j.call("POST", "/me/first-session-requests", body)["session_id"] == started["session_id"]
    execution = j.call("GET", f"/sessions/{started['session_id']}/execution")["execution"]
    assert len(execution["exercises"]) == 7
    assert sum(len(e["sets"]) for e in execution["exercises"]) == 14
    sid = started["session_id"]
    expected = {}
    for exercise in execution["exercises"]:
        context = exercise["prescription"]["context"]
        assert set(context) == PUBLIC_CONTEXT | {"canonical_exercise_id"}
        assert context["canonical_exercise_id"] == exercise["canonical_exercise_id"]
        for row in exercise["sets"]:
            observation = dict(
                context=context,
                setting=exercise["prescription"]["setting"],
                reps=9,
                completed=True,
                performed_at=datetime.now(UTC).isoformat(),
                performed_at_estimated=False,
            )
            command = dict(
                op_id=f"writer-readback-{row['set_id']}",
                expected_set_revision=0,
                observation=observation,
            )
            receipt = j.call("PUT", f"/sessions/{sid}/sets/{row['set_id']}", command)["receipt"]
            assert receipt["state"] == "APPLIED"
            assert (
                j.call("PUT", f"/sessions/{sid}/sets/{row['set_id']}", command)["receipt"]
                == receipt
            )
            expected[row["set_id"]] = (exercise, observation, receipt)
    finished = client.post(f"/api/mobile/v1/sessions/{sid}/finish", headers=h, json={})
    assert finished.status_code == 200, finished.text
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession
    from app.models.user import User

    with SessionLocal() as db:
        session = db.get(WorkoutSession, sid)
        owner = session.user_id
        assert session.status == "completed"
        assert not session.excluded_from_stats
        assert sum(len(e["sets"]) for e in execution["exercises"]) == 14
        original = [(s.id, s.completed_at, s.weight_kg) for s in db.scalars(select(SetLog))]
    out = read_owned(owner, science_bundle)
    assert len(out["facts"]) == 14
    from app.services.muscle_observed_load.provenance import SourceView

    bundle = SourceView.bundle(*science_bundle)
    catalogue = bundle.catalogue_view().document
    for fact in out["facts"]:
        exercise, observation, receipt = expected[fact["key"]["set_log_id"]]
        identity = exercise["canonical_exercise_id"]
        assert fact["key"]["session_id"] == sid
        assert fact["resolution"]["canonical_exercise_id"] == identity
        assert fact["context"] == {k: observation["context"][k] for k in PUBLIC_CONTEXT}
        assert fact["setting"] == observation["setting"]
        assert fact["reps"] == 9
        p = fact["provenance"]
        assert p["source_status"] == "QUALIFIED"
        assert p["binding_digest"] == execution["binding_digest"]
        assert (
            p["effective_operation"]["op_id"] == p["origin_operation"]["op_id"] == receipt["op_id"]
        )
        assert p["effective_operation"]["applied_revision"] == 1
        assert datetime.fromisoformat(
            fact["temporal"]["performed_at"].replace("Z", "+00:00")
        ) == datetime.fromisoformat(receipt["performed_at"])
        assert fact["temporal"]["performed_at_estimated"] is False
        record = next(x for x in catalogue["records"] if x["exercise_id"] == identity)
        roles = bundle.v3["candidates"][identity]["effective_roles"]
        assert fact["contributions"] == [
            dict(
                zone=x["zone"],
                raw_role=x["role"],
                role_basis=x["role_basis"],
                evidence_refs=list(x["evidence_refs"]),
                execution_uncertain="content_alignment" in record,
            )
            for x in roles
        ]
        if fact["context"]["load_semantics"] != "TOTAL_EXTERNAL":
            assert fact["weight_kg"] is None
    verify_digest(out)
    # Explicit independent Legacy fixtures: no claim of first-plan writer origin.
    with SessionLocal() as db:
        for i in range(86):
            legacy = WorkoutSession(
                user_id=owner,
                template_slug_snapshot="synthetic-legacy",
                template_name_snapshot="Synthetic Legacy",
                started_at=datetime.now(UTC),
                status="completed",
            )
            db.add(legacy)
            db.flush()
            ex = SessionExercise(
                session_id=legacy.id,
                exercise_code_snapshot="L",
                exercise_name_snapshot="Pompes",
                position=0,
            )
            db.add(ex)
            db.flush()
            db.add(
                SetLog(
                    session_exercise_id=ex.id,
                    kind="work",
                    set_index=1,
                    completed=True,
                    completed_at=datetime.now(UTC),
                    reps=8,
                )
            )
        other = User(username="readback-other", password_hash="synthetic-unused")
        db.add(other)
        db.commit()
        other_id = other.id
    mixed = read_owned(owner, science_bundle)
    assert len(mixed["facts"]) == 100
    assert sum(f["provenance"]["profile"] == "V3" for f in mixed["facts"]) == 14
    verify_digest(mixed)
    assert read_owned(other_id, science_bundle)["facts"] == []
    with SessionLocal() as db:
        actual = [
            (s.id, s.completed_at, s.weight_kg)
            for s in db.scalars(select(SetLog).where(SetLog.id.in_([x[0] for x in original])))
        ]
        assert actual == original
