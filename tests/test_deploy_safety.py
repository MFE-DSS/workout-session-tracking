"""Pin the production deploy safety guarantees (Sb_OPS_DEPLOY_SAFETY_01).

Three of these guarantees are shell-level and cannot be exercised without a production host, so
they are pinned as ORDERING and FAIL-CLOSED guards over the script sources. That is deliberate:
the defects being fixed were exactly ordering defects (a SHA read after the checkout that
overwrote it) and a fail-open defect (a warning where an abort was required). A source guard
catches a regression of either; a mock host would not.

The SQLite path resolution is real logic, so it is tested as real logic.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

from scripts.resolve_sqlite_path import (
    NO_FILE,
    NOT_SQLITE,
    is_sqlite_url,
    main,
    resolve_sqlite_path,
)

_ROOT = pathlib.Path(__file__).resolve().parent.parent
_WRAPPER = _ROOT / "scripts" / "deploy_from_github_actions.sh"
_DEPLOY = _ROOT / "scripts" / "deploy_prod.sh"
_SMOKE = _ROOT / "scripts" / "smoke_deploy.sh"
_WORKFLOW = _ROOT / ".github" / "workflows" / "deploy-production.yml"


def _src(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


# ─────────────────── 1. SQLite path resolution ───────────────────


@pytest.mark.parametrize(
    ("url", "expected_suffix"),
    [
        ("sqlite:///./var/workout.db", "/app/var/workout.db"),
        ("sqlite:///var/workout.db", "/app/var/workout.db"),
        ("sqlite:///data/other.db", "/app/data/other.db"),
        ("sqlite+pysqlite:///./var/workout.db", "/app/var/workout.db"),
        ("sqlite:///./var/workout.db?check_same_thread=False", "/app/var/workout.db"),
    ],
)
def test_relative_urls_resolve_against_app_dir(url, expected_suffix):
    resolved = resolve_sqlite_path(url, "/app")
    assert str(resolved) == expected_suffix


def test_absolute_url_is_not_reparented():
    resolved = resolve_sqlite_path("sqlite:////srv/workout/var/workout.db", "/app")
    assert str(resolved) == "/srv/workout/var/workout.db"


def test_the_real_production_url_resolves_to_the_real_file():
    """The exact pairing that the Aug-10 deploy relied on, previously hardcoded."""
    resolved = resolve_sqlite_path(
        "sqlite:///./var/workout.db", "/opt/workout-session-tracking"
    )
    assert str(resolved) == "/opt/workout-session-tracking/var/workout.db"


@pytest.mark.parametrize("url", ["sqlite://", "sqlite:///:memory:", "sqlite+pysqlite://"])
def test_in_memory_urls_resolve_to_no_file(url):
    assert resolve_sqlite_path(url, "/app") is None


@pytest.mark.parametrize(
    "url",
    [
        "postgresql://u:p@localhost/db",
        "postgresql+psycopg://u:p@localhost/db",
        "mysql://u:p@localhost/db",
    ],
)
def test_non_sqlite_urls_are_rejected(url):
    assert is_sqlite_url(url) is False
    with pytest.raises(ValueError):
        resolve_sqlite_path(url, "/app")


def test_sqlite_detection_covers_driver_suffixes():
    assert is_sqlite_url("sqlite:///x.db") is True
    assert is_sqlite_url("SQLite:///x.db") is True
    assert is_sqlite_url("sqlite+aiosqlite:///x.db") is True


# ─────────────────── 2. CLI exit-code contract (the shell API) ───────────────────


def test_cli_prints_path_and_exits_zero(capsys):
    assert main(["--database-url", "sqlite:///./var/x.db", "--app-dir", "/app"]) == 0
    assert capsys.readouterr().out.strip() == "/app/var/x.db"


def test_cli_signals_not_sqlite_so_postgres_skips_the_backup(capsys):
    assert main(["--database-url", "postgresql://u@h/db", "--app-dir", "/app"]) == NOT_SQLITE
    assert capsys.readouterr().out.strip() == ""


def test_cli_signals_no_file_for_in_memory(capsys):
    assert main(["--database-url", "sqlite:///:memory:", "--app-dir", "/app"]) == NO_FILE
    assert capsys.readouterr().out.strip() == ""


def test_cli_is_stdlib_only_and_runs_as_a_subprocess(tmp_path):
    """It runs on the host BEFORE `pip install`, so it must work on a bare interpreter."""
    result = subprocess.run(
        [
            sys.executable,
            str(_ROOT / "scripts" / "resolve_sqlite_path.py"),
            "--database-url",
            "sqlite:///./var/workout.db",
            "--app-dir",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == f"{tmp_path}/var/workout.db"


# ─────────────────── 3. Rollback SHA captured BEFORE the reset ───────────────────


def test_wrapper_captures_previous_sha_before_resetting_the_tree():
    """Anchor on the EXECUTED command, not on prose mentioning it in a comment."""
    src = _src(_WRAPPER)
    capture = src.index("HOST_PRE_SHA=")
    reset = src.index('sudo -u "$APP_USER" git reset --hard')
    assert capture < reset, "HOST_PRE_SHA must be read BEFORE git reset --hard"


def test_wrapper_exports_previous_sha():
    assert "export HOST_PRE_SHA" in _src(_WRAPPER)


def test_wrapper_reports_both_shas():
    src = _src(_WRAPPER)
    assert "previous SHA" in src
    assert "target   SHA" in src


def test_deploy_prefers_the_wrapper_supplied_previous_sha():
    """Falls back to reading HEAD only for manual runs, which pull themselves."""
    assert 'PRE_SHA="${HOST_PRE_SHA:-' in _src(_DEPLOY)


def test_target_sha_is_read_from_the_tree_not_copied_from_previous():
    """Previously `POST_SHA="${PRE_SHA}"`, which now would report the rollback target."""
    src = _src(_DEPLOY)
    assert 'POST_SHA="${PRE_SHA}"' not in src


def test_deploy_state_records_the_rollback_target():
    assert '--previous-sha "${PRE_SHA}"' in _src(_DEPLOY)


def test_deploy_state_writer_round_trips_previous_sha(tmp_path):
    """End-to-end through the real CLI: the rollback target must land in the JSON."""
    import json

    out = tmp_path / "deploy_state.json"
    result = subprocess.run(
        [
            sys.executable,
            str(_ROOT / "scripts" / "write_deploy_state.py"),
            "--sha",
            "b" * 40,
            "--previous-sha",
            "a" * 40,
            "--out",
            str(out),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["sha"] == "b" * 40
    assert payload["previous_sha"] == "a" * 40


# ─────────────────── 4. Backup fail-closed, before Alembic ───────────────────


def test_backup_no_longer_hardcodes_the_database_path():
    assert 'SQLITE_PATH="${APP_DIR}/var/workout.db"' not in _src(_DEPLOY)


def test_backup_resolves_the_path_from_database_url():
    assert "resolve_sqlite_path.py" in _src(_DEPLOY)


def test_missing_database_file_aborts_instead_of_warning():
    """The exact fail-open defect: a warning let the deploy migrate with no backup."""
    src = _src(_DEPLOY)
    assert "skipping backup" not in src
    assert "refusing to migrate without a backup" in src


def test_backup_requires_a_regular_non_empty_file():
    src = _src(_DEPLOY)
    assert '[ -f "${SQLITE_PATH}" ]' in src
    assert '[ -s "${SQLITE_BACKUP}" ]' in src


def test_backup_failure_aborts():
    src = _src(_DEPLOY)
    assert "sqlite3 backup FAILED" in src
    assert "cp backup FAILED" in src


def test_backup_block_precedes_alembic_invocation():
    """Ordering is the whole point: no migration may run before a verified snapshot."""
    src = _src(_DEPLOY)
    backup = src.index("Backing up SQLite database")
    alembic = src.index("upgrade head")
    assert backup < alembic


def test_postgres_path_is_untouched_by_the_sqlite_guards():
    """Every new abort lives inside the `IS_SQLITE -eq 1` branch."""
    src = _src(_DEPLOY)
    sqlite_branch = src.index('if [ "${IS_SQLITE}" -eq 1 ]')
    end_of_branch = src.index("Pull latest code", sqlite_branch)
    guarded = src[sqlite_branch:end_of_branch]
    assert guarded.count("refusing to migrate without a backup") >= 3
    assert "PostgreSQL" not in guarded


# ─────────────────── 5. Custom Program smoke ───────────────────


def test_smoke_covers_the_custom_program_surface():
    src = _src(_SMOKE)
    assert 'check_auth_redirect "GET /programs requires auth" "/programs"' in src
    assert "/programs/new" in src


def test_smoke_invents_no_credentials():
    """Non-destructive by construction: unauthenticated redirect checks only."""
    src = _src(_SMOKE)
    for forbidden in ("password", "testpass", "POST /programs", "--data"):
        assert forbidden not in src


# ─────────────────── 6. Workflow ref safety ───────────────────


def test_workflow_has_no_misleading_branch_default():
    src = _src(_WORKFLOW)
    assert 'default: "main"' not in src


def test_workflow_ref_is_still_required():
    src = _src(_WORKFLOW)
    ref_block = src[src.index("      ref:") : src.index("      skip_smoke:")]
    assert "required: true" in ref_block
    assert "default:" not in ref_block


def test_workflow_logs_the_resolved_full_sha():
    src = _src(_WORKFLOW)
    assert "Resolved SHA" in src
    assert "git rev-parse HEAD" in src


def test_workflow_stays_dispatch_only_with_production_approval():
    src = _src(_WORKFLOW)
    assert "workflow_dispatch:" in src
    assert "environment: production" in src
    trigger_block = src[: src.index("permissions:")]
    assert "\n  push:" not in trigger_block
    assert "\n  schedule:" not in trigger_block
