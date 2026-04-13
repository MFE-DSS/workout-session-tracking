"""Daily readiness self-assessment.

One entry per user per calendar day. All subjective fields use a
1-5 scale where 5 is always the best state. The unique constraint
on (user_id, recorded_on) is DB-enforced.
"""
from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ReadinessEntry(Base):
    __tablename__ = "readiness_entries"
    __table_args__ = (
        UniqueConstraint("user_id", "recorded_on", name="uq_readiness_user_day"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    recorded_on: Mapped[date] = mapped_column(Date, nullable=False)
    sleep_quality: Mapped[int] = mapped_column(Integer, nullable=False)
    fatigue_level: Mapped[int] = mapped_column(Integer, nullable=False)
    soreness_level: Mapped[int] = mapped_column(Integer, nullable=False)
    stress_level: Mapped[int] = mapped_column(Integer, nullable=False)
    motivation_level: Mapped[int] = mapped_column(Integer, nullable=False)
    resting_hr: Mapped[int | None] = mapped_column(Integer, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
