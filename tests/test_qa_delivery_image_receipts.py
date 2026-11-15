"""Independent image provenance; fixtures are external boundaries, never admissions."""

import hashlib
import io
import json
import zipfile

import httpx
import pytest

REPO = "MFE-DSS/workout-session-tracking"
SHA = "a" * 40


def image_fixture():
    payload = dict(
        schema_version="qa-image-build-payload/1.0.0",
        repository=REPO,
        workflow_path=".github/workflows/qa-release.yml",
        workflow_ref=f"{REPO}/.github/workflows/qa-release.yml@{SHA}",
        run_id=123,
        attempt=1,
        job="prepare-qa-image",
        source_sha=SHA,
        context_sha256="c" * 64,
        Dockerfile_sha256="d" * 64,
        base_image_digest="sha256:" + "b" * 64,
        platform="linux/amd64",
        exported_image_sha256="e" * 64,
        exported_image_bytes=1024,
        image_id="sha256:" + "f" * 64,
        completed_at="2026-11-15T10:00:00Z",
    )
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_STORED) as z:
        z.writestr("qa-image-build.json", json.dumps(payload))
    blob = buf.getvalue()
    pages = {
        "": {"default_branch": "trunk"},
        "branches/trunk/protection": {"required_status_checks": {"contexts": [], "checks": []}},
        "actions/runs/123": dict(
            id=123,
            head_sha=SHA,
            event="workflow_dispatch",
            path=payload["workflow_path"],
            run_attempt=1,
            status="completed",
            conclusion="success",
            repository={"full_name": REPO},
        ),
        "actions/runs/123/attempts/1/jobs?per_page=100": {
            "jobs": [
                dict(
                    name="prepare-qa-image",
                    status="completed",
                    conclusion="success",
                    head_sha=SHA,
                    started_at="2026-11-15T09:59:00Z",
                    completed_at="2026-11-15T10:00:20Z",
                )
            ]
        },
        "actions/artifacts/456": dict(
            id=456,
            name="qa-image-build",
            expired=False,
            size_in_bytes=len(blob),
            digest="sha256:" + hashlib.sha256(blob).hexdigest(),
            workflow_run={"id": 123, "head_sha": SHA},
        ),
        f"commits/{SHA}/check-runs?per_page=100": {"check_runs": []},
    }
    from tools.qa_delivery.pipeline import FLOOR

    pages[f"commits/{SHA}/check-runs?per_page=100"]["check_runs"] = [
        dict(name=n, head_sha=SHA, status="completed", conclusion="success", app={"id": 15368})
        for n in FLOOR
    ]
    return payload, blob, pages


def acquire(pages, blob, reference=None):
    from tools.qa_delivery.image_receipts import acquire_image_receipt

    def serve(request):
        assert request.url.host == "api.github.com"
        key = str(request.url).split(f"/repos/{REPO}/")[1]
        if key == "actions/artifacts/456/zip":
            return httpx.Response(200, content=blob)
        return httpx.Response(200, json=pages[key])

    with httpx.Client(transport=httpx.MockTransport(serve)) as client:
        return acquire_image_receipt(
            reference or {"run_id": 123, "attempt": 1, "artifact_id": 456, "source_sha": SHA},
            client,
            "synthetic-token",
        )


def test_independent_image_receipt_binds_download_and_ci():
    payload, blob, pages = image_fixture()
    receipt = acquire(pages, blob)
    assert receipt["schema_version"] == "qa-image-build/1.0.0"
    assert receipt["artifact_id"] == 456 and receipt["image_id"] == payload["image_id"]
    assert receipt["exported_image_sha256"] != receipt["image_id"].split(":")[1]


@pytest.mark.parametrize(
    "damage",
    ["source", "workflow", "attempt", "job", "artifact", "digest", "ci", "oversize", "unknown"],
)
def test_forged_or_incomplete_image_provenance_refused(damage):
    payload, blob, pages = image_fixture()
    if damage == "source":
        pages["actions/runs/123"]["head_sha"] = "b" * 40
    if damage == "workflow":
        pages["actions/runs/123"]["path"] = ".github/workflows/other.yml"
    if damage == "attempt":
        pages["actions/runs/123"]["run_attempt"] = 2
    if damage == "job":
        pages["actions/runs/123/attempts/1/jobs?per_page=100"]["jobs"][0]["conclusion"] = "failure"
    if damage == "artifact":
        pages["actions/artifacts/456"]["workflow_run"]["id"] = 124
    if damage == "digest":
        blob += b"forged"
    if damage == "ci":
        pages[f"commits/{SHA}/check-runs?per_page=100"]["check_runs"][0]["conclusion"] = "failure"
    if damage in {"oversize", "unknown"}:
        if damage == "oversize":
            payload["exported_image_bytes"] = 2**31 + 1
        else:
            payload["self_attested"] = True
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("qa-image-build.json", json.dumps(payload))
        blob = buf.getvalue()
        pages["actions/artifacts/456"]["size_in_bytes"] = len(blob)
        pages["actions/artifacts/456"]["digest"] = "sha256:" + hashlib.sha256(blob).hexdigest()
    with pytest.raises(ValueError, match="qa_image"):
        acquire(pages, blob)


def test_image_preparation_requires_actual_single_human_deployment_review():
    from tools.qa_delivery.image_receipts import image_preparation_approval

    env = {
        "GITHUB_REPOSITORY": REPO,
        "GITHUB_RUN_ID": "123",
        "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_SHA": SHA,
    }
    pages = {
        "environments/qa-release": {
            "name": "qa-release",
            "id": 42,
            "protection_rules": [
                {
                    "type": "required_reviewers",
                    "prevent_self_review": True,
                    "reviewers": [{"type": "User", "reviewer": {"id": 10}}],
                }
            ],
        },
        "actions/runs/123": {
            "head_sha": SHA,
            "event": "workflow_dispatch",
            "status": "in_progress",
            "path": ".github/workflows/qa-release.yml",
            "run_attempt": 1,
            "actor": {"id": 11},
        },
        "actions/runs/123/approvals": [
            {
                "state": "approved",
                "user": {"type": "User", "id": 10},
                "comment": "APPROVE_QA_IMAGE " + SHA,
                "environments": [{"id": 42, "name": "qa-release"}],
            }
        ],
    }
    image_preparation_approval(env, pages.__getitem__)
    pages["actions/runs/123/approvals"][0]["comment"] = "GO MERGE"
    with pytest.raises(ValueError, match="qa_image"):
        image_preparation_approval(env, pages.__getitem__)


def test_private_image_staging_is_bounded_authenticated_and_separate_from_db_caps(tmp_path):
    from tools.qa_delivery.image_receipts import restore_image, stage_image
    from tools.qa_delivery.proofs import MAX_FILE, MAX_TOTAL

    tmp_path.chmod(0o700)
    source = tmp_path / "image.tar"
    source.write_bytes(b"synthetic-image-bytes" * 200)
    source.chmod(0o600)
    key = tmp_path / "key"
    key.write_bytes(bytes(range(32)))
    key.chmod(0o600)
    encrypted = tmp_path / "image.aqi"
    receipt = stage_image(source, key, encrypted)
    assert receipt["image_sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert receipt["cipher_sha256"] == hashlib.sha256(encrypted.read_bytes()).hexdigest()
    restored = tmp_path / "restored.tar"
    restore_image(encrypted, key, restored, receipt)
    assert restored.read_bytes() == source.read_bytes()
    assert MAX_FILE == 128 * 1024**2 and MAX_TOTAL == 256 * 1024**2
    with pytest.raises(ValueError):
        restore_image(encrypted, key, restored, receipt)
    damaged = bytearray(encrypted.read_bytes())
    damaged[-1] ^= 1
    encrypted.write_bytes(damaged)
    output = tmp_path / "must-not-exist.tar"
    with pytest.raises(ValueError):
        restore_image(encrypted, key, output, receipt)
    assert not output.exists()
