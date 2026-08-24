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

import hashlib
import os
import pathlib
import re
import subprocess
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"
CI_SCRIPT = REPO_ROOT / "scripts" / "run_ci_pytest.sh"
SAMPLER = REPO_ROOT / "scripts" / "ci_resource_sampler.py"
TMP_PREFIX = "workout-test-"


def _tmp_dir_count(root: pathlib.Path) -> int:
    """Compte les répertoires du fixture **dans la racine passée**.

    La racine est celle que le test POSSÈDE, jamais le répertoire temporaire
    partagé de la machine — voir `pytester_like_run`.
    """
    return len(list(root.glob(f"{TMP_PREFIX}*")))


@pytest.fixture()
def pytester_like_run(tmp_path):
    """Run ONE test in a nested pytest and measure the temp-dir delta.

    The teardown of a fixture cannot be observed from inside a test that is
    still using it, so the proof has to happen in a separate process that runs
    to completion. The nested file lives under `tests/` so the real
    `conftest.py` — the thing under test — actually applies.

    **La mesure est confinée à une racine temporaire appartenant au test**
    (`Sb_CI_TMPSTATE_FLAKE_01`). Auparavant elle comptait les
    `workout-test-*` de `tempfile.gettempdir()` — un emplacement **partagé par
    toute la machine**, contenant ici plus de 53 000 répertoires hérités et
    alimenté en parallèle par les autres workers xdist. Il suffisait qu'un
    worker voisin crée son répertoire entre les deux relevés pour que
    `after > before` sans le moindre défaut : le test échantillonnait un état
    global.

    Le sous-processus reçoit donc `TMPDIR` pointant sur `tmp_path`, que pytest
    alloue par test **et par worker**. `tempfile.mkdtemp` du fixture `client`
    l'honore, si bien que les répertoires observés sont exactement ceux que ce
    test a provoqués — aucun autre worker ne peut y écrire.

    Returns `(count_before, count_after, exit_code)`.
    """
    created: list[pathlib.Path] = []
    owned_tmp = tmp_path / "owned-tmp"
    owned_tmp.mkdir()

    def run(body: str) -> tuple[int, int, int]:
        # Nom dérivé du contenu ET de la racine possédée : deux workers
        # exécutant le même corps n'écrivent pas dans le même fichier.
        # `hash()` est randomisé par processus, donc inutilisable comme
        # identité stable entre workers.
        stem = hashlib.sha256(
            f"{owned_tmp}|{body}".encode()).hexdigest()[:12]
        target = REPO_ROOT / "tests" / f"test_zz_nested_{stem}.py"
        target.write_text(
            "def test_nested(client):\n"
            f"    {body}\n",
            encoding="utf-8",
        )
        created.append(target)
        env = {**os.environ, "TMPDIR": str(owned_tmp)}
        before = _tmp_dir_count(owned_tmp)
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(target),
             "-q", "-p", "no:cacheprovider", "--no-header"],
            capture_output=True, text=True, cwd=REPO_ROOT, timeout=300,
            env=env,
        )
        after = _tmp_dir_count(owned_tmp)
        return (before, after, result.returncode)

    yield run

    for path in created:
        path.unlink(missing_ok=True)


CONFTEST = REPO_ROOT / "tests" / "conftest.py"


def _read(path: pathlib.Path) -> str:
    """Un seul point de lecture — évite de répéter l'encodage partout."""
    return path.read_text(encoding="utf-8")


def _workflow() -> str:
    return _read(WORKFLOW)


def _script() -> str:
    return _read(CI_SCRIPT)


# ─────────────────── WS4 — nettoyage du répertoire temporaire ───────────────────


class TestFixtureTempCleanup:
    def test_the_directory_exists_while_the_fixture_is_in_use(self, client):
        """Le répertoire de CETTE invocation, pas « au moins un quelque part ».

        La version précédente cherchait un `workout-test-*` n'importe où dans le
        répertoire temporaire de la machine. Avec les dizaines de milliers de
        répertoires hérités qui y traînent, elle passait même si le fixture
        n'avait rien créé : une assertion vacante, du même défaut que la course
        corrigée par `Sb_CI_TMPSTATE_FLAKE_01`.

        Le fixture publie son chemin exact via `DATABASE_URL` ; on interroge
        celui-là.
        """
        db_url = os.environ["DATABASE_URL"]
        db_path = pathlib.Path(db_url.replace("sqlite:///", "", 1))
        owned = db_path.parent

        assert owned.name.startswith(TMP_PREFIX), (
            f"le fixture n'utilise pas le préfixe attendu : {owned.name}"
        )
        assert owned.is_dir(), "le répertoire de ce fixture n'existe pas"

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

    def test_the_measurement_never_reads_the_shared_temp_root(self):
        """Garde structurelle contre le retour de la course.

        Le défaut n'était pas une malchance : le test comptait les
        `workout-test-*` de `tempfile.gettempdir()`, un emplacement **partagé
        par toute la machine** (plus de 53 000 répertoires hérités y traînent)
        et alimenté en parallèle par les autres workers xdist. Un voisin créant
        son répertoire entre les deux relevés suffisait à faire `after > before`.

        La mesure lit désormais une racine que le test **possède**. Ce test
        empêche quiconque de la reconnecter à la racine partagée.
        """
        source = _read(pathlib.Path(__file__))
        measurement = source.split("def _tmp_dir_count", 1)[1].split("\n\n\n", 1)[0]
        assert "gettempdir" not in measurement, (
            "la mesure est revenue sur le répertoire temporaire partagé"
        )

    def test_the_nested_run_gets_an_owned_temp_root(self):
        """Le sous-processus écrit dans `tmp_path`, alloué par test ET par worker."""
        source = _read(pathlib.Path(__file__))
        fixture = source.split("def pytester_like_run", 1)[1].split(
            "\n\nCONFTEST", 1)[0]
        assert 'TMPDIR' in fixture
        assert "owned_tmp" in fixture

    def test_two_owned_roots_cannot_observe_each_other(self, tmp_path):
        """Deux workers ne peuvent pas voir l'état temporaire l'un de l'autre.

        Reproduit la course exacte : une création « étrangère » dans la racine
        partagée pendant qu'on observe une racine possédée.
        """
        import tempfile as _tempfile

        owned_a = tmp_path / "a"
        owned_b = tmp_path / "b"
        owned_a.mkdir()
        owned_b.mkdir()

        (owned_a / f"{TMP_PREFIX}aaa").mkdir()
        before_b = _tmp_dir_count(owned_b)
        # Un « autre worker » crée le sien, dans la racine partagée.
        foreign = _tempfile.mkdtemp(prefix=TMP_PREFIX)
        try:
            assert _tmp_dir_count(owned_b) == before_b, (
                "une création étrangère est visible depuis une racine possédée"
            )
            assert _tmp_dir_count(owned_a) == 1
        finally:
            pathlib.Path(foreign).rmdir()

    def test_the_nested_file_name_is_stable_across_processes(self):
        """`hash()` est randomisé par processus : il ne peut pas nommer un fichier
        partagé entre workers. Le nom dérive donc d'un digest stable."""
        source = _read(pathlib.Path(__file__))
        fixture = source.split("def pytester_like_run", 1)[1].split(
            "\n\nCONFTEST", 1)[0]
        assert "hashlib.sha256" in fixture
        assert "abs(hash(" not in fixture

    def test_the_suite_is_not_serialized_to_hide_the_race(self):
        """Le correctif rend l'invariant déterministe — il ne masque rien.

        Ni `-p no:xdist`, ni `xfail`, ni marqueur `flaky`, ni sleep, ni retry.
        """
        source = _read(pathlib.Path(__file__))
        # Exclure le corps de CE test : il cite forcément les motifs qu'il
        # interdit, et un scan brut échouerait sur sa propre liste.
        marker = "def test_the_suite_is_not_serialized_to_hide_the_race"
        scanned = source.split(marker, 1)[0] + source.split(marker, 1)[1].split(
            "\n    def ", 1)[-1]
        for banned in ("no:xdist", "flaky", "xfail", "time.sleep",
                       "reruns", "--forked"):
            assert banned not in scanned, f"contournement détecté : {banned!r}"

    def test_the_fixture_deletes_only_its_own_directory(self):
        source = _read(CONFTEST)
        teardown = source.split("finally:", 1)[1]
        assert "rmtree(tmp_dir" in teardown

    def test_the_fixture_never_removes_a_shared_parent(self):
        source = _read(CONFTEST)
        teardown = source.split("finally:", 1)[1]
        assert "gettempdir" not in teardown

    def test_the_fixture_never_touches_the_dev_database(self):
        """Scanne le CODE, pas les commentaires.

        Le teardown mentionne `var/workout.db` précisément pour documenter qu'il
        n'y touche pas ; un scan brut échouerait sur sa propre explication.
        """
        source = _read(CONFTEST)
        code = "\n".join(
            line.split("#", 1)[0] for line in source.splitlines()
        )
        assert "var/workout.db" not in code

    def test_cleanup_runs_in_a_finally_block(self):
        """Un nettoyage après le `with` est sauté quand un test lève."""
        source = _read(CONFTEST)
        assert re.search(r"\n    finally:\n", source)

    def test_the_fixture_stays_function_scoped(self):
        """L'isolation par test n'est pas négociée par ce sprint."""
        source = _read(CONFTEST)
        assert "@pytest.fixture()" in source

    def test_no_session_scoped_client_was_introduced(self):
        source = _read(CONFTEST)
        assert 'scope="session"' not in source

    def test_each_invocation_gets_its_own_directory(self):
        """Deux invocations ⇒ deux `mkdtemp` : jamais de partage entre workers."""
        source = _read(CONFTEST)
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

    def test_the_default_worker_policy_is_bounded(self):
        """`-n auto` (4 workers) exhausted the runner — the bound is the fix.

        Pinned as a value, not a range: an accidental return to `auto` would
        silently reintroduce the memory pressure that caused three shutdowns.
        """
        assert 'CI_PYTEST_WORKERS:-2' in _script()

    def test_the_worker_bound_is_justified_in_the_script(self):
        """The number must travel with the measurement that produced it."""
        assert "MemAvailable" in _script()

    def test_a_non_numeric_worker_count_is_refused(self):
        """`Sb_OPS_LOCAL_SWEEP_CEILING_01` — la prose n'a pas suffi.

        Le littéral `auto` a déjà rendu une mitigation invisible : la variable
        était *définie*, donc le `:-2` ne jouait pas, et un run de validation
        est passé au vert sans exécuter la mitigation. Le script doit
        s'ARRÊTER sur une valeur non entière, pas la transmettre à pytest.
        """
        # ⚠ `ALLOW_LOCAL_CI_SWEEP` est indispensable depuis
        # `Sb_OPS_LOCAL_SWEEP_MEMORY_01` : sans lui le script refuse d'abord
        # parce qu'on est hors CI, et cette garde passerait en vérifiant le
        # MAUVAIS refus. Les deux messages contiennent « REFUS » ; on asserte
        # donc celui qui est propre à la valeur non entière.
        out = subprocess.run(
            ["bash", str(CI_SCRIPT), "--collect-only"],
            env={**os.environ, "CI_PYTEST_WORKERS": "auto",
                 "ALLOW_LOCAL_CI_SWEEP": "1"},
            capture_output=True, text=True, cwd=str(REPO_ROOT),
        )
        assert out.returncode == 2, out.stdout[-400:] + out.stderr[-400:]
        assert "n'est pas un entier" in out.stderr
        assert "-n auto" not in out.stdout

    def test_the_local_worker_count_is_capped_by_physical_ram(self):
        """Hors CI, un `-n` trop grand doit être RAMENÉ, pas obéi.

        La suite consomme ~4,4 Mo par test, ~16,6 Go au total. Sur un poste de
        développement, un worker par cœur fait partir la machine en swap et
        emporte ce qui tourne à côté — conteneurs compris. Vécu trois fois le
        2026-08-19.

        Le plafond est vérifié par le COMPORTEMENT du script, pas par la
        présence d'un commentaire : c'est précisément une règle écrite en
        prose qui a été enfreinte.
        """
        # `ALLOW_LOCAL_CI_SWEEP` : depuis `Sb_OPS_LOCAL_SWEEP_MEMORY_01`, le
        # script refuse purement et simplement hors CI. Ce plafond reste utile
        # pour ce diagnostic délibéré, et cette garde doit donc l'atteindre.
        env = {**os.environ, "CI_PYTEST_WORKERS": "64",
               "ALLOW_LOCAL_CI_SWEEP": "1"}
        env.pop("CI", None)
        out = subprocess.run(
            ["bash", str(CI_SCRIPT), "--collect-only", "-q"],
            env=env, capture_output=True, text=True, cwd=str(REPO_ROOT),
        )
        match = re.search(r"\[ci-pytest\] workers=(\d+)", out.stdout)
        assert match, out.stdout[-400:] + out.stderr[-400:]
        assert int(match.group(1)) < 64, "le plafond local n'a pas été appliqué"
        assert "ramenés à" in out.stderr

    def test_the_ci_policy_is_not_touched_by_the_local_cap(self):
        """Le plafond local ne doit pas réécrire la politique du runner : le
        chiffre de CI a été mesuré SUR le runner, pas déduit d'un poste."""
        script = _script()
        cap = script[script.find("if [[ -z \"${CI:-}\" ]]"):]
        assert cap, "le plafond local a disparu"
        assert "CI:-" in script, "le plafond doit être conditionné à l'absence de CI"

    def test_the_repo_contract_no_longer_prescribes_n_auto(self):
        """`CLAUDE.md §1` prescrivait `pytest -n auto` à la main, en
        contradiction avec son propre script canonique. C'est cette ligne qui
        a été exécutée, trois fois, sur le poste de l'opérateur."""
        contract = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        assert "run_ci_pytest.sh" in contract, (
            "le contrat doit pointer le script, pas une commande recopiée"
        )
        assert "`pytest -n auto --dist worksteal" not in contract

    def test_the_workflow_does_not_override_the_canonical_default(self):
        """A literal default in the workflow silently defeats the script's.

        The first mitigation attempt ran on 4 workers because the workflow set
        `CI_PYTEST_WORKERS` to the literal 'auto': the variable was *set*, so
        the script's `:-2` never applied, and a green run would have been
        reported as a validated fix. An unset repository variable must reach
        the script as an empty string so `:-` treats it as absent.
        """
        step = _workflow().split("Run pytest with coverage", 1)[1].split(
            "Upload coverage artifact", 1)[0]
        # Comments are stripped: the step documents this very trap, and a raw
        # scan would fail on its own explanation.
        code = "\n".join(
            line for line in step.splitlines()
            if not line.strip().startswith("#")
        )
        assert "'auto'" not in code

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
        assert 'PREFIX = "CI_RESOURCE"' in _read(SAMPLER)

    def test_the_sampler_streams_to_stdout(self):
        """Une mesure uploadée après l'arrêt du runner n'existe pas."""
        assert "flush=True" in _read(SAMPLER)

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
        source = _read(SAMPLER)
        assert "os.environ.items" not in source

    def test_the_sampler_reads_only_one_env_var(self):
        source = _read(SAMPLER)
        assert source.count("os.environ") == 1

    def test_the_sampler_never_raises_out_of_its_loop(self):
        source = _read(SAMPLER)
        assert "except Exception" in source


# ─────────────────── WS6 — mesure de la purge de modules ───────────────────


class TestModulePurgeMeasured:
    def test_the_purge_is_still_present(self):
        """Mesurer, pas supprimer : l'isolation reste autoritative."""
        source = _read(CONFTEST)
        assert "sys.modules.pop(mod_name, None)" in source

    def test_the_purge_scope_is_unchanged(self):
        source = _read(CONFTEST)
        assert 'm == "app" or m.startswith("app.")' in source

    def test_a_representative_app_module_count_is_measurable(self, client):
        """Combien de modules chaque cycle de purge recharge réellement."""
        import sys as live_sys

        loaded = [m for m in live_sys.modules if m == "app" or m.startswith("app.")]
        assert len(loaded) > 0


# ─────────────────── Sb_OPS_CI_SCALE_01 — partition des shards ───────────────────


def _shards():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "ci_test_shards", REPO_ROOT / "scripts" / "ci_test_shards.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestShardPartition:
    def test_the_union_is_the_whole_suite(self):
        """Un fichier oublié réduirait la couverture en gardant tout au vert."""
        mod = _shards()
        union: set[str] = set()
        for shard in mod.build_shards():
            union |= set(shard)
        assert union == set(mod.canonical_test_files())

    def test_the_shards_are_disjoint(self):
        """Sb_OPS_CI_SCALE_02 — généralisé à N shards.

        Cette assertion dépaquetait exactement deux shards (`first, second =
        …`), donc passer à 3 la faisait tomber sur un `ValueError` de
        dépaquetage — un échec de forme, pas de fond. Elle compare désormais
        **toutes les paires**, ce qui est l'invariant réel.
        """
        import itertools

        shards = _shards().build_shards()
        assert len(shards) >= 2
        for left, right in itertools.combinations(shards, 2):
            assert set(left) & set(right) == set()

    def test_the_partition_verifier_accepts_the_repository(self):
        _shards().verify()

    def test_the_partition_is_deterministic(self):
        mod = _shards()
        first = mod.build_shards()
        second = mod.build_shards()
        assert first == second

    def test_every_file_is_a_real_test_module(self):
        mod = _shards()
        for shard in mod.build_shards():
            for name in shard:
                assert (REPO_ROOT / name).is_file()

    def test_the_excluded_acceptance_file_is_never_sharded(self):
        """La même exclusion que la commande canonique, définie une seule fois."""
        mod = _shards()
        flat = [f for shard in mod.build_shards() for f in shard]
        assert "tests/test_v1_acceptance.py" not in flat

    def test_the_shards_are_balanced_within_one_file(self):
        mod = _shards()
        sizes = [len(s) for s in mod.build_shards()]
        assert max(sizes) - min(sizes) <= 1

    def test_a_shard_index_outside_the_range_is_refused(self):
        mod = _shards()
        beyond = mod.DEFAULT_SHARDS + 1
        with pytest.raises(ValueError):
            mod.shard_for(beyond, mod.DEFAULT_SHARDS)
        with pytest.raises(ValueError):
            mod.shard_for(0, mod.DEFAULT_SHARDS)

    def test_no_test_file_is_split_across_shards(self):
        """Granularité FICHIER : plusieurs modules sont sensibles à l'état."""
        mod = _shards()
        flat = [f for shard in mod.build_shards() for f in shard]
        assert len(flat) == len(set(flat))

    def test_the_workflow_verifies_the_partition_before_running(self):
        assert "ci_test_shards.py --verify" in _workflow()

    def test_the_workflow_combines_coverage_centrally(self):
        assert "coverage combine" in _workflow()

    def test_the_workflow_emits_one_authoritative_xml(self):
        assert "coverage xml -o coverage.xml" in _workflow()

    def test_the_required_check_name_is_preserved(self):
        """Une matrice nue l'aurait renommé et rendu toute PR non fusionnable."""
        assert "name: pytest + QA scripts" in _workflow()

    def test_the_aggregator_fails_when_a_shard_fails(self):
        assert "needs.test-shard.result != 'success'" in _workflow()

    def test_coverage_is_not_weakened_by_sharding(self):
        for banned in ("--cov-fail-under=0", "testmon", "--no-cov"):
            assert banned not in _workflow()


class TestLintJobHasNoNetworkDependency:
    """`Sb_OPS_CI_LINT_TIMEOUT_01` — le job lint ne doit pendre sur rien.

    QUATRE ANNULATIONS, ET UN DIAGNOSTIC FAUX PENDANT TOUT CE TEMPS
    ---------------------------------------------------------------
    Le job lint a été annulé quatre fois au plafond de 5 minutes, dont une sur
    la CI canonique. J'ai attribué ça à un « cache froid » pendant quatre
    occurrences. **La mesure a réfuté ce diagnostic** : sur l'annulation
    relevée (run `32226738467`), les neuf premiers steps prennent **22 s au
    total**, dont **6 s d'installation des linters** — pile la normale. C'est
    `shellcheck` SEUL qui a tourné **290 s** sans finir.

    La cause était `sudo apt-get update`, qui interroge un miroir Ubuntu au
    moment du job. **La seule dépendance réseau du job**, dans un step dont le
    travail réel dure une seconde.

    CE QUE CES GARDES EMPÊCHENT
    ----------------------------
    1. Qu'une dépendance réseau revienne dans le job lint. Le prochain miroir
       lent annulerait à nouveau le job — et une annulation n'est pas un job
       permissif, c'est un job **muet** : celle de la canonique a laissé
       `gitleaks`, `spec protocol` et le drift `requirements` NON EXÉCUTÉS.
    2. Qu'on « corrige » le symptôme en gonflant `timeout-minutes`. Sur 39
       exécutions réussies — min 36 s, médiane 51 s, p90 77 s, max 109 s — le
       budget de 5 minutes n'a jamais été en cause. L'augmenter ferait
       seulement durer le blocage plus longtemps.
    3. Qu'un step long puisse à nouveau emporter silencieusement les six steps
       suivants.
    """

    #: Le job lint commence à sa ligne `name:` et court jusqu'au job suivant.
    @staticmethod
    def _lint_job() -> str:
        wf = _workflow()
        start = wf.index("lint (ruff budget")
        rest = wf[start:]
        for marker in ("\n  sonar", "\n  aggregate", "\n  test:", "\n  deploy"):
            idx = rest.find(marker)
            if idx != -1:
                rest = rest[:idx]
                break
        return rest

    @classmethod
    def _lint_commands(cls) -> str:
        """Le job SANS ses commentaires.

        Le workflow EXPLIQUE pourquoi `apt-get` a été retiré, donc la chaîne
        apparaît dans sa propre justification. Une garde qui lit la prose
        rougirait sur l'explication du correctif — le motif
        `guards-that-guard-nothing` retourné contre lui-même, et la troisième
        fois qu'il se présente dans ce dépôt.
        """
        lines = []
        for line in cls._lint_job().splitlines():
            stripped = line.lstrip()
            if stripped.startswith("#"):
                continue
            lines.append(line)
        return "\n".join(lines)

    def test_the_lint_job_installs_nothing_over_the_network(self):
        """`apt-get` dans un job de lint, c'est un miroir distant sur le chemin
        critique d'un travail qui dure une seconde."""
        job = self._lint_commands()
        for banned in ("apt-get", "apt install", "add-apt-repository"):
            assert banned not in job, (
                f"{banned!r} réintroduit une dépendance réseau dans le job lint"
            )

    def test_shellcheck_still_runs_on_the_same_files(self):
        """Retirer l'installation ne doit pas retirer la vérification.
        L'outil est préinstallé sur l'image du runner."""
        job = self._lint_commands()
        assert "shellcheck -S warning" in job
        assert 'find scripts -maxdepth 2 -name "*.sh"' in job

    def test_shellcheck_declares_its_version_so_a_silent_swap_is_visible(self):
        """Un outil préinstallé peut changer de version avec l'image. La
        journaliser rend le changement lisible dans le log plutôt que dans un
        écart de résultat inexpliqué."""
        assert "shellcheck --version" in self._lint_commands()

    def test_the_shellcheck_step_carries_its_own_timeout(self):
        """Ceinture : un step d'une seconde qui dépasse la minute PEND. Sans
        garde de step, il consomme le budget du job et emporte les suivants
        sans les nommer."""
        job = self._lint_commands()
        head = job[:job.index("shellcheck -S warning")]
        assert "timeout-minutes: 1" in head, (
            "le step shellcheck doit porter sa propre limite"
        )

    #: Les steps requis, par leur DÉBUT DE DÉCLARATION exact.
    #:
    #: Chercher un simple mot-clé ne garde rien : la plantation a renommé
    #: « gitleaks scan (required — Sb_26.4) » en « gitleaks scan DISABLED
    #: (required — Sb_26.4) », et une garde qui cherchait `"gitleaks"` est
    #: restée VERTE. Neutraliser un gate en le renommant est exactement le
    #: geste qu'il faut attraper.
    REQUIRED_STEPS = (
        "- name: ruff budget check (required",
        "- name: bandit security scan (required",
        "- name: actionlint (required",
        "- name: shellcheck (required",
        "- name: pip-audit runtime dependencies (required",
        "- name: gitleaks scan (required",
        "- name: spec protocol check (required",
        "- name: auth scope matrix presence (required",
    )

    def test_no_required_lint_step_was_removed_or_renamed(self):
        """La correction ne devait retirer AUCUN gate — seulement une
        installation superflue."""
        job = self._lint_job()
        for step in self.REQUIRED_STEPS:
            assert step in job, f"gate requis disparu ou renommé : {step}"

    def test_the_dependency_drift_gate_is_still_blocking(self):
        """Le drift `requirements` ↔ lock faisait partie des six steps que
        l'annulation de la canonique a sautés. Il doit rester bloquant."""
        assert "drift (blocking)" in self._lint_job()


# ───────── Sb_OPS_LOCAL_SWEEP_MEMORY_01 — le sweep local ne tue plus la machine ─────────
#
# LE DÉFAUT, VÉCU PLUSIEURS FOIS. `run_ci_pytest.sh` lancée sur le poste de
# l'opérateur a fait tomber la machine à répétition : VS Code tué, sweep jamais
# terminé, donc AUCUNE information obtenue et du travail perdu à côté. Un
# garde-fou qui empêche de travailler n'est pas un garde-fou.
#
# LA CAUSE, MESURÉE le 2026-08-24. Le plafond « ~5 Go par worker » de ce script
# raisonne sur la RAM INSTALLÉE — 16 Go, donc 2 workers autorisés. Or seuls
# **5 365 Mo étaient DISPONIBLES** : l'éditeur et ses serveurs de langage
# occupaient le reste. La formule était juste, son hypothèse — machine dédiée
# au sweep — était fausse.
#
# S'y ajoute une croissance MONOTONE : un interpréteur qui enchaîne 5 200 tests
# cumule graphe applicatif, métadonnées SQLAlchemy, fixtures et traceur de
# couverture. Mesuré : un lot de 12 fichiers atteint 2 896 Mo, un lot de 6 en
# atteint 436 à 1 793 selon les fichiers. Le coût dépend des FICHIERS autant
# que de leur nombre.
#
# POURQUOI CES GARDES SONT MÉCANIQUES. La version précédente de ce dépôt
# expliquait déjà le risque, longuement, en commentaire et dans `CLAUDE.md`.
# Le script a quand même été lancé en local, plusieurs fois, par l'agent.
# La prose ne suffit pas ; le refus doit être exécutable.

LOCAL_SCRIPT = REPO_ROOT / "scripts" / "run_local_sweep.sh"


def _local_script() -> str:
    return LOCAL_SCRIPT.read_text(encoding="utf-8")


class TestLocalSweepMemory:
    def test_the_local_sweep_script_exists(self):
        assert LOCAL_SCRIPT.is_file()

    def test_the_ci_script_refuses_to_run_outside_ci(self):
        """LA GARDE CENTRALE. Elle éprouve le COMPORTEMENT, pas un commentaire."""
        env = {k: v for k, v in os.environ.items()
               if k not in ("CI", "ALLOW_LOCAL_CI_SWEEP")}
        out = subprocess.run(
            ["bash", str(CI_SCRIPT), "--collect-only", "-q"],
            env=env, capture_output=True, text=True, cwd=str(REPO_ROOT),
        )
        assert out.returncode == 2, out.stdout[-400:] + out.stderr[-400:]
        assert "run_local_sweep.sh" in out.stderr, (
            "le refus doit NOMMER la commande à utiliser à la place"
        )

    def test_the_refusal_can_be_lifted_deliberately_never_by_accident(self):
        """Un diagnostic reste possible — mais il faut le NOMMER."""
        assert "ALLOW_LOCAL_CI_SWEEP" in _script()

    def test_the_local_sweep_refuses_to_run_on_ci(self):
        """La réciproque. Deux chemins qui prétendent tous deux être « le
        sweep » est la divergence que `Sb_OPS_INSTALL_AUTHORITY_01` vient de
        fermer côté dépendances."""
        out = subprocess.run(
            ["bash", str(LOCAL_SCRIPT)],
            env={**os.environ, "CI": "true"},
            capture_output=True, text=True, cwd=str(REPO_ROOT),
        )
        assert out.returncode == 2
        assert "run_ci_pytest.sh" in out.stderr

    def test_the_local_sweep_batches_instead_of_running_one_process(self):
        """Le pic doit être borné par CONSTRUCTION, pas par une multiplication
        optimiste : un processus neuf par lot remet la RSS à zéro."""
        src = _local_script()
        assert "SWEEP_BATCH" in src
        assert "for ((i = 0" in src

    def test_the_local_sweep_has_a_memory_watchdog(self):
        src = _local_script()
        assert "SWEEP_BUDGET_MB" in src
        assert "ARRÊT" in src

    def test_the_budget_reads_available_memory_not_installed(self):
        """C'est TOUTE l'erreur du plafond précédent : 16 Go installés, 5,3 Go
        disponibles."""
        src = _local_script()
        assert "vm_stat" in src or "MemAvailable" in src
        assert "hw.memsize" not in src, (
            "la RAM installée ne dit pas ce qu'on peut prendre"
        )

    def test_coverage_is_off_by_default_locally(self):
        """`--cov` change le profil mémoire ET la durée. La couverture sert à
        Sonar, c'est-à-dire à la CI."""
        src = _local_script()
        assert "WITH_COVERAGE=0" in src
        assert "--with-coverage" in src

    def test_the_batch_default_carries_its_measurement(self):
        """Un chiffre doit voyager avec la mesure qui l'a produit."""
        src = _local_script()
        assert "SWEEP_BATCH:-4" in src
        assert "2896" in src, "le pic mesuré qui a fait baisser le défaut"

    def test_the_script_records_that_memory_is_not_released_between_files(self):
        """LA MESURE QUI A CHANGÉ LE RAISONNEMENT.

        Trois fichiers coûtent 1346 + 697 + 334 Mo individuellement, et
        2157 Mo en lot : la mémoire n'est **pas rendue** d'un fichier à
        l'autre dans un même processus. Le plancher du pic n'est donc pas la
        taille du lot mais le fichier le plus lourd — 1,3 Go à lui seul.

        Sans cette mesure, on réduit le lot indéfiniment en croyant descendre.
        """
        src = _local_script()
        assert "1346" in src
        assert "pas rendue" in src

    def test_the_budget_floor_stays_reachable(self):
        """Un plancher sous le coût du fichier le plus lourd arrêterait le
        sweep sur le premier lot venu — le défaut corrigé, sous une autre
        forme."""
        src = _local_script()
        assert "-lt 1600" in src

    def test_the_watchdog_names_the_files_of_the_offending_batch(self):
        """« réduire SWEEP_BATCH » sans dire lesquels laisse chercher à
        l'aveugle — le coût dépend des fichiers."""
        assert "fichiers du lot" in _local_script()

    def test_the_repo_contract_points_at_the_local_script(self):
        """`CLAUDE.md` prescrivait `run_ci_pytest.sh` « CI comme local ». C'est
        cette ligne qui a été exécutée, et qui a tué la machine."""
        contract = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        assert "run_local_sweep.sh" in contract
        assert "CI comme local, même source de vérité" not in contract

    def test_the_local_script_passes_shellcheck(self):
        """Le script neuf entre dans le même gate que les autres."""
        out = subprocess.run(
            ["shellcheck", str(LOCAL_SCRIPT)],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
        )
        if out.returncode == 127:
            pytest.skip("shellcheck absent de cet environnement")
        assert out.returncode == 0, out.stdout[-600:]
