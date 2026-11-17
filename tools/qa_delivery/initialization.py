"""Explicit new synthetic state only; never called by startup or publication.

Run as QA UID against the newly approved volume. Inputs already exist privately.
No secret creation, imported database, consent grant or fabricated performed fact.
Failure preserves the partial state for inspection and refuses automatic retry.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
from pathlib import Path


def require(ok):
    if not ok:
        raise ValueError("qa_initialization_refused")


def initialize(config_path):
    from tools.qa_delivery.server import (
        _closed_pairs,
        _private_feature_text,
        _safe_environment,
        _source_sha,
    )

    _safe_environment()
    config = json.loads(_private_feature_text(config_path), object_pairs_hook=_closed_pairs)
    require(
        set(config)
        == {
            "schema_version",
            "source_sha",
            "environment_id",
            "approval_ref",
            "accounts_file",
            "auth_secret_file",
            "data_dir",
            "bundle_root",
            "science_mode",
        }
    )
    require(
        config["schema_version"] == "qa-initialization/1.0.0"
        and config["source_sha"] == _source_sha()
    )
    require(
        isinstance(config["environment_id"], str)
        and re.fullmatch(r"qa-rel03-[a-z0-9_-]{3,48}", config["environment_id"])
    )
    require(isinstance(config["approval_ref"], str) and 1 <= len(config["approval_ref"]) <= 256)
    require(config["science_mode"] in {"DISABLED", "ACTIVE_PUBLISHED"})
    accounts = json.loads(
        _private_feature_text(config["accounts_file"]), object_pairs_hook=_closed_pairs
    )
    require(isinstance(accounts, list) and len(accounts) == 2)
    names = set()
    for account in accounts:
        require(set(account) == {"username", "password"})
        require(
            isinstance(account["username"], str)
            and re.fullmatch(r"qa02-rel03-[a-z0-9_-]{3,48}", account["username"])
        )
        require(account["username"] not in names and isinstance(account["password"], str))
        names.add(account["username"])
    secret = _private_feature_text(config["auth_secret_file"]).strip()
    require(len(secret) >= 32 and "\n" not in secret)
    data = Path(config["data_dir"])
    require(data.is_absolute() and not any(p.is_symlink() for p in (data, *data.parents)))
    info = data.stat()
    require(
        stat.S_ISDIR(info.st_mode)
        and stat.S_IMODE(info.st_mode) == 0o700
        and info.st_uid == os.getuid()
    )
    state = data / "state"
    require(not state.exists() and not state.is_symlink())
    bundle = Path(config["bundle_root"])
    require(bundle.is_absolute())
    from app.services.plan_v3.packaging import bundle_manifest, execute_science

    _, packaging = bundle_manifest(bundle)
    authority = execute_science("authorities", {}, root=bundle, expected_digest=packaging)
    # Selecting already published pins is operational activation, not SCI admission.
    pins = {
        key: authority["v3"][key]
        for key in (
            "registry_digest",
            "binding_digest",
            "bundle_digest",
            "effective_science_digest",
        )
    }
    state.mkdir(mode=0o700)  # Exclusive: never overwrite an existing or failed run.
    database = state / "qa.db"
    os.environ.update(APP_ENV="test", APP_SECRET_KEY=secret, DATABASE_URL=f"sqlite:///{database}")
    from app.config import get_settings

    get_settings.cache_clear()
    from alembic import command
    from alembic.config import Config
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    from app.models.first_plan_runtime import FirstPlanRuntimeAuthority
    from app.services.account_lifecycle import register_account
    from app.services.device_auth import open_device_session
    from tools.qa_delivery.database import ROOT, SCHEMA, verify_database
    from tools.qa_delivery.ownership import anchor_digest, capture_anchor

    migration = Config()
    migration.set_main_option("script_location", str(ROOT / "migrations"))
    migration.set_main_option("sqlalchemy.url", f"sqlite:///{database}")
    command.upgrade(migration, SCHEMA)
    database.chmod(0o600)
    engine = create_engine(f"sqlite:///{database}")
    active = config["science_mode"] == "ACTIVE_PUBLISHED"
    try:
        from app.services.mobile_program_builder import picker
        from app.services.seed import seed_method_rules, seed_reference_split
        from app.services.seed_exercise_identity import seed_exercise_identity

        # Reference seeds only on this new DB. Lifespan stays disabled and no
        # existing history or programme is imported, rewritten or fabricated.
        with Session(engine) as db:
            seed_reference_split(db)
            seed_method_rules(db)
            seed_exercise_identity(db)
            db.commit()
            options = len(picker(db))
            require(options > 0)
        with Session(engine) as db, db.begin():
            for account in accounts:
                user = register_account(
                    db,
                    username=account["username"],
                    password=account["password"],
                    password_confirm=account["password"],
                    email="",
                )
                open_device_session(db, user, device_label="synthetic-qa-initialization")
            db.add(
                FirstPlanRuntimeAuthority(
                    profile_key="first-session-runtime/3.0.0",
                    generation=1,
                    state="ACTIVE" if active else "DISABLED",
                    publication_json=json.dumps(pins) if active else None,
                    packaging_digest=packaging if active else None,
                    approval_ref=config["approval_ref"] if active else None,
                )
            )
    finally:
        engine.dispose()
    verify_database(database)
    anchor = capture_anchor(database, config["environment_id"])
    anchor_path = state / "ownership-anchor.json"
    fd = os.open(anchor_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as out:
        json.dump(anchor, out, sort_keys=True)
        out.flush()
        os.fsync(out.fileno())
    return {
        "environment_id": config["environment_id"],
        "source_sha": config["source_sha"],
        "schema": SCHEMA,
        "accounts": 2,
        "canonical_exercise_options": options,
        "authority_generation": 1,
        "science_state": "ACTIVE" if active else "DISABLED",
        "packaging_digest": packaging,
        "ownership_anchor_sha256": anchor_digest(anchor),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(initialize(args.config), sort_keys=True))
    except Exception:
        parser.exit(1, "qa_initialization_refused_partial_state_must_be_inspected\n")


if __name__ == "__main__":
    main()
