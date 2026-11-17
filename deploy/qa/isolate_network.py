#!/usr/bin/env python3
"""Fixed QA-only isolation installer/checker, after operational authorization.

Never run for an existing personal network. No daemon configuration or global
firewall policy changes. A conflicting preexisting resource fails closed.
"""

import argparse
import json
import os
import subprocess

NETWORK = "auren-qa-rel03-internal"
HOOK = "-A INPUT -i br-auren-qa -j AUREN-QA-IN"
CHAIN = [
    "-N AUREN-QA-IN",
    "-A AUREN-QA-IN -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT",
    "-A AUREN-QA-IN -j DROP",
]


def command(args, *, optional=False):
    result = subprocess.run(  # noqa: S603 — fixed root command table, no shell or request args
        args,
        capture_output=True,
        timeout=15,
        check=False,
        env={"PATH": "/usr/sbin:/usr/bin:/sbin:/bin"},
    )  # noqa: S603 — fixed root administrator command table, no shell
    if result.returncode and not optional:
        raise ValueError("qa_isolation_command_failed")
    if len(result.stdout) > 1024 * 1024:
        raise ValueError("qa_isolation_output_refused")
    return result


def check_shape(n):
    if not (
        n["Name"] == NETWORK
        and n["Driver"] == "bridge"
        and n["Scope"] == "local"
        and n["Internal"] is True
        and n["EnableIPv6"] is False
        and n.get("Labels", {}).get("org.auren.qa") == "rel03"
        and n["Options"].get("com.docker.network.bridge.name") == "br-auren-qa"
        and n["Options"].get("com.docker.network.bridge.enable_icc") == "false"
    ):
        raise ValueError("qa_isolation_resource_conflict")


def check_rules(input_rules, qa_rules):
    rules = [r for r in input_rules.splitlines() if r.startswith("-A INPUT ")]
    normalized = qa_rules.replace("ESTABLISHED,RELATED", "RELATED,ESTABLISHED").splitlines()
    if not rules or rules[0] != HOOK or rules.count(HOOK) != 1 or normalized != CHAIN:
        raise ValueError("qa_isolation_firewall_conflict")


def execute(apply=False):
    if os.geteuid() != 0:
        raise ValueError("qa_isolation_root_required")
    # Enumerate first: a failed inspect is never interpreted as permission to
    # overwrite a resource or silently continue after a daemon failure.
    names = (
        command(["/usr/bin/docker", "network", "ls", "--format", "{{.Name}}"])
        .stdout.decode()
        .splitlines()
    )
    if NETWORK not in names:
        if not apply:
            raise ValueError("qa_isolation_absent")
        command(
            [
                "/usr/bin/docker",
                "network",
                "create",
                "--internal",
                "--driver",
                "bridge",
                "--opt",
                "com.docker.network.bridge.name=br-auren-qa",
                "--opt",
                "com.docker.network.bridge.enable_icc=false",
                "--label",
                "org.auren.qa=rel03",
                NETWORK,
            ]
        )
    network = json.loads(command(["/usr/bin/docker", "network", "inspect", NETWORK]).stdout)
    if len(network) != 1:
        raise ValueError("qa_isolation_resource_conflict")
    check_shape(network[0])
    all_rules = command(["/usr/sbin/iptables", "-S"]).stdout.decode()
    if "-N AUREN-QA-IN" not in all_rules.splitlines():
        if not apply:
            raise ValueError("qa_isolation_absent")
        command(["/usr/sbin/iptables", "-N", "AUREN-QA-IN"])
        command(
            [
                "/usr/sbin/iptables",
                "-A",
                "AUREN-QA-IN",
                "-m",
                "conntrack",
                "--ctstate",
                "RELATED,ESTABLISHED",
                "-j",
                "ACCEPT",
            ]
        )
        command(["/usr/sbin/iptables", "-A", "AUREN-QA-IN", "-j", "DROP"])
    qa_rules = command(["/usr/sbin/iptables", "-S", "AUREN-QA-IN"]).stdout.decode()
    if qa_rules.replace("ESTABLISHED,RELATED", "RELATED,ESTABLISHED").splitlines() != CHAIN:
        raise ValueError("qa_isolation_firewall_conflict")
    inputs = command(["/usr/sbin/iptables", "-S", "INPUT"]).stdout.decode()
    if HOOK not in inputs.splitlines():
        if not apply:
            raise ValueError("qa_isolation_absent")
        command(
            ["/usr/sbin/iptables", "-I", "INPUT", "1", "-i", "br-auren-qa", "-j", "AUREN-QA-IN"]
        )
    check_rules(command(["/usr/sbin/iptables", "-S", "INPUT"]).stdout.decode(), qa_rules)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        execute(args.apply)
        print("QA_ISOLATION_CHECKED" if not args.apply else "QA_ISOLATION_APPLIED")
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError):
        parser.exit(1, "qa_isolation_refused\n")


if __name__ == "__main__":
    main()
