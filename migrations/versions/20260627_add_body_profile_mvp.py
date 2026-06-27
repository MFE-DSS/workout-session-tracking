"""Sb_Body_01 — Manual Body Profile MVP.

Additive only (ADD COLUMN ONLY contract). No drop, no rename, no UPDATE.

  * body_measurements.shoulder_width_cm  FLOAT NULL
  * body_measurements.calf_cm_left        FLOAT NULL
  * body_measurements.calf_cm_right       FLOAT NULL
  * CREATE TABLE body_consents            (granular Body consent)

Hard contract :
  - All new columns are nullable with no server_default → existing rows
    are untouched and remain valid (partial entries are the norm).
  - The legacy single ``body_measurements.calf_cm`` column is preserved
    for back-compat ; new lateralized entries write calf_cm_left/right.
  - Downgrade drops the additive columns and the new table — safe because
    no pre-existing code branches on them.
  - Idempotent : helpers guard against partial re-apply.

Revision ID: 7i0f5d1e2g43
Revises: 6h9e4c0d1f32
"""
from alembic import op
import sqlalchemy as sa

revision = "7i0f5d1e2g43"
down_revision = "6h9e4c0d1f32"
branch_labels = None
depends_on = None


def _column_exists(table: str, column: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = {col["name"] for col in inspector.get_columns(table)}
    return column in existing


def _table_exists(table: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table in set(inspector.get_table_names())


def upgrade() -> None:
    for column in ("shoulder_width_cm", "calf_cm_left", "calf_cm_right"):
        if not _column_exists("body_measurements", column):
            op.add_column(
                "body_measurements",
                sa.Column(column, sa.Float(), nullable=True),
            )

    if not _table_exists("body_consents"):
        op.create_table(
            "body_consents",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("consent_type", sa.String(length=64), nullable=False),
            sa.Column("granted", sa.Boolean(), nullable=False),
            sa.Column("consent_version", sa.Integer(), nullable=False),
            sa.Column("granted_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("withdrawn_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.UniqueConstraint(
                "user_id", "consent_type", name="uq_body_consent_user_type"
            ),
        )


def downgrade() -> None:
    if _table_exists("body_consents"):
        op.drop_table("body_consents")
    for column in ("calf_cm_right", "calf_cm_left", "shoulder_width_cm"):
        if _column_exists("body_measurements", column):
            op.drop_column("body_measurements", column)
