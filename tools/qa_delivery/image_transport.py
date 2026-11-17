"""Explicit private image custody. No repository/secret creation or Docker load.

One durable intent precedes a single POST. Reconciliation only reads the same
attempt; a lost response never grants a second upload. DB proof caps are separate.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from urllib.parse import urlencode, urlsplit

import httpx

from tools.qa_delivery.proofs import CONFIG, configured_repository, exclusive_write, private_parent

MAX_PLAINTEXT = 2**31 - 46
MAX_CIPHER = 2**31 - 1
MAX_METADATA = 2 * 1024**2
KEYS = {
    "schema_version",
    "repository",
    "release_id",
    "asset_id",
    "name",
    "cipher_sha256",
    "cipher_bytes",
    "image_sha256",
    "image_bytes",
    "source_sha",
    "run_id",
    "attempt",
}


def require(ok):
    if not ok:
        raise ValueError("qa_image_custody_refused")


def validate_record(record, *, complete=True):
    require(
        isinstance(record, dict) and set(record) == KEYS - (set() if complete else {"asset_id"})
    )
    require(record["schema_version"] == "qa-image-custody/1.0.0")
    require(
        isinstance(record["repository"], str)
        and re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", record["repository"])
    )
    require(record["repository"].casefold() != "mfe-dss/workout-session-tracking")
    for key in (
        "release_id",
        "run_id",
        "attempt",
        "image_bytes",
        "cipher_bytes",
        *(("asset_id",) if complete else ()),
    ):
        require(type(record[key]) is int and record[key] > 0)
    require(
        record["image_bytes"] <= MAX_PLAINTEXT
        and record["cipher_bytes"] == record["image_bytes"] + 45
    )
    for key, size in (("source_sha", 40), ("cipher_sha256", 64), ("image_sha256", 64)):
        require(isinstance(record[key], str) and re.fullmatch(f"[a-f0-9]{{{size}}}", record[key]))
    require(
        record["name"] == f"image-{record['source_sha']}-{record['run_id']}-{record['attempt']}.aqi"
    )
    return record


def durable_intent(path, record):
    path = Path(path)
    require(not any(p.is_symlink() for p in (path, *path.parents)))
    exclusive_write(path, json.dumps(record, sort_keys=True).encode())
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    parent = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(parent)
    finally:
        os.close(parent)


class ImageStore:
    def __init__(self, repository, release_id, token, client, *, config=CONFIG):
        require(configured_repository(config) == repository)
        require(type(release_id) is int and release_id > 0 and bool(token))
        self.repository, self.release_id = repository, release_id
        self.token, self.client = token, client

    def get(self, suffix=""):
        with self.client.stream(
            "GET",
            f"https://api.github.com/repos/{self.repository}{suffix}",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
            },
            follow_redirects=False,
            timeout=30,
        ) as response:
            require(response.status_code == 200)
            data = bytearray()
            for chunk in response.iter_bytes():
                data.extend(chunk)
                require(len(data) <= MAX_METADATA)
            return json.loads(data)

    def preflight(self):
        repo = self.get()
        require(repo.get("private") is True and repo.get("full_name") == self.repository)
        require(self.get(f"/releases/{self.release_id}").get("id") == self.release_id)

    def assets(self):
        result = []
        for page in range(1, 12):
            rows = self.get(f"/releases/{self.release_id}/assets?per_page=100&page={page}")
            require(isinstance(rows, list) and len(rows) <= 100)
            result.extend(rows)
            require(len(result) <= 1000)
            if len(rows) < 100:
                return result
        raise ValueError("qa_image_custody_refused")

    def check_asset(self, asset, record):
        require(
            asset.get("id") == record["asset_id"]
            and asset.get("name") == record["name"]
            and asset.get("state") == "uploaded"
            and asset.get("size") == record["cipher_bytes"]
            and asset.get("digest") == "sha256:" + record["cipher_sha256"]
        )

    def _download(self, record, output=None):
        self.check_asset(self.get(f"/releases/assets/{record['asset_id']}"), record)
        require(
            sum(
                a.get("id") == record["asset_id"] and a.get("name") == record["name"]
                for a in self.assets()
            )
            == 1
        )
        url = f"https://api.github.com/repos/{self.repository}/releases/assets/{record['asset_id']}"
        request = self.client.build_request(
            "GET",
            url,
            headers={"Authorization": f"Bearer {self.token}", "Accept": "application/octet-stream"},
            timeout=60,
        )
        response = self.client.send(request, stream=True, follow_redirects=False, auth=None)
        temporary = None
        try:
            if response.status_code == 302:
                target = urlsplit(response.headers.get("location", ""))
                require(
                    target.scheme == "https"
                    and not target.username
                    and not target.password
                    and not target.port
                    and target.hostname
                    in {"release-assets.githubusercontent.com", "objects.githubusercontent.com"}
                )
                response.close()
                request = self.client.build_request("GET", target.geturl(), timeout=60)
                request.headers.pop("authorization", None)
                response = self.client.send(request, stream=True, follow_redirects=False, auth=None)
            require(response.status_code == 200)
            if output is not None:
                output = private_parent(output)
                fd, name = tempfile.mkstemp(prefix=".image-download-", dir=output.parent)
                temporary = Path(name)
                stream = os.fdopen(fd, "wb")
            else:
                stream = None
            count, digest = 0, hashlib.sha256()
            try:
                for chunk in response.iter_bytes(1024 * 1024):
                    count += len(chunk)
                    require(count <= record["cipher_bytes"] <= MAX_CIPHER)
                    digest.update(chunk)
                    if stream:
                        stream.write(chunk)
                require(
                    count == record["cipher_bytes"]
                    and digest.hexdigest() == record["cipher_sha256"]
                )
                if stream:
                    stream.flush()
                    os.fsync(stream.fileno())
            finally:
                if stream:
                    stream.close()
            self.preflight()  # Visibility/identity is re-read after transfer.
            if temporary is not None:
                os.link(temporary, output)  # Exclusive publication, never clobber.
            return output
        finally:
            response.close()
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    def download(self, record, output):
        validate_record(record)
        require(record["repository"] == self.repository and record["release_id"] == self.release_id)
        self.preflight()
        return self._download(record, output)

    def upload(self, source, staged, payload, intent):
        from tools.qa_delivery.image_receipts import _private_image_digest

        source = Path(source)
        record = dict(
            schema_version="qa-image-custody/1.0.0",
            repository=self.repository,
            release_id=self.release_id,
            name=f"image-{payload['source_sha']}-{payload['run_id']}-{payload['attempt']}.aqi",
            source_sha=payload["source_sha"],
            run_id=payload["run_id"],
            attempt=payload["attempt"],
            **{
                k: staged[k]
                for k in ("image_sha256", "image_bytes", "cipher_sha256", "cipher_bytes")
            },
        )
        validate_record(record, complete=False)
        require(
            staged["schema_version"] == "qa-image-staging/1.0.0"
            and staged["distributable"] is False
        )
        require(
            _private_image_digest(source, MAX_CIPHER)
            == (record["cipher_bytes"], record["cipher_sha256"])
        )
        self.preflight()
        require(not any(a.get("name") == record["name"] for a in self.assets()))
        durable_intent(intent, record)
        # Durable intent exists before any POST. Every later failure is UNKNOWN;
        # callers must retain this file and reconcile it, never issue another POST.
        try:
            fd = os.open(source, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
            with os.fdopen(fd, "rb") as data:
                with self.client.stream(
                    "POST",
                    f"https://uploads.github.com/repos/{self.repository}/releases/{self.release_id}/assets?{urlencode({'name': record['name']})}",
                    headers={
                        "Authorization": f"Bearer {self.token}",
                        "Content-Type": "application/octet-stream",
                        "Content-Length": str(record["cipher_bytes"]),
                    },
                    content=iter(lambda: data.read(1024 * 1024), b""),
                    timeout=300,
                    follow_redirects=False,
                ) as response:
                    require(response.status_code == 201)
                    # The POST response is not a custody receipt. Re-read by ID/name
                    # through the repository, then hash the actual downloaded bytes.
            return self.reconcile(intent)
        except (OSError, ValueError, httpx.HTTPError, TypeError, KeyError):
            raise ValueError("qa_image_upload_unknown_reconcile_required") from None

    def reconcile(self, intent):
        from tools.qa_delivery.image_receipts import _private_image_digest

        _private_image_digest(intent, 65536)
        record = validate_record(json.loads(Path(intent).read_text()), complete=False)
        require(record["repository"] == self.repository and record["release_id"] == self.release_id)
        self.preflight()
        rows = [a for a in self.assets() if a.get("name") == record["name"]]
        require(len(rows) == 1)
        receipt = validate_record({**record, "asset_id": rows[0].get("id")})
        self.check_asset(rows[0], receipt)
        self._download(receipt)
        return receipt


def main():
    import argparse

    from tools.qa_delivery.image_receipts import (
        _private_image_digest,
        acquire_image_receipt,
        restore_image,
    )

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["restore", "reconcile"])
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--intent", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        _private_image_digest(args.config, 65536)
        config = json.loads(args.config.read_text())
        require(set(config) == {"repository", "release_id", "key_file"})
        with httpx.Client(trust_env=False, follow_redirects=False) as client:
            store = ImageStore(
                config["repository"],
                config["release_id"],
                os.environ.get("QA_IMAGE_READ_TOKEN", ""),
                client,
            )
            if args.action == "reconcile":
                require(args.intent is not None and args.reference is None)
                receipt = store.reconcile(args.intent)
                exclusive_write(args.output, json.dumps(receipt, sort_keys=True).encode())
                print("QA_IMAGE_CUSTODY_READ_VERIFIED_NO_RETRY_NO_DEPLOYMENT")
                return
            require(args.reference is not None and args.intent is None)
            _private_image_digest(args.reference, 65536)
            build = acquire_image_receipt(
                json.loads(args.reference.read_text()), client, os.environ.get("GH_TOKEN", "")
            )
            receipt = validate_record(build.get("custody"))
            output = private_parent(args.output)
            with tempfile.TemporaryDirectory(prefix=".image-restore-", dir=output.parent) as tmp:
                cipher = Path(tmp) / "image.aqi"
                store.download(receipt, cipher)
                staged = {
                    "schema_version": "qa-image-staging/1.0.0",
                    "distributable": False,
                    **{
                        k: receipt[k]
                        for k in ("image_bytes", "image_sha256", "cipher_bytes", "cipher_sha256")
                    },
                }
                restore_image(cipher, config["key_file"], output, staged)
            print("QA_IMAGE_RESTORED_AUTHENTICATED_NO_DOCKER_LOAD")
    except (ValueError, OSError, TypeError, KeyError, httpx.HTTPError):
        parser.exit(1, "qa_image_custody_refused_no_automatic_retry\n")


if __name__ == "__main__":
    main()
