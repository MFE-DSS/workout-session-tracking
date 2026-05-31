"""Sb_24.1 — verify the implicit signal + scoring version migration.

Hard contracts validated:
* workout_sessions.scoring_version exists, NOT NULL, default 1
* session_exercises.implicit_label exists, NULLABLE
* session_exercises.implicit_label_computed_at exists, NULLABLE
* New WorkoutSession rows receive scoring_version=1 by default
* SessionExercise rows can be created with implicit_label=None
* SessionExercise rows accept a string label up to 32 chars
"""
from __future__ import annotations


def _column_info(db, table: str) -> dict[str, dict]:
    """Return {column_name: {type, notnull, default}} via PRAGMA."""
    rows = db.execute(
        __import__("sqlalchemy").text(f"PRAGMA table_info({table})")
    ).fetchall()
    out: dict[str, dict] = {}
    for r in rows:
        # (cid, name, type, notnull, dflt_value, pk)
        out[r[1]] = {"type": r[2], "notnull": r[3], "default": r[4]}
    return out


def test_workout_sessions_has_scoring_version(client):
    """Spec §H — column exists with NOT NULL DEFAULT 1."""
    from app.database import SessionLocal
    with SessionLocal() as db:
        cols = _column_info(db, "workout_sessions")
    assert "scoring_version" in cols
    sv = cols["scoring_version"]
    assert "INT" in sv["type"].upper()
    assert sv["notnull"] == 1, "scoring_version must be NOT NULL"
    # SQLite stores DEFAULT as the literal text — "'1'" (with quotes)
    # for sa.text("1"). Strip quotes for robust assertion.
    default_value = str(sv["default"]).strip("'\"")
    assert default_value == "1", f"default should be 1, got {sv['default']!r}"


def test_session_exercises_has_implicit_label_columns(client):
    """Spec §D.2 — implicit_label + computed_at, both nullable."""
    from app.database import SessionLocal
    with SessionLocal() as db:
        cols = _column_info(db, "session_exercises")
    assert "implicit_label" in cols
    assert "implicit_label_computed_at" in cols
    assert cols["implicit_label"]["notnull"] == 0
    assert cols["implicit_label_computed_at"]["notnull"] == 0
    # VARCHAR(32) — SQLite stores as "VARCHAR(32)"
    assert "32" in cols["implicit_label"]["type"]


def test_new_session_defaults_to_scoring_version_1(client):
    """Spec §H — any new session created RIGHT NOW gets scoring_version=1
    because Sb_24.5 (formula switch) hasn't shipped yet. Once it does,
    new sessions will explicitly set scoring_version=2 in the handler."""
    from app.database import SessionLocal
    from app.models.user import User
    from app.models.session import WorkoutSession
    from datetime import datetime, timezone
    from sqlalchemy import select
    with SessionLocal() as db:
        uid = db.execute(
            select(User.id).where(User.username == "testuser")
        ).scalar_one()
        ws = WorkoutSession(
            user_id=uid,
            template_slug_snapshot="push-a",
            template_name_snapshot="Push A",
            started_at=datetime.now(timezone.utc),
            status="in_progress",
        )
        db.add(ws)
        db.commit()
        db.refresh(ws)
        assert ws.scoring_version == 1


def test_session_exercise_accepts_implicit_label_string(client):
    """The column can be written with a string label up to 32 chars."""
    from app.database import SessionLocal
    from app.models.user import User
    from app.models.session import SessionExercise, WorkoutSession
    from datetime import datetime, timezone
    from sqlalchemy import select
    with SessionLocal() as db:
        uid = db.execute(
            select(User.id).where(User.username == "testuser")
        ).scalar_one()
        ws = WorkoutSession(
            user_id=uid,
            template_slug_snapshot="push-a",
            template_name_snapshot="Push A",
            started_at=datetime.now(timezone.utc),
            status="in_progress",
        )
        db.add(ws)
        db.commit()
        se = SessionExercise(
            session_id=ws.id,
            exercise_code_snapshot="E1",
            exercise_name_snapshot="Incline Smith Press",
            position=1,
            implicit_label="trajectoire_coherente",
            implicit_label_computed_at=datetime.now(timezone.utc),
        )
        db.add(se)
        db.commit()
        db.refresh(se)
        assert se.implicit_label == "trajectoire_coherente"
        assert se.implicit_label_computed_at is not None


def test_session_exercise_implicit_label_nullable(client):
    """A session_exercise can stay with implicit_label=None forever
    (historic + sessions with < 3 work sets)."""
    from app.database import SessionLocal
    from app.models.user import User
    from app.models.session import SessionExercise, WorkoutSession
    from datetime import datetime, timezone
    from sqlalchemy import select
    with SessionLocal() as db:
        uid = db.execute(
            select(User.id).where(User.username == "testuser")
        ).scalar_one()
        ws = WorkoutSession(
            user_id=uid,
            template_slug_snapshot="push-a",
            template_name_snapshot="Push A",
            started_at=datetime.now(timezone.utc),
            status="in_progress",
        )
        db.add(ws)
        db.commit()
        se = SessionExercise(
            session_id=ws.id,
            exercise_code_snapshot="E1",
            exercise_name_snapshot="Incline Smith Press",
            position=1,
        )
        db.add(se)
        db.commit()
        db.refresh(se)
        assert se.implicit_label is None
        assert se.implicit_label_computed_at is None
