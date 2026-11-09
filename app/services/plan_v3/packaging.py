"""Hermetic SCI boundary. No module-cache or checkout fallback is permitted."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from app.config import get_settings


class ScienceInputFailure(ValueError):
    """Canonical shape rejected; distinct from unavailable trusted packaging."""


def bundle_manifest(root: Path, expected_digest: str | None = None):
    root = root.resolve(strict=True)
    raw = (root / "packaging-manifest.v1.json").read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if expected_digest is not None and actual != expected_digest:
        raise ValueError("bundle publication mismatch")
    manifest = json.loads(raw)
    if manifest["contract_version"] != "plan-v3-private-science-bundle/1.0.0":
        raise ValueError("unsupported packaging")
    for relative, expected in manifest["sha256"].items():
        path = (root / relative).resolve(strict=True)
        if Path(relative).is_absolute() or not path.is_relative_to(root):
            raise ValueError("invalid bundle path")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("bundle byte mismatch")
    return manifest, actual


def execute_science(
    operation: str, value: dict, *, root: Path | None = None, expected_digest: str | None = None
):
    try:
        path = root or Path(get_settings().plan_v3_bundle_path)
        if root is None and not get_settings().plan_v3_bundle_path:
            raise ValueError("bundle not configured")
        path = path.resolve(strict=True)
        manifest, actual = bundle_manifest(path, expected_digest)
        inventory = manifest.get("calibration_inventory_version")
        if inventory not in (None, "plan-calibration-inventory/2.0.0"):
            raise ValueError("unsupported calibration inventory")
        entry = "science_worker_v2.py" if inventory else "science_worker.py"
        worker = path / "app/services/plan_v3" / entry
        relative = str(worker.relative_to(path))
        if relative not in manifest["sha256"]:
            raise ValueError("worker not attested")
        request = json.dumps({"operation": operation, "value": value}, allow_nan=False)
        completed = subprocess.run(  # noqa: S603 — attested worker, fixed interpreter, no shell
            [sys.executable, "-I", str(worker), str(path), actual],
            input=request,
            text=True,
            capture_output=True,
            check=False,
            cwd=path,
            timeout=20,
        )
        if completed.returncode != 0:
            raise ValueError("isolated science failure")
        response = json.loads(completed.stdout)
        if response.get("error") == "invalid_scientific_input":
            raise ScienceInputFailure("invalid_scientific_input")
        if response.get("error"):
            raise ValueError(response["error"])
        return response["result"]
    except ScienceInputFailure:
        raise
    except (OSError, ValueError, KeyError, subprocess.SubprocessError):
        # Never expose request observations, private paths or worker stderr.
        raise ValueError("science_bundle_unavailable") from None
