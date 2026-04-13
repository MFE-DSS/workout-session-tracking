"""lateralize body measurements + add readiness_entries table

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-04-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'f6a7b8c9d0e1'
down_revision: Union[str, Sequence[str], None] = 'e5f6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -- 1. Create readiness_entries table --
    op.create_table(
        'readiness_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('recorded_on', sa.Date(), nullable=False),
        sa.Column('sleep_quality', sa.Integer(), nullable=False),
        sa.Column('fatigue_level', sa.Integer(), nullable=False),
        sa.Column('soreness_level', sa.Integer(), nullable=False),
        sa.Column('stress_level', sa.Integer(), nullable=False),
        sa.Column('motivation_level', sa.Integer(), nullable=False),
        sa.Column('resting_hr', sa.Integer(), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'recorded_on', name='uq_readiness_user_day'),
    )
    op.create_index(
        'ix_readiness_entries_user_date',
        'readiness_entries',
        ['user_id', 'recorded_on'],
    )

    # -- 2. Lateralize body_measurements: arm_cm → left/right, thigh_cm → left/right --
    #    Also add hip_cm and neck_cm.
    with op.batch_alter_table('body_measurements') as batch_op:
        # Add new lateralized columns + hip/neck
        batch_op.add_column(sa.Column('arm_cm_left', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('arm_cm_right', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('thigh_cm_left', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('thigh_cm_right', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('hip_cm', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('neck_cm', sa.Float(), nullable=True))

    # Copy existing data into lateralized columns
    op.execute(
        "UPDATE body_measurements SET "
        "arm_cm_left = arm_cm, arm_cm_right = arm_cm, "
        "thigh_cm_left = thigh_cm, thigh_cm_right = thigh_cm"
    )

    # Drop old columns
    with op.batch_alter_table('body_measurements') as batch_op:
        batch_op.drop_column('arm_cm')
        batch_op.drop_column('thigh_cm')


def downgrade() -> None:
    # Restore arm_cm and thigh_cm from left variants
    with op.batch_alter_table('body_measurements') as batch_op:
        batch_op.add_column(sa.Column('arm_cm', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('thigh_cm', sa.Float(), nullable=True))

    op.execute(
        "UPDATE body_measurements SET "
        "arm_cm = arm_cm_left, thigh_cm = thigh_cm_left"
    )

    with op.batch_alter_table('body_measurements') as batch_op:
        batch_op.drop_column('neck_cm')
        batch_op.drop_column('hip_cm')
        batch_op.drop_column('thigh_cm_right')
        batch_op.drop_column('thigh_cm_left')
        batch_op.drop_column('arm_cm_right')
        batch_op.drop_column('arm_cm_left')

    op.drop_index('ix_readiness_entries_user_date', table_name='readiness_entries')
    op.drop_table('readiness_entries')
