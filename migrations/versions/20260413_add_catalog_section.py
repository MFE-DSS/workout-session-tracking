"""add catalog_section and display_order to workout_templates

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-04-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, Sequence[str], None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('workout_templates', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('catalog_section', sa.String(32), nullable=False,
                      server_default='core')
        )
        batch_op.add_column(
            sa.Column('display_order', sa.Integer(), nullable=False,
                      server_default='0')
        )


def downgrade() -> None:
    with op.batch_alter_table('workout_templates', schema=None) as batch_op:
        batch_op.drop_column('display_order')
        batch_op.drop_column('catalog_section')
