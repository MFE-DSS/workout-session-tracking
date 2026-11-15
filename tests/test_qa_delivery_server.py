"""New QA transport reports current reality and retains closed QA02 admission."""

from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import httpx
import pytest

pytest_plugins = ["test_qa_delivery_database"]

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def bundle(tmp_path):
    from tools.plan_calibration_runtime_bundle import build_bundle

    target = tmp_path / "science"
    build_bundle(target)
    return target


@pytest.fixture
def upstream():
    calls = []

    class Echo(BaseHTTPRequestHandler):
        def do_GET(self):
            calls.append(self.path)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')

        def do_POST(self):
            calls.append(self.path)
            body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Echo)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    yield server.server_port, calls
    server.shutdown()
    server.server_close()
    worker.join()


def config(db, bundle, port=8140):
    from tools.qa_delivery.ownership import anchor_digest, capture_anchor
    from tools.qa_delivery.server import QAConfig

    anchor = capture_anchor(db, "qa-rel03-isolated")
    return QAConfig(
        db_path=db,
        bundle_root=bundle,
        environment_id="qa-rel03-isolated",
        source_sha="a" * 40,
        backend_port=port,
        ownership_anchor=anchor,
        ownership_anchor_sha256=anchor_digest(anchor),
        access={"signup_users": ["qa02-assigned"], "login_users": ["qa02-assigned"]},
    )


@pytest.mark.anyio
async def test_version_is_current_redacted_and_withdrawal_does_not_remove_transport(
    qa_database, bundle, upstream
):
    from tools.qa_delivery.server import create_qa_app

    port, _ = upstream
    app = create_qa_app(config(qa_database, bundle, port))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app), base_url="https://qa.invalid"
    ) as client:
        response = await client.get("/__qa_version")
        assert response.status_code == 200
        identity = response.json()
        assert identity["source_sha"] == "a" * 40
        assert identity["environment_id"] == "qa-rel03-isolated"
        assert identity["server_schema"] == "program_builder_operations_01"
        assert identity["authority"] == {"state": "WITHDRAWN", "generation": 3, "publication": None}
        with sqlite3.connect(qa_database) as db:
            db.execute("UPDATE first_plan_runtime_authorities SET generation=4,state='DISABLED'")
        assert (await client.get("/__qa_version")).json()["authority"]["generation"] == 4
        assert (await client.get("/__qa_health")).status_code == 200
        assert (await client.get("/api/mobile/v3/me/first-session-handoff")).status_code == 200
        assert all(
            x not in response.text
            for x in [
                "private-",
                str(qa_database),
                "qa02-assigned",
                "device-preserved",
                "subject-preserved",
                "approval_ref",
            ]
        )


@pytest.mark.anyio
@pytest.mark.parametrize("damage", ["db", "schema", "bundle", "authority"])
async def test_broken_dependency_returns_redacted_503(qa_database, bundle, upstream, damage):
    from tools.qa_delivery.server import create_qa_app

    app = create_qa_app(config(qa_database, bundle, upstream[0]))
    if damage == "db":
        qa_database.write_bytes(b"private-corruption")
    elif damage == "bundle":
        (bundle / "tools/science_calibration_extension/evaluator.py").write_text(
            "private-corruption"
        )
    else:
        with sqlite3.connect(qa_database) as db:
            db.execute(
                "UPDATE alembic_version SET version_num='unknown'"
                if damage == "schema"
                else "DELETE FROM first_plan_runtime_authorities"
            )
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app), base_url="https://qa.invalid"
    ) as client:
        for path in ["/__qa_health", "/__qa_version"]:
            response = await client.get(path)
            assert response.status_code == 503
            assert "private-" not in response.text and str(qa_database) not in response.text
        response = await client.get("/api/mobile/v1/me")
        # Missing science does not remove journal transport; V3 decides permission.
        assert response.status_code == (503 if damage in {"db", "schema"} else 200)


@pytest.mark.anyio
async def test_wrapper_reuses_mobile_allowlist_and_blocks_email_and_unassigned_accounts(
    qa_database, bundle, upstream
):
    from tools.qa_delivery.server import create_qa_app

    app = create_qa_app(config(qa_database, bundle, upstream[0]))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app), base_url="https://qa.invalid"
    ) as client:
        for path in [
            "/admin",
            "/docs",
            "/static/file",
            "/__qa_identity",
            "/api/mobile/v1/%252e%252e/admin",
        ]:
            assert (await client.get(path)).status_code == 404
        assert (
            await client.post(
                "/api/mobile/v1/auth/register",
                json={"username": "qa02-assigned", "email": "real@example.com"},
            )
        ).status_code == 403
        assert (
            await client.post("/api/mobile/v1/auth/login", json={"username": "outsider"})
        ).status_code == 403
        assert not upstream[1]
        response = await client.post(
            "/api/mobile/v1/auth/login",
            json={"username": "qa02-assigned", "password": "private-password"},
        )
        assert response.status_code == 200
        assert upstream[1] == ["/api/mobile/v1/auth/login"]


@pytest.mark.anyio
async def test_upstream_death_and_shutdown_are_honest(qa_database, bundle):
    from tools.qa_delivery.server import create_qa_app

    sock = ThreadingHTTPServer(("127.0.0.1", 0), BaseHTTPRequestHandler)
    port = sock.server_port
    sock.server_close()
    app = create_qa_app(config(qa_database, bundle, port))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app), base_url="https://qa.invalid"
    ) as client:
        assert (await client.get("/__qa_health")).status_code == 503
        assert (await client.get("/api/mobile/v1/me")).status_code == 502
        async with app.router.lifespan_context(app):
            pass
        assert (await client.get("/api/mobile/v1/me")).status_code == 503


@pytest.mark.parametrize(
    "key,value",
    [
        ("BODY_ASSESSMENT_ENABLED", "true"),
        ("SMTP_HOST", "mail.invalid"),
        ("SENTRY_DSN", "private-dsn"),
        ("PERF_LOG_SLOW_QUERIES_ENABLED", "1"),
        ("BODY_PROVIDER_BODYGRAM_ENABLED", "true"),
    ],
)
def test_cli_refuses_unsafe_environment_without_starting_process(tmp_path, key, value):
    import os

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.qa_delivery.server",
            "--config",
            str(tmp_path / "absent.json"),
            "--validate-only",
        ],
        cwd=ROOT,
        env={**os.environ, key: value},
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode != 0
    assert "qa_unsafe_environment" in result.stderr
    assert value not in result.stderr


@pytest.mark.anyio
async def test_active_publication_then_withdrawal_is_observed_without_cached_permission(
    qa_database, bundle, upstream
):
    import hashlib

    from app.services.plan_v3.packaging import execute_science
    from tools.qa_delivery.server import create_qa_app

    digest = hashlib.sha256((bundle / "packaging-manifest.v1.json").read_bytes()).hexdigest()
    authorities = execute_science("authorities", {}, root=bundle)
    pins = {
        key: authorities["v3"][key]
        for key in (
            "registry_digest",
            "binding_digest",
            "bundle_digest",
            "effective_science_digest",
        )
    }
    with sqlite3.connect(qa_database) as db:
        db.execute(
            "UPDATE first_plan_runtime_authorities SET state='ACTIVE',publication_json=?,packaging_digest=?,approval_ref='private-approval'",
            (json.dumps(pins), digest),
        )
    app = create_qa_app(config(qa_database, bundle, upstream[0]))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app), base_url="https://qa.invalid"
    ) as client:
        initial = (await client.get("/__qa_version")).json()
        assert initial["authority"] == {"state": "ACTIVE", "generation": 3, "publication": pins}
        with sqlite3.connect(qa_database) as db:
            db.execute("UPDATE first_plan_runtime_authorities SET state='WITHDRAWN',generation=4")
        after = await client.get("/__qa_version")
        assert after.json()["authority"]["state"] == "WITHDRAWN"
        assert after.json()["authority"]["generation"] == 4
        assert "private-approval" not in after.text
        assert (await client.get("/__qa_health")).status_code == 200


def test_valid_cli_configuration_does_not_seed_or_start_and_ambient_secret_is_not_inherited(
    qa_database, bundle, tmp_path
):
    from tools.qa_delivery.server import _child_environment

    secret = tmp_path / "secret"
    secret.write_text("synthetic-only-secret-do-not-use-live-1234")
    secret.chmod(0o600)
    access = tmp_path / "access.json"
    access.write_text('{"signup_users":[],"login_users":[]}')
    access.chmod(0o600)
    from tools.qa_delivery.ownership import anchor_digest, capture_anchor

    anchor = capture_anchor(qa_database, "qa-rel03-isolated")
    anchor_file = tmp_path / "ownership-anchor.json"
    anchor_file.write_text(json.dumps(anchor))
    anchor_file.chmod(0o600)
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "db_path": str(qa_database),
                "bundle_root": str(bundle),
                "environment_id": "qa-rel03-isolated",
                "source_sha": subprocess.check_output(
                    ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True
                ).strip(),
                "ownership_anchor_file": str(anchor_file),
                "ownership_anchor_sha256": anchor_digest(anchor),
                "secret_file": str(secret),
                "access_file": str(access),
                "data_scope": "SYNTHETIC_ONLY",
            }
        )
    )
    before = qa_database.read_bytes()
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.qa_delivery.server",
            "--config",
            str(path),
            "--validate-only",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "QA_CONFIG_VALIDATED_NO_SERVICE_STARTED"
    assert qa_database.read_bytes() == before
    env = _child_environment(config(qa_database, bundle), "synthetic-secret")
    assert env["APP_ENV"] == "test" and env["APP_SECRET_KEY"] == "synthetic-secret"
    assert env["DATABASE_URL"] == f"sqlite:///{qa_database}"
    assert "SMTP_HOST" not in env and "SENTRY_DSN" not in env and "HOME" not in env

    raw = json.loads(path.read_text())
    raw["source_sha"] = "b" * 40
    path.write_text(json.dumps(raw))
    refused = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.qa_delivery.server",
            "--config",
            str(path),
            "--validate-only",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert refused.returncode != 0


def test_supervisor_reaps_owned_sibling_when_child_dies(qa_database, bundle, tmp_path, monkeypatch):
    import tools.qa_delivery.server as module

    real_popen = subprocess.Popen
    children = []

    def spawn_owned(command, **kwargs):
        # Real disposable subprocesses, no network listeners or native app.
        script = "import time; time.sleep(0.2)" if not children else "import time; time.sleep(60)"
        child = real_popen([sys.executable, "-c", script], **kwargs)
        children.append((command, child))
        return child

    monkeypatch.setattr(module.subprocess, "Popen", spawn_owned)
    monkeypatch.setattr(module, "_require_free_loopback", lambda port: None)
    result = module.supervise(
        config(qa_database, bundle), "synthetic-secret", tmp_path / "not-read.json", 8080
    )
    assert result == 1
    assert len(children) == 2 and all(child.poll() is not None for _, child in children)
    canonical = children[0][0]
    assert canonical[canonical.index("--lifespan") + 1] == "off"
    assert canonical[canonical.index("--host") + 1] == "127.0.0.1"


def test_supervisor_refuses_an_already_owned_loopback_port_before_launch():
    import socket

    import tools.qa_delivery.server as module

    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        with pytest.raises(ValueError, match="qa_loopback_port_in_use"):
            module._require_free_loopback(listener.getsockname()[1])


def test_docker_copy_context_can_build_and_execute_real_bundle_without_checkout_fallback(tmp_path):
    import shlex
    import shutil

    deployed = tmp_path / "image-context"
    deployed.mkdir()
    # Execute the Dockerfile COPY boundary against a clean isolated source context.
    for line in (ROOT / "deploy/qa/Dockerfile").read_text().splitlines():
        if not line.startswith("COPY "):
            continue
        *sources, destination = shlex.split(line)[1:]
        target = deployed / destination
        for source in sources:
            origin = ROOT / source
            if origin.is_dir():
                shutil.copytree(
                    origin, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
                )
            else:
                output = target / origin.name if destination.endswith("/") else target
                output.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(origin, output)
    script = """
import sys
from pathlib import Path
root=Path(sys.argv[1]); sys.path.insert(0,str(root))
from tools.plan_calibration_runtime_bundle import build_bundle
from app.services.plan_v3.packaging import execute_science
bundle=root/'private-science'
digest=build_bundle(bundle)
result=execute_science('authorities',{},root=bundle,expected_digest=digest)
assert result['calibration_inventory']['version']=='plan-calibration-inventory/2.0.0'
assert (root/'app/static').is_dir() and (root/'app/templates').is_dir()
print('ISOLATED_IMAGE_CONTEXT_REAL_SCI_PASS')
"""
    result = subprocess.run(
        [sys.executable, "-I", "-c", script, str(deployed)],
        cwd=deployed,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr[-2000:]
    assert result.stdout.strip() == "ISOLATED_IMAGE_CONTEXT_REAL_SCI_PASS"


@pytest.mark.anyio
async def test_mobile_transport_does_not_repeat_full_science_preflight(
    qa_database, bundle, upstream, monkeypatch
):
    import tools.qa_delivery.server as module

    app = module.create_qa_app(config(qa_database, bundle, upstream[0]))

    def full_preflight_unavailable(*args, **kwargs):
        raise ValueError("private-science-error")

    monkeypatch.setattr(module, "read_version", full_preflight_unavailable)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app), base_url="https://qa.invalid"
    ) as client:
        assert (await client.get("/api/mobile/v1/me/sessions")).status_code == 200
        assert (await client.get("/__qa_health")).status_code == 503
        assert (await client.get("/__qa_version")).status_code == 503


@pytest.mark.anyio
async def test_liveness_remains_only_process_signal_if_database_disappears(
    qa_database, bundle, upstream
):
    from tools.qa_delivery.server import create_qa_app

    app = create_qa_app(config(qa_database, bundle, upstream[0]))
    qa_database.unlink()
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app), base_url="https://qa.invalid"
    ) as client:
        response = await client.get("/__qa_liveness")
        assert response.status_code == 200
        assert response.json() == {"alive": True, "data_ready": False}
        assert (await client.get("/__qa_version")).status_code == 503


@pytest.mark.anyio
@pytest.mark.parametrize(
    "damage",
    [
        "owner",
        "device",
        "subject",
        "device_owner",
        "subject_owner",
        "delete_device",
        "delete_subject",
        "user_created_at",
    ],
)
async def test_admitted_anchor_is_checked_on_business_health_and_version_after_startup(
    qa_database, bundle, upstream, damage
):
    from tools.qa_delivery.server import create_qa_app

    app = create_qa_app(config(qa_database, bundle, upstream[0]))
    with sqlite3.connect(qa_database) as db:
        if damage in {"device_owner", "subject_owner"}:
            db.execute(
                "INSERT INTO users (id,username,password_hash,is_active) VALUES (43,'qa02-other','other-hash',1)"
            )
        db.execute(
            {
                "device_owner": "UPDATE device_sessions SET user_id=43",
                "subject_owner": "UPDATE blueprint_source_events SET owner_id=43",
                "owner": "UPDATE users SET username='qa02-foreign' WHERE id=42",
                "device": "UPDATE device_sessions SET id='foreign-device'",
                "subject": "UPDATE blueprint_source_events SET id='foreign-subject'",
                "delete_device": "DELETE FROM device_sessions",
                "delete_subject": "DELETE FROM blueprint_source_events",
                "user_created_at": "UPDATE users SET created_at='2040-01-01 00:00:00' WHERE id=42",
            }[damage]
        )
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app), base_url="https://qa.invalid"
    ) as client:
        for path in ["/__qa_version", "/__qa_health", "/api/mobile/v1/me/sessions"]:
            response = await client.get(path)
            assert response.status_code == 503
            assert "foreign" not in response.text and str(qa_database) not in response.text
    assert upstream[1] == []


@pytest.mark.anyio
async def test_admitted_anchor_survives_growth_password_rotation_revocation_and_science_change(
    qa_database, bundle, upstream
):
    from tools.qa_delivery.server import create_qa_app

    cfg = config(qa_database, bundle, upstream[0])
    app = create_qa_app(cfg)
    with sqlite3.connect(qa_database) as db:
        db.execute(
            "INSERT INTO users (id,username,password_hash,is_active) VALUES (43,'qa02-new','new-hash',1)"
        )
        db.execute(
            "UPDATE users SET password_hash='rotated',session_epoch=7,is_active=0 WHERE id=42"
        )
        db.execute(
            "UPDATE device_sessions SET refresh_hash='rotated',session_epoch=7,last_used_at=CURRENT_TIMESTAMP,revoked_at=CURRENT_TIMESTAMP"
        )
        db.execute(
            "INSERT INTO device_sessions (id,user_id,refresh_hash,session_epoch,last_used_at) VALUES ('new-device',43,'hash',0,CURRENT_TIMESTAMP)"
        )
        db.execute(
            "INSERT INTO blueprint_source_events (id,owner_id,source_revision,request_id,body_digest,kind,payload_json) VALUES ('new-subject',42,2,'new-command','new-digest','CONTEXT_OPENED','{}')"
        )
        db.execute("UPDATE first_plan_runtime_authorities SET generation=4,state='DISABLED'")
    # Restart with the original admitted anchor, never recapture new rows.
    restarted = create_qa_app(cfg)
    for current in (app, restarted):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(current), base_url="https://qa.invalid"
        ) as client:
            response = await client.get("/__qa_version")
            assert response.status_code == 200
            assert response.json()["ownership_anchor_sha256"] == cfg.ownership_anchor_sha256
            assert response.json()["authority"]["generation"] == 4
            assert (
                "subject-preserved" not in response.text and "device-preserved" not in response.text
            )
            assert "qa02-assigned" not in response.text
            assert (await client.get("/__qa_health")).status_code == 200
            assert (await client.get("/api/mobile/v1/me/sessions")).status_code == 200


@pytest.mark.parametrize("damage", ["missing", "unknown_digest", "malformed", "other_environment"])
def test_unknown_or_malformed_admission_cannot_start_facade_or_writer(
    qa_database, bundle, monkeypatch, tmp_path, damage
):
    from dataclasses import replace

    from tools.qa_delivery import server

    cfg = config(qa_database, bundle)
    if damage == "missing":
        cfg = replace(cfg, ownership_anchor={})
    elif damage == "unknown_digest":
        cfg = replace(cfg, ownership_anchor_sha256="a" * 64)
    elif damage == "malformed":
        cfg = replace(cfg, ownership_anchor={**cfg.ownership_anchor, "device_sessions": []})
    else:
        cfg = replace(cfg, environment_id="qa-other")
    monkeypatch.setattr(
        server.subprocess, "Popen", lambda *a, **kw: pytest.fail("writer started before admission")
    )
    with pytest.raises(ValueError):
        server.create_qa_app(cfg)
    with pytest.raises(ValueError):
        server.supervise(cfg, "test-secret", tmp_path / "config", 8080)


def test_feature_config_private_references_and_distinct_child_environments(tmp_path):
    from tools.qa_delivery.server import (
        QAConfig,
        _child_environment,
        _facade_environment,
        load_feature_config,
    )

    tmp_path.chmod(0o700)
    refs = {}
    for name in ("NUT", "LIBRARY", "BUILDER"):
        key = tmp_path / (name + ".key")
        key.write_text("synthetic-signing-" + name + "-" * 40)
        key.chmod(0o600)
        refs[name] = {"identity": "qa-rel03-" + name.lower(), "signing_key_file": str(key)}
    source = tmp_path / "features.json"
    raw = {
        "schema_version": "qa-feature-config/1.0.0",
        "included_features": ["BODY", "NUT", "LIBRARY", "BUILDER"],
        "signatures": refs,
    }
    source.write_text(json.dumps(raw))
    source.chmod(0o600)
    env, profiles = load_feature_config(source)
    c = QAConfig(
        tmp_path / "db",
        tmp_path / "bundle",
        "qa-isolated",
        "a" * 40,
        feature_environment=env,
        feature_profiles=profiles,
    )
    backend = _child_environment(c, "private-synthetic-secret")
    facade = _facade_environment()
    assert backend["BODY_ASSESSMENT_ENABLED"] == "true"
    assert backend["NUTRITION_MANUAL_CONTROLLED_TEST_ENABLED"] == "true"
    assert backend["PROGRAM_BUILDER_SIGNING_KEY"].startswith("synthetic-signing-BUILDER")
    assert not any(
        k.startswith(("BODY_", "NUTRITION_", "LIBRARY_", "PROGRAM_BUILDER_")) for k in facade
    )
    assert "APP_SECRET_KEY" not in facade and "DATABASE_URL" not in facade
    assert not any("SIGNING_KEY" in k for k in profiles)
    assert set(profiles) == {"BODY", "NUT", "LIBRARY", "BUILDER"}
    for mutation in ("unknown", "duplicate", "shared_key", "permissions", "link"):
        changed = json.loads(json.dumps(raw))
        if mutation == "unknown":
            changed["ambient"] = True
        if mutation == "duplicate":
            changed["included_features"].append("BODY")
        if mutation == "shared_key":
            changed["signatures"]["NUT"] = refs["LIBRARY"]
        if mutation == "permissions":
            source.chmod(0o644)
        if mutation == "link":
            link = tmp_path / "linked.key"
            link.symlink_to(refs["NUT"]["signing_key_file"])
            changed["signatures"]["NUT"]["signing_key_file"] = str(link)
        source.write_text(json.dumps(changed))
        with pytest.raises(ValueError, match="qa_feature"):
            load_feature_config(source)
        source.chmod(0o600)
    source.write_text('{"schema_version":"qa-feature-config/1.0.0","schema_version":"other"}')
    with pytest.raises(ValueError, match="qa_feature"):
        load_feature_config(source)


def test_plan_only_environment_remains_without_feature_flags(tmp_path):
    from tools.qa_delivery.server import QAConfig, _child_environment

    c = QAConfig(tmp_path / "db", tmp_path / "bundle", "qa-isolated", "a" * 40)
    env = _child_environment(c, "synthetic-secret")
    assert not any(
        k.startswith(("BODY_", "NUTRITION_", "LIBRARY_", "PROGRAM_BUILDER_")) for k in env
    )


def test_real_supervisor_serves_explicit_families_with_separate_consent(
    qa_database, bundle, tmp_path
):
    import os
    import socket
    import time

    from app.services.auth import hash_password
    from tools.qa_delivery.ownership import anchor_digest, capture_anchor
    from tools.qa_delivery.server import _source_sha

    tmp_path.chmod(0o700)
    with sqlite3.connect(qa_database) as db:
        db.execute(
            "UPDATE users SET password_hash=? WHERE id=42",
            (hash_password("synthetic-qa-password"),),
        )

    def private(name, value):
        path = tmp_path / name
        path.write_text(value)
        path.chmod(0o600)
        return path

    refs = {}
    for family in ("NUT", "LIBRARY", "BUILDER"):
        refs[family] = {
            "identity": "qa-rel03-" + family.lower(),
            "signing_key_file": str(private(family + ".key", "synthetic-" + family + "-" * 40)),
        }
    features = private(
        "features.json",
        json.dumps(
            {
                "schema_version": "qa-feature-config/1.0.0",
                "included_features": ["BODY", "NUT", "LIBRARY", "BUILDER"],
                "signatures": refs,
            }
        ),
    )
    anchor = capture_anchor(qa_database, "qa-rel03-isolated")
    cfg = private(
        "config.json",
        json.dumps(
            dict(
                db_path=str(qa_database),
                bundle_root=str(bundle),
                environment_id="qa-rel03-isolated",
                source_sha=_source_sha(),
                data_scope="SYNTHETIC_ONLY",
                access_file=str(
                    private(
                        "access.json",
                        json.dumps({"signup_users": [], "login_users": ["qa02-assigned"]}),
                    )
                ),
                secret_file=str(private("secret", "synthetic-app-secret-" + "s" * 40)),
                ownership_anchor_file=str(private("anchor.json", json.dumps(anchor))),
                ownership_anchor_sha256=anchor_digest(anchor),
                feature_config_file=str(features),
            )
        ),
    )
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    child = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "tools.qa_delivery.server",
            "--config",
            str(cfg),
            "--port",
            str(port),
        ],
        cwd=ROOT,
        env={"PATH": os.environ["PATH"], "PYTHONPATH": str(ROOT)},
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    try:
        with httpx.Client(
            base_url=f"http://127.0.0.1:{port}", trust_env=False, timeout=5
        ) as client:
            deadline = time.monotonic() + 20
            while True:
                assert child.poll() is None, child.stderr.read().decode()
                try:
                    response = client.get("/__qa_version")
                    if response.status_code == 200:
                        break
                except httpx.TransportError:
                    pass
                assert time.monotonic() < deadline, "QA facade did not start"
                time.sleep(0.05)
            assert set(response.json()["feature_profiles"]) == {"BODY", "NUT", "LIBRARY", "BUILDER"}
            while True:
                try:
                    login = client.post(
                        "/api/mobile/v1/auth/login",
                        json={
                            "username": "qa02-assigned",
                            "password": "synthetic-qa-password",
                            "device_label": "synthetic-release-test",
                        },
                    )
                    if login.status_code == 200:
                        break
                except httpx.TransportError:
                    pass
                assert time.monotonic() < deadline, "canonical backend did not start"
                time.sleep(0.05)
            headers = {"Authorization": "Bearer " + login.json()["access_token"]}
            body_headers = {**headers, "X-Auren-Body-Contract": "body-measurements/1.0.0"}
            nut_headers = {**headers, "X-Auren-Nutrition-Contract": "nutrition-manual/1.0.0"}
            assert (
                client.get("/api/mobile/v1/me/body/consent", headers=body_headers).json()["granted"]
                is False
            )
            assert (
                client.get("/api/mobile/v1/me/body/measurements", headers=body_headers).status_code
                == 403
            )
            caps = client.get(
                "/api/mobile/v1/me/nutrition/capabilities", headers=nut_headers
            ).json()
            assert caps["state"] == "AVAILABLE" and caps["can_write"] is False
            assert caps["assisted_modes"] == []
            for path, header, version in [
                ("/api/mobile/v1/me/library", "X-Auren-Library-Contract", "owned-library/1.0.0"),
                (
                    "/api/mobile/v1/me/program-builder/programs",
                    "X-Auren-Program-Builder",
                    "program-builder/1.0.0",
                ),
            ]:
                result = client.get(path, headers={**headers, header: version})
                assert result.status_code == 200, result.text
    finally:
        child.terminate()
        try:
            child.wait(timeout=15)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait()
        child.stderr.close()


def test_private_feature_fifo_refuses_without_blocking_before_ssh_deadline(tmp_path):
    import os

    tmp_path.chmod(0o700)
    fifo = tmp_path / "not-a-regular-key"
    os.mkfifo(fifo, 0o600)
    code = 'from pathlib import Path; from tools.qa_delivery.server import _private_feature_text; _private_feature_text(Path(__import__("sys").argv[1]))'
    timed_out = False
    try:
        result = subprocess.run(
            [sys.executable, "-c", code, str(fifo)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except subprocess.TimeoutExpired:
        timed_out = True
    assert not timed_out, "private FIFO must refuse before any blocking open"
    assert result.returncode != 0 and "qa_feature_private_reference_required" in result.stderr
