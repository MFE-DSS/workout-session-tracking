"""Encrypted transport uses real Node crypto; only GitHub boundaries are replaced."""

import io
import json
import os
import stat
import zipfile

import pytest


@pytest.fixture
def transport(tmp_path):
    private = tmp_path / "private"
    private.mkdir(mode=0o700)
    key = private / "key"
    key.write_bytes(os.urandom(32))
    key.chmod(0o600)
    source = private / "proof"
    source.mkdir(mode=0o700)
    return private, key, source


def populate(source):
    from tools.qa_delivery.proofs import REQUIRED

    for name in REQUIRED:
        (source / name).write_bytes(b"proof-" + name.encode())


def test_real_crypto_roundtrip_random_nonce_private_outputs(transport):
    from tools.qa_delivery.pipeline import proof_digest
    from tools.qa_delivery.proofs import pack, unpack

    private, key, source = transport
    populate(source)
    receipt = pack(source, key, private / "first.aqp")
    pack(source, key, private / "second.aqp")
    assert (private / "first.aqp").read_bytes() != (private / "second.aqp").read_bytes()
    assert b"proof-backup.db" not in (private / "first.aqp").read_bytes()
    unpack(private / "first.aqp", key, private / "import", receipt["proof_sha256"])
    assert proof_digest(private / "import") == proof_digest(source)
    assert stat.S_IMODE((private / "import").stat().st_mode) == 0o700
    assert all(stat.S_IMODE(p.stat().st_mode) == 0o600 for p in (private / "import").iterdir())


@pytest.mark.parametrize(
    "damage",
    ["wrong_key", "magic", "version", "size", "nonce", "cipher", "tag", "truncated", "digest"],
)
def test_authentication_fails_before_any_output(transport, damage):
    from tools.qa_delivery.proofs import pack, unpack

    private, key, source = transport
    populate(source)
    receipt = pack(source, key, private / "proof.aqp")
    payload = bytearray((private / "proof.aqp").read_bytes())
    if damage == "wrong_key":
        key.write_bytes(os.urandom(32))
    elif damage == "digest":
        receipt["proof_sha256"] = "0" * 64
    elif damage == "truncated":
        payload = payload[:-1]
    else:
        position = {"magic": 0, "version": 8, "size": 10, "nonce": 17, "cipher": 31, "tag": -1}[
            damage
        ]
        payload[position] ^= 1
    (private / "proof.aqp").write_bytes(payload)
    with pytest.raises(ValueError, match="qa_proof_"):
        unpack(private / "proof.aqp", key, private / "output", receipt["proof_sha256"])
    assert not (private / "output").exists()


@pytest.mark.parametrize(
    "damage", ["extra", "symlink", "missing", "key_mode", "parent_mode", "existing"]
)
def test_packer_refuses_unsafe_input_and_never_overwrites(transport, damage):
    from tools.qa_delivery.proofs import pack

    private, key, source = transport
    populate(source)
    output = private / "proof.aqp"
    if damage == "extra":
        (source / "auth-secret").write_text("never-transport")
    if damage == "symlink":
        (source / "backup.db").unlink()
        (source / "backup.db").symlink_to(key)
    if damage == "missing":
        (source / "backup.db").unlink()
    if damage == "key_mode":
        key.chmod(0o644)
    if damage == "parent_mode":
        private.chmod(0o755)
    if damage == "existing":
        output.write_bytes(b"keep")
    with pytest.raises(ValueError, match="qa_proof_"):
        pack(source, key, output)
    assert not output.exists() or output.read_bytes() == b"keep"


@pytest.mark.parametrize("damage", ["traversal", "symlink", "duplicate", "compressed", "oversized"])
def test_authenticated_malicious_archive_refused_before_output(transport, monkeypatch, damage):
    from tools.qa_delivery import proofs

    private, key, source = transport
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as archive:
        name = "../backup.db" if damage == "traversal" else "backup.db"
        info = zipfile.ZipInfo(name)
        if damage == "symlink":
            info.create_system = 3
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
        if damage == "compressed":
            info.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(info, b"bad")
        if damage == "duplicate":
            with pytest.warns(UserWarning):
                archive.writestr(info, b"duplicate")
    if damage == "oversized":
        monkeypatch.setattr(proofs, "MAX_FILE", 2)
    encrypted = proofs.crypto("encrypt", key, buf.getvalue())
    (private / "bad.aqp").write_bytes(encrypted)
    with pytest.raises(ValueError, match="qa_proof_"):
        proofs.unpack(private / "bad.aqp", key, private / "output", "a" * 64)
    assert not (private / "output").exists()


class GitHubBoundary:
    """A fixed API/CLI boundary, not a fake crypto or proof verifier."""

    repository = "MFE-DSS/qa-proof-private"

    def __init__(self, blob):
        self.blob = blob
        self.calls = []
        self.private = True
        self.identity = self.repository
        self.asset_id = 321

    def __call__(self, args):
        self.calls.append(args)
        if args[0] == "release":
            return b""
        endpoint = args[-1]
        if endpoint == "repos/" + self.repository:
            return json.dumps(
                {"full_name": self.identity, "private": self.private, "default_branch": "main"}
            ).encode()
        if endpoint.endswith("/commits/main"):
            return json.dumps({"sha": "a" * 40}).encode()
        asset = {
            "id": self.asset_id,
            "name": "qa-proof.aqp",
            "size": len(self.blob),
            "state": "uploaded",
            "digest": "sha256:" + __import__("hashlib").sha256(self.blob).hexdigest(),
        }
        if "/releases/tags/" in endpoint:
            return json.dumps({"assets": [asset]}).encode()
        if endpoint.endswith("/releases/assets/321"):
            return (
                self.blob
                if "Accept: application/octet-stream" in args
                else json.dumps(asset).encode()
            )
        raise AssertionError(args)


@pytest.fixture
def store_case(transport):
    from tools.qa_delivery import proofs

    private, key, source = transport
    populate(source)
    blob = private / "proof.aqp"
    receipt = proofs.pack(source, key, blob)
    config = private / "store.json"
    config.write_text(
        json.dumps(
            {
                "schema_version": "qa-proof-store/1.0.0",
                "state": "CONFIGURED",
                "repository": GitHubBoundary.repository,
            }
        )
    )
    boundary = GitHubBoundary(blob.read_bytes())
    store = proofs.GitHubStore(GitHubBoundary.repository, config=config, command=boundary)
    return store, boundary, blob, receipt


def test_supported_release_upload_private_preflight_and_readback(store_case):
    store, boundary, blob, receipt = store_case
    uploaded = store.upload(blob, receipt)
    assert uploaded["asset_id"] == 321
    assert uploaded["repository"] == GitHubBoundary.repository
    create = next(args for args in boundary.calls if args[:2] == ["release", "create"])
    upload = next(args for args in boundary.calls if args[:2] == ["release", "upload"])
    assert "--prerelease" in create and "--target" in create
    assert "--clobber" not in upload
    assert all("run" not in args for args in boundary.calls)
    assert store.download(uploaded) == blob.read_bytes()


@pytest.mark.parametrize(
    "damage",
    [
        "public",
        "wrong_identity",
        "product",
        "unprovisioned",
        "url",
        "wrong_asset",
        "wrong_checksum",
    ],
)
def test_store_refuses_unsafe_remote_before_upload_or_import(store_case, damage):
    from tools.qa_delivery import proofs

    store, boundary, blob, receipt = store_case
    if damage == "public":
        boundary.private = False
    if damage == "wrong_identity":
        boundary.identity = "OTHER/repository"
    if damage in {"product", "unprovisioned", "url"}:
        config = json.loads(store.config.read_text())
        if damage == "product":
            config["repository"] = proofs.PRODUCT
        elif damage == "url":
            config["repository"] = "https://github.com/MFE-DSS/qa-proof-private"
        else:
            config["state"] = "UNPROVISIONED"
        store.config.write_text(json.dumps(config))
        with pytest.raises(ValueError, match="qa_proof_"):
            proofs.GitHubStore(config["repository"], config=store.config, command=boundary)
    elif damage in {"wrong_asset", "wrong_checksum"}:
        uploaded = store.upload(blob, receipt)
        if damage == "wrong_asset":
            boundary.asset_id = 999
        else:
            boundary.blob = boundary.blob[:-1] + b"X"
        with pytest.raises(ValueError, match="qa_proof_"):
            store.download(uploaded)
    else:
        with pytest.raises(ValueError, match="qa_proof_"):
            store.upload(blob, receipt)
        assert not any(args[0] == "release" for args in boundary.calls)


def test_archive_limits_exercise_each_member_not_only_missing_required(transport, monkeypatch):
    from tools.qa_delivery import proofs

    private, key, source = transport
    populate(source)
    # Include the complete required set, so archive admission reaches member checks.
    for damage in ("traversal", "symlink", "duplicate", "compressed", "oversized", "total"):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as archive:
            for name in sorted(proofs.REQUIRED):
                info = zipfile.ZipInfo(name)
                if name == "backup.db" and damage == "symlink":
                    info.create_system = 3
                    info.external_attr = (stat.S_IFLNK | 0o777) << 16
                if name == "backup.db" and damage == "compressed":
                    info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, b"abc")
            if damage == "traversal":
                archive.writestr("../backup.db", b"bad")
            if damage == "duplicate":
                with pytest.warns(UserWarning):
                    archive.writestr("backup.db", b"bad")
        with monkeypatch.context() as local:
            if damage == "oversized":
                local.setattr(proofs, "MAX_FILE", 2)
            if damage == "total":
                local.setattr(proofs, "MAX_TOTAL", 29)
            encrypted = proofs.crypto("encrypt", key, buf.getvalue())
            (private / "attack.aqp").write_bytes(encrypted)
            with pytest.raises(ValueError, match="qa_proof_archive_"):
                proofs.unpack(private / "attack.aqp", key, private / "output", "a" * 64)
        assert not (private / "output").exists()


def test_import_no_overwrite_and_no_output_for_wrong_approved_digest(store_case, transport):
    from tools.qa_delivery import proofs

    store, _, blob, receipt = store_case
    private, key, _ = transport
    record = proofs.declared_transport(321, receipt["cipher_sha256"], "0" * 64, store.config)
    package = {"proof_transport": record, "proof_sha256": "0" * 64}
    with pytest.raises(ValueError, match="qa_proof_digest_mismatch"):
        proofs.import_package(package, key, private / "new", store=store)
    assert not (private / "new").exists()
    assert not list(private.glob(".qa-*"))
    existing = private / "keep"
    existing.mkdir(mode=0o700)
    (existing / "keep.txt").write_text("keep")
    with pytest.raises(ValueError, match="qa_proof_output_exists"):
        proofs.unpack(blob, key, existing, receipt["proof_sha256"])
    assert (existing / "keep.txt").read_text() == "keep"


def test_unsupported_oversized_cipher_and_source_limits_fail_before_crypto(transport, monkeypatch):
    from tools.qa_delivery import proofs

    private, key, source = transport
    populate(source)
    monkeypatch.setattr(proofs, "MAX_FILE", 2)
    with pytest.raises(ValueError, match="qa_proof_files_too_large"):
        proofs.pack(source, key, private / "output.aqp")
    assert not (private / "output.aqp").exists()
    blob = private / "oversized.aqp"
    with blob.open("wb") as stream:
        stream.truncate(proofs.MAX_BLOB + 1)
    with pytest.raises(ValueError, match="qa_proof_cipher_invalid"):
        proofs.unpack(blob, key, private / "output", "a" * 64)
    assert not (private / "output").exists()


def test_crypto_passes_key_only_via_stdin_and_never_logs_it(transport, monkeypatch, capsys):
    from tools.qa_delivery import proofs

    private, key, _ = transport
    original = proofs.subprocess.run
    monkeypatch.setenv("PROOF_KEY_HEX", key.read_bytes().hex())
    monkeypatch.setenv("GH_TOKEN", "private-read-token")

    def boundary(argv, **kwargs):
        assert key.read_bytes().hex() not in str(argv)
        assert str(key) not in str(argv)
        assert "PROOF_KEY_HEX" not in kwargs["env"]
        assert "GH_TOKEN" not in kwargs["env"]
        assert kwargs["input"][:32] == key.read_bytes()
        return original(argv, **kwargs)

    monkeypatch.setattr(proofs.subprocess, "run", boundary)
    proofs.crypto("encrypt", key, b"data")
    captured = capsys.readouterr()
    assert not captured.out and not captured.err


def test_pack_receipt_hashes_the_exact_captured_bytes(transport, monkeypatch):
    from tools.qa_delivery import proofs

    private, key, source = transport
    populate(source)
    original = proofs.crypto

    def boundary(action, key_path, payload):
        encrypted = original(action, key_path, payload)
        (source / "backup.db").write_bytes(b"changed-after-capture")
        return encrypted

    monkeypatch.setattr(proofs, "crypto", boundary)
    receipt = proofs.pack(source, key, private / "proof.aqp")
    monkeypatch.setattr(proofs, "crypto", original)
    proofs.unpack(private / "proof.aqp", key, private / "imported", receipt["proof_sha256"])
    assert (private / "imported/backup.db").read_bytes() == b"proof-backup.db"


def test_upload_failure_stops_without_automatic_retry_or_cleanup(store_case):
    store, boundary, blob, receipt = store_case

    def command(args):
        if args[:2] == ["release", "upload"]:
            boundary.calls.append(args)
            raise ValueError("qa_proof_github_operation_failed_no_retry")
        return boundary(args)

    store.command = command
    with pytest.raises(ValueError, match="qa_proof_github_operation_failed_no_retry"):
        store.upload(blob, receipt)
    assert len([args for args in boundary.calls if args[:2] == ["release", "create"]]) == 1
    assert len([args for args in boundary.calls if args[:2] == ["release", "upload"]]) == 1
    assert not any("delete" in args for args in boundary.calls)
