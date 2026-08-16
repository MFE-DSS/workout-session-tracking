"""Tests for the restore service and the restore CLI script.

The core proof: export → wipe → restore → validate that the data
is exploitable (not just inserted but actually readable and
structurally coherent).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Pure service tests (restore_from_json_payload)
# ---------------------------------------------------------------------------


def _minimal_payload(*, count: int = 1, sessions: list | None = None) -> dict:
    """Build a minimal valid schema_version=1 payload."""
    if sessions is None:
        sessions = [
            {
                "id": i + 1,
                "status": "completed",
                "started_at": f"2026-04-0{i + 1}T18:30:00+00:00",
                "ended_at": f"2026-04-0{i + 1}T19:30:00+00:00",
                "template_slug": "push-a",
                "template_name": "Push A",
                "concentration": "high",
                "global_state": "good",
                "bodyweight_kg": 78.5,
                "free_note": None,
                "exercises": [
                    {
                        "position": 1,
                        "code": "E1",
                        "name": "Butterfly pec",
                        "success_score": 80,
                        "muscle_sensation": "strong",
                        "free_note": None,
                        "sets": [
                            {
                                "kind": "warmup",
                                "set_index": 1,
                                "weight_kg": 20.0,
                                "reps": 12,
                                "technique": None,
                                "execution_quality": None,
                                "reps_target": None,
                                "completed": True,
                            },
                            {
                                "kind": "work",
                                "set_index": 1,
                                "weight_kg": 40.0,
                                "reps": 12,
                                "technique": None,
                                "execution_quality": "clean",
                                "reps_target": "target_hit",
                                "completed": True,
                            },
                        ],
                    }
                ],
            }
            for i in range(count)
        ]
    from app.services.export_builder import SCHEMA_VERSION
    return {
        "schema_version": SCHEMA_VERSION,
        "exported_at": "2026-04-08T03:30:00+00:00",
        "count": count,
        "sessions": sessions,
    }


def test_restore_succeeds_on_valid_payload(client):
    from app.database import SessionLocal
    from app.services.restore import restore_from_json_payload

    payload = _minimal_payload(count=2)
    with SessionLocal() as db:
        result = restore_from_json_payload(db, payload)
        assert result.ok is True, f"errors: {result.errors}"
        assert result.sessions_restored == 2
        assert result.exercises_restored == 2
        assert result.sets_restored == 4  # 2 sessions × 1 exercise × 2 sets
        db.commit()

        # Post-restore data access: prove it's exploitable
        from sqlalchemy import select

        from app.models.session import SessionExercise, SetLog, WorkoutSession

        sessions = db.execute(select(WorkoutSession)).scalars().all()
        assert len(sessions) == 2
        assert sessions[0].template_slug_snapshot == "push-a"
        assert sessions[0].concentration == "high"
        assert sessions[0].started_at is not None

        exercises = db.execute(select(SessionExercise)).scalars().all()
        assert len(exercises) == 2
        assert exercises[0].exercise_code_snapshot == "E1"
        assert exercises[0].success_score == 80

        sets = db.execute(select(SetLog)).scalars().all()
        assert len(sets) == 4
        work_sets = [s for s in sets if s.kind == "work"]
        assert all(s.completed is True for s in work_sets)
        assert work_sets[0].weight_kg == 40.0
        assert work_sets[0].execution_quality == "clean"


def test_restore_fails_on_non_empty_db(client):
    """If the DB already has sessions, restore must refuse."""
    from app.database import SessionLocal
    from app.services.restore import restore_from_json_payload

    payload = _minimal_payload(count=1)
    with SessionLocal() as db:
        # First restore: succeeds
        r1 = restore_from_json_payload(db, payload)
        assert r1.ok is True
        db.commit()

        # Second restore: must refuse
        r2 = restore_from_json_payload(db, payload)
        assert r2.ok is False
        assert any("not empty" in e for e in r2.errors)
        db.rollback()


def test_restore_fails_on_corrupt_json(client):
    from app.database import SessionLocal
    from app.services.restore import restore_from_json_payload

    with SessionLocal() as db:
        result = restore_from_json_payload(db, "not a dict")
        assert result.ok is False
        assert any("not a dict" in e for e in result.errors)


def test_restore_fails_on_wrong_schema_version(client):
    from app.database import SessionLocal
    from app.services.restore import restore_from_json_payload

    payload = _minimal_payload()
    payload["schema_version"] = 999
    with SessionLocal() as db:
        result = restore_from_json_payload(db, payload)
        assert result.ok is False
        assert any("schema_version is 999" in e for e in result.errors)


def test_restore_fails_on_count_mismatch(client):
    from app.database import SessionLocal
    from app.services.restore import restore_from_json_payload

    payload = _minimal_payload(count=1)
    payload["count"] = 5  # says 5 but only 1 session in the list
    with SessionLocal() as db:
        result = restore_from_json_payload(db, payload)
        assert result.ok is False
        assert any("!= count" in e for e in result.errors)


def test_restore_handles_empty_payload(client):
    from app.database import SessionLocal
    from app.services.restore import restore_from_json_payload

    payload = _minimal_payload(count=0, sessions=[])
    with SessionLocal() as db:
        result = restore_from_json_payload(db, payload)
        assert result.ok is True
        assert result.sessions_restored == 0
        db.commit()


# ---------------------------------------------------------------------------
# Round-trip: export → restore → compare
# ---------------------------------------------------------------------------


def test_export_then_restore_round_trip(client):
    """The ultimate proof: create sessions via the app, export them,
    wipe the DB, restore from the export, and verify that the
    restored data is identical to the original."""
    from sqlalchemy import delete, select

    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession
    from app.services.export_builder import build_json_payload
    from app.services.restore import restore_from_json_payload

    # 1. Create a session via the normal app flow
    r = client.post("/sessions", data={"template_slug": "push-a"}, follow_redirects=False)
    sid = int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))

    # Fill one exercise card
    with SessionLocal() as db:
        se = db.execute(
            select(SessionExercise)
            .where(SessionExercise.session_id == sid)
            .where(SessionExercise.exercise_code_snapshot == "E2")
        ).scalar_one()
        se_id = se.id
        work_ids = sorted(
            s.id for s in db.execute(
                select(SetLog).where(SetLog.session_exercise_id == se_id)
            ).scalars().all()
            if s.kind == "work"
        )

    data = {"muscle_sensation": "strong"}
    for i, wid in enumerate(work_ids, start=1):
        data[f"set_{wid}_weight_kg"] = str(60 + i)
        data[f"set_{wid}_reps"] = "10"
        data[f"set_{wid}_completed"] = "1"
    client.post(f"/sessions/{sid}/exercises/{se_id}", data=data, follow_redirects=False)
    client.post(f"/sessions/{sid}", data={"concentration": "high", "action": "end"}, follow_redirects=False)

    # 2. Export
    with SessionLocal() as db:
        payload = build_json_payload(db)
    assert payload["count"] == 1

    # 3. Wipe the DB
    with SessionLocal() as db:
        db.execute(delete(SetLog))
        db.execute(delete(SessionExercise))
        db.execute(delete(WorkoutSession))
        db.commit()
        assert db.execute(select(WorkoutSession)).scalars().all() == []

    # 4. Restore from the export
    with SessionLocal() as db:
        result = restore_from_json_payload(db, payload)
        assert result.ok is True, f"errors: {result.errors}"
        assert result.sessions_restored == 1
        db.commit()

    # 5. Verify the data is exploitable
    with SessionLocal() as db:
        sessions = db.execute(
            select(WorkoutSession)
        ).scalars().all()
        assert len(sessions) == 1
        s = sessions[0]
        assert s.template_slug_snapshot == "push-a"
        assert s.status == "completed"
        assert s.concentration == "high"

        exercises = db.execute(
            select(SessionExercise).where(SessionExercise.session_id == s.id)
        ).scalars().all()
        assert len(exercises) == 7  # Push A has 7 exercises (v10)

        e2 = next(e for e in exercises if e.exercise_code_snapshot == "E2")
        assert e2.success_score in {100, 80, 50}  # derived by compute_success_score
        assert e2.muscle_sensation == "strong"

        work = [
            sl for sl in db.execute(
                select(SetLog).where(SetLog.session_exercise_id == e2.id)
            ).scalars().all()
            if sl.kind == "work"
        ]
        assert len(work) == 3
        assert all(w.completed is True for w in work)
        assert work[0].weight_kg == 61.0
        assert work[0].execution_quality is None  # no longer sent via form


# ---------------------------------------------------------------------------
# CLI script (subprocess)
# ---------------------------------------------------------------------------


def _run_restore_script(env: dict[str, str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "scripts.restore_latest_backup"],
        cwd=str(REPO_ROOT),
        env={**os.environ, **env},
        capture_output=True,
        text=True,
    )


def test_restore_script_succeeds_on_valid_backup(client, tmp_path):
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    payload = _minimal_payload(count=1)
    (backup_dir / "sessions-20260408_0330.json").write_text(
        json.dumps(payload), encoding="utf-8"
    )

    result = _run_restore_script({
        "BACKUP_DIR": str(backup_dir),
        "DATABASE_URL": os.environ["DATABASE_URL"],
    })
    assert result.returncode == 0, result.stderr + result.stdout
    assert "restore: OK" in result.stdout
    assert "Push A" in result.stdout  # post-commit verify line


def test_restore_script_fails_on_missing_backup(client, tmp_path):
    result = _run_restore_script({
        "BACKUP_DIR": str(tmp_path / "empty"),
        "DATABASE_URL": os.environ["DATABASE_URL"],
    })
    assert result.returncode == 1
    assert "no JSON backup found" in result.stderr


def test_restore_script_fails_on_corrupt_json(client, tmp_path):
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    (backup_dir / "sessions-20260408_0330.json").write_text("{corrupt")

    result = _run_restore_script({
        "BACKUP_DIR": str(backup_dir),
        "DATABASE_URL": os.environ["DATABASE_URL"],
    })
    assert result.returncode == 1
    assert "cannot read JSON" in result.stderr
