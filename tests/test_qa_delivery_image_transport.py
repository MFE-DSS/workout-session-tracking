"""Synthetic HTTP custody boundary; no provider upload or credentials."""

import hashlib
import json

import httpx
import pytest

from tools.qa_delivery.image_transport import MAX_PLAINTEXT, ImageStore

REPO = "example/auren-private"
SHA = "a" * 40


def fixture(tmp_path):
    tmp_path.chmod(0o700)
    config = tmp_path / "store.json"
    config.write_text(
        json.dumps(
            {"schema_version": "qa-proof-store/1.0.0", "state": "CONFIGURED", "repository": REPO}
        )
    )
    source = tmp_path / "image.aqi"
    blob = b"synthetic encrypted bytes" * 20
    source.write_bytes(blob)
    source.chmod(0o600)
    staged = dict(
        schema_version="qa-image-staging/1.0.0",
        image_sha256="b" * 64,
        image_bytes=len(blob) - 45,
        cipher_sha256=hashlib.sha256(blob).hexdigest(),
        cipher_bytes=len(blob),
        distributable=False,
    )
    payload = dict(source_sha=SHA, run_id=12, attempt=1)
    return config, source, blob, staged, payload


def server(blob, *, public=False, lose=False, redirect=False):
    calls = []
    state = {"uploaded": False}
    asset = dict(
        id=42,
        name=f"image-{SHA}-12-1.aqi",
        state="uploaded",
        size=len(blob),
        digest="sha256:" + hashlib.sha256(blob).hexdigest(),
    )

    def handle(request):
        calls.append((request.method, str(request.url), request.headers.get("authorization")))
        path = request.url.path
        if request.url.host == "release-assets.githubusercontent.com":
            assert not request.headers.get("authorization")
            return httpx.Response(200, content=blob)
        if path == f"/repos/{REPO}":
            return httpx.Response(200, json={"full_name": REPO, "private": not public})
        if path == f"/repos/{REPO}/releases/7":
            return httpx.Response(200, json={"id": 7})
        if path == f"/repos/{REPO}/releases/7/assets" and request.method == "GET":
            return httpx.Response(200, json=[asset] if state["uploaded"] else [])
        if request.url.host == "uploads.github.com":
            assert request.read() == blob
            state["uploaded"] = True
            if lose:
                raise httpx.ReadTimeout("synthetic response loss")
            return httpx.Response(201, json=asset)
        if path == f"/repos/{REPO}/releases/assets/42":
            if request.headers.get("accept") == "application/octet-stream":
                if redirect:
                    return httpx.Response(
                        302,
                        headers={
                            "location": "https://release-assets.githubusercontent.com/synthetic"
                        },
                    )
                return httpx.Response(200, content=blob)
            return httpx.Response(200, json=asset)
        raise AssertionError((request.method, request.url))

    return handle, calls


def test_upload_readback_and_private_restore_use_same_ciphertext(tmp_path):
    config, source, blob, staged, payload = fixture(tmp_path)
    handle, calls = server(blob, redirect=True)
    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        store = ImageStore(REPO, 7, "synthetic-token", client, config=config)
        receipt = store.upload(source, staged, payload, tmp_path / "intent.json")
        target = tmp_path / "download.aqi"
        store.download(receipt, target)
    assert target.read_bytes() == blob
    assert receipt["asset_id"] == 42
    assert receipt["image_sha256"] == staged["image_sha256"]
    assert len([x for x in calls if x[0] == "POST"]) == 1


def test_lost_upload_response_keeps_intent_and_never_posts_again(tmp_path):
    config, source, blob, staged, payload = fixture(tmp_path)
    handle, calls = server(blob, lose=True)
    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        store = ImageStore(REPO, 7, "synthetic-token", client, config=config)
        intent = tmp_path / "intent.json"
        with pytest.raises(ValueError, match="unknown"):
            store.upload(source, staged, payload, intent)
        with pytest.raises((ValueError, FileExistsError)):
            store.upload(source, staged, payload, intent)
        receipt = store.reconcile(intent)
        assert receipt["asset_id"] == 42
    assert len([x for x in calls if x[0] == "POST"]) == 1


@pytest.mark.parametrize("damage", ["public", "repository", "checksum", "limit", "symlink"])
def test_upload_refuses_bad_custody_before_any_post(tmp_path, damage):
    config, source, blob, staged, payload = fixture(tmp_path)
    handle, calls = server(blob, public=damage == "public")
    if damage == "checksum":
        staged["cipher_sha256"] = "f" * 64
    if damage == "limit":
        staged["image_bytes"] = MAX_PLAINTEXT + 1
        staged["cipher_bytes"] = staged["image_bytes"] + 45
    if damage == "symlink":
        link = tmp_path / "link"
        link.symlink_to(source)
        source = link
    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        with pytest.raises(ValueError):
            store = ImageStore(
                "other/private" if damage == "repository" else REPO,
                7,
                "synthetic",
                client,
                config=config,
            )
            store.upload(source, staged, payload, tmp_path / "intent.json")
    assert not [x for x in calls if x[0] == "POST"]


def test_existing_download_destination_is_preserved(tmp_path):
    config, source, blob, staged, payload = fixture(tmp_path)
    handle, _ = server(blob)
    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        store = ImageStore(REPO, 7, "synthetic", client, config=config)
        receipt = store.upload(source, staged, payload, tmp_path / "intent.json")
        with pytest.raises((ValueError, FileExistsError)):
            store.download(receipt, source)
    assert source.read_bytes() == blob


def test_provider_envelope_boundary_is_strict():
    assert MAX_PLAINTEXT + 45 == 2**31 - 1


def test_real_codec_roundtrip_through_streaming_custody(tmp_path):
    from tools.qa_delivery.image_receipts import restore_image, stage_image

    config, _, _, _, payload = fixture(tmp_path)
    raw = tmp_path / "synthetic.tar"
    original = b"synthetic Docker archive stand-in" * 5000
    raw.write_bytes(original)
    raw.chmod(0o600)
    key = tmp_path / "key"
    key.write_bytes(bytes(range(32)))
    key.chmod(0o600)
    cipher = tmp_path / "real.aqi"
    staged = stage_image(raw, key, cipher)
    handle, _ = server(cipher.read_bytes(), redirect=True)
    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        store = ImageStore(REPO, 7, "synthetic", client, config=config)
        record = store.upload(cipher, staged, payload, tmp_path / "intent.json")
        downloaded = tmp_path / "real-downloaded.aqi"
        store.download(record, downloaded)
        restore_image(downloaded, key, tmp_path / "restored.tar", staged)
    assert (tmp_path / "restored.tar").read_bytes() == original


def test_unprovisioned_store_performs_no_network_request(tmp_path):
    config, _, _, _, _ = fixture(tmp_path)
    config.write_text(
        json.dumps(
            {"schema_version": "qa-proof-store/1.0.0", "state": "UNPROVISIONED", "repository": None}
        )
    )
    requests = []
    with httpx.Client(
        transport=httpx.MockTransport(lambda request: requests.append(request))
    ) as client:
        with pytest.raises(ValueError, match="unprovisioned"):
            ImageStore(REPO, 7, "synthetic", client, config=config)
    assert requests == []


def test_build_payload_binds_custody_to_exact_archive_and_run(tmp_path):
    from tests.test_qa_delivery_image_receipts import image_fixture
    from tools.qa_delivery.image_receipts import validate_payload

    config, source, blob, staged, payload = fixture(tmp_path)
    handle, _ = server(blob)
    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        record = ImageStore(REPO, 7, "synthetic", client, config=config).upload(
            source, staged, payload, tmp_path / "intent.json"
        )
    build, _, _ = image_fixture()
    build.update(
        run_id=12,
        attempt=1,
        exported_image_bytes=staged["image_bytes"],
        exported_image_sha256=staged["image_sha256"],
        custody=record,
    )
    validate_payload(build)
    build["custody"]["image_sha256"] = "c" * 64
    with pytest.raises(ValueError):
        validate_payload(build)


def test_intent_file_and_directory_are_synced_before_post(tmp_path, monkeypatch):
    import os
    import stat

    from tools.qa_delivery import image_transport

    config, source, blob, staged, payload = fixture(tmp_path)
    handle, _ = server(blob)
    events = []

    def sync(fd):
        events.append("directory" if stat.S_ISDIR(os.fstat(fd).st_mode) else "file")

    def serve(request):
        if request.method == "POST":
            events.append("POST")
        return handle(request)

    monkeypatch.setattr(image_transport.os, "fsync", sync)
    with httpx.Client(transport=httpx.MockTransport(serve)) as client:
        ImageStore(REPO, 7, "synthetic", client, config=config).upload(
            source, staged, payload, tmp_path / "intent.json"
        )
    assert events[:3] == ["file", "directory", "POST"]


def test_failed_intent_sync_prevents_any_post(tmp_path, monkeypatch):
    from tools.qa_delivery import image_transport

    config, source, blob, staged, payload = fixture(tmp_path)
    handle, calls = server(blob)

    def fail(fd):
        raise OSError("synthetic sync failure")

    monkeypatch.setattr(image_transport.os, "fsync", fail)
    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        with pytest.raises(OSError):
            ImageStore(REPO, 7, "synthetic", client, config=config).upload(
                source, staged, payload, tmp_path / "intent.json"
            )
    assert not [c for c in calls if c[0] == "POST"]
