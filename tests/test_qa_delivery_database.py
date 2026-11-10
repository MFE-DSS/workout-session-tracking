"""Complete SQLite copies preserve identity, refresh and PLAN without source writes."""

from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from contextlib import closing
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def qa_database(tmp_path):
    path = tmp_path / "synthetic.db"
    with closing(sqlite3.connect(path)) as db, db:
        statements = (ROOT / "data/schema_snapshot.sql").read_text().splitlines()
        db.executescript(
            "\n".join(
                sorted(
                    (s for s in statements if s.startswith("CREATE ")),
                    key=lambda s: not s.startswith("CREATE TABLE"),
                )
            )
        )
        db.execute("CREATE TABLE alembic_version (version_num VARCHAR(32) PRIMARY KEY)")
        db.execute("INSERT INTO alembic_version VALUES ('plan_v3_20261107_01')")
        db.execute(
            "INSERT INTO users (id,username,password_hash,is_active) VALUES (42,'qa02-assigned','private-hash',1)"
        )
        db.execute(
            "INSERT INTO device_sessions (id,user_id,refresh_hash,session_epoch,last_used_at) VALUES ('device-preserved',42,'private-refresh',0,CURRENT_TIMESTAMP)"
        )
        db.execute(
            "INSERT INTO blueprint_source_events (id,owner_id,source_revision,request_id,body_digest,kind,payload_json) VALUES ('subject-preserved',42,1,'command-preserved','digest','CONTEXT_OPENED','{}')"
        )
        db.execute(
            "INSERT INTO owned_blueprint_snapshots (id,owner_id,request_id,body_digest,source_revision,as_of,snapshot_json,snapshot_digest) VALUES ('snapshot',42,'capture','digest',1,CURRENT_TIMESTAMP,'{}','digest')"
        )
        db.execute(
            "INSERT INTO first_plan_evaluations (id,owner_id,snapshot_id,operation_kind,request_id,body_digest,source_revision,authority_generation,request_json,result_json) VALUES ('evaluation',42,'snapshot','EVALUATE','evaluate','digest',1,3,'{}','{}')"
        )
        db.execute(
            "INSERT INTO workout_sessions (id,user_id,template_slug_snapshot,template_name_snapshot,started_at,status,excluded_from_stats) VALUES (7,42,'synthetic','Synthetic',CURRENT_TIMESTAMP,'in_progress',0)"
        )
        db.execute(
            "INSERT INTO session_exercises (id,session_id,exercise_code_snapshot,exercise_name_snapshot,position) VALUES (8,7,'synthetic','Synthetic',0)"
        )
        db.execute(
            "INSERT INTO set_logs (id,session_exercise_id,kind,set_index,completed) VALUES (9,8,'work',0,1)"
        )
        db.execute(
            "INSERT INTO first_session_requests (id,owner_id,request_id,body_digest,body_json,evaluation_id,state,session_id,scientific_session_id) VALUES ('start',42,'idempotent-start','digest','{}','evaluation','CREATED',7,'scientific-session')"
        )
        db.execute(
            "INSERT INTO first_plan_execution_bindings (session_id,owner_id,evaluation_id,execution_profile_version,scientific_session_id,immutable_payload_json,binding_digest) VALUES (7,42,'evaluation','first-session-runtime/3.0.0','scientific-session','{}','digest')"
        )
        observation = json.dumps(
            {
                "subject_ref": "subject-preserved",
                "context": {"load_semantics": "PER_IMPLEMENT"},
                "setting": {"kind": "MASS_KG", "value": 17, "unit": "kg"},
                "reps": 9,
            }
        )
        db.execute(
            "INSERT INTO first_plan_set_observations (id,owner_id,session_id,session_exercise_id,set_id,op_id,body_digest,expected_revision,applied_revision,observation_json,receipt_json) VALUES ('fact',42,7,8,9,'op-preserved','digest',0,1,?,'{}')",
            (observation,),
        )
        db.execute(
            "INSERT INTO first_plan_runtime_authorities (profile_key,generation,state) VALUES ('first-session-runtime/3.0.0',3,'WITHDRAWN')"
        )
    return path


def rows(path):
    with closing(sqlite3.connect(path)) as db:
        names = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        return {
            name: db.execute('SELECT * FROM "' + name.replace('"', '""') + '"').fetchall()
            for name in names
        }


def test_backup_restore_copies_all_tables_ids_and_refresh_without_source_mutation(
    qa_database, tmp_path
):
    from tools.qa_delivery.database import backup_database, verify_database

    original = qa_database.read_bytes()
    snapshot, restored = tmp_path / "backup.db", tmp_path / "restored.db"
    receipt = backup_database(qa_database, snapshot)
    backup_database(snapshot, restored)
    assert rows(qa_database) == rows(snapshot) == rows(restored)
    assert qa_database.read_bytes() == original
    assert receipt["server_schema"] == "plan_v3_20261107_01"
    assert receipt["tables"]["users"]["rows"] == 1
    assert receipt["tables"]["device_sessions"]["rows"] == 1
    assert receipt["tables"]["blueprint_source_events"]["rows"] == 1
    for table in (
        "owned_blueprint_snapshots",
        "first_plan_evaluations",
        "first_session_requests",
        "first_plan_execution_bindings",
        "first_plan_set_observations",
    ):
        assert receipt["tables"][table]["rows"] == 1
    assert receipt["continuity_digest"] == verify_database(restored)["continuity_digest"]
    assert "private-" not in json.dumps(receipt) and str(tmp_path) not in json.dumps(receipt)
    assert snapshot.stat().st_mode & 0o777 == 0o600


@pytest.mark.parametrize("damage", ["unknown_head", "fk", "corrupt", "missing", "schema"])
def test_invalid_database_refused_before_copy(qa_database, tmp_path, damage):
    from tools.qa_delivery.database import backup_database

    if damage == "corrupt":
        qa_database.write_bytes(b"private-corruption")
    elif damage == "missing":
        qa_database.unlink()
    else:
        with sqlite3.connect(qa_database) as db:
            db.execute(
                {
                    "unknown_head": "UPDATE alembic_version SET version_num='future'",
                    "fk": "UPDATE device_sessions SET user_id=999",
                    "schema": "DROP TABLE first_plan_set_observations",
                }[damage]
            )
    target = tmp_path / "new.db"
    with pytest.raises(ValueError, match="qa_database_invalid"):
        backup_database(qa_database, target)
    assert not target.exists()


def test_existing_destination_and_interrupted_backup_never_overwrite_or_leave_partial(
    qa_database, tmp_path, monkeypatch
):
    import tools.qa_delivery.database as module

    target = tmp_path / "preserved.db"
    target.write_bytes(b"existing-private")
    with pytest.raises(ValueError, match="qa_destination_exists"):
        module.backup_database(qa_database, target)
    assert target.read_bytes() == b"existing-private"
    target.unlink()

    def interrupted(*args, **kwargs):
        raise KeyboardInterrupt

    monkeypatch.setattr(module, "_copy_pages", interrupted)
    with pytest.raises(KeyboardInterrupt):
        module.backup_database(qa_database, target)
    assert not target.exists()
    assert sorted(p.name for p in tmp_path.iterdir()) == ["synthetic.db"]


def test_database_cli_restore_new_copy_has_redacted_manifest(qa_database, tmp_path):
    from tools.qa_delivery.database import backup_database

    snapshot = tmp_path / "snapshot.db"
    backup_database(qa_database, snapshot)
    target = tmp_path / "restored.db"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.qa_delivery.database",
            "restore",
            str(snapshot),
            str(target),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0, result.stderr
    assert rows(target) == rows(qa_database)
    assert "private-" not in result.stdout and str(tmp_path) not in result.stdout
    assert json.loads(result.stdout)["server_schema"] == "plan_v3_20261107_01"


def test_source_refresh_rotation_during_capture_refuses_publication(
    qa_database, tmp_path, monkeypatch
):
    import tools.qa_delivery.database as module

    copy = module._copy_pages

    def rotate(src, dst):
        copy(src, dst)
        with sqlite3.connect(qa_database) as db:
            db.execute("UPDATE device_sessions SET refresh_hash='private-new-refresh'")

    monkeypatch.setattr(module, "_copy_pages", rotate)
    target = tmp_path / "must-not-publish.db"
    with pytest.raises(ValueError, match="qa_source_changed_during_capture"):
        module.backup_database(qa_database, target)
    assert not target.exists()
    assert not target.with_name(target.name + ".manifest.json").exists()


def test_destination_publication_race_preserves_other_writer(qa_database, tmp_path, monkeypatch):
    import tools.qa_delivery.database as module

    original = module.os.link
    target = tmp_path / "raced.db"

    def race(src, dst):
        if dst == target:
            target.write_bytes(b"other-writer")
        original(src, dst)

    monkeypatch.setattr(module.os, "link", race)
    with pytest.raises(FileExistsError):
        module.backup_database(qa_database, target)
    assert target.read_bytes() == b"other-writer"
    assert not target.with_name(target.name + ".manifest.json").exists()


def test_online_wal_snapshot_contains_committed_frames_and_stays_independent(qa_database, tmp_path):
    from tools.qa_delivery.database import backup_database

    target = tmp_path / "wal-backup.db"
    with sqlite3.connect(qa_database) as writer:
        writer.execute("PRAGMA journal_mode=WAL")
        writer.execute("UPDATE device_sessions SET refresh_hash='private-wal-refresh'")
        writer.commit()
        backup_database(qa_database, target)
        assert rows(target) == rows(qa_database)
    for suffix in ("-wal", "-shm"):
        assert not Path(str(target) + suffix).exists()
    assert not list(tmp_path.glob(".qa-*"))


def test_restore_cli_refuses_logically_modified_backup_despite_valid_sqlite(qa_database, tmp_path):
    from tools.qa_delivery.database import backup_database

    snapshot = tmp_path / "tampered-backup.db"
    target = tmp_path / "must-stay-absent.db"
    backup_database(qa_database, snapshot)
    with sqlite3.connect(snapshot) as db:
        db.execute("UPDATE device_sessions SET refresh_hash='private-tampered-refresh'")
    result = subprocess.run(
        [sys.executable, "-m", "tools.qa_delivery.database", "restore", str(snapshot), str(target)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode != 0
    assert not target.exists()
    assert "private-" not in result.stderr


@pytest.mark.parametrize("mutation", ["refresh", "plan", "header"])
def test_restore_interphase_source_write_cannot_replace_validated_manifest_identity(
    qa_database, tmp_path, monkeypatch, capsys, mutation
):
    import tools.qa_delivery.database as module

    snapshot = tmp_path / "validated-backup.db"
    target = tmp_path / "must-not-publish.db"
    module.backup_database(qa_database, snapshot)
    original_source = qa_database.read_bytes()
    verify = module._verify_backup
    changed = {}

    def verify_then_write(path):
        validated = verify(path)
        with sqlite3.connect(path) as writer:
            writer.execute(
                {
                    "refresh": "UPDATE device_sessions SET refresh_hash='private-interphase-refresh'",
                    "plan": "UPDATE first_plan_set_observations SET observation_json='{}'",
                    "header": "PRAGMA user_version=17",
                }[mutation]
            )
        changed["bytes"] = path.read_bytes()
        changed["rows"] = rows(path)
        return validated

    monkeypatch.setattr(module, "_verify_backup", verify_then_write)
    monkeypatch.setattr(sys, "argv", ["qa-database", "restore", str(snapshot), str(target)])
    with pytest.raises(SystemExit) as refused:
        module.main()
    assert refused.value.code == 1
    assert not target.exists()
    assert not target.with_name(target.name + ".manifest.json").exists()
    assert not list(tmp_path.glob(".qa-*"))
    assert snapshot.read_bytes() == changed["bytes"]
    assert rows(snapshot) == changed["rows"]
    assert qa_database.read_bytes() == original_source
    output = capsys.readouterr()
    assert output.out == "" and "private-" not in output.err
