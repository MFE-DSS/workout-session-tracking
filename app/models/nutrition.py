"""NUT-01 canonical revisions. Not registered for application startup DDL."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class _Revision:
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    parent_ref: Mapped[int | None] = mapped_column(Integer)
    kcal_milli: Mapped[int | None] = mapped_column(Integer)
    protein_milli: Mapped[int | None] = mapped_column(Integer)
    carbohydrate_milli: Mapped[int | None] = mapped_column(Integer)
    fat_milli: Mapped[int | None] = mapped_column(Integer)
    provenance: Mapped[dict] = mapped_column(JSON(none_as_null=True), nullable=False)
    request_id: Mapped[str] = mapped_column(String(64), nullable=False)
    command_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    receipt: Mapped[dict] = mapped_column(JSON(none_as_null=True), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


_KNOWN = "(kcal_milli IS NOT NULL OR protein_milli IS NOT NULL OR carbohydrate_milli IS NOT NULL OR fat_milli IS NOT NULL)"
_EMPTY = "(kcal_milli IS NULL AND protein_milli IS NULL AND carbohydrate_milli IS NULL AND fat_milli IS NULL)"


def _constraints(table: str, prefix: str) -> tuple:
    return (
        UniqueConstraint("user_id", "id", name=f"uq_{prefix}_owner_id"),
        UniqueConstraint("user_id", "request_id", name=f"uq_{prefix}_request"),
        UniqueConstraint("user_id", "parent_ref", name=f"uq_{prefix}_successor"),
        ForeignKeyConstraint(
            ["user_id", "parent_ref"], [f"{table}.user_id", f"{table}.id"],
            ondelete="NO ACTION", deferrable=True, initially="DEFERRED",
            name=f"fk_{prefix}_parent",
        ),
        CheckConstraint(
            "typeof(revision) = 'integer' AND revision BETWEEN 1 AND 9007199254740991 "
            "AND ((revision = 1 AND parent_ref IS NULL) OR "
            "(revision > 1 AND parent_ref IS NOT NULL AND parent_ref > 0))",
            name=f"ck_{prefix}_revision",
        ),
        CheckConstraint("length(request_id) BETWEEN 1 AND 64", name=f"ck_{prefix}_request"),
        CheckConstraint(
            "length(command_digest) = 64 AND command_digest NOT GLOB '*[^0-9a-f]*'",
            name=f"ck_{prefix}_digest",
        ),
        CheckConstraint(
            "json_type(receipt) = 'object' AND json_type(provenance) = 'object'",
            name=f"ck_{prefix}_objects",
        ),
        *(CheckConstraint(
            f"{field} IS NULL OR (typeof({field}) = 'integer' AND {field} BETWEEN 0 AND 999999999)",
            name=f"ck_{prefix}_{field}",
        ) for field in ("kcal_milli", "protein_milli", "carbohydrate_milli", "fat_milli")),
    )


class NutritionTargetRevision(_Revision, Base):
    __tablename__ = "nutrition_target_revisions_v1"
    __table_args__ = (
        *_constraints(__tablename__, "nutrition_target"),
        UniqueConstraint("user_id", "variant", "effective_from", "revision",
                         name="uq_nutrition_target_revision"),
        CheckConstraint("variant IN ('STANDARD','TRAINING','REST')", name="ck_nutrition_target_variant"),
        CheckConstraint("length(effective_from) = 10", name="ck_nutrition_target_date"),
        CheckConstraint(
            f"(enabled = 1 AND {_KNOWN}) OR (enabled = 0 AND {_EMPTY})",
            name="ck_nutrition_target_state",
        ),
        Index("ix_nutrition_target_key", "user_id", "variant", "effective_from", "revision"),
        {"info": {"nutrition_manual": True}, "sqlite_autoincrement": True},
    )
    variant: Mapped[str] = mapped_column(String(8), nullable=False)
    effective_from: Mapped[str] = mapped_column(String(10), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean(create_constraint=True), nullable=False)


class NutritionDayRevision(_Revision, Base):
    __tablename__ = "nutrition_day_revisions_v1"
    __table_args__ = (
        *_constraints(__tablename__, "nutrition_day"),
        UniqueConstraint("user_id", "local_day", "revision", name="uq_nutrition_day_revision"),
        ForeignKeyConstraint(
            ["user_id", "target_ref"],
            ["nutrition_target_revisions_v1.user_id", "nutrition_target_revisions_v1.id"],
            ondelete="NO ACTION", deferrable=True, initially="DEFERRED",
            name="fk_nutrition_day_owned_target",
        ),
        CheckConstraint("length(local_day) = 10 AND length(timezone) BETWEEN 1 AND 128",
                        name="ck_nutrition_day_date"),
        CheckConstraint(
            f"(state = 'ACTIVE' AND {_KNOWN}) OR "
            f"(state = 'WITHDRAWN' AND {_EMPTY} AND target_ref IS NULL AND declared_complete = 0)",
            name="ck_nutrition_day_state",
        ),
        Index("ix_nutrition_day_key", "user_id", "local_day", "revision"),
        {"info": {"nutrition_manual": True}, "sqlite_autoincrement": True},
    )
    local_day: Mapped[str] = mapped_column(String(10), nullable=False)
    timezone: Mapped[str] = mapped_column(String(128), nullable=False)
    state: Mapped[str] = mapped_column(String(9), nullable=False)
    declared_complete: Mapped[bool] = mapped_column(Boolean(create_constraint=True), nullable=False)
    target_ref: Mapped[int | None] = mapped_column(Integer)
