"""Process boundaries are tested separately from Linux/runtime qualification."""

import hashlib
import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest


def module():
    try:
        return importlib.import_module("app.services.muscle_observed_load.supervisor")
    except ModuleNotFoundError:
        pytest.fail("BUILD01 bounded supervisor not implemented")


def test_missing_profile_and_wrong_platform_refuse_before_spawn(tmp_path):
    from app.services.muscle_observed_load.contracts import ObservedLoadReadError

    m = module()
    with pytest.raises(ObservedLoadReadError):
        m.load_runtime_profile("", "")
    raw = json.dumps({"qualification_state": "NON_QUALIFIED"}).encode()
    path = tmp_path / "profile.json"
    path.write_bytes(raw)
    with pytest.raises(ObservedLoadReadError):
        m.load_runtime_profile(str(path), hashlib.sha256(raw).hexdigest())


def test_bounded_pipe_kills_waits_and_does_not_capture_unlimited_output():
    m = module()
    from app.services.muscle_observed_load.contracts import ObservedLoadReadError

    child = subprocess.Popen(
        [sys.executable, "-I", "-c", "import os;os.write(1,b'x'*65536)"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    with pytest.raises(ObservedLoadReadError):
        m.collect_child(child, b"{}", max_bytes=1024, deadline=__import__("time").monotonic() + 2)
    assert child.poll() is not None


def test_wall_timeout_reaps_child_and_releases_slot():
    m = module()
    import time

    from app.services.muscle_observed_load.contracts import ObservedLoadReadError

    child = subprocess.Popen(
        [sys.executable, "-I", "-c", "import time;time.sleep(10)"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    with pytest.raises(ObservedLoadReadError):
        m.collect_child(child, b"{}", max_bytes=1024, deadline=time.monotonic() + 0.1)
    assert child.poll() is not None
    assert m.WORKER_SLOT.acquire(blocking=False)
    m.WORKER_SLOT.release()


def test_json_input_is_one_kibibyte_and_contains_no_credentials():
    m = module()
    from datetime import UTC, datetime

    from app.services.muscle_observed_load.contracts import ObservedLoadQuery

    body = m.encode_job(
        1,
        ObservedLoadQuery(datetime(2026, 11, 1, tzinfo=UTC), datetime(2026, 11, 25, tzinfo=UTC)),
        datetime(2026, 11, 25, tzinfo=UTC),
    )
    assert len(body) <= 1024
    assert set(json.loads(body)) == {"owner_id", "from", "until", "as_of"}


@pytest.mark.skipif(
    sys.platform != "linux",
    reason="Real RLIMIT Linux proof unavailable on this host; not runtime PASS",
)
def test_real_linux_worker_bootstraps_limits_without_changing_parent(tmp_path):
    import resource

    worker = Path(__file__).resolve().parents[1] / "app/services/muscle_observed_load/worker.py"
    before = {
        name: resource.getrlimit(getattr(resource, name))
        for name in ("RLIMIT_AS", "RLIMIT_CPU", "RLIMIT_CORE")
    }
    child = subprocess.run(
        [sys.executable, "-I", str(worker), "--qualify-limits"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        timeout=6,
        check=False,
    )
    assert child.returncode == 0
    proof = json.loads(child.stdout)
    assert proof["AS"] == [536870912, 536870912]
    assert proof["CPU"] == [2, 3] and proof["CORE"] == [0, 0]
    assert proof["memory_refused"] and proof["child_reaped_by_parent"] is False
    assert {name: resource.getrlimit(getattr(resource, name)) for name in before} == before


@pytest.mark.skipif(
    sys.platform != "linux", reason="Real CPU limit requires Linux; no local qualification claimed"
)
def test_real_linux_cpu_limit_terminates_and_parent_reaps_child():
    import signal
    import time

    worker = Path(__file__).resolve().parents[1] / "app/services/muscle_observed_load/worker.py"
    started = time.monotonic()
    child = subprocess.Popen(
        [sys.executable, "-I", str(worker), "--qualify-cpu"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        child.wait(timeout=6)
        assert child.returncode in (-signal.SIGXCPU, -signal.SIGKILL)
        assert time.monotonic() - started < 6
    finally:
        if child.poll() is None:
            child.kill()
            child.wait()


def test_parent_never_admits_or_parses_source_files_before_bounded_child(monkeypatch):
    m = module()
    from datetime import UTC, datetime

    from app.services.muscle_observed_load.contracts import ObservedLoadQuery, ObservedLoadReadError

    monkeypatch.setattr(m.sys, "platform", "linux")

    def forbidden(*args, **kwargs):
        pytest.fail("source/profile admission happened in HTTP parent")

    monkeypatch.setattr(m, "load_runtime_profile", forbidden)

    class Child:
        def __init__(self, *args, **kwargs):
            raise OSError("synthetic spawn refusal")

    monkeypatch.setattr(m.subprocess, "Popen", Child)
    with pytest.raises(ObservedLoadReadError):
        m.read_owned_muscle_observed_load(
            1,
            ObservedLoadQuery(
                datetime(2026, 11, 1, tzinfo=UTC), datetime(2026, 11, 25, tzinfo=UTC)
            ),
            runtime_profile=("/synthetic/profile", "0" * 64),
            database_url="sqlite:///synthetic",
        )
    assert m.WORKER_SLOT.acquire(blocking=False)
    m.WORKER_SLOT.release()


def qualification_module():
    try:
        return importlib.import_module("tools.muscle_observed_load_qualification")
    except ModuleNotFoundError:
        pytest.fail("isolated qualification harness not implemented")


def test_qualification_inventory_cannot_promote_current_host_to_qualified():
    report = qualification_module().inspect_runtime()
    assert report["reader"] == "NOT_QUALIFIED"
    assert report["runtime"] == "HOLD"
    assert report["fingerprint"]["python"] == __import__("platform").python_version()
    assert report["measurements"]["http_latency"] is None
    assert "FULL_TARGET_CAMPAIGN_NOT_EXECUTED" in report["reasons"]


def test_descriptor_anchored_read_rejects_symlink_mutable_ancestors_and_false_digest(tmp_path):
    import os

    m = qualification_module()
    trusted = tmp_path / "authority"
    trusted.mkdir(mode=0o700)
    target = trusted / "profile.json"
    target.write_bytes(b'{"synthetic":true}')
    target.chmod(0o600)
    pinned = hashlib.sha256(target.read_bytes()).hexdigest()
    descriptor = os.open(trusted, os.O_RDONLY | os.O_DIRECTORY)
    try:
        proof = m.inspect_relative(descriptor, "profile.json", pinned, trusted_uids={os.getuid()})
        assert proof["sha256"] == pinned and proof["bytes"] == 18
        target.chmod(0o666)
        with pytest.raises(ValueError, match="untrusted_permissions"):
            m.inspect_relative(descriptor, "profile.json", pinned, trusted_uids={os.getuid()})
        target.chmod(0o600)
        (trusted / "alias").symlink_to(target)
        with pytest.raises((ValueError, OSError)):
            m.inspect_relative(descriptor, "alias", pinned, trusted_uids={os.getuid()})
        with pytest.raises(ValueError, match="digest_mismatch"):
            m.inspect_relative(descriptor, "profile.json", "0" * 64, trusted_uids={os.getuid()})
        with pytest.raises(ValueError, match="invalid_path"):
            m.inspect_relative(
                descriptor, "../authority/profile.json", pinned, trusted_uids={os.getuid()}
            )
        (trusted / "child").mkdir(mode=0o777)
        (trusted / "child").chmod(0o777)
        (trusted / "child/profile.json").write_bytes(b"{}")
        with pytest.raises(ValueError, match="untrusted_permissions"):
            m.inspect_relative(descriptor, "child/profile.json", pinned, trusted_uids={os.getuid()})
        (trusted / "diralias").symlink_to(trusted, target_is_directory=True)
        with pytest.raises((ValueError, OSError)):
            m.inspect_relative(
                descriptor, "diralias/profile.json", pinned, trusted_uids={os.getuid()}
            )
    finally:
        os.close(descriptor)


@pytest.mark.skipif(
    sys.platform != "linux", reason="Real child pipeline requires Linux; not target qualification"
)
@pytest.mark.parametrize("readonly_bootstrap", [False, True])
def test_linux_real_child_admits_actual_catalogue_and_owned_read_without_writes(
    tmp_path, monkeypatch, readonly_bootstrap
):
    """TEST_ONLY admission fixture: exact runner profile, never a QA qualification."""
    from dataclasses import asdict
    from datetime import UTC, datetime

    from test_muscle_observed_load_sqlite import seed

    from app.services.muscle_observed_load.contracts import ObservedLoadQuery
    from app.services.muscle_observed_load.limits import ReadLimits

    m = module()
    root = Path(__file__).resolve().parents[1]
    # Parent ORM configuration must never select the worker's capture or bootstrap DB.
    monkeypatch.setenv("DATABASE_URL", "sqlite:////forbidden-parent/poison.sqlite")
    real_popen = subprocess.Popen

    def guarded_popen(args, **kwargs):
        assert "DATABASE_URL" not in kwargs["env"]
        if readonly_bootstrap:
            # Reproduce readonly mkdir refusal on writable CI too; the Linux qualification
            # separately mounts the actual complete checkout readonly.
            guard = (
                "import sys,runpy;from pathlib import Path;"
                "worker=sys.argv[1];sys.argv=sys.argv[1:];"
                "blocked=str(Path(worker).resolve().parents[3]/'var');"
                "sys.addaudithook(lambda event,args: "
                "(_ for _ in ()).throw(RuntimeError('readonly application root')) "
                "if event=='os.mkdir' and str(args[0])==blocked else None);"
                "runpy.run_path(worker,run_name='__main__')"
            )
            args = [*args[:3], "-c", guard, *args[3:]]
        return real_popen(args, **kwargs)

    monkeypatch.setattr(m.subprocess, "Popen", guarded_popen)
    db_path = seed(tmp_path / "synthetic.sqlite")
    with __import__("sqlite3").connect(db_path) as db:
        before = "\n".join(db.iterdump())
    profile = dict(
        qualification_state="QUALIFIED",
        qualification_ref="TEST_ONLY_NOT_OPERATIONAL",
        qualification_proof_sha256=hashlib.sha256(b"explicit isolated test fixture").hexdigest(),
        fingerprint=m.fingerprint(),
        limits=asdict(ReadLimits()),
        source_pins={
            name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in m._REQUIRED
        },
        http_processes=1,
        container_memory_bytes=2147483648,
        source_sha="9ef96e39aac400bc53583f62aecafc09f4dda1e3",
    )
    raw = json.dumps(profile).encode()
    profile_path = tmp_path / "test-profile.json"
    profile_path.write_bytes(raw)
    response = m.read_owned_muscle_observed_load(
        1,
        ObservedLoadQuery(datetime(2026, 11, 1, tzinfo=UTC), datetime(2026, 11, 25, tzinfo=UTC)),
        runtime_profile=(str(profile_path), hashlib.sha256(raw).hexdigest()),
        database_url="sqlite:///" + str(db_path),
    ).model_dump()
    assert response["owner_id"] == 1 and response["state"] == "PARTIAL"
    assert len(response["facts"]) == 1 and response["facts"][0]["reps"] == 9
    with __import__("sqlite3").connect(db_path) as db:
        assert "\n".join(db.iterdump()) == before
    assert m.WORKER_SLOT.acquire(blocking=False)
    m.WORKER_SLOT.release()


def test_worker_parses_catalogue_once_per_job_and_never_between_owners(tmp_path, monkeypatch):
    import io
    from dataclasses import asdict
    from datetime import UTC, datetime
    from types import SimpleNamespace

    from test_muscle_observed_load_provenance import parser_spy
    from test_muscle_observed_load_sqlite import seed

    monkeypatch.setattr(sys, "dont_write_bytecode", sys.dont_write_bytecode)
    monkeypatch.setattr(sys, "path", sys.path.copy())
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    from app.services.muscle_observed_load import worker
    from app.services.muscle_observed_load.contracts import ObservedLoadQuery
    from app.services.muscle_observed_load.limits import ReadLimits

    m = module()
    monkeypatch.setattr(m.sys, "platform", "linux")
    monkeypatch.setattr(worker, "install_limits", lambda: None)  # never set parent RLIMIT
    root = Path(__file__).resolve().parents[1]
    db = seed(tmp_path / "synthetic.sqlite")
    profile = dict(
        qualification_state="QUALIFIED",
        qualification_ref="TEST_ONLY_NOT_OPERATIONAL",
        qualification_proof_sha256=hashlib.sha256(b"isolated unit boundary").hexdigest(),
        fingerprint=m.fingerprint(),
        limits=asdict(ReadLimits()),
        source_pins={p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in m._REQUIRED},
        http_processes=1,
        container_memory_bytes=2147483648,
        source_sha="3d4c7577e5ffd39fb59de58d1aab3bded1936edb",
    )
    raw = json.dumps(profile).encode()
    profile_path = tmp_path / "profile.json"
    profile_path.write_bytes(raw)
    calls = parser_spy(monkeypatch)
    query = ObservedLoadQuery(datetime(2026, 11, 1, tzinfo=UTC), datetime(2026, 11, 25, tzinfo=UTC))
    for owner in [1, 2]:
        body = m.encode_job(owner, query, datetime(2026, 11, 26, tzinfo=UTC))
        output = io.BytesIO()
        monkeypatch.setattr(
            worker.sys,
            "argv",
            [
                str(root / "app/services/muscle_observed_load/worker.py"),
                str(profile_path),
                hashlib.sha256(raw).hexdigest(),
                "sqlite:///" + str(db),
                "",
            ],
        )
        monkeypatch.setattr(worker.sys, "stdin", SimpleNamespace(buffer=io.BytesIO(body)))
        monkeypatch.setattr(
            worker.sys,
            "stdout",
            SimpleNamespace(buffer=output, write=lambda s: output.write(s.encode())),
        )
        assert worker.main() == 0, output.getvalue()
        result = json.loads(output.getvalue())
        assert result["owner_id"] == owner
        assert [f["reps"] for f in result["facts"]] == ([9] if owner == 1 else [8])
        assert len(calls) == owner  # fresh parsing context per actual main invocation


def test_entry_finishes_without_running_unrelated_interpreter_teardown():
    """A successful flushed child must not spend its remaining CPU in atexit/GC."""
    worker = Path(__file__).resolve().parents[1] / "app/services/muscle_observed_load/worker.py"
    probe = r'''
import atexit, os, runpy, sys
worker = sys.argv[1]
def finished_main():
    sys.stdout.write('{"synthetic_exit_probe":true}')
    return 0
def substitute(frame, event, arg):
    if frame.f_code.co_filename == worker and event == 'line' and 'main' in frame.f_globals:
        frame.f_globals['main'] = finished_main
        sys.settrace(None)
    return substitute
atexit.register(lambda: os._exit(23))
sys.settrace(substitute)
runpy.run_path(worker, run_name='__main__')
'''
    child = subprocess.run(
        [sys.executable, "-I", "-c", probe, str(worker)],
        capture_output=True,
        timeout=5,
        check=False,
    )
    assert child.returncode == 0
    assert child.stdout == b'{"synthetic_exit_probe":true}'


@pytest.mark.parametrize("fault", ["flush", "closed_pipe", "exception"])
def test_entry_never_promotes_failure_to_success(fault):
    worker = Path(__file__).resolve().parents[1] / "app/services/muscle_observed_load/worker.py"
    probe = r'''
import runpy, sys
worker, fault = sys.argv[1:]
original = sys.stdout
class BrokenFlush:
    def write(self, value):
        return original.write(value)
    def flush(self):
        raise OSError('synthetic flush failure after valid output')
def failed_main():
    if fault == 'exception':
        raise ValueError('synthetic before validation')
    sys.stdout.write('{"synthetic_exit_probe":true}')
    return 0
def substitute(frame, event, arg):
    if frame.f_code.co_filename == worker and event == 'line' and 'main' in frame.f_globals:
        frame.f_globals['main'] = failed_main
        sys.settrace(None)
    return substitute
if fault == 'flush':
    sys.stdout = BrokenFlush()
elif fault == 'closed_pipe':
    sys.stdout.close()
sys.settrace(substitute)
runpy.run_path(worker, run_name='__main__')
'''
    child = subprocess.run(
        [sys.executable, "-I", "-c", probe, str(worker), fault],
        capture_output=True,
        timeout=5,
        check=False,
    )
    assert child.returncode != 0


@pytest.fixture
def worker_job(tmp_path, monkeypatch):
    """Real readonly capture/projection; only OS limits are disabled in pytest's parent."""
    import io
    import sqlite3
    from contextlib import contextmanager
    from dataclasses import asdict
    from datetime import UTC, datetime
    from types import SimpleNamespace

    from test_muscle_observed_load_sqlite import seed

    from app.services.muscle_observed_load import sqlite_source, worker
    from app.services.muscle_observed_load.contracts import ObservedLoadQuery
    from app.services.muscle_observed_load.limits import ReadLimits

    monkeypatch.setattr(sys, "dont_write_bytecode", sys.dont_write_bytecode)
    monkeypatch.setattr(sys, "path", sys.path.copy())
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setattr(worker, "install_limits", lambda: None)
    monkeypatch.setattr(sys, "platform", "linux")
    root = Path(__file__).resolve().parents[1]
    db_path = seed(tmp_path / "synthetic.sqlite")
    with sqlite3.connect(db_path) as db:
        before = "\n".join(db.iterdump())
    m = module()
    profile = dict(
        qualification_state="QUALIFIED",
        qualification_ref="TEST_ONLY_WORKER_EXIT_NOT_OPERATIONAL",
        qualification_proof_sha256=hashlib.sha256(b"isolated exit regression").hexdigest(),
        fingerprint=m.fingerprint(),
        limits=asdict(ReadLimits()),
        source_pins={p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in m._REQUIRED},
        http_processes=1,
        container_memory_bytes=2147483648,
        source_sha="54f68f65bd4c69f986bc887d7e7fbbec98a8c67b",
    )
    raw = json.dumps(profile).encode()
    profile_path = tmp_path / "profile.json"
    profile_path.write_bytes(raw)
    query = ObservedLoadQuery(datetime(2026, 11, 1, tzinfo=UTC), datetime(2026, 11, 25, tzinfo=UTC))
    body = m.encode_job(1, query, datetime(2026, 11, 26, tzinfo=UTC))
    output = io.BytesIO()
    captures = []
    state = SimpleNamespace(close_failure=False)
    real_open = sqlite_source.open_owned_capture

    @contextmanager
    def tracked_capture(*args, **kwargs):
        with real_open(*args, **kwargs) as capture:
            captures.append(capture.connection)
            yield capture
        if state.close_failure:
            raise OSError("synthetic required close failure")

    monkeypatch.setattr(sqlite_source, "open_owned_capture", tracked_capture)
    monkeypatch.setattr(
        sys,
        "argv",
        [str(root / "app/services/muscle_observed_load/worker.py"), str(profile_path),
         hashlib.sha256(raw).hexdigest(), "sqlite:///" + str(db_path), ""],
    )
    def run(stdout=None):
        # pytest reinstalls capture between fixture setup and the test call.
        monkeypatch.setattr(sys, "stdin", SimpleNamespace(buffer=io.BytesIO(body)))
        monkeypatch.setattr(
            sys, "stdout", stdout or SimpleNamespace(
                buffer=output, write=lambda value: output.write(value.encode())
            ),
        )
        return worker.main()

    yield SimpleNamespace(
        worker=worker, output=output, captures=captures, state=state, db_path=db_path, run=run
    )
    for connection in captures:
        with pytest.raises(sqlite3.ProgrammingError, match="closed"):
            connection.execute("SELECT 1")
    with sqlite3.connect(db_path) as db:
        assert "\n".join(db.iterdump()) == before


def test_worker_success_closes_capture_and_emits_independently_checkable_digest(worker_job):
    assert worker_job.run() == 0
    result = json.loads(worker_job.output.getvalue())
    assert result["owner_id"] == 1
    assert len(result["facts"]) == 1
    assert result["facts"][0]["reps"] == 9
    actual = result["consistency"]["result_digest"]
    result["consistency"]["result_digest"] = "0" * 64
    expected = hashlib.sha256(
        json.dumps(result, sort_keys=True, ensure_ascii=False, allow_nan=False,
                   separators=(",", ":")).encode()
    ).hexdigest()
    assert actual == expected


@pytest.mark.parametrize("fault", ["corrupt_digest", "invalid_dto", "exception", "close"])
def test_worker_refuses_invalid_result_or_required_close_failure(worker_job, monkeypatch, fault):
    from types import SimpleNamespace

    from app.services.muscle_observed_load import projection

    original = projection.project_capture

    def injected(*args, **kwargs):
        if fault == "exception":
            raise ValueError("synthetic failure before validation")
        result = original(*args, **kwargs).model_dump()
        if fault == "corrupt_digest":
            result["consistency"]["result_digest"] = "0" * 64
        elif fault == "invalid_dto":
            result["facts"][0]["reps"] = "invalid repetitions"
        return SimpleNamespace(model_dump=lambda: result)

    if fault == "close":
        worker_job.state.close_failure = True
    else:
        monkeypatch.setattr(projection, "project_capture", injected)
    assert worker_job.run() != 0
    assert json.loads(worker_job.output.getvalue()) == {
        "error": "muscle_observed_load_unavailable"
    }


@pytest.mark.parametrize("fault", ["short_write", "interrupted_write"])
def test_worker_never_accepts_incomplete_output_write(worker_job, monkeypatch, fault):
    from types import SimpleNamespace

    def incomplete_write(data):
        worker_job.output.write(data[:7])
        if fault == "interrupted_write":
            raise InterruptedError("synthetic interrupted write")
        return 7

    output = SimpleNamespace(
        buffer=SimpleNamespace(write=incomplete_write),
        write=lambda value: worker_job.output.write(value.encode()),
    )
    assert worker_job.run(output) != 0


@pytest.mark.parametrize("fault", ["incomplete_json", "sigxcpu", "sigterm"])
def test_parent_refuses_bad_child_output_reaps_and_releases_slot(monkeypatch, fault):
    import signal
    from datetime import UTC, datetime

    from app.services.muscle_observed_load.contracts import ObservedLoadQuery, ObservedLoadReadError

    m = module()
    real_popen = subprocess.Popen
    children = []
    code = "import os;os.write(1,b'{\"facts\":')"
    if fault != "incomplete_json":
        number = signal.SIGXCPU if fault == "sigxcpu" else signal.SIGTERM
        code = f"import os;os.write(1,b'{{}}');os.kill(os.getpid(),{int(number)})"

    def child_factory(*args, **kwargs):
        child = real_popen(
            [sys.executable, "-I", "-c", code], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        )
        children.append(child)
        return child

    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(m.subprocess, "Popen", child_factory)
    with pytest.raises(ObservedLoadReadError):
        m.read_owned_muscle_observed_load(
            1, ObservedLoadQuery(datetime(2026, 11, 1, tzinfo=UTC), datetime(2026, 11, 25, tzinfo=UTC)),
            runtime_profile=("/synthetic/profile", "0" * 64), database_url="sqlite:///synthetic",
        )
    assert len(children) == 1
    assert children[0].poll() is not None
    assert children[0].stdout.closed
    assert children[0].stdin.closed
    assert m.WORKER_SLOT.acquire(blocking=False)
    m.WORKER_SLOT.release()
