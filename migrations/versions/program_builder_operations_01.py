"""MOB07 additive technical receipts, no source copy or historical backfill."""

import sqlalchemy as sa
from alembic import op

revision = "program_builder_operations_01"
down_revision = "nutrition_manual_01"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "program_builder_operations_v1",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("command_id", sa.String(128), nullable=False),
        sa.Column("operation", sa.String(24), nullable=False),
        sa.Column("request_sha256", sa.String(64), nullable=False),
        sa.Column("program_id", sa.Integer(), nullable=True),
        sa.Column("source_digest_before", sa.String(64), nullable=True),
        sa.Column("source_digest_after", sa.String(64), nullable=False),
        sa.Column("result_version", sa.Integer(), nullable=False),
        sa.Column("result_json", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["program_id"], ["user_programs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "command_id", name="uq_program_builder_owner_command"),
        info={"program_builder": True},
    )
    op.create_index(
        "ix_program_builder_owner_program",
        "program_builder_operations_v1",
        ["user_id", "program_id", "id"],
    )


def downgrade():
    if (
        op.get_bind()
        .execute(sa.text("SELECT 1 FROM program_builder_operations_v1 LIMIT 1"))
        .first()
    ):
        raise RuntimeError("Program builder receipts are not empty; retain schema")
    # migration-justify: empty-only synthetic downgrade, populated receipts refuse above.
    op.drop_index("ix_program_builder_owner_program", table_name="program_builder_operations_v1")
    # migration-justify: empty-only table, never removes historical receipts.
    op.drop_table("program_builder_operations_v1")
