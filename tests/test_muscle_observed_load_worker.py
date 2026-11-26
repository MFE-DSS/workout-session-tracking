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
def test_linux_real_child_admits_actual_catalogue_and_owned_read_without_writes(tmp_path):
    """TEST_ONLY admission fixture: exact runner profile, never a QA qualification."""
    from dataclasses import asdict
    from datetime import UTC, datetime

    from test_muscle_observed_load_sqlite import seed

    from app.services.muscle_observed_load.contracts import ObservedLoadQuery
    from app.services.muscle_observed_load.limits import ReadLimits

    m = module()
    root = Path(__file__).resolve().parents[1]
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
