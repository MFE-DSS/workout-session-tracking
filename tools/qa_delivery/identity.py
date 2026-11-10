"""Read current transport identity without owners, secrets, paths or approval refs."""

from __future__ import annotations

import json
import re
from contextlib import closing
from pathlib import Path

from tools.qa_delivery.database import SCHEMA, connect_readonly, verify_database

CONTRACT = "first-session-runtime/3.0.0"


def read_version(db_path: Path, *, environment_id: str, source_sha: str, bundle_root: Path) -> dict:
    from app.services.plan_v3.packaging import bundle_manifest, execute_science

    try:
        if not re.fullmatch(r"qa-[a-z0-9_-]{3,60}", environment_id) or not re.fullmatch(
            r"[0-9a-f]{40}", source_sha
        ):
            raise ValueError
        verify_database(db_path)
        with closing(connect_readonly(db_path)) as db:
            row = db.execute(
                "SELECT generation,state,publication_json,packaging_digest FROM first_plan_runtime_authorities WHERE profile_key=?",
                (CONTRACT,),
            ).fetchone()
        if (
            row is None
            or type(row[0]) is not int
            or row[0] < 1
            or row[1] not in {"ACTIVE", "WITHDRAWN", "DISABLED"}
        ):
            raise ValueError
        manifest, digest = bundle_manifest(bundle_root)
        authorities = execute_science("authorities", {}, root=bundle_root, expected_digest=digest)
        if manifest.get("calibration_inventory_version") != "plan-calibration-inventory/2.0.0":
            raise ValueError
        publication = None
        if row[2] is not None:
            raw = json.loads(row[2])
            keys = (
                "registry_digest",
                "binding_digest",
                "bundle_digest",
                "effective_science_digest",
            )
            publication = {key: raw[key] for key in keys}
            if any(
                not isinstance(v, str) or not re.fullmatch("[0-9a-f]{64}", v)
                for v in publication.values()
            ):
                raise ValueError
        if row[1] == "ACTIVE" and (
            publication is None
            or row[3] != digest
            or publication != {key: authorities["v3"][key] for key in publication}
        ):
            raise ValueError
        return {
            "schema_version": "qa-backend/1.0.0",
            "data_scope": "SYNTHETIC_ONLY",
            "environment_id": environment_id,
            "source_sha": source_sha,
            "server_schema": SCHEMA,
            "api_contracts": [CONTRACT],
            "inventory": manifest["calibration_inventory_version"],
            "packaging_digest": digest,
            "authority": {"state": row[1], "generation": row[0], "publication": publication},
        }
    except Exception:
        raise ValueError("qa_identity_unavailable") from None
