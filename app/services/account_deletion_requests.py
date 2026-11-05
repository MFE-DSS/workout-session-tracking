"""Proposed durable workflow, NOT_SERVED. No startup import, route, migration or purge.

The caller owns the transaction. This metadata describes a future additive migration;
only isolated fixtures create it today. Production has no admitted policy or verifier.
App Bearer and web session/CSRF adapters must share this service after their own review.
"""

from __future__ import annotations

import hashlib
import hmac
import re
import secrets
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    MetaData,
    String,
    Table,
    UniqueConstraint,
    select,
    update,
)
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.account_lifecycle import AccountRejected, reauthenticate_account

workflow_metadata = MetaData()
requests = Table(
    "account_deletion_requests_v1",
    workflow_metadata,
    Column("id", Integer, primary_key=True),
    Column("owner_id", Integer, nullable=False),
    Column("request_id", String(128), nullable=False),
    Column("active_owner", Integer, unique=True),
    Column("state", String(24), nullable=False),
    Column("policy_ref", String(200), nullable=False),
    Column("scope_ref", String(200), nullable=False),
    Column("version", Integer, nullable=False),
    Column("created_at", DateTime, nullable=False),
    Column("updated_at", DateTime, nullable=False),
    Column("confirmed_at", DateTime),
    Column("reason", String(40)),
    Column("capability_hash", String(64)),
    Column("capability_expires_at", DateTime),
    Column("proof_ref", String(200)),
    UniqueConstraint("owner_id", "request_id"),
)
# No FK to users: an approved receipt policy must explicitly define the residual
# owner link after erasure. Nothing here creates it on a deployed database.


class PolicyRequired(ValueError):
    pass


class RequestRejected(ValueError):
    pass


class StatusDenied(ValueError):
    pass


@dataclass(frozen=True)
class Policy:
    ref: str
    scope_ref: str
    retention_ref: str
    controller_ref: str
    capability_lifetime: timedelta
    mechanism: str
    admitted: bool = False


def _instant(now: datetime) -> datetime:
    if now.tzinfo is None or now.utcoffset() is None:
        raise RequestRejected("explicit_timestamp_required")
    return now.astimezone(UTC).replace(tzinfo=None)


def _receipt(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "contract_version": "account-deletion/1.0.0",
        "owner_id": row["owner_id"],
        "request_id": row["request_id"],
        "state": {"CONFIRMED": "DELETED", "IN_PROGRESS": "PENDING"}.get(row["state"], row["state"]),
        "policy_ref": row["policy_ref"],
        "confirmed_at": row["confirmed_at"].replace(tzinfo=UTC).isoformat()
        if row["confirmed_at"]
        else None,
        "revocation": "CONFIRMED" if row["state"] == "CONFIRMED" else "UNKNOWN",
        "data_erasure": "CONFIRMED" if row["state"] == "CONFIRMED" else "UNKNOWN",
        "restore_protection": "CONFIRMED" if row["state"] == "CONFIRMED" else "UNKNOWN",
    }


class DeletionRequestService:
    """Policy/verifier supplied only by trusted server composition, never request JSON.

    No irreversible-start operation is implemented. A reviewed future executor owns
    write exclusion/revocation/erasure, and only its verified proof can confirm.
    """

    def __init__(
        self,
        policies: Mapping[str, Policy] | None = None,
        *,
        verifier: Callable[[Any], bool] | None = None,
    ):
        self._policies = dict(policies or {})
        self._verifier = verifier

    def _policy(self, ref: str) -> Policy:
        policy = self._policies.get(ref)
        if (
            not policy
            or not policy.admitted
            or not all((policy.ref, policy.scope_ref, policy.retention_ref, policy.controller_ref))
        ):
            raise PolicyRequired("controller_policy_required")
        if policy.mechanism not in {
            "MANUAL",
            "AUTOMATED",
        } or policy.capability_lifetime <= timedelta(0):
            raise PolicyRequired("controller_policy_required")
        return policy

    @staticmethod
    def _owner(db: Session, user: User) -> None:
        if type(user.id) is not int or user.id <= 0:
            raise StatusDenied("status_unavailable")
        epoch, hashed = user.session_epoch or 0, user.password_hash
        row = db.execute(
            select(User.is_active, User.session_epoch, User.password_hash).where(User.id == user.id)
        ).one_or_none()
        if (
            not row
            or not row.is_active
            or (row.session_epoch or 0) != epoch
            or not hmac.compare_digest(row.password_hash, hashed)
        ):
            raise StatusDenied("status_unavailable")

    @staticmethod
    def _reauth_lock(db: Session, user: User, password: str) -> None:
        current = reauthenticate_account(db, user, current_password=password)
        # Atomic identity guard + row lock, including SQLite where FOR UPDATE is ignored.
        # No epoch increment or credential revocation takes place.
        epoch, hashed = current.session_epoch or 0, current.password_hash
        locked = db.execute(
            update(User)
            .where(
                User.id == current.id,
                User.is_active.is_(True),
                User.session_epoch == epoch,
                User.password_hash == hashed,
            )
            .values(session_epoch=epoch),
            execution_options={"synchronize_session": False},
        )
        if locked.rowcount != 1:
            raise AccountRejected("reauthentication_required", "Réauthentification nécessaire.")

    @staticmethod
    def _row(db: Session, owner: int, key: str) -> Mapping[str, Any]:
        row = (
            db.execute(
                select(requests).where(requests.c.owner_id == owner, requests.c.request_id == key)
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            raise StatusDenied("status_unavailable")
        return row

    @staticmethod
    def _change(db: Session, row: Mapping[str, Any], **values: Any) -> None:
        changed = db.execute(
            update(requests)
            .where(requests.c.id == row["id"], requests.c.version == row["version"])
            .values(**values, version=row["version"] + 1)
        )
        if changed.rowcount != 1:
            raise RequestRejected("concurrent_transition")

    def request(
        self,
        db: Session,
        user: User,
        *,
        request_id: str,
        current_password: str,
        policy_ref: str,
        now: datetime,
    ) -> dict[str, Any]:
        policy, at = self._policy(policy_ref), _instant(now)
        if not isinstance(request_id, str) or not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9._:-]{7,127}", request_id
        ):
            raise RequestRejected("invalid_request_id")
        self._reauth_lock(db, user, current_password)
        prior = (
            db.execute(
                select(requests).where(
                    requests.c.owner_id == user.id, requests.c.request_id == request_id
                )
            )
            .mappings()
            .one_or_none()
        )
        if prior is not None:
            if prior["state"] not in {"PENDING", "REJECTED"}:
                raise RequestRejected("status_capability_required")
            if prior["policy_ref"] != policy.ref:
                raise RequestRejected("idempotency_conflict")
            return _receipt(prior)
        active = (
            db.execute(select(requests).where(requests.c.active_owner == user.id))
            .mappings()
            .one_or_none()
        )
        if active is not None:
            if active["state"] != "PENDING":
                raise RequestRejected("status_capability_required")
            return _receipt(active)
        db.execute(
            requests.insert().values(
                owner_id=user.id,
                request_id=request_id,
                active_owner=user.id,
                state="PENDING",
                policy_ref=policy.ref,
                scope_ref=policy.scope_ref,
                version=1,
                created_at=at,
                updated_at=at,
            )
        )
        return _receipt(self._row(db, user.id, request_id))

    def read(self, db: Session, user: User, request_id: str) -> dict[str, Any]:
        self._owner(db, user)
        row = self._row(db, user.id, request_id)
        if row["state"] not in {"PENDING", "REJECTED"}:
            raise StatusDenied("status_unavailable")
        return _receipt(row)

    def issue_status_capability(
        self, db: Session, user: User, request_id: str, *, current_password: str, now: datetime
    ) -> str:
        at = _instant(now)
        self._reauth_lock(db, user, current_password)
        row = self._row(db, user.id, request_id)
        if row["state"] not in {"PENDING", "REJECTED"}:
            raise StatusDenied("status_unavailable")
        policy = self._policy(row["policy_ref"])
        token = secrets.token_urlsafe(32)
        self._change(
            db,
            row,
            capability_hash=hashlib.sha256(token.encode()).hexdigest(),
            capability_expires_at=at + policy.capability_lifetime,
            updated_at=at,
        )
        return token  # Future adapter: private response only, never URL/log/receipt/outbox.

    def read_status_capability(
        self, db: Session, owner_id: int, request_id: str, capability: str, *, now: datetime
    ) -> dict[str, Any]:
        at = _instant(now)
        row = self._row(db, owner_id, request_id)
        if not isinstance(capability, str) or len(capability) > 128:
            raise StatusDenied("status_unavailable")
        if (
            not row["capability_hash"]
            or not row["capability_expires_at"]
            or at >= row["capability_expires_at"]
        ):
            raise StatusDenied("status_unavailable")
        if not hmac.compare_digest(
            row["capability_hash"], hashlib.sha256(capability.encode()).hexdigest()
        ):
            raise StatusDenied("status_unavailable")
        self._policy(row["policy_ref"])
        return _receipt(row)

    def reject(
        self, db: Session, owner_id: int, request_id: str, *, reason: str, now: datetime
    ) -> dict[str, Any]:
        row, at = self._row(db, owner_id, request_id), _instant(now)
        self._policy(row["policy_ref"])
        if reason != "OPERATOR_REJECTED" or row["state"] not in {"PENDING", "REJECTED"}:
            raise RequestRejected("invalid_transition")
        if row["state"] == "PENDING":
            self._change(db, row, state="REJECTED", active_owner=None, reason=reason, updated_at=at)
        return _receipt(self._row(db, owner_id, request_id))

    def confirm(
        self, db: Session, owner_id: int, request_id: str, *, proof: Any, now: datetime
    ) -> dict[str, Any]:
        row, at = self._row(db, owner_id, request_id), _instant(now)
        policy = self._policy(row["policy_ref"])
        expected = {
            "owner_id": owner_id,
            "request_id": request_id,
            "policy_ref": policy.ref,
            "scope_ref": row["scope_ref"],
            "revocation": "CONFIRMED",
            "data_erasure": "CONFIRMED",
            "restore_protection": "CONFIRMED",
        }
        if (
            row["state"] not in {"IN_PROGRESS", "CONFIRMED"}
            or not isinstance(proof, dict)
            or any(proof.get(key) != value for key, value in expected.items())
            or not isinstance(proof.get("proof_ref"), str)
            or not 0 < len(proof["proof_ref"]) <= 200
            or self._verifier is None
            or not self._verifier(proof)
        ):
            raise RequestRejected("authoritative_proof_required")
        if row["state"] != "CONFIRMED":
            self._change(
                db,
                row,
                state="CONFIRMED",
                active_owner=None,
                proof_ref=proof["proof_ref"],
                confirmed_at=at,
                updated_at=at,
            )
        return _receipt(self._row(db, owner_id, request_id))
