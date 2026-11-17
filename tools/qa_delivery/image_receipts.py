"""Image metadata acquired independently from GitHub; optional private custody.

The uploaded payload cannot contain its own not-yet-assigned artifact ID. Acquisition
adds that independently read immutable ID to the normalized build receipt.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import quote

import httpx

REPO = "MFE-DSS/workout-session-tracking"
WORKFLOW = ".github/workflows/qa-release.yml"
MAX_IMAGE = 2 * 1024**3
MAX_RECEIPT = 64 * 1024
PAYLOAD_KEYS = {
    "schema_version",
    "repository",
    "workflow_path",
    "workflow_ref",
    "run_id",
    "attempt",
    "job",
    "source_sha",
    "context_sha256",
    "Dockerfile_sha256",
    "base_image_digest",
    "platform",
    "exported_image_sha256",
    "exported_image_bytes",
    "image_id",
    "completed_at",
}


def require(ok):
    if not ok:
        raise ValueError("qa_image_provenance_refused")


def sha(payload):
    return hashlib.sha256(payload).hexdigest()


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result)
        result[key] = value
    return result


def _time(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(result.utcoffset() is not None)
    return result


def validate_payload(p):
    require(isinstance(p, dict) and set(p) in (PAYLOAD_KEYS, PAYLOAD_KEYS | {"custody"}))
    require(p["schema_version"] == "qa-image-build-payload/1.0.0")
    require(p["repository"] == REPO and p["workflow_path"] == WORKFLOW)
    require(isinstance(p["source_sha"], str) and re.fullmatch("[a-f0-9]{40}", p["source_sha"]))
    require(p["workflow_ref"] == f"{REPO}/{WORKFLOW}@{p['source_sha']}")
    require(p["job"] == "prepare-qa-image" and p["platform"] == "linux/amd64")
    for key in ("run_id", "attempt", "exported_image_bytes"):
        require(type(p[key]) is int and p[key] > 0)
    require(p["exported_image_bytes"] <= MAX_IMAGE)
    for key in ("context_sha256", "Dockerfile_sha256", "exported_image_sha256"):
        require(isinstance(p[key], str) and re.fullmatch("[a-f0-9]{64}", p[key]))
    for key in ("base_image_digest", "image_id"):
        require(isinstance(p[key], str) and re.fullmatch("sha256:[a-f0-9]{64}", p[key]))
    _time(p["completed_at"])
    if "custody" in p:
        from tools.qa_delivery.image_transport import validate_record

        custody = validate_record(p["custody"])
        require(all(custody[k] == p[k] for k in ("source_sha", "run_id", "attempt")))
        require(
            custody["image_bytes"] == p["exported_image_bytes"]
            and custody["image_sha256"] == p["exported_image_sha256"]
        )
    return p


def acquire_image_receipt(reference, client, token):
    """Only public metadata downloaded; request IDs are locators, not assertions."""
    try:
        require(
            set(reference) == {"run_id", "attempt", "artifact_id", "source_sha"} and bool(token)
        )
        for key in ("run_id", "attempt", "artifact_id"):
            require(type(reference[key]) is int and reference[key] > 0)
        require(
            isinstance(reference["source_sha"], str)
            and re.fullmatch("[a-f0-9]{40}", reference["source_sha"])
        )

        def get(path, binary=False):
            url = f"https://api.github.com/repos/{REPO}/{path}"
            with client.stream(
                "GET",
                url,
                headers={"Authorization": f"Bearer {token}"},
                timeout=15,
                follow_redirects=False,
            ) as response:
                # GitHub's signed artifact redirect is unauthenticated on a closed
                # storage-host suffix. Never forward the bearer to storage.
                if binary and response.status_code == 302:
                    from urllib.parse import urlsplit

                    dest = response.headers.get("location", "")
                    parsed = urlsplit(dest)
                    require(
                        parsed.scheme == "https"
                        and not parsed.username
                        and not parsed.password
                        and not parsed.port
                        and (parsed.hostname or "").endswith(
                            (".blob.core.windows.net", ".actions.githubusercontent.com")
                        )
                    )
                    with client.stream("GET", dest, timeout=15, follow_redirects=False) as stored:
                        require(stored.status_code == 200)
                        data = bytearray()
                        for part in stored.iter_bytes():
                            data.extend(part)
                            require(len(data) <= MAX_RECEIPT)
                        return bytes(data)
                require(response.status_code == 200)
                data = bytearray()
                for part in response.iter_bytes():
                    data.extend(part)
                    require(len(data) <= MAX_RECEIPT)
                return bytes(data) if binary else json.loads(data, object_pairs_hook=_pairs)

        run_id, attempt, artifact_id = (reference[k] for k in ("run_id", "attempt", "artifact_id"))
        run = get(f"actions/runs/{run_id}")
        require(
            run["id"] == run_id
            and run["repository"]["full_name"] == REPO
            and run["path"] == WORKFLOW
            and run["head_sha"] == reference["source_sha"]
            and run["event"] == "workflow_dispatch"
            and run["run_attempt"] == attempt
            and run["status"] == "completed"
            and run["conclusion"] == "success"
        )
        jobs = get(f"actions/runs/{run_id}/attempts/{attempt}/jobs?per_page=100")["jobs"]
        jobs = [j for j in jobs if j["name"] == "prepare-qa-image"]
        require(len(jobs) == 1)
        job = jobs[0]
        require(
            job["status"] == "completed"
            and job["conclusion"] == "success"
            and job["head_sha"] == run["head_sha"]
        )
        artifact = get(f"actions/artifacts/{artifact_id}")
        require(
            artifact["id"] == artifact_id
            and artifact["name"] == "qa-image-build"
            and artifact["expired"] is False
            and artifact["workflow_run"]["id"] == run_id
            and artifact["workflow_run"]["head_sha"] == run["head_sha"]
            and type(artifact["size_in_bytes"]) is int
            and 0 < artifact["size_in_bytes"] <= MAX_RECEIPT
        )
        blob = get(f"actions/artifacts/{artifact_id}/zip", True)
        require(
            len(blob) == artifact["size_in_bytes"] and artifact["digest"] == "sha256:" + sha(blob)
        )
        with zipfile.ZipFile(io.BytesIO(blob)) as archive:
            require(archive.namelist() == ["qa-image-build.json"])
            item = archive.infolist()[0]
            require(item.file_size <= MAX_RECEIPT and item.flag_bits & 1 == 0)
            payload = validate_payload(json.loads(archive.read(item), object_pairs_hook=_pairs))
        require(
            payload["run_id"] == run_id
            and payload["attempt"] == attempt
            and payload["source_sha"] == run["head_sha"]
        )
        require(
            _time(job["started_at"]) <= _time(payload["completed_at"]) <= _time(job["completed_at"])
        )
        from tools.qa_delivery.pipeline import FLOOR

        branch = quote(get("")["default_branch"], safe="")
        protection = get(f"branches/{branch}/protection")["required_status_checks"]
        required = (
            set(FLOOR) | set(protection["contexts"]) | {x["context"] for x in protection["checks"]}
        )
        checks = get(f"commits/{run['head_sha']}/check-runs?per_page=100")["check_runs"]
        for name in required:
            found = [x for x in checks if x["name"] == name]
            require(
                len(found) == 1
                and found[0]["head_sha"] == run["head_sha"]
                and found[0]["status"] == "completed"
                and found[0]["conclusion"] == "success"
                and found[0]["app"]["id"] == 15368
            )
        return {**payload, "schema_version": "qa-image-build/1.0.0", "artifact_id": artifact_id}
    except (
        OSError,
        ValueError,
        KeyError,
        TypeError,
        AttributeError,
        zipfile.BadZipFile,
        httpx.HTTPError,
    ):
        raise ValueError("qa_image_provenance_refused") from None


def image_preparation_approval(env, get=None):
    """Image compute has its own protected operator approval, never GO MERGE."""
    from tools.qa_delivery.pipeline import gh_get, protected_environment

    get = get or gh_get
    try:
        require(env.get("GITHUB_REPOSITORY") == REPO and env.get("GITHUB_RUN_ATTEMPT") == "1")
        run_id = env["GITHUB_RUN_ID"]
        require(re.fullmatch("[1-9][0-9]*", run_id))
        protection, rule = protected_environment(get)
        prevent_self_review = rule.get("prevent_self_review")
        require(type(prevent_self_review) is bool)
        run = get(f"actions/runs/{run_id}")
        require(
            run["head_sha"] == env["GITHUB_SHA"]
            and run["path"] == WORKFLOW
            and run["event"] == "workflow_dispatch"
            and run["status"] == "in_progress"
            and run["run_attempt"] == 1
        )
        reviewers = {r["reviewer"]["id"] for r in rule["reviewers"] if r["type"] == "User"}
        approvals = [
            a
            for a in get(f"actions/runs/{run_id}/approvals")
            if any(
                e["id"] == protection["id"] and e["name"] == "qa-release" for e in a["environments"]
            )
        ]
        require(len(approvals) == 1)
        approval = approvals[0]
        require(
            approval["state"] == "approved"
            and approval["user"]["type"] == "User"
            and approval["user"]["id"] in reviewers
            and (not prevent_self_review or approval["user"]["id"] != run["actor"]["id"])
            and approval["comment"].strip() == "APPROVE_QA_IMAGE " + env["GITHUB_SHA"]
        )
        if approval["user"]["id"] == run["actor"]["id"]:
            # Explicit OPS-02 solo exception: MFE-DSS, sole direct reviewer.
            require(len(rule["reviewers"]) == 1 and reviewers == {156458952})
    except (ValueError, KeyError, TypeError):
        raise ValueError("qa_image_preparation_approval_required") from None


def prepare_image(checkout, output, environment=None, *, custody=None):
    """Manual producer: clean exact archive and optional explicit private custody.

    Private image custody/transport is a separate authorized operation. This job
    removes its disposable local image/archive after recording their fingerprints.
    Default metadata-only behavior is preserved. Custody must be explicitly wired
    after its separate operational approval; neither path deploys or releases.
    """
    env = os.environ if environment is None else environment
    from tools.qa_delivery.pipeline import git

    require(
        env.get("GITHUB_ACTIONS") == "true"
        and env.get("GITHUB_EVENT_NAME") == "workflow_dispatch"
        and env.get("GITHUB_REPOSITORY") == REPO
    )
    source = git(checkout, "rev-parse", "HEAD")
    require(
        source == env.get("GITHUB_SHA")
        and not git(checkout, "status", "--porcelain", "--untracked-files=all")
    )
    require(env.get("GITHUB_WORKFLOW_REF", "").startswith(REPO + "/" + WORKFLOW + "@"))
    require(
        re.fullmatch("[1-9][0-9]*", env.get("GITHUB_RUN_ID", ""))
        and re.fullmatch("[1-9][0-9]*", env.get("GITHUB_RUN_ATTEMPT", ""))
    )
    image_preparation_approval(env)
    from tools.qa_delivery.pipeline import gh_get

    canonical = gh_get("branches/" + quote(gh_get("")["default_branch"], safe=""))["commit"]["sha"]
    require(git(checkout, "merge-base", source, canonical) == source)
    output = Path(output)
    require(not output.exists() and output.parent.is_dir() and not output.is_symlink())
    docker = shutil.which("docker")
    require(docker)

    def command(args, capture=True, timeout=900):
        result = subprocess.run(  # noqa: S603 — fixed Git/Docker command table, checked SHA, no shell
            args,
            stdout=subprocess.PIPE if capture else subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=timeout,
        )
        require(result.returncode == 0)
        return result.stdout

    tag = "auren-qa-prepare:" + source
    with tempfile.TemporaryDirectory(prefix="qa-image-") as temp:
        root = Path(temp)
        archive = root / "source.tar"
        context = root / "context"
        context.mkdir()
        gitexe = shutil.which("git")
        require(gitexe)
        command(
            [
                gitexe,
                "-C",
                str(checkout),
                "archive",
                "--format=tar",
                "--output",
                str(archive),
                source,
            ]
        )
        with tarfile.open(archive) as tar:
            # data filter rejects absolute/escaping links and special files.
            tar.extractall(context, filter="data")
        dockerfile = context / "deploy/qa/Dockerfile"
        source_dockerfile = dockerfile.read_bytes()
        require(
            source_dockerfile.startswith(b"#")
            and b"FROM python:3.11.14-slim\n" in source_dockerfile
        )
        command([docker, "pull", "--platform", "linux/amd64", "python:3.11.14-slim"])
        base = json.loads(
            command(
                [
                    docker,
                    "image",
                    "inspect",
                    "python:3.11.14-slim",
                    "--format",
                    "{{json .RepoDigests}}",
                ]
            )
        )
        require(isinstance(base, list) and len(base) == 1)
        digest = base[0].split("@")[-1]
        require(re.fullmatch("sha256:[a-f0-9]{64}", digest))
        dockerfile.write_bytes(
            source_dockerfile.replace(
                b"FROM python:3.11.14-slim\n", f"FROM python@{digest}\n".encode(), 1
            )
        )
        try:
            command(
                [
                    docker,
                    "build",
                    "--platform",
                    "linux/amd64",
                    "--build-arg",
                    "SOURCE_SHA=" + source,
                    "-f",
                    str(dockerfile),
                    "-t",
                    tag,
                    str(context),
                ],
                False,
            )
            image = json.loads(command([docker, "image", "inspect", tag, "--format", "{{json .}}"]))
            require(image["Architecture"] == "amd64" and image["Os"] == "linux")
            image_file = root / "image.tar"
            command([docker, "save", "--output", str(image_file), tag], False)
            require(0 < image_file.stat().st_size <= MAX_IMAGE)
            h = hashlib.sha256()
            with image_file.open("rb") as stream:
                while part := stream.read(1024 * 1024):
                    h.update(part)
            payload = validate_payload(
                dict(
                    schema_version="qa-image-build-payload/1.0.0",
                    repository=REPO,
                    workflow_path=WORKFLOW,
                    workflow_ref=f"{REPO}/{WORKFLOW}@{source}",
                    run_id=int(env["GITHUB_RUN_ID"]),
                    attempt=int(env["GITHUB_RUN_ATTEMPT"]),
                    job="prepare-qa-image",
                    source_sha=source,
                    context_sha256=sha(archive.read_bytes()),
                    Dockerfile_sha256=sha(source_dockerfile),
                    base_image_digest=digest,
                    platform="linux/amd64",
                    exported_image_sha256=h.hexdigest(),
                    exported_image_bytes=image_file.stat().st_size,
                    image_id=image["Id"],
                    completed_at=datetime.now(UTC).isoformat(),
                )
            )
            if custody is not None:
                store, key, intent = custody
                image_file.chmod(0o600)
                staged = stage_image(image_file, key, root / "image.aqi")
                payload["custody"] = store.upload(root / "image.aqi", staged, payload, intent)
                validate_payload(payload)
            with output.open("x") as out:
                json.dump(payload, out, sort_keys=True)
            return payload
        finally:
            command([docker, "image", "rm", tag], False, 30)


# Streaming image encryption uses the installed Node runtime, separately from the
# intentionally much smaller DB proof codec. No key appears in argv or output.
_IMAGE_CODEC = r"""
const fs=require('node:fs'),crypto=require('node:crypto');
const [action,input,output]=process.argv.slice(1),MAX=2*1024**3;
let src,dst,temporary=output+'.partial-'+crypto.randomBytes(16).toString('hex'),created=false;
try {
  const key=Buffer.alloc(32); if(fs.readSync(0,key,0,32,null)!==32)throw Error();
  src=fs.openSync(input,fs.constants.O_RDONLY|fs.constants.O_NOFOLLOW);
  const size=fs.fstatSync(src).size;
  let header,cipher,remaining;
  if(action==='encrypt') {
    if(size<1||size>MAX)throw Error();
    header=Buffer.alloc(29);header.write('AURENIMG');header[8]=1;
    header.writeBigUInt64BE(BigInt(size),9);crypto.randomBytes(12).copy(header,17);
    cipher=crypto.createCipheriv('aes-256-gcm',key,header.subarray(17));remaining=size;
  } else if(action==='decrypt') {
    if(size<46||size>MAX+45)throw Error();header=Buffer.alloc(29);
    if(fs.readSync(src,header,0,29,null)!==29||header.subarray(0,8).toString()!=='AURENIMG'||header[8]!==1||header.readBigUInt64BE(9)!==BigInt(size-45))throw Error();
    cipher=crypto.createDecipheriv('aes-256-gcm',key,header.subarray(17));remaining=size-45;
  } else throw Error();
  cipher.setAAD(header);
  dst=fs.openSync(temporary,fs.constants.O_WRONLY|fs.constants.O_CREAT|fs.constants.O_EXCL,0o600);created=true;
  function write(data){let p=0;while(p<data.length)p+=fs.writeSync(dst,data,p,data.length-p);}
  if(action==='encrypt')write(header);
  const buffer=Buffer.alloc(1024*1024);
  while(remaining){const n=fs.readSync(src,buffer,0,Math.min(buffer.length,remaining),null);if(!n)throw Error();write(cipher.update(buffer.subarray(0,n)));remaining-=n;}
  if(action==='decrypt'){const tag=Buffer.alloc(16);if(fs.readSync(src,tag,0,16,null)!==16)throw Error();cipher.setAuthTag(tag);}
  write(cipher.final());if(action==='encrypt')write(cipher.getAuthTag());
  fs.fsyncSync(dst);fs.closeSync(dst);dst=undefined;
  // New final destination only, and no unauthenticated plaintext is published.
  fs.linkSync(temporary,output);
} catch {process.exitCode=1;}
finally {if(src!==undefined)fs.closeSync(src);if(dst!==undefined)fs.closeSync(dst);if(created)fs.unlinkSync(temporary);}
"""


def _private_image_digest(path, maximum):
    import stat

    path = Path(path)
    require(not any(p.is_symlink() for p in (path, *path.parents)))
    require(
        path.parent.stat().st_uid == os.getuid()
        and stat.S_IMODE(path.parent.stat().st_mode) == 0o700
    )
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        info = os.fstat(stream.fileno())
        require(
            stat.S_ISREG(info.st_mode)
            and info.st_uid == os.getuid()
            and stat.S_IMODE(info.st_mode) == 0o600
            and 0 < info.st_size <= maximum
        )
        h = hashlib.sha256()
        count = 0
        while chunk := stream.read(1024 * 1024):
            count += len(chunk)
            require(count <= maximum)
            h.update(chunk)
        require(count == info.st_size)
        return count, h.hexdigest()


def _image_crypto(action, source, key, output):
    from tools.qa_delivery.proofs import key_bytes, private_parent

    output = private_parent(output)
    executable = shutil.which("node")
    require(executable)
    result = subprocess.run(  # noqa: S603 — fixed Git/Docker command table, checked SHA, no shell  # noqa: S603 — fixed streaming codec, private checked paths
        [executable, "-e", _IMAGE_CODEC, action, str(source), str(output)],
        input=key_bytes(key),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=300,
        check=False,
        env={"PATH": os.environ.get("PATH", "")},
    )
    require(result.returncode == 0)
    return output


def stage_image(source, key, output):
    size, checksum = _private_image_digest(source, MAX_IMAGE)
    output = _image_crypto("encrypt", source, key, output)
    cipher_size, cipher_sha = _private_image_digest(output, MAX_IMAGE + 45)
    require(cipher_size == size + 45)
    return {
        "schema_version": "qa-image-staging/1.0.0",
        "image_sha256": checksum,
        "image_bytes": size,
        "cipher_sha256": cipher_sha,
        "cipher_bytes": cipher_size,
        "distributable": False,
    }


def restore_image(source, key, output, receipt):
    require(
        set(receipt)
        == {
            "schema_version",
            "image_sha256",
            "image_bytes",
            "cipher_sha256",
            "cipher_bytes",
            "distributable",
        }
    )
    require(
        receipt["schema_version"] == "qa-image-staging/1.0.0" and receipt["distributable"] is False
    )
    size, checksum = _private_image_digest(source, MAX_IMAGE + 45)
    require(size == receipt["cipher_bytes"] and checksum == receipt["cipher_sha256"])
    output = _image_crypto("decrypt", source, key, output)
    actual = _private_image_digest(output, MAX_IMAGE)
    if actual != (receipt["image_bytes"], receipt["image_sha256"]):
        output.unlink()
        raise ValueError("qa_image_restored_checksum_mismatch")
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--custody-config", type=Path)
    args = parser.parse_args()
    try:
        if args.custody_config:
            from tools.qa_delivery.image_transport import ImageStore
            from tools.qa_delivery.proofs import key_bytes

            _private_image_digest(args.custody_config, 65536)
            config = json.loads(args.custody_config.read_text(), object_pairs_hook=_pairs)
            require(set(config) == {"repository", "release_id", "key_file"})
            key_bytes(config["key_file"])
            with httpx.Client(trust_env=False, follow_redirects=False) as client:
                store = ImageStore(
                    config["repository"],
                    config["release_id"],
                    os.environ.get("QA_IMAGE_WRITE_TOKEN", ""),
                    client,
                )
                store.preflight()
                prepare_image(
                    args.checkout,
                    args.output,
                    custody=(
                        store,
                        config["key_file"],
                        args.custody_config.parent / "qa-image-upload-intent.json",
                    ),
                )
            print("QA_IMAGE_PRIVATE_CUSTODY_VERIFIED_NO_DEPLOYMENT")
        else:
            prepare_image(args.checkout, args.output)
            print("QA_IMAGE_METADATA_ONLY_NO_TRANSFER")
    except (ValueError, OSError, subprocess.SubprocessError):
        parser.exit(1, "qa_image_preparation_refused\n")


if __name__ == "__main__":
    main()
