"""A new managed disk serves maintenance only until explicit private activation."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.anyio
async def test_maintenance_is_live_but_never_starts_or_exposes_business(tmp_path):
    from tools.qa_delivery.bootstrap import maintenance_app

    before = list(tmp_path.iterdir())
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(maintenance_app()), base_url="http://qa.invalid"
    ) as client:
        live = await client.get("/__qa_liveness")
        assert live.status_code == 200
        assert live.json() == {"alive": True, "data_ready": False}
        for method, path in [
            ("GET", "/__qa_version"),
            ("GET", "/__qa_health"),
            ("POST", "/api/mobile/v1/auth/login"),
            ("GET", "/etc/secrets/config.json"),
            ("POST", "/api/mobile/v3/me/first-session-handoff"),
        ]:
            response = await client.request(method, path)
            assert response.status_code == 503
            assert response.headers["retry-after"] == "30"
            assert "secret" not in response.text
    assert list(tmp_path.iterdir()) == before


def marker(tmp_path, config):
    path = tmp_path / "activation.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "qa-activation/1.0.0",
                "source_sha": "a" * 40,
                "config_sha256": hashlib.sha256(config.read_bytes()).hexdigest(),
            }
        )
    )
    path.chmod(0o600)
    return path


def test_missing_marker_never_reads_config_or_executes(tmp_path, monkeypatch):
    from tools.qa_delivery import bootstrap

    monkeypatch.setattr(bootstrap, "_load_config", lambda _: pytest.fail("must not read config"))
    assert (
        bootstrap.activation_command(tmp_path / "missing", tmp_path / "private.json", "8080")
        is None
    )
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("damage", ["mode", "symlink", "config_digest", "source", "invalid_config"])
def test_activation_refuses_incomplete_or_untrusted_marker(tmp_path, monkeypatch, damage):
    from tools.qa_delivery import bootstrap

    config = tmp_path / "config.json"
    config.write_text("{}")
    config.chmod(0o600)
    activation = marker(tmp_path, config)
    monkeypatch.setattr(bootstrap, "_source_sha", lambda: "a" * 40)
    if damage == "mode":
        activation.chmod(0o644)
    if damage == "symlink":
        target = activation.rename(tmp_path / "actual")
        activation.symlink_to(target)
    if damage == "config_digest":
        config.write_text('{"changed":true}')
    if damage == "source":
        monkeypatch.setattr(bootstrap, "_source_sha", lambda: "b" * 40)
    with pytest.raises(ValueError, match="qa_activation_refused"):
        bootstrap.activation_command(activation, config, "8080")


def test_activation_validates_full_task1_config_before_exec(tmp_path, monkeypatch):
    from tools.qa_delivery import bootstrap
    from tools.qa_delivery.server import QAConfig

    config = tmp_path / "config.json"
    config.write_text("{}")
    config.chmod(0o600)
    db = tmp_path / "existing.db"
    db.write_bytes(b"already-validated-db")
    activation = marker(tmp_path, config)
    called = []
    monkeypatch.setattr(bootstrap, "_source_sha", lambda: "a" * 40)
    monkeypatch.setattr(
        bootstrap,
        "_load_config",
        lambda path: (
            called.append(path) or QAConfig(db, tmp_path, "qa-test", "a" * 40),
            "private",
        ),
    )
    command = bootstrap.activation_command(activation, config, "8080")
    assert called == [config]
    assert command == [
        sys.executable,
        "-m",
        "tools.qa_delivery.server",
        "--config",
        str(config),
        "--port",
        "8080",
    ]
    assert not any("private" == item for item in command)


def test_cli_invalid_activation_fails_without_starting_service(tmp_path):
    activation = tmp_path / "activation.json"
    activation.write_text("{}")
    activation.chmod(0o600)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.qa_delivery.bootstrap",
            "--activation",
            str(activation),
            "--config",
            str(tmp_path / "missing"),
            "--port",
            "8080",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 1
    assert result.stderr.strip() == "qa_bootstrap_refused"
    assert list(tmp_path.iterdir()) == [activation]


@pytest.mark.anyio
async def test_maintenance_catches_unusual_methods_instead_of_serving_any_business():
    from tools.qa_delivery.bootstrap import maintenance_app

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(maintenance_app()), base_url="http://qa.invalid"
    ) as client:
        for method in ["TRACE", "CONNECT", "PROPFIND"]:
            assert (await client.request(method, "/api/mobile/v1/me")).status_code == 503


def test_real_maintenance_process_listens_without_config_db_or_activation(tmp_path):
    import socket
    import time

    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    env = {**os.environ, "PYTHONPATH": str(ROOT), "PYTHONDONTWRITEBYTECODE": "1"}
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "tools.qa_delivery.bootstrap",
            "--activation",
            str(tmp_path / "activation"),
            "--config",
            str(tmp_path / "config"),
            "--port",
            str(port),
        ],
        cwd=tmp_path,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        deadline = time.monotonic() + 8
        with httpx.Client(trust_env=False, timeout=1) as client:
            while True:
                try:
                    live = client.get(f"http://127.0.0.1:{port}/__qa_liveness")
                    break
                except httpx.ConnectError:
                    assert process.poll() is None and time.monotonic() < deadline
                    time.sleep(0.05)
            assert live.json() == {"alive": True, "data_ready": False}
            assert client.get(f"http://127.0.0.1:{port}/__qa_version").status_code == 503
        assert list(tmp_path.iterdir()) == []
    finally:
        process.terminate()
        process.wait(timeout=10)


def test_main_executes_only_validated_fixed_supervisor_command(tmp_path, monkeypatch):
    from tools.qa_delivery import bootstrap

    command = [
        sys.executable,
        "-m",
        "tools.qa_delivery.server",
        "--config",
        "/private/config",
        "--port",
        "8080",
    ]
    monkeypatch.setattr(sys, "argv", ["bootstrap"])
    monkeypatch.setattr(bootstrap, "activation_command", lambda *args: command)

    class Executed(Exception):
        pass

    def execute(executable, argv):
        assert executable == sys.executable and argv == command
        raise Executed

    monkeypatch.setattr(os, "execv", execute)
    with pytest.raises(Executed):
        bootstrap.main()


def test_docker_copy_closure_excludes_render_root_secrets_in_tracked_context(tmp_path):
    import shlex
    import tarfile

    dockerfile = (ROOT / "deploy/qa/Dockerfile").read_text()
    archive = tmp_path / "source.tar"
    with archive.open("wb") as output:
        subprocess.run(["git", "-C", str(ROOT), "archive", "HEAD"], stdout=output, check=True)
    context = tmp_path / "context"
    context.mkdir()
    with tarfile.open(archive) as source:
        source.extractall(context, filter="data")
    # Render injects secret files in the root of this context. Model actual COPY
    # source selection over an extracted tracked archive, not a Docker build claim.
    private = ["qa-config.json", "qa-access.json", "qa-auth-secret"]
    for name in private:
        (context / name).write_text("sentinel-private-material")
    selected = []
    for line in dockerfile.splitlines():
        if line.startswith("COPY "):
            sources = shlex.split(line)[1:-1]
            assert "." not in sources and not any("*" in value for value in sources)
            for value in sources:
                path = context / value
                assert path.exists()
                selected.extend(path.rglob("*") if path.is_dir() else [path])
    assert selected
    assert not {context / name for name in private}.intersection(selected)
    assert all(b"sentinel-private-material" not in p.read_bytes() for p in selected if p.is_file())
    ignore = (ROOT / "deploy/qa/Dockerfile.dockerignore").read_text().splitlines()
    assert all(name in ignore for name in private)
    assert "USER 10001" in dockerfile
    assert '"tools.qa_delivery.bootstrap"' in dockerfile


pytest_plugins = ["test_qa_delivery_database"]


def test_activation_runs_real_task1_schema_bundle_and_secret_validation(tmp_path, qa_database):
    from tools.plan_calibration_runtime_bundle import build_bundle
    from tools.qa_delivery.bootstrap import activation_command

    bundle = tmp_path / "science"
    build_bundle(bundle)
    source = subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True
    ).strip()
    access, secret, config = [
        tmp_path / name for name in ["access.json", "auth-secret", "config.json"]
    ]
    access.write_text(
        json.dumps({"signup_users": ["qa02-assigned"], "login_users": ["qa02-assigned"]})
    )
    secret.write_text("synthetic-test-only-secret-of-sufficient-length")
    config.write_text(
        json.dumps(
            {
                "data_scope": "SYNTHETIC_ONLY",
                "db_path": str(qa_database),
                "bundle_root": str(bundle),
                "environment_id": "qa-bootstrap-test",
                "source_sha": source,
                "access_file": str(access),
                "secret_file": str(secret),
            }
        )
    )
    for path in (access, secret, config):
        path.chmod(0o600)
    activation = marker(tmp_path, config)
    raw = json.loads(activation.read_text())
    raw["source_sha"] = source
    activation.write_text(json.dumps(raw))
    assert activation_command(activation, config, "8080")[2] == "tools.qa_delivery.server"
    qa_database.write_bytes(b"broken-database")
    with pytest.raises(ValueError, match="qa_activation_refused"):
        activation_command(activation, config, "8080")
