"""Pin the CI change-scope classifier (Sb_CI_02_1_PATH_AWARE_GATING).

The classifier decides whether a PR runs the full pytest/QA/coverage pipeline. A wrong
NON_RUNTIME silently skips the entire safety net, so these tests exist to make the
allow-list impossible to widen by accident: every NON_RUNTIME case is enumerated, and the
default for anything else — including the unknown — is pinned to RUNTIME_OR_INFRA.
"""
from __future__ import annotations

import sys

from scripts.classify_change_scope import (
    NON_RUNTIME,
    RUNTIME_OR_INFRA,
    classify,
    is_non_runtime_path,
    main,
    runtime_paths,
)

# ─────────────────── NON_RUNTIME: the closed allow-list ───────────────────


def test_docs_only_is_non_runtime():
    assert classify(["docs/SPRINT_X_REPORT.md", "docs/strategy/Sx_Y_SPEC.md"]) == NON_RUNTIME


def test_claude_skill_only_is_non_runtime():
    assert classify([".claude/skills/auren-standing-merge/SKILL.md"]) == NON_RUNTIME


def test_docs_and_skills_together_stay_non_runtime():
    scope = classify(
        ["docs/strategy/SPEC_REGISTRY.md", ".claude/skills/auren-sprint-from-spec/SKILL.md"]
    )
    assert scope == NON_RUNTIME


# ─────────────────── RUNTIME_OR_INFRA: every other category ───────────────────


def test_application_code_is_runtime():
    assert classify(["app/services/substitution.py"]) == RUNTIME_OR_INFRA


def test_test_code_is_runtime():
    assert classify(["tests/test_substitution.py"]) == RUNTIME_OR_INFRA


def test_data_taxonomy_is_runtime():
    assert classify(["data/exercise_properties.json"]) == RUNTIME_OR_INFRA


def test_scripts_are_runtime():
    assert classify(["scripts/check_ruff_budget.py"]) == RUNTIME_OR_INFRA


def test_workflow_is_runtime():
    assert classify([".github/workflows/ci.yml"]) == RUNTIME_OR_INFRA


def test_migration_is_runtime():
    assert classify(["migrations/versions/20260101_add_thing.py"]) == RUNTIME_OR_INFRA


def test_dependency_files_are_runtime():
    assert classify(["requirements.txt"]) == RUNTIME_OR_INFRA
    assert classify(["requirements-lock.txt"]) == RUNTIME_OR_INFRA
    assert classify(["pyproject.toml"]) == RUNTIME_OR_INFRA


def test_deploy_is_runtime():
    assert classify(["deploy/workout-backup.service"]) == RUNTIME_OR_INFRA


def test_templates_and_static_are_runtime():
    assert classify(["app/templates/base.html"]) == RUNTIME_OR_INFRA
    assert classify(["app/static/css/session_focus.css"]) == RUNTIME_OR_INFRA


# ─────────────────── fail-safe behaviour ───────────────────


def test_unknown_path_is_runtime():
    assert classify(["some/brand/new/thing.xyz"]) == RUNTIME_OR_INFRA


def test_empty_change_set_is_runtime():
    """An undetermined diff must never skip the suite."""
    assert classify([]) == RUNTIME_OR_INFRA
    assert classify(["", "   "]) == RUNTIME_OR_INFRA


def test_one_runtime_file_contaminates_a_docs_change_set():
    scope = classify(["docs/a.md", "docs/b.md", "app/main.py"])
    assert scope == RUNTIME_OR_INFRA


def test_repo_contract_and_claude_settings_are_not_allow_listed():
    """CLAUDE.md governs execution and .claude/settings.json governs permissions:
    neither is inert operator documentation."""
    assert classify(["CLAUDE.md"]) == RUNTIME_OR_INFRA
    assert classify([".claude/settings.json"]) == RUNTIME_OR_INFRA


def test_lookalike_prefixes_do_not_slip_through():
    """`docs` must be a directory, not a prefix of another name."""
    assert classify(["docsite/index.md"]) == RUNTIME_OR_INFRA
    assert classify(["app/docs/readme.md"]) == RUNTIME_OR_INFRA
    assert classify([".claude/skills_backup/x.md"]) == RUNTIME_OR_INFRA


def test_paths_are_normalised():
    assert is_non_runtime_path("./docs/a.md") is True
    assert is_non_runtime_path('"docs/a.md"') is True
    assert is_non_runtime_path(".claude\\skills\\x\\SKILL.md") is True


# ─────────────────── explainability + CLI ───────────────────


def test_runtime_paths_reports_only_the_forcing_files():
    forcing = runtime_paths(["docs/a.md", "app/main.py", "tests/test_x.py"])
    assert forcing == ["app/main.py", "tests/test_x.py"]


def test_cli_writes_github_output(tmp_path, monkeypatch, capsys):
    output = tmp_path / "gh_output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))

    assert main(["--files", "docs/a.md", "--github-output"]) == 0
    written = output.read_text(encoding="utf-8")
    assert "scope=NON_RUNTIME" in written
    assert "runtime=false" in written

    assert main(["--files", "app/main.py", "--github-output"]) == 0
    written = output.read_text(encoding="utf-8")
    assert "scope=RUNTIME_OR_INFRA" in written
    assert "runtime=true" in written


def test_cli_reads_stdin(monkeypatch, capsys):
    class _Stdin:
        @staticmethod
        def isatty() -> bool:
            return False

        @staticmethod
        def read() -> str:
            return "docs/a.md\ndocs/b.md\n"

    monkeypatch.setattr(sys, "stdin", _Stdin)
    assert main([]) == 0
    assert "NON_RUNTIME" in capsys.readouterr().out


def test_cli_requires_github_output_env(monkeypatch):
    monkeypatch.delenv("GITHUB_OUTPUT", raising=False)
    assert main(["--files", "docs/a.md", "--github-output"]) == 2
