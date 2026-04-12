"""add physical profile fields to users

Revision ID: a1b2c3d4e5f6
Revises: 36be39e26189
Create Date: 2026-04-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '36be39e26189'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('height_cm', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('weight_kg', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('resting_hr', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('waist_cm', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('bp_systolic', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('bp_diastolic', sa.Integer(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('bp_diastolic')
        batch_op.drop_column('bp_systolic')
        batch_op.drop_column('waist_cm')
        batch_op.drop_column('resting_hr')
        batch_op.drop_column('weight_kg')
        batch_op.drop_column('height_cm')
