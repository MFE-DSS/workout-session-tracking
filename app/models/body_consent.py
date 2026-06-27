"""Sb_Body_01 — granular Body Intelligence consent.

One row per (user, consent_type). The MVP uses a single type,
``body_measurements`` (manual measurement entry & processing). Photo
capture and external-provider consents (``photo_capture`` /
``external_provider``) are modelled-compatible but NOT exercised in this
sprint — see docs/strategy/SPIGNOS_BODY_PRIVACY_AND_CONSENT_SPEC.md.

Consent is explicit, withdrawable, versioned and timestamped. Deleting a
user cascades (ownership), and withdrawing simply flips ``granted`` while
keeping the audit timestamps.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

# MVP consent type. Kept as a module constant so the service and tests
# share one source of truth.
CONSENT_BODY_MEASUREMENTS = "body_measurements"

# Version of the consent wording the user accepted. Bump when the
# consent text/finalité changes so historical grants stay auditable.
CONSENT_TEXT_VERSION = 1


class BodyConsent(Base):
    __tablename__ = "body_consents"
    __table_args__ = (
        UniqueConstraint("user_id", "consent_type", name="uq_body_consent_user_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    consent_type: Mapped[str] = mapped_column(String(64), nullable=False)
    granted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    consent_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    granted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    withdrawn_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
