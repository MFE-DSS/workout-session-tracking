"""Synthetic host/TLS boundaries; no host commands or remote mutation."""

import hashlib
import ssl
from copy import deepcopy
from datetime import UTC, datetime

import httpx
import pytest


def fixture():
    from tools.qa_delivery.server import FEATURE_PROFILES

    policy = dict(
        environment_id="qa-rel03",
        resource="auren-qa-rel03",
        origin="https://qa.spignos.com",
        peer_ip="8.8.8.8",
        uid=10001,
        mounts=[
            {
                "type": "volume",
                "source": "auren-qa-rel03-data",
                "destination": "/var/lib/qa",
                "rw": True,
            },
            {
                "type": "volume",
                "source": "auren-qa-rel03-config",
                "destination": "/etc/secrets",
                "rw": False,
            },
        ],
        ports=[],
        container_ip="172.23.0.2",
        network="auren-qa-rel03-internal",
        restart_policy="no",
        memory_bytes=1073741824,
        nano_cpus=1000000000,
        pids_limit=128,
        configuration_sha256="c" * 64,
        routing_sha256="d" * 64,
        feature_profiles=FEATURE_PROFILES,
    )
    request = dict(
        schema_version="qa-ovh-observation-request/2.0.0",
        nonce="a" * 64,
        candidate_sha256="b" * 64,
        environment_id="qa-rel03",
        resource="auren-qa-rel03",
    )
    observation = dict(
        schema_version="qa-ovh-observation/2.0.0",
        nonce=request["nonce"],
        candidate_sha256=request["candidate_sha256"],
        observed_at="2026-11-15T12:00:00Z",
        environment_id="qa-rel03",
        container_id="f" * 64,
        image_id="sha256:" + "e" * 64,
        running=True,
        health="healthy",
        writer_count=1,
        **{
            k: deepcopy(v)
            for k, v in policy.items()
            if k not in {"resource", "origin", "peer_ip", "environment_id"}
        },
        routing={
            "origin": policy["origin"],
            "peer_ip": policy["peer_ip"],
            "container_id": "f" * 64,
            "upstream": "http://172.23.0.2:8080",
            "loaded_configuration_sha256": policy["routing_sha256"],
        },
    )
    return policy, request, observation


def test_fresh_observation_requires_runtime_routing_not_only_healthy_container():
    from tools.qa_delivery.ovh_observation import validate_observation

    policy, request, record = fixture()
    assert (
        validate_observation(
            record,
            request,
            policy,
            record["image_id"],
            now=datetime(2026, 11, 15, 12, 0, 20, tzinfo=UTC),
        )
        == record
    )


@pytest.mark.parametrize("old", ["request", "observation", "policy"])
def test_loopback_generation_cannot_authorize_direct_bridge_transport(old):
    from tools.qa_delivery.ovh_observation import validate_observation

    policy, request, record = fixture()
    if old == "request":
        request["schema_version"] = "qa-ovh-observation-request/1.0.0"
    elif old == "observation":
        record["schema_version"] = "qa-ovh-observation/1.0.0"
    else:
        policy.pop("container_ip")
        policy["ports"] = [{"host_ip": "127.0.0.1", "host_port": 8088, "container_port": 8080}]
    with pytest.raises(ValueError, match="qa_ovh"):
        validate_observation(
            record,
            request,
            policy,
            record["image_id"],
            now=datetime(2026, 11, 15, 12, 0, 20, tzinfo=UTC),
        )


@pytest.mark.parametrize(
    "damage",
    [
        "nonce",
        "time",
        "future",
        "image",
        "writer",
        "root",
        "mount",
        "port",
        "route",
        "unknown",
        "config",
    ],
)
def test_observation_rejects_replay_runtime_or_routing_mismatch(damage):
    from tools.qa_delivery.ovh_observation import validate_observation

    policy, request, record = fixture()
    if damage == "nonce":
        record["nonce"] = "0" * 64
    if damage == "time":
        record["observed_at"] = "2026-11-15T11:58:00Z"
    if damage == "future":
        record["observed_at"] = "2026-11-15T12:00:31Z"
    if damage == "image":
        record["image_id"] = "sha256:" + "0" * 64
    if damage == "writer":
        record["writer_count"] = 2
    if damage == "root":
        record["uid"] = 0
    if damage == "mount":
        record["mounts"].append({"source": "/var/run/docker.sock"})
    if damage == "port":
        record["ports"].append({"host_ip": "0.0.0.0", "host_port": 8088, "container_port": 8080})
    if damage == "route":
        record["routing"]["upstream"] = "http://127.0.0.1:9999"
    if damage == "unknown":
        record["Env"] = ["secret"]
    if damage == "config":
        record["configuration_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="qa_ovh"):
        validate_observation(
            record,
            request,
            policy,
            "sha256:" + "e" * 64,
            now=datetime(2026, 11, 15, 12, 0, 20, tzinfo=UTC),
        )


def test_ssh_command_is_fixed_and_private_references_are_required(tmp_path):
    from tools.qa_delivery.ovh_observation import ssh_command

    tmp_path.chmod(0o700)
    for name in ("key", "known_hosts"):
        (tmp_path / name).write_text("synthetic-private-reference")
        (tmp_path / name).chmod(0o600)
    private = dict(
        host="8.8.8.8",
        user="qa-audit",
        port=22,
        known_hosts_sha256=hashlib.sha256((tmp_path / "known_hosts").read_bytes()).hexdigest(),
    )
    refs = dict(identity_file=str(tmp_path / "key"), known_hosts_file=str(tmp_path / "known_hosts"))
    command = ssh_command(private, refs)
    assert command[-1] == "auren-qa-observe-v1"
    assert "StrictHostKeyChecking=yes" in command and "IdentitiesOnly=yes" in command
    assert command[-2] == "qa-audit@8.8.8.8"
    with pytest.raises(ValueError, match="qa_ovh"):
        ssh_command({**private, "host": "host; cat /etc/passwd"}, refs)


@pytest.mark.parametrize(
    "damage",
    [None, "copied_responder", "wrong_peer", "unverified_tls", "swapped_container", "redirect"],
)
def test_public_json_never_substitutes_for_bound_container_route(damage, monkeypatch):
    from test_qa_delivery_releases import candidate

    from tools.qa_delivery.ovh_observation import observe_ovh

    policy, _, record = fixture()
    c = candidate()
    c["target"] = dict(
        provider="OVH",
        url="https://qa.spignos.com",
        environment_id="qa-rel03",
        source_sha="a" * 40,
        configuration_sha256=policy["configuration_sha256"],
        feature_profiles=policy["feature_profiles"],
        ownership_anchor_sha256="0" * 64,
        deployment_reference="ovh:auren-qa-rel03/" + record["image_id"],
    )
    version = dict(
        source_sha="a" * 40,
        environment_id="qa-rel03",
        ownership_anchor_sha256="0" * 64,
        server_schema=c["compatibility"]["server_schema"],
        api_contracts=[c["compatibility"]["api"]],
        inventory=c["compatibility"]["inventory"],
        data_scope="SYNTHETIC_ONLY",
        feature_profiles=policy["feature_profiles"],
        packaging_digest="1" * 64,
        authority={"generation": 3},
    )
    proof = dict(
        provider={
            "kind": "OVH",
            "image_reference": {},
            "ssh": {"host": policy["peer_ip"]},
            "policy": policy,
        },
        version=version,
    )
    calls = []

    def ssh(_, request):
        calls.append("ssh")
        result = deepcopy(record)
        result.update(
            nonce=request["nonce"],
            candidate_sha256=request["candidate_sha256"],
            observed_at=datetime.now(UTC).isoformat(),
        )
        if damage == "copied_responder":
            result["routing"]["upstream"] = "http://127.0.0.1:9999"
        if damage == "swapped_container" and len(calls) > 2:
            result["container_id"] = "0" * 64
            result["routing"]["container_id"] = "0" * 64
        return result

    context = ssl.create_default_context()
    if damage == "unverified_tls":
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

    class Network:
        def get_extra_info(self, name):
            if name == "socket":

                class Socket:
                    def getpeername(self):
                        return ("1.1.1.1" if damage == "wrong_peer" else policy["peer_ip"], 443)

                return Socket()
            if name == "ssl_object":

                class TLS:
                    def getpeercert(self):
                        return {"subject": "synthetic-peer"}

                tls = TLS()
                tls.context = context
                return tls

    def http(request):
        calls.append(request.url.path)
        if damage == "redirect":
            return httpx.Response(302, headers={"location": "https://other.invalid"})
        return httpx.Response(
            200,
            json=version
            if request.url.path == "/__qa_version"
            else {"status": "ok", "transport_only": True},
            extensions={"network_stream": Network()},
        )

    with httpx.Client(transport=httpx.MockTransport(http)) as client:
        if damage:
            with pytest.raises(ValueError, match="qa_ovh_target"):
                observe_ovh(
                    c,
                    proof,
                    client,
                    ssh,
                    lambda *_: {"source_sha": "a" * 40, "image_id": record["image_id"]},
                )
        else:
            assert (
                observe_ovh(
                    c,
                    proof,
                    client,
                    ssh,
                    lambda *_: {"source_sha": "a" * 40, "image_id": record["image_id"]},
                )
                == c["target"]
            )
            assert calls == ["ssh", "/__qa_version", "/__qa_health", "ssh"]


def test_collector_refuses_private_or_extra_mounts_and_changed_loaded_generation():
    from deploy.qa.observe_ovh import project_runtime, verify_loaded_routing

    policy, _, record = fixture()
    host = {
        "Privileged": False,
        "ReadonlyRootfs": True,
        "CapAdd": [],
        "CapDrop": ["ALL"],
        "SecurityOpt": ["no-new-privileges"],
        "Devices": [],
        "PidMode": "",
        "IpcMode": "private",
        "Tmpfs": {"/tmp": "rw,noexec,nosuid,size=67108864,mode=1777"},
        "NetworkMode": "auren-qa-rel03-internal",
        "PortBindings": {},
        "PublishAllPorts": False,
        "RestartPolicy": {"Name": "no"},
        "Memory": policy["memory_bytes"],
        "NanoCpus": policy["nano_cpus"],
        "PidsLimit": policy["pids_limit"],
    }
    container = {
        "Id": record["container_id"],
        "Image": record["image_id"],
        "Name": "/auren-qa-rel03",
        "State": {
            "Running": True,
            "Health": {"Status": "healthy"},
            "StartedAt": "2026-11-15T12:00:00Z",
        },
        "HostConfig": host,
        "Config": {
            "User": "10001",
            "Entrypoint": ["python", "-m", "tools.qa_delivery.bootstrap"],
            "Cmd": [
                "--config",
                "/etc/secrets/qa-config.json",
                "--activation",
                "/var/lib/qa/activation.json",
            ],
        },
        "NetworkSettings": {
            "Ports": {"8080/tcp": None},
            "Networks": {policy["network"]: {"IPAddress": "172.23.0.2"}},
        },
        "Mounts": [
            {"Type": x["type"], "Name": x["source"], "Destination": x["destination"], "RW": x["rw"]}
            for x in policy["mounts"]
        ],
    }
    activation = {
        "container_id": record["container_id"],
        "image_id": record["image_id"],
        "started_at": container["State"]["StartedAt"],
        "configuration_sha256": policy["configuration_sha256"],
    }
    assert (
        project_runtime(policy, activation, container, [record["container_id"][:12]])["image_id"]
        == record["image_id"]
    )
    unexpected = {**policy, "unexpected_private": "SYNTHETIC_SENTINEL_NEVER_EMIT"}
    with pytest.raises(ValueError, match="qa_ovh"):
        project_runtime(unexpected, activation, container, [record["container_id"][:12]])
    wrong_command = deepcopy(container)
    wrong_command["Config"]["Entrypoint"] = ["python", "-m", "tools.qa_delivery.server"]
    wrong_command["Config"]["Cmd"] = ["--facade-only"]
    with pytest.raises(ValueError, match="qa_ovh_collector"):
        project_runtime(policy, activation, wrong_command, [record["container_id"][:12]])
    container["Mounts"].append({"Type": "bind", "Destination": "/var/run/docker.sock", "RW": True})
    with pytest.raises(ValueError):
        project_runtime(policy, activation, container, [record["container_id"][:12]])
    loaded = {
        "configuration_sha256": policy["routing_sha256"],
        "master": {"pid": 10, "start_ticks": 10},
        "workers": [{"pid": 11, "start_ticks": 11}],
        "qa_vhost": "arbitrary responder",
    }
    with pytest.raises(ValueError):
        verify_loaded_routing(
            policy,
            loaded,
            b"copied-version-upstream",
            {"master": loaded["master"], "workers": loaded["workers"]},
        )
