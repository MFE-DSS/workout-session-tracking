"""Explicit encrypted private-release-asset transport; never a publication grant.

The product repository is PUBLIC. Only ciphertext may leave operator staging.
Repository creation, credentials and upload require the separate external GO.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
import zipfile
from pathlib import Path

PRODUCT = "MFE-DSS/workout-session-tracking"
CONFIG = Path(__file__).resolve().parents[2] / "docs/release/rel-03/proof-store.json"
REQUIRED = frozenset(
    {
        "backup.db",
        "backup.db.manifest.json",
        "restored.db",
        "cutover.json",
        "ownership-anchor.json",
        "previous-native.json",
        "release-backup.db",
        "release-backup.db.manifest.json",
        "release-export.db",
        "release-export.db.manifest.json",
        "release-backup.json",
    }
)
ALLOWED = REQUIRED | {"known-good-update.json", "restored.db.manifest.json"}
MAX_FILE = 128 * 1024 * 1024
MAX_TOTAL = 256 * 1024 * 1024
MAX_BLOB = MAX_TOTAL + 65536 + 45
ASSET_NAME = "qa-proof.aqp"


def require(condition, reason):
    if not condition:
        raise ValueError("qa_proof_" + reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def hash_valid(value):
    return isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value) is not None


def key_bytes(path):
    path = Path(path)
    require(not path.is_symlink() and not path.parent.is_symlink(), "key_symlink")
    info, parent = path.stat(), path.parent.stat()
    require(
        stat.S_ISREG(info.st_mode)
        and stat.S_IMODE(info.st_mode) == 0o600
        and info.st_uid == os.getuid()
        and parent.st_uid == os.getuid()
        and stat.S_IMODE(parent.st_mode) == 0o700,
        "key_not_private",
    )
    require(not path.resolve().is_relative_to(Path(__file__).resolve().parents[2]), "key_in_source")
    require(info.st_size == 32, "key_size")
    return path.read_bytes()


def crypto(action, key, payload):
    require(len(payload) <= MAX_BLOB, "payload_too_large")
    executable = shutil.which("node")
    require(executable, "node_missing")
    result = subprocess.run(  # noqa: S603 — fixed checked-in script, binary stdin key
        [executable, str(Path(__file__).with_name("proof_crypto.cjs")), action],
        input=key_bytes(key) + payload,
        capture_output=True,
        timeout=120,
        check=False,
        env={"PATH": os.environ.get("PATH", "")},
    )
    require(result.returncode == 0, "authentication_or_crypto_failed")
    return result.stdout


def private_parent(output):
    output = Path(output)
    require(not output.exists() and not output.is_symlink(), "output_exists")
    require(
        not output.parent.is_symlink()
        and stat.S_IMODE(output.parent.stat().st_mode) == 0o700
        and output.parent.stat().st_uid == os.getuid(),
        "output_parent_not_private",
    )
    require(
        not output.resolve().is_relative_to(Path(__file__).resolve().parents[2]), "output_in_source"
    )
    return output


def exclusive_write(output, payload):
    output = private_parent(output)
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
    except BaseException:
        output.unlink(missing_ok=True)
        raise


def pack(source, key, output):
    from tools.qa_delivery.pipeline import digest

    source, output = Path(source), private_parent(output)
    require(not source.is_symlink() and source.is_dir(), "source_invalid")
    names = {p.name for p in source.iterdir()}
    require(REQUIRED <= names <= ALLOWED, "files_not_allowlisted")
    total = 0
    captured = {}
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as archive:
        for name in sorted(names):
            path = source / name
            require(not path.is_symlink() and path.is_file(), "file_not_regular")
            require(path.stat().st_size <= MAX_FILE, "files_too_large")
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
            with os.fdopen(fd, "rb") as stream:
                require(stat.S_ISREG(os.fstat(stream.fileno()).st_mode), "file_not_regular")
                data = stream.read(MAX_FILE + 1)
            total += len(data)
            require(len(data) <= MAX_FILE and total <= MAX_TOTAL, "files_too_large")
            captured[name] = sha(data)
            archive.writestr(name, data)
    payload = crypto("encrypt", key, buffer.getvalue())
    exclusive_write(output, payload)
    return {
        "schema_version": "qa-proof-staging/1.0.0",
        "proof_sha256": digest(captured),
        "cipher_sha256": sha(payload),
        "cipher_size": len(payload),
        "distributable": False,
    }


def archive_files(payload):
    require(len(payload) <= MAX_TOTAL + 65536, "archive_too_large")
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            infos = archive.infolist()
            names = [p.filename for p in infos]
            require(
                len(names) == len(set(names)) and REQUIRED <= set(names) <= ALLOWED, "archive_names"
            )
            total = 0
            for item in infos:
                mode = item.external_attr >> 16
                total += item.file_size
                require(
                    item.filename in ALLOWED
                    and not item.is_dir()
                    and stat.S_IFMT(mode) in {0, stat.S_IFREG}
                    and item.compress_type == zipfile.ZIP_STORED
                    and item.flag_bits & 1 == 0
                    and item.file_size <= MAX_FILE
                    and total <= MAX_TOTAL,
                    "archive_member_invalid",
                )
            return {item.filename: archive.read(item) for item in infos}
    except (zipfile.BadZipFile, RuntimeError, NotImplementedError):
        raise ValueError("qa_proof_archive_invalid") from None


def unpack(blob, key, output, expected):
    from tools.qa_delivery.pipeline import proof_digest

    output = private_parent(output)
    require(hash_valid(expected), "expected_hash_invalid")
    blob = Path(blob)
    require(
        not blob.is_symlink() and blob.is_file() and blob.stat().st_size <= MAX_BLOB,
        "cipher_invalid",
    )
    files = archive_files(crypto("decrypt", key, blob.read_bytes()))
    # Validate everything in a private sibling; failed authentication/digest never
    # creates the accepted output. rename is only used after exclusive mkdir.
    with tempfile.TemporaryDirectory(prefix=".qa-proof-", dir=output.parent) as temporary:
        staging = Path(temporary)
        for name, data in files.items():
            exclusive_write(staging / name, data)
        require(proof_digest(staging) == expected, "digest_mismatch")
        output.mkdir(mode=0o700)  # refuses any concurrent/existing destination
        try:
            for path in staging.iterdir():
                path.rename(output / path.name)
        except BaseException:
            shutil.rmtree(output)
            raise
    return output


def configured_repository(config=CONFIG):
    data = json.loads(Path(config).read_text())
    require(
        data.get("schema_version") == "qa-proof-store/1.0.0" and data.get("state") == "CONFIGURED",
        "store_unprovisioned",
    )
    repository = data.get("repository")
    require(
        isinstance(repository, str)
        and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*", repository)
        and repository.casefold() != PRODUCT.casefold(),
        "repository_invalid",
    )
    return repository


def gh_command(args):
    executable = shutil.which("gh")
    require(executable, "github_cli_missing")
    try:
        result = subprocess.run(  # noqa: S603 — fixed gh operations, no shell/URLs
            [executable, *args],
            capture_output=True,
            timeout=120,
            check=False,
            env={
                "PATH": os.environ.get("PATH", ""),
                "GH_HOST": "github.com",
                "GH_TOKEN": os.environ.get("GH_TOKEN", ""),
                "GH_PROMPT_DISABLED": "1",
            },
        )
        require(result.returncode == 0, "github_operation_failed_no_retry")
        return result.stdout
    except (OSError, subprocess.SubprocessError):
        raise ValueError("qa_proof_github_operation_failed_no_retry") from None


class GitHubStore:
    """Future explicit private repo operations; constructor performs no remote write."""

    def __init__(self, repository, *, config=CONFIG, command=gh_command):
        self.config = Path(config)
        self.repository = configured_repository(config)
        require(repository == self.repository, "repository_configuration_mismatch")
        self.command = command

    def get(self, suffix=""):
        payload = self.command(["api", "--method", "GET", f"repos/{self.repository}{suffix}"])
        require(len(payload) <= 2 * 1024 * 1024, "github_metadata_too_large")
        try:
            return json.loads(payload)
        except (ValueError, TypeError):
            raise ValueError("qa_proof_github_metadata_invalid") from None

    def preflight(self):
        require(configured_repository(self.config) == self.repository, "configuration_changed")
        actual = self.get()
        require(
            actual.get("private") is True and actual.get("full_name") == self.repository,
            "private_repository_required",
        )
        return actual

    def asset(self, record):
        require(record.get("repository") == self.repository, "asset_repository_mismatch")
        asset_id = record.get("asset_id")
        require(type(asset_id) is int and asset_id > 0, "asset_id_invalid")
        require(hash_valid(record.get("cipher_sha256")), "cipher_hash_invalid")
        actual = self.get(f"/releases/assets/{asset_id}")
        require(
            actual.get("id") == asset_id
            and actual.get("name") == ASSET_NAME
            and actual.get("state") == "uploaded"
            and type(actual.get("size")) is int
            and 45 < actual["size"] <= MAX_BLOB,
            "asset_identity_invalid",
        )
        if actual.get("digest") is not None:
            require(
                actual["digest"] == "sha256:" + record["cipher_sha256"], "asset_digest_mismatch"
            )
        return actual

    def download(self, record):
        self.preflight()
        actual = self.asset(record)
        payload = self.command(
            [
                "api",
                "--method",
                "GET",
                "-H",
                "Accept: application/octet-stream",
                f"repos/{self.repository}/releases/assets/{record['asset_id']}",
            ]
        )
        require(
            len(payload) == actual["size"] and sha(payload) == record["cipher_sha256"],
            "cipher_readback_mismatch",
        )
        return payload

    def upload(self, blob, receipt):
        blob = Path(blob)
        require(
            not blob.is_symlink() and blob.is_file() and 45 < blob.stat().st_size <= MAX_BLOB,
            "cipher_invalid",
        )
        payload = blob.read_bytes()
        require(
            payload[:9] == b"AURENQPF\x01"
            and int.from_bytes(payload[9:17], "big") == len(payload) - 45
            and sha(payload) == receipt.get("cipher_sha256")
            and hash_valid(receipt.get("proof_sha256")),
            "staging_receipt_mismatch",
        )
        repo = self.preflight()
        from urllib.parse import quote

        head = self.get("/commits/" + quote(repo["default_branch"], safe=""))["sha"]
        require(re.fullmatch(r"[a-f0-9]{40}", head), "private_head_invalid")
        tag = "qa-proof-" + os.urandom(16).hex()
        # Private repository, explicit unique prerelease at its actual HEAD.
        # gh refuses existing releases/assets; never --clobber or an auto retry.
        self.preflight()
        self.command(
            [
                "release",
                "create",
                tag,
                "--repo",
                self.repository,
                "--target",
                head,
                "--prerelease",
                "--title",
                tag,
                "--notes",
                "Encrypted QA proof; not distributable.",
            ]
        )
        with tempfile.TemporaryDirectory(prefix="qa-cipher-") as temporary:
            staged = Path(temporary) / ASSET_NAME
            exclusive_write(staged, payload)
            self.command(["release", "upload", tag, str(staged), "--repo", self.repository])
        release = self.get("/releases/tags/" + tag)
        assets = release.get("assets", [])
        require(
            len(assets) == 1 and assets[0].get("name") == ASSET_NAME,
            "uploaded_asset_missing_or_ambiguous",
        )
        record = {
            "schema_version": "qa-proof-transport/1.0.0",
            "repository": self.repository,
            "asset_id": assets[0]["id"],
            "cipher_sha256": receipt["cipher_sha256"],
            "proof_sha256": receipt["proof_sha256"],
            "verification": "CIPHERTEXT_READBACK",
            "distributable": False,
        }
        require(self.download(record) == payload, "uploaded_readback_mismatch")
        return record


def declared_transport(asset_id, cipher_sha256, expected, config=None):
    require(
        type(asset_id) is int
        and asset_id > 0
        and hash_valid(cipher_sha256)
        and hash_valid(expected),
        "declared_transport_invalid",
    )
    return {
        "schema_version": "qa-proof-transport/1.0.0",
        "repository": configured_repository() if config is None else configured_repository(config),
        "asset_id": asset_id,
        "cipher_sha256": cipher_sha256,
        "proof_sha256": expected,
        "verification": "DECLARED_NOT_VERIFIED",
        "distributable": False,
    }


def import_package(package, key, output, *, store=None):
    record = package["proof_transport"]
    require(
        record.get("verification") == "DECLARED_NOT_VERIFIED"
        and record.get("proof_sha256") == package["proof_sha256"]
        and hash_valid(package["proof_sha256"]),
        "package_transport_mismatch",
    )
    store = store or GitHubStore(record["repository"])
    output = private_parent(output)
    payload = store.download(record)
    with tempfile.TemporaryDirectory(prefix=".qa-cipher-", dir=output.parent) as temporary:
        blob = Path(temporary) / ASSET_NAME
        exclusive_write(blob, payload)
        return unpack(blob, key, output, package["proof_sha256"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["pack", "upload", "import"])
    parser.add_argument("--source", type=Path)
    parser.add_argument("--key", type=Path)
    parser.add_argument("--blob", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--package", type=Path)
    parser.add_argument("--repository")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        private_parent(args.output)
        if args.action == "pack":
            require(args.source and args.key and args.receipt, "pack_arguments_missing")
            private_parent(args.receipt)
            receipt = pack(args.source, args.key, args.output)
            exclusive_write(args.receipt, json.dumps(receipt, indent=2).encode())
        elif args.action == "upload":
            require(args.blob and args.receipt and args.repository, "upload_arguments_missing")
            receipt = GitHubStore(args.repository).upload(
                args.blob, json.loads(args.receipt.read_text())
            )
            exclusive_write(args.output, json.dumps(receipt, indent=2).encode())
        else:
            require(args.package and args.key, "import_arguments_missing")
            import_package(json.loads(args.package.read_text()), args.key, args.output)
        print("QA_PROOF_" + args.action.upper() + "_NON_DISTRIBUTABLE")
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        reason = (
            str(error)
            if isinstance(error, ValueError) and str(error).startswith("qa_proof_")
            else "qa_proof_refused"
        )
        parser.exit(1, reason + "\n")


if __name__ == "__main__":
    main()
