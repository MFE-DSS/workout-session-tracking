"""Body measurement time-series tracking.

Each row is one measurement session — the user fills in whichever
fields they measured that day. All measurement fields are nullable
to allow partial entries.

Lateralized fields (arm, thigh) store left/right independently.
The averaged values used by the physique dashboard are derived views,
not stored columns.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class BodyMeasurement(Base):
    __tablename__ = "body_measurements"
    __table_args__ = (
        Index("ix_body_measurements_user_date", "user_id", "measured_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    measured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    chest_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    arm_cm_left: Mapped[float | None] = mapped_column(Float, nullable=True)
    arm_cm_right: Mapped[float | None] = mapped_column(Float, nullable=True)
    waist_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    thigh_cm_left: Mapped[float | None] = mapped_column(Float, nullable=True)
    thigh_cm_right: Mapped[float | None] = mapped_column(Float, nullable=True)
    hip_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    neck_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    calf_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
