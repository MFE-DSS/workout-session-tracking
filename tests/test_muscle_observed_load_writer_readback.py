"""Real inventory2 -> evaluation -> START -> SET -> FINISH -> strict read-only DTO."""

import hashlib
import json
import os
import sqlite3
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


def structural_v3_history(path, science_bundle):
    """One hundred direct structural fixtures, never 100 permitted engine STARTs.

    SCI versions/roles come from the real attested bundle. Evaluation-request
    fingerprints are explicitly synthetic; no current engine evaluation is claimed.
    """
    from test_muscle_observed_load_sqlite import seed

    from app.services.muscle_observed_load.provenance import (
        V3_AUTHORITY_FIELDS,
        SourceView,
        digest,
    )

    seed(path, 100)
    effective = SourceView.bundle(*science_bundle).v3
    identity = "tirage-poulie-haute-prise-neutre"
    candidate = effective["candidates"][identity]
    context = dict(
        context_ref="synthetic:room",
        equipment_ref="synthetic:machine",
        realization_ref=candidate["realization_ref"],
        side="BILATERAL",
        load_semantics="MACHINE_DISPLAY_KG",
    )
    slot = dict(
        slot_id="synthetic-slot",
        intent_id=candidate["intent_id"],
        selected={"canonical_exercise_id": identity},
        prescription={"context": context, "dose": {"work_sets": 1}},
    )
    authority = {key: "synthetic-request:" + key for key in V3_AUTHORITY_FIELDS}
    for key in [
        "binding_ref",
        "binding_digest",
        "bundle_digest",
        "effective_science_digest",
        "engine_version",
        "policy_version",
    ]:
        authority[key] = effective[key]
    scientific_session = {"slots": [slot]}
    evaluated = dict(
        authority,
        authority_generation=1,
        candidate_plan={"sessions": [scientific_session], "allocation_ref": "synthetic-allocation"},
    )
    with sqlite3.connect(path) as db:
        db.executescript(
            "CREATE TABLE first_plan_execution_bindings(session_id INTEGER PRIMARY KEY,"
            "owner_id INTEGER,execution_profile_version TEXT,scientific_session_id TEXT,"
            "evaluation_id TEXT,binding_digest TEXT,immutable_payload_json TEXT);"
            "CREATE TABLE first_plan_evaluations(id TEXT PRIMARY KEY,owner_id INTEGER,"
            "authority_generation INTEGER,result_json TEXT);"
            "CREATE TABLE first_plan_runtime_authorities(profile_key TEXT PRIMARY KEY,"
            "generation INTEGER,state TEXT,publication_json TEXT,packaging_digest TEXT,"
            "approval_ref TEXT);"
        )
        db.execute("DELETE FROM first_plan_set_observations")
        db.execute(
            "UPDATE workout_sessions SET template_slug_snapshot=? WHERE user_id=1",
            ("science:v3:first-session",),
        )
        db.execute("UPDATE set_logs SET completed_at='2026-11-02 00:00:00' WHERE id<9999")
        db.execute(
            "UPDATE session_exercises SET exercise_name_snapshot=? WHERE id<9999",
            ("Synthetic historical V3 fixture",),
        )
        db.execute(
            "INSERT INTO first_plan_evaluations VALUES('shared-evaluation',1,1,?)",
            (json.dumps(evaluated),),
        )
        publication = {
            key: effective[key]
            for key in [
                "registry_digest",
                "binding_digest",
                "bundle_digest",
                "effective_science_digest",
            ]
        }
        db.execute(
            "INSERT INTO first_plan_runtime_authorities VALUES(?,1,'ACTIVE',?,?,?)",
            (
                "first-session-runtime/3.0.0",
                json.dumps(publication),
                science_bundle[1],
                "SYNTHETIC_STRUCTURAL_FIXTURE_ONLY",
            ),
        )
        for i in range(1, 101):
            payload = dict(
                authority=authority,
                authority_generation=1,
                allocation_ref="synthetic-allocation",
                scientific_session=scientific_session,
                mapping=[
                    dict(
                        se_id=i,
                        canonical_exercise_id=identity,
                        slot_id=slot["slot_id"],
                        intent_id=candidate["intent_id"],
                        set_ids=[i],
                    )
                ],
            )
            db.execute(
                "INSERT INTO first_plan_execution_bindings VALUES(?,1,?,?,?,?,?)",
                (
                    i,
                    "first-plan-execution/3.0.0",
                    "synthetic-session",
                    "shared-evaluation",
                    digest(payload),
                    json.dumps(payload),
                ),
            )
            observation = dict(
                context=context,
                setting={"kind": "MASS_KG", "value": 35, "unit": "kg"},
                reps=9,
                completed=True,
                performed_at="2026-11-02T00:00:00Z",
                performed_at_estimated=True,
            )
            op = f"synthetic-structural-{i}"
            receipt = dict(
                state="APPLIED",
                session_id=i,
                set_id=i,
                op_id=op,
                applied_revision=1,
                performed_at=observation["performed_at"],
                performed_at_adjusted=False,
            )
            body = dict(session_id=i, set_id=i, expected_revision=0, observation=observation)
            db.execute(
                "INSERT INTO first_plan_set_observations VALUES(?,1,?,?,?,1,0,?,?,?,?,?)",
                (
                    op,
                    i,
                    i,
                    i,
                    op,
                    digest(body),
                    json.dumps(observation),
                    json.dumps(receipt),
                    "2026-11-02 00:01:00",
                ),
            )
        assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    # Finish the fixture's writer before a byte-for-byte read-only witness;
    # a delayed WAL checkpoint is not a reader mutation.
    db.close()


def read_structural_v3(path, science_bundle):
    from pathlib import Path

    from app.services.muscle_observed_load.contracts import ObservedLoadQuery
    from app.services.muscle_observed_load.limits import ReadLimits
    from app.services.muscle_observed_load.projection import SourceView, project_capture
    from app.services.muscle_observed_load.provenance import CatalogueReadContext
    from app.services.muscle_observed_load.sqlite_source import open_owned_capture

    admitted = SourceView.local()
    context = CatalogueReadContext(1, "0" * 64)
    context.seed(admitted)
    source = SourceView(
        Path(__file__).resolve().parents[1], budget=admitted.budget, catalogue_context=context
    )
    source.raw, source.pins = dict(admitted.raw), dict(admitted.pins)
    source.bundle_root = str(science_bundle[0])
    until = datetime(2026, 11, 25, tzinfo=UTC)
    query = ObservedLoadQuery(datetime(2026, 11, 1, tzinfo=UTC), until)
    with open_owned_capture("sqlite:///" + str(path), 1, query) as capture:
        out = project_capture(
            capture, query, source, ReadLimits(), as_of=until, runtime_profile_digest="0" * 64
        ).model_dump()
        return out, dict(capture.budget.used)


def test_structural_100_v3_facts_fit_existing_sql_budget_without_authority_shortcut(
    tmp_path, science_bundle
):
    path = tmp_path / "structural-v3.sqlite"
    structural_v3_history(path, science_bundle)
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    out, used = read_structural_v3(path, science_bundle)
    assert len(out["facts"]) == 100
    assert all(f["provenance"]["profile"] == "V3" for f in out["facts"])
    assert all(f["provenance"]["source_status"] == "QUALIFIED" for f in out["facts"])
    assert all(f["temporal"]["performed_at_estimated"] for f in out["facts"])
    assert all(f["weight_kg"] is None for f in out["facts"])
    assert used["statements"] < 4096
    verify_digest(out)
    assert hashlib.sha256(path.read_bytes()).hexdigest() == before
    # A subsequent capture must reject a changed authority, not reuse the old verdict.
    with sqlite3.connect(path) as writer:
        writer.execute("UPDATE first_plan_runtime_authorities SET generation=2")
    changed, _ = read_structural_v3(path, science_bundle)
    assert len(changed["facts"]) == 100
    assert all(f["provenance"]["source_status"] != "QUALIFIED" for f in changed["facts"])
    assert changed["state"] == "UNKNOWN"
    verify_digest(changed)
