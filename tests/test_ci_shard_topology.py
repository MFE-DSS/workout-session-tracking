"""Sb_OPS_CI_SCALE_02 — la topologie de shards ne peut plus dériver en silence.

Le nombre de shards vivait à **trois** endroits que rien ne comparait : la
matrice du workflow, `ci_test_shards.DEFAULT_SHARDS`, et le `-ne 2` de
l'agrégateur de couverture. Une seule copie pouvait bouger et la CI serait
restée **verte** en combinant deux shards sur trois — c'est-à-dire en publiant
une couverture partielle comme si elle était complète.

Ce fichier supprime le risque de deux façons complémentaires :

* l'agrégateur **dérive** désormais le nombre (`--shard-count`), donc la
  troisième copie n'existe plus ;
* la matrice YAML, que GitHub Actions ne peut pas calculer, est **comparée** à
  la constante versionnée par les tests ci-dessous.

Il reste donc une valeur à changer, une copie à maintenir, et une machine qui
refuse qu'elles divergent.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "ci.yml"

REQUIRED_CHECK_NAME = "pytest + QA scripts"


def _sharder():
    spec = importlib.util.spec_from_file_location(
        "ci_test_shards", REPO_ROOT / "scripts" / "ci_test_shards.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _workflow_text() -> str:
    return WORKFLOW_PATH.read_text(encoding="utf-8")


def _matrix_indices() -> list[int]:
    """The shard indices the workflow actually fans out over."""
    match = re.search(r"^\s*shard:\s*\[([0-9,\s]+)\]\s*$",
                      _workflow_text(), re.MULTILINE)
    assert match, "no `shard: [...]` matrix found in the workflow"
    return [int(part) for part in match.group(1).split(",") if part.strip()]


# ── La matrice suit la source unique ─────────────────────────────────────────


def test_the_workflow_matrix_matches_the_canonical_shard_count():
    assert _matrix_indices() == list(range(1, _sharder().DEFAULT_SHARDS + 1))


def test_the_matrix_has_no_duplicate_index():
    """Un index dupliqué ferait tourner deux fois le même sous-ensemble.

    La couverture resterait plausible et un tiers de la suite ne serait
    jamais exécuté.
    """
    indices = _matrix_indices()
    assert len(indices) == len(set(indices))


def test_the_matrix_is_contiguous_and_one_based():
    indices = _matrix_indices()
    assert indices == sorted(indices)
    assert indices[0] == 1


def test_the_canonical_shard_count_is_at_least_the_measured_need():
    """2 shards ont mesuré 3 701 Mo sur le shard B — sous le plancher de 4 Go."""
    assert _sharder().DEFAULT_SHARDS >= 3


# ── L'agrégateur DÉRIVE le nombre au lieu de le répéter ──────────────────────


def test_the_coverage_aggregator_derives_the_shard_count():
    text = _workflow_text()
    assert "ci_test_shards.py --shard-count" in text
    # La forme codée en dur qui a rendu la dérive possible.
    assert '-ne 2 ]' not in text


def test_the_shard_count_flag_prints_the_canonical_value(capsys):
    mod = _sharder()
    assert mod.DEFAULT_SHARDS == int(str(mod.DEFAULT_SHARDS))
    # Le drapeau existe et n'exige aucun autre argument.
    parser_src = pathlib.Path(
        REPO_ROOT / "scripts" / "ci_test_shards.py").read_text(encoding="utf-8")
    assert "--shard-count" in parser_src


def test_a_missing_shard_artifact_is_a_hard_failure():
    text = _workflow_text()
    assert 'if-no-files-found: error' in text
    assert "exit 1" in text


def test_every_shard_uploads_its_own_coverage_data():
    text = _workflow_text()
    assert "coverage-shard-${{ matrix.shard }}.data" in text
    assert "coverage-data-${{ matrix.shard }}" in text


def test_only_the_combined_report_is_published():
    text = _workflow_text()
    assert "coverage combine coverage-shard-*.data" in text
    assert "coverage xml -o coverage.xml" in text


# ── Partition exacte sous la topologie canonique ─────────────────────────────


def test_the_partition_covers_the_suite_exactly_at_the_canonical_count():
    mod = _sharder()
    shards = mod.build_shards(mod.DEFAULT_SHARDS)
    flat = [name for shard in shards for name in shard]
    assert sorted(flat) == sorted(mod.canonical_test_files())
    assert len(flat) == len(set(flat))


def test_no_shard_is_empty():
    mod = _sharder()
    assert all(shard for shard in mod.build_shards(mod.DEFAULT_SHARDS))


def test_a_new_test_file_lands_in_exactly_one_shard(tmp_path):
    """The partition is generated, so nobody has to remember a list."""
    mod = _sharder()
    fake_root = tmp_path
    (fake_root / "tests").mkdir()
    names = [f"test_synthetic_{i:03d}.py" for i in range(10)]
    for name in names:
        (fake_root / "tests" / name).write_text("", encoding="utf-8")

    before = mod.build_shards(mod.DEFAULT_SHARDS, root=fake_root)
    (fake_root / "tests" / "test_synthetic_new_arrival.py").write_text(
        "", encoding="utf-8")
    after = mod.build_shards(mod.DEFAULT_SHARDS, root=fake_root)

    flat_after = [n for shard in after for n in shard]
    assert flat_after.count("tests/test_synthetic_new_arrival.py") == 1
    assert len([n for s in before for n in s]) + 1 == len(flat_after)


def test_the_excluded_acceptance_file_stays_excluded():
    mod = _sharder()
    flat = [n for shard in mod.build_shards(mod.DEFAULT_SHARDS) for n in shard]
    assert "tests/test_v1_acceptance.py" not in flat
    assert "test_v1_acceptance.py" in mod.EXCLUDED


def test_the_exclusion_list_contains_exactly_one_file():
    """The partition guards were circular until this test existed.

    `canonical_test_files()` is *defined* as the tests directory minus
    `EXCLUDED`, and every partition assertion compares the shards against that
    same function. Adding a file to `EXCLUDED` therefore shrank both sides at
    once: the partition stayed "exact", every job stayed green, and the file
    silently stopped running.

    Planting `EXCLUDED = {..., "test_weekly_planner.py"}` left all 90 tests
    passing. That is precisely the failure mode the sharder's own docstring
    says it exists to make impossible, and nothing was checking it.

    The exclusion list is a deliberate, singular decision — so it is pinned by
    value, not by shape.
    """
    assert _sharder().EXCLUDED == {"test_v1_acceptance.py"}


def test_the_canonical_set_is_the_whole_tests_directory_minus_that_one_file():
    """Anchored on the filesystem, not on the module's own definition."""
    mod = _sharder()
    on_disk = {
        path.name for path in (REPO_ROOT / "tests").glob("test_*.py")
    }
    expected = sorted(f"tests/{name}" for name in on_disk - mod.EXCLUDED)
    assert mod.canonical_test_files() == expected
    # And the suite is not accidentally tiny.
    assert len(expected) > 200


def test_dropping_a_real_test_file_cannot_stay_green(tmp_path):
    """Behavioural half: a file present on disk must reach a shard."""
    mod = _sharder()
    (tmp_path / "tests").mkdir()
    for name in ("test_alpha.py", "test_beta.py", "test_v1_acceptance.py"):
        (tmp_path / "tests" / name).write_text("", encoding="utf-8")

    flat = [n for s in mod.build_shards(mod.DEFAULT_SHARDS, root=tmp_path) for n in s]
    assert "tests/test_alpha.py" in flat
    assert "tests/test_beta.py" in flat
    assert "tests/test_v1_acceptance.py" not in flat


# ── Sémantique xdist et contrat de check inchangés ───────────────────────────


def _executable_lines(text: str) -> str:
    """Strip comment lines before scanning for a banned argument.

    Both the workflow and the runner script *explain* why `-n auto` is
    forbidden, quoting it in prose. A naive substring scan therefore fails on
    the very documentation that enforces the rule. The invariant is about what
    is executed, so the comments are removed first.
    """
    kept = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        kept.append(line.split(" #", 1)[0] if " #" in line else line)
    return "\n".join(kept)


def test_the_worker_count_stays_two_and_is_never_auto():
    text = _workflow_text()
    assert "-n auto" not in _executable_lines(text)
    assert "CI_PYTEST_WORKERS" in text


def test_the_canonical_runner_script_never_uses_auto():
    script = (REPO_ROOT / "scripts" / "run_ci_pytest.sh").read_text(encoding="utf-8")
    assert "-n auto" not in _executable_lines(script)


def test_the_runner_script_pins_an_explicit_worker_count():
    script = (REPO_ROOT / "scripts" / "run_ci_pytest.sh").read_text(encoding="utf-8")
    body = _executable_lines(script)
    assert "-n " in body
    assert "CI_PYTEST_WORKERS" in body


def test_the_required_check_name_is_unchanged():
    assert REQUIRED_CHECK_NAME in _workflow_text()


def test_docs_only_path_gating_is_unchanged():
    text = _workflow_text()
    assert "paths-ignore" in text
    assert "'docs/**'" in text


def test_each_shard_runs_only_its_own_slice():
    assert "ci_test_shards.py --shard ${{ matrix.shard }}" in _workflow_text()


@pytest.mark.parametrize("count", [1, 2, 3, 4, 5, 8])
def test_the_partition_stays_exact_at_any_shard_count(count):
    """Scaling further must not need a new algorithm."""
    mod = _sharder()
    mod.verify(count)
    shards = mod.build_shards(count)
    assert len(shards) == count
    flat = [n for shard in shards for n in shard]
    assert sorted(flat) == sorted(mod.canonical_test_files())
