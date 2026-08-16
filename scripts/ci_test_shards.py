"""Deterministic test-file sharding for CI (Sb_OPS_CI_SCALE_01).

The suite needs more memory than one hosted runner has: measured at
**~4,4 MB per test** over 3 861 tests ≈ **16,6 GB** against a **15,99 GB**
machine. That deficit is invariant to the xdist worker count — fewer workers
simply run more tests each and hold the same total. The only way under the
ceiling without dropping coverage is to run fewer tests **per machine**.

**Partitioning is at TEST FILE granularity, never finer.** Several modules in
this suite are state-sensitive: `tests/conftest.py::client` purges `app.*` from
`sys.modules` per test, and files carry their own module-level fixtures and
ordering assumptions. Splitting one file across two shards would break
guarantees that took several sprints to establish.

**The manifest is generated from the repository, not maintained by hand.**
Files are sorted by name — a stable key that does not depend on the filesystem,
the clock, or test durations — then dealt round-robin. A new test file lands in
a shard automatically, so nobody has to remember to update a list, and the
assignment is reproducible on any machine.

Two invariants are enforced here AND pinned by tests:

* ``union(shards) == canonical test-file set``   — nothing silently dropped
* ``intersection(shards) == empty``              — nothing run twice

Dropping a file would quietly reduce coverage while every job stayed green;
that is the failure mode this module exists to make impossible.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

#: Excluded from CI exactly as the canonical command excludes it: it exercises a
#: local VSCode setup. Kept in one place so the shard set and the canonical
#: command cannot disagree about what "the suite" means.
EXCLUDED = {"test_v1_acceptance.py"}

#: **Source unique et versionnée du nombre de shards.**
#:
#: Sb_OPS_CI_SCALE_02 — 2 → 3. Le nombre vivait auparavant à *trois* endroits
#: (matrice du workflow, ce constant, et le `-ne 2` de l'agrégateur de
#: couverture) : trois copies qu'aucune machine ne comparait. Une seule pouvait
#: bouger et la CI serait restée verte en publiant une couverture partielle.
#:
#: Désormais l'agrégateur **dérive** ce nombre (`--shard-count`) au lieu de le
#: répéter, et un test structurel compare la matrice YAML à cette constante.
#: Il reste donc une seule valeur à changer, et une seule copie — la matrice —
#: que le YAML ne peut pas calculer, mais qu'un test refuse de laisser diverger.
#:
#: Motif du passage à 3 : le shard B est descendu à **3 701 Mo** de
#: MemAvailable (plancher `HEALTHY` = 4 Go), après 5 065 → 4 772 → 4 380 →
#: 3 701 sur quatre tranches. Le goulet est la mémoire par machine, pas la
#: correction ni la couverture : moins de tests par machine, mêmes tests au
#: total.
DEFAULT_SHARDS = 3


def repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parent.parent


def canonical_test_files(root: pathlib.Path | None = None) -> list[str]:
    """Every test file CI runs, sorted. The single definition of "the suite"."""
    base = (root or repo_root()) / "tests"
    names = sorted(
        path.name
        for path in base.glob("test_*.py")
        if path.name not in EXCLUDED
    )
    return [f"tests/{name}" for name in names]


def build_shards(
    shard_count: int = DEFAULT_SHARDS, root: pathlib.Path | None = None
) -> list[list[str]]:
    """Deal the sorted files round-robin into `shard_count` buckets.

    Round-robin rather than contiguous blocks: file *size* is a poor proxy for
    runtime, and alphabetical blocks would cluster related — hence similarly
    slow — modules into the same shard. Dealing spreads them.
    """
    if shard_count < 1:
        raise ValueError(f"shard_count must be >= 1, got {shard_count}")
    files = canonical_test_files(root)
    shards: list[list[str]] = [[] for _ in range(shard_count)]
    for index, name in enumerate(files):
        shards[index % shard_count].append(name)
    return shards


def shard_for(
    index: int, shard_count: int = DEFAULT_SHARDS, root: pathlib.Path | None = None
) -> list[str]:
    """Files for a 1-based shard index, as the CI matrix addresses them."""
    if not 1 <= index <= shard_count:
        raise ValueError(f"shard index {index} outside 1..{shard_count}")
    return build_shards(shard_count, root)[index - 1]


def verify(shard_count: int = DEFAULT_SHARDS, root: pathlib.Path | None = None) -> None:
    """Raise unless the partition is exact. Called by CI before running."""
    expected = set(canonical_test_files(root))
    shards = build_shards(shard_count, root)

    seen: set[str] = set()
    for position, shard in enumerate(shards, start=1):
        overlap = seen & set(shard)
        if overlap:
            raise AssertionError(
                f"shard {position} repeats files already assigned: {sorted(overlap)}"
            )
        seen |= set(shard)

    missing = expected - seen
    if missing:
        raise AssertionError(f"files assigned to no shard: {sorted(missing)}")
    extra = seen - expected
    if extra:
        raise AssertionError(f"files assigned but not in the suite: {sorted(extra)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shard", type=int, help="1-based shard index to print")
    parser.add_argument("--count", type=int, default=DEFAULT_SHARDS)
    parser.add_argument("--verify", action="store_true")
    # Laisse la CI DÉRIVER le nombre de shards au lieu de le répéter. C'est ce
    # qui supprime la troisième copie du chiffre (l'assertion de couverture).
    parser.add_argument(
        "--shard-count", action="store_true",
        help="print the canonical shard count and exit",
    )
    args = parser.parse_args()

    if args.shard_count:
        print(DEFAULT_SHARDS)
        return 0

    verify(args.count)
    if args.verify:
        total = len(canonical_test_files())
        sizes = [len(s) for s in build_shards(args.count)]
        print(f"[shards] {total} files -> {args.count} shards {sizes}: partition exact")
        return 0

    if args.shard is None:
        parser.error("pass --shard N or --verify")
    print(" ".join(shard_for(args.shard, args.count)))
    return 0


if __name__ == "__main__":  # pragma: no cover - entry point
    sys.exit(main())
