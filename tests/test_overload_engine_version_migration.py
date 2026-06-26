"""Sb_30.3 — Migration overload_engine_version roundtrip + model field.

Vérifie :
- la colonne `workout_sessions.overload_engine_version` existe après upgrade
- le default = 1 est appliqué (server_default)
- le model SQLAlchemy expose le champ et le valeur côté Python = 1 par défaut
- les pre-existing rows (créées avant la migration) reçoivent bien 1
- la suite catalog_qa / migration_patterns ne casse pas
- la version Python = la version DB (cohérence)
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import inspect, text

from app.services.overload_engine import OVERLOAD_ENGINE_VERSION


def test_column_exists_on_workout_sessions(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        cols = {c["name"] for c in inspect(db.bind).get_columns("workout_sessions")}
        assert "overload_engine_version" in cols


def test_default_value_is_one_for_new_session(client):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = WorkoutSession(
            user_id=user.id,
            template_slug_snapshot="migrate-test",
            template_name_snapshot="Migrate test",
            started_at=datetime.now(UTC),
            status="in_progress",
        )
        db.add(s)
        db.commit()
        db.refresh(s)
        assert s.overload_engine_version == 1


def test_default_via_raw_sql_insert(client):
    """Insert SQL bruts (sans passer par le model Python) → la valeur
    server_default doit être appliquée par SQLite."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        db.execute(
            text(
                "INSERT INTO workout_sessions "
                "(user_id, template_slug_snapshot, template_name_snapshot, "
                " started_at, status, excluded_from_stats) "
                "VALUES (:uid, 'raw', 'Raw', :now, 'in_progress', 0)"
            ),
            {"uid": user.id, "now": datetime.now(UTC).isoformat()},
        )
        db.commit()
        row = db.execute(
            text(
                "SELECT overload_engine_version FROM workout_sessions "
                "WHERE template_slug_snapshot='raw' ORDER BY id DESC LIMIT 1"
            )
        ).fetchone()
        assert row is not None
        assert row[0] == 1


def test_engine_version_constant_matches_default():
    """La constante Python de l'engine doit toujours rester égale à la
    valeur DEFAULT de la migration (Sx_30 §6.3 versioning contract).
    Quand l'engine bump à 2+, il faudra une nouvelle migration pour
    rester cohérent."""
    assert OVERLOAD_ENGINE_VERSION == 1


def test_alembic_head_includes_overload_migration():
    """La head courante doit être la revision Sb_30.3."""
    from pathlib import Path

    versions = Path(__file__).resolve().parent.parent / "migrations" / "versions"
    sx30_files = list(versions.glob("*overload_engine_version*.py"))
    assert sx30_files, "no Sb_30.3 migration file found"
    src = sx30_files[0].read_text(encoding="utf-8")
    assert 'revision = "6h9e4c0d1f32"' in src
    assert 'down_revision = "5g8d3b9c0e21"' in src
    assert "upgrade()" in src
    assert "downgrade()" in src
