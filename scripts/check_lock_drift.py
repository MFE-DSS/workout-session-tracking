"""Sb_DEPENDENCY_LOCK_AUTHORITY_01 — requirements.txt ↔ requirements-lock.txt.

WHY
---
`requirements-lock.txt` is now the file CI and the production VPS install from.
That only helps if it still corresponds to `requirements.txt`. Someone adding a
dependency to the source spec without regenerating the lock would get a green CI
that never installed their new package — a silent, confusing failure.

This check makes that impossible, and it does so **offline**: it compares the
declared specs against the pins already in the lock, without resolving anything.
A network resolution in CI would be slow, flaky, and would defeat the point of
having a lock at all.

WHAT IT DOES NOT CHECK
----------------------
It does not verify the lock is the *freshest* possible resolution — a newer
version of a transitive dependency existing on PyPI is not drift, it is just
time passing. Dependabot's job is to propose those; this check's job is to prove
the lock still satisfies the spec.

    python scripts/check_lock_drift.py
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "requirements.txt"
LOCK = ROOT / "requirements-lock.txt"
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"

#: Must match TARGET_PYTHON in scripts/regen_lockfile.sh and python-version in CI.
TARGET_PYTHON = "3.11"

#: `name[extra]>=1.2,<2` → name, specs. Anchored and character-class based:
#: no nested quantifiers, so no backtracking blow-up on a malformed line.
_REQ = re.compile(r"^([A-Za-z0-9_.\-]+)(\[[^\]]*\])?([<>=!~].*)?$")
_PIN = re.compile(r"^([A-Za-z0-9_.\-]+)==([^\s;]+)", re.M)
_CLAUSE = re.compile(r"^(>=|<=|==|!=|~=|>|<)([^\s]+)$")


def _normalise(name: str) -> str:
    """PEP 503: names compare case-insensitively with -_. equivalent."""
    return re.sub(r"[-_.]+", "-", name).lower()


def _source_requirements() -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in SOURCE.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        match = _REQ.match(line.replace(" ", ""))
        if match:
            out[_normalise(match.group(1))] = match.group(3) or ""
    return out


def _lock_pins() -> dict[str, str]:
    return {
        _normalise(name): version
        for name, version in _PIN.findall(LOCK.read_text(encoding="utf-8"))
    }


def _version_tuple(version: str) -> tuple:
    return tuple(int(p) if p.isdigit() else p for p in re.split(r"[.\-+]", version))


#: Enough of PEP 440 for the operators this repo actually uses. A table rather
#: than a chain of `if`s: the chain read as seven near-identical negations and
#: Sonar was right that it was harder to check than it needed to be.
_COMPARATORS = {
    ">=": lambda left, right: left >= right,
    ">": lambda left, right: left > right,
    "<=": lambda left, right: left <= right,
    "<": lambda left, right: left < right,
    "==": lambda left, right: left == right,
    "!=": lambda left, right: left != right,
    # `~=X.Y` means ">=X.Y, ==X.*"; the lower bound is what matters here.
    "~=": lambda left, right: left >= right,
}


def _satisfies(version: str, specs: str) -> bool:
    if not specs:
        return True
    for raw in specs.split(","):
        match = _CLAUSE.match(raw.strip())
        if match is None:
            continue
        compare = _COMPARATORS.get(match.group(1))
        try:
            if compare and not compare(_version_tuple(version), _version_tuple(match.group(2))):
                return False
        except TypeError:  # pragma: no cover - mixed str/int version parts
            return False
    return True


def check() -> list[str]:
    """Return a list of blocking problems; empty means the lock is coherent."""
    problems: list[str] = []

    if not LOCK.is_file():
        return ["requirements-lock.txt est absent — lance scripts/regen_lockfile.sh"]

    source, pins = _source_requirements(), _lock_pins()
    if not pins:
        return ["requirements-lock.txt ne contient aucun paquet épinglé"]

    for name, specs in sorted(source.items()):
        pinned = pins.get(name)
        if pinned is None:
            problems.append(
                f"{name} est déclaré dans requirements.txt mais absent du lock — "
                f"régénère avec scripts/regen_lockfile.sh"
            )
        elif not _satisfies(pinned, specs):
            problems.append(
                f"{name}=={pinned} dans le lock ne satisfait pas « {name}{specs} » "
                f"de requirements.txt — régénère le lock"
            )

    # The lock carries no environment markers, so it is only valid for the
    # interpreter that produced it. Keep that interpreter aligned with CI.
    ci = CI_WORKFLOW.read_text(encoding="utf-8")
    declared = set(re.findall(r'python-version:\s*"([^"]+)"', ci))
    if declared and declared != {TARGET_PYTHON}:
        problems.append(
            f"la CI déclare Python {sorted(declared)} alors que le lock cible "
            f"{TARGET_PYTHON} — aligne TARGET_PYTHON ou la CI"
        )

    return problems


def main() -> int:
    print("=== lock drift check ===")
    print(f"  source : {SOURCE.name}")
    print(f"  lock   : {LOCK.name}")
    print(f"  cible  : Python {TARGET_PYTHON}")

    problems = check()
    if problems:
        print(f"\nFOUND {len(problems)} problème(s) :")
        for problem in problems:
            print(f"  ✗ {problem}")
        return 1

    pins = _lock_pins()
    print(f"\nOK: {len(_source_requirements())} dépendances déclarées, "
          f"{len(pins)} paquets épinglés, aucune dérive.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
