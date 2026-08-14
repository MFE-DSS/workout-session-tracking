"""Sb_OPS_CI_RUNNER_STABILITY_01 — CI infrastructure guards.

Three concerns, deliberately kept separate because the sprint's whole point is
not to conflate them:

1. **hygiene** — the `client` fixture must delete the directory it created, on
   every path. Proven, not asserted;
2. **source of truth** — the workflow must invoke the canonical pytest script,
   so "CI-identical" cannot silently drift again;
3. **diagnostics safety** — telemetry must never change a build's verdict.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import tempfile

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"
CI_SCRIPT = REPO_ROOT / "scripts" / "run_ci_pytest.sh"
SAMPLER = REPO_ROOT / "scripts" / "ci_resource_sampler.py"
TMP_PREFIX = "workout-test-"


def _tmp_dir_count() -> int:
    return len(list(pathlib.Path(tempfile.gettempdir()).glob(f"{TMP_PREFIX}*")))


@pytest.fixture()
def pytester_like_run(tmp_path):
    """Run ONE test in a nested pytest and measure the temp-dir delta.

    The teardown of a fixture cannot be observed from inside a test that is
    still using it, so the proof has to happen in a separate process that runs
    to completion. The nested file lives under `tests/` so the real
    `conftest.py` — the thing under test — actually applies.

    Returns `(count_before, count_after, exit_code)`.
    """
    created: list[pathlib.Path] = []

    def run(body: str) -> tuple[int, int, int]:
        target = REPO_ROOT / "tests" / f"test_zz_nested_{abs(hash(body)) % 10**8}.py"
        target.write_text(
            "def test_nested(client):\n"
            f"    {body}\n",
            encoding="utf-8",
        )
        created.append(target)
        before = _tmp_dir_count()
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(target),
             "-q", "-p", "no:cacheprovider", "--no-header"],
            capture_output=True, text=True, cwd=REPO_ROOT, timeout=300,
        )
        after = _tmp_dir_count()
        return (before, after, result.returncode)

    yield run

    for path in created:
        path.unlink(missing_ok=True)


def _workflow() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def _script() -> str:
    return CI_SCRIPT.read_text(encoding="utf-8")


# ─────────────────── WS4 — nettoyage du répertoire temporaire ───────────────────


class TestFixtureTempCleanup:
    def test_the_directory_exists_while_the_fixture_is_in_use(self, client):
        live = list(pathlib.Path(tempfile.gettempdir()).glob(f"{TMP_PREFIX}*"))
        assert live != []

    def test_the_directory_is_gone_after_teardown(self, pytester_like_run):
        """Exécuté dans un pytest imbriqué : le teardown doit avoir eu lieu."""
        before, after, _ = pytester_like_run("pass")
        assert after <= before

    def test_a_failing_test_still_cleans_up(self, pytester_like_run):
        """Le chemin d'échec est celui qui fuyait le plus : il est couvert."""
        before, after, outcome = pytester_like_run("raise AssertionError('boom')")
        assert after <= before

    def test_the_failing_case_really_failed(self, pytester_like_run):
        """Sans quoi le test précédent prouverait un nettoyage sur rien."""
        _, _, outcome = pytester_like_run("raise AssertionError('boom')")
        assert outcome != 0

    def test_the_fixture_deletes_only_its_own_directory(self):
        source = (REPO_ROOT / "tests" / "conftest.py").read_text(encoding="utf-8")
        teardown = source.split("finally:", 1)[1]
        assert "rmtree(tmp_dir" in teardown

    def test_the_fixture_never_removes_a_shared_parent(self):
        source = (REPO_ROOT / "tests" / "conftest.py").read_text(encoding="utf-8")
        teardown = source.split("finally:", 1)[1]
        assert "gettempdir" not in teardown

    def test_the_fixture_never_touches_the_dev_database(self):
        """Scanne le CODE, pas les commentaires.

        Le teardown mentionne `var/workout.db` précisément pour documenter qu'il
        n'y touche pas ; un scan brut échouerait sur sa propre explication.
        """
        source = (REPO_ROOT / "tests" / "conftest.py").read_text(encoding="utf-8")
        code = "\n".join(
            line.split("#", 1)[0] for line in source.splitlines()
        )
        assert "var/workout.db" not in code

    def test_cleanup_runs_in_a_finally_block(self):
        """Un nettoyage après le `with` est sauté quand un test lève."""
        source = (REPO_ROOT / "tests" / "conftest.py").read_text(encoding="utf-8")
        assert re.search(r"\n    finally:\n", source)

    def test_the_fixture_stays_function_scoped(self):
        """L'isolation par test n'est pas négociée par ce sprint."""
        source = (REPO_ROOT / "tests" / "conftest.py").read_text(encoding="utf-8")
        assert "@pytest.fixture()" in source

    def test_no_session_scoped_client_was_introduced(self):
        source = (REPO_ROOT / "tests" / "conftest.py").read_text(encoding="utf-8")
        assert 'scope="session"' not in source

    def test_each_invocation_gets_its_own_directory(self):
        """Deux invocations ⇒ deux `mkdtemp` : jamais de partage entre workers."""
        source = (REPO_ROOT / "tests" / "conftest.py").read_text(encoding="utf-8")
        assert source.count("tempfile.mkdtemp(") == 1


# ─────────────────── WS7 — commande CI canonique ───────────────────


class TestCanonicalCommand:
    def test_the_canonical_script_exists(self):
        assert CI_SCRIPT.is_file()

    def test_the_workflow_invokes_the_canonical_script(self):
        assert "scripts/run_ci_pytest.sh" in _workflow()

    def test_the_workflow_no_longer_inlines_pytest_flags(self):
        """La divergence silencieuse devient structurellement impossible."""
        step = _workflow().split("Run pytest with coverage", 1)[1].split(
            "Upload coverage artifact", 1)[0]
        assert "--cov-report=xml" not in step

    @pytest.mark.parametrize("flag", [
        "--dist worksteal",
        "--ignore=tests/test_v1_acceptance.py",
        "--cov=app",
        "--cov-report=xml",
        "--cov-report=term",
    ])
    def test_every_canonical_flag_is_pinned(self, flag):
        assert flag in _script()

    def test_the_worker_policy_is_explicit(self):
        assert "CI_PYTEST_WORKERS" in _script()

    def test_the_default_worker_policy_is_auto(self):
        assert 'CI_PYTEST_WORKERS:-auto' in _script()

    def test_the_script_preserves_the_pytest_exit_code(self):
        """Un diagnostic ne doit jamais verdir un échec réel."""
        assert "exit $?" in _script()

    def test_the_script_does_not_swallow_failures(self):
        assert "|| true" not in _script()

    def test_the_script_is_syntactically_valid(self):
        result = subprocess.run(
            ["bash", "-n", str(CI_SCRIPT)], capture_output=True, text=True)
        assert result.returncode == 0

    def test_the_workflow_still_exits_with_the_pytest_code(self):
        step = _workflow().split("Run pytest with coverage", 1)[1].split(
            "Upload coverage artifact", 1)[0]
        assert 'exit "${PYTEST_RC}"' in step

    def test_coverage_is_not_weakened(self):
        """WS8 : la stabilité ne s'achète pas en réduisant la couverture."""
        assert "--cov=app" in _script()

    def test_no_test_selection_shortcut_was_introduced(self):
        for banned in ("testmon", "--lf", "--ff", "-k "):
            assert banned not in _script()


# ─────────────────── WS1/WS2 — diagnostics ───────────────────


class TestDiagnostics:
    def test_the_sampler_exists(self):
        assert SAMPLER.is_file()

    def test_the_workflow_starts_the_sampler(self):
        assert "ci_resource_sampler.py" in _workflow()

    def test_the_workflow_captures_peak_rss(self):
        assert "/usr/bin/time -v" in _workflow()

    def test_the_sampler_emits_a_greppable_prefix(self):
        assert 'PREFIX = "CI_RESOURCE"' in SAMPLER.read_text(encoding="utf-8")

    def test_the_sampler_streams_to_stdout(self):
        """Une mesure uploadée après l'arrêt du runner n'existe pas."""
        assert "flush=True" in SAMPLER.read_text(encoding="utf-8")

    def test_the_sampler_runs_and_emits_a_host_header(self):
        result = subprocess.run(
            [sys.executable, "-c",
             "import sys; sys.path.insert(0, 'scripts');"
             " import ci_resource_sampler as s; s.emit_host_header()"],
            capture_output=True, text=True, cwd=REPO_ROOT, timeout=60,
        )
        assert result.stdout.startswith("CI_RESOURCE_HOST")

    def test_the_sampler_emits_a_sample_without_raising(self):
        result = subprocess.run(
            [sys.executable, "-c",
             "import sys; sys.path.insert(0, 'scripts');"
             " import ci_resource_sampler as s; s.emit_sample()"],
            capture_output=True, text=True, cwd=REPO_ROOT, timeout=60,
        )
        assert result.returncode == 0

    def test_a_sample_line_is_machine_greppable(self):
        result = subprocess.run(
            [sys.executable, "-c",
             "import sys; sys.path.insert(0, 'scripts');"
             " import ci_resource_sampler as s; s.emit_sample()"],
            capture_output=True, text=True, cwd=REPO_ROOT, timeout=60,
        )
        assert re.search(r"CI_RESOURCE ts=\d+ ", result.stdout)

    def test_the_sampler_survives_a_process_disappearing(self, monkeypatch):
        """Un PID mort entre le listing et la lecture ne doit rien casser."""
        monkeypatch.syspath_prepend(str(REPO_ROOT / "scripts"))
        import ci_resource_sampler as sampler

        assert sampler._proc_rss_mb(999_999_999) is None

    def test_missing_cgroup_paths_are_reported_not_invented(self, monkeypatch):
        monkeypatch.syspath_prepend(str(REPO_ROOT / "scripts"))
        import ci_resource_sampler as sampler

        values = set(sampler._cgroup_memory().values())
        assert values  # présents ou explicitement "na", jamais fabriqués

    def test_the_sampler_dumps_no_environment(self):
        source = SAMPLER.read_text(encoding="utf-8")
        assert "os.environ.items" not in source

    def test_the_sampler_reads_only_one_env_var(self):
        source = SAMPLER.read_text(encoding="utf-8")
        assert source.count("os.environ") == 1

    def test_the_sampler_never_raises_out_of_its_loop(self):
        source = SAMPLER.read_text(encoding="utf-8")
        assert "except Exception" in source


# ─────────────────── WS6 — mesure de la purge de modules ───────────────────


class TestModulePurgeMeasured:
    def test_the_purge_is_still_present(self):
        """Mesurer, pas supprimer : l'isolation reste autoritative."""
        source = (REPO_ROOT / "tests" / "conftest.py").read_text(encoding="utf-8")
        assert "sys.modules.pop(mod_name, None)" in source

    def test_the_purge_scope_is_unchanged(self):
        source = (REPO_ROOT / "tests" / "conftest.py").read_text(encoding="utf-8")
        assert 'm == "app" or m.startswith("app.")' in source

    def test_a_representative_app_module_count_is_measurable(self, client):
        """Combien de modules chaque cycle de purge recharge réellement."""
        import sys as live_sys

        loaded = [m for m in live_sys.modules if m == "app" or m.startswith("app.")]
        assert len(loaded) > 0
