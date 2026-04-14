"""Add cardio capture fields to workout_sessions."""
from alembic import op
import sqlalchemy as sa

revision = "4d3b232a9e46"
down_revision = "08f837a18a7e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("workout_sessions") as batch_op:
        batch_op.add_column(sa.Column("cardio_duration_min", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("cardio_bpm_avg", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("cardio_machine_calories", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("cardio_machine_type", sa.String(32), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("workout_sessions") as batch_op:
        batch_op.drop_column("cardio_machine_type")
        batch_op.drop_column("cardio_machine_calories")
        batch_op.drop_column("cardio_bpm_avg")
        batch_op.drop_column("cardio_duration_min")
