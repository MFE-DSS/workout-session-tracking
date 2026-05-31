"""Sb_24.1 — implicit signal + scoring version (Sx_24).

Additive only. Three new nullable/defaulted columns to support the
implicit signal scoring model defined by Sx_24 spec:

  * session_exercises.implicit_label           VARCHAR(32) NULL
  * session_exercises.implicit_label_computed_at TIMESTAMP NULL
  * workout_sessions.scoring_version           INT NOT NULL DEFAULT 1

Hard contract (spec §H — backward compatibility):
  - No UPDATE on existing rows.
  - All pre-existing rows get scoring_version=1 via the column DEFAULT,
    so compute_session_quality() continues to use the v1 formula
    forever for any session created before this migration runs.
  - implicit_label stays NULL on pre-existing rows — the future
    detection service only populates it on the completed→ transition
    of NEW sessions.
  - Downgrade drops the columns — safe because no other code references
    them yet (the service consuming them lands in Sb_24.2 → Sb_24.5).

Revision ID: 4f7c2a8b9d10
Revises: c3d5f1e82a04
"""
from alembic import op
import sqlalchemy as sa

revision = "4f7c2a8b9d10"
down_revision = "c3d5f1e82a04"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("session_exercises") as batch_op:
        batch_op.add_column(
            sa.Column("implicit_label", sa.String(32), nullable=True)
        )
        batch_op.add_column(
            sa.Column(
                "implicit_label_computed_at",
                sa.DateTime(timezone=True),
                nullable=True,
            )
        )

    with op.batch_alter_table("workout_sessions") as batch_op:
        # NOT NULL DEFAULT 1 — every existing row receives 1 automatically.
        # SQLite (production target) honors the server_default at ALTER time.
        batch_op.add_column(
            sa.Column(
                "scoring_version",
                sa.Integer(),
                nullable=False,
                server_default=sa.text("1"),
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("workout_sessions") as batch_op:
        batch_op.drop_column("scoring_version")
    with op.batch_alter_table("session_exercises") as batch_op:
        batch_op.drop_column("implicit_label_computed_at")
        batch_op.drop_column("implicit_label")
