"""Manual QA release orchestrator. All external publication follows acquired gates.

No environment/secret/protection creation, build auto-increment, production channel,
rollout override or inferred deployment approval is supported.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import httpx

from tools.qa_delivery.database import _verify_backup, verify_database
from tools.qa_delivery.releases import (
    classify_update,
    metadata_environment,
    stable_qa_url,
    storage_schema_digest,
    validate_candidate,
)

REPO = "MFE-DSS/workout-session-tracking"
FLOOR = (
    "pytest + QA scripts",
    "lint (ruff budget + bandit + actionlint + shellcheck)",
    "visual contract (DA-GOV-01)",
    "mobile checks (Jest + TypeScript)",
)
RUN_URL = f"https://github.com/{REPO}/actions/runs/"


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def git(root, *args):
    executable = shutil.which("git")
    require(executable, "qa_pipeline_git_missing")
    return subprocess.check_output(  # noqa: S603 — fixed Git subcommands, no shell
        [executable, "-C", str(root), *args],
        text=True,
        stderr=subprocess.DEVNULL,
        timeout=20,
    ).strip()


def prepare(raw, checkout):
    require(
        not git(checkout, "status", "--porcelain", "--untracked-files=all"),
        "qa_pipeline_source_dirty",
    )
    c = deepcopy(raw)
    # Ignore computed-only fields from a previous normalized receipt.
    c.pop("pending", None)
    c.pop("distributable", None)
    c["state"] = "PREPARED"
    c["source"]["js_sha"] = git(checkout, "rev-parse", "HEAD")
    if c["action"] == "BUILD_APK":
        c["source"]["native_sha"] = c["source"]["js_sha"]
    c["native"]["storage_schema_sha256"] = storage_schema_digest(checkout)
    return validate_candidate(c, {})


def gh_get(path):
    """Read-only GitHub API. Never return CLI stderr (may contain private URLs)."""
    try:
        executable = shutil.which("gh")
        require(executable, "qa_github_cli_missing")
        result = subprocess.run(  # noqa: S603 — fixed GET endpoint namespace
            [
                executable,
                "api",
                "--method",
                "GET",
                "--paginate",
                "--slurp",
                f"repos/{REPO}/{path}".rstrip("/"),
            ],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        require(result.returncode == 0, "qa_github_read_failed_audit_token_may_be_required")
        pages = json.loads(result.stdout)
        if len(pages) == 1:
            return pages[0]
        if all(isinstance(page, list) for page in pages):
            return [item for page in pages for item in page]
        if all("check_runs" in page for page in pages):
            return {"check_runs": [item for page in pages for item in page["check_runs"]]}
        raise ValueError("qa_github_pagination_unknown")
    except (OSError, subprocess.SubprocessError, TypeError, json.JSONDecodeError):
        raise ValueError("qa_github_read_failed") from None


def protected_environment(get=gh_get):
    protection = get("environments/qa-release")
    require(protection["name"] == "qa-release", "qa_github_environment_wrong")
    rules = [p for p in protection["protection_rules"] if p["type"] == "required_reviewers"]
    require(len(rules) == 1 and rules[0]["reviewers"], "qa_github_reviewers_missing")
    require(
        any(p["type"] == "User" for p in rules[0]["reviewers"]),
        "qa_github_direct_human_reviewer_required",
    )
    return protection, rules[0]


class GitHubGate:
    def __init__(self, get=gh_get, environment=None):
        self.get = get
        self.env = os.environ if environment is None else environment

    def collect(self, c, candidate_hash, proof_hash):
        try:
            env, get, sha = self.env, self.get, c["source"]["js_sha"]
            require(
                env.get("GITHUB_ACTIONS") == "true"
                and env.get("GITHUB_EVENT_NAME") == "workflow_dispatch"
                and env.get("GITHUB_REPOSITORY") == REPO,
                "qa_github_dispatch_required",
            )
            run_id = env["GITHUB_RUN_ID"]
            require(re.fullmatch(r"[1-9][0-9]*", run_id), "qa_github_run_invalid")
            run = get(f"actions/runs/{run_id}")
            require(
                run["event"] == "workflow_dispatch"
                and run["status"] == "in_progress"
                and run["head_sha"] == sha
                and run["path"] == ".github/workflows/qa-release.yml"
                and run["run_attempt"] == int(env["GITHUB_RUN_ATTEMPT"]),
                "qa_github_run_source_mismatch",
            )
            # Re-runs can inherit historical environment approval. A fresh dispatch
            # is required so approval cannot silently carry over to another attempt.
            require(run["run_attempt"] == 1, "qa_github_fresh_dispatch_required")
            branch = quote(get("")["default_branch"], safe="")
            canonical = get(f"branches/{branch}")["commit"]["sha"]
            policy = get(f"branches/{branch}/protection")["required_status_checks"]
            required = (
                set(FLOOR) | set(policy["contexts"]) | {p["context"] for p in policy["checks"]}
            )
            app_ids = {p["context"]: p["app_id"] for p in policy["checks"]}
            actual = get(f"commits/{sha}/check-runs?per_page=100")["check_runs"]
            checks = []
            for name in sorted(required):
                selected = [x for x in actual if x["name"] == name]
                require(len(selected) == 1, "qa_github_check_missing_or_ambiguous")
                check = selected[0]
                require(
                    check["head_sha"] == sha
                    and check["status"] == "completed"
                    and check["conclusion"] == "success",
                    "qa_github_check_not_green",
                )
                expected_app = app_ids.get(name, 15368 if name in FLOOR else None)
                require(
                    expected_app is not None and check["app"]["id"] == expected_app,
                    "qa_github_check_app_unknown",
                )
                match = re.fullmatch(
                    re.escape(RUN_URL) + r"([1-9][0-9]*)(?:/job/[1-9][0-9]*)?", check["details_url"]
                )
                require(match, "qa_github_check_run_unknown")
                checks.append(
                    {
                        "name": name,
                        "head_sha": sha,
                        "conclusion": "success",
                        "run_id": int(match[1]),
                        "url": check["details_url"],
                    }
                )
            protection, rule = protected_environment(get)
            # Team membership is deliberately not inferred from an actor's login.
            reviewers = {p["reviewer"]["id"] for p in rule["reviewers"] if p["type"] == "User"}
            require(reviewers, "qa_github_direct_human_reviewer_required")
            require(
                get(f"actions/runs/{run_id}/pending_deployments") == [],
                "qa_github_deployment_pending",
            )
            approvals = [
                a
                for a in get(f"actions/runs/{run_id}/approvals")
                if any(
                    e["id"] == protection["id"] and e["name"] == "qa-release"
                    for e in a["environments"]
                )
            ]
            require(len(approvals) == 1, "qa_github_single_candidate_approval_required")
            approval = approvals[-1]
            require(
                approval["state"] == "approved"
                and approval["user"]["type"] == "User"
                and approval["user"]["id"] in reviewers,
                "qa_github_human_approval_required",
            )
            if rule.get("prevent_self_review"):
                require(
                    approval["user"]["id"] != run["actor"]["id"], "qa_github_self_review_forbidden"
                )
            require(
                approval["comment"].strip() == f"APPROVE_QA {candidate_hash} {proof_hash}",
                "qa_github_candidate_approval_missing",
            )
            deployments = get(f"deployments?sha={sha}&environment=qa-release&per_page=100")
            bound = []
            for deployment in deployments:
                statuses = get(f"deployments/{deployment['id']}/statuses?per_page=100")
                if (
                    deployment["sha"] == sha
                    and deployment["environment"] == "qa-release"
                    and statuses
                    and statuses[0]["state"] == "in_progress"
                    and re.fullmatch(
                        re.escape(RUN_URL + run_id) + r"(?:/job/[1-9][0-9]*)?",
                        statuses[0]["log_url"],
                    )
                ):
                    bound.append(deployment)
            require(len(bound) == 1, "qa_github_run_deployment_unbound")
            return {
                "canonical_sha": canonical,
                "ci": {"head_sha": sha, "required_checks": sorted(required), "checks": checks},
                "approval": {
                    "head_sha": sha,
                    "environment": "qa-release",
                    "decision": "APPROVED",
                    "reviewer": approval["user"]["login"],
                    "deployment_id": bound[0]["id"],
                },
                "reviewer_ids": reviewers,
            }
        except (KeyError, IndexError, TypeError, AttributeError):
            raise ValueError("qa_github_evidence_incomplete") from None


def proof_digest(root):
    root = Path(root)
    files = sorted(root.rglob("*"))
    require(files and all(not p.is_symlink() for p in files), "qa_continuity_proof_missing")
    hashes = {}
    for path in files:
        if path.is_file():
            require(path.stat().st_size <= 128 * 1024 * 1024, "qa_continuity_proof_too_large")
            hashes[path.relative_to(root).as_posix()] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    return digest(hashes)


def verify_continuity(root, c):
    """Integrity is observed; historical writer stop remains OPERATOR_ATTESTED.

    These are point-in-time cutover copies, never a comparison of an old backup
    against the mutable current live database after subsequent journal writes.
    """
    try:
        root = Path(root)
        receipt = json.loads((root / "cutover.json").read_text())
        require(
            receipt["schema_version"] == "qa-cutover/1.0.0"
            and receipt["assurance"] == "OPERATOR_ATTESTED",
            "qa_continuity_receipt_invalid",
        )
        require(
            receipt["old_writer_stopped"] is True
            and receipt["single_writer_opened"] is True
            and receipt["uid10001_volume_and_private_files_qualified"] is True,
            "qa_continuity_cutover_unqualified",
        )
        require(receipt["target"] == c["target"], "qa_continuity_target_mismatch")
        backup = _verify_backup(root / "backup.db")
        restored = verify_database(root / "restored.db")
        require(
            restored == {k: v for k, v in backup.items() if k != "database_sha256"},
            "qa_continuity_restore_mismatch",
        )
        for name in ("backup.db", "backup.db.manifest.json", "restored.db"):
            require(
                receipt["files_sha256"][name]
                == hashlib.sha256((root / name).read_bytes()).hexdigest(),
                "qa_continuity_checksum_mismatch",
            )
        require(
            c["target"]["backup_reference"] == receipt["backup_reference"]
            and c["target"]["continuity_reference"] == receipt["continuity_reference"],
            "qa_continuity_reference_mismatch",
        )
        return receipt
    except (OSError, KeyError, TypeError, ValueError):
        raise ValueError("qa_continuity_verified_backup_and_cutover_required") from None


def _observed_time(value):
    require(isinstance(value, str), "qa_release_backup_timestamp_invalid")
    observed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(observed.utcoffset() is not None, "qa_release_backup_timezone_required")
    return observed


def verify_release_backup(root, c, package, gate, acquired):
    """Distinct recovery snapshot/export for this candidate, never old cutover data.

    SQLite bytes/manifests and GitHub chronology are checked independently.
    Physical off-service export and its observation remain OPERATOR_ATTESTED by
    the human review of the exact proof hash, not inferred from a JSON boolean.
    No arbitrary TTL or claim that a historical capture equals today's live DB.
    """
    try:
        root = Path(root)
        record = json.loads((root / "release-backup.json").read_text())
        require(
            record["schema_version"] == "qa-release-backup/1.0.0"
            and record["assurance"] == "OPERATOR_ATTESTED",
            "qa_release_backup_attestation_required",
        )
        require(
            record["release_id"] == c["release_id"]
            and record["candidate_sha256"] == package["candidate_sha256"]
            and record["source"] == c["source"]
            and record["target"] == c["target"],
            "qa_release_backup_candidate_mismatch",
        )
        export = record["off_service_export"]
        require(
            export["completed"] is True and export["off_service"] is True,
            "qa_release_backup_export_not_observed",
        )
        reference = export["reference"]
        require(
            isinstance(reference, str)
            and 0 < len(reference) <= 512
            and reference.strip() == reference,
            "qa_release_backup_export_reference_required",
        )
        names = {
            "release-backup.db",
            "release-backup.db.manifest.json",
            "release-export.db",
            "release-export.db.manifest.json",
        }
        require(set(record["files_sha256"]) == names, "qa_release_backup_files_missing")
        for name in names:
            require(
                record["files_sha256"][name]
                == hashlib.sha256((root / name).read_bytes()).hexdigest(),
                "qa_release_backup_checksum_mismatch",
            )
        snapshot = _verify_backup(root / "release-backup.db")
        exported = _verify_backup(root / "release-export.db")
        require(snapshot == exported, "qa_release_backup_export_snapshot_mismatch")
        preparation_id = record["preparation_run_id"]
        current_id = int(gate.env["GITHUB_RUN_ID"])
        require(
            type(preparation_id) is int and preparation_id > 0 and preparation_id != current_id,
            "qa_release_backup_prior_preparation_required",
        )
        preparation = gate.get(f"actions/runs/{preparation_id}")
        current = gate.get(f"actions/runs/{current_id}")
        require(
            preparation["id"] == preparation_id
            and preparation["event"] == "workflow_dispatch"
            and preparation["head_sha"] == c["source"]["js_sha"]
            and preparation["path"] == ".github/workflows/qa-release.yml"
            and preparation["status"] == "completed"
            and preparation["conclusion"] == "success"
            and preparation["run_attempt"] == 1,
            "qa_release_backup_preparation_unverified",
        )
        require(
            current["id"] == current_id and current["head_sha"] == c["source"]["js_sha"],
            "qa_release_backup_dispatch_mismatch",
        )
        # PREPARE generates BUILD_APK candidates today. It anchors source/time
        # only; UPDATE/ROLLBACK are bound exactly by the distinct record above.
        prepared_start = _observed_time(preparation["created_at"])
        prepared_done = _observed_time(preparation["updated_at"])
        capture = record["capture"]
        require(
            prepared_start
            <= prepared_done
            <= _observed_time(capture["started_at"])
            <= _observed_time(capture["completed_at"])
            <= _observed_time(export["completed_at"])
            <= _observed_time(export["observed_at"])
            <= _observed_time(current["created_at"]),
            "qa_release_backup_capture_or_export_chronology_stale",
        )
        deployments = gate.get("deployments?environment=qa-release&per_page=100")
        this_deployment = acquired["approval"]["deployment_id"]
        require(
            any(d["id"] == this_deployment for d in deployments),
            "qa_release_backup_current_deployment_unverified",
        )
        for deployment in deployments:
            require(
                deployment["environment"] == "qa-release", "qa_release_backup_deployment_unknown"
            )
            if deployment["id"] != this_deployment:
                require(
                    _observed_time(deployment["created_at"]) < prepared_start,
                    "qa_release_backup_preparation_predates_previous_release",
                )
        return record
    except (OSError, KeyError, TypeError, ValueError):
        raise ValueError(
            "qa_release_backup_fresh_capture_and_off_service_export_required"
        ) from None


def observe_target(c, proof, token, client):
    try:
        t, provider = c["target"], proof["provider"]
        require(token and stable_qa_url(t["url"]), "qa_target_credentials_or_origin_missing")
        sid, did = provider["service_id"], provider["deploy_id"]
        require(
            re.fullmatch(r"srv-[a-z0-9]{20}", sid) and re.fullmatch(r"dep-[a-z0-9]{20}", did),
            "qa_target_provider_id_invalid",
        )

        def get(url, auth=False):
            response = client.get(
                url,
                headers={"Authorization": f"Bearer {token}"} if auth else {},
                follow_redirects=False,
                timeout=15,
            )
            require(
                response.status_code == 200 and len(response.content) < 1024 * 1024,
                "qa_target_unavailable",
            )
            return response.json()

        service = get(f"https://api.render.com/v1/services/{sid}", True)
        deploy = get(f"https://api.render.com/v1/services/{sid}/deploys/{did}", True)
        details = service["serviceDetails"]
        require(
            service["id"] == sid
            and service["type"] == "web_service"
            and service["suspended"] == "not_suspended"
            and service["autoDeploy"] == "no",
            "qa_target_service_invalid",
        )
        require(
            service["repo"] == f"https://github.com/{REPO}"
            and service["branch"] == provider["branch"],
            "qa_target_repository_mismatch",
        )
        require(
            details["url"].rstrip("/") == t["url"].rstrip("/")
            and details["numInstances"] == 1
            and not details.get("autoscaling"),
            "qa_target_service_mismatch",
        )
        require(
            details["disk"]["sizeGB"] >= 1 and details["disk"]["mountPath"] == "/var/lib/qa",
            "qa_target_disk_missing",
        )
        require(
            deploy["id"] == did
            and deploy["status"] == "live"
            and deploy["commit"]["id"] == t["source_sha"],
            "qa_target_deployment_mismatch",
        )
        require(
            t["deployment_reference"] == f"render:{sid}/{did}",
            "qa_target_deployment_reference_mismatch",
        )
        version = get(t["url"].rstrip("/") + "/__qa_version")
        require(version == proof["version"], "qa_target_current_identity_changed")
        require(
            version["source_sha"] == t["source_sha"]
            and version["environment_id"] == t["environment_id"]
            and version["server_schema"] == c["compatibility"]["server_schema"]
            and version["api_contracts"] == [c["compatibility"]["api"]]
            and version["inventory"] == c["compatibility"]["inventory"]
            and version["data_scope"] == "SYNTHETIC_ONLY",
            "qa_target_identity_mismatch",
        )
        require(
            re.fullmatch(r"[a-f0-9]{64}", version["packaging_digest"])
            and type(version["authority"]["generation"]) is int
            and version["authority"]["generation"] > 0,
            "qa_target_authority_unknown",
        )
        require(
            get(t["url"].rstrip("/") + "/__qa_health") == {"status": "ok", "transport_only": True},
            "qa_target_not_healthy",
        )
        return t
    except (OSError, httpx.HTTPError, KeyError, TypeError, ValueError):
        raise ValueError("qa_target_provider_or_tls_proof_required") from None


class EAS:
    """Pinned executable, fixed argv, captured private output; no shell."""

    def __init__(self, mobile, environment):
        self.mobile, self.environment = Path(mobile), environment

    def __call__(self, *args):
        executable = shutil.which("eas")
        require(executable, "qa_eas_cli_missing")
        result = subprocess.run(  # noqa: S603 — allowlisted commands assembled below
            [executable, *args],
            cwd=self.mobile,
            env=self.environment,
            capture_output=True,
            text=True,
            check=False,
            timeout=3600,
        )
        require(result.returncode == 0, "qa_eas_command_failed_no_automatic_retry")
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            raise ValueError("qa_eas_response_unknown") from None


def check_quota(usage, action):
    try:
        require(usage["account"]["plan"] == "Free", "qa_eas_plan_not_approved")
        require(
            usage["builds"]["overage"]["count"] == 0
            and usage["builds"]["overage"]["costCents"] == 0
            and usage["updates"]["overageCostCents"] == 0,
            "qa_eas_overage_not_authorized",
        )
        if action == "BUILD_APK":
            for plan in (usage["builds"]["android"]["plan"], usage["builds"]["plan"]):
                require(
                    type(plan["used"]) is int
                    and type(plan["limit"]) is int
                    and 0 <= plan["used"] < plan["limit"],
                    "qa_eas_build_quota_unavailable",
                )
        else:
            plan = usage["updates"]["uniqueUpdaters"]["plan"]
            bandwidth = usage["updates"]["bandwidth"]["plan"]
            require(
                0 <= plan["used"] < plan["limit"]
                and 0 <= bandwidth["usedBytes"] < bandwidth["limitBytes"],
                "qa_eas_update_quota_unavailable",
            )
    except (KeyError, TypeError):
        raise ValueError("qa_eas_quota_unknown") from None


def check_channel(raw, c):
    """Only one unconditional qa→qa mapping; reject unknown/partial rollouts."""
    try:
        channel = raw["currentPage"]
        require(
            channel["name"] == "qa" and channel["isPaused"] is False, "qa_eas_channel_unavailable"
        )
        branches = channel["updateBranches"]
        require(len(branches) == 1 and branches[0]["name"] == "qa", "qa_eas_branch_mismatch")
        mapping = json.loads(channel["branchMapping"])
        require(
            mapping
            == {
                "version": 0,
                "data": [{"branchId": branches[0]["id"], "branchMappingLogic": "true"}],
            },
            "qa_eas_rollout_unknown",
        )
        for update in branches[0]["updateGroups"]:
            require(
                update["platform"] == "android"
                and isinstance(update["runtime"]["version"], str)
                and bool(update["runtime"]["version"]),
                "qa_eas_runtime_unknown",
            )
            # channel:view exposes only the latest global group. Another native
            # runtime cannot establish this installed runtime's compatibility or
            # rollout; the exact-runtime query below is the mandatory authority.
            if update["runtime"]["version"] != c["native"]["runtime_version"]:
                continue
            require(
                "rolloutPercentage" in update and "rolloutControlUpdate" in update,
                "qa_eas_rollout_unknown",
            )
            require(
                update["rolloutPercentage"] in (None, 100)
                and update["rolloutControlUpdate"] is None,
                "qa_eas_rollout_active",
            )
    except (KeyError, TypeError, ValueError):
        raise ValueError("qa_eas_channel_or_rollout_refused") from None


def check_remote_environment(c, token, client):
    """Read exact CLI27.2 GraphQL shape before env:set can merge environments.

    Only names/scopes/environment bindings are read, never variable values.
    This is a read-only GraphQL query, despite its HTTP POST transport.
    """
    try:
        names = ["EXPO_PUBLIC_QA_NATIVE_SHA", "EXPO_PUBLIC_QA_JS_SHA", "EXPO_PUBLIC_API_URL"]
        query = "query QAEnvironmentBindings($id:String!,$names:[String!]) { app { byId(appId:$id) { environmentVariables(filterNames:$names) { name scope environments visibility type } ownerAccount { environmentVariables(filterNames:$names) { name scope environments visibility type } } } } }"
        response = client.post(
            "https://api.expo.dev/graphql",
            json={"query": query, "variables": {"id": c["eas"]["project_id"], "names": names}},
            headers={"Authorization": f"Bearer {token}"},
            follow_redirects=False,
            timeout=15,
        )
        require(
            response.status_code == 200 and len(response.content) < 1024 * 1024,
            "qa_eas_environment_unavailable",
        )
        app = response.json()["data"]["app"]["byId"]
        shared = app["ownerAccount"]["environmentVariables"]
        require(
            not any(v["name"] in names and "preview" in v["environments"] for v in shared),
            "qa_eas_environment_account_shared",
        )
        for variable in app["environmentVariables"]:
            if variable["name"] in names and "preview" in variable["environments"]:
                require(
                    variable["scope"] == "PROJECT"
                    and variable["environments"] == ["preview"]
                    and variable["visibility"] == "PUBLIC"
                    and variable["type"] == "STRING",
                    "qa_eas_environment_linked_outside_preview",
                )
    except (httpx.HTTPError, KeyError, TypeError, ValueError):
        raise ValueError("qa_eas_environment_bindings_unqualified") from None


def check_current_runtime_rollout(c, token, client):
    """Channel view only shows the latest group globally; inspect this runtime."""
    try:
        query = 'query QARuntimeRollout($id:String!,$runtime:String!) { app { byId(appId:$id) { updateBranchByName(name:"qa") { name updates(offset:0,limit:1,filter:{platform:ANDROID,runtimeVersions:[$runtime]}) { runtime { version } rolloutPercentage rolloutControlUpdate { id } } } } } }'
        response = client.post(
            "https://api.expo.dev/graphql",
            json={
                "query": query,
                "variables": {
                    "id": c["eas"]["project_id"],
                    "runtime": c["native"]["runtime_version"],
                },
            },
            headers={"Authorization": f"Bearer {token}"},
            follow_redirects=False,
            timeout=15,
        )
        require(
            response.status_code == 200 and len(response.content) < 1024 * 1024,
            "qa_eas_rollout_unavailable",
        )
        branch = response.json()["data"]["app"]["byId"]["updateBranchByName"]
        require(
            branch["name"] == "qa"
            and isinstance(branch["updates"], list)
            and len(branch["updates"]) <= 1,
            "qa_eas_rollout_unknown",
        )
        for update in branch["updates"]:
            require(
                update["runtime"]["version"] == c["native"]["runtime_version"]
                and update["rolloutPercentage"] in (None, 100)
                and update["rolloutControlUpdate"] is None,
                "qa_eas_rollout_active_or_unknown",
            )
    except (httpx.HTTPError, KeyError, TypeError, ValueError):
        raise ValueError("qa_eas_rollout_current_runtime_unqualified") from None


def observe_native(checkout, c, environment):
    """Use real Expo config/SDK fingerprint; never trust a dispatch runtime hash."""
    mobile = Path(checkout) / "clients/mobile"
    profiles = json.loads((mobile / "eas.json").read_text())
    profile = profiles["build"]["qa-continuous-android"]
    require(
        profiles["cli"]["appVersionSource"] == "local"
        and not profile.get("autoIncrement")
        and not profile["android"].get("autoIncrement"),
        "qa_native_version_must_be_tracked",
    )
    node = shutil.which("node")
    require(node, "qa_native_node_missing")
    script = "const {getConfig}=require('expo/config'); const f=require('@expo/fingerprint'); (async()=>{const c=getConfig(process.cwd(),{skipSDKVersionRequirement:true}).exp;const h=await f.createFingerprintAsync(process.cwd(),{platforms:['android']}); console.log(JSON.stringify({version:c.version,android:c.android,updates:c.updates,runtimeVersion:c.runtimeVersion,hash:h.hash}));})().catch(()=>process.exit(1));"
    output = subprocess.run(  # noqa: S603 — fixed Node script, no source interpolation
        [node, "-e", script],
        cwd=mobile,
        env=environment,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    require(output.returncode == 0, "qa_native_config_or_fingerprint_unavailable")
    actual = json.loads(output.stdout)
    require(
        actual["version"] == c["native"]["app_version"]
        and actual["android"]["versionCode"] == c["native"]["version_code"]
        and actual["android"]["package"] == c["native"]["package"],
        "qa_native_tracked_version_mismatch",
    )
    require(
        actual["hash"] == c["native"]["fingerprint"] == c["native"]["runtime_version"]
        and actual["runtimeVersion"] == {"policy": "fingerprint"}
        and actual["updates"]["enabled"] is True,
        "qa_native_runtime_mismatch",
    )
    require(
        actual["updates"]["url"] == "https://u.expo.dev/" + c["eas"]["project_id"],
        "qa_native_update_url_mismatch",
    )


def publish(package, checkout, proof_root, gate=None, eas_factory=EAS, client=None):
    """Entry point performs every gate before its first publishing command.

    Successful submission is NOT BUILT/VERIFIED: artifact signature, build runtime,
    native/JS metadata and installation still require actual later observations.
    """
    try:
        require(
            os.environ.get("EXPO_TOKEN") and os.environ.get("RENDER_API_KEY"),
            "qa_publish_credentials_missing",
        )
        gate = gate or GitHubGate()
        c = package["candidate"]
        require(
            digest(c) == package["candidate_sha256"]
            and proof_digest(proof_root) == package["proof_sha256"],
            "qa_publish_frozen_package_changed",
        )
        require(prepare(c, checkout) == c, "qa_publish_source_or_candidate_changed")
        require(c["target"] is not None, "qa_publish_target_unprovisioned")
        acquired = gate.collect(c, package["candidate_sha256"], package["proof_sha256"])
        require(
            acquired["canonical_sha"] == package["canonical_sha"],
            "qa_publish_canonical_changed_prepare_again",
        )
        sha, canonical = c["source"]["js_sha"], acquired["canonical_sha"]
        require(
            git(checkout, "merge-base", sha, canonical) == sha,
            "qa_publish_source_not_canonical_ancestor",
        )
        require(
            git(checkout, "merge-base", c["source"]["native_sha"], canonical)
            == c["source"]["native_sha"],
            "qa_publish_native_source_not_canonical_ancestor",
        )
        proof = verify_continuity(proof_root, c)
        verify_release_backup(proof_root, c, package, gate, acquired)
        previous = json.loads((Path(proof_root) / "previous-native.json").read_text())
        metadata = metadata_environment(c, checkout, previous)
        environment = {
            **os.environ,
            **metadata,
            "AUREN_QA_DELIVERY": "1",
            "EXPO_PUBLIC_QA_DELIVERY": "1",
            "EXPO_PUBLIC_PLAN_V3_CONTROLLED_TEST": "1",
            "EXPO_PUBLIC_API_URL": c["target"]["url"],
        }
        own_client = client is None
        client = client or httpx.Client(trust_env=False, follow_redirects=False)
        try:
            target = observe_target(c, proof, os.environ["RENDER_API_KEY"], client)
            check_remote_environment(c, os.environ["EXPO_TOKEN"], client)
        finally:
            if own_client:
                client.close()
        evidence = {
            "schema_version": "qa-release-evidence/1.0.0",
            "git": {
                "head_sha": sha,
                "native_sha": c["source"]["native_sha"],
                "dirty_paths": [],
                "storage_schema_sha256": storage_schema_digest(checkout),
                "canonical_sha": canonical,
                "ancestor_shas": [sha],
            },
            "ci": acquired["ci"],
            "approval": acquired["approval"],
            # This is the actual protected candidate deployment review, not an
            # invented PR approval or a GO MERGE reinterpreted as release consent.
            "review": {
                "head_sha": sha,
                "base_sha": canonical,
                "decision": "APPROVED",
                "visual": "NOT_APPLICABLE",
                "reference": RUN_URL + os.environ["GITHUB_RUN_ID"],
            },
            "target": target,
            "previous_native": previous,
        }
        approved = validate_candidate({**c, "state": "APPROVED"}, evidence)
        observe_native(checkout, c, environment)
        eas = eas_factory(Path(checkout) / "clients/mobile", environment)
        check_quota(eas("account:usage", "grimais", "--json", "--non-interactive"), c["action"])
        check_channel(eas("channel:view", "qa", "--json", "--non-interactive"), c)
        if c["action"] in {"UPDATE", "ROLLBACK"}:
            require(classify_update(previous, c) == "JS_ASSETS_ONLY", "qa_publish_new_apk_required")
            build_id = previous["eas"]["build_id"]
            require(re.fullmatch(r"[a-f0-9-]{36}", build_id), "qa_native_prior_build_id_invalid")
            built = eas("build:view", build_id, "--json")
            require(
                built["id"] == build_id
                and built["status"] == "FINISHED"
                and built["platform"] == "ANDROID",
                "qa_native_prior_build_unavailable",
            )
            require(
                built["app"]["id"] == c["eas"]["project_id"]
                and built["updateChannel"]["name"] == "qa"
                and built["appIdentifier"] == c["native"]["package"],
                "qa_native_prior_build_project_mismatch",
            )
            require(
                built["appVersion"] == c["native"]["app_version"]
                and built["appBuildVersion"] == str(c["native"]["version_code"])
                and built["runtime"]["version"] == c["native"]["runtime_version"]
                and built["gitCommitHash"] == c["source"]["native_sha"],
                "qa_native_prior_build_identity_mismatch",
            )
        rollback_group = None
        if c["action"] == "ROLLBACK":
            known = json.loads((Path(proof_root) / "known-good-update.json").read_text())
            require(
                known["state"] == "VERIFIED"
                and known["distributable"] is True
                and classify_update(known, c) == "JS_ASSETS_ONLY"
                and known["source"] == c["source"],
                "qa_rollback_known_good_required",
            )
            rollback_group = known["js"]["update_group"]
            require(re.fullmatch(r"[a-f0-9-]{36}", rollback_group), "qa_rollback_group_invalid")
            updates = eas("update:view", rollback_group, "--json")
            require(
                len(updates) == 1
                and updates[0]["platform"] == "android"
                and updates[0]["runtimeVersion"] == c["native"]["runtime_version"]
                and updates[0]["branch"] == "qa"
                and updates[0]["gitCommitHash"] == sha
                and updates[0]["id"] == known["js"]["update_id"]
                and updates[0]["isRollBackToEmbedded"] is False,
                "qa_rollback_remote_identity_mismatch",
            )
        # Re-acquire policy/current canonical/approval immediately before mutations.
        final = gate.collect(c, package["candidate_sha256"], package["proof_sha256"])
        require(
            final == acquired
            and prepare(c, checkout) == c
            and proof_digest(proof_root) == package["proof_sha256"],
            "qa_publish_gate_changed",
        )
        # Refresh mutable target/authority and runtime-specific rollout immediately
        # before writes; private cutover copies remain historical point-in-time.
        final_client = (
            client if not own_client else httpx.Client(trust_env=False, follow_redirects=False)
        )
        try:
            observe_target(c, proof, os.environ["RENDER_API_KEY"], final_client)
            check_current_runtime_rollout(c, os.environ["EXPO_TOKEN"], final_client)
            check_remote_environment(c, os.environ["EXPO_TOKEN"], final_client)
        finally:
            if own_client:
                final_client.close()
        if c["action"] != "ROLLBACK":
            # EAS cloud workers do not inherit local process.env. Persist exactly
            # these three public values in preview; --environment preview on Update
            # reads those same server values. No generic env/key forwarding exists.
            for name, value in {**metadata, "EXPO_PUBLIC_API_URL": target["url"]}.items():
                stored = eas(
                    "env:set",
                    "preview",
                    "--name",
                    name,
                    "--value",
                    value,
                    "--type",
                    "string",
                    "--visibility",
                    "plaintext",
                    "--scope",
                    "project",
                    "--json",
                    "--non-interactive",
                )
                require(
                    stored["name"] == name
                    and stored["value"] == value
                    and stored["scope"] == "PROJECT"
                    and stored["environments"] == ["preview"]
                    and stored["visibility"] == "PUBLIC"
                    and stored["type"] == "STRING",
                    "qa_eas_public_metadata_not_persisted",
                )
        if c["action"] == "BUILD_APK":
            response = eas(
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
        elif c["action"] == "UPDATE":
            response = eas(
                "update",
                "--channel",
                "qa",
                "--platform",
                "android",
                "--environment",
                "preview",
                "--message",
                c["release_id"],
                "--json",
                "--non-interactive",
            )
        else:
            response = eas(
                "update:republish",
                "--group",
                rollback_group,
                "--destination-channel",
                "qa",
                "--platform",
                "android",
                "--message",
                c["release_id"],
                "--json",
                "--non-interactive",
            )
        return {
            "state": "SUBMITTED_NOT_DISTRIBUTABLE",
            "candidate": approved,
            "assurance": "OPERATOR_ATTESTED_CUTOVER_AND_PROTECTED_CANDIDATE_REVIEW",
            "response_sha256": digest(response),
            "observed_submission": [
                {
                    k: v
                    for k, v in item.items()
                    if k
                    in {
                        "id",
                        "group",
                        "status",
                        "platform",
                        "gitCommitHash",
                        "runtimeVersion",
                        "appVersion",
                        "appBuildVersion",
                    }
                    and isinstance(v, (str, int))
                }
                for item in (response if isinstance(response, list) else [response])
            ],
            "pending": ["actual_artifact_and_signature", "installed_client_verification"],
            "distributable": False,
        }
    except (OSError, KeyError, TypeError, subprocess.SubprocessError):
        raise ValueError("qa_publish_missing_or_unavailable_proof") from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "publish"])
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--checkout", type=Path, default=Path.cwd())
    parser.add_argument("--proof", type=Path)
    parser.add_argument("--operation", choices=["BUILD_APK", "UPDATE", "ROLLBACK"])
    parser.add_argument("--expected-proof-sha256")
    parser.add_argument("--proof-asset-id", type=int)
    parser.add_argument("--proof-cipher-sha256")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        checkout = args.checkout.resolve(strict=True)
        require(
            not args.output.resolve().is_relative_to(checkout),
            "qa_pipeline_output_must_be_outside_source",
        )
        require(
            not args.output.exists() and not args.output.is_symlink(), "qa_pipeline_output_exists"
        )
        raw = json.loads(args.candidate.read_text())
        if args.action == "prepare":
            if args.operation:
                raw["action"] = args.operation
            if raw["action"] != "BUILD_APK" and args.proof:
                prior = json.loads((args.proof / "previous-native.json").read_text())
                raw["source"]["native_sha"] = prior["source"]["native_sha"]
                raw["native"] = deepcopy(prior["native"])
            c = prepare(raw, checkout)
            canonical = None
            if os.environ.get("GITHUB_ACTIONS") == "true":
                branch = quote(gh_get("")["default_branch"], safe="")
                canonical = gh_get(f"branches/{branch}")["commit"]["sha"]
            from tools.qa_delivery.proofs import declared_transport

            declared = None
            if any((args.expected_proof_sha256, args.proof_asset_id, args.proof_cipher_sha256)):
                require(args.proof is None, "qa_pipeline_declared_and_local_proof_conflict")
                declared = declared_transport(
                    args.proof_asset_id, args.proof_cipher_sha256, args.expected_proof_sha256
                )
            package = {
                "schema_version": "qa-prepared-package/1.0.0",
                "candidate": c,
                "candidate_sha256": digest(c),
                "canonical_sha": canonical,
                "proof_sha256": (
                    args.expected_proof_sha256
                    if declared
                    else proof_digest(args.proof)
                    if args.proof
                    else None
                ),
                "proof_transport": declared,
                "distributable": False,
            }
        else:
            require(args.proof is not None, "qa_publish_private_proof_missing")
            package = publish(raw, checkout, args.proof)
        fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as output:
            json.dump(package, output, indent=2)
        print(
            "QA_PREPARED_NON_DISTRIBUTABLE"
            if args.action == "prepare"
            else "QA_SUBMITTED_VERIFICATION_PENDING"
        )
    except (OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError) as error:
        reason = (
            str(error)
            if isinstance(error, ValueError) and str(error).startswith("qa_")
            else "qa_pipeline_refused"
        )
        parser.exit(1, reason + "\n")


if __name__ == "__main__":
    main()
