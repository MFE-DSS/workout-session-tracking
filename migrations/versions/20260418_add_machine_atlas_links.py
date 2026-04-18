"""Add machine atlas link columns on template_exercises.

Adds two nullable fields that point to entries in data/machine_atlas.json:
- machine_slug   : specific machine (e.g. "chest-press-machine")
- machine_family : family slug when the exercise is not machine-specific
                   (e.g. "pecs-press" for free-weight variants)

Revision ID: a19c4e3b7f21
Revises: 4d3b232a9e46
"""
from alembic import op
import sqlalchemy as sa

revision = "a19c4e3b7f21"
down_revision = "4d3b232a9e46"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("template_exercises") as batch_op:
        batch_op.add_column(sa.Column("machine_slug", sa.String(64), nullable=True))
        batch_op.add_column(sa.Column("machine_family", sa.String(64), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("template_exercises") as batch_op:
        batch_op.drop_column("machine_family")
        batch_op.drop_column("machine_slug")
