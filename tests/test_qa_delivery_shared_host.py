"""Shared-host isolation/routing witnesses; no remote firewall modifications."""

import hashlib
from copy import deepcopy

import pytest

from deploy.qa.observe_ovh import qa_vhost, verify_loaded_routing, verify_network
from tests.test_qa_delivery_ovh_observation import fixture


def network_fixture():
    policy, _, _ = fixture()
    container = {
        "Id": "f" * 64,
        "NetworkSettings": {"Networks": {policy["network"]: {"NetworkID": "a" * 64}}},
    }
    network = {
        "Id": "a" * 64,
        "Name": policy["network"],
        "Driver": "bridge",
        "Scope": "local",
        "Internal": True,
        "EnableIPv6": False,
        "Labels": {"org.auren.qa": "rel03"},
        "Containers": {container["Id"]: {}},
        "Options": {
            "com.docker.network.bridge.name": "br-auren-qa",
            "com.docker.network.bridge.enable_icc": "false",
        },
    }
    input_rules = b"-P INPUT ACCEPT\n-A INPUT -i br-auren-qa -j AUREN-QA-IN\n-A INPUT -j OTHER\n"
    qa_rules = b"-N AUREN-QA-IN\n-A AUREN-QA-IN -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT\n-A AUREN-QA-IN -j DROP\n"
    return policy, container, network, input_rules, qa_rules


def test_dedicated_internal_network_and_host_filter_are_both_required():
    policy, container, network, input_rules, qa_rules = network_fixture()
    verify_network(policy, container, network, input_rules, qa_rules)
    for damage in (
        "default",
        "external",
        "extra",
        "host_filter",
        "early_accept",
        "ipv6",
        "gateway",
    ):
        p, c, n, i, q = deepcopy((policy, container, network, input_rules, qa_rules))
        if damage == "default":
            n["Name"] = "bridge"
        if damage == "external":
            n["Internal"] = False
        if damage == "extra":
            c["NetworkSettings"]["Networks"]["other"] = {}
        if damage == "host_filter":
            q = b"-N AUREN-QA-IN\n-A AUREN-QA-IN -j ACCEPT\n"
        if damage == "early_accept":
            i = b"-A INPUT -j ACCEPT\n" + i
        if damage == "ipv6":
            n["EnableIPv6"] = True
        if damage == "gateway":
            n["Options"]["com.docker.network.bridge.name"] = "other"
        with pytest.raises(ValueError):
            verify_network(p, c, n, i, q)


def test_shared_host_vhost_uses_public_address_and_no_request_logging():
    policy, _, _ = fixture()
    text = qa_vhost(policy)
    assert "listen 8.8.8.8:443 ssl;" in text
    assert "listen 443 ssl;" not in text
    assert "access_log off;" in text
    assert "location ^~ /.well-known/acme-challenge/" in text
    assert text.count("server_name qa.spignos.com;") == 2
    config = ("# configuration file /etc/nginx/conf.d/auren-qa-rel03.conf:\n" + text).encode()
    policy["routing_sha256"] = hashlib.sha256(config).hexdigest()
    identities = {
        "master": {"pid": 10, "start_ticks": 12},
        "workers": [{"pid": 11, "start_ticks": 13}],
    }
    loaded = {"configuration_sha256": policy["routing_sha256"], **identities, "qa_vhost": text}
    verify_loaded_routing(policy, loaded, config, identities)
    wildcard = config.replace(b"listen 8.8.8.8:443", b"listen 443")
    loaded["configuration_sha256"] = policy["routing_sha256"] = hashlib.sha256(wildcard).hexdigest()
    loaded["qa_vhost"] = wildcard.decode().split("\n", 1)[1]
    with pytest.raises(ValueError):
        verify_loaded_routing(policy, loaded, wildcard, identities)


def test_isolation_checker_never_repairs_or_flushes_existing_foreign_rules(monkeypatch):
    import subprocess

    from deploy.qa import isolate_network as installer

    policy, container, network, _, _ = network_fixture()
    network["Labels"] = {"org.auren.qa": "rel03"}
    calls = []

    def command(args, **kwargs):
        import json

        calls.append(args)
        if args[1:] == ["network", "ls", "--format", "{{.Name}}"]:
            return subprocess.CompletedProcess(args, 0, stdout=(policy["network"] + "\n").encode())
        if args[1] == "network":
            return subprocess.CompletedProcess(args, 0, stdout=json.dumps([network]).encode())
        return subprocess.CompletedProcess(
            args, 0, stdout=b"-N AUREN-QA-IN\n-A AUREN-QA-IN -j ACCEPT\n"
        )

    monkeypatch.setattr(installer.os, "geteuid", lambda: 0)
    monkeypatch.setattr(installer, "command", command)
    with pytest.raises(ValueError, match="conflict"):
        installer.execute(apply=True)
    assert all("-S" in c or c[1] == "network" for c in calls)
    assert not any("-F" in c or "-A" in c or "-I" in c for c in calls)
