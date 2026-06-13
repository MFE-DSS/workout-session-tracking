"""Sb_26.2 — tests for migration hardening tooling.

Covers:
* `scripts/check_migration_patterns.py` catches the patterns it claims to
  catch (synthetic migration snippets);
* the committed schema snapshot matches alembic head (delegates to the
  same logic as `check_schema_snapshot.py` so the pytest job blocks the
  PR even if CI yaml drifts);
* the migration roundtrip succeeds (downgrade -1 + upgrade head).
"""
from __future__ import annotations

import importlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def _load(name: str):
    """Load a script as a module (scripts/ is not a package)."""
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# ───────── pattern linter ─────────


def _write_migration(tmp_path: Path, body: str) -> Path:
    f = tmp_path / "20990101_test_migration.py"
    f.write_text(body, encoding="utf-8")
    return f


def _scan(monkeypatch, tmp_path, body, *, grandfathered=False, strict=False):
    """Scan a single synthetic migration and return findings."""
    mod = _load("check_migration_patterns")
    policy = json.loads((ROOT / ".migration-policy.json").read_text())
    if grandfathered:
        policy["grandfathered_files"] = [_write_migration(tmp_path, body).name]
        path = tmp_path / "20990101_test_migration.py"
    else:
        policy["grandfathered_files"] = []
        path = _write_migration(tmp_path, body)
    return mod._scan_file(path, policy)


def test_pattern_linter_flags_drop_column_in_upgrade(monkeypatch, tmp_path):
    body = (
        "def upgrade():\n"
        "    op.drop_column('users', 'email')\n"
        "def downgrade():\n"
        "    pass\n"
    )
    findings = _scan(monkeypatch, tmp_path, body)
    rules = {f.rule for f in findings}
    assert "drop_column_in_upgrade" in rules


def test_pattern_linter_flags_drop_table_in_upgrade(monkeypatch, tmp_path):
    body = (
        "def upgrade():\n"
        "    op.drop_table('legacy_table')\n"
        "def downgrade():\n"
        "    pass\n"
    )
    findings = _scan(monkeypatch, tmp_path, body)
    assert any(f.rule == "drop_table_in_upgrade" for f in findings)


def test_pattern_linter_flags_not_null_without_default(monkeypatch, tmp_path):
    body = (
        "import sqlalchemy as sa\n"
        "def upgrade():\n"
        "    op.add_column('users', sa.Column('age', sa.Integer(), nullable=False))\n"
        "def downgrade():\n"
        "    pass\n"
    )
    findings = _scan(monkeypatch, tmp_path, body)
    assert any(f.rule == "add_column_not_null_no_default" for f in findings)


def test_pattern_linter_accepts_not_null_with_server_default(monkeypatch, tmp_path):
    body = (
        "import sqlalchemy as sa\n"
        "def upgrade():\n"
        "    op.add_column('users',\n"
        "        sa.Column('age', sa.Integer(), nullable=False, server_default='0'))\n"
        "def downgrade():\n"
        "    pass\n"
    )
    findings = _scan(monkeypatch, tmp_path, body)
    assert not any(f.rule == "add_column_not_null_no_default" for f in findings)


def test_pattern_linter_flags_execute_delete(monkeypatch, tmp_path):
    body = (
        "def upgrade():\n"
        "    op.execute(\"DELETE FROM users WHERE is_active = 0\")\n"
        "def downgrade():\n"
        "    pass\n"
    )
    findings = _scan(monkeypatch, tmp_path, body)
    assert any(f.rule == "execute_delete_in_upgrade" for f in findings)


def test_pattern_linter_respects_justify_marker(monkeypatch, tmp_path):
    body = (
        "def upgrade():\n"
        "    # migration-justify: Sb_99 — table renamed, data backfilled separately\n"
        "    op.drop_table('legacy_table')\n"
        "def downgrade():\n"
        "    pass\n"
    )
    findings = _scan(monkeypatch, tmp_path, body)
    assert not any(f.rule == "drop_table_in_upgrade" for f in findings)


def test_pattern_linter_clean_on_simple_add_column(monkeypatch, tmp_path):
    body = (
        "import sqlalchemy as sa\n"
        "def upgrade():\n"
        "    op.add_column('users', sa.Column('age', sa.Integer(), nullable=True))\n"
        "def downgrade():\n"
        "    pass\n"
    )
    findings = _scan(monkeypatch, tmp_path, body)
    assert findings == []


def test_pattern_linter_on_real_repo_is_clean():
    """The current repo must pass its own linter — grandfathered list +
    no unjustified patterns in non-grandfathered files."""
    mod = _load("check_migration_patterns")
    policy = json.loads((ROOT / ".migration-policy.json").read_text())
    grandfathered = set(policy["grandfathered_files"])
    findings: list = []
    for f in sorted((ROOT / "migrations" / "versions").glob("*.py")):
        if f.name in grandfathered or f.name.startswith("__"):
            continue
        findings.extend(mod._scan_file(f, policy))
    assert findings == [], (
        f"Repo has {len(findings)} unjustified pattern(s): "
        + " | ".join(f.fmt() for f in findings)
    )


# ───────── schema snapshot ─────────


def test_schema_snapshot_matches_alembic_head():
    """If this fails: run `python scripts/generate_schema_snapshot.py`."""
    snapshot_mod = _load("generate_schema_snapshot")
    snapshot_path = ROOT / "data" / "schema_snapshot.sql"
    assert snapshot_path.exists(), "data/schema_snapshot.sql missing"

    import tempfile

    tmp_dir = tempfile.mkdtemp(prefix="schema-snap-test-")
    db_path = Path(tmp_dir) / "snap.db"
    snapshot_mod._alembic_upgrade(f"sqlite:///{db_path}")
    current = snapshot_mod._build_snapshot(db_path)
    committed = snapshot_path.read_text(encoding="utf-8")
    assert current == committed, (
        "Schema snapshot diverges from alembic head. "
        "Regenerate with `python scripts/generate_schema_snapshot.py`."
    )


# ───────── migration roundtrip ─────────


def test_migration_roundtrip_downgrade_one_then_upgrade():
    """Validates the prod rollback model: `downgrade -1` → `upgrade head`
    leaves the schema identical."""
    import tempfile

    from alembic import command
    from alembic.config import Config

    snapshot_mod = _load("generate_schema_snapshot")
    tmp_dir = tempfile.mkdtemp(prefix="roundtrip-test-")
    db_path = Path(tmp_dir) / "rt.db"
    db_url = f"sqlite:///{db_path}"
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", db_url)

    command.upgrade(cfg, "head")
    schema_before = snapshot_mod._build_snapshot(db_path)
    command.downgrade(cfg, "-1")
    command.upgrade(cfg, "head")
    schema_after = snapshot_mod._build_snapshot(db_path)

    assert schema_before == schema_after, (
        "Roundtrip downgrade -1 + upgrade head changes the schema — "
        "the last migration's downgrade() is not idempotent."
    )
