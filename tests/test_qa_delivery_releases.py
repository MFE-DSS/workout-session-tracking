"""Release gates consume separately collected evidence, never candidate assertions."""

from copy import deepcopy

import pytest

from tools.qa_delivery.releases import classify_update, validate_candidate

SHA = "a" * 40
CERT = "12b13109a2a41e2e2c0e97578364793e659a7548da4ce210d0dbd2f912f4bc75"


def candidate():
    return {
        "schema_version": "qa-release/1.0.0",
        "release_id": "rel-03-test",
        "state": "PREPARED",
        "action": "BUILD_APK",
        "source": {"native_sha": SHA, "js_sha": SHA},
        "native": {
            "app_version": "0.0.2",
            "version_code": 3,
            "package": "dev.auren.releaseqa02",
            "certificate_sha256": CERT,
            "runtime_version": None,
            "fingerprint": None,
            "updates_enabled": True,
            "storage_schema_sha256": "d" * 64,
        },
        "eas": {
            "project_id": "c7243bfc-29b3-4486-aafe-e69b9c904bbe",
            "channel": "qa",
            "branch": "qa",
            "platform": "android",
            "build_id": None,
            "build_url": None,
        },
        "js": {"update_group": None, "update_id": None, "assets_sha256": None},
        "artifact": {"sha256": None, "url": None},
        "target": None,
        "compatibility": {
            "api": "first-session-runtime/3.0.0",
            "inventory": "plan-calibration-inventory/2.0.0",
            "server_schema": "plan_v3_20261107_01",
            "local_schema": "first-session-local/3.0.0",
        },
    }


def evidence(c):
    """Synthetic trusted-adapter fixture; does not authorize any real publication."""
    return {
        "schema_version": "qa-release-evidence/1.0.0",
        "git": {
            "head_sha": SHA,
            "native_sha": SHA,
            "dirty_paths": [],
            "storage_schema_sha256": "d" * 64,
            "canonical_sha": SHA,
            "ancestor_shas": [SHA],
        },
        "ci": {
            "head_sha": SHA,
            "required_checks": ["tests"],
            "checks": [
                {
                    "name": "tests",
                    "head_sha": SHA,
                    "conclusion": "success",
                    "run_id": 123,
                    "url": "https://github.com/MFE-DSS/workout-session-tracking/actions/runs/123",
                }
            ],
        },
        "review": {
            "head_sha": SHA,
            "base_sha": SHA,
            "decision": "APPROVED",
            "reference": "https://github.com/MFE-DSS/workout-session-tracking/pull/123",
            "visual": "NOT_APPLICABLE",
        },
        "approval": {
            "head_sha": SHA,
            "environment": "qa-release",
            "deployment_id": 123,
            "reviewer": "human-operator",
            "decision": "APPROVED",
        },
        "target": {
            "schema_version": "qa-target-attestation/1.0.0",
            "state": "ATTESTED",
            "environment_id": "qa-rel03",
            "url": "https://qa-rel03.onrender.com",
            "data_scope": "SYNTHETIC_ONLY",
            "availability": "STABLE",
            "source_sha": SHA,
            "backup_reference": "private-backup-receipt",
            "continuity_reference": "private-cutover-receipt",
            "deployment_reference": "provider-deployment-receipt",
            "compatibility": deepcopy(c["compatibility"]),
        },
        "previous_native": {
            "package": "dev.auren.releaseqa02",
            "version_code": 2,
            "certificate_sha256": CERT,
        },
    }


def approved():
    c = candidate()
    e = evidence(c)
    c["state"] = "APPROVED"
    c["native"].update(runtime_version="1" * 40, fingerprint="1" * 40)
    c["target"] = deepcopy(e["target"])
    return c, e


def test_prepared_unknowns_stay_null_non_distributable():
    c = candidate()
    got = validate_candidate(c, {})
    assert got["target"] is None
    assert got["eas"]["build_id"] is None
    assert got["distributable"] is False
    assert "target" in got["pending"]
    assert "distributable" not in c


def test_approved_build_accepts_only_separate_complete_evidence():
    c, e = approved()
    assert validate_candidate(c, e)["pending"] == ["build_artifact"]
    assert validate_candidate(c, e)["distributable"] is False


@pytest.mark.parametrize(
    "section,key,value",
    [
        ("git", "dirty_paths", ["clients/mobile/ConnectedApp.tsx"]),
        ("git", "ancestor_shas", []),
        ("git", "head_sha", "b" * 40),
        ("ci", "checks", []),
        ("ci", "head_sha", "b" * 40),
        ("approval", "decision", "PENDING"),
        ("approval", "deployment_id", None),
        ("review", "visual", "PENDING"),
        ("review", "base_sha", "b" * 40),
        ("target", "url", "https://fake.trycloudflare.com"),
        ("target", "url", "https://spignos.com"),
        ("target", "url", "https://example.com"),
        ("target", "continuity_reference", None),
        ("previous_native", "certificate_sha256", "f" * 64),
        ("previous_native", "version_code", 3),
    ],
)
def test_publication_refuses_missing_or_incompatible_evidence(section, key, value):
    c, e = approved()
    e[section][key] = value
    if section == "target":
        c["target"] = deepcopy(e["target"])
    with pytest.raises(ValueError):
        validate_candidate(c, e)


@pytest.mark.parametrize(
    "change",
    [
        "red_ci",
        "missing_native",
        "wrong_channel",
        "wrong_project",
        "wrong_platform",
        "future_api",
        "future_schema",
        "fake_evidence",
    ],
)
def test_candidate_cannot_assert_its_own_readiness(change):
    c, e = approved()
    if change == "red_ci":
        e["ci"]["checks"][0]["conclusion"] = "failure"
    if change == "missing_native":
        c["native"]["fingerprint"] = None
    if change == "wrong_channel":
        c["eas"]["channel"] = "production"
    if change == "wrong_project":
        c["eas"]["project_id"] = "other"
    if change == "wrong_platform":
        c["eas"]["platform"] = "ios"
    if change == "future_api":
        c["compatibility"]["api"] = "first-session-runtime/4.0.0"
    if change == "future_schema":
        c["compatibility"]["local_schema"] = "first-session-local/4.0.0"
    if change == "fake_evidence":
        e = {"ci_green": True, "merged": True, "approved": True}
    with pytest.raises(ValueError):
        validate_candidate(c, e)


def test_built_requires_actual_eas_artifact_and_matching_binary_identity():
    c, e = approved()
    c["state"] = "BUILT"
    with pytest.raises(ValueError):
        validate_candidate(c, e)


def compatible():
    c = candidate()
    c["native"].update(runtime_version="1" * 40, fingerprint="1" * 40)
    return c


def test_js_change_retains_native_source_and_can_be_ota():
    before, after = compatible(), compatible()
    after["source"]["js_sha"] = "b" * 40
    assert classify_update(before, after) == "JS_ASSETS_ONLY"
    assert after["source"]["native_sha"] == SHA


@pytest.mark.parametrize(
    "section,key,value",
    [
        ("native", "fingerprint", "2" * 40),
        ("native", "runtime_version", "2" * 40),
        ("native", "package", "other"),
        ("native", "version_code", 4),
        ("native", "certificate_sha256", "f" * 64),
        ("native", "storage_schema_sha256", "e" * 64),
        ("compatibility", "local_schema", "first-session-local/4.0.0"),
    ],
)
def test_native_or_sqlite_change_requires_apk_even_if_other_hashes_match(section, key, value):
    before, after = compatible(), compatible()
    after[section][key] = value
    assert classify_update(before, after) == "NEW_APK_REQUIRED"


@pytest.mark.parametrize("before", [{}, None, {"native": {"updates_enabled": False}}])
def test_unknown_and_old_disabled_binary_never_ota_compatible(before):
    assert classify_update(before, compatible()) == "UNAVAILABLE"


def test_metadata_environment_uses_clean_git_and_immutable_native_receipt(tmp_path):
    import subprocess

    from tools.qa_delivery.releases import metadata_environment

    def git(*args):
        return subprocess.check_output(["git", "-C", str(tmp_path), *args], text=True).strip()

    git("init", "-q")
    (tmp_path / "source.js").write_text("revision A\n")
    git("add", ".")
    git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "A")
    native = git("rev-parse", "HEAD")
    c = candidate()
    c["source"] = {"native_sha": native, "js_sha": native}
    assert metadata_environment(c, tmp_path) == {
        "EXPO_PUBLIC_QA_NATIVE_SHA": native,
        "EXPO_PUBLIC_QA_JS_SHA": native,
    }
    (tmp_path / "source.js").write_text("revision B\n")
    with pytest.raises(ValueError):
        metadata_environment(c, tmp_path)
    git("add", ".")
    git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "B")
    c["source"]["js_sha"] = git("rev-parse", "HEAD")
    c["action"] = "UPDATE"
    with pytest.raises(ValueError):
        metadata_environment(c, tmp_path)
    receipt = {"source": {"native_sha": native}, "artifact": {"sha256": "f" * 64}}
    assert metadata_environment(c, tmp_path, receipt)["EXPO_PUBLIC_QA_NATIVE_SHA"] == native
    (tmp_path / "untracked.txt").write_text("untracked must refuse\n")
    with pytest.raises(ValueError):
        metadata_environment(c, tmp_path, receipt)


def test_unknown_fields_do_not_become_receipt_facts():
    c = candidate()
    c["native"]["owner_token"] = "never-receipt-this"
    with pytest.raises(ValueError):
        validate_candidate(c, {})


@pytest.mark.parametrize("value", [False, "yes", 1])
def test_updates_state_must_be_explicit_boolean(value):
    c = candidate()
    c["native"]["updates_enabled"] = value
    with pytest.raises(ValueError):
        validate_candidate(c, {})


def test_update_uses_prior_native_receipt_without_reusing_a_build_version():
    c, e = approved()
    c["action"] = "UPDATE"
    previous = deepcopy(c)
    previous["source"]["js_sha"] = "b" * 40
    # Immutable prior receipt includes native identity and compatibility, not just a code.
    e["previous_native"] = previous
    assert validate_candidate(c, e)["pending"] == ["update_artifact"]
    previous["native"]["updates_enabled"] = False
    with pytest.raises(ValueError):
        validate_candidate(c, e)


def test_actual_storage_digest_changes_when_sql_changes_without_version_bump(tmp_path):
    from tools.qa_delivery.releases import storage_schema_digest

    storage = tmp_path / "clients/mobile/src/storage"
    storage.mkdir(parents=True)
    schema = storage / "journal.ts"
    schema.write_text('const schema="CREATE TABLE facts (id INTEGER)";\n')
    before = storage_schema_digest(tmp_path)
    # Same local version string and same native fingerprint cannot hide this change.
    schema.write_text('const schema="CREATE TABLE facts (id INTEGER, value TEXT)";\n')
    assert storage_schema_digest(tmp_path) != before
    (storage / "journal.test.ts").write_text("test-only\n")
    after = storage_schema_digest(tmp_path)
    (storage / "journal.test.ts").write_text("test-only changed\n")
    assert storage_schema_digest(tmp_path) == after


def test_built_receipt_demands_artifact_ids_checksum_and_native_binding():
    c, e = approved()
    c["state"] = "BUILT"
    c["eas"].update(
        build_id="edc4b258-cfcf-49c3-8991-883902030576",
        build_url="https://expo.dev/accounts/grimais/projects/auren-vnext-lab/builds/edc4b258-cfcf-49c3-8991-883902030576",
    )
    c["artifact"] = {"sha256": "f" * 64, "url": "https://expo.dev/artifacts/test-only.apk"}
    e["artifact"] = {
        **deepcopy(c["artifact"]),
        "native": deepcopy(c["native"]),
        "source": deepcopy(c["source"]),
        **deepcopy(c["eas"]),
    }
    assert validate_candidate(c, e)["distributable"] is True
    e["artifact"]["source"]["native_sha"] = "b" * 40
    with pytest.raises(ValueError):
        validate_candidate(c, e)
