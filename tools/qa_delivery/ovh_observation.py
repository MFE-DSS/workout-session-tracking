"""Bounded authenticated readonly OVH observations. Never install or deploy.

The qualified administrator/host and pinned SSH identity are explicit trust
assumptions. Neither an app label nor copied public JSON substitutes for routing.
"""

from __future__ import annotations

import hashlib
import ipaddress
import json
import os
import re
import selectors
import shutil
import ssl
import subprocess
import time
from datetime import UTC, datetime

import httpx

RESOURCE = "auren-qa-rel03"
ORIGIN = "https://qa.spignos.com"
MAX_OUTPUT = 64 * 1024
POLICY_KEYS = {
    "environment_id",
    "resource",
    "origin",
    "peer_ip",
    "uid",
    "mounts",
    "ports",
    "network",
    "restart_policy",
    "memory_bytes",
    "nano_cpus",
    "pids_limit",
    "configuration_sha256",
    "routing_sha256",
    "feature_profiles",
}
REQUEST_KEYS = {"schema_version", "nonce", "candidate_sha256", "environment_id", "resource"}
OBSERVATION_KEYS = (POLICY_KEYS - {"resource", "origin", "peer_ip"}) | {
    "schema_version",
    "nonce",
    "candidate_sha256",
    "observed_at",
    "container_id",
    "image_id",
    "running",
    "health",
    "writer_count",
    "routing",
}


def require(ok):
    if not ok:
        raise ValueError("qa_ovh_observation_refused")


def _hex(value, size=64):
    return isinstance(value, str) and re.fullmatch(f"[a-f0-9]{{{size}}}", value) is not None


def validate_policy(policy):
    require(isinstance(policy, dict) and set(policy) == POLICY_KEYS)
    require(policy["origin"] == ORIGIN and policy["resource"] == RESOURCE)
    require(re.fullmatch("qa-[a-z0-9_-]{3,60}", policy["environment_id"]))
    ip = ipaddress.ip_address(policy["peer_ip"])
    require(
        not ip.is_loopback and not ip.is_private and not ip.is_multicast and not ip.is_unspecified
    )
    require(policy["uid"] == 10001 and type(policy["uid"]) is int)
    require(policy["network"] == "auren-qa-rel03-internal" and policy["restart_policy"] == "no")
    require(
        policy["mounts"]
        == [
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
        ]
    )
    require(
        policy["ports"] == [{"host_ip": "127.0.0.1", "host_port": 8088, "container_port": 8080}]
    )
    require(_hex(policy["configuration_sha256"]) and _hex(policy["routing_sha256"]))
    for key, upper in [
        ("memory_bytes", 2 * 1024**3),
        ("nano_cpus", 2 * 10**9),
        ("pids_limit", 256),
    ]:
        require(type(policy[key]) is int and 0 < policy[key] <= upper)
    from tools.qa_delivery.releases import FEATURE_PROFILES

    require(policy["feature_profiles"] == FEATURE_PROFILES)
    return policy


def validate_request(request):
    require(isinstance(request, dict) and set(request) == REQUEST_KEYS)
    require(
        request["schema_version"] == "qa-ovh-observation-request/1.0.0"
        and request["resource"] == RESOURCE
        and _hex(request["nonce"])
        and _hex(request["candidate_sha256"])
        and re.fullmatch("qa-[a-z0-9_-]{3,60}", request["environment_id"])
    )
    return request


def validate_observation(record, request, policy, image_id, now=None):
    try:
        validate_request(request)
        validate_policy(policy)
        require(isinstance(record, dict) and set(record) == OBSERVATION_KEYS)
        require(record["schema_version"] == "qa-ovh-observation/1.0.0")
        require(
            record["nonce"] == request["nonce"]
            and record["candidate_sha256"] == request["candidate_sha256"]
        )
        observed = datetime.fromisoformat(record["observed_at"].replace("Z", "+00:00"))
        require(observed.utcoffset() is not None)
        age = ((now or datetime.now(UTC)) - observed).total_seconds()
        require(-10 <= age <= 60)
        require(
            _hex(record["container_id"])
            and record["image_id"] == image_id
            and re.fullmatch("sha256:[a-f0-9]{64}", image_id)
        )
        require(
            record["running"] is True
            and record["health"] == "healthy"
            and type(record["writer_count"]) is int
            and record["writer_count"] == 1
        )
        for key in POLICY_KEYS - {"resource", "origin", "peer_ip"}:
            require(record[key] == policy[key])
        require(record["environment_id"] == request["environment_id"])
        require(
            record["routing"]
            == {
                "origin": ORIGIN,
                "peer_ip": policy["peer_ip"],
                "container_id": record["container_id"],
                "upstream": "http://127.0.0.1:8088",
                "loaded_configuration_sha256": policy["routing_sha256"],
            }
        )
        return record
    except (ValueError, TypeError, KeyError, AttributeError):
        raise ValueError("qa_ovh_observation_refused") from None


def ssh_command(private, references=None):
    try:
        require(set(private) == {"host", "user", "port", "known_hosts_sha256"})
        references = references or {
            "identity_file": os.environ.get("AUREN_QA_OVH_IDENTITY_FILE", ""),
            "known_hosts_file": os.environ.get("AUREN_QA_OVH_KNOWN_HOSTS_FILE", ""),
        }
        require(
            set(references) == {"identity_file", "known_hosts_file"}
            and _hex(private["known_hosts_sha256"])
        )
        require(str(ipaddress.ip_address(private["host"])) == private["host"])
        require(
            private["user"] == "qa-audit" and type(private["port"]) is int and private["port"] == 22
        )
        from tools.qa_delivery.server import _private_feature_text

        for key in ("identity_file", "known_hosts_file"):
            require(bool(_private_feature_text(references[key]).strip()))
        require(
            hashlib.sha256(
                _private_feature_text(references["known_hosts_file"]).encode()
            ).hexdigest()
            == private["known_hosts_sha256"]
        )
        executable = shutil.which("ssh")
        require(executable)
        return [
            executable,
            "-F",
            "/dev/null",
            "-T",
            "-o",
            "BatchMode=yes",
            "-o",
            "StrictHostKeyChecking=yes",
            "-o",
            "GlobalKnownHostsFile=/dev/null",
            "-o",
            "UserKnownHostsFile=" + references["known_hosts_file"],
            "-o",
            "IdentitiesOnly=yes",
            "-o",
            "IdentityAgent=none",
            "-o",
            "ForwardAgent=no",
            "-o",
            "ClearAllForwardings=yes",
            "-o",
            "ProxyCommand=none",
            "-o",
            "ProxyJump=none",
            "-o",
            "ConnectTimeout=5",
            "-o",
            "ConnectionAttempts=1",
            "-o",
            "LogLevel=ERROR",
            "-i",
            references["identity_file"],
            "-p",
            "22",
            "qa-audit@" + private["host"],
            "auren-qa-observe-v1",
        ]
    except (OSError, ValueError, TypeError, KeyError):
        raise ValueError("qa_ovh_ssh_configuration_refused") from None


def bounded_ssh(private, request):
    """Single fixed command, 4KiB stdin, 64KiB stdout, 15s wall clock."""
    validate_request(request)
    payload = json.dumps(request, sort_keys=True).encode()
    require(len(payload) <= 4096)
    command = ssh_command(private)
    child = subprocess.Popen(  # noqa: S603 — validated fixed SSH argv, no shell
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,  # noqa: S603 — validated fixed SSH/command
        env={"PATH": os.environ.get("PATH", "/usr/bin:/bin")},
    )
    try:
        child.stdin.write(payload)
        child.stdin.close()
        deadline = time.monotonic() + 15
        data = bytearray()
        with selectors.DefaultSelector() as selector:
            selector.register(child.stdout, selectors.EVENT_READ)
            while True:
                remaining = deadline - time.monotonic()
                require(remaining > 0)
                ready = selector.select(remaining)
                require(ready)
                chunk = os.read(child.stdout.fileno(), min(8192, MAX_OUTPUT + 1 - len(data)))
                if not chunk:
                    break
                data.extend(chunk)
                require(len(data) <= MAX_OUTPUT)
        require(child.wait(timeout=max(0.01, deadline - time.monotonic())) == 0)
        from tools.qa_delivery.image_receipts import _pairs

        return json.loads(data, object_pairs_hook=_pairs)
    except (OSError, ValueError, subprocess.SubprocessError):
        raise ValueError("qa_ovh_ssh_observation_failed") from None
    finally:
        if child.poll() is None:
            child.kill()
        child.wait()
        child.stdout.close()


def observe_ovh(candidate, proof, client, ssh_runner=bounded_ssh, image_acquirer=None):
    from tools.qa_delivery.image_receipts import acquire_image_receipt
    from tools.qa_delivery.pipeline import digest

    try:
        target = candidate["target"]
        provider = proof["provider"]
        require(set(provider) == {"kind", "image_reference", "ssh", "policy"})
        require(provider["kind"] == "OVH" and target["provider"] == "OVH")
        policy = validate_policy(provider["policy"])
        require(
            provider["ssh"]["host"] == policy["peer_ip"]
            and target["url"] == ORIGIN
            and target["configuration_sha256"] == policy["configuration_sha256"]
            and target["feature_profiles"] == policy["feature_profiles"]
            and target["environment_id"] == policy["environment_id"]
        )
        image = (image_acquirer or acquire_image_receipt)(
            provider["image_reference"], client, os.environ.get("GH_TOKEN", "")
        )
        require(image["source_sha"] == target["source_sha"])
        require(target["deployment_reference"] == "ovh:" + RESOURCE + "/" + image["image_id"])

        def observe():
            request = {
                "schema_version": "qa-ovh-observation-request/1.0.0",
                "nonce": os.urandom(32).hex(),
                "candidate_sha256": digest(candidate),
                "environment_id": target["environment_id"],
                "resource": RESOURCE,
            }
            return validate_observation(
                ssh_runner(provider["ssh"], request), request, policy, image["image_id"]
            )

        before = observe()

        def get(path):
            with client.stream(
                "GET", ORIGIN + path, follow_redirects=False, timeout=15
            ) as response:
                require(response.status_code == 200)
                stream = response.extensions.get("network_stream")
                require(stream is not None)
                sock = stream.get_extra_info("socket")
                tls = stream.get_extra_info("ssl_object")
                require(
                    sock is not None
                    and tls is not None
                    and tls.context.check_hostname
                    and tls.context.verify_mode == ssl.CERT_REQUIRED
                    and bool(tls.getpeercert())
                )
                require(str(ipaddress.ip_address(sock.getpeername()[0])) == policy["peer_ip"])
                data = bytearray()
                for part in response.iter_bytes():
                    data.extend(part)
                    require(len(data) <= MAX_OUTPUT)
                from tools.qa_delivery.image_receipts import _pairs

                return json.loads(data, object_pairs_hook=_pairs)

        version = get("/__qa_version")
        require(version == proof["version"])
        require(
            version["source_sha"] == target["source_sha"]
            and version["environment_id"] == target["environment_id"]
            and version["ownership_anchor_sha256"] == target["ownership_anchor_sha256"]
            and version["server_schema"] == candidate["compatibility"]["server_schema"]
            and version["api_contracts"] == [candidate["compatibility"]["api"]]
            and version["inventory"] == candidate["compatibility"]["inventory"]
            and version["data_scope"] == "SYNTHETIC_ONLY"
            and version["feature_profiles"] == policy["feature_profiles"]
            and _hex(version["packaging_digest"])
            and type(version["authority"]["generation"]) is int
            and version["authority"]["generation"] > 0
        )
        require(get("/__qa_health") == {"status": "ok", "transport_only": True})
        after = observe()
        ignore = {"nonce", "observed_at"}
        require(
            {k: v for k, v in before.items() if k not in ignore}
            == {k: v for k, v in after.items() if k not in ignore}
        )
        return target
    except (OSError, ValueError, KeyError, TypeError, AttributeError, httpx.HTTPError):
        raise ValueError("qa_ovh_target_proof_required") from None
