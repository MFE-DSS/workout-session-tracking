"""Owned PLAN workflow. DDL is applied by Alembic, never application startup.

Immutable evidence rows have no cascading user deletion. DATA must explicitly
handle their lifecycle before a real-person activation is possible.
"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy import (
    event as _event,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.session import SessionExercise, SetLog, WorkoutSession

PLAN_TABLE_NAMES = (
    "blueprint_source_events",
    "owned_blueprint_snapshots",
    "first_plan_evaluations",
    "first_session_requests",
    "first_plan_execution_bindings",
    "first_plan_set_observations",
    "first_plan_runtime_authorities",
)
PLAN_INDEX_NAMES = ("uq_plan_v3_ws_owner", "uq_plan_v3_se_session", "uq_plan_v3_set_exercise")

# Registration lives here: the historically pinned session model is immutable.
for name, table, columns in (
    (PLAN_INDEX_NAMES[0], WorkoutSession.__table__, ("id", "user_id")),
    (PLAN_INDEX_NAMES[1], SessionExercise.__table__, ("id", "session_id")),
    (PLAN_INDEX_NAMES[2], SetLog.__table__, ("id", "session_exercise_id")),
):
    Index(name, *(table.c[c] for c in columns), unique=True, info={"plan_v3": True})


class BlueprintSourceEvent(Base):
    __tablename__ = PLAN_TABLE_NAMES[0]
    __table_args__ = (
        UniqueConstraint("owner_id", "source_revision", name="uq_blueprint_source_revision"),
        UniqueConstraint("owner_id", "request_id", name="uq_blueprint_source_request"),
        CheckConstraint("source_revision > 0", name="ck_blueprint_positive_revision"),
        {"info": {"plan_v3": True}},
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    source_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    request_id: Mapped[str] = mapped_column(String(64), nullable=False)
    body_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )


class OwnedBlueprintSnapshot(Base):
    __tablename__ = PLAN_TABLE_NAMES[1]
    __table_args__ = (
        UniqueConstraint("owner_id", "id", name="uq_blueprint_snapshot_owner"),
        UniqueConstraint("owner_id", "request_id", name="uq_blueprint_snapshot_request"),
        CheckConstraint("source_revision >= 0", name="ck_snapshot_revision"),
        {"info": {"plan_v3": True}},
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    request_id: Mapped[str] = mapped_column(String(64), nullable=False)
    body_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    source_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    as_of: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    snapshot_json: Mapped[str] = mapped_column(Text, nullable=False)
    snapshot_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )


class FirstPlanEvaluation(Base):
    __tablename__ = PLAN_TABLE_NAMES[2]
    __table_args__ = (
        UniqueConstraint("owner_id", "id", name="uq_first_plan_evaluation_owner"),
        UniqueConstraint(
            "owner_id", "operation_kind", "request_id", name="uq_first_plan_evaluation_request"
        ),
        ForeignKeyConstraint(
            ["owner_id", "snapshot_id"],
            ["owned_blueprint_snapshots.owner_id", "owned_blueprint_snapshots.id"],
            name="fk_evaluation_snapshot_owner",
        ),
        ForeignKeyConstraint(
            ["owner_id", "parent_evaluation_id"],
            ["first_plan_evaluations.owner_id", "first_plan_evaluations.id"],
            name="fk_evaluation_parent_owner",
        ),
        CheckConstraint(
            "(operation_kind = 'EVALUATE' AND parent_evaluation_id IS NULL) OR (operation_kind = 'TIME_ACK' AND parent_evaluation_id IS NOT NULL)",
            name="ck_evaluation_kind",
        ),
        CheckConstraint(
            "source_revision >= 0 AND authority_generation > 0", name="ck_evaluation_generation"
        ),
        Index("ix_first_plan_evaluation_snapshot", "owner_id", "snapshot_id", "created_at"),
        {"info": {"plan_v3": True}},
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    snapshot_id: Mapped[str] = mapped_column(String(36), nullable=False)
    parent_evaluation_id: Mapped[str | None] = mapped_column(String(36))
    operation_kind: Mapped[str] = mapped_column(String(16), nullable=False)
    request_id: Mapped[str] = mapped_column(String(64), nullable=False)
    body_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    source_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    authority_generation: Mapped[int] = mapped_column(Integer, nullable=False)
    request_json: Mapped[str] = mapped_column(Text, nullable=False)
    result_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )


class FirstSessionRequest(Base):
    __tablename__ = PLAN_TABLE_NAMES[3]
    __table_args__ = (
        UniqueConstraint("owner_id", "request_id", name="uq_first_session_request"),
        UniqueConstraint("session_id", name="uq_first_session_request_session"),
        ForeignKeyConstraint(
            ["owner_id", "evaluation_id"],
            ["first_plan_evaluations.owner_id", "first_plan_evaluations.id"],
            name="fk_first_request_evaluation_owner",
        ),
        ForeignKeyConstraint(
            ["session_id", "owner_id"],
            ["workout_sessions.id", "workout_sessions.user_id"],
            name="fk_first_request_session_owner",
        ),
        CheckConstraint(
            "(state = 'CREATED' AND session_id IS NOT NULL AND evaluation_id IS NOT NULL AND scientific_session_id IS NOT NULL) OR (state IN ('DENIED', 'CANCELLED') AND session_id IS NULL)",
            name="ck_first_session_terminal",
        ),
        Index(
            "uq_first_created_handoff_owner",
            "owner_id",
            unique=True,
            sqlite_where=text("state = 'CREATED'"),
            postgresql_where=text("state = 'CREATED'"),
        ),
        {"info": {"plan_v3": True}},
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: uuid4().hex)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    request_id: Mapped[str] = mapped_column(String(64), nullable=False)
    body_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    body_json: Mapped[str] = mapped_column(Text, nullable=False)
    evaluation_id: Mapped[str | None] = mapped_column(String(36))
    state: Mapped[str] = mapped_column(String(16), nullable=False)
    session_id: Mapped[int | None] = mapped_column(Integer)
    scientific_session_id: Mapped[str | None] = mapped_column(String(128))
    terminal_code: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )


class FirstPlanExecutionBinding(Base):
    __tablename__ = PLAN_TABLE_NAMES[4]
    __table_args__ = (
        UniqueConstraint("session_id", "owner_id", name="uq_first_binding_session_owner"),
        ForeignKeyConstraint(
            ["session_id", "owner_id"],
            ["workout_sessions.id", "workout_sessions.user_id"],
            name="fk_first_binding_session_owner",
        ),
        ForeignKeyConstraint(
            ["owner_id", "evaluation_id"],
            ["first_plan_evaluations.owner_id", "first_plan_evaluations.id"],
            name="fk_first_binding_evaluation_owner",
        ),
        {"info": {"plan_v3": True}},
    )
    session_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    evaluation_id: Mapped[str] = mapped_column(String(36), nullable=False)
    execution_profile_version: Mapped[str] = mapped_column(String(64), nullable=False)
    scientific_session_id: Mapped[str] = mapped_column(String(128), nullable=False)
    immutable_payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    binding_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )


class FirstPlanSetObservation(Base):
    __tablename__ = PLAN_TABLE_NAMES[5]
    __table_args__ = (
        UniqueConstraint("owner_id", "op_id", name="uq_first_plan_set_operation"),
        UniqueConstraint("set_id", "applied_revision", name="uq_first_plan_set_revision"),
        ForeignKeyConstraint(
            ["session_id", "owner_id"],
            ["first_plan_execution_bindings.session_id", "first_plan_execution_bindings.owner_id"],
            name="fk_plan_set_binding_owner",
        ),
        ForeignKeyConstraint(
            ["session_exercise_id", "session_id"],
            ["session_exercises.id", "session_exercises.session_id"],
            name="fk_plan_set_exercise_session",
        ),
        ForeignKeyConstraint(
            ["set_id", "session_exercise_id"],
            ["set_logs.id", "set_logs.session_exercise_id"],
            name="fk_plan_set_log_exercise",
        ),
        CheckConstraint(
            "expected_revision >= 0 AND applied_revision = expected_revision + 1",
            name="ck_plan_set_revision",
        ),
        {"info": {"plan_v3": True}},
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    session_id: Mapped[int] = mapped_column(Integer, nullable=False)
    session_exercise_id: Mapped[int] = mapped_column(Integer, nullable=False)
    set_id: Mapped[int] = mapped_column(Integer, nullable=False)
    op_id: Mapped[str] = mapped_column(String(64), nullable=False)
    body_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    expected_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    applied_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    observation_json: Mapped[str] = mapped_column(Text, nullable=False)
    receipt_json: Mapped[str] = mapped_column(Text, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )


class FirstPlanRuntimeAuthority(Base):
    __tablename__ = PLAN_TABLE_NAMES[6]
    __table_args__ = (
        CheckConstraint("generation > 0", name="ck_plan_authority_generation"),
        CheckConstraint(
            "state IN ('DISABLED', 'ACTIVE', 'WITHDRAWN')", name="ck_plan_authority_state"
        ),
        CheckConstraint(
            "state != 'ACTIVE' OR (publication_json IS NOT NULL AND packaging_digest IS NOT NULL AND approval_ref IS NOT NULL)",
            name="ck_plan_active_publication",
        ),
        {"info": {"plan_v3": True}},
    )
    profile_key: Mapped[str] = mapped_column(String(64), primary_key=True)
    generation: Mapped[int] = mapped_column(Integer, nullable=False)
    state: Mapped[str] = mapped_column(String(16), nullable=False)
    publication_json: Mapped[str | None] = mapped_column(Text)
    packaging_digest: Mapped[str | None] = mapped_column(String(64))
    approval_ref: Mapped[str | None] = mapped_column(String(255))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )


def _immutable_update(mapper, connection, target):
    from sqlalchemy.orm import object_session

    from app.services.plan_v3.transactions import RuntimeFailure

    session = object_session(target)
    if session is not None and session.is_modified(target, include_collections=False):
        raise RuntimeFailure("immutable_plan_evidence")


def _immutable_delete(mapper, connection, target):
    from app.services.plan_v3.transactions import RuntimeFailure

    raise RuntimeFailure("immutable_plan_evidence")


for _evidence in (
    BlueprintSourceEvent,
    OwnedBlueprintSnapshot,
    FirstPlanEvaluation,
    FirstSessionRequest,
    FirstPlanExecutionBinding,
    FirstPlanSetObservation,
):
    _event.listen(_evidence, "before_update", _immutable_update)
    _event.listen(_evidence, "before_delete", _immutable_delete)
