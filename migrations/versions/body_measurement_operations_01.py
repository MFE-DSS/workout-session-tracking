"""BODY-01: additive metadata lineage, never numerical backfill.

Revision ID: body_measurement_operations_01
Revises: plan_v3_20261107_01
"""

import sqlalchemy as sa
from alembic import op

revision = "body_measurement_operations_01"
down_revision = "plan_v3_20261107_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "body_measurement_operations_v1",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("request_id", sa.String(64), nullable=False),
        sa.Column("command_digest", sa.String(64), nullable=False),
        sa.Column("operation", sa.String(8), nullable=False),
        sa.Column("root_ref", sa.Integer(), nullable=False),
        sa.Column("parent_ref", sa.Integer(), nullable=True),
        sa.Column("measurement_ref", sa.Integer(), nullable=False),
        sa.Column("applied_revision", sa.Integer(), nullable=False),
        sa.Column("changed_fields", sa.JSON(), nullable=False),
        sa.Column("provenance_by_changed_field", sa.JSON(), nullable=False),
        sa.Column("date_provenance", sa.JSON(), nullable=True),
        sa.Column("before_fingerprint", sa.String(64), nullable=True),
        sa.Column("after_fingerprint", sa.String(64), nullable=True),
        sa.Column("receipt", sa.JSON(), nullable=False),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("owner_id", "request_id", name="uq_body_operation_request"),
        sa.UniqueConstraint(
            "owner_id", "root_ref", "applied_revision", name="uq_body_operation_revision"
        ),
        sa.CheckConstraint(
            "operation IN ('CREATE','CORRECT','ERASE')", name="ck_body_operation_kind"
        ),
        sa.CheckConstraint(
            "applied_revision > 0 AND root_ref > 0 AND measurement_ref > 0",
            name="ck_body_operation_positive",
        ),
        sa.CheckConstraint(
            "(operation = 'CORRECT' AND parent_ref IS NOT NULL) OR (operation != 'CORRECT' AND parent_ref IS NULL)",
            name="ck_body_operation_parent",
        ),
        info={"body_01": True},
    )
    op.create_index(
        "ix_body_operation_root", "body_measurement_operations_v1", ["owner_id", "root_ref"]
    )
    op.create_index(
        "uq_body_correction_parent",
        "body_measurement_operations_v1",
        ["owner_id", "parent_ref"],
        unique=True,
        sqlite_where=sa.text("operation = 'CORRECT'"),
    )


def downgrade() -> None:
    # Synthetic empty-schema roundtrips are safe. Never erase a populated
    # lineage or identity reservations to make an old reader deployable.
    if (
        op.get_bind()
        .execute(sa.text("SELECT 1 FROM body_measurement_operations_v1 LIMIT 1"))
        .first()
    ):
        raise RuntimeError(
            "BODY lineage is not empty; retain schema and use a forward-compatible rollback"
        )
    op.drop_index("uq_body_correction_parent", table_name="body_measurement_operations_v1")
    op.drop_index("ix_body_operation_root", table_name="body_measurement_operations_v1")
    op.drop_table("body_measurement_operations_v1")
