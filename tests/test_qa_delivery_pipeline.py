"""Real gate consumers with synthetic external API responses, no external writes."""

from __future__ import annotations

import hashlib
import json
import subprocess
from copy import deepcopy
from pathlib import Path

import httpx
import pytest
from test_qa_delivery_releases import approved, candidate

SHA = "a" * 40


@pytest.fixture
def checkout(tmp_path):
    root = tmp_path / "source"
    root.mkdir()
    storage = root / "clients/mobile/src/storage"
    storage.mkdir(parents=True)
    (storage / "journal.ts").write_text("CREATE TABLE journal(id INTEGER)")
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "add", "."], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.invalid",
            "commit",
            "-qm",
            "source",
        ],
        check=True,
    )
    return root


def test_prepare_without_credentials_is_pending_and_derives_storage_from_git(checkout):
    from tools.qa_delivery.pipeline import prepare
    from tools.qa_delivery.releases import storage_schema_digest

    raw = candidate()
    result = prepare(raw, checkout)
    assert result["state"] == "PREPARED"
    assert result["distributable"] is False
    assert result["target"] is None
    assert result["native"]["storage_schema_sha256"] == storage_schema_digest(checkout)
    assert (
        result["source"]["js_sha"]
        == subprocess.check_output(
            ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True
        ).strip()
    )
    (checkout / "new.txt").write_text("dirty")
    with pytest.raises(ValueError, match="qa_pipeline_source_dirty"):
        prepare(raw, checkout)


def github_payloads(c):
    from tools.qa_delivery.pipeline import FLOOR

    return {
        "": {"default_branch": "trunk"},
        "branches/trunk": {"commit": {"sha": SHA}},
        "branches/trunk/protection": {
            "required_status_checks": {
                "checks": [{"context": n, "app_id": 15368} for n in FLOOR],
                "contexts": list(FLOOR),
            }
        },
        f"commits/{SHA}/check-runs?per_page=100": {
            "check_runs": [
                {
                    "name": n,
                    "head_sha": SHA,
                    "status": "completed",
                    "conclusion": "success",
                    "app": {"id": 15368},
                    "details_url": "https://github.com/MFE-DSS/workout-session-tracking/actions/runs/123/job/1",
                }
                for n in FLOOR
            ]
        },
        "environments/qa-release": {
            "id": 42,
            "name": "qa-release",
            "protection_rules": [
                {
                    "type": "required_reviewers",
                    "prevent_self_review": True,
                    "reviewers": [{"type": "User", "reviewer": {"id": 11, "login": "operator"}}],
                }
            ],
        },
        "actions/runs/456": {
            "id": 456,
            "event": "workflow_dispatch",
            "status": "in_progress",
            "head_sha": SHA,
            "run_attempt": 1,
            "path": ".github/workflows/qa-release.yml",
            "actor": {"id": 22},
        },
        "actions/runs/456/approvals": [
            {
                "state": "approved",
                "comment": "APPROVE_QA candidate-hash proof-hash",
                "user": {"id": 11, "login": "operator", "type": "User"},
                "environments": [{"id": 42, "name": "qa-release"}],
            }
        ],
        "actions/runs/456/pending_deployments": [],
        f"deployments?sha={SHA}&environment=qa-release&per_page=100": [
            {"id": 99, "sha": SHA, "environment": "qa-release"}
        ],
        "deployments/99/statuses?per_page=100": [
            {
                "state": "in_progress",
                "log_url": "https://github.com/MFE-DSS/workout-session-tracking/actions/runs/456/job/1",
            }
        ],
    }


@pytest.mark.parametrize(
    "damage",
    [
        "event",
        "empty_reviewers",
        "pending",
        "missing_approval",
        "wrong_candidate",
        "self_review",
        "run_sha",
        "ci_sha",
        "ci_red",
        "spoof_app",
        "no_deployment",
        "dispatch_missing",
        "protection_unavailable",
    ],
)
def test_github_preflight_refuses_missing_real_policy_ci_or_run_approval(damage):
    from tools.qa_delivery.pipeline import GitHubGate

    c, _ = approved()
    data = github_payloads(c)
    env = {
        "GITHUB_ACTIONS": "true",
        "GITHUB_EVENT_NAME": "workflow_dispatch",
        "GITHUB_RUN_ID": "456",
        "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_REPOSITORY": "MFE-DSS/workout-session-tracking",
    }
    if damage == "event":
        data["actions/runs/456"]["event"] = "push"
    if damage == "empty_reviewers":
        data["environments/qa-release"]["protection_rules"] = []
    if damage == "pending":
        data["actions/runs/456/pending_deployments"] = [{"environment": {"id": 42}}]
    if damage == "missing_approval":
        data["actions/runs/456/approvals"] = []
    if damage == "wrong_candidate":
        data["actions/runs/456/approvals"][0]["comment"] = "GO BUILD"
    if damage == "self_review":
        data["actions/runs/456"]["actor"]["id"] = 11
    if damage == "run_sha":
        data["actions/runs/456"]["head_sha"] = "b" * 40
    if damage in {"ci_sha", "ci_red", "spoof_app"}:
        check = data[f"commits/{SHA}/check-runs?per_page=100"]["check_runs"][0]
        if damage == "ci_sha":
            check["head_sha"] = "b" * 40
        if damage == "ci_red":
            check["conclusion"] = "failure"
        if damage == "spoof_app":
            check["app"]["id"] = 1
    if damage == "no_deployment":
        data[f"deployments?sha={SHA}&environment=qa-release&per_page=100"] = []
    if damage == "dispatch_missing":
        env = {}
    if damage == "protection_unavailable":
        del data["branches/trunk/protection"]
    gate = GitHubGate(lambda path: deepcopy(data[path]), env)
    with pytest.raises(ValueError, match="qa_github"):
        gate.collect(c, "candidate-hash", "proof-hash")


def test_github_collects_floor_and_actual_run_bound_approval():
    from tools.qa_delivery.pipeline import FLOOR, GitHubGate

    c, _ = approved()
    data = github_payloads(c)
    env = {
        "GITHUB_ACTIONS": "true",
        "GITHUB_EVENT_NAME": "workflow_dispatch",
        "GITHUB_RUN_ID": "456",
        "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_REPOSITORY": "MFE-DSS/workout-session-tracking",
    }
    result = GitHubGate(lambda path: deepcopy(data[path]), env).collect(
        c, "candidate-hash", "proof-hash"
    )
    assert set(result["ci"]["required_checks"]) == set(FLOOR)
    assert result["approval"]["deployment_id"] == 99
    assert result["approval"]["reviewer"] == "operator"
    assert all(check["head_sha"] == SHA for check in result["ci"]["checks"])


@pytest.mark.parametrize(
    "damage", ["none", "not_live", "source", "url", "disk", "instances", "identity", "tls_redirect"]
)
def test_render_adapter_requires_real_provider_and_tls_identity(damage):
    from tools.qa_delivery.pipeline import observe_target

    c, _ = approved()
    t = c["target"]
    proof = {
        "provider": {
            "service_id": "srv-" + "a" * 20,
            "deploy_id": "dep-" + "b" * 20,
            "branch": "trunk",
        },
        "version": {
            "source_sha": SHA,
            "environment_id": t["environment_id"],
            "server_schema": c["compatibility"]["server_schema"],
            "api_contracts": [c["compatibility"]["api"]],
            "inventory": c["compatibility"]["inventory"],
            "packaging_digest": "c" * 64,
            "authority": {"generation": 3, "state": "WITHDRAWN", "publication": None},
            "data_scope": "SYNTHETIC_ONLY",
            "schema_version": "qa-backend/1.0.0",
        },
    }
    t["deployment_reference"] = (
        f"render:{proof['provider']['service_id']}/{proof['provider']['deploy_id']}"
    )
    service = {
        "repo": "https://github.com/MFE-DSS/workout-session-tracking",
        "branch": "trunk",
        "id": proof["provider"]["service_id"],
        "type": "web_service",
        "suspended": "not_suspended",
        "autoDeploy": "no",
        "serviceDetails": {
            "url": t["url"],
            "numInstances": 1,
            "disk": {"sizeGB": 1, "mountPath": "/var/lib/qa"},
        },
    }
    deploy = {"id": proof["provider"]["deploy_id"], "status": "live", "commit": {"id": SHA}}
    version = deepcopy(proof["version"])
    if damage == "not_live":
        deploy["status"] = "deactivated"
    if damage == "source":
        deploy["commit"]["id"] = "b" * 40
    if damage == "url":
        service["serviceDetails"]["url"] = "https://production.onrender.com"
    if damage == "disk":
        service["serviceDetails"].pop("disk")
    if damage == "instances":
        service["serviceDetails"]["numInstances"] = 2
    if damage == "identity":
        version["authority"]["generation"] = 4

    def respond(req):
        if req.url.host == "api.render.com":
            return httpx.Response(200, json=deploy if "/deploys/" in req.url.path else service)
        if damage == "tls_redirect":
            return httpx.Response(302, headers={"location": "https://production.onrender.com"})
        return httpx.Response(
            200,
            json=version
            if req.url.path.endswith("version")
            else {"status": "ok", "transport_only": True},
        )

    with httpx.Client(transport=httpx.MockTransport(respond), follow_redirects=False) as client:
        if damage == "none":
            assert observe_target(c, proof, "test-token", client)["source_sha"] == SHA
        else:
            with pytest.raises(ValueError, match="qa_target"):
                observe_target(c, proof, "test-token", client)


def test_proof_hash_pins_every_file_and_backup_is_verified_not_presence(tmp_path):
    from tools.qa_delivery.pipeline import proof_digest, verify_continuity

    (tmp_path / "cutover.json").write_text("{}")
    first = proof_digest(tmp_path)
    (tmp_path / "backup.db").write_text("not sqlite")
    assert proof_digest(tmp_path) != first
    with pytest.raises(ValueError, match="qa_continuity"):
        verify_continuity(tmp_path, candidate())


def test_workflow_is_manual_and_publication_has_fixed_environment():
    import yaml

    workflow = yaml.safe_load(
        (Path(__file__).resolve().parents[1] / ".github/workflows/qa-release.yml").read_text()
    )
    triggers = workflow.get("on", workflow.get(True))
    assert set(triggers) == {"workflow_dispatch"}
    assert workflow["jobs"]["release"]["environment"]["name"] == "qa-release"
    assert "EXPO_TOKEN" not in json.dumps(workflow["jobs"]["prepare"])
    assert "write" not in json.dumps(workflow["permissions"])


def test_single_human_candidate_review_follows_existing_self_review_policy():
    from tools.qa_delivery.pipeline import GitHubGate

    c, _ = approved()
    data = github_payloads(c)
    data["environments/qa-release"]["protection_rules"][0]["prevent_self_review"] = False
    data["actions/runs/456"]["actor"]["id"] = 11
    env = {
        "GITHUB_ACTIONS": "true",
        "GITHUB_EVENT_NAME": "workflow_dispatch",
        "GITHUB_RUN_ID": "456",
        "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_REPOSITORY": "MFE-DSS/workout-session-tracking",
    }
    assert (
        GitHubGate(lambda p: data[p], env).collect(c, "candidate-hash", "proof-hash")["approval"][
            "reviewer"
        ]
        == "operator"
    )


@pytest.mark.parametrize("damage", ["missing", "empty", "team_only"])
def test_environment_preflight_before_environment_job_does_not_create_anything(damage):
    from tools.qa_delivery.pipeline import protected_environment

    c, _ = approved()
    data = github_payloads(c)
    environment = data["environments/qa-release"]
    if damage == "empty":
        environment["protection_rules"] = []
    if damage == "team_only":
        environment["protection_rules"][0]["reviewers"][0]["type"] = "Team"

    def get(path):
        assert path == "environments/qa-release"
        if damage == "missing":
            raise ValueError("qa_github_read_failed")
        return environment

    with pytest.raises(ValueError, match="qa_github"):
        protected_environment(get)


@pytest.mark.parametrize("damage", ["plan", "quota", "overage", "shape"])
def test_real_quota_shape_fails_closed_without_paid_auto_upgrade(damage):
    from tools.qa_delivery.pipeline import check_quota

    raw = {
        "account": {"plan": "Free"},
        "builds": {
            "plan": {"used": 5, "limit": 30},
            "android": {"plan": {"used": 5, "limit": 15}},
            "overage": {"count": 0, "costCents": 0},
        },
        "updates": {"overageCostCents": 0},
    }
    check_quota(raw, "BUILD_APK")
    if damage == "plan":
        raw["account"]["plan"] = "Starter"
    if damage == "quota":
        raw["builds"]["android"]["plan"]["used"] = 15
    if damage == "overage":
        raw["builds"]["overage"]["costCents"] = 1
    if damage == "shape":
        raw = {}
    with pytest.raises(ValueError, match="qa_eas"):
        check_quota(raw, "BUILD_APK")


@pytest.mark.parametrize(
    "damage", ["branch", "mapping", "unknown_rollout", "active_rollout", "runtime"]
)
def test_sdk_channel_response_rejects_unknown_rollout_and_wrong_mapping(damage):
    from tools.qa_delivery.pipeline import check_channel

    c, _ = approved()
    c["action"] = "UPDATE"
    page = {
        "name": "qa",
        "isPaused": False,
        "branchMapping": json.dumps(
            {"version": 0, "data": [{"branchId": "qa-id", "branchMappingLogic": "true"}]}
        ),
        "updateBranches": [
            {
                "id": "qa-id",
                "name": "qa",
                "updateGroups": [
                    {
                        "rolloutPercentage": None,
                        "rolloutControlUpdate": None,
                        "platform": "android",
                        "runtime": {"version": "1" * 40},
                    }
                ],
            }
        ],
    }
    check_channel({"currentPage": page}, c)
    if damage == "branch":
        page["updateBranches"][0]["name"] = "production"
    if damage == "mapping":
        page["branchMapping"] = "{}"
    update = page["updateBranches"][0]["updateGroups"][0]
    if damage == "unknown_rollout":
        del update["rolloutPercentage"]
    if damage == "active_rollout":
        update["rolloutPercentage"] = 50
    if damage == "runtime":
        update["runtime"]["version"] = "2" * 40
    with pytest.raises(ValueError, match="qa_eas"):
        check_channel({"currentPage": page}, c)


pytest_plugins = ["test_qa_delivery_database"]


@pytest.fixture
def release_case(tmp_path, checkout, qa_database, monkeypatch):
    from tools.qa_delivery import pipeline
    from tools.qa_delivery.database import _verify_backup, backup_database

    proof = tmp_path / "proof"
    proof.mkdir()
    c, _ = approved()
    c = pipeline.prepare(c, checkout)
    target = c["target"]
    sid, did = "srv-" + "a" * 20, "dep-" + "b" * 20
    target["deployment_reference"] = f"render:{sid}/{did}"
    backup_database(qa_database, proof / "backup.db")
    backup_database(
        proof / "backup.db",
        proof / "restored.db",
        expected_backup=_verify_backup(proof / "backup.db"),
    )
    version = {
        "source_sha": target["source_sha"],
        "environment_id": target["environment_id"],
        "server_schema": c["compatibility"]["server_schema"],
        "api_contracts": [c["compatibility"]["api"]],
        "inventory": c["compatibility"]["inventory"],
        "packaging_digest": "c" * 64,
        "authority": {"generation": 3, "state": "WITHDRAWN", "publication": None},
        "data_scope": "SYNTHETIC_ONLY",
        "schema_version": "qa-backend/1.0.0",
    }
    receipt = {
        "schema_version": "qa-cutover/1.0.0",
        "assurance": "OPERATOR_ATTESTED",
        "old_writer_stopped": True,
        "single_writer_opened": True,
        "uid10001_volume_and_private_files_qualified": True,
        "target": target,
        "backup_reference": target["backup_reference"],
        "continuity_reference": target["continuity_reference"],
        "provider": {"service_id": sid, "deploy_id": did, "branch": "trunk"},
        "version": version,
        "files_sha256": {
            name: hashlib.sha256((proof / name).read_bytes()).hexdigest()
            for name in ["backup.db", "backup.db.manifest.json", "restored.db"]
        },
    }
    (proof / "cutover.json").write_text(json.dumps(receipt))
    previous = {
        "package": c["native"]["package"],
        "certificate_sha256": c["native"]["certificate_sha256"],
        "version_code": 2,
    }
    (proof / "previous-native.json").write_text(json.dumps(previous))
    package = {
        "candidate": c,
        "candidate_sha256": pipeline.digest(c),
        "proof_sha256": pipeline.proof_digest(proof),
        "canonical_sha": c["source"]["js_sha"],
    }
    data = json.loads(json.dumps(github_payloads(c)).replace(SHA, c["source"]["js_sha"]))
    data["actions/runs/456/approvals"][0]["comment"] = (
        f"APPROVE_QA {package['candidate_sha256']} {package['proof_sha256']}"
    )
    environment = {
        "GITHUB_ACTIONS": "true",
        "GITHUB_EVENT_NAME": "workflow_dispatch",
        "GITHUB_RUN_ID": "456",
        "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_REPOSITORY": "MFE-DSS/workout-session-tracking",
    }
    for name, value in {
        **environment,
        "EXPO_TOKEN": "test-only",
        "RENDER_API_KEY": "test-only",
    }.items():
        monkeypatch.setenv(name, value)
    gate = pipeline.GitHubGate(lambda p: deepcopy(data[p]), environment)
    calls = []

    def factory(mobile, env):
        assert mobile == checkout / "clients/mobile"
        assert env["EXPO_PUBLIC_QA_NATIVE_SHA"] == c["source"]["native_sha"]
        assert env["EXPO_PUBLIC_QA_JS_SHA"] == c["source"]["js_sha"]

        def eas(*args):
            calls.append(args)
            if args[0] == "env:set":
                return {
                    "name": args[args.index("--name") + 1],
                    "value": args[args.index("--value") + 1],
                    "scope": "PROJECT",
                    "environments": ["preview"],
                    "visibility": "PUBLIC",
                    "type": "STRING",
                }
            if args[0] == "account:usage":
                return {
                    "account": {"plan": "Free"},
                    "builds": {
                        "plan": {"used": 5, "limit": 30},
                        "android": {"plan": {"used": 5, "limit": 15}},
                        "overage": {"count": 0, "costCents": 0},
                    },
                    "updates": {
                        "uniqueUpdaters": {"plan": {"used": 0, "limit": 1000}},
                        "bandwidth": {"plan": {"usedBytes": 0, "limitBytes": 100000}},
                        "overageCostCents": 0,
                    },
                }
            if args[0] == "channel:view":
                return {
                    "currentPage": {
                        "name": "qa",
                        "isPaused": False,
                        "branchMapping": json.dumps(
                            {
                                "version": 0,
                                "data": [{"branchId": "qa-id", "branchMappingLogic": "true"}],
                            }
                        ),
                        "updateBranches": [{"id": "qa-id", "name": "qa", "updateGroups": []}],
                    }
                }
            return [{"id": "actual-response-id", "status": "FINISHED"}]

        return eas

    service = {
        "id": sid,
        "type": "web_service",
        "repo": "https://github.com/MFE-DSS/workout-session-tracking",
        "branch": "trunk",
        "suspended": "not_suspended",
        "autoDeploy": "no",
        "serviceDetails": {
            "url": target["url"],
            "numInstances": 1,
            "disk": {"sizeGB": 1, "mountPath": "/var/lib/qa"},
        },
    }
    deploy = {"id": did, "status": "live", "commit": {"id": target["source_sha"]}}

    def http(request):
        if request.url.host == "api.expo.dev":
            if "QARuntimeRollout" in json.loads(request.content)["query"]:
                return httpx.Response(
                    200,
                    json={
                        "data": {
                            "app": {"byId": {"updateBranchByName": {"name": "qa", "updates": []}}}
                        }
                    },
                )
            return httpx.Response(
                200,
                json={
                    "data": {
                        "app": {
                            "byId": {
                                "environmentVariables": [],
                                "ownerAccount": {"environmentVariables": []},
                            }
                        }
                    }
                },
            )
        if request.url.host == "api.render.com":
            return httpx.Response(200, json=deploy if "/deploys/" in request.url.path else service)
        return httpx.Response(
            200,
            json=version
            if request.url.path.endswith("version")
            else {"status": "ok", "transport_only": True},
        )

    monkeypatch.setattr(pipeline, "observe_native", lambda root, candidate, env: None)
    return (
        package,
        checkout,
        proof,
        gate,
        factory,
        calls,
        httpx.Client(transport=httpx.MockTransport(http)),
        data,
    )


def test_actual_entrypoint_synchronizes_fixed_public_cloud_metadata_only_after_gates(release_case):
    from tools.qa_delivery.pipeline import publish

    package, root, proof, gate, eas, calls, client, _ = release_case
    with client:
        result = publish(package, root, proof, gate, eas, client)
    writes = [args for args in calls if args[0] == "env:set"]
    assert {args[args.index("--name") + 1] for args in writes} == {
        "EXPO_PUBLIC_QA_NATIVE_SHA",
        "EXPO_PUBLIC_QA_JS_SHA",
        "EXPO_PUBLIC_API_URL",
    }
    assert all(args[1] == "preview" and "plaintext" in args for args in writes)
    assert calls[-1] == (
        "build",
        "--platform",
        "android",
        "--profile",
        "qa-continuous-android",
        "--freeze-credentials",
        "--wait",
        "--json",
        "--non-interactive",
    )
    assert result["state"] == "SUBMITTED_NOT_DISTRIBUTABLE" and result["distributable"] is False
    assert result["observed_submission"] == [{"id": "actual-response-id", "status": "FINISHED"}]


@pytest.mark.parametrize(
    "damage",
    [
        "credentials",
        "candidate",
        "proof",
        "backup",
        "cutover",
        "ci",
        "approval",
        "canonical",
        "unprovisioned",
        "dirty",
    ],
)
def test_actual_publish_entrypoint_has_zero_mutations_when_a_gate_is_missing(
    release_case, monkeypatch, damage
):
    from tools.qa_delivery.pipeline import digest, proof_digest, publish

    package, root, proof, gate, eas, calls, client, data = release_case
    c = package["candidate"]
    if damage == "credentials":
        monkeypatch.delenv("EXPO_TOKEN")
    if damage == "candidate":
        c["eas"]["channel"] = "production"
    if damage == "proof":
        (proof / "new-file").write_text("changed")
    if damage in {"backup", "cutover"}:
        if damage == "backup":
            (proof / "backup.db").write_bytes(b"corrupted")
        else:
            receipt = json.loads((proof / "cutover.json").read_text())
            receipt["old_writer_stopped"] = False
            (proof / "cutover.json").write_text(json.dumps(receipt))
        package["proof_sha256"] = proof_digest(proof)
    if damage == "ci":
        data[f"commits/{c['source']['js_sha']}/check-runs?per_page=100"]["check_runs"][0][
            "conclusion"
        ] = "failure"
    if damage == "approval":
        data["actions/runs/456/approvals"] = []
    if damage == "canonical":
        package["canonical_sha"] = "b" * 40
    if damage == "unprovisioned":
        c["target"] = None
        package["candidate_sha256"] = digest(c)
    if damage == "dirty":
        (root / "untracked").write_text("dirty")
    if damage in {"backup", "cutover"}:
        data["actions/runs/456/approvals"][0]["comment"] = (
            f"APPROVE_QA {package['candidate_sha256']} {package['proof_sha256']}"
        )
    with client, pytest.raises(ValueError, match="qa_"):
        publish(package, root, proof, gate, eas, client)
    assert calls == []


@pytest.mark.parametrize("action", ["UPDATE", "ROLLBACK"])
def test_publish_ota_uses_sdk_environment_and_known_good_group_without_embedding_claim(
    release_case, action
):
    from tools.qa_delivery.pipeline import digest, proof_digest, publish

    package, root, proof, gate, factory, calls, client, data = release_case
    c = package["candidate"]
    c["action"] = action
    previous = deepcopy(c)
    previous.update(
        state="VERIFIED",
        distributable=True,
        artifact={"sha256": "f" * 64, "url": "https://expo.dev/artifacts/observed.apk"},
    )
    previous["eas"]["build_id"] = "edc4b258-cfcf-49c3-8991-883902030576"
    previous["js"] = {
        "update_group": "6a09751d-028f-4878-b4ea-dd658ac59ebe",
        "update_id": "80e3c598-c0f4-4496-a65b-f1f08b2968b0",
        "assets_sha256": "a" * 64,
    }
    (proof / "previous-native.json").write_text(json.dumps(previous))
    (proof / "known-good-update.json").write_text(json.dumps(previous))
    package["candidate_sha256"], package["proof_sha256"] = digest(c), proof_digest(proof)
    data["actions/runs/456/approvals"][0]["comment"] = (
        f"APPROVE_QA {package['candidate_sha256']} {package['proof_sha256']}"
    )

    def factory_with_native(mobile, env):
        basic = factory(mobile, env)

        def eas(*args):
            if args[0] == "build:view":
                calls.append(args)
                return {
                    "id": previous["eas"]["build_id"],
                    "status": "FINISHED",
                    "platform": "ANDROID",
                    "appIdentifier": c["native"]["package"],
                    "appVersion": c["native"]["app_version"],
                    "appBuildVersion": str(c["native"]["version_code"]),
                    "runtime": {"version": c["native"]["runtime_version"]},
                    "gitCommitHash": c["source"]["native_sha"],
                    "updateChannel": {"name": "qa"},
                    "app": {"id": c["eas"]["project_id"]},
                }
            if args[0] == "update:view":
                calls.append(args)
                return [
                    {
                        "id": previous["js"]["update_id"],
                        "group": previous["js"]["update_group"],
                        "platform": "android",
                        "runtimeVersion": c["native"]["runtime_version"],
                        "branch": "qa",
                        "gitCommitHash": c["source"]["js_sha"],
                        "isRollBackToEmbedded": False,
                    }
                ]
            return basic(*args)

        return eas

    with client:
        result = publish(package, root, proof, gate, factory_with_native, client)
    assert any(args[0] == "build:view" for args in calls)
    assert result["distributable"] is False
    if action == "UPDATE":
        assert calls[-1][0] == "update" and "--environment" in calls[-1] and "preview" in calls[-1]
        assert len([args for args in calls if args[0] == "env:set"]) == 3
    else:
        assert calls[-1][0] == "update:republish" and previous["js"]["update_group"] in calls[-1]
        assert not any(args[0] == "env:set" for args in calls)
        assert not any("embedded" in item for args in calls for item in args)


@pytest.mark.parametrize("damage", ["none", "shared_account", "preview_production", "unknown"])
def test_remote_environment_does_not_mutate_values_linked_to_other_environments(damage):
    from tools.qa_delivery.pipeline import check_remote_environment

    c, _ = approved()
    project = [
        {
            "name": "EXPO_PUBLIC_API_URL",
            "scope": "PROJECT",
            "environments": ["preview"],
            "visibility": "PUBLIC",
            "type": "STRING",
        }
    ]
    shared = []
    if damage == "shared_account":
        shared = [{"name": "EXPO_PUBLIC_API_URL", "scope": "SHARED", "environments": ["preview"]}]
    if damage == "preview_production":
        project[0]["environments"] = ["preview", "production"]

    def handler(request):
        assert request.method == "POST" and request.url == "https://api.expo.dev/graphql"
        query = json.loads(request.content)
        assert set(query["variables"]["names"]) == {
            "EXPO_PUBLIC_QA_NATIVE_SHA",
            "EXPO_PUBLIC_QA_JS_SHA",
            "EXPO_PUBLIC_API_URL",
        }
        # Query never asks values of pre-existing environment variables.
        assert " value " not in query["query"]
        return httpx.Response(
            200,
            json={}
            if damage == "unknown"
            else {
                "data": {
                    "app": {
                        "byId": {
                            "environmentVariables": project,
                            "ownerAccount": {"environmentVariables": shared},
                        }
                    }
                }
            },
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        if damage == "none":
            check_remote_environment(c, "test-only", client)
        else:
            with pytest.raises(ValueError, match="qa_eas_environment"):
                check_remote_environment(c, "test-only", client)


def test_new_apk_allows_known_previous_runtime_on_qa_but_update_does_not():
    from tools.qa_delivery.pipeline import check_channel

    c, _ = approved()
    page = {
        "name": "qa",
        "isPaused": False,
        "branchMapping": json.dumps(
            {"version": 0, "data": [{"branchId": "qa-id", "branchMappingLogic": "true"}]}
        ),
        "updateBranches": [
            {
                "id": "qa-id",
                "name": "qa",
                "updateGroups": [
                    {
                        "rolloutPercentage": None,
                        "rolloutControlUpdate": None,
                        "platform": "android",
                        "runtime": {"version": "2" * 40},
                    }
                ],
            }
        ],
    }
    check_channel({"currentPage": page}, c)
    c["action"] = "UPDATE"
    with pytest.raises(ValueError, match="qa_eas"):
        check_channel({"currentPage": page}, c)


@pytest.mark.parametrize("damage", ["none", "unknown", "percentage", "control", "runtime"])
def test_current_runtime_rollout_is_queried_even_if_channel_latest_is_another_runtime(damage):
    from tools.qa_delivery.pipeline import check_current_runtime_rollout

    c, _ = approved()
    update = {
        "runtime": {"version": c["native"]["runtime_version"]},
        "rolloutPercentage": None,
        "rolloutControlUpdate": None,
    }
    if damage == "percentage":
        update["rolloutPercentage"] = 50
    if damage == "control":
        update["rolloutControlUpdate"] = {"id": "active-control"}
    if damage == "runtime":
        update["runtime"]["version"] = "2" * 40
    if damage == "unknown":
        del update["rolloutPercentage"]

    def http(request):
        query = json.loads(request.content)
        assert query["variables"]["runtime"] == c["native"]["runtime_version"]
        assert "runtimeVersions" in query["query"] and "ANDROID" in query["query"]
        return httpx.Response(
            200,
            json={
                "data": {
                    "app": {"byId": {"updateBranchByName": {"name": "qa", "updates": [update]}}}
                }
            },
        )

    with httpx.Client(transport=httpx.MockTransport(http)) as client:
        if damage == "none":
            check_current_runtime_rollout(c, "test-only", client)
        else:
            with pytest.raises(ValueError, match="qa_eas_rollout"):
                check_current_runtime_rollout(c, "test-only", client)


def test_cli_prepare_uses_real_template_without_external_credentials(checkout, tmp_path):
    import os
    import sys

    root = Path(__file__).resolve().parents[1]
    output = tmp_path / "qa-prepared.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.qa_delivery.pipeline",
            "prepare",
            "--candidate",
            str(root / "docs/release/rel-03/candidate.json"),
            "--checkout",
            str(checkout),
            "--output",
            str(output),
        ],
        cwd=root,
        env={"PATH": os.environ["PATH"], "PYTHONPATH": str(root)},
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "QA_PREPARED_NON_DISTRIBUTABLE"
    package = json.loads(output.read_text())
    assert package["candidate"]["target"] is None
    assert package["proof_sha256"] is None and package["canonical_sha"] is None
    assert package["candidate"]["distributable"] is False
    assert output.stat().st_mode & 0o777 == 0o600
    assert (
        subprocess.check_output(["git", "-C", str(checkout), "status", "--porcelain"], text=True)
        == ""
    )
