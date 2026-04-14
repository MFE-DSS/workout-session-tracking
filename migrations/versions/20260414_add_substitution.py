"""Add substitution columns.

Revision ID: 7e43cf71eef5
Revises: g7h8i9j0k1l2
"""
from alembic import op
import sqlalchemy as sa

revision = "7e43cf71eef5"
down_revision = "g7h8i9j0k1l2"
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table("template_exercises") as batch_op:
        batch_op.add_column(sa.Column("substitutes_json", sa.Text(), nullable=True))
    with op.batch_alter_table("session_exercises") as batch_op:
        batch_op.add_column(sa.Column("substituted_name", sa.String(255), nullable=True))

def downgrade():
    with op.batch_alter_table("session_exercises") as batch_op:
        batch_op.drop_column("substituted_name")
    with op.batch_alter_table("template_exercises") as batch_op:
        batch_op.drop_column("substitutes_json")
