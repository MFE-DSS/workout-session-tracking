"""Squad models: squads, memberships, and invite codes.

Squads allow users to form groups for shared fitness tracking.
Each squad has an owner, members with roles, and invite codes
for joining.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Squad(Base):
    __tablename__ = "squads"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="(CURRENT_TIMESTAMP)",
        nullable=False,
    )

    memberships: Mapped[list["SquadMembership"]] = relationship(
        "SquadMembership",
        back_populates="squad",
        cascade="all, delete-orphan",
    )
    invite_codes: Mapped[list["SquadInviteCode"]] = relationship(
        "SquadInviteCode",
        back_populates="squad",
        cascade="all, delete-orphan",
    )


class SquadMembership(Base):
    __tablename__ = "squad_memberships"

    id: Mapped[int] = mapped_column(primary_key=True)
    squad_id: Mapped[int] = mapped_column(
        ForeignKey("squads.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(16), nullable=False, default="member"
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="(CURRENT_TIMESTAMP)",
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("squad_id", "user_id", name="uq_squad_membership"),
    )

    squad: Mapped["Squad"] = relationship("Squad", back_populates="memberships")


class SquadInviteCode(Base):
    __tablename__ = "squad_invite_codes"

    id: Mapped[int] = mapped_column(primary_key=True)
    squad_id: Mapped[int] = mapped_column(
        ForeignKey("squads.id", ondelete="CASCADE"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(12), unique=True, nullable=False)
    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    used_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    squad: Mapped["Squad"] = relationship("Squad", back_populates="invite_codes")
