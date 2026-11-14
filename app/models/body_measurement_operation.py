"""BODY-01 metadata only. Numeric observations remain in BodyMeasurement."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class BodyMeasurementOperation(Base):
    __tablename__ = "body_measurement_operations_v1"
    __table_args__ = (
        UniqueConstraint("owner_id", "request_id", name="uq_body_operation_request"),
        UniqueConstraint(
            "owner_id", "root_ref", "applied_revision", name="uq_body_operation_revision"
        ),
        CheckConstraint("operation IN ('CREATE','CORRECT','ERASE')", name="ck_body_operation_kind"),
        CheckConstraint(
            "applied_revision > 0 AND root_ref > 0 AND measurement_ref > 0",
            name="ck_body_operation_positive",
        ),
        CheckConstraint(
            "(operation = 'CORRECT' AND parent_ref IS NOT NULL) OR (operation != 'CORRECT' AND parent_ref IS NULL)",
            name="ck_body_operation_parent",
        ),
        Index("ix_body_operation_root", "owner_id", "root_ref"),
        Index(
            "uq_body_correction_parent",
            "owner_id",
            "parent_ref",
            unique=True,
            sqlite_where=text("operation = 'CORRECT'"),
        ),
        {"info": {"body_01": True}},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    request_id: Mapped[str] = mapped_column(String(64), nullable=False)
    command_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    operation: Mapped[str] = mapped_column(String(8), nullable=False)
    root_ref: Mapped[int] = mapped_column(Integer, nullable=False)
    parent_ref: Mapped[int | None] = mapped_column(Integer)
    measurement_ref: Mapped[int] = mapped_column(Integer, nullable=False)
    applied_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    changed_fields: Mapped[list] = mapped_column(JSON, nullable=False)
    provenance_by_changed_field: Mapped[dict] = mapped_column(JSON, nullable=False)
    date_provenance: Mapped[dict | None] = mapped_column(JSON)
    before_fingerprint: Mapped[str | None] = mapped_column(String(64))
    after_fingerprint: Mapped[str | None] = mapped_column(String(64))
    receipt: Mapped[dict] = mapped_column(JSON, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
