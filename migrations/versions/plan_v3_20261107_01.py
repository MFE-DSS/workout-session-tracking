"""PLAN V3: seven additive workflow tables and ownership indexes.

No activation seed, historical update or application-startup DDL.
Revision ID: plan_v3_20261107_01
Revises: z7a2u8v9x20
"""

import sqlalchemy as sa
from alembic import op

revision = "plan_v3_20261107_01"
down_revision = "z7a2u8v9x20"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("uq_plan_v3_ws_owner", "workout_sessions", ["id", "user_id"], unique=True)
    op.create_index("uq_plan_v3_se_session", "session_exercises", ["id", "session_id"], unique=True)
    op.create_index("uq_plan_v3_set_exercise", "set_logs", ["id", "session_exercise_id"], unique=True)

    op.create_table(
        "first_plan_runtime_authorities",
        sa.Column("profile_key", sa.String(length=64), nullable=False),
        sa.Column("generation", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(length=16), nullable=False),
        sa.Column("publication_json", sa.Text(), nullable=True),
        sa.Column("packaging_digest", sa.String(length=64), nullable=True),
        sa.Column("approval_ref", sa.String(length=255), nullable=True),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
        ),
        sa.CheckConstraint(
            "state != 'ACTIVE' OR (publication_json IS NOT NULL AND packaging_digest IS NOT NULL AND approval_ref IS NOT NULL)",
            name="ck_plan_active_publication",
        ),
        sa.CheckConstraint(
            "state IN ('DISABLED', 'ACTIVE', 'WITHDRAWN')", name="ck_plan_authority_state"
        ),
        sa.CheckConstraint("generation > 0", name="ck_plan_authority_generation"),
        sa.PrimaryKeyConstraint("profile_key"),
        info={"plan_v3": True},
    )
    op.create_table(
        "blueprint_source_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("source_revision", sa.Integer(), nullable=False),
        sa.Column("request_id", sa.String(length=64), nullable=False),
        sa.Column("body_digest", sa.String(length=64), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column(
            "recorded_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint("source_revision > 0", name="ck_blueprint_positive_revision"),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_id", "request_id", name="uq_blueprint_source_request"),
        sa.UniqueConstraint("owner_id", "source_revision", name="uq_blueprint_source_revision"),
        info={"plan_v3": True},
    )
    op.create_table(
        "owned_blueprint_snapshots",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("request_id", sa.String(length=64), nullable=False),
        sa.Column("body_digest", sa.String(length=64), nullable=False),
        sa.Column("source_revision", sa.Integer(), nullable=False),
        sa.Column("as_of", sa.DateTime(), nullable=False),
        sa.Column("snapshot_json", sa.Text(), nullable=False),
        sa.Column("snapshot_digest", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
        ),
        sa.CheckConstraint("source_revision >= 0", name="ck_snapshot_revision"),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_id", "id", name="uq_blueprint_snapshot_owner"),
        sa.UniqueConstraint("owner_id", "request_id", name="uq_blueprint_snapshot_request"),
        info={"plan_v3": True},
    )
    op.create_table(
        "first_plan_evaluations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("snapshot_id", sa.String(length=36), nullable=False),
        sa.Column("parent_evaluation_id", sa.String(length=36), nullable=True),
        sa.Column("operation_kind", sa.String(length=16), nullable=False),
        sa.Column("request_id", sa.String(length=64), nullable=False),
        sa.Column("body_digest", sa.String(length=64), nullable=False),
        sa.Column("source_revision", sa.Integer(), nullable=False),
        sa.Column("authority_generation", sa.Integer(), nullable=False),
        sa.Column("request_json", sa.Text(), nullable=False),
        sa.Column("result_json", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
        ),
        sa.CheckConstraint(
            "(operation_kind = 'EVALUATE' AND parent_evaluation_id IS NULL) OR (operation_kind = 'TIME_ACK' AND parent_evaluation_id IS NOT NULL)",
            name="ck_evaluation_kind",
        ),
        sa.CheckConstraint(
            "source_revision >= 0 AND authority_generation > 0", name="ck_evaluation_generation"
        ),
        sa.ForeignKeyConstraint(
            ["owner_id", "parent_evaluation_id"],
            ["first_plan_evaluations.owner_id", "first_plan_evaluations.id"],
            name="fk_evaluation_parent_owner",
        ),
        sa.ForeignKeyConstraint(
            ["owner_id", "snapshot_id"],
            ["owned_blueprint_snapshots.owner_id", "owned_blueprint_snapshots.id"],
            name="fk_evaluation_snapshot_owner",
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_id", "id", name="uq_first_plan_evaluation_owner"),
        sa.UniqueConstraint(
            "owner_id", "operation_kind", "request_id", name="uq_first_plan_evaluation_request"
        ),
        info={"plan_v3": True},
    )
    op.create_index(
        "ix_first_plan_evaluation_snapshot",
        "first_plan_evaluations",
        ["owner_id", "snapshot_id", "created_at"],
        unique=False,
    )
    op.create_table(
        "first_plan_execution_bindings",
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("evaluation_id", sa.String(length=36), nullable=False),
        sa.Column("execution_profile_version", sa.String(length=64), nullable=False),
        sa.Column("scientific_session_id", sa.String(length=128), nullable=False),
        sa.Column("immutable_payload_json", sa.Text(), nullable=False),
        sa.Column("binding_digest", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["owner_id", "evaluation_id"],
            ["first_plan_evaluations.owner_id", "first_plan_evaluations.id"],
            name="fk_first_binding_evaluation_owner",
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["session_id", "owner_id"],
            ["workout_sessions.id", "workout_sessions.user_id"],
            name="fk_first_binding_session_owner",
        ),
        sa.PrimaryKeyConstraint("session_id"),
        sa.UniqueConstraint("session_id", "owner_id", name="uq_first_binding_session_owner"),
        info={"plan_v3": True},
    )
    op.create_table(
        "first_session_requests",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("request_id", sa.String(length=64), nullable=False),
        sa.Column("body_digest", sa.String(length=64), nullable=False),
        sa.Column("body_json", sa.Text(), nullable=False),
        sa.Column("evaluation_id", sa.String(length=36), nullable=True),
        sa.Column("state", sa.String(length=16), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=True),
        sa.Column("scientific_session_id", sa.String(length=128), nullable=True),
        sa.Column("terminal_code", sa.String(length=64), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
        ),
        sa.CheckConstraint(
            "(state = 'CREATED' AND session_id IS NOT NULL AND evaluation_id IS NOT NULL AND scientific_session_id IS NOT NULL) OR (state IN ('DENIED', 'CANCELLED') AND session_id IS NULL)",
            name="ck_first_session_terminal",
        ),
        sa.ForeignKeyConstraint(
            ["owner_id", "evaluation_id"],
            ["first_plan_evaluations.owner_id", "first_plan_evaluations.id"],
            name="fk_first_request_evaluation_owner",
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["session_id", "owner_id"],
            ["workout_sessions.id", "workout_sessions.user_id"],
            name="fk_first_request_session_owner",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_id", "request_id", name="uq_first_session_request"),
        sa.UniqueConstraint("session_id", name="uq_first_session_request_session"),
        info={"plan_v3": True},
    )
    op.create_index(
        "uq_first_created_handoff_owner",
        "first_session_requests",
        ["owner_id"],
        unique=True,
        sqlite_where=sa.text("state = 'CREATED'"),
        postgresql_where=sa.text("state = 'CREATED'"),
    )
    op.create_table(
        "first_plan_set_observations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("session_exercise_id", sa.Integer(), nullable=False),
        sa.Column("set_id", sa.Integer(), nullable=False),
        sa.Column("op_id", sa.String(length=64), nullable=False),
        sa.Column("body_digest", sa.String(length=64), nullable=False),
        sa.Column("expected_revision", sa.Integer(), nullable=False),
        sa.Column("applied_revision", sa.Integer(), nullable=False),
        sa.Column("observation_json", sa.Text(), nullable=False),
        sa.Column("receipt_json", sa.Text(), nullable=False),
        sa.Column(
            "recorded_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "expected_revision >= 0 AND applied_revision = expected_revision + 1",
            name="ck_plan_set_revision",
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["session_exercise_id", "session_id"],
            ["session_exercises.id", "session_exercises.session_id"],
            name="fk_plan_set_exercise_session",
        ),
        sa.ForeignKeyConstraint(
            ["session_id", "owner_id"],
            ["first_plan_execution_bindings.session_id", "first_plan_execution_bindings.owner_id"],
            name="fk_plan_set_binding_owner",
        ),
        sa.ForeignKeyConstraint(
            ["set_id", "session_exercise_id"],
            ["set_logs.id", "set_logs.session_exercise_id"],
            name="fk_plan_set_log_exercise",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_id", "op_id", name="uq_first_plan_set_operation"),
        sa.UniqueConstraint("set_id", "applied_revision", name="uq_first_plan_set_revision"),
        info={"plan_v3": True},
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("first_plan_set_observations")
    op.drop_index(
        "uq_first_created_handoff_owner",
        table_name="first_session_requests",
        sqlite_where=sa.text("state = 'CREATED'"),
        postgresql_where=sa.text("state = 'CREATED'"),
    )
    op.drop_table("first_session_requests")
    op.drop_table("first_plan_execution_bindings")
    op.drop_index("ix_first_plan_evaluation_snapshot", table_name="first_plan_evaluations")
    op.drop_table("first_plan_evaluations")
    op.drop_table("owned_blueprint_snapshots")
    op.drop_table("blueprint_source_events")
    op.drop_table("first_plan_runtime_authorities")
    # ### end Alembic commands ###
    op.drop_index("uq_plan_v3_set_exercise", table_name="set_logs")
    op.drop_index("uq_plan_v3_se_session", table_name="session_exercises")
    op.drop_index("uq_plan_v3_ws_owner", table_name="workout_sessions")
