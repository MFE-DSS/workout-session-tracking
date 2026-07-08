"""Sb_32.1 — BodyZone / Muscle foundation + backfill invariance.

Guards the first relational object of the Sx_32 refactor:

Model & schema
  * ``BodyZone`` / ``Muscle`` models exist with the expected columns.
  * The migration creates ONLY the two new tables — no existing table's
    column set is mutated (invariance = contrainte #1).

Backfill invariance
  * The 11 zones are backfilled from the CURRENT ``muscle_mapping``
    constants, value-for-value (labels / measurement_field / radar_axis /
    volume_target), with ``core`` correctly off-radar (radar_axis NULL).
  * ``muscles`` stays EMPTY in V1 (OQ-32-B/F — no invented anatomy).

Behaviour invariance (non-regression baseline)
  * ``tests/fixtures/classify_exercise_baseline.json`` exists and is a
    faithful snapshot of the current ``classify_exercise`` output for the
    91-exercise catalog. Sb_32.2 (classify → DB lookup) must reproduce it
    exactly. No ``unknown`` regression on the catalog.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

ROOT = Path(__file__).resolve().parent.parent
BASELINE = ROOT / "tests" / "fixtures" / "classify_exercise_baseline.json"

# down_revision of Sb_32.1 — the schema state BEFORE our migration.
PREVIOUS_HEAD = "7i0f5d1e2g43"
SB_32_1_REVISION = "j1k6e2f3h54"


# ───────── helpers ─────────


def _fresh_db_at(revision: str) -> Path:
    """Build a throwaway SQLite migrated up to ``revision`` and return path."""
    tmp_dir = tempfile.mkdtemp(prefix="sb32-mig-")
    db_path = Path(tmp_dir) / "sb32.db"
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(cfg, revision)
    return db_path


def _columns_by_table(db_path: Path) -> dict[str, set[str]]:
    engine = create_engine(f"sqlite:///{db_path}")
    insp = inspect(engine)
    out = {t: {c["name"] for c in insp.get_columns(t)} for t in insp.get_table_names()}
    engine.dispose()
    return out


# ───────── models & structure ─────────


def test_bodyzone_model_exists():
    from app.models.body_zone import BodyZone

    cols = {c.name for c in BodyZone.__table__.columns}
    assert cols == {
        "id",
        "code",
        "label",
        "measurement_field",
        "radar_axis",
        "volume_target",
        "is_active",
        "created_at",
    }
    assert BodyZone.__tablename__ == "body_zones"


def test_muscle_model_exists():
    from app.models.muscle import Muscle

    cols = {c.name for c in Muscle.__table__.columns}
    assert cols == {
        "id",
        "code",
        "name",
        "body_zone_code",
        "category",
        "is_active",
        "created_at",
    }
    assert Muscle.__tablename__ == "muscles"


def test_migration_creates_only_new_tables():
    """The two new tables appear; no pre-existing table is added or removed."""
    before = set(_columns_by_table(_fresh_db_at(PREVIOUS_HEAD)))
    after_cols = _columns_by_table(_fresh_db_at(SB_32_1_REVISION))
    after = set(after_cols)

    added = after - before
    removed = before - after
    assert added == {"body_zones", "muscles"}, f"unexpected table delta: {added}"
    assert not removed, f"tables removed by migration: {removed}"


def test_no_existing_table_mutated():
    """Every table that existed before the migration keeps the EXACT same
    column set afterwards — no additive/removed column on legacy tables."""
    before = _columns_by_table(_fresh_db_at(PREVIOUS_HEAD))
    after = _columns_by_table(_fresh_db_at(SB_32_1_REVISION))
    for table, cols in before.items():
        assert after[table] == cols, f"columns of '{table}' changed: {cols} -> {after[table]}"


# ───────── backfill invariance ─────────


def _backfilled_zones(db_path: Path) -> dict[str, dict]:
    engine = create_engine(f"sqlite:///{db_path}")
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT code, label, measurement_field, radar_axis, "
                "volume_target, is_active FROM body_zones"
            )
        ).fetchall()
    engine.dispose()
    return {
        r[0]: {
            "label": r[1],
            "measurement_field": r[2],
            "radar_axis": r[3],
            "volume_target": r[4],
            "is_active": r[5],
        }
        for r in rows
    }


def test_bodyzone_backfill_matches_current_zone_constants():
    """Every zone in ``ZONE_LABELS`` is backfilled — same codes, no more,
    no less."""
    from app.services.muscle_mapping import ZONE_LABELS

    zones = _backfilled_zones(_fresh_db_at(SB_32_1_REVISION))
    assert set(zones) == set(ZONE_LABELS), (
        f"backfilled zones diverge from ZONE_LABELS: "
        f"{set(zones) ^ set(ZONE_LABELS)}"
    )
    assert len(zones) == 11


def test_bodyzone_backfill_preserves_labels_measurement_radar_volume():
    """Value-for-value invariance against the current constants — the
    single source of truth we are formalising, not re-deciding."""
    from app.services.muscle_mapping import (
        RADAR_AXES,
        ZONE_LABELS,
        ZONE_MEASUREMENT,
        ZONE_VOLUME_TARGET,
    )

    zone_to_axis: dict[str, str] = {}
    for axis, spec in RADAR_AXES.items():
        for zone_code in spec["zones"]:
            zone_to_axis[zone_code] = axis

    zones = _backfilled_zones(_fresh_db_at(SB_32_1_REVISION))
    for code, label in ZONE_LABELS.items():
        row = zones[code]
        assert row["label"] == label
        assert row["measurement_field"] == ZONE_MEASUREMENT.get(code)
        assert row["radar_axis"] == zone_to_axis.get(code)
        assert row["volume_target"] == ZONE_VOLUME_TARGET.get(code)
        assert row["is_active"] == 1


def test_core_zone_is_off_radar():
    """``core`` is the one zone absent from RADAR_AXES → its backfilled
    radar_axis must be NULL (explicit regression guard for the tricky row)."""
    zones = _backfilled_zones(_fresh_db_at(SB_32_1_REVISION))
    assert zones["core"]["radar_axis"] is None
    assert zones["core"]["measurement_field"] == "waist_cm"


def test_muscle_table_created_and_empty_v1():
    """muscles table exists but stays empty in V1 (no invented anatomy)."""
    db_path = _fresh_db_at(SB_32_1_REVISION)
    engine = create_engine(f"sqlite:///{db_path}")
    with engine.connect() as conn:
        assert "muscles" in inspect(engine).get_table_names()
        count = conn.execute(text("SELECT COUNT(*) FROM muscles")).scalar()
    engine.dispose()
    assert count == 0


# ───────── behaviour invariance (baseline) ─────────


def test_muscle_mapping_invariance_baseline_exists():
    assert BASELINE.exists(), "classify_exercise baseline fixture missing"
    data = json.loads(BASELINE.read_text(encoding="utf-8"))
    assert data["count"] == 91
    assert len(data["entries"]) == 91


def test_current_classify_exercise_matches_committed_baseline():
    """The committed baseline must EXACTLY reproduce today's
    ``classify_exercise`` output. This is the guard Sb_32.2 will run
    against once classification moves to a DB lookup — any drift there
    (or an accidental change here) fails loudly."""
    from app.services.muscle_mapping import classify_exercise

    data = json.loads(BASELINE.read_text(encoding="utf-8"))
    for entry in data["entries"]:
        primary, secondary = classify_exercise(entry["name"])
        assert primary == entry["primary"], (
            f"primary drift for {entry['name']!r}: "
            f"{primary} != baseline {entry['primary']}"
        )
        assert secondary == entry["secondary"], (
            f"secondary drift for {entry['name']!r}: "
            f"{secondary} != baseline {entry['secondary']}"
        )


def test_no_unknown_regression_on_catalog():
    """Every catalog exercise resolves to a known primary zone today —
    a lower bound Sb_32.2's DB-backed classifier must not regress below."""
    data = json.loads(BASELINE.read_text(encoding="utf-8"))
    unknown = [e["name"] for e in data["entries"] if e["primary"] == "unknown"]
    assert not unknown, f"catalog exercises with unknown primary zone: {unknown}"
