"""Sb_32.2 — ExerciseMuscleMapping + classify_exercise DB lookup/fallback.

Guards the second relational object of the Sx_32 refactor and, above all,
the **invariance** of exercise classification against the Sb_32.1 baseline.

Model & migration
  * ``ExerciseMuscleMapping`` model exists with the expected columns.
  * The migration creates ONLY the new table (no existing table mutated).
  * Additive-only ; FK to ``body_zones.code`` valid ; ``muscle_code`` nullable.

Backfill invariance (vs Sb_32.1 baseline)
  * Backfill row count = baseline known-primary + secondary rows (deduped by
    exercise name, the stable identity).
  * ``unknown`` baseline exercises are NOT inserted (fallback keeps ``unknown``).

Classification invariance (contrainte #1)
  * DB lookup (``exercise_code`` = name) reproduces the baseline EXACTLY for
    all 91 catalog exercises.
  * name-only ``classify_exercise(name)`` reproduces the baseline EXACTLY.
  * Lookup falls back to substring when no mapping exists for a code.
  * Output format unchanged ``tuple[str, list[str]]`` ; secondary order stable.
  * No consumer service file was changed by this sprint.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session

ROOT = Path(__file__).resolve().parent.parent
BASELINE = ROOT / "tests" / "fixtures" / "classify_exercise_baseline.json"

PREVIOUS_HEAD = "j1k6e2f3h54"      # Sb_32.1
SB_32_2_REVISION = "k2l7f3g4i65"   # Sb_32.2

# Consumer service files this sprint must NOT touch.
FORBIDDEN_CONSUMER_FILES = [
    "app/services/muscle_scoring.py",
    "app/services/body_intelligence_inputs.py",
    "app/services/coach_inference.py",
    "app/services/coach_report.py",
    "app/services/recommendation.py",
    "app/services/profile_metrics.py",
    "app/services/session_recap.py",
]


# ───────── helpers ─────────


def _fresh_db_at(revision: str) -> Path:
    tmp_dir = tempfile.mkdtemp(prefix="sb322-mig-")
    db_path = Path(tmp_dir) / "sb322.db"
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(cfg, revision)
    return db_path


def _tables(db_path: Path) -> set[str]:
    engine = create_engine(f"sqlite:///{db_path}")
    names = set(inspect(engine).get_table_names())
    engine.dispose()
    return names


def _columns_by_table(db_path: Path) -> dict[str, set[str]]:
    engine = create_engine(f"sqlite:///{db_path}")
    insp = inspect(engine)
    out = {t: {c["name"] for c in insp.get_columns(t)} for t in insp.get_table_names()}
    engine.dispose()
    return out


def _baseline_entries() -> list[dict]:
    return json.loads(BASELINE.read_text(encoding="utf-8"))["entries"]


def _baseline_by_name() -> dict[str, tuple[str, list[str]]]:
    by_name: dict[str, tuple[str, list[str]]] = {}
    for e in _baseline_entries():
        by_name.setdefault(e["name"], (e["primary"], list(e["secondary"])))
    return by_name


# ───────── 1. model ─────────


def test_exercise_muscle_mapping_model_exists():
    from app.models.exercise_muscle_mapping import ExerciseMuscleMapping

    cols = {c.name for c in ExerciseMuscleMapping.__table__.columns}
    assert cols == {
        "id",
        "exercise_code",
        "body_zone_code",
        "muscle_code",
        "role",
        "source",
        "position",
        "is_active",
        "created_at",
    }
    assert ExerciseMuscleMapping.__tablename__ == "exercise_muscle_mappings"


# ───────── 2-3. migration additive ─────────


def test_migration_creates_only_new_table():
    before = _tables(_fresh_db_at(PREVIOUS_HEAD))
    after = _tables(_fresh_db_at(SB_32_2_REVISION))
    assert after - before == {"exercise_muscle_mappings"}
    assert not (before - after)


def test_migration_is_additive_no_existing_table_mutated():
    before = _columns_by_table(_fresh_db_at(PREVIOUS_HEAD))
    after = _columns_by_table(_fresh_db_at(SB_32_2_REVISION))
    for table, cols in before.items():
        assert after[table] == cols, f"columns of '{table}' changed"


# ───────── 4-5. FK + nullable ─────────


def test_fk_to_body_zones_valid_and_muscle_code_nullable():
    db_path = _fresh_db_at(SB_32_2_REVISION)
    engine = create_engine(f"sqlite:///{db_path}")
    insp = inspect(engine)
    fks = insp.get_foreign_keys("exercise_muscle_mappings")
    targets = {(fk["referred_table"], tuple(fk["referred_columns"])) for fk in fks}
    assert ("body_zones", ("code",)) in targets
    assert ("muscles", ("code",)) in targets

    cols = {c["name"]: c for c in insp.get_columns("exercise_muscle_mappings")}
    assert cols["muscle_code"]["nullable"] is True
    assert cols["body_zone_code"]["nullable"] is False
    engine.dispose()

    # Every backfilled body_zone_code must reference an existing zone.
    with Session(engine := create_engine(f"sqlite:///{db_path}")) as db:
        orphan = db.execute(
            text(
                "SELECT COUNT(*) FROM exercise_muscle_mappings m "
                "LEFT JOIN body_zones z ON m.body_zone_code = z.code "
                "WHERE z.code IS NULL"
            )
        ).scalar()
    engine.dispose()
    assert orphan == 0


# ───────── 6-7. backfill row counts + unknown excluded ─────────


def test_backfill_count_matches_baseline_known_rows():
    by_name = _baseline_by_name()
    expected_primary = sum(1 for p, _ in by_name.values() if p != "unknown")
    expected_secondary = sum(
        len(secs) for p, secs in by_name.values() if p != "unknown"
    )

    db_path = _fresh_db_at(SB_32_2_REVISION)
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as db:
        total = db.execute(
            text("SELECT COUNT(*) FROM exercise_muscle_mappings")
        ).scalar()
        primary = db.execute(
            text("SELECT COUNT(*) FROM exercise_muscle_mappings WHERE role='primary'")
        ).scalar()
        secondary = db.execute(
            text(
                "SELECT COUNT(*) FROM exercise_muscle_mappings WHERE role='secondary'"
            )
        ).scalar()
    engine.dispose()

    assert primary == expected_primary
    assert secondary == expected_secondary
    assert total == expected_primary + expected_secondary


def test_unknown_baseline_not_inserted_as_mapping():
    by_name = _baseline_by_name()
    unknown_names = [n for n, (p, _) in by_name.items() if p == "unknown"]

    db_path = _fresh_db_at(SB_32_2_REVISION)
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as db:
        for name in unknown_names:
            n = db.execute(
                text(
                    "SELECT COUNT(*) FROM exercise_muscle_mappings "
                    "WHERE exercise_code = :c"
                ),
                {"c": name},
            ).scalar()
            assert n == 0, f"unknown exercise {name!r} should have no mapping"
    engine.dispose()

    # V1 backfill uses primary + secondary only ; no stabilizer invented.
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as db:
        roles = {
            r[0]
            for r in db.execute(
                text("SELECT DISTINCT role FROM exercise_muscle_mappings")
            ).fetchall()
        }
    engine.dispose()
    assert roles == {"primary", "secondary"}


# ───────── 8. DB lookup reproduces baseline for 91 ─────────


def test_db_lookup_reproduces_baseline_for_all_catalog():
    from app.services.muscle_mapping import classify_exercise

    db_path = _fresh_db_at(SB_32_2_REVISION)
    engine = create_engine(f"sqlite:///{db_path}")
    mismatches = []
    with Session(engine) as db:
        for e in _baseline_entries():
            name = e["name"]
            got = classify_exercise(name, db=db, exercise_code=name)
            if got[0] != e["primary"] or list(got[1]) != e["secondary"]:
                mismatches.append((name, (e["primary"], e["secondary"]), got))
    engine.dispose()
    assert not mismatches, f"DB lookup diverges from baseline: {mismatches[:5]}"


# ───────── 9, 11, 12. name-only unchanged + format + order ─────────


def test_name_only_classify_reproduces_baseline():
    from app.services.muscle_mapping import classify_exercise

    for e in _baseline_entries():
        got = classify_exercise(e["name"])
        assert got[0] == e["primary"]
        assert got[1] == e["secondary"]  # exact order


def test_output_format_is_tuple_str_list():
    from app.services.muscle_mapping import classify_exercise

    r = classify_exercise("Chest Press machine")
    assert isinstance(r, tuple) and len(r) == 2
    assert isinstance(r[0], str)
    assert isinstance(r[1], list)
    assert all(isinstance(x, str) for x in r[1])


def test_secondary_order_stable_via_position():
    """Secondary zones come back in baseline order (driven by `position`)."""
    from app.services.muscle_mapping import classify_exercise

    db_path = _fresh_db_at(SB_32_2_REVISION)
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as db:
        # A multi-secondary exercise exists? all our secondaries are single,
        # but the ordering contract must still hold for any code.
        name = "Chest Press machine"  # secondary = ["triceps"]
        got = classify_exercise(name, db=db, exercise_code=name)
    engine.dispose()
    assert got == ("pecs", ["triceps"])


# ───────── 10. fallback when mapping absent ─────────


def test_lookup_falls_back_to_substring_when_no_mapping():
    from app.services.muscle_mapping import classify_exercise

    db_path = _fresh_db_at(SB_32_2_REVISION)
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as db:
        # A code that is NOT backfilled → lookup miss → substring on the name.
        # "Curl truc inédit" has no mapping row but the name matches "curl".
        got = classify_exercise(
            "Curl truc inédit", db=db, exercise_code="Curl truc inédit"
        )
        assert got == ("biceps", [])  # substring fallback

        # Unknown code AND unknown name → substring returns unknown.
        got2 = classify_exercise(
            "Zzz inconnu total", db=db, exercise_code="Zzz inconnu total"
        )
        assert got2 == ("unknown", [])
    engine.dispose()


# ───────── 13-14. no consumer changed + public compat ─────────


def test_only_the_authorised_consumer_reads_the_formal_contract():
    """Exactly one heavy consumer is migrated — pinned at source level.

    Sb_32.4 replaces the previous `git diff --name-only HEAD` guard here. That
    guard was written for Sb_32.2 to prove *that* sprint deferred the consumer
    migration, and its own docstring named Sb_32.4 as the sprint that would
    perform it — so this is the sprint it anticipated, not a contract being
    broken. It is also **not weakened**: the old form compared the working tree,
    so it went green the moment the change was committed and asserted nothing in
    CI. This one reads the source and keeps biting forever.

    The contract it now enforces: `muscle_scoring` reads the canonical
    body-zone contract, and every other listed consumer still does not — a
    later migration must be a deliberate, reviewed step, not a drift.
    """
    migrated = {"app/services/muscle_scoring.py"}
    for rel in FORBIDDEN_CONSUMER_FILES:
        source = (ROOT / rel).read_text(encoding="utf-8")
        imports_contract = "body_zone_source" in source
        if rel in migrated:
            assert imports_contract, f"{rel} must read the formal contract"
        else:
            assert not imports_contract, (
                f"{rel} started reading body_zone_source outside a migration "
                f"sprint — migrating a consumer is a reviewed decision"
            )


def test_classify_exercise_public_compat_signature():
    """name-only positional call still works; new params are keyword-only."""
    import inspect as pyinspect

    from app.services.muscle_mapping import classify_exercise

    sig = pyinspect.signature(classify_exercise)
    params = sig.parameters
    assert list(params)[0] == "name"
    assert params["name"].kind in (
        params["name"].POSITIONAL_OR_KEYWORD,
        params["name"].POSITIONAL_ONLY,
    )
    assert params["exercise_code"].kind == params["exercise_code"].KEYWORD_ONLY
    assert params["db"].kind == params["db"].KEYWORD_ONLY
    assert params["exercise_code"].default is None
    assert params["db"].default is None


# ───────── 15. no unknown regression ─────────


def test_no_unknown_regression_on_catalog():
    from app.services.muscle_mapping import classify_exercise

    unknown = [e["name"] for e in _baseline_entries() if classify_exercise(e["name"])[0] == "unknown"]
    assert not unknown, f"unknown regression: {unknown}"
