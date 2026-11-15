"""Fresh owned library admission through the real legacy session services.

No server command receipt/idempotence is invented. An uncertain commit remains
uncertain to the caller; only explicitly rolled-back refusals are definitive.
"""

from __future__ import annotations

from datetime import UTC, datetime

from app.routers.sessions import _poser_adaptations
from app.services.environment_activation import ADAPTABLE, REFUSE, preparer_demarrage
from app.services.library_read_model import (
    VERSION,
    LibraryError,
    _sign,
    _unsigned,
    resolve_library_selection,
)
from app.services.mobile_read_models import execution_read_model, load_owned_session
from app.services.plan_v3.transactions import RuntimeFailure, admit_legacy_start, guard_owner
from app.services.session_builder import instantiate_session


def start_library_session(
    db,
    ctx,
    selection_ref,
    *,
    expected_epoch,
    expected_hash,
    device_id,
    controlled_test_enabled,
    app_env,
):
    if not controlled_test_enabled or app_env != "test":
        raise LibraryError("acquisition_unavailable", 403)
    if expected_epoch != ctx.epoch or not expected_hash:
        raise LibraryError("authentication_changed", 401)
    try:
        guard_owner(
            db,
            ctx.owner_id,
            expected_epoch=expected_epoch,
            expected_hash=expected_hash,
            device_id=device_id,
        )
        template = resolve_library_selection(db, ctx, selection_ref)
        admit_legacy_start(db, ctx.owner_id, reject_any_open=True)
        preparation = preparer_demarrage(db, ctx.owner_id, template)
        if preparation.etat == REFUSE:
            raise LibraryError("start_blocked", 409)
        session = instantiate_session(db, template, datetime.now(UTC), user_id=ctx.owner_id)
        if preparation.etat == ADAPTABLE:
            if _poser_adaptations(session, preparation.plan) != preparation.attendu:
                raise LibraryError("start_blocked", 409)
        session.creation_source = "library"
        db.flush()
        # Serialize before commit: a read-model error must roll back the entire
        # creation, never leave an unusable session hidden behind a refusal.
        execution = execution_read_model(db, load_owned_session(db, session.id, ctx.owner_id))
        value = _unsigned(ctx, selection_ref, "selection")
        result = {
            "contract_version": VERSION,
            "owner_id": ctx.owner_id,
            "source_ref": _sign(ctx, "source", value["source"]),
            "execution_profile": "LEGACY",
            "execution": execution,
        }
        db.commit()
        return result
    except RuntimeFailure as error:
        db.rollback()
        raise LibraryError(error.code, error.status) from None
    except Exception:
        db.rollback()
        # In particular, commit/storage failure is NOT an asserted NOT_CREATED.
        raise
