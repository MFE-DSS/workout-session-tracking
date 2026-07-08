"""Formal BodyZone model — Sb_32.1 foundation.

First relational object of the Sx_32 Muscle/BodyZone refactor. Replaces
(over the next sub-sprints) the hardcoded zone dicts in
``app/services/muscle_mapping.py`` with a DB-backed source of truth.

Sb_32.1 scope: create the table + backfill the 11 current zones from the
existing ``muscle_mapping`` constants. NO consumer is migrated yet
(``classify_exercise`` stays untouched) — invariance is contrainte #1.

Convention alignment with existing models (readiness, body_consents):
int PK + stable unique ``code`` + ``created_at`` server_default.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class BodyZone(Base):
    __tablename__ = "body_zones"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Stable zone identifier (e.g. "pecs") — matches muscle_mapping keys.
    code: Mapped[str] = mapped_column(String(length=64), nullable=False, unique=True)
    # Human label (fr), e.g. "Pectoraux".
    label: Mapped[str] = mapped_column(String(length=128), nullable=False)
    # Body measurement field this zone can be estimated from (e.g. "chest_cm")
    # or NULL when unmeasurable (e.g. lats). Nullable — never invented.
    measurement_field: Mapped[str | None] = mapped_column(
        String(length=64), nullable=True
    )
    # Radar macro-axis this zone aggregates into (e.g. "shoulders").
    radar_axis: Mapped[str | None] = mapped_column(String(length=64), nullable=True)
    # Weekly hard-set volume target (hypertrophy heuristic). Nullable.
    volume_target: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Soft-delete / activation flag (default active).
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="1"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
