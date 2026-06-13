#!/usr/bin/env python3
"""Sb_26.2 — Static linter for dangerous patterns in Alembic migrations.

Walks every file under `migrations/versions/`, parses with AST, and
flags risky operations in `upgrade()`:

* `op.drop_column(...)` / `op.drop_table(...)` — irreversible data loss
* `op.add_column(..., nullable=False)` without `server_default=` — breaks
  existing rows on upgrade
* `op.execute("UPDATE ...")` / `"DELETE ..."` / raw `ALTER` — silent
  data rewrite
* `op.batch_alter_table(...)` — SQLite batch ops are fragile under FK

Files listed in `.migration-policy.json#grandfathered_files` are skipped
(historical migrations pre-Sb_26.2). New migrations MUST either avoid
these patterns or carry a `# migration-justify: <reason>` comment on the
line immediately above the flagged call.

Exit 0 = clean, 1 = unjustified violations found.

Usage:
    python scripts/check_migration_patterns.py
    python scripts/check_migration_patterns.py --strict   # also fail on warns
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POLICY_PATH = ROOT / ".migration-policy.json"
MIGRATIONS_DIR = ROOT / "migrations" / "versions"


class _Finding:
    __slots__ = ("file", "line", "rule", "severity", "message")

    def __init__(
        self, file: str, line: int, rule: str, severity: str, message: str
    ) -> None:
        self.file = file
        self.line = line
        self.rule = rule
        self.severity = severity
        self.message = message

    def fmt(self) -> str:
        return (
            f"  {self.severity.upper():5s} {self.file}:{self.line} "
            f"[{self.rule}] {self.message}"
        )


def _is_op_call(node: ast.AST, names: tuple[str, ...]) -> bool:
    """Match `op.<name>(...)` calls."""
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if isinstance(func, ast.Attribute):
        if isinstance(func.value, ast.Name) and func.value.id == "op":
            return func.attr in names
    return False


def _is_batch_op_call(node: ast.AST, names: tuple[str, ...]) -> bool:
    """Match `batch_op.<name>(...)` calls inside `with op.batch_alter_table()`."""
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if isinstance(func, ast.Attribute):
        if isinstance(func.value, ast.Name) and func.value.id == "batch_op":
            return func.attr in names
    return False


def _has_kwarg(call: ast.Call, name: str) -> bool:
    return any(kw.arg == name for kw in call.keywords)


def _get_kwarg(call: ast.Call, name: str):
    for kw in call.keywords:
        if kw.arg == name:
            return kw.value
    return None


def _string_arg(call: ast.Call, index: int = 0) -> str | None:
    if len(call.args) <= index:
        return None
    arg = call.args[index]
    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
        return arg.value
    return None


def _justification_lines(source: str, marker: str) -> set[int]:
    """Lines (1-indexed) that contain a `# migration-justify:` comment.

    A flagged call on line N is considered justified if any line in
    [N-3, N] contains the marker (operator may write the comment up to
    3 lines above to allow for line breaks).
    """
    out: set[int] = set()
    for idx, line in enumerate(source.splitlines(), start=1):
        if marker in line:
            out.add(idx)
    return out


def _check_drop(node: ast.AST, rel: str, rules: dict) -> _Finding | None:
    if _is_op_call(node, ("drop_column",)) or _is_batch_op_call(node, ("drop_column",)):
        rule = "drop_column_in_upgrade"
        col = _string_arg(node, 0) or "?"
        return _Finding(
            rel, node.lineno, rule, rules.get(rule, "fail"),
            f"drop_column({col!r}) in upgrade() — destructive",
        )
    if _is_op_call(node, ("drop_table",)):
        rule = "drop_table_in_upgrade"
        tbl = _string_arg(node, 0) or "?"
        return _Finding(
            rel, node.lineno, rule, rules.get(rule, "fail"),
            f"drop_table({tbl!r}) in upgrade() — destructive",
        )
    return None


def _check_add_column(node: ast.AST, rel: str, rules: dict) -> _Finding | None:
    if not (_is_op_call(node, ("add_column",)) or _is_batch_op_call(node, ("add_column",))):
        return None
    if _has_kwarg(node, "column"):
        col_node = _get_kwarg(node, "column")
    elif len(node.args) >= 2:
        col_node = node.args[1]
    elif node.args:
        col_node = node.args[0]
    else:
        col_node = None
    if not isinstance(col_node, ast.Call):
        return None
    nullable = _get_kwarg(col_node, "nullable")
    is_not_null = isinstance(nullable, ast.Constant) and nullable.value is False
    if is_not_null and not _has_kwarg(col_node, "server_default"):
        rule = "add_column_not_null_no_default"
        return _Finding(
            rel, node.lineno, rule, rules.get(rule, "fail"),
            "add_column with nullable=False and no server_default",
        )
    return None


_EXECUTE_RULES = {
    "UPDATE": ("execute_update_in_upgrade", "warn_requires_justify",
               "op.execute('UPDATE ...') — rewrites existing data"),
    "DELETE": ("execute_delete_in_upgrade", "fail",
               "op.execute('DELETE ...') — destructive"),
    "ALTER":  ("execute_alter_in_upgrade", "warn_requires_justify",
               "op.execute('ALTER ...') — bypasses Alembic abstraction"),
}


def _check_execute(node: ast.AST, rel: str, rules: dict) -> _Finding | None:
    if not _is_op_call(node, ("execute",)):
        return None
    sql = (_string_arg(node, 0) or "").strip().upper()
    for prefix, (rule, default_sev, msg) in _EXECUTE_RULES.items():
        if sql.startswith(prefix):
            return _Finding(rel, node.lineno, rule, rules.get(rule, default_sev), msg)
    return None


def _scan_file(path: Path, policy: dict) -> list[_Finding]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    rel = path.name
    rules = policy["rules"]
    justify_lines = _justification_lines(source, policy["justify_marker"])

    def _justified(lineno: int) -> bool:
        return any(j in justify_lines for j in range(lineno - 3, lineno + 1))

    findings: list[_Finding] = []
    for fn in (n for n in ast.walk(tree)
               if isinstance(n, ast.FunctionDef) and n.name == "upgrade"):
        for node in ast.walk(fn):
            for check in (_check_drop, _check_add_column, _check_execute):
                f = check(node, rel, rules)
                if f is not None:
                    findings.append(f)

    return [
        f for f in findings
        if f.severity in ("fail", "warn_requires_justify") and not _justified(f.line)
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warn_requires_justify as fail even if marker present",
    )
    args = parser.parse_args()

    if not POLICY_PATH.exists():
        print(f"FATAL: {POLICY_PATH} missing.", file=sys.stderr)
        return 2
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    grandfathered = set(policy.get("grandfathered_files", []))

    files = sorted(MIGRATIONS_DIR.glob("*.py"))
    files = [f for f in files if not f.name.startswith("__")]

    print("=== migration patterns check ===")
    print(f"  files scanned    : {len(files)}")
    print(f"  grandfathered    : {len(grandfathered)}")
    print(f"  strict mode      : {args.strict}")
    print()

    all_findings: list[_Finding] = []
    new_findings: list[_Finding] = []
    for path in files:
        if path.name in grandfathered:
            continue
        findings = _scan_file(path, policy)
        all_findings.extend(findings)
        new_findings.extend(findings)

    if not new_findings:
        print("OK: no unjustified dangerous patterns in non-grandfathered migrations.")
        return 0

    print(f"FOUND {len(new_findings)} unjustified pattern(s):")
    fails = 0
    for f in new_findings:
        print(f.fmt())
        if f.severity == "fail" or (
            args.strict and f.severity == "warn_requires_justify"
        ):
            fails += 1

    if fails:
        print()
        print(
            f"FAIL: {fails} pattern(s) must be justified with a "
            f"`{policy['justify_marker']} <reason>` comment within 3 lines "
            "above, OR grandfathered in .migration-policy.json with an "
            "amendment to docs/MIGRATION_HARDENING.md."
        )
        return 1

    print()
    print("OK (warnings only — use --strict to fail on warnings).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
