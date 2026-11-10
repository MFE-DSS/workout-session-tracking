"""Fail-closed release receipt validation; no network, publication or trust acquisition.

`evidence` MUST come from the trusted orchestrator's independent GitHub/provider
queries, not a candidate JSON or dispatch input. This module checks consistency;
it cannot authenticate caller-supplied documents. PREPARED never grants release.
"""

from __future__ import annotations

import re
from copy import deepcopy
from urllib.parse import urlsplit

PROJECT = "c7243bfc-29b3-4486-aafe-e69b9c904bbe"
PACKAGE = "dev.auren.releaseqa02"
CERTIFICATE = "12b13109a2a41e2e2c0e97578364793e659a7548da4ce210d0dbd2f912f4bc75"
COMPATIBILITY = {
    "api": "first-session-runtime/3.0.0",
    "inventory": "plan-calibration-inventory/2.0.0",
    "server_schema": "plan_v3_20261107_01",
    "local_schema": "first-session-local/3.0.0",
}


def _require(condition):
    if not condition:
        raise ValueError("qa_release_refused")


def _hex(value, size):
    return isinstance(value, str) and re.fullmatch(f"[0-9a-f]{{{size}}}", value) is not None


def _text(value):
    return isinstance(value, str) and 0 < len(value) <= 512 and value.strip() == value


def stable_qa_url(value):
    """Only an independently attested dedicated stable public HTTPS QA origin."""
    try:
        url = urlsplit(value)
        host = url.hostname or ""
        labels = host.split(".")
        return (
            url.scheme == "https"
            and not url.username
            and not url.password
            and not url.port
            and url.path in {"", "/"}
            and not url.query
            and not url.fragment
            and len(labels) >= 3
            and all(re.fullmatch(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", s) for s in labels)
            and any(re.fullmatch(r"qa(?:-[a-z0-9-]+)?", s) for s in labels[:-2])
            and not any(
                s in {"prod", "production", "example", "invalid", "localhost"} for s in labels
            )
            and not any(
                host == h or host.endswith("." + h)
                for h in (
                    "spignos.com",
                    "trycloudflare.com",
                    "ngrok.io",
                    "ngrok-free.app",
                    "loca.lt",
                    "localtest.me",
                    "example.com",
                    "example.org",
                    "example.net",
                )
            )
        )
    except (ValueError, TypeError, AttributeError):
        return False


def _target(target, compatibility):
    _require(isinstance(target, dict))
    _require(target.get("schema_version") == "qa-target-attestation/1.0.0")
    _require(target.get("state") == "ATTESTED" and target.get("availability") == "STABLE")
    _require(target.get("data_scope") == "SYNTHETIC_ONLY")
    _require(re.fullmatch(r"qa-[a-z0-9_-]{3,60}", target.get("environment_id", "")))
    _require(stable_qa_url(target.get("url")) and _hex(target.get("source_sha"), 40))
    _require(target.get("compatibility") == compatibility)
    for key in ("backup_reference", "continuity_reference", "deployment_reference"):
        _require(_text(target.get(key)))


def _publication_evidence(c, evidence):
    _require(evidence.get("schema_version") == "qa-release-evidence/1.0.0")
    source, git, ci = c["source"], evidence["git"], evidence["ci"]
    sha = source["js_sha"]
    _require(git["head_sha"] == sha and git["native_sha"] == source["native_sha"])
    _require(git["dirty_paths"] == [] and _hex(git["canonical_sha"], 40))
    _require(sha in git["ancestor_shas"] and ci["head_sha"] == sha)
    required = ci["required_checks"]
    _require(isinstance(required, list) and bool(required) and len(set(required)) == len(required))
    for name in required:
        checks = [check for check in ci["checks"] if check.get("name") == name]
        _require(len(checks) == 1)
        check = checks[0]
        _require(check["head_sha"] == sha and check["conclusion"] == "success")
        _require(type(check["run_id"]) is int and check["run_id"] > 0)
        _require(
            check["url"].startswith(
                "https://github.com/MFE-DSS/workout-session-tracking/actions/runs/"
            )
        )
    review, approval = evidence["review"], evidence["approval"]
    _require(review["head_sha"] == sha and review["base_sha"] == git["canonical_sha"])
    _require(
        review["decision"] == "APPROVED" and review["visual"] in {"APPROVED", "NOT_APPLICABLE"}
    )
    _require(_text(review["reference"]))
    _require(approval["head_sha"] == sha and approval["environment"] == "qa-release")
    _require(approval["decision"] == "APPROVED" and _text(approval["reviewer"]))
    _require(type(approval["deployment_id"]) is int and approval["deployment_id"] > 0)
    _target(c["target"], c["compatibility"])
    _require(evidence["target"] == c["target"])
    previous_receipt, native = evidence["previous_native"], c["native"]
    previous = previous_receipt.get("native", previous_receipt)
    _require(previous["package"] == native["package"] == PACKAGE)
    _require(previous["certificate_sha256"] == native["certificate_sha256"] == CERTIFICATE)
    _require(type(previous["version_code"]) is int)
    if c["action"] == "BUILD_APK":
        _require(native["version_code"] > previous["version_code"])
    else:
        _require(native["version_code"] == previous["version_code"])
        _require(classify_update(previous_receipt, c) == "JS_ASSETS_ONLY")
    _require(_hex(native["fingerprint"], 40) and native["runtime_version"] == native["fingerprint"])
    _require(native["updates_enabled"] is True)
    _require(git["storage_schema_sha256"] == native["storage_schema_sha256"])


def validate_candidate(raw, evidence):
    """Normalize candidate or raise ValueError; return fresh allowlisted fields.

    PREPARED permits null future IDs and target, reports pending, never distributable.
    APPROVED checks pre-publication evidence (future build/update IDs may be null).
    BUILT+ require observed artifacts; VERIFIED/ROLLED_BACK also require installation
    evidence bound to native and current JS identities. Evidence must be trusted by
    the caller, collected at the final gate; no candidate boolean grants readiness.
    """
    try:
        _require(isinstance(raw, dict) and isinstance(evidence, dict))
        keys = (
            "schema_version",
            "release_id",
            "state",
            "action",
            "source",
            "native",
            "eas",
            "js",
            "artifact",
            "target",
            "compatibility",
        )
        c = {k: deepcopy(raw[k]) for k in keys}
        _require(c["schema_version"] == "qa-release/1.0.0")
        _require(re.fullmatch(r"[a-z0-9][a-z0-9._-]{2,80}", c["release_id"]))
        _require(c["state"] in {"PREPARED", "APPROVED", "BUILT", "VERIFIED", "ROLLED_BACK"})
        _require(c["action"] in {"BUILD_APK", "UPDATE", "ROLLBACK"})
        _require(set(c["source"]) == {"native_sha", "js_sha"})
        _require(all(_hex(v, 40) for v in c["source"].values()))
        native, eas = c["native"], c["eas"]
        shapes = {
            "native": {
                "app_version",
                "version_code",
                "package",
                "certificate_sha256",
                "runtime_version",
                "fingerprint",
                "updates_enabled",
                "storage_schema_sha256",
            },
            "eas": {"project_id", "channel", "branch", "platform", "build_id", "build_url"},
            "js": {"update_group", "update_id", "assets_sha256"},
            "artifact": {"sha256", "url"},
        }
        for key, shape in shapes.items():
            _require(set(c[key]) == shape)
        _require(native["updates_enabled"] is True)
        _require(_hex(native["storage_schema_sha256"], 64))
        for key in ("runtime_version", "fingerprint"):
            _require(native[key] is None or _hex(native[key], 40))
        _require(native["package"] == PACKAGE and native["certificate_sha256"] == CERTIFICATE)
        _require(re.fullmatch(r"\d+\.\d+\.\d+", native["app_version"]))
        _require(type(native["version_code"]) is int and 2 < native["version_code"] < 2100000000)
        _require(eas["project_id"] == PROJECT and eas["channel"] == eas["branch"] == "qa")
        _require(eas["platform"] == "android" and c["compatibility"] == COMPATIBILITY)
        # Force explicit nullable fields; omitted fields never silently become facts.
        for fields, names in (
            (native, ("runtime_version", "fingerprint", "updates_enabled")),
            (eas, ("build_id", "build_url")),
            (c["js"], ("update_group", "update_id", "assets_sha256")),
            (c["artifact"], ("sha256", "url")),
        ):
            for name in names:
                _require(name in fields)
        pending = []
        if c["state"] == "PREPARED":
            if c["target"] is None:
                pending.append("target")
            else:
                _target(c["target"], c["compatibility"])
            pending.extend(["trusted_release_evidence", "build_artifact"])
        else:
            _publication_evidence(c, evidence)
            if c["state"] == "APPROVED":
                pending.append(
                    "build_artifact" if c["action"] == "BUILD_APK" else "update_artifact"
                )
            else:
                artifact = evidence["artifact"]
                _require(_hex(c["artifact"]["sha256"], 64) and _text(c["artifact"]["url"]))
                _require(artifact["sha256"] == c["artifact"]["sha256"])
                _require(artifact["url"] == c["artifact"]["url"])
                _require(artifact["native"] == native and artifact["source"] == c["source"])
                _require(_text(eas["build_id"]) and _text(eas["build_url"]))
                _require(
                    artifact["build_id"] == eas["build_id"]
                    and artifact["build_url"] == eas["build_url"]
                )
                if c["action"] != "BUILD_APK":
                    for name in ("update_group", "update_id", "assets_sha256"):
                        _require(_text(c["js"][name]) and artifact["js"][name] == c["js"][name])
                if c["state"] in {"VERIFIED", "ROLLED_BACK"}:
                    installation = evidence["installation"]
                    _require(installation["source"] == c["source"])
                    _require(installation["native"] == native and installation["js"] == c["js"])
                    _require(_text(installation["reference"]))
        c["pending"] = pending
        c["distributable"] = c["state"] in {"BUILT", "VERIFIED", "ROLLED_BACK"} and not pending
        return c
    except (KeyError, TypeError, ValueError, AttributeError):
        raise ValueError("qa_release_refused") from None


def classify_update(before, after):
    """Conservative compatibility only, not a publication authorization.

    Accept a full previous receipt, or previous_native containing native fields plus
    `compatibility`, `source`, `eas`. Missing/disabled Updates always UNAVAILABLE.
    SQLite schema is explicitly compared even if Expo's native fingerprint matches.
    """
    try:
        b = before.get("native", before)
        a = after["native"]
        if b["updates_enabled"] is not True or a["updates_enabled"] is not True:
            return "UNAVAILABLE"
        for n in (a, b):
            if (
                not _hex(n["fingerprint"], 40)
                or not _text(n["runtime_version"])
                or not _hex(n["storage_schema_sha256"], 64)
            ):
                return "UNAVAILABLE"
        for key in (
            "fingerprint",
            "runtime_version",
            "package",
            "certificate_sha256",
            "app_version",
            "version_code",
            "storage_schema_sha256",
        ):
            if b[key] != a[key]:
                return "NEW_APK_REQUIRED"
        if before["compatibility"] != after["compatibility"]:
            return "NEW_APK_REQUIRED"
        if before["source"]["native_sha"] != after["source"]["native_sha"]:
            return "NEW_APK_REQUIRED"
        for key in ("project_id", "channel", "branch", "platform"):
            if before["eas"][key] != after["eas"][key]:
                return "NEW_APK_REQUIRED"
        return "JS_ASSETS_ONLY"
    except (KeyError, TypeError, AttributeError):
        return "UNAVAILABLE"


def metadata_environment(raw, checkout, native_receipt=None):
    """Generate deterministic JS-only Metro env from a completely clean checkout.

    Dirty means tracked changes OR non-ignored untracked files anywhere in checkout.
    Outputs must be written outside source (or ignored staging), never committed.
    For OTA, caller supplies the independently verified immutable native receipt;
    its native SHA stays A while the checkout HEAD/current JS SHA advances to B.
    A generated output checksum belongs in the release receipt, not native extra.
    """
    import shutil
    import subprocess
    from pathlib import Path

    try:
        c = validate_candidate({**raw, "state": "PREPARED"}, {})
        root = Path(checkout).resolve(strict=True)

        git_path = shutil.which("git")
        _require(git_path is not None)

        def git(*args):
            return subprocess.check_output(  # noqa: S603 — fixed Git commands, validated SHA; no shell
                [git_path, "-C", str(root), *args],
                text=True,
                stderr=subprocess.DEVNULL,
                timeout=10,
            ).strip()

        _require(git("status", "--porcelain", "--untracked-files=all") == "")
        head = git("rev-parse", "HEAD")
        _require(head == c["source"]["js_sha"])
        native = c["source"]["native_sha"]
        if c["action"] == "BUILD_APK":
            _require(native == head)
        else:
            _require(native_receipt["source"]["native_sha"] == native)
            _require(_hex(native_receipt["artifact"]["sha256"], 64))
        _require(git("cat-file", "-t", native) == "commit")
        return {"EXPO_PUBLIC_QA_NATIVE_SHA": native, "EXPO_PUBLIC_QA_JS_SHA": head}
    except (OSError, subprocess.SubprocessError, KeyError, TypeError, ValueError):
        raise ValueError("qa_metadata_refused") from None


def storage_schema_digest(checkout):
    """Conservative SQLite boundary: hash all production storage source paths/bytes.

    The trusted collector computes this from the exact clean JS checkout, and the
    immutable native receipt records its original value. Tests are excluded, no
    production storage source is excluded (including web/ownership/journal code).
    """
    import hashlib
    from pathlib import Path

    root = Path(checkout) / "clients/mobile/src/storage"
    files = sorted(p for p in root.glob("*.ts") if not p.name.endswith(".test.ts"))
    _require(bool(files))
    digest = hashlib.sha256()
    for path in files:
        _require(not path.is_symlink())
        digest.update(path.name.encode() + b"\0" + path.read_bytes() + b"\0")
    return digest.hexdigest()
