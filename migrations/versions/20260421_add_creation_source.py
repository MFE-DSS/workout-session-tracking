"""Add creation_source column on workout_sessions (Sb_13 telemetry).

Additive only — nullable, no backfill. Values persisted by the router:
    'reco_top'  — primary CTA under the recommendation block
    'reco_alt'  — alternative link in the recommendation block
    'launcher'  — full 3-step picker
    'library'   — library page CTA (if any)
    'replay'    — reserved for future re-run of a past session
    NULL        — pre-Sb_13 sessions, or any value outside the whitelist

Downgrade is trivial: drop the column.

Revision ID: c3d5f1e82a04
Revises: a19c4e3b7f21
"""
from alembic import op
import sqlalchemy as sa

revision = "c3d5f1e82a04"
down_revision = "a19c4e3b7f21"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("workout_sessions") as batch_op:
        batch_op.add_column(sa.Column("creation_source", sa.String(16), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("workout_sessions") as batch_op:
        batch_op.drop_column("creation_source")
