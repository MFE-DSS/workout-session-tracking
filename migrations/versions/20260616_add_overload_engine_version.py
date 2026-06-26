"""Sb_30.3 — overload_engine_version on workout_sessions (Sx_30 OQ-B).

Additive only. One new column :

  * workout_sessions.overload_engine_version INT NOT NULL DEFAULT 1

Hard contract :
  - No UPDATE on existing rows ; the column DEFAULT supplies 1 to all
    pre-existing rows. The overload engine is currently at version 1
    (cf. ``app.services.overload_engine.OVERLOAD_ENGINE_VERSION``), so
    every pre-existing session is implicitly compatible.
  - Downgrade drops the column — safe because no other code branches on
    it yet (Sb_30.3 only persists the marker ; consumers in Sb_30.4+).
  - Idempotent : the helper guards against partial re-apply.

Revision ID: 6h9e4c0d1f32
Revises: 5g8d3b9c0e21
"""
from alembic import op
import sqlalchemy as sa

revision = "6h9e4c0d1f32"
down_revision = "5g8d3b9c0e21"
branch_labels = None
depends_on = None


def _column_exists(table: str, column: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = {col["name"] for col in inspector.get_columns(table)}
    return column in existing


def upgrade() -> None:
    if not _column_exists("workout_sessions", "overload_engine_version"):
        op.add_column(
            "workout_sessions",
            sa.Column(
                "overload_engine_version",
                sa.Integer(),
                nullable=False,
                server_default="1",
            ),
        )


def downgrade() -> None:
    if _column_exists("workout_sessions", "overload_engine_version"):
        op.drop_column("workout_sessions", "overload_engine_version")
