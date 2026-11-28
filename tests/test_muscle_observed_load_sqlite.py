"""Real disposable SQLite: bounded candidates and a single read snapshot."""

import importlib
import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest

DDL = """
CREATE TABLE workout_sessions(id INTEGER PRIMARY KEY,user_id INTEGER,status TEXT,excluded_from_stats INTEGER,started_at TEXT,template_slug_snapshot TEXT);
CREATE INDEX ix_workout_sessions_user_id ON workout_sessions(user_id);
CREATE TABLE session_exercises(id INTEGER PRIMARY KEY,session_id INTEGER,exercise_name_snapshot TEXT,substituted_name TEXT,position INTEGER,template_exercise_id INTEGER);
CREATE INDEX ix_session_exercises_session_id ON session_exercises(session_id);
CREATE TABLE set_logs(id INTEGER PRIMARY KEY,session_exercise_id INTEGER,kind TEXT,completed INTEGER,completed_at TEXT,reps INTEGER,weight_kg REAL,set_index INTEGER);
CREATE INDEX ix_set_logs_exercise_kind_completed ON set_logs(session_exercise_id,kind,completed);
CREATE TABLE first_plan_set_observations(id TEXT PRIMARY KEY,owner_id INTEGER,session_id INTEGER,session_exercise_id INTEGER,set_id INTEGER,applied_revision INTEGER,expected_revision INTEGER,op_id TEXT,body_digest TEXT,observation_json TEXT,receipt_json TEXT,recorded_at TEXT);
CREATE UNIQUE INDEX uq_first_plan_set_revision ON first_plan_set_observations(set_id,applied_revision);
"""


def seed(path: Path, sessions=1):
    with sqlite3.connect(path) as db:
        db.execute("PRAGMA journal_mode=WAL")
        db.executescript(DDL)
        for i in range(1, sessions + 1):
            db.execute(
                "INSERT INTO workout_sessions VALUES (?,?,?,0,?,?)",
                (i, 1, "completed", "2026-10-01 00:00:00", "legacy"),
            )
            db.execute("INSERT INTO session_exercises VALUES (?,?,?,NULL,0,NULL)", (i, i, "Pompes"))
            db.execute(
                "INSERT INTO set_logs VALUES (?,?,?,1,?,9,NULL,1)",
                (i, i, "work", "2026-11-02 00:00:00" if i == sessions else "2026-10-02 00:00:00"),
            )
        db.execute(
            "INSERT INTO workout_sessions VALUES (9999,2,?,0,?,?)",
            ("completed", "2026-11-01 00:00:00", "legacy"),
        )
        db.execute("INSERT INTO session_exercises VALUES (9999,9999,?,NULL,0,NULL)", ("Foreign",))
        db.execute(
            "INSERT INTO set_logs VALUES (9999,9999,?,1,?,8,NULL,1)",
            ("work", "2026-11-02 00:00:00"),
        )
        db.execute(
            "INSERT INTO first_plan_set_observations VALUES ('op',1,1,1,1,1,0,'op','digest','{}','{}','2026-11-02 00:01:00')"
        )
    db.close()
    return path


def capture(path, owner=1, **kwargs):
    try:
        m = importlib.import_module("app.services.muscle_observed_load.sqlite_source")
    except ModuleNotFoundError:
        pytest.fail("BUILD01 SQLite read capture is not implemented")
    from app.services.muscle_observed_load.contracts import ObservedLoadQuery
    from app.services.muscle_observed_load.limits import ReadLimits

    return m.open_owned_capture(
        "sqlite:///" + str(path),
        owner,
        ObservedLoadQuery(datetime(2026, 11, 1, tzinfo=UTC), datetime(2026, 11, 25, tzinfo=UTC)),
        kwargs.get("limits", ReadLimits()),
    )


def test_old_id_prefix_marks_truncation_and_owner_isolation(tmp_path):
    path = seed(tmp_path / "db.sqlite", 201)
    with capture(path) as c:
        rows = list(c.candidates())
        assert len(rows) == 200
        assert all(r["session_id"] != 9999 for r in rows)
        assert all(r["completed_at"] == "2026-10-02 00:00:00" for r in rows)
        assert c.truncated
        assert c.budget.used["sessions"] == 200


def test_actual_snapshot_stays_coherent_across_concurrent_correction(tmp_path):
    path = seed(tmp_path / "db.sqlite")
    with capture(path) as c:
        before = list(c.candidates())[0]
        with sqlite3.connect(path) as writer:
            writer.execute("UPDATE set_logs SET reps=12 WHERE id=1")
            writer.execute(
                "UPDATE first_plan_set_observations SET receipt_json=? WHERE id=?",
                ('{"reps":12}', "op"),
            )
        assert before["reps"] == 9
        assert c.operation_rows(1)[0]["receipt"] == {}
    with capture(path) as c:
        assert list(c.candidates())[0]["reps"] == 12
        assert c.operation_rows(1)[0]["receipt"] == {"reps": 12}


def test_oversize_and_foreign_text_not_materialized(tmp_path):
    path = seed(tmp_path / "db.sqlite")
    with sqlite3.connect(path) as writer:
        writer.execute("UPDATE first_plan_set_observations SET receipt_json=?", ("x" * 2_097_152,))
    with capture(path) as c:
        result = c.operation_rows(1)[0]
        assert result["receipt"] is None and "TEXT_LIMIT" in result["reasons"]
        assert c.budget.used.get("db_input_bytes", 0) < 8192
        assert c.operation_rows(9999) == []


def test_reader_refuses_dml_and_invalid_json_without_repair(tmp_path):
    path = seed(tmp_path / "db.sqlite")
    with capture(path) as c:
        with pytest.raises(sqlite3.DatabaseError):
            c.connection.execute("UPDATE set_logs SET reps=0")
        assert list(c.candidates())[0]["reps"] == 9
    with sqlite3.connect(path) as writer:
        writer.execute("UPDATE first_plan_set_observations SET receipt_json=?", ('{"x":1,"x":2}',))
    with capture(path) as c:
        row = c.operation_rows(1)[0]
        assert row["receipt"] is None and "JSON_LIMIT" in row["reasons"]


def test_non_work_and_incomplete_rows_are_not_candidates(tmp_path):
    path = seed(tmp_path / "db.sqlite")
    with sqlite3.connect(path) as writer:
        writer.execute("INSERT INTO set_logs VALUES(2,1,'warmup',1,NULL,5,NULL,2)")
        writer.execute("INSERT INTO set_logs VALUES(3,1,'work',0,NULL,5,NULL,3)")
    with capture(path) as c:
        assert [x["set_log_id"] for x in c.candidates()] == [1]


def test_global_caps_and_vm_deadline_abort_without_writes(tmp_path):
    from app.services.muscle_observed_load.contracts import ObservedLoadReadError
    from app.services.muscle_observed_load.limits import ReadLimits

    path = seed(tmp_path / "db.sqlite", 3)
    with capture(path, limits=ReadLimits(exercises=1)) as c:
        assert len(list(c.candidates())) == 1
        assert c.truncated
    with capture(path, limits=ReadLimits(vm_steps=1000)) as c:
        with pytest.raises(ObservedLoadReadError):
            c.rows(
                "WITH RECURSIVE n(x) AS (VALUES(1) UNION ALL SELECT x+1 FROM n WHERE x<100000) SELECT sum(x) FROM n"
            ).fetchall()


@pytest.mark.parametrize(
    "raw",
    [
        b"[" * 17 + b"0" + b"]" * 17,
        b'{"k":"' + b"x" * 4097 + b'"}',
        b'{"k":NaN}',
        b'{"k":1e999}',
        b'{"k":"\\ud800"}',
        b'{"x":1,"x":2}',
        b"\xff",
    ],
)
def test_json_resource_admission_is_fail_closed(raw):
    from app.services.muscle_observed_load.limits import ReadLimits
    from app.services.muscle_observed_load.sqlite_source import bounded_json

    with pytest.raises((ValueError, UnicodeError)):
        bounded_json(raw, ReadLimits())


def test_unbounded_alias_and_binding_access_are_not_exposed(tmp_path):
    path = seed(tmp_path / "db.sqlite")
    with capture(path) as c:
        # These adapters must remain in this capture and cannot expose another owner.
        assert c.binding_for(9999) is None
        assert c.alias_name("unmapped") is None


def test_setup_statements_are_in_global_budget(tmp_path):
    path = seed(tmp_path / "db")
    with capture(path) as c:
        assert c.budget.used["statements"] >= 2


def seed_authority_reads(path):
    seed(path)
    with sqlite3.connect(path) as db:
        db.executescript(
            "CREATE TABLE first_plan_evaluations(id TEXT PRIMARY KEY,owner_id INTEGER,"
            "authority_generation INTEGER,result_json TEXT);"
            "CREATE TABLE first_plan_runtime_authorities(profile_key TEXT PRIMARY KEY,"
            "generation INTEGER,state TEXT,publication_json TEXT,packaging_digest TEXT,"
            "approval_ref TEXT);"
            "CREATE TABLE first_plan_execution_bindings(session_id INTEGER PRIMARY KEY);"
        )
        for name, owner in [("shared", 1), ("foreign", 2), ("second", 1), ("third", 1)]:
            db.execute(
                "INSERT INTO first_plan_evaluations VALUES(?,?,1,?)",
                (name, owner, json.dumps({"nested": {"owner": owner, "version": 1}})),
            )
        db.execute(
            "INSERT INTO first_plan_runtime_authorities VALUES(?,1,'ACTIVE',?,?,?)",
            ("first-session-runtime/3.0.0", '{"nested":{"version":1}}', "pin", "test-only"),
        )
    db.close()
    return path


def test_repeated_snapshot_authority_reads_preserve_budget_and_independent_values(tmp_path):
    path = seed_authority_reads(tmp_path / "authority.sqlite")
    with capture(path) as c:
        assert c.has_table("first_plan_execution_bindings")
        evaluation = c.evaluation_for("shared")
        authority = c.runtime_authority()
        used = dict(c.budget.used)
        evaluation["result"]["nested"]["version"] = 99
        evaluation["reasons"].append("CALLER_MUTATION")
        authority["publication"]["nested"]["version"] = 99
        authority["reasons"].append("CALLER_MUTATION")
        # A cache hit must also be independent, not just the first returned row.
        hit = c.evaluation_for("shared")
        hit["result"]["nested"]["version"] = 88
        hit["reasons"].append("CACHE_HIT_MUTATION")
        hit = c.runtime_authority()
        hit["publication"]["nested"]["version"] = 88
        hit["reasons"].append("CACHE_HIT_MUTATION")
        for _ in range(10):
            assert c.has_table("first_plan_execution_bindings")
            assert c.evaluation_for("shared") == {
                "authority_generation": 1,
                "reasons": [],
                "id": "shared",
                "result": {"nested": {"owner": 1, "version": 1}},
            }
            assert c.runtime_authority() == {
                "generation": 1,
                "state": "ACTIVE",
                "publication": {"nested": {"version": 1}},
                "packaging_digest": "pin",
                "approval_ref": "test-only",
                "reasons": [],
            }
        assert c.budget.used == used


def test_authority_cache_is_confined_to_owner_and_transaction_snapshot(tmp_path):
    path = seed_authority_reads(tmp_path / "snapshots.sqlite")
    with capture(path) as first:
        assert first.evaluation_for("shared")["result"]["nested"]["version"] == 1
        assert first.runtime_authority()["generation"] == 1
        assert first.evaluation_for("foreign") is None
        with sqlite3.connect(path) as writer:
            writer.execute(
                "UPDATE first_plan_evaluations SET result_json=? WHERE id='shared'",
                ('{"nested":{"owner":1,"version":2}}',),
            )
            writer.execute("UPDATE first_plan_runtime_authorities SET generation=2")
        assert first.evaluation_for("shared")["result"]["nested"]["version"] == 1
        assert first.runtime_authority()["generation"] == 1
    with capture(path) as next_snapshot:
        assert next_snapshot.evaluation_for("shared")["result"]["nested"]["version"] == 2
        assert next_snapshot.runtime_authority()["generation"] == 2
    with capture(path, owner=2) as foreign:
        assert foreign.evaluation_for("shared") is None
        assert foreign.evaluation_for("foreign")["result"]["nested"]["owner"] == 2


def test_absent_authority_reads_stay_absent_in_same_snapshot(tmp_path):
    path = seed_authority_reads(tmp_path / "missing.sqlite")
    with sqlite3.connect(path) as writer:
        writer.execute("DELETE FROM first_plan_runtime_authorities")
    with capture(path) as c:
        assert c.evaluation_for("later") is None
        assert c.runtime_authority() is None
        assert c.has_table("exercise_aliases") is False
        used = dict(c.budget.used)
        with sqlite3.connect(path) as writer:
            writer.execute("INSERT INTO first_plan_evaluations VALUES('later',1,1,'{}')")
            writer.execute(
                "INSERT INTO first_plan_runtime_authorities VALUES(?,1,'ACTIVE','{}','p','a')",
                ("first-session-runtime/3.0.0",),
            )
            writer.execute("CREATE TABLE exercise_aliases(normalized TEXT,exercise_id INTEGER)")
        assert c.evaluation_for("later") is None
        assert c.runtime_authority() is None
        assert c.has_table("exercise_aliases") is False
        assert c.budget.used == used
    with capture(path) as c:
        assert c.evaluation_for("later")["result"] == {}
        assert c.runtime_authority()["generation"] == 1
        assert c.has_table("exercise_aliases")


def test_authority_reuse_is_bounded_without_skipping_real_read_limits(tmp_path):
    from app.services.muscle_observed_load.contracts import ObservedLoadReadError
    from app.services.muscle_observed_load.limits import ReadLimits

    path = seed_authority_reads(tmp_path / "bounded.sqlite")
    with capture(path, limits=ReadLimits(sessions=2)) as c:
        for identity in ["shared", "second", "third"]:
            assert c.evaluation_for(identity)["id"] == identity
        used = c.budget.used["statements"]
        assert c.evaluation_for("shared")["id"] == "shared"
        assert c.evaluation_for("second")["id"] == "second"
        assert c.budget.used["statements"] == used
        assert c.evaluation_for("third")["id"] == "third"
        assert c.budget.used["statements"] > used
    with pytest.raises(ObservedLoadReadError):
        with capture(path, limits=ReadLimits(statements=12)) as c:
            for identity in ["shared", "second", "third"]:
                c.evaluation_for(identity)


@pytest.mark.parametrize("fail_in_capture", [False, True])
def test_closed_capture_cannot_serve_cached_authority(tmp_path, fail_in_capture):
    from app.services.muscle_observed_load.contracts import ObservedLoadReadError

    path = seed_authority_reads(tmp_path / "closed.sqlite")
    try:
        with capture(path) as c:
            assert c.evaluation_for("shared") and c.runtime_authority()
            assert c.has_table("first_plan_execution_bindings")
            if fail_in_capture:
                raise RuntimeError("synthetic abort")
    except RuntimeError:
        assert fail_in_capture
    for read in [
        lambda: c.evaluation_for("shared"),
        c.runtime_authority,
        lambda: c.has_table("first_plan_execution_bindings"),
    ]:
        with pytest.raises(ObservedLoadReadError):
            read()


@pytest.mark.parametrize("kind", ["table", "evaluation", "runtime"])
def test_cached_reads_do_not_bypass_capture_deadline(tmp_path, kind):
    from app.services.muscle_observed_load.contracts import ObservedLoadReadError

    path = seed_authority_reads(tmp_path / "expired.sqlite")
    with pytest.raises(ObservedLoadReadError):
        with capture(path) as c:
            read = {
                "table": lambda: c.has_table("first_plan_execution_bindings"),
                "evaluation": lambda: c.evaluation_for("shared"),
                "runtime": c.runtime_authority,
            }[kind]
            assert read()
            # Synthetic expiry of this read budget, without touching TIME-01 clocks.
            c.budget.started -= 2
            read()
