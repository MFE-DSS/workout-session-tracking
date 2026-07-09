"""Sb_OPS.scope-guard — tests du classifieur anti-overcheck.

Verrouille la logique de `scripts/check_scope.py` : la classification en
tiers doit rester déterministe et conservative (précédence
migration > ci_infra > shared_code > isolated > docs), et le tier `isolated`
doit bien autoriser à SKIPPER le full sweep local (le point de la feature).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def _load(name: str):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _classify(files: list[str]) -> str:
    mod = _load("check_scope")
    return mod.classify(files, mod._load_policy())["tier"]


# ───────── tier classification ─────────


def test_docs_only_is_docs_tier():
    assert _classify(["docs/SPRINT_X.md", "docs/strategy/SPEC_REGISTRY.md"]) == "docs"


def test_migration_files_are_migration_tier():
    assert _classify(["migrations/versions/foo.py"]) == "migration"
    assert _classify(["app/models/bar.py"]) == "migration"
    assert _classify(["data/schema_snapshot.sql"]) == "migration"


def test_ci_infra_files_are_ci_infra_tier():
    assert _classify([".github/workflows/ci.yml"]) == "ci_infra"
    assert _classify(["scripts/check_scope.py"]) == "ci_infra"
    assert _classify(["requirements.txt"]) == "ci_infra"


def test_shared_code_when_modified_file_imported_elsewhere():
    # muscle_mapping is imported by many consumers → shared.
    assert _classify(["app/services/muscle_mapping.py"]) == "shared_code"


def test_isolated_when_new_leaf_file_not_imported_anywhere():
    # body_map_descriptor exists but is not imported by any app/ module yet.
    assert _classify(["app/services/body_map_descriptor.py"]) == "isolated"


def test_isolated_tier_allows_skipping_full_sweep():
    """The whole point of the guard: an isolated diff must NOT require a
    local full sweep."""
    mod = _load("check_scope")
    policy = mod._load_policy()
    isolated = policy["tiers"]["isolated"]
    assert "full_sweep_local" in isolated.get("skip", [])
    assert "full_sweep_local" not in isolated["required_local_checks"]
    assert "broad_sweep_scoped" in isolated["required_local_checks"]


# ───────── precedence (conservative: never downgrade) ─────────


def test_precedence_migration_wins_over_isolated():
    # A diff with both a new leaf AND a migration must classify as migration.
    assert _classify(["app/services/new_leaf.py", "migrations/versions/x.py"]) == "migration"


def test_precedence_shared_wins_over_docs():
    assert _classify(["app/services/muscle_mapping.py", "docs/X.md"]) == "shared_code"


def test_docs_tier_requires_only_spec_protocol():
    mod = _load("check_scope")
    policy = mod._load_policy()
    docs = policy["tiers"]["docs"]
    assert docs["required_local_checks"] == ["check_spec_protocol"]
    assert "full_sweep" in docs.get("skip", [])
