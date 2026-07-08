"""Formal Muscle model — Sb_32.1 foundation.

Prepares fine-grained muscle granularity for the Sx_32 refactor. Per
OQ-32-B, V1 keeps the analytical layer at the BodyZone level; this table
is created but intentionally peuplée au minimum (empty V1 acceptable) —
NO fine anatomy is invented (OQ-32-F). It will be populated from explicit
sources in later sub-sprints.

Convention alignment: int PK + stable unique ``code`` + FK to body_zones
via ``body_zone_code`` (natural code, robust to reseeds) + ``created_at``.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Muscle(Base):
    __tablename__ = "muscles"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Stable muscle identifier (e.g. "pectoralis_major").
    code: Mapped[str] = mapped_column(String(length=64), nullable=False, unique=True)
    # Human name (fr), e.g. "Grand pectoral".
    name: Mapped[str] = mapped_column(String(length=128), nullable=False)
    # Owning body zone (natural code FK, aligned with snapshot-robust identity).
    body_zone_code: Mapped[str | None] = mapped_column(
        String(length=64),
        ForeignKey("body_zones.code", ondelete="SET NULL"),
        nullable=True,
    )
    # Category (upper | lower | core) — nullable until populated.
    category: Mapped[str | None] = mapped_column(String(length=32), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="1"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
