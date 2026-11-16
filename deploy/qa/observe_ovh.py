#!/usr/bin/env python3
"""Install only under distinct administrator authorization, outside app checkout.

Forced command: /usr/local/libexec/auren-qa-observe-v1. No arguments are accepted.
Administrator pins root-owned policy, activation proof and loaded nginx generation.
This is not attestation against a compromised administrator or host.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

POLICY = Path("/etc/auren-qa/observer-policy.json")
ACTIVATION = Path("/etc/auren-qa/activation-proof.json")
ROUTING = Path("/etc/auren-qa/routing-loaded.json")
RESOURCE = "auren-qa-rel03"


def require(ok):
    if not ok:
        raise ValueError("qa_ovh_collector_refused")


def admin_json(path):
    require(not any(p.is_symlink() for p in (path, *path.parents)))
    for parent in path.parents:
        info = parent.stat()
        require(info.st_uid == 0 and info.st_mode & 0o022 == 0)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd) as stream:
        info = os.fstat(stream.fileno())
        require(
            stat.S_ISREG(info.st_mode)
            and info.st_uid == 0
            and info.st_mode & 0o022 == 0
            and info.st_size <= 65536
        )
        return json.load(stream)


def fixed_read(args, maximum=65536):
    # All call sites pass fixed executables/commands; no user-provided shell.
    with __import__("tempfile").TemporaryFile() as output:
        child = subprocess.Popen(  # noqa: S603 — fixed administrator readonly command table, no shell
            args,
            stdout=output,
            stderr=subprocess.DEVNULL,  # noqa: S603 — fixed readonly command table
            env={"PATH": "/usr/sbin:/usr/bin:/sbin:/bin"},
        )
        try:
            import time

            deadline = time.monotonic() + 4
            while child.poll() is None:
                require(output.tell() <= maximum and time.monotonic() < deadline)
                time.sleep(0.02)
            require(child.returncode == 0 and output.tell() <= maximum)
            output.seek(0)
            return output.read(maximum + 1)
        finally:
            if child.poll() is None:
                child.kill()
            child.wait()


def process_identity(pid):
    require(type(pid) is int and pid > 1)
    # Linux start ticks distinguish PID reuse. Children generation pins reloads.
    raw = Path(f"/proc/{pid}/stat").read_text()
    tail = raw[raw.rindex(")") + 2 :].split()
    return {"pid": pid, "start_ticks": int(tail[19])}


def verify_loaded_routing(policy, loaded, config, identities):
    require(set(loaded) == {"configuration_sha256", "master", "workers", "qa_vhost"})
    require(
        hashlib.sha256(config).hexdigest()
        == loaded["configuration_sha256"]
        == policy["routing_sha256"]
    )
    require(loaded["master"] == identities["master"] and loaded["workers"] == identities["workers"])
    # The single closed vhost forbids alternate /__qa_version or /api upstreams.
    expected = """server {
    listen 443 ssl;
    server_name qa.spignos.com;
    ssl_certificate /etc/letsencrypt/live/qa.spignos.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/qa.spignos.com/privkey.pem;
    location / {
        proxy_pass http://127.0.0.1:8088;
        proxy_set_header Host qa.spignos.com;
        proxy_set_header X-Forwarded-Proto https;
    }
}
"""
    require(loaded["qa_vhost"] == expected)
    text = config.decode("utf-8")
    marker = "# configuration file /etc/nginx/conf.d/auren-qa-rel03.conf:\n"
    require(text.count(marker) == 1)
    section = text.split(marker, 1)[1].split("# configuration file ", 1)[0].strip() + "\n"
    require(
        section == expected
        and len(re.findall(r"\bserver_name\s+[^;]*\bqa\.spignos\.com\b", text)) == 1
    )


def project_runtime(policy, activation, container, writers):
    """Pure projection; caller supplies actually acquired fixed-command output."""
    state, host = container["State"], container["HostConfig"]
    require(container["Name"] == "/" + RESOURCE and state["Running"] is True)
    require(state["Health"]["Status"] == "healthy")
    require(container["Config"]["User"] == "10001" and not host["Privileged"])
    require(container["Config"]["Entrypoint"] == ["python", "-m", "tools.qa_delivery.bootstrap"])
    require(
        container["Config"]["Cmd"]
        == [
            "--config",
            "/etc/secrets/qa-config.json",
            "--activation",
            "/var/lib/qa/activation.json",
        ]
    )
    require(
        host["ReadonlyRootfs"] is True
        and host["CapAdd"] in (None, [])
        and host["CapDrop"] == ["ALL"]
        and "no-new-privileges" in host["SecurityOpt"]
    )
    require(
        host["Devices"] in (None, []) and host["PidMode"] == "" and host["IpcMode"] == "private"
    )
    require(host["Tmpfs"] == {"/tmp": "rw,noexec,nosuid,size=67108864,mode=1777"})  # noqa: S108 — bounded container tmpfs policy, no host temp path
    require(host["NetworkMode"] == policy["network"])
    require(host["PortBindings"] == {"8080/tcp": [{"HostIp": "127.0.0.1", "HostPort": "8088"}]})
    require(set(container["NetworkSettings"]["Ports"]) == {"8080/tcp"})
    mounts = [
        {
            "type": m["Type"],
            "source": m.get("Name", ""),
            "destination": m["Destination"],
            "rw": m["RW"],
        }
        for m in container["Mounts"]
    ]
    require(
        sorted(mounts, key=lambda m: m["destination"])
        == sorted(policy["mounts"], key=lambda m: m["destination"])
    )
    require(set(activation) == {"container_id", "image_id", "started_at", "configuration_sha256"})
    require(
        activation
        == {
            "container_id": container["Id"],
            "image_id": container["Image"],
            "started_at": state["StartedAt"],
            "configuration_sha256": policy["configuration_sha256"],
        }
    )
    require(len(writers) == 1 and container["Id"].startswith(writers[0]))
    return {
        **{k: v for k, v in policy.items() if k not in {"resource", "origin", "peer_ip"}},
        "container_id": container["Id"],
        "image_id": container["Image"],
        "running": True,
        "health": "healthy",
        "writer_count": 1,
        "uid": 10001,
        "mounts": policy["mounts"],
        "ports": policy["ports"],
        "restart_policy": host["RestartPolicy"]["Name"],
        "memory_bytes": host["Memory"],
        "nano_cpus": host["NanoCpus"],
        "pids_limit": host["PidsLimit"],
        "routing": {
            "origin": policy["origin"],
            "peer_ip": policy["peer_ip"],
            "container_id": container["Id"],
            "upstream": "http://127.0.0.1:8088",
            "loaded_configuration_sha256": policy["routing_sha256"],
        },
    }


def collect(request):
    require(os.geteuid() == 0)
    require(
        set(request)
        == {"schema_version", "nonce", "candidate_sha256", "environment_id", "resource"}
    )
    require(
        request["schema_version"] == "qa-ovh-observation-request/1.0.0"
        and request["resource"] == RESOURCE
    )
    require(
        all(
            isinstance(request[k], str) and re.fullmatch("[a-f0-9]{64}", request[k])
            for k in ("nonce", "candidate_sha256")
        )
    )
    policy = admin_json(POLICY)
    require(request["environment_id"] == policy["environment_id"])
    fields = (
        "Privileged",
        "ReadonlyRootfs",
        "CapAdd",
        "CapDrop",
        "SecurityOpt",
        "Devices",
        "PidMode",
        "IpcMode",
        "Tmpfs",
        "NetworkMode",
        "PortBindings",
        "RestartPolicy",
        "Memory",
        "NanoCpus",
        "PidsLimit",
    )
    host = ",".join('"' + name + '":{{json .HostConfig.' + name + "}}" for name in fields)
    projection = (
        '{"Id":{{json .Id}},"Name":{{json .Name}},"Image":{{json .Image}},"State":{"Running":{{json .State.Running}},"StartedAt":{{json .State.StartedAt}},"Health":{"Status":{{json .State.Health.Status}}}},"HostConfig":{'
        + host
        + '},"Mounts":{{json .Mounts}},"Config":{"User":{{json .Config.User}},"Entrypoint":{{json .Config.Entrypoint}},"Cmd":{{json .Config.Cmd}}},"NetworkSettings":{"Ports":{{json .NetworkSettings.Ports}}}}'
    )
    container = json.loads(
        fixed_read(["/usr/bin/docker", "inspect", "--format", projection, RESOURCE])
    )
    container = [container]
    require(len(container) == 1)
    container = container[0]
    writers = (
        fixed_read(
            [
                "/usr/bin/docker",
                "ps",
                "--filter",
                "volume=auren-qa-rel03-data",
                "--format",
                "{{.ID}}",
            ]
        )
        .decode()
        .splitlines()
    )
    result = project_runtime(policy, admin_json(ACTIVATION), container, writers)
    loaded = admin_json(ROUTING)
    master = int(Path("/run/nginx.pid").read_text().strip())
    children = Path(f"/proc/{master}/task/{master}/children").read_text().split()
    identities = {
        "master": process_identity(master),
        "workers": [process_identity(int(p)) for p in children],
    }
    verify_loaded_routing(
        policy, loaded, fixed_read(["/usr/sbin/nginx", "-T"], 1024 * 1024), identities
    )
    return {
        **result,
        "schema_version": "qa-ovh-observation/1.0.0",
        "nonce": request["nonce"],
        "candidate_sha256": request["candidate_sha256"],
        "observed_at": datetime.now(UTC).isoformat(),
    }


def main():
    try:
        require(
            len(sys.argv) == 1
            and os.environ.get("SSH_ORIGINAL_COMMAND", "auren-qa-observe-v1")
            == "auren-qa-observe-v1"
        )
        raw = sys.stdin.buffer.read(4097)
        require(len(raw) <= 4096)
        response = json.dumps(collect(json.loads(raw)), sort_keys=True).encode()
        require(len(response) <= 65536)
        sys.stdout.buffer.write(response)
    except (ValueError, OSError, KeyError, TypeError, AttributeError):
        print("qa_ovh_collector_refused", file=sys.stderr)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
