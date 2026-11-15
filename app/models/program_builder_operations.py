"""Owner-scoped immutable technical receipts. No prescription tree is stored."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ProgramBuilderOperation(Base):
    __tablename__ = "program_builder_operations_v1"
    __table_args__ = (
        UniqueConstraint("user_id", "command_id", name="uq_program_builder_owner_command"),
        Index("ix_program_builder_owner_program", "user_id", "program_id", "id"),
        {"info": {"program_builder": True}},
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    command_id: Mapped[str] = mapped_column(String(128), nullable=False)
    operation: Mapped[str] = mapped_column(String(24), nullable=False)
    request_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    program_id: Mapped[int | None] = mapped_column(
        ForeignKey("user_programs.id", ondelete="SET NULL")
    )
    source_digest_before: Mapped[str | None] = mapped_column(String(64))
    source_digest_after: Mapped[str] = mapped_column(String(64), nullable=False)
    result_version: Mapped[int] = mapped_column(Integer, nullable=False)
    result_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
